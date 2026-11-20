import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os
import base64
import unicodedata
import re
import time
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests

ARQUIVO_LOGO = next((f for f in ["logo_grano.png", "logo_grano.jpg", "logo_grano.jpeg"] if os.path.exists(f)), None)

st.set_page_config(
    page_title="WMS Grano — Gestão Logística",
    page_icon=ARQUIVO_LOGO if ARQUIVO_LOGO else "📦",
    layout="wide"
)

st.markdown(
    """
    <style>
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    div[data-testid="InputInstructions"] {
        font-size: 0 !important;
    }
    div[data-testid="InputInstructions"]::after {
        content: "Press Enter";
        font-size: 0.75rem !important;
        color: rgba(28, 36, 30, 0.55);
    }
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"] {
        border-color: rgba(27, 94, 32, 0.45) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-color: rgba(27, 94, 32, 0.4) !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #1B5E20 !important;
        box-shadow: 0 0 0 1px #1B5E20 !important;
    }

    /* === PAINEL LATERAL ESCURO === */
    section[data-testid="stSidebar"] {
        background-color: #141A16 !important;
        border-right: 2px solid #1B5E20 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #E6E1D6 !important;
    }
    /* Cartão do Usuário Logado */
    section[data-testid="stSidebar"] div[data-testid="stAlert"],
    section[data-testid="stSidebar"] div[data-testid="stAlertContainer"] {
        background-color: #1F2922 !important;
        border: 1px solid rgba(76, 175, 80, 0.45) !important;
        border-radius: 10px !important;
    }
    /* Caixa Alterar Senha (fechada e aberta) */
    section[data-testid="stSidebar"] div[data-testid="stExpander"],
    section[data-testid="stSidebar"] div[data-testid="stExpander"] details,
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
    section[data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
        background-color: #1F2922 !important;
        border-color: rgba(76, 175, 80, 0.4) !important;
        border-radius: 8px !important;
    }
        /* Campos de senha com fundo off-white claro e letra escura */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: #EAE7E0 !important;
        color: #141A16 !important;
        caret-color: #141A16 !important;
        border-color: #4CAF50 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"] button {
        background-color: #EAE7E0 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"] button svg,
    section[data-testid="stSidebar"] div[data-baseweb="input"] button svg path {
        fill: #141A16 !important;
        color: #141A16 !important;
    }

    /* Botões do menu lateral com fundo claro e letra escura */
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondaryFormSubmit"] {
        background-color: #EAE7E0 !important;
        border: 1px solid #4CAF50 !important;
    }
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] *,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondaryFormSubmit"] * {
        color: #141A16 !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background-color: #FFFFFF !important;
        border-color: #1B5E20 !important;
    }    
    /* Escurece as caixas de aviso (st.success / st.info / st.warning) e botões secundários */
    [data-testid="stAppViewContainer"] div[role="alert"],
    [data-testid="stAppViewContainer"] div[data-testid="stAlert"],
    [data-testid="stAppViewContainer"] div[data-testid="stAlertContainer"],
    [data-testid="stAppViewContainer"] div[data-testid="stNotification"] {
        background-color: #C7D1C5 !important;
        border: 1px solid rgba(27, 94, 32, 0.6) !important;
        border-radius: 10px !important;
    }
    [data-testid="stAppViewContainer"] div[role="alert"] *,
    [data-testid="stAppViewContainer"] div[data-testid="stAlert"] *,
    [data-testid="stAppViewContainer"] div[data-testid="stAlertContainer"] * {
        color: #141A16 !important;
        font-weight: 500 !important;
    }
    [data-testid="stAppViewContainer"] button[data-testid="stBaseButton-secondary"],
    [data-testid="stAppViewContainer"] button[data-testid="stBaseButton-secondaryFormSubmit"] {
        background-color: #CFC9BC !important;
        color: #141A16 !important;
        border: 1px solid rgba(27, 94, 32, 0.55) !important;
    }
        section[data-testid="stSidebar"] div[data-testid="stAlert"] *,
    section[data-testid="stSidebar"] div[data-testid="stAlertContainer"] * {
        color: #E6E1D6 !important;
    }
    [data-testid="stAppViewContainer"] button[data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stAppViewContainer"] button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background-color: #C2BBA9 !important;
        border-color: #1B5E20 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
conn = st.connection("gsheets", type=GSheetsConnection)

FUSO_BR = ZoneInfo("America/Sao_Paulo")

if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
if "msg_sucesso_carga" not in st.session_state:
    st.session_state.msg_sucesso_carga = ""

def obter_logo_base64():
    if ARQUIVO_LOGO:
        with open(ARQUIVO_LOGO, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        mime = "image/jpeg" if ARQUIVO_LOGO.lower().endswith((".jpg", ".jpeg")) else "image/png"
        return b64, mime
    return None, None

LOGO_B64, LOGO_MIME = obter_logo_base64()

def limpar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    if texto in ("NAN", "NONE", "<NA>"):
        return ""
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto

def normalizar_chave_coluna(nome):
    txt = str(nome).strip().lower()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")
    txt = txt.replace("nº", "numero").replace("no ", "numero ").replace("n.", "numero")
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    stop_words = {"de", "do", "da", "dos", "das", "o", "a", "os", "as"}
    palavras = [p for p in txt.split() if p not in stop_words]
    return " ".join(palavras)

def interpretar_data_br(valor):
    if pd.isna(valor):
        return None
    s = str(valor).strip()
    if not s or s.upper() in ("NAN", "NONE", "<NA>", "-"):
        return None
    parte_data = s.split()[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(parte_data, fmt).date()
        except ValueError:
            continue
    return None

def formatar_data_br_str(valor):
    dt = interpretar_data_br(valor)
    if dt is not None:
        return dt.strftime("%d/%m/%Y")
    s = str(valor).strip() if pd.notna(valor) else ""
    return "" if s.upper() in ("NAN", "NONE", "<NA>") else s

def formatar_hora_br_str(valor):
    if pd.isna(valor):
        return ""
    s = str(valor).strip()
    if not s or s.upper() in ("NAN", "NONE", "<NA>", "-"):
        return ""
    if " " in s:
        s = s.split()[-1]
    partes = s.split(":")
    if len(partes) >= 2 and partes[0].isdigit() and partes[1].isdigit():
        return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
    return s

def formatar_moeda_br_str(valor):
    if pd.isna(valor):
        return ""
    s = str(valor).strip()
    if not s or s.upper() in ("NAN", "NONE", "<NA>", "-"):
        return ""
    limpo = re.sub(r"[R$\s]", "", s)
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        num = float(limpo)
        return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return s
def converter_moeda_para_float(valor):
    if pd.isna(valor):
        return 0.0
    s = str(valor).strip()
    if not s or s.upper() in ("NAN", "NONE", "<NA>", "-"):
        return 0.0
    limpo = re.sub(r"[R$\s]", "", s)
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return 0.0

def eh_pedido_transferencia(valor_pedido):
    if pd.isna(valor_pedido):
        return False
    s = unicodedata.normalize("NFKD", str(valor_pedido)).encode("ASCII", "ignore").decode("utf-8").upper().strip()
    if not s:
        return False
    if "TRANSF" in s:
        return True
    if re.search(r"\bTRF\b", s):
        return True
    return False
    
COLUNAS_TEXTO = ["id_carga", "codigo", "etiqueta", "codigo_bipado", "codigo_vinculado", "lote", "Nº Pedido", "Ordem de Carregamento", "Placa do veículo", "Lacre"]

COLUNAS_PLANEJAMENTO = [
    "Data", "Hora", "Local de Carregamento", "Ordem de Carregamento",
    "Nº Pedido", "Valor Pedido", "Cliente", "Transportadora", "Placa do veículo",
    "Tipo de Veículo", "Valor de Frete", "UF", "Cidade", "CIF/FOB",
    "Veículo compartilhado", "Data da entrega", "Observação", "Status", "Notificação","Nota Fiscal"
]

STATUS_PLANEJAMENTO = [
    "⏳ Aguardando Veículo",
    "🚚 Veículo no Pátio",
    "📦 Em Conferência",
    "✅ Carregado / Liberado",
    "⚠️ Atrasado / Ocorrência"
]

TODOS_MODULOS_SISTEMA = [
    "📊 Análise de Pedidos",
    "🚚 Planejamento Logística",
    "📥 Importação de Pedidos",
    "📦 Conferência dos Pedidos",
    "📈 Painel de Acompanhamento",
    "📋 Gestão de Pedidos",
    "✅ Auditoria e Ajustes",
    "👥 Central de Usuários"
]

TODAS_PERMISSOES_CRITICAS = [
    "✂️ Gerar e Editar Cortes",
    "↩️ Estornar Etiquetas e Corrigir Lotes",
    "🗑️ Excluir Cargas e Pedidos",
    "🔔 Lançar Notificações",
    "👁️ Ver Conferência Completa (Supervisão)"
]

COLUNAS_USUARIOS = ["login", "nome", "senha", "perfil", "modulos_liberados", "permissoes", "ativo","foto_b64", "ultimo_acesso"]

def gerar_hash_senha(senha_plana):
    return hashlib.sha256(str(senha_plana).strip().encode("utf-8")).hexdigest()

def tem_permissao(nome_permissao):
    if st.session_state.get("perfil_usuario") == "ADMIN":
        return True
    return nome_permissao in st.session_state.get("permissoes_usuario", list())

def carregar_usuarios_sistema():
    st.cache_data.clear()
    df_u = carregar_dados("usuarios")
    if df_u.empty or "login" not in df_u.columns:
        df_init = pd.DataFrame([{
            "login": "ADMIN",
            "nome": "ADMINISTRADOR MASTER",
            "senha": gerar_hash_senha("grano2026"),
            "perfil": "ADMIN",
            "modulos_liberados": " | ".join(TODOS_MODULOS_SISTEMA),
            "permissoes": " | ".join(TODAS_PERMISSOES_CRITICAS),
            "ativo": "SIM",
            "foto_b64": "",
            "ultimo_acesso": ""
        }])
        
        salvar_dados(df_init, "usuarios")
        return df_init
    for col in COLUNAS_USUARIOS:
        if col not in df_u.columns:
            df_u[col] = ""
    return df_u
def processar_foto_avatar(arquivo_upload):
    if arquivo_upload is None:
        return ""
    img = Image.open(arquivo_upload).convert("RGB")
    largura, altura = img.size
    lado = min(largura, altura)
    left = (largura - lado) // 2
    top = (altura - lado) // 2
    img = img.crop((left, top, left + lado, top + lado)).resize((64, 64), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=45)
    return "IMG_" + base64.b64encode(buf.getvalue()).decode("utf-8")
def carregar_foto_usuario(login_user):
    login_limpo = limpar_texto(login_user)
    for ext in ["jpg", "jpeg", "png", "webp"]:
        caminho = os.path.join("fotos", f"{login_limpo}.{ext}")
        if os.path.exists(caminho):
            with open(caminho, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""    
def salvar_foto_github(login_user, arquivo_upload):
    if arquivo_upload is None:
        return True, ""
    token = st.secrets.get("GITHUB_TOKEN", "")
    repo = st.secrets.get("GITHUB_REPO", "")
    if not token or not repo:
        return False, "Configure GITHUB_TOKEN e GITHUB_REPO nos Secrets."

    login_limpo = limpar_texto(login_user)
    img = Image.open(arquivo_upload).convert("RGB")
    largura, altura = img.size
    lado = min(largura, altura)
    left = (largura - lado) // 2
    top = (altura - lado) // 2
    img = img.crop((left, top, left + lado, top + lado)).resize((200, 200), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    conteudo_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    api_base = "https://api." + "github.com" + "/repos/" + repo.strip("/") + "/contents/fotos/"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    for ext_ant in ("jpg", "jpeg", "webp"):
        url_ant = f"{api_base}{login_limpo}.{ext_ant}"
        r_ant = requests.get(url_ant, headers=headers)
        if r_ant.status_code == 200:
            requests.delete(url_ant, headers=headers, json={"message": f"Remove foto antiga {login_limpo}", "sha": r_ant.json()["sha"]})

    url_png = f"{api_base}{login_limpo}.png"
    r_get = requests.get(url_png, headers=headers)
    payload = {"message": f"Atualiza foto de {login_limpo}", "content": conteudo_b64}
    if r_get.status_code == 200:
        payload["sha"] = r_get.json()["sha"]

    r_put = requests.put(url_png, headers=headers, json=payload)
    if r_put.status_code in (200, 201):
        return True, ""
    return False, f"Erro GitHub ({r_put.status_code}): {r_put.text}"
        
def encontrar_coluna_correspondente(col_alvo, cols_arquivo):
    alvo_norm = normalizar_chave_coluna(col_alvo)
    for c in cols_arquivo:
        if normalizar_chave_coluna(c) == alvo_norm:
            return c
    if col_alvo == "Nº Pedido":
        for c in cols_arquivo:
            c_norm = normalizar_chave_coluna(c)
            if c_norm in ("pedido", "numero pedido", "num pedido", "id carga", "carga"):
                return c
    if col_alvo == "Placa do veículo":
        for c in cols_arquivo:
            c_norm = normalizar_chave_coluna(c)
            if "placa" in c_norm:
                return c
    return "(Ignorar / Deixar em branco)"

def padronizar_df_maiusculo(df):
    if df.empty:
        return df
    df = df.copy()
    colunas_nao_alterar = {"pedido_real", "bipado", "quantidade", "Status", "senha", "modulos_liberados", "permissoes"}
    for col in df.columns:
        if col in COLUNAS_TEXTO:
            df[col] = df[col].astype(object).apply(limpar_texto)
        elif col not in colunas_nao_alterar:
            df[col] = df[col].astype(object).apply(
                lambda v: "" if (pd.isna(v) or str(v).strip().upper() in ("NAN", "NONE", "<NA>")) else str(v).strip().upper()
            )
    return df

@st.cache_data(ttl=300, show_spinner=False)
def _ler_planilha_com_cache(aba):
    for tentativa in range(3):
        try:
            df = conn.read(worksheet=aba, ttl=0)
            df = df.dropna(how="all")
            return padronizar_df_maiusculo(df)
        except Exception as e:
            if tentativa < 2:
                time.sleep(1.2)
            else:
                raise e

def carregar_dados(aba):
    try:
        return _ler_planilha_com_cache(aba).copy()
    except Exception as e:
        st.error(f"⚠️ Instabilidade temporária na comunicação com o Google Sheets ao ler '{aba}'. Aguarde 3 segundos e recarregue. (Detalhe: {e})")
        st.stop()

def salvar_dados(df, aba):
    df_padronizado = padronizar_df_maiusculo(df)
    for tentativa in range(3):
        try:
            conn.update(worksheet=aba, data=df_padronizado)
            st.cache_data.clear()
            return
        except Exception as e:
            if tentativa < 2:
                time.sleep(1.2)
            else:
                raise e

def verificar_carga_100_concluida(df_carga_especifica):
    if df_carga_especifica.empty:
        return False
    df_calc = df_carga_especifica.copy()
    df_calc["pedido_real"] = pd.to_numeric(df_calc["pedido_real"], errors="coerce").fillna(0).astype(int)
    df_calc["bipado"] = pd.to_numeric(df_calc["bipado"], errors="coerce").fillna(0).astype(int)
    
    tem_corte = df_calc["produto"].astype(str).str.contains(r"\[CORTADO:", regex=True).any()
    total_ped = df_calc["pedido_real"].sum()
    if total_ped <= 0 and not tem_corte:
        return False
    
    return (df_calc["pedido_real"] == df_calc["bipado"]).all()

def carga_possui_corte(df_carga_especifica):
    if df_carga_especifica.empty or "produto" not in df_carga_especifica.columns:
        return False
    return df_carga_especifica["produto"].astype(str).str.contains(r"\[CORTADO:", regex=True).any()

def extrair_detalhes_corte(df_carga_especifica):
    if df_carga_especifica.empty or "produto" not in df_carga_especifica.columns:
        return "-"
    detalhes = list()
    for _, r in df_carga_especifica.iterrows():
        prod = str(r["produto"])
        if "[CORTADO:" in prod:
            trecho = prod.split("[CORTADO:")[-1].rstrip("]").strip()
            if "| Motivo:" in trecho:
                partes = trecho.split("| Motivo:")
                qtd_parte = partes[0].strip()
                motivo_parte = partes[1].strip()
            else:
                qtd_parte = trecho
                motivo_parte = ""

            try:
                nums = [int(n.strip()) for n in qtd_parte.split("->")]
                if len(nums) == 2:
                    vol_cortado = max(0, nums[0] - nums[1])
                    texto_vol = f"{vol_cortado} volume" if vol_cortado == 1 else f"{vol_cortado} volumes"
                else:
                    texto_vol = qtd_parte
            except Exception:
                texto_vol = qtd_parte

            if motivo_parte:
                detalhes.append(f"SKU {r['codigo']} - {texto_vol} | Motivo: {motivo_parte}")
            else:
                detalhes.append(f"SKU {r['codigo']} - {texto_vol}")
    return " | ".join(detalhes) if detalhes else "-"
def obter_lacre_carga(df_carga_especifica):
    if df_carga_especifica.empty or "lacre" not in df_carga_especifica.columns:
        return ""
    valores = [limpar_texto(v) for v in df_carga_especifica["lacre"] if limpar_texto(v)]
    return valores[0] if valores else ""

def salvar_lacre_carga(id_carga_alvo, numero_lacre):
    df_banco_lacre = carregar_dados("cargas")
    if df_banco_lacre.empty or "id_carga" not in df_banco_lacre.columns:
        return
    if "lacre" not in df_banco_lacre.columns:
        df_banco_lacre["lacre"] = ""
    df_banco_lacre["lacre"] = df_banco_lacre["lacre"].astype(object)
    filtro_l = df_banco_lacre["id_carga"] == id_carga_alvo
    df_banco_lacre.loc[filtro_l, "lacre"] = limpar_texto(numero_lacre)
    salvar_dados(df_banco_lacre, "cargas")

for chave_sessao, valor_padrao in [
    ("usuario_autenticado", False),
    ("login_usuario", ""),
    ("nome_usuario", ""),
    ("perfil_usuario", ""),
    ("modulos_usuario", list()),
    ("permissoes_usuario", list())
]:
    if chave_sessao not in st.session_state:
        st.session_state[chave_sessao] = valor_padrao
if not st.session_state.usuario_autenticado:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #C9C5BA !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #DCD9D0 !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([2.2, 1.6, 2.2])
    with col_l2:
        with st.container(border=True):
            if LOGO_B64:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding-top: 8px; padding-bottom: 12px;">
                        <img src="data:{LOGO_MIME};base64,{LOGO_B64}" style="width: 100px; height: 100px; border-radius: 16px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 14px;">
                        <h2 style="margin: 0; padding: 0;">WMS Grano</h2>
                        <p style="color: gray; margin-top: 4px;">Acesso Restrito — Identifique-se para continuar</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.title("📦 WMS Grano")
                st.caption("Identifique-se para continuar")

            with st.form("form_login_wms"):
                in_login = st.text_input("👤 Usuário (Login):", placeholder="Ex: GRANO.LOG")
                in_senha = st.text_input("🔑 Senha:", type="password", placeholder="Digite sua senha...")
                btn_entrar = st.form_submit_button("Login", type="primary", use_container_width=True)

                if btn_entrar:
                    login_limpo = limpar_texto(in_login)
                    senha_hash = gerar_hash_senha(in_senha)
                    df_users = carregar_usuarios_sistema()
                    user_match = df_users[
                        (df_users["login"].apply(limpar_texto) == login_limpo) &
                        (df_users["senha"].astype(str).str.strip() == senha_hash)
                    ]
                    if user_match.empty:
                        st.error("🚫 Usuário ou senha inválidos.")
                    else:
                        u_row = user_match.iloc[0]
                        if limpar_texto(u_row["ativo"]) != "SIM":
                            st.error("🔒 Este usuário está INATIVO. Procure o administrador.")
                        else:
                            mods = [m.strip() for m in str(u_row["modulos_liberados"]).split("|") if m.strip() in TODOS_MODULOS_SISTEMA]
                            perms = [p.strip() for p in str(u_row["permissoes"]).split("|") if p.strip() in TODAS_PERMISSOES_CRITICAS]
                            if limpar_texto(u_row["perfil"]) == "ADMIN":
                                mods = TODOS_MODULOS_SISTEMA.copy()
                                perms = TODAS_PERMISSOES_CRITICAS.copy()

                            st.session_state.usuario_autenticado = True
                            st.session_state.login_usuario = login_limpo
                            st.session_state.nome_usuario = limpar_texto(u_row["nome"])
                            st.session_state.perfil_usuario = limpar_texto(u_row["perfil"])
                            st.session_state.modulos_usuario = mods
                            st.session_state.permissoes_usuario = perms
                            raw_foto = str(u_row.get("foto_b64", "")).strip()
                            if raw_foto.startswith("IMG_"):
                               raw_foto = raw_foto[4:]
                            st.session_state.foto_usuario = "" if raw_foto.lower() in ["", "nan", "none", "null"] else raw_foto
                            st.rerun()
    components.html(
        """
        <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
        }
        /* Caminhão entra pela esquerda, para na doca no centro (30% a 65%), carrega e cruza até o cliente */
        @keyframes trajetoCarregamento {
            0%   { transform: translateX(-85px); opacity: 0; }
            6%   { opacity: 1; }
            30%  { transform: translateX(455px); }
            65%  { transform: translateX(455px); }
            94%  { opacity: 1; }
            100% { transform: translateX(975px); opacity: 0; }
        }
        @keyframes girarRodasComPausa {
            0%   { transform: rotate(0deg); }
            30%  { transform: rotate(900deg); }
            65%  { transform: rotate(900deg); }
            100% { transform: rotate(1800deg); }
        }
        @keyframes carregarCaixa {
            0%, 31%  { transform: translate(0px, 8px); opacity: 0; }
            39%      { transform: translate(0px, 0px); opacity: 1; }
            53%      { transform: translate(-18px, -12px); opacity: 1; }
            61%      { transform: translate(-24px, -12px); opacity: 0; }
            100%     { opacity: 0; }
        }
        @keyframes sinalConferido {
            0%, 56%  { opacity: 0; transform: scale(0.6); }
            61%, 68% { opacity: 1; transform: scale(1.1); }
            74%, 100%{ opacity: 0; transform: scale(0.8); }
        }
        .cena-cd-wrapper {
            width: 100%;
            max-width: 1050px;
            margin: 12px auto 0 auto;
            overflow: hidden;
            position: relative;
            height: 86px;
        }
        .caminhao-cd {
            position: absolute;
            bottom: 14px;
            left: 0;
            animation: trajetoCarregamento 10.5s ease-in-out infinite;
        }
        .roda-cd {
            transform-box: fill-box;
            transform-origin: center;
            animation: girarRodasComPausa 10.5s ease-in-out infinite;
        }
        .caixa-carga {
            animation: carregarCaixa 10.5s ease-in-out infinite;
        }
        .check-cd {
            transform-box: fill-box;
            transform-origin: center;
            animation: sinalConferido 10.5s ease-in-out infinite;
        }
        </style>

        <div class="cena-cd-wrapper">
            <svg width="100%" height="86" viewBox="0 0 1050 86" fill="none" xmlns="http://w3.org">
                <!-- Galpão / CD Grano bem no Centro -->
                <path d="M465 72 V34 L495 20 L525 34 V72" stroke="#141A16" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                <!-- Doca de Carregamento -->
                <rect x="480" y="44" width="30" height="28" stroke="#141A16" stroke-width="1.4" stroke-dasharray="3 2"/>
                <!-- Detalhe verde no topo do CD -->
                <line x1="486" y1="32" x2="504" y2="32" stroke="#1B5E20" stroke-width="2" stroke-linecap="round"/>

                <!-- Estrada longa de ponta a ponta -->
                <line x1="12" y1="72" x2="1038" y2="72" stroke="#141A16" stroke-width="1.7" stroke-linecap="round"/>
                <line x1="28" y1="78" x2="1022" y2="78" stroke="#141A16" stroke-width="1.2" stroke-dasharray="7 9" stroke-linecap="round" opacity="0.45"/>

                <!-- Supermercado / Destino na ponta direita -->
                <rect x="986" y="42" width="52" height="30" stroke="#141A16" stroke-width="1.7" stroke-linejoin="round"/>
                <!-- Placa / Letreiro no topo do Supermercado -->
                <rect x="994" y="34" width="36" height="8" rx="1" fill="#DDD8CE" stroke="#1B5E20" stroke-width="1.6"/>
                <line x1="1001" y1="38" x2="1023" y2="38" stroke="#1B5E20" stroke-width="1.5" stroke-linecap="round"/>
                <!-- Toldo da fachada -->
                <path d="M984 48 H1040 L1037 53 H987 L984 48 Z" fill="#DDD8CE" stroke="#141A16" stroke-width="1.4" stroke-linejoin="round"/>
                <!-- Porta automática e vitrines -->
                <rect x="1007" y="57" width="10" height="15" stroke="#141A16" stroke-width="1.4"/>
                <rect x="991" y="57" width="11" height="9" stroke="#141A16" stroke-width="1.3"/>
                <rect x="1022" y="57" width="11" height="9" stroke="#141A16" stroke-width="1.3"/>

                <!-- Caixinha sendo carregada na doca -->
                <g class="caixa-carga">
                    <rect x="508" y="52" width="11" height="11" rx="1.5" fill="#DDD8CE" stroke="#1B5E20" stroke-width="1.7"/>
                    <line x1="513.5" y1="52" x2="513.5" y2="63" stroke="#1B5E20" stroke-width="1.2"/>
                </g>

                <!-- Check verde de conferência concluída acima do CD -->
                <g class="check-cd">
                    <circle cx="495" cy="11" r="7" fill="#1B5E20"/>
                    <path d="M491.5 11 L494 13.5 L498.5 8.5" stroke="#EAE7E0" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                </g>
            </svg>

            <!-- Caminhão Black Line -->
            <div class="caminhao-cd">
                <svg width="86" height="44" viewBox="0 0 86 44" fill="none" xmlns="http://w3.org">
                    <rect x="15" y="8" width="42" height="24" rx="2" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7"/>
                    <line x1="22" y1="14" x2="50" y2="14" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                    <path d="M57 15 H68 L76 23 V32 H57 V15 Z" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7" stroke-linejoin="round"/>
                    <path d="M60 18 H66.5 L72 23.5 H60 V18 Z" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                    <line x1="13" y1="32" x2="78" y2="32" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <g class="roda-cd">
                        <circle cx="27" cy="34" r="5.5" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7"/>
                        <circle cx="27" cy="34" r="1.8" fill="#141A16"/>
                    </g>
                    <g class="roda-cd">
                        <circle cx="66" cy="34" r="5.5" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7"/>
                        <circle cx="66" cy="34" r="1.8" fill="#141A16"/>
                    </g>
                </svg>
            </div>
        </div>
        """,
        height=100
    )
    
    st.stop()

with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div style="text-align: center; padding-top: 4px; padding-bottom: 12px;">
                <img src="data:{LOGO_MIME};base64,{LOGO_B64}" style="width: 96px; height: 96px; border-radius: 16px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 16px;">
                <h2 style="margin: 0; padding: 0; font-size: 1.45rem;">WMS Grano</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("📦 WMS Grano")

    foto_b64_atual = carregar_foto_usuario(st.session_state.login_usuario)
    nome_exib = st.session_state.nome_usuario
    mapa_perfis_visual = {"ADMIN": "Administrador", "AUXILIAR ADMINISTRATIVO": "Auxiliar Administrativo"}
    perfil_exib = mapa_perfis_visual.get(str(st.session_state.perfil_usuario).upper(), str(st.session_state.perfil_usuario).title())
    iniciais = "".join([p[0] for p in nome_exib.split()[:2]]).upper() if nome_exib else "U"

    if foto_b64_atual:
        avatar_html = f'<img src="data:image/jpeg;base64,{foto_b64_atual}" style="width: 46px; height: 46px; border-radius: 50%; object-fit: cover; border: 2px solid #4CAF50; flex-shrink: 0;">'
    else:
        avatar_html = f'<div style="width: 46px; height: 46px; border-radius: 50%; background-color: #1B5E20; color: #E6E1D6; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem; border: 2px solid #4CAF50; flex-shrink: 0;">{iniciais}</div>'

    st.markdown(
        f"""
        <div style="background-color: #1F2922; border: 1px solid rgba(76, 175, 80, 0.45); border-radius: 10px; padding: 10px 12px; display: flex; align-items: center; gap: 11px; margin-bottom: 12px;">
            {avatar_html}
            <div style="min-width: 0;">
                <div style="font-weight: 700; font-size: 0.85rem; color: #E6E1D6; line-height: 1.25; word-break: break-word;">{nome_exib}</div>
                <div style="font-size: 0.78rem; color: #A5D6A7; margin-top: 3px;">{perfil_exib}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )    

    modulos_disponiveis = st.session_state.modulos_usuario
    if not modulos_disponiveis:
        st.warning("⚠️ Nenhum módulo liberado para seu usuário. Solicite ao administrador.")
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.usuario_autenticado = False
            st.rerun()
        st.stop()

    st.markdown("<div style='font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #81C784; font-weight: 700; margin-top: 22px; margin-bottom: 10px;'>MÓDULOS DO SISTEMA</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] div.stButton > button {
            background-color: transparent !important;
            border: 1px solid transparent !important;
            color: #E6E1D6 !important;
            justify-content: flex-start !important;
            padding: 8px 12px !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] div.stButton > button p,
        section[data-testid="stSidebar"] div.stButton > button span {
            color: #E6E1D6 !important;
        }
        section[data-testid="stSidebar"] div.stButton > button > div {
            justify-content: flex-start !important;
            width: 100% !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: rgba(76, 175, 80, 0.14) !important;
            border-color: rgba(76, 175, 80, 0.35) !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover p {
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
        section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] {
            background-color: #243329 !important;
            border: 1px solid rgba(76, 175, 80, 0.65) !important;
            border-left: 4px solid #4CAF50 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
        section[data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    if "aba_ativa" not in st.session_state or st.session_state.aba_ativa not in modulos_disponiveis:
        st.session_state.aba_ativa = next(iter(modulos_disponiveis))

    for mod_item in modulos_disponiveis:
        eh_ativo = (st.session_state.aba_ativa == mod_item)
        if st.button(mod_item, key=f"nav_{mod_item}", use_container_width=True, type="primary" if eh_ativo else "secondary"):
            st.session_state.aba_ativa = mod_item
            st.rerun()

    aba = st.session_state.aba_ativa

    st.divider()
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            background-color: #1F2922;
            border: 1px solid rgba(76, 175, 80, 0.45);
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            background-color: #161E18;
            border: 1px dashed rgba(76, 175, 80, 0.55);
            border-radius: 8px;
            padding: 8px;
            min-height: unset;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            width: 100%;
            background-color: #243329;
            color: #E6E1D6;
            border: 1px solid rgba(76, 175, 80, 0.5);
        }
        section[data-testid="stSidebar"] input {
            background-color: #161E18 !important;
            color: #E6E1D6 !important;
            border: 1px solid rgba(76, 175, 80, 0.4) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.expander("👤 Meu Perfil e Senha"):
        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #A5D6A7; margin-bottom: 4px;'>📸 Foto de Perfil</div>", unsafe_allow_html=True)
        minha_nova_foto = st.file_uploader("Trocar foto", type=["png", "jpg", "jpeg", "webp"], key="up_minha_foto", label_visibility="collapsed")
        if st.button("💾 Salvar Minha Foto", use_container_width=True, disabled=(minha_nova_foto is None)):
            with st.spinner("Atualizando foto..."):
                ok_f, msg_f = salvar_foto_github(st.session_state.login_usuario, minha_nova_foto)
                if ok_f:
                    st.success("✅ Foto atualizada!")
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar foto: {msg_f}")

        st.markdown("<hr style='margin: 10px 0; border-color: rgba(76, 175, 80, 0.25);'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #A5D6A7; margin-bottom: 4px;'>🔑 Alterar Senha</div>", unsafe_allow_html=True)

        with st.form("form_trocar_propria_senha", clear_on_submit=True):
            s_atual = st.text_input("Senha Atual:", type="password")
            s_nova = st.text_input("Nova Senha:", type="password")
            s_conf = st.text_input("Confirmar Nova Senha:", type="password")
            if st.form_submit_button("💾 Atualizar Senha", use_container_width=True):
                df_u_alt = carregar_usuarios_sistema()
                idx_u = df_u_alt.index[df_u_alt["login"].apply(limpar_texto) == st.session_state.login_usuario]
                if not idx_u.empty:
                    i_u = idx_u[0]
                    if str(df_u_alt.at[i_u, "senha"]).strip() != gerar_hash_senha(s_atual):
                        st.error("Senha atual incorreta.")
                    elif len(s_nova.strip()) < 4:
                        st.error("A nova senha deve ter pelo menos 4 caracteres.")
                    elif s_nova != s_conf:
                        st.error("A confirmação não confere.")
                    else:
                        df_u_alt.at[i_u, "senha"] = gerar_hash_senha(s_nova)
                        salvar_dados(df_u_alt[COLUNAS_USUARIOS], "usuarios")
                        st.success("✅ Senha alterada com sucesso!")
    if st.button("🚪 Sair / Trocar Usuário", use_container_width=True):
        df_u_out = carregar_usuarios_sistema()
        mask_out = df_u_out["login"].apply(limpar_texto) == st.session_state.login_usuario
        if mask_out.any():
            df_u_out.loc[mask_out, "ultimo_acesso"] = ""
            salvar_dados(df_u_out[COLUNAS_USUARIOS], "usuarios")
            st.cache_data.clear()
        st.session_state.usuario_autenticado = False
        st.rerun()
agora_ping = datetime.now()
ultimo_ping_sessao = st.session_state.get("ultimo_ping_ts")
if ultimo_ping_sessao is None or (agora_ping - ultimo_ping_sessao).total_seconds() >= 180:
    st.cache_data.clear()
    df_u_ping = carregar_dados("usuarios")
    if not df_u_ping.empty and len(df_u_ping) >= 1 and "login" in df_u_ping.columns:
        if "ultimo_acesso" not in df_u_ping.columns:
            df_u_ping["ultimo_acesso"] = ""
        df_u_ping["ultimo_acesso"] = df_u_ping["ultimo_acesso"].astype(object)
        mask_ping = df_u_ping["login"].apply(limpar_texto) == st.session_state.login_usuario
        if mask_ping.any():
            df_u_ping.loc[mask_ping, "ultimo_acesso"] = agora_ping.strftime("%Y-%m-%d %H:%M:%S")
            salvar_dados(df_u_ping, "usuarios")
            st.cache_data.clear()
    st.session_state.ultimo_ping_ts = agora_ping
    
df_u_online = carregar_dados("usuarios")
avatares_online_html = ""
qtd_online = 0
if not df_u_online.empty and "ultimo_acesso" in df_u_online.columns:
    for idx_on, r_on in df_u_online.iterrows():
        ts_str = str(r_on.get("ultimo_acesso", "")).strip()
        if ts_str and ts_str.lower() not in ("nan", "none", "null"):
            try:
                dt_acesso = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                if dt_acesso.tzinfo is None and agora_ping.tzinfo is not None:
                    dt_acesso = dt_acesso.replace(tzinfo=agora_ping.tzinfo)
                if (agora_ping - dt_acesso).total_seconds() <= 600:
                    qtd_online += 1
                    l_on = limpar_texto(r_on.get("login", ""))
                    n_on = str(r_on.get("nome", l_on)).strip()
                    p_on = str(r_on.get("perfil", "")).strip()
                    ini_on = "".join(p[:1] for p in n_on.split()[:2]).upper() if n_on else "U"
                    foto_on = carregar_foto_usuario(l_on)
                    ml_style = "margin-left: -10px;" if qtd_online > 1 else ""
                    if foto_on:
                        bolinha = f'<img src="data:image/png;base64,{foto_on}" title="{n_on} ({p_on}) - Online" style="width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid #4CAF50; background-color: #1F2922; {ml_style}">'
                    else:
                        bolinha = f'<div title="{n_on} ({p_on}) - Online" style="width: 36px; height: 36px; border-radius: 50%; background-color: #1B5E20; color: #E6E1D6; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; border: 2px solid #4CAF50; {ml_style}">{ini_on}</div>'
                    avatares_online_html += bolinha
            except Exception:
                pass

if qtd_online > 0:
    st.markdown(
        f"""
        <div style="position: fixed; top: 12px; right: 210px; z-index: 999999; display: flex; align-items: center;">
            <div style="display: flex; align-items: center;">{avatares_online_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
if aba == "📊 Análise de Pedidos":
    st.title("📊 Análise de Pedidos & Lead Time")
    st.caption("Cruzamento da carteira do BI com a tabela de trânsito (aba 'lead time') para definição de janela de programação, vínculo de NF-e e envio ao Planejamento.")

    def achar_col_bi(lista_cols, palavras_chave):
        for p in palavras_chave:
            p_l = limpar_texto(p)
            for c in lista_cols:
                if p_l == limpar_texto(c):
                    return c
        for p in palavras_chave:
            p_l = limpar_texto(p)
            for c in lista_cols:
                if p_l in limpar_texto(c):
                    return c
        return None

    def limpar_numero_bi(val_raw):
        s = str(val_raw).strip().replace("R$", "").replace(" ", "")
        if not s or s.lower() in ("nan", "none", "-"):
            return 0.0
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        elif "," in s:
            s = s.replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    def pedido_contido_no_planejamento(ped_bi_str, campo_plan_str):
        p_limpo = str(ped_bi_str).strip()
        c_limpo = str(campo_plan_str).strip()
        if not p_limpo or not c_limpo:
            return False
        if limpar_texto(p_limpo) == limpar_texto(c_limpo):
            return True
        padrao = r"(?<!\d)" + re.escape(p_limpo) + r"(?!\d)"
        return bool(re.search(padrao, c_limpo))

    df_lt = carregar_dados("lead time")
    mapa_lt = {}
    if not df_lt.empty:
        cols_lt_lista = list(df_lt.columns)
        col_uf_lt = achar_col_bi(cols_lt_lista, ("ESTADO", "UF"))
        col_cid_lt = achar_col_bi(cols_lt_lista, ("CIDADE", "MUNICIPIO"))
        col_dias_lt = achar_col_bi(cols_lt_lista, ("DIAS", "LEAD TIME", "PRAZO"))
        if col_uf_lt and col_cid_lt and col_dias_lt:
            for _, r_lt in df_lt.iterrows():
                uf_k = limpar_texto(r_lt[col_uf_lt])
                cid_k = limpar_texto(r_lt[col_cid_lt])
                val_str = str(r_lt[col_dias_lt]).strip().replace(",", ".")
                try:
                    mapa_lt[(uf_k, cid_k)] = float(val_str)
                except Exception:
                    pass

    c_up_bi, c_cfg_bi = st.columns((3, 1))
    with c_up_bi:
        arquivo_bi = st.file_uploader("📂 Importar Planilha de Pedidos do BI (.xls, .xlsx, .csv):", type=("xls", "xlsx", "csv"), key="up_bi_analise")
    with c_cfg_bi:
        limite_critico = st.number_input("⚠️ Limite Crítico (dias p/ expedir):", min_value=0.0, max_value=15.0, value=2.0, step=0.5)

    if arquivo_bi is not None:
        try:
            nome_arq_bi = arquivo_bi.name.lower()
            if nome_arq_bi.endswith(".csv"):
                df_bi = pd.read_csv(arquivo_bi, sep=None, engine="python", dtype=str)
            else:
                df_bi = pd.read_excel(arquivo_bi, dtype=str)
            df_bi = df_bi.dropna(how="all").fillna("")

            if df_bi.empty:
                st.warning("O arquivo enviado está vazio.")
            else:
                cols_bi = list(df_bi.columns)
                def achar_idx_bi(termos):
                    c_enc = achar_col_bi(cols_bi, termos)
                    return cols_bi.index(c_enc) if c_enc in cols_bi else 0

                with st.expander("⚙️ Mapeamento das Colunas do BI (confirme se estão corretas)", expanded=True):
                    m1, m2, m3, m4 = st.columns(4)
                    col_ped_bi = m1.selectbox("Número do Pedido / Carga:", cols_bi, index=achar_idx_bi(("PEDIDO", "CARGA", "ORDEM", "NUMERO", "DOCUMENTO")))
                    cli_enc = achar_col_bi(cols_bi, ("CLIENTE", "DESTINATARIO", "RAZAO"))
                    col_cli_bi = m2.selectbox("Cliente (Opcional):", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(cli_enc) + 1) if cli_enc in cols_bi else 0)
                    col_uf_bi = m3.selectbox("Estado (UF):", cols_bi, index=achar_idx_bi(("UF", "ESTADO")))
                    col_cid_bi = m4.selectbox("Cidade:", cols_bi, index=achar_idx_bi(("CIDADE", "MUNICIPIO")))

                    m5, m6, m7, m8 = st.columns(4)
                    col_dt_cria = m5.selectbox("Data de Criação/Lançamento:", cols_bi, index=achar_idx_bi(("LANCAMENTO", "CRIACAO", "EMISSAO", "DATA PEDIDO", "INCLUSAO", "DATA")))
                    col_dt_ent = m6.selectbox("Data de Entrega:", cols_bi, index=achar_idx_bi(("ENTREGA", "PREVISAO", "AGENDAMENTO", "PRAZO")))
                    val_enc = achar_col_bi(cols_bi, ("VALOR", "TOTAL", "FATURAMENTO", "PRECO", "VLR"))
                    col_val_bi = m7.selectbox("Valor do Pedido (R$):", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(val_enc) + 1) if val_enc in cols_bi else 0)
                    vol_enc = achar_col_bi(cols_bi, ("VOLUME", "CAIXA", "QTD", "QUANTIDADE", "UNIDADE"))
                    col_vol_bi = m8.selectbox("Qtd de Volumes:", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(vol_enc) + 1) if vol_enc in cols_bi else 0)

                    nf_enc = achar_col_bi(cols_bi, ("NOTA FISCAL", "NF", "NFE", "NOTA", "DANFE"))
                    col_nf_bi = st.selectbox("Nota Fiscal de Venda (Opcional — para vincular pedidos faturados):", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(nf_enc) + 1) if nf_enc in cols_bi else 0)

                df_plan_exist = carregar_dados("planejamento")
                lista_peds_plan = []
                if not df_plan_exist.empty and "Nº Pedido" in df_plan_exist.columns:
                    lista_peds_plan = df_plan_exist["Nº Pedido"].astype(str).tolist()

                hoje_dt = pd.Timestamp(datetime.now().date())
                linhas_analise = list()
                cidades_sem_lt = set()

                for _, r_bi in df_bi.iterrows():
                    ped_val = str(r_bi[col_ped_bi]).strip()
                    if not ped_val:
                        continue
                    cli_val = str(r_bi[col_cli_bi]).strip() if col_cli_bi != "(Nenhum)" else ""
                    uf_val = limpar_texto(r_bi[col_uf_bi])
                    cid_val = limpar_texto(r_bi[col_cid_bi])
                    valor_num = limpar_numero_bi(r_bi[col_val_bi]) if col_val_bi != "(Nenhum)" else 0.0
                    vol_num = int(round(limpar_numero_bi(r_bi[col_vol_bi]))) if col_vol_bi != "(Nenhum)" else 0
                    nf_raw = str(r_bi[col_nf_bi]).strip() if col_nf_bi != "(Nenhum)" else ""
                    if nf_raw.lower() in ("nan", "none", "null", "-"):
                        nf_raw = ""
                    elif nf_raw.endswith(".0"):
                        nf_raw = nf_raw[:-2]

                    dt_c = pd.to_datetime(str(r_bi[col_dt_cria]).strip(), dayfirst=True, errors="coerce")
                    dt_e = pd.to_datetime(str(r_bi[col_dt_ent]).strip(), dayfirst=True, errors="coerce")

                    lt_dias = mapa_lt.get((uf_val, cid_val))
                    if lt_dias is None and (uf_val or cid_val):
                        cidades_sem_lt.add(f"{cid_val}/{uf_val}")

                    if pd.notna(dt_c) and pd.notna(dt_e) and lt_dias is not None:
                        prazo_total = round((dt_e - dt_c).days, 1)
                        janela_exp = round(prazo_total - lt_dias, 1)
                        dt_limite_exp = dt_e - pd.to_timedelta(lt_dias, unit="D")
                        dias_ate_limite = round((dt_limite_exp - hoje_dt).days, 1)

                        if janela_exp <= 0:
                            status_sla = "🔴 Inviável na Origem"
                            ordem_prio = 1
                        elif dias_ate_limite < 0:
                            status_sla = "🟠 Atrasado p/ Expedir"
                            ordem_prio = 2
                        elif janela_exp <= limite_critico or dias_ate_limite <= limite_critico:
                            status_sla = "🟡 Atenção / Expedir Logo"
                            ordem_prio = 3
                        else:
                            status_sla = "🟢 Viável / Programação Normal"
                            ordem_prio = 4
                        dt_lim_str = dt_limite_exp.strftime("%d/%m/%Y")
                    else:
                        prazo_total = None
                        janela_exp = None
                        dt_lim_str = "-"
                        status_sla = "⚪ Sem Lead Time / Data Inválida"
                        ordem_prio = 5

                    esta_no_plan = any(pedido_contido_no_planejamento(ped_val, p_ex) for p_ex in lista_peds_plan)
                    ja_wms = "🚚 Já no Planejamento" if esta_no_plan else "🆕 Novo (Fora do WMS)"
                    valor_fmt = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    linhas_analise.append({
                        "Prioridade": ordem_prio,
                        "Status SLA": status_sla,
                        "Pedido": ped_val,
                        "Nota Fiscal": nf_raw if nf_raw else "-",
                        "NF_Raw": nf_raw,
                        "Cliente": cli_val,
                        "Cidade": cid_val,
                        "UF": uf_val,
                        "Valor_Num": valor_num,
                        "Valor (R$)": valor_fmt,
                        "Volumes": vol_num,
                        "Criação": dt_c.strftime("%d/%m/%Y") if pd.notna(dt_c) else "-",
                        "Entrega": dt_e.strftime("%d/%m/%Y") if pd.notna(dt_e) else "-",
                        "Prazo Total (d)": prazo_total,
                        "Lead Time (d)": lt_dias,
                        "Janela p/ Expedir (d)": janela_exp,
                        "Data Limite Expedição": dt_lim_str,
                        "Situação WMS": ja_wms
                    })

                df_res_bi = pd.DataFrame(linhas_analise)
                if not df_res_bi.empty:
                    df_res_bi = df_res_bi.sort_values(by=["Prioridade", "Janela p/ Expedir (d)"], ascending=[True, True], na_position="last")

                    if cidades_sem_lt:
                        st.warning(f"⚠️ **{len(cidades_sem_lt)} cidade(s)** não encontrada(s) na aba `lead time`: {', '.join(sorted(list(cidades_sem_lt))[:10])}")

                    k1, k2, k3, k4, k5, k6 = st.columns(6)
                    k1.metric("📦 Total Pedidos", len(df_res_bi))
                    k2.metric("🔴/🟠 Críticos/Atraso", int(df_res_bi["Prioridade"].isin([1, 2]).sum()))
                    k3.metric("🟡 Urgentes", int((df_res_bi["Prioridade"] == 3).sum()))
                    k4.metric("🟢 Viáveis", int((df_res_bi["Prioridade"] == 4).sum()))
                    tot_val_str = f"R$ {df_res_bi['Valor_Num'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    k5.metric("💰 Valor Carteira", tot_val_str)
                    k6.metric("🧊 Total Volumes", f"{int(df_res_bi['Volumes'].sum()):,}".replace(",", "."))

                    filtro_sla = st.multiselect(
                        "Filtrar por Indicador de Prazo:",
                        options=df_res_bi["Status SLA"].unique().tolist(),
                        default=df_res_bi["Status SLA"].unique().tolist()
                    )
                    df_exib_bi = df_res_bi[df_res_bi["Status SLA"].isin(filtro_sla)].drop(columns=["Prioridade", "Valor_Num", "NF_Raw"])

                    st.dataframe(df_exib_bi, use_container_width=True, hide_index=True)

                    df_com_nf = df_res_bi[(df_res_bi["NF_Raw"] != "") & (df_res_bi["Situação WMS"] == "🚚 Já no Planejamento")]
                    if not df_com_nf.empty:
                        st.info(f"🧾 Encontramos **{len(df_com_nf)} pedido(s) faturado(s)** neste arquivo que já estão no Planejamento Logística.")
                        if st.button("🧾 Vincular Notas Fiscais no Planejamento e Gestão de Pedidos", type="primary"):
                            df_p_nf = carregar_dados("planejamento")
                            if "Nota Fiscal" not in df_p_nf.columns:
                                df_p_nf["Nota Fiscal"] = ""
                            df_p_nf["Nota Fiscal"] = df_p_nf["Nota Fiscal"].fillna("").astype(str)

                            qtd_vinc = 0
                            for _, r_nf in df_com_nf.iterrows():
                                ped_alvo = r_nf["Pedido"]
                                nf_nova = f"NF {r_nf['NF_Raw']}" if not r_nf["NF_Raw"].upper().startswith("NF") else r_nf["NF_Raw"]
                                for idx_p, r_p in df_p_nf.iterrows():
                                    if pedido_contido_no_planejamento(ped_alvo, r_p.get("Nº Pedido", "")):
                                        atual_nf = str(df_p_nf.at[idx_p, "Nota Fiscal"]).strip()
                                        if atual_nf.lower() in ("nan", "none", "-"):
                                            atual_nf = ""
                                        partes_nf = [x.strip() for x in atual_nf.split("|") if x.strip()]
                                        if nf_nova not in partes_nf:
                                            partes_nf.append(nf_nova)
                                            df_p_nf.at[idx_p, "Nota Fiscal"] = " | ".join(partes_nf)
                                            qtd_vinc += 1

                            if qtd_vinc > 0:
                                salvar_dados(df_p_nf[COLUNAS_PLANEJAMENTO], "planejamento")
                                st.cache_data.clear()
                                st.success(f"✅ {qtd_vinc} Nota(s) Fiscal(is) vinculada(s) com sucesso!")
                                st.rerun()
                            else:
                                st.warning("Todas essas Notas Fiscais já estavam vinculadas no Planejamento.")

                    st.divider()
                    st.subheader("🚚 Enviar Pedidos Pertinentes para o Planejamento Logística")
                    st.caption("Selecione abaixo apenas os pedidos que você decidiu assumir para enviá-los direto à fila do Planejamento.")

                    opcoes_envio = df_exib_bi[df_exib_bi["Situação WMS"] == "🆕 Novo (Fora do WMS)"]["Pedido"].tolist()
                    pedidos_escolhidos = st.multiselect("Pedidos selecionados para programar:", options=opcoes_envio)

                    if st.button("🚚 Imputar Selecionados no Planejamento Logística", type="primary", disabled=(len(pedidos_escolhidos) == 0)):
                        st.cache_data.clear()
                        df_p_atual = carregar_dados("planejamento")
                        if df_p_atual is None:
                            st.error("⚠️ Falha temporária ao ler a aba 'planejamento' no Google Sheets. Tente clicar novamente em 3 segundos (nenhum dado foi alterado).")
                            st.stop()

                        for c_p in COLUNAS_PLANEJAMENTO:
                            if c_p not in df_p_atual.columns:
                                df_p_atual[c_p] = ""

                        df_p_atual = df_p_atual.dropna(how="all").fillna("")
                        novos_plan = list()
                        for p_esc in pedidos_escolhidos:
                            linhas_match = df_res_bi[df_res_bi["Pedido"] == p_esc].to_dict(orient="records")
                            if not linhas_match:
                                continue
                            r_esc = linhas_match.pop(0)
                            nova_l = {c_p: "" for c_p in COLUNAS_PLANEJAMENTO}
                            nova_l["Data"] = r_esc["Data Limite Expedição"] if r_esc["Data Limite Expedição"] != "-" else ""
                            nova_l["Nº Pedido"] = r_esc["Pedido"]
                            nova_l["Valor Pedido"] = r_esc["Valor (R$)"]
                            nova_l["Cliente"] = r_esc["Cliente"]
                            nova_l["UF"] = r_esc["UF"]
                            nova_l["Cidade"] = r_esc["Cidade"]
                            nova_l["Data da entrega"] = r_esc["Entrega"] if r_esc["Entrega"] != "-" else ""
                            nova_l["Observação"] = f"SLA BI | {r_esc['Volumes']} vol | Janela: {r_esc['Janela p/ Expedir (d)']}d | LT: {r_esc['Lead Time (d)']}d"
                            nova_l["Status"] = "⏳ Aguardando Veículo"
                            nova_l["Nota Fiscal"] = f"NF {r_esc['NF_Raw']}" if r_esc.get("NF_Raw") else ""
                            novos_plan.append(nova_l)

                        if novos_plan:
                            df_p_final = pd.concat([df_p_atual[COLUNAS_PLANEJAMENTO], pd.DataFrame(novos_plan)], ignore_index=True)
                            salvar_dados(df_p_final[COLUNAS_PLANEJAMENTO], "planejamento")
                            st.cache_data.clear()
                            st.success(f"🎉 {len(novos_plan)} pedido(s) adicionado(s) ao Planejamento sem alterar os existentes!")

                    buf_bi = io.BytesIO()
                    with pd.ExcelWriter(buf_bi, engine="openpyxl") as writer:
                        df_exib_bi.to_excel(writer, index=False, sheet_name="Analise_Lead_Time")
                    st.download_button(
                        "📥 Baixar Análise Completa em Excel (.xlsx)",
                        data=buf_bi.getvalue(),
                        file_name=f"Analise_Pedidos_LeadTime_{datetime.now().strftime('%d%m%Y')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e_bi:
            st.error(f"Erro ao ler a planilha do BI: {e_bi}")

elif aba == "🚚 Planejamento Logística":
    st.title("📡 Monitoramento e Indicadores de Pedidos")
    st.caption("Controle de programação, frota e andamento operacional dos carregamentos.")

    df_plan = carregar_dados("planejamento")

    if df_plan.empty:
        df_plan = pd.DataFrame(columns=COLUNAS_PLANEJAMENTO)
    else:
        for col in COLUNAS_PLANEJAMENTO:
            if col not in df_plan.columns:
                df_plan[col] = ""

    df_plan = df_plan.fillna("").astype(object)
    for col_p in COLUNAS_PLANEJAMENTO:
        if col_p in df_plan.columns:
            df_plan[col_p] = df_plan[col_p].apply(
                lambda v: "" if str(v).strip().upper() in ("NAN", "NONE", "<NA>") else (
                    str(v).strip()[:-2] if str(v).strip().endswith(".0") else str(v).strip()
                )
            )
    for col_dt in ("Data", "Data da entrega"):
        if col_dt in df_plan.columns:
            df_plan[col_dt] = df_plan[col_dt].apply(formatar_data_br_str)
    if "Hora" in df_plan.columns:
        df_plan["Hora"] = df_plan["Hora"].apply(formatar_hora_br_str)
    for col_vl in ("Valor Pedido", "Valor de Frete"):
        if col_vl in df_plan.columns:
            df_plan[col_vl] = df_plan[col_vl].apply(formatar_moeda_br_str)

    df_plan["Nº Pedido"] = df_plan["Nº Pedido"].apply(limpar_texto)
    status_padrao = STATUS_PLANEJAMENTO.copy().pop(0)
    df_plan["Status"] = df_plan["Status"].apply(lambda s: s if str(s).strip() != "" else status_padrao)
    MESES_PT = {
        "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
        "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
        "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
    }

    REV_MESES_PT = {v: k for k, v in MESES_PT.items()}

    def extrair_mes_ano_label(data_str):
        s = str(data_str).strip()
        partes = s.split("/")
        if len(partes) == 3 and len(partes[1]) == 2 and len(partes[2]) == 4:
            nome_m = MESES_PT.get(partes[1], partes[1])
            return f"{nome_m}/{partes[2]}"
        return ""

    df_plan["_mes_ano_kpi"] = df_plan["Data"].apply(extrair_mes_ano_label)
    meses_disponiveis = sorted(
        [m for m in df_plan["_mes_ano_kpi"].unique() if m != ""],
        key=lambda x: (x.split("/")[1], REV_MESES_PT.get(x.split("/")[0], "00"))
    )
    
    col_f_mes, _ = st.columns([2, 3])
    mes_escolhido = col_f_mes.selectbox(
        "📅 Filtrar Indicadores por Mês:",
        ["Todos os meses"] + meses_disponiveis,
        key="kpi_plan_mes_selecionado"
    )

    df_kpi_plan = df_plan.copy() if mes_escolhido == "Todos os meses" else df_plan[df_plan["_mes_ano_kpi"] == mes_escolhido].copy()

    total_prog_kpi = len(df_kpi_plan)
    soma_pedidos_kpi = df_kpi_plan["Valor Pedido"].apply(converter_moeda_para_float).sum()
    soma_frete_kpi = df_kpi_plan["Valor de Frete"].apply(converter_moeda_para_float).sum()
    perc_frete_kpi = (soma_frete_kpi / soma_pedidos_kpi * 100) if soma_pedidos_kpi > 0 else 0.0

    fmt_pedidos_kpi = f"R$ {soma_pedidos_kpi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    fmt_frete_kpi = f"R$ {soma_frete_kpi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    k_top1, k_top2, k_top3 = st.columns(3)
    k_top1.metric("📋 Total Programado", total_prog_kpi)
    k_top2.metric("💰 Valor Total dos Pedidos", fmt_pedidos_kpi)
    k_top3.metric("🚛 Valor Total de Frete", fmt_frete_kpi, delta=f"{perc_frete_kpi:.1f}% sobre pedidos".replace(".", ","), delta_color="off")

    c_locais, c_top_clientes = st.columns(2)
    with c_locais:
        with st.container(border=True):
            st.markdown("**🏭 Quantidade por Local de Carregamento**")
            df_loc_kpi = df_kpi_plan.copy()
            df_loc_kpi["_loc_limpo"] = df_loc_kpi["Local de Carregamento"].astype(str).str.strip()
            df_loc_validos = df_loc_kpi[df_loc_kpi["_loc_limpo"] != ""].copy()

            if not df_loc_validos.empty:
                df_loc_validos["_eh_transf"] = df_loc_validos["Nº Pedido"].apply(eh_pedido_transferencia)
                linhas_locais = []
                for loc_nome, grupo_loc in df_loc_validos.groupby("_loc_limpo", sort=False):
                    qtd_tot_loc = len(grupo_loc)
                    qtd_tr_loc = int(grupo_loc["_eh_transf"].sum())
                    detalhe_tr = f" ({qtd_tr_loc} transf.)" if qtd_tr_loc > 0 else ""
                    linhas_locais.append(f"• **{loc_nome}:** {qtd_tot_loc}{detalhe_tr}")

                linhas_locais.sort(key=lambda t: int(re.search(r":\*\*\s*(\d+)", t).group(1)), reverse=True)
                st.markdown(" &nbsp;|&nbsp; ".join(linhas_locais))
            else:
                st.caption("Nenhum local de carregamento informado neste período.")

    with c_top_clientes:
        with st.container(border=True):
            st.markdown("**🏆 Top 3 Clientes Mais Atendidos**")
            mask_nao_transf = ~df_kpi_plan["Nº Pedido"].apply(eh_pedido_transferencia)
            clientes_series = df_kpi_plan.loc[mask_nao_transf, "Cliente"].astype(str).str.strip()
            clientes_validos = clientes_series[clientes_series != ""]

            if not clientes_validos.empty:
                top3_cli = clientes_validos.value_counts().head(3)
                medalhas = ["🥇", "🥈", "🥉"]
                linhas_cli = [
                    f"{medalhas[idx]} **{cli}:** {qtd} pedido(s)"
                    for idx, (cli, qtd) in enumerate(top3_cli.items())
                ]
                st.markdown(" &nbsp;|&nbsp; ".join(linhas_cli))
            else:
                st.caption("Nenhum cliente comercial registrado neste período.")

    df_plan.drop(columns=["_mes_ano_kpi"], inplace=True, errors="ignore")

    st.divider()

    st.subheader("🖥️ Painel de Expedição")
    df_exibir_plan = df_plan[COLUNAS_PLANEJAMENTO].copy()

    if not df_exibir_plan.empty:
        df_plan["Notificação"] = df_plan["Notificação"].astype(str).str.strip()
        login_atual_nt = st.session_state.get("login_usuario", "")
        nome_atual_nt = st.session_state.get("nome_usuario", "")

        def notif_eh_para_mim(txt_nt):
            if not txt_nt:
                return False
            if "[PARA:" not in txt_nt:
                return True
            destino = txt_nt.split("[PARA:")[1].split("]")[0].strip()
            return destino in ("TODOS", login_atual_nt, nome_atual_nt)

        mask_minhas_notifs = df_plan["Notificação"].apply(notif_eh_para_mim)
        df_notif_pendentes = df_plan[mask_minhas_notifs]

        if not df_notif_pendentes.empty:
            with st.container(border=True):
                st.error(f"🔔 **Você tem {len(df_notif_pendentes)} notificação(ões) importante(s)!**")
                for idx_nt, row_nt in df_notif_pendentes.iterrows():
                    c_nt_txt, c_nt_btn = st.columns([4, 1], vertical_alignment="center")
                    msg_exibir = re.sub(r"^\[PARA:\s*[^\]]+\]\s*", "", str(row_nt["Notificação"]).strip())
                    msg_exibir = msg_exibir.replace("(DE: ", "(")
                    c_nt_txt.markdown(
                        f"📌 **Pedido {row_nt['Nº Pedido']}** ({row_nt['Cliente']} — {row_nt['Data']} {row_nt['Hora']}): "
                        f"<span style='color: #1B5E20; font-weight: bold;'>{msg_exibir}</span>",
                        unsafe_allow_html=True
                    )
                st.markdown(
                    """
                    <style>
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.stAlert) div.stButton > button {
                        background-color: #C65353 !important;
                        border: 1px solid #A83E3E !important;
                        color: #FFFFFF !important;
                    }
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.stAlert) div.stButton > button p {
                        color: #FFFFFF !important;
                        font-weight: 600 !important;
                    }
                    div[data-testid="stVerticalBlockBorderWrapper"]:has(.stAlert) div.stButton > button:hover {
                        background-color: #B24343 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )                    
            if c_nt_btn.button("✔️ Marcar como Lido", key=f"btn_ler_notif_{idx_nt}", use_container_width=True):
                df_plan["Notificação"] = df_plan["Notificação"].astype(object)
                df_plan.at[idx_nt, "Notificação"] = ""
                salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                st.toast(f"✔️ Notificação do pedido {row_nt['Nº Pedido']} concluída!", icon="✔️")
                st.rerun()        

        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            datas_carreg = sorted([d for d in df_exibir_plan["Data"].dropna().unique().tolist() if str(d).strip() != ""])
            filtro_data_carreg = st.selectbox("Filtrar por Data de Carregamento:", ["Todas as datas"] + datas_carreg, key="filtro_fila_data_carreg")
        with f_col2:
            filtro_status_plan = st.selectbox("Filtrar por Status:", ["Todos os status"] + STATUS_PLANEJAMENTO, key="filtro_fila_status")
        with f_col3:
            busca_livre = st.text_input("Buscar Pedido, Cliente, Placa ou Transportadora:", placeholder="Ex: 303820, Zaffari, ABC1D23 ou Transportadora...")

        if filtro_data_carreg != "Todas as datas":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Data"] == filtro_data_carreg]
        if filtro_status_plan != "Todos os status":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Status"] == filtro_status_plan]
        if busca_livre.strip():
            termo = busca_livre.strip().lower()
            mask_busca = (
                df_exibir_plan["Nº Pedido"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Cliente"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Placa do veículo"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Transportadora"].astype(str).str.lower().str.contains(termo, na=False)
            )
            df_exibir_plan = df_exibir_plan[mask_busca]

        qtd_total_kpi = len(df_exibir_plan)
        qtd_aguardando = int(df_exibir_plan["Status"].isin(["⏳ Aguardando Veículo", "🚚 Veículo no Pátio"]).sum())
        qtd_conferencia = int((df_exibir_plan["Status"] == "📦 Em Conferência").sum())
        qtd_liberados = int((df_exibir_plan["Status"] == "✅ Carregado / Liberado").sum())

        qtd_st1 = int((df_exibir_plan["Status"] == "⏳ Aguardando Veículo").sum())
        qtd_st2 = int((df_exibir_plan["Status"] == "🚚 Veículo no Pátio").sum())
        qtd_st3 = int((df_exibir_plan["Status"] == "📦 Em Conferência").sum())
        qtd_st4 = int((df_exibir_plan["Status"] == "✅ Carregado / Liberado").sum())
        qtd_st5 = int((df_exibir_plan["Status"] == "⚠️ Atrasado / Ocorrência").sum())

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("⏳ Aguardando Veículo", qtd_st1)
        k2.metric("🚚 Veículo no Pátio", qtd_st2)
        k3.metric("📦 Em Conferência", qtd_st3)
        k4.metric("✅ Carregado / Liberado", qtd_st4)
        k5.metric("⚠️ Atrasado / Ocorrência", qtd_st5)

        st.dataframe(df_exibir_plan.drop(columns=["Notificação"], errors="ignore"), use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.markdown("**⚡ Atualização Rápida de Status**")
            st_c1, st_c2, st_c3 = st.columns(3, vertical_alignment="bottom")
            opcoes_rapidas = {
                f"Pedido {r['Nº Pedido']} — {r['Cliente']} (Atual: {r['Status']})": idx
                for idx, r in df_exibir_plan.iterrows()
            }
            if opcoes_rapidas:
                sel_rapida = st_c1.selectbox("Selecione o Pedido:", list(opcoes_rapidas.keys()), key="sel_status_rapido")
                idx_rapido = opcoes_rapidas[sel_rapida]
                status_atual_item = df_plan.at[idx_rapido, "Status"]
                idx_st_padrao = STATUS_PLANEJAMENTO.index(status_atual_item) if status_atual_item in STATUS_PLANEJAMENTO else 0
                novo_status_rapido = st_c2.selectbox("Novo Status:", STATUS_PLANEJAMENTO, index=idx_st_padrao, key="novo_status_rapido")
                if st_c3.button("💾 Atualizar", type="primary", use_container_width=True, key="btn_status_rapido"):
                    df_plan["Status"] = df_plan["Status"].astype(object)
                    df_plan.at[idx_rapido, "Status"] = novo_status_rapido
                    salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.toast(f"✅ Status do pedido '{df_plan.at[idx_rapido, 'Nº Pedido']}' alterado para {novo_status_rapido}!", icon="✅")
                    st.rerun()
                    
        if tem_permissao("🔔 Lançar Notificações"):
            with st.container(border=True):
                st.markdown("**🔔 Lançar Notificação no Pedido**")
                opcoes_notif = {
                    f"Pedido {r['Nº Pedido']} — {r['Cliente']}": idx
                    for idx, r in df_exibir_plan.iterrows()
                }
                df_users_nt = carregar_usuarios_sistema()
                df_users_ativos_nt = df_users_nt[df_users_nt["ativo"].apply(limpar_texto) == "SIM"]
                opcoes_destino_nt = {"👥 TODOS OS USUÁRIOS": "TODOS"}
                for _, u_nt in df_users_ativos_nt.iterrows():
                    opcoes_destino_nt[f"👤 {limpar_texto(u_nt['nome'])} ({limpar_texto(u_nt['login'])})"] = limpar_texto(u_nt["login"])

                if opcoes_notif:
                    with st.form("form_lancar_notif", clear_on_submit=True):
                        nt_c1, nt_c2, nt_c3, nt_c4 = st.columns([2, 2, 3, 1], vertical_alignment="bottom")
                        sel_nt_ped = nt_c1.selectbox("Selecione o Pedido:", list(opcoes_notif.keys()))
                        sel_nt_dest = nt_c2.selectbox("Para quem?", list(opcoes_destino_nt.keys()))
                        txt_nova_notif = nt_c3.text_input(
                            "Mensagem da Notificação:",
                            placeholder="Ex: PRIORIDADE DE CARREGAMENTO..."
                        )
                        btn_enviar_notif = nt_c4.form_submit_button("🔔 Notificar", type="primary", use_container_width=True)

                        if btn_enviar_notif:
                            if txt_nova_notif.strip():
                                idx_nt_alvo = opcoes_notif[sel_nt_ped]
                                dest_codigo = opcoes_destino_nt[sel_nt_dest]
                                df_plan["Notificação"] = df_plan["Notificação"].astype(object)
                                df_plan.at[idx_nt_alvo, "Notificação"] = f"[PARA: {dest_codigo}] {txt_nova_notif.strip().upper()} ({st.session_state.nome_usuario})"
                                salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                                st.toast("🔔 Notificação enviada com sucesso!", icon="🔔")
                                st.rerun()
                            else:
                                st.error("⚠️ Digite a mensagem da notificação antes de salvar.")
               
    else:
        st.info("Nenhum pedido cadastrado no planejamento ainda.")

    st.divider()

    with st.expander("➕ Incluir Pedido Manualmente"):
        with st.form("form_novo_planejamento", clear_on_submit=True):
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            in_data = r1c1.text_input("Data (DD/MM/AAAA):", placeholder="Ex: 18/11/2026")
            in_hora = r1c2.text_input("Hora:", placeholder="Ex: 08:30")
            in_pedido = r1c3.text_input("Nº Pedido (ID da Carga)*:", placeholder="Ex: 106915")
            in_ordem = r1c4.text_input("Ordem de Carregamento:", placeholder="Ex: OC-450")

            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            in_local = r2c1.text_input("Local de Carregamento:", placeholder="Ex: CD Canoas")
            in_cliente = r2c2.text_input("Cliente:", placeholder="Nome do cliente")
            in_val_ped = r2c3.text_input("Valor Pedido:", placeholder="Ex: 15.400,00")
            in_data_ent = r2c4.text_input("Data da entrega (DD/MM/AAAA):", placeholder="Ex: 20/11/2026")

            r3c1, r3c2, r3c3, r3c4 = st.columns(4)
            in_transp = r3c1.text_input("Transportadora:", placeholder="Nome da transportadora")
            in_placa = r3c2.text_input("Placa do veículo:", placeholder="Ex: ABC1D23")
            in_tipo_veic = r3c3.text_input("Tipo de Veículo:", placeholder="Ex: Carreta / Truck")
            in_val_frete = r3c4.text_input("Valor de Frete:", placeholder="Ex: 2.100,00")

            r4c1, r4c2, r4c3, r4c4 = st.columns(4)
            in_uf = r4c1.text_input("UF:", placeholder="Ex: RS")
            in_cidade = r4c2.text_input("Cidade:", placeholder="Ex: Porto Alegre")
            in_cif_fob = r4c3.selectbox("CIF/FOB:", ["CIF", "FOB"])
            in_compart = r4c4.selectbox("Veículo compartilhado:", ["NÃO", "SIM"])

            r5c1, r5c2 = st.columns(2)
            in_status = r5c1.selectbox("Status Inicial:", STATUS_PLANEJAMENTO)
            in_obs = r5c2.text_input("Observação:", placeholder="Observações gerais do agendamento...")

            salvar_novo_plan = st.form_submit_button("➕ Incluir Pedido", type="primary", use_container_width=True)

            if salvar_novo_plan:
                ped_limpo = limpar_texto(in_pedido)
                if not ped_limpo:
                    st.error("⚠️ O campo **Nº Pedido** é obrigatório!")
                elif ped_limpo in df_plan["Nº Pedido"].values:
                    st.error(f"🚫 O pedido **'{ped_limpo}'** já está cadastrado na agenda! Use a opção de editar abaixo.")
                else:
                    nova_linha_plan = pd.DataFrame([{
                        "Data": formatar_data_br_str(in_data),
                        "Hora": formatar_hora_br_str(in_hora),
                        "Local de Carregamento": in_local.strip(),
                        "Ordem de Carregamento": limpar_texto(in_ordem),
                        "Nº Pedido": ped_limpo,
                        "Valor Pedido": formatar_moeda_br_str(in_val_ped),
                        "Cliente": in_cliente.strip(),
                        "Transportadora": in_transp.strip(),
                        "Placa do veículo": limpar_texto(in_placa),
                        "Tipo de Veículo": in_tipo_veic.strip(),
                        "Valor de Frete": formatar_moeda_br_str(in_val_frete),
                        "UF": limpar_texto(in_uf),
                        "Cidade": in_cidade.strip(),
                        "CIF/FOB": in_cif_fob,
                        "Veículo compartilhado": in_compart,
                        "Data da entrega": formatar_data_br_str(in_data_ent),
                        "Observação": in_obs.strip(),
                        "Status": in_status,
                        "Notificação": ""
                    }])
                    df_plan_atualizado = pd.concat([df_plan, nova_linha_plan], ignore_index=True)
                    salvar_dados(df_plan_atualizado[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.success(f"✅ Pedido **'{ped_limpo}'** adicionado ao planejamento!")
                    st.rerun()

    with st.expander("✏️ Editar ou Excluir Pedido"):
        if not df_plan.empty:
            opcoes_plan = {
                f"Pedido: {r['Nº Pedido']} | Cliente: {r['Cliente']} | Data: {r['Data']} {r['Hora']} | Status: {r['Status']}": idx
                for idx, r in df_plan.iterrows()
            }
            escolha_plan = st.selectbox("Selecione o agendamento para editar:", list(opcoes_plan.keys()), key="sel_edit_plan")
            idx_plan = opcoes_plan[escolha_plan]
            reg_plan = df_plan.loc[idx_plan]

            with st.form("form_editar_planejamento"):
                e1c1, e1c2, e1c3, e1c4 = st.columns(4)
                ed_data = e1c1.text_input("Data:", value=str(reg_plan["Data"]))
                ed_hora = e1c2.text_input("Hora:", value=str(reg_plan["Hora"]))
                ed_pedido = e1c3.text_input("Nº Pedido:", value=str(reg_plan["Nº Pedido"]))
                ed_ordem = e1c4.text_input("Ordem de Carregamento:", value=str(reg_plan["Ordem de Carregamento"]))

                e2c1, e2c2, e2c3, e2c4 = st.columns(4)
                ed_local = e2c1.text_input("Local de Carregamento:", value=str(reg_plan["Local de Carregamento"]))
                ed_cliente = e2c2.text_input("Cliente:", value=str(reg_plan["Cliente"]))
                ed_val_ped = e2c3.text_input("Valor Pedido:", value=str(reg_plan["Valor Pedido"]))
                ed_data_ent = e2c4.text_input("Data da entrega:", value=str(reg_plan["Data da entrega"]))

                e3c1, e3c2, e3c3, e3c4 = st.columns(4)
                ed_transp = e3c1.text_input("Transportadora:", value=str(reg_plan["Transportadora"]))
                ed_placa = e3c2.text_input("Placa do veículo:", value=str(reg_plan["Placa do veículo"]))
                ed_tipo_veic = e3c3.text_input("Tipo de Veículo:", value=str(reg_plan["Tipo de Veículo"]))
                ed_val_frete = e3c4.text_input("Valor de Frete:", value=str(reg_plan["Valor de Frete"]))

                e4c1, e4c2, e4c3, e4c4 = st.columns(4)
                ed_uf = e4c1.text_input("UF:", value=str(reg_plan["UF"]))
                ed_cidade = e4c2.text_input("Cidade:", value=str(reg_plan["Cidade"]))
                ed_cif_fob = e4c3.text_input("CIF/FOB:", value=str(reg_plan["CIF/FOB"]))
                ed_compart = e4c4.text_input("Veículo compartilhado:", value=str(reg_plan["Veículo compartilhado"]))

                e5c1, e5c2 = st.columns(2)
                st_atual_ed = str(reg_plan["Status"])
                idx_ed_st = STATUS_PLANEJAMENTO.index(st_atual_ed) if st_atual_ed in STATUS_PLANEJAMENTO else 0
                ed_status = e5c1.selectbox("Status:", STATUS_PLANEJAMENTO, index=idx_ed_st)
                ed_obs = e5c2.text_input("Observação:", value=str(reg_plan["Observação"]))

                if tem_permissao("🗑️ Excluir Cargas e Pedidos"):
                 c_btn_save, c_btn_del = st.columns(2)
                 btn_atualizar_plan = c_btn_save.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                 btn_excluir_plan = c_btn_del.form_submit_button("🗑️ Excluir este Pedido", use_container_width=True)
                else:
                 btn_atualizar_plan = st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                 btn_excluir_plan = False

                if btn_atualizar_plan:
                    dados_editados = {
                        "Data": formatar_data_br_str(ed_data),
                        "Hora": formatar_hora_br_str(ed_hora),
                        "Local de Carregamento": ed_local.strip(),
                        "Ordem de Carregamento": limpar_texto(ed_ordem),
                        "Nº Pedido": limpar_texto(ed_pedido),
                        "Valor Pedido": formatar_moeda_br_str(ed_val_ped),
                        "Cliente": ed_cliente.strip(),
                        "Transportadora": ed_transp.strip(),
                        "Placa do veículo": limpar_texto(ed_placa),
                        "Tipo de Veículo": ed_tipo_veic.strip(),
                        "Valor de Frete": formatar_moeda_br_str(ed_val_frete),
                        "UF": limpar_texto(ed_uf),
                        "Cidade": ed_cidade.strip(),
                        "CIF/FOB": limpar_texto(ed_cif_fob),
                        "Veículo compartilhado": limpar_texto(ed_compart),
                        "Data da entrega": formatar_data_br_str(ed_data_ent),
                        "Observação": ed_obs.strip(),
                        "Status": ed_status
                    }
                    for col_nome, novo_valor in dados_editados.items():
                        df_plan[col_nome] = df_plan[col_nome].astype(object)
                        df_plan.at[idx_plan, col_nome] = novo_valor

                    salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.success("✅ Agendamento atualizado com sucesso!")
                    st.rerun()

                if btn_excluir_plan:
                    df_plan_rest = df_plan.drop(idx_plan)
                    if df_plan_rest.empty:
                        df_plan_rest = pd.DataFrame(columns=COLUNAS_PLANEJAMENTO)
                    salvar_dados(df_plan_rest[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.warning("🗑️ Agendamento removido da agenda!")
                    st.rerun()
        else:
            st.info("Nenhum agendamento cadastrado na planilha ainda.")

elif aba == "📥 Importação de Pedidos":
    st.title("📥 Importar Pedidos para Conferência")
    st.write("Suba um ou vários arquivos de pedido (SKU, Produto e Quantidade). Eles ficarão disponíveis imediatamente para o conferente.")

    arquivos_pedidos = st.file_uploader(
        "Suba o(s) Excel/CSV do(s) pedido(s)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key=f"uploader_pedido_{st.session_state.upload_key}"
    )

    if st.session_state.msg_sucesso_carga:
        st.success(st.session_state.msg_sucesso_carga)
        st.session_state.msg_sucesso_carga = ""

    if arquivos_pedidos:
        df_existente_check = carregar_dados("cargas")
        cargas_cadastradas = df_existente_check["id_carga"].unique().tolist() if (not df_existente_check.empty and "id_carga" in df_existente_check.columns) else list()

        st.subheader("Identificação da(s) Carga(s)")
        ids_informados = list()
        tem_erro_id = False

        if len(arquivos_pedidos) == 1:
            arq_unico = arquivos_pedidos[0]
            id_input = st.text_input(
                "Identificação da Carga / Pedido (Ex: CARGA-105):",
                placeholder="Digite um código único para esta carga",
                key=f"id_unico_{st.session_state.upload_key}"
            )
            id_limpo = limpar_texto(id_input)
            if id_limpo:
                if id_limpo in cargas_cadastradas:
                    st.error(f"🚫 BLOQUEADO! A carga **'{id_limpo}'** já existe no sistema! Digite outro código ou exclua a antiga abaixo.")
                    tem_erro_id = True
                ids_informados.append((arq_unico, id_limpo))
            else:
                tem_erro_id = True
        else:
            st.caption("Informe o código/ID de carga correspondente a cada arquivo selecionado:")
            vistos_na_remessa = set()
            for idx_arq, arq in enumerate(arquivos_pedidos):
                c_nome, c_id = st.columns([2, 3], vertical_alignment="center")
                with c_nome:
                    st.markdown(f"📄 **{arq.name}**")
                with c_id:
                    sugestao_id = os.path.splitext(arq.name)[0].strip()
                    val_id = st.text_input(
                        f"ID da Carga ({arq.name}):",
                        value=sugestao_id,
                        label_visibility="collapsed",
                        placeholder="Digite o ID desta carga...",
                        key=f"id_massa_{st.session_state.upload_key}_{idx_arq}"
                    )
                    val_limpo = limpar_texto(val_id)
                    if not val_limpo:
                        tem_erro_id = True
                    elif val_limpo in cargas_cadastradas:
                        st.error(f"🚫 A carga '{val_limpo}' já existe no banco!")
                        tem_erro_id = True
                    elif val_limpo in vistos_na_remessa:
                        st.error(f"🚫 Código '{val_limpo}' repetido nesta lista!")
                        tem_erro_id = True
                    else:
                        vistos_na_remessa.add(val_limpo)
                        ids_informados.append((arq, val_limpo))

        primeiro_arq = arquivos_pedidos[0]
        primeiro_arq.seek(0)
        df_amostra = pd.read_csv(primeiro_arq, sep=None, engine="python", dtype=str) if primeiro_arq.name.endswith(".csv") else pd.read_excel(primeiro_arq, dtype=str)
        cols_ped = list(df_amostra.columns)

        st.subheader("Mapeamento de Colunas")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_cod = st.selectbox("Coluna do SKU / CÓDIGO:", cols_ped)
        with c2:
            p_prod = st.selectbox("Coluna do NOME DO PRODUTO:", cols_ped)
        with c3:
            p_qtd = st.selectbox("Coluna da QUANTIDADE PEDIDA:", cols_ped)

        texto_botao = "🚀 Enviar Pedido para o Celular do Conferente" if len(arquivos_pedidos) == 1 else f"🚀 Enviar {len(arquivos_pedidos)} Pedidos para Conferência"

        if st.button(texto_botao, type="primary", use_container_width=True, disabled=tem_erro_id):
            try:
                df_existente = carregar_dados("cargas")
                existentes_agora = df_existente["id_carga"].unique().tolist() if (not df_existente.empty and "id_carga" in df_existente.columns) else list()

                novas_bases = list()
                nomes_enviados = list()

                for arq_item, id_carga_item in ids_informados:
                    if id_carga_item in existentes_agora:
                        st.error(f"🚫 BLOQUEADO! A carga '{id_carga_item}' já está cadastrada.")
                        st.stop()

                    arq_item.seek(0)
                    df_ped = pd.read_csv(arq_item, sep=None, engine="python", dtype=str) if arq_item.name.endswith(".csv") else pd.read_excel(arq_item, dtype=str)

                    base_ped = pd.DataFrame({
                        "id_carga": id_carga_item,
                        "codigo": df_ped[p_cod].apply(limpar_texto),
                        "produto": df_ped[p_prod].astype(str).str.strip(),
                        "pedido_real": pd.to_numeric(df_ped[p_qtd], errors="coerce").fillna(0).astype(int)
                    })
                    base_ped = base_ped[base_ped["codigo"] != ""]
                    base_ped = base_ped.groupby(["id_carga", "codigo", "produto"], as_index=False).sum()
                    base_ped["bipado"] = 0

                    novas_bases.append(base_ped)
                    nomes_enviados.append(id_carga_item)

                df_novos_todos = pd.concat(novas_bases, ignore_index=True)

                if not df_existente.empty and "id_carga" in df_existente.columns:
                    df_final = pd.concat([df_existente, df_novos_todos], ignore_index=True)
                else:
                    df_final = df_novos_todos

                salvar_dados(df_final, "cargas")

                if len(nomes_enviados) == 1:
                    st.session_state.msg_sucesso_carga = f"✅ Carga '{nomes_enviados[0]}' enviada com sucesso! O conferente já pode iniciar a conferência."
                else:
                    lista_str = ", ".join(nomes_enviados)
                    st.session_state.msg_sucesso_carga = f"✅ Cargas ({lista_str}) enviadas com sucesso! O conferente já pode iniciar a conferência."

                st.session_state.upload_key += 1
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar arquivo(s): {e}")

    st.divider()
    with st.expander("✏️ Renomear Carga Existente"):
        df_cargas_ren = carregar_dados("cargas")
        if not df_cargas_ren.empty and "id_carga" in df_cargas_ren.columns:
            lista_cargas_ren = df_cargas_ren["id_carga"].dropna().unique().tolist()
            if lista_cargas_ren:
                carga_antiga = st.selectbox("Selecione a carga que deseja renomear:", lista_cargas_ren, key="sel_renomear_carga")
                novo_nome_input = st.text_input(
                    "Novo código / nome da carga:",
                    placeholder="Digite o novo ID da carga...",
                    key="input_novo_nome_carga"
                )
                novo_nome_limpo = limpar_texto(novo_nome_input)

                if st.button("💾 Salvar Novo Nome da Carga", type="primary", disabled=not bool(novo_nome_limpo)):
                    if novo_nome_limpo == carga_antiga:
                        st.warning("⚠️ O novo nome é igual ao nome atual.")
                    elif novo_nome_limpo in lista_cargas_ren:
                        st.error(f"🚫 BLOQUEADO! Já existe uma carga cadastrada com o nome '{novo_nome_limpo}'.")
                    else:
                        df_cargas_ren["id_carga"] = df_cargas_ren["id_carga"].astype(object)
                        df_cargas_ren.loc[df_cargas_ren["id_carga"] == carga_antiga, "id_carga"] = novo_nome_limpo
                        salvar_dados(df_cargas_ren, "cargas")

                        df_bipes_ren = carregar_dados("bipes")
                        if not df_bipes_ren.empty and "id_carga" in df_bipes_ren.columns:
                            df_bipes_ren["id_carga"] = df_bipes_ren["id_carga"].astype(object)
                            df_bipes_ren.loc[df_bipes_ren["id_carga"] == carga_antiga, "id_carga"] = novo_nome_limpo
                            salvar_dados(df_bipes_ren, "bipes")

                        st.success(f"✅ Carga '{carga_antiga}' renomeada para '{novo_nome_limpo}' com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhuma carga cadastrada no momento.")
        else:
            st.info("Nenhuma carga cadastrada no momento.")

    if tem_permissao("🗑️ Excluir Cargas e Pedidos"):
     with st.expander("🗑️ Gerenciar / Excluir Carga Existente"):
        df_cargas_ger = carregar_dados("cargas")
        if not df_cargas_ger.empty and "id_carga" in df_cargas_ger.columns:
            lista_cargas_ex = df_cargas_ger["id_carga"].dropna().unique().tolist()
            if lista_cargas_ex:
                carga_para_excluir = st.selectbox("Selecione a carga que deseja apagar:", lista_cargas_ex, key="sel_excluir_carga")
                confirmar_exclusao = st.checkbox(f"Confirmo que desejo excluir permanentemente a carga '{carga_para_excluir}' e todos os seus bipes.")
                
                if st.button("🗑️ Excluir Carga Definitivamente", type="primary", disabled=not confirmar_exclusao):
                    df_cargas_restante = df_cargas_ger[df_cargas_ger["id_carga"] != carga_para_excluir]
                    if df_cargas_restante.empty:
                        df_cargas_restante = pd.DataFrame(columns=["id_carga", "codigo", "produto", "pedido_real", "bipado"])
                    salvar_dados(df_cargas_restante, "cargas")

                    df_bipes_ger = carregar_dados("bipes")
                    if not df_bipes_ger.empty and "id_carga" in df_bipes_ger.columns:
                        df_bipes_restante = df_bipes_ger[df_bipes_ger["id_carga"] != carga_para_excluir]
                        if df_bipes_restante.empty:
                            df_bipes_restante = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade", "conferente"])
                        salvar_dados(df_bipes_restante, "bipes")

                    st.success(f"✅ Carga '{carga_para_excluir}' excluída com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhuma carga cadastrada no momento.")
        else:
            st.info("Nenhuma carga cadastrada no momento.")

elif aba == "📋 Gestão de Pedidos":
    st.title("📋 Gestão de Pedidos: Conferidos x Pendentes")

    if st.button("🔄 Atualizar Status"):
        st.cache_data.clear()
        st.rerun()

    df_todas = carregar_dados("cargas")
    if df_todas.empty or "id_carga" not in df_todas.columns:
        st.info("Nenhuma carga cadastrada no sistema.")
        st.stop()

    df_todas["pedido_real"] = pd.to_numeric(df_todas["pedido_real"], errors="coerce").fillna(0).astype(int)
    df_todas["bipado"] = pd.to_numeric(df_todas["bipado"], errors="coerce").fillna(0).astype(int)

    df_bipes_datas = carregar_dados("bipes")
    ultimas_datas_carga = {}
    conferentes_por_carga = {}
    if not df_bipes_datas.empty and "id_carga" in df_bipes_datas.columns:
        for cid_b, grp_b in df_bipes_datas.groupby("id_carga", sort=False):
            if "data_hora" in grp_b.columns:
                datas_validas = [str(d).strip() for d in grp_b["data_hora"] if str(d).strip() and str(d).strip().upper() != "NAN"]
                if datas_validas:
                    ultimas_datas_carga[cid_b] = datas_validas[0].split()[0]
            if "conferente" in grp_b.columns:
                confs_validos = sorted(set(
                    limpar_texto(c) for c in grp_b["conferente"] if limpar_texto(c)
                ))
                if confs_validos:
                    conferentes_por_carga[cid_b] = ", ".join(confs_validos)

    lista_pendentes = list()
    lista_concluidas = list()

    df_plan_gp = carregar_dados("planejamento")
    mapa_validados_gp = {}
    mapa_nf_gp = {}
    if not df_plan_gp.empty:
        col_ped_gp = "Nº Pedido" if "Nº Pedido" in df_plan_gp.columns else ("id_carga" if "id_carga" in df_plan_gp.columns else None)
        if col_ped_gp:
            for _, r_p in df_plan_gp.iterrows():
                ped_p_str = str(r_p.get(col_ped_gp, "")).strip()
                val_str = str(r_p.get("validado", "")).strip()
                nf_str = str(r_p.get("Nota Fiscal", "")).strip()
                if val_str and val_str.lower() not in ("nan", "none", "null", "nao", "não"):
                    mapa_validados_gp[limpar_texto(ped_p_str)] = val_str
                if nf_str and nf_str.lower() not in ("nan", "none", "null", "-"):
                    mapa_nf_gp[ped_p_str] = nf_str
    for cid, grupo in df_todas.groupby("id_carga", sort=False):
        tot_ped = int(grupo["pedido_real"].sum())
        tot_bip = int(grupo["bipado"].sum())
        skus_ped = len(grupo[(grupo["pedido_real"] > 0) | (grupo["produto"].astype(str).str.contains(r"\[CORTADO:", regex=True))])
        falta = max(0, int((grupo["pedido_real"] - grupo["bipado"]).clip(lower=0).sum()))
        sobra = max(0, int((grupo["bipado"] - grupo["pedido_real"]).clip(lower=0).sum()))

        concluida_100 = verificar_carga_100_concluida(grupo)
        teve_corte = carga_possui_corte(grupo)
        selo_corte = " | ✂️ PEDIDO COM CORTE" if teve_corte else ""

        if concluida_100:
            data_conclusao = ultimas_datas_carga.get(cid, "Concluído via Corte" if teve_corte else "-")
            lista_concluidas.append({
                "Carga / Pedido": cid,
                "Nota Fiscal": next((nf_v for ped_k, nf_v in mapa_nf_gp.items() if limpar_texto(cid) == limpar_texto(ped_k) or bool(re.search(r"(?<!\d)" + re.escape(str(cid).strip()) + r"(?!\d)", ped_k))), "-"),
                "Qtd de SKUs": skus_ped,
                "Volumes Pedidos": tot_ped,
                "Volumes Bipados": tot_bip,
                "Conferido em": data_conclusao,
                "Conferido por": conferentes_por_carga.get(cid, "-"),
                "Lacre": obter_lacre_carga(grupo) or "-",
                "Situação": f"🟢 100% Conferida{selo_corte}",
                "Validação Final": f"✅ {mapa_validados_gp[limpar_texto(cid)]}" if limpar_texto(cid) in mapa_validados_gp else "⏳ Aguardando Auditoria"
            })
        else:
            if tot_bip == 0:
                situacao = f"🔴 Não Iniciada{selo_corte}"
            elif sobra > 0:
                situacao = f"⚠️ Em Conferência (Falta: {falta} | Excedente: {sobra}){selo_corte}"
            else:
                situacao = f"🟡 Em Conferência (Faltam {falta} un.){selo_corte}"

            lista_pendentes.append({
                "Carga / Pedido": cid,
                "Nota Fiscal": next((nf_v for ped_k, nf_v in mapa_nf_gp.items() if limpar_texto(cid) == limpar_texto(ped_k) or bool(re.search(r"(?<!\d)" + re.escape(str(cid).strip()) + r"(?!\d)", ped_k))), "-"),
                "Qtd de SKUs": skus_ped,
                "Volumes Pedidos": tot_ped,
                "Volumes Bipados": tot_bip,
                "Falta Bipar": falta,
                "Situação": situacao
            })

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Cargas", len(lista_pendentes) + len(lista_concluidas))
    m2.metric("⏳ Faltam Conferir", len(lista_pendentes))
    m3.metric("🟢 Conferidas (100%)", len(lista_concluidas))

    st.divider()

    st.subheader("⏳ Pedidos Aguardando Conferir")
    if lista_pendentes:
        st.dataframe(pd.DataFrame(lista_pendentes), use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Nenhuma carga pendente! Todas as cargas cadastradas já foram conferidas.")

    st.subheader("✅ Pedidos Conferidos (100% Concluídos)")
    if lista_concluidas:
        st.dataframe(pd.DataFrame(lista_concluidas), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma carga atingiu 100% de conclusão ainda.")

    st.divider()
    with st.expander("🔍 Consultar Itens e Quantidades de uma Carga"):
        lista_cargas_consulta = df_todas["id_carga"].unique().tolist()
        carga_detalhe = st.selectbox("Selecione a carga para visualizar o pedido:", lista_cargas_consulta, key="sel_detalhe_status")
        
        df_det = df_todas[df_todas["id_carga"] == carga_detalhe].copy()
        df_det = df_det[(df_det["pedido_real"] > 0) | (df_det["produto"].astype(str).str.contains(r"\[CORTADO:", regex=True))]

        linhas_pedido = list()
        itens_cortados_edicao = {}

        for _, r in df_det.iterrows():
            prod_raw = str(r["produto"])
            if "[CORTADO:" in prod_raw:
                desc_limpa = prod_raw.split(" [CORTADO:")[0].strip()
                trecho_corte = prod_raw.split("[CORTADO:")[-1].rstrip("]").strip()
                if "| Motivo:" in trecho_corte:
                    partes = trecho_corte.split("| Motivo:")
                    qtd_corte_str = partes[0].strip()
                    motivo_info = partes[1].strip()
                else:
                    qtd_corte_str = trecho_corte
                    motivo_info = ""

                try:
                    nums = [int(n.strip()) for n in qtd_corte_str.split("->")]
                    qtd_cortada_num = max(0, nums[0] - nums[1]) if len(nums) == 2 else qtd_corte_str
                except Exception:
                    qtd_cortada_num = qtd_corte_str

                corte_info = f"✂️ {qtd_cortada_num}"
                itens_cortados_edicao[f"{r['codigo']} - {desc_limpa} ({qtd_corte_str})"] = {
                    "codigo": r["codigo"],
                    "desc_limpa": desc_limpa,
                    "qtd_corte_str": qtd_corte_str,
                    "motivo_atual": motivo_info
                }
            else:
                desc_limpa = prod_raw
                corte_info = ""
                motivo_info = ""

            linhas_pedido.append({
                "SKU": r["codigo"],
                "Descrição": desc_limpa,
                "Quantidade": int(r["pedido_real"]),
                "Corte": corte_info,
                "Motivo do Corte": motivo_info
            })

        if linhas_pedido:
            st.dataframe(pd.DataFrame(linhas_pedido), use_container_width=True, hide_index=True)

            if itens_cortados_edicao and tem_permissao("✂️ Gerar e Editar Cortes"):
                st.markdown("---")
                st.markdown("**✏️ Editar Motivo do Corte**")
                item_edit_label = st.selectbox(
                    "Selecione o item cortado para alterar o motivo:",
                    list(itens_cortados_edicao.keys()),
                    key="sel_edit_motivo_corte"
                )
                dados_edit = itens_cortados_edicao[item_edit_label]
                novo_motivo_corte = st.text_input(
                    "Novo motivo / observação do corte:",
                    value=dados_edit["motivo_atual"],
                    placeholder="Digite o novo motivo do corte...",
                    key=f"input_edit_motivo_{carga_detalhe}_{dados_edit['codigo']}"
                )
                if st.button("💾 Salvar Novo Motivo do Corte", type="primary", key="btn_salvar_motivo_corte"):
                    df_banco_edit_corte = carregar_dados("cargas")
                    filtro_ed = (df_banco_edit_corte["id_carga"] == carga_detalhe) & (df_banco_edit_corte["codigo"].apply(limpar_texto) == limpar_texto(dados_edit["codigo"]))
                    if filtro_ed.any():
                        idx_ed = df_banco_edit_corte.index[filtro_ed][0]
                        motivo_novo_limpo = novo_motivo_corte.strip()
                        if motivo_novo_limpo:
                            nova_tag = f" [CORTADO: {dados_edit['qtd_corte_str']} | Motivo: {motivo_novo_limpo}]"
                        else:
                            nova_tag = f" [CORTADO: {dados_edit['qtd_corte_str']}]"
                        df_banco_edit_corte.at[idx_ed, "produto"] = dados_edit["desc_limpa"] + nova_tag
                        salvar_dados(df_banco_edit_corte, "cargas")
                        st.success("✅ Motivo do corte atualizado com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum item encontrado neste pedido.")

elif aba == "📦 Conferência dos Pedidos":
    st.title("📦 Conferência dos Pedidos")

    df_todas_cargas = carregar_dados("cargas")
    
    if df_todas_cargas.empty or "id_carga" not in df_todas_cargas.columns:
        st.warning("Nenhuma carga disponível no momento. Aguarde a liberação do administrativo.")
        st.stop()

    cargas_pendentes_conf = []
    for cid_check, grupo_check in df_todas_cargas.groupby("id_carga", sort=False):
        concluida_check = verificar_carga_100_concluida(grupo_check)
        lacre_check = obter_lacre_carga(grupo_check)
        if not concluida_check or not lacre_check:
            cargas_pendentes_conf.append(cid_check)

    if not cargas_pendentes_conf:
        st.success("🎉 **Parabéns! Todas as cargas importadas já foram 100% conferidas e lacradas!**")
        st.info("Quando o administrativo importar um novo pedido, ele aparecerá automaticamente aqui.")
        st.stop()

    carga_selecionada = st.selectbox("Selecione a Carga Pendente para Conferir:", cargas_pendentes_conf)
    df_plan_conf = carregar_dados("planejamento")
    if not df_plan_conf.empty and "Nº Pedido" in df_plan_conf.columns and "Notificação" in df_plan_conf.columns:
        df_plan_conf["Nº Pedido"] = df_plan_conf["Nº Pedido"].apply(limpar_texto)
        df_plan_conf["Notificação"] = df_plan_conf["Notificação"].astype(str).str.strip()
        login_conf_nt = st.session_state.get("login_usuario", "")
        nome_conf_nt = st.session_state.get("nome_usuario", "")
        carga_alvo_limpa = limpar_texto(carga_selecionada)

        def notif_conf_para_mim(row_p):
            ped_plan_txt = limpar_texto(row_p["Nº Pedido"])
            if not ped_plan_txt or not carga_alvo_limpa:
                return False
            if ped_plan_txt != carga_alvo_limpa and not re.search(rf"\b{re.escape(carga_alvo_limpa)}\b", ped_plan_txt):
                return False
            txt_nt = str(row_p["Notificação"]).strip()
            if not txt_nt:
                return False
            if "[PARA:" not in txt_nt:
                return True
            destino = txt_nt.split("[PARA:")[1].split("]")[0].strip()
            return destino in ("TODOS", login_conf_nt, nome_conf_nt)

        df_notifs_carga_conf = df_plan_conf[df_plan_conf.apply(notif_conf_para_mim, axis=1)]
        if not df_notifs_carga_conf.empty:
            with st.container(border=True):
                st.error(f"🔔 **ATENÇÃO NESTA CARGA ({carga_selecionada}):**")
                for idx_nc, row_nc in df_notifs_carga_conf.iterrows():
                    cc_txt, cc_btn = st.columns([4, 1], vertical_alignment="center")
                    msg_nc = re.sub(r"^\[PARA:\s*[^\]]+\]\s*", "", str(row_nc["Notificação"]).strip()).replace("(DE: ", "(")
                    cc_txt.markdown(
                        f"📌 <span style='color: #38BDF8; font-weight: bold;'>{msg_nc}</span>",
                        unsafe_allow_html=True
                    )
                    if cc_btn.button("✔️ Marcar como Lido", key=f"btn_ler_notif_conf_{idx_nc}", use_container_width=True):
                        df_plan_conf["Notificação"] = df_plan_conf["Notificação"].astype(object)
                        df_plan_conf.at[idx_nc, "Notificação"] = ""
                        salvar_dados(df_plan_conf[COLUNAS_PLANEJAMENTO], "planejamento")
                        st.toast("✔️ Notificação confirmada como lida!", icon="✔️")
                        st.rerun()
    df_carga_selecionada_atual = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada]
    if verificar_carga_100_concluida(df_carga_selecionada_atual):
        st.success("✅ Conferência realizada com sucesso!")
        lacre_atual_conf = obter_lacre_carga(df_carga_selecionada_atual)
        if lacre_atual_conf:
            st.info(f"🔒 **Lacre Registrado:** {lacre_atual_conf}")
        with st.container(border=True):
            c_lac1, c_lac2 = st.columns([3, 1], vertical_alignment="bottom")
            novo_lacre_conf = c_lac1.text_input(
                "🔒 Número do Lacre:",
                value="",
                placeholder="Digite ou bipe o número do lacre...",
                key=f"input_lacre_conf_{carga_selecionada}"
            )
            if c_lac2.button("💾 Salvar Lacre", type="primary", use_container_width=True, key=f"btn_lacre_conf_{carga_selecionada}"):
                if novo_lacre_conf.strip():
                    salvar_lacre_carga(carga_selecionada, novo_lacre_conf)
                    st.toast(f"🔒 Lacre '{limpar_texto(novo_lacre_conf)}' salvo com sucesso!", icon="🔒")
                    st.rerun()
                else:
                    st.error("⚠️ Digite o número do lacre antes de salvar.")


    if "etiqueta_validada" not in st.session_state:
        st.session_state.etiqueta_validada = ""
    if "erro_etiqueta" not in st.session_state:
        st.session_state.erro_etiqueta = ""
    if "pendencia_substituicao" not in st.session_state:
        st.session_state.pendencia_substituicao = None

    def concluir_gravacao(etiq_atual, sku_bipado, sku_destino, lote_limpo, qtd_final, obs_tipo):
        df_bipes_check = carregar_dados("bipes")
        if not df_bipes_check.empty and "etiqueta" in df_bipes_check.columns:
            dup = (df_bipes_check["id_carga"] == carga_selecionada) & (df_bipes_check["etiqueta"].apply(limpar_texto) == limpar_texto(etiq_atual))
            if dup.any():
                st.error(f"🚫 BLOQUEADO! A etiqueta '{etiq_atual}' já foi registrada!")
                st.stop()

        df_banco = carregar_dados("cargas")
        filtro = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_texto) == limpar_texto(sku_destino))

        if filtro.any():
            idx = df_banco.index[filtro][0]
            qtd_pedida_item = int(pd.to_numeric(df_banco.at[idx, "pedido_real"], errors="coerce") or 0)
            qtd_ja_bipada = int(pd.to_numeric(df_banco.at[idx, "bipado"], errors="coerce") or 0)

            if (qtd_ja_bipada + qtd_final) > qtd_pedida_item:
                st.error("🚫 BLOQUEADO! A quantidade informada ultrapassa o saldo permitido para este SKU neste pedido. Verifique com o administrativo.")
                st.stop()

            df_banco.at[idx, "bipado"] = qtd_ja_bipada + qtd_final
            if obs_tipo == "SUBSTITUIDO":
                desc_atual = str(df_banco.at[idx, "produto"])
                tag_sub = f" [Subst. p/ {sku_bipado}]"
                if tag_sub not in desc_atual:
                    df_banco.at[idx, "produto"] = desc_atual + tag_sub
        else:
            nova_linha = pd.DataFrame([{
                "id_carga": carga_selecionada,
                "codigo": limpar_texto(sku_bipado),
                "produto": "⚠️ ITEM EXTRA (Fora do Pedido)",
                "pedido_real": 0,
                "bipado": qtd_final
            }])
            df_banco = pd.concat([df_banco, nova_linha], ignore_index=True)

        salvar_dados(df_banco, "cargas")

        agora_br = datetime.now(FUSO_BR).strftime("%d/%m/%Y %H:%M:%S")
        novo_bipe = pd.DataFrame([{
            "data_hora": agora_br,
            "id_carga": carga_selecionada,
            "etiqueta": limpar_texto(etiq_atual),
            "codigo_bipado": limpar_texto(sku_bipado),
            "codigo_vinculado": limpar_texto(sku_destino),
            "tipo": obs_tipo,
            "lote": limpar_texto(lote_limpo),
            "quantidade": qtd_final,
            "conferente": st.session_state.nome_usuario
        }])
        df_bipes_atualizado = pd.concat([novo_bipe, df_bipes_check], ignore_index=True)
        salvar_dados(df_bipes_atualizado, "bipes")

        st.session_state.etiqueta_validada = ""
        st.session_state.pendencia_substituicao = None
        st.toast(f"✅ Etiqueta {etiq_atual} salva com sucesso! (+{qtd_final} un.)", icon="📦")
        st.rerun()

    def validar_etiqueta():
        etiq = st.session_state.input_etiqueta.strip()
        if not etiq:
            return

        df_bipes = carregar_dados("bipes")
        ja_existe = False

        if not df_bipes.empty and "etiqueta" in df_bipes.columns and "id_carga" in df_bipes.columns:
            filtro_dup = (df_bipes["id_carga"] == carga_selecionada) & (df_bipes["etiqueta"].apply(limpar_texto) == limpar_texto(etiq))
            if filtro_dup.any():
                ja_existe = True

        if ja_existe:
            st.session_state.erro_etiqueta = f"🚫 BLOQUEADO! A etiqueta '{etiq}' JÁ FOI BIPADA nesta carga. Não é possível prosseguir com ela."
            st.session_state.etiqueta_validada = ""
            st.session_state.input_etiqueta = ""
        else:
            st.session_state.erro_etiqueta = ""
            st.session_state.etiqueta_validada = etiq
            st.session_state.pendencia_substituicao = None
            st.session_state.input_etiqueta = ""

    if not st.session_state.etiqueta_validada:
        if st.session_state.erro_etiqueta:
            st.error(st.session_state.erro_etiqueta)

        st.text_input(
            "1º ETIQUETA (Bipe ou Digite):",
            key="input_etiqueta",
            on_change=validar_etiqueta,
            placeholder="Bipe ou digite o código da etiqueta..."
        )
        st.button("✔️ Verificar Etiqueta", on_click=validar_etiqueta, type="primary", use_container_width=True)

    else:
        st.success(f"✅ Etiqueta Liberada: **{st.session_state.etiqueta_validada}**")
        
        if st.button("🔄 Trocar / Cancelar esta Etiqueta"):
            st.session_state.etiqueta_validada = ""
            st.session_state.pendencia_substituicao = None
            st.rerun()

        st.divider()

        if st.session_state.pendencia_substituicao is not None:
            dados_sub = st.session_state.pendencia_substituicao
            st.warning(f"⚠️ **SKU Não Encontrado no Pedido:** O código **{dados_sub['sku']}** ({dados_sub['qtd']} un.) não consta na lista original.")
            st.write("O que você deseja fazer com este registro?")

            df_carga_atual = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada].copy()
            itens_originais = df_carga_atual[pd.to_numeric(df_carga_atual["pedido_real"]) > 0]

            if not itens_originais.empty:
                opcoes_dict = {
                    f"{limpar_texto(row['codigo'])} - {row['produto']}": limpar_texto(row['codigo'])
                    for _, row in itens_originais.iterrows()
                }
                escolha_label = st.selectbox("Se for substituição, selecione o item original:", list(opcoes_dict.keys()))
                sku_escolhido = opcoes_dict[escolha_label]

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔁 Confirmar Substituição", type="primary", use_container_width=True):
                        concluir_gravacao(
                            dados_sub["etiq"],
                            dados_sub["sku"],
                            sku_escolhido,
                            dados_sub["lote"],
                            dados_sub["qtd"],
                            "SUBSTITUIDO"
                        )
                with c2:
                    if st.button("➕ Registrar como Item Extra", use_container_width=True):
                        concluir_gravacao(
                            dados_sub["etiq"],
                            dados_sub["sku"],
                            dados_sub["sku"],
                            dados_sub["lote"],
                            dados_sub["qtd"],
                            "ITEM EXTRA"
                        )
            else:
                if st.button("➕ Registrar como Item Extra", type="primary", use_container_width=True):
                    concluir_gravacao(
                        dados_sub["etiq"],
                        dados_sub["sku"],
                        dados_sub["sku"],
                        dados_sub["lote"],
                        dados_sub["qtd"],
                        "ITEM EXTRA"
                    )

            if st.button("🔙 Voltar e Digitar SKU Correto", use_container_width=True):
                st.session_state.pendencia_substituicao = None
                st.rerun()

        else:
            with st.form("form_itens_etiqueta", clear_on_submit=True):
                sku_in = st.text_input(
                    "2º SKU / Código do Produto (Bipe ou Digite):", 
                    placeholder="Bipe ou digite o SKU..."
                )
                lote_in = st.text_input(
                    "3º LOTE (Bipe ou Digite):", 
                    placeholder="Bipe ou digite o Lote..."
                )
                qtd_in = st.text_input(
                    "4º QUANTIDADE (Bipe ou Digite):", 
                    value="",
                    placeholder="Bipe ou digite a quantidade..."
                )

                confirmar = st.form_submit_button("✅ SALVAR E FINALIZAR ETIQUETA", type="primary", use_container_width=True)

                if confirmar:
                    sku_limpo = sku_in.strip()
                    lote_limpo = lote_in.strip() if lote_in.strip() else "SEM LOTE"
                    qtd_texto = qtd_in.strip()
                    etiq_atual = st.session_state.etiqueta_validada

                    if not sku_limpo:
                        st.error("⚠️ O campo SKU é obrigatório!")
                    elif not qtd_texto.isdigit() or int(qtd_texto) <= 0:
                        st.error("⚠️ A Quantidade é obrigatória e precisa ser um número inteiro maior que zero!")
                    else:
                        qtd_final = int(qtd_texto)
                        df_banco = carregar_dados("cargas")
                        filtro_existe = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_texto) == limpar_texto(sku_limpo))

                        if filtro_existe.any():
                            concluir_gravacao(etiq_atual, sku_limpo, sku_limpo, lote_limpo, qtd_final, "NORMAL")
                        else:
                            st.session_state.pendencia_substituicao = {
                                "etiq": etiq_atual,
                                "sku": sku_limpo,
                                "lote": lote_limpo,
                                "qtd": qtd_final
                            }
                            st.rerun()

    st.divider()
    
    if st.button("↩️ Desfazer Última Etiqueta Registrada", use_container_width=True):
        df_bipes = carregar_dados("bipes")
        if not df_bipes.empty and "id_carga" in df_bipes.columns:
            bipes_carga = df_bipes[df_bipes["id_carga"] == carga_selecionada]
            if not bipes_carga.empty:
                ultimo_registro = bipes_carga.iloc[0]
                idx_bipe = bipes_carga.index[0]
                
                ult_etiq = str(ultimo_registro["etiqueta"])
                col_alvo = "codigo_vinculado" if "codigo_vinculado" in ultimo_registro else "codigo"
                ult_sku_alvo = limpar_texto(ultimo_registro[col_alvo])
                ult_qtd = int(ultimo_registro["quantidade"])

                df_banco = carregar_dados("cargas")
                filtro = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_texto) == ult_sku_alvo)

                if filtro.any():
                    idx_prod = df_banco.index[filtro][0]
                    nova_qtd = max(0, int(df_banco.at[idx_prod, "bipado"]) - ult_qtd)
                    df_banco.at[idx_prod, "bipado"] = nova_qtd
                    salvar_dados(df_banco, "cargas")

                df_bipes = df_bipes.drop(idx_bipe)
                if df_bipes.empty:
                    df_bipes = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade", "conferente"])
                salvar_dados(df_bipes, "bipes")
                st.warning(f"↩️ Etiqueta '{ult_etiq}' ({ult_qtd}x) foi estornada e liberada novamente!")
                st.rerun()

    st.subheader("Últimas Etiquetas Conferidas")
    df_bipes_vis = carregar_dados("bipes")
    if not df_bipes_vis.empty and "id_carga" in df_bipes_vis.columns:
        df_carga_bipes = df_bipes_vis[df_bipes_vis["id_carga"] == carga_selecionada].copy()
        if "quantidade" in df_carga_bipes.columns:
            df_carga_bipes["quantidade"] = pd.to_numeric(df_carga_bipes["quantidade"], errors="coerce").fillna(0).astype(int)

        if tem_permissao("👁️ Ver Conferência Completa (Supervisão)"):
            st.dataframe(df_carga_bipes, use_container_width=True, hide_index=True, height=385)
        else:
            st.dataframe(df_carga_bipes.head(10), use_container_width=True, hide_index=True)

elif aba == "📈 Painel de Acompanhamento":
    st.title("📈 Painel de Acompanhamento")

    df_todas_cargas = carregar_dados("cargas")
    if df_todas_cargas.empty:
        st.info("Nenhuma carga cadastrada.")
        st.stop()

    carga_selecionada = st.selectbox("Selecione a Carga:", df_todas_cargas["id_carga"].unique().tolist())
    
    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()

    df = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada].copy()
    df["pedido_real"] = pd.to_numeric(df["pedido_real"]).astype(int)
    df["bipado"] = pd.to_numeric(df["bipado"]).astype(int)
    df["Falta Bipar"] = df["pedido_real"] - df["bipado"]

    if carga_possui_corte(df):
        st.warning(f"✂️ **ATENÇÃO:** Este pedido possui **CORTE** registrado: **{extrair_detalhes_corte(df)}**")

    total_pedido = int(df["pedido_real"].sum())
    total_bipado = int(df["bipado"].sum())
    total_falta = max(0, df[df["Falta Bipar"] > 0]["Falta Bipar"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total do Pedido", total_pedido)
    c2.metric("Total Já Bipado", total_bipado)
    c3.metric("Falta Bipar", int(total_falta))

    progresso = min(1.0, total_bipado / total_pedido) if total_pedido > 0 else (1.0 if verificar_carga_100_concluida(df) else 0)
    st.progress(progresso, text=f"Progresso: {int(progresso * 100)}%")

    lacre_atual_painel = obter_lacre_carga(df)
    if verificar_carga_100_concluida(df):
        st.success("✅ Carga 100% concluída!")
        with st.container(border=True):
            cp_lac1, cp_lac2 = st.columns([3, 1], vertical_alignment="bottom")
            novo_lacre_painel = cp_lac1.text_input(
                "🔒 Número do Lacre da Carga:",
                value="",
                placeholder="Digite o número do lacre...",
                key=f"input_lacre_painel_{carga_selecionada}"
            )
            if cp_lac2.button("💾 Salvar Lacre", type="primary", use_container_width=True, key=f"btn_lacre_painel_{carga_selecionada}"):
                if novo_lacre_painel.strip():
                    salvar_lacre_carga(carga_selecionada, novo_lacre_painel)
                    st.success(f"🔒 Lacre '{limpar_texto(novo_lacre_painel)}' registrado com sucesso!")
                    st.rerun()
                else:
                    st.error("⚠️ Digite o número do lacre antes de salvar.")
    elif lacre_atual_painel:
        st.info(f"🔒 **Lacre Registrado:** {lacre_atual_painel}")

    st.subheader("⚠️ Itens Pendentes")
    pendentes = df[df["Falta Bipar"] > 0][["codigo", "produto", "pedido_real", "bipado", "Falta Bipar"]]
    if pendentes.empty:
        st.success("🎉 Todos os itens do pedido foram bipados!")
    else:
        st.dataframe(pendentes, use_container_width=True, hide_index=True)
        
        if tem_permissao("✂️ Gerar e Editar Cortes"):
            with st.expander("✂️ Administrativo: Gerar Corte em Item Pendente"):
                st.caption("Use esta opção quando um item do pedido foi cortado (totalmente ou parcialmente) e não será embarcado.")
                opcoes_corte = {
                    f"{row['codigo']} - {row['produto']} (Pedido atual: {row['pedido_real']} | Bipado: {row['bipado']})": row['codigo']
                    for _, row in pendentes.iterrows()
                }
                item_corte_label = st.selectbox("Selecione o item para registrar corte:", list(opcoes_corte.keys()))
                sku_corte = opcoes_corte[item_corte_label]
                
                linha_alvo_corte = df[df["codigo"] == sku_corte].iloc[0]
                qtd_atual_ped = int(linha_alvo_corte["pedido_real"])
                qtd_atual_bip = int(linha_alvo_corte["bipado"])
    
                nova_qtd_autorizada = st.number_input(
                    f"Nova quantidade final após o corte (mínimo {qtd_atual_bip}, máximo {qtd_atual_ped - 1}):",
                    min_value=qtd_atual_bip,
                    max_value=max(qtd_atual_bip, qtd_atual_ped - 1),
                    value=qtd_atual_bip,
                    step=1
                )
    
                motivo_corte = st.text_input(
                    "Motivo / Observação do Corte (Opcional):",
                    placeholder="Ex: Falta em estoque, avaria no lote, corte comercial..."
                )
    
                confirma_corte = st.checkbox(
                    f"Confirmo o corte do SKU '{sku_corte}' de {qtd_atual_ped} para {nova_qtd_autorizada} unidades (o pedido ficará marcado com corte)."
                )
    
                if st.button("✂️ Confirmar Corte no Pedido", type="primary", disabled=not confirma_corte):
                    df_banco_corte = carregar_dados("cargas")
                    filtro_corte = (df_banco_corte["id_carga"] == carga_selecionada) & (df_banco_corte["codigo"].apply(limpar_texto) == limpar_texto(sku_corte))
                    if filtro_corte.any():
                        idx_ct = df_banco_corte.index[filtro_corte][0]
                        df_banco_corte.at[idx_ct, "pedido_real"] = int(nova_qtd_autorizada)
                        desc_antiga = str(df_banco_corte.at[idx_ct, "produto"])
                        motivo_limpo = motivo_corte.strip()
                        if motivo_limpo:
                            tag_corte = f" [CORTADO: {qtd_atual_ped} -> {int(nova_qtd_autorizada)} | Motivo: {motivo_limpo}]"
                        else:
                            tag_corte = f" [CORTADO: {qtd_atual_ped} -> {int(nova_qtd_autorizada)}]"
                        if "[CORTADO:" not in desc_antiga:
                            df_banco_corte.at[idx_ct, "produto"] = desc_antiga + tag_corte
                        else:
                            base_nome = desc_antiga.split(" [CORTADO:")[0]
                            df_banco_corte.at[idx_ct, "produto"] = base_nome + tag_corte
    
                        salvar_dados(df_banco_corte, "cargas")
                        st.success(f"✂️ Corte registrado com sucesso! O pedido '{carga_selecionada}' agora está sinalizado com corte.")
                        st.rerun()

    sobras = df[df["Falta Bipar"] < 0].copy()
    if not sobras.empty:
        sobras["Qtd Excedente"] = sobras["bipado"] - sobras["pedido_real"]
        st.subheader("🚨 Itens Bipados a Mais / Fora do Pedido")
        st.dataframe(sobras[["codigo", "produto", "pedido_real", "bipado", "Qtd Excedente"]], use_container_width=True, hide_index=True)

elif aba == "✅ Auditoria e Ajustes":
    st.title("✅ Validação Final: Pedido x Bipado x Cliente x Lotes")

    df_todas_cargas = carregar_dados("cargas")
    if df_todas_cargas.empty:
        st.info("Nenhuma carga cadastrada.")
        st.stop()

    df_plan_aud = carregar_dados("planejamento")
    cargas_ja_validadas = set()
    if not df_plan_aud.empty and "id_carga" in df_plan_aud.columns and "validado" in df_plan_aud.columns:
        for _, r_pa in df_plan_aud.iterrows():
            v_str = str(r_pa.get("validado", "")).strip()
            if v_str and v_str.lower() not in ["nan", "none", "null", "nao", "não"]:
                cargas_ja_validadas.add(limpar_texto(r_pa["id_carga"]))

    todas_cargas_lista = df_todas_cargas["id_carga"].unique().tolist()
    mostrar_validadas = st.checkbox("👁️ Mostrar também cargas já validadas", value=False)
    cargas_disponiveis_aud = todas_cargas_lista if mostrar_validadas else [c for c in todas_cargas_lista if limpar_texto(c) not in cargas_ja_validadas]
    if cargas_disponiveis_aud and st.session_state.perfil_usuario == "ADMIN":
        with st.expander("⚙️ Baixa em Lote: Marcar Pedidos Selecionados como Auditados"):
            st.caption("Selecione os pedidos já expedidos que deseja marcar como auditados no histórico.")
            selecionar_todos_lote = st.checkbox("Selecionar todos os pedidos listados acima", value=False)
            cargas_lote_escolhidas = st.multiselect(
                "Pedidos para marcar como Auditado (Histórico):",
                options=cargas_disponiveis_aud,
                default=cargas_disponiveis_aud if selecionar_todos_lote else []
            )
            if st.button("✅ Marcar Selecionados como Auditado (Histórico)", disabled=len(cargas_lote_escolhidas) == 0):
                df_plan_lote = carregar_dados("planejamento")
                if df_plan_lote.empty or "id_carga" not in df_plan_lote.columns:
                    df_plan_lote = pd.DataFrame(columns=["id_carga", "cliente", "transportadora", "placa", "data_carregamento", "status", "observacoes", "validado"])
                if "validado" not in df_plan_lote.columns:
                    df_plan_lote["validado"] = ""
                df_plan_lote["validado"] = df_plan_lote["validado"].astype(object)

                existentes_plan = set(df_plan_lote["id_carga"].apply(limpar_texto).tolist())
                novas_linhas_lote = []

                for cid_ant in cargas_lote_escolhidas:
                    cid_l = limpar_texto(cid_ant)
                    if cid_l in existentes_plan:
                        df_plan_lote.loc[df_plan_lote["id_carga"].apply(limpar_texto) == cid_l, "validado"] = "Auditado (Histórico)"
                    else:
                        nl = {col: "" for col in df_plan_lote.columns}
                        nl["id_carga"] = cid_ant
                        nl["status"] = "🟢 Carregado / Liberado"
                        nl["validado"] = "Auditado (Histórico)"
                        novas_linhas_lote.append(nl)

                if novas_linhas_lote:
                    df_plan_lote = pd.concat([df_plan_lote, pd.DataFrame(novas_linhas_lote)], ignore_index=True)

                salvar_dados(df_plan_lote, "planejamento")
                st.cache_data.clear()
                st.success(f"🎉 {len(cargas_lote_escolhidas)} pedido(s) marcados como Auditado (Histórico)!")
                st.rerun()

    if not cargas_disponiveis_aud:
        st.success("🎉 Todas as cargas cadastradas já foram validadas!")
        st.stop()

    carga_selecionada = st.selectbox("Selecione a Carga para Auditar:", cargas_disponiveis_aud)  

    df_carga_aud = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada]
    if carga_possui_corte(df_carga_aud):
        st.warning(f"✂️ **OBSERVAÇÃO:** Este pedido foi gerado/finalizado **COM CORTE**: **{extrair_detalhes_corte(df_carga_aud)}**")
        
    if tem_permissao("↩️ Estornar Etiquetas e Corrigir Lotes"):
        with st.expander("🛠️ Administrativo: Corrigir Lote ou Estornar Etiqueta (Solicitar Rebipagem)"):
            df_bipes_adm = carregar_dados("bipes")
            if not df_bipes_adm.empty and "id_carga" in df_bipes_adm.columns:
                bipes_da_carga = df_bipes_adm[df_bipes_adm["id_carga"] == carga_selecionada].copy()
                
                if not bipes_da_carga.empty:
                    opcoes_etiq = {}
                    for idx_row, r in bipes_da_carga.iterrows():
                        etiq_str = limpar_texto(r["etiqueta"])
                        sku_str = limpar_texto(r["codigo_bipado"])
                        lote_str = limpar_texto(r["lote"])
                        qtd_str = str(int(float(r["quantidade"]))) if pd.notna(r["quantidade"]) else "0"
                        label = f"Etiqueta: {etiq_str} | SKU: {sku_str} | Lote atual: {lote_str} | Qtd: {qtd_str}"
                        opcoes_etiq[label] = idx_row
    
                    escolha_adm = st.selectbox("Selecione a etiqueta bipada para corrigir ou estornar:", list(opcoes_etiq.keys()))
                    idx_selecionado = opcoes_etiq[escolha_adm]
                    registro_alvo = df_bipes_adm.loc[idx_selecionado]
    
                    col_edit, col_estorno = st.columns(2)
    
                    with col_edit:
                        st.markdown("**1️⃣ Corrigir Lote e/ou Quantidade**")
                        qtd_atual_etiq = int(float(registro_alvo["quantidade"])) if pd.notna(registro_alvo["quantidade"]) else 1
                        c_ed_lote, c_ed_qtd = st.columns(2)
                        novo_lote_input = c_ed_lote.text_input(
                            "Lote correto:",
                            value=limpar_texto(registro_alvo["lote"]),
                            key="adm_novo_lote"
                        )
                        nova_qtd_input = c_ed_qtd.number_input(
                            "Quantidade correta:",
                            min_value=1,
                            value=max(1, qtd_atual_etiq),
                            step=1,
                            key="adm_nova_qtd"
                        )
                        if st.button("💾 Atualizar Lote e Quantidade", use_container_width=True):
                            if not novo_lote_input.strip():
                                st.error("⚠️ O lote não pode ficar em branco.")
                            else:
                                col_alvo_sku = "codigo_vinculado" if "codigo_vinculado" in registro_alvo else "codigo_bipado"
                                sku_alvo_ed = limpar_texto(registro_alvo[col_alvo_sku])
                                diff_qtd = int(nova_qtd_input) - qtd_atual_etiq
    
                                df_cargas_adm = carregar_dados("cargas")
                                filtro_c = (df_cargas_adm["id_carga"] == carga_selecionada) & (df_cargas_adm["codigo"].apply(limpar_texto) == sku_alvo_ed)
    
                                if filtro_c.any() and diff_qtd != 0:
                                    idx_c = df_cargas_adm.index[filtro_c][0]
                                    qtd_ped_sku = int(pd.to_numeric(df_cargas_adm.at[idx_c, "pedido_real"], errors="coerce") or 0)
                                    qtd_bip_sku = int(pd.to_numeric(df_cargas_adm.at[idx_c, "bipado"], errors="coerce") or 0)
                                    novo_total_bip = qtd_bip_sku + diff_qtd
    
                                    if qtd_ped_sku > 0 and novo_total_bip > qtd_ped_sku:
                                        st.error(f"🚫 BLOQUEADO! Essa alteração deixaria o SKU '{sku_alvo_ed}' com {novo_total_bip} un., ultrapassando o pedido ({qtd_ped_sku} un.).")
                                        st.stop()
    
                                    df_cargas_adm.at[idx_c, "bipado"] = max(0, novo_total_bip)
                                    salvar_dados(df_cargas_adm, "cargas")
    
                                df_bipes_adm["lote"] = df_bipes_adm["lote"].astype(object)
                                df_bipes_adm["quantidade"] = pd.to_numeric(df_bipes_adm["quantidade"], errors="coerce").fillna(0).astype(int)
                                df_bipes_adm.at[idx_selecionado, "lote"] = limpar_texto(novo_lote_input)
                                df_bipes_adm.at[idx_selecionado, "quantidade"] = int(nova_qtd_input)
                                salvar_dados(df_bipes_adm, "bipes")
    
                                if "relatorio_final" in st.session_state:
                                    del st.session_state.relatorio_final
                                st.success(f"✅ Etiqueta '{limpar_texto(registro_alvo['etiqueta'])}' atualizada (Lote: {limpar_texto(novo_lote_input)} | Qtd: {int(nova_qtd_input)})!")
                                st.rerun()

                    with col_estorno:
                        st.markdown("**2️⃣ Estornar Etiqueta (Solicitar Rebipagem)**")
                        st.caption("Remove o bipe, abate a quantidade e libera a etiqueta para o conferente bipar novamente.")
                        confirma_estorno_adm = st.checkbox(f"Confirmar estorno da etiqueta '{limpar_texto(registro_alvo['etiqueta'])}'", key="chk_estorno_adm")
                        if st.button("↩️ Estornar Etiqueta", type="primary", disabled=not confirma_estorno_adm, use_container_width=True):
                            col_alvo_sku = "codigo_vinculado" if "codigo_vinculado" in registro_alvo else "codigo_bipado"
                            sku_estornar = limpar_texto(registro_alvo[col_alvo_sku])
                            qtd_estornar = int(float(registro_alvo["quantidade"]))

                            df_cargas_adm = carregar_dados("cargas")
                            filtro_c = (df_cargas_adm["id_carga"] == carga_selecionada) & (df_cargas_adm["codigo"].apply(limpar_texto) == sku_estornar)
                            if filtro_c.any():
                                idx_c = df_cargas_adm.index[filtro_c][0]
                                df_cargas_adm.at[idx_c, "bipado"] = max(0, int(df_cargas_adm.at[idx_c, "bipado"]) - qtd_estornar)
                                salvar_dados(df_cargas_adm, "cargas")

                            df_bipes_adm = df_bipes_adm.drop(idx_selecionado)
                            if df_bipes_adm.empty:
                                df_bipes_adm = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade", "conferente"])
                            salvar_dados(df_bipes_adm, "bipes")

                            if "relatorio_final" in st.session_state:
                                del st.session_state.relatorio_final
                            st.warning(f"↩️ Etiqueta '{limpar_texto(registro_alvo['etiqueta'])}' estornada! O conferente já pode bipar novamente.")
                            st.rerun()
                else:
                    st.info("Nenhuma etiqueta bipada nesta carga ainda.")
            else:
                st.info("Nenhuma etiqueta bipada nesta carga ainda.")

    st.divider()
    arq_cliente = st.file_uploader("Suba o Excel/CSV enviado pelo cliente", type=["xlsx", "xls", "csv"])

    if arq_cliente:
        df_cli = pd.read_csv(arq_cliente, sep=None, engine="python", dtype=str) if arq_cliente.name.endswith(".csv") else pd.read_excel(arq_cliente, dtype=str)
        cols_cli = list(df_cli.columns)

        c1, c2, c3 = st.columns(3)
        with c1:
            c_cod = st.selectbox("Coluna do SKU / CÓDIGO (Cliente):", cols_cli)
        with c2:
            c_qtd = st.selectbox("Coluna da QUANTIDADE (Cliente):", cols_cli)
        with c3:
            c_lote = st.selectbox("Coluna do LOTE (Cliente):", ["(Não informar lote)"] + cols_cli)

        if st.button("⚖️ Gerar Validação Tripla + Lotes", type="primary", use_container_width=True):
            df_cli_prep = pd.DataFrame({
                "codigo": df_cli[c_cod].apply(limpar_texto),
                "informado_cliente": pd.to_numeric(df_cli[c_qtd], errors="coerce").fillna(0).astype(int),
                "lote_cli": df_cli[c_lote].apply(limpar_texto) if c_lote != "(Não informar lote)" else "N/I"
            })
            df_cli_prep = df_cli_prep[df_cli_prep["codigo"] != ""]

            base_cli_qtd = df_cli_prep.groupby("codigo", as_index=False)["informado_cliente"].sum()
            base_cli_lotes = df_cli_prep.groupby("codigo")["lote_cli"].apply(
                lambda x: ", ".join(sorted(set(v for v in x if v and v != "NAN")))
            ).reset_index().rename(columns={"lote_cli": "Lotes Cliente"})
            base_cli = pd.merge(base_cli_qtd, base_cli_lotes, on="codigo", how="left")

            df_bipes_all = carregar_dados("bipes")
            if not df_bipes_all.empty and "id_carga" in df_bipes_all.columns:
                bipes_carga = df_bipes_all[df_bipes_all["id_carga"] == carga_selecionada].copy()
                col_sku_bipe = "codigo_vinculado" if "codigo_vinculado" in bipes_carga.columns else "codigo"
                bipes_carga[col_sku_bipe] = bipes_carga[col_sku_bipe].apply(limpar_texto)
                bipes_carga["lote"] = bipes_carga["lote"].apply(limpar_texto)
                
                lotes_conf = bipes_carga.groupby(col_sku_bipe)["lote"].apply(
                    lambda x: ", ".join(sorted(set(v for v in x if v and v != "NAN")))
                ).reset_index().rename(columns={col_sku_bipe: "codigo", "lote": "Lotes Conferente"})
            else:
                lotes_conf = pd.DataFrame(columns=["codigo", "Lotes Conferente"])

            df_conferencia = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada].copy()
            df_conferencia["codigo"] = df_conferencia["codigo"].apply(limpar_texto)
            df_conferencia["pedido_real"] = pd.to_numeric(df_conferencia["pedido_real"]).astype(int)
            df_conferencia["bipado"] = pd.to_numeric(df_conferencia["bipado"]).astype(int)

            df_validacao = pd.merge(df_conferencia[["codigo", "produto", "pedido_real", "bipado"]], base_cli, on="codigo", how="outer")
            df_validacao = pd.merge(df_validacao, lotes_conf, on="codigo", how="left")

            df_validacao["produto"] = df_validacao["produto"].fillna("⚠️ ITEM APENAS NO ARQUIVO DO CLIENTE")
            df_validacao["pedido_real"] = df_validacao["pedido_real"].fillna(0).astype(int)
            df_validacao["bipado"] = df_validacao["bipado"].fillna(0).astype(int)
            df_validacao["informado_cliente"] = df_validacao["informado_cliente"].fillna(0).astype(int)
            df_validacao["Lotes Conferente"] = df_validacao["Lotes Conferente"].fillna("-")
            df_validacao["Lotes Cliente"] = df_validacao["Lotes Cliente"].fillna("-")

            def validar_linha(row):
                pedido = row["pedido_real"]
                bipado = row["bipado"]
                cliente = row["informado_cliente"]
                l_conf = row["Lotes Conferente"]
                l_cli = row["Lotes Cliente"]
                prod_str = str(row["produto"])
                item_cortado = "[CORTADO:" in prod_str

                lote_divergente = False
                if c_lote != "(Não informar lote)" and l_conf != "-" and l_cli != "-" and l_conf != l_cli:
                    lote_divergente = True

                tag_corte_status = " [✂️ ITEM COM CORTE]" if item_cortado else ""

                if pedido == bipado == cliente:
                    if lote_divergente:
                        return f"⚠️ QTD OK, MAS LOTE DIVERGENTE (Conferente x Cliente){tag_corte_status}"
                    return f"✅ CORRETO (100% Validado){tag_corte_status}"
                elif pedido == bipado and cliente != pedido:
                    return f"⚠️ ERRO NO ARQUIVO DO CLIENTE (Pedido e físico batem, cliente informou diferente){tag_corte_status}"
                elif pedido != cliente and bipado == cliente:
                    return f"⚠️ DIVERGÊNCIA NO PEDIDO (Bipado bate com cliente, mas difere do seu pedido){tag_corte_status}"
                elif pedido == cliente and bipado != cliente:
                    return f"❌ DIVERGÊNCIA FÍSICA (Cliente informou igual ao pedido, mas bipagem divergiu){tag_corte_status}"
                else:
                    return f"🚨 DIVERGÊNCIA GERAL (Os três números estão diferentes){tag_corte_status}"

            df_validacao["Dif. Pedido x Bipado"] = df_validacao["bipado"] - df_validacao["pedido_real"]
            df_validacao["Dif. Cliente x Bipado"] = df_validacao["bipado"] - df_validacao["informado_cliente"]
            df_validacao["Status Validação"] = df_validacao.apply(validar_linha, axis=1)

            st.session_state.relatorio_final = df_validacao

    if "relatorio_final" in st.session_state:
        df_res = st.session_state.relatorio_final
        st.divider()

        total_skus = len(df_res)
        ok_skus = len(df_res[df_res["Status Validação"].str.contains("✅")])
        erro_skus = total_skus - ok_skus

        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Produtos", total_skus)
        m2.metric("Produtos 100% Corretos", ok_skus)
        m3.metric("Produtos com Divergência", erro_skus)

        apenas_erros = st.checkbox("Mostrar apenas itens com divergência")
        df_exibir = df_res[~df_res["Status Validação"].str.contains("✅")] if apenas_erros else df_res

        st.dataframe(df_exibir, use_container_width=True, hide_index=True)

        df_bipes_rel = carregar_dados("bipes")
        df_bipes_carga = df_bipes_rel[df_bipes_rel["id_carga"] == carga_selecionada] if not df_bipes_rel.empty else pd.DataFrame()

        buffer_relatorio = io.BytesIO()
        with pd.ExcelWriter(buffer_relatorio, engine="openpyxl") as writer:
            df_res.to_excel(writer, index=False, sheet_name="Validacao_Final")
            if not df_bipes_carga.empty:
                df_bipes_carga.to_excel(writer, index=False, sheet_name="Etiquetas_e_Lotes")

        st.download_button(
            label="📥 Baixar Relatório Completo em Excel (.xlsx)",
            data=buffer_relatorio.getvalue(),
            file_name=f"validacao_{carga_selecionada}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.divider()
        ja_esta_validada = limpar_texto(carga_selecionada) in cargas_ja_validadas
        if ja_esta_validada:
            st.info(f"✅ Esta carga (**{carga_selecionada}**) já foi validada e liberada para expedição.")
        else:
            if erro_skus > 0:
                st.error(f"🚫 Validação bloqueada: existem **{erro_skus} produto(s) com divergência** no cruzamento acima. Corrija antes de liberar o pedido.")
            if st.button("✅ Validar Pedido e Liberar para Expedição", type="primary", use_container_width=True, disabled=(erro_skus > 0)):
                df_plan_salvar = carregar_dados("planejamento")
                agora_val = datetime.fromtimestamp(datetime.now().timestamp() - 3*3600).strftime("%d/%m/%Y %H:%M")
                carimbo_val = f"Validado por {st.session_state.nome_usuario} ({agora_val})"

                if df_plan_salvar.empty or "id_carga" not in df_plan_salvar.columns:
                    df_plan_salvar = pd.DataFrame(columns=["id_carga", "cliente", "transportadora", "placa", "data_carregamento", "status", "observacoes", "validado"])

                if "validado" not in df_plan_salvar.columns:
                    df_plan_salvar["validado"] = ""

                df_plan_salvar["validado"] = df_plan_salvar["validado"].astype(object)
                mask_p = df_plan_salvar["id_carga"].apply(limpar_texto) == limpar_texto(carga_selecionada)

                if mask_p.any():
                    df_plan_salvar.loc[mask_p, "validado"] = carimbo_val
                else:
                    nova_linha_p = {col: "" for col in df_plan_salvar.columns}
                    nova_linha_p["id_carga"] = carga_selecionada
                    nova_linha_p["status"] = "🟢 Carregado / Liberado"
                    nova_linha_p["validado"] = carimbo_val
                    df_plan_salvar = pd.concat([df_plan_salvar, pd.DataFrame([nova_linha_p])], ignore_index=True)

                salvar_dados(df_plan_salvar, "planejamento")
                st.cache_data.clear()
                st.success(f"🎉 Pedido **{carga_selecionada}** validado com sucesso e liberado para expedição!")
                st.rerun()
        
elif aba == "👥 Central de Usuários":
    st.title("👥 Central de Usuários e Permissões")
    st.caption("Gerencie logins, perfis, módulos liberados e travas de ações críticas da equipe.")

    df_usuarios = carregar_usuarios_sistema()

    u_m1, u_m2, u_m3 = st.columns(3)
    u_m1.metric("👥 Total de Usuários", len(df_usuarios))
    u_m2.metric("✅ Ativos", int((df_usuarios["ativo"].apply(limpar_texto) == "SIM").sum()))
    u_m3.metric("🔒 Inativos", int((df_usuarios["ativo"].apply(limpar_texto) != "SIM").sum()))

    st.divider()

    st.subheader("📋 Usuários Cadastrados")
    df_vis_users = df_usuarios[["login", "nome", "perfil", "modulos_liberados", "permissoes", "ativo"]].copy()
    st.dataframe(df_vis_users, use_container_width=True, hide_index=True)

    st.divider()

    with st.expander("➕ Cadastrar Novo Usuário", expanded=True):
        nu_foto = st.file_uploader("📷 Foto de Perfil (Opcional):", type=["png", "jpg", "jpeg"], key="nu_foto_upload")
        with st.form("form_novo_usuario", clear_on_submit=True):
            nu_c1, nu_c2, nu_c3, nu_c4 = st.columns(4)
            nu_nome = nu_c1.text_input("Nome Completo*:", placeholder="Ex: JOÃO SILVA")
            nu_login = nu_c2.text_input("Login de Acesso*:", placeholder="Ex: JOAO.SILVA")
            nu_senha = nu_c3.text_input("Senha Inicial*:", type="password", placeholder="Mínimo 4 caracteres")
            nu_perfil = nu_c4.selectbox("Perfil Base:", ["CONFERENTE", "AUXILIAR ADMINISTRATIVO", "ANALISTA", "SUPERVISOR", "GERENTE", "ADMIN"])
            
            nu_mods = st.multiselect(
                "📂 Módulos / Telas Liberadas:",
                TODOS_MODULOS_SISTEMA,
                default=["📦 Conferência dos Pedidos"]
            )
            nu_perms = st.multiselect(
                "🛡️ Permissões de Ações Críticas:",
                TODAS_PERMISSOES_CRITICAS,
                default=list()
            )

            if st.form_submit_button("💾 Criar Usuário", type="primary", use_container_width=True):

                login_novo = limpar_texto(nu_login).replace(" ", "")
                nome_novo = limpar_texto(nu_nome)
                if not login_novo or not nome_novo or len(nu_senha.strip()) < 4:
                    st.error("⚠️ Preencha Nome, Login e uma Senha com pelo menos 4 caracteres.")
                elif login_novo in df_usuarios["login"].apply(limpar_texto).values:
                    st.error(f"🚫 O login **'{login_novo}'** já está cadastrado!")
                else:
                    mods_salvar = TODOS_MODULOS_SISTEMA if nu_perfil == "ADMIN" else nu_mods
                    perms_salvar = TODAS_PERMISSOES_CRITICAS if nu_perfil == "ADMIN" else nu_perms
                    novo_u = pd.DataFrame([{
                        "login": login_novo,
                        "nome": nome_novo,
                        "senha": gerar_hash_senha(nu_senha),
                        "perfil": nu_perfil,
                        "modulos_liberados": " | ".join(mods_salvar),
                        "permissoes": " | ".join(perms_salvar),
                        "ativo": "SIM",
                        "foto_b64": processar_foto_avatar(nu_foto)
                    }])
                    df_u_final = pd.concat([df_usuarios, novo_u], ignore_index=True)
                    salvar_dados(df_u_final[COLUNAS_USUARIOS], "usuarios")
                    if nu_foto is not None:
                        ok_gh, msg_gh = salvar_foto_github(login_novo, nu_foto)
                        if not ok_gh:
                            st.warning(f"⚠️ Usuário criado, mas houve falha ao enviar a foto: {msg_gh}")
                    
                    st.success(f"✅ Usuário **{nome_novo}** (`{login_novo}`) criado com sucesso!")
                    st.rerun()

    with st.expander("✏️ Editar Permissões, Resetar Senha ou Bloquear Usuário"):
        opcoes_u = {
            f"{r['nome']} ({r['login']}) — Perfil: {r['perfil']} [{r['ativo']}]": idx
            for idx, r in df_usuarios.iterrows()
        }
        sel_u_label = st.selectbox("Selecione o usuário para editar:", list(opcoes_u.keys()), key="sel_edit_usuario")
        idx_u_edit = opcoes_u[sel_u_label]
        reg_u = df_usuarios.loc[idx_u_edit]

        mods_atuais = [m.strip() for m in str(reg_u["modulos_liberados"]).split("|") if m.strip() in TODOS_MODULOS_SISTEMA]
        perms_atuais = [p.strip() for p in str(reg_u["permissoes"]).split("|") if p.strip() in TODAS_PERMISSOES_CRITICAS]
        perfis_lista = ["CONFERENTE", "AUXILIAR ADMINISTRATIVO", "ANALISTA", "SUPERVISOR", "GERENTE", "ADMIN"]
        idx_perf = perfis_lista.index(limpar_texto(reg_u["perfil"])) if limpar_texto(reg_u["perfil"]) in perfis_lista else 0
        
        ed_foto = st.file_uploader("📷 Alterar Foto de Perfil (Opcional):", type=["png", "jpg", "jpeg"], key=f"ed_foto_{idx_u_edit}")
        with st.form("form_editar_usuario"):
            eu_c1, eu_c2, eu_c3, eu_c4 = st.columns(4)
            eu_nome = eu_c1.text_input("Nome Completo:", value=str(reg_u["nome"]))
            eu_perfil = eu_c2.selectbox("Perfil Base:", perfis_lista, index=idx_perf)
            eu_ativo = eu_c3.selectbox("Status de Acesso:", ["SIM", "NÃO"], index=0 if limpar_texto(reg_u["ativo"]) == "SIM" else 1)
            eu_nova_senha = eu_c4.text_input("Nova Senha (deixe vazio para manter):", type="password")

            eu_mods = st.multiselect("📂 Módulos / Telas Liberadas:", TODOS_MODULOS_SISTEMA, default=mods_atuais)
            eu_perms = st.multiselect("🛡️ Permissões de Ações Críticas:", TODAS_PERMISSOES_CRITICAS, default=perms_atuais)

            if st.form_submit_button("💾 Salvar Alterações do Usuário", type="primary", use_container_width=True):
                mods_ed = TODOS_MODULOS_SISTEMA if eu_perfil == "ADMIN" else eu_mods
                perms_ed = TODAS_PERMISSOES_CRITICAS if eu_perfil == "ADMIN" else eu_perms

                if limpar_texto(reg_u["login"]) == st.session_state.login_usuario:
                    st.session_state.nome_usuario = eu_nome.strip().upper()
                    st.session_state.perfil_usuario = eu_perfil                

                df_usuarios["nome"] = df_usuarios["nome"].astype(object)
                df_usuarios["perfil"] = df_usuarios["perfil"].astype(object)
                df_usuarios["ativo"] = df_usuarios["ativo"].astype(object)
                df_usuarios["modulos_liberados"] = df_usuarios["modulos_liberados"].astype(object)
                df_usuarios["permissoes"] = df_usuarios["permissoes"].astype(object)

                df_usuarios.at[idx_u_edit, "nome"] = limpar_texto(eu_nome)
                df_usuarios.at[idx_u_edit, "perfil"] = eu_perfil
                df_usuarios.at[idx_u_edit, "ativo"] = eu_ativo
                df_usuarios.at[idx_u_edit, "modulos_liberados"] = " | ".join(mods_ed)
                df_usuarios.at[idx_u_edit, "permissoes"] = " | ".join(perms_ed)
                if ed_foto is not None:
                    ok_gh, msg_gh = salvar_foto_github(reg_u["login"], ed_foto)
                    if not ok_gh:
                        st.warning(f"⚠️ Dados salvos, mas houve falha ao enviar a foto: {msg_gh}")                

                if eu_nova_senha.strip():
                    if len(eu_nova_senha.strip()) < 4:
                        st.error("⚠️ A nova senha deve ter pelo menos 4 caracteres.")
                        st.stop()
                    df_usuarios["senha"] = df_usuarios["senha"].astype(object)
                    df_usuarios.at[idx_u_edit, "senha"] = gerar_hash_senha(eu_nova_senha)

                salvar_dados(df_usuarios[COLUNAS_USUARIOS], "usuarios")
                st.cache_data.clear()
                st.success(f"✅ Permissões e dados de **{limpar_texto(eu_nome)}** atualizados com sucesso!")
                st.rerun()
