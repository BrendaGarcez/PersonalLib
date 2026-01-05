import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io

# --- CONFIGURAÇÃO ---
# Substitua pelo ID da pasta que você copiou da URL do Drive
PASTA_ID = "1xRfwj7OH1BnbDORB-fTdDqFCOoIj_AIj" 

# Autenticação
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
drive_service = build('drive', 'v3', credentials=creds)

st.title("📚 Minha Biblioteca Particular")

st.divider()

# --- LISTAGEM DE LIVROS ---
st.subheader("📚 Minha Estante")

results = drive_service.files().list(
    q=f"'{PASTA_ID}' in parents and trashed = false",
    fields="files(id, name, webViewLink, thumbnailLink)"
).execute()

items = results.get('files', [])

if not items:
    st.info("A pasta está vazia.")
else:
    # Cria uma grade (grid) de 3 colunas
    cols = st.columns(3)
    
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            # Link da imagem (usa a do Drive ou um ícone de PDF bonito)
            img_url = item.get('thumbnailLink', "https://cdn-icons-png.flaticon.com/512/337/337946.png")
            
            # Container para o livro
            st.image(img_url, use_container_width=True)
            st.markdown(f"<div style='text-align: center;'><a href='{item['webViewLink']}'>{item['name']}</a></div>", unsafe_allow_html=True)
            st.write("") # Espaçamento