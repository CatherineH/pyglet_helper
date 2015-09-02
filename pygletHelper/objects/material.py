# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.util.shader_program import shader_program
from pygletHelper.util.texture import texture

class material(object):
    def __init__(self, translucent = False, shader_program = None):
        self.translucent = translucent
        self.textures = [texture()]
        self.shader = shader_program

    @property
    def textures(self):
        return self._textures
    @textures.setter
    def textures(self, tex):
        self._textures = tex

    @property
    def shader(self):
        if hasattr(self,'_shader') and type(self._shader) == 'shader_program':
            return self._shader.get_source()
        else:
            return None

    @shader.setter
    def shader(self, source):
        if source is not None:
            self._shader = shader_program(source)
        else:
            self._shader = None

    @property
    def translucent(self):
        return self._translucent
    @translucent.setter
    def translucent(self, t):
        self._translucent = t

    def get_shader_program(self):
        if type(self.shader) == shader_program:
            return self.shader.get()
        else:
            return None


class apply_material(object):
    def __init__(self, v, m, material_matrix, sp = None, shader_program = shader_program()):
        self.v = v
        self.m = m
        self.material_matrix = material_matrix
        if sp == None:
            if m:
                sp = shader_program(v, m.shader)
            else:
                sp = shader_program(v, None)
        self.sp = sp
        if not self.m or not sp.ok():
            return
        self.texa = "tex0"
        for t in range(0,self.m.textures.size()):
            if (t and self.v.glext.ARB_multitexture):
                self.v.glext.glActiveTexture(GL_TEXTURE0 + t)
            self.m.textures[t].gl_activate(self.v)
            if self.m.shader and self.v.glext.ARB_shader_objects:
                texa[3] = '0'+t
                self.v.glext.glUniform1iARB( self.m.shader.get_uniform_location( self.v, self.texa ), t )
            if not self.v.glext.ARB_multitexture:
                break

        # For compatibility, set the texture unit back
        if self.m.textures.size() > 1 and self.v.glext.ARB_multitexture:
            self.v.glext.glActiveTexture(GL_TEXTURE0)
        loc = self.m.shader.get_uniform_location( self.v, "model_material" )
        if ( loc >= 0 ):
            self.m.shader.set_uniform_matrix( self.v, self.loc, self.model_material )
        loc = self.m.shader.get_uniform_location( self.v, "light_count" )
        if ( loc >= 0 ):
            self.v.glext.glUniform1iARB( self.loc, self.v.light_count[0] )
        loc = self.m.shader.get_uniform_location( self.v, "light_pos" )
        if ( loc >= 0 and self.v.light_count[0]):
            self.v.light_pos[0] = self.v.glext.glUniform4fvARB( loc, self.v.light_count[0])
        loc = self.m.shader.get_uniform_location( self.v, "light_color" )
        if ( loc >= 0 and self.v.light_count[0] ):
            self.v.light_color[0] = self.v.glext.glUniform4fvARB( loc, self.v.light_count[0])

unshaded = material(shader_program = """
[vertex]
        void main() {
            gl_Position = ftransform();
            gl_FrontColor = gl_Color;
        }
[fragment]
        void main() {
            gl_FragColor = gl_Color;
        }""")
emissive = material( shader_program = """
    [fragment]
    void material_main() {
        float d = dot(normalize(-position), normal);
        d = pow(d * 1.5,.4) * 1.1;
        if (d > 1.0) d = 1.0;
        material_color = object_color * d;
        material_opacity = object_opacity;
    }""")
diffuse = material(shader_program = """
        [fragment]
        void material_main() {
            material_color = lightAt( normalize(normal), normalize(-position), object_color, vec3(0,0,0), 0.0 );
            material_opacity = object_opacity;
        }""")
plastic = material(shader_program = """
        [fragment]
        void material_main() {
            material_color = lightAt( normalize(normal), normalize(-position), object_color, vec3(.8,.8,.8), 64.0 );
            material_opacity = object_opacity;
        }
        """)
rough  = material(shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal + noise3D(tex0, mat_pos, 1.0) * .4;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(N2), normalize(-position),
                                        object_color,
                                        vec3(.5,.5,.5),
                                        16. )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = object_opacity;
        }
        """)
shiny = material( shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal/2.0 + noise3D(tex0, acos(normal/mat_pos), 0.2) * 1.4;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(N2), normalize(position),
                                        object_color,
                                        vec3(1.0,1.0,1.0),
                                        16. )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = object_opacity;
        }
        """)
chrome = material(shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal/2.0 + noise3D(tex0, log((position/35.0+0.5)), 0.2) * 2.4;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(cross(N2,mat_pos)), normalize(-cross(mat_pos,normal)),
                                        object_color*((2.,2.,2.)-gl_LightModel.ambient.rgb),
                                        vec3(0.5,0.5,0.5),
                                        0.2 )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = 1.0;
        }
        """),

ice = material( shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal/2.0 + noise3D(tex0, log2((position/5.791+0.5)), 0.2) * 1.4;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(cross(N2,mat_pos)), normalize(-cross(position,normal)),
                                        vec3(1.0,0.9,1.0),
                                        vec3(0.5,0.5,0.5),
                                        0.1 )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = 0.5;
        }
        """)

glass = material(shader_program = """
        [varying]
        varying vec3 gln;
        [vertex]
        void main(void) {
            basic();
            gln = gl_Normal;
        }
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            // vec3 N2 = normal/1.0 + noise3D(tex0, acos(normal/mat_pos), 0.2) * 2.4;

            material_color = lightAt( normalize(normal), normalize(-position), object_color, vec3(.7,.7,.7), 32.0 );

            material_opacity = 0.4; // dot(cross(gln,-position),mat_pos);
        }
        """)

blazed = material(shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal + noise3D(tex0, sqrt((normal+0.5)/(position+0.5)), 0.2) * 1.4;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(cross(N2,mat_pos)), normalize(-cross(position,normal)),
                                        object_color,
                                        vec3(1.0,1.0,1.0),
                                        16. )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = 1.0;
        }
        """),
silver = material(shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            // Displace the surface normal using a 3D noise function
            vec3 N2 = normal/2.0 + noise3D(tex0, mat_pos*32.0, 1.0) * 0.2;

            // Compute lighting based on the displaced normal
            material_color = lightAt( normalize(N2), normalize(-position),
                                        object_color,
                                        vec3(0.5,0.5,0.5),
                                        0.2 )
                                // TODO hack to reduce ambient
                                - object_color * gl_LightModel.ambient.rgb * .7;

            material_opacity = 1.0;
        }
        """)

wood = material(shader_program = """
        [fragment]
        uniform sampler2D tex0;  // wood cross-section
        uniform sampler3D tex1;  // 3D turbulence

        void material_main() {
            // Compute a position in the 2D cross section texture
            vec2 wood_pos = -.85 * mat_pos.zy +    //< simple rectangular mapping
                            -.10 * mat_pos.x +     //< slight skew to display wood grain on xy and xz surfaces
                            -.05 * noise3D(tex1, mat_pos * .5, 1.).xy;   //< turbulence so grain isn't perfectly straight

            // Look up the color in the texture
            vec3 C = texture2D( tex0, wood_pos ).rgb;

            // Apply lighting
            material_color = lightAt( normalize(normal), normalize(-position),
                                        C*object_color,
                                        vec3(.5,.5,.5),
                                        5. );
            material_opacity = object_opacity;
        }
        """)
marble =material( shader_program = """
        [fragment]
        uniform sampler3D tex0;

        void material_main() {
            vec3 noise = noise3D( tex0, mat_pos, 2.0 );

            // "marble" varies between two colors in a sine wave pattern in y,
            //    displaced heavily by a noise function.
            float a = 0.5 + 0.5*sin( mat_pos.y*16. + noise.x*10. );
            vec3 C = mix( vec3(.4,.3,.3), vec3(1.,1.,1.), a );

            // We are also doing a normal displacement similar to "rough".
            // TODO: Is this desired?  I normally think of marble as smooth!
            vec3 N2 = normal + noise*1.;

            // Modulate the marble color by the object color, and apply lighting
            material_color = lightAt( normalize(N2), normalize(-position), C*object_color, vec3(.8,.8,.8), 100. );
            material_opacity = object_opacity;
        }
        """),
# TODO: fancy earth renderer with atmosphere, gloss map, bump map
earth =material(shader_program = """
        [fragment]
        void material_main() {
            material_color = mat_pos * .5;
            if ( fract( mat_pos.x * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( fract( mat_pos.y * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( fract( mat_pos.z * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( mat_pos.x < 0. || mat_pos.x > 1. ) material_color = vec3(1.,0.8,0.8);
            if ( mat_pos.y < 0. || mat_pos.y > 1. ) material_color = vec3(0.8,1.,0.8);
            if ( mat_pos.z < 0. || mat_pos.z > 1. ) material_color = vec3(0.8,0.8,1.);
            material_opacity = object_opacity;
        }
        """ )
# fancy earth renderer with clouds
BlueMarble = material( shader_program = """
        [fragment]
        void material_main() {
            material_color = mat_pos * .5;
            if ( fract( mat_pos.x * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( fract( mat_pos.y * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( fract( mat_pos.z * 10. + .021 ) < .02 ) material_color *= 0.5;
            if ( mat_pos.x < 0. || mat_pos.x > 1. ) material_color = vec3(1.,0.8,0.8);
            if ( mat_pos.y < 0. || mat_pos.y > 1. ) material_color = vec3(0.8,1.,0.8);
            if ( mat_pos.z < 0. || mat_pos.z > 1. ) material_color = vec3(0.8,0.8,1.);
            material_opacity = object_opacity;
        }
        """ )
bricks = material(shader_program = """
        [fragment]
        void material_main() {
            material_color = mat_pos;
            material_opacity = object_opacity;
        }
        """ )
