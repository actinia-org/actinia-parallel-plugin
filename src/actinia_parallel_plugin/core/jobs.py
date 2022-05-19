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

Module to start the process Standortsicherung
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.resource_base import ResourceBase


# from actinia_gdi.api.common import checkConnectionWithoutResponse
# from actinia_gdi.core.actiniaCore import postActiniaCore, cancelActiniaCore
# from actinia_gdi.core.actiniaCore import parseActiniaIdFromUrl
# from actinia_gdi.core.gnosWriter import update
from actinia_parallel_plugin.core.jobtable import (
    getJobById,
    getJobByResource,
    insertNewJob,
    updateJobByID,
)
# from actinia_gdi.core.jobtable import insertNewJob, getJobById
# from actinia_gdi.core.jobtable import getAllIds, getAllJobs, cancelJobById
# from actinia_gdi.core.jobtable import getJobByResource
# from actinia_gdi.core.jobtable import updateJobWithActiniaByID
# from actinia_gdi.core.jobtable import updateJobWithTerraformByID
# from actinia_gdi.core.regeldatei import parseRulefile
# from actinia_gdi.model.regeldatei import Regeldatei
# from actinia_gdi.model.batchProcessChain import BatchProcessChain
# from actinia_gdi.resources.config import ACTINIACORE
# from actinia_gdi.resources.config import ACTINIACORE_VM
# from actinia_gdi.resources.config import PROCESSING
from actinia_parallel_plugin.resources.logging import log
# from actinia_gdi.core.terraformer import createVM, destroyVM
# from actinia_gdi.core.actiniaCore import shortenActiniaCoreResp


# def startJob(process, regeldatei, actinia, jobid):
#     """ Starting job in running actinia-core instance and update job db """
#     job, err = getJobById(jobid)
#     # url = job['actinia_core_url']
#     # platform = job['actinia_core_platform']
#     # connection = checkConnectionWithoutResponse(actinia, url)
#     # if connection is not None:
#     #     actiniaCoreResp = postActiniaCore(
#     #         process,
#     #         regeldatei,
#     #         url,
#     #         platform
#     #     )
#     #     log.debug(actiniaCoreResp)
#     #     status = actiniaCoreResp['status']
#     #
#     #     if status == 'error':
#     #         log.error("Error start processing in actinia-core")
#     #
#     #     resourceId = parseActiniaIdFromUrl(actiniaCoreResp['resource_id'])
#     #     # initial actinia update, therefore with resourceId
#     #     job = updateJobWithActiniaByID(
#     #         jobid, status, shortenActiniaCoreResp(actiniaCoreResp), resourceId
#     #     )
#     #     return job
#     # else:
#     #     job = updateJobWithActiniaByID(
#     #         jobid, 'error', None,
#     #         message=f"Error connection check to actinia ({url}) failed")
#     #     return job
#
#     # TODO start job
#     import pdb; pdb.set_trace()
#     # initial actinia update, therefore with resourceId
#     # job = updateJobWithActiniaByID(
#     #     jobid, status, shortenActiniaCoreResp(actiniaCoreResp), resourceId
#     # )
#     # return job


def insertJob(jsonDict, process, process_chain):
    """ function to prepare and call InsertNewJob from regeldatei"""
    # actinia_core_url = None
    # actinia_core_platform = None
    # actinia_core_platform_name = None

    try:
        process_chain_struct = process_chain.to_struct()
    except Exception as e:
        log.error('Regeldatei is invalid!')
        log.error(e)
        return None

    # vm_procs = PROCESSING.actinia_vm_processes.replace(
    #     ' ', '').split(',')
    #
    # # set default actinia connection parameter
    # if (process in vm_procs):
    #     actinia_core_url = None
    #     actinia_core_platform = 'vm'
    # else:
    #     actinia_core_url = ACTINIACORE.url
    #     actinia_core_platform = 'openshift'
    #
    # # overwrite actinia connection parameter if set in rulefile
    # if (regeldatei.processing_platform):
    #     if (regeldatei.processing_platform.lower() == 'vm'):
    #         actinia_core_url = None
    #         actinia_core_platform = 'vm'
    #     elif (regeldatei.processing_platform.lower() == 'openshift'):
    #         actinia_core_url = ACTINIACORE.url
    #         actinia_core_platform = 'openshift'
    #
    # # overwrite actinia connection parameter if set in rulefile
    # if (regeldatei.processing_host):
    #     actinia_core_url = regeldatei.processing_host
    #     if not actinia_core_url.startswith('http'):
    #         actinia_core_url = ACTINIACORE_VM.scheme + '://' + actinia_core_url
    #     if len(actinia_core_url.split(':')) == 2:
    #         actinia_core_url += ':' + ACTINIACORE_VM.port
    #
    # if (regeldatei.processing_platform_name):
    #     actinia_core_platform_name = regeldatei.processing_platform_name

    job = insertNewJob(
        jsonDict,
        process_chain_struct,
        process,
        process_chain.feature_type,
        # actinia_core_url,
        # actinia_core_platform,
        # actinia_core_platform_name
    )
    return job


# def startJobByActiniaType(process, regeldatei, jobid,
#                           actinia_core_platform=None, actinia_core_url=None):
#     """ Helper function to start job or create VM """
#     # if actinia_core_platform == 'vm' and actinia_core_url is None:
#     #     job = createVM(process, regeldatei, jobid)
#     # elif actinia_core_platform == 'vm':
#     #     job = startJob(process, regeldatei, 'actinia-core-vm', jobid)
#     # else:
#     #     job = startJob(process, regeldatei, 'actinia-core', jobid)
#     job = startJob(process, regeldatei, 'actinia-core', jobid)
#     return job


# def createJob(jsonDict, process):
#     """ Method to parse regeldatei including fetching information from
#     geonetwork and writing information to Jobtable
#     as well as starting job in actinia-core
#
#     This method can be called by HTTP POST
#     @app.route('/processes/standortsicherung/jobs')
#     """
#
#     if process == "netdefinition":
#         regeldatei = BatchProcessChain(**jsonDict)
#         regeldatei.feature_type = "null"
#     else:
#         regeldatei = parseRulefile(jsonDict)
#
#     job = insertJob(jsonDict, process, regeldatei)
#     jobid = job['idpk_jobs']
#     actinia_core_platform = job["actinia_core_platform"]
#     actinia_core_url = job["actinia_core_url"]
#     job = startJobByActiniaType(process=process, regeldatei=regeldatei,
#                                 jobid=jobid,
#                                 actinia_core_platform=actinia_core_platform,
#                                 actinia_core_url=actinia_core_url)
#
#     return job


def getJob(jobid):
    """ Method to read job from Jobtable by id

    This method can be called by HTTP GET
    @app.route('/processes/standortsicherung/jobs/<jobid>')
    """

    job, err = getJobById(jobid)

    return job, err


# def getAllJobIDs():
#     """ Method to read all job ids from Jobtable
#
#     This method can be called by HTTP GET
#     @app.route('/processes/standortsicherung/jobs.html')
#     """
#
#     job = getAllIds(batch=False)
#
#     return job
#
#
# def getJobs(filters, process):
#     """ Method to read all jobs from Jobtable with filter
#
#     This method can be called by HTTP GET
#     @app.route('/processes/standortsicherung/jobs')
#     """
#
#     jobs = getAllJobs(filters, process)
#
#     return jobs

# status

def shortenActiniaCoreResp(fullResp):
    # replace webhook authentication with '***'
    if 'process_chain_list' in fullResp:
        if len(fullResp['process_chain_list']) > 0:
            if 'webhooks' in fullResp['process_chain_list'][0]:
                if 'auth' in fullResp['process_chain_list'][0]['webhooks']:
                    fullResp['process_chain_list'][0]['webhooks']['auth'] = \
                        '***:***'
    return fullResp


def updateJob(resource_id, actinia_resp, jobid):
    """ Method to update job in Jobtable

    This method is called by webhook endpoint
    """

    status = actinia_resp["status"]
    # record = getJobByResource("actinia_core_jobid", resource_id)

    # follow-up actinia update, therefore without resourceId
    record = updateJobByID(
        jobid,
        status,
        shortenActiniaCoreResp(actinia_resp),
        resourceId=resource_id
    )

    # # TODO: for now if multiple records need to be updated (eg. for PT), this
    # # can be told by specifying multiple uuids comma-separated in the
    # # "feature_uuid" field of the rulefile. This might change later...
    # if status == 'finished':
    #     try:
    #         gnosUuid = record['job_description']['feature_uuid']
    #         utcnow = record['time_ended']
    #     except Exception:
    #         log.warning('Feature has no uuid or time_ended')
    #         gnosUuid = None
    #         utcnow = None
    #     try:
    #         uuids = gnosUuid.split(',')
    #         for uuid in uuids:
    #             update(uuid, utcnow)
    #     except Exception:
    #         log.warning('Could not update geonetwork record')

    # # shutdown VM if process was calculated on VM
    # terminate_status = ['finished', 'error', 'terminated']
    # processing_platform = record['actinia_core_platform']
    # process = record['process']
    #
    # if (status in terminate_status
    #         and processing_platform is not None
    #         and processing_platform.lower() == 'vm'
    #         and 'processing_host' not in record['rule_configuration']):
    #
    #     record = destroyVM(process, jobid)

    return record


# def updateJobByTerraform(terraformer_id, resp):
#     """ Method to update job in Jobtable
#
#     This method is called by webhook endpoint
#     """
#     record = getJobByResource('terraformer_id', terraformer_id)
#     jobid = record['idpk_jobs']
#     instance_ips = resp['instance_ips']
#     status = resp['status']
#
#     log.debug('Status of %s is %s' % (jobid, status))
#     if (status != 'STARTING'
#             and (instance_ips is None or len(instance_ips) == 0)):
#         log.error('Terraformer did not tell an IP for %s. Cannot start'
#                   ' processing or terminate', str(jobid))
#         record = updateJobWithTerraformByID(
#             jobid,
#             terraformer_id,
#             resp,
#             status='ERROR'
#         )
#         return record
#
#     if status != 'STARTING':
#         if len(instance_ips) > 1:
#             log.warning('Found more than one IP, only using last one')
#             log.debug(instance_ips)
#         # Currently we only start one VM for one dedicated job. Therefore we
#         # assume, that only one VM was created and assign one IP to the
#         # variable. If multiple VMs were created, we take the last IP
#         for key, val in instance_ips.items():
#             actinia_core_ip = val
#
#         actinia_core_url = (ACTINIACORE_VM.scheme + '://' + actinia_core_ip
#                             + ':' + ACTINIACORE_VM.port)
#     else:
#         actinia_core_url = None
#
#     if status in ['PENDING', 'STARTING', 'STARTED', 'INSTALLING', 'RUNNING']:
#         status = 'PREPARING'
#     elif status == 'ERROR':
#         status = 'ERROR'
#         # shutdown VM
#         process = record['process']
#         record = destroyVM(process, jobid)
#     elif status == 'TERMINATING':
#         status = None  # keep actinia status
#     elif status == 'TERMINATED':
#         status = None  # keep actinia status
#
#     record = updateJobWithTerraformByID(
#         jobid,
#         terraformer_id,
#         resp,
#         actinia_core_url=actinia_core_url,
#         status=status
#     )
#
#     # start job in actinia
#     if resp['status'] == 'RUNNING':
#         process = record['process']
#         regeldatei = record['job_description']
#         rulefile = Regeldatei(**regeldatei)
#         record = startJob(process, rulefile, 'actinia-core-vm', jobid)
#     else:
#         log.debug('Terraformer status is not "RUNNING", waiting further')
#
#     return record
#
#
# def cancelJob(jobid):
#     """ Method to cancel job from Jobtable by id
#
#     This method can be called by HTTP POST
#     @app.route('/processes/standortsicherung/jobs/<jobid>/operations/cancel')
#     """
#
#     actiniacore = 'actinia-core'
#     vm_needs_to_be_destroyed = False
#
#     job, err = getJobById(jobid)
#
#     if job is None:
#         log.error(f"Error by requesting job with jobid {jobid}: {err['msg']}")
#         return None
#
#     status = job['status']
#     resourceId = job['actinia_core_jobid']
#
#     if not status or not resourceId:
#         # the VM should be destroyed if the status is PREPARING and no resourcId
#         # is set, e.g. if the starting of the VM fails without an ERROR
#         if status == 'PREPARING' and not resourceId:
#             pass
#         else:
#             log.error('Job status or resourceId is not set!')
#             return None
#
#     if resourceId:
#         log.debug('Job status is ' + status + ' and resourceId is: ' + resourceId)
#         url = job['actinia_core_url']
#     platform = job['actinia_core_platform']
#
#     if platform.lower() == 'vm':
#         actiniacore = 'actinia-core-vm'
#         vm_needs_to_be_destroyed = True
#
#     if ('processing_host' in job['rule_configuration']
#             and job['rule_configuration']['processing_host'] is not None):
#         vm_needs_to_be_destroyed = False
#
#     if resourceId:
#         connection = checkConnectionWithoutResponse(actiniacore, url)
#     else:
#         connection = None
#
#     if status in ['PENDING', 'RUNNING'] and connection is not None:
#         log.debug('Status is in PENDING or RUNNING, will cancel')
#         res = cancelActiniaCore(resourceId, url, platform)
#         if res:
#             log.debug('Actinia-Core response TRUE')
#             job = cancelJobById(jobid)
#             log.debug('Job in jobtable is ' + job['status'])
#             return job
#         else:
#             log.debug('Actinia-Core response is None')
#             return None
#
#     elif platform.lower() == 'vm' and vm_needs_to_be_destroyed is True:
#         if connection is not None:
#             log.debug('actinia-core connection exists and VM will ' +
#                       'be destroyed')
#         else:
#             log.debug('actinia-core connection does not exist, but ' +
#                       'VM will be destroyed')
#         # destroy actinia-core VM
#         record = destroyVM(job['process'], jobid)
#         if record:
#             log.debug('DestroyVM response exists')
#             job = cancelJobById(jobid)
#             log.debug('Job in jobtable is ' + job['status'])
#             return job
#
#     elif connection is not None:
#         log.debug('Status not in PENDING or RUNNING and no VM to destroy, pass')
#         return job
#
#     else:
#         log.error('There is no connection to actinia-core')
#         return None
