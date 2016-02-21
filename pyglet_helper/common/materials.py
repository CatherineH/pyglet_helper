"""
VPython material tools and definitions
Stable Interfaces:
    materials.unshaded
    materials.diffuse
    materials.plastic
    materials.rough
    materials.wood
    materials.marble
    materials.earth
        Individual named materials.  The exact look of these might change in
        future versions of Visual, but the names should continue to work.
    materials.texture( data, channels=None, mipmap=True,
                       interpolate=True, name="texture" )
        Create a material by "extruding"/projecting a 2D image.
        See VPython documentation for more details.
    materials.loadTGA(file)
    materials.saveTGA(file,data)
        Load and save uncompressed TGA files; typically used to supply the data
        parameter to texture().  file may be a filename or file object.
Unstable interfaces:
    materials.shader( name, shader, version, textures=(), translucent=False )
        This is the low level interface for constructing a material based on
        a GLSL shader program.

        It is not fully documented because it is subject to change in future
        versions.  In particular, it is likely that some or all programs using
        materials.shader() directly will require modification to run in future
        versions of Visual.
        If you come up with really nice new materials, be sure to post them
        to the VPython forum, so that they can be considered for
        incorporation in new versions of Visual.  As well as benefitting other
        users, this will remove from you the burden of updating your shader for
        new versions.
        If you want to learn how to write shaders, look at some of the examples
        below (such as "wood"), and consult the GLSL reference specification
        which is available online.
        To minimize the likelihood that you will have to rewrite your shaders
        for future architectural changes in Visual, avoid accessing the
        built in gl_* variables defined in that specification; instead use
        only normal, position, mat_pos, object_color, and object_opacity as
        inputs and write your output shaded material color to material_color
        and material_opacity.  Many of these are currently simple macros
        expanding to gl_* variables, but in the future their definitions may
        change.  Use lightAt() instead of the light_* uniforms if possible.
    materials.raw_texture( data, interpolate, mipmap )
    materials.tx_turb3
    materials.tx_wood
        raw 2D textures useful only for filling in the textures parameter of
        materials.shader().
"""

from numpy import array, reshape, fromstring, ubyte, zeros, asarray
import os.path
import math

from pyglet_helper.util.texture import Texture
from pyglet_helper.objects.material import Material, unshaded, emissive, diffuse, plastic, rough, shiny, chrome, ice, \
    glass, blazed, silver, wood, marble, earth, BlueMarble, bricks


class RawTexture(Texture):
    def __init__(self, **kwargs):
        Texture.__init__(self)
        for key, value in kwargs.items():
            if key == 'data' and value is None:
                raise RuntimeError, "Cannot nullify a texture by assigning its data to None"
            else:
                self.__setattr__(key, value)


class ShaderMaterial(Material):
    def __init__(self, **kwargs):
        Material.__init__(self)
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        if not hasattr(self, "name"):
            self.name = "no_name"


Lheader = 18  # length of header in targa file


def convert_data(data):
    data = asarray(data)
    if data.dtype != ubyte:
        data = array(255 * data, ubyte)
    if len(data.shape) == 2:
        data = reshape(data, data.shape + (1,))
    return data


def saveTGA(fileid, data):
    data = convert_data(data)
    dims = data.shape
    height = dims[0]
    width = dims[1]
    bytes = dims[2]
    length = width * height * bytes
    attributes = 32  # byte 17; start in upper left
    targa_type = 2  # rgb or rgbo
    if data.dtype.kind == 'u':
        databytes = data.flatten()
    else:
        databytes = 255 * data.flatten()
    if bytes == 1:
        targa_type = 3  # 1 byte per pixel (luminance by default, or opacity)
    elif bytes == 2:  # luminance+opacity
        targa_type = 3  # luminance + opacity (not in the targa spec)
        attributes += 8  # signal presence of 8 bits of opacity
    elif 3 <= bytes <= 4:  # rgb
        if bytes == 4:
            attributes += 8  # signal presence of 8 bits of opacity
        red = databytes[0::bytes].copy()  # make copy; must reverse byte order rgb -> bgr
        databytes[0::bytes] = databytes[2::bytes]  # blue
        databytes[2::bytes] = red
    else:
        raise ValueError("Must have 1, 3, or 4 values per pixel, not %d." % bytes)
    output = zeros(Lheader + length, ubyte)
    output[:Lheader] = [0, 0, targa_type, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        width & 255, width >> 8, height & 255, height >> 8, 8 * bytes, attributes]
    output[Lheader:] = databytes
    if isinstance(fileid, str):
        if fileid[-4:] != ".tga":
            fileid += ".tga"
        fileid = open(fileid, "wb")
    fileid.write(output)
    fileid.close()


def loadTGA(fileid):
    if isinstance(fileid, str):
        if fileid[-4:] != ".tga":
            fileid += ".tga"
        fileid = open(fileid, "rb")
    data = fromstring(fileid.read(), ubyte)
    width = data[12] + 256 * data[13]
    height = data[14] + 256 * data[15]
    bytes = data[16] >> 3
    image = data[Lheader:Lheader + width * height * bytes]
    if 1 <= bytes <= 2:
        image = image.reshape((height, width, bytes))
    elif 3 <= bytes <= 4:
        red = image[0::bytes].copy()  # make copy; must reverse byte order bgr -> rgb
        image[0::bytes] = image[2::bytes]  # blue
        image[2::bytes] = red
        image = image.reshape((height, width, bytes))
    else:
        raise IOError("%s is not a valid targa file." % fileid)
    # Photoshop "save as targa" starts the data in lower left; last byte in header is zero.
    # Visual and POV-Ray start data in upper left; last header byte is nonzero.
    if data[Lheader - 1] == 0:
        image = image[::-1]
    return image

# The following code addresses a problem for those packaging a program using py2exe,
# as reported by Jason Morgan.
import sys

if hasattr(sys, 'frozen'):
    if getattr(sys, 'frozen') == "windows_exe" or getattr(sys, 'frozen') == "console_exe":
        texturePath = "visual\\"
else:
    texturePath = os.path.split(__file__)[0] + "/"
del sys

data = loadTGA(texturePath + "turbulence3")  # the targa file is 512*512*3
tx_turb3 = RawTexture(data=reshape(data, (64, 64, 64, 3)), interpolate=True, mipmap=False)
tx_wood = RawTexture(data=loadTGA(texturePath + "wood"), interpolate=True)
tx_brick = RawTexture(data=loadTGA(texturePath + "brickbump"), interpolate=True)
data_r = loadTGA(texturePath + "random")
tx_random = RawTexture(data=reshape(data_r, (64, 64, 64, 3)), interpolate=True, mipmap=False)


def get_default_channels(data):
    dims = data.shape
    bytes = dims[2]
    if bytes == 1:
        channels = ("luminance",)  # default; else must specify opacity explicitly
    elif bytes == 2:
        channels = ("luminance", "opacity")
    elif bytes == 3:
        channels = ("red", "green", "blue")
    elif bytes == 4:
        channels = ("red", "green", "blue", "opacity")
    else:
        raise ValueError("Must have 1, 3, or 4 values per pixel, not %d." % bytes)
    return channels


def texture(data, channels=None,
            mapping="rectangular", mipmap=True, interpolate=True, name="texture"):
    data = convert_data(data)

    if channels is None:
        channels = get_default_channels(data)
    if len(channels) != data.shape[2]:
        raise ValueError("Channel combination does not match number of values per pixel in data.")
    channel_code = {("luminance",): "luminance",
                    ("opacity",): "opacity",
                    ("luminance", "opacity"): "luminance_opacity",
                    ("red", "green", "blue"): "rgb",
                    ("red", "green", "blue", "opacity"): "rgbo"
    }.get(tuple(channels), None)
    if not channel_code:
        raise ValueError("Unsupported channel combination: " + repr(channels))

    raw_tx = RawTexture(data=data,
                         type=channel_code,
                         mipmap=mipmap,
                         interpolate=interpolate,
                         clamp=(mapping in ("rectangular", "sign")))  # < TODO: clamp y for spherical

    p2x, p2y = 1., 1.
    while p2x < data.shape[1]: p2x *= 2
    while p2y < data.shape[0]: p2y *= 2

    if interpolate:
        # We want non-wrapping axes to end at pixel centers, not pixel edges
        cax, cay = (-0.5 / p2x, -0.5 / p2y )
    else:
        # Trim just enough off the edges to avoid broken wrapping
        cax, cay = (-0.01 / p2x, -0.01 / p2y)

    # Adjustment for interpolation, rectangular, and non-power-of-two textures
    m = max(data.shape[1], data.shape[0])
    adjust = ( (data.shape[1] + m) / 2. / p2x + cax, (data.shape[0] + m) / 2. / p2y + cay,
               -2 * cax - m / p2x, -2 * cay - m / p2y,
               -cax, -cay,
               data.shape[1] / p2x + cax, data.shape[0] / p2y + cay )

    # TODO: Creating shaders here is inefficient if there are lots of textures.
    # What we want is multiple materials sharing one shader program, with uniforms, but that's not
    # supported by the core at the moment.
    if mapping == "rectangular":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent="opacity" in channels,
            shader="""
                [fragment]
                uniform sampler2D tex0;

                void material_main(void) {
                    vec4 C = texture2D( tex0, clamp(vec2(%f,%f) + vec2(%f,%f)*mat_pos.zy, vec2(%f,%f), vec2(%f,%f)) );
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb*object_color,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a * object_opacity;
                }""" % adjust)
    elif mapping == "spherical":
        if p2x != data.shape[1] or p2y != data.shape[0]:
            raise ValueError("spherical textures must currently be 2**N x 2**M.")
        raw_tx.mipmap = False
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent="opacity" in channels,
            shader="""
                [fragment]
                uniform sampler2D tex0;

                void material_main(void) {
                    vec2 tp = vec2( atan( mat_pos.x-0.5, mat_pos.z-0.5 ) * (0.5 / 3.14159) + 0.5,
                                    0.5 + atan( (mat_pos.y-0.5) / length( mat_pos.xz - 0.5 ) ) * %f );
                    vec4 C = texture2D( tex0, tp );
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb*object_color,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a * object_opacity;
                }""" % (1.0 / math.pi * (-2 * cay - data.shape[0] / p2y)))
    elif mapping == "sign":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float front_face;
                [vertex]
                void main(void) {
                    basic();
                    if (gl_Normal.x > .001) front_face = 1.0;
                    else front_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( front_face > 0.5 ) {
                        C = texture2D( tex0, clamp(vec2(%f,%f) + vec2(%f,%f)*mat_pos.zy, vec2(%f,%f), vec2(%f,%f)) );
                        // Texture is decaled over opaque color
                        C.rgb = mix( object_color, C.rgb, C.a );
                        C.a = object_opacity;
                    } else
                        C = gl_Color;
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a;
                }""" % adjust)
    elif mapping == "top":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.y) > 0.5) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face > 0.9999 ) C = vec4(texture2D( tex0, vec2(-mat_pos.x, mat_pos.z) ));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""")


    elif mapping == "bottom":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.y) > 0.5) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face < 0.0001 ) C = vec4(texture2D( tex0, mat_pos.xz ));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""")
    elif mapping == "front":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.x) > 0.5) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face > 0.9999 ) C = vec4(texture2D( tex0, -mat_pos.yz ));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""")

    elif mapping == "left":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.z) > 0.9999) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face > 0.9999 ) C = vec4(texture2D( tex0, vec2(-mat_pos.x, mat_pos.y)));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""")

    elif mapping == "right":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.z) < 0.0001) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face > 0.9999 ) C = vec4(texture2D( tex0, -mat_pos.yx));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""")

    elif mapping == "back":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                [vertex]
                void main(void) {
                    basic();
                    if (float(mat_pos.x) < 0.0001) top_face = 1.0;
                    else top_face = 0.0;
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    /* %f, %f, %f, %f, %f, %f, %f, %f */
                    if ( top_face > 0.9999 ) C = vec4(texture2D( tex0, vec2(-mat_pos.y, mat_pos.z)));
                    else C = vec4(object_color[0], object_color[1], object_color[2], object_opacity);
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a*object_opacity;
                }""" % adjust)

    elif mapping == "cubic":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                varying float front_face;
                varying float side_face;
                [vertex]
                void main(void) {
                    basic();
                    if (gl_Normal.y > .001) top_face = 1.0;
                    else {
                        if (gl_Normal.y <-0.001) top_face = 1.0;
                        else top_face = 0.0;
                    }
                    if (gl_Normal.x > .001) front_face = 1.0;
                    else {
                        if (gl_Normal.x <-0.001) front_face = 1.0;
                        else front_face = 0.0;
                    }
                    if (gl_Normal.z > .001) side_face = 1.0;
                    else {
                        if (gl_Normal.z <-0.001) side_face = 1.0;
                        else side_face = 0.0;
                    }
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face > 0. ) C = texture2D( tex0, mat_pos.xz + %f );
                    else {
                        if ( front_face > 0. ) C = texture2D( tex0, mat_pos.zy + %f );
                        else {
                            if ( side_face > 0. ) C = texture2D( tex0, mat_pos.xy + %f);
                            else
                                C = gl_Color;
                        }
                    }
                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a;
                }""" % (
            (1.0 * (data.shape[0] / p2x) + 1, 1.0 * (data.shape[1] / p2y) + 1, 1.0 * (data.shape[1] / p2y) + 1)))
    elif mapping == "hollow_box":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                varying float front_face;
                [vertex]
                void main(void) {
                    basic();
                    if (gl_Normal.y > .001) top_face = 1.0;
                    else {
                        if (gl_Normal.y <-0.001) top_face = 1.0;
                        else top_face = 0.0;
                    }
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face < 0.5 ) {
                        vec2 tp = vec2( atan( mat_pos.x-0.5, mat_pos.z-0.5 ) * 0.5 ,
                                         atan( (mat_pos.y-0.5) ) * %f );
                        C = texture2D( tex0, tp );
                    } else {
                        C = gl_Color;
                        C.a = 0.5;
                        }

                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = C.a;
                }""" % 1.0),
    elif mapping == "cylinder":
        return shader(
            name=name,
            version=5.00,
            textures=[raw_tx],
            translucent=False,
            shader="""
                [varying]
                varying float top_face;
                varying float front_face;
                [vertex]
                void main(void) {
                    basic();
                    if (gl_Normal.y > .001) top_face = 1.0;
                    else {
                        if (gl_Normal.y <-0.001) top_face = 1.0;
                        else top_face = 0.0;
                    }
                }
                [fragment]
                uniform sampler2D tex0;
                void material_main(void) {
                    vec4 C;
                    if ( top_face < 0.5 ) {
                        vec2 tp = vec2( atan( mat_pos.x-0.5, mat_pos.z-0.5 ) * 0.5 ,
                                         atan( (mat_pos.y-0.5) ) * %f );
                        C = texture2D( tex0, tp );
                    } else {
                        vec2 tp = vec2( mat_pos.x-0.5, mat_pos.y-0.5 );
                        C = texture2D( tex0, tp );
                        }

                    material_color = lightAt( normalize(normal), normalize(-position),
                                                C.rgb,
                                                vec3(0.,0.,0.),
                                                0. );
                    material_opacity = object_opacity;
                }""" % 1.0)
    else:
        raise ValueError("Unknown mapping type: " + str(mapping))


library = """
[vertex]
    uniform mat4 model_material;  // object space -> material position
    void basic(void)
    {
        position = vec3(gl_ModelViewMatrix * gl_Vertex);
        normal = normalize(gl_NormalMatrix * gl_Normal);
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        gl_FrontColor = gl_Color;
        mat_pos = vec3( model_material * gl_Vertex );
    }
[varying]
    #version 110
    // These are available to fragment shaders and must be set by vertex shaders.

    varying vec3 normal;          // eye space surface normal
    varying vec3 position;        // eye space surface position
    varying vec3 mat_pos;         // surface material position in [0,1]^3
    #define VPYTHON_SHADER_VERSION 400
[fragment]
    // Available inputs (see also the varying section)

    #define object_color gl_Color.rgb // the .color attribute of the object being rendered
    #define object_opacity gl_Color.a // the .opacity attribute of the object being rendered
    uniform int light_count;
    uniform vec4 light_pos[8];
    uniform vec4 light_color[8];
    // Outputs of a material_main() function
    #define material_color gl_FragColor.rgb
    #define material_opacity gl_FragColor.a
    // Return lit surface color based on the given surface properties and the lights
    //   specified by the light_* uniforms.
    vec3 lightAt( vec3 normal, vec3 to_eye, vec3 diffuse_color, vec3 specular_color, float shininess )
    {
        vec3 color = gl_LightModel.ambient.rgb * diffuse_color;
        // All this ugliness is to deal with the need of Geforce 7xxx (and probably similar generation
        // ATI cards) to unroll loops at compile time.  If you are trying to understand this code, look
        // at just the else case.
        int count = light_count;
        if (count <= 2) {
            for(int i=0; i<2; i++) {
                if (i<count) {
                    vec3 L = normalize( light_pos[i].xyz - position*light_pos[i].w );
                    color += (light_color[i].rgb * max(dot(normal,L), 0.0))*diffuse_color;
                    if (shininess != 0.0) {
                        vec3 R = -reflect(L,normal);
                        color += specular_color * light_color[i].rgb * pow(max(dot(R,to_eye),0.0),shininess);
                    }
                }
            }
        } else if (count <= 4) {
            for(int i=0; i<4; i++) {
                if (i<count) {
                    vec3 L = normalize( light_pos[i].xyz - position*light_pos[i].w );
                    color += (light_color[i].rgb * max(dot(normal,L), 0.0))*diffuse_color;
                    if (shininess != 0.0) {
                        vec3 R = -reflect(L,normal);
                        color += specular_color * light_color[i].rgb * pow(max(dot(R,to_eye),0.0),shininess);
                    }
                }
            }
        } else {
            for(int i=0; i<8; i++) {
                if (i<count) {
                    vec3 L = normalize( light_pos[i].xyz - position*light_pos[i].w );
                    color += (light_color[i].rgb * max(dot(normal,L), 0.0))*diffuse_color;
                    if (shininess != 0.0) {
                        vec3 R = -reflect(L,normal);
                        color += specular_color * light_color[i].rgb * pow(max(dot(R,to_eye),0.0),shininess);
                    }
                }
            }
        }

        return color;
    }
    vec3 noise3D( sampler3D tex, vec3 mat_pos, const float second_octave_scale ) {
        const float octave = 8.;
        return texture3D( tex, mat_pos).rgb + texture3D( tex, mat_pos*octave ).rgb * (second_octave_scale / octave);
    }
    // Eventually there will probably be an "outer" main function which will call material_main
    #define material_main main
"""


def shader(name, shader, version, library=library, **kwargs):
    if isinstance(version, tuple):
        min_version, max_version = version
    else:
        min_version, max_version = version, version
    if max_version < 5.00 or min_version >= 5.10:
        raise ValueError("shader version " + str(version) + " not supported.")
    if shader.find("[vertex]") < 0 and library:
        shader += """
            [vertex]
            void main() {
                basic();
            }"""
    shader = library + "\n".join([l.strip() for l in shader.split("\n")])
    return ShaderMaterial(name=name, shader=shader, **kwargs)


materials = [unshaded, emissive, diffuse, plastic, rough, shiny, chrome, ice,
             glass, blazed, silver, wood, marble, earth, BlueMarble, bricks]

