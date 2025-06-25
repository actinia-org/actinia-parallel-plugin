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

Add endpoints to flask app with endpoint definitions and routes
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from flask_restful_swagger_2 import Resource

from actinia_parallel_plugin.api.batch import BatchJobsId
from actinia_parallel_plugin.api.job import JobId
# from actinia_parallel_plugin.api.parallel_processing import \
#     AsyncParallelPersistentResource
from actinia_parallel_plugin.api.parallel_ephemeral_processing import \
    AsyncParallelEphermeralResource
from actinia_parallel_plugin.core.jobtable import initJobDB, applyMigrations


def get_endpoint_class_name(
    endpoint_class: Resource,
    projects_url_part: str = "projects",
) -> str:
    """Create the name for the given endpoint class."""
    endpoint_class_name = endpoint_class.__name__.lower()
    if projects_url_part != "projects":
        name = f"{endpoint_class_name}_{projects_url_part}"
    else:
        name = endpoint_class_name
    return name


def create_project_endpoints(apidoc, projects_url_part="projects"):
    """
    Function to add resources with "projects" inside the endpoint url.
    Args:
        apidoc (flask_restful_swagger_2.Api): Flask api
        projects_url_part (str): The name of the projects inside the endpoint
                                 URL; to add deprecated location endpoints set
                                 it to "locations"
    """

    # POST parallel ephemeral processing
    apidoc.add_resource(
        AsyncParallelEphermeralResource,
        f"/{projects_url_part}/<string:project_name>/processing_parallel",
        endpoint=get_endpoint_class_name(
            AsyncParallelEphermeralResource, projects_url_part
        ),
    )

    # # POST parallel persistent processing
    # apidoc.add_resource(
    #     AsyncParallelPersistentResource,
    #     f"/{projects_url_part}/<string:project_name>/mapsets/"
    #     "<string:mapset_name>/processing_parallel",
    #     endpoint=get_endpoint_class_name(
    #         AsyncParallelPersistentResource, projects_url_part
    #     ),
    # )


# endpoints loaded if run as actinia-core plugin
def create_endpoints(flask_api):

    apidoc = flask_api

    # add deprecated location and project endpoints
    create_project_endpoints(apidoc)
    create_project_endpoints(apidoc, projects_url_part="locations")

    # GET batch jobs TODO
    # "/resources/<string:user_id>/batches"

    # GET batch jobs by ID
    apidoc.add_resource(
        BatchJobsId,
        "/resources/<string:user_id>/batches/<int:batchid>")

    # GET all jobs of one batch TODO
    # "/resources/<string:user_id>/batches/<int:batchid>/jobs"

    # GET job by ID
    apidoc.add_resource(
        JobId,
        "/resources/<string:user_id>/batches/<int:batchid>/jobs/<int:jobid>")

    # initilalize jobtable
    initJobDB()
    applyMigrations()
