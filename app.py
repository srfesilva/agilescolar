import streamlit as st
import pandas as pd
from datetime import datetime
import random
import re

# ==============================================================================
# CONFIGURAÇÃO E DESIGN (CSS)
# ==============================================================================
st.set_page_config(page_title="SGDE - Sistema de Gestão Educacional", layout="wide")

# Cores definidas no requisito
COLOR_SIDEBAR_BG = "#ADD8E6" # Azul claro
COLOR_SIDEBAR_TEXT = "#FFFFFF" # Branco
COLOR_MAIN_TEXT = "#000000" # Preto
COLOR_BORDER_BOX = "#ADD8E6" # Azul claro

# CSS Personalizado para injetar no Streamlit
custom_css = f"""
<style>
    /* Sidebar Background e Texto */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_SIDEBAR_BG};
    }}
    section[data-testid="stSidebar"] .css-1d391kg, /* Ajuste para classes dinâmicas do Streamlit */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {{
        color: {COLOR_SIDEBAR_TEXT} !important;
    }}

    /* Main Content Text */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {{
        color: {COLOR_MAIN_TEXT} !important;
    }}

    /* Caixas com borda Azul Claro (Inputs, Selects, etc.) */
    .stTextInput > div > div[data-baseweb="input"],
    .stSelectbox > div > div[data-baseweb="select"],
    .stNumberInput > div > div[data-baseweb="input"],
    .stTextArea > div > div[data-baseweb="textarea"],
    .stDateInput > div > div[data-baseweb="input"] {{
        border-color: {COLOR_BORDER_BOX} !important;
    }}
    
    /* Ajuste fino para focar a borda também */
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: {COLOR_BORDER_BOX} !important;
        box-shadow: 0 0 0 1px {COLOR_BORDER_BOX} !important;
    }

    /* Centralizar a mensagem da Home */
    .home-welcome {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 50vh;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==============================================================================
# ESTADO DA SESSÃO (BANCO DE DADOS EM MEMÓRIA)
# ==============================================================================
# Inicializa listas para armazenar dados enquanto o app está rodando
if 'escola_info' not in st.session_state: st.session_state['escola_info'] = {}
if 'dependencias' not in st.session_state: st.session_state['dependencias'] = []
if 'alunos' not in st.session_state: st.session_state['alunos'] = []
if 'turmas' not in st.session_state: st.session_state['turmas'] = []
if 'matriculas' not in st.session_state: st.session_state['matriculas'] = []

# ==============================================================================
# FUNÇÕES AUXILIARES E REGRAS DE NEGÓCIO
# ==============================================================================
def validar_cnpj(cnpj):
    # Validação simplificada para MVP (apenas numérico e tamanho)
    cnpj_limpo = re.sub(r'\D', '', str(cnpj))
    return len(cnpj_limpo) == 14 and cnpj_limpo.isdigit()

def calcular_capacidade_sala(metragem):
    # Regra: Metragem / 1.2
    if metragem and metragem > 0:
        return int(float(metragem) / 1.2)
    return 0

def gerar_codigo_turma(ano, etapa_cod, sequencial):
    # Padrão XXX.YYY.ZZZ
    xxx = str(ano)[-3:]
    yyy = str(etapa_cod).zfill(3)
    zzz = str(sequencial).zfill(3)
    return f"{xxx}.{yyy}.{zzz}"

def gerar_nra_sequencial():
    # Gera um NRA simples baseado no timestamp e um random para o MVP
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    rand = random.randint(10, 99)
    return f"NRA{timestamp}{rand}"

def validar_idade_etapa(data_nascimento, tipo_etapa):
    # Placeholder para regra de validação etária do MEC.
    # Em produção, isso requer uma tabela complexa de datas de corte.
    if not data_nascimento or not tipo_etapa:
        return False, "Dados incompletos."
    
    hoje = datetime.now().date()
    idade_anos = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    # Exemplo de regra simplificada (DEVE SER SUBSTITUÍDA PELAS REGRAS REAIS DO MEC)
    if "Infantil" in tipo_etapa and idade_anos > 6:
        return False, f"Aluno com {idade_anos} anos. Idade incompatível para Educação Infantil."
    if "Fundamental" in tipo_etapa and idade_anos < 6:
        return False, f"Aluno com {idade_anos} anos. Muito jovem para o Ensino Fundamental."
        
    return True, "Idade compatível."

# ==============================================================================
# MÓDULOS (VIEWS)
# ==============================================================================

def view_home():
    st.markdown('<div class="home-welcome">Seja bem-vindo ao sistema de gestão ágil</div>', unsafe_allow_html=True)

def view_transporte():
    st.title("Transporte Escolar")
    st.info("Módulo em construção. Funcionalidade em Stand-by.")

def view_cadastro_escola():
    st.title("Cadastro de Escola")
    
    tab1, tab2 = st.tabs(["Institucional", "Dependências Físicas"])
    
    # --- 3.2.1 Subsistema Institucional ---
    with tab1:
        st.header("Dados da Instituição")
        with st.form("form_escola_inst"):
            gestor = st.text_input("Gestor Responsável", value=st.session_state['escola_info'].get('gestor',''))
            nome_escola = st.text_input("Nome da Escola", value=st.session_state['escola_info'].get('nome_escola',''))
            razao_social = st.text_input("Razão Social", value=st.session_state['escola_info'].get('razao_social',''))
            cnpj = st.text_input("CNPJ (apenas números)", value=st.session_state['escola_info'].get('cnpj',''), max_chars=14)
            endereco = st.text_area("Endereço Completo", value=st.session_state['escola_info'].get('endereco',''))
            regional = st.selectbox("Unidade Regional", ["Norte", "Sul", "Leste", "Oeste", "Centro"], index=0) # Exemplo
            inep = st.number_input("Cód. INEP", min_value=0, step=1, value=st.session_state['escola_info'].get('inep', 0))
            
            if st.form_submit_button("Salvar Dados Institucionais"):
                if not validar_cnpj(cnpj):
                    st.error("CNPJ Inválido.")
                else:
                    st.session_state['escola_info'] = {
                        'gestor': gestor, 'nome_escola': nome_escola, 'razao_social': razao_social,
                        'cnpj': cnpj, 'endereco': endereco, 'regional': regional, 'inep': inep
                    }
                    st.success("Dados institucionais salvos com sucesso!")

    # --- 3.2.2 Subsistema de Dependências Físicas ---
    with tab2:
        st.header("Cadastrar Sala/Ambiente")
        with st.form("form_dependencia"):
            col1, col2 = st.columns(2)
            with col1:
                dep_nome = st.text_input("Nome da Dependência (Ex: Sala 01)")
                dep_num = st.number_input("Número", min_value=0, max_value=999, step=1)
                dep_clima = st.checkbox("Climatização?")
            with col2:
                dep_metragem = st.number_input("Metragem (m²)", min_value=0.0, format="%.2f", step=0.5)
                # Regra: Capacidade calculada automaticamente
                capacidade_calc = calcular_capacidade_sala(dep_metragem)
                dep_capacidade = st.number_input(f"Capacidade Física Total (Sugerido: {capacidade_calc})", min_value=0, max_value=999, value=capacidade_calc)
                dep_anexo = st.file_uploader("Anexos (Foto ou Planta)", type=["png", "jpg", "jpeg", "pdf"])

            if st.form_submit_button("Adicionar Dependência"):
                if dep_nome and dep_metragem > 0:
                    nova_dep = {
                        'id': len(st.session_state['dependencias']) + 1,
                        'nome': dep_nome, 'numero': dep_num, 'climatizacao': dep_clima,
                        'metragem': dep_metragem, 'capacidade': dep_capacidade,
                        'anexo_nome': dep_anexo.name if dep_anexo else None
                    }
                    st.session_state['dependencias'].append(nova_dep)
                    st.success(f"Dependência '{dep_nome}' adicionada!")
                else:
                    st.warning("Preencha o nome e a metragem corretamente.")
        
        # Exibir dependências cadastradas
        if st.session_state['dependencias']:
            st.subheader("Dependências Cadastradas")
            df_dep = pd.DataFrame(st.session_state['dependencias'])
            st.dataframe(df_dep[['nome', 'numero', 'metragem', 'capacidade', 'climatizacao']])

def view_cadastro_alunos():
    st.title("Cadastro de Alunos")
    
    # --- 3.3.1 Ficha Cadastral Completa ---
    tab_id, tab_docs, tab_familia, tab_saude, tab_funcs = st.tabs([
        "Identificação Pessoal", "Documentação Civil", "Dados Familiares/Contato", "Saúde e Acessibilidade", "Funcionalidades"
    ])

    with st.form("form_aluno_completo"):
        with tab_id:
            st.subheader("Identificação Pessoal")
            nome_completo = st.text_input("Nome Completo *")
            col1, col2 = st.columns(2)
            nome_social = col1.text_input("Nome Social")
            nome_afetivo = col2.text_input("Nome Afetivo")
            col3, col4 = st.columns(2)
            dt_nascimento = col3.date_input("Data de Nascimento *", min_value=datetime(1990, 1, 1))
            sexo = col4.selectbox("Sexo *", ["Masculino", "Feminino"])
            col5, col6 = st.columns(2)
            raca = col5.selectbox("Raça/Cor", ["Não declarado", "Branca", "Preta", "Parda", "Amarela", "Indígena"])
            nacionalidade = col6.text_input("Nacionalidade", value="Brasileira")
            municipio_nasc = st.text_input("Município de Nascimento")

        with tab_docs:
            st.subheader("Documentação Civil")
            ra_aluno = st.text_input("RA (Registro do Aluno) - Formato padrão")
            educacenso = st.text_input("Identificação Única (Educacenso)")
            st.markdown("**RG**")
            col_rg1, col_rg2, col_rg3, col_rg4 = st.columns([2, 1, 2, 1])
            rg_num = col_rg1.text_input("Número RG")
            rg_dig = col_rg2.text_input("Dígito RG")
            rg_emissao = col_rg3.date_input("Data Emissão RG")
            rg_uf = col_rg4.text_input("UF RG", max_chars=2)
            
            st.markdown("**Certidão de Nascimento**")
            col_cert1, col_cert2, col_cert3 = st.columns(3)
            cert_matricula = col_cert1.text_input("Matrícula/Termo")
            cert_livro = col_cert2.text_input("Livro")
            cert_folha = col_cert3.text_input("Folha")
            col_cert4, col_cert5 = st.columns(2)
            cert_comarca = col_cert4.text_input("Comarca")
            cert_distrito = col_cert5.text_input("Distrito")
            
            st.markdown("**Outros**")
            col_out1, col_out2, col_out3 = st.columns(3)
            cpf = col_out1.text_input("CPF")
            nis = col_out2.text_input("NIS")
            sus = col_out3.text_input("Cartão SUS")

        with tab_familia:
            st.subheader("Dados Familiares e Contato")
            col_f1, col_f2 = st.columns(2)
            filiacao1 = col_f1.text_input("Filiação 1")
            filiacao2 = col_f2.text_input("Filiação 2")
            bolsa_familia = st.checkbox("Participação em Bolsa Família?")
            st.markdown("**Endereço Residencial**")
            end_logra = st.text_input("Logradouro")
            col_end1, col_end2, col_end3 = st.columns([1,2,1])
            end_num = col_end1.text_input("Número")
            end_bairro = col_end2.text_input("Bairro")
            end_cep = col_end3.text_input("CEP")
            end_cidade = st.text_input("Cidade")
            st.markdown("**Contato**")
            col_cont1, col_cont2 = st.columns(2)
            telefones = col_cont1.text_input("Telefones")
            email_contato = col_cont2.text_input("E-mail")

        with tab_saude:
            st.subheader("Educação Especial")
            deficiencia = st.checkbox("Estudante com Deficiência?")
            tipo_deficiencia = st.text_input("Tipo de Deficiência") if deficiencia else ""
            tgd_tea = st.text_input("TGD/TEA (Ex: Autista Infantil)") if deficiencia else ""
            nivel_apoio = st.selectbox("Nível de Apoio", ["", "Nível 1", "Nível 2", "Nível 3"]) if deficiencia else ""
            col_s1, col_s2, col_s3 = st.columns(3)
            laudo = col_s1.checkbox("Possui Laudo Médico?") if deficiencia else False
            apoio_prof = col_s2.checkbox("Necessita Profissional de Apoio?") if deficiencia else False
            mobilidade = col_s3.checkbox("Mobilidade Reduzida?") if deficiencia else False

        # Botão de submissão principal do formulário
        submit_aluno = st.form_submit_button("Salvar Ficha do Aluno")
        if submit_aluno:
            if not nome_completo or not dt_nascimento:
                st.error("Campos obrigatórios: Nome Completo e Data de Nascimento.")
            else:
                novo_aluno = {
                    'id': len(st.session_state['alunos']) + 1,
                    'nome_completo': nome_completo, 'dt_nascimento': dt_nascimento,
                    'ra': ra_aluno if ra_aluno else "N/A",
                    # ... (armazenar todos os outros campos aqui)
                    'nra_gerado': None # Será preenchido na outra aba
                }
                st.session_state['alunos'].append(novo_aluno)
                st.success(f"Aluno {nome_completo} cadastrado com sucesso!")

    # --- 3.3.2 Funcionalidades do Aluno ---
    with tab_funcs:
        st.subheader("Ações do Aluno")
        if not st.session_state['alunos']:
            st.warning("Cadastre um aluno primeiro para acessar as funcionalidades.")
        else:
            # Selecionar aluno para ação
            lista_alunos_nomes = [f"{a['id']} - {a['nome_completo']}" for a in st.session_state['alunos']]
            aluno_selecionado_str = st.selectbox("Selecione o Aluno:", lista_alunos_nomes)
            aluno_id = int(aluno_selecionado_str.split(' - ')[0])
            
            # Encontrar o objeto aluno na lista
            aluno_obj = next((a for a in st.session_state['alunos'] if a['id'] == aluno_id), None)

            if aluno_obj:
                st.write(f"Aluno selecionado: **{aluno_obj['nome_completo']}**")
                
                col_btn, col_res = st.columns(2)
                if col_btn.button("Gerar NRA (Número de Registro do Aluno)"):
                    nra = gerar_nra_sequencial()
                    aluno_obj['nra_gerado'] = nra
                    col_res.success(f"NRA Gerado: {nra}")
                
                if aluno_obj.get('nra_gerado'):
                    st.info(f"NRA Atual: {aluno_obj['nra_gerado']}")

                st.subheader("Histórico de Matrículas")
                # Filtrar matrículas deste aluno
                matriculas_aluno = [m for m in st.session_state['matriculas'] if m['aluno_id'] == aluno_id]
                if matriculas_aluno:
                    df_hist = pd.DataFrame(matriculas_aluno)
                    st.dataframe(df_hist[['turma_codigo', 'ano_letivo', 'status_rendimento']])
                else:
                    st.write("Nenhuma matrícula encontrada.")

def view_gestao_turmas():
    st.title("Gestão de Turmas e Matrículas")
    
    tab_turma, tab_matricula = st.tabs(["Cadastro de Turma", "Matrícula (Enturmação)"])

    # --- 3.4.1 Cadastro de Turma ---
    with tab_turma:
        st.header("Nova Turma")
        
        # Verificar se existem dependências físicas cadastradas
        opcoes_dependencias = ["Selecione..."] + [f"{d['id']} - {d['nome']} (Cap: {d['capacidade']})" for d in st.session_state['dependencias']]
        
        with st.form("form_turma"):
            ano_letivo = st.number_input("Ano Letivo", min_value=2024, max_value=2030, value=2025, step=1)
            
            # Códigos fictícios do MEC para o exemplo
            etapas_mec = {
                "101 - Infantil Creche": 101,
                "102 - Infantil Pré-escola": 102,
                "201 - Fundamental Anos Iniciais": 201,
                "202 - Fundamental Anos Finais": 202
            }
            tipo_etapa_label = st.selectbox("Tipo de Etapa (MEC)", list(etapas_mec.keys()))
            etapa_cod = etapas_mec[tipo_etapa_label]
            
            horario_oferta = st.selectbox("Horário da Oferta", ["Manhã", "Tarde", "Noite", "Integral"])
            
            dep_selecionada_str = st.selectbox("Dependência Física (Sala)", opcoes_dependencias)
            
            # Calcular sequencial
            sequencial_sug = len(st.session_state['turmas']) + 1
            
            if st.form_submit_button("Criar Turma"):
                if dep_selecionada_str == "Selecione...":
                    st.error("Selecione uma Dependência Física.")
                else:
                    # Extrair ID da dependência e achar capacidade
                    dep_id = int(dep_selecionada_str.split(' - ')[0])
                    dep_obj = next((d for d in st.session_state['dependencias'] if d['id'] == dep_id), None)
                    capacidade_turma = dep_obj['capacidade'] if dep_obj else 0
                    
                    codigo_turma = gerar_codigo_turma(ano_letivo, etapa_cod, sequencial_sug)
                    
                    nova_turma = {
                        'id': len(st.session_state['turmas']) + 1,
                        'codigo': codigo_turma,
                        'ano_letivo': ano_letivo,
                        'etapa_label': tipo_etapa_label,
                        'horario': horario_oferta,
                        'dependencia_id': dep_id,
                        'capacidade_max': capacidade_turma,
                        'alunos_matriculados': 0
                    }
                    st.session_state['turmas'].append(nova_turma)
                    st.success(f"Turma {codigo_turma} criada com capacidade para {capacidade_turma} alunos!")
        
        # Listar turmas
        if st.session_state['turmas']:
             st.subheader("Turmas Existentes")
             st.dataframe(pd.DataFrame(st.session_state['turmas'])[['codigo', 'etapa_label', 'horario', 'capacidade_max', 'alunos_matriculados']])


    # --- 3.4.2 Matrícula (Enturmação) ---
    with tab_matricula:
        st.header("Enturmação de Alunos")
        
        if not st.session_state['turmas'] or not st.session_state['alunos']:
             st.warning("É necessário cadastrar Alunos e Turmas antes de realizar matrículas.")
        else:
            # Seleção de Turma
            opcoes_turmas = [f"{t['codigo']} - {t['etapa_label']} (Vagas: {t['capacidade_max'] - t['alunos_matriculados']})" for t in st.session_state['turmas']]
            turma_sel_str = st.selectbox("Selecione a Turma Destino", opcoes_turmas)
            turma_codigo = turma_sel_str.split(' - ')[0]
            turma_obj = next((t for t in st.session_state['turmas'] if t['codigo'] == turma_codigo), None)

            st.divider()

            # Busca de Aluno (Simples dropdown para MVP, em prod seria um search box com AJAX)
            st.markdown("**Buscar Aluno para Matrícula**")
            opcoes_alunos_matr = ["Selecione..."] + [f"{a['id']} - {a['nome_completo']} (DN: {a['dt_nascimento']})" for a in st.session_state['alunos']]
            aluno_sel_str = st.selectbox("Selecione o Aluno por Nome/ID", opcoes_alunos_matr)
            
            if aluno_sel_str != "Selecione..." and turma_obj:
                aluno_id = int(aluno_sel_str.split(' - ')[0])
                aluno_obj = next((a for a in st.session_state['alunos'] if a['id'] == aluno_id), None)
                
                # --- Validação Etária (Regra de Negócio) ---
                idade_compativel, msg_validacao = validar_idade_etapa(aluno_obj['dt_nascimento'], turma_obj['etapa_label'])
                
                if not idade_compativel:
                     st.error(f"BLOQUEIO: {msg_validacao}")
                else:
                    st.success(f"Validação: {msg_validacao}")
                    
                    # Verificar capacidade da turma
                    if turma_obj['alunos_matriculados'] >= turma_obj['capacidade_max']:
                        st.warning("Esta turma atingiu a capacidade máxima física.")
                    else:
                        if st.button(f"Confirmar Matrícula de {aluno_obj['nome_completo']} na turma {turma_obj['codigo']}"):
                            # Registrar matrícula
                            nova_matricula = {
                                'id': len(st.session_state['matriculas']) + 1,
                                'aluno_id': aluno_id,
                                'turma_id': turma_obj['id'],
                                'turma_codigo': turma_obj['codigo'],
                                'ano_letivo': turma_obj['ano_letivo'],
                                'data_matricula': datetime.now().date(),
                                'status_rendimento': 'Cursando' # Inicial
                            }
                            st.session_state['matriculas'].append(nova_matricula)
                            
                            # Atualizar contador da turma
                            turma_obj['alunos_matriculados'] += 1
                            st.success("Matrícula realizada com sucesso! A ficha do aluno foi atualizada.")
                            st.rerun()

# ==============================================================================
# NAVEGAÇÃO PRINCIPAL (SIDEBAR)
# ==============================================================================
# Itens do menu conforme Seção 2 e necessidade da Seção 3.4
menu_options = [
    "Página Inicial",
    "Cadastro de Escola",
    "Cadastro de Alunos",
    "Gestão de Turmas", # Adicionado para suportar o requisito 3.4
    "Transporte Escolar"
]

# Sidebar com radio button para navegação
selection = st.sidebar.radio("Navegação SGDE", menu_options)

# Roteamento das views
if selection == "Página Inicial":
    view_home()
elif selection == "Cadastro de Escola":
    view_cadastro_escola()
elif selection == "Cadastro de Alunos":
    view_cadastro_alunos()
elif selection == "Gestão de Turmas":
    view_gestao_turmas()
elif selection == "Transporte Escolar":
    view_transporte()

# --- Rodapé da Sidebar (Opcional) ---
st.sidebar.divider()
st.sidebar.markdown("SGDE v1.0 - 10/02/2026")
