# @title Coletor Bluesky V6: Recorte Exato 2025 (PT-BR)
import os
import time
import requests
import pandas as pd
from datetime import datetime
from google.colab import drive
from getpass import getpass
from tqdm.notebook import tqdm

drive.mount('/content/drive')
PASTA_DRIVE = "/content/drive/My Drive/TCC_Dados"

if not os.path.exists(PASTA_DRIVE):
    os.makedirs(PASTA_DRIVE)

BSKY_HANDLE = input("Usuário (ex: usuario.bsky.social): ").strip()
BSKY_PASSWORD = getpass("Senha de App: ").strip()

KEYWORDS = ["dengue", "aedes"]
DATA_INICIO = "2025-01-01T00:00:00Z"
DATA_FIM = "2025-12-31T23:59:59Z"
LIMITE_POSTS = 3000
ARQUIVO_SAIDA = os.path.join(PASTA_DRIVE, "ARQUIVO_SAIDA.csv")
URL = "https://bsky.social/xrpc"

# [TRECHO IMUTÁVEL - Figura 2 do TCC]
def autenticar():
    try:
        resp = requests.post(
            f"{URL}/com.atproto.server.createSession",
            json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}
        )
        if resp.status_code != 200:
            print(f"Erro Login: {resp.json().get('message')}")
            return None
        return resp.json()['accessJwt']
    except Exception as e:
        print(f"Erro Conexão: {e}")
        return None

# [TRECHO IMUTÁVEL - Figura 5 do TCC]
def buscar_respostas(uri_post, headers):
    try:
        params = {'uri': uri_post, 'depth': 1}
        resp = requests.get(f"{URL}/app.bsky.feed.getPostThread", params=params, headers=headers, timeout=5)
        if resp.status_code != 200: return ""
        
        dados = resp.json()
        if 'thread' not in dados or 'replies' not in dados['thread']: return ""
            
        respostas = []
        for r in dados['thread']['replies']:
            if 'post' in r and 'record' in r['post'] and 'text' in r['post']['record']:
                respostas.append(f"[{r['post']['author']['handle']}]: {r['post']['record']['text']}")
        return " | ".join(respostas)
    except:
        return ""

def main():
    token = autenticar()
    if not token: 
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    todos_posts = []
    pbar = tqdm(total=LIMITE_POSTS, desc="Coletando")

    for termo in KEYWORDS:
        cursor = None
        
        while True:
            # [TRECHO IMUTÁVEL - Figura 3 do TCC]
            params = {
                'q': termo, 
                'lang': 'pt',
                'sort': 'latest', 
                'since': DATA_INICIO,
                'until': DATA_FIM,
                'limit': 50
            }
            if cursor: 
                params['cursor'] = cursor

            try:
                resp = requests.get(f"{URL}/app.bsky.feed.searchPosts", params=params, headers=headers)
                
                if resp.status_code == 429:
                    time.sleep(60)
                    continue
                if resp.status_code != 200: 
                    break
                
                data = resp.json()
                posts = data.get('posts', [])
                if not posts: 
                    break

                # [TRECHO IMUTÁVEL - Figura 4 do TCC]
                for post in posts:
                    if len(todos_posts) >= LIMITE_POSTS: break
                    
                    data_post = post['record']['createdAt']
                    
                    if data_post > DATA_FIM:
                        continue 
                    
                    if data_post < DATA_INICIO:
                        cursor = None
                        break

                    uri = post['uri']
                    reply_txt = ""
                    if post.get('replyCount', 0) > 0:
                        reply_txt = buscar_respostas(uri, headers)
                        time.sleep(0.1)

                    todos_posts.append({
                        'data': data_post,
                        'autor': post['author']['handle'],
                        'texto_original': post['record']['text'],
                        'respostas_coletadas': reply_txt,
                        'likes': post.get('likeCount', 0),
                        'reposts': post.get('repostCount', 0),
                        'uri': uri,
                        'termo_busca': termo
                    })
                    pbar.update(1)

                if len(todos_posts) >= LIMITE_POSTS: 
                    break
                
                cursor = data.get('cursor')
                if not cursor: 
                    break

            except Exception:
                time.sleep(5)
                continue
        
        if len(todos_posts) >= LIMITE_POSTS: 
            break

    pbar.close()
    
    if todos_posts:
        df = pd.DataFrame(todos_posts)
        df = df.drop_duplicates(subset=['uri'])
        df['data'] = pd.to_datetime(df['data'], utc=True)
        df = df[df['data'].dt.year == 2025]
        
        df.to_csv(ARQUIVO_SAIDA, index=False)

if __name__ == "__main__":
    main()