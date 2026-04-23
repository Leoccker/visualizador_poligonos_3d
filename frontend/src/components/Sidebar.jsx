import React from 'react';

export default function Sidebar({ viewerState, stats, materialsData }) {
  const eulerColor = stats?.status === 'OK' ? 'var(--success)' : 'var(--warning)';

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
        <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--text-primary)' }}>Informações da Malha</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <div>Vértices (V):</div><div style={{ textAlign: 'right' }}>{stats?.V ?? '-'}</div>
          <div>Arestas (E):</div><div style={{ textAlign: 'right' }}>{stats?.E ?? '-'}</div>
          <div>Faces (F):</div><div style={{ textAlign: 'right' }}>{stats?.F ?? '-'}</div>
        </div>
        
        <div style={{ marginTop: '12px', padding: '12px', backgroundColor: 'var(--bg-elevated)', borderRadius: '8px', borderLeft: `4px solid ${stats ? eulerColor : 'var(--border)'}` }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Característica de Euler</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{stats?.euler ?? '-'}</span>
            <span style={{ fontSize: '0.8rem', color: stats ? eulerColor : 'inherit' }}>{stats?.status ?? 'Nenhum'}</span>
          </div>
        </div>
      </div>

      <div style={{ height: '1px', backgroundColor: 'var(--border)' }} />

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
          {['rotate', 'translate', 'scale'].map(mode => (
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
              {mode === 'rotate' ? 'Rot' : mode === 'translate' ? 'Pos' : 'Esc'}
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
      </div>
    </div>
  );
}
