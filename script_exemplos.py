import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Texto Exato Utilizado na Metodologia do TCC
TEXTO_EXEMPLO = """
Gente, a situação da dengue tá muito complicada aqui no bairro! Sério, não aguento mais ver tanto mosquito da dengue voando por aí. É mosquito picando de dia, mosquito picando de noite, um inferno! Já passei repelente umas mil vezes hoje, o cheiro de repelente tá impregnado, mas o mosquito não desiste. Meu vizinho pegou dengue, minha prima tá com dengue, tá todo mundo com aquela febre alta e muita dor no corpo. Dizem que essa dor da dengue é horrível, quebra a pessoa inteira. E a febre? A febre não baixa nunca! Pelo amor de Deus, vamos vigiar a água parada, pessoal. Água nos vasos de planta, água nos pneus velhos, água na calha... tudo isso vira casa pro mosquito da dengue. Não deixem água acumular de jeito nenhum! Tem que usar repelente, tem que cuidar do quintal. O mosquito tá solto e a dengue mata, viu? Vamos acabar com os focos de água e mandar esse mosquito embora. Xô dengue! Sai pra lá mosquito chato! É muita dor e febre pra uma doença só. Cuidem-se e usem muito repelente!
"""

# Lista Customizada do Autor
STOPWORDS_PT = [
    'a', 'o', 'e', 'de', 'da', 'do', 'em', 'que', 'tá', 'no', 'na', 'um', 'uma', 'com', 'não', 'os', 'as', 
    'pra', 'se', 'por', 'isso', 'tem', 'mas', 'foi', 'muito', 'muita', 'mais', 'meu', 'minha', 'nos', 'nas', 
    'pelo', 'pela', 'só', 'para', 'ja', 'já', 'está'
]

def main():
    print("A gerar a Figura 1 (Nuvem de Exemplo Metodológico)...")
    
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white', 
        stopwords=STOPWORDS_PT,
        colormap='viridis',
        max_words=100,
        collocations=False
    ).generate(TEXTO_EXEMPLO)

    plt.figure(figsize=(10, 5), dpi=300)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    nome_img = "exemplo_nuvem_figura_1.png"
    plt.savefig(nome_img, bbox_inches='tight', dpi=300)
    print(f"Artefato guardado: {nome_img}")

if __name__ == "__main__":
    main()