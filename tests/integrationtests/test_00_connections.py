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

import os
import pytest
import valkey
import psycopg2

from actinia_core.core.common.config import global_config as config

from actinia_parallel_plugin.resources.config import JOBTABLE

from ..test_resource_base import ActiniaResourceTestCaseBase


class ConnectionTest(ActiniaResourceTestCaseBase):

    @pytest.mark.integrationtest
    def test_kvdb_connection(self):
        """Test kvdb connection
        """
        if "ACTINIA_CUSTOM_TEST_CFG" in os.environ:
            config.read(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
        kwargs = dict()
        kwargs["host"] = config.KVDB_SERVER_URL
        kwargs["port"] = config.KVDB_SERVER_PORT
        if config.KVDB_SERVER_PW and config.KVDB_SERVER_PW is not None:
            kwargs["password"] = config.KVDB_SERVER_PW
        connection_pool = valkey.ConnectionPool(**kwargs)
        kvdb_server = valkey.StrictValkey(connection_pool=connection_pool)
        try:
            kvdb_server.ping()
            assert True
        except valkey.exceptions.ResponseError:
            assert False, "Could not connect to kvdb ({kwargs['host']})"
        except valkey.exceptions.AuthenticationError:
            assert False, "Invalid kvdb password"
        except valkey.exceptions.ConnectionError as e:
            assert False, f"Kvdb connection error: {e}"
        connection_pool.disconnect()

    @pytest.mark.integrationtest
    def test_postgis_connection(self):
        """Test postgis connection
        """
        try:
            conn = psycopg2.connect(**{
                'host': JOBTABLE.host,
                'port': JOBTABLE.port,
                'user': JOBTABLE.user,
                'password': JOBTABLE.pw
            })
            assert True
            conn.close()
        except Exception:
            assert False, "Postgis connection failed!"
