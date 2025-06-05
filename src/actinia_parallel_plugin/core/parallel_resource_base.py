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

Parallel processing
"""

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import time
import os
from datetime import datetime

from flask_restful_swagger_2 import Resource

from actinia_core.core.common.config import global_config
from actinia_core.core.messages_logger import MessageLogger
from actinia_core.core.resources_logger import ResourceLogger
from actinia_rest_lib.resource_base import ResourceBase
from actinia_core.models.response_models import (
    create_response_from_model,
    ApiInfoModel,
    ProcessingResponseModel,
)
from actinia_core.core.resource_data_container import ResourceDataContainer


class ParallelResourceBase(ResourceBase):
    """This is the base class for all asynchronous and synchronous processing
    resources.
    """

    def __init__(self, user, request_url, endpoint, method, path,
                 base_status_url,
                 resource_id=None, iteration=None, post_url=None):
        # Configuration
        Resource.__init__(self)

        # Store the user id, user group and all credentials of the current user
        self.user = user
        self.user_id = user.get_id()
        self.user_group = user.get_group()
        self.user_role = user.get_role()
        self.has_superadmin_role = user.has_superadmin_role()
        self.user_credentials = user.get_credentials()

        self.orig_time = time.time()
        self.orig_datetime = str(datetime.now())

        kwargs = dict()
        kwargs['host'] = global_config.KVDB_SERVER_URL
        kwargs['port'] = global_config.KVDB_SERVER_PORT
        if (global_config.KVDB_SERVER_PW and
                global_config.KVDB_SERVER_PW is not None):
            kwargs['password'] = global_config.KVDB_SERVER_PW
        self.resource_logger = ResourceLogger(**kwargs)
        del kwargs

        self.message_logger = MessageLogger()

        self.grass_data_base = global_config.GRASS_DATABASE
        self.grass_user_data_base = global_config.GRASS_USER_DATABASE
        self.grass_base_dir = global_config.GRASS_GIS_BASE
        self.grass_start_script = global_config.GRASS_GIS_START_SCRIPT
        self.grass_addon_path = global_config.GRASS_ADDON_PATH
        self.download_cache = os.path.join(
            global_config.DOWNLOAD_CACHE, self.user_id)

        # Set the resource id
        if resource_id is None:
            # Generate the resource id
            self.request_id, self.resource_id = self.generate_uuids()
        else:
            self.resource_id = resource_id
            self.request_id = self.generate_request_id_from_resource_id()

        # set iteration and post_url
        self.iteration = iteration
        self.post_url = post_url

        # The base URL's for resources that will be streamed
        self.resource_url_base = None

        # Generate the status URL
        self.status_url = f"{base_status_url}{self.resource_id}"

        if (global_config.FORCE_HTTPS_URLS is True
                and "http://" in self.status_url):
            self.status_url = self.status_url.replace("http://", "https://")

        self.request_url = request_url
        self.resource_url = None
        self.request_data = None
        self.response_data = None
        self.job_timeout = 0

        # Replace this with the correct response model in subclasses
        # The class that is used to create the response
        self.response_model_class = ProcessingResponseModel

        # Put API information in the response for later accounting
        kwargs = {
            'endpoint': endpoint,
            'method': method,
            'path': path,
            'request_url': self.request_url}
        if self.post_url is not None:
            kwargs['post_url'] = self.post_url
        self.api_info = ApiInfoModel(**kwargs)

    def preprocess(self, has_json=True, has_xml=False,
                   project_name=None, mapset_name=None, map_name=None):
        """Preprocessing steps for asynchronous processing

            - Check if the request has a data field
            - Check if the module chain description can be loaded
            - Initialize the response and request ids as well as the
              url for status polls
            - Send an accept entry to the resource kvdb database

        Args:
            has_json (bool): Set True if the request has JSON data, False
                             otherwise
            has_xml (bool): Set True if the request has XML data, False
                            otherwise
            project_name (str): The name of the project to work in
            mapset_name (str): The name of the target mapset in which the
                               computation should be performed
            map_name: The name of the map or other resource (raster, vector,
                      STRDS, color, ...)

        Returns:
            The ResourceDataContainer that contains all required information
            for the async process or None if the request was wrong. Then use
            the self.response_data variable to send a response.

        """

        # Compute the job timeout of the worker queue from the user credentials
        process_time_limit = self.user_credentials["permissions"][
            "process_time_limit"]
        process_num_limit = self.user_credentials["permissions"][
            "process_num_limit"]
        self.job_timeout = int(process_time_limit * process_num_limit * 20)

        # Create the resource URL base and use a placeholder for the file name
        # The placeholder __None__ must be replaced by the resource URL
        # generator
        self.resource_url_base = f"{self.status_url}/__None__"

        if (global_config.FORCE_HTTPS_URLS is True
                and "http://" in self.resource_url_base):
            self.resource_url_base = self.resource_url_base.replace(
                "http://", "https://")

        # Create the accepted response that will be always send
        self.response_data = create_response_from_model(
            self.response_model_class,
            status="accepted",
            user_id=self.user_id,
            resource_id=self.resource_id,
            iteration=self.iteration,
            process_log=None,
            results={},
            message="Resource accepted",
            http_code=200,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            status_url=self.status_url,
            api_info=self.api_info)

        # Send the status to the database
        self.resource_logger.commit(
            self.user_id, self.resource_id, self.iteration, self.response_data)

        # Return the ResourceDataContainer that includes all
        # required data for the asynchronous processing
        return ResourceDataContainer(
            grass_data_base=self.grass_data_base,
            grass_user_data_base=self.grass_user_data_base,
            grass_base_dir=self.grass_base_dir,
            request_data=self.request_data,
            user_id=self.user_id,
            user_group=self.user_group,
            user_credentials=self.user_credentials,
            resource_id=self.resource_id,
            iteration=self.iteration,
            status_url=self.status_url,
            api_info=self.api_info,
            resource_url_base=self.resource_url_base,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            config=global_config,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=map_name
        )
