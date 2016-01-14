bl_info = {
    "name": "Blender Rokuro",
    "author": "Yuichi Sato",
    "version": (0, 1),
    "blender": (2, 76, 0),
    "location": "Found in the properties shelf.",
    "description": "Modeling on the rokuro.",
    "warning": "",
    "wiki_url": "https://github.com/satoyuichi/BlenderRokuro",
    "tracker_url": "",
    "category": "3D View"}

import bpy
import math
import copy

class BlenderRokuroProps(bpy.types.PropertyGroup):
    rotate_axis_x = bpy.props.BoolProperty(name="X", default=False)
    rotate_axis_y = bpy.props.BoolProperty(name="Y", default=False)
    rotate_axis_z = bpy.props.BoolProperty(name="Z", default=True)
    rotate_direction = bpy.props.BoolProperty(name="Rotate Left", default=True)
    rotate_step = bpy.props.FloatProperty(name="Step", min=1.0, max=32.0, soft_max=32.0, soft_min=1.0, step=1.0)
    rotate_previous_euler = copy.deepcopy(bpy.context.object.rotation_euler)
    rotate_started = False

def rokuro_add_euler(euler, r):
    props = bpy.context.window_manager.rokuro

    if props.rotate_direction:
        if (euler + r) < 0:
            new_euler = euler + r + (2.0 * math.pi)
        else:
            new_euler = euler + r
    else:
        if (euler + r) > (2.0 * math.pi):
            new_euler = euler + r - (2.0 * math.pi)
        else:
            new_euler = euler + r
        
    return new_euler


def rokuro_proc(scene):
    props = bpy.context.window_manager.rokuro

    r = props.rotate_step * 2.0 * math.pi / (scene.frame_end - scene.frame_start)
    if props.rotate_direction:
        r *= -1.0
    
    if props.rotate_axis_x:
        bpy.context.object.rotation_euler[0] = rokuro_add_euler(bpy.context.object.rotation_euler[0], r)

    if props.rotate_axis_y:
        bpy.context.object.rotation_euler[1] = rokuro_add_euler(bpy.context.object.rotation_euler[1], r)

    if props.rotate_axis_z:
        bpy.context.object.rotation_euler[2] = rokuro_add_euler(bpy.context.object.rotation_euler[2], r)

    
    
class BlenderRokuroRotate(bpy.types.Operator):
    bl_idname = "rokuro.rotate"
    bl_label = "Start"

    def execute(self, context):
        if BlenderRokuroProps.rotate_started:
            bpy.ops.screen.animation_cancel()
            bpy.app.handlers.frame_change_post.remove(rokuro_proc)
            bpy.context.object.rotation_euler = BlenderRokuroProps.rotate_previous_euler
        else:
            BlenderRokuroProps.rotate_previous_euler = copy.deepcopy(bpy.context.object.rotation_euler)
            bpy.app.handlers.frame_change_post.append(rokuro_proc)
            bpy.ops.screen.animation_play()

        BlenderRokuroProps.rotate_started = not BlenderRokuroProps.rotate_started
        
        return {'FINISHED'}

        
class BlenderRokuroPanel(bpy.types.Panel):
    bl_label = "Rokuro"
    bl_idname = "OBJECT_PT_rokuro"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    @classmethod
    def poll(self, context):
        return context.mode == 'SCULPT'
        
    def draw(self, context):
        props = context.window_manager.rokuro
        
        layout = self.layout

        row = layout.row()
        column = row.column()
        column.prop(props, "rotate_axis_x")
        column = row.column()
        column.prop(props, "rotate_axis_y")
        column = row.column()
        column.prop(props, "rotate_axis_z")

        row = layout.row()
        row.prop(props, "rotate_direction")

        row = layout.row(align=True)
        row.prop(context.scene, "frame_start", text="Start")
        row.prop(context.scene, "frame_end", text="End")

        row = layout.row()
        row.prop(props, "rotate_step")
        
        row = layout.row()
        if BlenderRokuroProps.rotate_started:
            row.operator("rokuro.rotate", text="Disable Rokuro")
        else:
            row.operator("rokuro.rotate", text="Enable Rokuro")

            
def register():
    bpy.utils.register_class(BlenderRokuroProps)
    bpy.utils.register_class(BlenderRokuroPanel)
    bpy.utils.register_class(BlenderRokuroRotate)

    bpy.types.WindowManager.rokuro = bpy.props.PointerProperty(type=BlenderRokuroProps)


def unregister():
    bpy.utils.unregister_class(BlenderRokuroProps)
    bpy.utils.unregister_class(BlenderRokuroPanel)
    bpy.utils.unregister_class(BlenderRokuroRotate)

    try:
        del bpy.types.WindowManager.rokuro
    except:
        pass

if __name__ == "__main__":
    register()
