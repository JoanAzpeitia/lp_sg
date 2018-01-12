# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import maya.cmds as cmds

import sgtk
from sgtk.platform.qt import QtGui

HookClass = sgtk.get_hook_baseclass()


class SceneOperation(HookClass):
    """
    Hook called to perform an operation with the
    current scene
    """

    def execute(self, operation, file_path, context, parent_action, file_version, read_only, **kwargs):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)

        :param context:         Context
                                The context the file operation is being
                                performed in.

        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as
                                - version_up

        :param file_version:    The version/revision of the file to be opened.  If this is 'None'
                                then the latest version should be opened.

        :param read_only:       Specifies if the file should be opened read-only or not

        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'reset'        - True if scene was reset to an empty
                                                 state, otherwise False
                                all others     - None
        """

        if operation == "prepare_new":

            # get the app from the hook
            app = self.parent
            # now get work files settings so that we can work out what template we should be using to save with
            app_settings = sgtk.platform.find_app_settings(
                app.engine.name, app.name, app.sgtk, context, app.engine.instance_name
            )
            # get the template name from the settings
            template_name = app_settings[0]['settings']['template_work']
            # using the template name get an template object
            template = app.sgtk.templates[template_name]

            # now use the context to resolve as many of the template fields as possible
            fields = context.as_template_fields(template)

            # The name of the shot
            entity = context.entity
            shotEntity = entity['name']
            shotName = shotEntity.replace("_", "")
            fields['name'] = shotName
            # The version can't be resolved from context so we must add the value
            fields['version'] = 1

            # now resolve the template path using the field values.
            file_path = template.apply_fields(fields)
            length = len(file_path)
            lengthNoExt = length - 2
            resolved_path = file_path[0:lengthNoExt] + 'mb'

            #maya file path
            eng = sgtk.platform.current_engine()
            tk =  eng.sgtk
            entityType = entity['type']
            entityName = entity['name']

            if entityType == 'Shot':
                template_maya = tk.templates['3Dshot_root']
            elif entityType == 'Asset':
                template_maya = tk.templates['asset_root']
            else:
                print "Could not find the entity type"

            shot_path_maya = tk.paths_from_template(template_maya,{entityType: entityName})
            shot_path_maya_str = ''.join(shot_path_maya)
            #find workspace path
            #cmds.workspace(directory=shot_path_maya_str)
            #set workspace path
            cmds.workspace(shot_path_maya_str, openWorkspace=True)
            #cmds.workspace( entityName, newWorkspace=True)
            #cmds.workspace(saveWorkspace=True)
            #cmds.workspace(baseWorkspace='default')

            #save scene
            cmds.file(rename=resolved_path)
            cmds.file(save=True, type='mayaBinary')



        elif operation == "current_path":
            # return the current scene path
            return cmds.file(query=True, sceneName=True)
        elif operation == "open":
            # do new scene as Maya doesn't like opening
            # the scene it currently has open!
            cmds.file(new=True, force=True)
            cmds.file(file_path, open=True, force=True)
        elif operation == "save":
            # save the current scene:
            cmds.file(save=True)
        elif operation == "save_as":
            # first rename the scene as file_path:
            cmds.file(rename=file_path)

            # Maya can choose the wrong file type so
            # we should set it here explicitely based
            # on the extension
            maya_file_type = None
            if file_path.lower().endswith(".ma"):
                maya_file_type = "mayaAscii"
            elif file_path.lower().endswith(".mb"):
                maya_file_type = "mayaBinary"

            # save the scene:
            if maya_file_type:
                cmds.file(save=True, force=True, type=maya_file_type)
            else:
                cmds.file(save=True, force=True)

        elif operation == "reset":
            """
            Reset the scene to an empty state
            """
            while cmds.file(query=True, modified=True):
                # changes have been made to the scene
                res = QtGui.QMessageBox.question(None,
                                                 "Save your scene?",
                                                 "Your scene has unsaved changes. Save before proceeding?",
                                                 QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)

                if res == QtGui.QMessageBox.Cancel:
                    return False
                elif res == QtGui.QMessageBox.No:
                    break
                else:
                    scene_name = cmds.file(query=True, sn=True)
                    if not scene_name:
                        cmds.SaveSceneAs()
                    else:
                        cmds.file(save=True)

            # do new file:
            cmds.file(newFile=True, force=True)
            return True
