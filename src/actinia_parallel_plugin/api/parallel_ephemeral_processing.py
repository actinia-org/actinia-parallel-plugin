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

Parallel processing
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from flask import request, make_response, jsonify, g
from flask_restful_swagger_2 import swagger, Resource

from actinia_api import URL_PREFIX

from actinia_core.core.common.app import auth
from actinia_core.core.common.config import global_config
# from actinia_core.core.common.api_logger import log_api_call
from actinia_core.models.response_models import \
    SimpleResponseModel
# from actinia_core.rest.base.user_auth import check_user_permissions
from actinia_core.rest.base.user_auth import create_dummy_user

from actinia_parallel_plugin.apidocs import batch
from actinia_parallel_plugin.core.batches import (
    createBatch,
    createBatchId,
    createBatchResponseDict,
    getJobsByBatchId,
    startProcessingBlock,
)
from actinia_parallel_plugin.resources.logging import log


class AsyncParallelEphermeralResource(Resource):
    """Resource for parallel processing"""

    decorators = []

    # if global_config.LOG_API_CALL is True:
    #     decorators.append(log_api_call)
    #
    # if global_config.CHECK_CREDENTIALS is True:
    #     decorators.append(check_user_permissions)

    if global_config.LOGIN_REQUIRED is True:
        decorators.append(auth.login_required)
    else:
        decorators.append(create_dummy_user)

    def __init__(self):
        super(AsyncParallelEphermeralResource, self).__init__()
        self.project_name = None
        self.batch_id = None

    @swagger.doc(batch.batchjobs_post_docs)
    def post(self, project_name):
        """Persistent parallel processing."""

        self.project_name = project_name
        self.post_url = request.base_url

        json_dict = request.get_json(force=True)
        log.info("Received HTTP POST with batchjob: %s" %
                 str(json_dict))

        # assign new batchid
        self.batch_id = createBatchId()

        # Generate the base of the status URL
        host_url = request.host_url
        if host_url.endswith("/") and URL_PREFIX.startswith("/"):
            self.base_status_url = f"{host_url[:-1]}{URL_PREFIX}/" \
                f"resources/{g.user.user_id}/"
        elif not host_url.endswith("/") and not URL_PREFIX.startswith("/"):
            self.base_status_url = f"{host_url}/{URL_PREFIX}/resources/" \
                f"{g.user.user_id}/"
        else:
            self.base_status_url = f"{host_url}{URL_PREFIX}/resources/" \
                f"{g.user.user_id}/"

        # create processing blocks and insert jobs into jobtable
        status_url = f"{self.base_status_url}batches/{self.batch_id}"
        jobs_in_db = createBatch(json_dict, self.batch_id, status_url)
        if jobs_in_db is None:
            res = (jsonify(SimpleResponseModel(
                        status=500,
                        message=('Error: Batch Processing Chain JSON has no '
                                 'jobs.')
                   )))
            return make_response(res, 500)

        # start first processing block
        first_jobs = startProcessingBlock(
            jobs_in_db,
            1,
            self.batch_id,
            self.project_name,
            None,  # mapset_name
            g.user,
            request.url,
            self.post_url,
            request.endpoint,
            request.method,
            request.path,
            self.base_status_url,
            "ephemeral"
        )
        first_status = [entry["status"] for entry in first_jobs]
        all_jobs = getJobsByBatchId(self.batch_id)
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
