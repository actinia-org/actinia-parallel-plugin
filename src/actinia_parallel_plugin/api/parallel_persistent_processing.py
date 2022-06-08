#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018-present mundialis GmbH & Co. KG

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

Parallel persistent processing
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from flask_restful_swagger_2 import swagger

from actinia_core.core.common.app import auth
from actinia_core.core.common.config import global_config
from actinia_core.rest.base.user_auth import create_dummy_user

from actinia_parallel_plugin.api.parallel_ephemeral_processing import \
    AsyncParallelEphermeralResource
from actinia_parallel_plugin.apidocs import batch


class AsyncParallelPersistentResource(AsyncParallelEphermeralResource):
    """Resource for parallel persistent processing"""

    decorators = []

    # if global_config.LOG_API_CALL is True:
    #     decorators.append(log_api_call)
    #
    # if global_config.CHECK_CREDENTIALS is True:
    #     decorators.append(check_user_permissions)

    if global_config.LOGIN_REQUIRED is True:
        decorators.append(auth.login_required)
    else:
        decorators.append(create_dummy_user)

    @swagger.doc(batch.batchjobs_post_docs)
    def post(self, location_name, mapset_name):
        """Persistent parallel processing."""

        self.mapset_name = mapset_name
        self.type = "persistent"
        super(AsyncParallelPersistentResource, self).post(location_name)
