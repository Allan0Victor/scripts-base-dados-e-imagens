import os
import pandas as pd

# Configurações Globais
ARQUIVO_BRUTO = "ARQUIVO_SAIDA.csv" 
ARQUIVO_SENTIMENTOS = "DADOS_COM_SENTIMENTO_FINAL.csv"
ARQUIVO_SAIDA = "DADOS_COMPLETOS_PARA_GRAFICOS.csv"

def contar_respostas(texto):
    """Conta respostas baseando-se no separador ' | ' extraído pela API."""
    if pd.isna(texto) or str(texto).strip() == "":
        return 0
    
    texto_str = str(texto)
    if " | " not in texto_str:
        return 1
        
    return len(texto_str.split(" | "))

def main():
    if not os.path.exists(ARQUIVO_BRUTO) or not os.path.exists(ARQUIVO_SENTIMENTOS):
        raise FileNotFoundError("Ficheiros de entrada não encontrados para a mesclagem.")
        
    print("A iniciar o processo de recuperação de métricas de engajamento...")
    
    df_sentimento = pd.read_csv(ARQUIVO_SENTIMENTOS)
    df_recuperar = pd.read_csv(ARQUIVO_BRUTO)
    
    df_recuperar = df_recuperar.drop_duplicates(subset=['uri']).copy()

    # Processamento de Respostas
    if 'respostas_coletadas' in df_recuperar.columns:
        df_recuperar['reply_count'] = df_recuperar['respostas_coletadas'].apply(contar_respostas)
    else:
        df_recuperar['reply_count'] = 0

    # Normalização de Nomenclaturas
    col_reposts = next((col for col in ['reposts', 'repost_count'] if col in df_recuperar.columns), None)
    if col_reposts and col_reposts != 'repost_count':
        df_recuperar.rename(columns={col_reposts: 'repost_count'}, inplace=True)

    col_likes = next((col for col in ['likes', 'like_count'] if col in df_recuperar.columns), None)
    if col_likes and col_likes != 'like_count':
        df_recuperar.rename(columns={col_likes: 'like_count'}, inplace=True)

    # Filtragem e Junção (Merge)
    colunas_interesse = ['uri', 'reply_count', 'repost_count', 'like_count']
    colunas_presentes = [c for c in colunas_interesse if c in df_recuperar.columns]
    
    df_final = pd.merge(df_sentimento, df_recuperar[colunas_presentes], on='uri', how='left')

    # Tratamento de Nulos
    for col in ['repost_count', 'reply_count', 'like_count']:
        if col in df_final.columns:
            df_final[col] = df_final[col].fillna(0).astype(int)

    df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding='utf-8')
    print(f"Mesclagem concluída. Ficheiro gerado: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()