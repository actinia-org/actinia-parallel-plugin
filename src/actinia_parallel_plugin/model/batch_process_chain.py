#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021-2022 mundialis GmbH & Co. KG

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

Model classes for Batch Process Chain
"""

__license__ = "GPLv3"
__author__ = "Julia Haas, Guido Riembauer"
__copyright__ = "Copyright 2021-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"


from jsonmodels import models, fields


class ModuleStdOut(models.Base):
    """Model for object in BatchProcessChain

    Model for optional stdout in module
    """
    id = fields.StringField(required=True)
    format = fields.StringField(required=True)
    delimiter = fields.StringField(required=True)


class ModuleExport(models.Base):
    """Model for object in BatchProcessChain

    Model for optional export in output
    """
    format = fields.StringField()
    type = fields.StringField()


class ModuleOutput(models.Base):
    """Model for object in BatchProcessChain

    Model for each output in module outputs array
    """
    param = fields.StringField()
    value = fields.StringField()
    export = fields.EmbeddedField(ModuleExport)


class ModuleInput(models.Base):
    """Model for object in BatchProcessChain

    Model for each input in module inputs array
    """
    param = fields.StringField(required=True)
    value = fields.StringField(required=True)


class Module(models.Base):
    """Model for object in BatchProcessChain

    Model for each module in module list array
    """
    module = fields.StringField(required=True)  # string
    id = fields.StringField(required=True)  # string
    inputs = fields.ListField([ModuleInput])  # array of objects
    flags = fields.StringField()  # string
    stdout = fields.EmbeddedField(ModuleStdOut)  # string
    outputs = fields.ListField([ModuleOutput])


class Job(models.Base):
    """Model for object in BatchProcessChain

    Model for each job in jobs array
    """
    version = fields.StringField()  # string
    parallel = fields.StringField(required=True)  # bool
    list = fields.ListField([Module], required=True)  # array of objects
    # the block and batch id is not in the json but is filled later
    batch_processing_block = fields.IntField()
    batch_id = fields.IntField()


class BatchProcessChain(models.Base):
    """Model for BatchProcessChain
    Including all information for all jobs
    This is used by the parallel processing endpoints
    """

    # processing_platform = fields.StringField()  # string
    # processing_platform_name = fields.StringField()  # string
    # processing_host = fields.StringField()  # string
    jobs = fields.ListField([Job], required=True)  # array of objects
