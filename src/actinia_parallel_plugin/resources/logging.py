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

The logger
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2018-2022 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH % Co. KG"

import logging
from datetime import datetime
from logging import FileHandler

from colorlog import ColoredFormatter
from pythonjsonlogger import json

from actinia_parallel_plugin.resources.config import LOGCONFIG


# Notice: do not call logging.warning (will create new logger for ever)
# logging.warning("called actinia_gdi logger after 1")

log = logging.getLogger('actinia-parallel-plugin')
werkzeugLog = logging.getLogger('werkzeug')
gunicornLog = logging.getLogger('gunicorn')


def setLogFormat(veto=None):
    logformat = ""
    if LOGCONFIG.type == 'json' and not veto:
        logformat = CustomJsonFormatter(
            '%(time) %(level) %(component) %(module)'
            '%(message) %(pathname) %(lineno)'
            '%(processName) %(threadName)'
        )
    else:
        logformat = ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)s.%(module)-'
            '10s -%(message)s [in %(pathname)s:%(lineno)d]%(reset)s'
        )
    return logformat


def setLogHandler(logger, type, format):
    if type == 'stdout':
        handler = logging.StreamHandler()
    elif type == 'file':
        # For readability, json is never written to file
        handler = FileHandler(LOGCONFIG.logfile)

    handler.setFormatter(format)
    logger.addHandler(handler)


class CustomJsonFormatter(json.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(
            log_record, record, message_dict)

        # (Pdb) dir(record)
        # ... 'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName'
        # ,'getMessage', 'levelname', 'levelno', 'lineno', 'message', 'module',
        # 'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
        # 'relativeCreated', 'stack_info', 'thread', 'threadName']

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['time'] = now
        log_record['level'] = record.levelname
        log_record['component'] = record.name


def createLogger():
    # create logger, set level and define format
    log.setLevel(getattr(logging, LOGCONFIG.level))
    fileformat = setLogFormat('veto')
    stdoutformat = setLogFormat()
    setLogHandler(log, 'file', fileformat)
    setLogHandler(log, 'stdout', stdoutformat)


def createWerkzeugLogger():
    werkzeugLog.setLevel(getattr(logging, LOGCONFIG.level))
    fileformat = setLogFormat('veto')
    stdoutformat = setLogFormat()
    setLogHandler(werkzeugLog, 'file', fileformat)
    setLogHandler(werkzeugLog, 'stdout', stdoutformat)


def createGunicornLogger():
    gunicornLog.setLevel(getattr(logging, LOGCONFIG.level))
    fileformat = setLogFormat('veto')
    stdoutformat = setLogFormat()
    setLogHandler(gunicornLog, 'file', fileformat)
    setLogHandler(gunicornLog, 'stdout', stdoutformat)
    # gunicorn already has a lot of children logger, e.g gunicorn.http,
    # gunicorn.access. These lines deactivate their default handlers.
    for name in logging.root.manager.loggerDict:
        if "gunicorn." in name:
            logging.getLogger(name).propagate = True
            logging.getLogger(name).handlers = []


createLogger()
createWerkzeugLogger()
createGunicornLogger()
