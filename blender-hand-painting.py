import bpy
import bgl
import blf
import math
import cv2
import os
import sys

# TODO: Load other modules without this hax
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from trackers import PointerTracker
from bpy.props import IntProperty, FloatProperty
from bpy_extras import view3d_utils

class HandDrawOperator(bpy.types.Operator):
    bl_idname = 'gpencil.hand_draw'
    bl_label = 'Hand Draw Modal Operator'

    _timer = None

    def modal(self, context, event):
        if self.debug is True:
            context.area.tag_redraw()

        if event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'TIMER':

            if self.video_capture.isOpened():
                rval, image = self.video_capture.read()
            else:
                error('Video capture is closed')
                return {'CANCELLED'}

            self.tracker.update(image)
            if len(self.tracker.pointers) > 0:
                # TODO: move to tracer
                region = bpy.context.region
                region3d = bpy.context.space_data.region_3d
                pos_x, pos_y = get_pointer_pos(self.tracker.pointers[0].rect, image, region.width, region.height)

                if self.prev_pos_x is None or self.prev_pos_y is None:
                    self.prev_pos_x = pos_x
                    self.prev_pos_y = pos_y
                    view_vector = view3d_utils.region_2d_to_vector_3d(region, region3d, [pos_x, pos_y])
                    self.last_pos = view3d_utils.region_2d_to_location_3d(region, region3d, [pos_x, pos_y], view_vector)
                    return {'PASS_THROUGH'}

                if math.fabs(self.prev_pos_x - pos_x) > 0.2 * region.width or math.fabs(self.prev_pos_y - pos_y) > 0.2 * region.height :
                    self.prev_pos_x = None
                    self.prev_pos_y = None
                    self.last_pos = None
                    return {'PASS_THROUGH'}

                self.prev_pos_x = pos_x
                self.prev_pos_y = pos_y

                self.mouse_pos = [pos_x, pos_y]
                if self.debug:
                    print('[INFO]: Position <{}, {}>'.format(pos_x, pos_y))
                view_vector = view3d_utils.region_2d_to_vector_3d(region, region3d, self.mouse_pos)
                self.loc = view3d_utils.region_2d_to_location_3d(region, region3d, self.mouse_pos, view_vector)

                stroke = get_stroke()
                stroke.points.add(count = 2)
                stroke.points[0].co = (self.last_pos)
                stroke.points[1].co = (self.loc)
                self.last_pos = self.loc

        return {'PASS_THROUGH'}

    def execute(self, context):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        self.tracker = PointerTracker()
        self.video_capture = cv2.VideoCapture(0)
        self.mouse_pos = [0, 0]
        self.last_pos = [0, 0, 0]
        self.loc = [0, 0, 0]
        self.prev_pos_x = None
        self.prev_pos_y = None

        self.debug = True

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self.viceo_capture.close()

def error(msg):
    print('[ERROR]: {msg}'.format(msg=msg))

def get_pointer_pos(pointer_rect, image, viewport_x, viewport_y):
    pointer_x, pointer_y, pointer_w, pointer_h = pointer_rect
    image_w, image_h, image_channels = image.shape

    pos_x_abs = pointer_x + 0.5 * pointer_w
    pos_y_abs = pointer_y + 0.5 * pointer_h

    pos_x_view = viewport_x * (1 - ((pointer_x + 0.5 * pointer_w) / image_w))
    pos_y_view = viewport_y * (1 - ((pointer_y + 0.5 * pointer_h) / image_h))

    return pos_x_view, pos_y_view

def get_stroke():
    sc = bpy.context.scene

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
