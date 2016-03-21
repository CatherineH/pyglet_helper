""" pyglet_helper.material contains an object for describing materials which
can be applied to objects
"""
from pyglet_helper.util import ShaderProgram, Texture


class Material(object):
    """
     A Material object, used for storing and handling shader programs.
    """
    def __init__(self, translucent=False, shader_program=None):
        """

        :param translucent:
        :type translucent: bool
        :param shader_program: The GLSL (Graphics library shader language) code
         to be executed).
        :type shader_program: str
        :return:
        """

        self._textures = None
        self._shader = None
        self._translucent = None
        self.translucent = translucent
        self.textures = [Texture()]
        self.shader = shader_program

    @property
    def textures(self):
        """
        Gets the material's texture
        :return: the texture
        """
        return self._textures

    @textures.setter
    def textures(self, new_texture):
        """
        Sets the material's texture
        :param new_texture: the new texture
        """
        self._textures = new_texture

    @property
    def shader(self):
        """
        Gets the shader program, if it exists
        :return: the shader program
        :rtype: pyglet_helper.util.ShaderProgram
        """
        if hasattr(self, '_shader') and type(self._shader) == 'shader_program':
            return self._shader
        else:
            return None

    @shader.setter
    def shader(self, source):
        """
        Sets the shader source
        :param source: the source of a new shader program
        :type source: str
        """
        if source is not None:
            self._shader = ShaderProgram(source)
        else:
            self._shader = None

    @property
    def translucent(self):
        """
        Gets the translucence value of the material
        :return: the translucence value
        :rtype: float
        """
        return self._translucent

    @translucent.setter
    def translucent(self, new_translucent):
        """
        Sets the translucence value of the material
        :param new_translucent: the translucence value
        :type new_translucent: float
        """
        self._translucent = new_translucent

    def get_shader_program(self):
        """
        Gets the current ShaderProgram
        """
        if type(self.shader) == ShaderProgram:
            return self.shader.get()
        else:
            return None


UNSHADED = Material(shader_program="""
[vertex]
        void main() {
            gl_Position = ftransform();
            gl_FrontColor = gl_Color;
        }
[fragment]
        void main() {
            gl_FragColor = gl_Color;
        }""")
EMISSIVE = Material(shader_program="""
    [fragment]
    void material_main() {
        float d = dot(normalize(-position), normal);
        d = pow(d * 1.5,.4) * 1.1;
        if (d > 1.0) d = 1.0;
        material_color = object_color * d;
        material_opacity = object_opacity;
    }""")
DIFFUSE = Material(shader_program="""
        [fragment]
        void material_main() {
            material_color = lightAt( normalize(normal), normalize(-position), object_color, vec3(0,0,0), 0.0 );
            material_opacity = object_opacity;
        }""")
PLASTIC = Material(shader_program="""
        [fragment]
        void material_main() {
            material_color = lightAt( normalize(normal), normalize(-position), object_color, vec3(.8,.8,.8), 64.0 );
            material_opacity = object_opacity;
        }
        """)
ROUGH = Material(shader_program="""
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
SHINY = Material(shader_program="""
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
CHROME = Material(shader_program="""
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

ICE = Material(shader_program="""
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

GLASS = Material(shader_program="""
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

BLAZED = Material(shader_program="""
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
SILVER = Material(shader_program="""
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

WOOD = Material(shader_program="""
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
MARBLE = Material(shader_program="""
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
EARTH = Material(shader_program="""
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
        """)
# fancy earth renderer with clouds
BLUEMARBLE = Material(shader_program="""
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
        """)
BRICKS = Material(shader_program="""
        [fragment]
        void material_main() {
            material_color = mat_pos;
            material_opacity = object_opacity;
        }
        """)
