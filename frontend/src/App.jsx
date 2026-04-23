import React, { useState, useEffect } from 'react';

import Viewport from './components/Viewport';
import Toolbar from './components/Toolbar';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';
import FileDropZone from './components/FileDropZone';
import HelpModal from './components/HelpModal';

import { useViewerState } from './hooks/useViewerState';
import { useModelLoader } from './hooks/useModelLoader';

export default function App() {
  const viewerState = useViewerState();
  const { model, stats, materialsData, isLoading, error, fileName, loadFromFiles, loadDefaultCube } = useModelLoader();
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  return (
    <FileDropZone onFilesDrop={loadFromFiles}>
      <div style={{ width: '100vw', height: '100vh', overflow: 'hidden', position: 'relative' }}>
        
        <Viewport 
          model={model} 
          viewerState={viewerState} 
        />
        
        <Toolbar 
          viewerState={viewerState} 
          onOpenHelp={() => setIsHelpOpen(true)} 
          onFileSelect={loadFromFiles}
        />
        
        {model && (
          <Sidebar 
            viewerState={viewerState} 
            stats={stats} 
            materialsData={materialsData}
          />
        )}
        
        <StatusBar 
          fileName={fileName} 
          isLoading={isLoading} 
          error={error} 
          viewerState={viewerState}
        />

        <HelpModal 
          isOpen={isHelpOpen} 
          onClose={() => setIsHelpOpen(false)} 
        />
      </div>
    </FileDropZone>
  );
}
