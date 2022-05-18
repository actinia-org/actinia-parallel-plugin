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
__author__ = "Julia Haas, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from flask_restful import Resource
from flask_restful_swagger_2 import swagger
from flask import make_response, jsonify, request

from actinia_core.models.response_models import \
    SimpleResponseModel

from actinia_parallel_plugin.resources.logging import log
from actinia_parallel_plugin.core.batches import (
    createBatchResponseDict,
    getJobsByBatchId,
)
from actinia_parallel_plugin.apidocs import batch


class BatchJobsId(Resource):
    """ Definition for endpoint
    @app.route('processing_parallel/batchjobs/<batchid>')

    Contains HTTP GET endpoint
    Contains HTTP POST endpoint
    Contains swagger documentation
    """
    @swagger.doc(batch.batchjobId_get_docs)
    def get(self, batchid):
        if batchid is None:
            return make_response("No batchid was given", 400)

        log.info(("\n Received HTTP GET request for batch"
                  f" with id {str(batchid)}"))

        jobs = getJobsByBatchId(batch)
        if len(jobs) == 0:
            res = (jsonify(SimpleResponseModel(
                        status=404,
                        message='Either batchid does not exist or there was a '
                                'connection problem to the database. Please '
                                'try again later.'
                   )))
            return make_response(res, 404)
        else:
            resp_dict = createBatchResponseDict(jobs)
            return make_response(jsonify(resp_dict), 200)

    # no docs because 405
    def post(self, batchid):
        res = jsonify(SimpleResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)
