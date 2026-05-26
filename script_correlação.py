import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# Ficheiros de Entrada
ARQ_GOVERNO = "sinannet_cnv_denguebbr190704187_181_28_134.csv"
ARQ_SOCIAL = "ARQUIVO_SAIDA.csv" 

# Configurações Visuais
TAMANHO_TITULOS = 18
TAMANHO_TICKS = 14
TAMANHO_LEGENDA = 12

def carregar_governo(arquivo):
    """Extrai e formata os dados governamentais."""
    if not os.path.exists(arquivo):
        raise FileNotFoundError(f"Ficheiro Governamental não encontrado: {arquivo}")
        
    with open(arquivo, 'r', encoding='latin1') as f:
        linhas = f.readlines()
        
    inicio = next((i for i, linha in enumerate(linhas) if "Semana" in linha and ";" in linha), 3)
    conteudo = "".join(linhas[inicio:])
    
    df = pd.read_csv(io.StringIO(conteudo), sep=';', encoding='latin1', quotechar='"')
    df = df.iloc[:, [0, 1]]
    df.columns = ['Semana_Txt', 'Casos']
    df = df[df['Semana_Txt'].astype(str).str.contains("Semana", na=False)]
    df['semana_epi'] = df['Semana_Txt'].str.extract(r'(\d+)').astype(int)
    
    if df['Casos'].dtype == object:
        df['Casos'] = df['Casos'].astype(str).str.replace('.', '', regex=False)
        
    df['Casos'] = pd.to_numeric(df['Casos'], errors='coerce').fillna(0)
    return df[['semana_epi', 'Casos']]

def carregar_social(arquivo):
    """Carrega os dados da rede social, gerindo fallbacks para nomes de ficheiros."""
    if not os.path.exists(arquivo):
        alternativas = ["DADOS_PRONTOS_ANALISE.csv", "dataset_tcc_dengue_pt_2025_final.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                arquivo = alt
                break
        else:
            raise FileNotFoundError("Ficheiro social não encontrado.")

    try: 
        df = pd.read_csv(arquivo)
    except UnicodeDecodeError: 
        df = pd.read_csv(arquivo, encoding='latin1')

    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], format='mixed', utc=True, errors='coerce')
        df = df.dropna(subset=['data'])
        df['semana_epi'] = df['data'].dt.isocalendar().week.astype(int)
        
    df_agg = df.groupby('semana_epi').size().reset_index(name='Posts_Total')
    return df_agg

def plotar_correlacao_eixos(df_final):
    """Plota o gráfico de correlação com eixo duplo (barras e linha)."""
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    sns.set_theme(style="white")

    color_gov = '#B0B0B0' 
    ax1.bar(df_final['semana_epi'], df_final['Casos'], color=color_gov, alpha=0.6, label='Casos Oficiais')
    
    ax1.set_xlabel('Semana Epidemiológica (2025)', fontsize=TAMANHO_TITULOS, fontweight='bold')
    ax1.set_ylabel('Casos Notificados (DataSus)', color='#505050', fontsize=TAMANHO_TITULOS, fontweight='bold')
    ax1.tick_params(axis='both', labelsize=TAMANHO_TICKS, labelcolor='#505050')
    ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(",", ".")))

    ax2 = ax1.twinx() 
    color_social = '#D62728' 
    sns.lineplot(data=df_final, x='semana_epi', y='Posts_Total', ax=ax2, 
                 color=color_social, linewidth=3, marker='o', markersize=8)
    
    ax2.set_ylabel('Volume de Postagens', color=color_social, fontsize=TAMANHO_TITULOS, fontweight='bold')
    ax2.tick_params(axis='y', labelsize=TAMANHO_TICKS, labelcolor=color_social)
    
    if len(df_final) > 20:
        for i, label in enumerate(ax1.xaxis.get_ticklabels()):
            if i % 2 != 0: 
                label.set_visible(False)

    handle_barras = mpatches.Patch(color=color_gov, alpha=0.6, label='Casos Oficiais (DataSus)')
    handle_linha = Line2D([0], [0], color=color_social, lw=3, marker='o', label='Volume de Postagens')
    
    ax1.legend(handles=[handle_barras, handle_linha], 
               title="Legenda",
               loc='upper right', 
               fontsize=TAMANHO_LEGENDA,
               title_fontsize=TAMANHO_LEGENDA + 1,
               frameon=True, 
               facecolor='white', 
               framealpha=1)

    plt.title("")
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    nome_img = "grafico_correlacao_formatado.png"
    plt.savefig(nome_img, bbox_inches='tight')
    print(f"Gráfico de correlação guardado: {nome_img}")

def main():
    df_gov = carregar_governo(ARQ_GOVERNO)
    df_social = carregar_social(ARQ_SOCIAL)
    
    if df_gov.empty or df_social.empty: 
        return

    df_final = pd.merge(df_gov, df_social, on='semana_epi', how='inner')
    df_final = df_final.sort_values('semana_epi')
    
    if df_final.empty:
        raise ValueError("Cruzamento vazio. Verifique a convergência das semanas epidemiológicas.")
    
    correlacao = df_final['Casos'].corr(df_final['Posts_Total'])
    
    print("\n--- Estatísticas de Correlação ---")
    print(f"Correlação de Pearson (r): {correlacao:.4f}")
    
    interpretacao = "Desprezível"
    if abs(correlacao) > 0.9: interpretacao = "Muito Forte"
    elif abs(correlacao) > 0.7: interpretacao = "Forte"
    elif abs(correlacao) > 0.5: interpretacao = "Moderada"
    elif abs(correlacao) > 0.3: interpretacao = "Fraca"
    
    print(f"Interpretação: {interpretacao}")
    print("----------------------------------\n")

    plotar_correlacao_eixos(df_final)

if __name__ == "__main__":
    main()