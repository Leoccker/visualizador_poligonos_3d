import unittest
from unittest.mock import patch

from models import Mesh, Triangle
from viewer_app import ViewerApp
from viewer_state import ViewerState


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeLoader:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def load(self, _path):
        if self.error is not None:
            raise self.error
        return self.result


class ViewerAppTests(unittest.TestCase):
    def _make_app(self):
        app = ViewerApp.__new__(ViewerApp)
        app.state = ViewerState()
        app.status_var = FakeVar("old status")
        app.info_var = FakeVar("old info")
        app.mesh = None
        app.drag_anchor = (10, 10)
        app.draw_calls = 0

        def _draw():
            app.draw_calls += 1

        app.draw = _draw
        return app

    def test_build_render_data_sorts_far_triangles_first(self):
        app = self._make_app()
        app.mesh = Mesh(
            vertices=[
                (0.0, 0.0, 1.0),
                (1.0, 0.0, 1.0),
                (0.0, 1.0, 1.0),
                (0.0, 0.0, -2.0),
                (1.0, 0.0, -2.0),
                (0.0, 1.0, -2.0),
            ],
            triangles=[
                Triangle(vertex_indices=(0, 1, 2), material_name=None, face_normal=(0.0, 0.0, -1.0)),
                Triangle(vertex_indices=(3, 4, 5), material_name=None, face_normal=(0.0, 0.0, -1.0)),
            ],
        )
        app.state.projection = "perspective"

        render_data = app._build_render_data()

        self.assertEqual([item["triangle"].vertex_indices for item in render_data], [(0, 1, 2), (3, 4, 5)])
        self.assertEqual([item["depth"] for item in render_data], [1.0, -2.0])

    def test_open_obj_clears_stale_mesh_state_after_load_failure(self):
        app = self._make_app()
        app.loader = FakeLoader(error=ValueError("broken obj"))
        app.mesh = Mesh(source_path="old.obj")
        app.state.rotation = [1.0, 2.0, 3.0]

        with patch("viewer_app.filedialog.askopenfilename", return_value="/tmp/bad.obj"):
            with patch("viewer_app.messagebox.showerror") as showerror:
                app.open_obj()

        self.assertIsNone(app.mesh)
        self.assertIsNone(app.drag_anchor)
        self.assertEqual(app.state.rotation, [0.0, 0.0, 0.0])
        self.assertEqual(app.status_var.get(), "Falha ao carregar: bad.obj")
        self.assertEqual(app.info_var.get(), "")
        self.assertEqual(app.draw_calls, 1)
        showerror.assert_called_once_with("Erro ao carregar OBJ", "broken obj")


if __name__ == "__main__":
    unittest.main()
