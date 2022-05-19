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

from flask_restful_swagger_2 import Schema

from actinia_parallel_plugin.apidocs.regeldatei import (
    RegeldateiModel,
    ProcessesProcOutputModel,
)


class EnrichedProcInputBaseModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
            'description': 'Name of input data'
        },
        'type': {
            'type': 'string',
            'enum': ["GNOS", "DATABASE", "PARAMETER", "STATUS"],
            'description': 'Type of input. Can be "GNOS", "DATABASE", ' +
                           '"PARAMETER" or "STATUS"'
        },
        'geodata_meta': "string"  # TODO: GeodataResponseModel
    }


class EnrichedProcInputGnosModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        EnrichedProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        # },
        # ProcessesProcInputGnosModel,
        # {
        #     '$ref': '#/definitions/ProcessesProcInputGnosModel'
        }

    ]


class EnrichedProcInputDatabaseModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        EnrichedProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        # },
        # ProcessesProcInputDatabaseModel,
        # {
        #     '$ref': '#/definitions/ProcessesProcInputDatabaseModel'
        }
    ]


class EnrichedProcInputParameterModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        EnrichedProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        # },
        # ProcessesProcInputParameterModel,
        # {
        #     '$ref': '#/definitions/ProcessesProcInputParameterModel'
        }
    ]


class EnrichedProcInputStatusModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        EnrichedProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        # },
        # ProcessesProcInputStatusModel,
        # {
        #     '$ref': '#/definitions/ProcessesProcInputStatusModel'
        }
    ]


class EnrichedProcInputModel(Schema):
    """Request schema for creating a job"""
    type = 'object'
    # TODO: use oneOf (was not parsed in petstore)
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        EnrichedProcInputGnosModel,
        EnrichedProcInputDatabaseModel,
        EnrichedProcInputParameterModel,
        EnrichedProcInputStatusModel,
        {
            '$ref': '#/definitions/EnrichedProcInputGnosModel'
        },
        {
            '$ref': '#/definitions/EnrichedProcInputDatabaseModel'
        },
        {
            '$ref': '#/definitions/EnrichedProcInputParameterModel'
        },
        {
            '$ref': '#/definitions/EnrichedProcInputStatusModel'
        }
    ]


class EnrichedProcModel(Schema):
    """Request schema for creating a job"""
    type = 'object'
    properties = {
        'name': {
            'type': 'integer',
            'description': 'Name of process'
        },
        'input': {
            'type': 'array',
            'description': 'Definitions for process input data',
            'items': EnrichedProcInputModel
        },
        'output': {
            'type': 'array',
            'description': 'Definitions for process output data',
            'items': ProcessesProcOutputModel
        },
        'dependsOn': {
            'type': 'string',
            'description': 'List of names of processes on which this process' +
                           ' depends on. See also "status" as input parameter'
        }
    }


class EnrichedRegeldateiModel(Schema):
    """Request schema for creating a job"""
    type = 'object'
    properties = {
        'rule_area_id': {
            'type': 'integer',
            'description': 'Identifier of area where Regeldatei is valid'
        },
        'rule_area': {
            'type': 'string',
            'description': 'Name of area where Regeldatei is valid'
        },
        'feature_type': {
            'type': 'string',
            'description': 'Name of feature type to run job with'
        },
        'feature_uuid': {
            'type': 'string',
            'description': 'Geonetwork UUID of feature type to run job with'
        },
        'feature_source': EnrichedProcInputBaseModel,
        'processing_platform': {
            'type': 'string',
            'description': 'The actinia-core platform, either "openshift" or "vm". If platform is "vm" and no actinia_core_url is given, actinia-gdi will create a new VM.'
        },
        'processing_platform_name': {
            'type': 'string',
            'description': 'The actinia-core platform name. Only used to match a job to a VM if VM not started by actinia-gdi. Ideally it would contain the job type (actinia-core-pt or actinia-core-oc) and a unique ID.'
        },
        'processing_host': {
            'type': 'string',
            'description': 'The actinia-core IP or URL in case the platform is not OpenShift and no new VM should be created by actinia-gdi'
        },
        'procs': {
            'type': 'array',
            'description': 'List of processes to run',
            'items': EnrichedProcModel
        },
        'geodata_meta': "string" # TODO: GeodataResponseModel
    }
    # TODO add example
    # example = jobs_post_docs_request_example
    required = ["feature_source", "procs"]


class ProcessesJobResponseModel(Schema):
    """Response schema for creating a job"""
    type = 'object'
    properties = {
        'idpk_jobs': {
            'type': 'integer',
            'description': 'The job ID'
        },
        'process': {
            'type': 'string',
            'description': 'The process of the job, e.g standortsicherung ' +
                           'or potentialtrenches'
        },
        'feature_type': {
            'type': 'string',
            'description': 'The feature type of the job'
        },
        'rule_configuration': RegeldateiModel,
        'job_description': EnrichedRegeldateiModel,
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
        'metadata': {
            'type': 'string',
            'description': 'Not specified yet'
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
        'actinia_core_response': {
            'type': 'object',
            'description': 'The Response of actinia-core at creation time'
        },
        'actinia_core_jobid': {
            'type': 'string',
            'description': 'The actinia-core resource ID for the job'
        },
        'actinia_core_platform': {
            'type': 'string',
            'description': 'The actinia-core platform, either "openshift" or "vm"'
        },
        'actinia_core_platform_name': {
            'type': 'string',
            'description': 'The actinia-core platform name'
        },
        'actinia_core_url': {
            'type': 'string',
            'description': 'The actinia-core IP or URL where actinia-core is processing the job'
        },
        'creation_uuid': {
            'type': 'string',
            'description': 'A unique id for the job at creation time before idpk_jobs is known. (More unique than creation timestamp)'
        },
        'terraformer_id': {
            'type': 'string',
            'description': 'The terraformer instances ID for the job'
        },
        'terraformer_response': {
            'type': 'string',
            'description': 'The Response/Status of terraformer'
        }
    }
    # TODO add example
    # example = jobs_post_docs_response_example


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
