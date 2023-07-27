import numpy as np
import trimesh
import pyrender
import pyglet
import transforms3d as t3d
import math


class MyViewer(pyrender.Viewer):
    def __init__(self, scene, viewport_size=None,
                 render_flags=None, viewer_flags=None,
                 registered_keys=None, run_in_thread=False, **kwargs):
        super().__init__(scene, viewport_size,
                 render_flags, viewer_flags,
                 registered_keys, run_in_thread, **kwargs)
        self.ctrl_down = False
        self.shift_down = False

    def register_rotate_node(self, node, init_pose):
        self.rotate_node = node
        self.rotate_pose = init_pose

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.LCTRL:
            self.ctrl_down = False
        elif symbol == pyglet.window.key.LSHIFT:
            self.shift_down = False

    def on_key_press(self, symbol, modifiers):
        rotation = None
        theta = 1 / 18 * math.pi
        if self.ctrl_down:
            theta = -theta

        if symbol == pyglet.window.key.LEFT:
            if not self.shift_down:
                rotation = t3d.axangles.axangle2mat(axis=[1, 0, 0], angle=theta)
            else:
                rotation = t3d.axangles.axangle2mat(axis=self.rotate_pose[:3, 0], angle=theta)
        elif symbol == pyglet.window.key.DOWN:
            if not self.shift_down:
                rotation = t3d.axangles.axangle2mat(axis=[0, 1, 0], angle=theta)
            else:
                rotation = t3d.axangles.axangle2mat(axis=self.rotate_pose[:3, 1], angle=theta)
        elif symbol == pyglet.window.key.RIGHT:
            if not self.shift_down:
                rotation = t3d.axangles.axangle2mat(axis=[0, 0, 1], angle=theta)
            else:
                rotation = t3d.axangles.axangle2mat(axis=self.rotate_pose[:3, 2], angle=theta)
        elif symbol == pyglet.window.key.UP:
            rotation = np.eye(3)
            self.rotate_pose[:3, :3] = np.eye(3)
        elif symbol == pyglet.window.key.LCTRL:
            self.ctrl_down = True
        elif symbol == pyglet.window.key.LSHIFT:
            self.shift_down = True
        else:
            super().on_key_press(symbol, modifiers)

        if rotation is not None:
            self.rotate_pose[:3, :3] = np.matmul(rotation, self.rotate_pose[:3, :3])
            self.render_lock.acquire()
            self.scene.set_pose(self.rotate_node, self.rotate_pose)
            self.render_lock.release()


scene = pyrender.Scene(ambient_light=[0.2, 0.2, 0.2], bg_color=[0.5, 0.3, 0.3])
obj = trimesh.load('asset/airplane.stl')
obj = pyrender.Mesh.from_trimesh(obj)
light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
cam = pyrender.PerspectiveCamera(yfov=np.pi / 2.0, aspectRatio=2, znear=0.01, zfar=100)
light_pose = np.array([[1, 0, 0, 0.1],
                       [0, 1, 0, 0.1],
                       [0, 0, 1, 0.1],
                       [0, 0, 0, 1]])
scene.add(light, pose=light_pose)

cam_pose = np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0.2],
                     [0, 0, 0, 1]])
scene.add(cam, pose=cam_pose)

obj_pose = np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])
obj_node = scene.add(obj, pose=obj_pose, name='obj')

viewer = MyViewer(scene, use_raymond_lighting=True, run_in_thread=True)
viewer.register_rotate_node(obj_node, obj_pose.astype(float).copy())
