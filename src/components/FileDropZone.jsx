import React, { useRef } from 'react';

export default function FileDropZone({ onFilesDrop, children }) {
  const [isDragging, setIsDragging] = React.useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const processFiles = (fileList) => {
    const files = Array.from(fileList);
    const objFile = files.find(f => f.name.toLowerCase().endsWith('.obj'));
    const mtlFile = files.find(f => f.name.toLowerCase().endsWith('.mtl'));

    if (objFile) {
      onFilesDrop(objFile, mtlFile);
    } else {
      alert("Nenhum arquivo .obj encontrado.");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  return (
    <div 
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      style={{ width: '100%', height: '100%', position: 'relative' }}
    >
      {children}
      
      {isDragging && (
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(99, 102, 241, 0.1)',
          backdropFilter: 'blur(4px)',
          border: '4px dashed var(--accent)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          pointerEvents: 'none'
        }}>
          <h2 style={{ color: 'var(--accent)', fontSize: '2rem', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
            Solte o arquivo .obj e .mtl aqui
          </h2>
        </div>
      )}
    </div>
  );
}
