import os
import pandas as pd

ARQUIVO_ENTRADA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv"

def investigar_termo_especifico(df, termo="covid"):
    """Filtra publicações que contêm o termo específico e extrai uma amostra."""
    if 'txt_sentimento' not in df.columns:
        return

    mask = df['txt_sentimento'].astype(str).str.contains(termo, case=False, na=False)
    df_alvo = df[mask].copy()

    total_encontrado = len(df_alvo)
    pct = (total_encontrado / len(df)) * 100

    relatorio = [
        f"--- INVESTIGAÇÃO DO TERMO: '{termo.upper()}' ---",
        f"Total de publicações: {total_encontrado} ({pct:.2f}% da base geral)\n"
    ]

    ordem_fases = ["1_Crescimento", "2_Pico_e_Queda", "3_Baixa", "4_Anomalia"]
    for fase in ordem_fases:
        df_fase = df_alvo[df_alvo['fase'] == fase]
        relatorio.append(f"\n>>> FASE: {fase.split('_')[-1].upper()}")
        
        if df_fase.empty:
            relatorio.append("Nenhuma publicação encontrada nesta fase.")
            continue
            
        amostra = df_fase.sample(n=min(5, len(df_fase)), random_state=42)
        for idx, row in amostra.iterrows():
            texto = str(row.get('texto_original', row.get('texto', '')))[:200]
            relatorio.append(f"- {texto}...")
            
    return "\n".join(relatorio)

def investigar_anomalia_engajamento(df):
    """Extrai as publicações de maior engajamento na fase Anomalia."""
    df_anomalia = df[df['fase'] == '4_Anomalia'].copy()
    if df_anomalia.empty:
        return "Nenhum dado encontrado para a Fase 4_Anomalia."

    colunas_possiveis_like = ['like_count', 'likes', 'curtidas']
    colunas_possiveis_repost = ['repost_count', 'reposts', 'compartilhamentos']
    
    col_like = next((c for c in colunas_possiveis_like if c in df.columns), None)
    col_repost = next((c for c in colunas_possiveis_repost if c in df.columns), None)

    if not col_like or not col_repost:
        return "Colunas de engajamento não encontradas para calcular a anomalia."

    df_anomalia['engajamento_total'] = df_anomalia[col_like].fillna(0) + df_anomalia[col_repost].fillna(0)
    df_top = df_anomalia.sort_values('engajamento_total', ascending=False)

    relatorio = [
        "\n--- INVESTIGAÇÃO DE ANOMALIA (MAIOR ENGAJAMENTO FASE 4) ---",
        f"Total de publicações analisadas na fase: {len(df_anomalia)}\n"
    ]

    for i in range(min(5, len(df_top))):
        post = df_top.iloc[i]
        relatorio.append(f"POSIÇÃO #{i+1} | Engajamento Total: {post['engajamento_total']}")
        relatorio.append(f"Autor: {post.get('autor', 'Desconhecido')}")
        relatorio.append(f"Texto: {str(post.get('texto_original', post.get('texto', '')))[:250]}...\n")

    return "\n".join(relatorio)

def main():
    caminho = ARQUIVO_ENTRADA
    if not os.path.exists(caminho):
        alternativas = ["DADOS_COM_SENTIMENTO_FINAL.csv", "base_dados_expandida_limpa.csv"]
        for alt in alternativas:
            if os.path.exists(alt):
                caminho = alt
                break
        else:
            raise FileNotFoundError("Ficheiro de dados não encontrado.")

    print(f"A executar extração qualitativa a partir de: {caminho}")
    try: 
        df = pd.read_csv(caminho)
    except UnicodeDecodeError: 
        df = pd.read_csv(caminho, encoding='latin1')

    mapa_fases = {
        "1_Alerta": "1_Crescimento", "2_Crise": "2_Pico_e_Queda",
        "3_Baixa": "3_Baixa", "4_Vacina": "4_Anomalia"
    }
    if 'fase' in df.columns:
        df['fase'] = df['fase'].replace(mapa_fases)

    relatorio_covid = investigar_termo_especifico(df, "covid")
    relatorio_anomalia = investigar_anomalia_engajamento(df)

    # Guarda os resultados num ficheiro de texto
    with open("relatorio_amostras_qualitativas.txt", "w", encoding="utf-8") as f:
        f.write(relatorio_covid + "\n" + relatorio_anomalia)
        
    print("Extração concluída. Relatório guardado em: relatorio_amostras_qualitativas.txt")

if __name__ == "__main__":
    main()