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

Model classes for regeldatei
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

# import os
# import json

from flask_restful_swagger_2 import Schema

# script_dir = os.path.dirname(os.path.abspath(__file__))
# null = "null"
#
# rel_path = ("../apidocs/examples/" +
#             "standortsicherung_jobs_post_request_example.json")
# abs_file_path = os.path.join(script_dir, rel_path)
# with open(abs_file_path) as jsonfile:
#     sos_jobs_post_docs_request_example = json.load(jsonfile)
#
# rel_path = ("../apidocs/examples/" +
#             "pt_jobs_post_request_example.json")
# abs_file_path = os.path.join(script_dir, rel_path)
# with open(abs_file_path) as jsonfile:
#     pt_jobs_post_docs_request_example = json.load(jsonfile)


class ProcessesProcInputBaseModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
            'description': 'Name of input data'
        },
        'type': {
            'type': 'string',
            'enum': ["GNOS", "DATABASE", "PARAMETER", "STATUS"],
            'description': 'Type of input. Can be "GNOS", "DATABASE", '
                           '"PARAMETER" or "STATUS"'
        }
    }


class ProcessesFilterModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
            'description': 'Not yet implemented or specified'
        },
        # 'metadata_field': {
        #     'type': 'string',
        #     'description': 'Not yet implemented or specified'
        # },
        # 'metadata_value': {
        #     'type': 'string',
        #     'description': 'Not yet implemented or specified'
        # },
        'operator': {
            'type': 'string',
            'description': 'Not yet implemented or specified'
        }
    }


class ProcessesProcInputDatabaseModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        ProcessesProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        },
        {
            'type': 'object',
            'properties': {
                'table': {
                    'type': 'string',
                    'description': 'Database connection string with table'
                },
                'attributes': {
                    'type': 'array',
                    'description': 'Database attribute of data source to use',
                    'items': {
                        'type': 'string'
                    }
                },
                'filter': {
                    'type': 'array',
                    'description': 'Not yet implemented or specified',
                    'items': ProcessesFilterModel
                }
            }
        }
    ]


class ProcessesProcInputParameterModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        ProcessesProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        },
        {
            'type': 'object',
            'properties': {
                'value': {
                    'type': 'array',
                    'description': 'Array of input parameter. Can be int, '
                                   'float or string',
                    'items': {
                        # TODO: find out how to allow multiple types
                        # 'type': 'int, float, string'
                    }
                },
                'uom': {
                    'type': 'string',
                    'description': 'Unit of measurement for values'
                }
            }
        }
    ]


class ProcessesProcInputFileModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        ProcessesProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        },
        {
            'type': 'object',
            'properties': {
                'value': {
                    'type': 'array',
                    'description': 'Array of input parameter. Can be int, '
                                   'float or string',
                    'items': {
                        # TODO: find out how to allow multiple types
                        # 'type': 'int, float, string'
                    }
                }
            }
        }
    ]


class ProcessesProcInputStatusModel(Schema):
    """Request schema for creating a job"""
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        ProcessesProcInputBaseModel,
        {
            '$ref': '#/definitions/ProcessesProcInputBaseModel'
        },
        {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'description': 'Status of another process as input. See '
                                   'also "dependsOn"'
                }
            }
        }
    ]


class ProcessesProcInputModel(Schema):
    """Definitions for process input data"""
    type = 'object'
    # TODO: use oneOf (was not parsed in petstore)
    allOf = [
        # keep this line, otherwise BaseModel does not exist in document
        ProcessesProcInputDatabaseModel,
        ProcessesProcInputParameterModel,
        ProcessesProcInputFileModel,
        ProcessesProcInputStatusModel,
        {
            '$ref': '#/definitions/ProcessesProcInputDatabaseModel'
        },
        {
            '$ref': '#/definitions/ProcessesProcInputParameterModel'
        },
        {
            '$ref': '#/definitions/ProcessesProcInputFileModel'
        },
        {
            '$ref': '#/definitions/ProcessesProcInputStatusModel'
        }
    ]


class ProcessesProcOutputModel(Schema):
    """Definitions for process output data"""
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
            'description': 'Name of attribute column in output datasource'
        },
        'type': {
            'type': 'string',
            'description': 'Column type of attribut column'
        },
        'default': {
            'type': 'string',
            'description': 'Default value of attribut column'
        },
        'value': {
            'type': 'string',
            'description': 'Filename if output is file'
        }
    }


class ProcessesProcModel(Schema):
    """List of processes to run"""
    type = 'object'
    properties = {
        'name': {
            'type': 'integer',
            'description': 'Name of process'
        },
        'input': {
            'type': 'array',
            'description': 'Definitions for process input data',
            'items': ProcessesProcInputModel
        },
        'output': {
            'type': 'array',
            'description': 'Definitions for process output data',
            'items': ProcessesProcOutputModel
        },
        'dependsOn': {
            'type': 'string',
            'description': 'List of names of processes on which this process'
                           ' depends on. See also "status" as input parameter'
        }
    }
