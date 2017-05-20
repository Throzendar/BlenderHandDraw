import bpy
import bgl
import blf
import math
import cv2
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)


from trackers import FaceTracker
from bpy.props import IntProperty, FloatProperty
from bpy_extras import view3d_utils

class HandDrawOperator(bpy.types.Operator):
    bl_idname = 'gpencil.hand_draw'
    bl_label = 'Hand Draw Modal Operator'

    _timer = None

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        elif event.type == 'TIMER':
            print('[INFO]: Checking input')

            if self.video_capture.isOpened():
                print('[INFO]: Video capture is open')
                rval, frame = self.video_capture.read()
            else:
                print('[INFO]: Video capture is closed')
                rval = False

            if rval:
                print('[INFO]: Updating position')
                image = frame
                self.face_tracker.update(image)
                if len(self.face_tracker._faces) > 0:
                    x, y, w, h = self.face_tracker._faces[0].faceRect
                    im_y, im_x, channels = image.shape

                    region = bpy.context.region
                    region3d = bpy.context.space_data.region_3d

                    pos_x = region.width * (1 - ((x + 0.5 * w) / im_x))
                    pos_y = region.height * (1 - ((y + 0.5 * h) / im_y))

                    pos_x_a = x + 0.5 * w
                    pos_y_a = y + 0.5 * h

                    if self.pos_x_a is None:
                        self.pos_x_a = pos_x_a
                    if self.pos_y_a is None:
                        self.pos_y_a = pos_y_a

                    if math.fabs(self.pos_x_a - pos_x_a) > 0.2 * im_x:
                        return {'PASS_THROUGH'}
                    if math.fabs(self.pos_y_a - pos_y_a) > 0.2 * im_y:
                        return {'PASS_THROUGH'}

                    self.pos_x_a = pos_x_a
                    self.pos_y_a = pos_y_a

                    self.mouse_pos = [pos_x, pos_y]
                    print('[INFO]: Position <{}, {}>'.format(pos_x, pos_y))
                    view_vector = view3d_utils.region_2d_to_vector_3d(region, region3d, self.mouse_pos)
                    self.loc = view3d_utils.region_2d_to_location_3d(region, region3d, self.mouse_pos, view_vector)

                    stroke = get_stroke()
                    stroke.points.add(count = 2)
                    stroke.points[0].co = (self.last_pos)
                    stroke.points[1].co = (self.loc)
                    self.last_pos = self.loc
            else:
                print('Shit...')


        return {'PASS_THROUGH'}

    def execute(self, context):
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

        self._timer = context.window_manager.event_timer_add(0.1, context.window)
        self.counter = 0
        self.mouse_pos = [0, 0]
        self.last_pos = [0, 0, 0]
        self.loc = [0, 0, 0]
        self.pos_x_a = None
        self.pos_y_a = None

        self.face_tracker = FaceTracker()
        print('[INFO]: Opening video capture')
        self.video_capture = cv2.VideoCapture(0)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self.viceo_capture.close()

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
