import streamlit as st
import pandas as pd
# ===============================
# LOGIN SIMPLES
# ===============================

def check_login():
    if "logged" not in st.session_state:
        st.session_state["logged"] = False

    if not st.session_state["logged"]:
        st.title("🔐 Login")

        user = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if user == "admin" and password == "1234":
                st.session_state["logged"] = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

        st.stop()

check_login()
import sqlite3
from datetime import date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="NeuroData Research", layout="wide")

# ===============================
# BANCO SQLITE
# ===============================

conn = sqlite3.connect("neurodata.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS participantes (
    id TEXT,
    tempo TEXT,
    idade_meses INTEGER,
    sexo TEXT,
    srs_bruto INTEGER,
    asq_com INTEGER,
    asq_mg INTEGER,
    asq_mf INTEGER,
    asq_res INTEGER,
    asq_soc INTEGER,
    raven_bruto INTEGER,
    cbcl_total INTEGER
)
""")
conn.commit()

# ===============================
# SESSION STATE
# ===============================

if "registro_atual" not in st.session_state:
    st.session_state["registro_atual"] = {}

def selecionar_faixa_asq(idade_meses):
    if 33 <= idade_meses <= 39:
        return "36m"
    elif 45 <= idade_meses <= 51:
        return "48m"
    elif 51 <= idade_meses <= 57:
        return "54m"
    elif 57 <= idade_meses <= 66:
        return "60m"
    else:
        return "fora_da_faixa"
# ===============================
# INTERFACE
# ===============================

st.title("🧠 NeuroData - Sistema de Pesquisa")

aba = st.sidebar.radio("Menu", ["Cadastro", "Avaliação", "Dataset"])

# ===============================
# CADASTRO
# ===============================

if aba == "Cadastro":

    nome = st.text_input("ID Participante")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    nasc = st.date_input("Data de nascimento")

    tempo = st.selectbox("Momento", ["baseline", "36m", "48m", "52m", "60m"])

    if not nome:
        st.warning("Digite um ID válido")
        st.stop()

    idade = relativedelta(date.today(), nasc)
    idade_meses = idade.years * 12 + idade.months

    st.session_state["registro_atual"] = {
        "id": nome,
        "tempo": tempo,
        "idade_meses": idade_meses,
        "sexo": sexo,
        "srs_bruto": None,
        "asq_com": None,
        "asq_mg": None,
        "asq_mf": None,
        "asq_res": None,
        "asq_soc": None,
        "raven_bruto": None,
        "cbcl_total": None
    }

    st.success("Cadastro iniciado")
    st.json(st.session_state["registro_atual"])

# ===============================
# AVALIAÇÃO
# ===============================

elif aba == "Avaliação":

    if not st.session_state["registro_atual"]:
        st.warning("Cadastre primeiro")
        st.stop()
instrumento = st.selectbox("Instrumento", ["SRS-2", "ASQ-3", "Raven", "CBCL"])

    # SRS-2
    if instrumento == "SRS-2":
        respostas = [st.number_input(f"Item {i}", 1, 4, 1, key=f"srs_{i}") for i in range(1,66)]
        bruto = sum([r-1 for r in respostas])
        st.success(f"SRS bruto: {bruto}")

        if st.button("Salvar SRS"):
            st.session_state["registro_atual"]["srs_bruto"] = bruto

    # ASQ-3
  elif instrumento == "ASQ-3":

    faixa_asq = selecionar_faixa_asq(st.session_state["registro_atual"]["idade_meses"])

    st.info(f"📊 ASQ correspondente: {faixa_asq}")

    doms = ["Comunicação","Motor Grosso","Motor Fino","Resolução","Social"]
    resultados = {}

    for d in doms:
        total = 0
            with st.expander(d):
                for i in range(1,7):
                    total += st.radio(f"{d}-{i}", [10,5,0], key=f"{d}_{i}")
            resultados[d] = total

        st.write(resultados)

        if st.button("Salvar ASQ"):
            st.session_state["registro_atual"].update({
                "asq_com": resultados["Comunicação"],
                "asq_mg": resultados["Motor Grosso"],
                "asq_mf": resultados["Motor Fino"],
                "asq_res": resultados["Resolução"],
                "asq_soc": resultados["Social"]
            })

    # Raven
    elif instrumento == "Raven":
        acertos = st.number_input("Acertos", 0, 36, 0)
        if st.button("Salvar Raven"):
            st.session_state["registro_atual"]["raven_bruto"] = acertos

    # CBCL
    elif instrumento == "CBCL":
        total = st.number_input("Total CBCL")
        if st.button("Salvar CBCL"):
            st.session_state["registro_atual"]["cbcl_total"] = total

    st.json(st.session_state["registro_atual"])

    # FINALIZAR PARTICIPANTE
    if st.button("Finalizar Participante"):

        r = st.session_state["registro_atual"]

        # validação
        if None in r.values():
            st.error("Preencha TODOS os instrumentos")
            st.stop()

        # evitar duplicação
        df_ids = pd.read_sql_query("SELECT id, tempo FROM participantes", conn)
        if ((df_ids["id"] == r["id"]) & (df_ids["tempo"] == r["tempo"])).any():
            st.error("Registro já existe para esse participante nesse tempo")
            st.stop()

        cursor.execute("""
        INSERT INTO participantes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(r.values()))

        conn.commit()

        st.session_state["registro_atual"] = {}
        st.success("Participante salvo")

# ===============================
# DATASET
# ===============================

elif aba == "Dataset":

    df = pd.read_sql_query("SELECT * FROM participantes", conn)

    st.dataframe(df)

    st.download_button(
        "Baixar CSV",
        df.to_csv(index=False),
        "dataset.csv",
        "text/csv"
    )
