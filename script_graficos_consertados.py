import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# Configurações Globais
ARQUIVO_SOCIAL = "DADOS_PRONTOS_ANALISE.csv" 
ARQUIVO_DENGUE = "sinannet_cnv_denguebbr190704187_181_28_134.csv"

CORES_FASES = {
    "1_Crescimento": "#FFD700",
    "2_Pico_e_Queda": "#d62728",
    "3_Baixa": "#2ca02c",
    "4_Anomalia": "#1f77b4"
}

def carregar_dados_governo(arquivo):
    """Extrai e estrutura as semanas epidemiológicas do DATASUS."""
    if not os.path.exists(arquivo):
        raise FileNotFoundError(f"Ficheiro DATASUS não encontrado: {arquivo}")
        
    with open(arquivo, 'r', encoding='latin1') as f:
        linhas = f.readlines()
        
    inicio = next((i for i, l in enumerate(linhas) if "Semana" in l and ";" in l), 3)
    df = pd.read_csv(io.StringIO("".join(linhas[inicio:])), sep=';', encoding='latin1', quotechar='"')
    
    df = df.iloc[:, [0, 1]]
    df.columns = ['Semana_Txt', 'Casos']
    df = df[df['Semana_Txt'].astype(str).str.contains("Semana", na=False)]
    df['semana_epi'] = df['Semana_Txt'].str.extract(r'(\d+)').astype(int)
    
    if df['Casos'].dtype == object:
        df['Casos'] = df['Casos'].astype(str).str.replace('.', '', regex=False)
    df['Casos'] = pd.to_numeric(df['Casos'], errors='coerce').fillna(0)
    
    return df[['semana_epi', 'Casos']]

def carregar_dados_sociais(arquivo):
    """Agrega os dados sociais e processa o mapeamento temporal."""
    if not os.path.exists(arquivo):
        alternativas = ["DADOS_COMPLETOS_PARA_GRAFICOS.csv", "base_dados_expandida_limpa.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                arquivo = alt
                break
        else:
            raise FileNotFoundError("Ficheiro da rede social não encontrado.")
            
    try:
        df = pd.read_csv(arquivo)
    except UnicodeDecodeError:
        df = pd.read_csv(arquivo, encoding='latin1')
        
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], format='mixed', utc=True, errors='coerce')
        df = df.dropna(subset=['data'])
        df['semana_epi'] = df['data'].dt.isocalendar().week.astype(int)
        
    mapa_fases = {
        "1_Alerta": "1_Crescimento", "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", "4_Vacina": "4_Anomalia"
    }
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)
        
    return df.groupby(['semana_epi', 'fase']).size().reset_index(name='Posts_Total')

def main():
    print("A gerar Gráfico de Correlação Epidemiológico com blocos de Fases...")
    df_gov = carregar_dados_governo(ARQUIVO_DENGUE)
    df_soc = carregar_dados_sociais(ARQUIVO_SOCIAL)

    df_final = pd.merge(df_gov, df_soc, on='semana_epi', how='inner').sort_values('semana_epi')

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    sns.set_theme(style="white")

    # Mapeamento de cores baseado nas fases ativas
    cores_barras = [CORES_FASES.get(f, "#B0B0B0") for f in df_final['fase']]
    ax1.bar(df_final['semana_epi'], df_final['Casos'], color=cores_barras, alpha=0.7)
    
    ax1.set_xlabel("Semana Epidemiológica (2025)", fontsize=16, fontweight='bold')
    ax1.set_ylabel("Casos Notificados (DataSUS)", color='#505050', fontsize=16, fontweight='bold')
    ax1.tick_params(axis='both', labelsize=14)
    ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(",", ".")))

    # Segunda Escala (Postagens)
    ax2 = ax1.twinx()
    sns.lineplot(data=df_final, x='semana_epi', y='Posts_Total', ax=ax2, color='black', linewidth=2, marker='o', markersize=5)
    ax2.set_ylabel("Volume de Postagens (BlueSky)", color='black', fontsize=16, fontweight='bold')
    ax2.tick_params(axis='y', labelsize=14)

    # Reestruturação Profissional da Legenda
    handles_fases = [mpatches.Patch(color=color, label=nome.split('_')[-1]) for nome, color in CORES_FASES.items()]
    handle_linha = Line2D([0], [0], color='black', lw=2, marker='o', markersize=5, label="Postagem na Rede")
    
    ax1.legend(handles=handles_fases + [handle_linha], 
               title="Legenda", 
               loc='upper right', 
               fontsize=11, 
               title_fontsize=12, 
               frameon=True, 
               facecolor='white')

    nome_img = "grafico_fases_consertado.png"
    plt.savefig(nome_img, bbox_inches='tight')
    print(f"Artefato visual gerado: {nome_img}")

if __name__ == "__main__":
    main()