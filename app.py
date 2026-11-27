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
    /* === LOADER EXECUTIVO GRANO (G + ANEL GIRANDO) === */
    @keyframes giroAnelGrano {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
    div[data-testid="stAppViewContainer"][aria-busy="true"]::before,
    .stApp[data-test-script-state="running"]::before {
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 58px;
        height: 58px;
        background-color: transparent;
        border-radius: 50%;
        box-shadow: 0 0 0 9999px rgba(201, 197, 186, 0.42);
        z-index: 999990;
        pointer-events: none;
    }
    div[data-testid="stAppViewContainer"][aria-busy="true"]::after,
    .stApp[data-test-script-state="running"]::after {
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        width: 68px;
        height: 68px;
        border-radius: 50%;
        border: 3.5px solid rgba(27, 94, 32, 0.18);
        border-top-color: #1B5E20;
        border-right-color: #4CAF50;
        animation: giroAnelGrano 0.75s linear infinite;
        z-index: 999991;
        pointer-events: none;
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
    </style>
    """,
    unsafe_allow_html=True
)
_SVG_LOGO_GRANO = f'<svg xmlns="{"http://www." + "w3.org/2000/svg"}" viewBox="0 0 100 100"><path fill="none" stroke="#1B5E20" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" d="M68 26 L50 16 L23 31.5 L23 68.5 L50 84 L77 68.5 L77 48 C77 35 65.5 27 52 27 C39 27 31 36.5 31 49.5 C31 61.5 40.5 70 52 70 C61.5 70 68 62.5 68 53 C68 44.5 61.5 39 53 39 C45.5 39 41 44.5 41 51 C41 55.5 44.5 59 49 59 C52.5 59 55 56 55 52.5"/></svg>'
_B64_LOGO_GRANO = base64.b64encode(_SVG_LOGO_GRANO.encode("utf-8")).decode("utf-8")
st.markdown(f'<style>div[data-testid="stAppViewContainer"][aria-busy="true"]::before,.stApp[data-test-script-state="running"]::before{{background-image:url("data:image/svg+xml;base64,{_B64_LOGO_GRANO}") !important;background-repeat:no-repeat !important;background-position:center !important;background-size:54px 54px !important;}}</style>', unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)
if st.session_state.get("toast_global"):
    st.toast(st.session_state.pop("toast_global"), icon="✅")

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

@st.cache_data(ttl=43200, show_spinner=False)
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
    if dt_alvo is None or pd.isna(dt_alvo):
        return pd.NaT
    try:
        ts = pd.Timestamp(dt_alvo)
        if pd.isna(ts):
            return pd.NaT
        d = ts.date()
    except Exception:
        return pd.NaT
    dias_corridos_rota = int(round(max(0.0, float(qtd_dias))))
    if dias_corridos_rota > 0:
        d = (pd.Timestamp(d) - pd.Timedelta(days=dias_corridos_rota)).date()
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
    import numpy as np
    fer_arr = np.array(sorted(list(feriados_set)), dtype="datetime64[D]") if feriados_set else np.array([], dtype="datetime64[D]")
    s1 = np.datetime64(d1.isoformat(), "D")
    s2 = np.datetime64(d2.isoformat(), "D")
    if d2 > d1:
        return int(np.busday_count(s1, s2, holidays=fer_arr))
    return -int(np.busday_count(s2, s1, holidays=fer_arr))

@st.cache_data(ttl=43200, show_spinner=False)
def obter_mapa_lead_time():
    df_lt = carregar_dados("lead time")
    mapa = {}
    if df_lt is not None and not df_lt.empty:
        col_uf, col_cid, col_dias, col_km, col_fc, col_ft = None, None, None, None, None, None
        for c in df_lt.columns:
            cl = limpar_texto(c)
            if not col_uf and cl in ("ESTADO", "UF"):
                col_uf = c
            elif not col_cid and cl in ("CIDADE", "MUNICIPIO"):
                col_cid = c
            elif not col_dias and ("DIAS" in cl or "LEAD" in cl or "PRAZO" in cl):
                col_dias = c
            elif not col_km and ("KM" in cl or "DIST" in cl):
                col_km = c
            elif not col_fc and "CARRETA" in cl:
                col_fc = c
            elif not col_ft and "TRUCK" in cl:
                col_ft = c
        if col_uf and col_cid and col_dias:
            for _, r in df_lt.iterrows():
                u_k = limpar_texto(r[col_uf])
                c_k = limpar_texto(r[col_cid])
                try:
                    dias_v = float(str(r[col_dias]).strip().replace(",", "."))
                    km_v = converter_moeda_para_float(r[col_km]) if (col_km and str(r[col_km]).strip() not in ("", "NAN", "NONE")) else None
                    fc_v = converter_moeda_para_float(r[col_fc]) if (col_fc and str(r[col_fc]).strip() not in ("", "NAN", "NONE")) else None
                    ft_v = converter_moeda_para_float(r[col_ft]) if (col_ft and str(r[col_ft]).strip() not in ("", "NAN", "NONE")) else None
                    mapa[(u_k, c_k)] = (dias_v, km_v, fc_v, ft_v)
                except Exception:
                    pass
    return mapa

def calcular_dias_rota_efetivos(lt_info):
    if lt_info is None:
        return None, None, None, None, None
    vals = list(lt_info) if isinstance(lt_info, (tuple, list)) else [lt_info]
    while len(vals) < 4:
        vals.append(None)
    lt_dias, km_val, fc_val, ft_val = vals
    if km_val is not None:
        if km_val <= 80:
            dias_rota = 0.0
        elif km_val <= 350:
            dias_rota = 1.0
        else:
            dias_rota = round(max(0.0, lt_dias - 2.0), 1)
    else:
        dias_rota = round(max(0.0, lt_dias - 2.0), 1)
    return lt_dias, dias_rota, km_val, fc_val, ft_val

def limpar_texto(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
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
    _ler_planilha_com_cache.clear("usuarios")
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
def renderizar_tabela_wms(df_in, chave_unica, **kwargs):
    if df_in is None or df_in.empty:
        return st.dataframe(df_in, **kwargs)
    df_f = df_in.copy()
    cols_disponiveis = [c for c in df_f.columns if str(c).strip() != ""]
    mem_w = st.session_state.setdefault("_memoria_widgets", {})
    k_col, k_txt, k_ms, k_c = f"wms_col_{chave_unica}", f"wms_txt_{chave_unica}", f"wms_ms_{chave_unica}", f"wms_c_{chave_unica}"
    def _salvar_mem(chave_m):
        mem_w[chave_m] = st.session_state.get(chave_m)

    aberto_mem = bool(mem_w.get(k_txt) or mem_w.get(k_ms) or mem_w.get(k_c) or (mem_w.get(k_col) and mem_w.get(k_col) != "(Todas as colunas)"))
    with st.expander("🔍 Filtrar Tabela por Coluna", expanded=aberto_mem):
        fc1, fc2, fc3 = st.columns((1.4, 2.0, 1.2), vertical_alignment="bottom")
        opcoes_cols = ["(Todas as colunas)"] + cols_disponiveis
        idx_col_m = opcoes_cols.index(mem_w[k_col]) if mem_w.get(k_col) in opcoes_cols else 0
        col_sel = fc1.selectbox("Coluna:", opcoes_cols, index=idx_col_m, key=k_col, on_change=_salvar_mem, args=(k_col,))
        if col_sel == "(Todas as colunas)":
            termo_g = fc2.text_input("Buscar em qualquer coluna:", value=str(mem_w.get(k_txt, "")), placeholder="Digite pedido, cliente, cidade, NF, placa...", key=k_txt, on_change=_salvar_mem, args=(k_txt,))
            if termo_g.strip():
                t_l = termo_g.strip().lower()
                mask_g = df_f.apply(lambda r: r.astype(str).str.lower().str.contains(t_l, na=False).any(), axis=1)
                df_f = df_f[mask_g]
        else:
            vals_unicos = sorted([str(v).strip() for v in df_f[col_sel].dropna().unique() if str(v).strip() not in ("", "nan", "None")])
            if 0 < len(vals_unicos) <= 40:
                vals_salvos = [v for v in mem_w.get(k_ms, list()) if v in vals_unicos]
                vals_esc = fc2.multiselect(f"Valores de '{col_sel}':", options=vals_unicos, default=vals_salvos, placeholder="Selecione um ou mais...", key=k_ms, on_change=_salvar_mem, args=(k_ms,))
                if vals_esc:
                    df_f = df_f[df_f[col_sel].astype(str).str.strip().isin(vals_esc)]
            else:
                termo_c = fc2.text_input(f"Filtrar '{col_sel}':", value=str(mem_w.get(k_c, "")), placeholder="Digite para filtrar...", key=k_c, on_change=_salvar_mem, args=(k_c,))
                if termo_c.strip():
                    df_f = df_f[df_f[col_sel].astype(str).str.lower().str.contains(termo_c.strip().lower(), na=False)]
        fc3.caption(f"📋 Exibindo **{len(df_f)}** de **{len(df_in)}** registro(s)")
    df_f_reset = df_f.reset_index(drop=True)
    
    styler = df_f_reset.style.apply(
        lambda row: ["background-color: #EFF4EE; color: #111812;" if row.name % 2 == 1 else "background-color: #FAF8F5; color: #111812;" for _ in row],
        axis=1
    )
    return st.dataframe(styler, **kwargs)   

@st.cache_data(ttl=3600, show_spinner=False)
def _ler_planilha_com_cache(aba):
    for tentativa in range(4):
        try:
            df = conn.read(worksheet=aba, ttl=0)
            df = df.dropna(how="all")
            return padronizar_df_maiusculo(df)
        except Exception as e:
            if tentativa < 3:
                espera = 3.0 * (tentativa + 1) if "429" in str(e) or "Quota" in str(e) else 1.5
                time.sleep(espera)
            else:
                raise e

def carregar_dados(aba):
    try:
        return _ler_planilha_com_cache(aba).copy()
    except Exception as e:
        st.warning(f"⏳ O Google Sheets pediu uma pausa rápida ao ler '{aba}'. Aguarde 10 segundos e clique em atualizar.")
        st.stop()

def salvar_dados(df, aba):
    if df is None or df.empty:
        st.warning(f"⚠️ Operação de gravação bloqueada na aba '{aba}' para proteger os dados existentes contra sobrescrita vazia.")
        return
    df_padronizado = padronizar_df_maiusculo(df)
    if df_padronizado.empty:
        return
    for tentativa in range(4):
        try:
            conn.update(worksheet=aba, data=df_padronizado)
            _ler_planilha_com_cache.clear(aba)
            return
        except Exception as e:
            if tentativa < 3:
                espera = 3.0 * (tentativa + 1) if "429" in str(e) or "Quota" in str(e) else 1.5
                time.sleep(espera)
            else:
                raise e
def limpar_cache_operacional():
    for _aba_op in ("planejamento", "cargas", "bipes", "usuarios"):
        _ler_planilha_com_cache.clear(_aba_op)
    if "montar_html_usuarios_online" in globals():
        montar_html_usuarios_online.clear()             

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
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container, [data-testid="stMainBlockContainer"] {
            padding-top: 1.2rem !important;
            padding-bottom: 0.5rem !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #DCD9D0 !important;
            border: 1px solid rgba(20, 26, 22, 0.14) !important;
            border-radius: 16px !important;
            box-shadow: 0 14px 36px rgba(20, 26, 22, 0.10) !important;
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
                in_login = st.text_input("Usuário", placeholder="Ex: GRANO.LOG")
                in_senha = st.text_input("Senha", type="password", placeholder="Digite sua senha...")
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
                            st.session_state.aba_ativa = "🏠 Início" if len(mods) > 1 else (mods if mods else "")
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
                0%   { transform: translateX(-230px); }
                19%  { transform: translateX(188px); }
                22%  { transform: translateX(188px); }
                28%  { transform: translateX(142px); }
                40%  { transform: translateX(142px); }
                63%  { transform: translateX(632px); }
                66%  { transform: translateX(632px); }
                72%  { transform: translateX(586px); }
                84%  { transform: translateX(586px); }
                100% { transform: translateX(1180px); }
            }
            @keyframes sinalManobraRe {
                0%, 21%, 29%, 65%, 73%, 100% { opacity: 0; }
                22.5%, 27.5%, 66.5%, 71.5% { opacity: 1; }
            }
            @keyframes piscaGiroflex {
                0%, 100% { fill: #F59E0B; opacity: 1; }
                50% { fill: #FEF3C7; opacity: 0.35; }
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
                0%, 27.5%, 40.5%, 100% { fill: #D5D0C5; }
                29%, 39% { fill: #C8E6C9; }
            }
            @keyframes brilhoDocaDestino {
                0%, 71.5%, 84.5%, 100% { fill: #D5D0C5; }
                73%, 83% { fill: #C8E6C9; }
            }
            @keyframes checkEntregaLoja {
                0%, 72%, 85.5%, 100% { transform: scale(0); opacity: 0; }
                75%, 82.5% { transform: scale(1.1); opacity: 1; }
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
            @keyframes nuvemFlutua {
                0% { transform: translateX(-25px); }
                50% { transform: translateX(25px); }
                100% { transform: translateX(-25px); }
            }
            .rota-wrap {
                width: 100%;
                margin: 10px 0 0 0;
                height: 145px;
                position: relative;
                overflow: hidden;
            }
            .asfalto-full {
                position: absolute;
                left: 0;
                right: 0;
                bottom: 22px;
                height: 2px;
                background-color: #141A16;
            }
            .faixa-full {
                position: absolute;
                left: 0;
                right: 0;
                bottom: 14px;
                height: 2px;
                background-image: repeating-linear-gradient(to right, rgba(20, 26, 22, 0.45) 0 10px, transparent 10px 22px);
            }
            .carreta-grupo { animation: viagemCarretaGrano 16s ease-in-out infinite; }
            .carreta-carroceria { animation: suspensaoCarreta 0.45s ease-in-out infinite; }
            .sinal-re-wrap { animation: sinalManobraRe 16s ease-in-out infinite; }
            .giroflex-luz { animation: piscaGiroflex 0.35s ease-in-out infinite; }
            .limpador-anim { transform-box: fill-box; transform-origin: bottom right; animation: limpadorParabrisa 0.7s ease-in-out infinite; }
            .nuvem-1 { animation: nuvemFlutua 18s ease-in-out infinite; }
            .nuvem-2 { animation: nuvemFlutua 24s ease-in-out 4s infinite; }
            .fumo-1 { transform-box: fill-box; transform-origin: center; animation: fumoEscapamento 0.9s ease-out infinite; }
            .fumo-2 { transform-box: fill-box; transform-origin: center; animation: fumoEscapamento 0.9s ease-out 0.45s infinite; }
            .doca-cd-luz { animation: brilhoDocaCD 16s ease-in-out infinite; }
            .doca-dest-luz { animation: brilhoDocaDestino 16s ease-in-out infinite; }
            .badge-entregue { transform-box: fill-box; transform-origin: center; animation: checkEntregaLoja 16s ease-out infinite; }
            .gota-chuva-1 { animation: chuvaCaindo 0.85s linear infinite; }
            .gota-chuva-2 { animation: chuvaCaindo 0.95s linear 0.25s infinite; }
            .gota-chuva-3 { animation: chuvaCaindo 0.80s linear 0.50s infinite; }
            .gota-chuva-4 { animation: chuvaCaindo 0.90s linear 0.70s infinite; }
            .respingo-1 { transform-box: fill-box; transform-origin: center; animation: respingoAsfalto 0.85s ease-out infinite; }
            .respingo-2 { transform-box: fill-box; transform-origin: center; animation: respingoAsfalto 0.95s ease-out 0.35s infinite; }
            </style>

            <div class="rota-wrap">
                <div class="asfalto-full"></div>
                <div class="faixa-full"></div>

                <svg width="100%" height="145" viewBox="0 0 880 132" preserveAspectRatio="xMidYMax meet" fill="none" xmlns="http://w3.org" style="position:relative; z-index:2; overflow:visible;">
                    <defs>
                        <linearGradient id="feixeFarol" x1="0%" y1="50%" x2="100%" y2="50%">
                            <stop offset="0%" stop-color="#C8E6C9" stop-opacity="0.82"/>
                            <stop offset="100%" stop-color="#C8E6C9" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="feixeRe" x1="100%" y1="50%" x2="0%" y2="50%">
                            <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.95"/>
                            <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
                        </linearGradient>
                    </defs>

                    <!-- Nuvens de Chuva Minimalistas -->
                    <g class="nuvem-1" opacity="0.84">
                        <path d="M95 16 H131 C135 16 138 13 138 9.5 C138 6.2 135.5 3.6 132.2 3.3 C130.8 0 127.5 -2 123.6 -2 C120.2 -2 117.2 -0.4 115.6 2.1 C114.4 1.4 113 1 111.5 1 C107.2 1 103.6 4.2 103.1 8.3 C99 8.6 95.8 12 95.8 16 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                    </g>
                    <g class="nuvem-2" opacity="0.84">
                        <path d="M430 15 H474 C479 15 482.5 11.5 482.5 7.2 C482.5 3.3 479.5 0.2 475.6 0 C473.8 -3.8 469.8 -6 465.2 -6 C461.1 -6 457.5 -4.1 455.5 -1.1 C454 -1.9 452.3 -2.4 450.5 -2.4 C445.3 -2.4 441 1.4 440.4 6.4 C435.5 6.8 431.8 10.8 431.8 15 Z" transform="translate(0, 7)" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                    </g>
                    <g class="nuvem-1" opacity="0.84">
                        <path d="M745 17 H783 C787.2 17 790.5 13.8 790.5 9.8 C790.5 6.1 787.8 3.2 784.2 2.9 C782.7 -0.6 779.2 -2.8 775 -2.8 C771.3 -2.8 768.1 -1.1 766.3 1.6 C765 0.8 763.5 0.4 761.8 0.4 C757.2 0.4 753.3 3.9 752.8 8.3 C748.4 8.6 745 12.2 745 17 Z" transform="translate(0, 4)" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                    </g>

                    <!-- 1. CENTRO DE DISTRIBUIÇÃO GRANO (Estrutura Ampliada + Letreiro Encaixado + Paletes + Árvores) -->
                    <g>
                        <ellipse cx="185" cy="110" rx="90" ry="3.6" fill="#141A16" opacity="0.16"/>

                        <!-- Árvore Copada à Esquerda -->
                        <line x1="88" y1="110" x2="88" y2="85" stroke="#141A16" stroke-width="1.7"/>
                        <circle cx="83" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="93" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="88" cy="74" r="8.5" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5"/>

                        <!-- Bloco Administrativo Lateral -->
                        <rect x="103" y="65" width="30" height="45" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7" stroke-linejoin="round"/>
                        <rect x="108" y="71" width="8.5" height="7.5" rx="1" fill="#E8F5E9" stroke="#141A16" stroke-width="1.1"/>
                        <rect x="120" y="71" width="8.5" height="7.5" rx="1" fill="#E8F5E9" stroke="#141A16" stroke-width="1.1"/>
                        <rect x="113" y="89" width="10" height="21" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3"/>

                        <!-- Galpão Principal Mais Largo e Alto (Placa 100% interna) -->
                        <path d="M133 110 V49 L191 25 L249 49 V110 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <polygon points="134,51 191,28 248,51 248,56 191,33 134,56" fill="#D5D0C5"/>
                        <path d="M126 52 L191 23 L256 52" stroke="#1B5E20" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/>
                        <rect x="178" y="18" width="26" height="5" rx="1.5" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3"/>

                        <!-- Placa CD GRANO totalmente dentro da fachada -->
                        <rect x="160" y="42" width="62" height="13" rx="2.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.3"/>
                        <text x="191" y="51.2" text-anchor="middle" font-family="sans-serif" font-size="8.2" font-weight="800" fill="#FFFFFF" letter-spacing="0.5">CD GRANO</text>

                        <!-- Plataforma das Docas -->
                        <rect x="138" y="102" width="106" height="8" fill="#D5D0C5" stroke="#141A16" stroke-width="1.4"/>

                        <!-- Doca 01 -->
                        <rect x="145" y="62" width="27" height="40" rx="1" fill="#DDD8CE" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="145" y1="69" x2="172" y2="69" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="145" y1="76" x2="172" y2="76" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="143" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="171" y="102" width="3" height="8" fill="#141A16"/>

                        <!-- Doca 02 (Onde a traseira da carreta encosta de ré) -->
                        <rect class="doca-cd-luz" x="178" y="62" width="27" height="40" rx="1" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="178" y1="69" x2="205" y2="69" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="178" y1="76" x2="205" y2="76" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="176" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="204" y="102" width="3" height="8" fill="#141A16"/>

                        <!-- Doca 03 -->
                        <rect x="211" y="62" width="27" height="40" rx="1" fill="#DDD8CE" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="211" y1="69" x2="238" y2="69" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="211" y1="76" x2="238" y2="76" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="209" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="237" y="102" width="3" height="8" fill="#141A16"/>

                        <!-- Pilha de Paletes com Caixas + Árvore Copada à Direita do CD -->
                        <line x1="251" y1="109" x2="266" y2="109" stroke="#141A16" stroke-width="1.6"/>
                        <rect x="252" y="103" width="6.5" height="5.5" fill="#C8E6C9" stroke="#141A16" stroke-width="1.2"/>
                        <rect x="258.5" y="103" width="6.5" height="5.5" fill="#A5D6A7" stroke="#141A16" stroke-width="1.2"/>
                        <rect x="255" y="97.5" width="7" height="5.5" fill="#E8F5E9" stroke="#141A16" stroke-width="1.2"/>
                        <line x1="274" y1="110" x2="274" y2="85" stroke="#141A16" stroke-width="1.7"/>
                        <circle cx="269" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="279" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="274" cy="74" r="8.5" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5"/>
                    </g>

                    <!-- 2. CD MERCADO / CENTRO DE DISTRIBUIÇÃO DO CLIENTE (Direita + Paletes + Árvore) -->
                    <g>
                        <ellipse cx="654" cy="110" rx="76" ry="3.4" fill="#141A16" opacity="0.16"/>

                        <!-- Guarita / Controle de Acesso à Esquerda -->
                        <rect x="586" y="72" width="24" height="38" fill="#DDD8CE" stroke="#141A16" stroke-width="1.7" stroke-linejoin="round"/>
                        <rect x="591" y="78" width="14" height="8" rx="1" fill="#E8F5E9" stroke="#141A16" stroke-width="1.2"/>
                        <rect x="593" y="92" width="10" height="18" fill="#EAE7E0" stroke="#141A16" stroke-width="1.3"/>

                        <!-- Galpão Logístico Principal -->
                        <rect x="610" y="52" width="88" height="58" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <rect x="610" y="52" width="88" height="6" fill="#C8E6C9" stroke="#141A16" stroke-width="1.4"/>

                        <!-- Placa CD MERCADO -->
                        <rect x="619" y="38" width="70" height="14" rx="2.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.3"/>
                        <text x="654" y="47.8" text-anchor="middle" font-family="sans-serif" font-size="8.2" font-weight="800" fill="#FFFFFF" letter-spacing="0.5">CD MERCADO</text>

                        <!-- Plataforma Elevada de Recebimento -->
                        <rect x="614" y="102" width="80" height="8" fill="#D5D0C5" stroke="#141A16" stroke-width="1.4"/>

                        <!-- Doca de Recebimento 01 (Onde a traseira da carreta encosta de ré) -->
                        <rect class="doca-dest-luz" x="621" y="65" width="30" height="37" rx="1" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="621" y1="72" x2="651" y2="72" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="621" y1="79" x2="651" y2="79" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="619" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="650" y="102" width="3" height="8" fill="#141A16"/>

                        <!-- Doca de Recebimento 02 -->
                        <rect x="658" y="65" width="30" height="37" rx="1" fill="#DDD8CE" stroke="#141A16" stroke-width="1.5"/>
                        <line x1="658" y1="72" x2="688" y2="72" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <line x1="658" y1="79" x2="688" y2="79" stroke="#141A16" stroke-width="1" opacity="0.5"/>
                        <rect x="656" y="102" width="3" height="8" fill="#141A16"/>
                        <rect x="687" y="102" width="3" height="8" fill="#141A16"/>

                        <!-- Palete Recebido + Árvore Copada à Direita do CD Mercado -->
                        <line x1="700" y1="109" x2="713" y2="109" stroke="#141A16" stroke-width="1.6"/>
                        <rect x="701" y="103.5" width="5.5" height="5" fill="#C8E6C9" stroke="#141A16" stroke-width="1.1"/>
                        <rect x="706.5" y="103.5" width="5.5" height="5" fill="#A5D6A7" stroke="#141A16" stroke-width="1.1"/>
                        <line x1="722" y1="110" x2="722" y2="85" stroke="#141A16" stroke-width="1.7"/>
                        <circle cx="717" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="727" cy="81" r="7" fill="#81C784" stroke="#1B5E20" stroke-width="1.4"/>
                        <circle cx="722" cy="74" r="8.5" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5"/>

                        <!-- Selo Verde de Descarga Concluída -->
                        <g class="badge-entregue">
                            <circle cx="654" cy="21" r="10" fill="#1B5E20" stroke="#141A16" stroke-width="1.5"/>
                            <path d="M649.5 21 L653 24.5 L659.5 18" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </g>
                    </g>

                    <!-- 3. CARRETA BAÚ REFRIGERADA GRANO -->
                    <g class="carreta-grupo">
                        <ellipse cx="115" cy="110" rx="64" ry="3" fill="#141A16" opacity="0.20"/>

                        <circle class="fumo-1" cx="144" cy="63" r="2.6" fill="#8A928C"/>
                        <circle class="fumo-2" cx="141" cy="60" r="2.1" fill="#8A928C"/>

                        <g class="carreta-carroceria">
                            <polygon points="178,94 216,86 216,103" fill="url(#feixeFarol)"/>

                            <g class="sinal-re-wrap">
                                <polygon points="50,94 16,86 16,102" fill="url(#feixeRe)"/>
                                <circle cx="50" cy="94" r="2.5" fill="#FFFFFF" stroke="#141A16" stroke-width="0.9"/>
                                <rect class="giroflex-luz" x="155" y="62.5" width="4" height="3.5" rx="1" stroke="#141A16" stroke-width="0.9"/>
                            </g>

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
                        <path class="respingo-2" d="M350 110 Q353 106 356 110"/>
                        <path class="respingo-1" d="M510 110 Q513 106 516 110"/>
                        <path class="respingo-2" d="M760 110 Q763 106 766 110"/>
                    </g>
                </svg>
            </div>
            """,
            height=148
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

        /* 4. Tabelas e Dataframes (Alto Contraste Corporativo Grano) */
        [data-testid="stDataFrame"] {
            background-color: #FFFFFF !important;
            border: 1.5px solid #2E7D32 !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 12px rgba(27, 94, 32, 0.08) !important;
        }
        [data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
            --gdg-bg-cell: #FFFFFF !important;
            --gdg-bg-cell-medium: #F4F7F3 !important;
            --gdg-bg-header: #1B5E20 !important;
            --gdg-bg-header-has-focus: #144718 !important;
            --gdg-bg-header-hovered: #236B28 !important;
            --gdg-text-header: #FFFFFF !important;
            --gdg-text-dark: #111827 !important;
            --gdg-text-medium: #1F2937 !important;
            --gdg-text-light: #4B5563 !important;
            --gdg-border-color: #D1DDD0 !important;
            --gdg-horizontal-border-color: #DCE6DB !important;
            --gdg-accent-color: #1B5E20 !important;
            --gdg-accent-light: rgba(27, 94, 32, 0.12) !important;
        }
        /* 5. Barras e Caixas de Filtro Sofisticadas (Acabamento Premium Grano) */
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) {
            background: linear-gradient(135deg, #DCE7DB 0%, #D0DED0 100%) !important;
            border: 1px solid rgba(27, 94, 32, 0.35) !important;
            border-left: 3.5px solid #1B5E20 !important;
            border-radius: 12px !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.06) !important;
            overflow: hidden !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]):hover {
            border-color: rgba(27, 94, 32, 0.65) !important;
            box-shadow: 0 5px 14px rgba(27, 94, 32, 0.11) !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) summary,
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) [data-testid="stExpanderDetails"] {
            background: transparent !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) summary {
            padding: 8px 14px !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) summary p {
            color: #143618 !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
            letter-spacing: 0.02em !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) label p {
            color: #1B4320 !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
        }
        div[data-testid="stSelectbox"]:has(input[aria-label*="Filtrar"]),
        div[data-testid="stSelectbox"]:has(input[aria-label*="Selecione a Carga"]),
        div[data-testid="stMultiSelect"]:has(input[aria-label*="Filtrar"]) {
            background: linear-gradient(135deg, #DCE7DB 0%, #D2DFD1 100%) !important;
            border: 1px solid rgba(27, 94, 32, 0.35) !important;
            border-left: 3.5px solid #1B5E20 !important;
            border-radius: 12px !important;
            padding: 8px 14px 10px 14px !important;
            box-shadow: 0 3px 10px rgba(27, 94, 32, 0.06) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stSelectbox"]:has(input[aria-label*="Filtrar"]):hover,
        div[data-testid="stSelectbox"]:has(input[aria-label*="Selecione a Carga"]):hover,
        div[data-testid="stMultiSelect"]:has(input[aria-label*="Filtrar"]):hover {
            border-color: rgba(27, 94, 32, 0.65) !important;
            box-shadow: 0 5px 14px rgba(27, 94, 32, 0.11) !important;
        }
        div[data-testid="stSelectbox"]:has(input[aria-label*="Filtrar"]) label p,
        div[data-testid="stSelectbox"]:has(input[aria-label*="Selecione a Carga"]) label p,
        div[data-testid="stMultiSelect"]:has(input[aria-label*="Filtrar"]) label p {
            color: #143618 !important;
            font-weight: 700 !important;
            font-size: 0.79rem !important;
            letter-spacing: 0.02em !important;
        }
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) div[data-baseweb="select"] > div,
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) div[data-baseweb="input"] > div,
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) div[data-baseweb="base-input"],
        [data-testid="stExpander"]:has(input[aria-label^="Coluna:"]) input,
        div[data-testid="stSelectbox"]:has(input[aria-label*="Filtrar"]) div[data-baseweb="select"] > div,
        div[data-testid="stSelectbox"]:has(input[aria-label*="Selecione a Carga"]) div[data-baseweb="select"] > div,
        div[data-testid="stMultiSelect"]:has(input[aria-label*="Filtrar"]) div[data-baseweb="select"] > div {
            background-color: #FAFBF9 !important;
            border: 1px solid rgba(27, 94, 32, 0.28) !important;
            border-radius: 9px !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03) !important;
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
            limpar_cache_operacional()
        st.session_state.usuario_autenticado = False
        st.rerun()
    st.markdown("<div style='text-align:center; color:#8A928C; font-size:0.72rem; margin-top:14px; line-height:1.35;'><strong>WMS Grano v2.0</strong><br>Inteligência Logística</div>", unsafe_allow_html=True)        
agora_ping = datetime.now()
ultimo_ping_sessao = st.session_state.get("ultimo_ping_ts")
if ultimo_ping_sessao is None or (agora_ping - ultimo_ping_sessao).total_seconds() >= 600:
    _ler_planilha_com_cache.clear("usuarios")
    df_u_ping = carregar_dados("usuarios")
    if not df_u_ping.empty and len(df_u_ping) >= 1 and "login" in df_u_ping.columns:
        if "ultimo_acesso" not in df_u_ping.columns:
            df_u_ping["ultimo_acesso"] = ""
        df_u_ping["ultimo_acesso"] = df_u_ping["ultimo_acesso"].astype(object)
        mask_ping = df_u_ping["login"].apply(limpar_texto) == st.session_state.login_usuario
        if mask_ping.any():
            df_u_ping.loc[mask_ping, "ultimo_acesso"] = agora_ping.strftime("%Y-%m-%d %H:%M:%S")
            conn.update(worksheet="usuarios", data=padronizar_df_maiusculo(df_u_ping))
            _ler_planilha_com_cache.clear("usuarios")
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
# === BARRA DE GUIAS FIXA COM "🏠 INÍCIO" SEMPRE EM 1º LUGAR E "✕" EM CADA ABA ===
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

mapa_rotulos_guia = {m: ("🏠 Início" if m == "🏠 Início" else f"{m}\u00A0\u00A0✕") for m in abas_nav}
mapa_reverso_guia = {v: k for k, v in mapa_rotulos_guia.items()}

def _ao_mudar_guia():
    sel_rotulo = st.session_state.get("barra_guias_topo")
    agora_ms = time.time()
    def _destino():
        orig = st.session_state.get("_aba_origem_antes_x")
        if orig and orig in st.session_state.abas_abertas and (agora_ms - st.session_state.get("_ts_origem_x", 0)) < 1.5:
            return orig
        return st.session_state.abas_abertas[-1] if st.session_state.abas_abertas else "🏠 Início"

    mod_escolhido = mapa_reverso_guia.get(sel_rotulo) if sel_rotulo else st.session_state.aba_ativa
    if mod_escolhido and mod_escolhido in st.session_state.abas_abertas:
        if (not sel_rotulo or mod_escolhido == st.session_state.aba_ativa) and mod_escolhido != "🏠 Início":
            st.session_state.abas_abertas.remove(mod_escolhido)
            st.session_state.aba_ativa = _destino()
        elif sel_rotulo:
            st.session_state["_aba_origem_antes_x"] = st.session_state.aba_ativa
            st.session_state["_ts_origem_x"] = agora_ms
            st.session_state.aba_ativa = mod_escolhido

if len(abas_nav) > 1:
    st.markdown(
        """
        <style>
        div[data-testid="stDecoration"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background-color: #141A16 !important;
            border-bottom: none !important;
            height: 2.95rem !important;
            left: 0 !important;
            width: 100vw !important;
            z-index: 999995 !important;
            pointer-events: none !important;
        }
        section[data-testid="stSidebar"][aria-expanded="true"] {
            top: 2.95rem !important;
            height: calc(100vh - 2.95rem) !important;
        }
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div {
            border-right: none !important;
        }        
        header[data-testid="stHeader"] *,
        header[data-testid="stHeader"] button {
            pointer-events: auto !important;
            color: #E8EDE9 !important;
        }

        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) {
            position: fixed !important;
            top: 15px !important;
            left: 21.5rem !important;
            width: max-content !important;
            max-width: calc(100vw - 34rem) !important;
            height: 32px !important;
            display: flex !important;
            align-items: center !important;
            gap: 0px !important;
            z-index: 999998 !important;
            background: transparent !important;
            flex-wrap: nowrap !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) {
            left: 4.5rem !important;
            max-width: calc(100vw - 18rem) !important;
        }
        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) > div[data-testid="stColumn"] {
            width: auto !important;
            min-width: unset !important;
            flex: 0 0 auto !important;
            height: 32px !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
        }
        div[class*="st-key-nav_guia_"],
        div[class*="st-key-x_guia_"] {
            margin: 0 !important;
            padding: 0 !important;
            height: 32px !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button,
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button:hover,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button:hover,
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button[kind="primary"],
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button[kind="primary"],
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button[kind="primary"]:hover,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button[kind="primary"]:hover {
            background-color: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            height: 32px !important;
            min-height: 32px !important;
            max-height: 32px !important;
            margin: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: auto !important;
            min-width: unset !important;
            transform: none !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button > div,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button > div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 0 10px 0 !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button {
            padding-left: 14px !important;
            padding-right: 6px !important;
            white-space: nowrap !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_inicio"] button {
            padding-left: 14px !important;
            padding-right: 14px !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button {
            padding-left: 2px !important;
            padding-right: 10px !important;
        }
        /* Container da aba (espaçamento entre guias) */
        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) > div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_"]:not([class*="inicio"])) {
            margin-left: 4px !important;
            border-radius: 10px 0 0 0 !important;
            border-top: 2.5px solid transparent !important;
            transition: background-color 0.15s ease !important;
        }
        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) > div[data-testid="stColumn"]:has(div[class*="st-key-x_guia_"]) {
            border-radius: 0 10px 0 0 !important;
            border-top: 2.5px solid transparent !important;
            transition: background-color 0.15s ease !important;
        }
        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_guia_"]) > div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_inicio"]) {
            border-radius: 10px 10px 0 0 !important;
            border-top: 2.5px solid transparent !important;
            transition: background-color 0.15s ease !important;
        }
        /* Hover unificado sem sobreposição */
        div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_"]):hover,
        div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_"]):hover + div[data-testid="stColumn"],
        div[data-testid="stColumn"]:has(+ div[data-testid="stColumn"]:has(div[class*="st-key-x_guia_"]):hover),
        div[data-testid="stColumn"]:has(div[class*="st-key-x_guia_"]):hover {
            background-color: rgba(255, 255, 255, 0.12) !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button:hover,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button:hover,
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button:focus,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button:focus {
            background-color: transparent !important;
            background: transparent !important;
        }
        /* Aba Ativa */
        div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_"] button[kind="primary"]),
        div[data-testid="stColumn"]:has(div[class*="st-key-x_guia_"] button[kind="primary"]),
        div[data-testid="stColumn"]:has(div[class*="st-key-nav_guia_"] button[kind="primary"]):hover,
        div[data-testid="stColumn"]:has(div[class*="st-key-x_guia_"] button[kind="primary"]):hover {
            background-color: #A5D6A7 !important;
            border-top: 2.5px solid #1B5E20 !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button p,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button p {
            font-size: 0.77rem !important;
            font-weight: 600 !important;
            color: #DCE3DD !important;
            line-height: 1 !important;
            padding: 0 !important;
            margin: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-nav_guia_"] button[kind="primary"] p,
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button[kind="primary"] p {
            font-weight: 700 !important;
            color: #143618 !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button p {
            justify-content: center !important;
            width: 18px !important;
            height: 18px !important;
            border-radius: 5px !important;
            font-size: 0.75rem !important;
            margin-top: 7px !important;
        }
        [data-testid="stAppViewContainer"] div[class*="st-key-x_guia_"] button:hover p {
            background-color: rgba(183, 28, 28, 0.18) !important;
            color: #B71C1C !important;
        }
        </style>

        """,
        unsafe_allow_html=True
    )
    cols_guias = st.columns(1 + (len(abas_nav) - 1) * 2)
    idx_col_g = 0
    for idx_g, mod_g in enumerate(abas_nav):
        eh_ativa_g = (st.session_state.aba_ativa == mod_g)
        tipo_btn_g = "primary" if eh_ativa_g else "secondary"
        if mod_g == "🏠 Início":
            if cols_guias[idx_col_g].button("🏠 Início", key="nav_guia_inicio", type=tipo_btn_g):
                st.session_state.aba_ativa = "🏠 Início"
                st.rerun()
            idx_col_g += 1
        else:
            if cols_guias[idx_col_g].button(mod_g, key=f"nav_guia_{idx_g}", type=tipo_btn_g):
                st.session_state.aba_ativa = mod_g
                st.rerun()
            if cols_guias[idx_col_g + 1].button("✕", key=f"x_guia_{idx_g}", type=tipo_btn_g):
                st.session_state.abas_abertas.remove(mod_g)
                if st.session_state.aba_ativa == mod_g:
                    st.session_state.aba_ativa = st.session_state.abas_abertas[-1] if st.session_state.abas_abertas else "🏠 Início"
                st.rerun()
            idx_col_g += 2
    
aba = st.session_state.aba_ativa

PREFIXOS_MEMORIA_ABA = ("filtro_", "kpi_", "sel_", "in_", "q_lt_", "adm_")
mem_global = st.session_state.setdefault("_memoria_widgets", {})

for _k_w, _v_w in list(st.session_state.items()):
    if _k_w.startswith(PREFIXOS_MEMORIA_ABA):
        mem_global[_k_w] = _v_w

for _k_m, _v_m in mem_global.items():
    if _k_m.startswith(PREFIXOS_MEMORIA_ABA) and _k_m not in st.session_state:
        st.session_state[_k_m] = _v_m

if aba == "🏠 Início":

    st.markdown("<style>[data-stale='true'] { display: none !important; }</style>", unsafe_allow_html=True)    
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
    c_topo_esq, c_topo_clima, c_topo_cal = st.columns([1.25, 1.65, 1.15], vertical_alignment="center")

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
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:2px; flex-wrap:nowrap;">
                            <span style="font-size:clamp(1.65rem, 2.1vw, 2.35rem); font-weight:800; color:#141A16; letter-spacing:-0.5px; line-height:1.08; white-space:nowrap;">Olá, {primeiro_nome_ini}</span>
                            <span class="ponto-vivo-grano" style="margin:0; flex-shrink:0;"></span>
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
                    linhas_cal_html += f"<td style='padding:1px 0;'><span style='display:inline-flex; align-items:center; justify-content:center; width:17px; height:17px; background:#1B5E20; color:#FFFFFF; border-radius:50%; font-weight:700; white-space:nowrap;'>{d_i}</span></td>"
                elif d_i in feriados_i:
                    linhas_cal_html += f"<td style='padding:1px 0;'><span style='display:inline-flex; align-items:center; justify-content:center; width:17px; height:17px; background:#FFCDD2; color:#B71C1C; border-radius:50%; font-weight:700; white-space:nowrap;' title='Feriado'>{d_i}</span></td>"
                elif idx_s in (0, 6):
                    linhas_cal_html += f"<td style='color:#8A928C;'>{d_i}</td>"
                else:
                    linhas_cal_html += f"<td style='color:#141A16;'>{d_i}</td>"
            linhas_cal_html += "</tr>"

        st.markdown(
            f'<div style="background:rgba(255,255,255,0.52); backdrop-filter:blur(8px); border:1px solid rgba(255,255,255,0.8); border-radius:16px; padding:9px 10px; box-shadow:0 6px 18px rgba(20,26,22,0.06); overflow:hidden;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; gap:4px; margin-bottom:4px; padding-bottom:3px; border-bottom:1px solid rgba(27,94,32,0.15);">'
            f'<span style="font-size:0.70rem; font-weight:700; color:#141A16; white-space:nowrap;">📅 {meses_nomes_i[mes_i][:3]}/{ano_i}</span>'
            f'<span style="font-size:0.58rem; color:#B71C1C; font-weight:600; white-space:nowrap;">● Feriado</span>'
            f'</div>'
            f'<table class="mini-cal-grano" style="width:100%; table-layout:fixed; border-collapse:collapse; text-align:center; font-size:0.62rem; line-height:1.3;">'
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
            if st.button(f"{mod_at} || {desc_modulos.get(mod_at, '')}", key=f"btn_atalho_ini_{idx_at}", use_container_width=True):
                st.session_state.aba_ativa = mod_at
                st.rerun()

    components.html("""<script>
    const d = window.parent.document;
    const f = () => d.querySelectorAll('button').forEach(b => {
        const p = b.querySelector('p');
        if (!p || !p.textContent.includes(' || ')) return;
        const [t, s] = p.textContent.split(' || ');
        p.innerHTML = `<b style="display:block;font-size:.9rem;color:#141A16;margin-bottom:5px;white-space:normal">${t}</b><span style="display:block;font-size:.75rem;color:#4A524C;line-height:1.35;white-space:normal">${s}</span>`;
        b.style.cssText = 'width:100%!important;height:106px!important;min-height:106px!important;background:#E4E0D6!important;border:1px solid rgba(27,94,32,.32)!important;border-radius:12px!important;padding:14px 16px!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;align-items:flex-start!important;text-align:left!important;box-shadow:0 2px 6px rgba(0,0,0,.04)!important';
        const dv = b.querySelector('div');
        if (dv) dv.style.cssText = 'width:100%!important;display:block!important;text-align:left!important';
        p.style.cssText = 'white-space:normal!important;overflow:visible!important;text-overflow:unset!important;text-align:left!important;margin:0!important;width:100%!important';
    });
    f(); setTimeout(f, 150); new MutationObserver(f).observe(d.body, {childList:true, subtree:true});
    </script>""", height=0, width=0)

    # 4. Banda de Vegetais Ilustrada 3D (Black Line + Verde Grano)
    components.html(
        """
        <style>
        body { margin: 0; padding: 0; background: transparent; overflow: hidden; }

        /* 1. Brócolis Guitarrista: pés fixos no chão, cintura flexiona e guitarra articula */
        @keyframes troncoGrooveBrocolis {
            0%, 100% { transform: translateY(0px) rotateZ(-2deg); }
            50% { transform: translateY(2.5px) rotateZ(2.5deg); }
        }
        @keyframes guitarraSolo {
            0%, 100% { transform: rotateZ(-4deg) translateY(0px); }
            50% { transform: rotateZ(6deg) translateY(-1.5px); }
        }
        @keyframes palhetaRapida {
            0%, 100% { transform: rotateZ(-18deg); }
            50% { transform: rotateZ(22deg); }
        }
        @keyframes cabecaSolo {
            0%, 100% { transform: rotateZ(-4deg); }
            50% { transform: rotateZ(5deg); }
        }

        /* 2. Cenoura Vocalista: pés e pedestal fixos, cintura balança e braço segura o mic */
        @keyframes troncoGrooveCenoura {
            0%, 100% { transform: translateY(0px) rotateZ(-2.5deg); }
            50% { transform: translateY(2px) rotateZ(2.5deg); }
        }
        @keyframes bocaCantaAnim {
            0%, 100% { transform: scaleY(0.55) scaleX(1.15); }
            50% { transform: scaleY(1.3) scaleX(0.88); }
        }
        @keyframes topeteBalanca {
            0%, 100% { transform: rotateZ(-7deg); }
            50% { transform: rotateZ(8deg); }
        }
        @keyframes bracoCanta {
            0%, 100% { transform: rotateZ(0deg); }
            50% { transform: rotateZ(-18deg); }
        }
        @keyframes bracoMicCompensa {
            0%, 100% { transform: rotateZ(3deg); }
            50% { transform: rotateZ(-4deg); }
        }

        /* 3. Tomate Baterista: baqueta voa girando 360° no compasso */
        @keyframes bateristaShow3D {
            0%, 100% { transform: translateY(0px) scaleY(1); }
            50% { transform: translateY(-2.5px) scaleY(0.96); }
        }
        @keyframes bumboPulsa {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
        }
        @keyframes pratoVibra {
            0%, 100% { transform: rotateZ(0deg); }
            25% { transform: rotateZ(-13deg); }
            75% { transform: rotateZ(13deg); }
        }
        @keyframes baqE {
            0%, 100% { transform: rotateZ(-30deg); }
            50% { transform: rotateZ(22deg); }
        }
        @keyframes baqD {
            0%   { transform: translate(0px, 0px) rotateZ(20deg); }
            12%  { transform: translate(0px, 0px) rotateZ(-30deg); }
            25%  { transform: translate(0px, 0px) rotateZ(20deg); }
            37%  { transform: translate(0px, 0px) rotateZ(-30deg); }
            50%  { transform: translate(0px, 0px) rotateZ(15deg); }
            75%  { transform: translate(6px, -30px) rotateZ(200deg); }
            100% { transform: translate(0px, 0px) rotateZ(380deg); }
        }

        /* 4. Milho Baixista */
        @keyframes baixistaGroove3D {
            0%, 100% { transform: rotateZ(2deg) translateY(0px); }
            50% { transform: rotateZ(-2deg) translateY(-2.5px); }
        }
        @keyframes dedilhaBaixo {
            0%, 100% { transform: translateY(-2.5px) rotateZ(-10deg); }
            50% { transform: translateY(3.5px) rotateZ(14deg); }
        }
        @keyframes palhaGroove {
            0%, 100% { transform: rotateZ(-4deg); }
            50% { transform: rotateZ(5deg); }
        }

        /* Gerais: piscada, pés, equalizador, holofotes e notas */
        @keyframes piscaOlho {
            0%, 44%, 48%, 100% { transform: scaleY(1); }
            46% { transform: scaleY(0.1); }
        }
        @keyframes peRitmo {
            0%, 100% { transform: rotateZ(0deg); }
            50% { transform: rotateZ(-14deg); }
        }
        @keyframes eqBar1 { 0%, 100% { transform: scaleY(0.35); } 50% { transform: scaleY(1); } }
        @keyframes eqBar2 { 0%, 100% { transform: scaleY(0.85); } 50% { transform: scaleY(0.3); } }
        @keyframes eqBar3 { 0%, 100% { transform: scaleY(0.45); } 50% { transform: scaleY(0.95); } }
        @keyframes luzPalco { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.8; } }
        @keyframes ondaSom {
            0% { transform: scale(0.6); opacity: 0; }
            40% { opacity: 0.95; }
            100% { transform: scale(1.5); opacity: 0; }
        }
        @keyframes notaSobe3D {
            0% { transform: perspective(260px) translateY(6px) rotateY(0deg) scale(0.75); opacity: 0; }
            25% { opacity: 1; }
            100% { transform: perspective(260px) translateY(-34px) rotateY(360deg) scale(1.18); opacity: 0; }
        }

        .palco-3d-container {
            width: 100%;
            max-width: 920px;
            margin: 6px auto 0 auto;
            height: 158px;
            position: relative;
        }
        .musico-box {
            position: absolute;
            bottom: 14px;
            transform-origin: bottom center;
            filter: drop-shadow(0 4px 5px rgba(20, 26, 22, 0.18));
        }
        /* Posições alinhadas exatas com os centros dos holofotes (185, 365, 550, 720) */
        .m-brocolis { left: 16.5%; }
        .m-cenoura  { left: 36.2%; }
        .m-tomate   { left: 54.8%; bottom: 11px; animation: bateristaShow3D 0.55s ease-in-out infinite; }
        .m-vagem    { left: 74.2%; animation: baixistaGroove3D 1.45s ease-in-out infinite; }

        /* Articulações Brócolis */
        .tronco-brocolis { transform-box: fill-box; transform-origin: bottom center; animation: troncoGrooveBrocolis 0.75s ease-in-out infinite; }
        .copa-brocolis { transform-box: fill-box; transform-origin: bottom center; animation: cabecaSolo 0.75s ease-in-out infinite; }
        .guitarra-anim { transform-box: fill-box; transform-origin: 25% 60%; animation: guitarraSolo 0.75s ease-in-out infinite; }
        .palheta-brocolis { transform-box: fill-box; transform-origin: top center; animation: palhetaRapida 0.3s ease-in-out infinite; }

        /* Articulações Cenoura */
        .tronco-cenoura { transform-box: fill-box; transform-origin: bottom center; animation: troncoGrooveCenoura 0.85s ease-in-out infinite; }
        .topete-cenoura { transform-box: fill-box; transform-origin: bottom center; animation: topeteBalanca 0.85s ease-in-out infinite; }
        .boca-canta { transform-box: fill-box; transform-origin: center; animation: bocaCantaAnim 0.42s ease-in-out infinite; }
        .braco-cenoura-esq { transform-box: fill-box; transform-origin: top right; animation: bracoCanta 0.85s ease-in-out infinite; }
        .braco-cenoura-mic { transform-box: fill-box; transform-origin: top left; animation: bracoMicCompensa 0.85s ease-in-out infinite; }

        /* Articulações Tomate */
        .bumbo-anim { transform-box: fill-box; transform-origin: center; animation: bumboPulsa 0.55s ease-in-out infinite; }
        .prato-anim { transform-box: fill-box; transform-origin: center; animation: pratoVibra 0.55s ease-in-out infinite; }
        .be-anim { transform-box: fill-box; transform-origin: bottom right; animation: baqE 0.55s ease-in-out infinite; }
        .bd-anim { transform-box: fill-box; transform-origin: center; animation: baqD 2.2s ease-in-out infinite; }

        /* Articulações Milho */
        .dedilha-milho { transform-box: fill-box; transform-origin: top center; animation: dedilhaBaixo 0.4s ease-in-out infinite; }
        .palha-milho { transform-box: fill-box; transform-origin: bottom center; animation: palhaGroove 1.45s ease-in-out infinite; }

        .olho-pisca { transform-box: fill-box; transform-origin: center; animation: piscaOlho 3.6s ease-in-out infinite; }
        .pe-batida { transform-box: fill-box; transform-origin: bottom left; animation: peRitmo 0.55s ease-in-out infinite; }

        .eq-1 { transform-box: fill-box; transform-origin: bottom center; animation: eqBar1 0.55s ease-in-out infinite; }
        .eq-2 { transform-box: fill-box; transform-origin: bottom center; animation: eqBar2 0.72s ease-in-out infinite; }
        .eq-3 { transform-box: fill-box; transform-origin: bottom center; animation: eqBar3 0.62s ease-in-out infinite; }
        .holofote-feixe { animation: luzPalco 2.4s ease-in-out infinite; }

        .onda-1 { transform-box: fill-box; transform-origin: center; animation: ondaSom 1.3s ease-out infinite; }
        .onda-2 { transform-box: fill-box; transform-origin: center; animation: ondaSom 1.3s ease-out 0.65s infinite; }

        .nota-flut { position: absolute; pointer-events: none; }
        .nf-1 { left: 20.5%; top: 26px; animation: notaSobe3D 2.2s ease-out infinite; }
        .nf-2 { left: 40.5%; top: 22px; animation: notaSobe3D 2.5s ease-out 0.6s infinite; }
        .nf-3 { left: 59.5%; top: 26px; animation: notaSobe3D 2.0s ease-out 1.1s infinite; }
        .nf-4 { left: 78.5%; top: 24px; animation: notaSobe3D 2.4s ease-out 1.6s infinite; }
        </style>

        <div class="palco-3d-container">
            <svg width="100%" height="158" viewBox="0 0 920 158" fill="none" style="position:absolute; left:0; top:0;">
                <defs>
                    <radialGradient id="holofoteGrano" cx="50%" cy="88%" r="52%">
                        <stop offset="0%" stop-color="#4CAF50" stop-opacity="0.26"/>
                        <stop offset="100%" stop-color="#4CAF50" stop-opacity="0"/>
                    </radialGradient>
                    <linearGradient id="feixeLuzShow" x1="50%" y1="0%" x2="50%" y2="100%">
                        <stop offset="0%" stop-color="#81C784" stop-opacity="0.32"/>
                        <stop offset="100%" stop-color="#81C784" stop-opacity="0"/>
                    </linearGradient>
                </defs>

                <!-- Feixes de Holofote Centralizados sobre cada Músico -->
                <g class="holofote-feixe">
                    <polygon points="186,8 122,134 250,134" fill="url(#feixeLuzShow)"/>
                    <polygon points="366,8 302,134 430,134" fill="url(#feixeLuzShow)"/>
                    <polygon points="552,8 486,134 618,134" fill="url(#feixeLuzShow)"/>
                    <polygon points="718,8 654,134 782,134" fill="url(#feixeLuzShow)"/>
                </g>

                <!-- Equalizadores Centralizados nos Vãos entre os Músicos -->
                <g opacity="0.28" fill="#1B5E20">
                    <rect class="eq-1" x="265" y="108" width="5" height="24" rx="1.5"/>
                    <rect class="eq-2" x="274" y="102" width="5" height="30" rx="1.5"/>
                    <rect class="eq-3" x="283" y="110" width="5" height="22" rx="1.5"/>
                    <rect class="eq-1" x="292" y="105" width="5" height="27" rx="1.5"/>

                    <rect class="eq-2" x="448" y="106" width="5" height="26" rx="1.5"/>
                    <rect class="eq-3" x="457" y="100" width="5" height="32" rx="1.5"/>
                    <rect class="eq-1" x="466" y="108" width="5" height="24" rx="1.5"/>
                    <rect class="eq-2" x="475" y="104" width="5" height="28" rx="1.5"/>

                    <rect class="eq-3" x="625" y="108" width="5" height="24" rx="1.5"/>
                    <rect class="eq-1" x="634" y="101" width="5" height="31" rx="1.5"/>
                    <rect class="eq-2" x="643" y="109" width="5" height="23" rx="1.5"/>
                    <rect class="eq-3" x="652" y="104" width="5" height="28" rx="1.5"/>
                </g>

                <ellipse cx="460" cy="138" rx="380" ry="22" fill="url(#holofoteGrano)"/>
                <polygon points="62,134 858,134 882,146 38,146" fill="#EAE7E0" stroke="#141A16" stroke-width="1.6" stroke-linejoin="round"/>
                <rect x="38" y="146" width="844" height="6" rx="1" fill="#D5D0C5" stroke="#141A16" stroke-width="1.6"/>
                <line x1="190" y1="134" x2="178" y2="146" stroke="#141A16" stroke-width="0.9" opacity="0.25"/>
                <line x1="345" y1="134" x2="339" y2="146" stroke="#141A16" stroke-width="0.9" opacity="0.25"/>
                <line x1="460" y1="134" x2="460" y2="146" stroke="#141A16" stroke-width="0.9" opacity="0.25"/>
                <line x1="575" y1="134" x2="581" y2="146" stroke="#141A16" stroke-width="0.9" opacity="0.25"/>
                <line x1="730" y1="134" x2="742" y2="146" stroke="#141A16" stroke-width="0.9" opacity="0.25"/>
                <polygon points="78,141 102,141 106,146 74,146" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                <polygon points="818,141 842,141 846,146 814,146" fill="#C8E6C9" stroke="#141A16" stroke-width="1.3" stroke-linejoin="round"/>
                <rect x="225" y="143" width="13" height="3" rx="1" fill="#1B5E20"/>
                <rect x="385" y="143" width="13" height="3" rx="1" fill="#1B5E20"/>
                <rect x="522" y="143" width="13" height="3" rx="1" fill="#1B5E20"/>
                <rect x="682" y="143" width="13" height="3" rx="1" fill="#1B5E20"/>
            </svg>

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

            <!-- 1. BRÓCOLIS GUITARRISTA ARTICULADO (Pernas fixas + cintura flexiona + guitarra independente) -->
            <div class="musico-box m-brocolis">
                <svg width="82" height="84" viewBox="0 0 82 84" fill="none" style="overflow:visible;">
                    <ellipse cx="32" cy="81" rx="18" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <!-- Pernas e Pés plantados no palco -->
                    <path d="M25 63 V79 M38 63 V79" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M20 80 H27 C27 77.5 22 77.5 20 80 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <path class="pe-batida" d="M36 80 H43 C43 77.5 38 77.5 36 80 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>

                    <!-- Tronco articulado a partir da cintura -->
                    <g class="tronco-brocolis">
                        <path d="M22 41 L24 65 H39 L41 41 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <path d="M35 41 L34 65 H39 L41 41 Z" fill="#D5D0C5"/>

                        <g class="copa-brocolis">
                            <circle cx="16" cy="31" r="10" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7"/>
                            <circle cx="47" cy="31" r="10" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7"/>
                            <circle cx="31.5" cy="21" r="12" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.7"/>
                            <path d="M12 40 C6 36 8 25 16 25 C18 16 28 13 33 18 C39 13 49 17 49 26 C56 28 56 38 49 41 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.9" stroke-linejoin="round"/>
                            <path d="M20 27 C23 23 28 23 30 26 M36 28 C39 25 43 26 44 29" stroke="#2E7D32" stroke-width="1.3" stroke-linecap="round"/>
                        </g>

                        <path d="M22 46 H41" stroke="#141A16" stroke-width="1.5"/>
                        <rect x="23" y="45" width="7.5" height="5" rx="1.5" fill="#141A16"/>
                        <rect x="32.5" y="45" width="7.5" height="5" rx="1.5" fill="#141A16"/>
                        <line x1="25" y1="46.5" x2="27" y2="48.5" stroke="#FFFFFF" stroke-width="0.9" stroke-linecap="round"/>
                        <line x1="34.5" y1="46.5" x2="36.5" y2="48.5" stroke="#FFFFFF" stroke-width="0.9" stroke-linecap="round"/>
                        <path d="M29 53 Q32 56 35 53" stroke="#141A16" stroke-width="1.4" stroke-linecap="round"/>

                        <!-- Guitarra + Braço esquerdo + Mão palhetando articulados -->
                        <g class="guitarra-anim">
                            <path d="M18 59 C14 55 17 49 23 51 L33 54 C36 55 36 61 31 62 L22 62 C19 62 18 60 18 59 Z" fill="#C8E6C9" stroke="#141A16" stroke-width="1.7"/>
                            <circle cx="25" cy="56.5" r="2.2" fill="#1B5E20"/>
                            <line x1="34" y1="54" x2="60" y2="43" stroke="#141A16" stroke-width="2.3" stroke-linecap="round"/>
                            <path d="M59 41 L64 39 L65 43 L60 45 Z" fill="#1B5E20" stroke="#141A16" stroke-width="1.3"/>
                            <path d="M40 48 Q45 50 48 48" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                            <path class="palheta-brocolis" d="M23 48 Q19 54 25 58" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                        </g>

                        <path class="onda-1" d="M67 35 C71 39 71 45 67 49" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                        <path class="onda-2" d="M72 31 C77 37 77 47 72 53" stroke="#4CAF50" stroke-width="1.4" stroke-linecap="round"/>
                    </g>
                </svg>
            </div>

            <!-- 2. CENOURA VOCALISTA ARTICULADA (Pernas e pedestal fixos + corpo balança na cintura) -->
            <div class="musico-box m-cenoura">
                <svg width="74" height="88" viewBox="0 0 74 88" fill="none" style="overflow:visible;">
                    <ellipse cx="30" cy="85" rx="16" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <!-- Pernas e Pés plantados no palco -->
                    <path d="M24 66 V83 M35 66 V83" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M19 84 H26 C26 81.5 21 81.5 19 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <path class="pe-batida" d="M34 84 H41 C41 81.5 36 81.5 34 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>

                    <!-- Pedestal e Microfone fixos no palco -->
                    <line x1="54" y1="38" x2="54" y2="84" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <path d="M47 84 H61" stroke="#141A16" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="51" cy="36" r="4.2" fill="#1B5E20" stroke="#141A16" stroke-width="1.5"/>
                    <line x1="48" y1="35" x2="54" y2="37" stroke="#E8F5E9" stroke-width="1"/>
                    <path class="onda-1" d="M58 29 C62 33 62 39 58 43" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>

                    <!-- Corpo articulado na cintura -->
                    <g class="tronco-cenoura">
                        <g class="topete-cenoura">
                            <path d="M29 22 C22 10 14 12 19 22 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                            <path d="M30 22 C28 8 34 8 32 22 Z" fill="#66BB6A" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                            <path d="M31 22 C38 10 45 13 39 22 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.7" stroke-linejoin="round"/>
                        </g>

                        <path d="M16 26 C16 19 43 19 43 26 L33 68 C32 71 27 71 26 68 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                        <path d="M37 22 C41 22 43 24 43 26 L33 68 C32 70 31 70 30 70 L37 22 Z" fill="#D5D0C5"/>
                        <path d="M19 34 H24 M35 44 H40 M21 53 H25" stroke="#141A16" stroke-width="1.2" stroke-linecap="round" opacity="0.55"/>

                        <g class="olho-pisca">
                            <circle cx="25" cy="34" r="2.2" fill="#141A16"/>
                            <circle cx="24.3" cy="33.3" r="0.7" fill="#FFFFFF"/>
                            <circle cx="34" cy="34" r="2.2" fill="#141A16"/>
                            <circle cx="33.3" cy="33.3" r="0.7" fill="#FFFFFF"/>
                        </g>
                        <ellipse class="boca-canta" cx="29.5" cy="41.5" rx="2.6" ry="3.2" fill="#1B5E20" stroke="#141A16" stroke-width="1.4"/>

                        <path class="braco-cenoura-esq" d="M17 42 Q10 45 17 50" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                        <path class="braco-cenoura-mic" d="M40 43 L50 38" stroke="#141A16" stroke-width="1.7" stroke-linecap="round"/>
                    </g>
                </svg>
            </div>

            <!-- 3. TOMATE BATERISTA -->
            <div class="musico-box m-tomate">
                <svg width="94" height="96" viewBox="0 -20 94 96" fill="none" style="overflow:visible;">
                    <ellipse cx="47" cy="73" rx="30" ry="3.2" fill="#141A16" opacity="0.20"/>
                    <ellipse cx="47" cy="36" rx="19" ry="15" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8"/>
                    <path d="M35 28 C37 25 41 24 44 25" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/>
                    <path d="M47 21 L39 16 L44 21 L47 13 L50 21 L55 16 L47 21 Z" fill="#81C784" stroke="#1B5E20" stroke-width="1.6" stroke-linejoin="round"/>
                    <path d="M28 35 C28 22 66 22 66 35" stroke="#141A16" stroke-width="1.6"/>
                    <rect x="25.5" y="32" width="3.5" height="7" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                    <rect x="65" y="32" width="3.5" height="7" rx="1.5" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>
                    <g class="olho-pisca">
                        <circle cx="41.5" cy="35" r="2" fill="#141A16"/>
                        <circle cx="40.9" cy="34.4" r="0.6" fill="#FFFFFF"/>
                        <circle cx="52.5" cy="35" r="2" fill="#141A16"/>
                        <circle cx="51.9" cy="34.4" r="0.6" fill="#FFFFFF"/>
                    </g>
                    <path d="M43.5 40.5 Q47 44 50.5 40.5" stroke="#141A16" stroke-width="1.5" stroke-linecap="round"/>

                    <line class="be-anim" x1="31" y1="39" x2="20" y2="26" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <line class="bd-anim" x1="63" y1="39" x2="74" y2="26" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>

                    <g class="bumbo-anim">
                        <circle cx="47" cy="58" r="15" fill="#DDD8CE" stroke="#141A16" stroke-width="2"/>
                        <circle cx="47" cy="58" r="11.5" stroke="#141A16" stroke-width="1" stroke-dasharray="3 3"/>
                        <circle cx="47" cy="58" r="6" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.6"/>
                    </g>

                    <rect x="17" y="47" width="15" height="9" rx="1.5" fill="#EAE7E0" stroke="#141A16" stroke-width="1.6"/>
                    <line x1="17" y1="50" x2="32" y2="50" stroke="#1B5E20" stroke-width="1.3"/>
                    <line x1="24.5" y1="56" x2="24.5" y2="73" stroke="#141A16" stroke-width="1.7"/>
                    <line x1="74" y1="33" x2="74" y2="73" stroke="#141A16" stroke-width="1.7"/>
                    <ellipse class="prato-anim" cx="74" cy="33" rx="13" ry="2.8" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.8"/>
                </svg>
            </div>

            <!-- 4. MILHO BAIXISTA -->
            <div class="musico-box m-vagem">
                <svg width="88" height="88" viewBox="0 0 88 88" fill="none">
                    <ellipse cx="32" cy="85" rx="16" ry="2.8" fill="#141A16" opacity="0.18"/>
                    <path d="M27 69 V83 M37 69 V83" stroke="#141A16" stroke-width="1.9" stroke-linecap="round"/>
                    <path d="M22 84 H29 C29 81.5 24 81.5 22 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>
                    <path class="pe-batida" d="M36 84 H43 C43 81.5 38 81.5 36 84 Z" fill="#141A16" stroke="#141A16" stroke-width="1.4"/>

                    <g class="palha-milho">
                        <path d="M32 69 C22 63 18 44 10 34 C18 35 24 46 28 58 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5" stroke-linejoin="round"/>
                        <path d="M32 69 C42 63 46 44 54 34 C46 35 40 46 36 58 Z" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.5" stroke-linejoin="round"/>
                    </g>

                    <path d="M29 16 C25 9 20 11 22 16 M32 15 C31 7 35 7 34 15 M35 16 C39 9 43 12 40 17" stroke="#141A16" stroke-width="1.5" stroke-linecap="round"/>

                    <path d="M32 15 C22 15 21 56 32 67 C43 56 42 15 32 15 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8" stroke-linejoin="round"/>
                    <path d="M36 17 C41 23 41 53 32 65 C37 54 38 24 36 17 Z" fill="#D5D0C5"/>
                    <path d="M27 23 V48 M32 20 V50 M37 23 V48" stroke="#141A16" stroke-width="1.1" stroke-dasharray="2 3" stroke-linecap="round" opacity="0.32"/>

                    <g class="olho-pisca">
                        <circle cx="28.8" cy="28.5" r="1.9" fill="#141A16"/>
                        <circle cx="28.2" cy="27.9" r="0.65" fill="#FFFFFF"/>
                        <circle cx="35.5" cy="28.5" r="1.9" fill="#141A16"/>
                        <circle cx="34.9" cy="27.9" r="0.65" fill="#FFFFFF"/>
                    </g>
                    <path d="M29.5 34 Q32.5 36.5 35.5 33.8" stroke="#141A16" stroke-width="1.4" stroke-linecap="round"/>

                    <path d="M32 70 C19 66 14 53 7 45 C16 45 23 51 32 63 Z" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.5" stroke-linejoin="round"/>
                    <path d="M28 65 Q20 55 12 48" stroke="#1B5E20" stroke-width="1" stroke-linecap="round" opacity="0.65"/>
                    <path d="M32 70 C45 66 50 53 57 45 C48 45 41 51 32 63 Z" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.5" stroke-linejoin="round"/>
                    <path d="M36 65 Q44 55 52 48" stroke="#1B5E20" stroke-width="1" stroke-linecap="round" opacity="0.65"/>

                    <ellipse cx="31" cy="52" rx="10" ry="5.8" transform="rotate(-15 31 52)" fill="#2E7D32" stroke="#141A16" stroke-width="1.7"/>
                    <circle cx="29" cy="52.5" r="2" fill="#EAE7E0"/>
                    <line x1="40" y1="49" x2="66" y2="41" stroke="#141A16" stroke-width="2.3" stroke-linecap="round"/>
                    <rect x="65" y="38.5" width="5" height="4" rx="1" transform="rotate(-15 65 38.5)" fill="#1B5E20" stroke="#141A16" stroke-width="1.2"/>

                    <path class="dedilha-milho" d="M22 47 Q20 52 26 53" stroke="#141A16" stroke-width="1.8" stroke-linecap="round"/>
                    <path d="M42 45 Q48 46 52 44" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>

                    <path class="onda-1" d="M73 34 C77 38 77 44 73 48" stroke="#1B5E20" stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            </div>
        </div>
        """,
        height=162
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
    with st.expander("🚚 Importar Agendamentos do Portal Trizy (Excel .xls / .xlsx)", expanded=False):
        st.caption("Suba a planilha exportada do Trizy, escolha a aba e as colunas correspondentes. O sistema cruza o ID/Demanda com a coluna Observação do planejamento e atualiza a Data da entrega.")
        arq_trizy = st.file_uploader("📂 Planilha do Portal Trizy (.xls ou .xlsx):", type=("xls", "xlsx"), key="up_trizy_analise")
        if arq_trizy is not None:
            try:
                xl_trizy = pd.ExcelFile(arq_trizy)
                abas_trizy = xl_trizy.sheet_names
                idx_aba_tz = next(
                    (i for i, nm in enumerate(abas_trizy) if "DEMANDA" in limpar_texto(nm) or "AGEND" in limpar_texto(nm)),
                    0
                )
                aba_trizy_sel = st.selectbox(
                    "📑 Selecione a aba da planilha Trizy:",
                    options=abas_trizy,
                    index=idx_aba_tz,
                    key="sel_aba_trizy"
                )
                df_tz_raw = xl_trizy.parse(aba_trizy_sel, dtype=str).dropna(how="all").fillna("")
                if df_tz_raw.empty:
                    st.warning("A aba selecionada está vazia.")
                else:
                    cols_tz = list(df_tz_raw.columns)
                    col_id_sug = achar_col_bi(cols_tz, ("ID AGENDAMENTO", "ID", "DEMANDA", "PEDIDO", "CODIGO"))
                    idx_id_tz = cols_tz.index(col_id_sug) if col_id_sug in cols_tz else 0

                    cols_tz_rest = [c for c in cols_tz if c != cols_tz[idx_id_tz]] or cols_tz
                    col_dt_sug = achar_col_bi(cols_tz_rest, ("DATA DO AGENDAMENTO", "DATA AGENDAMENTO", "AGENDAMENTO", "DATA ENTREGA", "ENTREGA", "DATA"))
                    idx_dt_tz = cols_tz.index(col_dt_sug) if col_dt_sug in cols_tz else min(1, len(cols_tz) - 1)

                    tz_c1, tz_c2 = st.columns(2)
                    col_id_tz = tz_c1.selectbox("🔢 Coluna do ID / Demanda (para buscar na Observação):", options=cols_tz, index=idx_id_tz, key="map_col_id_tz")
                    col_dt_tz = tz_c2.selectbox("📅 Coluna da Data do Agendamento:", options=cols_tz, index=idx_dt_tz, key="map_col_dt_tz")

                    mapa_trizy = {}
                    for _, r_tz in df_tz_raw.iterrows():
                        id_val = str(r_tz.get(col_id_tz, "")).strip()
                        if not id_val or id_val.lower() in ("nan", "none", "null", "-"):
                            continue
                        if id_val.endswith(".0"):
                            id_val = id_val[:-2]

                        dt_raw_tz = str(r_tz.get(col_dt_tz, "")).strip()
                        if not dt_raw_tz or dt_raw_tz.lower() in ("nan", "none", "null", "nat", "-"):
                            continue

                        dt_parsed_tz = pd.to_datetime(dt_raw_tz, dayfirst=True, errors="coerce")
                        if pd.notna(dt_parsed_tz):
                            dt_fmt_tz = dt_parsed_tz.strftime("%d/%m/%Y")
                        else:
                            dt_fmt_tz = formatar_data_br_str(dt_raw_tz)

                        if id_val and dt_fmt_tz and "/" in dt_fmt_tz:
                            mapa_trizy[id_val] = dt_fmt_tz

                    if not mapa_trizy:
                        st.info("Nenhuma linha válida com ID/Demanda e Data do Agendamento encontrada nas colunas selecionadas.")
                    else:
                        df_plan_tz = carregar_dados("planejamento")
                        if df_plan_tz.empty:
                            st.warning("Nenhum pedido cadastrado no Planejamento Logística para cruzar.")
                        else:
                            for col_req_tz in COLUNAS_PLANEJAMENTO:
                                if col_req_tz not in df_plan_tz.columns:
                                    df_plan_tz[col_req_tz] = ""

                            matches_tz = list()
                            matches_tz = list()
                            for idx_ptz, row_ptz in df_plan_tz.iterrows():
                                obs_txt_tz = str(row_ptz.get("Observação", "")).strip()
                                if not obs_txt_tz or obs_txt_tz.lower() in ("nan", "none", "null"):
                                    continue
                                nums_obs = re.findall(r"\d+", obs_txt_tz)
                                id_encontrado = next((n for n in nums_obs if n in mapa_trizy), None)
                                if id_encontrado:
                                    nova_dt_tz = mapa_trizy[id_encontrado]
                                    ent_atual_tz = formatar_data_br_str(row_ptz.get("Data da entrega", ""))
                                    precisa_atualizar = (ent_atual_tz != nova_dt_tz)
                                    matches_tz.append({
                                        "_idx": idx_ptz,
                                        "Ordem": str(row_ptz.get("Ordem de Carregamento", "")).strip(),
                                        "Pedido": str(row_ptz.get("Nº Pedido", "")).strip(),
                                        "Cliente": str(row_ptz.get("Cliente", "")).strip(),
                                        "ID / Demanda Trizy": id_encontrado,
                                        "Entrega Atual": ent_atual_tz if ent_atual_tz else "—",
                                        "Nova Data Trizy": nova_dt_tz,
                                        "Situação": "🔄 Atualizar Data" if precisa_atualizar else "✅ Já Atualizada",
                                        "_alterar": precisa_atualizar
                                    })

                            if not matches_tz:
                                st.warning(f"Foram lidos {len(mapa_trizy)} registro(s) do Trizy, mas nenhum ID/Demanda foi encontrado na coluna 'Observação' dos pedidos do planejamento.")
                            else:
                                df_prev_tz = pd.DataFrame(matches_tz)
                                qtd_upd_tz = int(df_prev_tz["_alterar"].sum())
                                st.success(f"✅ {len(df_prev_tz)} pedido(s) localizado(s) pela Observação ({qtd_upd_tz} com data diferente para atualizar).")
                                st.dataframe(
                                    df_prev_tz[["Ordem", "Pedido", "Cliente", "ID / Demanda Trizy", "Entrega Atual", "Nova Data Trizy", "Situação"]],
                                    use_container_width=True,
                                    hide_index=True
                                )
                                if qtd_upd_tz > 0:
                                    if st.button(f"💾 Confirmar e Atualizar {qtd_upd_tz} Data(s) de Entrega no Planejamento", type="primary", key="btn_confirmar_trizy"):
                                        with st.spinner("Gravando datas de agendamento do Trizy no Planejamento..."):
                                            limpar_cache_operacional()
                                            df_plan_gravar = carregar_dados("planejamento")
                                            for c_pl_tz in COLUNAS_PLANEJAMENTO:
                                                if c_pl_tz not in df_plan_gravar.columns:
                                                    df_plan_gravar[c_pl_tz] = ""
                                            df_plan_gravar["Data da entrega"] = df_plan_gravar["Data da entrega"].astype(object)
                                            for item_tz in matches_tz:
                                                if item_tz["_alterar"] and item_tz["_idx"] in df_plan_gravar.index:
                                                    df_plan_gravar.at[item_tz["_idx"], "Data da entrega"] = item_tz["Nova Data Trizy"]
                                            salvar_dados(df_plan_gravar[COLUNAS_PLANEJAMENTO], "planejamento")
                                            limpar_cache_operacional()
                                        st.success(f"🎉 {qtd_upd_tz} pedido(s) atualizado(s) com a Data do Agendamento do Trizy!")
                                        st.rerun()
            except Exception as e_tz:
                st.error(f"Erro ao processar a planilha do Trizy: {e_tz}")
        
    feriados_sys = obter_feriados_sistema()
    mapa_lt = obter_mapa_lead_time()

    def _parse_data_bi_segura(val_raw):
        if val_raw is None or pd.isna(val_raw):
            return pd.NaT
        if isinstance(val_raw, (datetime, pd.Timestamp)):
            return pd.Timestamp(val_raw.year, val_raw.month, val_raw.day)
        s = str(val_raw).strip()
        if not s or s.upper() in ("NAN", "NONE", "NAT", "<NA>", "-"):
            return pd.NaT
        parte_dt = s.split()[0]
        m_iso = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", parte_dt)
        if m_iso:
            try:
                return pd.Timestamp(int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3)))
            except Exception:
                return pd.NaT
        m_br = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})$", parte_dt)
        if m_br:
            dia_i, mes_i, ano_i = int(m_br.group(1)), int(m_br.group(2)), int(m_br.group(3))
            if ano_i < 100:
                ano_i += 2000
            try:
                return pd.Timestamp(ano_i, mes_i, dia_i)
            except Exception:
                return pd.NaT
        return pd.to_datetime(s, dayfirst=True, errors="coerce")

    with st.expander("📂 Importar Planilha de Pedidos do BI (Excel .xls / .xlsx / .csv)", expanded=False):
        st.caption("Suba a carteira exportada do BI para compilar os SKUs por pedido, cruzar com o Lead Time e flagar os pedidos para o Planejamento.")
        c_up_bi, c_cfg_bi = st.columns((3, 1))
        with c_up_bi:
            arquivo_bi = st.file_uploader("📂 Planilha de Pedidos do BI (.xls, .xlsx, .csv):", type=("xls", "xlsx", "csv"), key="up_bi_analise")
        with c_cfg_bi:
            limite_critico = st.number_input("⚠️ Limite Crítico (dias úteis p/ carregar):", min_value=0.0, max_value=15.0, value=2.0, step=0.5)

    if arquivo_bi is not None:
        assinatura_bi = f"{arquivo_bi.name}_{arquivo_bi.size}"
        if st.session_state.get("bi_assinatura_cols") != assinatura_bi:
            try:
                cab_bytes = arquivo_bi.read(8)
                arquivo_bi.seek(0)
                if cab_bytes.startswith(b"PK\x03\x04"):
                    import openpyxl
                    wb_cab = openpyxl.load_workbook(arquivo_bi, read_only=True, data_only=True)
                    cols_detectadas = list()
                    for nm_aba in wb_cab.sheetnames:
                        ws_c = wb_cab[nm_aba]
                        for row_c in ws_c.iter_rows(max_row=5, values_only=True):
                            if row_c and sum(1 for v in row_c if v is not None and str(v).strip() != "") >= 2:
                                cols_detectadas = [str(c).strip() if c is not None and str(c).strip() != "" else f"Col_{i+1}" for i, c in enumerate(row_c)]
                                break
                        if cols_detectadas:
                            break
                    wb_cab.close()
                elif cab_bytes.startswith(b"\xd0\xcf\x11\xe0"):
                    df_cab = pd.read_excel(arquivo_bi, nrows=2, dtype=str)
                    cols_detectadas = [str(c).strip() for c in df_cab.columns]
                else:
                    primeira_linha_txt = arquivo_bi.readline().decode("utf-8-sig", errors="ignore")
                    arquivo_bi.seek(0)
                    sep_bi = ";" if primeira_linha_txt.count(";") >= primeira_linha_txt.count(",") else ","
                    try:
                        df_cab = pd.read_csv(arquivo_bi, sep=sep_bi, nrows=2, dtype=str, encoding="utf-8-sig", on_bad_lines="skip")
                    except Exception:
                        arquivo_bi.seek(0)
                        df_cab = pd.read_csv(arquivo_bi, sep=sep_bi, nrows=2, dtype=str, encoding="latin-1", on_bad_lines="skip")
                    cols_detectadas = [str(c).strip() for c in df_cab.columns]

                st.session_state["bi_cols_disponiveis"] = cols_detectadas
                st.session_state["bi_assinatura_cols"] = assinatura_bi
                st.session_state.pop("bi_compilado_cache", None)
            except Exception as e_cab:
                st.error(f"Erro ao ler cabeçalho do BI: {e_cab}")

    cols_bi = st.session_state.get("bi_cols_disponiveis", list())
    if arquivo_bi is not None and cols_bi:
        try:
            with st.expander("⚙️ Mapeamento das Colunas do BI (confirme se estão corretas)", expanded=True):
                def _opcoes_bi(termos):
                    enc = achar_col_bi(cols_bi, termos)
                    return ["(Nenhum)"] + cols_bi, (cols_bi.index(enc) + 1) if enc in cols_bi else 0

                m1, m2, m3, m4, m5 = st.columns(5)
                op_ped, idx_ped = _opcoes_bi(("PEDIDO", "CARGA", "ORDEM", "NUMERO", "DOCUMENTO"))
                col_ped_bi = m1.selectbox("Número do Pedido / Carga:", op_ped, index=idx_ped)
                op_fil, idx_fil = _opcoes_bi(("FILIAL", "UNIDADE", "LOCAL", "CD", "DEPOSITO", "EMPRESA"))
                col_filial_bi = m2.selectbox("Filial (Local Carreg.):", op_fil, index=idx_fil)
                op_cli, idx_cli = _opcoes_bi(("CLIENTE", "DESTINATARIO", "RAZAO"))
                col_cli_bi = m3.selectbox("Cliente (Opcional):", op_cli, index=idx_cli)
                op_uf, idx_uf = _opcoes_bi(("UF", "ESTADO"))
                col_uf_bi = m4.selectbox("Estado (UF):", op_uf, index=idx_uf)
                op_cid, idx_cid = _opcoes_bi(("CIDADE", "MUNICIPIO"))
                col_cid_bi = m5.selectbox("Cidade:", op_cid, index=idx_cid)

                m6, m7, m8, m9, m10 = st.columns(5)
                op_dc, idx_dc = _opcoes_bi(("EMISSAO", "CRIADA", "LANCAMENTO", "CRIACAO", "DATA PEDIDO", "INCLUSAO", "DATA", "FATURAMENTO"))
                col_dt_cria = m6.selectbox("Data de Criação/Lançamento:", op_dc, index=idx_dc)
                op_de, idx_de = _opcoes_bi(("ENTREGA", "PREVISAO", "AGENDAMENTO", "PRAZO"))
                col_dt_ent = m7.selectbox("Data de Entrega:", op_de, index=idx_de)
                op_val, idx_val = _opcoes_bi(("VALOR", "TOTAL", "FATURAMENTO", "PRECO", "VLR"))
                col_val_bi = m8.selectbox("Valor do Pedido (R$):", op_val, index=idx_val)
                op_vol, idx_vol = _opcoes_bi(("VOLUME", "CAIXA", "QTD", "QUANTIDADE", "UNIDADE"))
                col_vol_bi = m9.selectbox("Qtd de Volumes:", op_vol, index=idx_vol)
                op_nf, idx_nf = _opcoes_bi(("NOTA FISCAL", "NF", "NFE", "NOTA", "DANFE"))
                col_nf_bi = m10.selectbox("Nota Fiscal (Opcional):", op_nf, index=idx_nf)

            chave_comp = f"{st.session_state.get('bi_assinatura_cols')}|{col_ped_bi}|{col_filial_bi}|{col_cli_bi}|{col_uf_bi}|{col_cid_bi}|{col_dt_cria}|{col_dt_ent}|{col_val_bi}|{col_vol_bi}|{col_nf_bi}"

            if st.button("🚀 Processar e Analisar Carteira do BI", type="primary", use_container_width=True, key="btn_processar_bi_agora"):
                idx_map = {c: i for i, c in enumerate(cols_bi)}
                mapa_cols_usar = {
                    "ped": idx_map.get(col_ped_bi, -1),
                    "fil": idx_map.get(col_filial_bi, -1),
                    "cli": idx_map.get(col_cli_bi, -1),
                    "uf": idx_map.get(col_uf_bi, -1),
                    "cid": idx_map.get(col_cid_bi, -1),
                    "dc": idx_map.get(col_dt_cria, -1),
                    "de": idx_map.get(col_dt_ent, -1),
                    "val": idx_map.get(col_val_bi, -1),
                    "vol": idx_map.get(col_vol_bi, -1),
                    "nf": idx_map.get(col_nf_bi, -1),
                }
                cols_usar_idx = sorted({v for v in mapa_cols_usar.values() if v >= 0})

                arquivo_bi.seek(0)
                cab_b = arquivo_bi.read(8)
                arquivo_bi.seek(0)

                if cab_b.startswith(b"PK\x03\x04"):
                    import openpyxl
                    wb_s = openpyxl.load_workbook(arquivo_bi, read_only=True, data_only=True)
                    linhas_util = list()
                    for nm_aba in wb_s.sheetnames:
                        ws_s = wb_s[nm_aba]
                        achou_hdr = False
                        vazias = 0
                        for r_vals in ws_s.iter_rows(values_only=True):
                            if not r_vals or not any(v is not None and str(v).strip() != "" for v in r_vals):
                                vazias += 1
                                if achou_hdr and vazias >= 30:
                                    break
                                continue
                            vazias = 0
                            if not achou_hdr:
                                achou_hdr = True
                                continue
                            n_c = len(r_vals)
                            linhas_util.append([r_vals[idx_u] if idx_u < n_c else "" for idx_u in cols_usar_idx])
                        if achou_hdr:
                            break
                    wb_s.close()
                    df_raw_min = pd.DataFrame(linhas_util, columns=cols_usar_idx).astype(str)
                    del linhas_util
                elif cab_b.startswith(b"\xd0\xcf\x11\xe0"):
                    df_raw_min = pd.read_excel(arquivo_bi, usecols=cols_usar_idx, dtype=str)
                    df_raw_min.columns = cols_usar_idx
                else:
                    primeira_linha_b = arquivo_bi.readline().decode("utf-8-sig", errors="ignore")
                    arquivo_bi.seek(0)
                    sep_bi_b = ";" if primeira_linha_b.count(";") >= primeira_linha_b.count(",") else ","
                    try:
                        df_raw_min = pd.read_csv(arquivo_bi, sep=sep_bi_b, dtype=str, usecols=cols_usar_idx, encoding="utf-8-sig", on_bad_lines="skip")
                    except Exception:
                        arquivo_bi.seek(0)
                        df_raw_min = pd.read_csv(arquivo_bi, sep=sep_bi_b, dtype=str, usecols=cols_usar_idx, encoding="latin-1", on_bad_lines="skip")
                    df_raw_min.columns = cols_usar_idx

                df_raw_min = df_raw_min.fillna("")

                def _col_min(chave_m):
                    ix = mapa_cols_usar[chave_m]
                    if ix >= 0 and ix in df_raw_min.columns:
                        return df_raw_min[ix].astype(str).str.strip()
                    return pd.Series("", index=df_raw_min.index)

                if mapa_cols_usar["ped"] >= 0:
                    s_ped = _col_min("ped").str.replace(r"\.0$", "", regex=True)
                else:
                    s_ped = pd.Series([f"LINHA-{i+1}" for i in range(len(df_raw_min))], index=df_raw_min.index)

                s_ped_k = s_ped.str.upper()
                mask_ok = ~s_ped_k.isin(["", "NAN", "NONE", "NULL", "<NA>"])
                total_linhas_lidas_v = int(mask_ok.sum())

                def _num_vec(s_str):
                    s = s_str.str.replace("R$", "", regex=False).str.replace(" ", "", regex=False)
                    tem_v = s.str.contains(",", na=False)
                    tem_p = s.str.contains(r"\.", na=False)
                    s_amb = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                    s_vir = s.str.replace(",", ".", regex=False)
                    s = s.where(~(tem_v & tem_p), s_amb).where(~(tem_v & ~tem_p), s_vir)
                    return pd.to_numeric(s, errors="coerce").fillna(0.0)

                df_ag = pd.DataFrame({
                    "ped_k": s_ped_k[mask_ok],
                    "ped_exib": s_ped[mask_ok],
                    "filial": _col_min("fil")[mask_ok],
                    "cliente": _col_min("cli")[mask_ok],
                    "uf": _col_min("uf")[mask_ok],
                    "cidade": _col_min("cid")[mask_ok],
                    "dc_raw": _col_min("dc")[mask_ok],
                    "de_raw": _col_min("de")[mask_ok],
                    "val": _num_vec(_col_min("val")[mask_ok]),
                    "vol": _num_vec(_col_min("vol")[mask_ok]),
                    "qtd": 1,
                    "nf": _col_min("nf")[mask_ok].str.replace(r"\.0$", "", regex=True)
                })
                del df_raw_min

                for col_txt_ag in ("filial", "cliente", "uf", "cidade", "dc_raw", "de_raw", "nf"):
                    df_ag[col_txt_ag] = df_ag[col_txt_ag].where(~df_ag[col_txt_ag].str.upper().isin(["NAN", "NONE", "NULL", "-", "<NA>"]), "")

                # Agregação 100% nativa em C (sem funções Python lentas por grupo)
                df_somas = df_ag.groupby("ped_k", sort=False, as_index=False).agg(
                    ped_exib=("ped_exib", "first"),
                    filial=("filial", "max"),
                    cliente=("cliente", "max"),
                    uf=("uf", "max"),
                    cidade=("cidade", "max"),
                    dc_raw=("dc_raw", "max"),
                    de_raw=("de_raw", "max"),
                    val=("val", "sum"),
                    vol=("vol", "sum"),
                    qtd=("qtd", "sum")
                )
                df_nfs_grp = (
                    df_ag[df_ag["nf"] != ""][["ped_k", "nf"]]
                    .drop_duplicates()
                    .groupby("ped_k", sort=False)["nf"]
                    .apply(list)
                    .reset_index()
                )
                df_grp = pd.merge(df_somas, df_nfs_grp, on="ped_k", how="left")
                del df_ag, df_somas, df_nfs_grp

                df_grp["dt_c_vec"] = pd.to_datetime(df_grp["dc_raw"], dayfirst=True, errors="coerce")
                df_grp["dt_e_vec"] = pd.to_datetime(df_grp["de_raw"], dayfirst=True, errors="coerce")

                pedidos_compilados = {}
                ordem_pedidos_bi = list()
                for rg in df_grp.itertuples(index=False):
                    pk = rg.ped_k
                    ordem_pedidos_bi.append(pk)
                    pedidos_compilados[pk] = {
                        "ped_exib": rg.ped_exib,
                        "filial": rg.filial,
                        "cliente": rg.cliente,
                        "uf": rg.uf,
                        "cidade": rg.cidade,
                        "valor_num": float(rg.val),
                        "vol_num": int(round(float(rg.vol))),
                        "qtd_itens": int(rg.qtd),
                        "nfs": rg.nf if isinstance(rg.nf, list) else list(),
                        "dt_c": rg.dt_c_vec,
                        "dt_e": rg.dt_e_vec
                    }
                del df_grp

                st.session_state["bi_compilado_cache"] = (pedidos_compilados, ordem_pedidos_bi, total_linhas_lidas_v)
                st.session_state["bi_chave_compilada"] = chave_comp

            if st.session_state.get("bi_compilado_cache") is None:
                st.info("👆 Confirme as colunas acima e clique em **🚀 Processar e Analisar Carteira do BI**.")
                st.stop()

            pedidos_compilados, ordem_pedidos_bi, total_linhas_lidas = st.session_state["bi_compilado_cache"]

            if not ordem_pedidos_bi:
                st.warning("Nenhum pedido válido encontrado com as colunas mapeadas.")
            else:
                df_plan_exist = carregar_dados("planejamento")
                peds_plan_exatos = set()
                peds_plan_tokens = set()
                mapa_plan_por_ped = {}
                if not df_plan_exist.empty and "Nº Pedido" in df_plan_exist.columns:
                    for idx_pe, r_pe in df_plan_exist.iterrows():
                        p_limp = limpar_texto(r_pe.get("Nº Pedido", ""))
                        if p_limp:
                            peds_plan_exatos.add(p_limp)
                            mapa_plan_por_ped[p_limp] = (idx_pe, r_pe)
                            for tok in re.findall(r"[A-Z0-9]+", p_limp):
                                peds_plan_tokens.add(tok)
                                if tok not in mapa_plan_por_ped:
                                    mapa_plan_por_ped[tok] = (idx_pe, r_pe)

                hoje_dt = pd.Timestamp(datetime.now(FUSO_BR).date())
                linhas_analise = list()
                cidades_sem_lt = set()
                alteracoes_entrega = list()

                for ped_k_raw in ordem_pedidos_bi:
                    comp = pedidos_compilados[ped_k_raw]
                    ped_val = comp["ped_exib"]
                    ped_k = limpar_texto(ped_val)
                    fil_val = comp["filial"]
                    cli_val = comp["cliente"]
                    uf_val = limpar_texto(comp["uf"])
                    cid_val = limpar_texto(comp["cidade"])
                    valor_num = comp["valor_num"]
                    vol_num = comp["vol_num"]
                    qtd_skus_ped = comp["qtd_itens"]
                    nf_raw = " | ".join(comp["nfs"])
                    dt_c = comp["dt_c"]
                    dt_e = comp["dt_e"]

                    lt_info = mapa_lt.get((uf_val, cid_val))
                    if lt_info is None and (uf_val or cid_val):
                        cidades_sem_lt.add(f"{cid_val}/{uf_val}")

                    if pd.notna(dt_c) and pd.notna(dt_e) and lt_info is not None:
                        lt_dias, dias_rota, km_val, fc_val, ft_val = calcular_dias_rota_efetivos(lt_info)
                        km_tag_bi = f" • {int(round(km_val))}km" if km_val is not None else ""
                        veic_sug = "CARRETA" if vol_num > 1800 else "TRUCK"
                        frete_sug_num = (fc_val if veic_sug == "CARRETA" else ft_val) or 0.0
                        frete_sug_fmt = f"R$ {frete_sug_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if frete_sug_num > 0 else "-"
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
                        rota_str = f"{lt_dias}d ({dias_rota}d rota{km_tag_bi})"
                    else:
                        janela_exp = None
                        dt_lim_str = "-"
                        obs_criacao = "-"
                        veic_sug = "CARRETA" if vol_num > 1800 else "TRUCK"
                        frete_sug_fmt = "-"
                        lt_tot_exib = lt_info[0] if isinstance(lt_info, tuple) else lt_info
                        rota_str = f"{lt_tot_exib}d" if lt_tot_exib is not None else "-"
                        status_sla = "⚪ Sem Lead Time / Data Inválida"
                        ordem_prio = 5

                    esta_no_plan = (ped_k in peds_plan_exatos) or (ped_k in peds_plan_tokens)
                    ja_wms = "🚚 Já no Planejamento" if esta_no_plan else "🆕 Novo (Fora do WMS)"
                    valor_fmt = f"R$ {valor_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    if esta_no_plan and pd.notna(dt_e) and ped_k in mapa_plan_por_ped:
                        nova_ent_str = dt_e.strftime("%d/%m/%Y")
                        idx_pe, r_pe = mapa_plan_por_ped[ped_k]
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
                        "Programar": False,
                        "Prioridade": ordem_prio,
                        "Status SLA": status_sla,
                        "Filial": fil_val if fil_val else "-",
                        "Pedido": ped_val,
                        "SKUs": qtd_skus_ped,
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
                        "Veículo Sugerido": veic_sug,
                        "Frete Tabela": frete_sug_fmt,
                        "Situação WMS": ja_wms
                    })

                df_res_bi = pd.DataFrame(linhas_analise)

                if not df_res_bi.empty:
                    df_res_bi = df_res_bi.sort_values(by=["Prioridade", "Dias Úteis p/ Carregar"], ascending=[True, True], na_position="last").reset_index(drop=True)

                    if total_linhas_lidas > len(df_res_bi):
                        st.info(f"🧩 **Compilação automática:** {total_linhas_lidas} linhas de itens do BI foram consolidadas em **{len(df_res_bi)} pedido(s) único(s)** com valores e volumes somados.")

                    if alteracoes_entrega:
                        with st.container(border=True):
                            st.error(f"🚨 **ALERTA COMERCIAL: {len(alteracoes_entrega)} pedido(s) já programado(s) tiveram a Data de Entrega alterada no BI!**")
                            st.dataframe(pd.DataFrame(alteracoes_entrega).drop(columns=["idx_plan"]), use_container_width=True, hide_index=True)
                            if st.button("🔄 Atualizar Datas no Planejamento e Disparar Alerta para a Equipe", type="primary"):
                                limpar_cache_operacional()
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
                                    limpar_cache_operacional()
                                    st.success(f"🔔 {qtd_alt} pedido(s) atualizados no Planejamento e notificação disparada para toda a equipe!")
                                    st.rerun()

                    if cidades_sem_lt:
                        st.warning(f"⚠️ **{len(cidades_sem_lt)} cidade(s)** não encontrada(s) na aba `lead time`: {', '.join(sorted(list(cidades_sem_lt))[:10])}")

                    qtd_atrasados_bi = int(df_res_bi["Prioridade"].isin([1, 2]).sum())
                    qtd_atencao_bi = int((df_res_bi["Prioridade"] == 3).sum())
                    qtd_prazo_bi = int((df_res_bi["Prioridade"] == 4).sum())
                    tot_val_str = f"R$ {df_res_bi['Valor_Num'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    tot_vol_str = f"{int(df_res_bi['Volumes'].sum()):,}".replace(",", ".")

                    def _card_kpi_bi(titulo, valor, bg, borda, cor_tit, cor_val):
                        return (
                            f"<div style='background:{bg}; border:1px solid {borda}44; border-left:4px solid {borda}; "
                            f"border-radius:10px; padding:8px 12px; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.03);'>"
                            f"<div style='font-size:0.67rem; text-transform:uppercase; letter-spacing:0.04em; font-weight:700; color:{cor_tit}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{titulo}</div>"
                            f"<div style='font-size:1.28rem; font-weight:800; color:{cor_val}; margin-top:2px;'>{valor}</div>"
                            f"</div>"
                        )

                    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
                    k1.markdown(_card_kpi_bi("📦 Pedidos Únicos", f"{len(df_res_bi):,}".replace(",", "."), "#FAF8F5", "#1B5E20", "#4A544D", "#141A16"), unsafe_allow_html=True)
                    k2.markdown(_card_kpi_bi("🔴/🟠 Críticos/Hoje", qtd_atrasados_bi, "#FEF2F2", "#DC2626", "#991B1B", "#7F1D1D"), unsafe_allow_html=True)
                    k3.markdown(_card_kpi_bi("🟡 Atenção", qtd_atencao_bi, "#FFFBEB", "#D97706", "#92400E", "#78350F"), unsafe_allow_html=True)
                    k4.markdown(_card_kpi_bi("🟢 No Prazo", qtd_prazo_bi, "#ECFDF5", "#059669", "#065F46", "#064E3B"), unsafe_allow_html=True)
                    k5.markdown(_card_kpi_bi("💰 Valor Carteira", tot_val_str, "linear-gradient(135deg, #141A16 0%, #1E3323 100%)", "#4CAF50", "#A5D6A7", "#FFFFFF"), unsafe_allow_html=True)
                    k6.markdown(_card_kpi_bi("🧊 Total Volumes", tot_vol_str, "#F0F9FF", "#0284C7", "#075985", "#0C4A6E"), unsafe_allow_html=True)

                    f_bi1, f_bi2 = st.columns(2)
                    filtro_sla = f_bi1.multiselect(
                        "Filtrar por Indicador de Prazo:",
                        options=df_res_bi["Status SLA"].unique().tolist(),
                        default=df_res_bi["Status SLA"].unique().tolist()
                    )
                    filtro_wms_bi = f_bi2.multiselect(
                        "Filtrar por Situação WMS:",
                        options=df_res_bi["Situação WMS"].unique().tolist(),
                        default=df_res_bi["Situação WMS"].unique().tolist()
                    )

                    df_exib_bi = df_res_bi[
                        (df_res_bi["Status SLA"].isin(filtro_sla)) &
                        (df_res_bi["Situação WMS"].isin(filtro_wms_bi))
                    ].drop(columns=["Prioridade", "Valor_Num", "NF_Raw"]).copy()
   
                    df_pagina_bi = df_exib_bi.head(300).copy()

                    def _cor_linha_sla_bi(row_bi):
                        st_txt = str(row_bi.get("Status SLA", ""))
                        if "Atrasado" in st_txt:
                            bg = "#FEE2E2"
                        elif "Hoje" in st_txt:
                            bg = "#FFEDD5"
                        elif "Atenção" in st_txt:
                            bg = "#FEF9C3"
                        elif "Viável" in st_txt or "Prazo" in st_txt:
                            bg = "#DCFCE7"
                        else:
                            bg = "#F8FAFC"
                        return [f"background-color: {bg}; color: #111827;" for _ in row_bi]

                    st.caption("☑️ **Marque a caixinha `Programar` na primeira coluna** nos pedidos que deseja enviar ao Planejamento Logística:")
                    cols_readonly_bi = [c for c in df_exib_bi.columns if c != "Programar"]
                    df_editado_bi = st.data_editor(
                        df_pagina_bi.style.apply(_cor_linha_sla_bi, axis=1),
                        df_pagina_bi,
                        key="editor_flags_analise_bi",
                        use_container_width=True,
                        hide_index=True,
                        disabled=cols_readonly_bi,
                        column_config={
                            "Programar": st.column_config.CheckboxColumn("☑️ Programar", help="Marque para enviar este pedido ao Planejamento Logística", default=False, width="small"),
                            "Status SLA": st.column_config.TextColumn("🚦 Status SLA", width="medium"),
                            "Filial": st.column_config.TextColumn("🏭 Filial", width="small"),
                            "Pedido": st.column_config.TextColumn("📦 Pedido", width="small"),
                            "SKUs": st.column_config.NumberColumn("🏷️ SKUs", width="small"),
                            "Nota Fiscal": st.column_config.TextColumn("🧾 NF", width="small"),
                            "Cliente": st.column_config.TextColumn("🏢 Cliente", width="medium"),
                            "Cidade": st.column_config.TextColumn("📍 Cidade", width="medium"),
                            "UF": st.column_config.TextColumn("🗺️ UF", width="small"),
                            "Valor (R$)": st.column_config.TextColumn("💰 Valor Total", width="small"),
                            "Volumes": st.column_config.NumberColumn("🧊 Volumes", width="small"),
                            "Criação": st.column_config.TextColumn("📅 Criação", width="small"),
                            "Tempo Parado": st.column_config.TextColumn("⏳ Tempo Parado", width="medium"),
                            "Entrega": st.column_config.TextColumn("🏁 Entrega", width="small"),
                            "LT Total (Rota)": st.column_config.TextColumn("⏱️ Lead Time", width="small"),
                            "Dias Úteis p/ Carregar": st.column_config.NumberColumn("📆 Dias Úteis", width="small"),
                            "Sugestão Carregamento": st.column_config.TextColumn("🎯 Sugestão Carreg.", width="small"),
                            "Veículo Sugerido": st.column_config.TextColumn("🚛 Veículo", width="small"),
                            "Frete Tabela": st.column_config.TextColumn("💵 Frete Tabela", width="small"),
                            "Situação WMS": st.column_config.TextColumn("📋 Situação WMS", width="medium"),
                        }
                    )

                    df_flagados_novos = df_editado_bi[
                        (df_editado_bi["Programar"] == True) &
                        (df_editado_bi["Situação WMS"] == "🆕 Novo (Fora do WMS)")
                    ]
                    df_flagados_ja_wms = df_editado_bi[
                        (df_editado_bi["Programar"] == True) &
                        (df_editado_bi["Situação WMS"] != "🆕 Novo (Fora do WMS)")
                    ]

                    if not df_flagados_ja_wms.empty:
                        st.warning(f"⚠️ {len(df_flagados_ja_wms)} pedido(s) flagado(s) já estão no Planejamento Logística e serão ignorados para evitar duplicidade.")

                    c_act1, c_act2 = st.columns((2, 1.5), vertical_alignment="center")
                    with c_act1:
                        qtd_flag_ok = len(df_flagados_novos)
                        if st.button(f"🚚 Imputar {qtd_flag_ok} Pedido(s) Flagado(s) no Planejamento Logística", type="primary", disabled=(qtd_flag_ok == 0), use_container_width=True):
                            limpar_cache_operacional()
                            df_p_atual = carregar_dados("planejamento")
                            if df_p_atual is None:
                                st.error("⚠️ Falha temporária ao ler a aba 'planejamento' no Google Sheets. Tente clicar novamente em 3 segundos.")
                                st.stop()

                            for c_p in COLUNAS_PLANEJAMENTO:
                                if c_p not in df_p_atual.columns:
                                    df_p_atual[c_p] = ""

                            df_p_atual = df_p_atual.dropna(how="all").fillna("")
                            peds_existentes_agora = df_p_atual["Nº Pedido"].astype(str).tolist()
                            novos_plan = list()

                            for p_esc in df_flagados_novos["Pedido"].tolist():
                                if any(pedido_contido_no_planejamento(p_esc, p_ex) for p_ex in peds_existentes_agora):
                                    continue
                                linhas_match = df_res_bi[df_res_bi["Pedido"] == p_esc].to_dict(orient="records")
                                if not linhas_match:
                                    continue
                                r_esc = linhas_match.pop(0)
                                nova_l = {c_p: "" for c_p in COLUNAS_PLANEJAMENTO}
                                nova_l["Data"] = r_esc["Sugestão Carregamento"] if r_esc["Sugestão Carregamento"] != "-" else ""
                                nova_l["Local de Carregamento"] = r_esc["Filial"] if r_esc.get("Filial", "-") != "-" else ""
                                nova_l["Nº Pedido"] = r_esc["Pedido"]
                                nova_l["Valor Pedido"] = r_esc["Valor (R$)"]
                                nova_l["Cliente"] = r_esc["Cliente"]
                                nova_l["UF"] = r_esc["UF"]
                                nova_l["Cidade"] = r_esc["Cidade"]
                                nova_l["Data da entrega"] = formatar_data_br_str(r_esc["Entrega"]) if r_esc["Entrega"] != "-" else ""
                                nova_l["Observação"] = f"SLA BI | {r_esc['SKUs']} SKUs | {r_esc['Volumes']} vol | LT: {r_esc['LT Total (Rota)']} | {r_esc['Tempo Parado']}"
                                nova_l["Status"] = "⏳ Aguardando Veículo"
                                nova_l["Nota Fiscal"] = f"NF {r_esc['NF_Raw']}" if r_esc.get("NF_Raw") else ""
                                nova_l["Tipo de Veículo"] = r_esc.get("Veículo Sugerido", "")
                                nova_l["Valor de Frete"] = r_esc.get("Frete Tabela", "") if r_esc.get("Frete Tabela", "-") != "-" else ""
                                novos_plan.append(nova_l)

                            if novos_plan:
                                df_p_final = pd.concat([df_p_atual[COLUNAS_PLANEJAMENTO], pd.DataFrame(novos_plan)], ignore_index=True)
                                salvar_dados(df_p_final[COLUNAS_PLANEJAMENTO], "planejamento")
                                limpar_cache_operacional()
                                st.session_state.pop("editor_flags_analise_bi", None)
                                st.success(f"🎉 {len(novos_plan)} pedido(s) consolidado(s) adicionado(s) ao Planejamento sem duplicidade!")
                                st.rerun()

                    with c_act2:
                        buf_bi = io.BytesIO()
                        with pd.ExcelWriter(buf_bi, engine="openpyxl") as writer:
                            df_exib_bi.drop(columns=["Programar"], errors="ignore").to_excel(writer, index=False, sheet_name="Analise_Lead_Time")
                        st.download_button(
                            "📥 Baixar Análise Consolidada (.xlsx)",
                            data=buf_bi.getvalue(),
                            file_name=f"Analise_Pedidos_LeadTime_{datetime.now(FUSO_BR).strftime('%d%m%Y')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

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
                                limpar_cache_operacional()
                                st.success(f"✅ {qtd_vinc} Nota(s) Fiscal(is) vinculada(s) com sucesso!")
                                st.rerun()
                            else:
                                st.warning("Todas essas Notas Fiscais já estavam vinculadas no Planejamento.")

        except Exception as e_bi:
            st.error(f"Erro ao ler a planilha do BI: {e_bi}")

    if arq_trizy is None and arquivo_bi is None:
        components.html(
            """
            <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
            @keyframes digitarEsq {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-3px) rotate(-7deg); }
            }
            @keyframes digitarDir {
                0%, 100% { transform: translateY(-3px) rotate(7deg); }
                50% { transform: translateY(0px) rotate(0deg); }
            }
            @keyframes cabecaAnalisa {
                0%, 100% { transform: rotate(0deg) translateY(0px); }
                50% { transform: rotate(2.5deg) translateY(-1.5px); }
            }
            @keyframes barraSobe {
                0%, 100% { transform: scaleY(0.8); }
                50% { transform: scaleY(1.15); }
            }
            @keyframes vaporCafe {
                0% { transform: translateY(0px); opacity: 0; }
                50% { opacity: 0.75; }
                100% { transform: translateY(-11px); opacity: 0; }
            }
            @keyframes dadoFlutua1 {
                0%, 100% { transform: translateY(0px) scale(0.95); opacity: 0.65; }
                50% { transform: translateY(-7px) scale(1.05); opacity: 1; }
            }
            @keyframes dadoFlutua2 {
                0%, 100% { transform: translateY(-5px) scale(1.05); opacity: 1; }
                50% { transform: translateY(2px) scale(0.95); opacity: 0.65; }
            }
            .analista-wrap {
                width: 100%;
                max-width: 480px;
                margin: 22px auto 0 auto;
                text-align: center;
                font-family: sans-serif;
            }
            .cabeca-nerd { transform-box: fill-box; transform-origin: bottom center; animation: cabecaAnalisa 2.5s ease-in-out infinite; }
            .braco-esq { transform-box: fill-box; transform-origin: top left; animation: digitarEsq 0.4s ease-in-out infinite; }
            .braco-dir { transform-box: fill-box; transform-origin: top left; animation: digitarDir 0.4s ease-in-out infinite; }
            .barra-g { transform-box: fill-box; transform-origin: bottom center; animation: barraSobe 1.5s ease-in-out infinite; }
            .fumaca-cafe { animation: vaporCafe 2.1s ease-in-out infinite; }
            .flut-1 { animation: dadoFlutua1 2.8s ease-in-out infinite; }
            .flut-2 { animation: dadoFlutua2 3.1s ease-in-out infinite; }
            </style>
            <div class="analista-wrap">
                <svg width="310" height="168" viewBox="0 0 310 168" fill="none">
                    <!-- Sombra da Mesa -->
                    <ellipse cx="155" cy="150" rx="122" ry="4.5" fill="#141A16" opacity="0.15"/>

                    <!-- Ícones Flutuantes de Análise acima da Tela -->
                    <g class="flut-1">
                        <rect x="182" y="34" width="22" height="16" rx="4" fill="#E8F5E9" stroke="#1B5E20" stroke-width="1.5"/>
                        <path d="M188 42 L191.5 45.5 L198 38.5" stroke="#1B5E20" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </g>
                    <g class="flut-2">
                        <circle cx="222" cy="48" r="10" fill="#C8E6C9" stroke="#1B5E20" stroke-width="1.5"/>
                        <text x="222" y="51.5" text-anchor="middle" font-family="sans-serif" font-size="9.5" font-weight="800" fill="#143618">BI</text>
                    </g>

                    <!-- Caneca de Café Grano + Vapor -->
                    <g>
                        <path class="fumaca-cafe" d="M44 116 Q42 110 45 105 M50 116 Q48 110 51 105" stroke="#1B5E20" stroke-width="1.4" stroke-linecap="round"/>
                        <rect x="39" y="121" width="17" height="23" rx="2.5" fill="#EAE7E0" stroke="#141A16" stroke-width="1.8"/>
                        <path d="M56 126 H60 C63.5 126 63.5 138 60 138 H56" stroke="#141A16" stroke-width="1.8"/>
                        <rect x="43" y="127.5" width="9" height="9" rx="1.5" fill="#1B5E20"/>
                    </g>

                    <!-- Brócolis Nerd Analista (Com volume 3D e textura detalhada) -->
                    <g>
                        <!-- Corpo / Caule com sombra lateral -->
                        <path d="M88 86 L92 144 H126 L122 86 Z" fill="#EAE7E0" stroke="#141A16" stroke-width="1.9" stroke-linejoin="round"/>
                        <path d="M88 86 L92 144 H101 L98 86 Z" fill="#D5D0C5"/>

                        <!-- Cabeça e Copa do Brócolis Detalhada -->
                        <g class="cabeca-nerd">
                            <!-- Camada traseira da copa (mais escura para profundidade) -->
                            <circle cx="78" cy="68" r="16" fill="#81C784" stroke="#1B5E20" stroke-width="1.8"/>
                            <circle cx="128" cy="66" r="15" fill="#81C784" stroke="#1B5E20" stroke-width="1.8"/>
                            <circle cx="104" cy="50" r="19" fill="#A5D6A7" stroke="#1B5E20" stroke-width="1.8"/>

                            <!-- Camada frontal da copa -->
                            <path d="M72 82 C62 76 66 57 79 57 C83 43 99 39 108 46 C118 39 132 45 132 59 C142 63 141 79 130 83 Z" fill="#E8F5E9" stroke="#1B5E20" stroke-width="2" stroke-linejoin="round"/>

                            <!-- Cachos internos de textura de brócolis -->
                            <path d="M82 66 C86 61 93 61 96 66" stroke="#2E7D32" stroke-width="1.6" stroke-linecap="round"/>
                            <path d="M106 60 C110 55 117 55 120 60" stroke="#2E7D32" stroke-width="1.6" stroke-linecap="round"/>
                            <path d="M93 74 C97 70 103 70 106 74" stroke="#4CAF50" stroke-width="1.4" stroke-linecap="round"/>
                            <circle cx="86" cy="53" r="1.4" fill="#2E7D32"/>
                            <circle cx="115" cy="49" r="1.4" fill="#2E7D32"/>
                            <circle cx="123" cy="69" r="1.4" fill="#2E7D32"/>

                            <!-- Óculos de Nerd Quadrado com Aro Grosso + Reflexo -->
                            <rect x="99" y="86" width="12.5" height="10.5" rx="2.2" fill="#FFFFFF" stroke="#141A16" stroke-width="2.2"/>
                            <rect x="114.5" y="86" width="12.5" height="10.5" rx="2.2" fill="#FFFFFF" stroke="#141A16" stroke-width="2.2"/>
                            <line x1="111.5" y1="91" x2="114.5" y2="91" stroke="#141A16" stroke-width="2.2"/>
                            <line x1="91" y1="89" x2="99" y2="90" stroke="#141A16" stroke-width="2"/>
                            <!-- Pupilas olhando para a tela -->
                            <circle cx="107.5" cy="91.2" r="2.1" fill="#141A16"/>
                            <circle cx="123" cy="91.2" r="2.1" fill="#141A16"/>
                            <!-- Brilho nas lentes -->
                            <line x1="101.5" y1="88.5" x2="104.5" y2="94" stroke="#81C784" stroke-width="1.3" stroke-linecap="round"/>
                            <line x1="117" y1="88.5" x2="120" y2="94" stroke="#81C784" stroke-width="1.3" stroke-linecap="round"/>
                            <!-- Sorriso concentrado -->
                            <path d="M110 103 Q115 106 120 102" stroke="#141A16" stroke-width="1.6" stroke-linecap="round"/>
                        </g>

                        <!-- Bracinhos Digitando no Teclado -->
                        <path class="braco-esq" d="M118 114 L139 132 L154 135" stroke="#141A16" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle class="braco-esq" cx="155" cy="135" r="3.6" fill="#A5D6A7" stroke="#141A16" stroke-width="1.5"/>

                        <path class="braco-dir" d="M120 120 L141 137 L160 139" stroke="#141A16" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle class="braco-dir" cx="161" cy="139" r="3.6" fill="#A5D6A7" stroke="#141A16" stroke-width="1.5"/>
                    </g>

                    <!-- Notebook Aberto na Mesa -->
                    <g>
                        <polygon points="176,84 228,78 222,134 170,134" fill="#1F2922" stroke="#141A16" stroke-width="2" stroke-linejoin="round"/>
                        <polygon points="180,88 223,83 218,129 175,129" fill="#E8F5E9"/>
                        <!-- Gráficos Animados na Tela -->
                        <rect class="barra-g" x="182" y="111" width="6" height="14" rx="1" fill="#81C784"/>
                        <rect class="barra-g" x="191" y="102" width="6" height="23" rx="1" fill="#2E7D32"/>
                        <rect class="barra-g" x="200" y="94" width="6" height="31" rx="1" fill="#1B5E20"/>
                        <line x1="209" y1="96" x2="217" y2="95" stroke="#1B5E20" stroke-width="1.8" stroke-linecap="round"/>
                        <line x1="209" y1="103" x2="216" y2="102" stroke="#2E7D32" stroke-width="1.8" stroke-linecap="round"/>
                        <line x1="208" y1="110" x2="215" y2="109" stroke="#81C784" stroke-width="1.8" stroke-linecap="round"/>
                        <!-- Base / Teclado -->
                        <polygon points="142,134 222,134 230,144 136,144" fill="#D5D0C5" stroke="#141A16" stroke-width="1.9" stroke-linejoin="round"/>
                    </g>

                    <!-- Pilha de Relatórios / Prancheta à Direita -->
                    <g>
                        <rect x="242" y="139" width="28" height="5" rx="1" fill="#EAE7E0" stroke="#141A16" stroke-width="1.5"/>
                        <rect x="244" y="134" width="24" height="5" rx="1" fill="#C8E6C9" stroke="#141A16" stroke-width="1.5"/>
                    </g>

                    <!-- Tampo da Mesa -->
                    <line x1="22" y1="145" x2="288" y2="145" stroke="#141A16" stroke-width="2.4" stroke-linecap="round"/>
                </svg>
                <div style="font-size: 0.9rem; font-weight: 700; color: #141A16; margin-top: 4px;">Aguardando planilha para análise</div>
                <div style="font-size: 0.77rem; color: #5A635C; margin-top: 4px;">Abra um dos painéis acima para importar dados do <b>Portal Trizy</b> ou do <b>BI</b>.</div>
            </div>
            """,
            height=248
        )
     
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
    def _carga_bate_com_pedido(id_carga_limpo, campo_plan_limpo):
        if not id_carga_limpo or not campo_plan_limpo:
            return False
        if id_carga_limpo == campo_plan_limpo:
            return True
        return bool(re.search(r"(?<![A-Z0-9])" + re.escape(id_carga_limpo) + r"(?![A-Z0-9])", campo_plan_limpo))

    def sincronizar_status_planejamento_auto(df_p_in):
        if df_p_in.empty:
            return df_p_in
        df_c_sync = carregar_dados("cargas")
        status_cargas_map = {}
        if not df_c_sync.empty and "id_carga" in df_c_sync.columns:
            df_c_sync["pedido_real"] = pd.to_numeric(df_c_sync["pedido_real"], errors="coerce").fillna(0).astype(int)
            df_c_sync["bipado"] = pd.to_numeric(df_c_sync["bipado"], errors="coerce").fillna(0).astype(int)
            for cid_s, grp_s in df_c_sync.groupby("id_carga", sort=False):
                cid_k = limpar_texto(cid_s)
                if cid_k:
                    status_cargas_map[cid_k] = {
                        "bipado": int(grp_s["bipado"].sum()),
                        "concluida": verificar_carga_100_concluida(grp_s)
                    }

        agora_sp = datetime.now(FUSO_BR)
        alterou_algo = False
        df_p_out = df_p_in.copy()
        df_p_out["Status"] = df_p_out["Status"].astype(object)

        for idx_s, row_s in df_p_out.iterrows():
            ped_s = limpar_texto(row_s.get("Nº Pedido", ""))
            idc_s = limpar_texto(row_s.get("id_carga", ""))
            st_atual = str(row_s.get("Status", "")).strip()
            val_s = str(row_s.get("validado", "")).strip()
            esta_auditada = bool(val_s and val_s.lower() not in ("nan", "none", "null", "nao", "não"))

            info_c = status_cargas_map.get(idc_s) or status_cargas_map.get(ped_s)
            if info_c is None and ped_s:
                for k_cid, v_inf in status_cargas_map.items():
                    if _carga_bate_com_pedido(k_cid, ped_s):
                        info_c = v_inf
                        break

            novo_st = st_atual

            if esta_auditada and (info_c is None or info_c["concluida"]):
                novo_st = "✅ Carregado / Liberado"
            elif info_c is not None and info_c["bipado"] > 0 and st_atual != "✅ Carregado / Liberado":
                novo_st = "📦 Em Conferência"
            elif limpar_texto(st_atual) == limpar_texto("⏳ Aguardando Veículo"):
                dt_ag = interpretar_data_br(row_s.get("Data", ""))
                hr_ag = formatar_hora_br_str(row_s.get("Hora", ""))
                if dt_ag is not None and (agora_sp.date() - dt_ag).days <= 7:
                    if hr_ag and ":" in hr_ag:
                        hh, mm = [int(x) for x in hr_ag.split(":")[:2]]
                        dt_hr_ag = datetime(dt_ag.year, dt_ag.month, dt_ag.day, hh, mm, tzinfo=FUSO_BR)
                        if agora_sp > dt_hr_ag:
                            novo_st = "⚠️ Atrasado / Ocorrência"
                    elif agora_sp.date() > dt_ag:
                        novo_st = "⚠️ Atrasado / Ocorrência"

            if novo_st != st_atual:
                df_p_out.at[idx_s, "Status"] = novo_st
                alterou_algo = True

        if alterou_algo:
            salvar_dados(df_p_out[COLUNAS_PLANEJAMENTO], "planejamento")
        return df_p_out

    df_plan = sincronizar_status_planejamento_auto(df_plan)    
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

    k_top1, k_top2, k_top3 = st.columns(3, gap="medium")
    k_top1.markdown(
        f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.3); border-left:5px solid #1B5E20; border-radius:10px; padding:8px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.04);'>"
        f"<div style='font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em; color:#4A544D; font-weight:700;'>📋 Total Programado</div>"
        f"<div style='font-size:1.38rem; font-weight:800; color:#141A16; margin-top:1px;'>{total_prog_kpi} <span style='font-size:0.78rem; font-weight:600; color:#5A635C;'>pedidos</span></div>"
        f"</div>",
        unsafe_allow_html=True
    )
    k_top2.markdown(
        f"<div style='background:linear-gradient(135deg, #141A16 0%, #1E3323 100%); border:1px solid #2E7D32; border-left:5px solid #4CAF50; border-radius:10px; padding:8px 14px; box-shadow:0 4px 12px rgba(20,26,22,0.12);'>"
        f"<div style='font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em; color:#A5D6A7; font-weight:700;'>💰 Valor Total dos Pedidos</div>"
        f"<div style='font-size:1.38rem; font-weight:800; color:#FFFFFF; margin-top:1px;'>{fmt_pedidos_kpi}</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    perc_fr_str = f"{perc_frete_kpi:.1f}".replace(".", ",")
    k_top3.markdown(
        f"<div style='background:#FAF8F5; border:1px solid rgba(2,132,199,0.35); border-left:5px solid #0284C7; border-radius:10px; padding:8px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.04);'>"
        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"<span style='font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em; color:#0369A1; font-weight:700;'>🚛 Valor Total de Frete</span>"
        f"<span style='background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; font-size:0.68rem; font-weight:800; padding:1px 7px; border-radius:10px;'>{perc_fr_str}% s/ pedidos</span>"
        f"</div>"
        f"<div style='font-size:1.38rem; font-weight:800; color:#0C4A6E; margin-top:1px;'>{fmt_frete_kpi}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    c_locais, c_top_clientes = st.columns(2, gap="medium")
    with c_locais:
        df_loc_kpi = df_kpi_plan.copy()
        df_loc_kpi["_loc_limpo"] = df_loc_kpi["Local de Carregamento"].astype(str).str.strip()
        df_loc_validos = df_loc_kpi[df_loc_kpi["_loc_limpo"] != ""].copy()

        if not df_loc_validos.empty:
            df_loc_validos["_eh_transf"] = df_loc_validos["Nº Pedido"].apply(eh_pedido_transferencia)
            dados_loc_sort = list()
            for loc_nome, grupo_loc in df_loc_validos.groupby("_loc_limpo", sort=False):
                qtd_tot_loc = int(len(grupo_loc))
                qtd_tr_loc = int(grupo_loc["_eh_transf"].sum())
                dados_loc_sort.append((qtd_tot_loc, loc_nome, qtd_tr_loc))
            dados_loc_sort.sort(key=lambda x: x[0], reverse=True)

            badges_loc_html = ""
            for q_loc, nm_loc, q_tr in dados_loc_sort:
                tr_tag = f" <span style='color:#1B5E20; font-size:0.72rem;'>({q_tr} transf.)</span>" if q_tr > 0 else ""
                badges_loc_html += (
                    f"<span style='display:inline-flex; align-items:center; gap:5px; background:#FFFFFF; border:1px solid rgba(27,94,32,0.3); "
                    f"border-radius:8px; padding:4px 10px; font-size:0.78rem; color:#141A16;'>"
                    f"<b>{nm_loc}</b><span style='background:#E8F5E9; color:#1B5E20; font-weight:800; padding:1px 7px; border-radius:6px;'>{q_loc}</span>{tr_tag}</span>"
                )
            st.markdown(
                f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.28); border-radius:12px; padding:12px 16px; height:100%;'>"
                f"<div style='font-size:0.8rem; font-weight:800; color:#141A16; margin-bottom:8px;'>🏭 Quantidade por Local de Carregamento</div>"
                f"<div style='display:flex; flex-wrap:wrap; gap:6px;'>{badges_loc_html}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Nenhum local de carregamento informado neste período.")

    with c_top_clientes:
        mask_nao_transf = ~df_kpi_plan["Nº Pedido"].apply(eh_pedido_transferencia)
        clientes_series = df_kpi_plan.loc[mask_nao_transf, "Cliente"].astype(str).str.strip()
        clientes_validos = clientes_series[clientes_series != ""]

        if not clientes_validos.empty:
            top3_cli = clientes_validos.value_counts().head(3)
            medalhas = ["🥇", "🥈", "🥉"]
            cores_med = ["#FEF3C7", "#F1F5F9", "#FFEDD5"]
            bordas_med = ["#F59E0B", "#94A3B8", "#F97316"]
            badges_cli_html = ""
            for idx_c, (cli, qtd) in enumerate(top3_cli.items()):
                badges_cli_html += (
                    f"<span style='display:inline-flex; align-items:center; gap:6px; background:{cores_med[idx_c]}; border:1px solid {bordas_med[idx_c]}; "
                    f"border-radius:8px; padding:4px 10px; font-size:0.78rem; color:#141A16;'>"
                    f"<span>{medalhas[idx_c]}</span><b>{cli}</b>"
                    f"<span style='background:#FFFFFF; color:#141A16; font-weight:800; padding:1px 7px; border-radius:6px;'>{qtd}</span></span>"
                )
            st.markdown(
                f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.28); border-radius:12px; padding:12px 16px; height:100%;'>"
                f"<div style='font-size:0.8rem; font-weight:800; color:#141A16; margin-bottom:8px;'>🏆 Top 3 Clientes Mais Atendidos</div>"
                f"<div style='display:flex; flex-wrap:wrap; gap:6px;'>{badges_cli_html}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Nenhum cliente comercial registrado neste período.")

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
                    
    ferramenta_plan_sel = ""
    if not df_exibir_plan.empty:
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            datas_carreg = sorted([d for d in df_exibir_plan["Data"].dropna().unique().tolist() if str(d).strip() != ""])
            filtro_data_carreg = st.selectbox("Filtrar por Data de Carregamento:", ["Todas as datas"] + datas_carreg, key="filtro_fila_data_carreg")
        with f_col2:
            filtro_status_plan = st.selectbox("Filtrar por Status:", ["Todos os status"] + STATUS_PLANEJAMENTO, key="filtro_fila_status")

        if filtro_data_carreg != "Todas as datas":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Data"] == filtro_data_carreg]
        if filtro_status_plan != "Todos os status":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Status"].apply(limpar_texto) == limpar_texto(filtro_status_plan)]

        st_norm = df_exibir_plan["Status"].apply(limpar_texto)
        tr_norm = df_exibir_plan["Transportadora"].apply(limpar_texto)
        qtd_st1 = int((st_norm == limpar_texto("⏳ Aguardando Veículo")).sum())
        qtd_st2 = int((st_norm == limpar_texto("🚚 Veículo no Pátio")).sum())
        qtd_st3 = int((st_norm == limpar_texto("📦 Em Conferência")).sum())
        qtd_st4 = int((st_norm == limpar_texto("✅ Carregado / Liberado")).sum())
        qtd_st5 = int((st_norm == limpar_texto("⚠️ Atrasado / Ocorrência")).sum())
        qtd_contratar = int(tr_norm.str.contains("CONTRATAR", na=False).sum())

        def _card_status_exp(icone, titulo, valor, bg, borda, cor_tit, cor_val):
            return (
                f"<div style='background:{bg}; border:1px solid {borda}55; border-left:4px solid {borda}; "
                f"border-radius:10px; padding:8px 10px; margin-bottom:8px; box-shadow:0 2px 5px rgba(0,0,0,0.03);'>"
                f"<div style='font-size:0.68rem; font-weight:700; color:{cor_tit}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{icone} {titulo}</div>"
                f"<div style='font-size:1.35rem; font-weight:800; color:{cor_val}; margin-top:2px;'>{valor}</div>"
                f"</div>"
            )

        k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
        k1.markdown(_card_status_exp("⏳", "Aguardando Veículo", qtd_st1, "#FFFBEB", "#D97706", "#92400E", "#78350F"), unsafe_allow_html=True)
        k2.markdown(_card_status_exp("🚚", "Veículo no Pátio", qtd_st2, "#F0F9FF", "#0284C7", "#075985", "#0C4A6E"), unsafe_allow_html=True)
        k3.markdown(_card_status_exp("📦", "Em Conferência", qtd_st3, "#EEF2FF", "#4F46E5", "#3730A3", "#312E81"), unsafe_allow_html=True)
        k4.markdown(_card_status_exp("✅", "Carregado / Liberado", qtd_st4, "#ECFDF5", "#059669", "#065F46", "#064E3B"), unsafe_allow_html=True)
        k5.markdown(_card_status_exp("⚠️", "Atrasado / Ocorrência", qtd_st5, "#FEF2F2", "#DC2626", "#991B1B", "#7F1D1D"), unsafe_allow_html=True)
        k6.markdown(_card_status_exp("📝", "Contratar Transp.", qtd_contratar, "#FFF7ED", "#EA580C", "#9A3412", "#7C2D12"), unsafe_allow_html=True)
             
        feriados_plan = obter_feriados_sistema()
        mapa_lt_plan = obter_mapa_lead_time()

        def calc_lt_e_sugestao(row_p):
            u_p = limpar_texto(row_p.get("UF", ""))
            c_p = limpar_texto(row_p.get("Cidade", ""))
            lt_info_p = mapa_lt_plan.get((u_p, c_p))
            if lt_info_p is None:
                return "-", "-"
            lt_v, rota_v, km_v, _, _ = calcular_dias_rota_efetivos(lt_info_p)
            km_tag = f" • {int(round(km_v))}km" if km_v is not None else ""
            dt_ent_p = pd.to_datetime(str(row_p.get("Data da entrega", "")).strip(), dayfirst=True, errors="coerce")
            if pd.isna(dt_ent_p):
                return f"{lt_v}d ({rota_v}d rota{km_tag})", "-"
            dt_sug_p = subtrair_dias_uteis(dt_ent_p, rota_v, feriados_plan)
            return f"{lt_v}d ({rota_v}d rota{km_tag})", dt_sug_p.strftime("%d/%m/%Y")

        df_tab_plan = df_exibir_plan.drop(columns=["Notificação"], errors="ignore").copy()
        res_lt_plan = [list(t) for t in df_tab_plan.apply(calc_lt_e_sugestao, axis=1).tolist()]
        df_tab_plan["Lead Time"] = [t[0] for t in res_lt_plan]
        df_tab_plan["Sugestão Carreg."] = [t[1] for t in res_lt_plan]

        renderizar_tabela_wms(
            df_tab_plan,
            "planejamento_geral",

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
        st.markdown(
            """
            <style>
            div[data-testid="stElementContainer"]:has(.marc-azul) + div[data-testid="stExpander"] > details > summary {
                background: linear-gradient(90deg, #E0F2FE 0%, #F8FAFC 100%) !important;
                border-left: 6px solid #0284C7 !important;
            }
            div[data-testid="stElementContainer"]:has(.marc-verde) + div[data-testid="stExpander"] > details > summary {
                background: linear-gradient(90deg, #DCFCE7 0%, #F8FAF8 100%) !important;
                border-left: 6px solid #2E7D32 !important;
            }
            div[data-testid="stElementContainer"]:has(.marc-ambar) + div[data-testid="stExpander"] > details > summary {
                background: linear-gradient(90deg, #FEF3C7 0%, #FFFBEB 100%) !important;
                border-left: 6px solid #D97706 !important;
            }
            </style>
            <div style="display:flex; align-items:center; gap:8px; margin:14px 0 8px 0;">
                <span style="background:#141A16; color:#A5D6A7; font-size:0.7rem; font-weight:800; padding:3px 10px; border-radius:6px; letter-spacing:0.06em; text-transform:uppercase;">Operação Rápida</span>
                <span style="color:#5A635C; font-size:0.78rem; font-weight:600;">Atualize status e envie alertas em 1 clique</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_op_st, col_op_nt = st.columns(2, gap="medium")

        with col_op_st:
            with st.container(border=True):
                st.markdown(
                    "<div style='border-left:4px solid #2E7D32; padding-left:10px; margin-bottom:8px;'>"
                    "<div style='font-size:0.86rem; font-weight:800; color:#141A16;'>⚡ Atualização Rápida de Status</div>"
                    "<div style='font-size:0.74rem; color:#5A635C;'>Altere o andamento operacional em 1 clique</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
                opcoes_rapidas = {
                    f"Pedido {r['Nº Pedido']} — {r['Cliente']} ({r['Status']})": idx
                    for idx, r in df_exibir_plan.iterrows()
                }
                if opcoes_rapidas:
                    sel_rapida = st.selectbox("Selecione o Pedido:", list(opcoes_rapidas.keys()), key="sel_status_rapido")
                    idx_rapido = opcoes_rapidas[sel_rapida]
                    status_atual_item = df_plan.at[idx_rapido, "Status"]
                    idx_st_padrao = STATUS_PLANEJAMENTO.index(status_atual_item) if status_atual_item in STATUS_PLANEJAMENTO else 0
                    st_b1, st_b2 = st.columns((2, 1.1), vertical_alignment="bottom")
                    novo_status_rapido = st_b1.selectbox("Novo Status:", STATUS_PLANEJAMENTO, index=idx_st_padrao, key="novo_status_rapido")
                    if st_b2.button("💾 Atualizar", type="primary", use_container_width=True, key="btn_status_rapido"):
                        df_plan["Status"] = df_plan["Status"].astype(object)
                        df_plan.at[idx_rapido, "Status"] = novo_status_rapido
                        salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                        st.toast(f"✅ Status do pedido '{df_plan.at[idx_rapido, 'Nº Pedido']}' alterado para {novo_status_rapido}!", icon="✅")
                        st.rerun()

        with col_op_nt:
            if tem_permissao("🔔 Lançar Notificações"):
                with st.container(border=True):
                    st.markdown(
                        "<div style='border-left:4px solid #D97706; padding-left:10px; margin-bottom:8px;'>"
                        "<div style='font-size:0.86rem; font-weight:800; color:#141A16;'>🔔 Lançar Notificação no Pedido</div>"
                        "<div style='font-size:0.74rem; color:#5A635C;'>Envie alertas diretos para a equipe ou usuário</div>"
                        "</div>",
                        unsafe_allow_html=True
                    )
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
                            nt_c1, nt_c2 = st.columns(2)
                            sel_nt_ped = nt_c1.selectbox("Pedido:", list(opcoes_notif.keys()))
                            sel_nt_dest = nt_c2.selectbox("Para quem?", list(opcoes_destino_nt.keys()))
                            nt_m1, nt_m2 = st.columns((2.3, 1.0), vertical_alignment="bottom")
                            txt_nova_notif = nt_m1.text_input("Mensagem:", placeholder="Ex: PRIORIDADE DE CARREGAMENTO...")
                            btn_enviar_notif = nt_m2.form_submit_button("🔔 Notificar", type="primary", use_container_width=True)

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
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:8px; margin:18px 0 8px 0;">
                <span style="background:#1B5E20; color:#FFFFFF; font-size:0.7rem; font-weight:800; padding:3px 10px; border-radius:6px; letter-spacing:0.06em; text-transform:uppercase;">Cálculo & Cadastro</span>
                <span style="color:#5A635C; font-size:0.78rem; font-weight:600;">Selecione a aba da ferramenta desejada</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        tab_calc_fr, tab_inc_ped, tab_ed_ped = st.tabs([
            "🧮 Calculadora de Frete (Roteiros)",
            "➕ Incluir Pedido Manualmente",
            "✏️ Editar ou Excluir Pedido"
        ])
        with tab_calc_fr:

            st.markdown(
                """
                <style>
                div[data-testid="stExpander"]:has(div[data-testid="stElementContainer"] .calc-frete-banner) {
                    background: linear-gradient(180deg, #F4F7F4 0%, #EAECE7 100%) !important;
                    border: 1.5px solid #2E7D32 !important;
                    border-radius: 14px !important;
                    box-shadow: 0 4px 14px rgba(20, 26, 22, 0.06) !important;
                }
                div.stButton > button[key="btn_undo_parada_fr"],
                div[class*="st-key-btn_undo_parada_fr"] button {
                    background-color: #FEF3C7 !important;
                    border: 1px solid #D97706 !important;
                    color: #92400E !important;
                }
                div[class*="st-key-btn_undo_parada_fr"] button p { color: #92400E !important; font-weight: 700 !important; }
                div[class*="st-key-btn_limpar_parada_fr"] button {
                    background-color: #FEE2E2 !important;
                    border: 1px solid #DC2626 !important;
                    color: #991B1B !important;
                }
                div[class*="st-key-btn_limpar_parada_fr"] button p { color: #991B1B !important; font-weight: 700 !important; }
                </style>
                <div class="calc-frete-banner" style="background:linear-gradient(90deg, #141A16 0%, #1E3323 100%); border-left:5px solid #4CAF50; border-radius:10px; padding:10px 16px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between;">
                    <div>
                        <div style="color:#A5D6A7; font-size:0.72rem; font-weight:800; letter-spacing:0.06em; text-transform:uppercase;">Simulador Logístico de Roteiros</div>
                        <div style="color:#FFFFFF; font-size:0.88rem; font-weight:600; margin-top:2px;">Monte coletas e entregas em sequência (ex: Friozem ➔ Fábrica ➔ São Paulo/SP) com cálculo automático por trecho.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            @st.cache_data(ttl=43200, show_spinner=False)
            def carregar_tabela_frete_oficial():
                df_tf = conn.read(worksheet="tabela frete", ttl=0).dropna(how="all").fillna("")
                if df_tf is None or df_tf.empty:
                    return {},
                c_fil, c_uf, c_cid, c_km, c_fc, c_ft = None, None, None, None, None, None
                for col_t in df_tf.columns:
                    cl = limpar_texto(col_t)
                    if not c_fil and "FILIAL" in cl:
                        c_fil = col_t
                    elif not c_uf and cl in ("ESTADO", "UF"):
                        c_uf = col_t
                    elif not c_cid and ("CIDADE" in cl or "MUNICIPIO" in cl):
                        c_cid = col_t
                    elif not c_km and "DISTANCIA" in cl:
                        c_km = col_t
                    elif not c_fc and "CARRETA" in cl:
                        c_fc = col_t
                    elif not c_ft and "TRUCK" in cl:
                        c_ft = col_t

                mapa_tf = {}
                filiais_set = set()
                if c_fil and c_cid and (c_fc or c_ft):
                    for _, rt in df_tf.iterrows():
                        fil_n = str(rt[c_fil]).strip()
                        fil_k = limpar_texto(fil_n)
                        cid_k = limpar_texto(rt[c_cid])
                        uf_k = limpar_texto(rt[c_uf]) if c_uf else ""
                        if not fil_k or not cid_k:
                            continue
                        filiais_set.add(fil_n)
                        dest_lbl = f"{cid_k}/{uf_k}" if uf_k else cid_k
                        km_v = converter_moeda_para_float(rt[c_km]) if c_km else 0.0
                        fc_v = converter_moeda_para_float(rt[c_fc]) if c_fc else 0.0
                        ft_v = converter_moeda_para_float(rt[c_ft]) if c_ft else 0.0
                        mapa_tf[(fil_k, dest_lbl)] = {
                            "km": km_v,
                            "frete_carreta": fc_v,
                            "frete_truck": ft_v
                        }
                return mapa_tf, sorted(list(filiais_set))

            try:
                mapa_frete_of, lista_filiais_of = carregar_tabela_frete_oficial()
            except Exception as e_tf:
                mapa_frete_of, lista_filiais_of = {},
                st.error(f"Erro ao ler aba 'tabela frete': {e_tf}")

            if not mapa_frete_of:
                st.warning("⚠️ Nenhuma rota encontrada na aba `'tabela frete'`.")
            else:
                if "roteiro_frete_paradas" not in st.session_state:
                    st.session_state.roteiro_frete_paradas = list()

                filiais_tags = [f"🏭 {f}" for f in lista_filiais_of]
                todas_cidades_fr = sorted(list({dest for (_, dest) in mapa_frete_of.keys()}))
                opcoes_pontos_fr = filiais_tags + todas_cidades_fr

                sede_para_filial = {
                    "ESTEIO/RS": "FRIOZEM",
                    "SAPUCAIA DO SUL/RS": "FRIOZEM",
                    "SERAFINA CORREA/RS": "FABRICA",
                    "COLOMBO/PR": "COLOMBO",
                    "ITUPEVA/SP": "BRASFRIGO",
                }
                filial_para_sede = {
                    "FRIOZEM": "ESTEIO/RS",
                    "FABRICA": "SERAFINA CORREA/RS",
                    "COLOMBO": "COLOMBO/PR",
                    "BRASFRIGO": "ITUPEVA/SP",
                }

                def _resolver_filial_e_cidade(ponto_str):
                    if ponto_str.startswith("🏭 "):
                        fn = limpar_texto(ponto_str[2:])
                        return fn, filial_para_sede.get(fn, "")
                    cid_l = limpar_texto(ponto_str)
                    return sede_para_filial.get(cid_l, ""), cid_l

                with st.container(border=True):
                    cf1, cf2, cf3, cf4, cf5 = st.columns((1.5, 1.2, 1.8, 0.95, 0.95), vertical_alignment="bottom")
                    ponto_saida_fr = cf1.selectbox("🚩 Ponto de Saída (1ª Origem):", options=opcoes_pontos_fr, index=0, key="calc_fr_saida")
                    veic_calc_fr = cf2.selectbox("🚛 Tipo de Veículo:", options=["CARRETA", "TRUCK / BI-TRUCK"], key="calc_fr_veic")
                    prox_parada_fr = cf3.selectbox("📍 Próxima Parada (Coleta / Entrega):", options=opcoes_pontos_fr, key="calc_fr_prox")
                    if cf4.button("➕ Adicionar", type="primary", use_container_width=True, key="btn_add_parada_fr"):
                        st.session_state.roteiro_frete_paradas.append(prox_parada_fr)
                        st.rerun()
                    if cf5.button("🔄 Tabela", use_container_width=True, key="btn_reload_tab_frete", help="Recarregar valores da aba tabela frete"):
                        carregar_tabela_frete_oficial.clear()
                        st.rerun()

                if st.session_state.roteiro_frete_paradas:
                    paradas_atuais = st.session_state.roteiro_frete_paradas
                    eh_carreta = (veic_calc_fr == "CARRETA")
                    linhas_trechos = list()

                    ponto_ant = ponto_saida_fr
                    filial_ativa, _ = _resolver_filial_e_cidade(ponto_saida_fr)
                    if not filial_ativa and lista_filiais_of:
                        filial_ativa = limpar_texto(lista_filiais_of)

                    for seq_p, parada_dest in enumerate(paradas_atuais, start=1):
                        fil_orig_tr, cid_orig_tr = _resolver_filial_e_cidade(ponto_ant)
                        fil_dest_tr, cid_dest_tr = _resolver_filial_e_cidade(parada_dest)

                        km_tr, val_tr = 0.0, 0.0
                        if fil_orig_tr and cid_dest_tr and (fil_orig_tr, cid_dest_tr) in mapa_frete_of:
                            d = mapa_frete_of[(fil_orig_tr, cid_dest_tr)]
                            km_tr = d["km"]
                            val_tr = d["frete_carreta"] if eh_carreta else d["frete_truck"]
                        elif fil_dest_tr and cid_orig_tr and (fil_dest_tr, cid_orig_tr) in mapa_frete_of:
                            d = mapa_frete_of[(fil_dest_tr, cid_orig_tr)]
                            km_tr = d["km"]
                            val_tr = d["frete_carreta"] if eh_carreta else d["frete_truck"]
                        elif filial_ativa and cid_orig_tr in [c for (f, c) in mapa_frete_of if f == filial_ativa] and cid_dest_tr in [c for (f, c) in mapa_frete_of if f == filial_ativa]:
                            d1 = mapa_frete_of[(filial_ativa, cid_orig_tr)]
                            d2 = mapa_frete_of[(filial_ativa, cid_dest_tr)]
                            km_tr = abs(d2["km"] - d1["km"])
                            t1 = d1["frete_carreta"] if eh_carreta else d1["frete_truck"]
                            t2 = d2["frete_carreta"] if eh_carreta else d2["frete_truck"]
                            val_tr = abs(t2 - t1)

                        linhas_trechos.append({
                            "Etapa": f"Trecho {seq_p}",
                            "De (Saída/Parada)": ponto_ant,
                            "Para (Parada/Destino)": parada_dest,
                            "KM Trecho": round(km_tr, 1),
                            "Valor Trecho (R$)": round(val_tr, 2)
                        })
                        ponto_ant = parada_dest
                        if fil_dest_tr:
                            filial_ativa = fil_dest_tr

                    # Linha do Tempo Colorida por Tipo de Etapa
                    nos_rota_html = (
                        f"<div style='display:inline-flex; align-items:center; gap:6px; background:#141A16; color:#FFFFFF; "
                        f"padding:6px 13px; border-radius:20px; font-size:0.78rem; font-weight:700; border:1.5px solid #4CAF50;'>"
                        f"<span style='color:#81C784;'>🚩 SAÍDA</span><span>{ponto_saida_fr.replace('🏭 ', '')}</span></div>"
                    )
                    for idx_no, p_no in enumerate(paradas_atuais, start=1):
                        eh_ultimo_no = (idx_no == len(paradas_atuais))
                        if eh_ultimo_no:
                            bg_no, bd_no, cor_tag, cor_txt, tag_no = "#E0F2FE", "#0284C7", "#0369A1", "#0C4A6E", "🏁 DESTINO FINAL"
                        else:
                            bg_no, bd_no, cor_tag, cor_txt, tag_no = "#FEF3C7", "#D97706", "#B45309", "#78350F", f"📍 PARADA {idx_no}"
                        nos_rota_html += (
                            f"<span style='color:#2E7D32; font-weight:900; font-size:0.95rem;'>➔</span>"
                            f"<div style='display:inline-flex; align-items:center; gap:6px; background:{bg_no}; color:{cor_txt}; "
                            f"padding:6px 13px; border-radius:20px; font-size:0.78rem; font-weight:700; border:1.5px solid {bd_no};'>"
                            f"<span style='color:{cor_tag};'>{tag_no}</span><span>{p_no.replace('🏭 ', '')}</span></div>"
                        )

                    st.markdown(
                        f"<div style='background:#FFFFFF; border:1px solid #C8D6C9; border-radius:12px; "
                        f"padding:10px 14px; margin:8px 0 10px 0; display:flex; flex-wrap:wrap; align-items:center; gap:8px;'>"
                        f"{nos_rota_html}</div>",
                        unsafe_allow_html=True
                    )

                    st.caption("✏️ **Tabela Editável:** Clique sobre `KM Trecho` ou `Valor Trecho (R$)` se precisar ajustar algum desvio:")
                    df_trechos_edit = st.data_editor(
                        pd.DataFrame(linhas_trechos),
                        key="editor_trechos_frete",
                        use_container_width=True,
                        hide_index=True,
                        disabled=["Etapa", "De (Saída/Parada)", "Para (Parada/Destino)"],
                        column_config={
                            "Etapa": st.column_config.TextColumn("Etapa", width="small"),
                            "De (Saída/Parada)": st.column_config.TextColumn("🚩 Origem do Trecho", width="medium"),
                            "Para (Parada/Destino)": st.column_config.TextColumn("📍 Destino do Trecho", width="medium"),
                            "KM Trecho": st.column_config.NumberColumn("🛣️ KM Trecho", min_value=0.0, step=1.0, format="%.1f km"),
                            "Valor Trecho (R$)": st.column_config.NumberColumn("💰 Valor Trecho (R$)", min_value=0.0, step=10.0, format="R$ %.2f"),
                        }
                    )

                    total_frete_rota = float(pd.to_numeric(df_trechos_edit["Valor Trecho (R$)"], errors="coerce").fillna(0.0).sum())
                    total_km_rota = float(pd.to_numeric(df_trechos_edit["KM Trecho"], errors="coerce").fillna(0.0).sum())
                    tot_fr_fmt = f"R$ {total_frete_rota:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                    c_kpi_f1, c_kpi_f2, c_kpi_f3, c_btns_fr = st.columns((1.6, 1.2, 1.0, 1.5), vertical_alignment="center")
                    with c_kpi_f1:
                        st.markdown(
                            f"<div style='background:linear-gradient(135deg, #1B4332 0%, #081C15 100%); border:1.5px solid #40916C; "
                            f"border-left:6px solid #74C69D; border-radius:12px; padding:10px 16px; box-shadow:0 3px 10px rgba(0,0,0,0.1);'>"
                            f"<div style='font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; color:#B7E4C7; font-weight:800;'>💰 Frete Total Estimado</div>"
                            f"<div style='font-size:1.45rem; font-weight:800; color:#FFFFFF; margin-top:2px;'>{tot_fr_fmt}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with c_kpi_f2:
                        st.markdown(
                            f"<div style='background:#E0F2FE; border:1.5px solid #38BDF8; border-left:5px solid #0284C7; "
                            f"border-radius:12px; padding:10px 14px;'>"
                            f"<div style='font-size:0.72rem; text-transform:uppercase; color:#0369A1; font-weight:800;'>🛣️ Distância Total</div>"
                            f"<div style='font-size:1.35rem; font-weight:800; color:#0C4A6E; margin-top:2px;'>{int(round(total_km_rota))} km</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with c_kpi_f3:
                        st.markdown(
                            f"<div style='background:#FEF3C7; border:1.5px solid #FBBF24; border-left:5px solid #D97706; "
                            f"border-radius:12px; padding:10px 14px;'>"
                            f"<div style='font-size:0.72rem; text-transform:uppercase; color:#B45309; font-weight:800;'>📍 Paradas</div>"
                            f"<div style='font-size:1.35rem; font-weight:800; color:#78350F; margin-top:2px;'>{len(paradas_atuais)}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with c_btns_fr:
                        cb_u1, cb_u2 = st.columns(2)
                        if cb_u1.button("↩️ Desfazer", use_container_width=True, key="btn_undo_parada_fr"):
                            st.session_state.roteiro_frete_paradas.pop()
                            st.rerun()
                        if cb_u2.button("🗑️ Limpar", use_container_width=True, key="btn_limpar_parada_fr"):
                            st.session_state.roteiro_frete_paradas = list()
                            st.rerun()

                    if opcoes_rapidas and total_frete_rota > 0:
                        with st.container(border=True):
                            ca_p1, ca_p2, _ = st.columns((2.2, 1.0, 2.2), vertical_alignment="bottom")
                            ped_aplicar_fr = ca_p1.selectbox("📌 Vincular e gravar este frete no pedido:", list(opcoes_rapidas.keys()), key="sel_aplicar_frete_ped")
                            if ca_p2.button("💾 Gravar no Pedido", type="primary", use_container_width=True, key="btn_gravar_frete_ped"):
                                idx_fr_alvo = opcoes_rapidas[ped_aplicar_fr]
                                df_plan["Valor de Frete"] = df_plan["Valor de Frete"].astype(object)
                                df_plan["Veículo compartilhado"] = df_plan["Veículo compartilhado"].astype(object)
                                df_plan.at[idx_fr_alvo, "Valor de Frete"] = formatar_moeda_br_str(f"{total_frete_rota:.2f}")
                                if len(paradas_atuais) > 1:
                                    df_plan.at[idx_fr_alvo, "Veículo compartilhado"] = "SIM"
                                salvar_dados(df_plan[COLUNAS_PLANEJAMENTO], "planejamento")
                                st.toast(f"💰 Frete {tot_fr_fmt} gravado no pedido {df_plan.at[idx_fr_alvo, 'Nº Pedido']}!", icon="💰")
                                st.rerun()
                else:
                    st.info("Selecione o **Ponto de Saída**, o **Tipo de Veículo** e clique em **➕ Adicionar** para montar as paradas do roteiro.")
                    
    else:
        st.info("Nenhum pedido cadastrado no planejamento ainda.")    

    with tab_inc_ped:
        st.markdown(
            """
            <div style="background:linear-gradient(90deg, #141A16 0%, #1E3323 100%); border-left:5px solid #4CAF50; border-radius:10px; padding:10px 16px; margin-bottom:12px;">
                <div style="color:#A5D6A7; font-size:0.72rem; font-weight:800; letter-spacing:0.06em; text-transform:uppercase;">Cadastro Manual de Programação</div>
                <div style="color:#FFFFFF; font-size:0.86rem; font-weight:600; margin-top:2px;">Consulte o Lead Time e o frete de referência antes de preencher os dados da programação.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#1B5E20; margin-bottom:6px;'>🔍 Consulta Rápida de Lead Time e Frete Tabela</div>", unsafe_allow_html=True)
            q_c1, q_c2, q_c3 = st.columns((0.8, 1.8, 1.4))
            q_uf = q_c1.text_input("UF p/ Consulta:", placeholder="Ex: RS", key="q_lt_uf")
            q_cid = q_c2.text_input("Cidade p/ Consulta:", placeholder="Ex: PORTO ALEGRE", key="q_lt_cid")
            q_ent = q_c3.text_input("Data Entrega Prevista:", placeholder="DD/MM/AAAA", key="q_lt_ent")

            if q_uf.strip() and q_cid.strip():
                mapa_lt_q = obter_mapa_lead_time()
                feriados_q = obter_feriados_sistema()
                lt_q = mapa_lt_q.get((limpar_texto(q_uf), limpar_texto(q_cid)))
                if lt_q is not None:
                    lt_tot_q, dias_rota_q, km_q, fc_q, ft_q = calcular_dias_rota_efetivos(lt_q)
                    km_txt_q = f"{int(round(km_q))} km" if km_q is not None else "—"
                    ft_str_q = f"R$ {ft_q:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if ft_q else "—"
                    fc_str_q = f"R$ {fc_q:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if fc_q else "—"

                    dt_q_parsed = pd.to_datetime(q_ent.strip(), dayfirst=True, errors="coerce") if q_ent.strip() else pd.NaT
                    dt_sug_q_str = subtrair_dias_uteis(dt_q_parsed, dias_rota_q, feriados_q).strftime("%d/%m/%Y") if pd.notna(dt_q_parsed) else "Informe a entrega"

                    kq1, kq2, kq3, kq4 = st.columns(4)
                    kq1.markdown(
                        f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.3); border-left:4px solid #1B5E20; border-radius:10px; padding:8px 12px;'>"
                        f"<div style='font-size:0.68rem; text-transform:uppercase; color:#5A635C; font-weight:700;'>⏱️ Lead Time / Rota</div>"
                        f"<div style='font-size:1.05rem; font-weight:800; color:#141A16; margin-top:2px;'>{lt_tot_q}d ({dias_rota_q}d • {km_txt_q})</div></div>",
                        unsafe_allow_html=True
                    )
                    kq2.markdown(
                        f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.3); border-left:4px solid #2E7D32; border-radius:10px; padding:8px 12px;'>"
                        f"<div style='font-size:0.68rem; text-transform:uppercase; color:#5A635C; font-weight:700;'>🚚 Frete Truck</div>"
                        f"<div style='font-size:1.05rem; font-weight:800; color:#141A16; margin-top:2px;'>{ft_str_q}</div></div>",
                        unsafe_allow_html=True
                    )
                    kq3.markdown(
                        f"<div style='background:#FAF8F5; border:1px solid rgba(27,94,32,0.3); border-left:4px solid #2E7D32; border-radius:10px; padding:8px 12px;'>"
                        f"<div style='font-size:0.68rem; text-transform:uppercase; color:#5A635C; font-weight:700;'>🚛 Frete Carreta</div>"
                        f"<div style='font-size:1.05rem; font-weight:800; color:#141A16; margin-top:2px;'>{fc_str_q}</div></div>",
                        unsafe_allow_html=True
                    )
                    kq4.markdown(
                        f"<div style='background:linear-gradient(135deg, #1B4332 0%, #081C15 100%); border:1px solid #40916C; border-left:5px solid #74C69D; border-radius:10px; padding:8px 12px;'>"
                        f"<div style='font-size:0.68rem; text-transform:uppercase; color:#B7E4C7; font-weight:800;'>🎯 Sugestão Carreg.</div>"
                        f"<div style='font-size:1.05rem; font-weight:800; color:#FFFFFF; margin-top:2px;'>{dt_sug_q_str}</div></div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.warning(f"⚠️ Cidade **{limpar_texto(q_cid)}/{limpar_texto(q_uf)}** não encontrada na aba `lead time`.")

        with st.form("form_novo_planejamento", clear_on_submit=True):
            st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin-bottom:8px;'>📦 1. Dados da Programação e Datas</div>", unsafe_allow_html=True)
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            in_data = r1c1.text_input("Data Carregamento (DD/MM/AAAA):", placeholder="Ex: 18/11/2026")
            in_hora = r1c2.text_input("Hora:", placeholder="Ex: 08:30")
            in_pedido = r1c3.text_input("Nº Pedido (ID da Carga)*:", placeholder="Ex: 106915")
            in_ordem = r1c4.text_input("Ordem de Carregamento:", placeholder="Ex: OC-450")

            r2c1, r2c2, r2c3 = st.columns((1.5, 1.2, 1.3))
            in_local = r2c1.text_input("Local de Carregamento:", placeholder="Ex: CD Canoas / Friozem")
            in_data_ent = r2c2.text_input("Data da entrega (DD/MM/AAAA):", placeholder="Ex: 20/11/2026")
            in_status = r2c3.selectbox("Status Inicial:", STATUS_PLANEJAMENTO)

            st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin:12px 0 8px 0;'>🏢 2. Cliente, Destino e Modalidade</div>", unsafe_allow_html=True)
            r3c1, r3c2, r3c3, r3c4 = st.columns((2.0, 1.2, 0.7, 1.5))
            in_cliente = r3c1.text_input("Cliente:", placeholder="Nome do cliente")
            in_val_ped = r3c2.text_input("Valor Pedido (R$):", placeholder="Ex: 15.800,00")
            in_uf = r3c3.text_input("UF:", placeholder="Ex: RS")
            in_cidade = r3c4.text_input("Cidade:", placeholder="Ex: Porto Alegre")

            st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin:12px 0 8px 0;'>🚛 3. Transporte, Frete e Observações</div>", unsafe_allow_html=True)
            r4c1, r4c2, r4c3, r4c4 = st.columns(4)
            in_transp = r4c1.text_input("Transportadora:", placeholder="Nome da transportadora")
            in_placa = r4c2.text_input("Placa do veículo:", placeholder="Ex: ABC1D23")
            in_tipo_veic = r4c3.text_input("Tipo de Veículo:", placeholder="Ex: Carreta / Truck")
            in_val_frete = r4c4.text_input("Valor de Frete (R$):", placeholder="Ex: 3.200,00")

            r5c1, r5c2, r5c3 = st.columns((1.0, 1.0, 2.5))
            in_cif_fob = r5c1.selectbox("CIF/FOB:", ["CIF", "FOB", "OUTRO"])
            in_compart = r5c2.selectbox("Veículo compartilhado:", ["NÃO", "SIM"])
            in_obs = r5c3.text_input("Observação:", placeholder="Observações gerais do agendamento...")

            salvar_novo_plan = st.form_submit_button("➕ Incluir Pedido na Programação", type="primary", use_container_width=True)

            if salvar_novo_plan:
                ped_limpo = limpar_texto(in_pedido)
                if not ped_limpo:
                    st.error("⚠️ O campo **Nº Pedido** é obrigatório!")
                elif ped_limpo in df_plan["Nº Pedido"].values:
                    st.error(f"🚫 O pedido **'{ped_limpo}'** já está cadastrado na agenda! Use a opção de editar abaixo.")
                else:
                    frete_final_manual = formatar_moeda_br_str(in_val_frete)
                    if not frete_final_manual and in_uf.strip() and in_cidade.strip() and in_tipo_veic.strip():
                        lt_m = obter_mapa_lead_time().get((limpar_texto(in_uf), limpar_texto(in_cidade)))
                        if lt_m is not None:
                            _, _, _, fc_m, ft_m = calcular_dias_rota_efetivos(lt_m)
                            v_norm = limpar_texto(in_tipo_veic)
                            val_m = fc_m if "CARRETA" in v_norm else (ft_m if ("TRUCK" in v_norm or "BITRUCK" in v_norm or "BI-TRUCK" in v_norm) else None)
                            if val_m and val_m > 0:
                                frete_final_manual = f"R$ {val_m:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                            
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
                        "Valor de Frete": frete_final_manual,
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
                    
    with tab_ed_ped:
        st.markdown(
            """
            <div style="background:linear-gradient(90deg, #141A16 0%, #1E3323 100%); border-left:5px solid #4CAF50; border-radius:10px; padding:10px 16px; margin-bottom:12px;">
                <div style="color:#A5D6A7; font-size:0.72rem; font-weight:800; letter-spacing:0.06em; text-transform:uppercase;">Manutenção de Programação</div>
                <div style="color:#FFFFFF; font-size:0.86rem; font-weight:600; margin-top:2px;">Selecione o pedido na lista abaixo para alterar horários, transportadora, frete, status ou excluir o registro.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not df_plan.empty:
            opcoes_plan = {
                f"Pedido: {r['Nº Pedido']} | Cliente: {r['Cliente']} | Data: {r['Data']} {r['Hora']} | Status: {r['Status']}": idx
                for idx, r in df_plan.iterrows()
            }
            sel_label = st.selectbox("📌 Selecione o agendamento para editar:", list(opcoes_plan.keys()), key="sel_edit_plan")
            idx_plan = opcoes_plan[sel_label]
            row_ed = df_plan.loc[idx_plan]

            with st.form("form_editar_planejamento"):
                st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin-bottom:8px;'>📦 1. Dados da Programação e Datas</div>", unsafe_allow_html=True)
                e1c1, e1c2, e1c3, e1c4 = st.columns(4)
                ed_data = e1c1.text_input("Data:", value=str(row_ed["Data"]))
                ed_hora = e1c2.text_input("Hora:", value=str(row_ed["Hora"]))
                ed_pedido = e1c3.text_input("Nº Pedido:", value=str(row_ed["Nº Pedido"]))
                ed_ordem = e1c4.text_input("Ordem de Carregamento:", value=str(row_ed["Ordem de Carregamento"]))

                e2c1, e2c2, e2c3 = st.columns((1.5, 1.2, 1.3))
                ed_local = e2c1.text_input("Local de Carregamento:", value=str(row_ed["Local de Carregamento"]))
                ed_data_ent = e2c2.text_input("Data da entrega:", value=str(row_ed["Data da entrega"]))
                idx_st = STATUS_PLANEJAMENTO.index(row_ed["Status"]) if row_ed["Status"] in STATUS_PLANEJAMENTO else 0
                ed_status = e2c3.selectbox("Status:", STATUS_PLANEJAMENTO, index=idx_st)

                st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin:12px 0 8px 0;'>🏢 2. Cliente, Destino e Modalidade</div>", unsafe_allow_html=True)
                e3c1, e3c2, e3c3, e3c4 = st.columns((2.0, 1.2, 0.7, 1.5))
                ed_cliente = e3c1.text_input("Cliente:", value=str(row_ed["Cliente"]))
                ed_val_ped = e3c2.text_input("Valor Pedido:", value=str(row_ed["Valor Pedido"]))
                ed_uf = e3c3.text_input("UF:", value=str(row_ed["UF"]))
                ed_cidade = e3c4.text_input("Cidade:", value=str(row_ed["Cidade"]))

                st.markdown("<div style='font-size:0.82rem; font-weight:800; color:#141A16; border-bottom:1px solid rgba(27,94,32,0.2); padding-bottom:4px; margin:12px 0 8px 0;'>🚛 3. Transporte, Frete e Observações</div>", unsafe_allow_html=True)
                e4c1, e4c2, e4c3, e4c4 = st.columns(4)
                ed_transp = e4c1.text_input("Transportadora:", value=str(row_ed["Transportadora"]))
                ed_placa = e4c2.text_input("Placa do veículo:", value=str(row_ed["Placa do veículo"]))
                ed_tipo_veic = e4c3.text_input("Tipo de Veículo:", value=str(row_ed["Tipo de Veículo"]))
                ed_val_frete = e4c4.text_input("Valor de Frete:", value=str(row_ed["Valor de Frete"]))

                e5c1, e5c2, e5c3 = st.columns((1.0, 1.0, 2.5))
                idx_cf = ["CIF", "FOB"].index(row_ed["CIF/FOB"]) if row_ed["CIF/FOB"] in ["CIF", "FOB"] else 0
                ed_cif_fob = e5c1.selectbox("CIF/FOB:", ["CIF", "FOB"], index=idx_cf)
                idx_cp = ["NÃO", "SIM"].index(row_ed["Veículo compartilhado"]) if row_ed["Veículo compartilhado"] in ["NÃO", "SIM"] else 0
                ed_compart = e5c2.selectbox("Veículo compartilhado:", ["NÃO", "SIM"], index=idx_cp)
                ed_obs = e5c3.text_input("Observação:", value=str(row_ed["Observação"]))

                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if tem_permissao("🗑️ Excluir Pedidos"):
                    col_b1, col_b2 = st.columns((3, 1.2))
                    btn_atualizar_plan = col_b1.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                    btn_excluir_plan = col_b2.form_submit_button("🗑️ Excluir este Pedido", use_container_width=True)
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
                    st.session_state.toast_global = f"Agendamento do pedido '{limpar_texto(ed_pedido)}' atualizado com sucesso!"
                    st.session_state.pop("sel_edit_plan", None)
                    st.rerun()

                if btn_excluir_plan:
                    df_plan_rest = df_plan.drop(idx_plan)
                    if df_plan_rest.empty:
                        df_plan_rest = pd.DataFrame(columns=COLUNAS_PLANEJAMENTO)
                    salvar_dados(df_plan_rest[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.session_state.toast_global = "Agendamento removido da agenda com sucesso!"
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

                        st.session_state.toast_global = f"Carga '{carga_antiga}' renomeada para '{novo_nome_limpo}' com sucesso!"
                        st.session_state.pop("sel_renomear_carga", None)
                        st.session_state.pop("input_novo_nome_carga", None)
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

                    st.session_state.toast_global = f"Carga '{carga_para_excluir}' excluída com sucesso!"
                    st.session_state.pop("sel_excluir_carga", None)
                    st.rerun()
                    
            else:
                st.info("Nenhuma carga cadastrada no momento.")
        else:
            st.info("Nenhuma carga cadastrada no momento.")

elif aba == "📋 Gestão de Pedidos":
    st.title("📋 Gestão de Pedidos: Conferidos x Pendentes")

    if st.button("🔄 Atualizar Status"):
        limpar_cache_operacional()
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
                "Validação Final": next((f"✅ {val_v}" for ped_k, val_v in mapa_validados_gp.items() if limpar_texto(cid) == ped_k or bool(re.search(r"(?<![A-Z0-9])" + re.escape(limpar_texto(cid)) + r"(?![A-Z0-9])", ped_k))), "⏳ Aguardando Auditoria")
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
        renderizar_tabela_wms(
            pd.DataFrame(lista_pendentes),
            "gestao_pendentes",
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
        renderizar_tabela_wms(
                pd.DataFrame(lista_concluidas),
                "gestao_concluidas",
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
                        st.session_state.toast_global = "Motivo do corte atualizado com sucesso!"
                        st.rerun()
        else:
            st.info("Nenhum item encontrado neste pedido.")
    if st.session_state.perfil_usuario in ("ADMIN", "GERENTE", "SUPERVISOR", "ANALISTA") and lista_pendentes:
        with st.expander("✅ Administrativo: Concluir Carga 100% Automaticamente"):
            st.caption("Use esta opção quando uma carga já foi expedida ou conferida fisicamente e precisa sair da fila de pendentes.")
            opcoes_baixa = [item["Carga / Pedido"] for item in lista_pendentes]
            c_bx1, c_bx2 = st.columns((2, 1))
            carga_baixa = c_bx1.selectbox("Selecione a carga pendente para concluir:", opcoes_baixa, key="sel_baixa_manual_gp")
            lacre_baixa = c_bx2.text_input("Lacre (Opcional):", placeholder="Ex: 123456", key="in_lacre_baixa_gp")
            conf_baixa = st.checkbox(f"Confirmo que desejo marcar a carga '{carga_baixa}' como 100% conferida agora.", key="chk_baixa_manual_gp")

            if st.button("✅ Marcar Carga como 100% Conferida", type="primary", disabled=not conf_baixa, key="btn_baixa_manual_gp"):
                df_banco_bx = carregar_dados("cargas")
                mask_bx = df_banco_bx["id_carga"] == carga_baixa
                if mask_bx.any():
                    df_banco_bx.loc[mask_bx, "bipado"] = pd.to_numeric(df_banco_bx.loc[mask_bx, "pedido_real"], errors="coerce").fillna(0).astype(int)
                    if lacre_baixa.strip():
                        if "lacre" not in df_banco_bx.columns:
                            df_banco_bx["lacre"] = ""
                        df_banco_bx["lacre"] = df_banco_bx["lacre"].astype(object)
                        df_banco_bx.loc[mask_bx, "lacre"] = limpar_texto(lacre_baixa)
                    salvar_dados(df_banco_bx, "cargas")

                    df_bipes_bx = carregar_dados("bipes")
                    agora_bx = datetime.now(FUSO_BR).strftime("%d/%m/%Y %H:%M:%S")
                    reg_bx = pd.DataFrame([{
                        "data_hora": agora_bx,
                        "id_carga": carga_baixa,
                        "etiqueta": "BAIXA-MANUAL",
                        "codigo_bipado": "TODOS",
                        "codigo_vinculado": "TODOS",
                        "tipo": "CONCLUSAO MANUAL",
                        "lote": "-",
                        "quantidade": int(pd.to_numeric(df_banco_bx.loc[mask_bx, "pedido_real"], errors="coerce").fillna(0).sum()),
                        "conferente": st.session_state.nome_usuario
                    }])
                    df_bipes_bx = pd.concat([reg_bx, df_bipes_bx], ignore_index=True) if not df_bipes_bx.empty else reg_bx
                    salvar_dados(df_bipes_bx, "bipes")

                    st.session_state.toast_global = f"Carga '{carga_baixa}' concluída 100% e movida para Conferidas!"
                    st.rerun()
            
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
            renderizar_tabela_wms(df_carga_bipes, "conf_bipes_sup", use_container_width=True, hide_index=True, height=385)
        else:
            renderizar_tabela_wms(df_carga_bipes.head(10), "conf_bipes_op", use_container_width=True, hide_index=True)

elif aba == "📈 Painel de Acompanhamento":
    st.title("📈 Painel de Acompanhamento")

    df_todas_cargas = carregar_dados("cargas")
    if df_todas_cargas.empty:
        st.info("Nenhuma carga cadastrada.")
        st.stop()

    c_sel_pa, c_btn_pa, _ = st.columns((2.0, 1.0, 3.0), vertical_alignment="bottom")
    carga_selecionada = c_sel_pa.selectbox("Selecione a Carga:", df_todas_cargas["id_carga"].unique().tolist(), key="sel_carga_painel")
    if c_btn_pa.button("🔄 Atualizar Dados", type="primary"):
        limpar_cache_operacional()
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
    st.caption("Conferência cruzada entre pedido planejado, etiquetas bipadas, lotes e retorno do cliente.")
    st.markdown(
        """
        <style>
        /* Cards modernos para Expanders e Uploader na Auditoria */
        div[data-testid="stExpander"] {
            background-color: rgba(255, 255, 255, 0.45) !important;
            border: 1px solid rgba(20, 26, 22, 0.14) !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 14px rgba(20, 26, 22, 0.04) !important;
            margin-bottom: 8px !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(27, 94, 32, 0.45) !important;
        }
        section[data-testid="stFileUploaderDropzone"] {
            background-color: rgba(255, 255, 255, 0.45) !important;
            border: 1.5px dashed rgba(27, 94, 32, 0.45) !important;
            border-radius: 14px !important;
            padding: 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
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
    if not df_plan_aud.empty and "validado" in df_plan_aud.columns:
        for _, r_pa in df_plan_aud.iterrows():
            v_str = str(r_pa.get("validado", "")).strip()
            if v_str and v_str.lower() not in ["nan", "none", "null", "nao", "não"]:
                for col_aud_k in ("id_carga", "Nº Pedido"):
                    val_k = limpar_texto(r_pa.get(col_aud_k, ""))
                    if val_k:
                        cargas_ja_validadas.add(val_k)
                        for tok in re.findall(r"[A-Z0-9-]+", val_k):
                            cargas_ja_validadas.add(tok)
                
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
                limpar_cache_operacional()
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
                limpar_cache_operacional()
                st.success(f"🎉 {len(cargas_lote_escolhidas)} pedido(s) marcados como Auditado (Histórico)!")
                st.rerun()

    if not cargas_disponiveis_aud:
        st.success("🎉 Todas as cargas cadastradas já foram validadas!")
        st.stop()

    col_aud_esq, col_aud_dir = st.columns([1.15, 1.35], gap="medium")
    with col_aud_esq:
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
                    limpar_cache_operacional()
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
                                st.session_state.toast_global = f"Etiqueta '{limpar_texto(registro_alvo['etiqueta'])}' atualizada (Lote: {limpar_texto(novo_lote_input)} | Qtd: {int(nova_qtd_input)})!"
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
                            st.session_state.toast_global = f"Etiqueta '{limpar_texto(registro_alvo['etiqueta'])}' estornada! Liberada para rebipagem."
                            st.rerun()
                else:
                    st.info("Nenhuma etiqueta bipada nesta carga ainda.")
            else:
                st.info("Nenhuma etiqueta bipada nesta carga ainda.")

    with col_aud_dir:
        arq_cliente = st.file_uploader("Suba o Excel/CSV enviado pelo cliente:", type=["xlsx", "xls", "csv"])    

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

        _, col_btn_gerar_aud = st.columns((4.4, 1.0))
        if col_btn_gerar_aud.button("🔍 Iniciar Validação", type="primary", use_container_width=True):    
                
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

        ja_esta_validada = limpar_texto(carga_selecionada) in cargas_ja_validadas
        if ja_esta_validada:
            st.info(f"✅ Esta carga (**{carga_selecionada}**) já foi validada e liberada para expedição.")
        elif erro_skus > 0:
            st.error(f"🚫 Validação bloqueada: existem **{erro_skus} produto(s) com divergência** no cruzamento acima. Corrija antes de liberar o pedido.")

        col_btn_dl_aud, _, col_btn_val_aud = st.columns((1.8, 1.4, 2.0), vertical_alignment="center")
        with col_btn_dl_aud:
            st.download_button(
                label="📥 Baixar Relatório Completo em Excel (.xlsx)",
                data=buffer_relatorio.getvalue(),
                file_name=f"validacao_{carga_selecionada}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        btn_validar_clicado = False
        if not ja_esta_validada:
            with col_btn_val_aud:
                btn_validar_clicado = st.button("✅ Validar Pedido e Liberar para Expedição", type="primary", use_container_width=True)

        if btn_validar_clicado:
            df_plan_salvar = carregar_dados("planejamento")
            agora_val = datetime.now(FUSO_BR).strftime("%d/%m/%Y %H:%M")
            carimbo_val = f"Validado por {st.session_state.nome_usuario} ({agora_val})"

            if df_plan_salvar.empty or "id_carga" not in df_plan_salvar.columns:
                df_plan_salvar = pd.DataFrame(columns=["id_carga", "cliente", "transportadora", "placa", "data_carregamento", "status", "observacoes", "validado"])

            if "validado" not in df_plan_salvar.columns:
                df_plan_salvar["validado"] = ""

            df_plan_salvar["validado"] = df_plan_salvar["validado"].astype(object)
            cid_aud_limpo = limpar_texto(carga_selecionada)
            padrao_aud = r"(?<![A-Z0-9])" + re.escape(cid_aud_limpo) + r"(?![A-Z0-9])"
            mask_p = (
                (df_plan_salvar["id_carga"].apply(limpar_texto) == cid_aud_limpo) |
                df_plan_salvar["Nº Pedido"].apply(limpar_texto).str.contains(padrao_aud, regex=True, na=False)
            )

            if mask_p.any():
                df_plan_salvar.loc[mask_p, "validado"] = carimbo_val
            else:
                nova_linha_p = {col: "" for col in df_plan_salvar.columns}
                nova_linha_p["id_carga"] = carga_selecionada
                nova_linha_p["status"] = "🟢 Carregado / Liberado"
                nova_linha_p["validado"] = carimbo_val
                df_plan_salvar = pd.concat([df_plan_salvar, pd.DataFrame([nova_linha_p])], ignore_index=True)

            salvar_dados(df_plan_salvar, "planejamento")
            limpar_cache_operacional()
            st.session_state.toast_global = f"Pedido '{carga_selecionada}' validado e liberado para expedição!"
            st.rerun()
                
    st.divider()
    if st.session_state.perfil_usuario in ("ADMIN", "GERENTE", "SUPERVISOR") and cargas_ja_validadas:
        with st.expander("🗄️ Arquivar Cargas Já Auditadas (Por Período)"):
            st.caption("Selecione um período para arquivar cargas já auditadas. Os registros encerrados são movidos para o histórico para manter o sistema leve, sem afetar as cargas em andamento.")

            c_arq_dt1, c_arq_dt2 = st.columns(2)
            hoje_arq = datetime.now(FUSO_BR).date()
            dt_ini_arq = c_arq_dt1.date_input("📅 Data Inicial:", value=hoje_arq.replace(day=1), format="DD/MM/YYYY", key="dt_ini_arq")
            dt_fim_arq = c_arq_dt2.date_input("📅 Data Final:", value=hoje_arq, format="DD/MM/YYYY", key="dt_fim_arq")

            if dt_ini_arq > dt_fim_arq:
                st.warning("⚠️ A Data Inicial não pode ser maior que a Data Final.")
            else:
                df_cargas_base_arq = carregar_dados("cargas")
                df_plan_base_arq = carregar_dados("planejamento")
                df_bipes_base_arq = carregar_dados("bipes")

                mapa_data_carga = {}
                if df_plan_base_arq is not None and not df_plan_base_arq.empty and "Data" in df_plan_base_arq.columns:
                    for _, rp_a in df_plan_base_arq.iterrows():
                        dt_p_a = interpretar_data_br(rp_a.get("Data", ""))
                        if dt_p_a is not None:
                            for col_k_a in ("id_carga", "Nº Pedido"):
                                val_k_a = limpar_texto(rp_a.get(col_k_a, ""))
                                if val_k_a:
                                    mapa_data_carga[val_k_a] = dt_p_a
                                    for tok_a in re.findall(r"[A-Z0-9-]+", val_k_a):
                                        mapa_data_carga[tok_a] = dt_p_a

                if df_bipes_base_arq is not None and not df_bipes_base_arq.empty and "id_carga" in df_bipes_base_arq.columns and "data_hora" in df_bipes_base_arq.columns:
                    for _, rb_a in df_bipes_base_arq.iterrows():
                        cid_b_a = limpar_texto(rb_a.get("id_carga", ""))
                        if cid_b_a and cid_b_a not in mapa_data_carga:
                            dt_b_a = interpretar_data_br(rb_a.get("data_hora", ""))
                            if dt_b_a is not None:
                                mapa_data_carga[cid_b_a] = dt_b_a

                cargas_ativas_aud = [
                    limpar_texto(c) for c in df_cargas_base_arq["id_carga"].dropna().unique().tolist()
                    if limpar_texto(c) in cargas_ja_validadas
                ]
                cargas_no_periodo = sorted([
                    cid_chk for cid_chk in cargas_ativas_aud
                    if (cid_chk in mapa_data_carga) and (dt_ini_arq <= mapa_data_carga[cid_chk] <= dt_fim_arq)
                ])

                if cargas_no_periodo:
                    st.info(f"📋 **{len(cargas_no_periodo)} carga(s) auditada(s)** encontrada(s) entre **{dt_ini_arq.strftime('%d/%m/%Y')}** e **{dt_fim_arq.strftime('%d/%m/%Y')}**.")
                    sel_arq_todas = st.checkbox("Selecionar todas as cargas deste período", value=False, key="chk_arq_todas")
                    escolhidas_arq = st.multiselect(
                        "Confirme ou ajuste as cargas que serão arquivadas:",
                        options=cargas_no_periodo,
                        default=cargas_no_periodo if sel_arq_todas else list(),
                        key="ms_cargas_arquivar"
                    )
                    if st.button("🗄️ Mover Selecionadas para o Histórico", type="primary", disabled=len(escolhidas_arq) == 0, key="btn_exec_arquivar"):
                        with st.spinner("Arquivando cargas, etiquetas e planejamento com segurança..."):
                            limpar_cache_operacional()
                            df_c_at = carregar_dados("cargas")
                            df_b_at = carregar_dados("bipes")
                            df_p_at = carregar_dados("planejamento")

                            if df_c_at is None or df_c_at.empty:
                                st.error("⚠️ Falha ao ler a aba 'cargas'. Operação cancelada por segurança.")
                                st.stop()

                            ids_arq_set = {limpar_texto(x) for x in escolhidas_arq}

                            mask_c_arq = df_c_at["id_carga"].apply(limpar_texto).isin(ids_arq_set)
                            df_c_mover = df_c_at[mask_c_arq].copy()
                            df_c_ficar = df_c_at[~mask_c_arq].copy()

                            if not df_c_mover.empty:
                                df_c_hist = carregar_dados("cargas_historico")
                                df_c_hist_final = pd.concat([df_c_hist, df_c_mover], ignore_index=True) if not df_c_hist.empty else df_c_mover
                                salvar_dados(df_c_hist_final, "cargas_historico")

                                if df_c_ficar.empty:
                                    linha_vazia_c = pd.DataFrame([{col: "" for col in df_c_at.columns}])
                                    conn.update(worksheet="cargas", data=linha_vazia_c)
                                else:
                                    salvar_dados(df_c_ficar, "cargas")

                            if df_b_at is not None and not df_b_at.empty and "id_carga" in df_b_at.columns:
                                mask_b_arq = df_b_at["id_carga"].apply(limpar_texto).isin(ids_arq_set)
                                df_b_mover = df_b_at[mask_b_arq].copy()
                                df_b_ficar = df_b_at[~mask_b_arq].copy()

                                if not df_b_mover.empty:
                                    df_b_hist = carregar_dados("bipes_historico")
                                    df_b_hist_final = pd.concat([df_b_hist, df_b_mover], ignore_index=True) if not df_b_hist.empty else df_b_mover
                                    salvar_dados(df_b_hist_final, "bipes_historico")

                                    if df_b_ficar.empty:
                                        linha_vazia_b = pd.DataFrame([{col: "" for col in df_b_at.columns}])
                                        conn.update(worksheet="bipes", data=linha_vazia_b)
                                    else:
                                        salvar_dados(df_b_ficar, "bipes")

                            if df_p_at is not None and not df_p_at.empty:
                                def _linha_plan_no_arq(row_pa):
                                    for c_pa in ("id_carga", "Nº Pedido"):
                                        v_pa = limpar_texto(row_pa.get(c_pa, ""))
                                        if v_pa in ids_arq_set:
                                            return True
                                        for tk in re.findall(r"[A-Z0-9-]+", v_pa):
                                            if tk in ids_arq_set:
                                                return True
                                    return False

                                mask_p_arq = df_p_at.apply(_linha_plan_no_arq, axis=1)
                                df_p_mover = df_p_at[mask_p_arq].copy()
                                df_p_ficar = df_p_at[~mask_p_arq].copy()

                                if not df_p_mover.empty:
                                    df_p_hist = carregar_dados("planejamento_historico")
                                    df_p_hist_final = pd.concat([df_p_hist, df_p_mover], ignore_index=True) if not df_p_hist.empty else df_p_mover
                                    salvar_dados(df_p_hist_final, "planejamento_historico")

                                    if df_p_ficar.empty:
                                        linha_vazia_p = pd.DataFrame([{col: "" for col in df_p_at.columns}])
                                        conn.update(worksheet="planejamento", data=linha_vazia_p)
                                    else:
                                        salvar_dados(df_p_ficar, "planejamento")

                            limpar_cache_operacional()
                            st.success(f"🗄️ {len(escolhidas_arq)} carga(s) arquivada(s) com segurança em 'cargas_historico', 'bipes_historico' e 'planejamento_historico'!")
                            st.rerun()
                else:
                    st.caption("Nenhuma carga auditada encontrada neste intervalo de datas.")

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
        "SUPERVISOR": (TODOS_MODULOS_SISTEMA[:-1], TODAS_PERMISSOES_CRITICAS),
        "GERENTE": (TODOS_MODULOS_SISTEMA[:-1], TODAS_PERMISSOES_CRITICAS),
        "ADMIN": (TODOS_MODULOS_SISTEMA, TODAS_PERMISSOES_CRITICAS),
    }

    with st.expander("➕ Cadastrar Novo Colaborador", expanded=False):
        c_nu_top1, c_nu_top2 = st.columns((1.5, 2.5), vertical_alignment="center")
        nu_perfil = c_nu_top1.selectbox(
            "1️⃣ Escolha o Perfil Base (preenche acessos automaticamente):",
            ["CONFERENTE", "AUXILIAR ADMINISTRATIVO", "ANALISTA", "SUPERVISOR", "GERENTE"] + (["ADMIN"] if st.session_state.perfil_usuario == "ADMIN" else []),
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
        df_edit_u = df_usuarios if st.session_state.perfil_usuario == "ADMIN" else df_usuarios[df_usuarios["perfil"].apply(limpar_texto) != "ADMIN"]
        opcoes_u = {
            f"{limpar_texto(r['nome'])} ({limpar_texto(r['login'])}) — {limpar_texto(r['perfil'])} [{'🟢 Ativo' if limpar_texto(r['ativo']) == 'SIM' else '🔴 Inativo'}]": idx
            for idx, r in df_edit_u.iterrows()
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
                limpar_cache_operacional()
                st.success(f"✅ Acessos e dados de **{limpar_texto(eu_nome)}** atualizados com sucesso!")
                st.rerun()


