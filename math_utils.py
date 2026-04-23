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


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r = int(clamp(rgb[0], 0, 255))
    g = int(clamp(rgb[1], 0, 255))
    b = int(clamp(rgb[2], 0, 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def kd_to_rgb(kd: Vec3) -> tuple[int, int, int]:
    return (
        int(clamp(kd[0], 0.0, 1.0) * 255),
        int(clamp(kd[1], 0.0, 1.0) * 255),
        int(clamp(kd[2], 0.0, 1.0) * 255),
    )


def apply_shading(base_rgb: tuple[int, int, int], intensity: float) -> str:
    ambient = 0.35
    shade = clamp(ambient + (1.0 - ambient) * intensity, 0.0, 1.0)
    return rgb_to_hex(
        (
            int(base_rgb[0] * shade),
            int(base_rgb[1] * shade),
            int(base_rgb[2] * shade),
        )
    )


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


def mat_vec_mul(
    matrix: Mat4, vector: Vec3, w: float = 1.0
) -> tuple[float, float, float, float]:
    x, y, z = vector[0], vector[1], vector[2]
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z + matrix[0][3] * w,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z + matrix[1][3] * w,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z + matrix[2][3] * w,
        matrix[3][0] * x + matrix[3][1] * y + matrix[3][2] * z + matrix[3][3] * w,
    )


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
    """
    Returns the correct normal matrix: transpose(inverse(upper-left 3×3)).

    This is mathematically correct for all affine transforms, including
    non-uniform scaling and shear.  It is computed as the cofactor matrix of
    the upper-left 3×3 divided by its determinant, which equals
    transpose(inverse(M)) without needing a separate transpose step.

    Falls back to the plain upper-left 3×3 if the sub-matrix is singular
    (determinant ≈ 0), which only happens for degenerate/collapsed meshes.
    """
    a = model_matrix[0][0]
    b = model_matrix[0][1]
    c = model_matrix[0][2]
    d = model_matrix[1][0]
    e = model_matrix[1][1]
    f = model_matrix[1][2]
    g = model_matrix[2][0]
    h = model_matrix[2][1]
    i = model_matrix[2][2]

    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)

    if abs(det) < 1e-10:
        # Degenerate transform – fall back to the plain upper-left 3×3.
        return [
            [a, b, c],
            [d, e, f],
            [g, h, i],
        ]

    inv_det = 1.0 / det

    # transpose(inverse(M)) equals the cofactor matrix divided by det(M).
    # Cofactor C_ij = (-1)^(i+j) * minor_ij
    return [
        [
            (e * i - f * h) * inv_det,
            -(d * i - f * g) * inv_det,
            (d * h - e * g) * inv_det,
        ],
        [
            -(b * i - c * h) * inv_det,
            (a * i - c * g) * inv_det,
            -(a * h - b * g) * inv_det,
        ],
        [
            (b * f - c * e) * inv_det,
            -(a * f - c * d) * inv_det,
            (a * e - b * d) * inv_det,
        ],
    ]


def mat3_vec_mul(matrix: Mat3, vector: Vec3) -> Vec3:
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    )
