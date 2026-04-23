export function computeEulerStats(geometry) {
  if (!geometry) {
    return { V: 0, E: 0, F: 0, euler: 0, status: 'Nenhum' };
  }

  const index = geometry.getIndex();
  const position = geometry.getAttribute('position');

  if (!index || !position) {
    return { V: 0, E: 0, F: 0, euler: 0, status: 'Inválido' };
  }

  const verticesCount = position.count;
  const facesCount = index.count / 3;

  const edges = new Set();

  for (let i = 0; i < index.count; i += 3) {
    const a = index.getX(i);
    const b = index.getX(i + 1);
    const c = index.getX(i + 2);

    const ab = a < b ? `${a}-${b}` : `${b}-${a}`;
    const bc = b < c ? `${b}-${c}` : `${c}-${b}`;
    const ca = c < a ? `${c}-${a}` : `${a}-${c}`;

    edges.add(ab);
    edges.add(bc);
    edges.add(ca);
  }

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
