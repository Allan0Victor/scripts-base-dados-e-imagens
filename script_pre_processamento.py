import os
import re
import spacy
import nltk
import unidecode
import pandas as pd
from nltk.corpus import stopwords

try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")

nltk.download('stopwords', quiet=True)
STOPWORDS_PT = set(stopwords.words('portuguese'))
EXTRAS = {
    "dengue", "aedes", "mosquito", "zika", "chikungunya", "aegypti",
    "pra", "pro", "vc", "pq", "ta", "tá", "ter", "vai", "ser", "tava", "né", "ai",
    "fazer", "gente", "tudo", "coisa", "falar", "ver", "agora", "dia",
    "aqui", "sobre", "então", "tem", "pode", "anos", "ano", "caso",
    "ficar", "estar", "onde", "quando", "user_type", "termo_busca",
    "https", "tco", "k", "kk", "kkk", "rs"
}
STOPWORDS_PT.update(EXTRAS)

def definir_fase(semana):
    if semana <= 9: return "1_Crescimento"
    if 9 < semana <= 20: return "2_Pico_e_Queda"
    if 20 < semana < 48: return "3_Baixa"
    return "4_Anomalia"

# [TRECHO IMUTÁVEL - Figura 6 do TCC]
def limpar_sentimento(texto):
    if not isinstance(texto, str): return ""
    texto = re.sub(r'http\S+', '', texto) 
    texto = re.sub(r'@\S+', '', texto)
    return texto.strip()

# [TRECHO IMUTÁVEL - Figura 7 do TCC]
def limpar_nuvem(texto):
    if not isinstance(texto, str): return ""
    t = re.sub(r'http\S+|@\S+', '', texto)
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\d+', '', t)
    t = unidecode.unidecode(t.lower())
    return " ".join([p for p in t.split() if p not in STOPWORDS_PT and len(p) > 2])

# [TRECHO IMUTÁVEL - Figura 8 (LDA) do TCC]
def limpar_lda(texto):
    if not isinstance(texto, str): return ""
    t = re.sub(r'http\S+|@\S+', '', texto.lower())
    doc = nlp(t)
    tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_space and not token.is_stop]
    tokens = [lemma for lemma in tokens if lemma not in STOPWORDS_PT and len(lemma) > 2]
    return " ".join(tokens)

def main():
    ARQUIVO_ENTRADA = "base_dados_expandida_limpa.csv"
    ARQUIVO_SAIDA = "DADOS_PRONTOS_ANALISE.csv"
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        raise FileNotFoundError(f"Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")

    df = pd.read_csv(ARQUIVO_ENTRADA)
    
    df['data'] = pd.to_datetime(df['data'], format='ISO8601', utc=True)
    df['semana_epi'] = df['data'].dt.isocalendar().week.astype(int)
    df['fase'] = df['semana_epi'].apply(definir_fase)
    
    df['txt_sentimento'] = df['texto'].apply(limpar_sentimento)
    df['txt_nuvem'] = df['texto'].apply(limpar_nuvem)
    df['txt_lda'] = df['texto'].apply(limpar_lda)
    
    df_final = df.dropna(subset=['texto']).copy()
    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding='utf-8')

if __name__ == "__main__":
    main()