"""Fixtures determinísticas para demonstração e testes sem depender da rede."""

from seguramente.models import WeatherObservation


def chuva_intensa_sao_paulo() -> WeatherObservation:
    return WeatherObservation(
        source="Open-Meteo (fixture demonstrativa)",
        source_url="https://open-meteo.com/en/docs",
        location="São Paulo, São Paulo, Brasil",
        latitude=-23.55,
        longitude=-46.63,
        observed_at="2026-08-18T12:00",
        temperature_c=20.4,
        precipitation_mm=18.0,
        wind_speed_kmh=22.0,
        wind_gust_kmh=34.0,
        precipitation_probability=82,
        weather_code=63,
        raw={"fixture": True, "scenario": "chuva_intensa"},
    )


def granizo_sao_paulo() -> WeatherObservation:
    return WeatherObservation(
        source="Open-Meteo (fixture demonstrativa)",
        source_url="https://open-meteo.com/en/docs",
        location="São Paulo, São Paulo, Brasil",
        latitude=-23.55,
        longitude=-46.63,
        observed_at="2026-08-18T12:00",
        temperature_c=19.1,
        precipitation_mm=12.0,
        wind_speed_kmh=35.0,
        wind_gust_kmh=55.0,
        precipitation_probability=90,
        weather_code=96,
        raw={"fixture": True, "scenario": "granizo"},
    )


def ventos_fortes_sao_paulo() -> WeatherObservation:
    return WeatherObservation(
        source="Open-Meteo (fixture demonstrativa)",
        source_url="https://open-meteo.com/en/docs",
        location="São Paulo, São Paulo, Brasil",
        latitude=-23.55,
        longitude=-46.63,
        observed_at="2026-08-18T12:00",
        temperature_c=24.0,
        precipitation_mm=1.0,
        wind_speed_kmh=48.0,
        wind_gust_kmh=72.0,
        precipitation_probability=20,
        weather_code=3,
        raw={"fixture": True, "scenario": "ventos_fortes"},
    )


def alagamento_sao_paulo() -> WeatherObservation:
    return WeatherObservation(
        source="Open-Meteo (fixture demonstrativa)",
        source_url="https://open-meteo.com/en/docs",
        location="São Paulo, São Paulo, Brasil",
        latitude=-23.55,
        longitude=-46.63,
        observed_at="2026-08-18T12:00",
        temperature_c=19.0,
        precipitation_mm=35.0,
        wind_speed_kmh=20.0,
        wind_gust_kmh=32.0,
        precipitation_probability=95,
        weather_code=65,
        raw={"fixture": True, "scenario": "alagamento"},
    )


FIXTURES = {
    "chuva_intensa": chuva_intensa_sao_paulo,
    "granizo": granizo_sao_paulo,
    "ventos_fortes": ventos_fortes_sao_paulo,
    "alagamento": alagamento_sao_paulo,
}
