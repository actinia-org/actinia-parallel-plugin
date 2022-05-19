#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-2022 mundialis GmbH & Co. KG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Module to communicate with jobtable
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


from datetime import datetime

from playhouse.shortcuts import model_to_dict
from peewee import Expression, AutoField, OperationalError
from uuid import uuid4
from yoyo import read_migrations
from yoyo import get_backend

from actinia_parallel_plugin.model.jobtabelle import Job, jobdb
from actinia_parallel_plugin.resources.config import JOBTABLE
from actinia_parallel_plugin.resources.logging import log


# We used `jobdb.connect(reuse_if_open=True)` at the beginning
# of every method. Now we use `with jobdb:` as described in the
# peewee docs but we still try to jobdb.close() at the end of
# each method.

def initJobDB():
    """Create jobtable on startup."""
    Job.create_table(safe=True)
    log.debug('Created jobtable if not exists')


def applyMigrations():
    backend = get_backend(
        'postgres://%s:%s@%s/%s?schema=%s' %
        (JOBTABLE.user, JOBTABLE.pw, JOBTABLE.host, JOBTABLE.database,
         JOBTABLE.schema))
    migrations = read_migrations('actinia_parallel_plugin/resources/migrations')

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    log.debug('Applied migrations.')


def getAllIds(batch=False):
    """ Method to read all jobs from jobtabelle

    Args:
    batch (bool): indicate whether only batch jobs should be read

    Returns:
    jobIds (list): the record matching the id
    """
    if batch is True:
        field = JOBTABLE.batch_id_field
    else:
        field = JOBTABLE.id_field
    with jobdb:
        queryResult = Job.select(getattr(Job, field)).dicts()

    jobIds = []

    # iterating reopens db connection!!
    for i in queryResult:
        jobIds.append(i[field])

    # log.debug("Information read from jobtable.")

    jobdb.close()

    return jobIds


def getAllJobs(filters, process=None):
    """ Method to read all jobs from jobtabelle with filter

    Args: filters (ImmutableMultiDict): the args from the HTTP call

    Returns:
    jobs (list): the records matching the filter
    """
    log.debug('Received query for jobs')

    if process == 'test':
        query = Expression('a', '=', 'a')
    elif process is None:
        query = None
    else:
        query = Expression(getattr(Job, 'process'), '=', process)

    if filters:
        log.debug("Found filters: " + str(filters))
        keys = [key for key in filters]

        for key in keys:

            try:
                getattr(Job, key)
            except Exception as e:
                log.warning(str(e))
                continue

            log.debug("Filter " + str(key)
                      + " with value " + str(filters[key]))

            if isinstance(getattr(Job, key), AutoField):
                try:
                    int(filters[key])
                except Exception as e:
                    log.error(str(e))
                    jobdb.close()
                    return

            try:
                # even though operators are listed as == and & in peewee docs,
                # for Expression creation use '=' and 'AND'.
                exp = Expression(getattr(Job, key), '=', filters[key])
                if query is not None:
                    query = Expression(query, 'AND', exp)
                else:
                    query = exp
            except AttributeError as e:
                log.error(str(e))

    with jobdb:
        queryResult = Job.select().where(query).dicts()

    jobs = []
    # iterating reopens db connection!!
    for i in queryResult:
        jobs.append(i)

    log.info("Found " + str(len(jobs)) + " results for query.")

    jobdb.close()

    return jobs


def getJobById(jobid):
    """ Method to read job from jobtabelle by id

    Args:
    jobid (int): id of job

    Returns:
    record (dict): the record matching the id
    """
    try:
        with jobdb:
            queryResult = Job.select().where(
                getattr(Job, JOBTABLE.id_field) == jobid).get()
        record = model_to_dict(queryResult)
        # log.info("Information read from jobtable for job with id "
        #          + str(record['idpk_jobs']) + ".")
        err = None
    except Job.DoesNotExist:
        record = None
        err = {
            "status": 503,
            "msg": "Either jobid does not exist or there was a "
                   "connection problem to the database. Please "
                   "try again later."
        }
    except OperationalError:
        record = None
        err = {
            "status": 412,
            "msg": "Database connection terminated abnormally before or "
                   "while processing the request. Please "
                   "try again later."
        }
    except Exception:
        record = None
        err = {
            "status": 503,
            "msg": "Either jobid does not exist or there was a "
                   "connection problem to the database. Please "
                   "try again later."
        }

    jobdb.close()

    return record, err


def getJobByResource(key, val):
    """ Method to read job from jobtabelle by resource

    Args:
    key (string): key of attribute
    val (string): value of attribute

    Returns:
    record (dict): the record matching the id
    """
    try:
        with jobdb:
            queryResult = Job.select().where(
                getattr(Job, key) == val).get()
        record = model_to_dict(queryResult)
        # log.info("Information read from jobtable for job with id "
        #          + str(record['idpk_jobs']) + ".")

    except Job.DoesNotExist:
        record = None

    jobdb.close()

    return record


def insertNewJob(
        rule_configuration,
        job_description,
        process,
        feature_type,
        actinia_core_url=None,
        actinia_core_platform=None,
        actinia_core_platform_name=None
        ):
    """Insert new job into jobtabelle.

    Args:
      rule_configuration (dict): original regeldatei
      job_description (TODO): enriched regeldatei with geometadata
      feature_type (string): feature_type name
      actinia_core_url (string): url where processing will run
      actinia_core_platform (string): platform where processing will run

    Returns:
      record (dict): the new record

    """
    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    creation_uuid = uuid4()

    job_kwargs = {
        'rule_configuration': rule_configuration,
        'job_description': job_description,
        'process': process,
        'status': 'PREPARING',
        'time_created': utcnow,
        'feature_type': feature_type,
        'actinia_core_url': actinia_core_url,
        'actinia_core_platform': actinia_core_platform,
        'actinia_core_platform_name': actinia_core_platform_name,
        'creation_uuid': creation_uuid
    }
    if "batch_id" in rule_configuration.keys():
        # then it's a batch job
        job_kwargs["processing_block"] = rule_configuration["processing_block"]
        job_kwargs["batch_id"] = rule_configuration["batch_id"]
        job_kwargs["batch_description"] = rule_configuration[
            "batch_description"]
    job = Job(**job_kwargs)

    with jobdb:
        job.save()
    # try to avoid "peewee.InterfaceError: connection already closed"
    # so make each connection duration as short as possible
    with jobdb:
        queryResult = Job.select().where((Job.time_created == utcnow) & (
            Job.creation_uuid == creation_uuid)).get()

    record = model_to_dict(queryResult)

    log.info("Created new job with id " + str(record['idpk_jobs']) + ".")

    jobdb.close()

    return record


def updateJobByID(
        jobid, status, resp, resourceId=None, message=None):
    """ Method to update job in jobtabelle when processing status changed

    Args:
    jobid (int): the id of the job
    status (string): actinia-core processing status
    resp (dict): actinia-core response
    resourceId (str): actinia-core resourceId
    message (str): general message for the job

    Returns:
    updatedRecord (TODO): the updated record
    """

    # terraformer ["PENDING", "STARTING", "STARTED", "INSTALLING", "RUNNING",
    #              "ERROR", "TERMINATING", "TERMINATED"]
    # terraformer ERROR leads to ERROR, else PREPARING or SUCCESS
    # actinia-gdi ["PREPARING"]
    # actinia-gdi ["PENDING", "RUNNING", "SUCCESS", "ERROR", "TERMINATED"]
    # actinia-core [accepted, running, finished, error, terminated]

    if status == 'accepted':
        status = 'PENDING'
    elif status == 'running':
        status = 'RUNNING'
    elif status == 'finished':
        status = 'SUCCESS'
    elif status == 'error':
        status = 'ERROR'
    elif status == 'terminated':
        status = 'TERMINATED'

    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    record, err = getJobById(jobid)
    dbStatus = record['status']

    try:
        # outcommented to see if more feasable if whole logs are passed
        # if current_app.debug is False:
        #     smallRes = dict()
        #     smallRes['message'] = resp.get('message', None)
        #     smallRes['process_results'] = resp.get('process_results', None)
        #     resp = smallRes

        if status == 'PENDING':
            if dbStatus == status:
                return record
            log.debug("Update status to " + status + " for job with id "
                      + str(record['idpk_jobs']) + ".")
            updatekwargs = {
                'status': status,
                'actinia_core_response': resp,
                'actinia_core_jobid': resourceId
            }
            if message is not None:
                updatekwargs['message'] = message

            query = Job.update(**updatekwargs).where(
                getattr(Job, JOBTABLE.id_field) == jobid
            )

        elif status == 'RUNNING':
            updatekwargs = dict()

            if dbStatus == status:
                updatekwargs['actinia_core_response'] = resp
                if message is not None:
                    updatekwargs['message'] = message

            else:
                log.debug("Update status to " + status + " for job with id "
                          + str(record['idpk_jobs']) + ".")
                updatekwargs['status'] = status
                updatekwargs['actinia_core_response'] = resp
                updatekwargs['time_started'] = utcnow
                if message is not None:
                    updatekwargs['message'] = message
                if resourceId is not None:
                    updatekwargs['actinia_core_jobid'] = resourceId
                # TODO: check if time_estimated can be set
                # time_estimated=

            query = Job.update(**updatekwargs).where(
                getattr(Job, JOBTABLE.id_field) == jobid
            )

        elif status in ['SUCCESS', 'ERROR', 'TERMINATED']:
            log.debug("Update status to " + status + " for job with id "
                      + str(record['idpk_jobs']) + ".")
            updatekwargs = {
                'status': status,
                'actinia_core_response': resp,
                'time_ended': utcnow
            }
            if message is not None:
                updatekwargs['message'] = message
            if resourceId is not None:
                updatekwargs['actinia_core_jobid'] = resourceId

            query = Job.update(**updatekwargs).where(
                getattr(Job, JOBTABLE.id_field) == jobid
            )

        else:
            log.error('Could not set the status to actinia-core status: '
                      + status + '(Status not found.)')
            return None

        with jobdb:
            query.execute()
            queryResult = Job.select().where(
                getattr(Job, JOBTABLE.id_field) == jobid).get()

        record = model_to_dict(queryResult)
    except Exception as e:
        log.error('Could not set the status to actinia-core status: ' + status)
        log.error(str(e))
        return None

    # log.debug("Updated status to " + status + " for job with id "
    #          + str(record['idpk_jobs']) + ".")

    jobdb.close()

    return record
