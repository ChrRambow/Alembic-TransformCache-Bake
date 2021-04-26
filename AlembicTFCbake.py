bl_info = {
    "name": "Alembic TransFormCache Bake",
    "author": "Christian Rambow",
    "version": (1, 0),
    "blender": (2, 91, 0),
    "location": "View3D > Object",
    "description": "Bakes an alembic Transform Cache into keyframes",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.types import (
    AddonPreferences,
    Operator,
    Panel,
    PropertyGroup,
)
from bpy.props import (IntProperty)

class OBJECT_OT_AlembicTRCBake(Operator):
    
    bl_label = "Alembic TFC Bake"
    bl_idname = "object.alembicbake"
    bl_description = "Bakes an alembic Transform Cache into keyframes"
    bl_space_type = "OUTLINER"
    bl_region_type = "UI"
    bl_options = {'REGISTER', 'UNDO'}
    
    sampleRate: bpy.props.IntProperty(
        name = "Frame Step",
        default = 1,
        min = 1,
        max = 120,
        description = "Set Keyframe every Nth frame",
    )
    
    @classmethod
    def poll(cls, context):
        getObj =  bpy.context.object.constraints
        #conType = getObj.constraints
        #print(getObj)
        if getObj:
            return context.object.select_get() #and context.object.type == 'CAMERA' 
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):

        scene = bpy.context.scene
        
        #store SourceObject + SourceObject name
        sourceObj = bpy.context.active_object
        sourceName = sourceObj.name
        
        
        #duplicate Source and store target Object
        bpy.ops.object.duplicate_move(
            OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, 
            TRANSFORM_OT_translate={
                "value":(0, 0, 0), 
                "orient_type":'GLOBAL',
                "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), 
                "orient_matrix_type":'GLOBAL', 
                "constraint_axis":(False, False, False), 
                "mirror":False, 
                "use_proportional_edit":False, 
                "proportional_edit_falloff":'SMOOTH', 
                "proportional_size":1, 
                "use_proportional_connected":False, 
                "use_proportional_projected":False, 
                "snap":False, 
                "snap_target":'CLOSEST', 
                "snap_point":(0, 0, 0), 
                "snap_align":False, 
                "snap_normal":(0, 0, 0), 
                "gpencil_strokes":False, 
                "cursor_transform":False, 
                "texture_space":False, 
                "remove_on_cancel":False, 
                "release_confirm":False, 
                "use_accurate":False, 
                "use_automerge_and_split":False})

        targetObj = bpy.context.active_object

        bpy.ops.constraint.delete(constraint="Transform Cache", owner='OBJECT')

        #ZeroOut Transforms on TargetObject and add CopyTransforms Constrain

        bpy.ops.object.rotation_clear(clear_delta=False)
        bpy.ops.object.scale_clear(clear_delta=False)
        bpy.ops.object.location_clear(clear_delta=False)
                
        trans_constraint = targetObj.constraints.new(type='COPY_TRANSFORMS')
        trans_constraint.target = sourceObj

        #Bake TargetObject to Keyframes

        bpy.ops.nla.bake(frame_start=scene.frame_start, frame_end=scene.frame_end, step=self.sampleRate, visual_keying=True, clear_constraints=True, bake_types={'OBJECT'})

        #Select SourceObject and Delete

        bpy.ops.object.select_all(action='DESELECT')
        sourceObj.select_set(state=True)
        bpy.ops.object.delete()

        #Name Target with SourcObject name
                
        targetObj.name = sourceName

        return {'FINISHED'}
        

def menu_func(self, context):
        self.layout.operator(OBJECT_OT_AlembicTRCBake.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_AlembicTRCBake)
    bpy.types.OUTLINER_MT_context_menu.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AlembicTRCBake)
    bpy.types.OUTLINER_MT_context_menu.remove(menu_func)
    
if __name__ == "__main__":
    register()