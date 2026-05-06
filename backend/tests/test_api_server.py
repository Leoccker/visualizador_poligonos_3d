import unittest

from api_server import parse_model_payload


class ApiServerTests(unittest.TestCase):
    def test_parse_model_payload_uses_obj_loader_and_extra_mtl(self):
        result = parse_model_payload(
            {
                "obj": {
                    "name": "triangle.obj",
                    "content": "\n".join(
                        [
                            "v 0 0 0",
                            "v 1 0 0",
                            "v 0 1 0",
                            "usemtl red",
                            "f 1 2 3",
                        ]
                    ),
                },
                "mtl": {
                    "name": "colors.mtl",
                    "content": "\n".join(["newmtl red", "Kd 1 0 0"]),
                },
            }
        )

        self.assertEqual(result["sourceName"], "triangle.obj")
        self.assertEqual(len(result["vertices"]), 3)
        self.assertEqual(len(result["triangles"]), 1)
        self.assertEqual(result["triangles"][0]["materialName"], "red")
        self.assertEqual(result["materials"][0]["color"], "#ff0000")
        self.assertEqual(result["eulerStats"]["euler"], 1)
        self.assertTrue(result["rendering"]["backfaceCulling"])

    def test_parse_model_payload_rejects_empty_obj(self):
        with self.assertRaisesRegex(ValueError, "Conteudo OBJ vazio"):
            parse_model_payload({"obj": {"name": "empty.obj", "content": ""}})


if __name__ == "__main__":
    unittest.main()
