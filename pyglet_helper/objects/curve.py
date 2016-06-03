try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from pyglet_helper.objects import ColorArrayPrimitive
from pyglet_helper.util import Rgb


class Curve(ColorArrayPrimitive):
    def __init__(self, color=Rgb()):
        super(Curve, self).__init__(color=color)
        ### since wxPython is not being used, the frame argument is not important for now

    @property
    def degenerate(self):
        return self.count < 2

    def render(self, scene):
        if self.degenerate:
            return
        true_size = self.count
        # Set up the leading and trailing points for the joins.  See
        # glePolyCylinder() for details.  The intent is to create joins that are
        # perpendicular to the path at the last segment.  When the path appears
        # to be closed, it should be rendered that way on-screen.
        # The maximum number of points to display.
        LINE_LENGTH = 1000
        # Data storage for the position and color data (plus room for 3 extra points)
        spos = [3*(LINE_LENGTH+3)]
        tcolor = [3*(LINE_LENGTH+3)] # opacity not yet implemented for curves
        fstep = (float)(self.count-1)/(float)(LINE_LENGTH-1)
        if fstep < 1.0:
            fstep = 1.0
        iptr=0
        pcount=0

        p_i = self.pos.data()
        c_i = self.color.data()

        # Choose which points to display
        fptr = 0.0
        while iptr < self.count and pcount < LINE_LENGTH:
            iptr3 = 3*iptr
            spos[3*pcount] = p_i[iptr3]
            spos[3*pcount+1] = p_i[iptr3+1]
            spos[3*pcount+2] = p_i[iptr3+2]
            tcolor[3*pcount] = c_i[iptr3]
            tcolor[3*pcount+1] = c_i[iptr3+1]
            tcolor[3*pcount+2] = c_i[iptr3+2]
            fptr += fstep
            iptr = (int) (fptr+.5)
            pcount += 1

        # Do scaling if necessary
        scaled_radius = self.radius
        if scene.gcf != 1.0 or scene.gcfvec[0] != scene.gcfvec[1]:
            scaled_radius = self.radius*scene.gcfvec[0]
            for i in range(0, pcount):
                spos[3*i] *= scene.gcfvec[0]
                spos[3*i+1] *= scene.gcfvec[1]
                spos[3*i+2] *= scene.gcfvec[2]

        if self.radius == 0.0:
            gl.glEnableClientState( gl.GL_VERTEX_ARRAY)
            gl.glDisable( gl.GL_LIGHTING)
            # Assume monochrome.
            if self.antialias:
                gl.glEnable( gl.GL_LINE_SMOOTH)

            gl.glVertexPointer( 3, gl.GL_DOUBLE, 0, spos)
            mono = self.adjust_colors( scene, tcolor, pcount)
            if not mono:
                gl.glColorPointer( 3, gl.GL_FLOAT, 0, tcolor)
            gl.glDrawArrays( gl.GL_LINE_STRIP, 0, pcount)
            gl.glDisableClientState( gl.GL_VERTEX_ARRAY)
            gl.glDisableClientState( gl.GL_COLOR_ARRAY)
            gl.glEnable( gl.GL_LIGHTING)
            if self.antialias:
                gl.glDisable( gl.GL_LINE_SMOOTH)
        else:
            self.thickline( scene, spos, tcolor, pcount, scaled_radius)

    def adjust_colors(self, scene, tcolor, pcount):
        mono = self.monochrome(tcolor, pcount)
        if mono:
            # We can get away without using a color array.
            rendered_color = Rgb( tcolor[0], tcolor[1], tcolor[2])
            if scene.anaglyph:
                if scene.coloranaglyph:
                    rendered_color.desaturate().gl_set(self.opacity)
                else:
                    rendered_color.grayscale().gl_set(self.opacity)
            else:
                rendered_color.gl_set(self.opacity)
        else:
            gl.glEnableClientState( gl.GL_COLOR_ARRAY)
            if scene.anaglyph:
                # Must desaturate or grayscale the color.

                for i in range(0, pcount):
                    rendered_color = Rgb( tcolor[3*i], tcolor[3*i+1], tcolor[3*i+2])
                    if scene.coloranaglyph:
                        rendered_color = rendered_color.desaturate()
                    else:
                        rendered_color = rendered_color.grayscale()
                    tcolor[3*i] = rendered_color.red
                    tcolor[3*i+1] = rendered_color.green
                    tcolor[3*i+2] = rendered_color.blue
        return mono

    def monochrome(self, tcolor, pcount):
        first_color = Rgb( tcolor[0], tcolor[1], tcolor[2])
        for nn in range(0, pcount):
            if tcolor[nn*3] != first_color.red:
                return False
            if tcolor[nn*3+1] != first_color.green:
                return False
            if tcolor[nn*3+2] != first_color.blue:
                return False

        return True


