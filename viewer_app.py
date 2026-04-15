import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox

from constants import (
    BACKGROUND,
    WIRE_COLOR,
    HUD_COLOR,
    LIGHT_DIRECTION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from math_utils import (
    vec_dot, vec_scale, vec_normalize,
    kd_to_rgb, apply_shading, rgb_to_hex,
    identity_matrix, mat_mul, mat_vec_mul,
    rotation_x, rotation_y,
    normal_matrix, mat3_vec_mul,
)
from obj_loader import ObjLoader
from viewer_state import ViewerState


class ViewerApp:
    DEFAULT_STATUS = "Abra um arquivo .obj para iniciar"

    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador 3D de Poligonos OBJ/MTL")
        self.root.configure(bg=BACKGROUND)
        self.loader = ObjLoader()
        self.state = ViewerState()
        self.mesh = None
        self.drag_anchor = None

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value=self.DEFAULT_STATUS)
        self.info_var = tk.StringVar(value="")

        controls = tk.Frame(root, bg=BACKGROUND)
        controls.place(x=14, y=14)

        open_button = tk.Button(controls, text="Abrir OBJ", command=self.open_obj)
        open_button.pack(side="left", padx=(0, 8))

        status_label = tk.Label(
            controls, textvariable=self.status_var, fg=HUD_COLOR, bg=BACKGROUND, anchor="w"
        )
        status_label.pack(side="left")

        self.root.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.root.bind("<Configure>", self.on_resize)

        self.draw()

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def open_obj(self):
        path = filedialog.askopenfilename(
            title="Selecionar OBJ",
            filetypes=[("Wavefront OBJ", "*.obj"), ("Todos os arquivos", "*.*")],
        )
        if not path:
            return

        try:
            mesh = self.loader.load(path)
        except (OSError, ValueError) as exc:
            self._clear_loaded_mesh(f"Falha ao carregar: {os.path.basename(path)}")
            self.draw()
            messagebox.showerror("Erro ao carregar OBJ", str(exc))
            return

        self._set_loaded_mesh(mesh, path)
        self.draw()

    def _set_loaded_mesh(self, mesh, path):
        self.mesh = mesh
        self.drag_anchor = None
        self.state.reset()
        stats = self.mesh.euler_stats
        self.status_var.set(f"Modelo carregado: {os.path.basename(path)}")
        self.info_var.set(
            f"V={stats['V']}  E={stats['E']}  F={stats['F']}  Euler={stats['Euler']} ({stats['status']})"
        )

    def _clear_loaded_mesh(self, status_message):
        self.mesh = None
        self.drag_anchor = None
        self.state.reset()
        self.status_var.set(status_message or self.DEFAULT_STATUS)
        self.info_var.set("")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

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
            self.state.projection = (
                "perspective" if self.state.projection == "isometric" else "isometric"
            )
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
            self.state.apply_arrow_transform(key)
        elif self.state.transform_mode == "rotate" and key in {"x", "y", "z"}:
            self.state.apply_rotation_axis(key, -1 if event.state & 0x0001 else 1)

        self.draw()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _get_view_matrix(self):
        if self.state.projection == "isometric":
            return mat_mul(rotation_y(math.radians(45)), rotation_x(math.radians(-35.264)))
        return identity_matrix()

    def _project_point(self, point, canvas_width, canvas_height):
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

    def _triangle_color(self, triangle, normal):
        light_dir = vec_normalize(LIGHT_DIRECTION)
        intensity = max(0.0, vec_dot(vec_normalize(normal), vec_scale(light_dir, -1.0)))
        material = self.mesh.materials.get(triangle.material_name) if triangle.material_name else None
        base_rgb = kd_to_rgb(material.kd if material else (0.75, 0.78, 0.84))
        return apply_shading(base_rgb, intensity)

    def _build_render_data(self):
        if not self.mesh:
            return []

        model = self.state.model_matrix()
        view = self._get_view_matrix()
        norm_mat = normal_matrix(mat_mul(view, model))
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
            transformed_normal = vec_normalize(mat3_vec_mul(norm_mat, triangle.face_normal))

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

        # Painter's algorithm needs far geometry first because the canvas has no z-buffer.
        render_triangles.sort(key=lambda item: item["depth"], reverse=True)
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
            self._draw_hud(width, height)
            return

        for item in self._build_render_data():
            points_2d = []
            clipped = False
            for point in item["points_3d"]:
                projected = self._project_point(point, width, height)
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
                    fill=self._triangle_color(triangle, item["normal"]),
                    outline="",
                )

            if self.state.render_mode in {"wireframe", "both"}:
                wire_color = WIRE_COLOR
                if triangle.material_name and triangle.material_name in self.mesh.materials:
                    base = kd_to_rgb(self.mesh.materials[triangle.material_name].kd)
                    wire_color = rgb_to_hex(tuple(min(255, value + 20) for value in base))
                self.canvas.create_polygon(points_2d, outline=wire_color, width=1, fill="")

        self._draw_hud(width, height)

    def _draw_hud(self, width, height):
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
