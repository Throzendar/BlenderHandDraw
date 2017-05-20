import bpy
import bgl
import blf
import math

from bpy.props import IntProperty, FloatProperty
from bpy_extras import view3d_utils

class HandDrawOperator(bpy.types.Operator):
    bl_idname = 'gpencil.hand_draw'
    bl_label = 'Hand Draw Modal Operator'

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'MOSUEMOVE':
            self.counter += 1

        self.mouse_pos = [event.mouse_region_x, event.mouse_region_y]
        self.object = bpy.context.object
        region = bpy.context.region
        region3d = bpy.context.space_data.region_3d

        view_vector = view3d_utils.region_2d_to_vector_3d(region, region3d, self.mouse_pos)
        self.loc = view3d_utils.region_2d_to_location_3d(region, region3d, self.mouse_pos, view_vector)

        self.counter += 1
        if self.counter == 10:
            stroke = get_stroke()

            stroke.points.add(count = 2)
            stroke.points[0].co = (self.last_pos)
            stroke.points[1].co = (self.loc)
            self.last_pos = self.loc
            self.counter = 0

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        self.counter = 0
        self.mouse_pos = [0, 0]
        self.last_pos = [0, 0, 0]
        self.loc = [0, 0, 0]

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

def get_stroke():
    sc= bpy.context.scene

    # Create grease pencil data if none exists
    if not sc.grease_pencil:
        a = [ a for a in bpy.context.screen.areas if a.type == 'VIEW_3D' ][0]
        override = {
            'scene'         : sc,
            'screen'        : bpy.context.screen,
            'object'        : bpy.context.object,
            'area'          : a,
            'region'        : a.regions[0],
            'window'        : bpy.context.window,
            'active_object' : bpy.context.object
        }

        bpy.ops.gpencil.data_add( override )

    gp = sc.grease_pencil

    # Reference grease pencil layer or create one of none exists
    if gp.layers:
        gpl = gp.layers[0]
    else:
        gpl = gp.layers.new('gpl', set_active = True )

    # Reference active GP frame or create one of none exists
    if gpl.frames:
        fr = gpl.active_frame
    else:
        fr = gpl.frames.new(1)

    # Create a new stroke
    stroke = fr.strokes.new()
    stroke.draw_mode = '3DSPACE'
    return stroke

def register():
    bpy.utils.register_class(HandDrawOperator)


def unregister():
    bpy.utils.unregister_class(HandDrawOperator)

def draw_callback_px(self, context):
    font_id = 0
    blf.position(font_id, 15, 100, 0)
    blf.size(font_id, 12, 72)
    blf.draw(font_id, "Mouse position: " + str(self.mouse_pos[0]) + "/" + str(self.mouse_pos[1]) )
    blf.position(font_id, 15, 115, 0)
    blf.draw(font_id, "3d pos" + str(self.loc[0]) + "/" + str(self.loc[1]) + "/" + str(self.loc[2])  )

if __name__ == '__main__':
    register()
