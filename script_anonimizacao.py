import os
import pandas as pd

ARQUIVO_ENTRADA = "ARQUIVO_SAIDA.csv"
ARQUIVO_SAIDA_FINAL = "base_dados_expandida_limpa.csv"

def processar_anonimizacao(df):
    """
    Substitui identificadores comuns (*.bsky.social) por IDs anónimos,
    mantém domínios oficiais, cria a categoria e padroniza as colunas.
    """
    # 1. Anonimização
    mascara_comum = df['autor'].str.endswith('.bsky.social', na=False)
    autores_comuns = df.loc[mascara_comum, 'autor'].unique()
    
    mapa_anonimo = {autor: f"usuario_anonimo_{i+1}" for i, autor in enumerate(autores_comuns)}
    df['autor'] = df['autor'].apply(lambda x: mapa_anonimo.get(x, x))
    
    # 2. Criação da Categoria de Autor
    df['categoria_autor'] = df['autor'].apply(
        lambda x: "Comum" if str(x).startswith("usuario_anonimo_") else "Oficial/Verificado"
    )
    
    # 3. Adaptação para o Script de Pré-processamento (TCC)
    if 'texto_original' in df.columns:
        df.rename(columns={'texto_original': 'texto'}, inplace=True)
        
    return df

def main():
    print(f"A iniciar a Preparação e Anonimização da Base de Dados...")
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        raise FileNotFoundError(f"Ficheiro bruto não encontrado: {ARQUIVO_ENTRADA}")
        
    df = pd.read_csv(ARQUIVO_ENTRADA)
    
    if 'autor' not in df.columns:
        raise ValueError("A coluna 'autor' não existe no ficheiro de entrada.")
        
    df_anonimizado = processar_anonimizacao(df)
    
    # Guarda o ficheiro pronto para ser consumido pelo pré-processamento
    df_anonimizado.to_csv(ARQUIVO_SAIDA_FINAL, index=False, encoding='utf-8')
    
    total_comuns = (df_anonimizado['categoria_autor'] == 'Comum').sum()
    total_oficiais = (df_anonimizado['categoria_autor'] == 'Oficial/Verificado').sum()
    
    print(f"✅ Sucesso! Base de dados limpa gerada: {ARQUIVO_SAIDA_FINAL}")
    print(f"   - Utilizadores Comuns (Anonimizados): {total_comuns}")
    print(f"   - Domínios Oficiais/Verificados: {total_oficiais}\n")

if __name__ == "__main__":
    main()