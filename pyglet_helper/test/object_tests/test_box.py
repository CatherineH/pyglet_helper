from mock import patch
import sys
import os

test_filename = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(test_filename)
import fake_gl


@patch('pyglet.gl', fake_gl)
def test_box_generate_model():
    from pyglet_helper.objects import Box
    box = Box()
    box.generate_model()