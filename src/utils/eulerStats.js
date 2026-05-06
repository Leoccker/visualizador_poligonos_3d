/**
 * Compute Euler characteristic stats (V, E, F) from a Three.js BufferGeometry.
 * 
 * Handles both indexed and non-indexed geometries.
 * Deduplicates vertices by POSITION ONLY (ignoring normals/UVs) so that
 * shared vertices across faces with different normals are counted once.
 */
export function computeEulerStats(geometry) {
  if (!geometry) {
    return { V: 0, E: 0, F: 0, euler: 0, status: 'Nenhum' };
  }

  const position = geometry.getAttribute('position');
  if (!position) {
    return { V: 0, E: 0, F: 0, euler: 0, status: 'Inválido' };
  }

  const index = geometry.getIndex();

  // Build triangle list (each triangle = 3 raw vertex indices into position buffer)
  const triangles = [];
  if (index) {
    for (let i = 0; i < index.count; i += 3) {
      triangles.push([index.getX(i), index.getX(i + 1), index.getX(i + 2)]);
    }
  } else {
    // Non-indexed: every 3 consecutive positions form a triangle
    for (let i = 0; i < position.count; i += 3) {
      triangles.push([i, i + 1, i + 2]);
    }
  }

  if (triangles.length === 0) {
    return { V: 0, E: 0, F: 0, euler: 0, status: 'Inválido' };
  }

  // Deduplicate vertices by position only (ignore normals, UVs, etc.)
  // This is critical because OBJLoader duplicates vertices per-face when
  // normals differ (e.g. flat shading on a cube: 24 positions but only 8 unique)
  const PRECISION = 6;
  const posMap = new Map(); // "x,y,z" -> unique ID
  let nextId = 0;

  function getUniqueVertexId(rawIndex) {
    const x = position.getX(rawIndex).toFixed(PRECISION);
    const y = position.getY(rawIndex).toFixed(PRECISION);
    const z = position.getZ(rawIndex).toFixed(PRECISION);
    const key = `${x},${y},${z}`;

    if (!posMap.has(key)) {
      posMap.set(key, nextId++);
    }
    return posMap.get(key);
  }

  // Remap triangles to unique vertex IDs and collect edges
  const edges = new Set();
  const facesCount = triangles.length;

  for (const [rawA, rawB, rawC] of triangles) {
    const a = getUniqueVertexId(rawA);
    const b = getUniqueVertexId(rawB);
    const c = getUniqueVertexId(rawC);

    // Add edges (sorted to avoid duplicates)
    const ab = a < b ? `${a}-${b}` : `${b}-${a}`;
    const bc = b < c ? `${b}-${c}` : `${c}-${b}`;
    const ca = c < a ? `${c}-${a}` : `${a}-${c}`;

    edges.add(ab);
    edges.add(bc);
    edges.add(ca);
  }

  const verticesCount = posMap.size;
  const edgeCount = edges.size;
  const eulerValue = verticesCount - edgeCount + facesCount;

  return {
    V: verticesCount,
    E: edgeCount,
    F: facesCount,
    euler: eulerValue,
    status: eulerValue === 2 ? 'OK' : 'Não fechado/não convexo',
  };
}
