# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import maya.cmds as cmds
import maya.mel as mel

import tank
from tank import Hook
from tank import TankError

class PrePublishHook(Hook):
    """
    Single hook that implements pre-publish functionality
    """
    def execute(self, tasks, work_template, progress_cb, user_data, **kwargs):
        """
        Main hook entry point
        :param tasks:           List of tasks to be pre-published.  Each task is be a 
                                dictionary containing the following keys:
                                {   
                                    item:   Dictionary
                                            This is the item returned by the scan hook 
                                            {   
                                                name:           String
                                                description:    String
                                                type:           String
                                                other_params:   Dictionary
                                            }
                                           
                                    output: Dictionary
                                            This is the output as defined in the configuration - the 
                                            primary output will always be named 'primary' 
                                            {
                                                name:             String
                                                publish_template: template
                                                tank_type:        String
                                            }
                                }
                        
        :param work_template:   template
                                This is the template defined in the config that
                                represents the current work file
               
        :param progress_cb:     Function
                                A progress callback to log progress during pre-publish.  Call:
                                
                                    progress_cb(percentage, msg)
                                     
                                to report progress to the UI

        :param user_data:       A dictionary containing any data shared by other hooks run prior to
                                this hook. Additional data may be added to this dictionary that will
                                then be accessible from user_data in any hooks run after this one.
                        
        :returns:               A list of any tasks that were found which have problems that
                                need to be reported in the UI.  Each item in the list should
                                be a dictionary containing the following keys:
                                {
                                    task:   Dictionary
                                            This is the task that was passed into the hook and
                                            should not be modified
                                            {
                                                item:...
                                                output:...
                                            }
                                            
                                    errors: List
                                            A list of error messages (strings) to report    
                                }
        """      
        results = []
        
        # validate tasks:
        for task in tasks:
            item = task["item"]
            output = task["output"]
            errors = []
        
            # report progress:
            progress_cb(0, "Validating", task)
        
            # pre-publish alembic_cache output
            if output["name"] == "alembic_cache":
                errors.extend(self.__validate_item_for_alembic_cache_publish(item))


            if output["name"] == "camera":
                errors.extend(self.__validate_item_for_camera(item))

            if output["name"] == "rendered_image":
                errors.extend(self.__validate_item_for_image_sequence(output, progress_cb))

            else:
                # don't know how to publish this output types!
                errors.append("Don't know how to publish this item!")            

            # if there is anything to report then add to result
            if len(errors) > 0:
                # add result:
                results.append({"task":task, "errors":errors})
                
            progress_cb(100)
            
        return results

    def __validate_item_for_alembic_cache_publish(self, item):
        """
        Validate that the item is valid to be exported to an alembic cache
        
        :param item:    The item to validate
        :returns:       A list of any errors found during validation that should be reported
                        to the artist
        """
        errors = []
        
        # check that the AbcExport command is available!
        if not mel.eval("exists \"AbcExport\""):
            errors.append("Could not find the AbcExport command needed to publish Alembic caches!")
        
        # check that there is still geometry in the scene:
        if not cmds.ls(geometry=True, noIntermediate=True):
            errors.append("The scene does not contain any geometry!")
    
        # finally return any errors
        return errors    

    def __validate_item_for_camera(self, item):
        """
        Validate that the item is valid to be exported to a camera

        :param item:    The item to validate
        :returns:       A list of any errors found during validation

        """

        # check that there is a camera in the scene:
        errors = []
        if not cmds.ls(cameras=True, noIntermediate=True):
            errors.append("The scene does not contain any camera!")
        return errors

    def __validate_item_for_image_sequence(self, output, progress_cb):
        """
        Validate that the item is valid to be exported as an image sequence

        :param item:    The item to validate
        :returns:       A list of any errors found during validation

        """

        errors = []

        try:
            import sgtk
            currentEngine = sgtk.platform.current_engine()
            tk = currentEngine.sgtk
            scene_path = os.path.abspath(cmds.file(query=True, sn=True))
            work_template = tk.templates["maya_shot_work"]
            fields = work_template.get_fields(scene_path)
            render_template = tk.templates["maya_shot_render_mono_exr"]
            render_files = tk.paths_from_template(render_template, fields)

            if len(render_files) == 0:
                is_valid = False
                errors.append("No render files exist to be published!")
            else:
                # ensure that published files don't already exist

                # need the render template, publish template and tank type
                publish_template = tk.templates["maya_shot_render_publish_mono_exr"]
                tank_type = output["tank_type"]

                progress_cb(25.0, "Checking for existing files")

                # check files:
                existing_files = []
                for fi, rf in enumerate(render_files):

                    progress_cb(25 + (75 * (len(render_files) / (fi + 1))))

                    # construct the publish path:
                    fields = render_template.get_fields(rf)
                    fields["TankType"] = tank_type
                    target_path = publish_template.apply_fields(fields)

                    if os.path.exists(target_path):
                        existing_files.append(target_path)

                if existing_files:
                    # one or more published files already exist!
                    msg = "Published render file '%s'" % existing_files[0]
                    if len(existing_files) > 1:
                        msg += " (+%d others)" % (len(existing_files) - 1)
                    msg += " already exists!"
                    errors.append(msg)
        except Exception, e:

            errors.append("Unhandled exception: %s" % e)

        return errors

