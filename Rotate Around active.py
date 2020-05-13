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
    "name": "Rotate around active and cursor",
    "author": "1COD",
    "version": (1, 2, 0),
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

bpy.types.Scene.whole_scene=BoolProperty(default=False)
bpy.types.Scene.around_cursor=BoolProperty(default=False)

def remove_prop (self,context):        

    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_loc_x')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_loc_y')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_loc_z')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_rot_x')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_rot_y')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'cur_rot_z') 

    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_x')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_y')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'loc_z')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_x')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_y')                
    bpy.ops.wm.properties_remove(data_path = 'scene', property = 'rot_z') 
  

class OBJ_OT_rot_loc (Operator):    
    bl_idname = "obj.rot_loc"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll (cls, context):
        return context.object and not getattr(context.scene,'rot_x', None) and not context.object.parent    
    
    def execute(self, context):       

        bpy.types.Scene.rot_x=FloatProperty() #for active object
        bpy.types.Scene.rot_y=FloatProperty() 
        bpy.types.Scene.rot_z=FloatProperty() 
        bpy.types.Scene.loc_x=FloatProperty()   
        bpy.types.Scene.loc_y=FloatProperty()   
        bpy.types.Scene.loc_z=FloatProperty()            
 
        
        bpy.types.Scene.cur_rot_x=FloatProperty()  
        bpy.types.Scene.cur_rot_y=FloatProperty()  
        bpy.types.Scene.cur_rot_z=FloatProperty()  
        bpy.types.Scene.cur_loc_x=FloatProperty()  
        bpy.types.Scene.cur_loc_y=FloatProperty()  
        bpy.types.Scene.cur_loc_z=FloatProperty() 
        
        context.scene.cur_rot_x = context.scene.cursor.rotation_euler.x
        context.scene.cur_rot_y = context.scene.cursor.rotation_euler.y
        context.scene.cur_rot_z = context.scene.cursor.rotation_euler.z   
        context.scene.cur_loc_x = context.scene.cursor.location.x
        context.scene.cur_loc_y = context.scene.cursor.location.y 
        context.scene.cur_loc_z = context.scene.cursor.location.z  
#        cao=context.active_object
#        context.scene.rot_x = cao.rotation_euler.x #doublon to make poll True


        cao=context.active_object
        context.scene.rot_x = cao.rotation_euler.x
        context.scene.rot_y = cao.rotation_euler.y
        context.scene.rot_z = cao.rotation_euler.z   
        context.scene.loc_x = cao.location.x
        context.scene.loc_y = cao.location.y 
        context.scene.loc_z = cao.location.z
        if context.scene.around_cursor: 
            rot = context.scene.cursor.rotation_euler.copy()
            loc = context.scene.cursor.location.copy()         
        else:
            rot = cao.rotation_euler.copy()
            loc = cao.location.copy()        

        to_qt = rot.to_quaternion()
        to_qt.invert()

        R = to_qt.to_matrix().to_4x4()
        T = Matrix.Translation(loc)
        M = T @ R @ T.inverted()
        if context.scene.around_cursor:
            M=M.inverted()
        
        if context.scene.whole_scene:            
            for obj in context.scene.objects:
                if obj.parent :
                    continue
                if context.scene.around_cursor:
                    obj.location = M @ loc
                else:
                    obj.location = M @ obj.location -loc
                obj.rotation_euler.rotate(M)            
        else:
            for obj in context.selected_objects:
                if obj.parent:
                    continue
                if context.scene.around_cursor:
                    obj.location = M @ loc
                else:
                    obj.location = M @ obj.location -loc
                obj.rotation_euler.rotate(M)
            
        return {'FINISHED'}

class OBJ_OT_rot_loc_cancel (Operator):    
    bl_idname = "obj.rot_loc_cancel"
    bl_label = "cancel rot loc"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll (cls, context):
        return context.object and getattr(context.scene, 'rot_x', None)
    def execute(self, context):
        
        if context.scene.around_cursor:
            rot = Euler((
                     context.scene.cur_rot_x,
                    context.scene.cur_rot_y,
                    context.scene.cur_rot_z), 
        'XYZ')
            loc = (context.scene.loc_x,
                    context.scene.loc_y,
                    context.scene.loc_z)# - context.scene.cur_loc_z)
            loc1 = (context.scene.cur_loc_x,context.scene.cur_loc_y,context.scene.cur_loc_z) 
        else:
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
        if context.scene.around_cursor:
            M = M.inverted()            
        
        if context.scene.whole_scene:
            for obj in context.scene.objects:
                if obj.parent:
                    continue
                obj.location = M @ (obj.location + Vector(loc))
                obj.rotation_euler.rotate(M)
        else:
            for obj in context.selected_objects:
                if obj.parent:
                    continue 
                if context.scene.around_cursor: 
                    obj.location = M @ (obj.location + Vector(loc)-Vector(loc1))
                else:
                    obj.location = M @ (obj.location + Vector(loc))
                obj.rotation_euler.rotate(M)                      
 
        remove_prop(self,context)
        del bpy.types.Scene.rot_x
            
        return {'FINISHED'}
 
class OBJ_OT_rot_loc_confirm (Operator):    
    bl_idname = "obj.rot_loc_confirm"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll (cls, context):
        return context.object and getattr(context.scene, 'rot_x', None)
        
    def execute(self, context):        
        

        remove_prop(self,context) 
        del bpy.types.Scene.rot_x       
        
        return {'FINISHED'}

class OBJ_PT_loc_rot_menu(Panel):
    bl_label = "Global rotation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "0data"  # not valid name to hide it
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.separator() #to hold the menu to drag it easier
        row = layout.row()
        label='Cursor'if context.scene.around_cursor else 'Active'
        row.operator("obj.rot_loc",text=label)       
        row.prop(context.scene,'whole_scene',text='Scene')
        row.prop(context.scene,'around_cursor',text='Cursor')
        row=layout.row()
        row.operator("obj.rot_loc_confirm", text='Confirm')
        row.operator("obj.rot_loc_cancel", text='Cancel')

addon_keymaps = []

def register():
    bpy.utils.register_class(OBJ_OT_rot_loc)
    bpy.utils.register_class(OBJ_OT_rot_loc_cancel)
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
    bpy.utils.unregister_class(OBJ_OT_rot_loc_cancel)
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
    
