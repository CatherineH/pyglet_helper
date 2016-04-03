from mock import patch
import sys
import os

test_filename = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(test_filename)
import fake_gl

import_base = "pyglet_helper.objects.box.pyglet.gl"

@patch(import_base)
def test_box_generate_model(fake_gl):
    from pyglet_helper.objects import Box
    box = Box()
    box.generate_model()