# Visualizador 3D de Poligonos

Aplicacao em Python com `tkinter` para carregar modelos `.obj`, ler materiais `.mtl` e visualizar a malha em 3D com renderizacao em software.

## Como executar

```bash
python3 main.py
```

## Controles

- `Abrir OBJ`: seleciona um arquivo `.obj`
- `P`: alterna entre projecao isometrica e perspectiva
- `W`: wireframe
- `S`: solido
- `B`: wireframe + solido
- `R`: modo rotacao
- `T`: modo translacao
- `Shift+S`: modo escala
- `Setas`: aplicam a transformacao do modo atual
- `X`, `Y`, `Z`: rotacionam em torno do eixo atual quando o modo e rotacao
- `Shift+X`, `Shift+Y`, `Shift+Z`: rotacao no sentido oposto
- `Mouse`: arrastar com o botao esquerdo para rotacao continua
- `Esc`: reset das transformacoes

## Recursos implementados

- Parser OBJ com suporte a `v`, `vt`, `vn`, `f`, `mtllib`, `usemtl`
- Faces nos formatos `f v`, `f v//vn`, `f v/vt/vn`
- Suporte a indices negativos em faces
- Triangulacao automatica por fan para poligonos com 4+ vertices
- Centralizacao na origem e normalizacao de escala
- Calculo de normais por face via produto vetorial
- Backface culling pelo sinal da componente `Z` da normal transformada
- Sombreamento simples por face com luz direcional fixa
- Estatisticas `V`, `E`, `F` e verificacao da Formula de Euler ao carregar o modelo
