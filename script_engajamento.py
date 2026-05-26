import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Configurações Globais
ARQUIVO_ENTRADA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv"
TAMANHO_EIXOS_LABEL = 16
TAMANHO_TICKS = 14
TAMANHO_ANOTACOES = 16

try:
    from leia import SentimentIntensityAnalyzer
except ImportError:
    class SentimentIntensityAnalyzer:
        def polarity_scores(self, text):
            return {'compound': 0}

analyzer = SentimentIntensityAnalyzer()

def classificar_sentimento(compound):
    if compound >= 0.05: return "Positivo"
    if compound <= -0.05: return "Negativo"
    return "Neutro"

def main():
    caminho = ARQUIVO_ENTRADA
    if not os.path.exists(caminho):
        alternativas = ["base_dados_expandida_limpa.csv", "ARQUIVO_SAIDA.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                caminho = alt
                break
        else:
            raise FileNotFoundError("Ficheiro de dados não encontrado.")

    print(f"A carregar dados para análise de engajamento: {caminho}")
    try: 
        df = pd.read_csv(caminho)
    except UnicodeDecodeError: 
        df = pd.read_csv(caminho, encoding='latin1')

    if 'sentimento' not in df.columns:
        print("A calcular sentimentos em tempo de execução...")
        df['sentimento'] = df['txt_sentimento'].apply(
            lambda x: classificar_sentimento(analyzer.polarity_scores(str(x))['compound'])
        )

    colunas_finais = ['like_count', 'reply_count', 'repost_count']
    for col in colunas_finais:
        if col not in df.columns:
            df[col] = 0

    ordem_real = ["Negativo", "Neutro", "Positivo"]
    mapa_fases = {
        "1_Alerta": "1_Crescimento", "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", "4_Vacina": "4_Anomalia"
    }
    
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)

    print("A processar estatísticas globais...")
    tabela_geral = df.groupby('sentimento')[colunas_finais].mean()
    tabela_geral = tabela_geral.reindex(ordem_real)

    cores = ["#cccccc", "#2ca02c", "#d62728"] 
    cmap_personalizado = LinearSegmentedColormap.from_list("custom_green_red", cores, N=256)

    plt.figure(figsize=(10, 6), dpi=300)
    ax = sns.heatmap(
        tabela_geral, 
        annot=True, 
        fmt=".2f", 
        cmap=cmap_personalizado, 
        linewidths=.5,
        annot_kws={"size": TAMANHO_ANOTACOES, "weight": "bold"},
        cbar_kws={'label': 'Média de Engajamento'}
    )

    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=TAMANHO_TICKS)
    cbar.set_label('Média de Engajamento', size=TAMANHO_EIXOS_LABEL)

    plt.title("", fontsize=1)
    plt.xlabel('Métrica de Engajamento', fontsize=TAMANHO_EIXOS_LABEL, fontweight='bold')
    plt.ylabel('Sentimento', fontsize=TAMANHO_EIXOS_LABEL, fontweight='bold')

    ax.set_xticklabels(['Like', 'Reply', 'Repost'], fontsize=TAMANHO_TICKS)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=TAMANHO_TICKS)

    nome_img = "grafico_heatmap_engajamento.png"
    plt.savefig(nome_img, bbox_inches='tight', dpi=300)
    print(f"Heatmap guardado com sucesso: {nome_img}")

    print("\n--- Relatório de Engajamento por Fase Epidemiológica ---")
    ordem_fases = ["1_Crescimento", "2_Pico_e_Queda", "3_Baixa", "4_Anomalia"]
    
    for fase in ordem_fases:
        if 'fase' in df.columns and fase in df['fase'].unique():
            df_fase = df[df['fase'] == fase]
            tabela = df_fase.groupby('sentimento')[colunas_finais].mean()
            tabela = tabela.reindex(ordem_real)
            
            print(f"\nFase: {fase.split('_')[-1].upper()}")
            print("-" * 50)
            print(f"{'Sentimento':<15} | {'Likes':<10} | {'Replies':<10} | {'Reposts':<10}")
            print("-" * 50)
            for sentimento in ordem_real:
                if sentimento in tabela.index:
                    likes = tabela.loc[sentimento, 'like_count']
                    replies = tabela.loc[sentimento, 'reply_count']
                    reposts = tabela.loc[sentimento, 'repost_count']
                    print(f"{sentimento:<15} | {likes:<10.2f} | {replies:<10.2f} | {reposts:<10.2f}")
    print("--------------------------------------------------------\n")

if __name__ == "__main__":
    main()