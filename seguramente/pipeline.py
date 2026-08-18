"""Orquestração ponta a ponta do MVP SeguraMente."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from .llm import LLMProvider, build_provider, generate_message
from .models import PipelineResult, SimulationRecord, utc_now_iso
from .profiles import load_profiles
from .rules import classify_event, evaluate_eligibility
from .weather import OpenMeteoClient


class PipelineError(RuntimeError):
    """Erro controlado do fluxo de negócio."""


def simulate_message(message: Any) -> SimulationRecord:
    """Registra envio simulado; não há chamada a SMS, e-mail ou push."""

    return SimulationRecord(
        simulation_id=f"SIM-{uuid.uuid4().hex[:10].upper()}",
        profile_id=message.profile_id,
        channel=message.channel,
        recipient=message.recipient,
        text=message.text,
        status="SIMULADO — nenhuma comunicação real foi disparada",
        created_at=utc_now_iso(),
    )


def run_pipeline(
    location: str,
    profiles_path: str | Path,
    provider: LLMProvider | None = None,
    client: OpenMeteoClient | None = None,
    approve_simulation: bool = False,
) -> PipelineResult:
    """Executa o fluxo completo com dados meteorológicos ao vivo."""

    started = utc_now_iso()
    weather_client = client or OpenMeteoClient()
    observation = weather_client.observe(location)
    return run_pipeline_from_observation(
        requested_location=location,
        observation=observation,
        profiles_path=profiles_path,
        provider=provider or build_provider("openai"),
        approve_simulation=approve_simulation,
        started_at=started,
    )


def run_pipeline_from_observation(
    requested_location: str,
    observation: Any,
    profiles_path: str | Path,
    provider: LLMProvider,
    approve_simulation: bool = False,
    started_at: str | None = None,
) -> PipelineResult:
    """Executa as etapas de análise usando observação real ou fixture controlada."""

    started = started_at or utc_now_iso()
    event = classify_event(observation)
    profiles = load_profiles(profiles_path)
    decisions = evaluate_eligibility(event, profiles)
    messages = []
    simulations = []
    if event.relevance:
        for decision in decisions:
            if decision.status != "elegivel":
                continue
            message = generate_message(event, decision.profile, provider)
            messages.append(message)
            if approve_simulation:
                simulations.append(simulate_message(message))
    return PipelineResult(
        requested_location=requested_location,
        observation=observation,
        event=event,
        decisions=decisions,
        messages=messages,
        simulations=simulations,
        execution_started_at=started,
        execution_finished_at=utc_now_iso(),
    )
