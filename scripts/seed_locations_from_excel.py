import argparse
import re
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
    # Usa la hoja indicada o la primera por defecto
    df = pd.read_excel(path, sheet_name=(sheet if sheet is not None else 0))

    cols_lower = {c.lower().strip(): c for c in df.columns}

    # ¿archivo ya con columnas separadas?
    aliases = {
        "place": ("place", "lugar", "sitio"),
        "furniture": ("furniture", "mueble"),
        "module": ("module", "modulo", "m\u00F3dulo", "módulo"),
        "shelf": ("shelf", "estante", "balda"),
    }
    has_all = all(any(a in cols_lower for a in poss) for poss in aliases.values())

    if has_all:
        mapping = {k: next(cols_lower[a] for a in poss if a in cols_lower) for k, poss in aliases.items()}
        df = df.rename(columns={v: k for k, v in mapping.items()})

        def coerce_str(x, maxlen=30):
            if pd.isna(x): return None
            s = str(x).strip()
            return s[:maxlen] if s else None

        def coerce_int(x):
            if pd.isna(x): return None
            s = str(x).strip()
            if not s: return None
            try: return int(float(s))
            except ValueError: raise ValueError(f"Valor no numérico en 'shelf': {x!r}")

        df["place"] = df["place"].apply(coerce_str)
        df["furniture"] = df["furniture"].apply(coerce_str)
        df["module"] = df["module"].apply(coerce_str)
        df["shelf"] = df["shelf"].apply(coerce_int)

    else:
        # Columna única con la ubicación
        # Si no hay columna "Ubicación", usa la única columna disponible
        ubic_col = None
        for name in ("ubicación", "ubicacion", "ubicacion ", "ubicación "):
            if name in cols_lower:
                ubic_col = cols_lower[name]; break
        if not ubic_col:
            if len(df.columns) == 1:
                ubic_col = df.columns[0]
            else:
                raise KeyError("No encuentro columna 'Ubicación' y tampoco columnas separadas.")

        place, furniture, module, shelf = [], [], [], []

        def nz(x, maxlen=30):
            if x is None: return None
            s = str(x).strip()
            return s[:maxlen] if s else None

        mod_re = re.compile(r"(m[oó]dulo|modulo|^m\d+$|^m[_\-\s]?\d+$)", re.IGNORECASE)
        shelf_hint_re = re.compile(r"(balda|estante|shelf)", re.IGNORECASE)

        for raw in df[ubic_col].astype(str):
            parts = [p.strip() for p in raw.split("/") if p.strip()]
            if not parts:
                place.append(None); furniture.append(None); module.append(None); shelf.append(None)
                continue

            p = parts[0]
            rest = parts[1:]

            # 1) Detectar shelf (último tramo si parece balda/estante o tiene dígitos)
            shelf_token = None
            if rest:
                last = rest[-1]
                if shelf_hint_re.search(last) or any(ch.isdigit() for ch in last):
                    shelf_token = last
                    rest = rest[:-1]

            # 2) Detectar module por palabra clave
            module_token = None
            module_idx = None
            for i, t in enumerate(rest):
                if mod_re.search(t):
                    module_token = t
                    module_idx = i
                    break

            # 3) Furniture = lo que queda (si hay módulo, lo anterior al módulo; si no hay módulo, todo el resto)
            if module_token is not None:
                furn_tokens = rest[:module_idx]
            else:
                furn_tokens = rest

            f = " / ".join(furn_tokens) if furn_tokens else None
            m = module_token

            # 4) shelf a número si procede (p. ej., "Balda_4")
            shelf_num = None
            if shelf_token:
                digits = "".join(ch for ch in shelf_token if ch.isdigit())
                shelf_num = int(digits) if digits else None

            place.append(nz(p))
            furniture.append(nz(f))
            module.append(nz(m))
            shelf.append(shelf_num)

        df = pd.DataFrame({"place": place, "furniture": furniture, "module": module, "shelf": shelf})

        # limpiar y deduplicar
        df = df.dropna(how="all", subset=["place", "furniture", "module", "shelf"])
        df = df.drop_duplicates(subset=["place", "furniture", "module", "shelf"])
        return df

def exists(session, place, furniture, module, shelf):
    stmt = (
        select(func.count())
        .select_from(Location)
        .where(
            and_(
                Location.place.is_(place) if place is None else Location.place == place,
                Location.furniture.is_(furniture) if furniture is None else Location.furniture == furniture,
                Location.module.is_(module) if module is None else Location.module == module,
                Location.shelf.is_(shelf) if shelf is None else Location.shelf == shelf,
            )
        )
    )
    return session.execute(stmt).scalar_one() > 0

def insert_locations(path, sheet=None, dry=False):
    df = load_df(path, sheet)
    to_insert = df.to_dict(orient="records")
    inserted, skipped = 0, 0
    with SessionLocal() as s:
        try:
            for row in to_insert:
                if exists(s, row["place"], row["furniture"], row["module"], row["shelf"]):
                    skipped += 1
                    continue
                if dry:
                    print("[DRY] Insertaría:", row)
                    inserted += 1
                else:
                    s.add(Location(**row))
                    inserted += 1
            if not dry:
                s.commit()
        except Exception:
            s.rollback()
            raise
    return inserted, skipped, len(to_insert)

def main():
    p = argparse.ArgumentParser(description="Seed of locations from Excel")
    p.add_argument("excel", help="Root to .xlsx (e.x., ubicacion.xlsx)")
    p.add_argument("--sheet", help="Sheet's name (optional)", default=None)
    p.add_argument("--dry-run", action="store_true", help="Doesn't insert; Only shows")
    args = p.parse_args()

    ins, skp, total = insert_locations(args.excel, args.sheet, args.dry_run)
    mode = "DRY-RUN" if args.dry_run else "INSERT"
    print(f"[{mode}] Total filas leídas: {total} | Nuevas: {ins} | Duplicadas/omitidas: {skp}")

if __name__ == "__main__":
    main()