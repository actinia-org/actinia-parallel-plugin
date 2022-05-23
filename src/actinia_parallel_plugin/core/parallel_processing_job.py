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

Parallel processing job
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import json
import pickle

# from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job

# from actinia_parallel_plugin.core.batches import (
#     # createBatch,
#     # createBatchId,
#     # createBatchResponseDict,
#     # getJobsByBatchId,
# )
from actinia_parallel_plugin.core.jobtable import (
    getJobById,
)
# from actinia_parallel_plugin.model.response_models import (
#     SimpleStatusCodeResponseModel,
# )
from actinia_parallel_plugin.core.jobs import updateJob
from actinia_parallel_plugin.resources.logging import log
# from actinia_parallel_plugin.core.persistent_processing import start_job
from actinia_parallel_plugin.core.parallel_resource_base import ParallelResourceBase


class AsyncParallelJobResource(ParallelResourceBase):
    """Job for parallel processing"""

    def __init__(self, user, request_url, post_url, endpoint, method, path,
                 process_chain, location_name, mapset_name,
                 batch_id, job_id, base_status_url):
        super(AsyncParallelJobResource, self).__init__(
            user=user,
            request_url=request_url,
            endpoint=endpoint,
            method=method,
            path=path,
            post_url=post_url,
            base_status_url=base_status_url
        )
        self.location_name = location_name
        self.mapset_name = mapset_name
        self.batch_id = batch_id
        self.job_id = job_id
        self.request_data = process_chain
        self.post_url = post_url
        self.endpoint = endpoint
        self.method = method
        self.path = path
        self.base_status_url = base_status_url

    def start_parallel_job(self, process, block):
        """Starting job in running actinia-core instance and update job db."""
        job, err = getJobById(self.job_id)
        # TODO prepare_actinia ?
        # TODO execute_actinia ?
        # TODO goodby_actinia ?

        rdc = self.preprocess(
            has_json=False,
            location_name=self.location_name,
            mapset_name=self.mapset_name
        )
        if rdc:

            if process == "persistent":
                from actinia_parallel_plugin.core.persistent_processing import \
                    start_job
                # # for debugging (works not so gogd with parallel processing)
                # from actinia_parallel_plugin.core.persistent_processing import \
                #     ParallelPersistentProcessing
                # processing = ParallelPersistentProcessing(
                #     rdc, self.batch_id, block, self.job_id,
                #     self.user,
                #     self.request_url,
                #     self.post_url,
                #     self.endpoint,
                #     self.method,
                #     self.path,
                #     self.base_status_url)
                # processing.run()
            elif process == "ephemeral":
                from actinia_parallel_plugin.core.ephemeral_processing import \
                    start_job
                # for debugging
                for var in [
                        'GISRC', 'GISBASE', 'LD_LIBRARY_PATH',
                        'GRASS_ADDON_PATH', 'GIS_LOCK']:
                    import os
                    if var in os.environ:
                        del os.environ[var]
                from actinia_parallel_plugin.core.ephemeral_processing import \
                    ParallelEphemeralProcessing
                processing = ParallelEphemeralProcessing(
                    rdc, self.batch_id, block, self.job_id,
                    self.user,
                    self.request_url,
                    self.post_url,
                    self.endpoint,
                    self.method,
                    self.path,
                    self.base_status_url)
                processing.run()
            else:
                # TODO change start_job import
                from actinia_parallel_plugin.core.persistent_processing import \
                    start_job
            # enqueue_job(
            #     self.job_timeout,
            #     start_job,
            #     rdc,
            #     self.batch_id,
            #     block,
            #     self.job_id,
            #     self.user,
            #     self.request_url,
            #     self.post_url,
            #     self.endpoint,
            #     self.method,
            #     self.path,
            #     self.base_status_url
            # )

        # update job in jobtable
        self.response_data = self.resource_logger.get(
            self.user_id, self.resource_id, self.iteration)
        _, response_model = pickle.loads(self.response_data)
        job = updateJob(self.resource_id, response_model, self.job_id)
        return job

    def get_job_entry(self):
        """Return job entry by requesting jobtable from db."""
        return getJobById(self.job_id)[0]

    # # first_jobs = self._start_processing_block(jobs_in_db, 1)
    # def _start_processing_block(self, jobs, block):
    #     """Starts first processing block of jobs from batch process.
    #     """
    #     jobs_to_start = [
    #         job for job in jobs if job["processing_block"] == block]
    #     jobs_responses = []
    #     for job in jobs_to_start:
    #         process_chain = dict()
    #         process_chain["list"] = job["rule_configuration"]["list"]
    #         process_chain["version"] = job["rule_configuration"]["version"]
    #         start_kwargs = {
    #             "process": job["process"],
    #             "process_chain": process_chain,
    #             "jobid": job["idpk_jobs"],
    #             # "actinia_core_platform": job["actinia_core_platform"],
    #             # "actinia_core_url": job["actinia_core_url"]
    #         }
    #         job_entry = self._start_job(**start_kwargs)
    #         jobs_responses.append(job_entry)
    #     return jobs_responses
