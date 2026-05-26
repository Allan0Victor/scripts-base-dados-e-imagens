import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de Arquivo
ARQUIVO_ENTRADA = "DADOS_PRONTOS_ANALISE.csv"
NOME_ARQUIVO_SAIDA = "DADOS_COM_SENTIMENTO_FINAL.csv"

# Configurações Visuais
TAMANHO_TITULOS = 18
TAMANHO_EIXOS_LABEL = 16
TAMANHO_TICKS = 14
TAMANHO_LEGENDA = 12
TAMANHO_ROTULO_BARRA = 12

try:
    from leia import SentimentIntensityAnalyzer
except ImportError:
    class SentimentIntensityAnalyzer:
        def polarity_scores(self, text):
            return {'compound': 0}

def classificar_sentimento(compound):
    if compound >= 0.05:
        return "Positivo"
    if compound <= -0.05:
        return "Negativo"
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
            raise FileNotFoundError("Arquivo de dados não encontrado.")

    print(f"Lendo dados: {caminho}")
    try: 
        df = pd.read_csv(caminho, encoding='utf-8')
    except UnicodeDecodeError: 
        df = pd.read_csv(caminho, encoding='latin-1')
    
    mapa_fases = {
        "1_Alerta": "1_Crescimento", 
        "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", 
        "4_Vacina": "4_Anomalia"
    }
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)
    
    ordem_fases = ["1_Crescimento", "2_Pico_e_Queda", "3_Baixa", "4_Anomalia"]

    print("Calculando sentimentos...")
    coluna_alvo = 'txt_sentimento' if 'txt_sentimento' in df.columns else 'texto'
    df = df.dropna(subset=[coluna_alvo])
    
    analyzer = SentimentIntensityAnalyzer()
    resultados_polaridade = []
    resultados_intensidade = []

    for texto in df[coluna_alvo]:
        s = analyzer.polarity_scores(str(texto))
        compound = s['compound']
        resultados_polaridade.append(classificar_sentimento(compound))
        resultados_intensidade.append(abs(compound))
        
    df['sentimento'] = resultados_polaridade
    df['intensidade'] = resultados_intensidade
    
    df.to_csv(NOME_ARQUIVO_SAIDA, index=False, encoding='utf-8')

    # Configuração de Cores
    ordem_geral = ["Negativo", "Neutro", "Positivo"]
    cores_geral = {"Negativo": "#d62728", "Neutro": "#bfbfbf", "Positivo": "#2ca02c"}

    # Gráfico 1: Geral
    plt.figure(figsize=(8, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    ax = sns.countplot(x='sentimento', data=df, order=ordem_geral, palette=cores_geral)
    
    plt.title('')
    plt.xlabel('Sentimento Predominante', fontsize=TAMANHO_EIXOS_LABEL)
    plt.ylabel('Quantidade de Postagens', fontsize=TAMANHO_EIXOS_LABEL)
    ax.tick_params(axis='both', labelsize=TAMANHO_TICKS)

    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}', 
                        (p.get_x() + p.get_width()/2, height), 
                        ha='center', va='bottom', 
                        fontsize=TAMANHO_TICKS, color='black')

    plt.tight_layout()
    plt.savefig("grafico_1_sentimento_geral_qtd.png")

    # Gráfico 2: Intensidade Média
    df_polarizado = df[df['sentimento'] != 'Neutro']
    ordem_pol = ["Negativo", "Positivo"]
    cores_pol = {"Negativo": "#d62728", "Positivo": "#2ca02c"}

    plt.figure(figsize=(8, 6), dpi=300)
    if not df_polarizado.empty:
        media_int = df_polarizado.groupby('sentimento')['intensidade'].mean().reset_index()
        ax2 = sns.barplot(x='sentimento', y='intensidade', data=media_int, order=ordem_pol, palette=cores_pol)
        
        plt.title('')
        plt.ylabel('Intensidade Média (0 a 1)', fontsize=TAMANHO_EIXOS_LABEL)
        plt.xlabel('Polaridade', fontsize=TAMANHO_EIXOS_LABEL)
        plt.ylim(0, 1)
        ax2.tick_params(axis='both', labelsize=TAMANHO_TICKS)

        for p in ax2.patches:
            height = p.get_height()
            ax2.annotate(f'{height:.3f}', 
                        (p.get_x() + p.get_width()/2, height), 
                        ha='center', va='bottom', 
                        fontsize=TAMANHO_TICKS, color='black')

        plt.tight_layout()
        plt.savefig("grafico_2_intensidade_media.png")

    # Gráfico 3: Fases (Stacked)
    fases_presentes = [f for f in ordem_fases if f in df['fase'].unique()]
    if fases_presentes:
        ct_counts = pd.crosstab(df['fase'], df['sentimento'])
        ct_counts = ct_counts.reindex(index=fases_presentes, columns=ordem_geral).fillna(0)
        ct_pct = ct_counts.div(ct_counts.sum(1), axis=0) * 100
        
        lista_cores = [cores_geral[s] for s in ordem_geral]
        ax3 = ct_pct.plot(kind='bar', stacked=True, color=lista_cores, figsize=(11, 7), width=0.8)
        
        plt.title('')
        plt.ylabel('Distribuição de Sentimentos (%)', fontsize=TAMANHO_EIXOS_LABEL)
        plt.xlabel('Fase Epidemiológica', fontsize=TAMANHO_EIXOS_LABEL)
        plt.ylim(0, 100)
        
        labels_fases = [f.split('_')[-1] for f in ct_pct.index]
        plt.xticks(range(len(labels_fases)), labels_fases, rotation=0, fontsize=TAMANHO_TICKS)
        plt.yticks(fontsize=TAMANHO_TICKS)
        
        for c_idx, container in enumerate(ax3.containers):
            sentimento_atual = ordem_geral[c_idx]
            for i, bar in enumerate(container):
                fase_atual = ct_pct.index[i]
                pct_val = bar.get_height()
                n_val = ct_counts.loc[fase_atual, sentimento_atual]
                
                if pct_val > 5: 
                    label_text = f"{int(n_val)}\n({pct_val:.1f}%)"
                    ax3.text(
                        bar.get_x() + bar.get_width() / 2, 
                        bar.get_y() + bar.get_height() / 2, 
                        label_text, 
                        ha='center', va='center', 
                        color='black',
                        fontsize=TAMANHO_ROTULO_BARRA
                    )

        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', title="Sentimento", 
                   fontsize=TAMANHO_LEGENDA, title_fontsize=TAMANHO_LEGENDA)
        
        plt.tight_layout()
        plt.savefig("grafico_3_fases_com_neutros.png", dpi=300)

    print("Processamento de sentimentos e gráficos concluído.")

if __name__ == "__main__":
    main()