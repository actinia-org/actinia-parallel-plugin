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

from actinia_parallel_plugin.core.jobtable import (
    getJobById,
    insertNewJob,
    updateJobByID,
)
from actinia_parallel_plugin.resources.logging import log


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
    #         actinia_core_url = ACTINIACORE_VM.scheme + '://' + \
    #             actinia_core_url
    #     if len(actinia_core_url.split(':')) == 2:
    #         actinia_core_url += ':' + ACTINIACORE_VM.port
    #
    # if (regeldatei.processing_platform_name):
    #     actinia_core_platform_name = regeldatei.processing_platform_name

    job = insertNewJob(
        jsonDict,
        process_chain_struct,
        process,
        # actinia_core_url,
        # actinia_core_platform,
        # actinia_core_platform_name
    )
    return job


def getJob(jobid):
    """ Method to read job from Jobtable by id

    This method can be called by HTTP GET
    @app.route('/processes/standortsicherung/jobs/<jobid>')
    """

    job, err = getJobById(jobid)

    return job, err


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
