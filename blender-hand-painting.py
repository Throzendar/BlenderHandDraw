import bpy, math

from bpy.props import IntProperty, FloatProperty

class HandDrawOperator(bpy.types.Operator):
    bl_idname = 'gpencil.hand_draw'
    bl_label = 'Hand Draw Modal Operator'

    #def execute(self, context):
    #    str = get_stroke()
    #    # Number of stroke points
    #    strokeLength = 500

    #    # Add points
    #    str.points.add(count = strokeLength )

    #    pi, twopi = math.pi, 2*math.pi

    #    theta = [20 * twopi * i / strokeLength for i in range(strokeLength)]

    #    mean  = sum(theta)/float(len(theta))

    #    theta = [th - mean for th in theta]

    #    r = [4 - 2*math.cos(0.1*th) for th in theta]

    #    y = [th/twopi for th in theta]
    #    x = [a*math.cos(b) for a, b in zip(r, theta)]
    #    z = [a*math.sin(b) for a, b in zip(r, theta)]

    #    krazy_koil_points = list(zip(x, y, z))

    #    points = str.points
    #    for i, point in enumerate(points):
    #        points[i].co = krazy_koil_points[i]
    #    return {'FINISHED'}

    first_mouse_x = IntProperty()
    first_mouse_y = IntProperty()
    counter = 0

    def modal(self, context, event):
        self.counter += 1

        if self.counter == 10:
            stroke = get_stroke()

            stroke.points.add(count = 2)
            print(len(stroke.points))

            print(event.mouse_x)
            print(event.mouse_y)
            print(self.first_mouse_x)
            print(self.first_mouse_y)
            stroke.points[0].co = (event.mouse_x, event.mouse_y, 0)
            stroke.points[1].co = (self.first_mouse_x, self.first_mouse_y, 0)


            self.first_mouse_x = event.mouse_x
            self.first_mouse_y = event.mouse_y
            self.counter = 0

        if event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.first_mouse_x = event.mouse_x
        self.first_mouse_y = event.mouse_y

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

if __name__ == '__main__':
    register()
