import * as THREE from 'three';

const DEFAULT_MATERIAL_KEY = '__default__';
const DEFAULT_MATERIAL_COLOR = '#cccccc';

function normalizeColor(color) {
  if (typeof color !== 'string' || color.length === 0) {
    return DEFAULT_MATERIAL_COLOR;
  }

  return color.startsWith('#') ? color : `#${color}`;
}

function sidebarColor(color) {
  return normalizeColor(color).replace(/^#/, '');
}

function createMaterial(record) {
  return new THREE.MeshStandardMaterial({
    color: normalizeColor(record?.color),
    flatShading: true,
    side: THREE.FrontSide,
  });
}

export function createModelFromMesh(mesh) {
  const vertices = mesh?.vertices ?? [];
  const triangles = mesh?.triangles ?? [];

  if (vertices.length === 0 || triangles.length === 0) {
    throw new Error('Malha sem vertices ou faces para renderizar.');
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(vertices.flat(), 3),
  );

  const materialRecords = Array.isArray(mesh.materials) ? mesh.materials : [];
  const materialIndexByName = new Map();
  const materials = [];

  const addMaterial = (record, key) => {
    const index = materials.length;
    materials.push(createMaterial(record));
    materialIndexByName.set(key, index);
    return index;
  };

  materialRecords.forEach((material) => {
    addMaterial(material, material.name);
  });

  addMaterial({ color: DEFAULT_MATERIAL_COLOR }, DEFAULT_MATERIAL_KEY);
  const defaultMaterialIndex = materialIndexByName.get(DEFAULT_MATERIAL_KEY);

  const indices = [];
  let currentGroup = null;

  triangles.forEach((triangle, triangleIndex) => {
    const vertexIndices = triangle.vertexIndices ?? [];
    if (vertexIndices.length !== 3) {
      throw new Error(`Face invalida no indice ${triangleIndex}.`);
    }

    indices.push(...vertexIndices);

    const materialIndex =
      materialIndexByName.get(triangle.materialName) ?? defaultMaterialIndex;
    const start = triangleIndex * 3;

    if (currentGroup?.materialIndex === materialIndex) {
      currentGroup.count += 3;
    } else {
      if (currentGroup) {
        geometry.addGroup(
          currentGroup.start,
          currentGroup.count,
          currentGroup.materialIndex,
        );
      }
      currentGroup = { start, count: 3, materialIndex };
    }
  });

  if (currentGroup) {
    geometry.addGroup(
      currentGroup.start,
      currentGroup.count,
      currentGroup.materialIndex,
    );
  }

  geometry.setIndex(indices);
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  const modelMesh = new THREE.Mesh(geometry, materials);
  modelMesh.castShadow = true;
  modelMesh.receiveShadow = true;

  const group = new THREE.Group();
  group.name = mesh.sourceName || 'Modelo OBJ';
  group.add(modelMesh);

  return {
    model: group,
    materialsData: materialRecords.map((material) => ({
      name: material.name,
      color: sidebarColor(material.color),
    })),
  };
}
