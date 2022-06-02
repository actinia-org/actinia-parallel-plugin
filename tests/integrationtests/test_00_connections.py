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
import redis
import psycopg2

# from actinia_core.core.common.redis_base import RedisBaseInterface
from actinia_core.core.common.config import global_config as config

from actinia_parallel_plugin.resources.config import JOBTABLE

from ..test_resource_base import ActiniaResourceTestCaseBase#, URL_PREFIX


class ConnectionTest(ActiniaResourceTestCaseBase):

    @pytest.mark.integrationtest
    def test_redis_connection(self):
        """Test redis connection
        """
        if "ACTINIA_CUSTOM_TEST_CFG" in os.environ:
            config.read(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
        kwargs = dict()
        kwargs["host"] = config.REDIS_SERVER_URL
        kwargs["port"] = config.REDIS_SERVER_PORT
        if config.REDIS_SERVER_PW and config.REDIS_SERVER_PW is not None:
            kwargs["password"] = config.REDIS_SERVER_PW
        connection_pool = redis.ConnectionPool(**kwargs)
        redis_server = redis.StrictRedis(connection_pool=connection_pool)
        try:
            redis_server.ping()
            assert True
        except redis.exceptions.ResponseError:
            assert False, "Could not connect to redis ({kwargs['host']})"
        except redis.exceptions.AuthenticationError:
            assert False, "Invalid redis password"
        except redis.exceptions.ConnectionError as e:
            assert False, f"Redis connection error: {e}"
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
