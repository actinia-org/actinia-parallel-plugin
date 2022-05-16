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

Module to communicate with jobtable
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


from datetime import datetime

from playhouse.shortcuts import model_to_dict
from peewee import Expression, AutoField, OperationalError
from uuid import uuid4
from yoyo import read_migrations
from yoyo import get_backend

from actinia_parallel_plugin.model.jobtabelle import Job, jobdb
from actinia_parallel_plugin.resources.config import JOBTABLE
from actinia_parallel_plugin.resources.logging import log


# We used `jobdb.connect(reuse_if_open=True)` at the beginning
# of every method. Now we use `with jobdb:` as described in the
# peewee docs but we still try to jobdb.close() at the end of
# each method.

def initJobDB():
    """Create jobtable on startup."""
    Job.create_table(safe=True)
    log.debug('Created jobtable if not exists')


def applyMigrations():
    backend = get_backend(
        'postgres://%s:%s@%s/%s?schema=%s' %
        (JOBTABLE.user, JOBTABLE.pw, JOBTABLE.host, JOBTABLE.database,
         JOBTABLE.schema))
    migrations = read_migrations('actinia_parallel_plugin/resources/migrations')

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    log.debug('Applied migrations.')
