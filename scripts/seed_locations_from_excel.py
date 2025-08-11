import argparse
import pandas as pd
from sqlalchemy import select, and_, func
from database.db_config import SessionLocal
from models.location import Location

def coerce_str(x, maxlen=30):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    return s[:maxlen] if s else None

def coerce_int(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    if s == "":
        return None
    try:
        return int(float(s))
    except ValueError:
        raise ValueError(f"Valor no numérico en 'shelf': {x!r}")

def load_df(path, sheet=None):
    df = pd.read_excel(path, sheet_name=sheet)

    cols = {c.lower().strip(): c for c in df.columns}
    needed = ("place", "furniture", "module", "shelf")

    aliases = {
        "place": ("place", "lugar", "sitio"),
        "furniture": ("furniture", "mueble"),
        "module": ("module", "modulo", "módulo"),
        "shelf": ("shelf", "estante", "balda")
    }

    mapping = {}
    for k, poss in aliases.items():
        found = next((cols[c] for c in cols if c in poss), None)
        if not found:
            raise KeyError(f"Columna '{k}' no encontrada. Esperaba una de {poss}.")
        mapping[k] = found
    df = df.rename(columns={v: k for k, v in mapping.items()})
    # Normaliza
    df["place"] = df["place"].apply(coerce_str)
    df["furniture"] = df["furniture"].apply(coerce_str)
    df["module"] = df["module"].apply(coerce_str)
    df["shelf"] = df["shelf"].apply(coerce_int)
    # Elimina filas totalmente vacías
    df = df.dropna(how="all", subset=["place", "furniture", "module", "shelf"])
    # Dedup en memoria
    df = df.drop_duplicates(subset=["place", "furniture", "module", "shelf"])
    return df