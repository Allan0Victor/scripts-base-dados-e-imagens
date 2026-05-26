import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações de Ficheiros e Variáveis
ARQUIVO_SINAN = "sinannet_cnv_denguebbr190704187_181_28_134.csv"
SEMANA_CORTE_SEMESTRE = 26

# Configurações Visuais
TAMANHO_TITULOS = 18
TAMANHO_TICKS = 14

def ler_arquivo_sinan(caminho_arquivo):
    """Lê e estrutura os dados brutos do DATASUS (SINAN)."""
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo do DATASUS não encontrado: {caminho_arquivo}")
    
    with open(caminho_arquivo, 'r', encoding='latin1') as f:
        linhas = f.readlines()

    # Identifica o início dos dados para contornar o cabeçalho sujo do Tabnet
    inicio_dados = next((i for i, linha in enumerate(linhas) if "Semana" in linha and ";" in linha), 3)
    conteudo_limpo = "".join(linhas[inicio_dados:])
    
    df = pd.read_csv(io.StringIO(conteudo_limpo), sep=';', encoding='latin1', quotechar='"')
    df = df.iloc[:, [0, 1]]
    df.columns = ['Semana_Texto', 'Casos']
    df = df[df['Semana_Texto'].astype(str).str.contains("Semana", na=False)]

    df['semana_epi'] = df['Semana_Texto'].str.extract(r'(\d+)').astype(int)
    
    if df['Casos'].dtype == object:
        df['Casos'] = df['Casos'].astype(str).str.replace('.', '', regex=False)
    
    df['Casos'] = pd.to_numeric(df['Casos'], errors='coerce').fillna(0)
    
    return df

def calcular_estatisticas_semestre(df):
    """Calcula a representatividade dos casos por semestre epidemiológico."""
    total_casos = df['Casos'].sum()
    mask_primeiro_semestre = df['semana_epi'] <= SEMANA_CORTE_SEMESTRE
    casos_primeiro_semestre = df.loc[mask_primeiro_semestre, 'Casos'].sum()
    
    pct_primeiro = (casos_primeiro_semestre / total_casos) * 100
    pct_segundo = 100 - pct_primeiro
    
    print("\n--- Relatório Epidemiológico (2025) ---")
    print(f"Total Geral de Casos: {int(total_casos):,}".replace(",", "."))
    print(f"1º Semestre (SE 01-{SEMANA_CORTE_SEMESTRE}): {int(casos_primeiro_semestre):,} casos ({pct_primeiro:.2f}%)")
    print(f"2º Semestre (SE {SEMANA_CORTE_SEMESTRE+1}+): {int(total_casos - casos_primeiro_semestre):,} casos ({pct_segundo:.2f}%)")
    print("---------------------------------------\n")

def plotar_grafico_casos(df):
    """Gera e guarda o gráfico de barras dos casos oficiais (Referência: TCC)."""
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(data=df, x='semana_epi', y='Casos', color='#595959', alpha=0.9)

    plt.xlabel('Semana Epidemiológica (SE)', fontsize=TAMANHO_TITULOS, fontweight='bold')
    plt.ylabel('Casos Prováveis Notificados (DataSus)', fontsize=TAMANHO_TITULOS, fontweight='bold')
    
    ax.tick_params(axis='both', labelsize=TAMANHO_TICKS)
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)).replace(",", ".")))

    ticks = ax.get_xticks()
    labels = ax.get_xticklabels()
    if len(ticks) > 20:
        for i, label in enumerate(labels):
            if i % 2 != 0: 
                label.set_visible(False)

    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    nome_img = "grafico_casos_oficiais_sinan.png"
    plt.savefig(nome_img, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado como: {nome_img}")

def main():
    df = ler_arquivo_sinan(ARQUIVO_SINAN)
    if not df.empty:
        calcular_estatisticas_semestre(df)
        plotar_grafico_casos(df)

if __name__ == "__main__":
    main()