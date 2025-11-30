import streamlit as st
import pandas as pd
import time
from pdf_utils import compress_single_pdf, merge_pdfs_separated, check_file_size, MAX_FILE_SIZE_MB

st.set_page_config(
    page_title="QDS - Otimizador de PDF",
    page_icon="🎲",
    layout="centered"
)

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
def render_login():
  st.title("🔒 QDS - Ferramenta Bloqueada")
  
  st.markdown("""
  Esta ferramenta exclusiva de compressão e unificação de PDFs está disponível 
  apenas para seguidores.
  
  **Para liberar o acesso:**
  1. Siga meu perfil no Instagram: 📷 **[@dr.andreq](https://instagram.com/dr.andreq)**
  2. Procure a **senha do dia** nos meus Stories.
  3. Digite a senha abaixo. 👇
  """)
  
  st.divider()
  
  password_input = st.text_input("Digite a senha dos stories:", type="password")
  
  if st.button("🔓 Desbloquear Ferramenta"):
    try:
      CORRECT_PASSWORD = st.secrets.get("KEYPASS", "medicoprogramador")
    except FileNotFoundError:
      CORRECT_PASSWORD = "medicoprogramador"
    
    if password_input.strip() == CORRECT_PASSWORD:
      st.session_state.authenticated = True
      st.success("Senha correta! Carregando...")
      st.rerun()
    else:
      st.error("Senha incorreta. Verifique os stories novamente!")
def render_tool():
  st.title("📄 QDS - Otimizador de PDF")
  
  st.markdown("""
  <p>Arraste seus arquivos para criar um único PDF otimizado do seu currículo.</p>
  <p>Todos os arquivos enviados serão comprimidos e unidos em um único PDF.</p>
  """, unsafe_allow_html=True)

  
  st.info(f"🛡️ Segurança: O limite máximo por arquivo é de {MAX_FILE_SIZE_MB}MB.")

  with st.sidebar:
    st.header("⚙️ Configurações")
    jpg_quality = st.slider("Qualidade JPEG", 10, 100, 65, help="Menor = Mais leve.")
    target_dpi = st.slider("DPI Alvo", 72, 300, 120, help="120 é ótimo para leitura.")

    if st.button("🔒 Bloquear"):
      st.session_state.authenticated = False
      st.rerun()

  st.subheader("1. Seleção de Arquivos")
  
  col1, col2 = st.columns(2)
  
  with col1:
    st.markdown("**1️⃣ Capa (Opcional)**")
    cover_file = st.file_uploader(
      "Arquivo que será a primeira página", 
      type=["pdf"], 
      accept_multiple_files=False,
      key="cover_uploader"
    )

  with col2:
    st.markdown("**2️⃣ Conteúdo (Corpo)**")
    body_files = st.file_uploader(
      "Demais arquivos (serão ordenados alfabeticamente)", 
      type=["pdf"], 
      accept_multiple_files=True,
      key="body_uploader"
    )

  if st.button("🚀 Iniciar Compressão e Unificação", type="primary"):
    start_time = time.time()

    # 1. Validação de Segurança (Tamanho)
    files_to_check = []
    if cover_file: files_to_check.append(cover_file)
    if body_files: files_to_check.extend(body_files)
    
    if not files_to_check:
      st.warning("Por favor, selecione pelo menos um arquivo.")
      return

    for f in files_to_check:
      is_safe, size_mb = check_file_size(f)
      if not is_safe:
        st.error(f"Erro: O arquivo '{f.name}' é muito grande ({size_mb:.1f}MB). O limite é {MAX_FILE_SIZE_MB}MB.")
        return

    # 2. Início do Processamento
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_data = []
    
    # Variáveis para armazenar os bytes processados
    processed_cover = None
    processed_body_list = []

    total_steps = len(files_to_check) + 1 # +1 para o merge final
    current_step = 0

    # A. Processar Capa (se houver)
    if cover_file:
      status_text.text(f"Comprimindo Capa: {cover_file.name}...")
      bytes_data = cover_file.getvalue()
      new_bytes, o_mb, f_mb, red, status = compress_single_pdf(bytes_data, cover_file.name, jpg_quality, target_dpi)
      
      processed_cover = {'filename': cover_file.name, 'bytes': new_bytes}
      
      results_data.append({
        "Tipo": "CAPA",
        "Arquivo": cover_file.name,
        "Redução": f"{red:.1f}%",
        "Status": status
      })
      
      current_step += 1
      progress_bar.progress(current_step / total_steps)

    # B. Processar Corpo (Ordenação Alfabética)
    if body_files:
      # A ordenação acontece aqui
      body_files.sort(key=lambda x: x.name)
      
      for b_file in body_files:
        status_text.text(f"Comprimindo Conteúdo: {b_file.name}...")
        bytes_data = b_file.getvalue()
        new_bytes, o_mb, f_mb, red, status = compress_single_pdf(bytes_data, b_file.name, jpg_quality, target_dpi)
        
        processed_body_list.append({'filename': b_file.name, 'bytes': new_bytes})
        
        results_data.append({
          "Tipo": "CORPO",
          "Arquivo": b_file.name,
          "Redução": f"{red:.1f}%",
          "Status": status
        })
        
        current_step += 1
        progress_bar.progress(current_step / total_steps)

    # Exibir Tabela de Resultados
    st.subheader("2. Relatório de Compressão")
    st.dataframe(pd.DataFrame(results_data), width='stretch')

    # C. Unificação (Merge)
    status_text.text("Unificando arquivos...")
    final_pdf_bytes = merge_pdfs_separated(processed_cover, processed_body_list)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    progress_bar.progress(1.0)
    status_text.success(f"Concluído com sucesso em {elapsed_time:.2f} segundos!")

    # D. Download
    st.subheader("3. Download")
    final_size_mb = final_pdf_bytes.getbuffer().nbytes / (1024**2)
    st.write(f"Tamanho Final: **{final_size_mb:.2f} MB**")

    st.download_button(
      label="⬇️ Baixar PDF Completo",
      data=final_pdf_bytes,
      file_name="qds_pdfunifier.pdf",
      mime="application/pdf"
    )
if __name__ == "__main__":
  if not st.session_state.authenticated:
    render_login()
  else:
    render_tool()