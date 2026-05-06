import React, { useRef, useState } from "react";

export default function Toolbar({ viewerState, onOpenHelp, onFileSelect }) {
  const fileInputRef = useRef(null);
  const [showAuthorsModal, setShowAuthorsModal] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      const objFile = files.find((f) => f.name.toLowerCase().endsWith(".obj"));
      const mtlFile = files.find((f) => f.name.toLowerCase().endsWith(".mtl"));

      if (objFile) {
        onFileSelect(objFile, mtlFile);
      } else {
        alert("Nenhum arquivo .obj selecionado.");
      }

      e.target.value = null;
    }
  };

  return (
    <>
      <div
        className="glass-panel"
        style={{
          position: "absolute",
          top: "16px",
          left: "16px",
          display: "flex",
          gap: "12px",
          padding: "8px",
          zIndex: 10,
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: "none" }}
          multiple
          accept=".obj,.mtl"
          onChange={handleFileChange}
        />

        <button
          onClick={() => fileInputRef.current.click()}
          style={{
            backgroundColor: "var(--accent)",
            borderColor: "var(--accent)",
            color: "white",
          }}
        >
          Abrir OBJ
        </button>

        <div
          style={{
            width: "1px",
            backgroundColor: "var(--border)",
            margin: "0 4px",
          }}
        />

        <div
          style={{
            display: "flex",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <button
            style={{
              borderRadius: 0,
              border: "none",
              backgroundColor:
                viewerState.renderMode === "wireframe"
                  ? "var(--bg-surface)"
                  : "transparent",
            }}
            onClick={() => viewerState.setRenderMode("wireframe")}
          >
            Wire
          </button>

          <button
            style={{
              borderRadius: 0,
              border: "none",
              borderLeft: "1px solid var(--border)",
              backgroundColor:
                viewerState.renderMode === "solid"
                  ? "var(--bg-surface)"
                  : "transparent",
            }}
            onClick={() => viewerState.setRenderMode("solid")}
          >
            Solid
          </button>

          <button
            style={{
              borderRadius: 0,
              border: "none",
              borderLeft: "1px solid var(--border)",
              backgroundColor:
                viewerState.renderMode === "both"
                  ? "var(--bg-surface)"
                  : "transparent",
            }}
            onClick={() => viewerState.setRenderMode("both")}
          >
            Both
          </button>
        </div>

        <div
          style={{
            width: "1px",
            backgroundColor: "var(--border)",
            margin: "0 4px",
          }}
        />

        <button
          onClick={() =>
            viewerState.setProjection((p) =>
              p === "perspective" ? "isometric" : "perspective",
            )
          }
        >
          {viewerState.projection === "perspective"
            ? "Perspectiva"
            : "Isométrica"}
        </button>

        <button
          onClick={viewerState.reset}
          style={{ color: "var(--text-secondary)" }}
        >
          Reset
        </button>

        <button
          onClick={onOpenHelp}
          style={{ width: "38px", padding: "0", borderRadius: "50%" }}
        >
          ?
        </button>

        <button
          onClick={() => setShowAuthorsModal(true)}
          style={{ padding: "0 12px" }}
        >
          Autores
        </button>
      </div>

      {showAuthorsModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(0, 0, 0, 0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
          onClick={() => setShowAuthorsModal(false)}
        >
          <div
            className="glass-panel"
            style={{
              width: "320px",
              padding: "24px",
              borderRadius: "12px",
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border)",
              color: "var(--text-primary)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginTop: 0, marginBottom: "16px" }}>
              Autores do Projeto
            </h2>

            <ul style={{ margin: 0, paddingLeft: "20px" }}>
              <li>Christian Gabriel Candeloni</li>
              <li>Christian Mathias Michelson</li>
              <li>Leonardo Daniel Becker</li>
            </ul>

            <p style={{ marginTop: "16px", marginBottom: 0 }}>
              Criado com Codex CLI
            </p>

            <button
              onClick={() => setShowAuthorsModal(false)}
              style={{
                marginTop: "20px",
                width: "100%",
              }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </>
  );
}
