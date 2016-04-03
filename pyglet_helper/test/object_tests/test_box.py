from mock import patch

from pyglet_helper.test import fake_gl

import_base = "pyglet_helper.objects.box.pyglet.gl"


@patch(import_base)
def test_box_generate_model(fake_gl):
    from pyglet_helper.objects import Box
    box = Box()
    box.generate_model()