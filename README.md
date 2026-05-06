# Visualizador de Polígonos 3D

Um aplicativo web interativo para visualizar e analisar modelos 3D no formato OBJ/MTL. Desenvolvido com React, Three.js, Vite e Python, oferece ferramentas para manipular câmeras, analisar estatísticas de Euler e inspecionar propriedades de modelos 3D. O desenvolvimento faz parte da disciplina de Computação Gráfica, do curso de graduação em Ciência da Computação.

## Funcionalidades

- **Carregamento de Modelos**: Suporte para arquivos OBJ e MTL
- **Visualização 3D**: Renderização em tempo real com Three.js
- **Controle de Câmera**: 
  - Rotação (clique esquerdo + arrastar)
  - Zoom (roda do mouse)
  - Panorama (clique direito + arrastar)
  - Reset de transformações e visualização
- **Análise de Topologia**: Cálculo de vértices, arestas, faces, característica de Euler e status da malha
- **Inspeção de Materiais**: Visualização de nomes e cores dos materiais dos modelos

## Instalação e Execução

### Pré-requisitos

- Node.js 20.19+ ou 22.12+ instalado
- npm
- Python 3.10+ instalado

### Passo 1: Instalação de Dependências

```bash
npm install
```

### Passo 2: Executar o Backend

Em um terminal:

```bash
python3 backend/api_server.py
```

Por padrão, a API inicia em `http://127.0.0.1:8000`. Use `--host` e `--port` apenas se quiser alterar esses valores.

### Passo 3: Executar o Frontend

Em outro terminal:

```bash
npm run dev
```

O frontend encaminha chamadas `/api` para o backend local em `http://127.0.0.1:8000`.
O aplicativo será acessível em `http://localhost:5173` (ou outra porta indicada no terminal).

## Como Usar

### Carregar um Modelo

1. **Opção 1 - Arrastar e Soltar**: Arraste um arquivo `.obj` e, opcionalmente, um arquivo `.mtl` diretamente na tela
2. **Opção 2 - Botão de Upload**: Clique no botão "Abrir OBJ" na barra de ferramentas e selecione o `.obj` e, se houver, o `.mtl`

### Controlar a Câmera

- **Rotacionar**: Clique esquerdo + arraste o mouse
- **Zoom**: Use a roda do mouse para aproximar/afastar
- **Panorama**: Clique direito + arraste o mouse
- **Resetar Transformações e Visualização**: Use o botão de reset na barra de ferramentas

### Alternar Modo de Visualização

- **Wireframe**: Exibe apenas as arestas do modelo
- **Preenchido**: Exibe o modelo com faces preenchidas
- **Ambos**: Exibe o modelo preenchido com as arestas sobrepostas

### Analisar o Modelo

- **Estatísticas de Euler**: Característica de Euler (V - E + F)
  - V: Número de vértices
  - E: Número de arestas
  - F: Número de faces
- **Status da Malha**: Indica se a característica de Euler é compatível com uma malha fechada e convexa
- **Propriedades de Materiais**: Cores dos materiais aplicados

### Atalhos de Teclado

- **P**: Alternar projeção entre perspectiva e isométrica
- **W / S / B**: Alternar renderização entre wireframe, sólido e ambos
- **R / T / Shift+S / C**: Alternar modo de transformação entre rotação, translação, escala e cisalhamento
- **Setas**: Aplicar a transformação do modo atual
- **X / Y / Z**: Rotacionar no eixo correspondente no modo de rotação
- **Shift + X / Y / Z**: Rotacionar no sentido inverso no eixo correspondente
- **Esc**: Resetar transformações e visualização

## Formatos de Arquivo Suportados

- **OBJ** (.obj): Formato de geometria 3D
- **MTL** (.mtl): Formato de definição de materiais

## Tecnologias Utilizadas

- **React 19**
- **Three.js**: Biblioteca 3D WebGL
- **React Three Fiber**: Renderizador React para Three.js
- **Drei**: Utilitários para React Three Fiber
- **Vite**
- **Python 3**: Backend local para leitura e processamento de arquivos OBJ/MTL
- **CSS customizado**: Estilização com variáveis CSS e estilos locais

## Testes e Verificação

```bash
npm run lint
npm run build
cd backend && python3 -m unittest discover tests
```

## Documentações

- [Documentação Three.js](https://threejs.org/docs/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber/)
