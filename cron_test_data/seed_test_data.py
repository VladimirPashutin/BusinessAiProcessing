from __future__ import annotations

import csv
from pathlib import Path

import psycopg2 as ps


def _read_csv_rows(path: Path, expected_cols: int) -> list[list[str | None]]:
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = []
        for row in reader:
            if expected_cols is not None and len(row) != expected_cols:
                raise ValueError(
                    f"Unexpected column count in {path.name}: {len(row)} (expected {expected_cols})"
                )
            rows.append([None if value == '' else value for value in row])
        return rows


def debug_seed_test_data(get_connection_string, db_schema_key: str, env) -> str:
    base_dir = Path(__file__).resolve().parent
    org_rows = _read_csv_rows(base_dir / "organization.csv", 33)
    assortment_rows = _read_csv_rows(base_dir / "assortment.csv", 11)
    ass_image_rows = _read_csv_rows(base_dir / "ass_image.csv", 2)

    org_columns = [
        "capital", "defunct", "fend", "fkind", "fstart", "nalog_reg_date", "reg_date", "sel_kind",
        "id", "low_address_id", "post_address_id", "foms", "fss", "inn", "kpp", "low_kladr",
        "nalog_code", "ogrn", "okato", "okdp", "okfs", "okopf", "okpo", "okved", "pfr",
        "post_kladr", "furl", "country", "nalog_name", "strictname", "fullname", "low_address",
        "post_address",
    ]
    assortment_columns = [
        "fmode", "barcode", "id", "issuer_id", "manufacturer", "article", "measure", "ok_code",
        "fname", "trademark", "description",
    ]

    conn = ps.connect(get_connection_string())
    dbSchema = env.get(db_schema_key, "business_ai")
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM " + dbSchema + ".ass_image")
        cursor.execute("DELETE FROM " + dbSchema + ".assortment")
        cursor.execute("DELETE FROM " + dbSchema + ".organization")

        cursor.executemany(
            "INSERT INTO " + dbSchema + ".organization (" + ",".join(org_columns) + ") VALUES (" +
            ",".join(["%s"] * len(org_columns)) + ")",
            org_rows,
        )
        cursor.executemany(
            "INSERT INTO " + dbSchema + ".assortment (" + ",".join(assortment_columns) + ") VALUES (" +
            ",".join(["%s"] * len(assortment_columns)) + ")",
            assortment_rows,
        )
        cursor.executemany(
            "INSERT INTO " + dbSchema + ".ass_image (assortment_id, images) VALUES (%s, %s)",
            ass_image_rows,
        )
    conn.commit()

    return (
        f"Загружено: organization={len(org_rows)}, "
        f"assortment={len(assortment_rows)}, ass_image={len(ass_image_rows)}"
    )
