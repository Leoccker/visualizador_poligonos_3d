import math

# Type aliases for clarity
Vec3 = tuple[float, float, float]
Mat3 = list[list[float]]
Mat4 = list[list[float]]


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


# ---------------------------------------------------------------------------
# Vector math
# ---------------------------------------------------------------------------

def vec_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_length(v: Vec3) -> float:
    return math.sqrt(vec_dot(v, v))


def vec_scale(v: Vec3, scalar: float) -> Vec3:
    return (v[0] * scalar, v[1] * scalar, v[2] * scalar)


def vec_normalize(v: Vec3) -> Vec3:
    length = vec_length(v)
    if length == 0:
        return (0.0, 0.0, 1.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def centroid(points: list[Vec3]) -> Vec3:
    if not points:
        return (0.0, 0.0, 0.0)
    total = (0.0, 0.0, 0.0)
    for point in points:
        total = vec_add(total, point)
    return (total[0] / len(points), total[1] / len(points), total[2] / len(points))


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def rgb_to_hex(rgb: tuple[int, ...]) -> str:
    r = int(clamp(rgb[0], 0, 255))
    g = int(clamp(rgb[1], 0, 255))
    b = int(clamp(rgb[2], 0, 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def kd_to_rgb(kd: Vec3) -> tuple[int, int, int]:
    return tuple(int(clamp(channel, 0.0, 1.0) * 255) for channel in kd)


def apply_shading(base_rgb: tuple[int, ...], intensity: float) -> str:
    ambient = 0.18
    shade = clamp(ambient + (1.0 - ambient) * intensity, 0.0, 1.0)
    return rgb_to_hex(tuple(channel * shade for channel in base_rgb))


# ---------------------------------------------------------------------------
# Matrix math (4×4 homogeneous)
# ---------------------------------------------------------------------------

def identity_matrix() -> Mat4:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat_mul(a: Mat4, b: Mat4) -> Mat4:
    result = [[0.0] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            result[row][col] = sum(a[row][k] * b[k][col] for k in range(4))
    return result


def mat_vec_mul(matrix: Mat4, vector: Vec3, w: float = 1.0) -> tuple[float, float, float, float]:
    values = [vector[0], vector[1], vector[2], w]
    result = tuple(sum(matrix[row][col] * values[col] for col in range(4)) for row in range(4))
    return result


def translation_matrix(tx: float, ty: float, tz: float) -> Mat4:
    matrix = identity_matrix()
    matrix[0][3] = tx
    matrix[1][3] = ty
    matrix[2][3] = tz
    return matrix


def scaling_matrix(sx: float, sy: float, sz: float) -> Mat4:
    matrix = identity_matrix()
    matrix[0][0] = sx
    matrix[1][1] = sy
    matrix[2][2] = sz
    return matrix


def rotation_x(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_y(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_z(angle: float) -> Mat4:
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def normal_matrix(model_matrix: Mat4) -> Mat3:
    # WARNING: This extracts the upper-left 3×3 sub-matrix directly, which is
    # only a correct normal matrix when the transformation consists solely of
    # rotations and *uniform* scaling.  For non-uniform scaling or shear, the
    # proper normal matrix is the transpose of the inverse of this sub-matrix.
    return [
        [model_matrix[0][0], model_matrix[0][1], model_matrix[0][2]],
        [model_matrix[1][0], model_matrix[1][1], model_matrix[1][2]],
        [model_matrix[2][0], model_matrix[2][1], model_matrix[2][2]],
    ]


def mat3_vec_mul(matrix: Mat3, vector: Vec3) -> Vec3:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    )
