"""Back up and verify the additive UI migration; default mode never migrates.

Run without flags for a read-only preflight. Use --apply only when the integrated
checks have passed. --database accepts an existing copy for a rehearsal. This
script does not seed data, contact payment providers or run post_migrate hooks.
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import struct
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
TARGET = ("commerce", "0003_invoice_return_lesson")
COLUMN = "return_lesson_id"


class MigrationSafetyError(RuntimeError):
    pass


def quoted(identifier):
    return '"' + identifier.replace('"', '""') + '"'


def rows_digest(database, table, columns, exclude_id=None):
    # CASE expressions bypass Django's date/bool converters and hash the exact
    # SQLite storage values consistently on Django and plain backup connections.
    column_sql = ", ".join(
        f"typeof({quoted(column)}), CASE WHEN typeof({quoted(column)})='text' "
        f"THEN CAST({quoted(column)} AS BLOB) ELSE {quoted(column)} END"
        for column in columns
    )
    info = database.execute(f"PRAGMA table_info({quoted(table)})").fetchall()
    order = [row[1] for row in sorted(info, key=lambda row: row[5]) if row[5]] or columns
    query = f"SELECT {column_sql} FROM {quoted(table)}"
    parameters = ()
    if exclude_id is not None:
        query += ' WHERE "id" != ?'
        parameters = (exclude_id,)
    query += " ORDER BY " + ", ".join(quoted(column) for column in order)
    digest = hashlib.sha256()
    count = 0
    for row in database.execute(query, parameters):
        digest.update(b"row\x00")
        for index in range(0, len(row), 2):
            storage_type, value = row[index:index + 2]
            if value is None:
                kind, data = b"null", b""
            elif isinstance(value, bytes):
                kind, data = storage_type.encode("ascii"), value
            elif isinstance(value, int):
                kind, data = b"int", str(value).encode("ascii")
            elif isinstance(value, float):
                kind, data = b"float", struct.pack(">d", value)
            else:
                kind, data = b"text", value.encode("utf-8")
            digest.update(kind + b"\x00" + len(data).to_bytes(8, "big") + data)
        count += 1
    return {"rows": count, "sha256": digest.hexdigest()}


def snapshot(database):
    objects = {(row[0], row[1]): {"table": row[2], "sql": row[3]} for row in database.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
    )}
    tables = {}
    for kind, name in objects:
        if kind != "table":
            continue
        info = database.execute(f"PRAGMA table_info({quoted(name)})").fetchall()
        columns = [row[1] for row in info]
        tables[name] = {"columns": columns, "definitions": [tuple(row[1:]) for row in info],
                        **rows_digest(database, name, columns)}
    return {"objects": objects, "tables": tables,
            "invoice_foreign_keys": [tuple(row[2:]) for row in database.execute('PRAGMA foreign_key_list("commerce_invoice")')],
            "migration_ids": {row[0] for row in database.execute('SELECT id FROM django_migrations')},
            "sequences": dict(database.execute('SELECT name, seq FROM sqlite_sequence'))}


def check_integrity(database):
    if database.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise MigrationSafetyError("La comprobación de integridad SQLite no pasó.")
    if database.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise MigrationSafetyError("La comprobación de claves foráneas no pasó.")


def verify_changes(database, before):
    after = snapshot(database)
    if set(before["tables"]) != set(after["tables"]):
        raise MigrationSafetyError("La migración cambió el conjunto de tablas.")
    new_ids = after["migration_ids"] - before["migration_ids"]
    if len(new_ids) != 1 or before["migration_ids"] - after["migration_ids"]:
        raise MigrationSafetyError("El historial de migraciones contiene cambios inesperados.")
    new_id = next(iter(new_ids))
    record = database.execute("SELECT app, name, applied FROM django_migrations WHERE id=?", (new_id,)).fetchone()
    if record[:2] != TARGET or not record[2]:
        raise MigrationSafetyError("El nuevo registro no corresponde a la migración autorizada.")
    expected_sequences = dict(before["sequences"])
    expected_sequences["django_migrations"] = new_id
    if new_id != before["sequences"]["django_migrations"] + 1 or after["sequences"] != expected_sequences:
        raise MigrationSafetyError("Los contadores SQLite cambiaron fuera del registro de migración.")
    for table, values in before["tables"].items():
        if table == "sqlite_sequence":
            continue
        old_columns = values["columns"]
        definitions = after["tables"][table]["definitions"]
        original_definitions = [item for item in definitions if item[0] in old_columns]
        if original_definitions != values["definitions"]:
            raise MigrationSafetyError(f"Cambió una definición previa de {table}.")
        expected_columns = old_columns + ([COLUMN] if table == "commerce_invoice" else [])
        if after["tables"][table]["columns"] != expected_columns:
            raise MigrationSafetyError(f"Cambió una columna fuera de lo permitido en {table}.")
        actual = rows_digest(database, table, old_columns, new_id if table == "django_migrations" else None)
        if actual != {"rows": values["rows"], "sha256": values["sha256"]}:
            raise MigrationSafetyError(f"Los datos históricos de {table} no conservaron su huella.")
    added = after["tables"]["commerce_invoice"]["definitions"][-1]
    if added[0] != COLUMN or added[1].lower() != "bigint" or added[2:] != (0, None, 0):
        raise MigrationSafetyError("La nueva columna no tiene la definición nullable esperada.")
    if database.execute(f'SELECT COUNT(*) FROM commerce_invoice WHERE "{COLUMN}" IS NOT NULL').fetchone()[0]:
        raise MigrationSafetyError("Se asignó un destino a una factura histórica.")
    old_foreign_keys = sorted(before["invoice_foreign_keys"])
    expected_foreign_keys = sorted(old_foreign_keys + [("content_versionlesson", COLUMN, "id", "NO ACTION", "NO ACTION", "NONE")])
    if sorted(after["invoice_foreign_keys"]) != expected_foreign_keys:
        raise MigrationSafetyError("Cambió una relación de factura fuera de lo permitido.")
    old_objects, new_objects = before["objects"], after["objects"]
    if old_objects.keys() - new_objects.keys():
        raise MigrationSafetyError("Desapareció un objeto del esquema SQLite.")
    for key, value in old_objects.items():
        if key != ("table", "commerce_invoice") and new_objects[key] != value:
            raise MigrationSafetyError("Cambió un objeto previo del esquema SQLite.")
    # SQLite appends this exact nullable clause; original checks and SQL survive.
    invoice_sql = new_objects[("table", "commerce_invoice")]["sql"]
    pattern = r',\s*"return_lesson_id"\s+bigint\s+NULL\s+REFERENCES\s+"content_versionlesson"\s+\("id"\)\s+DEFERRABLE\s+INITIALLY\s+DEFERRED\s*(?=\)\s*$)'
    original_sql, substitutions = re.subn(pattern, "", invoice_sql, flags=re.IGNORECASE)
    def normalized(value):
        return " ".join(value.split())
    if substitutions != 1 or normalized(original_sql) != normalized(old_objects[("table", "commerce_invoice")]["sql"]):
        raise MigrationSafetyError("El SQL de factura cambió fuera de la columna autorizada.")
    extra_objects = new_objects.keys() - old_objects.keys()
    if len(extra_objects) != 1:
        raise MigrationSafetyError("La migración creó objetos adicionales inesperados.")
    kind, index = next(iter(extra_objects))
    if kind != "index" or new_objects[(kind, index)]["table"] != "commerce_invoice":
        raise MigrationSafetyError("El objeto adicional no es el índice esperado de factura.")
    indexes = database.execute('PRAGMA index_list("commerce_invoice")').fetchall()
    definition = next(item for item in indexes if item[1] == index)
    index_columns = [row[2] for row in database.execute(f"PRAGMA index_info({quoted(index)})")]
    if definition[2] or definition[4] or index_columns != [COLUMN]:
        raise MigrationSafetyError("El índice nuevo no corresponde exclusivamente al destino nullable.")
    check_integrity(database)
    return after


def public_manifest(state):
    return {"tables": {name: {key: values[key] for key in ("columns", "rows", "sha256")}
                       for name, values in state["tables"].items()}, "schema_sha256": {
        f"{kind}:{name}": hashlib.sha256((value["sql"] or "").encode("utf-8")).hexdigest()
        for (kind, name), value in state["objects"].items()
    }}


def connect_readonly(path):
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=20)


def configure(database_override):
    sys.path.insert(0, str(SRC))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform_config.settings")
    import django
    from django.conf import settings
    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
        raise MigrationSafetyError("Este procedimiento admite únicamente SQLite.")
    database = Path(database_override or settings.DATABASES["default"]["NAME"]).resolve()
    if not database.is_file():
        raise MigrationSafetyError("La base indicada no existe; no se creará una base vacía.")
    settings.DATABASES["default"]["NAME"] = str(database)
    django.setup()
    return database


def authorized_plan(connection):
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan([TARGET])
    if plan and [(migration.app_label, migration.name, backwards) for migration, backwards in plan] != [(*TARGET, False)]:
        raise MigrationSafetyError("El plan requiere otras migraciones o retrocesos; no se aplicará.")
    return executor, plan


def apply(database, connection):
    connection.ensure_connection()
    source = connection.connection
    source.execute("PRAGMA busy_timeout=5000")
    source.execute("PRAGMA locking_mode=EXCLUSIVE")
    source.execute("BEGIN EXCLUSIVE")
    source.execute("COMMIT")
    # Exclusive locking remains held by this connection through verification.
    executor, plan = authorized_plan(connection)
    if not plan:
        raise MigrationSafetyError("La migración ya está aplicada; no hay nada que cambiar.")
    check_integrity(source)
    before = snapshot(source)
    local = (SRC / ".local").resolve()
    folder = local / "backups" / ("overhaul-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10])
    if not folder.resolve().is_relative_to(local):
        raise MigrationSafetyError("La ruta de respaldo queda fuera del directorio local.")
    folder.mkdir(parents=True, exist_ok=False)
    backup_path = folder / "before.sqlite3"
    manifest_path = folder / "verification.json"
    report = {"database": str(database), "backup": str(backup_path), "migration": ".".join(TARGET),
              "status": "backing_up", "before": public_manifest(before)}
    migration_started = False
    def save_report():
        manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save_report()
    with sqlite3.connect(backup_path) as backup:
        source.backup(backup)
        check_integrity(backup)
        if snapshot(backup) != before:
            raise MigrationSafetyError("La copia SQLite no coincide con la huella de origen.")
    print(f"Respaldo verificado: {backup_path}")
    try:
        migration_started = True
        executor.migrate([TARGET])
        after = verify_changes(source, before)
        report.update(status="verified", after=public_manifest(after), historical_rows_unchanged=True,
                      nullable_destinations_empty=True, foreign_key_check="ok", integrity_check="ok")
        save_report()
        print("Migración verificada: datos históricos intactos; destino nullable vacío; FK e integridad correctos.")
        print(f"Huellas por tabla: {manifest_path}")
    except BaseException as error:
        if migration_started:
            source.rollback()
            try:
                with connect_readonly(backup_path) as backup:
                    backup.backup(source)
                if snapshot(source) != before:
                    raise MigrationSafetyError("La restauración no conservó la huella inicial.")
                check_integrity(source)
                report.update(status="restored", error_type=type(error).__name__, historical_rows_unchanged=True)
                save_report()
                print("Se restauró y verificó el respaldo original; la migración no quedó aplicada.")
            except BaseException as restore_error:
                report.update(status="restore_failed", error_type=type(error).__name__, restore_error_type=type(restore_error).__name__)
                save_report()
                raise MigrationSafetyError(f"No se confirmó la restauración. Conserva el respaldo: {backup_path}") from None
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Aplicar solo commerce0003 después de los controles integrados.")
    parser.add_argument("--database", help="Ruta de una base existente; permite ensayar sobre una copia sin tocar la principal.")
    args = parser.parse_args()
    database = configure(args.database)
    from django.db import connections
    connection = connections["default"]
    try:
        print(f"Base SQLite: {database}")
        executor, plan = authorized_plan(connection)
        with connect_readonly(database) as readonly:
            check_integrity(readonly)
            columns = [row[1] for row in readonly.execute('PRAGMA table_info("commerce_invoice")')]
            if (COLUMN in columns) != (not plan):
                raise MigrationSafetyError("La columna y el historial de migración no coinciden.")
            before = snapshot(readonly)
        print(f"Tablas verificadas: {len(before['tables'])}. FK e integridad: correctos.")
        if not plan:
            print("commerce0003 ya está aplicada. No se realizaron cambios.")
        elif args.apply:
            apply(database, connection)
        else:
            print("Pendiente: commerce.0003_invoice_return_lesson. Preflight terminado; no se modificó la base ni se creó respaldo.")
    finally:
        connections.close_all()


if __name__ == "__main__":
    try:
        main()
    except MigrationSafetyError as error:
        raise SystemExit(str(error)) from None
    except Exception as error:
        raise SystemExit(f"No se completó el procedimiento ({type(error).__name__}); no se muestran datos ni credenciales.") from None
