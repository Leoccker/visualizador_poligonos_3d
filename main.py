import math
import os
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
BACKGROUND = "#0d1117"
WIRE_COLOR = "#d9e2ec"
HUD_COLOR = "#e6edf3"
LIGHT_DIRECTION = (0.35, -0.45, -1.0)
TRANSLATION_STEP = 0.08
ROTATION_STEP = math.radians(7)
SCALE_STEP = 1.08


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_length(v):
    return math.sqrt(vec_dot(v, v))


def vec_scale(v, scalar):
    return (v[0] * scalar, v[1] * scalar, v[2] * scalar)


def vec_normalize(v):
    length = vec_length(v)
    if length == 0:
        return (0.0, 0.0, 1.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def centroid(points):
    if not points:
        return (0.0, 0.0, 0.0)
    total = (0.0, 0.0, 0.0)
    for point in points:
        total = vec_add(total, point)
    return (total[0] / len(points), total[1] / len(points), total[2] / len(points))


def rgb_to_hex(rgb):
    r = int(clamp(rgb[0], 0, 255))
    g = int(clamp(rgb[1], 0, 255))
    b = int(clamp(rgb[2], 0, 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def kd_to_rgb(kd):
    return tuple(int(clamp(channel, 0.0, 1.0) * 255) for channel in kd)


def apply_shading(base_rgb, intensity):
    ambient = 0.18
    shade = clamp(ambient + (1.0 - ambient) * intensity, 0.0, 1.0)
    return rgb_to_hex(tuple(channel * shade for channel in base_rgb))


def identity_matrix():
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def mat_mul(a, b):
    result = [[0.0] * 4 for _ in range(4)]
    for row in range(4):
        for col in range(4):
            result[row][col] = sum(a[row][k] * b[k][col] for k in range(4))
    return result


def mat_vec_mul(matrix, vector, w=1.0):
    values = [vector[0], vector[1], vector[2], w]
    result = [sum(matrix[row][col] * values[col] for col in range(4)) for row in range(4)]
    return result


def translation_matrix(tx, ty, tz):
    matrix = identity_matrix()
    matrix[0][3] = tx
    matrix[1][3] = ty
    matrix[2][3] = tz
    return matrix


def scaling_matrix(sx, sy, sz):
    matrix = identity_matrix()
    matrix[0][0] = sx
    matrix[1][1] = sy
    matrix[2][2] = sz
    return matrix


def rotation_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def normal_matrix(model_matrix):
    return [
        [model_matrix[0][0], model_matrix[0][1], model_matrix[0][2]],
        [model_matrix[1][0], model_matrix[1][1], model_matrix[1][2]],
        [model_matrix[2][0], model_matrix[2][1], model_matrix[2][2]],
    ]


def mat3_vec_mul(matrix, vector):
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    )


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
                    face_items = [self.parse_face_vertex(item, mesh) for item in values]
                    for tri in self.triangulate(face_items, current_material):
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
                mesh.materials.update(self.load_mtl(mtl_path))

        self.center_and_scale(mesh)
        self.ensure_face_normals(mesh)
        mesh.euler_stats = self.compute_euler_stats(mesh)
        return mesh

    def parse_face_vertex(self, token, mesh):
        items = token.split("/")
        vertex_index = self.resolve_index(items[0], len(mesh.vertices))
        uv_index = None
        normal_index = None

        if len(items) >= 2 and items[1] != "":
            uv_index = self.resolve_index(items[1], len(mesh.uvs))
        if len(items) >= 3 and items[2] != "":
            normal_index = self.resolve_index(items[2], len(mesh.normals))

        return vertex_index, uv_index, normal_index

    def resolve_index(self, token, size):
        value = int(token)
        if value > 0:
            return value - 1
        if value < 0:
            return size + value
        raise ValueError("OBJ index cannot be zero")

    def triangulate(self, face_items, material_name):
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

    def load_mtl(self, mtl_path):
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

    def center_and_scale(self, mesh):
        if not mesh.vertices:
            return

        center = centroid(mesh.vertices)
        centered = [vec_sub(vertex, center) for vertex in mesh.vertices]
        max_extent = max(max(abs(component) for component in vertex) for vertex in centered)
        scale = 1.0 / max_extent if max_extent else 1.0
        mesh.vertices = [vec_scale(vertex, scale) for vertex in centered]

    def ensure_face_normals(self, mesh):
        for triangle in mesh.triangles:
            v0 = mesh.vertices[triangle.vertex_indices[0]]
            v1 = mesh.vertices[triangle.vertex_indices[1]]
            v2 = mesh.vertices[triangle.vertex_indices[2]]
            edge_a = vec_sub(v1, v0)
            edge_b = vec_sub(v2, v0)
            triangle.face_normal = vec_normalize(vec_cross(edge_a, edge_b))

    def compute_euler_stats(self, mesh):
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
        trans = translation_matrix(self.translation[0], self.translation[1], self.translation[2])
        return mat_mul(trans, mat_mul(rot_z, mat_mul(rot_y, mat_mul(rot_x, scale))))


class ViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador 3D de Poligonos OBJ/MTL")
        self.root.configure(bg=BACKGROUND)
        self.loader = ObjLoader()
        self.state = ViewerState()
        self.mesh = None
        self.drag_anchor = None

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Abra um arquivo .obj para iniciar")
        self.info_var = tk.StringVar(value="")

        controls = tk.Frame(root, bg=BACKGROUND)
        controls.place(x=14, y=14)

        open_button = tk.Button(controls, text="Abrir OBJ", command=self.open_obj)
        open_button.pack(side="left", padx=(0, 8))

        status_label = tk.Label(controls, textvariable=self.status_var, fg=HUD_COLOR, bg=BACKGROUND, anchor="w")
        status_label.pack(side="left")

        self.root.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Configure>", self.on_resize)

        self.draw()

    def open_obj(self):
        path = filedialog.askopenfilename(
            title="Selecionar OBJ",
            filetypes=[("Wavefront OBJ", "*.obj"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return

        try:
            self.mesh = self.loader.load(path)
            self.state.reset()
            stats = self.mesh.euler_stats
            self.status_var.set(f"Modelo carregado: {os.path.basename(path)}")
            self.info_var.set(
                f"V={stats['V']}  E={stats['E']}  F={stats['F']}  Euler={stats['Euler']} ({stats['status']})"
            )
            self.draw()
        except Exception as exc:
            messagebox.showerror("Erro ao carregar OBJ", str(exc))

    def on_resize(self, _event):
        self.draw()

    def on_mouse_down(self, event):
        self.drag_anchor = (event.x, event.y)

    def on_mouse_drag(self, event):
        if not self.drag_anchor:
            return
        dx = event.x - self.drag_anchor[0]
        dy = event.y - self.drag_anchor[1]
        self.state.rotation[1] += dx * 0.01
        self.state.rotation[0] += dy * 0.01
        self.drag_anchor = (event.x, event.y)
        self.draw()

    def on_mouse_up(self, _event):
        self.drag_anchor = None

    def on_key_press(self, event):
        key = event.keysym.lower()

        if event.keysym == "Escape":
            self.state.reset()
            self.draw()
            return

        if key == "p":
            self.state.projection = "perspective" if self.state.projection == "isometric" else "isometric"
        elif key == "w":
            self.state.render_mode = "wireframe"
        elif key == "s":
            if event.state & 0x0001:
                self.state.transform_mode = "scale"
            else:
                self.state.render_mode = "solid"
        elif key == "b":
            self.state.render_mode = "both"
        elif key == "r":
            self.state.transform_mode = "rotate"
        elif key == "t":
            self.state.transform_mode = "translate"
        elif key in {"left", "right", "up", "down"}:
            self.apply_arrow_transform(key)
        elif self.state.transform_mode == "rotate" and key in {"x", "y", "z"}:
            self.apply_rotation_axis(key, -1 if event.state & 0x0001 else 1)

        self.draw()

    def apply_arrow_transform(self, key):
        if self.state.transform_mode == "translate":
            if key == "left":
                self.state.translation[0] -= TRANSLATION_STEP
            elif key == "right":
                self.state.translation[0] += TRANSLATION_STEP
            elif key == "up":
                self.state.translation[1] += TRANSLATION_STEP
            elif key == "down":
                self.state.translation[1] -= TRANSLATION_STEP
        elif self.state.transform_mode == "scale":
            if key in {"up", "right"}:
                self.state.scale *= SCALE_STEP
            else:
                self.state.scale /= SCALE_STEP
            self.state.scale = clamp(self.state.scale, 0.1, 10.0)
        elif self.state.transform_mode == "rotate":
            if key == "left":
                self.state.rotation[1] -= ROTATION_STEP
            elif key == "right":
                self.state.rotation[1] += ROTATION_STEP
            elif key == "up":
                self.state.rotation[0] -= ROTATION_STEP
            elif key == "down":
                self.state.rotation[0] += ROTATION_STEP

    def apply_rotation_axis(self, axis, direction):
        amount = ROTATION_STEP * direction
        if axis == "x":
            self.state.rotation[0] += amount
        elif axis == "y":
            self.state.rotation[1] += amount
        elif axis == "z":
            self.state.rotation[2] += amount

    def get_view_matrix(self):
        if self.state.projection == "isometric":
            return mat_mul(rotation_y(math.radians(45)), rotation_x(math.radians(-35.264)))
        return identity_matrix()

    def project_point(self, point, canvas_width, canvas_height):
        if self.state.projection == "perspective":
            camera_z = 4.0
            z = point[2] + camera_z
            if z <= 0.05:
                return None
            factor = 480 / z
        else:
            factor = min(canvas_width, canvas_height) * 0.33

        x = canvas_width / 2 + point[0] * factor
        y = canvas_height / 2 - point[1] * factor
        return (x, y)

    def triangle_color(self, triangle, normal):
        light_dir = vec_normalize(LIGHT_DIRECTION)
        intensity = max(0.0, vec_dot(vec_normalize(normal), vec_scale(light_dir, -1.0)))
        material = self.mesh.materials.get(triangle.material_name) if triangle.material_name else None
        base_rgb = kd_to_rgb(material.kd if material else (0.75, 0.78, 0.84))
        return apply_shading(base_rgb, intensity)

    def build_render_data(self):
        if not self.mesh:
            return []

        model = self.state.model_matrix()
        view = self.get_view_matrix()
        normal_mat = normal_matrix(mat_mul(view, model))
        transformed_vertices = []
        for vertex in self.mesh.vertices:
            world = mat_vec_mul(model, vertex)
            camera = mat_vec_mul(view, (world[0], world[1], world[2]))
            transformed_vertices.append((camera[0], camera[1], camera[2]))

        render_triangles = []
        for triangle in self.mesh.triangles:
            v0 = transformed_vertices[triangle.vertex_indices[0]]
            v1 = transformed_vertices[triangle.vertex_indices[1]]
            v2 = transformed_vertices[triangle.vertex_indices[2]]
            transformed_normal = vec_normalize(mat3_vec_mul(normal_mat, triangle.face_normal))

            if transformed_normal[2] >= 0:
                continue

            depth = (v0[2] + v1[2] + v2[2]) / 3.0
            render_triangles.append(
                {
                    "triangle": triangle,
                    "points_3d": (v0, v1, v2),
                    "normal": transformed_normal,
                    "depth": depth,
                }
            )

        render_triangles.sort(key=lambda item: item["depth"])
        return render_triangles

    def draw(self):
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)

        if not self.mesh:
            self.canvas.create_text(
                width / 2,
                height / 2,
                text="Clique em 'Abrir OBJ' para carregar um modelo Wavefront.",
                fill=HUD_COLOR,
                font=("TkDefaultFont", 16, "bold"),
            )
            self.draw_hud(width, height)
            return

        for item in self.build_render_data():
            points_2d = []
            clipped = False
            for point in item["points_3d"]:
                projected = self.project_point(point, width, height)
                if projected is None:
                    clipped = True
                    break
                points_2d.extend(projected)

            if clipped:
                continue

            triangle = item["triangle"]
            if self.state.render_mode in {"solid", "both"}:
                self.canvas.create_polygon(
                    points_2d,
                    fill=self.triangle_color(triangle, item["normal"]),
                    outline="",
                )

            if self.state.render_mode in {"wireframe", "both"}:
                wire_color = WIRE_COLOR
                if triangle.material_name and triangle.material_name in self.mesh.materials:
                    base = kd_to_rgb(self.mesh.materials[triangle.material_name].kd)
                    wire_color = rgb_to_hex(tuple(min(255, value + 20) for value in base))
                self.canvas.create_polygon(points_2d, outline=wire_color, width=1, fill="")

        self.draw_hud(width, height)

    def draw_hud(self, width, height):
        lines = [
            self.status_var.get(),
            self.info_var.get(),
            f"Projecao: {self.state.projection} | Render: {self.state.render_mode} | Transformacao: {self.state.transform_mode}",
            f"Arquivo: {os.path.basename(self.mesh.source_path) if self.mesh else '-'}",
            "W=wireframe  S=solido  B=ambos  P=projecao  R=rotacao  T=translacao  Shift+S=escala  Esc=reset",
            "Setas aplicam a transformacao atual | Em rotacao: X/Y/Z giram no eixo (Shift inverte) | Mouse: arrastar para rotacionar",
        ]
        self.canvas.create_text(
            20,
            height - 110,
            text="\n".join(line for line in lines if line),
            fill=HUD_COLOR,
            font=("Consolas", 11),
            anchor="sw",
        )


def main():
    root = tk.Tk()
    app = ViewerApp(root)
    root.minsize(900, 650)
    root.mainloop()


if __name__ == "__main__":
    main()
