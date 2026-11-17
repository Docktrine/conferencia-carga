import streamlit as st
import pandas as pd
import io
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema de Conferência de Carga", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# Senha do Administrativo para liberar as Etapas 1, 3 e 4
SENHA_ADMIN = "grano2026"

if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
if "msg_sucesso_carga" not in st.session_state:
    st.session_state.msg_sucesso_carga = ""

def limpar_id(valor):
    texto = str(valor).strip().upper()
    if texto.endswith(".0"):
        texto = texto[:-2]
    return texto

def carregar_dados(aba):
    try:
        df = conn.read(worksheet=aba, ttl=0)
        df = df.dropna(how="all")
        if not df.empty and "id_carga" in df.columns:
            df["id_carga"] = df["id_carga"].apply(limpar_id)
        return df
    except Exception:
        return pd.DataFrame()

def salvar_dados(df, aba):
    if not df.empty and "id_carga" in df.columns:
        df["id_carga"] = df["id_carga"].apply(limpar_id)
    conn.update(worksheet=aba, data=df)

# ==============================================================================
# CONTROLE DE PERFIL (CONFERÊNCIA ÀS CEGAS VS ADMINISTRATIVO)
# ==============================================================================
with st.sidebar:
    st.title("📦 Grano Logística")
    if not st.session_state.admin_autenticado:
        st.info("👷‍♂️ Modo: **Conferente (Às Cegas)**")
        aba = "2️⃣ [Celular] Bipagem / Digitação"
        
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
                "1️⃣ [PC] Carregar Meu Pedido",
                "2️⃣ [Celular] Bipagem / Digitação",
                "3️⃣ [PC] Painel: O que falta",
                "4️⃣ [PC] Validação Final (Cliente)"
            ]
        )
        st.divider()
        if st.button("🔒 Sair do Modo Admin", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

# ==============================================================================
# ETAPA 1: CARREGAR PEDIDO NO PC (LIMPA AUTOMATICAMENTE APÓS ENVIAR) + EXCLUIR
# ==============================================================================
if aba == "1️⃣ [PC] Carregar Meu Pedido":
    st.title("1️⃣ Importar Pedido para Conferência")
    st.write("Suba a planilha do pedido no PC (SKU, Produto e Quantidade). Ela ficará disponível imediatamente no celular do conferente.")

    # Exibe o alerta verde caso tenha acabado de enviar uma carga
    if st.session_state.msg_sucesso_carga:
        st.success(st.session_state.msg_sucesso_carga)
        st.session_state.msg_sucesso_carga = ""

    id_carga = st.text_input(
        "Identificação da Carga / Pedido (Ex: CARGA-105):",
        placeholder="Digite um código único para esta carga",
        key=f"input_id_carga_{st.session_state.upload_key}"
    )
    
    # Verificação imediata se o código da carga já existe na planilha
    df_existente_check = carregar_dados("cargas")
    carga_ja_existe = False
    id_limpo = limpar_id(id_carga)

    if id_limpo and not df_existente_check.empty and "id_carga" in df_existente_check.columns:
        cargas_cadastradas = df_existente_check["id_carga"].unique().tolist()
        if id_limpo in cargas_cadastradas:
            carga_ja_existe = True
            st.error(f"🚫 BLOQUEADO! A carga **'{id_limpo}'** já existe no sistema! Para evitar perda de dados, digite um código diferente ou exclua a carga antiga lá embaixo primeiro.")

    arq_pedido = st.file_uploader(
        "Suba o Excel/CSV do seu pedido",
        type=["xlsx", "xls", "csv"],
        key=f"uploader_pedido_{st.session_state.upload_key}"
    )
    
    if arq_pedido and id_limpo and not carga_ja_existe:
        df_ped = pd.read_csv(arq_pedido, sep=None, engine="python", dtype=str) if arq_pedido.name.endswith(".csv") else pd.read_excel(arq_pedido, dtype=str)
        cols_ped = list(df_ped.columns)
        
        st.subheader("Mapeamento de Colunas")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_cod = st.selectbox("Coluna do SKU / CÓDIGO:", cols_ped)
        with c2:
            p_prod = st.selectbox("Coluna do NOME DO PRODUTO:", cols_ped)
        with c3:
            p_qtd = st.selectbox("Coluna da QUANTIDADE PEDIDA:", cols_ped)

        if st.button("🚀 Enviar Pedido para o Celular do Conferente", type="primary", use_container_width=True):
            try:
                df_existente = carregar_dados("cargas")
                if not df_existente.empty and "id_carga" in df_existente.columns:
                    if id_limpo in df_existente["id_carga"].unique().tolist():
                        st.error(f"🚫 BLOQUEADO! A carga '{id_limpo}' já está cadastrada.")
                        st.stop()

                base_ped = pd.DataFrame({
                    "id_carga": id_limpo,
                    "codigo": df_ped[p_cod].astype(str).str.strip(),
                    "produto": df_ped[p_prod].astype(str).str.strip(),
                    "pedido_real": pd.to_numeric(df_ped[p_qtd], errors="coerce").fillna(0).astype(int)
                })
                base_ped = base_ped[base_ped["codigo"] != "nan"]
                base_ped = base_ped.groupby(["id_carga", "codigo", "produto"], as_index=False).sum()
                base_ped["bipado"] = 0

                if not df_existente.empty and "id_carga" in df_existente.columns:
                    df_final = pd.concat([df_existente, base_ped], ignore_index=True)
                else:
                    df_final = base_ped

                salvar_dados(df_final, "cargas")
                
                # Limpa o arquivo e o campo de texto automaticamente para o próximo envio
                st.session_state.msg_sucesso_carga = f"✅ Carga '{id_limpo}' enviada para a nuvem! O conferente já pode iniciar no celular."
                st.session_state.upload_key += 1
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")

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
# ETAPA 2: CONFERÊNCIA ÀS CEGAS (TELA PADRÃO DO CONFERENTE)
# ==============================================================================
elif aba == "2️⃣ [Celular] Bipagem / Digitação":
    st.title("📦 Conferência Física de Carga")

    df_todas_cargas = carregar_dados("cargas")
    
    if df_todas_cargas.empty or "id_carga" not in df_todas_cargas.columns:
        st.warning("Nenhuma carga disponível no momento. Aguarde a liberação do administrativo.")
        st.stop()

    lista_cargas = df_todas_cargas["id_carga"].unique().tolist()
    carga_selecionada = st.selectbox("Selecione a Carga para Conferir:", lista_cargas)

    if "etiqueta_validada" not in st.session_state:
        st.session_state.etiqueta_validada = ""
    if "erro_etiqueta" not in st.session_state:
        st.session_state.erro_etiqueta = ""
    if "pendencia_substituicao" not in st.session_state:
        st.session_state.pendencia_substituicao = None

    def concluir_gravacao(etiq_atual, sku_bipado, sku_destino, lote_limpo, qtd_final, obs_tipo):
        df_bipes_check = carregar_dados("bipes")
        if not df_bipes_check.empty and "etiqueta" in df_bipes_check.columns:
            dup = (df_bipes_check["id_carga"] == carga_selecionada) & (df_bipes_check["etiqueta"].apply(limpar_id) == limpar_id(etiq_atual))
            if dup.any():
                st.error(f"🚫 BLOQUEADO! A etiqueta '{etiq_atual}' já foi registrada!")
                st.stop()

        df_banco = carregar_dados("cargas")
        filtro = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_id) == limpar_id(sku_destino))

        if filtro.any():
            idx = df_banco.index[filtro][0]
            df_banco.at[idx, "bipado"] = int(df_banco.at[idx, "bipado"]) + qtd_final
            if obs_tipo == "SUBSTITUIDO":
                desc_atual = str(df_banco.at[idx, "produto"])
                tag_sub = f" [Subst. p/ {sku_bipado}]"
                if tag_sub not in desc_atual:
                    df_banco.at[idx, "produto"] = desc_atual + tag_sub
        else:
            nova_linha = pd.DataFrame([{
                "id_carga": carga_selecionada,
                "codigo": sku_bipado,
                "produto": "⚠️ ITEM EXTRA (Fora do Pedido)",
                "pedido_real": 0,
                "bipado": qtd_final
            }])
            df_banco = pd.concat([df_banco, nova_linha], ignore_index=True)

        salvar_dados(df_banco, "cargas")

        novo_bipe = pd.DataFrame([{
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "id_carga": carga_selecionada,
            "etiqueta": etiq_atual,
            "codigo_bipado": sku_bipado,
            "codigo_vinculado": sku_destino,
            "tipo": obs_tipo,
            "lote": lote_limpo.upper(),
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
            filtro_dup = (df_bipes["id_carga"] == carga_selecionada) & (df_bipes["etiqueta"].apply(limpar_id) == limpar_id(etiq))
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
        st.info("📌 **Passo 1 de 4:** Bipe ou digite a ETIQUETA da caixa/volume.")
        
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
            st.write("Este produto está **substituindo** algum item do pedido original?")

            df_carga_atual = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada].copy()
            itens_originais = df_carga_atual[pd.to_numeric(df_carga_atual["pedido_real"]) > 0]

            if not itens_originais.empty:
                opcoes_dict = {
                    f"{limpar_id(row['codigo'])} - {row['produto']}": limpar_id(row['codigo'])
                    for _, row in itens_originais.iterrows()
                }
                escolha_label = st.selectbox("Selecione o item original que está sendo substituído:", list(opcoes_dict.keys()))
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

        else:
            st.info("📌 **Passos 2, 3 e 4:** Bipe ou digite os dados abaixo e clique em Salvar.")

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
                    value="1",
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
                        st.error("⚠️ A Quantidade precisa ser um número inteiro maior que zero!")
                    else:
                        qtd_final = int(qtd_texto)
                        df_banco = carregar_dados("cargas")
                        filtro_existe = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_id) == limpar_id(sku_limpo))

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
                ult_sku_alvo = limpar_id(ultimo_registro[col_alvo])
                ult_qtd = int(ultimo_registro["quantidade"])

                df_banco = carregar_dados("cargas")
                filtro = (df_banco["id_carga"] == carga_selecionada) & (df_banco["codigo"].apply(limpar_id) == ult_sku_alvo)

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
        st.dataframe(df_bipes_vis[df_bipes_vis["id_carga"] == carga_selecionada].head(10), use_container_width=True, hide_index=True)

# ==============================================================================
# ETAPA 3: PAINEL DE ACOMPANHAMENTO (APENAS ADMIN)
# ==============================================================================
elif aba == "3️⃣ [PC] Painel: O que falta":
    st.title("3️⃣ Acompanhamento em Tempo Real")

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

    total_pedido = int(df["pedido_real"].sum())
    total_bipado = int(df["bipado"].sum())
    total_falta = max(0, df[df["Falta Bipar"] > 0]["Falta Bipar"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total do Pedido", total_pedido)
    c2.metric("Total Já Bipado", total_bipado)
    c3.metric("Falta Bipar", int(total_falta))

    progresso = min(1.0, total_bipado / total_pedido) if total_pedido > 0 else 0
    st.progress(progresso, text=f"Progresso: {int(progresso * 100)}%")

    st.subheader("⚠️ Itens Pendentes")
    pendentes = df[df["Falta Bipar"] > 0][["codigo", "produto", "pedido_real", "bipado", "Falta Bipar"]]
    if pendentes.empty:
        st.success("🎉 Todos os itens do pedido foram bipados!")
    else:
        st.dataframe(pendentes, use_container_width=True, hide_index=True)

    sobras = df[df["Falta Bipar"] < 0].copy()
    if not sobras.empty:
        sobras["Qtd Excedente"] = sobras["bipado"] - sobras["pedido_real"]
        st.subheader("🚨 Itens Bipados a Mais / Fora do Pedido")
        st.dataframe(sobras[["codigo", "produto", "pedido_real", "bipado", "Qtd Excedente"]], use_container_width=True, hide_index=True)

# ==============================================================================
# ETAPA 4: VALIDAÇÃO FINAL (CLIENTE) + CONTROLE ADMINISTRATIVO DE ETIQUETAS
# ==============================================================================
elif aba == "4️⃣ [PC] Validação Final (Cliente)":
    st.title("4️⃣ Auditoria Final: Pedido x Bipado x Cliente (+ Lotes)")

    df_todas_cargas = carregar_dados("cargas")
    if df_todas_cargas.empty:
        st.info("Nenhuma carga cadastrada.")
        st.stop()

    carga_selecionada = st.selectbox("Selecione a Carga para Auditar:", df_todas_cargas["id_carga"].unique().tolist())

    with st.expander("🛠️ Administrativo: Corrigir Lote ou Estornar Etiqueta (Mandar Rebipar)"):
        df_bipes_adm = carregar_dados("bipes")
        if not df_bipes_adm.empty and "id_carga" in df_bipes_adm.columns:
            bipes_da_carga = df_bipes_adm[df_bipes_adm["id_carga"] == carga_selecionada].copy()
            
            if not bipes_da_carga.empty:
                opcoes_etiq = {}
                for idx_row, r in bipes_da_carga.iterrows():
                    etiq_str = limpar_id(r["etiqueta"])
                    sku_str = limpar_id(r["codigo_bipado"])
                    lote_str = str(r["lote"]).strip()
                    qtd_str = str(r["quantidade"]).strip()
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
                        value=str(registro_alvo["lote"]),
                        key="adm_novo_lote"
                    )
                    if st.button("💾 Atualizar Lote", use_container_width=True):
                        if novo_lote_input.strip():
                            df_bipes_adm.at[idx_selecionado, "lote"] = novo_lote_input.strip().upper()
                            salvar_dados(df_bipes_adm, "bipes")
                            if "relatorio_final" in st.session_state:
                                del st.session_state.relatorio_final
                            st.success(f"✅ Lote da etiqueta '{registro_alvo['etiqueta']}' atualizado para '{novo_lote_input.strip().upper()}'!")
                            st.rerun()
                        else:
                            st.error("⚠️ O lote não pode ficar em branco.")

                with col_estorno:
                    st.markdown("**2️⃣ Estornar Etiqueta (Mandar Rebipar)**")
                    st.caption("Remove o bipe, abate a quantidade e libera a etiqueta para o conferente bipar novamente.")
                    confirma_estorno_adm = st.checkbox(f"Confirmar estorno da etiqueta '{registro_alvo['etiqueta']}'", key="chk_estorno_adm")
                    if st.button("↩️ Estornar Etiqueta", type="primary", disabled=not confirma_estorno_adm, use_container_width=True):
                        col_alvo_sku = "codigo_vinculado" if "codigo_vinculado" in registro_alvo else "codigo_bipado"
                        sku_estornar = limpar_id(registro_alvo[col_alvo_sku])
                        qtd_estornar = int(registro_alvo["quantidade"])

                        df_cargas_adm = carregar_dados("cargas")
                        filtro_c = (df_cargas_adm["id_carga"] == carga_selecionada) & (df_cargas_adm["codigo"].apply(limpar_id) == sku_estornar)
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
                        st.warning(f"↩️ Etiqueta '{registro_alvo['etiqueta']}' estornada! O conferente já pode bipar novamente.")
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
                "codigo": df_cli[c_cod].apply(limpar_id),
                "informado_cliente": pd.to_numeric(df_cli[c_qtd], errors="coerce").fillna(0).astype(int),
                "lote_cli": df_cli[c_lote].astype(str).str.strip().str.upper() if c_lote != "(Não informar lote)" else "N/I"
            })
            df_cli_prep = df_cli_prep[df_cli_prep["codigo"] != "NAN"]

            base_cli_qtd = df_cli_prep.groupby("codigo", as_index=False)["informado_cliente"].sum()
            base_cli_lotes = df_cli_prep.groupby("codigo")["lote_cli"].apply(
                lambda x: ", ".join(sorted(set(v for v in x if v and v != "NAN")))
            ).reset_index().rename(columns={"lote_cli": "Lotes Cliente"})
            base_cli = pd.merge(base_cli_qtd, base_cli_lotes, on="codigo", how="left")

            df_bipes_all = carregar_dados("bipes")
            if not df_bipes_all.empty and "id_carga" in df_bipes_all.columns:
                bipes_carga = df_bipes_all[df_bipes_all["id_carga"] == carga_selecionada].copy()
                col_sku_bipe = "codigo_vinculado" if "codigo_vinculado" in bipes_carga.columns else "codigo"
                bipes_carga[col_sku_bipe] = bipes_carga[col_sku_bipe].apply(limpar_id)
                bipes_carga["lote"] = bipes_carga["lote"].astype(str).str.strip().str.upper()
                
                lotes_conf = bipes_carga.groupby(col_sku_bipe)["lote"].apply(
                    lambda x: ", ".join(sorted(set(v for v in x if v and v != "NAN")))
                ).reset_index().rename(columns={col_sku_bipe: "codigo", "lote": "Lotes Conferente"})
            else:
                lotes_conf = pd.DataFrame(columns=["codigo", "Lotes Conferente"])

            df_conferencia = df_todas_cargas[df_todas_cargas["id_carga"] == carga_selecionada].copy()
            df_conferencia["codigo"] = df_conferencia["codigo"].apply(limpar_id)
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

                lote_divergente = False
                if c_lote != "(Não informar lote)" and l_conf != "-" and l_cli != "-" and l_conf != l_cli:
                    lote_divergente = True

                if pedido == bipado == cliente:
                    if lote_divergente:
                        return "⚠️ QTD OK, MAS LOTE DIVERGENTE (Conferente x Cliente)"
                    return "✅ CORRETO (100% Validado)"
                elif pedido == bipado and cliente != pedido:
                    return "⚠️ ERRO NO ARQUIVO DO CLIENTE (Pedido e físico batem, cliente informou diferente)"
                elif pedido != cliente and bipado == cliente:
                    return "⚠️ DIVERGÊNCIA NO PEDIDO (Bipado bate com cliente, mas difere do seu pedido)"
                elif pedido == cliente and bipado != cliente:
                    return "❌ DIVERGÊNCIA FÍSICA (Cliente informou igual ao pedido, mas bipagem divergiu)"
                else:
                    return "🚨 DIVERGÊNCIA GERAL (Os três números estão diferentes)"

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
