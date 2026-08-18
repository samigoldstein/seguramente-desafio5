"""Interface Streamlit do SeguraMente."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fixtures import FIXTURES  # noqa: E402
from seguramente.llm import build_provider  # noqa: E402
from seguramente.pipeline import run_pipeline, run_pipeline_from_observation, simulate_message  # noqa: E402

PROFILES_PATH = ROOT / "data" / "insured_profiles.csv"

st.set_page_config(page_title="SeguraMente", page_icon="", layout="wide")
st.title("SeguraMente")
st.caption("MVP de comunicação proativa com o segurado — Desafio 5 InsurMinds")

with st.sidebar:
    st.header("Configuração da execução")
    execution_mode = st.radio("Fonte meteorológica", ["Demonstração reproduzível", "API ao vivo"])
    provider_mode = st.radio(
        "Gerador de mensagens",
        ["openai", "template"],
        help="OpenAI usa o modelo configurado por OPENAI_API_KEY. Template é somente para demonstração offline e testes.",
    )
    if execution_mode == "Demonstração reproduzível":
        scenario = st.selectbox("Cenário", list(FIXTURES.keys()))
    else:
        location = st.text_input("Localidade", value="São Paulo")
    st.divider()
    st.info("Nenhuma comunicação real é disparada. Todos os perfis são sintéticos.")

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("Executar fluxo completo", type="primary"):
    try:
        provider = build_provider(provider_mode)
        if execution_mode == "Demonstração reproduzível":
            observation = FIXTURES[scenario]()
            st.session_state.result = run_pipeline_from_observation(
                requested_location=observation.location,
                observation=observation,
                profiles_path=PROFILES_PATH,
                provider=provider,
                approve_simulation=False,
            )
        else:
            if not location.strip():
                st.error("Informe uma localidade.")
                st.stop()
            st.session_state.result = run_pipeline(
                location=location,
                profiles_path=PROFILES_PATH,
                provider=provider,
                approve_simulation=False,
            )
        st.success("Fluxo executado até a etapa de revisão humana.")
    except Exception as exc:  # pragma: no cover - camada visual
        st.error(str(exc))

result = st.session_state.result
if result is None:
    st.markdown(
        """
        ### Como demonstrar

        Selecione um cenário reproduzível ou uma localidade real, escolha o
        gerador, execute o fluxo e revise as decisões. Após a revisão, registre
        a simulação para gerar o histórico sem disparar mensagens.
        """
    )
    st.stop()

st.header("1. Coleta e normalização")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Fonte", result.observation.source)
col2.metric("Localidade", result.observation.location)
col3.metric("Observado em", result.observation.observed_at)
col4.metric("Precipitação", f"{result.observation.precipitation_mm or 0:.1f} mm")

st.json(
    {
        "source_url": result.observation.source_url,
        "latitude": result.observation.latitude,
        "longitude": result.observation.longitude,
        "temperature_c": result.observation.temperature_c,
        "wind_gust_kmh": result.observation.wind_gust_kmh,
        "precipitation_probability": result.observation.precipitation_probability,
        "weather_code": result.observation.weather_code,
    }
)

st.header("2. Classificação automática do evento")
st.write(f"**Tipo:** {result.event.event_type.replace('_', ' ').title()}")
st.write(f"**Severidade:** {result.event.severity.title()}  ")
st.write(f"**Relevância:** {'Sim' if result.event.relevance else 'Não'}  ")
st.write(f"**Justificativa:** {result.event.justification}")
st.json(result.event.indicators)

st.header("3. Regras de negócio e elegibilidade")
decisions_df = pd.DataFrame(
    [
        {
            "Perfil": decision.profile.name,
            "Produto": decision.profile.product,
            "Canal": decision.profile.channel,
            "Consentimento": "Ativo" if decision.profile.consent else "Inativo",
            "Status": decision.status,
            "Motivo": "; ".join(decision.reasons),
        }
        for decision in result.decisions
    ]
)
st.dataframe(decisions_df, use_container_width=True, hide_index=True)

st.header("4. Mensagens geradas para revisão humana")
if not result.messages:
    st.warning("Nenhuma mensagem foi gerada: evento irrelevante ou todos os perfis foram bloqueados.")
else:
    for index, message in enumerate(result.messages, start=1):
        with st.container(border=True):
            st.write(f"**Mensagem {index} — {message.channel.upper()} — {message.recipient}**")
            st.write(message.text)
            st.caption(f"Provider: {message.provider} | Modelo: {message.model} | Gerada em: {message.generated_at}")

    st.divider()
    st.subheader("Revisão humana")
    approved = st.checkbox("Confirmo que revisei as mensagens e desejo apenas registrar uma simulação.")
    if st.button("Registrar envio simulado", disabled=not approved):
        result.simulations = [simulate_message(message) for message in result.messages]
        st.success("Simulação registrada. Nenhum canal externo foi acionado.")

st.header("5. Histórico da simulação")
if result.simulations:
    simulations_df = pd.DataFrame(
        [
            {
                "ID": simulation.simulation_id,
                "Perfil": simulation.profile_id,
                "Canal": simulation.channel,
                "Destinatário sintético": simulation.recipient,
                "Status": simulation.status,
                "Criado em": simulation.created_at,
            }
            for simulation in result.simulations
        ]
    )
    st.dataframe(simulations_df, use_container_width=True, hide_index=True)
else:
    st.info("A simulação ainda não foi registrada; a revisão humana é obrigatória.")
