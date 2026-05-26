import pandas as pd
import gensim
from gensim import corpora
from gensim.models import LdaMulticore
import os

# --- CONFIGURAÇÃO ---
ARQUIVO_ENTRADA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv"
if not os.path.exists(ARQUIVO_ENTRADA):
    ARQUIVO_ENTRADA = "DADOS_COM_SENTIMENTO_FINAL.csv"

# SEUS VALORES DEFINIDOS (K)
CONFIG_K = {
    "Geral": 5,
    "1_Crescimento": 3,
    "2_Pico_e_Queda": 4,
    "3_Baixa": 4,
    "4_Anomalia": 4
}

NUM_PALAVRAS = 15 # Vamos pegar 15 palavras para ter contexto suficiente

def treinar_e_listar(df_alvo, titulo, num_topics):
    print(f"\n>>> PROCESSANDO: {titulo.upper()} (K={num_topics})")
    
    # Prepara o texto
    docs = df_alvo['txt_lda'].astype(str).apply(lambda x: x.split())
    dictionary = corpora.Dictionary(docs)
    dictionary.filter_extremes(no_below=3, no_above=0.6)
    corpus = [dictionary.doc2bow(text) for text in docs]
    
    if len(corpus) == 0:
        return []

    # Treina o modelo
    lda = LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=num_topics, 
                       random_state=42, passes=20, workers=3)
    
    # Extrai palavras
    resultados = []
    topics = lda.show_topics(num_topics=num_topics, num_words=NUM_PALAVRAS, formatted=False)
    
    for topic_id, words in topics:
        # Pega apenas as palavras (sem os pesos numéricos)
        lista_palavras = [w[0] for w in words]
        texto_limpo = ", ".join(lista_palavras)
        
        # Guarda para o CSV
        resultados.append({
            "Dataset": titulo,
            "Tópico": topic_id + 1,
            "Palavras": texto_limpo
        })
        
        # Printa formatado para copiar pro Chat
        print(f"[{titulo}] Tópico {topic_id + 1}: {texto_limpo}")
        
    return resultados

def main():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print("❌ Arquivo não encontrado.")
        return

    print("📂 Lendo dados...")
    try: df = pd.read_csv(ARQUIVO_ENTRADA)
    except: df = pd.read_csv(ARQUIVO_ENTRADA, encoding='latin1')

    # Limpeza básica
    df = df.dropna(subset=['txt_lda'])
    df = df[df['txt_lda'].str.strip().astype(bool)]
    
    # Mapa de fases
    mapa = {
        "1_Alerta": "1_Crescimento", "1_Crescimento": "1_Crescimento",
        "2_Crise": "2_Pico_e_Queda", "2_Pico_e_Queda": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa",
        "4_Vacina": "4_Anomalia", "4_Anomalia": "4_Anomalia"
    }
    if 'fase' in df.columns: df['fase'] = df['fase'].replace(mapa)

    todos_resultados = []

    # Loop principal
    for chave, k in CONFIG_K.items():
        if chave == "Geral":
            res = treinar_e_listar(df, "Geral", k)
            todos_resultados.extend(res)
        else:
            df_fase = df[df['fase'] == chave]
            if len(df_fase) > 10:
                res = treinar_e_listar(df_fase, chave, k)
                todos_resultados.extend(res)

    # Salva CSV
    pd.DataFrame(todos_resultados).to_csv("TABELA_TOPICOS_FINAL.csv", index=False, encoding='utf-8-sig')
    print("\n✅ Tabela salva em 'TABELA_TOPICOS_FINAL.csv'.")
    print("👉 COPIE AS LINHAS ACIMA E COLE NO CHAT PARA EU DAR OS NOMES!")

if __name__ == "__main__":
    main()