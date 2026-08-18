from pathlib import Path

import pytest

from fixtures import chuva_intensa_sao_paulo, granizo_sao_paulo, ventos_fortes_sao_paulo
from seguramente.llm import LLMGenerationError, TemplateProvider, validate_message
from seguramente.pipeline import run_pipeline_from_observation
from seguramente.rules import classify_event, evaluate_eligibility
from seguramente.profiles import load_profiles

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data" / "insured_profiles.csv"


def test_classifica_chuva_intensa_por_limiar():
    event = classify_event(chuva_intensa_sao_paulo())
    assert event.event_type == "chuva_intensa"
    assert event.relevance is True
    assert event.severity == "moderada"


def test_classifica_granizo_por_codigo_wmo():
    event = classify_event(granizo_sao_paulo())
    assert event.event_type == "granizo"
    assert event.severity == "alta"


def test_classifica_vento_forte_por_rajada():
    event = classify_event(ventos_fortes_sao_paulo())
    assert event.event_type == "ventos_fortes"
    assert event.relevance is True


def test_bloqueia_sem_consentimento_e_produto_incompativel():
    event = classify_event(chuva_intensa_sao_paulo())
    decisions = evaluate_eligibility(event, load_profiles(PROFILES))
    by_id = {decision.profile.profile_id: decision for decision in decisions}
    assert by_id["P001"].status == "elegivel"
    assert by_id["P005"].status == "bloqueado"
    assert "consentimento inativo" in by_id["P005"].reasons
    assert by_id["P007"].status == "bloqueado"
    assert "produto sem relação com o evento" in by_id["P007"].reasons


def test_guardrail_rejeita_promessa_de_cobertura():
    with pytest.raises(LLMGenerationError):
        validate_message("Sua cobertura garantida está confirmada.")


def test_guardrail_aceita_mensagem_preventiva():
    text = validate_message("Olá. Recolha objetos soltos e acompanhe os comunicados oficiais.")
    assert text.startswith("Olá")


def test_fluxo_completo_gera_mensagem_e_simulacao():
    observation = chuva_intensa_sao_paulo()
    result = run_pipeline_from_observation(
        requested_location=observation.location,
        observation=observation,
        profiles_path=PROFILES,
        provider=TemplateProvider(),
        approve_simulation=True,
    )
    assert result.event.relevance is True
    assert len(result.messages) >= 1
    assert len(result.simulations) == len(result.messages)
    assert all("nenhuma comunicação real" in item.status for item in result.simulations)
