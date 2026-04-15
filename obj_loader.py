import os

from math_utils import (
    vec_normalize, vec_sub, vec_scale, vec_cross,
    centroid,
)
from models import Material, Mesh, Triangle


class ObjLoader:
    def load(self, obj_path):
        mesh = Mesh(source_path=obj_path)
        current_material = None
        mtllibs = []
        uvs = []
        normals = []

        try:
            with open(obj_path, "r", encoding="utf-8-sig") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()
                    keyword = parts[0]
                    values = parts[1:]

                    try:
                        if keyword == "v":
                            mesh.vertices.append(self._parse_components(values, 3, "vertex"))
                        elif keyword == "vn":
                            normals.append(
                                vec_normalize(self._parse_components(values, 3, "normal"))
                            )
                        elif keyword == "vt":
                            uvs.append(self._parse_components(values, 2, "texture coordinate"))
                        elif keyword == "f":
                            if len(values) < 3:
                                raise ValueError("face requires at least 3 vertices")
                            face_vertices = [
                                self._parse_face_vertex(
                                    item,
                                    len(mesh.vertices),
                                    len(uvs),
                                    len(normals),
                                )
                                for item in values
                            ]
                            mesh.triangles.extend(
                                self._triangulate(face_vertices, current_material)
                            )
                        elif keyword == "mtllib":
                            mtllibs.extend(values)
                        elif keyword == "usemtl":
                            current_material = values[0] if values else None
                        elif keyword == "g":
                            continue
                    except ValueError as exc:
                        raise ValueError(
                            f"{os.path.basename(obj_path)}:{line_number}: {exc}"
                        ) from exc
        except UnicodeDecodeError as exc:
            raise ValueError(f"{os.path.basename(obj_path)}: invalid UTF-8 data") from exc

        for mtllib in mtllibs:
            mtl_path = os.path.join(os.path.dirname(obj_path), mtllib)
            if os.path.exists(mtl_path):
                mesh.materials.update(self._load_mtl(mtl_path))

        self._center_and_scale(mesh)
        self._ensure_face_normals(mesh)
        mesh.euler_stats = self._compute_euler_stats(mesh)
        return mesh

    def _parse_components(self, values, count, label):
        if len(values) < count:
            raise ValueError(f"{label} requires at least {count} components")
        try:
            return tuple(float(value) for value in values[:count])
        except ValueError as exc:
            raise ValueError(f"invalid {label} value") from exc

    def _parse_face_vertex(self, token, vertex_count, uv_count, normal_count):
        items = token.split("/")
        if len(items) > 3 or not items[0]:
            raise ValueError(f"invalid face vertex '{token}'")

        vertex_index = self._resolve_index(items[0], vertex_count, "vertex")

        if len(items) >= 2 and items[1] != "":
            self._resolve_index(items[1], uv_count, "texture coordinate")
        if len(items) >= 3 and items[2] != "":
            self._resolve_index(items[2], normal_count, "normal")

        return vertex_index

    def _resolve_index(self, token, size, label):
        try:
            value = int(token)
        except ValueError as exc:
            raise ValueError(f"invalid {label} index '{token}'") from exc

        if value == 0:
            raise ValueError(f"{label} index cannot be zero")
        if size == 0:
            raise ValueError(f"{label} index {value} references an empty {label} list")

        index = value - 1 if value > 0 else size + value
        if not 0 <= index < size:
            raise ValueError(f"{label} index {value} out of range for {size} entries")
        return index

    def _triangulate(self, face_items, material_name):
        base = face_items[0]
        triangles = []
        for index in range(1, len(face_items) - 1):
            second = face_items[index]
            third = face_items[index + 1]
            triangles.append(
                Triangle(
                    vertex_indices=(base, second, third),
                    material_name=material_name,
                )
            )
        return triangles

    def _load_mtl(self, mtl_path):
        materials = {}
        current = None

        try:
            with open(mtl_path, "r", encoding="utf-8-sig") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()
                    keyword = parts[0]
                    values = parts[1:]

                    try:
                        if keyword == "newmtl" and values:
                            current = Material(values[0])
                            materials[current.name] = current
                        elif keyword == "Kd" and current:
                            current.kd = self._parse_components(values, 3, "diffuse color")
                    except ValueError as exc:
                        raise ValueError(
                            f"{os.path.basename(mtl_path)}:{line_number}: {exc}"
                        ) from exc
        except UnicodeDecodeError as exc:
            raise ValueError(f"{os.path.basename(mtl_path)}: invalid UTF-8 data") from exc

        return materials

    def _center_and_scale(self, mesh):
        if not mesh.vertices:
            return

        center = centroid(mesh.vertices)
        centered = [vec_sub(vertex, center) for vertex in mesh.vertices]
        max_extent = max(max(abs(component) for component in vertex) for vertex in centered)
        scale = 1.0 / max_extent if max_extent else 1.0
        mesh.vertices = [vec_scale(vertex, scale) for vertex in centered]

    def _ensure_face_normals(self, mesh):
        for triangle in mesh.triangles:
            v0 = mesh.vertices[triangle.vertex_indices[0]]
            v1 = mesh.vertices[triangle.vertex_indices[1]]
            v2 = mesh.vertices[triangle.vertex_indices[2]]
            edge_a = vec_sub(v1, v0)
            edge_b = vec_sub(v2, v0)
            triangle.face_normal = vec_normalize(vec_cross(edge_a, edge_b))

    def _compute_euler_stats(self, mesh):
        edges = set()
        for triangle in mesh.triangles:
            a, b, c = triangle.vertex_indices
            edges.add(tuple(sorted((a, b))))
            edges.add(tuple(sorted((b, c))))
            edges.add(tuple(sorted((c, a))))

        vertices = len(mesh.vertices)
        edge_count = len(edges)
        faces = len(mesh.triangles)
        euler_value = vertices - edge_count + faces
        return {
            "V": vertices,
            "E": edge_count,
            "F": faces,
            "Euler": euler_value,
            "status": "OK" if euler_value == 2 else "Nao fechado/nao convexo",
        }
