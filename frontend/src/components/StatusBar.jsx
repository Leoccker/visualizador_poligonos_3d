import React from 'react';

export default function StatusBar({ fileName, isLoading, error, viewerState }) {
  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      bottom: '16px',
      left: '16px',
      right: '16px',
      padding: '8px 16px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      zIndex: 10,
      fontSize: '0.85rem'
    }}>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        {isLoading ? (
          <span style={{ color: 'var(--accent)' }}>Carregando...</span>
        ) : error ? (
          <span style={{ color: 'var(--danger)' }}>Erro: {error}</span>
        ) : fileName ? (
          <span style={{ color: 'var(--text-primary)' }}>Modelo: {fileName}</span>
        ) : (
          <span style={{ color: 'var(--text-secondary)' }}>Abra ou arraste um arquivo .obj para iniciar</span>
        )}
      </div>

      <div style={{ display: 'flex', gap: '16px', color: 'var(--text-secondary)' }}>
        <span>Render: <strong style={{ color: 'var(--text-primary)' }}>{viewerState.renderMode}</strong></span>
        <span>Modo: <strong style={{ color: 'var(--text-primary)' }}>{viewerState.transformMode}</strong></span>
      </div>
    </div>
  );
}
