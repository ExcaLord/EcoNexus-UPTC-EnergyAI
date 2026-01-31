import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def load_consumos():
    """Carga datos de consumo energético"""
    return pd.read_csv(RAW_DIR / "consumos_uptc.csv")


def load_sedes():
    """Carga información de sedes"""
    return pd.read_csv(RAW_DIR / "sedes_uptc.csv")
