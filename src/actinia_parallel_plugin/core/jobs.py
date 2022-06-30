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

Functions to communicate with the job db
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


def insertJob(jsonDict):
    """ function to prepare and call InsertNewJob"""

    job = insertNewJob(jsonDict)
    return job


def getJob(jobid):
    """ Method to read job from Jobtable by id

    This method can be called by HTTP GET
    @app.route('/processing_parallel/jobs/<jobid>')
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

    # follow-up actinia update, therefore without resourceId
    record = updateJobByID(
        jobid,
        status,
        shortenActiniaCoreResp(actinia_resp),
        resourceId=resource_id
    )

    return record
