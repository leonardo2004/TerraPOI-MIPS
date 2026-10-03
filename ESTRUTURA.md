# Estrutura do repositório

## Árvore

```
TerraPOI-MIPS/
├── src/                          # Código Assembly MIPS (MARS)
│   ├── main.mar
│   ├── math.mar
│   ├── parser.mar
│   ├── poi_output.mar
│   └── spatial_filter.mar
├── python/                       # Scripts Python
│   ├── MDE_downloader.py
│   └── requirements.txt
├── data/
│   ├── input_maps/               # Mapas de entrada (GeoTIFF + mde.txt)
│   │   ├── regiao_1_vale_paraiba/
│   │   ├── regiao_2_sao_paulo/
│   │   ├── regiao_3_campos_do_jordao/
│   │   ├── regiao_4/
│   │   └── regiao_personalizada/ # criada pelo MDE_downloader.py
│   └── generated/                # Saídas do MARS (poi_output.txt)
│       ├── regiao_1_vale_paraiba/
│       ├── regiao_2_sao_paulo/
│       ├── regiao_3_campos_do_jordao/
│       ├── regiao_4/
│       └── regiao_personalizada/
├── docs/
│   └── Relatório1_AOC_IB_3.pdf
├── tests/                        # Reservado para dados de teste (ainda vazio)
│   └── .gitkeep
├── README.md
└── ESTRUTURA.md
```

## Arquivos movidos e renomeados (antigo → novo)

| Antigo | Novo |
|---|---|
| `Mips Code/*.mar` | `src/*.mar` (mesmos nomes) |
| `Python Code/MDE_downloader.py`, `requirements.txt` | `python/` (mesmos nomes) |
| `Relatório1_AOC_IB_3.pdf` | `docs/Relatório1_AOC_IB_3.pdf` |
| `Região 1 - Vale paraiba/` | `data/input_maps/regiao_1_vale_paraiba/` e `data/generated/regiao_1_vale_paraiba/` |
| `Região 2 - São paulo/` | `data/input_maps/regiao_2_sao_paulo/` e `data/generated/regiao_2_sao_paulo/` |
| `Região 3 - Campos de jordão/` | `data/input_maps/regiao_3_campos_do_jordao/` e `data/generated/regiao_3_campos_do_jordao/` |
| `Região 4/` | `data/input_maps/regiao_4/` e `data/generated/regiao_4/` |
| `mde região N.txt` (e variações) | `.../regiao_N.../mde.txt` |
| `região N.tif` / `regiao N.tif` (+ `.aux.xml`) | `.../regiao_N.../regiao_N.tif` (+ `.aux.xml`) |
| `poi_output.txt` de cada região | `data/generated/<região>/poi_output.txt` |

Os nomes foram padronizados sem acentos e sem espaços para funcionarem de forma confiável nos caminhos
usados pelo MARS e pelo Python. O conteúdo dos arquivos de dados não foi alterado.

## Ajustes feitos no código para os novos caminhos

- **`src/main.mar`**: os caminhos de entrada/saída agora são uma tabela de 5 regiões, relativos à raiz do
  repositório (`data/input_maps/<região>/mde.txt` e `data/generated/<região>/poi_output.txt`).
  O programa pergunta a região (1–5) no início; valor inválido usa a região 1. Também imprime o arquivo lido.
  `filename` e `output_filename` passaram de strings para ponteiros preenchidos em tempo de execução.
- **`src/poi_output.mar`**: `save_matrix_to_file` passou a usar o ponteiro `output_filename` (`lw` em vez de `la`).
- **`python/MDE_downloader.py`**: saídas gravadas em `data/input_maps/regiao_personalizada/`
  (`mde_baixado.tif` e `mde.txt`), calculadas a partir da localização do script, então podem ser
  executadas de qualquer diretório. A lógica de download e de processamento não mudou.
- Os `.include` em `main.mar` não foram alterados: os cinco `.mar` continuam na mesma pasta.
- O programa deve ser executado com a raiz do repositório como diretório de trabalho do MARS.
