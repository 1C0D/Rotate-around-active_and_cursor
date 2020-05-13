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

def remove_prop (self,context):        
    
    rmv=bpy.ops.wm.properties_remove #kind of unlink. if del prop cause error when ctrl+z
    
    rmv(data_path = 'scene', property = 'cur_loc_x')                
    rmv(data_path = 'scene', property = 'cur_loc_y')                
    rmv(data_path = 'scene', property = 'cur_loc_z')                
    rmv(data_path = 'scene', property = 'cur_rot_x')                
    rmv(data_path = 'scene', property = 'cur_rot_y')                
    rmv(data_path = 'scene', property = 'cur_rot_z') 

    rmv(data_path = 'scene', property = 'loc_x')                
    rmv(data_path = 'scene', property = 'loc_y')                
    rmv(data_path = 'scene', property = 'loc_z')                
    rmv(data_path = 'scene', property = 'rot_x')                
    rmv(data_path = 'scene', property = 'rot_y')                
    rmv(data_path = 'scene', property = 'rot_z')     

Scn = bpy.types.Scene
Scn.whole_scene=BoolProperty(default=False)
Scn.around_cursor=BoolProperty(default=False)

def loc_rot_props(self,context):
    
    Scn = bpy.types.Scene  
    context = bpy.context    
    scn = context.scene 
    cao=context.active_object

    Scn.rot_x=FloatProperty() #for active object
    Scn.rot_y=FloatProperty() 
    Scn.rot_z=FloatProperty() 
    Scn.loc_x=FloatProperty()   
    Scn.loc_y=FloatProperty()   
    Scn.loc_z=FloatProperty() 
    
    scn.rot_x = cao.rotation_euler.x
    scn.rot_y = cao.rotation_euler.y
    scn.rot_z = cao.rotation_euler.z   
    scn.loc_x = cao.location.x
    scn.loc_y = cao.location.y 
    scn.loc_z = cao.location.z   
    
    Scn.cur_rot_x=FloatProperty()  #for cursor
    Scn.cur_rot_y=FloatProperty()  
    Scn.cur_rot_z=FloatProperty()  
    Scn.cur_loc_x=FloatProperty()  
    Scn.cur_loc_y=FloatProperty()  
    Scn.cur_loc_z=FloatProperty()                

    scn.cur_rot_x = scn.cursor.rotation_euler.x
    scn.cur_rot_y = scn.cursor.rotation_euler.y
    scn.cur_rot_z = scn.cursor.rotation_euler.z   
    scn.cur_loc_x = scn.cursor.location.x
    scn.cur_loc_y = scn.cursor.location.y 
    scn.cur_loc_z = scn.cursor.location.z 

    
def call_props(self,context):
    
    context = bpy.context    
    scn = context.scene 
    cao=context.active_object
    
    rot_cur = context.scene.cursor.rotation_euler.copy()
    loc_cur = context.scene.cursor.location.copy()         
    rot = cao.rotation_euler.copy()
    loc = cao.location.copy()   

    self.rot = Euler((rot.x, rot.y, rot.z), 'XYZ')  
    self.loc = loc      

    rot_to_curs = Euler((
                        -rot_cur.x + rot.x,
                        -rot_cur.y + rot.y,
                        -rot_cur.z + rot.z
                        ), 'XYZ')
    
    if scn.around_cursor:                 
        self.rot = rot_to_curs
        self.loc_cur = loc_cur
        
def call_props_back(self,context):

    context = bpy.context    
    scn = context.scene 
    
    self.rot = Euler((
            scn.rot_x,
            scn.rot_y,
            scn.rot_z), 
            'XYZ')     
               
    self.loc = Vector((scn.loc_x, scn.loc_y, scn.loc_z))
    
    rot_curs = Euler((
                    -scn.cur_rot_x + scn.rot_x,
                    -scn.cur_rot_y + scn.rot_y,
                    -scn.cur_rot_z + scn.rot_z
                        ))

    loc_curs = Vector((
                        scn.cur_loc_x,
                        scn.cur_loc_y,
                        scn.cur_loc_z
                        ))

    if scn.around_cursor:                 
        self.rot = rot_curs
        self.loc_curs= loc_curs
  

class OBJ_OT_rot_loc (Operator):    
    bl_idname = "obj.rot_loc"
    bl_label = "matrice loc rot from active"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll (cls, context):
        return context.object and not getattr(context.scene,'rot_x', None) and not context.object.parent    #getattr because not rot_x is not enough, can be == 0
    
    def execute(self, context):   
        
        context = bpy.context    
        scn = context.scene 
         
        loc_rot_props(self,context)
        call_props(self,context)
        
        rot=self.rot
        loc=self.loc
        
        to_qt = rot.to_quaternion()
        to_qt.invert()
        R = to_qt.to_matrix().to_4x4()
        T = Matrix.Translation(loc)
        M = T @ R @ T.inverted()

            
        if scn.whole_scene:
            obj = scn.objects
        else:
            obj = context.selected_objects
        
        for ob in obj:
            if ob.parent:
                continue
            ob.location = M @ ob.location -loc
            ob.rotation_euler.rotate(M)
            if scn.around_cursor:
                ob.location +=  self.loc_cur
            
        return {'FINISHED'}


class OBJ_OT_rot_loc_cancel (Operator):    
    bl_idname = "obj.rot_loc_cancel"
    bl_label = "cancel rot loc"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll (cls, context):
        return context.object and getattr(context.scene, 'rot_x', None)
    def execute(self, context):
        
        context = bpy.context    
        scn = context.scene          

        call_props_back(self,context)
        
        loc= self.loc
        rot= self.rot
        
        to_qt = rot.to_quaternion()
        to_qt.invert()

        R = to_qt.to_matrix().to_4x4()
        T = Matrix.Translation(loc)
        M = T @ R @ T.inverted()
        M = M.inverted() #rotation inverted

        if scn.whole_scene:
            obj = scn.objects
        else:
            obj = context.selected_objects
        
        for ob in obj:  
            if ob.parent:
                continue            
            
            if scn.around_cursor:
                ob.location = M @ (ob.location + loc- self.loc_curs)
            else:
                ob.location = M @ (ob.location + loc)
                
            ob.rotation_euler.rotate(M)
 
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
        
        scn = context.scene
        layout = self.layout
        layout.separator() #to hold the menu to drag it easier
        row = layout.row()
        label='Cursor'if scn.around_cursor else 'Active'
        row.operator("obj.rot_loc",text=label)       
        row.prop(scn,'whole_scene',text='Scene')
        row.prop(scn,'around_cursor',text='Cursor')
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
    

