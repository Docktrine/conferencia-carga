import streamlit as st
import pandas as pd
import io
import os
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_gsheets import GSheetsConnection

ARQUIVO_LOGO = next((f for f in ["logo_grano.png", "logo_grano.jpg", "logo_grano.jpeg"] if os.path.exists(f)), None)

st.set_page_config(
    page_title="Sistema de Conferência de Carga - Grano",
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

COLUNAS_TEXTO = ["id_carga", "codigo", "etiqueta", "codigo_bipado", "codigo_vinculado", "lote"]

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

# ==============================================================================
# CONTROLE DE PERFIL + LOGO CENTRALIZADO NO TOPO DO MENU LATERAL
# ==============================================================================
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
        aba = "2️⃣ Bipagem / Digitação"
        
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
                "1️⃣ Carregar Meu Pedido",
                "2️⃣ Bipagem / Digitação",
                "3️⃣ Painel de Acompanhamento",
                "📊 Gestão de Pedidos",
                "4️⃣ Validação Final (Cliente)"
            ]
        )
        st.divider()
        if st.button("🔒 Sair do Modo Admin", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

# ==============================================================================
# ETAPA 1: IMPORTAR PEDIDO (INDIVIDUAL OU EM MASSA) + EXCLUIR CARGA
# ==============================================================================
if aba == "1️⃣ Carregar Meu Pedido":
    st.title("1️⃣ Importar Pedido para Conferência")
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
                c_nome, c_id = st.columns([1.2, 1], vertical_alignment="center")
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

# ==============================================================================
# GESTÃO DE PEDIDOS + DATA DE CONCLUSÃO + CONSULTA SUSPENSA + EDIÇÃO DO MOTIVO
# ==============================================================================
elif aba == "📊 Gestão de Pedidos":
    st.title("📊 Gestão de Pedidos: Conferidos x Pendentes")

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

# ==============================================================================
# ETAPA 2: CONFERÊNCIA ÀS CEGAS
# ==============================================================================
elif aba == "2️⃣ Bipagem / Digitação":
    st.title("📦 Conferência Física de Carga")

    df_todas_cargas = carregar_dados("cargas")
    
    if df_todas_cargas.empty or "id_carga" not in df_todas_cargas.columns:
        st.warning("Nenhuma carga disponível no momento. Aguarde a liberação do administrativo.")
        st.stop()

    lista_cargas = df_todas_cargas["id_carga"].unique().tolist()
    carga_selecionada = st.selectbox("Selecione a Carga para Conferir:", lista_cargas)

    df_carga_selecionada_atual = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada]
    if verificar_carga_100_concluida(df_carga_selecionada_atual):
        st.success("✅ Conferência realizada com sucesso!")

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

# ==============================================================================
# ETAPA 3: PAINEL DE ACOMPANHAMENTO + CORTE COM MOTIVO
# ==============================================================================
elif aba == "3️⃣ Painel de Acompanhamento":
    st.title("3️⃣ Painel de Acompanhamento")

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

# ==============================================================================
# ETAPA 4: VALIDAÇÃO FINAL (CLIENTE)
# ==============================================================================
elif aba == "4️⃣ Validação Final (Cliente)":
    st.title("4️⃣ Auditoria Final: Pedido x Bipado x Cliente (+ Lotes)")

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
                    st.markdown("**1️⃣ Corrigir Apenas o Lote**")
                    novo_lote_input = st.text_input(
                        "Digite o Lote correto:",
                        value=limpar_texto(registro_alvo["lote"]),
                        key="adm_novo_lote"
                    )
                    if st.button("💾 Atualizar Lote", use_container_width=True):
                        if novo_lote_input.strip():
                            df_bipes_adm["lote"] = df_bipes_adm["lote"].astype(object)
                            df_bipes_adm.at[idx_selecionado, "lote"] = limpar_texto(novo_lote_input)
                            salvar_dados(df_bipes_adm, "bipes")
                            if "relatorio_final" in st.session_state:
                                del st.session_state.relatorio_final
                            st.success(f"✅ Lote da etiqueta '{limpar_texto(registro_alvo['etiqueta'])}' atualizado para '{limpar_texto(novo_lote_input)}'!")
                            st.rerun()
                        else:
                            st.error("⚠️ O lote não pode ficar em branco.")

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
