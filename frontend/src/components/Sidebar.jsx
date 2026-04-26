export default function Sidebar({ viewerState, materialsData }) {
  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      top: '16px',
      right: '16px',
      width: '280px',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      zIndex: 10,
      maxHeight: 'calc(100vh - 80px)',
      overflowY: 'auto'
    }}>
      <div>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--text-primary)' }}>Materiais</h3>
        {materialsData && materialsData.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {materialsData.map((mat, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
                <div style={{ width: '16px', height: '16px', borderRadius: '4px', backgroundColor: `#${mat.color}`, border: '1px solid var(--border)' }} />
                <span>{mat.name || 'Sem nome'}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Nenhum material carregado.</div>
        )}
      </div>

      <div style={{ height: '1px', backgroundColor: 'var(--border)' }} />

      <div>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--text-primary)' }}>Transformação</h3>
        
        <div style={{ display: 'flex', gap: '4px', marginBottom: '16px' }}>
          {['rotate', 'translate', 'scale', 'shear'].map(mode => (
            <button 
              key={mode}
              onClick={() => viewerState.setTransformMode(mode)}
              style={{ 
                flex: 1, 
                padding: '4px 0', 
                fontSize: '0.8rem',
                backgroundColor: viewerState.transformMode === mode ? 'var(--accent)' : 'transparent',
                borderColor: viewerState.transformMode === mode ? 'var(--accent)' : 'var(--border)'
              }}
            >
              {mode === 'rotate' ? 'Rot' : mode === 'translate' ? 'Pos' : mode === 'scale' ? 'Esc' : 'Cis'}
            </button>
          ))}
        </div>

        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          Rot: X: {viewerState.rotation[0].toFixed(2)} Y: {viewerState.rotation[1].toFixed(2)} Z: {viewerState.rotation[2].toFixed(2)}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          Pos: X: {viewerState.position[0].toFixed(2)} Y: {viewerState.position[1].toFixed(2)} Z: {viewerState.position[2].toFixed(2)}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          Esc: {viewerState.scale.toFixed(2)}x
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
          Cis: XY: {viewerState.shear[0].toFixed(2)} XZ: {viewerState.shear[1].toFixed(2)} YZ: {viewerState.shear[2].toFixed(2)}
        </div>
      </div>
    </div>
  );
}
