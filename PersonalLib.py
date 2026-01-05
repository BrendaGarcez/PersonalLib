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

# --- ÁREA DE UPLOAD ---
uploaded_file = st.file_uploader("Escolha um PDF para carregar", type="pdf")

if uploaded_file is not None:
    with st.spinner('Enviando para o Google Drive...'):
        file_metadata = {
            'name': uploaded_file.name,
            'parents': [PASTA_ID]
        }
        # Converte o arquivo do Streamlit para um fluxo de bytes
        media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), 
                                  mimetype='application/pdf')
        
        drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success(f"O livro '{uploaded_file.name}' foi salvo com sucesso!")

st.divider()

# --- LISTAGEM DE LIVROS ---
st.subheader("Meus Livros")

results = drive_service.files().list(
    q=f"'{PASTA_ID}' in parents and trashed = false",
    fields="files(id, name, webViewLink)"
).execute()

items = results.get('files', [])

if not items:
    st.info("A pasta está vazia.")
else:
    for item in items:
        # Cria um link que abre o PDF direto no Drive
        st.markdown(f"📖 [{item['name']}]({item['webViewLink']})")