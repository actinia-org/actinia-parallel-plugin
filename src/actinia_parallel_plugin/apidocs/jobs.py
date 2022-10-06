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

Documentation objects for generic job endpoints
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import os
import json
from flask_restful_swagger_2 import Schema


script_dir = os.path.dirname(os.path.abspath(__file__))

rel_path = "../apidocs/examples/jobs_get_docs_response_example.json"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as jsonfile:
    jobs_get_docs_response_example = json.load(jsonfile)


class ProcessesJobResponseModel(Schema):
    """Response schema for creating a job"""
    type = 'object'
    properties = {
        'id': {
            'type': 'integer',
            'description': 'The job ID'
        },
        'time_created': {
            'type': 'string',
            'description': 'Timestamp when job was created'
        },
        'time_started': {
            'type': 'string',
            'description': 'Timestamp when job was created'
        },
        'time_estimated': {
            'type': 'string',
            'description': 'Timestamp when job was created'
        },
        'time_ended': {
            'type': 'string',
            'description': 'Timestamp when job was created'
        },
        'status': {
            'type': 'string',
            'description': 'Status of the Job',
            'enum': [
                "PENDING",
                "RUNNING",
                "SUCCESS",
                "ERROR",
                "TERMINATED"
            ]
        },
        'resource_response': {
            'type': 'object',
            'description': 'The Response at creation time'
        },
        'resource_id': {
            'type': 'string',
            'description': 'The resource ID for the job'
        },
        'creation_uuid': {
            'type': 'string',
            'description': 'A unique id for the job at creation time before '
                           'id is known. (More unique than creation '
                           'timestamp)'
        }
    }
    example = jobs_get_docs_response_example


jobId_get_docs = {
    "summary": "Returns job by jobid.",
    "description": "This request will get the requested job from the jobtable",
    "tags": [
        "processing"
    ],
    "parameters": [
      {
        "in": "path",
        "name": "jobid",
        "type": "string",
        "description": "a jobid",
        "required": True
      }
    ],
    "responses": {
        "200": {
            "description": "The job object of the requested id",
            "schema": ProcessesJobResponseModel
        }
    }
}
