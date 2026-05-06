import { useState, useCallback } from 'react';
import { parseModelFiles } from '../api/models';
import { createModelFromMesh } from '../utils/meshFactory';

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
      const mesh = await parseModelFiles(objFile, mtlFile);
      const { model: loadedModel, materialsData: loadedMaterials } = createModelFromMesh(mesh);

      setModel(loadedModel);
      setStats(mesh.eulerStats);
      setMaterialsData(loadedMaterials);
      setFileName(mesh.sourceName || objFile.name);

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
