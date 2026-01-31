import argparse
import re
import pandas as pd
from database.db_config import SessionLocal
from models.location import Location

LIBRARY_ID = 2  # Iglesias-Hurtado


def normalize_text(x, maxlen=30):
    """Convierte '', 'nan', NaN, None -> None. Si hay texto, lo recorta."""
    if x is None:
        return None
    # pandas/numpy NaN
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    s = str(x).strip()
    if s == "" or s.lower() in ("nan", "none", "null"):
        return None
    return s[:maxlen]


def parse_locations_csv(path: str) -> list[dict]:
    df = pd.read_csv(path)
    cols_lower = {c.lower().strip(): c for c in df.columns}

    ubic_col = None
    for name in ("ubicación", "ubicacion", "location", "ubicacionih", "ubicacion_ih"):
        if name in cols_lower:
            ubic_col = cols_lower[name]
            break

    if not ubic_col:
        if len(df.columns) == 1:
            ubic_col = df.columns[0]
        else:
            raise KeyError("No encuentro columna de ubicación (Ubicacion/Ubicación).")

    mod_re = re.compile(r"(m[oó]dulo|modulo|^m\d+$|^m[_\-\s]?\d+$|^m[oó]dulo[_\-\s]?\d+$)", re.IGNORECASE)
    shelf_hint_re = re.compile(r"(balda|estante|shelf)", re.IGNORECASE)

    out = []
    for raw in df[ubic_col].astype(str):
        raw = raw.strip()
        if raw == "" or raw.lower() in ("nan", "none", "null"):
            continue

        parts = [p.strip() for p in raw.split("/") if p.strip()]
        if not parts:
            continue

        place = parts[0]
        rest = parts[1:]

        # shelf = último tramo si tiene dígitos o "balda/estante"
        shelf_token = None
        if rest:
            last = rest[-1]
            if shelf_hint_re.search(last) or any(ch.isdigit() for ch in last):
                shelf_token = last
                rest = rest[:-1]

        # module = primer token que parezca módulo
        module_token = None
        module_idx = None
        for i, t in enumerate(rest):
            if mod_re.search(t):
                module_token = t
                module_idx = i
                break

        # furniture = lo que quede antes del módulo (o todo si no hay módulo)
        furn_tokens = rest[:module_idx] if module_token is not None else rest
        furniture = " / ".join(furn_tokens) if furn_tokens else None

        # shelf a int
        shelf_num = None
        if shelf_token:
            digits = "".join(ch for ch in shelf_token if ch.isdigit())
            shelf_num = int(digits) if digits else None

        row = {
            "place": normalize_text(place),
            "furniture": normalize_text(furniture),
            "module": normalize_text(module_token),
            "shelf": shelf_num,
        }

        # descarta fila completamente vacía
        if all(v is None for v in row.values()):
            continue

        out.append(row)

    # dedupe en memoria
    seen = set()
    uniq = []
    for r in out:
        key = (r["place"], r["furniture"], r["module"], r["shelf"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)

    return uniq


def load_existing_keys(session) -> set:
    """Carga keys existentes SOLO de library_id=2 en memoria."""
    rows = (
        session.query(Location.place, Location.furniture, Location.module, Location.shelf)
        .filter(Location.library_id == LIBRARY_ID)
        .all()
    )
    return set((p, f, m, s) for (p, f, m, s) in rows)


def insert_locations(path: str, dry: bool = False):
    to_insert = parse_locations_csv(path)

    inserted, skipped = 0, 0
    with SessionLocal() as s:
        try:
            existing = load_existing_keys(s)

            for r in to_insert:
                key = (r["place"], r["furniture"], r["module"], r["shelf"])
                if key in existing:
                    skipped += 1
                    continue

                payload = {
                    "library_id": LIBRARY_ID,
                    "place": r["place"],
                    "furniture": r["furniture"],
                    "module": r["module"],
                    "shelf": r["shelf"],
                }

                if dry:
                    print("[DRY] Insertaría:", payload)
                    inserted += 1
                else:
                    s.add(Location(**payload))
                    inserted += 1
                    existing.add(key)  # evita duplicados dentro de la misma ejecución

            if not dry:
                s.commit()

        except Exception:
            s.rollback()
            raise

    return inserted, skipped, len(to_insert)


def main():
    p = argparse.ArgumentParser(description="Seed locations from CSV into locations (library_id=2)")
    p.add_argument("csv", help="Ruta a .csv (ej: ubicacionIH.csv)")
    p.add_argument("--dry-run", action="store_true", help="No inserta; solo muestra")
    args = p.parse_args()

    ins, skp, total = insert_locations(args.csv, args.dry_run)
    mode = "DRY-RUN" if args.dry_run else "INSERT"
    print(f"[{mode}] Total filas procesadas: {total} | Nuevas: {ins} | Duplicadas/omitidas: {skp}")


if __name__ == "__main__":
    main()
