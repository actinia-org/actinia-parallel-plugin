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

Model class for batch
"""

__license__ = "GPLv3"
__author__ = "Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import os
import json
from flask_restful_swagger_2 import Schema

from actinia_core.models.process_chain import ProcessChainModel
from actinia_core.models.response_models import UrlModel

script_dir = os.path.dirname(os.path.abspath(__file__))

rel_path = "../apidocs/examples/batchjob_post_response_example.json"
abs_file_path = os.path.join(script_dir, rel_path)
print(abs_file_path)
with open(abs_file_path) as jsonfile:
    batchjob_post_docs_response_example = json.load(jsonfile)


class BatchJobsSummaryModel(Schema):
    """Schema for a batchjob response summary"""
    type = 'object'
    properties = {
        'blocks': {
            'type': 'array',
            'description': 'Status summary for each processing blocks',
            'items': {
                'block_num': {
                    'type': 'integer',
                    'description': 'Number of processing block'
                    },
                'parallel': {
                    'type': 'integer',
                    'description': ('Number of parallel jobs within '
                                    'processing block')
                    },
                'accepted': {
                    'type': 'integer',
                    'description': ('Number of jobs with actinia-core status '
                                    '"ACCEPTED" within block')
                    },
                'error': {
                    'type': 'integer',
                    'description': ('Number of jobs with actinia-core status '
                                    '"ERROR" within block')
                    },
                'finished': {
                    'type': 'integer',
                    'description': ('Number of jobs with actinia-core status '
                                    '"FINISHED" within block')
                    },
                'preparing': {
                    'type': 'integer',
                    'description': ('Number of jobs with status '
                                    '"PREPARING" within block (jobs that '
                                    'exist in the jobtable but have not yet '
                                    'been posted to actinia-core)')
                    },
                'running': {
                    'type': 'integer',
                    'description': ('Number of jobs with actinia-core status '
                                    '"RUNNING" within block')
                    },
                'terminated': {
                    'type': 'integer',
                    'description': ('Number of jobs with actinia-core status '
                                    '"TERMINATED" within block')
                    },
                }
            },
        'status': {
            'type': 'array',
            'description': 'Status summary for all jobs',
            'items': {
                'accepted': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'actinia-core status "ACCEPTED"')
                    },
                'error': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'actinia-core status "ERROR"')
                    },
                'finished': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'actinia-core status "FINISHED"')
                    },
                'preparing': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'status "PREPARING" (jobs that '
                                    'exist in the jobtable but have not yet '
                                    'been posted to actinia-core)')
                    },
                'running': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'actinia-core status "RUNNING"')
                    },
                'terminated': {
                    'type': 'integer',
                    'description': ('Overall number  of jobs with '
                                    'actinia-core status "TERMINATED"')
                    },
                }
            },
        'total': {
            'type': 'integer',
            'description': 'Overall number of jobs within batchjob'
            }
        }


class BatchProcessChainModel(Schema):
    """Definition of the actinia-gdi batch process chain that includes several
       actinia process chains that can be run in parallel or sequentially
    """
    type = 'object'
    properties = {
        'jobs': {
            'type': 'array',
            'items': ProcessChainModel,
            'description': "A list of process chains (jobs) that should "
                           "be executed in parallel or sequentially "
                           "in the order provided by the list."
        }
    }
    required = ["jobs"]


class BatchJobResponseModel(Schema):
    """Response schema for creating and requesting the status of a Batchjob
    """
    type = 'object'
    properties = {
        'resource_id': {
            'type': 'array',
            'description': ('The resource IDs for all individual '
                            'jobs'),
            'items': {'type': 'string'}
        },
        'resource_response': {
            'type': 'array',
            'description': 'The responses of actinia-core for individual jobs',
            'items': {'type': 'object'}
        },
        'batch_id': {
            'type': 'integer',
            'description': 'The batch ID'
        },
        'creation_uuid': {
            'type': 'array',
            'description': ('Unique ids for the individual jobs at creation '
                            'time before id is known. '
                            '(More unique than creation timestamp)'),
            'items': {'type': 'string'}
        },
        'id': {
            'type': 'array',
            'description': 'The individual job IDs',
            'items': {'type': 'integer'}
        },
        'status': {
            'type': 'string',
            'description': 'The overall status of the batchjob',
            'enum': [
                "PREPARING",
                "PENDING",
                "RUNNING",
                "SUCCESS",
                "ERROR",
                "TERMINATING",
                "TERMINATED"]
        },
        'jobs_status': {
            'type': 'array',
            'description': ('Status of the individual Jobs by actinia-core '
                            'resource ID and job ID'),
            'items': {
                'actinia_core_job_id': {
                    'type': 'string',
                    'description': 'The actinia-core resource ID for the job'
                        },
                'id': {
                    'type': 'integer',
                    'description': 'The job ID'
                        },
                'status': {
                    'type': 'string',
                    'description': 'Status of the Job',
                    'enum': [
                        "PREPARING",
                        "PENDING",
                        "RUNNING",
                        "SUCCESS",
                        "ERROR",
                        "TERMINATED"
                        ]
                    }
                }
        },
        'summary': BatchJobsSummaryModel,
        'urls': UrlModel
    }
    example = batchjob_post_docs_response_example
