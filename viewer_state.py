from constants import ROTATION_STEP, SCALE_STEP, TRANSLATION_STEP
from math_utils import (
    clamp,
    mat_mul,
    rotation_x,
    rotation_y,
    rotation_z,
    scaling_matrix,
    translation_matrix,
)


class ViewerState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.scale = 1.0
        self.rotation = [0.0, 0.0, 0.0]
        self.translation = [0.0, 0.0, 0.0]
        self.projection = "isometric"
        self.render_mode = "solid"
        self.transform_mode = "rotate"

    def model_matrix(self):
        scale = scaling_matrix(self.scale, self.scale, self.scale)
        rot_x = rotation_x(self.rotation[0])
        rot_y = rotation_y(self.rotation[1])
        rot_z = rotation_z(self.rotation[2])
        trans = translation_matrix(
            self.translation[0], self.translation[1], self.translation[2]
        )
        return mat_mul(trans, mat_mul(rot_z, mat_mul(rot_y, mat_mul(rot_x, scale))))

    def apply_arrow_transform(self, key):
        if self.transform_mode == "translate":
            if key == "left":
                self.translation[0] -= TRANSLATION_STEP
            elif key == "right":
                self.translation[0] += TRANSLATION_STEP
            elif key == "up":
                self.translation[1] += TRANSLATION_STEP
            elif key == "down":
                self.translation[1] -= TRANSLATION_STEP
        elif self.transform_mode == "scale":
            if key in {"up", "right"}:
                self.scale *= SCALE_STEP
            else:
                self.scale /= SCALE_STEP
            self.scale = clamp(self.scale, 0.1, 10.0)
        elif self.transform_mode == "rotate":
            if key == "left":
                self.rotation[1] -= ROTATION_STEP
            elif key == "right":
                self.rotation[1] += ROTATION_STEP
            elif key == "up":
                self.rotation[0] -= ROTATION_STEP
            elif key == "down":
                self.rotation[0] += ROTATION_STEP

    def apply_rotation_axis(self, axis, direction):
        amount = ROTATION_STEP * direction
        if axis == "x":
            self.rotation[0] += amount
        elif axis == "y":
            self.rotation[1] += amount
        elif axis == "z":
            self.rotation[2] += amount
