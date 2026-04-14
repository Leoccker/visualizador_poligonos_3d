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

        with open(obj_path, "r", encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                keyword = parts[0]
                values = parts[1:]

                if keyword == "v" and len(values) >= 3:
                    mesh.vertices.append(tuple(float(value) for value in values[:3]))
                elif keyword == "vn" and len(values) >= 3:
                    mesh.normals.append(vec_normalize(tuple(float(value) for value in values[:3])))
                elif keyword == "vt" and len(values) >= 2:
                    mesh.uvs.append((float(values[0]), float(values[1])))
                elif keyword == "f" and len(values) >= 3:
                    face_items = [self._parse_face_vertex(item, mesh) for item in values]
                    for tri in self._triangulate(face_items, current_material):
                        mesh.triangles.append(tri)
                elif keyword == "mtllib":
                    mtllibs.extend(values)
                elif keyword == "usemtl":
                    current_material = values[0] if values else None
                elif keyword == "g":
                    continue

        for mtllib in mtllibs:
            mtl_path = os.path.join(os.path.dirname(obj_path), mtllib)
            if os.path.exists(mtl_path):
                mesh.materials.update(self._load_mtl(mtl_path))

        self._center_and_scale(mesh)
        self._ensure_face_normals(mesh)
        mesh.euler_stats = self._compute_euler_stats(mesh)
        return mesh

    def _parse_face_vertex(self, token, mesh):
        items = token.split("/")
        vertex_index = self._resolve_index(items[0], len(mesh.vertices))
        uv_index = None
        normal_index = None

        if len(items) >= 2 and items[1] != "":
            uv_index = self._resolve_index(items[1], len(mesh.uvs))
        if len(items) >= 3 and items[2] != "":
            normal_index = self._resolve_index(items[2], len(mesh.normals))

        return vertex_index, uv_index, normal_index

    def _resolve_index(self, token, size):
        value = int(token)
        if value > 0:
            return value - 1
        if value < 0:
            return size + value
        raise ValueError("OBJ index cannot be zero")

    def _triangulate(self, face_items, material_name):
        base = face_items[0]
        triangles = []
        for index in range(1, len(face_items) - 1):
            second = face_items[index]
            third = face_items[index + 1]
            triangles.append(
                Triangle(
                    vertex_indices=(base[0], second[0], third[0]),
                    uv_indices=(base[1], second[1], third[1]),
                    normal_indices=(base[2], second[2], third[2]),
                    material_name=material_name,
                )
            )
        return triangles

    def _load_mtl(self, mtl_path):
        materials = {}
        current = None

        with open(mtl_path, "r", encoding="utf-8", errors="ignore") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split()
                keyword = parts[0]
                values = parts[1:]

                if keyword == "newmtl" and values:
                    current = Material(values[0])
                    materials[current.name] = current
                elif keyword == "Kd" and current and len(values) >= 3:
                    current.kd = tuple(float(value) for value in values[:3])

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
