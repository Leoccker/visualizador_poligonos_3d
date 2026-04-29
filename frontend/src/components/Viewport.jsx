import { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, OrthographicCamera, Grid, Environment } from '@react-three/drei';
import * as THREE from 'three';

// Tag used to identify wireframe helpers we add so we can clean them up
const WIRE_TAG = '__wireOverlay';
const BOTH_MODE_WIRE_SCALE = 1.0; // wireframe overlays the solid model at the same size

function disposeWireOverlay(root) {
  if (!root) return;

  root.traverse((child) => {
    child.geometry?.dispose();

    if (Array.isArray(child.material)) {
      child.material.forEach((mat) => mat.dispose());
    } else {
      child.material?.dispose();
    }
  });
}

function removeWireOverlays(model) {
  const overlays = [];

  model.traverse((child) => {
    if (child.userData[WIRE_TAG]) overlays.push(child);
  });

  overlays.forEach((overlay) => {
    overlay.parent?.remove(overlay);
    disposeWireOverlay(overlay);
  });
}

function createCenteredWireOverlay(model) {
  const overlay = new THREE.Group();
  const rootInverse = new THREE.Matrix4();

  overlay.userData[WIRE_TAG] = true;
  overlay.scale.setScalar(BOTH_MODE_WIRE_SCALE);

  model.updateMatrixWorld(true);
  rootInverse.copy(model.matrixWorld).invert();

  model.traverse((child) => {
    if (!child.isMesh) return;

    const edgesGeom = new THREE.WireframeGeometry(child.geometry);
    const edgesMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.75,
      depthTest: true,
    });
    const edgesLine = new THREE.LineSegments(edgesGeom, edgesMat);

    edgesLine.matrix.copy(rootInverse).multiply(child.matrixWorld);
    edgesLine.matrixAutoUpdate = false;
    overlay.add(edgesLine);
  });

  return overlay;
}

const ModelRenderer = ({ model, renderMode, viewerPosition, viewerRotation, viewerScale, viewerShear }) => {
  const groupRef = useRef();
  const tempPosition = useRef(new THREE.Vector3());
  const tempQuaternion = useRef(new THREE.Quaternion());
  const tempScale = useRef(new THREE.Vector3());
  const tempShear = useRef(new THREE.Matrix4());

  // Apply transformations from viewer state
  useFrame(() => {
    if (groupRef.current) {
      const position = tempPosition.current.set(viewerPosition[0], viewerPosition[1], viewerPosition[2]);
      const quaternion = tempQuaternion.current.setFromEuler(
        new THREE.Euler(viewerRotation[0], viewerRotation[1], viewerRotation[2], 'XYZ')
      );
      const scale = tempScale.current.set(viewerScale, viewerScale, viewerScale);

      groupRef.current.matrix.compose(position, quaternion, scale);
      tempShear.current.set(
        1, viewerShear[0], viewerShear[1], 0,
        0, 1, viewerShear[2], 0,
        0, 0, 1, 0,
        0, 0, 0, 1
      );
      groupRef.current.matrix.multiply(tempShear.current);
      groupRef.current.matrixAutoUpdate = false;
    }
  });

  // Apply render mode: manages mesh materials and the enlarged wire overlay.
  useEffect(() => {
    if (!model) return;

    // 1. Remove any previously-added wireframe helpers
    removeWireOverlays(model);

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

    });

    // 3. For "both": add one centered wireframe copy around the solid model
    if (renderMode === 'both') {
      const wireOverlay = createCenteredWireOverlay(model);
      model.add(wireOverlay);
    }

    // Cleanup when renderMode changes or unmounts
    return () => {
      if (!model) return;
      removeWireOverlays(model);
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
  const { projection, renderMode, position, rotation, scale, shear } = viewerState;

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
          viewerShear={shear}
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
