# 📄 Otimizador de PDF Pro

Uma ferramenta web desenvolvida em Python e Streamlit para comprimir, otimizar e unificar arquivos PDF, focada em documentos escaneados.

A aplicação inclui:
- Compressão inteligente (Rasterização) para reduzir tamanho.
- Unificação (Merge) de múltiplos arquivos.
- Ordenação automática e definição de capa.
- Sistema de bloqueio por senha ("Gatekeeper").

---

## 🚀 Como Rodar

Você pode executar este projeto de duas formas: usando **Docker** (recomendado para isolamento e facilidade) ou **Python Localmente**.

### Opção A: Rodando com Docker (Recomendado)

Se você tem o Docker instalado, não precisa configurar Python ou bibliotecas na sua máquina.

**1. Construir a Imagem**
Abra o terminal na pasta do projeto e rode:

```bash
docker build -t qds_pdfunifier .
```

**2. Rodar o Container**
Após a construção, inicie o aplicativo com o comando:

```bash
docker run -p 8501:8501 qds_pdfunifier
```

**3. Acessar**
Abra seu navegador e acesse: `http://localhost:8501`

---

### Opção B: Rodando Localmente (Python & Venv)

Se preferir rodar direto na sua máquina, siga os passos abaixo para criar um ambiente virtual isolado.

**Pré-requisitos:** Python 3.9 ou superior instalado.

**1. Clone ou baixe este repositório**
Entre na pasta do projeto via terminal.

**2. Crie o Ambiente Virtual (venv)**

* **No Windows:**
    ```bash
    python -m venv venv
    ```
* **No Linux / Mac:**
    ```bash
    python3 -m venv venv
    ```

**3. Ative o Ambiente Virtual**

* **No Windows (Powershell):**
    ```bash
    .\venv\Scripts\Activate.ps1
    ```
* **No Windows (CMD):**
    ```bash
    .\venv\Scripts\activate.bat
    ```
* **No Linux / Mac:**
    ```bash
    source venv/bin/activate
    ```

**4. Instale as Dependências**
Com o ambiente ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

**5. Execute a Aplicação**
```bash
streamlit run app.py
```

O navegador abrirá automaticamente no endereço `http://localhost:8501`.

---

## 🔑 Acesso e Senhas

O aplicativo possui uma tela de bloqueio inicial.
- **Senha de acesso padrão:** `medicoprogramador`

## 🛠️ Tecnologias Utilizadas

- **Frontend:** Streamlit
- **Processamento de PDF:** PyMuPDF (Fitz)
- **Manipulação de Dados:** Pandas
- **Linguagem:** Python 3.10+