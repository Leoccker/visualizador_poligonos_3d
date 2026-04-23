import React from 'react';

export default function HelpModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 2000
    }} onClick={onClose}>
      <div className="glass-panel" style={{
        padding: '24px', width: '90%', maxWidth: '500px',
        maxHeight: '90vh', overflowY: 'auto'
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0, color: 'var(--text-primary)' }}>Controles e Atalhos</h2>
          <button onClick={onClose} style={{ padding: '4px 12px', background: 'transparent', border: 'none', color: 'var(--text-secondary)', fontSize: '1.2rem' }}>✕</button>
        </div>
        
        <table style={{ width: '100%', borderCollapse: 'collapse', color: 'var(--text-primary)', fontSize: '0.9rem' }}>
          <tbody>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>P</strong></td>
              <td>Alternar Projeção (Perspectiva / Isométrica)</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>W / S / B</strong></td>
              <td>Render: Wireframe / Sólido / Ambos</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>R / T / Shift+S</strong></td>
              <td>Modo Transformação: Rotação / Translação / Escala</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>Setas</strong></td>
              <td>Aplicam a transformação do modo atual</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>X / Y / Z</strong></td>
              <td>Rotação no eixo (no modo Rotação)</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>Shift + X/Y/Z</strong></td>
              <td>Rotação reversa no eixo</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              <td style={{ padding: '8px 0' }}><strong>Mouse</strong></td>
              <td>Arrastar: Orbitar | Scroll: Zoom | Direito: Pan</td>
            </tr>
            <tr>
              <td style={{ padding: '8px 0' }}><strong>Esc</strong></td>
              <td>Reset de Transformações</td>
            </tr>
          </tbody>
        </table>
        
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <button onClick={onClose} style={{ width: '100%' }}>Fechar</button>
        </div>
      </div>
    </div>
  );
}
