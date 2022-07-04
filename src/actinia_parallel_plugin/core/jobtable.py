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
from time import sleep
from uuid import uuid4
from yoyo import read_migrations
from yoyo import get_backend

from actinia_parallel_plugin.model.jobtable import Job, jobdb
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
    migrations = read_migrations(
        'actinia_parallel_plugin/resources/migrations')

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    log.debug('Applied migrations.')


def getAllIds(batch=False):
    """ Method to read all jobs from jobtable

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

    jobdb.close()

    return jobIds


def getAllJobs(filters):
    """ Method to read all jobs from jobtable with filter

    Args: filters (ImmutableMultiDict): the args from the HTTP call

    Returns:
    jobs (list): the records matching the filter
    """
    log.debug('Received query for jobs')

    query = None

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
    """ Method to read job from jobtable by id

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
    """ Method to read job from jobtable by resource

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

    except Job.DoesNotExist:
        record = None

    jobdb.close()

    return record


def insertNewJob(
        rule_configuration,
        ):
    """Insert new job into jobtable.

    Args:
      rule_configuration (dict): original regeldatei

    Returns:
      record (dict): the new record

    """
    utcnow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    creation_uuid = uuid4()

    job_kwargs = {
        'rule_configuration': rule_configuration,
        'status': 'PREPARING',
        'time_created': utcnow,
        'creation_uuid': creation_uuid
    }
    if "batch_id" in rule_configuration.keys():
        # then it's a batch job
        job_kwargs["batch_processing_block"] = rule_configuration[
            "batch_processing_block"]
        job_kwargs["batch_id"] = rule_configuration["batch_id"]
    if "urls" in rule_configuration.keys():
        job_kwargs["urls"] = rule_configuration["urls"]
    job = Job(**job_kwargs)

    with jobdb:
        job.save()
    # try to avoid "peewee.InterfaceError: connection already closed"
    # so make each connection duration as short as possible
    with jobdb:
        queryResult = Job.select().where((Job.time_created == utcnow) & (
            Job.creation_uuid == creation_uuid)).get()

    record = model_to_dict(queryResult)

    log.info("Created new job with id " + str(record['id']) + ".")

    jobdb.close()

    return record


def updateJobByID(jobid, status, resp, resourceId=None):
    """ Method to update job in jobtable when processing status changed

    Args:
    jobid (int): the id of the job
    status (string): actinia-core processing status
    resp (dict): actinia-core response
    resourceId (str): actinia-core resourceId

    Returns:
    updatedRecord (TODO): the updated record
    """

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
    record = None
    while record is None:
        record, err = getJobById(jobid)
        sleep(1)
    dbStatus = record['status']

    try:
        if status == 'PENDING':
            if dbStatus == status:
                return record
            log.debug("Update status to " + status + " for job with id "
                      + str(record['id']) + ".")
            updatekwargs = {
                'status': status,
                'resource_response': resp,
                'resource_id': resourceId
            }

            query = Job.update(**updatekwargs).where(
                getattr(Job, JOBTABLE.id_field) == jobid
            )

        elif status == 'RUNNING':
            updatekwargs = dict()

            if dbStatus == status:
                updatekwargs['resource_response'] = resp

            else:
                log.debug("Update status to " + status + " for job with id "
                          + str(record['id']) + ".")
                updatekwargs['status'] = status
                updatekwargs['resource_response'] = resp
                updatekwargs['time_started'] = utcnow
                if resourceId is not None:
                    updatekwargs['resource_id'] = resourceId
                # TODO: check if time_estimated can be set
                # time_estimated=

            query = Job.update(**updatekwargs).where(
                getattr(Job, JOBTABLE.id_field) == jobid
            )

        elif status in ['SUCCESS', 'ERROR', 'TERMINATED']:
            log.debug("Update status to " + status + " for job with id "
                      + str(record['id']) + ".")
            updatekwargs = {
                'status': status,
                'resource_response': resp,
                'time_ended': utcnow
            }
            if resourceId is not None:
                updatekwargs['resource_id'] = resourceId

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

    jobdb.close()

    return record
