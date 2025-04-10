#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021-2022 mundialis GmbH & Co. KG

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
__author__ = "Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from json import loads

from actinia_parallel_plugin.core.jobs import insertJob
from actinia_parallel_plugin.core.jobtable import getAllIds, getAllJobs
from actinia_parallel_plugin.core.parallel_processing_job import \
    AsyncParallelJobResource
from actinia_parallel_plugin.model.batch_process_chain import (
    BatchProcessChain,
)
from actinia_parallel_plugin.resources.logging import log


def assignProcessingBlocks(jsonDict):
    """ Function to parse input BPC and split up the joblist according
        to the parallel parameter into processing blocks
    """
    bpc_dict = checkBatchProcessChain(jsonDict)

    if bpc_dict is None:
        return None
    else:
        # find out individual jobs
        jobs = [job for job in bpc_dict["jobs"]]
        parallel_jobs = [loads(job["parallel"]) for job in jobs]
        # a single parallel job makes no sense so this is corrected here
        parallel_jobs_corrected = []
        for idx, job in enumerate(parallel_jobs):
            if job is True:
                if idx != 0 and idx != len(parallel_jobs)-1:
                    if (parallel_jobs[idx-1] is False
                       and parallel_jobs[idx+1] is False):
                        job = False
                        jobs[idx]["parallel"] = "false"
                elif idx == 0:
                    if parallel_jobs[idx+1] is False:
                        job = False
                        jobs[idx]["parallel"] = "false"
                elif idx == len(parallel_jobs)-1:
                    if parallel_jobs[idx-1] is False:
                        job = False
                        jobs[idx]["parallel"] = "false"
            parallel_jobs_corrected.append(job)
        # determine the different "processing blocks"
        block_num = 1
        result_jobs = []
        for idx, job in enumerate(jobs):
            parallel = parallel_jobs_corrected[idx]
            prev_parallel = parallel_jobs_corrected[idx-1]
            if idx > 0 and (parallel is False or prev_parallel is False):
                block_num += 1
            job["batch_processing_block"] = block_num
            result_jobs.append(job)
        return result_jobs


# def cancelBatch(batchid):
#     """ Function to cancel all jobs that are RUNNING or PENDING
#         by batchid
#     """
#     jobs = getJobsByBatchId(batchid)
#     cancel_jobs = []
#     id_field = JOBTABLE.id_field
#     for job in jobs:
#         cancel_job = cancelJob(job[id_field])
#         cancel_jobs.append(cancel_job)
#     if None not in cancel_jobs:
#         # then all jobs already have a resource id etc.
#         return cancel_jobs
#     else:
#         # then there are jobs that have not been posted to actinia yet,
#         # where cancelJob returns None only
#         return getJobsByBatchId(batchid)


def checkBatchProcessChain(jsonDict):
    """ Function to test the creation of a BatchProcessChain object from the
        input JSON and return
    """

    bpc = BatchProcessChain(**jsonDict)
    # bpc.feature_type = "default"
    # check consistency
    bpc_dict = bpc.to_struct()
    if len(bpc_dict["jobs"]) == 0:
        log.error('Batch Processing Chain JSON has no jobs!')
        return None
    return bpc_dict


def checkProcessingBlockFinished(jobs, block):
    """ Function to check if a certain processing block has finished from
        an input list of jobs (db entries)
    """
    status_list = [job["status"] for job
                   in jobs if job["batch_processing_block"] == block]
    finished = all(status == "SUCCESS" for status in status_list)
    return finished


def createBatch(jsonDict, batchid, statusurl):
    """ Function to insert all jobs from a batch into the joblist
    """
    jobs = assignProcessingBlocks(jsonDict)
    if jobs is None:
        return None
    else:
        jobs_in_db = []
        for job in jobs:
            job["batch_id"] = batchid
            job["urls"] = {"status": statusurl, "resources": []}
            # assign the model
            job_in_db = insertJob(job)
            jobs_in_db.append(job_in_db)
    return jobs_in_db


def createBatchId():
    """ Function to create a unique BatchId
    """
    existing_batch_ids = getAllBatchIds()
    if len(existing_batch_ids) == 0:
        batch_id = 1
    else:
        batch_id = max(existing_batch_ids) + 1
    return batch_id


def createBatchResponseDict(jobs_list):
    """ Function to create a status response dictionary from an input list of
        jobs (db entries)
    """

    # get relevant information for each job
    if len(jobs_list) == 0:
        return {}

    # sort the jobs according to their id
    jobs = sorted(jobs_list, key=lambda d: d["id"])
    batch_id = jobs[0]["batch_id"]
    resource_ids = []
    uuids = []
    jobs_status = []
    responses = {}
    job_ids = []
    blocks = []
    for job in jobs:
        resource_id = job["resource_id"]
        # this way we also have "None" if no resource_id is given yet:
        resource_ids.append(str(resource_id))
        if resource_id is not None:
            responses[resource_id] = job["resource_response"]
        job_status = {
            "id": job["id"],
            "resource_id": str(resource_id),
            "status": str(job["status"])
            }
        jobs_status.append(job_status)
        # status.append(str(job["status"]))
        uuids.append(job["creation_uuid"])
        job_ids.append(str(job["id"]))
        blocks.append(job["batch_processing_block"])

    # determine an overall batch status
    overall_status_list = [job["status"] for job in jobs_status]
    if "ERROR" in overall_status_list:
        batch_status = "ERROR"
    elif "TERMINATED" in overall_status_list:
        if (("RUNNING" in overall_status_list)
                or ("PENDING" in overall_status_list)):
            batch_status = "TERMINATING"
        else:
            batch_status = "TERMINATED"
    elif all(status == "SUCCESS" for status in overall_status_list):
        batch_status = "SUCCESS"
    elif all(status == "PREPARING" for status in overall_status_list):
        batch_status = "PREPARING"
    elif all((status == "PENDING" or status == "PREPARING") for status
             in overall_status_list):
        batch_status = "PENDING"
    else:
        batch_status = "RUNNING"

    # create block-wise statistics
    batch_processing_blocks = []
    for block in sorted(set(blocks)):
        status_list = [job["status"] for job in jobs if
                       job["batch_processing_block"] == block]
        status_dict = _count_status_from_list(status_list)
        if len(status_list) > 1:
            parallel = len(status_list)
        else:
            parallel = 1

        block_info = {
            "block_num": block,
            "parallel": parallel
        }
        block_stats = {**block_info, **status_dict}
        batch_processing_blocks.append(block_stats)

    # create summary statistics
    summary_dict = {
        "total": len(job_ids),
        "status": _count_status_from_list(overall_status_list),
        "blocks": batch_processing_blocks
    }

    # create urls
    urls = jobs[0]["urls"]

    # create overall response dict
    responseDict = {
        "batch_id": batch_id,
        "resource_id": resource_ids,
        "summary": summary_dict,
        "resource_response": responses,
        "creation_uuids": uuids,
        "id": job_ids,
        "jobs_status": jobs_status,
        "status": batch_status,
        "urls": urls,
    }
    return responseDict


def getAllBatchIds():
    """ Function to return all unique batch_ids from the database
    """
    batch_ids_raw = set(getAllIds(batch=True))
    batch_ids = sorted([bid for bid in batch_ids_raw if bid is not None])
    return batch_ids


# def getAllBatches():
#     """ Function to return all jobs that are part of a batch from the
#     database
#     """
#     result_list = []
#     batchids = getAllBatchIds()
#     for batchid in batchids:
#         jobs = getJobsByBatchId(batchid)
#         jobs_response = createBatchResponseDict(jobs)
#         result_list.append(jobs_response)
#     result_dict = {"batch_jobs": result_list}
#     return result_dict


def getJobsByBatchId(batch_id):
    """ Function to return all jobs (db entries) via a batch_id
    """
    filter_dict = {"batch_id": batch_id}
    jobs = getAllJobs(filter_dict)
    return jobs


def startProcessingBlock(jobs, block, batch_id, project_name, mapset_name,
                         user, request_url, post_url, endpoint, method, path,
                         base_status_url, process):
    """ Function to start a specific processing block for an input list of
        jobs (db entries)
    """
    jobs_to_start = [
        job for job in jobs if job["batch_processing_block"] == block]
    jobs_responses = []
    mapset_suffix = ""
    if len(jobs_to_start) > 1:
        mapset_suffix = "_parallel_"
    for num, job in enumerate(jobs_to_start):
        process_chain = dict()
        process_chain["list"] = job["rule_configuration"]["list"]
        process_chain["version"] = job["rule_configuration"]["version"]
        jobid = job["id"]
        mapset_name_parallel = mapset_name
        if mapset_suffix != "" and mapset_name is not None:
            mapset_name_parallel += f"{mapset_suffix}{num}"
        parallel_job = AsyncParallelJobResource(
            user=user,
            request_url=request_url,
            post_url=post_url,
            endpoint=endpoint,
            method=method,
            path=path,
            process_chain=process_chain,
            project_name=project_name,
            mapset_name=mapset_name_parallel,
            batch_id=batch_id,
            job_id=jobid,
            base_status_url=base_status_url
        )
        parallel_job.start_parallel_job(process, block)
        job_entry = parallel_job.get_job_entry()
        jobs_responses.append(job_entry)
    return jobs_responses


def _count_status_from_list(input_list):
    """ Function to count the occurence of different status strings
        from a list
    """
    lower_list = [item.lower() for item in input_list]
    res_dict = {
        "preparing": lower_list.count("preparing"),
        "accepted": lower_list.count("pending"),
        "running": lower_list.count("running"),
        "finished": lower_list.count("success"),
        "error": lower_list.count("error"),
        "terminated": lower_list.count("terminated")
    }
    return res_dict
