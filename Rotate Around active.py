# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Rotate Around active",
    "author": "1COD",
    "version": (1, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D",
    "description": "activ object as new space referential. ctrl+. numpad", 
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}

import bpy
from mathutils import Matrix, Euler, Vector
from bpy.types import Operator, Panel
from bpy.props import FloatProperty, BoolProperty

bpy.types.Scene.rot_x=FloatProperty()   
bpy.types.Scene.rot_y=FloatProperty() 
bpy.types.Scene.rot_z=FloatProperty() 
bpy.types.Scene.loc_x=FloatProperty()   
bpy.types.Scene.loc_y=FloatProperty()   
bpy.types.Scene.loc_z=FloatProperty()  
bpy.types.Scene.whole_scene=BoolProperty()

class OBJ_OT_rot_loc (Operator):    
    bl_idname = "obj.rot_loc"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll (cls, context):
        return context.object and not context.scene.rot_x and not context.object.parent
    
    def execute(self, context):
        
        if context.scene.rot_x:
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_z')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_z')       
                
        cao=context.object
        rot = cao.rotation_euler.copy()
        loc = cao.location.copy()
        context.scene.rot_x = cao.rotation_euler.x
        context.scene.rot_y = cao.rotation_euler.y
        context.scene.rot_z = cao.rotation_euler.z   
        context.scene.loc_x = cao.location.x
        context.scene.loc_y = cao.location.y 
        context.scene.loc_z = cao.location.z   
        to_qt = rot.to_quaternion()
        to_qt.invert()

        R = to_qt.to_matrix().to_4x4()
        T = Matrix.Translation(loc)
        M = T @ R @ T.inverted()
        
        if context.scene.whole_scene:            
            for obj in context.scene.objects:
                if obj.parent :
                    continue
                obj.location = M @ obj.location -loc
                obj.rotation_euler.rotate(M)            
        else:
            for obj in context.selected_objects:
                if obj.parent:
                    continue
                obj.location = M @ obj.location -loc
                obj.rotation_euler.rotate(M)
            
        return {'FINISHED'}

class OBJ_OT_inv_rot_loc (Operator):    
    bl_idname = "obj.inv_rot_loc"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll (cls, context):
        return context.object and context.scene.rot_x
        
    def execute(self, context):
        
        rot = Euler((
        context.scene.rot_x,
        context.scene.rot_y,
        context.scene.rot_z), 
        'XYZ')
        loc = (context.scene.loc_x,context.scene.loc_y,context.scene.loc_z)
        
        to_qt = rot.to_quaternion()
        to_qt.invert()

        R = to_qt.to_matrix().to_4x4()
        T = Matrix.Translation(loc)
        M = T @ R @ T.inverted()
        M = M.inverted() #rotation inverted
        
        if context.scene.whole_scene:
            for obj in context.scene.objects:
                if obj.parent:
                    continue
                obj.location += Vector(loc)  #location before and invert
                obj.location = M @ obj.location
                obj.rotation_euler.rotate(M)            
            
        else:
            for obj in context.selected_objects:
                if obj.parent:
                    continue
                obj.location += Vector(loc)  #location before and invert
                obj.location = M @ obj.location
                obj.rotation_euler.rotate(M)
        
        if context.scene.rot_x:
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_z')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_z') 
        
        return {'FINISHED'}

class OBJ_OT_rot_loc_confirm (Operator):    
    bl_idname = "obj.rot_loc_confirm"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll (cls, context):
        return context.object and context.scene.rot_x
        
    def execute(self, context):
        
        if context.scene.rot_x:
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_z')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_x')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_y')                
            bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_z')        
        
        return {'FINISHED'}

class OBJ_PT_loc_rot_menu(Panel):
    bl_label = "Global rotation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "0data"  # not valid name to hide it
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("obj.rot_loc",text='Active new referential')       
        row.prop(context.scene,'whole_scene',text='Whole Scene')
        row=layout.row()
        row.operator("obj.rot_loc_confirm", text='Confirm')
        row.operator("obj.inv_rot_loc", text='Cancel')


addon_keymaps = []

def register():
    bpy.utils.register_class(OBJ_OT_rot_loc)
    bpy.utils.register_class(OBJ_OT_inv_rot_loc)
    bpy.utils.register_class(OBJ_PT_loc_rot_menu)
    bpy.utils.register_class(OBJ_OT_rot_loc_confirm)
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:

        km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
        kmi = km.keymap_items.new(idname='wm.call_panel', type='NUMPAD_PERIOD', value='PRESS',shift=True)
        kmi.properties.name = "OBJ_PT_loc_rot_menu"
        addon_keymaps.append((km, kmi))  

def unregister():
    bpy.utils.unregister_class(OBJ_OT_rot_loc)
    bpy.utils.unregister_class(OBJ_OT_inv_rot_loc)
    bpy.utils.unregister_class(OBJ_PT_loc_rot_menu)
    bpy.utils.unregister_class(OBJ_OT_rot_loc_confirm)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()  

if __name__ == "__main__":
    register()
    
