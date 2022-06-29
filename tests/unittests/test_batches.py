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

Unit tests for core functionallity of batches
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import pytest
import datetime
from actinia_parallel_plugin.core.batches import checkProcessingBlockFinished


baseurl = "http://localhost:8088/api/v3"
resource_id1 = "resource_id-a6da5e00-d2a3-4804-b82f-e03f92ab1cd4"
resource_id2 = "resource_id-291e8428-ec86-40a6-9ed2-ef1e14357aff"
jobs = [
    {
        "idpk_jobs": 7,
        "process": "ephemeral",
        "rule_configuration": {
            "list": [{"..."}],
            "version": "1",
            "batch_id": 2,
            "parallel": "true",
            "processing_block": 2,
            "batch_description": {
                "jobs": [
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                ]
            },
        },
        "time_created": datetime.datetime(2022, 6, 2, 7, 20, 14, 930771),
        "time_started": None,
        "time_estimated": None,
        "time_ended": None,
        "status": "PREPARING",
        "actinia_core_response": None,
        "actinia_core_jobid": None,
        "terraformer_id": None,
        "terraformer_response": None,
        "creation_uuid": "81eae975-62c1-46f1-97d3-e027834a11b8",
        "message": None,
        "batch_id": 2,
        "processing_block": 2,
        "batch_description": {
            "jobs": [
                {"list": [{"..."}], "version": "1", "parallel": "false"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "false"},
            ]
        },
    },
    {
        "idpk_jobs": 8,
        "process": "ephemeral",
        "rule_configuration": {
            "list": [{"..."}],
            "version": "1",
            "batch_id": 2,
            "parallel": "false",
            "processing_block": 3,
            "batch_description": {
                "jobs": [
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                ]
            },
        },
        "time_created": datetime.datetime(2022, 6, 2, 7, 20, 14, 940472),
        "time_started": None,
        "time_estimated": None,
        "time_ended": None,
        "status": "PREPARING",
        "actinia_core_response": None,
        "actinia_core_jobid": None,
        "terraformer_id": None,
        "terraformer_response": None,
        "creation_uuid": "a4be1541-70cc-42ac-b134-c17f0ea8d311",
        "message": None,
        "batch_id": 2,
        "processing_block": 3,
        "batch_description": {
            "jobs": [
                {"list": [{"..."}], "version": "1", "parallel": "false"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "false"},
            ]
        },
    },
    {
        "idpk_jobs": 5,
        "process": "ephemeral",
        "rule_configuration": {
            "list": [{"..."}],
            "version": "1",
            "batch_id": 2,
            "parallel": "false",
            "processing_block": 1,
            "batch_description": {
                "jobs": [
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                ]
            },
        },
        "time_created": datetime.datetime(2022, 6, 2, 7, 20, 14, 906827),
        "time_started": None,
        "time_estimated": None,
        "time_ended": datetime.datetime(2022, 6, 2, 7, 20, 15),
        "status": "SUCCESS",
        "actinia_core_response": {
            "urls": {
                "status": f"{baseurl}/resources/actinia-gdi/{resource_id2}",
                "resources": [],
            },
            "status": "finished",
            "message": "Processing successfully finished",
            "user_id": "actinia-gdi",
            "api_info": {
                "path": "/api/v3/locations/nc_spm_08_grass7_root/"
                        "processing_parallel",
                "method": "POST",
                "endpoint": "asyncparallelephermeralresource",
                "post_url": f"{baseurl}/locations/nc_spm_08_grass7_root/"
                            "processing_parallel",
                "request_url": f"{baseurl}/locations/nc_spm_08_grass7_root/"
                               "processing_parallel",
            },
            "datetime": "2022-06-02 07:20:15.942998",
            "progress": {"step": 2, "num_of_steps": 2},
            "http_code": 200,
            "timestamp": 1654154415.9429944,
            "time_delta": 0.9949047565460205,
            "process_log": [{"..."}],
            "resource_id": resource_id2,
            "accept_datetime": "2022-06-02 07:20:14.948113",
            "process_results": {},
            "accept_timestamp": 1654154414.9481106,
            "process_chain_list": [
                {
                    "list": [{"..."}],
                    "version": "1",
                }
            ],
        },
        "actinia_core_jobid": resource_id2,
        "terraformer_id": None,
        "terraformer_response": None,
        "creation_uuid": "767596e2-a9e4-4e96-b05b-4d77ae304a54",
        "message": None,
        "batch_id": 2,
        "processing_block": 1,
        "batch_description": {
            "jobs": [
                {"list": [{"..."}], "version": "1", "parallel": "false"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "false"},
            ]
        },
    },
    {
        "idpk_jobs": 6,
        "process": "ephemeral",
        "rule_configuration": {
            "list": [{"..."}],
            "version": "1",
            "batch_id": 2,
            "parallel": "true",
            "processing_block": 2,
            "batch_description": {
                "jobs": [
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "true"},
                    {"list": [{"..."}], "version": "1", "parallel": "false"},
                ]
            },
        },
        "time_created": datetime.datetime(2022, 6, 2, 7, 20, 14, 920875),
        "time_started": None,
        "time_estimated": None,
        "time_ended": datetime.datetime(2022, 6, 2, 7, 20, 49),
        "status": "SUCCESS",
        "actinia_core_response": {
            "urls": {
                "status": f"{baseurl}/resources/actinia-gdi/{resource_id1}",
                "resources": [],
            },
            "status": "finished",
            "message": "Processing successfully finished",
            "user_id": "actinia-gdi",
            "api_info": {
                "path": "/api/v3/locations/nc_spm_08_grass7_root/"
                        "processing_parallel",
                "method": "POST",
                "endpoint": "asyncparallelephermeralresource",
                "post_url": f"{baseurl}/locations/nc_spm_08_grass7_root/"
                            "processing_parallel",
                "request_url": f"{baseurl}/locations/nc_spm_08_grass7_root/"
                               "processing_parallel",
            },
            "datetime": "2022-06-02 07:20:49.262223",
            "progress": {"step": 2, "num_of_steps": 2},
            "http_code": 200,
            "timestamp": 1654154449.2622168,
            "time_delta": 0.4729771614074707,
            "process_log": [{"..."}],
            "resource_id": resource_id1,
            "accept_datetime": "2022-06-02 07:20:48.789271",
            "process_results": {},
            "accept_timestamp": 1654154448.7892694,
            "process_chain_list": [
                {
                    "list": [{"..."}],
                    "version": "1",
                }
            ],
        },
        "actinia_core_jobid": resource_id1,
        "terraformer_id": None,
        "terraformer_response": None,
        "creation_uuid": "d08c1bbb-72f4-482f-bc78-672756937efa",
        "message": None,
        "batch_id": 2,
        "processing_block": 2,
        "batch_description": {
            "jobs": [
                {"list": [{"..."}], "version": "1", "parallel": "false"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "true"},
                {"list": [{"..."}], "version": "1", "parallel": "false"},
            ]
        },
    },
]
block = [1, 2, 3]
ref_out = [True, False, False]


@pytest.mark.unittest
@pytest.mark.parametrize(
    "block,ref_out",
    [(block[0], ref_out[0]), (block[1], ref_out[1]), (block[2], ref_out[2])],
)
def test_checkProcessingBlockFinished(block, ref_out):
    """Test for checkProcessingBlockFinished function."""

    out = checkProcessingBlockFinished(jobs, block)
    assert (
        out is ref_out
    ), f"Wrong result from transform_input for block {block}"
