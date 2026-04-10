import streamlit as st
import pandas as pd

st.set_page_config(page_title="NeuroData", layout="wide")

# =========================
# ESTADO GLOBAL
# =========================

if "dados" not in st.session_state:
    st.session_state["dados"] = []

# =========================
# MENU
# =========================

aba = st.sidebar.selectbox("Menu", ["Cadastro", "Avaliação", "Dataset"])

# =========================
# CADASTRO
# =========================

if aba == "Cadastro":

    st.title("Cadastro do Participante")

    id_participante = st.text_input("ID Participante")
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
    idade_meses = st.number_input("Idade (meses)", min_value=0, max_value=120)

    if st.button("Salvar Cadastro"):

        if id_participante == "":
            st.error("Digite um ID válido")
        else:
            st.session_state["id"] = id_participante
            st.session_state["sexo"] = sexo
            st.session_state["idade_meses"] = idade_meses

            st.success("Cadastro salvo!")

# =========================
# AVALIAÇÃO
# =========================

elif aba == "Avaliação":

    st.title("Avaliação")

    if "id" not in st.session_state:
        st.warning("Faça o cadastro primeiro")
        st.stop()

    st.write(f"Participante: {st.session_state['id']}")

    idade_meses = st.session_state.get("idade_meses", 0)

    # =========================
    # ASQ-SE
    # =========================

    st.subheader("ASQ-SE (Socioemocional)")

    # faixa etária
    if 15 <= idade_meses <= 20:
        faixa = "18 meses"
    elif 21 <= idade_meses <= 26:
        faixa = "24 meses"
    elif 27 <= idade_meses <= 32:
        faixa = "30 meses"
    elif 33 <= idade_meses <= 41:
        faixa = "36 meses"
    elif 42 <= idade_meses <= 53:
        faixa = "48 meses"
    elif 54 <= idade_meses <= 65:
        faixa = "60 meses"
    else:
        faixa = "Fora da faixa"

    st.write(f"Faixa selecionada: {faixa}")

    respostas_asq = []

    for i in range(1, 11):
        r = st.selectbox(
            f"Pergunta {i}",
            ["Na maioria das vezes", "Às vezes", "Raramente/Nunca"],
            key=f"asqse_{i}"
        )
        respostas_asq.append(r)

    if st.button("Calcular ASQ-SE"):

        score = 0

        for r in respostas_asq:
            if r == "Na maioria das vezes":
                score += 0
            elif r == "Às vezes":
                score += 5
            else:
                score += 10

        st.write(f"Score total: {score}")

        if score > 60:
            classificacao = "Risco elevado"
            st.error(classificacao)
        elif score > 40:
            classificacao = "Monitoramento"
            st.warning(classificacao)
        else:
            classificacao = "Adequado"
            st.success(classificacao)

        # salvar resultado
        registro = {
            "id": st.session_state["id"],
            "sexo": st.session_state["sexo"],
            "idade_meses": idade_meses,
            "asq_se_score": score,
            "asq_se_classificacao": classificacao
        }

        st.session_state["dados"].append(registro)

        st.success("Resultado salvo!")

# =========================
# DATASET
# =========================

elif aba == "Dataset":

    st.title("Dados coletados")

    if len(st.session_state["dados"]) == 0:
        st.write("Nenhum dado ainda")
    else:
        df = pd.DataFrame(st.session_state["dados"])
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Baixar CSV",
            csv,
            "dados.csv",
            "text/csv"
        )
