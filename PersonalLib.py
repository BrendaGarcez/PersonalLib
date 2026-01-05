import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- CONFIGURAÇÃO ---
# ID da sua pasta principal (Biblioteca)
PASTA_RAIZ_ID = "1xRfwj7OH1BnbDORB-fTdDqFCOoIj_AIj" 

# Autenticação
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
drive_service = build('drive', 'v3', credentials=creds)

# --- FUNÇÕES DE AUXÍLIO ---
def buscar_categorias(id_pai):
    """Busca todas as pastas dentro da pasta raiz para usar como categorias"""
    query = f"'{id_pai}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def listar_livros(id_pasta):
    """Lista PDFs dentro de uma pasta específica"""
    query = f"'{id_pasta}' in parents and mimeType = 'application/pdf' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name, webViewLink, thumbnailLink)").execute()
    return results.get('files', [])

# --- INTERFACE ---
st.set_page_config(page_title="Minha Biblioteca", layout="wide")

# Sidebar para Navegação
st.sidebar.title("🗂️ Categorias")
categorias = buscar_categorias(PASTA_RAIZ_ID)

# Criar lista de nomes para o rádio button
nomes_categorias = ["📚 Todos (Raiz)"] + [c['name'] for c in categorias]
categoria_selecionada = st.sidebar.radio("Ir para:", nomes_categorias)

# Definir qual ID de pasta usar
if categoria_selecionada == "📚 Todos (Raiz)":
    id_atual = PASTA_RAIZ_ID
else:
    id_atual = next(c['id'] for c in categorias if c['name'] == categoria_selecionada)

# --- BARRA DE PESQUISA NA SIDEBAR ---
st.sidebar.divider()
st.sidebar.subheader("🔍 Pesquisar")
termo_busca = st.sidebar.text_input("Digite o nome do livro", "").lower()

# --- FILTRAGEM E EXIBIÇÃO ---
livros = listar_livros(id_atual)

# Lógica de Filtro: se houver pesquisa, filtramos a lista de livros
if termo_busca:
    livros = [l for l in livros if termo_busca in l['name'].lower()]

# Título Principal
st.title(f"Biblioteca: {categoria_selecionada}")

if not livros:
    if termo_busca:
        st.warning(f"Nenhum livro encontrado com o termo: '{termo_busca}'")
    else:
        st.info(f"Nenhum PDF encontrado em '{categoria_selecionada}'.")
else:
    # Mostra o status da busca ou total da categoria
    if termo_busca:
        st.write(f"🔍 Encontrado(s) **{len(livros)}** resultado(s) para sua busca.")
    else:
        st.write(f"Você tem **{len(livros)}** livros nesta categoria.")
    
    # Grid de Exibição
    cols = st.columns(4)
    for idx, livro in enumerate(livros):
        with cols[idx % 4]:
            capa = livro.get('thumbnailLink', "https://cdn-icons-png.flaticon.com/512/337/337946.png")
            st.image(capa, width='stretch')
            st.markdown(
                f"<div style='text-align: center; font-size: 0.85rem; height: 50px; overflow: hidden;'>"
                f"<a href='{livro['webViewLink']}' target='_blank'>{livro['name']}</a>"
                f"</div>", 
                unsafe_allow_html=True
            )
            st.write("---")