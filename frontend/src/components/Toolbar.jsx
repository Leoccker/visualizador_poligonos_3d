import React, { useRef } from 'react';

export default function Toolbar({ viewerState, onOpenHelp, onFileSelect }) {
  const fileInputRef = useRef(null);
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      const objFile = files.find(f => f.name.toLowerCase().endsWith('.obj'));
      const mtlFile = files.find(f => f.name.toLowerCase().endsWith('.mtl'));
      
      if (objFile) {
        onFileSelect(objFile, mtlFile);
      } else {
        alert("Nenhum arquivo .obj selecionado.");
      }
      e.target.value = null;
    }
  };

  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      top: '16px',
      left: '16px',
      display: 'flex',
      gap: '12px',
      padding: '8px',
      zIndex: 10
    }}>
      <input 
        type="file" 
        ref={fileInputRef} 
        style={{ display: 'none' }} 
        multiple 
        accept=".obj,.mtl" 
        onChange={handleFileChange}
      />
      <button onClick={() => fileInputRef.current.click()} style={{ backgroundColor: 'var(--accent)', borderColor: 'var(--accent)', color: 'white' }}>
        Abrir OBJ
      </button>

      <div style={{ width: '1px', backgroundColor: 'var(--border)', margin: '0 4px' }} />

      <div style={{ display: 'flex', border: '1px solid var(--border)', borderRadius: '8px', overflow: 'hidden' }}>
        <button 
          style={{ borderRadius: 0, border: 'none', backgroundColor: viewerState.renderMode === 'wireframe' ? 'var(--bg-surface)' : 'transparent' }}
          onClick={() => viewerState.setRenderMode('wireframe')}
        >
          Wire
        </button>
        <button 
          style={{ borderRadius: 0, border: 'none', borderLeft: '1px solid var(--border)', backgroundColor: viewerState.renderMode === 'solid' ? 'var(--bg-surface)' : 'transparent' }}
          onClick={() => viewerState.setRenderMode('solid')}
        >
          Solid
        </button>
        <button 
          style={{ borderRadius: 0, border: 'none', borderLeft: '1px solid var(--border)', backgroundColor: viewerState.renderMode === 'both' ? 'var(--bg-surface)' : 'transparent' }}
          onClick={() => viewerState.setRenderMode('both')}
        >
          Both
        </button>
      </div>

      <div style={{ width: '1px', backgroundColor: 'var(--border)', margin: '0 4px' }} />

      <button 
        onClick={() => viewerState.setProjection(p => p === 'perspective' ? 'isometric' : 'perspective')}
      >
        {viewerState.projection === 'perspective' ? 'Perspectiva' : 'Isométrica'}
      </button>

      <button onClick={viewerState.reset} style={{ color: 'var(--text-secondary)' }}>
        Reset
      </button>

      <button onClick={onOpenHelp} style={{ width: '38px', padding: '0', borderRadius: '50%' }}>
        ?
      </button>
    </div>
  );
}
