# Visualizador de Polígonos 3D

Um aplicativo web interativo para visualizar e analisar modelos 3D no formato OBJ/MTL. Desenvolvido com React, Three.js e Vite, oferece ferramentas para manipular câmeras, analisar estatísticas de Euler e inspecionar propriedades de modelos 3D. O desenvolvimento faz parte da disciplina de Computação Gráfica, do curso de graduação em Ciência da Computação.

## Funcionalidades

- **Carregamento de Modelos**: Suporte para arquivos OBJ e MTL
- **Visualização 3D**: Renderização em tempo real com Three.js
- **Controle de Câmera**: 
  - Rotação (click esquerdo + arrastar)
  - Zoom (roda do mouse)
  - Panorama (click direito + arrastar)
  - Reset de câmera
- **Análise de Topologia**: Cálculo de características de Euler e análise topológica
- **Inspeção de Materiais**: Visualização de propriedades de materiais dos modelos

## Instalação e Execução

### Pré-requisitos

- Node.js 16+ instalado
- npm ou yarn
- Python 3.10+ instalado

### Passo 1: Instalação de Dependências

```bash
npm install
```

### Passo 2: Executar o Backend

Em um terminal:

```bash
python3 backend/api_server.py --host 127.0.0.1 --port 8000
```

### Passo 3: Executar o Frontend

Em outro terminal:

```bash
npm run dev
```

O frontend encaminha chamadas `/api` para o backend local em `http://127.0.0.1:8000`.
O aplicativo será acessível em `http://localhost:5173` (ou outra porta indicada no terminal).

## Como Usar

### Carregar um Modelo

1. **Opção 1 - Arrastar e Soltar**: Arraste arquivos `.obj` e `.mtl` diretamente na tela
2. **Opção 2 - Botão de Upload**: Clique no botão "Abrir OBJ" na barra de ferramentas e selecione os arquivos

### Controlar a Câmera

- **Rotacionar**: Clique esquerdo + arraste o mouse
- **Zoom**: Use a roda do mouse para aproximar/afastar
- **Panorama**: Clique direito + arraste o mouse
- **Resetar Câmera**: Use o botão de reset na barra de ferramentas

### Alternar Modo de Visualização

- **Wireframe**: Exibe apenas as arestas do modelo
- **Preenchido**: Exibe o modelo com faces preenchidas
- **Pontos**: Exibe apenas os vértices

### Analisar o Modelo

- **Estatísticas de Euler**: Característica de Euler (V - E + F)
  - V: Número de vértices
  - E: Número de arestas
  - F: Número de faces
- **Informações Topológicas**: Gênero e outras propriedades
- **Propriedades de Materiais**: Cores, brilho e outras propriedades dos materiais aplicados

### Atalhos de Teclado

- **H**: Abrir ajuda
- **R**: Resetar câmera
- **W**: Alternar wireframe
- **P**: Alternar modo de pontos
- **D**: Carregar modelo padrão (cubo)

## Formatos de Arquivo Suportados

- **OBJ** (.obj): Formato de geometria 3D
- **MTL** (.mtl): Formato de definição de materiais

## Tecnologias Utilizadas

- **React 19**
- **Three.js**: Biblioteca 3D WebGL
- **React Three Fiber**: Renderizador React para Three.js
- **Drei**: Utilitários para React Three Fiber
- **Vite**
- **Tailwind CSS**

## Documentações

- [Documentação Three.js](https://threejs.org/docs/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber/)
