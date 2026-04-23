import React, { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, OrthographicCamera, Grid, Environment } from '@react-three/drei';
import * as THREE from 'three';

// Tag used to identify wireframe helpers we add so we can clean them up
const WIRE_TAG = '__wireOverlay';
const WIRE_SCALE = 1.02; // wireframe is slightly larger than the solid

const ModelRenderer = ({ model, renderMode, viewerPosition, viewerRotation, viewerScale }) => {
  const groupRef = useRef();

  // Apply transformations from viewer state
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.position.set(viewerPosition[0], viewerPosition[1], viewerPosition[2]);
      groupRef.current.rotation.set(viewerRotation[0], viewerRotation[1], viewerRotation[2]);
      groupRef.current.scale.set(viewerScale, viewerScale, viewerScale);
    }
  });

  // Apply render mode — manages materials AND per-mesh wireframe children
  useEffect(() => {
    if (!model) return;

    // 1. Remove any previously-added wireframe helpers
    const toRemove = [];
    model.traverse((child) => {
      if (child.userData[WIRE_TAG]) toRemove.push(child);
    });
    toRemove.forEach((obj) => {
      obj.parent?.remove(obj);
      obj.geometry?.dispose();
      if (obj.material) obj.material.dispose();
    });

    // 2. Configure materials on every mesh
    model.traverse((child) => {
      if (!child.isMesh) return;

      const mats = Array.isArray(child.material) ? child.material : [child.material];

      if (renderMode === 'wireframe') {
        // Pure wireframe: show material in wireframe mode
        mats.forEach((mat) => {
          mat.wireframe = true;
          mat.transparent = false;
          mat.opacity = 1.0;
          mat.flatShading = true;
          mat.needsUpdate = true;
        });
      } else {
        // solid or both: show material as solid
        mats.forEach((mat) => {
          mat.wireframe = false;
          mat.transparent = false;
          mat.opacity = 1.0;
          mat.flatShading = true;
          mat.needsUpdate = true;
        });
      }

      // 3. For "both": attach a scaled-up wireframe child to THIS mesh
      if (renderMode === 'both') {
        const edgesGeom = new THREE.EdgesGeometry(child.geometry, 15);
        const edgesMat = new THREE.LineBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.35,
          depthTest: true,
        });
        const edgesLine = new THREE.LineSegments(edgesGeom, edgesMat);
        edgesLine.userData[WIRE_TAG] = true;
        edgesLine.scale.set(WIRE_SCALE, WIRE_SCALE, WIRE_SCALE);
        // Render on top so edges aren't hidden behind faces
        edgesLine.renderOrder = 1;
        child.add(edgesLine);
      }
    });

    // Cleanup when renderMode changes or unmounts
    return () => {
      if (!model) return;
      const cleanup = [];
      model.traverse((child) => {
        if (child.userData[WIRE_TAG]) cleanup.push(child);
      });
      cleanup.forEach((obj) => {
        obj.parent?.remove(obj);
        obj.geometry?.dispose();
        if (obj.material) obj.material.dispose();
      });
    };
  }, [model, renderMode]);

  if (!model) return null;

  return (
    <group ref={groupRef}>
      <primitive object={model} />
    </group>
  );
};

export default function Viewport({ model, viewerState }) {
  const { projection, renderMode, position, rotation, scale } = viewerState;

  const aspect = window.innerWidth / window.innerHeight;
  const isoSize = 4; // Adjust zoom for isometric

  return (
    <div style={{ width: '100%', height: '100%', background: 'var(--bg-primary)' }}>
      <Canvas shadows gl={{ antialias: true }}>
        {projection === 'perspective' ? (
          <PerspectiveCamera makeDefault position={[0, 0, 4]} fov={45} />
        ) : (
          <OrthographicCamera 
            makeDefault 
            position={[4, 4, 4]} 
            zoom={100}
            left={-isoSize * aspect} 
            right={isoSize * aspect} 
            top={isoSize} 
            bottom={-isoSize} 
            near={-100} 
            far={100} 
          />
        )}
        
        {/* Lights mapping to Python: LIGHT_DIRECTION = (0.35, -0.45, -1.0) */}
        {/* The directional light in 3js looks AT the origin from position. So invert direction. */}
        <ambientLight intensity={0.4} />
        <directionalLight 
          position={[-0.35, 0.45, 1.0]} 
          intensity={2.5} 
          castShadow 
        />
        <directionalLight 
          position={[0.35, -0.45, -1.0]} 
          intensity={0.5} 
        />

        <Environment preset="city" opacity={0.2} />
        
        <Grid 
          infiniteGrid 
          fadeDistance={20} 
          sectionColor="#4f46e5" 
          cellColor="#27272a" 
          position={[0, -1.5, 0]} 
        />

        <ModelRenderer 
          model={model} 
          renderMode={renderMode} 
          viewerPosition={position}
          viewerRotation={rotation}
          viewerScale={scale}
        />

        <OrbitControls 
          makeDefault
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          target={[0, 0, 0]}
        />
      </Canvas>
    </div>
  );
}
