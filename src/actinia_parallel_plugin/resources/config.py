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

Configuration file
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import configparser
import os
# from pathlib import Path


# # config can be overwritten by mounting *.ini files into folders inside
# # the config folder.
# DEFAULT_CONFIG_PATH = "config"
# CONFIG_FILES = [str(f) for f in Path(
#     DEFAULT_CONFIG_PATH).glob('**/*.ini') if f.is_file()]
# GENERATED_CONFIG = DEFAULT_CONFIG_PATH + '/actinia-parallel-plugin.cfg'

DEFAULT_CONFIG_PATH = os.getenv('DEFAULT_CONFIG_PATH', "/etc/default/actinia")
GENERATED_CONFIG = os.path.join(
    os.path.dirname(DEFAULT_CONFIG_PATH), 'actinia-parallel-plugin.cfg')
if not os.path.isfile(DEFAULT_CONFIG_PATH):
    open(DEFAULT_CONFIG_PATH, 'a').close()
CONFIG_FILES = [DEFAULT_CONFIG_PATH]


class JOBTABLE:
    """Default config for database connection for jobtable
    """
    host = 'localhost'
    port = '5432'
    database = 'gis'
    user = 'gis'
    pw = 'gis'
    schema = 'actinia'
    table = 'tab_jobs'
    id_field = 'id'
    batch_id_field = "batch_id"
    resource_id_field = "resource_id"


class LOGCONFIG:
    """Default config for logging
    """
    logfile = 'actinia-gdi.log'
    level = 'DEBUG'
    type = 'stdout'


class Configfile:

    def __init__(self):
        """
        This class will overwrite the config classes above when config files
        named DEFAULT_CONFIG_PATH/**/*.ini exist.
        On first import of the module it is initialized.
        """

        config = configparser.ConfigParser()
        config.read(CONFIG_FILES)

        if len(config) <= 1:
            # print("Could not find any config file, using default values.")
            return

        with open(GENERATED_CONFIG, 'w') as configfile:
            config.write(configfile)

        # JOBTABLE
        if config.has_section("JOBTABLE"):
            if config.has_option("JOBTABLE", "host"):
                JOBTABLE.host = config.get("JOBTABLE", "host")
            if config.has_option("JOBTABLE", "port"):
                JOBTABLE.port = config.get("JOBTABLE", "port")
            if config.has_option("JOBTABLE", "database"):
                JOBTABLE.database = config.get("JOBTABLE", "database")
            if config.has_option("JOBTABLE", "user"):
                JOBTABLE.user = config.get("JOBTABLE", "user")
            if config.has_option("JOBTABLE", "pw"):
                JOBTABLE.pw = config.get("JOBTABLE", "pw")
            if config.has_option("JOBTABLE", "schema"):
                JOBTABLE.schema = config.get("JOBTABLE", "schema")
            if config.has_option("JOBTABLE", "table"):
                JOBTABLE.table = config.get("JOBTABLE", "table")
            if config.has_option("JOBTABLE", "id_field"):
                JOBTABLE.id_field = config.get("JOBTABLE", "id_field")

        # overwrite values if ENV values exist:
        if os.environ.get('JOBTABLE_USER'):
            JOBTABLE.user = os.environ['JOBTABLE_USER']
        if os.environ.get('JOBTABLE_PW'):
            JOBTABLE.pw = os.environ['JOBTABLE_PW']

        # LOGGING
        if config.has_section("LOGCONFIG"):
            if config.has_option("LOGCONFIG", "logfile"):
                LOGCONFIG.logfile = config.get("LOGCONFIG", "logfile")
            if config.has_option("LOGCONFIG", "level"):
                LOGCONFIG.level = config.get("LOGCONFIG", "level")
            if config.has_option("LOGCONFIG", "type"):
                LOGCONFIG.type = config.get("LOGCONFIG", "type")


init = Configfile()
