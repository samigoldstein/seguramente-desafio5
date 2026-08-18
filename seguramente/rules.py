"""Regras determinísticas de eventos e elegibilidade."""

from __future__ import annotations

from collections.abc import Iterable

from .models import EligibilityDecision, InsuredProfile, WeatherEvent, WeatherObservation

PRODUCTS_BY_EVENT: dict[str, set[str]] = {
    "chuva_intensa": {"residencial", "empresarial"},
    "granizo": {"automovel", "residencial"},
    "ventos_fortes": {"residencial", "empresarial", "automovel"},
    "alagamento": {"residencial", "empresarial"},
}

CHANNELS: set[str] = {"email", "sms", "push"}


def classify_event(observation: WeatherObservation) -> WeatherEvent:
    """Classifica a observação com limiares documentados e reproduzíveis.

    Limiares do MVP:
    - granizo: código WMO 96 ou 99;
    - alagamento: precipitação atual >= 30 mm;
    - chuva intensa: precipitação atual >= 10 mm ou probabilidade >= 70%;
    - ventos fortes: rajada >= 60 km/h.

    Quando mais de uma regra se aplica, a ordem acima prioriza o risco mais
    específico ou severo para manter uma única decisão principal.
    """

    rain = observation.precipitation_mm or 0.0
    gust = observation.wind_gust_kmh or 0.0
    probability = observation.precipitation_probability or 0
    code = observation.weather_code
    indicators = {
        "precipitation_mm": rain,
        "precipitation_probability": probability,
        "wind_gust_kmh": gust,
        "weather_code": code,
    }

    if code in {96, 99}:
        return WeatherEvent(
            event_type="granizo",
            severity="alta",
            relevance=True,
            justification="Código meteorológico WMO 96/99 indica trovoada com granizo.",
            indicators=indicators,
        )
    if rain >= 30:
        return WeatherEvent(
            event_type="alagamento",
            severity="critica",
            relevance=True,
            justification="Precipitação atual igual ou superior a 30 mm indica risco elevado de alagamento.",
            indicators=indicators,
        )
    if gust >= 60:
        return WeatherEvent(
            event_type="ventos_fortes",
            severity="alta",
            relevance=True,
            justification="Rajada de vento igual ou superior a 60 km/h supera o limiar preventivo.",
            indicators=indicators,
        )
    if rain >= 10 or probability >= 70:
        return WeatherEvent(
            event_type="chuva_intensa",
            severity="moderada",
            relevance=True,
            justification="Precipitação atual igual ou superior a 10 mm ou probabilidade igual ou superior a 70%.",
            indicators=indicators,
        )
    return WeatherEvent(
        event_type="sem_evento_relevante",
        severity="baixa",
        relevance=False,
        justification="Nenhum indicador ultrapassou os limiares de comunicação preventiva.",
        indicators=indicators,
    )


def evaluate_eligibility(
    event: WeatherEvent,
    profiles: Iterable[InsuredProfile],
) -> list[EligibilityDecision]:
    """Aplica regras explicáveis e retorna aprovados e bloqueados."""

    decisions: list[EligibilityDecision] = []
    allowed_products = PRODUCTS_BY_EVENT.get(event.event_type, set())
    for profile in profiles:
        reasons: list[str] = []
        if not event.relevance:
            reasons.append("evento abaixo do limiar de relevância")
        if not profile.consent:
            reasons.append("consentimento inativo")
        if profile.channel not in CHANNELS:
            reasons.append("canal não suportado")
        if profile.product not in allowed_products:
            reasons.append("produto sem relação com o evento")
        if not profile.contact.strip():
            reasons.append("contato ausente para o canal selecionado")
        if not reasons:
            reasons.append("localidade, produto, consentimento e canal compatíveis")
            status = "elegivel"
        else:
            status = "bloqueado"
        decisions.append(EligibilityDecision(profile=profile, status=status, reasons=tuple(reasons)))
    return decisions
