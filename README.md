# TerraPOI-MIPS

> **Aviso:** Este projeto foi desenvolvido para fins didáticos, como parte das atividades da disciplina de Arquitetura e Organização de Computadores da Universidade Federal de São Paulo (UNIFESP). O código e a documentação aqui presentes têm caráter acadêmico e não se destinam a uso profissional sem as devidas adaptações e validações.

Detecção de pontos de interesse (POIs) em Modelos Digitais de Elevação (MDE) com Assembly MIPS (MARS),
com apoio de scripts Python para obtenção dos dados. Relatório completo em `docs/`.

## Estrutura de diretórios

```
TerraPOI-MIPS/
├── src/            # Código Assembly MIPS (main, math, parser, poi_output, spatial_filter — extensão .mar)
├── python/         # Scripts Python (MDE_downloader.py) e requirements.txt
├── data/
│   ├── input_maps/ # Mapas de entrada por região: GeoTIFF (.tif) e matriz de elevação (mde.txt)
│   └── generated/  # Saídas do MARS (poi_output.txt) por região
├── docs/           # Relatório do projeto (PDF)
├── tests/          # Reservado para dados de teste (vazio por enquanto)
├── README.md
└── ESTRUTURA.md    # Detalhes da organização e dos ajustes feitos no código
```

## Descrição das pastas

- **`src/`**: programa principal (`main.mar`) e módulos incluídos via `.include`: leitura/parse da matriz,
  cálculo de slope/aspect, saída em arquivo e filtro espacial 3x3.
- **`python/`**: obtém o MDE (Copernicus GLO-30), recorta e exporta uma matriz 128x128 em texto.
  Dependências em `requirements.txt`.
- **`data/input_maps/`**: regiões de estudo, cada uma com `mde.txt` (matriz de elevação) e o `.tif` de origem:
  `regiao_1_vale_paraiba`, `regiao_2_sao_paulo`, `regiao_3_campos_do_jordao` e `regiao_4`.
  A pasta `regiao_personalizada` é criada pelo `MDE_downloader.py`.
- **`data/generated/`**: matriz binária de POIs (`poi_output.txt`) de cada região, com a mesma divisão de pastas.
- **`docs/`**: `Relatório1_AOC_IB_3.pdf`.

## Como usar

Execute tudo **a partir da raiz do repositório** (os caminhos são relativos a ela).

1. (Opcional) Gerar uma matriz própria, que usa a internet para baixar o tile:
   ```
   python python/MDE_downloader.py
   ```
   Grava `data/input_maps/regiao_personalizada/mde.txt` (e o `.tif` baixado).
2. Rodar o MARS na raiz do repositório e abrir `src/main.mar`:
   ```
   java -jar Mars.jar                      # interface gráfica
   java -jar Mars.jar nc src/main.mar      # linha de comando
   ```
3. O programa pergunta a **região** (1 a 5; 5 = personalizada) e o **hemisfério** (0 = Norte, 1 = Sul,
   2 = Equador). Valores inválidos usam o padrão (região 1, hemisfério Sul).
4. O resultado é gravado em `data/generated/<região>/poi_output.txt`.
