#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-present mundialis GmbH & Co. KG

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

Parallel processing
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import json
import pickle
from flask import request, make_response, jsonify
from flask_restful_swagger_2 import swagger
# from flask_restful_swagger_2 import Resource

from actinia_core.models.response_models import \
    SimpleResponseModel
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job

from actinia_parallel_plugin.apidocs import helloworld
from actinia_parallel_plugin.core.batches import (
    createBatch,
    createBatchId,
    createBatchResponseDict,
    getJobsByBatchId,
    # startProcessingBlock,
)
from actinia_parallel_plugin.core.jobtable import (
    getJobById,
)
from actinia_parallel_plugin.model.response_models import (
    SimpleStatusCodeResponseModel,
)
# from actinia_parallel_plugin.model.batch_process_chain import (
#     SingleJob,
# )
# from actinia_parallel_plugin.core.jobtable import updateJobByID
# from actinia_parallel_plugin.core.jobs import updateJob
from actinia_parallel_plugin.resources.logging import log
from actinia_parallel_plugin.core.persistent_processing import start_job
from actinia_parallel_plugin.core.parallel_processing_job import AsyncParallelJobResource


class AsyncParallelPersistentResource(ResourceBase):
    """Resource for parallel processing"""

    def __init__(self):
        super(AsyncParallelPersistentResource, self).__init__()
        self.location_name = None
        self.mapset_name = None
        self.batch_id = None

    @swagger.doc(helloworld.describeHelloWorld_get_docs)
    def get(self, location_name, mapset_name):
        """Get 'Hello world!' as answer string."""
        return SimpleStatusCodeResponseModel(status=200, message="TEST")

    # def prepare_actinia(self):
    # e.g. start a VM and check connection to actinia-core on it
    # return things

    def _start_job(self, process, process_chain, jobid):
        """Starting job in running actinia-core instance and update job db."""
        job, err = getJobById(jobid)
        # TODO prepare_actinia ?
        # TODO execute_actinia ?
        # TODO goodby_actinia ?

        # has_json = False
        # self.request_data = pc

        rdc = self.preprocess(
            has_json=True,
            location_name=self.location_name,
            mapset_name=self.mapset_name
        )
        if rdc:
            block = 1
            from actinia_parallel_plugin.core.persistent_processing import \
                ParallelPersistentProcessing
            processing = ParallelPersistentProcessing(
                rdc, self.batch_id, block, jobid)
            processing.run(process_chain)

            # enqueue_job(
            #     self.job_timeout,
            #     start_job,
            #     rdc,
            #     self.batch_id,
            #     block,
            #     jobid,
            #     json.dumps(process_chain)
            # )

        # html_code, response_model = pickle.loads(self.response_data)
        # job = updateJob(resourceId, actiniaCoreResp, jobid)
        # job = updateJobByID(
        #     jobid, status, shortenActiniaCoreResp(actiniaCoreResp), resourceId
        # )
        job = getJobById(jobid)[0]
        return job
        # return make_response(jsonify(response_model), html_code)

        # initial actinia update, therefore with resourceId
        # job = updateJobWithActiniaByID(
        #     jobid, status, shortenActiniaCoreResp(actiniaCoreResp), resourceId
        # )
        # return job

    def _start_processing_block(self, jobs, block):
        """Starts first processing block of jobs from batch process.
        """
        jobs_to_start = [
            job for job in jobs if job["processing_block"] == block]
        jobs_responses = []
        for job in jobs_to_start:
            process_chain = dict()
            process_chain["list"] = job["rule_configuration"]["list"]
            process_chain["version"] = job["rule_configuration"]["version"]
            jobid = job["idpk_jobs"]
            start_kwargs = {
                "process": job["process"],
                # "pc": SingleJob(**job["job_description"]),
                "process_chain": process_chain,
                "jobid": job["idpk_jobs"],
                # "actinia_core_platform": job["actinia_core_platform"],
                # "actinia_core_url": job["actinia_core_url"]
            }
            parallel_job = AsyncParallelJobResource(
                post_url=self.post_url,
                process_chain=process_chain,
                location_name=self.location_name,
                mapset_name=self.mapset_name,
                batch_id=self.batch_id,
                job_id=jobid
            )
            parallel_job.start_job("persistent", 1)
            job_entry = parallel_job.get_job_entry()
            jobs_responses.append(job_entry)
        return jobs_responses

    # TODO get all batch jobs
    @swagger.doc(helloworld.describeHelloWorld_get_docs)
    # def get(self):
    def post(self, location_name, mapset_name):
        """Persistent parallel processing."""

        self.location_name = location_name
        self.mapset_name = mapset_name
        # import pdb; pdb.set_trace()

        json_dict = request.get_json(force=True)
        log.info("Received HTTP POST with batchjob: %s" %
                 str(json_dict))

        # assign new batchid
        self.batch_id = createBatchId()
        # create processing blocks and insert jobs into jobtable
        jobs_in_db = createBatch(json_dict, "persistent", self.batch_id)
        if jobs_in_db is None:
            res = (jsonify(SimpleResponseModel(
                        status=500,
                        message=('Error: Batch Processing Chain JSON has no '
                                 'jobs.')
                   )))
            return make_response(res, 500)

        # start first processing block
        first_jobs = self._start_processing_block(jobs_in_db, 1)
        first_status = [entry["status"] for entry in first_jobs]
        all_jobs = getJobsByBatchId(self.batch_id, "persistent")
        if None in first_jobs:
            res = (jsonify(SimpleResponseModel(
                        status=500,
                        message=('Error: There was a problem starting the '
                                 'first jobs of the batchjob.')
                   )))
            return make_response(res, 500)
        elif "ERROR" not in first_status:
            return make_response(jsonify(createBatchResponseDict(all_jobs)),
                                 201)
        else:
            return make_response(jsonify(createBatchResponseDict(all_jobs)),
                                 412)

    # # TODO start a parallel processing job as batch job
    # @swagger.doc(helloworld.describeHelloWorld_post_docs)
    # def post(self):
    #     """Hello World post method with name from postbody."""
    #
    #     req_data = request.get_json(force=True)
    #     if isinstance(req_data, dict) is False or "name" not in req_data:
    #         return make_response("Missing name in JSON content", 400)
    #     name = req_data["name"]
    #     msg = transform_input(name)
    #
    #     return SimpleStatusCodeResponseModel(status=200, message=msg)
