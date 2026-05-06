import argparse
import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from math_utils import kd_to_rgb, rgb_to_hex
from obj_loader import ObjLoader


MAX_BODY_BYTES = 20 * 1024 * 1024


def safe_filename(name, fallback):
    candidate = Path(name or fallback).name
    if not candidate or candidate in {".", ".."}:
        return fallback
    return candidate


def serialize_mesh(mesh, source_name):
    stats = dict(mesh.euler_stats)
    if "Euler" in stats:
        stats["euler"] = stats["Euler"]

    materials = []
    for material in mesh.materials.values():
        materials.append(
            {
                "name": material.name,
                "kd": list(material.kd),
                "color": rgb_to_hex(kd_to_rgb(material.kd)),
            }
        )

    return {
        "sourceName": source_name,
        "vertices": [list(vertex) for vertex in mesh.vertices],
        "triangles": [
            {
                "vertexIndices": list(triangle.vertex_indices),
                "materialName": triangle.material_name,
                "faceNormal": list(triangle.face_normal),
            }
            for triangle in mesh.triangles
        ],
        "materials": materials,
        "eulerStats": stats,
        "rendering": {
            "backfaceCulling": True,
            "shading": "ambient + diffuse * max(n dot L, 0)",
        },
    }


def parse_model_payload(payload):
    obj_data = payload.get("obj") if isinstance(payload, dict) else None
    if not isinstance(obj_data, dict):
        raise ValueError("Campo 'obj' ausente.")

    obj_content = obj_data.get("content")
    if not isinstance(obj_content, str) or not obj_content.strip():
        raise ValueError("Conteudo OBJ vazio ou invalido.")

    obj_name = safe_filename(obj_data.get("name"), "model.obj")
    mtl_data = payload.get("mtl")
    mtl_name = None
    mtl_content = None

    if isinstance(mtl_data, dict) and isinstance(mtl_data.get("content"), str):
        mtl_content = mtl_data["content"]
        mtl_name = safe_filename(mtl_data.get("name"), "model.mtl")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        obj_path = tmp_path / obj_name
        obj_path.write_text(obj_content, encoding="utf-8")

        extra_mtllibs = []
        if mtl_name and mtl_content is not None:
            (tmp_path / mtl_name).write_text(mtl_content, encoding="utf-8")
            extra_mtllibs.append(mtl_name)

        mesh = ObjLoader().load(obj_path, extra_mtllibs=extra_mtllibs)

    return serialize_mesh(mesh, obj_name)


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "PolygonViewerAPI/1.0"

    def do_OPTIONS(self):
        self._send_json(204, None)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json(200, {"ok": True})
            return

        self._send_json(404, {"error": "Endpoint nao encontrado."})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/models/parse":
            self._send_json(404, {"error": "Endpoint nao encontrado."})
            return

        try:
            payload = self._read_json()
            mesh_data = parse_model_payload(payload)
            self._send_json(200, {"mesh": mesh_data})
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
        except Exception as exc:
            self._send_json(500, {"error": f"Erro ao processar OBJ: {exc}"})

    def _read_json(self):
        length_header = self.headers.get("Content-Length")
        if not length_header:
            raise ValueError("Corpo da requisicao vazio.")

        try:
            length = int(length_header)
        except ValueError as exc:
            raise ValueError("Content-Length invalido.") from exc

        if length > MAX_BODY_BYTES:
            raise ValueError("Arquivo muito grande para este servidor local.")

        raw_body = self.rfile.read(length)
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("JSON invalido.") from exc
        except UnicodeDecodeError as exc:
            raise ValueError("Corpo da requisicao precisa estar em UTF-8.") from exc

    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        if payload is None:
            self.end_headers()
            return

        body = json.dumps(payload).encode("utf-8")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host, port):
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"Backend API em http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API local do visualizador 3D.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run(args.host, args.port)
