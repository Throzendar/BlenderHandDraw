import bpy
import bgl
import blf

from bpy_extras import view3d_utils


def draw_callback_px(self, context):
    font_id = 0
    blf.position(font_id, 15, 100, 0)
    blf.size(font_id, 12, 72)
    blf.draw(font_id, "Mouse position: " + str(self.mouse_pos[0]) + "/" + str(self.mouse_pos[1]) )
    blf.position(font_id, 15, 115, 0)
    blf.draw(font_id, "3D position from " + self.object.name + ": " + str(self.loc[0]) + "/" + str(self.loc[1]) + "/" + str(self.loc[2])  )

class ModalDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':

            #Get the mouse position thanks to the event            
            self.mouse_pos = [event.mouse_region_x, event.mouse_region_y]

            #Contextual active object, 2D and 3D regions
            self.object = bpy.context.object
            region = bpy.context.region
            region3D = bpy.context.space_data.region_3d

            #The direction indicated by the mouse position from the current view
            view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
            #The 3D location in this direction
            self.loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, view_vector)
            #The 3D location converted in object local coordinates
            self.loc = self.object.matrix_world.inverted() * self.loc

        elif event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            #Keeps mouse position current 3D location and current object for the draw callback
            #(not needed to make it self attribute if you don't want to use the callback)
            self.mouse_pos = [0,0]
            self.loc = [0,0,0]
            self.object = None

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)

if __name__ == "__main__":
    register()
