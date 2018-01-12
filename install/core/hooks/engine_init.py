# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that gets executed every time an engine has fully initialized.

"""

from tank import Hook
import sgtk
import os


class EngineInit(Hook):
    
    def execute(self, **kwargs):
        """
        Gets executed when a Toolkit engine has fully initialized.
        At this point, all applications and frameworks have been loaded,
        and the engine is fully operational.
        :param engine: The current engine being initialised
        """

    pass