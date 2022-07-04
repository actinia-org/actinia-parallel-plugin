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

Endpoint definitions for job
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from flask_restful_swagger_2 import swagger
from flask import make_response, jsonify

from actinia_core.rest.resource_management import ResourceManagerBase
from actinia_core.models.response_models import \
    SimpleResponseModel

from actinia_parallel_plugin.resources.logging import log
from actinia_parallel_plugin.core.jobs import (
    getJob,
)
from actinia_parallel_plugin.apidocs import jobs


class JobId(ResourceManagerBase):
    """ Definition for endpoint standortsicherung
    @app.route('/processing_parallel/jobs/<jobid>')

    Contains HTTP GET endpoint reading a job
    Contains swagger documentation
    """

    @swagger.doc(jobs.jobId_get_docs)
    def get(self, user_id, batchid, jobid):
        """ Wrapper method to receive HTTP call and pass it to function

        This method is called by HTTP GET
        @app.route(
        '/resources/<string:user_id>/batches/<int:batchid>/jobs/<int:jobid>')
        This method is calling core method readJob
        """

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        if batchid is None:
            return make_response("No batchid was given", 400)

        if jobid is None:
            return make_response("No jobid was given", 400)

        log.info("\n Received HTTP GET request for job with id " + str(jobid))

        job, err = getJob(jobid)

        if job is not None:
            return make_response(jsonify(job), 200)
        else:
            res = (jsonify(SimpleResponseModel(
                        status=err["status"],
                        message=err["msg"]
                   )))
            return make_response(res, err["status"])

    def post(self, user_id, batchid, jobid):
        res = jsonify(SimpleResponseModel(
            status=405,
            message="Method Not Allowed"
        ))
        return make_response(res, 405)
