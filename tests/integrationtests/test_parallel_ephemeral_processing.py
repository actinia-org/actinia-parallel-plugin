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

Parallel ephemeral processing tests
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


import json
import pytest
from flask import Response

from ..test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

PC = """{
  "jobs": [
    {
      "list": [
        {
          "module": "g.region",
          "id": "g_region_nonparallel_block1",
          "inputs":[
            {"param": "raster", "value": "elevation@PERMANENT"}
          ]
        },
        {
          "module": "r.mapcalc",
          "id": "r_mapcalc_0_nonparallel_block1",
          "inputs":[
            {"param": "expression", "value": "baum = elevation@PERMANENT * 2"}
          ]
        }
      ],
      "parallel": "false",
      "version": "1"
    },
    {
      "list": [
        {
          "module": "g.region",
          "id": "g_region_1_parallel_block2",
          "inputs":[
            {"param": "raster", "value": "elevation@PERMANENT"}
          ],
          "flags": "p"
        },
        {
          "module": "r.info",
          "id": "r_info_1_parallel_block2",
          "inputs":[
            {"param": "map", "value": "elevation@PERMANENT"}
          ]
        }
      ],
      "parallel": "true",
      "version": "1"
    },
    {
      "list": [
        {
          "module": "g.region",
          "id": "g_region_2_parallel_block2",
          "inputs":[
            {
              "import_descr":
                {
                  "source": "https://apps.mundialis.de/actinia_test_datasets/elev_ned_30m.tif",
                  "type": "raster"
                },
                "param": "raster",
                "value": "elev_ned_30m"
            }
          ],
          "flags": "p"
        },
        {
          "module": "r.univar",
          "id": "r_univar_2_parallel_block2",
          "inputs":[
            {"param": "map", "value": "elev_ned_30m"}
          ],
          "stdout": {"id": "stats", "format": "kv", "delimiter": "="},
          "flags": "g"
        }
      ],
      "parallel": "true",
      "version": "1"
    },
    {
      "list": [
        {
          "module": "g.region",
          "id": "g_region_nonparallel_block3",
          "inputs":[
            {"param": "raster", "value": "elevation@PERMANENT"}
          ],
          "flags": "p"
        }
      ],
      "parallel": "false",
      "version": "1"
    }
  ]
}
"""


class ActiniaParallelProcessingTest(ActiniaResourceTestCaseBase):

    location = "nc_spm_08"
    base_url = f"{URL_PREFIX}/locations/{location}"
    content_type = "application/json"

    @pytest.mark.integrationtest
    def test_post_parallel_ephemeral_processing(self):
        """Test the post method of the parallel ephemeral processing endpoint
        """
        url = f"{self.base_url}/processing_parallel"

        rv = self.server.post(
            url,
            headers=self.user_auth_header,
            content_type=self.content_type,
            data=PC,
        )
        import pdb; pdb.set_trace()
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=200,
            status="finished",
        )
        assert "process_results" in resp, "No 'process_results' in response"
        assert resp["process_results"] == ["grid1", "grid2", "grid3", "grid4"]
