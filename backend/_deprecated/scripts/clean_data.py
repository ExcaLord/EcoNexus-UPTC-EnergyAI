import pandas as pd
import numpy as np


def normalize_periodo_academico(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "semestre_1": "SEM_1",
        "SEMESTRE_1": "SEM_1",
        "Semestre_1": "SEM_1",
        "semestre1": "SEM_1",
        "semestre_2": "SEM_2",
        "SEMESTRE_2": "SEM_2",
        "Semestre_2": "SEM_2",
        "semestre2": "SEM_2",
        "vacaciones": "VAC_FIN",
        "vacaciones_fin": "VAC_FIN",
        "vacaciones_mitad": "VAC_MITAD",
    }

    df["periodo_academico"] = df["periodo_academico"].map(mapping).fillna("UNKNOWN")
    return df


def fix_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hora"] = df["timestamp"].dt.hour
    df["dia_semana"] = df["timestamp"].dt.dayofweek
    df["mes"] = df["timestamp"].dt.month
    df["año"] = df["timestamp"].dt.year
    return df


SECTORES = [
    "energia_comedor_kwh",
    "energia_salones_kwh",
    "energia_laboratorios_kwh",
    "energia_auditorios_kwh",
    "energia_oficinas_kwh",
]


def recal_energia_total(df: pd.DataFrame) -> pd.DataFrame:
    df[SECTORES] = df[SECTORES].fillna(0)

    df["energia_total_calc_kwh"] = df[SECTORES].sum(axis=1)

    df["energia_total_inconsistente"] = (
        df["energia_total_kwh"] - df["energia_total_calc_kwh"]
    ).abs() > 0

    df["energia_total_kwh"] = df["energia_total_calc_kwh"]

    return df
