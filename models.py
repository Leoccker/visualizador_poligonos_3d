from dataclasses import dataclass, field


@dataclass
class Material:
    name: str
    kd: tuple[float, float, float] = (0.75, 0.75, 0.75)


@dataclass
class Triangle:
    vertex_indices: tuple[int, int, int]
    uv_indices: tuple[int | None, int | None, int | None]
    normal_indices: tuple[int | None, int | None, int | None]
    material_name: str | None
    face_normal: tuple[float, float, float] = (0.0, 0.0, 1.0)


@dataclass
class Mesh:
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    normals: list[tuple[float, float, float]] = field(default_factory=list)
    uvs: list[tuple[float, float]] = field(default_factory=list)
    triangles: list[Triangle] = field(default_factory=list)
    materials: dict[str, Material] = field(default_factory=dict)
    source_path: str = ""
    euler_stats: dict[str, int | str] = field(default_factory=dict)
