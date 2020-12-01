# -*- coding: utf-8 -*-

# Copyright (c) 2020, Jason Godden <jason@godden.id.au>
# Copyright (c) 2020, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


log = logging.getLogger()


class EruptrException(Exception):
    """
    Base class for all Eruptr exceptions
    """

class EruptrModuleArgumentError(EruptrException):
    """
    Raised when arguments passed to modules are invalid or cannot be determined
    """

class EruptrPythonException(EruptrException):
    """
    Raised when a block of python code cannot be loaded or instantiated
    """

class EruptrNotImplementedException(EruptrException):
    """
    Raised when a method in an object hierarchy is not implemented
    """

class EruptrSQLException(EruptrException):
    """
    Raised when an SQL exception occurs
    """

class EruptrConfigException(EruptrException):
    """
    Raised when an error occurs during configuraton processing
    """