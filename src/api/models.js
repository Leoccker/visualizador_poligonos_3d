export async function parseModelFiles(objFile, mtlFile) {
  const payload = {
    obj: {
      name: objFile.name,
      content: await objFile.text(),
    },
  };

  if (mtlFile) {
    payload.mtl = {
      name: mtlFile.name,
      content: await mtlFile.text(),
    };
  }

  let response;
  try {
    response = await fetch('/api/models/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new Error(
      'Backend indisponivel. Inicie a API Python em http://127.0.0.1:8000.',
      { cause: error },
    );
  }

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error('Resposta invalida do backend.');
  }

  if (!response.ok) {
    throw new Error(data?.error || 'Erro ao processar modelo no backend.');
  }

  if (!data?.mesh) {
    throw new Error('Resposta do backend nao contem dados de malha.');
  }

  return data.mesh;
}
