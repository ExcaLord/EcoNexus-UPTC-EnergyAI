def validate_ranges(df):
    """Valida rangos de ocupación y consumo de agua"""
    df["flag_ocupacion_fuera_rango"] = (df["ocupacion_pct"] < 0) | (
        df["ocupacion_pct"] > 100
    )
    df["flag_agua_fuera_rango"] = df["agua_litros"] < 0
    return df
