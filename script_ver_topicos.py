import os
import pandas as pd
from gensim import corpora
from gensim.models import LdaMulticore
import pyLDAvis
import pyLDAvis.gensim_models

# Configurações Globais
ARQUIVO_ENTRADA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv"

# Matriz de Tópicos Ótimos (K) obtidos na análise
CONFIG_K = {
    "Geral": 5,
    "1_Crescimento": 3,
    "2_Pico_e_Queda": 4,
    "3_Baixa": 4,
    "4_Anomalia": 4
}

def processar_e_gerar_html(df_alvo, titulo, num_topics):
    """Treina o modelo LDA e gera a visualização interativa em HTML."""
    print(f"A gerar modelo interativo para: {titulo} (K={num_topics})")
    
    docs = df_alvo['txt_lda'].astype(str).apply(lambda x: x.split())
    dictionary = corpora.Dictionary(docs)
    dictionary.filter_extremes(no_below=3, no_above=0.6)
    corpus = [dictionary.doc2bow(text) for text in docs]
    
    if not corpus:
        print(f"Aviso: Corpus vazio para {titulo}. Geração ignorada.")
        return

    model = LdaMulticore(
        corpus=corpus, 
        id2word=dictionary, 
        num_topics=num_topics, 
        random_state=42, 
        passes=10
    )
    
    vis = pyLDAvis.gensim_models.prepare(model, corpus, dictionary, sort_topics=False)
    nome_html = f"lda_interativo_{titulo.lower()}.html"
    pyLDAvis.save_html(vis, nome_html)
    print(f"Artefato visual guardado: {nome_html}")

def main():
    caminho = ARQUIVO_ENTRADA
    if not os.path.exists(caminho):
        caminho = "DADOS_COM_SENTIMENTO_FINAL.csv"

    if not os.path.exists(caminho):
        raise FileNotFoundError("Ficheiro de dados não encontrado para processamento LDA.")

    try: 
        df = pd.read_csv(caminho)
    except UnicodeDecodeError: 
        df = pd.read_csv(caminho, encoding='latin1')

    if 'txt_lda' not in df.columns:
        raise ValueError("Coluna 'txt_lda' ausente. Execute o pré-processamento primeiro.")

    df = df.dropna(subset=['txt_lda'])
    df = df[df['txt_lda'].str.strip().astype(bool)]

    mapa_fases = {
        "1_Alerta": "1_Crescimento", "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", "4_Vacina": "4_Anomalia"
    }
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)

    for chave, k_escolhido in CONFIG_K.items():
        if chave == "Geral":
            processar_e_gerar_html(df, "Geral", k_escolhido)
        else:
            df_fase = df[df['fase'] == chave]
            if len(df_fase) > 10:
                processar_e_gerar_html(df_fase, chave, k_escolhido)
            else:
                print(f"Dados insuficientes para gerar a visualização da fase {chave}.")

if __name__ == "__main__":
    main()