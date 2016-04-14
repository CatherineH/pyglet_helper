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
    materials.load_tga(file)
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

from numpy import array, reshape, fromstring, ubyte, asarray
import os.path
import sys

from pyglet_helper.util.texture import Texture
from pyglet_helper.objects.material import Material, UNSHADED, EMISSIVE, \
    DIFFUSE, PLASTIC, ROUGH, SHINY, CHROME, ICE, GLASS, BLAZED, SILVER, \
    WOOD, MARBLE, EARTH, BLUEMARBLE, BRICKS


class RawTexture(Texture):
    """
    An extension of the pyglet_helper.util.Texture object to allow for
    arbitrary input data
    """
    def __init__(self, **kwargs):
        Texture.__init__(self)
        for key, value in kwargs.items():
            if key == 'data' and value is None:
                raise ValueError("Cannot nullify a texture by assigning its "
                                   "data to None")
            else:
                self.__setattr__(key, value)


class ShaderMaterial(Material):
    """
    An extension of the pyglet_helper.object.Material object to allow for
    arbitrary input data
    """
    def __init__(self, **kwargs):
        Material.__init__(self)
        for key, value in kwargs.items():
            self.__setattr__(key, value)
        if not hasattr(self, "name"):
            self.name = "no_name"


def convert_data(data):
    """
    Convert an input data object into a numpy array of unsigned bytes
    :param data:
    :return:
    """
    data = asarray(data)
    if data.dtype != ubyte:
        data = array(255 * data, ubyte)
    if len(data.shape) == 2:
        data = reshape(data, data.shape + (1,))
    return data


def load_tga(fileid):
    """
    Load a TGA image file to use as a texture
    :param fileid: the filename of image
    :type fileid: str
    :return: image data
    """
    header_length = 18 # length of header in targa file
    if isinstance(fileid, str):
        if fileid[-4:] != ".tga":
            fileid += ".tga"
        fileid = open(fileid, "rb")
    data = fromstring(fileid.read(), ubyte)
    width = data[12] + 256 * data[13]
    height = data[14] + 256 * data[15]
    _bytes = data[16] >> 3
    image = data[header_length:header_length + width * height * _bytes]
    if 1 <= _bytes <= 2:
        image = image.reshape((height, width, _bytes))
    elif 3 <= _bytes <= 4:
        # make copy; must reverse byte order bgr -> rgb
        red = image[0::_bytes].copy()
        image[0::_bytes] = image[2::_bytes]  # blue
        image[2::_bytes] = red
        image = image.reshape((height, width, _bytes))
    else:
        raise IOError("%s is not a valid targa file." % fileid)
    # Photoshop "save as targa" starts the data in lower left;
    # last byte in header is zero.
    # Visual and POV-Ray start data in upper left; last header byte is nonzero.
    if data[header_length - 1] == 0:
        image = image[::-1]
    return image

# The following code addresses a problem for those packaging a program using
# py2exe, as reported by Jason Morgan.

TEXTURE_PATH = ""

if hasattr(sys, 'frozen'):
    if getattr(sys, 'frozen') == "windows_exe" or getattr(sys, 'frozen') == \
            "console_exe":
        TEXTURE_PATH = "visual\\"
else:
    TEXTURE_PATH = os.path.split(__file__)[0] + "/"

TURBULENCE3_DATA = load_tga(str(TEXTURE_PATH) + "turbulence3")  # the targa
# file is 512*512*3
TX_TURB3 = RawTexture(data=reshape(TURBULENCE3_DATA, (64, 64, 64, 3)),
                      interpolate=True,
                      mipmap=False)
TX_WOOD = RawTexture(data=load_tga(TEXTURE_PATH + "wood"), interpolate=True)
TX_BRICK = RawTexture(data=load_tga(TEXTURE_PATH + "brickbump"),
                      interpolate=True)
DATA_R = load_tga(TEXTURE_PATH + "random")
TX_RANDOM = RawTexture(data=reshape(DATA_R, (64, 64, 64, 3)), interpolate=True,
                       mipmap=False)

LIBRARY = open(os.path.join(os.path.dirname(__file__), "library.txt"),
               "r").read()


def shader(name, _shader, version, library=LIBRARY, **kwargs):
    """
    Create a shader material by reading in from the library
    :param name: the name of the shader program in the library to select
    :type name: str
    :param _shader: the existing shader to read from, can be empty
    :type _shader: str
    :param version:
    :param library: the library to draw from
    :param kwargs:
    :return:
    """

    if isinstance(version, tuple):
        min_version, max_version = version
    else:
        min_version, max_version = version, version
    if max_version < 5.00 or min_version >= 5.10:
        raise ValueError("shader version " + str(version) + " not supported.")
    if _shader.find("[vertex]") < 0 and library:
        _shader += """
            [vertex]
            void main() {
                basic();
            }"""
    _shader = library + "\n".join([l.strip() for l in _shader.split("\n")])
    return ShaderMaterial(name=name, shader=_shader, **kwargs)


MATERIALS = [UNSHADED, EMISSIVE, DIFFUSE, PLASTIC, ROUGH, SHINY, CHROME, ICE,
             GLASS, BLAZED, SILVER, WOOD, MARBLE, EARTH, BLUEMARBLE, BRICKS]