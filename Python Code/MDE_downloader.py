import os
import math
import requests
import numpy as np
import rasterio as rio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from tqdm import tqdm

# --- CONFIGURAÇÃO INICIAL ---
# BBOX: Área de interesse (Min Lon, Min Lat, Max Lon, Max Lat)
BBOX = (-47.0, -22.4, -46.8, -22.2)
ARQUIVO_MDE_LOCAL = "mde_baixado.tif"
# Dimensão fixa da matriz de saída, crucial para processamento em Assembly (MARS)
MATRIX_DIMENSION = 128 

# --- CLASSE: Downloader de MDE (Copernicus GLO-30) ---
class CopernicusDownloader:
    """
    Baixa dados do Copernicus DEM GLO-30 (30m) diretamente do bucket público da AWS via HTTP.
    Evita o uso de GDAL VSI/VRT que pode ser bloqueado por firewalls.
    """
    # Base URL do Bucket público da AWS para o Copernicus DEM
    BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com"

    def __init__(self, bbox):
        self.bbox = bbox

    def _get_tile_name(self, lat, lon):
        """Calcula o nome do tile no padrão Copernicus (ex: Copernicus_DSM_COG_10_S20_00_W044_00_DEM)"""
        # Arredonda para o grau inteiro inferior (floor)
        lat_int = math.floor(lat)
        lon_int = math.floor(lon)
        
        # Formata N/S e E/W
        ns = 'S' if lat_int < 0 else 'N'
        ew = 'W' if lon_int < 0 else 'E'
        
        # Formata os números (lat 2 digitos, lon 3 digitos)
        lat_str = f"{abs(lat_int):02d}"
        lon_str = f"{abs(lon_int):03d}"
        
        # Monta o nome
        # Exemplo real: Copernicus_DSM_COG_10_S20_00_W044_00_DEM
        return f"Copernicus_DSM_COG_10_{ns}{lat_str}_00_{ew}{lon_str}_00_DEM"

    def download(self, output_filename):
        # Pega o canto inferior esquerdo do BBOX para determinar o tile principal
        lon_min, lat_min = self.bbox[0], self.bbox[1]
        
        # Usa lat_min e lon_min para calcular o tile (o Copernicus usa o canto superior esquerdo ou inferior esquerdo do tile)
        tile_name = self._get_tile_name(lat_min, lon_min) 
        print(f"📡 Calculando Tile correspondente: {tile_name}")
        
        # Caminho completo na AWS S3 (estrutura de pastas padrão)
        url = f"{self.BASE_URL}/{tile_name}/{tile_name}.tif"
        
        print(f"🌐 Tentando baixar de: {url}")
        
        try:
            # Faz a requisição HTTP com stream ativado para arquivos grandes
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_filename, 'wb') as file, tqdm(
                    desc=output_filename,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
                
                print("✅ Download concluído com sucesso via HTTP!")
                return True
            else:
                print(f"❌ Falha no download. Código HTTP: {response.status_code}")
                print("Motivo provável: A URL calculada não existe ou o tile não está disponível publicamente.")
                return False
                
        except Exception as e:
            print(f"🚨 Erro de conexão: {e}")
            return False

# --- FUNÇÃO: Carregamento do MDE e Exportação da Matriz Pura (Dimensão Fixa) ---
def construir_matriz_mde(arquivo_entrada, bbox, dimension):
    """Lê o GeoTIFF baixado, recorta e retorna a matriz MDE pura na dimensão fixa."""
    if not os.path.exists(arquivo_entrada):
        print("Arquivo de entrada não encontrado. Pulando construção da matriz.")
        return None

    try:
        with rio.open(arquivo_entrada) as src:
            print(f"\n⚙️ Construindo matriz MDE a partir de: {arquivo_entrada}")
            print(f"Dimensão de saída fixa: {dimension}x{dimension}")
            
            # Recorta (Crop) a área exata do BBOX
            try:
                window = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], transform=src.transform)
                
                # Lê os dados, forçando a reamostragem (resampling) para a dimensão fixa
                mde_data = src.read(
                    1, 
                    window=window, 
                    # FORÇA a dimensão de saída
                    out_shape=(dimension, dimension),
                    # Usa reamostragem Bilinear para suavizar a transição de resolução
                    resampling=Resampling.bilinear
                ).astype('float32')
            except Exception as e:
                print(f"Erro ao cortar BBOX (pode estar fora do tile): {e}")
                print("Lendo arquivo inteiro como fallback...")
                mde_data = src.read(1).astype('float32')
            
            # Não fazemos tratamento de NoData aqui. A matriz é retornada com os valores brutos.
            
            print(f"✅ Matriz MDE construída com dimensões: {mde_data.shape}")
            return mde_data

    except Exception as e:
        print(f"Erro no processamento rasterio: {e}")
        return None

# --- FUNÇÃO: Exportação ---
def exportar_txt(matriz, nome):
    # A exportação usa o formato %.4f (quatro casas decimais) e o separador de espaço (padrão)
    if matriz is not None:
        np.savetxt(nome, matriz, fmt='%.4f', delimiter=' ')
        print(f"💾 Arquivo salvo: {nome}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("=== INICIANDO SISTEMA DE AQUISIÇÃO E CONSTRUÇÃO DE MATRIZ ===")
    
    # 1. Download
    downloader = CopernicusDownloader(BBOX)
    sucesso = downloader.download(ARQUIVO_MDE_LOCAL)
    
    mde_final = None

    # 2. Construção da Matriz MDE
    if sucesso:
        # Passa a dimensão fixa para a função de construção
        mde_final = construir_matriz_mde(ARQUIVO_MDE_LOCAL, BBOX, MATRIX_DIMENSION)
    else:
        # Fallback de Simulação (também na dimensão fixa)
        print(f"\n⚠️ Usando dados simulados devido à falha no download. Dimensão: {MATRIX_DIMENSION}x{MATRIX_DIMENSION}")
        # Cria um MDE falso 128x128
        simulated_data = np.arange(MATRIX_DIMENSION * MATRIX_DIMENSION).reshape(MATRIX_DIMENSION, MATRIX_DIMENSION)
        mde_final = simulated_data + 800

    # 3. Exportação
    exportar_txt(mde_final, "matriz_elevacao.txt")
    
    print("\n✅ Concluído. Matriz de elevação pura exportada na dimensão fixa.")