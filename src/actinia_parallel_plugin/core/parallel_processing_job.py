#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022 mundialis GmbH & Co. KG

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

import pickle

from actinia_core.core.common.kvdb_interface import enqueue_job

from actinia_parallel_plugin.core.jobtable import getJobById
from actinia_parallel_plugin.core.jobs import updateJob
from actinia_parallel_plugin.resources.logging import log
from actinia_parallel_plugin.core.parallel_resource_base import \
    ParallelResourceBase


class AsyncParallelJobResource(ParallelResourceBase):
    """Job for parallel processing"""

    def __init__(self, user, request_url, post_url, endpoint, method, path,
                 process_chain, project_name, mapset_name,
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
        self.project_name = project_name
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
            project_name=self.project_name,
            mapset_name=self.mapset_name
        )
        if rdc:
            if process == "ephemeral":
                from actinia_parallel_plugin.core.ephemeral_processing import \
                    start_job
                # # for debugging comment enqueue_job(...) and use the
                # # following commented lines
                # for var in [
                #         'GISRC', 'GISBASE', 'LD_LIBRARY_PATH',
                #         'GRASS_ADDON_PATH', 'GIS_LOCK']:
                #     import os
                #     if var in os.environ:
                #         del os.environ[var]
                # from actinia_parallel_plugin.core.ephemeral_processing \
                #     import ParallelEphemeralProcessing
                # processing = ParallelEphemeralProcessing(
                #     rdc, self.batch_id, block, self.job_id,
                #     self.user,
                #     self.request_url,
                #     self.post_url,
                #     self.endpoint,
                #     self.method,
                #     self.path,
                #     self.base_status_url)
                # processing.run()
            # elif process == "persistent":
            #     from actinia_parallel_plugin.core.persistent_processing \
            #         import start_job
            #     # TODO
            #     # # for debugging
            #     # from actinia_parallel_plugin.core.persistent_processing \
            #     #     import ParallelPersistentProcessing
            #     # processing = ParallelPersistentProcessing(
            #     #     rdc, self.batch_id, block, self.job_id,
            #     #     self.user,
            #     #     self.request_url,
            #     #     self.post_url,
            #     #     self.endpoint,
            #     #     self.method,
            #     #     self.path,
            #     #     self.base_status_url)
            #     # processing.run()
            else:
                msg = f"Process '{process}' not yet supported!"
                log.error(msg)
                _, response_model = pickle.loads(self.response_data)
                response_model["status"] = "error"
                response_model["message"] = msg
                job = updateJob(self.resource_id, response_model, self.job_id)
                return job
            enqueue_job(
                self.job_timeout,
                start_job,
                rdc,
                self.batch_id,
                block,
                self.job_id,
                self.user,
                self.request_url,
                self.post_url,
                self.endpoint,
                self.method,
                self.path,
                self.base_status_url
            )

        # update job in jobtable
        self.response_data = self.resource_logger.get(
            self.user_id, self.resource_id, self.iteration)
        _, response_model = pickle.loads(self.response_data)
        job = updateJob(self.resource_id, response_model, self.job_id)
        return job

    def get_job_entry(self):
        """Return job entry by requesting jobtable from db."""
        return getJobById(self.job_id)[0]
