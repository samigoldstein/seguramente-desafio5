"""Carga e validação da base sintética de perfis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import InsuredProfile

REQUIRED_COLUMNS = {
    "profile_id",
    "name",
    "city",
    "state",
    "product",
    "channel",
    "consent",
    "contact",
}


def load_profiles(path: str | Path) -> list[InsuredProfile]:
    """Carrega perfis sintéticos do CSV e valida campos obrigatórios."""

    dataframe = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")
    profiles: list[InsuredProfile] = []
    for row in dataframe.to_dict(orient="records"):
        profiles.append(
            InsuredProfile(
                profile_id=str(row["profile_id"]),
                name=str(row["name"]),
                city=str(row["city"]),
                state=str(row["state"]),
                product=str(row["product"]).strip().lower(),
                channel=str(row["channel"]).strip().lower(),
                consent=_as_bool(row["consent"]),
                contact=str(row["contact"]),
            )
        )
    return profiles


def _as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "sim", "yes", "ativo"}
