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

import sgtk
import tank
from tank import Hook
from tank import TankError

class ScanSceneHook(Hook):
    """
    Hook to scan scene for items to publish
    """
    
    def execute(self, **kwargs):
        """
        Main hook entry point
        :returns:       A list of any items that were found to be published.
                        Each item in the list should be a dictionary containing
                        the following keys:
                        {
                            type:   String
                                    This should match a scene_item_type defined in
                                    one of the outputs in the configuration and is
                                    used to determine the outputs that should be
                                    published for the item

                            name:   String
                                    Name to use for the item in the UI

                            description:    String
                                            Description of the item to use in the UI

                            selected:       Bool
                                            Initial selected state of item in the UI.
                                            Items are selected by default.

                            required:       Bool
                                            Required state of item in the UI.  If True then
                                            item will not be deselectable.  Items are not
                                            required by default.

                            other_params:   Dictionary
                                            Optional dictionary that will be passed to the
                                            pre-publish and publish hooks
                        }
        """

        items = []

        # get the main scene:
        scene_name = cmds.file(query=True, sn=True)
        if not scene_name:
            raise TankError("Please Save your file before Publishing")

        scene_path = os.path.abspath(scene_name)
        name = os.path.basename(scene_path)

        # create the primary item - this will match the primary output 'scene_item_type':
        items.append({"type": "work_file", "name": name})

        # if there is any geometry in the scene (poly meshes or nurbs patches), then
        # add a geometry item to the list:
        if cmds.ls(geometry=True, noIntermediate=True):
            items.append({"type":"geometry", "name":"All Scene Geometry"})

        # look for cameras to publish
        for camera in cmds.listCameras(perspective=True):
            items.append({"type": "camera", "name": camera})

        # look for root level groups that have meshes as children:
        for grp in cmds.ls(assemblies=True, long=True):
            if cmds.ls(grp, dag=True, type="mesh"):
                # include this group as a 'mesh_group' type
                items.append({"type": "mesh_group", "name": grp})

        # get the engine we are running
        engine = sgtk.platform.current_engine()
        app = self.parent
        # get shotgun engine and installation path (shotgun API)
        #tk = engine.sgtk
        # get the current context, entity type and entity name
        ctx = engine.context
        # giving shot type, id, entity name
        entity = ctx.entity
        #scene_path = os.path.abspath(cmds.file(query=True, sn=True))
        if entity['type'] == 'Asset':
            None
        elif entity['type'] == 'Shot':
            # look up the template for the work file in the configuration
            # will get the proper template based on context (Asset, Shot, etc)
            work_template = app.get_template("template_work")
            work_template_fields = work_template.get_fields(scene_name)
            version = work_template_fields["version"]
            shotName = work_template_fields["name"]
            # get all the secondary output render templates and match them against
            # what is on disk
            secondary_outputs = app.get_setting("secondary_outputs")
            render_outputs = [out for out in secondary_outputs if out["tank_type"] == "Rendered Image"]
            for render_output in render_outputs:

                render_template = app.get_template_by_name(render_output["publish_template"])

                # now look for rendered images. note that the cameras returned from
                # listCameras will include full DAG path. You may need to account
                # for this in your, more robust solution, if you want the camera name
                # to be part of the publish path. For my simple test, the cameras
                # are not parented, so there is no hierarchy.

                # iterate over all layers
                #for camera in cmds.listCameras():
                for layer in cmds.ls(type="renderLayer"):

                    # apparently maya has 2 names for the default layer. I'm
                    # guessing it actually renders out as 'masterLayer'.
                    layer = layer.replace("defaultRenderLayer", "masterLayer")


                    # these are the fields to populate into the template to match
                    # against
                    fields = {
                        #'maya.camera_name': camera,
                        'maya.layer_name': layer,
                        'name': shotName,
                        'version': version,
                    }

                    # match existing paths against the render template
                    paths = engine.tank.abstract_paths_from_template(
                        render_template, fields)

                    # if there's a match, add an item to the render
                    if paths:
                        items.append({
                            "type": "rendered_image",
                            "name": shotName,

                            # since we already know the path, pass it along for
                            # publish hook to use
                            "other_params": {
                                # just adding first path here. may want to do some
                                # additional validation if there are multiple.
                                'path': paths[0],
                            }
                        })
        return items





