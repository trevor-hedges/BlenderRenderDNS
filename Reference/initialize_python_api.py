# Make sure Blender is launched from the Render2018 directory (lib directory?)
# Some of the directories below will need to be updated

import os
import sys

sys.path.append("/home/thedges/Documents/CFM/BlenderRender2018/Render2018")
sys.path.append("/home/thedges/Documents/CFM/BlenderRender2018/Render2018/lib")
sys.path.append("/home/thedges/Documents/CFM/BlenderRender2018/Render2018/lib/Blender")

from lib.Blender.transform_mesh import center_databox
from lib.Blender.scene_config import configure_scene
from lib.Blender.droplet import import_droplet

configure_scene("/home/thedges/Documents/CFM/RenderConfig/bounds-case.cfg","/home/thedges/Documents/CFM/RenderConfig/bounds-render.cfg","/home/thedges/Documents/CFM/Render2017_postGFM/lib/Blender")
import_droplet("/home/thedges/Documents/CFM/RenderOutput/bounds/geometry_data/ply/unsmooth/frame_0.ply", "Obd", (15,15,15), 10, "WaterMaterial5")
