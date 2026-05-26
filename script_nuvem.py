import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

ARQUIVO_ENTRADA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv" 

def gerar_nuvem(texto, nome_arquivo):
    """Gera e guarda a nuvem de palavras num ficheiro PNG."""
    wc = WordCloud(
        width=1080, 
        height=720, 
        background_color="white", 
        colormap="viridis",
        max_words=100, 
        collocations=False
    ).generate(texto)
    
    wc.to_file(nome_arquivo)
    print(f"Nuvem gerada: {nome_arquivo}")

def main():
    caminho = ARQUIVO_ENTRADA
    if not os.path.exists(caminho):
        alternativas = ["DADOS_COM_SENTIMENTO_FINAL.csv", "base_dados_expandida_limpa.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                caminho = alt
                break
        else:
            raise FileNotFoundError("Ficheiro não encontrado para geração de nuvens.")

    print(f"A iniciar geração de Nuvens de Palavras a partir de: {caminho}")
    try:
        df = pd.read_csv(caminho)
    except UnicodeDecodeError:
        df = pd.read_csv(caminho, encoding='latin1')

    if 'txt_nuvem' not in df.columns:
        raise ValueError("Coluna 'txt_nuvem' não encontrada. Execute o pré-processamento.")
        
    df = df.dropna(subset=['txt_nuvem'])

    mapa_fases = {
        "1_Alerta": "1_Crescimento", "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", "4_Vacina": "4_Anomalia"
    }
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)
    
    ordem_fases = ["1_Crescimento", "2_Pico_e_Queda", "3_Baixa", "4_Anomalia"]

    # Nuvem Geral
    texto_geral = " ".join(df['txt_nuvem'].astype(str))
    gerar_nuvem(texto_geral, "nuvem_palavras_geral.png")

    # Nuvens por Fase
    for fase in ordem_fases:
        df_fase = df[df['fase'] == fase]
        if not df_fase.empty:
            texto_fase = " ".join(df_fase['txt_nuvem'].astype(str))
            nome_fase_limpo = fase.split('_')[-1].lower()
            gerar_nuvem(texto_fase, f"nuvem_palavras_{nome_fase_limpo}.png")

    print("Processamento de nuvens concluído com sucesso.")

if __name__ == "__main__":
    main()