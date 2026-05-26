import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from gensim import corpora
from gensim.models import CoherenceModel, LdaMulticore

# Configurações de Arquivo
ARQUIVO_ENTRADA = "DADOS_PRONTOS_ANALISE.csv"

# Configurações Visuais
TAMANHO_TITULOS = 18
TAMANHO_EIXOS_LABEL = 16
TAMANHO_TICKS = 14
TAMANHO_LEGENDA = 12

# Parâmetros LDA
START = 2
LIMIT = 13 
STEP = 1

def preparar_corpus(df_alvo):
    docs = df_alvo['txt_lda'].astype(str).apply(lambda x: x.split())
    dictionary = corpora.Dictionary(docs)
    dictionary.filter_extremes(no_below=3, no_above=0.5)
    corpus = [dictionary.doc2bow(text) for text in docs]
    return dictionary, corpus, docs

def calcular_coerencia_range(dictionary, corpus, texts, start, limit, step, nome_fase):
    coherence_values = []
    print(f"Processando coerência para: {nome_fase}")
    
    for num_topics in range(start, limit, step):
        model = LdaMulticore(
            corpus=corpus, 
            id2word=dictionary, 
            num_topics=num_topics, 
            random_state=42, 
            passes=10
        )          
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        score = coherencemodel.get_coherence()
        coherence_values.append(score)
        print(f"  [{nome_fase}] {num_topics} tópicos: Score = {score:.4f}")
        
    return coherence_values

def main():
    caminho = ARQUIVO_ENTRADA
    if not os.path.exists(caminho):
        alternativas = ["DADOS_COMPLETOS_PARA_GRAFICOS.csv", "ARQUIVO_SAIDA.csv", "base_dados_expandida_limpa.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                caminho = alt
                break
        else:
            raise FileNotFoundError("Arquivo não encontrado para análise LDA.")

    try: 
        df = pd.read_csv(caminho)
    except UnicodeDecodeError: 
        df = pd.read_csv(caminho, encoding='latin1')

    coluna_texto = 'txt_lda'
    df = df.dropna(subset=[coluna_texto])
    df = df[df[coluna_texto].str.strip().astype(bool)] 

    mapa_fases = {
        "1_Alerta": "1_Crescimento", "1_Crescimento": "1_Crescimento",
        "2_Crise": "2_Pico_e_Queda", "2_Pico_e_Queda": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa",
        "4_Vacina": "4_Anomalia", "4_Anomalia": "4_Anomalia"
    }
    if 'fase' in df.columns: 
        df['fase'] = df['fase'].replace(mapa_fases)

    datasets = {"Geral": df}
    ordem_fases = ["1_Crescimento", "2_Pico_e_Queda", "3_Baixa", "4_Anomalia"]
    
    if 'fase' in df.columns:
        for fase in ordem_fases:
            df_temp = df[df['fase'] == fase]
            if len(df_temp) > 10: 
                datasets[fase] = df_temp
            else: 
                print(f"Aviso: Fase '{fase}' ignorada (poucos dados para LDA).")

    resultados = {}
    x_axis = range(START, LIMIT, STEP)

    for nome, dataset in datasets.items():
        dictionary, corpus, texts = preparar_corpus(dataset)
        scores = calcular_coerencia_range(dictionary, corpus, texts, START, LIMIT, STEP, nome)
        resultados[nome] = scores

    print("Gerando gráfico comparativo de coerência...")
    plt.figure(figsize=(10, 6), dpi=300)
    sns.set_theme(style="whitegrid")

    palette = sns.color_palette("tab10", len(resultados))
    markers = ['o', 's', '^', 'v', 'D']

    for i, (nome, scores) in enumerate(resultados.items()):
        label_limpo = nome.split('_')[-1] if '_' in nome else nome
        plt.plot(x_axis, scores, 
                 marker=markers[i % len(markers)], 
                 linewidth=2, 
                 label=label_limpo,
                 color=palette[i])

    plt.title("", fontsize=TAMANHO_TITULOS)
    plt.xlabel("Número de Tópicos ($K$)", fontsize=TAMANHO_EIXOS_LABEL, fontweight='bold')
    plt.ylabel("Coerência ($C_v$)", fontsize=TAMANHO_EIXOS_LABEL, fontweight='bold')
    
    plt.xticks(x_axis, fontsize=TAMANHO_TICKS)
    plt.yticks(fontsize=TAMANHO_TICKS)
    
    plt.legend(title="Dataset", 
               title_fontsize=TAMANHO_LEGENDA,
               fontsize=TAMANHO_LEGENDA,
               loc='upper left', 
               bbox_to_anchor=(1.02, 1), 
               borderaxespad=0.,
               frameon=True,
               framealpha=1)
    
    nome_img = "grafico_coerencia_lda_formatado.png"
    plt.savefig(nome_img, bbox_inches='tight', dpi=300)
    
    print("Conclusão (Melhor K Matemático por Fase):")
    for nome, scores in resultados.items():
        melhor_k = x_axis[scores.index(max(scores))]
        print(f"  - {nome:<15}: {melhor_k} tópicos (Score: {max(scores):.4f})")

if __name__ == "__main__":
    main()