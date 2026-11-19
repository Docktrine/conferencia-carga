import streamlit as st
import pandas as pd
import io
import os
import base64
import unicodedata
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection

ARQUIVO_LOGO = next((f for f in ["logo_grano.png", "logo_grano.jpg", "logo_grano.jpeg"] if os.path.exists(f)), None)

st.set_page_config(
    page_title="WMS Grano — Gestão Logística",
    page_icon=ARQUIVO_LOGO if ARQUIVO_LOGO else "📦",
    layout="wide"
)

conn = st.connection("gsheets", type=GSheetsConnection)

SENHA_ADMIN = "grano2026"
FUSO_BR = ZoneInfo("America/Sao_Paulo")

if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False
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

COLUNAS_TEXTO = ["id_carga", "codigo", "etiqueta", "codigo_bipado", "codigo_vinculado", "lote", "Nº Pedido", "Ordem de Carregamento", "Placa do veículo", "Lacre"]

COLUNAS_PLANEJAMENTO = [
    "Data", "Hora", "Local de Carregamento", "Ordem de Carregamento",
    "Nº Pedido", "Valor Pedido", "Cliente", "Transportadora", "Placa do veículo",
    "Tipo de Veículo", "Valor de Frete", "UF", "Cidade", "CIF/FOB",
    "Veículo compartilhado", "Data da entrega", "Observação", "Status"
]

STATUS_PLANEJAMENTO = [
    "⏳ Aguardando Veículo",
    "🚚 Veículo no Pátio",
    "📦 Em Conferência",
    "✅ Carregado / Liberado",
    "⚠️ Atrasado / Ocorrência"
]

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

def carregar_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        df = df.dropna(how="all")
        if not df.empty:
            for col in COLUNAS_TEXTO:
                if col in df.columns:
                    df[col] = df[col].astype(object).apply(limpar_texto)
        return df
    except Exception:
        return pd.DataFrame()

def salvar_dados(df, aba):
    if not df.empty:
        for col in COLUNAS_TEXTO:
            if col in df.columns:
                df[col] = df[col].astype(object).apply(limpar_texto)
    conn.update(worksheet=aba, data=df)

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

with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div style="text-align: center; padding-top: 4px; padding-bottom: 12px;">
                <img src="data:{LOGO_MIME};base64,{LOGO_B64}" style="width: 96px; height: 96px; border-radius: 16px; object-fit: cover; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin-bottom: 20px;">
                <h2 style="margin: 0; padding: 0; font-size: 1.45rem;">Grano Logística</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("📦 Grano Logística")

    if not st.session_state.admin_autenticado:
        st.info("👷‍♂️ Modo: **Conferente (Às Cegas)**")
        aba = "📦 Conferência dos Pedidos"
        
        st.divider()
        with st.expander("🔐 Acesso Administrativo"):
            senha_digitada = st.text_input("Senha do Administrativo:", type="password", key="input_senha_adm")
            if st.button("Entrar como Admin", use_container_width=True):
                if senha_digitada == SENHA_ADMIN:
                    st.session_state.admin_autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    else:
        st.success("👔 Modo: **Administrativo**")
        aba = st.radio(
            "Escolha a etapa:",
            [
                "🚚 Planejamento Logística",
                "📥 Importação de Pedidos",
                "📦 Conferência dos Pedidos",
                "📈 Painel de Acompanhamento",
                "📋 Gestão de Pedidos",
                "✅ Auditoria e Ajustes"
            ]
        )
        st.divider()
        if st.button("🔒 Sair do Modo Admin", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

if aba == "🚚 Planejamento Logística":
    st.title("📡 Monitoramento de Pedidos Pendentes")
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

    st.divider()

    st.subheader("Controle de Pedidos Planejados")
    df_exibir_plan = df_plan[COLUNAS_PLANEJAMENTO].copy()

    if not df_exibir_plan.empty:
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            datas_carreg = sorted([d for d in df_exibir_plan["Data"].dropna().unique().tolist() if str(d).strip() != ""])
            filtro_data_carreg = st.selectbox("Filtrar por Data de Carregamento:", ["Todas as datas"] + datas_carreg, key="filtro_fila_data_carreg")
        with f_col2:
            filtro_status_plan = st.selectbox("Filtrar por Status:", ["Todos os status"] + STATUS_PLANEJAMENTO, key="filtro_fila_status")
        with f_col3:
            busca_livre = st.text_input("Buscar Pedido, Cliente ou Placa:", placeholder="Digite para filtrar...", key="filtro_fila_busca")

        if filtro_data_carreg != "Todas as datas":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Data"] == filtro_data_carreg]
        if filtro_status_plan != "Todos os status":
            df_exibir_plan = df_exibir_plan[df_exibir_plan["Status"] == filtro_status_plan]
        if busca_livre.strip():
            termo = busca_livre.strip().lower()
            mask_busca = (
                df_exibir_plan["Nº Pedido"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Cliente"].astype(str).str.lower().str.contains(termo, na=False) |
                df_exibir_plan["Placa do veículo"].astype(str).str.lower().str.contains(termo, na=False)
            )
            df_exibir_plan = df_exibir_plan[mask_busca]

        qtd_total_kpi = len(df_exibir_plan)
        qtd_aguardando = int(df_exibir_plan["Status"].isin(["⏳ Aguardando Veículo", "🚚 Veículo no Pátio"]).sum())
        qtd_conferencia = int((df_exibir_plan["Status"] == "📦 Em Conferência").sum())
        qtd_liberados = int((df_exibir_plan["Status"] == "✅ Carregado / Liberado").sum())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📋 Pedidos na Fila", qtd_total_kpi)
        k2.metric("⏳ Aguardando / Pátio", qtd_aguardando)
        k3.metric("📦 Em Conferência", qtd_conferencia)
        k4.metric("✅ Carregados / Liberados", qtd_liberados)

        st.dataframe(df_exibir_plan, use_container_width=True, hide_index=True)

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
    else:
        st.info("Nenhum pedido cadastrado no planejamento ainda.")

    st.divider()

    with st.expander("➕ Importar Pedido Manualmente"):
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

            salvar_novo_plan = st.form_submit_button("💾 Salvar na Agenda", type="primary", use_container_width=True)

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
                        "Status": in_status
                    }])
                    df_plan_atualizado = pd.concat([df_plan, nova_linha_plan], ignore_index=True)
                    salvar_dados(df_plan_atualizado[COLUNAS_PLANEJAMENTO], "planejamento")
                    st.success(f"✅ Pedido **'{ped_limpo}'** adicionado ao planejamento!")
                    st.rerun()

    with st.expander("📥 Importar Planilha de Planejamento (.xlsx / .csv)"):
        st.caption("O sistema reconhece automaticamente colunas mesmo com letras maiúsculas/minúsculas, acentos ou variações (ex: 'Placa Veículo' ou 'Placa do veículo').")
        arq_plan = st.file_uploader("Selecione o Excel ou CSV de planejamento:", type=["xlsx", "xls", "csv"], key="up_plan_massa")
        if arq_plan:
            df_up_plan = pd.read_csv(arq_plan, sep=None, engine="python", dtype=str) if arq_plan.name.endswith(".csv") else pd.read_excel(arq_plan, dtype=str)
            cols_arquivo = list(df_up_plan.columns)
            opcoes_mapeamento = ["(Ignorar / Deixar em branco)"] + cols_arquivo

            st.write(f"Linhas encontradas no arquivo: **{len(df_up_plan)}**. Confira o vínculo automático das colunas:")
            mapeamento_escolhido = {}

            for i in range(0, len(COLUNAS_PLANEJAMENTO), 3):
                cols_ui = st.columns(3)
                for j in range(3):
                    if i + j < len(COLUNAS_PLANEJAMENTO):
                        col_dest = COLUNAS_PLANEJAMENTO[i + j]
                        sugestao = encontrar_coluna_correspondente(col_dest, cols_arquivo)
                        idx_padrao = opcoes_mapeamento.index(sugestao) if sugestao in opcoes_mapeamento else 0
                        mapeamento_escolhido[col_dest] = cols_ui[j].selectbox(
                            f"{col_dest}:",
                            opcoes_mapeamento,
                            index=idx_padrao,
                            key=f"map_plan_{col_dest}"
                        )

            if st.button("🚀 Importar Linhas para a Agenda", type="primary", use_container_width=True):
                if mapeamento_escolhido["Nº Pedido"] == "(Ignorar / Deixar em branco)":
                    st.error("⚠️ Selecione qual coluna do seu arquivo corresponde ao **Nº Pedido**!")
                else:
                    df_novo_lote = pd.DataFrame()
                    for col_dest, col_orig in mapeamento_escolhido.items():
                        if col_orig != "(Ignorar / Deixar em branco)" and col_orig in df_up_plan.columns:
                            df_novo_lote[col_dest] = df_up_plan[col_orig].fillna("").astype(str).str.strip()
                        else:
                            df_novo_lote[col_dest] = ""

                    df_novo_lote["Nº Pedido"] = df_novo_lote["Nº Pedido"].apply(limpar_texto)
                    df_novo_lote["Status"] = df_novo_lote["Status"].apply(lambda s: s if str(s).strip() != "" else status_padrao)
                    for col_dt in ("Data", "Data da entrega"):
                        df_novo_lote[col_dt] = df_novo_lote[col_dt].apply(formatar_data_br_str)
                    df_novo_lote["Hora"] = df_novo_lote["Hora"].apply(formatar_hora_br_str)
                    for col_vl in ("Valor Pedido", "Valor de Frete"):
                        df_novo_lote[col_vl] = df_novo_lote[col_vl].apply(formatar_moeda_br_str)

                    df_novo_lote = df_novo_lote[df_novo_lote["Nº Pedido"] != ""]
                    df_novo_lote = df_novo_lote[~df_novo_lote["Nº Pedido"].isin(df_plan["Nº Pedido"].values)]

                    if not df_novo_lote.empty:
                        df_plan_comb = pd.concat([df_plan, df_novo_lote], ignore_index=True)
                        salvar_dados(df_plan_comb[COLUNAS_PLANEJAMENTO], "planejamento")
                        st.success(f"✅ {len(df_novo_lote)} pedido(s) importado(s) para o planejamento!")
                        st.rerun()
                    else:
                        st.warning("Nenhum pedido novo encontrado (todos já constavam na agenda ou estavam sem Nº Pedido).")

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

                c_btn_save, c_btn_del = st.columns(2)
                btn_atualizar_plan = c_btn_save.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
                btn_excluir_plan = c_btn_del.form_submit_button("🗑️ Excluir este Agendamento", use_container_width=True)

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
                            df_bipes_restante = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade"])
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
        st.rerun()

    df_todas = carregar_dados("cargas")
    if df_todas.empty or "id_carga" not in df_todas.columns:
        st.info("Nenhuma carga cadastrada no sistema.")
        st.stop()

    df_todas["pedido_real"] = pd.to_numeric(df_todas["pedido_real"], errors="coerce").fillna(0).astype(int)
    df_todas["bipado"] = pd.to_numeric(df_todas["bipado"], errors="coerce").fillna(0).astype(int)

    df_bipes_datas = carregar_dados("bipes")
    ultimas_datas_carga = {}
    if not df_bipes_datas.empty and "id_carga" in df_bipes_datas.columns and "data_hora" in df_bipes_datas.columns:
        for cid_b, grp_b in df_bipes_datas.groupby("id_carga", sort=False):
            datas_validas = [str(d).strip() for d in grp_b["data_hora"] if str(d).strip() and str(d).strip().upper() != "NAN"]
            if datas_validas:
                ultimas_datas_carga[cid_b] = datas_validas[0].split()[0]

    lista_pendentes = list()
    lista_concluidas = list()

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
                "Qtd de SKUs": skus_ped,
                "Volumes Pedidos": tot_ped,
                "Volumes Bipados": tot_bip,
                "Conferido em": data_conclusao,
                "Lacre": obter_lacre_carga(grupo) or "-",
                "Situação": f"✅ 100% Conferida{selo_corte}"
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
                "Qtd de SKUs": skus_ped,
                "Volumes Pedidos": tot_ped,
                "Volumes Bipados": tot_bip,
                "Falta Bipar": falta,
                "Situação": situacao
            })

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Cargas", len(lista_pendentes) + len(lista_concluidas))
    m2.metric("⏳ Faltam Conferir", len(lista_pendentes))
    m3.metric("✅ Conferidas (100%)", len(lista_concluidas))

    st.divider()

    st.subheader("⏳ Pedidos que Faltam Conferir")
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

            if itens_cortados_edicao:
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

    lista_cargas = df_todas_cargas["id_carga"].unique().tolist()
    carga_selecionada = st.selectbox("Selecione a Carga para Conferir:", lista_cargas)

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
                    st.session_state[f"input_lacre_conf_{carga_selecionada}"] = ""
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
            "quantidade": qtd_final
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
                    df_bipes = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade"])
                salvar_dados(df_bipes, "bipes")
                st.warning(f"↩️ Etiqueta '{ult_etiq}' ({ult_qtd}x) foi estornada e liberada novamente!")
                st.rerun()

    st.subheader("Últimas Etiquetas Conferidas")
    df_bipes_vis = carregar_dados("bipes")
    if not df_bipes_vis.empty and "id_carga" in df_bipes_vis.columns:
        df_carga_bipes = df_bipes_vis[df_bipes_vis["id_carga"] == carga_selecionada].copy()
        if "quantidade" in df_carga_bipes.columns:
            df_carga_bipes["quantidade"] = pd.to_numeric(df_carga_bipes["quantidade"], errors="coerce").fillna(0).astype(int)

        if st.session_state.admin_autenticado:
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
                    st.session_state[f"input_lacre_painel_{carga_selecionada}"] = ""
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

    carga_selecionada = st.selectbox("Selecione a Carga para Auditar:", df_todas_cargas["id_carga"].unique().tolist())

    df_carga_aud = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada]
    if carga_possui_corte(df_carga_aud):
        st.warning(f"✂️ **OBSERVAÇÃO:** Este pedido foi gerado/finalizado **COM CORTE**: **{extrair_detalhes_corte(df_carga_aud)}**")

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
                            df_bipes_adm = pd.DataFrame(columns=["data_hora", "id_carga", "etiqueta", "codigo_bipado", "codigo_vinculado", "tipo", "lote", "quantidade"])
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
