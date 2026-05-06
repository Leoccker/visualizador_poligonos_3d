import tempfile
import unittest
from pathlib import Path

from obj_loader import ObjLoader


class ObjLoaderTests(unittest.TestCase):
    def setUp(self):
        self.loader = ObjLoader()

    def test_accepts_valid_negative_face_indices(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = Path(tmpdir) / "valid_negative.obj"
            obj_path.write_text(
                "\n".join(
                    [
                        "v 0 0 0",
                        "v 1 0 0",
                        "v 0 1 0",
                        "f -3 -2 -1",
                    ]
                ),
                encoding="utf-8",
            )

            mesh = self.loader.load(obj_path)

        self.assertEqual(len(mesh.triangles), 1)
        self.assertEqual(mesh.triangles[0].vertex_indices, (0, 1, 2))

    def test_accepts_face_tokens_with_uv_and_normal_indices(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = Path(tmpdir) / "valid_full_face.obj"
            obj_path.write_text(
                "\n".join(
                    [
                        "v 0 0 0",
                        "v 1 0 0",
                        "v 0 1 0",
                        "vt 0 0",
                        "vt 1 0",
                        "vt 0 1",
                        "vn 0 0 1",
                        "f 1/1/1 2/2/1 3/3/1",
                    ]
                ),
                encoding="utf-8",
            )

            mesh = self.loader.load(obj_path)

        self.assertEqual(len(mesh.triangles), 1)
        self.assertEqual(mesh.triangles[0].vertex_indices, (0, 1, 2))

    def test_rejects_out_of_range_positive_face_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = Path(tmpdir) / "bad_positive.obj"
            obj_path.write_text(
                "\n".join(
                    [
                        "v 0 0 0",
                        "v 1 0 0",
                        "v 0 1 0",
                        "f 1 2 4",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                r"bad_positive\.obj:4: vertex index 4 out of range for 3 entries",
            ):
                self.loader.load(obj_path)

    def test_rejects_out_of_range_negative_face_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = Path(tmpdir) / "bad_negative.obj"
            obj_path.write_text(
                "\n".join(
                    [
                        "v 0 0 0",
                        "v 1 0 0",
                        "v 0 1 0",
                        "f -4 -2 -1",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                r"bad_negative\.obj:4: vertex index -4 out of range for 3 entries",
            ):
                self.loader.load(obj_path)

    def test_reports_invalid_utf8_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            obj_path = Path(tmpdir) / "bad_encoding.obj"
            obj_path.write_bytes(b"v 0 0 0\n\xff\xfe")

            with self.assertRaisesRegex(ValueError, r"bad_encoding\.obj: invalid UTF-8 data"):
                self.loader.load(obj_path)


if __name__ == "__main__":
    unittest.main()
