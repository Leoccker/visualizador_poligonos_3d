import { useState, useCallback } from 'react';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import { computeEulerStats } from '../utils/eulerStats';

export function useModelLoader() {
  const [model, setModel] = useState(null);
  const [stats, setStats] = useState(null);
  const [materialsData, setMaterialsData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState('');

  const loadFromFiles = useCallback(async (objFile, mtlFile) => {
    setIsLoading(true);
    setError(null);
    setFileName(objFile.name);

    try {
      let materials = null;

      // Load MTL if provided
      if (mtlFile) {
        const mtlUrl = URL.createObjectURL(mtlFile);
        const mtlLoader = new MTLLoader();
        
        // This sets the base url for the materials (textures etc), although this project doesn't use textures much
        mtlLoader.setPath(''); 
        
        materials = await new Promise((resolve, reject) => {
          mtlLoader.load(mtlUrl, resolve, undefined, reject);
        });
        
        materials.preload();
        URL.revokeObjectURL(mtlUrl);
      }

      // Load OBJ
      const objUrl = URL.createObjectURL(objFile);
      const objLoader = new OBJLoader();
      if (materials) {
        objLoader.setMaterials(materials);
      }

      const obj = await new Promise((resolve, reject) => {
        objLoader.load(objUrl, resolve, undefined, reject);
      });
      URL.revokeObjectURL(objUrl);

      // Process object (center and normalize scale)
      let combinedGeometry = new THREE.BufferGeometry();
      const meshes = [];
      const extractedMaterials = [];

      obj.traverse((child) => {
        if (child.isMesh) {
          meshes.push(child);
          // Fallback material if none loaded
          if (!materials && !Array.isArray(child.material)) {
              child.material = new THREE.MeshStandardMaterial({ color: 0xcccccc });
          }
          
          if (child.material) {
             const mats = Array.isArray(child.material) ? child.material : [child.material];
             mats.forEach(m => {
                 if(m.name && !extractedMaterials.find(exM => exM.name === m.name)) {
                     extractedMaterials.push({ name: m.name, color: m.color.getHexString() });
                 }
             });
          }
        }
      });

      setMaterialsData(extractedMaterials);

      if (meshes.length === 0) {
        throw new Error("Nenhuma malha encontrada no arquivo OBJ.");
      }

      // Compute bounding box to center and scale
      const box = new THREE.Box3().setFromObject(obj);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxExtent = Math.max(size.x, size.y, size.z);
      const scaleFactor = 2.0 / (maxExtent > 0 ? maxExtent : 1.0); // Scale to fit in a 2x2x2 box

      obj.position.sub(center);
      
      const wrapper = new THREE.Group();
      wrapper.add(obj);
      wrapper.scale.set(scaleFactor, scaleFactor, scaleFactor);

      // Collect Euler stats from all geometries combined or just the first
      // Assuming single main mesh for Euler stats for simplicity
      const mainMesh = meshes.reduce((max, mesh) => 
        (mesh.geometry.attributes.position.count > max.geometry.attributes.position.count) ? mesh : max
      , meshes[0]);

      const eulerStats = computeEulerStats(mainMesh.geometry);
      
      setModel(wrapper);
      setStats(eulerStats);

    } catch (err) {
      console.error(err);
      setError(err.message || "Erro ao carregar modelo.");
      setModel(null);
      setStats(null);
      setMaterialsData([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadDefaultCube = useCallback(async () => {
    setIsLoading(true);
    try {
      const responseObj = await fetch('/models/cubo.obj');
      const responseMtl = await fetch('/models/cubo.mtl');
      
      if (!responseObj.ok || !responseMtl.ok) {
        throw new Error("Failed to fetch default models");
      }

      const objBlob = await responseObj.blob();
      const mtlBlob = await responseMtl.blob();
      
      await loadFromFiles(
        new File([objBlob], "cubo.obj"),
        new File([mtlBlob], "cubo.mtl")
      );
    } catch (e) {
      console.warn("Could not load default cube. Ignoring.", e);
      setIsLoading(false);
    }
  }, [loadFromFiles]);

  return { model, stats, materialsData, isLoading, error, fileName, loadFromFiles, loadDefaultCube };
}
