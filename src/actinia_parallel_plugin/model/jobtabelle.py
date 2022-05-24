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

Response models
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

from peewee import Model, CharField, DateTimeField, AutoField, IntegerField
from playhouse.postgres_ext import BinaryJSONField
from playhouse.pool import PooledPostgresqlExtDatabase

from actinia_parallel_plugin.resources.config import JOBTABLE
from actinia_parallel_plugin.resources.logging import log


log.debug("Database config loaded: " + JOBTABLE.host + ":" + JOBTABLE.port +
          "/" + JOBTABLE.database + "/" +
          JOBTABLE.schema + "." + JOBTABLE.table)


"""database connection"""

jobdb = PooledPostgresqlExtDatabase(
    JOBTABLE.database, **{
        'host': JOBTABLE.host,
        'port': JOBTABLE.port,
        'user': JOBTABLE.user,
        'password': JOBTABLE.pw,
        'max_connections': 8,
        'stale_timeout': 300
    }
)


class BaseModel(Model):
    """Base Model for tables in jobdb
    """
    class Meta:
        database = jobdb


class Job(BaseModel):
    """Model for jobtable in database
    """
    idpk_jobs = AutoField()
    process = CharField(null=True)
    # feature_type = CharField(null=True)
    rule_configuration = BinaryJSONField(null=True)
    job_description = BinaryJSONField(null=True)
    time_created = DateTimeField(null=True)
    time_started = DateTimeField(null=True)
    time_estimated = DateTimeField(null=True)
    time_ended = DateTimeField(null=True)
    # metadata = CharField(null=True)
    status = CharField(null=True)
    actinia_core_response = BinaryJSONField(null=True)
    actinia_core_jobid = CharField(null=True)
    actinia_core_url = CharField(null=True)
    actinia_core_platform = CharField(null=True)
    actinia_core_platform_name = CharField(null=True)
    terraformer_id = IntegerField(null=True)
    terraformer_response = BinaryJSONField(null=True)
    creation_uuid = CharField(null=True)
    message = CharField(null=True)
    # add a potential parent_job
    batch_id = IntegerField(null=True)
    processing_block = IntegerField(null=True)
    batch_description = BinaryJSONField(null=True)

    class Meta:
        table_name = JOBTABLE.table
        schema = JOBTABLE.schema
