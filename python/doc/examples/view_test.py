import os
import sys
filename = os.path.dirname(os.path.realpath(__file__))
filename = filename.replace("doc/examples", "src")
sys.path.append(filename)

from objects.renderable import view

scene = view()