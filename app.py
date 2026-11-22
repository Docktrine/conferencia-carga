import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os
import base64
import unicodedata
import re
import math
import time
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import requests

ARQUIVO_LOGO = next((f for f in ["logo_grano.png", "logo_grano.jpg", "logo_grano.jpeg"] if os.path.exists(f)), None)

st.set_page_config(
    page_title="WMS Grano — Inteligência Logística",
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
    section[data-testid="stSidebar"] div[data-baseweb="input"] button svg * {
        fill: #141A16 !important;
        stroke: #141A16 !important;
        color: #141A16 !important;
        opacity: 1 !important;
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
    /* === TABELAS SOFISTICADAS ESTILO ERP === */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(27, 94, 32, 0.45) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06) !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #1F2922 !important;
        color: #E6E1D6 !important;
        font-weight: 700 !important;
        font-size: 0.80rem !important;
        letter-spacing: 0.03em !important;
        border-bottom: 2px solid #4CAF50 !important;
    }
    [data-testid="stDataFrame"] [role="columnheader"] * {
        color: #E6E1D6 !important;
    }
    [data-testid="stDataFrame"] [role="gridcell"] {
        font-size: 0.84rem !important;
        border-bottom: 1px solid rgba(27, 94, 32, 0.12) !important;
    }
    [data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] {
        background-color: rgba(76, 175, 80, 0.10) !important;
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

def _calcular_pascoa(ano):
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(ano, mes, dia).date()

@st.cache_data(ttl=300, show_spinner=False)
def obter_feriados_sistema():
    feriados = set()
    ano_base = datetime.now().year
    for y in (ano_base - 1, ano_base, ano_base + 1, ano_base + 2):
        for m_f, d_f in ((1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)):
            feriados.add(datetime(y, m_f, d_f).date())
        pascoa = _calcular_pascoa(y)
        feriados.add((pd.Timestamp(pascoa) - pd.Timedelta(days=48)).date())
        feriados.add((pd.Timestamp(pascoa) - pd.Timedelta(days=47)).date())
        feriados.add((pd.Timestamp(pascoa) - pd.Timedelta(days=2)).date())
        feriados.add((pd.Timestamp(pascoa) + pd.Timedelta(days=60)).date())
    try:
        df_fer = _ler_planilha_com_cache("feriados")
        if df_fer is not None and not df_fer.empty:
            for col_f in df_fer.columns:
                if "DATA" in limpar_texto(col_f):
                    for v_f in df_fer[col_f].dropna():
                        dt_f = pd.to_datetime(str(v_f).strip(), dayfirst=True, errors="coerce")
                        if pd.notna(dt_f):
                            feriados.add(dt_f.date())
                    break
    except Exception:
        pass
    return feriados

def subtrair_dias_uteis(dt_alvo, qtd_dias, feriados_set):
    if pd.isna(dt_alvo):
        return pd.NaT
    d = dt_alvo.date() if hasattr(dt_alvo, "date") else dt_alvo
    passos = int(math.ceil(max(0.0, float(qtd_dias))))
    while passos > 0:
        d = (pd.Timestamp(d) - pd.Timedelta(days=1)).date()
        if d.weekday() < 5 and d not in feriados_set:
            passos -= 1
    while d.weekday() >= 5 or d in feriados_set:
        d = (pd.Timestamp(d) - pd.Timedelta(days=1)).date()
    return pd.Timestamp(d)

def contar_dias_uteis_entre(dt_inicio, dt_fim, feriados_set):
    if pd.isna(dt_inicio) or pd.isna(dt_fim):
        return 0
    d1 = dt_inicio.date() if hasattr(dt_inicio, "date") else dt_inicio
    d2 = dt_fim.date() if hasattr(dt_fim, "date") else dt_fim
    if d1 == d2:
        return 0
    sinal = 1 if d2 > d1 else -1
    atual, alvo = (d1, d2) if d2 > d1 else (d2, d1)
    uteis = 0
    while atual < alvo:
        atual = (pd.Timestamp(atual) + pd.Timedelta(days=1)).date()
        if atual.weekday() < 5 and atual not in feriados_set:
            uteis += 1
    return uteis * sinal

@st.cache_data(ttl=900, show_spinner=False)
def obter_mapa_lead_time():
    df_lt = carregar_dados("lead time")
    mapa = {}
    if df_lt is not None and not df_lt.empty:
        col_uf, col_cid, col_dias = None, None, None
        for c in df_lt.columns:
            cl = limpar_texto(c)
            if not col_uf and cl in ("ESTADO", "UF"):
                col_uf = c
            elif not col_cid and cl in ("CIDADE", "MUNICIPIO"):
                col_cid = c
            elif not col_dias and ("DIAS" in cl or "LEAD" in cl or "PRAZO" in cl):
                col_dias = c
        if col_uf and col_cid and col_dias:
            for _, r in df_lt.iterrows():
                u_k = limpar_texto(r[col_uf])
                c_k = limpar_texto(r[col_cid])
                try:
                    mapa[(u_k, c_k)] = float(str(r[col_dias]).strip().replace(",", "."))
                except Exception:
                    pass
    return mapa

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
    "Veículo compartilhado", "Data da entrega", "Observação", "Status", "Notificação", "Nota Fiscal", "id_carga", "validado"
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
@st.cache_data(ttl=600, show_spinner=False)    
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

@st.cache_data(ttl=900, show_spinner=False)
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
    if df is None or df.empty:
        st.warning(f"⚠️ Operação de gravação bloqueada na aba '{aba}' para proteger os dados existentes contra sobrescrita vazia.")
        return
    df_padronizado = padronizar_df_maiusculo(df)
    if df_padronizado.empty:
        return
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
                        <p style="color: #1B5E20; font-weight: 700; font-size: 0.85rem; margin: 2px 0 4px 0;">v2.0 — Inteligência Logística</p>
                        <p style="color: gray; margin-top: 2px; font-size: 0.82rem;">Acesso Restrito — Identifique-se para continuar</p>
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
                            st.session_state.aba_ativa = "🏠 Início" if len(mods) > 1 else (mods.pop(0) if mods else "")
                            st.session_state.abas_abertas = ["🏠 Início"] if len(mods) > 1 else [st.session_state.aba_ativa]
                            raw_foto = str(u_row.get("foto_b64", "")).strip()
                            if raw_foto.startswith("IMG_"):
                               raw_foto = raw_foto[4:]
                            st.session_state.foto_usuario = "" if raw_foto.lower() in ["", "nan", "none", "null"] else raw_foto
                            st.rerun()
        logo_bau_svg = (
            f'<image href="data:{LOGO_MIME};base64,{LOGO_B64}" x="81" y="54" width="24" height="24" preserveAspectRatio="xMidYMid slice" clip-path="url(#clipLogoBau)"/>'
            if LOGO_B64 else
            '<text x="93" y="69" text-anchor="middle" font-family="sans-serif" font-size="8.5" font-weight="800" fill="#1B5E20">GRANO</text>'
        )
        components.html(
            """
            <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
            @keyframes viagemCarretaGrano {
                0% { transform: translateX(-185px); }
                40% { transform: translateX(285px); }
                50% { transform: translateX(285px); }
                82% { transform: translateX(565px); }
                90% { transform: translateX(565px); }
                100% { transform: translateX(835px); }
            }
            @keyframes suspensaoCarreta {
                0%, 100% { transform: translateY(0px); }
                25% { transform: translateY(-1.1px); }
                50% { transform: translateY(0.5px); }
                75% { transform: translateY(-0.9px); }
            }
            @keyframes fumoEscapamento {
                0% { transform: translate(0, 0) scale(0.5); opacity: 0.75; }
                100% { transform: translate(-20px, -12px) scale(1.6); opacity: 0; }
            }
            @keyframes brilhoDocaCD {
                0%, 36%, 54%, 100% { fill: #D5D0C5; }
                41%, 49% { fill: #C8E6C9; }
            }
            @keyframes checkEntregaLoja {
                0%, 80%, 100% { transform: scale(0); opacity: 0; }
                84%, 91% { transform: scale(1.1); opacity: 1; }
            }
            @keyframes chuvaCaindo {
                0% { transform: translate(16px, -25px); opacity: 0; }
                15% { opacity: 0.45; }
                85% { opacity: 0.45; }
                100% { transform: translate(-24px, 118px); opacity: 0; }
            }
            @keyframes respingoAsfalto {
                0%, 70%, 100% { transform: scale(0.2); opacity: 0; }
                82% { transform: scale(1.1); opacity: 0.45; }
            }
            @keyframes limpadorParabrisa {
                0%, 100% { transform: rotate(0deg); }
                50% { transform: rotate(-38deg); }
            }
            .rota-wrap {
                width: 100%;
                max-width: 880px;
                margin: 14px auto 0 auto;
                height: 132px;
                position: relative;
                overflow: hidden;
            }
            .carreta-grupo { animation: viagemCarretaGrano 11.5s ease-in-out infinite; }
            .carreta-carroceria { animation: suspensaoCarreta 0.45s ease-in-out infinite; }
            .limpador-anim { transform-box: fill-box; transform-origin: bottom right; animation: limpadorParabrisa 0.7s ease-in-out infinite; }
            .fumo-1 { transform-box: fill-box; transform-origin: center; animation: fumoEscapamento 0.9s ease-out infinite; }
            .fumo-2 { transform-box: fill-box; transform-origin: center; animation: fumoEscapamento 0.9s ease-out 0.45s infinite; }
            .doca-cd-luz { animation: brilhoDocaCD 11.5s ease-in-out infinite; }
            .badge-entregue { transform-box: fill-box; transform-origin: center; animation: checkEntregaLoja 11.5s ease-out infinite; }
            .gota-chuva-1 { animation: chuvaCaindo 0.85s linear infinite; }
            .gota-chuva-2 { animation: chuvaCaindo 0.95s linear 0.25s infinite; }
            .gota-chuva-3 { animation: chuvaCaindo 0.80s linear 0.50s infinite; }
            .gota-chuva-4 { animation: chuvaCaindo 0.90s linear 0.70s infinite; }
            .respingo-1 { transform-box: fill-box; transform-origin: center; animation: respingoAsfalto 0.85s ease-out infinite; }
            .respingo-2 { transform-box: fill-box; transform-origin: center; animation: respingoAsfalto 0.95s ease-out 0.35s infinite; }
            </style>

            <div class="rota-wrap">
                <svg width="100%" height="132" viewBox="0 0 880 132" fill="none" xmlns="http://w3.org">
                    <defs>
                        <linearGradient id="feixeFarol" x1="0%" y1="50%" x2="100%" y2="50%">
                            <stop offset="0%" stop-color="#C8E6C9" stop-opacity="0.82"/>
                            <stop offset="100%" stop-color="#C8E6C9" stop-opacity="0"/>
                        </linearGradient>
                    </defs>

                    <!-- Estrada / Asfalto -->
                    <line x1="0" y1="110" x2="880" y2="110" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <line x1="0" y1="117" x2="880" y2="117" stroke="#141A16" stroke-width="1.2" stroke-dasharray="7 9" opacity="0.45"/>

                    <!-- 1. CENTRO DE DISTRIBUIÇÃO GRANO (Centro) -->
                    <g>
                        <ellipse cx="425" cy="110" rx="84" ry="3.4" fill="#141A16" opacity="0.16"/>
                        <rect x="349" y="68" width="28" height="42" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7" stroke-linejoin="round"/>
                        <rect x="354" y="74" width="8" height="7" rx="1" fill="#E8F5E9" stroke="#141A16" stroke-width="1.1"/>
                        <rect x="365" y="74" width="8" height="7" rx="1" fill="#E8F5E9" stroke="#141A16" stroke-width="1.1"/>
                        <rect x="358" y="90" width="10" height="20" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3"/>

                        <path d="M377 110 V54 L431 32 L485 54 V110 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <polygon points="378,56 431,35 484,56 484,61 431,40 378,61" fill="#D5D0C5"/>
                        <path d="M371 57 L431 30 L491 57" stroke="#1B5E20" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
                        <rect x="418" y="26" width="26" height="5" rx="1.5" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3"/>

                        <rect x="405" y="45" width="52" height="11" rx="2" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                        <text x="431" y="52.6" text-anchor="middle" font-family="sans-serif" font-size="6.4" font-weight="800" fill="#FFFFFF" letter-spacing="0.5">CD GRANO</text>

                        <rect x="381" y="102" width="100" height="8" fill="#D5D0C5" stroke="#141A16" stroke-width="1.4"/>

                        <rect class="doca-cd-luz" x="387" y="64" width="26" height="38" rx="1" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="387" y1="71" x2="413" y2="71" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="387" y1="78" x2="413" y2="78" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="385" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="412" y="102" width="3" height="8" fill="#141A16"/>

                        <rect x="419" y="64" width="26" height="38" rx="1" fill="#DDD8CE" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="419" y1="71" x2="445" y2="71" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="419" y1="78" x2="445" y2="78" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="417" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="444" y="102" width="3" height="8" fill="#141A16"/>

                        <rect x="451" y="64" width="26" height="38" rx="1" fill="#DDD8CE" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="451" y1="71" x2="477" y2="71" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="451" y1="78" x2="477" y2="78" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="449" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="476" y="102" width="3" height="8" fill="#141A16"/>

                        <rect x="489" y="96" width="10" height="6" fill="#C8E6C9" stroke="#141A16" stroke-width="1.2"/>
                        <line x1="488" y1="103" x2="500" y2="103" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="506" y1="110" x2="506" y2="92" stroke="#141A16" stroke-width="1.6"/>
                        <circle cx="506" cy="87" r="7" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5"/>
                    </g>

                    <!-- 2. SUPERMERCADO / CLIENTE -->
                    <g>
                        <ellipse cx="732" cy="110" rx="58" ry="3.2" fill="#141A16" opacity="0.16"/>

                        <rect x="690" y="46" width="28" height="64" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <rect x="693" y="42" width="22" height="5" rx="1" fill="#1B5E20"/>
                        <rect x="695" y="80" width="18" height="30" fill="#E8F5E9" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="704" y1="80" x2="704" y2="110" stroke="#141A16" stroke-width="1.4"/>
                        <rect x="696" y="53" width="16" height="18" rx="1" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3"/>

                        <rect x="718" y="58" width="60" height="52" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <rect x="723" y="49" width="50" height="10" rx="2" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.5"/>
                        <text x="748" y="56.2" text-anchor="middle" font-family="sans-serif" font-size="6.2" font-weight="800" fill="#1B5E20" letter-spacing="0.4">MERCADO</text>

                        <path d="M717 59 H781 L777 67 H717 Z" fill="#A5D6A7" stroke="#141A16" stroke-width="1.5" stroke-linejoin="round"/>
                        <line x1="731" y1="59" x2="731" y2="67" stroke="#1B5E20" stroke-width="1.5"/>
                        <line x1="746" y1="59" x2="746" y2="67" stroke="#1B5E20" stroke-width="1.5"/>
                        <line x1="761" y1="59" x2="761" y2="67" stroke="#1B5E20" stroke-width="1.5"/>

                        <rect x="726" y="76" width="44" height="22" rx="1.5" fill="#E8F5E9" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="730" y1="84" x2="766" y2="84" stroke="#4CAF50" stroke-width="1.3" opacity="0.65"/>
                        <line x1="730" y1="91" x2="766" y2="91" stroke="#4CAF50" stroke-width="1.3" opacity="0.65"/>
                        <line x1="731" y1="79" x2="738" y2="89" stroke="#FFFFFF" stroke-width="1.4" stroke-linecap="round"/>

                        <g class="badge-entregue">
                            <circle cx="734" cy="28" r="10" fill="#1B5E20" stroke="#141A16" stroke-width="1.5"/>
                            <path d="M729.5 28 L733 31.5 L739.5 25" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </g>
                    </g>

                    <!-- FUNDO ESCURO DOS TÚNEIS (Camada traseira) -->
                    <path d="M0 110 V56 H24 C36 56 44 65 44 77 V110 Z" fill="#1F2922"/>
                    <path d="M880 110 V56 H856 C844 56 836 65 836 77 V110 Z" fill="#1F2922"/>

                    <!-- 3. CARRETA BAÚ REFRIGERADA GRANO (Passa por dentro dos túneis) -->
                    <g class="carreta-grupo">
                        <ellipse cx="115" cy="110" rx="64" ry="3" fill="#141A16" opacity="0.20"/>

                        <circle class="fumo-1" cx="144" cy="63" r="2.6" fill="#8A928C"/>
                        <circle class="fumo-2" cx="141" cy="60" r="2.1" fill="#8A928C"/>

                        <g class="carreta-carroceria">
                            <polygon points="178,94 216,86 216,103" fill="url(#feixeFarol)"/>

                            <rect x="50" y="59" width="92" height="39" rx="2.5" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8"/>
                            <rect x="51" y="93" width="90" height="4" fill="#D5D0C5"/>
                            <rect x="136" y="61" width="6" height="13" rx="1" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3"/>

                            <line x1="56" y1="75" x2="80" y2="75" stroke="#1B5E20" stroke-width="2.2" stroke-linecap="round"/>
                            <line x1="112" y1="75" x2="132" y2="75" stroke="#1B5E20" stroke-width="2.2" stroke-linecap="round"/>
                            <line x1="56" y1="80" x2="77" y2="80" stroke="#4CAF50" stroke-width="1.3" stroke-linecap="round"/>
                            <line x1="115" y1="80" x2="132" y2="80" stroke="#4CAF50" stroke-width="1.3" stroke-linecap="round"/>

                            <circle cx="96" cy="76" r="11.5" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.5"/>
                            <path d="M101.5 72.5 C100.2 70.6 98.2 69.8 95.8 69.8 C91.8 69.8 89 72.6 89 76.2 C89 79.8 91.8 82.5 96 82.5 C99.6 82.5 102 80.3 102 77.2 H96.5" stroke="#1B5E20" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>

                            <rect x="134" y="98" width="16" height="4" rx="1" fill="#141A16"/>
                            <rect x="122" y="99" width="53" height="4" rx="1" fill="#141A16"/>

                            <path d="M147 99 V65 L144 63" stroke="#141A16" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M150 72 L161 66 V72 Z" fill="#C8E6C9" stroke="#141A16" stroke-width="1.4" stroke-linejoin="round"/>

                            <path d="M150 72 H165 L177 85 V99 H150 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                            <path d="M161 74.5 H164.5 L173.5 84.5 H161 Z" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                            <line class="limpador-anim" x1="173" y1="84" x2="167" y2="77" stroke="#141A16" stroke-width="1.2" stroke-linecap="round"/>
                            <rect x="153" y="75" width="5.5" height="9" rx="0.8" fill="#E8F5E9" stroke="#141A16" stroke-width="1.1"/>
                            <line x1="160" y1="76" x2="158" y2="82" stroke="#141A16" stroke-width="1.4" stroke-linecap="round"/>
                            <line x1="177" y1="89" x2="177" y2="96" stroke="#1B5E20" stroke-width="2" stroke-linecap="round"/>
                            <circle cx="177" cy="94" r="1.9" fill="#1B5E20"/>
                        </g>

                        <g>
                            <circle cx="66" cy="104.5" r="5.2" fill="#141A16"/>
                            <circle cx="66" cy="104.5" r="2.1" fill="#EAE7E0"/>
                            <circle cx="79" cy="104.5" r="5.2" fill="#141A16"/>
                            <circle cx="79" cy="104.5" r="2.1" fill="#EAE7E0"/>

                            <circle cx="129" cy="104.5" r="5.2" fill="#141A16"/>
                            <circle cx="129" cy="104.5" r="2.1" fill="#EAE7E0"/>
                            <circle cx="142" cy="104.5" r="5.2" fill="#141A16"/>
                            <circle cx="142" cy="104.5" r="2.1" fill="#EAE7E0"/>

                            <circle cx="166" cy="104.5" r="5.2" fill="#141A16"/>
                            <circle cx="166" cy="104.5" r="2.1" fill="#EAE7E0"/>
                        </g>
                    </g>

                    <!-- MOLDURA FRONTAL DOS TÚNEIS COM MÁSCARA SÓLIDA -->
                    <!-- Túnel Esquerdo (Origem) -->
                    <g>
                        <!-- Máscara sólida na cor do fundo da tela para esconder a carreta antes da boca -->
                        <path d="M0 28 H64 V112 H44 V77 C44 65 36 56 24 56 H0 Z" fill="#C9C5BA"/>
                        <!-- Encosta/Morro verde -->
                        <path d="M0 32 C26 32 48 48 56 76 L62 110 H44 V77 C44 65 36 56 24 56 H0 Z" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                        <!-- Portal de concreto do Túnel -->
                        <path d="M0 48 H26 C41 48 51 59 51 75 V110 H43 V76 C43 64 35 56 24 56 H0 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <!-- Placa de sinalização verde -->
                        <rect x="6" y="41" width="22" height="6" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.1"/>
                    </g>

                    <!-- Túnel Direito (Destino) -->
                    <g>
                        <!-- Máscara sólida na cor do fundo da tela para esconder a carreta após entrar -->
                        <path d="M880 28 H816 V112 H836 V77 C836 65 844 56 856 56 H880 Z" fill="#C9C5BA"/>
                        <!-- Encosta/Morro verde -->
                        <path d="M880 32 C854 32 832 48 824 76 L818 110 H836 V77 C836 65 844 56 856 56 H880 Z" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                        <!-- Portal de concreto do Túnel -->
                        <path d="M880 48 H854 C839 48 829 59 829 75 V110 H837 V76 C837 64 845 56 856 56 H880 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <!-- Placa de sinalização verde -->
                        <rect x="852" y="41" width="22" height="6" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.1"/>
                    </g>

                    <!-- 4. CAMADA DE CHUVA SUAVE E RESPINGOS -->
                    <g stroke="#1B5E20" stroke-width="1.1" stroke-linecap="round" opacity="0.55">
                        <g class="gota-chuva-1">
                            <line x1="85" y1="0" x2="81" y2="11"/><line x1="185" y1="8" x2="181" y2="19"/>
                            <line x1="295" y1="2" x2="291" y2="13"/><line x1="415" y1="10" x2="411" y2="21"/>
                            <line x1="535" y1="4" x2="531" y2="15"/><line x1="655" y1="12" x2="651" y2="23"/>
                            <line x1="775" y1="3" x2="771" y2="14"/>
                        </g>
                        <g class="gota-chuva-2">
                            <line x1="115" y1="5" x2="111" y2="16"/><line x1="225" y1="0" x2="221" y2="11"/>
                            <line x1="335" y1="9" x2="331" y2="20"/><line x1="455" y1="3" x2="451" y2="14"/>
                            <line x1="575" y1="11" x2="571" y2="22"/><line x1="695" y1="4" x2="691" y2="15"/>
                            <line x1="805" y1="8" x2="801" y2="19"/>
                        </g>
                        <g class="gota-chuva-3">
                            <line x1="145" y1="10" x2="141" y2="21"/><line x1="255" y1="4" x2="251" y2="15"/>
                            <line x1="375" y1="12" x2="371" y2="23"/><line x1="495" y1="2" x2="491" y2="13"/>
                            <line x1="615" y1="8" x2="611" y2="19"/><line x1="735" y1="5" x2="731" y2="16"/>
                        </g>
                        <g class="gota-chuva-4">
                            <line x1="70" y1="6" x2="66" y2="17"/><line x1="165" y1="12" x2="161" y2="23"/>
                            <line x1="275" y1="3" x2="271" y2="14"/><line x1="395" y1="9" x2="391" y2="20"/>
                            <line x1="515" y1="5" x2="511" y2="16"/><line x1="635" y1="11" x2="631" y2="22"/>
                            <line x1="755" y1="2" x2="751" y2="13"/>
                        </g>
                    </g>

                    <g stroke="#1B5E20" stroke-width="1" stroke-linecap="round" fill="none">
                        <path class="respingo-1" d="M120 110 Q123 106 126 110"/>
                        <path class="respingo-2" d="M290 110 Q293 106 296 110"/>
                        <path class="respingo-1" d="M560 110 Q563 106 566 110"/>
                        <path class="respingo-2" d="M660 110 Q663 106 666 110"/>
                    </g>
                </svg>
            </div>
            """,
            height=136
        )
            
    st.stop()

with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div style="text-align: center; padding-top: 2px; padding-bottom: 8px;">
                <img src="data:{LOGO_MIME};base64,{LOGO_B64}" style="width: 82px; height: 82px; border-radius: 16px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 8px;">
                <h2 style="margin: 0; padding: 0; font-size: 1.25rem; letter-spacing: 0.3px;">WMS Grano</h2>
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
# === TEMA VISUAL GLOBAL MODERNIZADO (WMS GRANO) ===
    st.markdown(
        """
        <style>
        /* 1. Botões Principais (Pílula Verde-Floresta) */
        .stMain button[kind="primary"],
        .stMain button[kind="primaryFormSubmit"],
        [data-testid="stAppViewContainer"] button[kind="primary"],
        [data-testid="stAppViewContainer"] button[kind="primaryFormSubmit"] {
            background-color: #1F2922 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 20px !important;
            min-height: 36px !important;
            padding: 4px 20px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.14) !important;
            transition: all 0.18s ease !important;
        }
        .stMain button[kind="primary"] p,
        .stMain button[kind="primaryFormSubmit"] p,
        [data-testid="stAppViewContainer"] button[kind="primary"] p,
        [data-testid="stAppViewContainer"] button[kind="primaryFormSubmit"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.84rem !important;
        }
        .stMain button[kind="primary"]:hover,
        .stMain button[kind="primaryFormSubmit"]:hover,
        [data-testid="stAppViewContainer"] button[kind="primary"]:hover,
        [data-testid="stAppViewContainer"] button[kind="primaryFormSubmit"]:hover {
            background-color: #1B5E20 !important;
            transform: translateY(-1px) !important;
        }

        /* 2. Cartões de Métricas (KPIs com borda verde à esquerda) */
        [data-testid="stMetric"] {
            background-color: #E4E0D6 !important;
            border: 1px solid rgba(27, 94, 32, 0.28) !important;
            border-left: 4px solid #1B5E20 !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        }

        /* 3. Caixas, Containers e Expanders */
        [data-testid="stExpander"],
        .stMain [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #E4E0D6 !important;
            border: 1px solid rgba(27, 94, 32, 0.28) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }

        /* 4. Tabelas e Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(27, 94, 32, 0.30) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    ) 

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
    usar_inicio = len(modulos_disponiveis) > 1
    menu_lateral_itens = (["🏠 Início"] + modulos_disponiveis) if usar_inicio else modulos_disponiveis

    if "aba_ativa" not in st.session_state or st.session_state.aba_ativa not in menu_lateral_itens:
        st.session_state.aba_ativa = "🏠 Início" if usar_inicio else next(iter(modulos_disponiveis))

    for mod_item in menu_lateral_itens:
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
        section[data-testid="stSidebar"] [data-testid="stTextInputRootElement"] button {
         background-color: #1F2922 !important;
         border-left: 1px solid rgba(76, 175, 80, 0.45) !important;
         height: 100% !important;
         align-self: stretch !important;
         border-radius: 0 7px 7px 0 !important;
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
    st.markdown("<div style='text-align:center; color:#8A928C; font-size:0.72rem; margin-top:14px; line-height:1.35;'><strong>WMS Grano v2.0</strong><br>Inteligência Logística</div>", unsafe_allow_html=True)        
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
    
@st.cache_data(ttl=60, show_spinner=False)
def montar_html_usuarios_online():
    df_u_on = _ler_planilha_com_cache("usuarios")
    agora_ref = datetime.now()
    html_res = ""
    qtd_on = 0
    if not df_u_on.empty and "ultimo_acesso" in df_u_on.columns:
        for _, r_on in df_u_on.iterrows():
            ts_str = str(r_on.get("ultimo_acesso", "")).strip()
            if ts_str and ts_str.lower() not in ("nan", "none", "null"):
                try:
                    dt_acesso = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if (agora_ref - dt_acesso).total_seconds() <= 600:
                        qtd_on += 1
                        l_on = limpar_texto(r_on.get("login", ""))
                        n_on = str(r_on.get("nome", l_on)).strip()
                        p_on = str(r_on.get("perfil", "")).strip()
                        ini_on = "".join(p[:1] for p in n_on.split()[:2]).upper() if n_on else "U"
                        foto_on = carregar_foto_usuario(l_on)
                        ml_style = "margin-left: -10px;" if qtd_on > 1 else ""
                        if foto_on:
                            bolinha = f'<img src="data:image/png;base64,{foto_on}" title="{n_on} ({p_on}) - Online" style="width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid #4CAF50; background-color: #1F2922; {ml_style}">'
                        else:
                            bolinha = f'<div title="{n_on} ({p_on}) - Online" style="width: 36px; height: 36px; border-radius: 50%; background-color: #1B5E20; color: #E6E1D6; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; border: 2px solid #4CAF50; {ml_style}">{ini_on}</div>'
                        html_res += bolinha
                except Exception:
                    pass
    return qtd_on, html_res

qtd_online, avatares_online_html = montar_html_usuarios_online()
if qtd_online > 0:
    st.markdown(
        f"""
        <div style="position: fixed; top: 12px; right: 210px; z-index: 999999; display: flex; align-items: center;">
            <div style="display: flex; align-items: center;">{avatares_online_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
# === BARRA DE GUIAS FIXA COM "🏠 INÍCIO" SEMPRE EM 1º LUGAR ===
if "abas_abertas" not in st.session_state or not st.session_state.abas_abertas:
    st.session_state.abas_abertas = ["🏠 Início"] if usar_inicio else [aba]

if usar_inicio:
    outras_abas = [m for m in st.session_state.abas_abertas if m != "🏠 Início" and m in menu_lateral_itens]
    if aba != "🏠 Início" and aba in menu_lateral_itens and aba not in outras_abas:
        if len(outras_abas) >= 4:
            outras_abas.pop(0)
        outras_abas.append(aba)
    abas_nav = ["🏠 Início"] + outras_abas
else:
    abas_nav = [aba]

st.session_state.abas_abertas = abas_nav

def _ao_mudar_guia():
    sel = st.session_state.get("barra_guias_topo")
    if sel == "✕ Fechar guia atual":
        atual = st.session_state.aba_ativa
        if atual != "🏠 Início" and atual in st.session_state.abas_abertas:
            st.session_state.abas_abertas.remove(atual)
        st.session_state.aba_ativa = st.session_state.abas_abertas[-1] if st.session_state.abas_abertas else "🏠 Início"
        st.session_state["barra_guias_topo"] = st.session_state.aba_ativa
    elif sel and sel in st.session_state.abas_abertas:
        st.session_state.aba_ativa = sel

if len(abas_nav) > 1:
    st.markdown(
        """
        <style>
        /* Faz o header nativo do Streamlit deixar cliques passarem na faixa central */
        header[data-testid="stHeader"] {
            background-color: #C9C5BA !important;
            border-bottom: 1px solid rgba(27, 94, 32, 0.16) !important;
            height: 3.35rem !important;
            pointer-events: none !important;
        }
            
        header[data-testid="stHeader"] * {
            pointer-events: auto !important;
        }

        /* Sobe e congela a barra de guias no topo da janela (mesma linha dos avatares) */
        [data-testid="stButtonGroup"],
        [data-testid="stPills"],
        div[data-testid="stMainBlockContainer"] div:has(> [data-testid="stButtonGroup"]),
        div[data-testid="stMainBlockContainer"] div:has(> [data-testid="stPills"]) {
            position: fixed !important;
            top: 10px !important;
            left: 21.5rem !important;
            width: auto !important;
            max-width: calc(100vw - 38rem) !important;
            z-index: 999998 !important;
            pointer-events: auto !important;
        }

        /* Ajusta a posição à esquerda quando a barra lateral estiver recolhida */
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div [data-testid="stButtonGroup"],
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div [data-testid="stPills"],
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div div[data-testid="stMainBlockContainer"] div:has(> [data-testid="stButtonGroup"]),
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div div[data-testid="stMainBlockContainer"] div:has(> [data-testid="stPills"]) {
            left: 4.5rem !important;
            max-width: calc(100vw - 21rem) !important;
        }
        /* Destaca o último botão ("✕ Fechar guia atual") em vermelho suave */
        [data-testid="stButtonGroup"] button:last-of-type,
        [data-testid="stPills"] button:last-of-type {
            background-color: #FDECEA !important;
            border: 1px solid #E57373 !important;
            margin-left: 6px !important;
            transition: all 0.18s ease !important;
        }
        [data-testid="stButtonGroup"] button:last-of-type p,
        [data-testid="stPills"] button:last-of-type p {
            color: #B71C1C !important;
            font-weight: 700 !important;
        }
        [data-testid="stButtonGroup"] button:last-of-type:hover,
        [data-testid="stPills"] button:last-of-type:hover {
            background-color: #B71C1C !important;
            border-color: #B71C1C !important;
        }
        [data-testid="stButtonGroup"] button:last-of-type:hover p,
        [data-testid="stPills"] button:last-of-type:hover p {
            color: #FFFFFF !important;
        }        
        </style>
        """,
        unsafe_allow_html=True
    )
    st.session_state["barra_guias_topo"] = st.session_state.aba_ativa
    st.pills(
        "Guias abertas:",
        options=abas_nav + ["✕ Fechar guia atual"],
        label_visibility="collapsed",
        key="barra_guias_topo",
        on_change=_ao_mudar_guia
    )

aba = st.session_state.aba_ativa

if aba == "🏠 Início":

    hoje_str_ini = datetime.now(FUSO_BR).strftime("%d/%m/%Y")
    primeiro_nome_ini = st.session_state.nome_usuario.split().pop(0).title() if st.session_state.nome_usuario else "Equipe"

    CIDADES_CLIMA_INI = {
        "Sapucaia do Sul/RS": (-29.8278, -51.1456),
        "Canoas/RS": (-29.9178, -51.1836),
        "Esteio/RS": (-29.8525, -51.1844),
        "São Leopoldo/RS": (-29.7604, -51.1480),
        "Novo Hamburgo/RS": (-29.6875, -51.1328),
        "Porto Alegre/RS": (-30.0346, -51.2177),
        "Gravataí/RS": (-29.9444, -50.9919),
    }

    @st.cache_data(ttl=1800, show_spinner=False)
    def obter_clima_inicio(lat_c, lon_c):
        import urllib.request
        import json
        host_api = "https://api." + "open-meteo.com" + "/v1/forecast"
        url_w = (
            f"{host_api}?latitude={lat_c}&longitude={lon_c}"
            "&current=temperature_2m,weather_code"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min"
            "&timezone=America%2FSao_Paulo&forecast_days=5"
        )
        req = urllib.request.Request(url_w, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _icone_clima_ini(c):
        if c == 0:
            return "☀️", "Céu limpo"
        elif c in (1, 2):
            return "🌤️", "Poucas nuvens"
        elif c == 3:
            return "⛅", "Nublado"
        elif c in (45, 48):
            return "🌫️", "Neblina"
        elif c in (51, 53, 55, 61, 63, 65, 80, 81, 82):
            return "🌧️", "Chuva"
        elif c in (95, 96, 99):
            return "⛈️", "Trovoada"
        return "🌤️", "Estável"
        
    st.markdown(
        """
        <style>
        /* Sobe a barra de abas para perto da linha do topo e deixa o seletor da cidade discreto */
        .stMainBlockContainer, [data-testid="stMainBlockContainer"], .block-container {
             padding-top: 3.1rem !important;
        }
        div[data-testid="stSelectbox"]:has(input[aria-label="Cidade:"]) div[data-baseweb="select"] > div {
            min-height: 28px !important;
            height: 28px !important;
            font-size: 0.76rem !important;
            background-color: rgba(255, 255, 255, 0.45) !important;
            border: 1px solid rgba(27, 94, 32, 0.25) !important;
            border-radius: 16px !important;
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        /* Remove bordas de grade internas do mini-calendário */
        .mini-cal-grano, .mini-cal-grano tr, .mini-cal-grano th, .mini-cal-grano td {
            border: none !important;
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    c_topo_esq, c_topo_clima, _, c_topo_cal = st.columns((1.30, 1.85, 0.35, 1.05), vertical_alignment="center")

    with c_topo_esq:
        st.markdown(
            f"""
            <style>
            @keyframes pulsoVivoGrano {{
                0%, 100% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.35); opacity: 0.55; }}
            }}
            @keyframes balancoArvoreGrano {{
                0%, 100% {{ transform: rotate(-1.5deg); }}
                50% {{ transform: rotate(2.5deg); }}
            }}
            @keyframes rastroVentoGrano {{
                0% {{ stroke-dashoffset: 330; opacity: 0; }}
                20% {{ opacity: 0.45; }}
                80% {{ opacity: 0.38; }}
                100% {{ stroke-dashoffset: -330; opacity: 0; }}
            }}
            @keyframes pirueta3DFolha1 {{
                0% {{ transform: perspective(380px) translate(54px, 16px) rotateX(0deg) rotateY(0deg) rotateZ(0deg) scale(0.95); opacity: 0; }}
                12% {{ opacity: 1; }}
                32% {{ transform: perspective(380px) translate(140px, 56px) rotateX(180deg) rotateY(90deg) rotateZ(140deg) scale(1.12); }}
                60% {{ transform: perspective(380px) translate(240px, 14px) rotateX(360deg) rotateY(220deg) rotateZ(290deg) scale(1.02); }}
                85% {{ transform: perspective(380px) translate(325px, 50px) rotateX(520deg) rotateY(320deg) rotateZ(440deg) scale(0.95); opacity: 0.92; }}
                100% {{ transform: perspective(380px) translate(390px, 24px) rotateX(680deg) rotateY(420deg) rotateZ(580deg) scale(0.85); opacity: 0; }}
            }}
            @keyframes pirueta3DFolha2 {{
                0% {{ transform: perspective(380px) translate(60px, 34px) rotateX(40deg) rotateY(0deg) rotateZ(30deg) scale(0.9); opacity: 0; }}
                15% {{ opacity: 0.95; }}
                45% {{ transform: perspective(380px) translate(180px, 10px) rotateX(-190deg) rotateY(160deg) rotateZ(-150deg) scale(1.08); }}
                75% {{ transform: perspective(380px) translate(290px, 54px) rotateX(-380deg) rotateY(300deg) rotateZ(-320deg) scale(0.98); opacity: 0.88; }}
                100% {{ transform: perspective(380px) translate(380px, 28px) rotateX(-540deg) rotateY(420deg) rotateZ(-460deg) scale(0.85); opacity: 0; }}
            }}
            @keyframes pirueta3DFolha3 {{
                0% {{ transform: perspective(380px) translate(48px, 24px) rotateX(0deg) rotateY(30deg) rotateZ(-20deg) scale(0.88); opacity: 0; }}
                15% {{ opacity: 0.9; }}
                40% {{ transform: perspective(380px) translate(160px, 60px) rotateX(150deg) rotateY(-140deg) rotateZ(180deg) scale(1.04); }}
                70% {{ transform: perspective(380px) translate(265px, 18px) rotateX(320deg) rotateY(-280deg) rotateZ(350deg) scale(0.95); opacity: 0.82; }}
                100% {{ transform: perspective(380px) translate(360px, 44px) rotateX(480deg) rotateY(-400deg) rotateZ(500deg) scale(0.82); opacity: 0; }}
            }}
            .saudacao-wrap-grano {{
                position: relative;
                padding-top: 6px;
            }}
            .arvore-grano-anim {{
                transform-origin: bottom center;
                animation: balancoArvoreGrano 4.2s ease-in-out infinite;
                margin-right: 14px;
                flex-shrink: 0;
            }}
            .ponto-vivo-grano {{
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: #2E7D32;
                box-shadow: 0 0 0 4px rgba(46, 125, 50, 0.18);
                animation: pulsoVivoGrano 2.2s ease-in-out infinite;
                margin-left: 12px;
                vertical-align: middle;
                flex-shrink: 0;
            }}
            .vento-overlay-grano {{
                position: absolute;
                left: 0;
                top: 0;
                height: 92px;
                width: 415px;
                z-index: 5;
                overflow: visible;
                pointer-events: none;
            }}
            .linha-brisa-1 {{
                stroke-dasharray: 120 210;
                animation: rastroVentoGrano 4.8s ease-in-out infinite;
            }}
            .linha-brisa-2 {{
                stroke-dasharray: 95 235;
                animation: rastroVentoGrano 5.7s ease-in-out 1.6s infinite;
            }}
            .f-voa-1 {{ position: absolute; left: 0px; top: 4px; filter: drop-shadow(0 3px 4px rgba(20,26,22,0.20)); animation: pirueta3DFolha1 6.4s cubic-bezier(0.37, 0, 0.63, 1) infinite; }}
            .f-voa-2 {{ position: absolute; left: 0px; top: 8px; filter: drop-shadow(0 3px 4px rgba(20,26,22,0.16)); animation: pirueta3DFolha2 7.6s cubic-bezier(0.37, 0, 0.63, 1) 2.0s infinite; }}
            .f-voa-3 {{ position: absolute; left: 0px; top: 6px; filter: drop-shadow(0 3px 4px rgba(20,26,22,0.16)); animation: pirueta3DFolha3 7.0s cubic-bezier(0.37, 0, 0.63, 1) 3.6s infinite; }}
            </style>
            <div class="saudacao-wrap-grano">
                <div class="vento-overlay-grano">
                    <svg width="410" height="92" viewBox="0 0 410 92" fill="none" style="position:absolute; left:0; top:0;">
                        <path class="linha-brisa-1" d="M58 26 Q 150 62, 240 24 T 400 46" stroke="#1B5E20" stroke-width="1.3" stroke-linecap="round" fill="none"/>
                        <path class="linha-brisa-2" d="M64 54 Q 170 18, 270 52 T 405 30" stroke="#4CAF50" stroke-width="1.1" stroke-linecap="round" fill="none"/>
                    </svg>
                    <svg class="f-voa-1" width="28" height="28" viewBox="0 0 32 32" fill="none">
                        <path d="M4 27 C6 25 8 23 10 21" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                        <path d="M10 21 C8 12 16 5 27 5 C22 11 16 16 10 21 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                        <path d="M10 21 C19 22 26 15 27 5 C22 11 16 16 10 21 Z" fill="#66BB6A" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                    </svg>
                    <svg class="f-voa-2" width="24" height="24" viewBox="0 0 32 32" fill="none">
                        <path d="M4 27 C6 25 8 23 10 21" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                        <path d="M10 21 C8 12 16 5 27 5 C22 11 16 16 10 21 Z" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1.6" stroke-linejoin="round"/>
                        <path d="M10 21 C19 22 26 15 27 5 C22 11 16 16 10 21 Z" fill="#81C784" stroke="#2E7D32" stroke-width="1.6" stroke-linejoin="round"/>
                    </svg>
                    <svg class="f-voa-3" width="26" height="26" viewBox="0 0 32 32" fill="none">
                        <path d="M4 27 C6 25 8 23 10 21" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                        <path d="M10 21 C8 12 16 5 27 5 C22 11 16 16 10 21 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                        <path d="M10 21 C19 22 26 15 27 5 C22 11 16 16 10 21 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div style="display:flex; align-items:center; position:relative; z-index:1;">
                    <svg class="arvore-grano-anim" width="74" height="86" viewBox="0 0 74 86" fill="none">
                        <!-- Solo e gramínea sutil -->
                        <line x1="12" y1="82" x2="62" y2="82" stroke="#141A16" stroke-width="1.7" stroke-linecap="round"/>
                        <path d="M18 82 L16 78 M21 82 L22 79 M54 82 L55 78" stroke="#1B5E20" stroke-width="1.4" stroke-linecap="round"/>
                        <!-- Copa traseira mais escura (profundidade) -->
                        <circle cx="24" cy="40" r="16" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.6"/>
                        <circle cx="50" cy="38" r="15" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.6"/>
                        <circle cx="37" cy="24" r="18" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.6"/>
                        <!-- Copa frontal clara -->
                        <path d="M18 48 C10 47 7 37 14 31 C11 21 20 12 30 14 C34 7 46 8 49 16 C59 16 65 26 59 35 C65 42 59 51 50 50 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.8" stroke-linejoin="round"/>
                        <!-- Detalhes de folhagem interna -->
                        <path d="M23 26 C27 22 33 22 36 25" stroke="#2E7D32" stroke-width="1.4" stroke-linecap="round"/>
                        <path d="M43 32 C47 29 52 30 54 34" stroke="#2E7D32" stroke-width="1.4" stroke-linecap="round"/>
                        <!-- Tronco orgânico com raízes e galhos -->
                        <path d="M31 82 C34 74 35 62 35 45 M43 82 C40 74 39 62 39 45" stroke="#141A16" stroke-width="2" stroke-linecap="round"/>
                        <path d="M35 56 L24 44 M39 52 L50 41 M37 46 L37 33" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    </svg>
                    <div style="padding-top: 10px;">
                        <div style="display:flex; align-items:flex-end; margin-bottom:2px;">
                            <span style="font-size:2.45rem; font-weight:800; color:#141A16; letter-spacing:-0.6px; line-height:1.05; white-space:nowrap;">Olá, {primeiro_nome_ini}</span>
                            <span class="ponto-vivo-grano" style="margin-left: 8px; margin-bottom: 10px;"></span>
                        </div>
                        <div style="font-size:0.84rem; color:#5A635C; margin-top:6px;">Torre de Controle Logística • {hoje_str_ini}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with c_topo_clima:
        try:
            dw = obter_clima_inicio(-29.8278, -51.1456)
            t_agora = round(dw["current"]["temperature_2m"])
            ic_ag, desc_ag = _icone_clima_ini(dw["current"]["weather_code"])
            dias_pt_i = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            daily_i = dw["daily"]

            cols_dias_html = ""
            total_dias_w = len(daily_i["time"])
            for idx_d in range(total_dias_w):
                dt_d = datetime.strptime(daily_i["time"][idx_d], "%Y-%m-%d")
                nm_d = "Hoje" if idx_d == 0 else dias_pt_i[dt_d.weekday()]
                dt_curta = dt_d.strftime("%d/%m")
                ic_d, _ = _icone_clima_ini(daily_i["weather_code"][idx_d])
                tmax_d = round(daily_i["temperature_2m_max"][idx_d])
                tmin_d = round(daily_i["temperature_2m_min"][idx_d])
                borda_dir = "border-right:1px solid rgba(27,94,32,0.16);" if idx_d < total_dias_w - 1 else ""
                destaque_hoje = "background:rgba(27,94,32,0.08); border-radius:8px;" if idx_d == 0 else ""
                cols_dias_html += (
                    f'<div style="{borda_dir} {destaque_hoje} padding:4px 2px; text-align:center;">'
                    f'<div style="font-size:0.76rem; font-weight:700; color:#141A16;">{nm_d}</div>'
                    f'<div style="font-size:0.60rem; color:#5A635C;">{dt_curta}</div>'
                    f'<div style="font-size:1.25rem; line-height:1.15; margin:2px 0;">{ic_d}</div>'
                    f'<div style="font-size:0.68rem; font-weight:700; color:#141A16;">{tmax_d}° <span style="font-weight:400; color:#5A635C;">/ {tmin_d}°</span></div>'
                    f'</div>'
                )

            st.markdown(
                f'<div style="background:rgba(255,255,255,0.52); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,0.8); border-radius:18px; padding:10px 14px; box-shadow:0 6px 18px rgba(20,26,22,0.06);">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; padding-bottom:2px; border-bottom:1px solid rgba(27,94,32,0.15);">'
                f'<span style="font-size:0.72rem; font-weight:700; color:#141A16;">📍 Sapucaia do Sul/RS • <span style="font-weight:500; color:#4A524C;">{desc_ag}</span></span>'
                f'<span style="font-size:0.73rem; font-weight:700; color:#1B5E20;">Agora: {ic_ag} {t_agora}°C</span>'
                f'</div>'
                f'<div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:2px;">{cols_dias_html}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        except Exception:
            st.caption("🌤️ Clima indisponível no momento")

    with c_topo_cal:
        import calendar
        agora_c = datetime.now(FUSO_BR)
        ano_i, mes_i, dia_i = agora_c.year, agora_c.month, agora_c.day
        meses_nomes_i = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        feriados_i = set()
        try:
            for dt_f in obter_feriados_sistema():
                if dt_f.year == ano_i and dt_f.month == mes_i:
                    feriados_i.add(dt_f.day)
        except Exception:
            pass

        mat_cal = calendar.Calendar(firstweekday=6).monthdayscalendar(ano_i, mes_i)
        linhas_cal_html = ""
        for sem_i in mat_cal:
            linhas_cal_html += "<tr>"
            for idx_s, d_i in enumerate(sem_i):
                if d_i == 0:
                    linhas_cal_html += "<td></td>"
                elif d_i == dia_i:
                    linhas_cal_html += f"<td><span style='background:#1B5E20; color:#FFFFFF; border-radius:50%; padding:0px 4px; font-weight:700;'>{d_i}</span></td>"
                elif d_i in feriados_i:
                    linhas_cal_html += f"<td><span style='background:#FFCDD2; color:#B71C1C; border-radius:50%; padding:0px 4px; font-weight:700;' title='Feriado'>{d_i}</span></td>"
                elif idx_s in (0, 6):
                    linhas_cal_html += f"<td style='color:#8A928C;'>{d_i}</td>"
                else:
                    linhas_cal_html += f"<td style='color:#141A16;'>{d_i}</td>"
            linhas_cal_html += "</tr>"

        st.markdown(
            f'<div style="background:rgba(255,255,255,0.52); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,0.8); border-radius:18px; padding:10px 12px; box-shadow:0 6px 18px rgba(20,26,22,0.06);">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px; padding-bottom:2px; border-bottom:1px solid rgba(27,94,32,0.15);">'
            f'<span style="font-size:0.72rem; font-weight:700; color:#141A16;">📅 {meses_nomes_i[mes_i]} {ano_i}</span>'
            f'<span style="font-size:0.58rem; color:#B71C1C; font-weight:600;">● Feriado</span>'
            f'</div>'
            f'<table class="mini-cal-grano" style="width:100%; border-collapse:collapse; text-align:center; font-size:0.62rem; line-height:1.22;">'
            f'<tr style="color:#5A635C; font-weight:700;"><th>D</th><th>S</th><th>T</th><th>Q</th><th>Q</th><th>S</th><th>S</th></tr>'
            f'{linhas_cal_html}'
            f'</table></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-bottom: 44px;'></div>", unsafe_allow_html=True)

    df_plan_ini = carregar_dados("planejamento")
    df_cargas_ini = carregar_dados("cargas")

    # 1. Mural de Notificações Pendentes
    alertas_ini = list()
    if not df_plan_ini.empty and "Notificação" in df_plan_ini.columns:
        login_u_ini = limpar_texto(st.session_state.login_usuario)
        nome_u_ini = limpar_texto(st.session_state.nome_usuario)
        for idx_i, r_i in df_plan_ini.iterrows():
            txt_nt_i = str(r_i.get("Notificação", "")).strip()
            if not txt_nt_i or txt_nt_i.lower() in ("nan", "none", "null"):
                continue
            for parte_i in txt_nt_i.split(" || "):
                p_limpa_i = parte_i.strip()
                if not p_limpa_i:
                    continue
                lidos_i = set()
                if "[LIDO:" in p_limpa_i:
                    trecho_l_i = p_limpa_i.split("[LIDO:").pop(1).split("]").pop(0)
                    lidos_i = {limpar_texto(u) for u in trecho_l_i.split(",") if limpar_texto(u)}
                if login_u_ini in lidos_i or nome_u_ini in lidos_i:
                    continue
                if "[PARA:" not in p_limpa_i:
                    alertas_ini.append((idx_i, r_i, p_limpa_i))
                else:
                    dest_i = limpar_texto(p_limpa_i.split("[PARA:").pop(1).split("]").pop(0))
                    if dest_i in ("TODOS", login_u_ini, nome_u_ini):
                        alertas_ini.append((idx_i, r_i, p_limpa_i))

    if alertas_ini:
        with st.container(border=True):
            st.error(f"🔔 **Você tem {len(alertas_ini)} recado(s) pendente(s) no sistema:**")
            for seq_i, (idx_i, r_i, msg_b_i) in enumerate(alertas_ini):
                ci_txt, ci_btn = st.columns((4, 1), vertical_alignment="center")
                msg_limpa_i = re.sub(r"^\[PARA:\s*[^\]]+\]\s*", "", msg_b_i).strip()
                msg_limpa_i = re.sub(r"\s*\[LIDO:\s*[^\]]+\]", "", msg_limpa_i).strip().replace("(DE: ", "(")
                ped_ref_i = limpar_texto(r_i.get("Nº Pedido", "")) or "GERAL"
                cli_ref_i = str(r_i.get("Cliente", "")).strip()
                cli_tag_i = f" ({cli_ref_i})" if cli_ref_i and cli_ref_i.lower() not in ("nan", "none", "null") else ""

                autor_html_i = ""
                corpo_msg_i = msg_limpa_i
                m_autor = re.search(r"\(([^()]+)\)\s*$", msg_limpa_i)
                if m_autor:
                    autor_nome_i = m_autor.group(1).strip()
                    corpo_msg_i = msg_limpa_i[:m_autor.start()].strip()
                    autor_html_i = (
                        f" <span style='background:#E3EEF8; color:#1E3A5F; border:1px solid #B6D2EC; "
                        f"padding:1px 8px; border-radius:10px; font-size:0.74rem; font-weight:700; "
                        f"margin-left:6px; white-space:nowrap;'>👤 {autor_nome_i}</span>"
                    )

                badge_ped_html = (
                    f"<span style='background:#1F2922; color:#FFFFFF; border:1px solid #4CAF50; "
                    f"padding:2px 9px; border-radius:10px; font-size:0.76rem; font-weight:700; "
                    f"margin-right:6px; white-space:nowrap;'>📌 Pedido {ped_ref_i}{cli_tag_i}</span>"
                )

                ci_txt.markdown(
                    f"{badge_ped_html} <span style='color:#08240E; font-weight:700;'>{corpo_msg_i}</span>{autor_html_i}",
                    unsafe_allow_html=True
                )
                
                if ci_btn.button("✔️ Marcar como Lido", key=f"ini_ler_nt_{idx_i}_{seq_i}", use_container_width=True):
                    df_plan_ini["Notificação"] = df_plan_ini["Notificação"].fillna("").astype(object)
                    partes_at_i = [x.strip() for x in str(df_plan_ini.at[idx_i, "Notificação"]).split(" || ") if x.strip()]
                    if msg_b_i in partes_at_i:
                        idx_m_i = partes_at_i.index(msg_b_i)
                        if "[PARA: TODOS]" in msg_b_i.upper():
                            if "[LIDO:" in msg_b_i:
                                base_i, resto_i = msg_b_i.split("[LIDO:", 1)
                                lidos_at_i = resto_i.split("]", 1).pop(0).strip()
                                novos_l_i = f"{lidos_at_i}, {login_u_ini}" if lidos_at_i else login_u_ini
                                partes_at_i[idx_m_i] = f"{base_i.strip()} [LIDO: {novos_l_i}]"
                            else:
                                partes_at_i[idx_m_i] = f"{msg_b_i} [LIDO: {login_u_ini}]"
                        else:
                            partes_at_i.remove(msg_b_i)
                    df_plan_ini.at[idx_i, "Notificação"] = " || ".join(partes_at_i)
                    salvar_dados(df_plan_ini[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.toast("✔️ Recado marcado como lido!", icon="✔️")
                    st.rerun()

    # 2. Pulso Rápido da Operação Hoje (4 Cartões)
    prog_hoje, patio_conf_hoje, carreg_hoje, pend_auditoria = 0, 0, 0, 0
    cargas_validadas_ini = set()

    if not df_plan_ini.empty:
        if "validado" in df_plan_ini.columns:
            for _, r_v in df_plan_ini.iterrows():
                val_s = str(r_v.get("validado", "")).strip()
                if val_s and val_s.lower() not in ("nan", "none", "null", "nao", "não"):
                    for c_k in ("Nº Pedido", "id_carga"):
                        v_k = limpar_texto(r_v.get(c_k, ""))
                        if v_k:
                            cargas_validadas_ini.add(v_k)

        df_p_ativos_ini = df_plan_ini[df_plan_ini["Nº Pedido"].astype(str).str.strip() != ""].copy()
        if not df_p_ativos_ini.empty:
            datas_ini = df_p_ativos_ini["Data"].apply(formatar_data_br_str)
            status_ini = df_p_ativos_ini["Status"].apply(limpar_texto)
            prog_hoje = int((datas_ini == hoje_str_ini).sum())
            patio_conf_hoje = int(status_ini.isin((limpar_texto("🚚 Veículo no Pátio"), limpar_texto("📦 Em Conferência"))).sum())
            carreg_hoje = int(((datas_ini == hoje_str_ini) & (status_ini == limpar_texto("✅ Carregado / Liberado"))).sum())

    if not df_cargas_ini.empty and "id_carga" in df_cargas_ini.columns:
        for cid_i, grp_i in df_cargas_ini.groupby("id_carga", sort=False):
            if verificar_carga_100_concluida(grp_i) and limpar_texto(cid_i) not in cargas_validadas_ini:
                pend_auditoria += 1

    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    c_kpi1.metric("📅 Programados Hoje", prog_hoje)
    c_kpi2.metric("🚚 Pátio / Conferindo", patio_conf_hoje)
    c_kpi3.metric("✅ Carregados Hoje", carreg_hoje)
    c_kpi4.metric("🛡️ Aguardando Auditoria", pend_auditoria)

    st.divider()

    # 3. Atalhos Rápidos para os Módulos
    st.subheader("🚀 Acesso Rápido aos Módulos")
    st.markdown(
        """
        <style>
        /* Cartões compactos e botões pílula modernos na Página Inicial */
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"]:has(button[data-testid="stBaseButton-primary"]) {
            background-color: #E4E0D6 !important;
            border: 1px solid rgba(27, 94, 32, 0.30) !important;
            border-radius: 10px !important;
            padding: 2px 6px !important;
            transition: all 0.18s ease !important;
        }
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"]:has(button[data-testid="stBaseButton-primary"]):hover {
            border-color: #1B5E20 !important;
            background-color: #EAE7DE !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.10) !important;
        }
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] button[data-testid="stBaseButton-primary"] {
            background-color: #1F2922 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 20px !important;
            padding: 2px 12px !important;
            min-height: 28px !important;
            height: 28px !important;
            width: auto !important;
            float: right !important;
            box-shadow: none !important;
        }
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] button[data-testid="stBaseButton-primary"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.74rem !important;
            white-space: nowrap !important;
        }
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] button[data-testid="stBaseButton-primary"]:hover {
            background-color: #1B5E20 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    desc_modulos = {
        "📊 Análise de Pedidos": "Importar carteira do BI, calcular SLA/dias úteis e vincular NF-e.",
        "🚚 Planejamento Logística": "Programar frota, acompanhar status e disparar alertas.",
        "📥 Importação de Pedidos": "Subir arquivos de pedidos para liberar ao conferente.",
        "📦 Conferência dos Pedidos": "Bipagem de etiquetas, lotes e registro de lacre.",
        "📈 Painel de Acompanhamento": "Progresso em tempo real e registro de cortes.",
        "📋 Gestão de Pedidos": "Visão geral de cargas conferidas, pendentes e validadas.",
        "✅ Auditoria e Ajustes": "Validação tripla (Pedido x Bipado x Cliente) e estornos.",
        "👥 Central de Usuários": "Gerenciar logins, fotos, perfis e permissões da equipe."
    }
    cols_atalho = st.columns(4)
    for idx_at, mod_at in enumerate(modulos_disponiveis):
        with cols_atalho[idx_at % 4]:
            with st.container(border=True):
                st.markdown(f"<div style='font-weight:700; font-size:0.86rem; color:#141A16; margin-bottom:3px;'>{mod_at}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:0.72rem; color:#4A524C; line-height:1.25; min-height:34px; margin-bottom:6px;'>{desc_modulos.get(mod_at, 'Acessar módulo operacional.')}</div>", unsafe_allow_html=True)
                if st.button("Abrir ➔", key=f"btn_atalho_ini_{idx_at}", type="primary", use_container_width=True):
                    st.session_state.aba_ativa = mod_at
                    st.rerun()

    # 4. Banda de Vegetais Ilustrada 3D (Black Line + Verde Grano)
    components.html(
        """
        <style>
        body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
        @keyframes soloGuitarra3D {
            0%, 100% { transform: rotateZ(-2.5deg) translateY(0px); }
            50% { transform: rotateZ(2.5deg) translateY(-3px); }
        }
        @keyframes vocalistaShow3D {
            0%, 100% { transform: rotateZ(-2deg) translateY(0px); }
            50% { transform: rotateZ(3deg) translateY(-3px); }
        }
        @keyframes bateristaShow3D {
            0%, 100% { transform: translateY(0px) scaleY(1); }
            50% { transform: translateY(-2px) scaleY(0.98); }
        }
        @keyframes pratoVibra {
            0%, 100% { transform: rotateZ(0deg); }
            25% { transform: rotateZ(-9deg); }
            75% { transform: rotateZ(9deg); }
        }
        @keyframes baqE {
            0%, 100% { transform: rotateZ(-22deg); }
            50% { transform: rotateZ(18deg); }
        }
        @keyframes baqD {
            0%, 100% { transform: rotateZ(18deg); }
            50% { transform: rotateZ(-22deg); }
        }
        @keyframes baixistaGroove3D {
            0%, 100% { transform: rotateZ(2deg) translateY(0px); }
            50% { transform: rotateZ(-2deg) translateY(-2.5px); }
        }

        @keyframes ondaSom {
            0% { transform: scale(0.6); opacity: 0; }
            40% { opacity: 0.9; }
            100% { transform: scale(1.45); opacity: 0; }
        }
        @keyframes notaSobe3D {
            0% { transform: perspective(260px) translateY(6px) rotateY(0deg) scale(0.75); opacity: 0; }
            25% { opacity: 1; }
            100% { transform: perspective(260px) translateY(-30px) rotateY(360deg) scale(1.15); opacity: 0; }
        }
        .palco-3d-container {
            width: 100%;
            max-width: 920px;
            margin: 6px auto 0 auto;
            height: 134px;
            position: relative;
        }
        .musico-box {
            position: absolute;
            bottom: 14px;
            transform-origin: bottom center;
            filter: drop-shadow(0 4px 5px rgba(20, 26, 22, 0.18));
        }
        .m-brocolis { left: 16%; animation: soloGuitarra3D 1.6s ease-in-out infinite; }
        .m-cenoura  { left: 36%; animation: vocalistaShow3D 1.35s ease-in-out infinite; }
        .m-tomate   { left: 55%; animation: bateristaShow3D 0.55s ease-in-out infinite; }
        .m-vagem    { left: 74%; animation: baixistaGroove3D 1.5s ease-in-out infinite; }

        .prato-anim { transform-box: fill-box; transform-origin: center; animation: pratoVibra 0.55s ease-in-out infinite; }
        .be-anim { transform-box: fill-box; transform-origin: bottom right; animation: baqE 0.55s ease-in-out infinite; }
        .bd-anim { transform-box: fill-box; transform-origin: bottom left; animation: baqD 0.55s ease-in-out infinite; }
        .onda-1 { transform-box: fill-box; transform-origin: center; animation: ondaSom 1.4s ease-out infinite; }
        .onda-2 { transform-box: fill-box; transform-origin: center; animation: ondaSom 1.4s ease-out 0.7s infinite; }

        .nota-flut { position: absolute; pointer-events: none; }
        .nf-1 { left: 22%; top: 14px; animation: notaSobe3D 2.3s ease-out infinite; }
        .nf-2 { left: 41%; top: 10px; animation: notaSobe3D 2.6s ease-out 0.6s infinite; }
        .nf-3 { left: 59%; top: 14px; animation: notaSobe3D 2.1s ease-out 1.1s infinite; }
        .nf-4 { left: 78%; top: 12px; animation: notaSobe3D 2.5s ease-out 1.6s infinite; }
        </style>

        <div class="palco-3d-container">
            <!-- Chão do palco + Luz verde suave -->
            <svg width="100%" height="134" viewBox="0 0 920 134" fill="none" style="position:absolute; left:0; top:0;">
                <defs>
                    <radialGradient id="holofoteGrano" cx="50%" cy="88%" r="52%">
                        <stop offset="0%" stop-color="#4CAF50" stop-opacity="0.18"/>
                        <stop offset="100%" stop-color="#4CAF50" stop-opacity="0"/>
                    </radialGradient>
                </defs>
                <ellipse cx="460" cy="116" rx="370" ry="22" fill="url(#holofoteGrano)"/>
                <line x1="30" y1="118" x2="890" y2="118" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                <line x1="80" y1="124" x2="840" y2="124" stroke="#141A16" stroke-width="1.1" stroke-dasharray="6 8" opacity="0.42"/>
            </svg>

            <!-- Notas musicais girando em 3D -->
            <svg class="nota-flut nf-1" width="18" height="22" viewBox="0 0 18 22" fill="none">
                <circle cx="5" cy="17" r="3" fill="#1B5E20"/><path d="M8 17 V4 L15 2 V14" stroke="#1B5E20" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="14" r="3" fill="#1B5E20"/>
            </svg>
            <svg class="nota-flut nf-2" width="16" height="20" viewBox="0 0 16 20" fill="none">
                <circle cx="5" cy="15" r="3.2" fill="#1B5E20"/><path d="M8.2 15 V3 L14 5" stroke="#1B5E20" stroke-width="1.7" stroke-linecap="round"/>
            </svg>
            <svg class="nota-flut nf-3" width="18" height="22" viewBox="0 0 18 22" fill="none">
                <circle cx="5" cy="17" r="3" fill="#1B5E20"/><path d="M8 17 V4 L15 2 V14" stroke="#1B5E20" stroke-width="1.7" stroke-linecap="round"/><circle cx="12" cy="14" r="3" fill="#1B5E20"/>
            </svg>
            <svg class="nota-flut nf-4" width="16" height="20" viewBox="0 0 16 20" fill="none">
                <circle cx="5" cy="15" r="3.2" fill="#1B5E20"/><path d="M8.2 15 V3 L14 5" stroke="#1B5E20" stroke-width="1.7" stroke-linecap="round"/>
            </svg>

            <!-- 1. BRÓCOLIS GUITARRISTA (Óculos de Rockstar + Guitarra Elétrica) -->
            <div class="musico-box m-brocolis">
                <svg width="82" height="84" viewBox="0 0 82 84" fill="none">
                    <ellipse cx="32" cy="81" rx="18" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <!-- Pernas e Sapatinhos -->
                    <path d="M25 65 V79 M38 65 V79" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M20 80 H27 C27 77.5 22 77.5 20 80 Z M36 80 H43 C43 77.5 38 77.5 36 80 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <!-- Caule/Tronco com sombra -->
                    <path d="M22 41 L24 65 H39 L41 41 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                    <path d="M35 41 L34 65 H39 L41 41 Z" fill="#D5D0C5"/>
                    <!-- Copa do Brócolis em 2 camadas (volume) -->
                    <circle cx="16" cy="31" r="10" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7"/>
                    <circle cx="47" cy="31" r="10" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7"/>
                    <circle cx="31.5" cy="21" r="12" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.7"/>
                    <path d="M12 40 C6 36 8 25 16 25 C18 16 28 13 33 18 C39 13 49 17 49 26 C56 28 56 38 49 41 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.9" stroke-linejoin="round"/>
                    <path d="M20 27 C23 23 28 23 30 26 M36 28 C39 25 43 26 44 29" stroke="#2E7D32" stroke-width="1.3" stroke-linecap="round"/>
                    <!-- Óculos Escuros Rockstar + Sorriso -->
                    <path d="M22 46 H41" stroke="#141A16" stroke-width="1.5"/>
                    <rect x="23" y="45" width="7.5" height="5" rx="1.5" fill="#141A16"/>
                    <rect x="32.5" y="45" width="7.5" height="5" rx="1.5" fill="#141A16"/>
                    <line x1="25" y1="46.5" x2="27" y2="48.5" stroke="#FFFFFF" stroke-width="0.9" stroke-linecap="round"/>
                    <line x1="34.5" y1="46.5" x2="36.5" y2="48.5" stroke="#FFFFFF" stroke-width="0.9" stroke-linecap="round"/>
                    <path d="M29 53 Q32 56 35 53" stroke="#141A16" stroke-width="1.4" stroke-linecap="round"/>
                    <!-- Guitarra Elétrica + Bracinhos -->
                    <path d="M18 59 C14 55 17 49 23 51 L33 54 C36 55 36 61 31 62 L22 62 C19 62 18 60 18 59 Z" fill="#C8E6C9" stroke="#141A16" stroke-width="1.7"/>
                    <circle cx="25" cy="56.5" r="2.2" fill="#1B5E20"/>
                    <line x1="34" y1="54" x2="60" y2="43" stroke="#141A16" stroke-width="2.3" stroke-linecap="round"/>
                    <path d="M59 41 L64 39 L65 43 L60 45 Z" fill="#1B5E20" stroke="#141A16" stroke-width="1.3"/>
                    <!-- Bracinho direito palhetando e esquerdo no braço -->
                    <path d="M23 48 Q20 53 24 56" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                    <path d="M40 48 Q45 50 48 48" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                    <!-- Ondas sonoras -->
                    <path class="onda-1" d="M67 35 C71 39 71 45 67 49" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                    <path class="onda-2" d="M72 31 C77 37 77 47 72 53" stroke="#4CAF50" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
            </div>

            <!-- 2. CENOURA VOCALISTA (Topete Folhudo + Olhos Expressivos + Pedestal) -->
            <div class="musico-box m-cenoura">
                <svg width="74" height="88" viewBox="0 0 74 88" fill="none">
                    <ellipse cx="30" cy="85" rx="16" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <!-- Pernas e Sapatinhos -->
                    <path d="M24 68 V83 M35 68 V83" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M19 84 H26 C26 81.5 21 81.5 19 84 Z M34 84 H41 C41 81.5 36 81.5 34 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <!-- Topete de Folhas Verdes em Camadas -->
                    <path d="M29 22 C22 10 14 12 19 22 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                    <path d="M30 22 C28 8 34 8 32 22 Z" fill="#66BB6A" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                    <path d="M31 22 C38 10 45 13 39 22 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                    <!-- Corpo da Cenoura com Sombra Lateral e Ranhuras -->
                    <path d="M16 26 C16 19 43 19 43 26 L33 68 C32 71 27 71 26 68 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                    <path d="M37 22 C41 22 43 24 43 26 L33 68 C32 70 31 70 30 70 L37 22 Z" fill="#D5D0C5"/>
                    <path d="M19 34 H24 M35 44 H40 M21 53 H25" stroke="#141A16" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/>
                    <!-- Olhos com Brilho e Boca Cantando -->
                    <circle cx="25" cy="34" r="2.2" fill="#141A16"/>
                    <circle cx="24.3" cy="33.3" r="0.7" fill="#FFFFFF"/>
                    <circle cx="34" cy="34" r="2.2" fill="#141A16"/>
                    <circle cx="33.3" cy="33.3" r="0.7" fill="#FFFFFF"/>
                    <ellipse cx="29.5" cy="41.5" rx="2.6" ry="3.2" fill="#1B5E20" stroke="#141A16" stroke-width="1.4"/>
                    <!-- Bracinho esquerdo na cintura e direito no microfone -->
                    <path d="M17 42 Q11 46 18 50" stroke="#141A16" stroke-width="1.7" stroke-linecap="round"/>
                    <path d="M40 43 L49 38" stroke="#141A16" stroke-width="1.7" stroke-linecap="round"/>
                    <!-- Pedestal e Microfone Profissional -->
                    <line x1="54" y1="38" x2="54" y2="84" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <path d="M47 84 H61" stroke="#141A16" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="51" cy="36" r="4.2" fill="#1B5E20" stroke="#141A16" stroke-width="1.5"/>
                    <line x1="48" y1="35" x2="54" y2="37" stroke="#E8F5E9" stroke-width="1"/>
                    <path class="onda-1" d="M58 29 C62 33 62 39 58 43" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>

            <!-- 3. TOMATE BATERISTA (Fone de Retorno + Bateria Completa) -->
            <div class="musico-box m-tomate">
                <svg width="94" height="76" viewBox="0 0 94 76" fill="none">
                    <ellipse cx="47" cy="73" rx="30" ry="3.2" fill="#141A16" opacity="0.20"/>
                    <!-- Corpo do Tomate com Brilho -->
                    <ellipse cx="47" cy="36" rx="19" ry="15" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8"/>
                    <path d="M35 28 C37 25 41 24 44 25" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>
                    <!-- Coroa de Sépalas Verdes -->
                    <path d="M47 21 L39 16 L44 21 L47 13 L50 21 L55 16 L47 21 Z" fill="#81C784" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                    <!-- Fone de Retorno -->
                    <path d="M28 35 C28 22 66 22 66 35" stroke="#141A16" stroke-width="1.6"/>
                    <rect x="25.5" y="32" width="3.5" height="7" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                    <rect x="65" y="32" width="3.5" height="7" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                    <!-- Olhos com Brilho e Sorriso -->
                    <circle cx="41.5" cy="35" r="2" fill="#141A16"/>
                    <circle cx="40.9" cy="34.4" r="0.6" fill="#FFFFFF"/>
                    <circle cx="52.5" cy="35" r="2" fill="#141A16"/>
                    <circle cx="51.9" cy="34.4" r="0.6" fill="#FFFFFF"/>
                    <path d="M43.5 40.5 Q47 44 50.5 40.5" stroke="#141A16" stroke-width="1.5" stroke-linecap="round"/>
                    <!-- Baquetas Animadas -->
                    <line class="be-anim" x1="31" y1="39" x2="20" y2="26" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <line class="bd-anim" x1="63" y1="39" x2="74" y2="26" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <!-- Bumbo Central Duplo -->
                    <circle cx="47" cy="58" r="15" fill="#DDD8CE" stroke="#141A16" stroke-width="2"/>
                    <circle cx="47" cy="58" r="11.5" stroke="#141A16" stroke-width="1" stroke-dasharray="3 3"/>
                    <circle cx="47" cy="58" r="6" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.6"/>
                    <!-- Caixa à Esquerda -->
                    <rect x="17" y="47" width="15" height="9" rx="1.5" fill="#EAE7E0" stroke="#141A16" stroke-width="1.6"/>
                    <line x1="17" y1="50" x2="32" y2="50" stroke="#1B5E20" stroke-width="1.3"/>
                    <line x1="24.5" y1="56" x2="24.5" y2="73" stroke="#141A16" stroke-width="1.7"/>
                    <!-- Prato de Ataque à Direita -->
                    <line x1="74" y1="33" x2="74" y2="73" stroke="#141A16" stroke-width="1.7"/>
                    <ellipse class="prato-anim" cx="74" cy="33" rx="13" ry="2.8" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.8"/>
                </svg>
            </div>

            <!-- 4. VAGEM BAIXISTA (4 Ervilhas Expressivas + Contrabaixo) -->
            <div class="musico-box m-vagem">
                <svg width="80" height="88" viewBox="0 0 80 88" fill="none">
                    <ellipse cx="26" cy="85" rx="16" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <!-- Pernas e Sapatinhos -->
                    <path d="M21 69 V83 M31 69 V83" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M16 84 H23 C23 81.5 18 81.5 16 84 Z M30 84 H37 C37 81.5 32 81.5 30 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <!-- Cabinho Curvo no Topo -->
                    <path d="M27 15 C27 9 32 8 34 11" stroke="#1B5E20" stroke-width="2" stroke-linecap="round"/>
                    <!-- Casca da Vagem em 2 Tons -->
                    <path d="M27 15 C13 23 12 56 26 70 C40 56 39 23 27 15 Z" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.9" stroke-linejoin="round"/>
                    <path d="M27 18 C17 25 16 54 26 66 C36 54 35 25 27 18 Z" fill="#E8F5E9"/>
                    <!-- 4 Ervilhas / Grãos Internos -->
                    <circle cx="26" cy="27" r="4.6" fill="#DDD8CE" stroke="#141A16" stroke-width="1.4"/>
                    <circle cx="26" cy="38" r="5" fill="#DDD8CE" stroke="#141A16" stroke-width="1.4"/>
                    <circle cx="26" cy="50" r="5" fill="#DDD8CE" stroke="#141A16" stroke-width="1.4"/>
                    <circle cx="26" cy="61" r="4" fill="#DDD8CE" stroke="#141A16" stroke-width="1.4"/>
                    <!-- Rostinho da Ervilha Líder (Topo) -->
                    <circle cx="24.3" cy="26.2" r="1.2" fill="#141A16"/>
                    <circle cx="27.7" cy="26.2" r="1.2" fill="#141A16"/>
                    <path d="M24.5 28.8 Q26 30.5 27.5 28.8" stroke="#141A16" stroke-width="1.2" stroke-linecap="round"/>
                    <!-- Rostinho Sorrindo na 2ª Ervilha -->
                    <circle cx="24.5" cy="37.3" r="1" fill="#141A16"/>
                    <circle cx="27.5" cy="37.3" r="1" fill="#141A16"/>
                    <path d="M24.8 39.5 Q26 40.8 27.2 39.5" stroke="#141A16" stroke-width="1.1" stroke-linecap="round"/>
                    <!-- Contrabaixo + Bracinhos -->
                    <ellipse cx="25" cy="52" rx="10" ry="5.8" transform="rotate(-15 25 52)" fill="#A5D6A7" stroke="#141A16" stroke-width="1.7"/>
                    <circle cx="23" cy="52.5" r="2" fill="#141A16"/>
                    <line x1="34" y1="49" x2="60" y2="41" stroke="#141A16" stroke-width="2.3" stroke-linecap="round"/>
                    <rect x="59" y="38.5" width="5" height="4" rx="1" transform="rotate(-15 59 38.5)" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                    <path d="M16 45 Q14 50 19 52" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                    <path d="M36 44 Q42 46 46 44" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                    <path class="onda-1" d="M67 34 C71 38 71 44 67 48" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
        </div>
        """,
        height=138
    )
    
elif aba == "📊 Análise de Pedidos":
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

    feriados_sys = obter_feriados_sistema()
    mapa_lt = obter_mapa_lead_time()

    c_up_bi, c_cfg_bi = st.columns((3, 1))
    with c_up_bi:
        arquivo_bi = st.file_uploader("📂 Importar Planilha de Pedidos do BI (.xls, .xlsx, .csv):", type=("xls", "xlsx", "csv"), key="up_bi_analise")
    with c_cfg_bi:
        limite_critico = st.number_input("⚠️ Limite Crítico (dias úteis p/ carregar):", min_value=0.0, max_value=15.0, value=2.0, step=0.5)

    if arquivo_bi is not None:
        st.session_state["bi_cache_nome"] = arquivo_bi.name
        st.session_state["bi_cache_bytes"] = arquivo_bi.getvalue()

    if st.session_state.get("bi_cache_bytes") is not None:
        try:
            nome_arq_bi = st.session_state["bi_cache_nome"].lower()
            arquivo_bi = io.BytesIO(st.session_state["bi_cache_bytes"])
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
                    col_dt_cria = m5.selectbox("Data de Criação/Lançamento:", cols_bi, index=achar_idx_bi(("CRIADA", "LANCAMENTO", "CRIACAO", "EMISSAO", "FATURAMENTO", "DATA PEDIDO", "INCLUSAO", "DATA")))
                    col_dt_ent = m6.selectbox("Data de Entrega:", cols_bi, index=achar_idx_bi(("ENTREGA", "PREVISAO", "AGENDAMENTO", "PRAZO")))
                    val_enc = achar_col_bi(cols_bi, ("VALOR", "TOTAL", "FATURAMENTO", "PRECO", "VLR"))
                    col_val_bi = m7.selectbox("Valor do Pedido (R$):", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(val_enc) + 1) if val_enc in cols_bi else 0)
                    vol_enc = achar_col_bi(cols_bi, ("VOLUME", "CAIXA", "QTD", "QUANTIDADE", "UNIDADE"))
                    col_vol_bi = m8.selectbox("Qtd de Volumes:", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(vol_enc) + 1) if vol_enc in cols_bi else 0)

                    nf_enc = achar_col_bi(cols_bi, ("NOTA FISCAL", "NF", "NFE", "NOTA", "DANFE"))
                    col_nf_bi = st.selectbox("Nota Fiscal de Venda (Opcional — para vincular pedidos faturados):", ["(Nenhum)"] + cols_bi, index=(cols_bi.index(nf_enc) + 1) if nf_enc in cols_bi else 0)

                df_plan_exist = carregar_dados("planejamento")
                lista_peds_plan = list()
                if not df_plan_exist.empty and "Nº Pedido" in df_plan_exist.columns:
                    lista_peds_plan = df_plan_exist["Nº Pedido"].astype(str).tolist()

                hoje_dt = pd.Timestamp(datetime.now().date())
                linhas_analise = list()
                cidades_sem_lt = set()
                alteracoes_entrega = list()

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
                        dias_rota = round(max(0.0, lt_dias - 5.0), 1)
                        dt_sug_carreg = subtrair_dias_uteis(dt_e, dias_rota, feriados_sys)
                        uteis_desde_criacao = contar_dias_uteis_entre(dt_c, hoje_dt, feriados_sys)
                        uteis_ate_carreg = contar_dias_uteis_entre(hoje_dt, dt_sug_carreg, feriados_sys)
                        janela_exp = uteis_ate_carreg

                        if uteis_ate_carreg < 0:
                            status_sla = "🔴 Atrasado p/ Carregar"
                            ordem_prio = 1
                        elif uteis_ate_carreg == 0:
                            status_sla = "🟠 Carregar Hoje"
                            ordem_prio = 2
                        elif uteis_ate_carreg <= limite_critico or uteis_desde_criacao > 1:
                            status_sla = "🟡 Atenção / Operação Apertada"
                            ordem_prio = 3
                        else:
                            status_sla = "🟢 Viável / No Prazo"
                            ordem_prio = 4

                        dt_lim_str = dt_sug_carreg.strftime("%d/%m/%Y")
                        obs_criacao = f"{uteis_desde_criacao}d úteis (SLA 1d)" if uteis_desde_criacao <= 1 else f"⚠️ {uteis_desde_criacao}d úteis (perdeu {uteis_desde_criacao - 1}d)"
                        rota_str = f"{lt_dias}d ({dias_rota}d rota)"
                    else:
                        janela_exp = None
                        dt_lim_str = "-"
                        obs_criacao = "-"
                        rota_str = f"{lt_dias}d" if lt_dias is not None else "-"
                        status_sla = "⚪ Sem Lead Time / Data Inválida"
                        ordem_prio = 5

                    esta_no_plan = any(pedido_contido_no_planejamento(ped_val, p_ex) for p_ex in lista_peds_plan)
                    ja_wms = "🚚 Já no Planejamento" if esta_no_plan else "🆕 Novo (Fora do WMS)"
                    valor_fmt = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    if esta_no_plan and pd.notna(dt_e) and not df_plan_exist.empty:
                        nova_ent_str = dt_e.strftime("%d/%m/%Y")
                        for idx_pe, r_pe in df_plan_exist.iterrows():
                            if pedido_contido_no_planejamento(ped_val, r_pe.get("Nº Pedido", "")):
                                ent_ant_str = formatar_data_br_str(r_pe.get("Data da entrega", ""))
                                if ent_ant_str and ent_ant_str != nova_ent_str:
                                    alteracoes_entrega.append({
                                        "idx_plan": idx_pe,
                                        "Pedido": ped_val,
                                        "Cliente": cli_val or str(r_pe.get("Cliente", "")),
                                        "Entrega Anterior": ent_ant_str,
                                        "Nova Entrega (BI)": nova_ent_str,
                                        "Nova Sugestão Carreg.": dt_lim_str
                                    })

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
                        "Tempo Parado": obs_criacao,
                        "Entrega": dt_e.strftime("%d/%m/%Y") if pd.notna(dt_e) else "-",
                        "LT Total (Rota)": rota_str,
                        "Dias Úteis p/ Carregar": janela_exp,
                        "Sugestão Carregamento": dt_lim_str,
                        "Situação WMS": ja_wms
                    })

                df_res_bi = pd.DataFrame(linhas_analise)
                if not df_res_bi.empty:
                    df_res_bi = df_res_bi.sort_values(by=["Prioridade", "Dias Úteis p/ Carregar"], ascending=[True, True], na_position="last")

                    if alteracoes_entrega:
                        with st.container(border=True):
                            st.error(f"🚨 **ALERTA COMERCIAL: {len(alteracoes_entrega)} pedido(s) já programado(s) tiveram a Data de Entrega alterada no BI!**")
                            st.dataframe(pd.DataFrame(alteracoes_entrega).drop(columns=["idx_plan"]), use_container_width=True, hide_index=True)
                            if st.button("🔄 Atualizar Datas no Planejamento e Disparar Alerta para a Equipe", type="primary"):
                                st.cache_data.clear()
                                df_p_alt = carregar_dados("planejamento")
                                for col_p_a in COLUNAS_PLANEJAMENTO:
                                    if col_p_a not in df_p_alt.columns:
                                        df_p_alt[col_p_a] = ""
                                df_p_alt["Data da entrega"] = df_p_alt["Data da entrega"].astype(object)
                                df_p_alt["Notificação"] = df_p_alt["Notificação"].fillna("").astype(object)
                                qtd_alt = 0
                                for item_alt in alteracoes_entrega:
                                    i_p = item_alt["idx_plan"]
                                    if i_p in df_p_alt.index:
                                        df_p_alt.at[i_p, "Data da entrega"] = item_alt["Nova Entrega (BI)"]
                                        aviso_com = f"[PARA: TODOS] ⚠️ COMERCIAL ALTEROU DATA DE ENTREGA DO PEDIDO {item_alt['Pedido']}: DE {item_alt['Entrega Anterior']} PARA {item_alt['Nova Entrega (BI)']} (NOVA SUGESTÃO CARREG.: {item_alt['Nova Sugestão Carreg.']}) (SISTEMA BI)"
                                        nt_atual = str(df_p_alt.at[i_p, "Notificação"]).strip()
                                        if nt_atual and nt_atual.lower() not in ("nan", "none", "null"):
                                            if aviso_com not in nt_atual:
                                                df_p_alt.at[i_p, "Notificação"] = f"{nt_atual} || {aviso_com}"
                                        else:
                                            df_p_alt.at[i_p, "Notificação"] = aviso_com
                                        qtd_alt += 1
                                if qtd_alt > 0:
                                    salvar_dados(df_p_alt[COLUNAS_PLANEJAMENTO], "planejamento")
                                    st.cache_data.clear()
                                    st.success(f"🔔 {qtd_alt} pedido(s) atualizados no Planejamento e notificação disparada para toda a equipe!")
                                    st.rerun()

                    if cidades_sem_lt:
                        st.warning(f"⚠️ **{len(cidades_sem_lt)} cidade(s)** não encontrada(s) na aba `lead time`: {', '.join(sorted(list(cidades_sem_lt))[:10])}")

                    k1, k2, k3, k4, k5, k6 = st.columns(6)
                    k1.metric("📦 Total Pedidos", len(df_res_bi))
                    k2.metric("🔴/🟠 Críticos/Hoje", int(df_res_bi["Prioridade"].isin((1, 2)).sum()))
                    k3.metric("🟡 Atenção", int((df_res_bi["Prioridade"] == 3).sum()))
                    k4.metric("🟢 No Prazo", int((df_res_bi["Prioridade"] == 4).sum()))
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
                            nova_l["Data"] = r_esc["Sugestão Carregamento"] if r_esc["Sugestão Carregamento"] != "-" else ""
                            nova_l["Nº Pedido"] = r_esc["Pedido"]
                            nova_l["Valor Pedido"] = r_esc["Valor (R$)"]
                            nova_l["Cliente"] = r_esc["Cliente"]
                            nova_l["UF"] = r_esc["UF"]
                            nova_l["Cidade"] = r_esc["Cidade"]
                            nova_l["Data da entrega"] = r_esc["Entrega"] if r_esc["Entrega"] != "-" else ""
                            nova_l["Observação"] = f"SLA BI | {r_esc['Volumes']} vol | LT: {r_esc['LT Total (Rota)']} | {r_esc['Tempo Parado']}"
                            nova_l["Status"] = "⏳ Aguardando Veículo"
                            nova_l["Nota Fiscal"] = f"NF {r_esc['NF_Raw']}" if r_esc.get("NF_Raw") else ""
                            novos_plan.append(nova_l)

                        if novos_plan:
                            df_p_final = pd.concat([df_p_atual[COLUNAS_PLANEJAMENTO], pd.DataFrame(novos_plan)], ignore_index=True)
                            salvar_dados(df_p_final[COLUNAS_PLANEJAMENTO], "planejamento")
                            st.cache_data.clear()
                            st.success(f"🎉 {len(novos_plan)} pedido(s) adicionado(s) ao Planejamento sem alterar os existentes!")
                            st.rerun()

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

    df_plan_ativos = df_plan[df_plan["Nº Pedido"].astype(str).str.strip() != ""].copy()
    df_kpi_plan = df_plan_ativos.copy() if mes_escolhido == "Todos os meses" else df_plan_ativos[df_plan_ativos["_mes_ano_kpi"] == mes_escolhido].copy()

    total_prog_kpi = int(len(df_kpi_plan))
    soma_pedidos_kpi = float(pd.to_numeric(df_kpi_plan["Valor Pedido"].apply(converter_moeda_para_float), errors="coerce").fillna(0.0).sum()) if not df_kpi_plan.empty else 0.0
    soma_frete_kpi = float(pd.to_numeric(df_kpi_plan["Valor de Frete"].apply(converter_moeda_para_float), errors="coerce").fillna(0.0).sum()) if not df_kpi_plan.empty else 0.0
    perc_frete_kpi = (soma_frete_kpi / soma_pedidos_kpi * 100.0) if soma_pedidos_kpi > 0 else 0.0
    
    fmt_pedidos_kpi = f"R$ {soma_pedidos_kpi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    fmt_frete_kpi = f"R$ {soma_frete_kpi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    k_top1, k_top2, k_top3 = st.columns(3)
    k_top1.metric("📋 Total Programado", total_prog_kpi)
    k_top2.metric("💰 Valor Total dos Pedidos", fmt_pedidos_kpi)
    k_top3.metric("🚛 Valor Total de Frete", fmt_frete_kpi, delta=f"{perc_frete_kpi:.1f}% sobre pedidos".replace(".", ","), delta_color="inverse")

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
    df_exibir_plan = df_plan[df_plan["Nº Pedido"].astype(str).str.strip() != ""][COLUNAS_PLANEJAMENTO].copy()

    df_plan["Notificação"] = df_plan["Notificação"].astype(str).str.strip()
    login_atual_nt = st.session_state.get("login_usuario", "")
    nome_atual_nt = st.session_state.get("nome_usuario", "")

    def extrair_minhas_notifs(txt_raw):
        s_nt = str(txt_raw).strip()
        if not s_nt or s_nt.lower() in ("nan", "none", "null"):
            return list()
        login_u = limpar_texto(st.session_state.login_usuario)
        nome_u = limpar_texto(st.session_state.nome_usuario)
        minhas = list()
        for parte in s_nt.split(" || "):
            p_limpa = parte.strip()
            if not p_limpa:
                continue
            lidos_set = set()
            if "[LIDO:" in p_limpa:
                trecho_lidos = p_limpa.split("[LIDO:").pop(1).split("]").pop(0)
                lidos_set = {limpar_texto(u) for u in trecho_lidos.split(",") if limpar_texto(u)}
            if login_u in lidos_set or nome_u in lidos_set:
                continue
            if "[PARA:" not in p_limpa:
                minhas.append(p_limpa)
            else:
                destino = limpar_texto(p_limpa.split("[PARA:").pop(1).split("]").pop(0))
                if destino in ("TODOS", login_u, nome_u):
                    minhas.append(p_limpa)
        return minhas

    lista_alertas_plan = list()
    for idx_nt, row_nt in df_plan.iterrows():
        for msg_bruta in extrair_minhas_notifs(row_nt.get("Notificação", "")):
            lista_alertas_plan.append((idx_nt, row_nt, msg_bruta))

    if lista_alertas_plan:
        with st.container(border=True):
            st.error(f"🔔 **Você tem {len(lista_alertas_plan)} notificação(ões) importante(s)!**")
            st.markdown(
                """
                <style>
                div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stAlert"]) div.stButton > button {
                    background-color: #C65353 !important;
                    border: 1px solid #A83E3E !important;
                    color: #FFFFFF !important;
                }
                div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stAlert"]) div.stButton > button p {
                    color: #FFFFFF !important;
                    font-weight: 600 !important;
                }
                div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stAlert"]) div.stButton > button:hover {
                    background-color: #B24343 !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            for seq_nt, (idx_nt, row_nt, msg_bruta) in enumerate(lista_alertas_plan):
                c_nt_txt, c_nt_btn = st.columns((4, 1), vertical_alignment="center")
                msg_exibir = re.sub(r"^\[PARA:\s*[^\]]+\]\s*", "", msg_bruta).strip()
                msg_exibir = re.sub(r"\s*\[LIDO:\s*[^\]]+\]", "", msg_exibir).strip()
                msg_exibir = msg_exibir.replace("(DE: ", "(")
                c_nt_txt.markdown(
                    f"📌 **Pedido {row_nt['Nº Pedido']}** ({row_nt['Cliente']} - {row_nt['Data']} {row_nt['Hora']}): "
                    f"<span style='color: #0D3B16; font-weight: bold;'>{msg_exibir}</span>",
                    unsafe_allow_html=True
                )
                if c_nt_btn.button("✔️ Marcar como Lido", key=f"btn_ler_notif_{idx_nt}_{seq_nt}", use_container_width=True):
                    df_plan["Notificação"] = df_plan["Notificação"].fillna("").astype(object)
                    partes_atuais = [x.strip() for x in str(df_plan.at[idx_nt, "Notificação"]).split(" || ") if x.strip()]
                    if msg_bruta in partes_atuais:
                        idx_msg = partes_atuais.index(msg_bruta)
                        if "[PARA: TODOS]" in msg_bruta.upper():
                            login_leitor = limpar_texto(st.session_state.login_usuario)
                            if "[LIDO:" in msg_bruta:
                                base_m, resto_m = msg_bruta.split("[LIDO:", 1)
                                lidos_atual = resto_m.split("]", 1).pop(0).strip()
                                novos_lidos = f"{lidos_atual}, {login_leitor}" if lidos_atual else login_leitor
                                partes_atuais[idx_msg] = f"{base_m.strip()} [LIDO: {novos_lidos}]"
                            else:
                                partes_atuais[idx_msg] = f"{msg_bruta} [LIDO: {login_leitor}]"
                        else:
                            partes_atuais.remove(msg_bruta)
                    df_plan.at[idx_nt, "Notificação"] = " || ".join(partes_atuais)
                    salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.toast(f"✔️ Notificação do pedido {row_nt['Nº Pedido']} concluída!", icon="✔️")
                    st.rerun()

    if not df_exibir_plan.empty:
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
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Status"].apply(limpar_texto) == limpar_texto(filtro_status_plan)]
        if busca_livre.strip():
            termo = busca_livre.strip().lower()
            mask_busca = (
                df_exibir_plan["Nº Pedido"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Cliente"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Placa do veículo"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Transportadora"].astype(str).str.lower().str.contains(termo, na=False)
            )
            df_exibir_plan = df_exibir_plan[mask_busca]

        st_norm = df_exibir_plan["Status"].apply(limpar_texto)
        qtd_st1 = int((st_norm == limpar_texto("⏳ Aguardando Veículo")).sum())
        qtd_st2 = int((st_norm == limpar_texto("🚚 Veículo no Pátio")).sum())
        qtd_st3 = int((st_norm == limpar_texto("📦 Em Conferência")).sum())
        qtd_st4 = int((st_norm == limpar_texto("✅ Carregado / Liberado")).sum())
        qtd_st5 = int((st_norm == limpar_texto("⚠️ Atrasado / Ocorrência")).sum())

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("⏳ Aguardando Veículo", qtd_st1)
        k2.metric("🚚 Veículo no Pátio", qtd_st2)
        k3.metric("📦 Em Conferência", qtd_st3)
        k4.metric("✅ Carregado / Liberado", qtd_st4)
        k5.metric("⚠️ Atrasado / Ocorrência", qtd_st5)

        feriados_plan = obter_feriados_sistema()
        mapa_lt_plan = obter_mapa_lead_time()

        def calc_lt_e_sugestao(row_p):
            u_p = limpar_texto(row_p.get("UF", ""))
            c_p = limpar_texto(row_p.get("Cidade", ""))
            lt_v = mapa_lt_plan.get((u_p, c_p))
            if lt_v is None:
                return "-", "-"
            rota_v = round(max(0.0, lt_v - 5.0), 1)
            dt_ent_p = pd.to_datetime(str(row_p.get("Data da entrega", "")).strip(), dayfirst=True, errors="coerce")
            if pd.isna(dt_ent_p):
                return f"{lt_v}d ({rota_v}d rota)", "-"
            dt_sug_p = subtrair_dias_uteis(dt_ent_p, rota_v, feriados_plan)
            return f"{lt_v}d ({rota_v}d rota)", dt_sug_p.strftime("%d/%m/%Y")

        df_tab_plan = df_exibir_plan.drop(columns=["Notificação"], errors="ignore").copy()
        res_lt_plan = [list(t) for t in df_tab_plan.apply(calc_lt_e_sugestao, axis=1).tolist()]
        df_tab_plan["Lead Time"] = [x.pop(0) for x in res_lt_plan]
        df_tab_plan["Sugestão Carreg."] = [x.pop(0) for x in res_lt_plan]

        st.dataframe(
            df_tab_plan,
            use_container_width=True,
            hide_index=True,
            column_order=[
                "Data", "Hora", "Local de Carregamento", "Ordem de Carregamento",
                "Nº Pedido", "Valor Pedido", "Cliente", "Transportadora",
                "Placa do veículo", "Tipo de Veículo", "Valor de Frete",
                "UF", "Cidade", "CIF/FOB", "Veículo compartilhado",
                "Data da entrega", "Lead Time", "Sugestão Carreg.",
                "Observação", "Status", "Nota Fiscal"
            ],
            column_config={
                "Data": st.column_config.TextColumn("📅 Data", width="small"),
                "Hora": st.column_config.TextColumn("⏰ Hora", width="small"),
                "Local de Carregamento": st.column_config.TextColumn("🏭 Local", width="small"),
                "Ordem de Carregamento": st.column_config.TextColumn("📄 Ordem", width="small"),
                "Nº Pedido": st.column_config.TextColumn("📦 Pedido / Carga", width="medium"),
                "Valor Pedido": st.column_config.TextColumn("💰 Valor Pedido", width="small"),
                "Cliente": st.column_config.TextColumn("🏢 Cliente", width="medium"),
                "Transportadora": st.column_config.TextColumn("🚚 Transportadora", width="medium"),
                "Placa do veículo": st.column_config.TextColumn("🚛 Placa", width="small"),
                "Tipo de Veículo": st.column_config.TextColumn("🚐 Veículo", width="small"),
                "Valor de Frete": st.column_config.TextColumn("💵 Frete", width="small"),
                "UF": st.column_config.TextColumn("🗺️ UF", width="small"),
                "Cidade": st.column_config.TextColumn("📍 Cidade", width="medium"),
                "CIF/FOB": st.column_config.TextColumn("🔄 CIF/FOB", width="small"),
                "Veículo compartilhado": st.column_config.TextColumn("🤝 Compartilhado", width="small"),
                "Data da entrega": st.column_config.TextColumn("🏁 Entrega", width="small"),
                "Lead Time": st.column_config.TextColumn("⏱️ Lead Time", width="small"),
                "Sugestão Carreg.": st.column_config.TextColumn("🎯 Sugestão Carreg.", width="small"),
                "Observação": st.column_config.TextColumn("📝 Observação", width="large"),
                "Status": st.column_config.TextColumn("🚦 Status", width="medium"),
                "Nota Fiscal": st.column_config.TextColumn("🧾 Nota Fiscal", width="small"),
            }
        )
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
                        nt_c1, nt_c2, nt_c3, nt_c4 = st.columns((2, 2, 3, 1), vertical_alignment="bottom")
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
                                df_plan["Notificação"] = df_plan["Notificação"].fillna("").astype(object)
                                nova_msg_nt = f"[PARA: {dest_codigo}] {txt_nova_notif.strip().upper()} (DE: {st.session_state.nome_usuario})"
                                atual_nt = str(df_plan.at[idx_nt_alvo, "Notificação"]).strip()
                                if atual_nt and atual_nt.lower() not in ("nan", "none", "null"):
                                    df_plan.at[idx_nt_alvo, "Notificação"] = f"{atual_nt} || {nova_msg_nt}"
                                else:
                                    df_plan.at[idx_nt_alvo, "Notificação"] = nova_msg_nt
                                salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                                st.toast("🔔 Notificação enviada com sucesso!", icon="🔔")
                                st.rerun()
                            else:
                                st.error("⚠️ Digite a mensagem da notificação antes de salvar.")
    else:
        st.info("Nenhum pedido cadastrado no planejamento ainda.")    

    st.divider()

    with st.expander("➕ Incluir Pedido Manualmente"):
        st.caption("💡 Consulte rapidamente o trânsito e a data útil ideal de carregamento antes de preencher:")
        q_c1, q_c2, q_c3 = st.columns((1, 2, 2))
        q_uf = q_c1.text_input("UF p/ Consulta:", placeholder="Ex: DF", key="q_lt_uf")
        q_cid = q_c2.text_input("Cidade p/ Consulta:", placeholder="Ex: BRASILIA", key="q_lt_cid")
        q_ent = q_c3.text_input("Data Entrega Prevista:", placeholder="Ex: 26/11/2026", key="q_lt_ent")
        if q_uf.strip() and q_cid.strip():
            lt_q = obter_mapa_lead_time().get((limpar_texto(q_uf), limpar_texto(q_cid)))
            if lt_q is not None:
                rota_q = round(max(0.0, lt_q - 5.0), 1)
                dt_ent_q = pd.to_datetime(q_ent.strip(), dayfirst=True, errors="coerce") if q_ent.strip() else pd.NaT
                if pd.notna(dt_ent_q):
                    dt_sug_q = subtrair_dias_uteis(dt_ent_q, rota_q, obter_feriados_sistema())
                    st.info(f"⏱️ **{limpar_texto(q_cid)}/{limpar_texto(q_uf)}:** Lead Time Total `{lt_q}d` (`{rota_q}d` de rota) | 🎯 **Sugestão de Carregamento (dia útil):** **{dt_sug_q.strftime('%d/%m/%Y')}**")
                else:
                    st.info(f"⏱️ **{limpar_texto(q_cid)}/{limpar_texto(q_uf)}:** Lead Time Total `{lt_q}d` (`{rota_q}d` de rota). Informe a data de entrega ao lado para ver a data sugerida.")
            else:
                st.warning(f"⚠️ Cidade **{limpar_texto(q_cid)}/{limpar_texto(q_uf)}** não encontrada na aba `lead time`.")
        
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
                        "Notificação": "",
                        "Nota Fiscal": ""
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

        texto_botao = "🚀 Importar Pedido" if len(arquivos_pedidos) == 1 else f"🚀 Enviar {len(arquivos_pedidos)} Pedidos para Conferência"

        _, col_btn_imp = st.columns((4, 1))
        if col_btn_imp.button(texto_botao, type="primary", use_container_width=True, disabled=tem_erro_id):    
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
        for _, r_p in df_plan_gp.iterrows():
                val_str = str(r_p.get("validado", "")).strip()
                nf_str = str(r_p.get("Nota Fiscal", "")).strip()
                for col_chave in ("Nº Pedido", "id_carga"):
                    ped_p_str = str(r_p.get(col_chave, "")).strip()
                    if not ped_p_str or ped_p_str.lower() in ("nan", "none"):
                        continue
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
        st.dataframe(
            pd.DataFrame(lista_pendentes),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Carga / Pedido": st.column_config.TextColumn("📦 Carga / Pedido", width="medium"),
                "Nota Fiscal": st.column_config.TextColumn("🧾 Nota Fiscal", width="small"),
                "Qtd de SKUs": st.column_config.NumberColumn("🏷️ SKUs", width="small"),
                "Volumes Pedidos": st.column_config.NumberColumn("📋 Pedidos", width="small"),
                "Volumes Bipados": st.column_config.NumberColumn("✅ Bipados", width="small"),
                "Falta Bipar": st.column_config.NumberColumn("⚠️ Falta Bipar", width="small"),
                "Situação": st.column_config.TextColumn("🚦 Situação", width="medium"),
            }
        )
    else:
        st.success("🎉 Nenhuma carga pendente! Todas as cargas cadastradas já foram conferidas.")

    st.subheader("✅ Pedidos Conferidos (100% Concluídos)")
    if lista_concluidas:
        st.dataframe(
            pd.DataFrame(lista_concluidas),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Carga / Pedido": st.column_config.TextColumn("📦 Carga / Pedido", width="medium"),
                "Nota Fiscal": st.column_config.TextColumn("🧾 Nota Fiscal", width="small"),
                "Qtd de SKUs": st.column_config.NumberColumn("🏷️ SKUs", width="small"),
                "Volumes Pedidos": st.column_config.NumberColumn("📋 Pedidos", width="small"),
                "Volumes Bipados": st.column_config.NumberColumn("✅ Bipados", width="small"),
                "Conferido em": st.column_config.TextColumn("📅 Conferido em", width="small"),
                "Conferido por": st.column_config.TextColumn("👤 Conferido por", width="medium"),
                "Lacre": st.column_config.TextColumn("🔒 Lacre", width="small"),
                "Situação": st.column_config.TextColumn("🚦 Situação", width="medium"),
                "Validação Final": st.column_config.TextColumn("🛡️ Validação Final", width="medium"),
            }
        )
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

        def extrair_notifs_conf(row_p):
            ped_plan_txt = limpar_texto(row_p.get("Nº Pedido", ""))
            id_carga_plan_txt = limpar_texto(row_p.get("id_carga", ""))
            txt_nt = str(row_p.get("Notificação", "")).strip()
            if not txt_nt or txt_nt.lower() in ("nan", "none", "null"):
                return list()

            # Aceita notificação geral (sem pedido) ou que contenha o número do pedido/carga
            eh_geral = (not ped_plan_txt and not id_carga_plan_txt) or ped_plan_txt == "GERAL"
            bate_carga = False
            if carga_alvo_limpa:
                if carga_alvo_limpa in ped_plan_txt or (ped_plan_txt and ped_plan_txt in carga_alvo_limpa):
                    bate_carga = True
                elif carga_alvo_limpa in id_carga_plan_txt or (id_carga_plan_txt and id_carga_plan_txt in carga_alvo_limpa):
                    bate_carga = True

            if not eh_geral and not bate_carga:
                return list()

            login_u_c = limpar_texto(login_conf_nt)
            nome_u_c = limpar_texto(nome_conf_nt)
            minhas_c = list()
            for parte in txt_nt.split(" || "):
                p_limpa = parte.strip()
                if not p_limpa:
                    continue
                lidos_c = set()
                if "[LIDO:" in p_limpa:
                    trecho_l = p_limpa.split("[LIDO:").pop(1).split("]").pop(0)
                    lidos_c = {limpar_texto(u) for u in trecho_l.split(",") if limpar_texto(u)}
                if login_u_c in lidos_c or nome_u_c in lidos_c:
                    continue
                if "[PARA:" not in p_limpa:
                    minhas_c.append(p_limpa)
                else:
                    destino = limpar_texto(p_limpa.split("[PARA:").pop(1).split("]").pop(0))
                    if destino in ("TODOS", "CONFERENTE", "CONFERENTES", login_u_c, nome_u_c):
                        minhas_c.append(p_limpa)
            return minhas_c

        lista_alertas_conf = list()
        for idx_nc, row_nc in df_plan_conf.iterrows():
            for msg_bruta_nc in extrair_notifs_conf(row_nc):
                lista_alertas_conf.append((idx_nc, row_nc, msg_bruta_nc))

        if lista_alertas_conf:
            with st.container(border=True):
                st.error(f"🔔 **ATENÇÃO NESTA CARGA ({carga_selecionada}) — {len(lista_alertas_conf)} notificação(ões):**")
                for i_nc, (idx_nc, row_nc, msg_bruta_nc) in enumerate(lista_alertas_conf):
                    cc_txt, cc_btn = st.columns((4, 1), vertical_alignment="center")
                    msg_nc = re.sub(r"^\[PARA:\s*[^\]]+\]\s*", "", msg_bruta_nc).strip()
                    msg_nc = re.sub(r"\s*\[LIDO:\s*[^\]]+\]", "", msg_nc).strip().replace("(DE: ", "(")
                    cc_txt.markdown(
                        f"📌 <span style='color: #0D3B16; font-weight: bold;'>{msg_nc}</span>",
                        unsafe_allow_html=True
                    )
                    if cc_btn.button("✔️ Marcar como Lido", key=f"btn_ler_notif_conf_{idx_nc}_{i_nc}", use_container_width=True):
                        df_plan_conf["Notificação"] = df_plan_conf["Notificação"].fillna("").astype(object)
                        partes_c = [x.strip() for x in str(df_plan_conf.at[idx_nc, "Notificação"]).split(" || ") if x.strip()]
                        if msg_bruta_nc in partes_c:
                            idx_mc = partes_c.index(msg_bruta_nc)
                            if "[PARA: TODOS]" in msg_bruta_nc.upper() or "[PARA: CONFERENTE" in msg_bruta_nc.upper():
                                leitor_c = limpar_texto(login_conf_nt)
                                if "[LIDO:" in msg_bruta_nc:
                                    base_c, resto_c = msg_bruta_nc.split("[LIDO:", 1)
                                    lidos_at_c = resto_c.split("]", 1).pop(0).strip()
                                    novos_lidos_c = f"{lidos_at_c}, {leitor_c}" if lidos_at_c else leitor_c
                                    partes_c[idx_mc] = f"{base_c.strip()} [LIDO: {novos_lidos_c}]"
                                else:
                                    partes_c[idx_mc] = f"{msg_bruta_nc} [LIDO: {leitor_c}]"
                            else:
                                partes_c.remove(msg_bruta_nc)
                        df_plan_conf.at[idx_nc, "Notificação"] = " || ".join(partes_c)
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

    c_sel_pa, c_btn_pa, _ = st.columns((2.0, 1.0, 3.0), vertical_alignment="bottom")
    carga_selecionada = c_sel_pa.selectbox("Selecione a Carga:", df_todas_cargas["id_carga"].unique().tolist(), key="sel_carga_painel")
    if c_btn_pa.button("🔄 Atualizar Dados", type="primary"):
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
            cp_lac1, cp_lac2, _ = st.columns((2.0, 0.8, 2.2), vertical_alignment="bottom")
            novo_lacre_painel = cp_lac1.text_input(
                "🔒 Número do Lacre da Carga:",
                value="",
                placeholder="Digite o número do lacre...",
                key=f"input_lacre_painel_{carga_selecionada}"
            )
            if cp_lac2.button("💾 Salvar Lacre", type="primary", key=f"btn_lacre_painel_{carga_selecionada}"):
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
    st.markdown(
        """
        <style>
        section[data-testid="stMain"] button[data-testid="stBaseButton-primary"] {
            background-color: #1F2922 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 20px !important;
            min-height: 38px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
            transition: all 0.15s ease !important;
        }
        section[data-testid="stMain"] button[data-testid="stBaseButton-primary"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
        section[data-testid="stMain"] button[data-testid="stBaseButton-primary"]:hover {
            background-color: #1B5E20 !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    

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
    eh_gestao_aud = st.session_state.get("perfil_usuario", "") in ("ADMIN", "GERENTE", "SUPERVISOR", "ANALISTA")
    mostrar_validadas = False
    if eh_gestao_aud:
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
                st.cache_data.clear()
                df_plan_lote = carregar_dados("planejamento")
                if df_plan_lote is None:
                    st.error("⚠️ Falha temporária ao ler a aba 'planejamento'. Tente novamente em 3 segundos.")
                    st.stop()
                for c_pl in COLUNAS_PLANEJAMENTO:
                    if c_pl not in df_plan_lote.columns:
                        df_plan_lote[c_pl] = ""
                df_plan_lote = df_plan_lote.fillna("").astype(object)

                novas_linhas_lote = list()
                for cid_ant in cargas_lote_escolhidas:
                    cid_l = limpar_texto(cid_ant)
                    mask_match = (df_plan_lote["id_carga"].apply(limpar_texto) == cid_l) | (df_plan_lote["Nº Pedido"].apply(limpar_texto) == cid_l)
                    if mask_match.any():
                        df_plan_lote.loc[mask_match, "validado"] = "Auditado (Histórico)"
                    else:
                        nl = {col: "" for col in COLUNAS_PLANEJAMENTO}
                        nl["id_carga"] = cid_ant
                        nl["Status"] = "✅ Carregado / Liberado"
                        nl["validado"] = "Auditado (Histórico)"
                        novas_linhas_lote.append(nl)

                if novas_linhas_lote:
                    df_plan_lote = pd.concat([df_plan_lote[COLUNAS_PLANEJAMENTO], pd.DataFrame(novas_linhas_lote)], ignore_index=True)

                salvar_dados(df_plan_lote[COLUNAS_PLANEJAMENTO], "planejamento")
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
        
    carga_ja_encerrada = limpar_texto(carga_selecionada) in cargas_ja_validadas
    if carga_ja_encerrada:
        st.info("🔒 **Carga já validada e encerrada:** correções de lote, quantidade e estornos estão bloqueados para preservar o histórico.")
        if st.session_state.get("perfil_usuario", "") in ("ADMIN", "GERENTE","SUPERVISOR"):
            if st.button("🔓 Reabrir Carga para Correção (Exclusivo Gestão)", key="btn_reabrir_auditoria"):
                df_p_reab = carregar_dados("planejamento")
                if not df_p_reab.empty and "id_carga" in df_p_reab.columns and "validado" in df_p_reab.columns:
                    df_p_reab["validado"] = df_p_reab["validado"].astype(object)
                    df_p_reab.loc[df_p_reab["id_carga"].apply(limpar_texto) == limpar_texto(carga_selecionada), "validado"] = ""
                    salvar_dados(df_p_reab, "planejamento")
                    st.cache_data.clear()
                    st.warning(f"🔓 Carga **{carga_selecionada}** reaberta pela gestão para ajustes!")
                    st.rerun()

    if not carga_ja_encerrada and tem_permissao("↩️ Estornar Etiquetas e Corrigir Lotes"):
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

        _, col_btn_gerar_aud = st.columns((3.5, 1.5))
        if col_btn_gerar_aud.button("⚖️ Gerar Validação Tripla + Lotes", type="primary", use_container_width=True):
                
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
            _, col_btn_val_aud = st.columns((3.2, 1.8))
            if col_btn_val_aud.button("✅ Validar Pedido e Liberar para Expedição", type="primary", use_container_width=True):    
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
    st.caption("Administração de acessos, perfis operacionais, módulos liberados e travas de segurança da equipe.")
    st.markdown(
        """
        <style>
        /* Botões de ação de formulário compactos e modernos */
        section[data-testid="stMain"] [data-testid="stForm"] button[kind="primaryFormSubmit"],
        section[data-testid="stMain"] [data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] {
            background-color: #1F2922 !important;
            border: 1px solid #4CAF50 !important;
            border-radius: 20px !important;
            padding: 6px 24px !important;
            min-height: 36px !important;
            width: auto !important;
            float: right !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
            transition: all 0.15s ease !important;
        }
        section[data-testid="stMain"] [data-testid="stForm"] button[kind="primaryFormSubmit"] p,
        section[data-testid="stMain"] [data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] p {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }
        section[data-testid="stMain"] [data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
        section[data-testid="stMain"] [data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
            background-color: #1B5E20 !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    df_usuarios = carregar_usuarios_sistema()

    u_m1, u_m2, u_m3, u_m4 = st.columns(4)
    u_m1.metric("👥 Total da Equipe", len(df_usuarios))
    u_m2.metric("🟢 Usuários Ativos", int((df_usuarios["ativo"].apply(limpar_texto) == "SIM").sum()))
    u_m3.metric("🔴 Bloqueados / Inativos", int((df_usuarios["ativo"].apply(limpar_texto) != "SIM").sum()))
    u_m4.metric("🛡️ Administradores", int((df_usuarios["perfil"].apply(limpar_texto) == "ADMIN").sum()))

    st.divider()

    c_tit_u, c_busca_u = st.columns((2.5, 1.5), vertical_alignment="center")
    c_tit_u.subheader("📋 Diretório da Equipe")
    busca_u = c_busca_u.text_input("Buscar usuário:", placeholder="🔍 Filtrar por nome, login ou perfil...", label_visibility="collapsed")

    df_vis_users = df_usuarios.copy()
    if busca_u.strip():
        t_u = busca_u.strip().lower()
        mask_u = (
            df_vis_users["nome"].astype(str).str.lower().str.contains(t_u, na=False) |
            df_vis_users["login"].astype(str).str.lower().str.contains(t_u, na=False) |
            df_vis_users["perfil"].astype(str).str.lower().str.contains(t_u, na=False)
        )
        df_vis_users = df_vis_users[mask_u]

    def fmt_lista_tags(val_str, vazio_txt="—"):
        s = str(val_str).strip()
        if not s or s.lower() in ("nan", "none", "null"):
            return vazio_txt
        itens = [x.strip() for x in s.split("|") if x.strip() and x.strip().lower() != "none"]
        return "  •  ".join(itens) if itens else vazio_txt

    df_tabela_u = pd.DataFrame({
        "Login": df_vis_users["login"].apply(limpar_texto),
        "Colaborador": df_vis_users["nome"].apply(limpar_texto),
        "Cargo / Perfil": df_vis_users["perfil"].apply(limpar_texto),
        "Módulos Liberados": df_vis_users["modulos_liberados"].apply(lambda v: fmt_lista_tags(v, "Nenhum módulo")),
        "Permissões Críticas": df_vis_users["permissoes"].apply(lambda v: fmt_lista_tags(v, "Padrão (Sem ações críticas)")),
        "Status": df_vis_users["ativo"].apply(lambda v: "🟢 Ativo" if limpar_texto(v) == "SIM" else "🔴 Inativo")
    })

    st.dataframe(
        df_tabela_u,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Login": st.column_config.TextColumn("🔑 Login", width="small"),
            "Colaborador": st.column_config.TextColumn("👤 Colaborador", width="medium"),
            "Cargo / Perfil": st.column_config.TextColumn("🏷️ Perfil", width="small"),
            "Módulos Liberados": st.column_config.TextColumn("📂 Módulos Liberados", width="large"),
            "Permissões Críticas": st.column_config.TextColumn("🛡️ Permissões Críticas", width="large"),
            "Status": st.column_config.TextColumn("🚦 Status", width="small"),
        }
    )

    st.divider()

    PRESETS_PERFIL = {
        "CONFERENTE": (["📦 Conferência dos Pedidos"], []),
        "AUXILIAR ADMINISTRATIVO": (["🚚 Planejamento Logística", "📥 Importação de Pedidos", "📋 Gestão de Pedidos"], ["🔔 Lançar Notificações"]),
        "ANALISTA": (["📊 Análise de Pedidos", "🚚 Planejamento Logística", "📥 Importação de Pedidos", "📈 Painel de Acompanhamento", "📋 Gestão de Pedidos", "✅ Auditoria e Ajustes"], ["✂️ Gerar e Editar Cortes", "🔔 Lançar Notificações"]),
        "SUPERVISOR": (TODOS_MODULOS_SISTEMA[:-1], ["✂️ Gerar e Editar Cortes", "↩️ Estornar Etiquetas e Corrigir Lotes", "🔔 Lançar Notificações", "👁️ Ver Conferência Completa (Supervisão)"]),
        "GERENTE": (TODOS_MODULOS_SISTEMA[:-1], TODAS_PERMISSOES_CRITICAS),
        "ADMIN": (TODOS_MODULOS_SISTEMA, TODAS_PERMISSOES_CRITICAS),
    }

    with st.expander("➕ Cadastrar Novo Colaborador", expanded=False):
        c_nu_top1, c_nu_top2 = st.columns((1.5, 2.5), vertical_alignment="center")
        nu_perfil = c_nu_top1.selectbox(
            "1️⃣ Escolha o Perfil Base (preenche acessos automaticamente):",
            ["CONFERENTE", "AUXILIAR ADMINISTRATIVO", "ANALISTA", "SUPERVISOR", "GERENTE", "ADMIN"],
            key="nu_perfil_preset"
        )
        nu_foto = c_nu_top2.file_uploader("📷 Foto de Perfil (Opcional — PNG ou JPG):", type=["png", "jpg", "jpeg"], key="nu_foto_upload")

        mods_sugeridos, perms_sugeridas = PRESETS_PERFIL.get(nu_perfil, (["📦 Conferência dos Pedidos"], []))

        with st.form("form_novo_usuario", clear_on_submit=True):
            nu_c1, nu_c2, nu_c3 = st.columns(3)
            nu_nome = nu_c1.text_input("Nome Completo*:", placeholder="Ex: JOÃO SILVA")
            nu_login = nu_c2.text_input("Login de Acesso*:", placeholder="Ex: JOAO.SILVA")
            nu_senha = nu_c3.text_input("Senha Inicial*:", type="password", placeholder="Mínimo 4 caracteres")

            nu_mods = st.multiselect(
                "📂 Módulos / Telas Liberadas (personalizável):",
                TODOS_MODULOS_SISTEMA,
                default=mods_sugeridos
            )
            nu_perms = st.multiselect(
                "🛡️ Permissões de Ações Críticas (personalizável):",
                TODAS_PERMISSOES_CRITICAS,
                default=perms_sugeridas
            )

            _, col_btn_criar = st.columns((4, 1))
            if col_btn_criar.form_submit_button("💾 Criar Usuário", type="primary", use_container_width=True):
                
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
                        "foto_b64": processar_foto_avatar(nu_foto),
                        "ultimo_acesso": ""
                    }])
                    df_u_final = pd.concat([df_usuarios, novo_u], ignore_index=True)
                    salvar_dados(df_u_final[COLUNAS_USUARIOS], "usuarios")
                    if nu_foto is not None:
                        ok_gh, msg_gh = salvar_foto_github(login_novo, nu_foto)
                        if not ok_gh:
                            st.warning(f"⚠️ Usuário criado, mas houve falha ao enviar a foto: {msg_gh}")

                    st.success(f"✅ Colaborador **{nome_novo}** (`{login_novo}`) cadastrado com sucesso!")
                    st.rerun()

    with st.expander("✏️ Editar Acessos, Foto, Senha ou Bloquear Colaborador", expanded=True):
        opcoes_u = {
            f"{limpar_texto(r['nome'])} ({limpar_texto(r['login'])}) — {limpar_texto(r['perfil'])} [{'🟢 Ativo' if limpar_texto(r['ativo']) == 'SIM' else '🔴 Inativo'}]": idx
            for idx, r in df_usuarios.iterrows()
        }
        sel_u_label = st.selectbox("Selecione o colaborador:", list(opcoes_u.keys()), key="sel_edit_usuario")
        idx_u_edit = opcoes_u[sel_u_label]
        reg_u = df_usuarios.loc[idx_u_edit]

        login_ed_limpo = limpar_texto(reg_u["login"])
        nome_ed_limpo = limpar_texto(reg_u["nome"])
        foto_ed_b64 = carregar_foto_usuario(login_ed_limpo)
        ini_ed = "".join(p[:1] for p in nome_ed_limpo.split()[:2]).upper() if nome_ed_limpo else "U"
        cor_badge_st = "#2E7D32" if limpar_texto(reg_u["ativo"]) == "SIM" else "#C62828"
        txt_badge_st = "ATIVO" if limpar_texto(reg_u["ativo"]) == "SIM" else "INATIVO"

        if foto_ed_b64:
            av_card_html = f'<img src="data:image/png;base64,{foto_ed_b64}" style="width:52px; height:52px; border-radius:50%; object-fit:cover; border:2px solid #4CAF50;">'
        else:
            av_card_html = f'<div style="width:52px; height:52px; border-radius:50%; background:#1F2922; color:#E6E1D6; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.05rem; border:2px solid #4CAF50;">{ini_ed}</div>'

        c_card_u, c_foto_u = st.columns((2.2, 1.8), vertical_alignment="center")
        with c_card_u:
            st.markdown(
                f"""
                <div style="background:#E4E0D6; border:1px solid rgba(27,94,32,0.35); border-radius:12px; padding:10px 14px; display:flex; align-items:center; gap:12px;">
                    {av_card_html}
                    <div>
                        <div style="font-weight:700; font-size:0.95rem; color:#141A16;">{nome_ed_limpo} <span style="font-size:0.75rem; color:#4A524C;">(@{login_ed_limpo})</span></div>
                        <div style="margin-top:4px; display:flex; gap:6px; align-items:center;">
                            <span style="background:#1F2922; color:#FFFFFF; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:600;">{limpar_texto(reg_u['perfil'])}</span>
                            <span style="background:{cor_badge_st}; color:#FFFFFF; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:600;">{txt_badge_st}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_foto_u:
            ed_foto = st.file_uploader("📷 Atualizar Foto (PNG/JPG):", type=["png", "jpg", "jpeg"], key=f"ed_foto_{idx_u_edit}")

        mods_atuais = [m.strip() for m in str(reg_u["modulos_liberados"]).split("|") if m.strip() in TODOS_MODULOS_SISTEMA]
        perms_atuais = [p.strip() for p in str(reg_u["permissoes"]).split("|") if p.strip() in TODAS_PERMISSOES_CRITICAS]
        perfis_lista = ["CONFERENTE", "AUXILIAR ADMINISTRATIVO", "ANALISTA", "SUPERVISOR", "GERENTE", "ADMIN"]
        idx_perf = perfis_lista.index(limpar_texto(reg_u["perfil"])) if limpar_texto(reg_u["perfil"]) in perfis_lista else 0

        with st.form("form_editar_usuario"):
            eu_c1, eu_c2, eu_c3, eu_c4 = st.columns(4)
            eu_nome = eu_c1.text_input("Nome Completo:", value=str(reg_u["nome"]))
            eu_perfil = eu_c2.selectbox("Perfil Base:", perfis_lista, index=idx_perf)
            eu_ativo = eu_c3.selectbox("Status de Acesso:", ["SIM", "NÃO"], index=0 if limpar_texto(reg_u["ativo"]) == "SIM" else 1)
            eu_nova_senha = eu_c4.text_input("Nova Senha (vazio p/ manter):", type="password")

            eu_mods = st.multiselect("📂 Módulos / Telas Liberadas:", TODOS_MODULOS_SISTEMA, default=mods_atuais)
            eu_perms = st.multiselect("🛡️ Permissões de Ações Críticas:", TODAS_PERMISSOES_CRITICAS, default=perms_atuais)

            _, col_btn_salvar = st.columns((4, 1))
            if col_btn_salvar.form_submit_button("💾 Salvar Alterações do Usuário", type="primary", use_container_width=True):
                
                mods_ed = TODOS_MODULOS_SISTEMA if eu_perfil == "ADMIN" else eu_mods
                perms_ed = TODAS_PERMISSOES_CRITICAS if eu_perfil == "ADMIN" else eu_perms

                if login_ed_limpo == st.session_state.login_usuario:
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
                st.success(f"✅ Acessos e dados de **{limpar_texto(eu_nome)}** atualizados com sucesso!")
                st.rerun()

