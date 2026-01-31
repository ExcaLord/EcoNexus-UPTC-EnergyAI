from src.load_data import load_consumos
from src.clean_data import normalize_periodo_academico, fix_timestamp, recal_energia_total
from src.validate_data import validate_ranges
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
CLEAN_DIR = BASE_DIR / "data" / "clean"


def main():
    df = load_consumos()
    df = normalize_periodo_academico(df)
    df = fix_timestamp(df)
    df = recal_energia_total(df)
    df = validate_ranges(df)

    CLEAN_DIR.mkdir(exist_ok=True)
    df.to_csv(CLEAN_DIR / "consumos_uptc_clean.csv", index=False)
    print("✅ Datos limpios generados correctamente")


if __name__ == "__main__":
    main()
