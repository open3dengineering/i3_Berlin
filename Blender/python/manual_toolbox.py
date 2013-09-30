#############################
# License : https://www.gnu.org/licenses/lgpl.html  LGPL V3
# Author: Morris Winkler m.winkler@open3dengineering.org
#
# toolbox for writing manuals in blender 

import bpy

##################################
# globals

##################################
# UI functions


class OBJECT_OT_SET_KEYFRAME_HIDE_RENDER(bpy.types.Operator):
    bl_idname = "manual_toolbox.set_keframe_hide_render"
    bl_label = "Set Keframe hide render"
    
    def execute(self, context):
        for ob in bpy.data.objects:
            if( ob.select == True):
                ob.hide = True
                ob.hide_render = True 
                ob.keyframe_insert(data_path='hide')
                ob.keyframe_insert(data_path='hide_render')
        return{'FINISHED'}
            
class OBJECT_OT_UNSET_KEYFRAME_HIDE_RENDER(bpy.types.Operator):
    bl_idname = "manual_toolbox.unset_keframe_hide_render"
    bl_label = "Unset Keframe hide render"
    
    def execute(self, context):
        for ob in bpy.data.objects:
            if( ob.select == True):
                ob.hide = False
                ob.hide_render = False 
                ob.keyframe_delete(data_path='hide')
                ob.keyframe_delete(data_path='hide_render')    
        return{'FINISHED'}    
    

class ToolsPanel(bpy.types.Panel):
    bl_label = "Manual Toolbox"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("manual_toolbox.set_keframe_hide_render")
        self.layout.operator("manual_toolbox.unset_keframe_hide_render")
        
        
        
bpy.utils.register_module(__name__)        