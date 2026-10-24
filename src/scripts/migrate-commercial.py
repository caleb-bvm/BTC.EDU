"""Verify the commercial migration plan; migrate only with explicit --apply.

Only commerce0004, learning0012 and the official admin metadata for four new
commerce models are allowed. An existing --database copy can be used for
rehearsal. No seeds, provider calls or general post_migrate hooks are run.
Backups and manifests contain local verification material under ignored .local;
console output never includes row contents, personal data or credentials.
"""
import argparse
import hashlib
import importlib.util
import json
import sqlite3
import struct
import uuid
from datetime import UTC, datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
TARGETS = (
    ("commerce", "0004_orderline_alter_invoice_offer_cart_cartitem_order_and_more"),
    ("learning", "0012_saveditem_course_version"),
)
NEW_MODELS = ("Cart", "CartItem", "Order", "OrderLine")
NEW_TABLES = {"commerce_" + model.lower() for model in NEW_MODELS}
CHANGED_TABLES = {"commerce_invoice", "learning_saveditem"}
METADATA_TABLES = ("django_content_type", "auth_permission")

# Reuse the previous migration's raw SQLite hashing, backup and integrity rules.
spec = importlib.util.spec_from_file_location("overhaul_migration_checks", SRC / "scripts/migrate-overhaul.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
MigrationSafetyError = checks.MigrationSafetyError


def normalized(value):
    return " ".join((value or "").strip().rstrip(";").split())


def historical_rows_digest(database, table, columns, exclude_ids):
    expressions = ", ".join(
        f"typeof({checks.quoted(column)}), CASE WHEN typeof({checks.quoted(column)})='text' "
        f"THEN CAST({checks.quoted(column)} AS BLOB) ELSE {checks.quoted(column)} END"
        for column in columns
    )
    query = f"SELECT {expressions} FROM {checks.quoted(table)}"
    if exclude_ids:
        placeholders = ",".join("?" for _ in exclude_ids)
        query += f" WHERE id NOT IN ({placeholders})"
    query += " ORDER BY id"
    digest, count = hashlib.sha256(), 0
    for row in database.execute(query, sorted(exclude_ids)):
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


def metadata_requirements():
    from django.apps import apps
    from django.contrib.auth import get_permission_codename
    requirements = {}
    for name in NEW_MODELS:
        model = apps.get_model("commerce", name)
        opts = model._meta
        if tuple(opts.default_permissions) != ("add", "change", "delete", "view") or opts.permissions:
            raise MigrationSafetyError("Los permisos del modelo no coinciden con los 16 metadatos autorizados.")
        requirements[opts.model_name] = {get_permission_codename(action, opts): f"Can {action} {opts.verbose_name_raw}"
                                         for action in opts.default_permissions}
    return requirements


def metadata_state(database):
    required = metadata_requirements()
    placeholders = ",".join("?" for _ in required)
    ctypes = {model: identity for identity, model in database.execute(
        f"SELECT id,model FROM django_content_type WHERE app_label=? AND model IN ({placeholders})",
        ["commerce", *required],
    )}
    permissions = {(model, codename): identity for identity, model, codename in database.execute(
        f"SELECT p.id,c.model,p.codename FROM auth_permission p JOIN django_content_type c ON c.id=p.content_type_id "
        f"WHERE c.app_label=? AND c.model IN ({placeholders})", ["commerce", *required],
    ) if codename in required[model]}
    return {"content_types": ctypes, "permissions": permissions,
            "missing_content_types": set(required) - set(ctypes),
            "missing_permissions": {(model, code) for model, codes in required.items() for code in codes} - set(permissions)}


def snapshot(database):
    state = checks.snapshot(database)
    state["metadata_ids"] = {table: {row[0] for row in database.execute(f"SELECT id FROM {checks.quoted(table)}")}
                             for table in METADATA_TABLES}
    state["admin_metadata"] = metadata_state(database)
    return state


def initialize_admin_metadata():
    from django.apps import apps
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    from django.db import transaction
    required = metadata_requirements()
    models = [apps.get_model("commerce", name) for name in NEW_MODELS]
    # Use Django's public manager APIs only for the four approved models.
    # No permissions are assigned to users or groups and no general hooks run.
    ContentType.objects.clear_cache()
    with transaction.atomic(using="default"):
        ctypes = ContentType.objects.db_manager("default").get_for_models(*models, for_concrete_models=False)
        for model in models:
            for codename, name in required[model._meta.model_name].items():
                Permission.objects.using("default").get_or_create(content_type=ctypes[model], codename=codename, defaults={"name": name})


def verify_admin_metadata(database, before, after):
    added = {}
    expected_records = {"django_content_type": {("commerce", model) for model in before["admin_metadata"]["missing_content_types"]}}
    required = metadata_requirements()
    current = after["admin_metadata"]
    if current["missing_content_types"] or current["missing_permissions"]:
        raise MigrationSafetyError("Los cuatro modelos comerciales no tienen todos sus metadatos oficiales.")
    expected_records["auth_permission"] = {(current["content_types"][model], code, required[model][code])
                                           for model, code in before["admin_metadata"]["missing_permissions"]}
    for table in METADATA_TABLES:
        prior_ids = before["metadata_ids"][table]
        actual_ids = after["metadata_ids"][table]
        new_ids = actual_ids - prior_ids
        if prior_ids - actual_ids or len(new_ids) != len(expected_records[table]):
            raise MigrationSafetyError("Los metadatos de administración cambiaron fuera de la lista autorizada.")
        if new_ids:
            first_id = before["sequences"].get(table, max(prior_ids, default=0)) + 1
            if sorted(new_ids) != list(range(first_id, first_id + len(new_ids))):
                raise MigrationSafetyError("Los identificadores nuevos de administración son inesperados.")
            placeholders = ",".join("?" for _ in new_ids)
            columns = "app_label,model" if table == "django_content_type" else "content_type_id,codename,name"
            records = set(database.execute(f"SELECT {columns} FROM {checks.quoted(table)} WHERE id IN ({placeholders})", sorted(new_ids)))
            if records != expected_records[table]:
                raise MigrationSafetyError("Se crearon metadatos ajenos a los cuatro modelos y 16 permisos autorizados.")
        added[table] = new_ids
    return added


def authorized_plan(connection):
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(TARGETS)
    names = [(migration.app_label, migration.name) for migration, backwards in plan]
    if any(backwards for migration, backwards in plan) or len(names) != len(set(names)) or not set(names).issubset(TARGETS):
        raise MigrationSafetyError("El plan requiere migraciones o retrocesos fuera de commerce0004/learning0012.")
    return executor, plan, set(names)


def schema_objects(database, tables):
    return {(kind, name): {"table": table, "sql": normalized(sql)}
            for kind, name, table, sql in database.execute("SELECT type, name, tbl_name, sql FROM sqlite_master")
            if table in tables}


def expected_schema(connection, executor):
    # Build just the authorized final tables in memory from migration state.
    # This checks exact constraints, types, FK declarations and named indexes,
    # including SQLite's implicit unique indexes, without touching the source.
    from django.db import connections
    alias = "commercial-schema-reference"
    reference = connection.copy(alias=alias)
    reference.settings_dict["NAME"] = ":memory:"
    reference.settings_dict["OPTIONS"] = {"timeout": 20}
    connections[alias] = reference
    apps = executor.loader.project_state(TARGETS).apps
    try:
        with reference.schema_editor() as editor:
            for name in NEW_MODELS + ("Invoice",):
                editor.create_model(apps.get_model("commerce", name))
            editor.create_model(apps.get_model("learning", "SavedItem"))
        return schema_objects(reference.connection, NEW_TABLES | CHANGED_TABLES)
    finally:
        reference.close()
        del connections[alias]


def schema_matches_history(database, pending):
    commerce_pending, learning_pending = TARGETS[0] in pending, TARGETS[1] in pending
    tables = {row[0] for row in database.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if (NEW_TABLES <= tables) == commerce_pending or (NEW_TABLES & tables and not NEW_TABLES <= tables):
        raise MigrationSafetyError("Las tablas comerciales y el historial de migraciones no coinciden.")
    for table, column, is_pending in (("commerce_invoice", "order_id", commerce_pending),
                                      ("learning_saveditem", "course_version_id", learning_pending)):
        columns = {row[1] for row in database.execute(f"PRAGMA table_info({checks.quoted(table)})")}
        if (column in columns) == is_pending:
            raise MigrationSafetyError("Una columna nueva y el historial de migración no coinciden.")


def preserve_saved_sequence(database, before, pending):
    # SQLite table remakes can reset an AUTOINCREMENT high-water mark when the
    # highest historical IDs were deleted. Preserve that metadata exactly.
    if TARGETS[1] not in pending:
        return
    table = "learning_saveditem"
    if table in before["sequences"]:
        prior = before["sequences"][table]
        changed = database.execute("UPDATE sqlite_sequence SET seq=? WHERE name=?", (prior, table)).rowcount
        if not changed:
            database.execute("INSERT INTO sqlite_sequence(name,seq) VALUES (?,?)", (table, prior))
    else:
        database.execute("DELETE FROM sqlite_sequence WHERE name=?", (table,))


def verify_changes(database, before, pending, expected):
    after = snapshot(database)
    commerce_pending, learning_pending = TARGETS[0] in pending, TARGETS[1] in pending
    added_tables = NEW_TABLES if commerce_pending else set()
    if set(after["tables"]) != set(before["tables"]) | added_tables:
        raise MigrationSafetyError("La migración cambió tablas fuera de lo autorizado.")
    new_ids = after["migration_ids"] - before["migration_ids"]
    if len(new_ids) != len(pending) or before["migration_ids"] - after["migration_ids"]:
        raise MigrationSafetyError("El historial de migraciones contiene cambios inesperados.")
    placeholders = ",".join("?" for _ in new_ids)
    records = (database.execute(f"SELECT app,name,applied FROM django_migrations WHERE id IN ({placeholders})", sorted(new_ids)).fetchall()
               if new_ids else [])
    if {(app, name) for app, name, applied in records if applied} != pending:
        raise MigrationSafetyError("Los registros nuevos no corresponden a las migraciones autorizadas.")
    first_id = before["sequences"]["django_migrations"] + 1
    if sorted(new_ids) != list(range(first_id, first_id + len(pending))):
        raise MigrationSafetyError("Los identificadores nuevos de migración son inesperados.")
    added_metadata = verify_admin_metadata(database, before, after)
    expected_sequences = dict(before["sequences"])
    if new_ids:
        expected_sequences["django_migrations"] = max(new_ids)
    for table, identities in added_metadata.items():
        if identities:
            expected_sequences[table] = max(identities)
    if after["sequences"] != expected_sequences:
        raise MigrationSafetyError("Los contadores SQLite cambiaron fuera de lo permitido.")
    for table, values in before["tables"].items():
        if table == "sqlite_sequence":
            continue
        old_columns = values["columns"]
        extra = (["order_id"] if table == "commerce_invoice" and commerce_pending else
                 ["course_version_id"] if table == "learning_saveditem" and learning_pending else [])
        if after["tables"][table]["columns"] != old_columns + extra:
            raise MigrationSafetyError(f"Cambió una columna fuera de lo permitido en {table}.")
        definitions = [item for item in after["tables"][table]["definitions"] if item[0] in old_columns]
        expected_definitions = [tuple(item[:2]) + (0,) + tuple(item[3:])
                                if table == "commerce_invoice" and commerce_pending and item[0] == "offer_id" else item
                                for item in values["definitions"]]
        if definitions != expected_definitions:
            raise MigrationSafetyError(f"Cambió una definición histórica fuera de lo permitido en {table}.")
        excluded = new_ids if table == "django_migrations" else added_metadata.get(table, set())
        actual = (historical_rows_digest(database, table, old_columns, excluded) if table == "django_migrations" or table in METADATA_TABLES
                  else checks.rows_digest(database, table, old_columns))
        if actual != {"rows": values["rows"], "sha256": values["sha256"]}:
            raise MigrationSafetyError(f"Las filas históricas de {table} no conservaron su huella.")
    for table in added_tables:
        if after["tables"][table]["rows"]:
            raise MigrationSafetyError("Una tabla comercial nueva recibió datos no autorizados.")
    for table, column, is_pending in (("commerce_invoice", "order_id", commerce_pending),
                                      ("learning_saveditem", "course_version_id", learning_pending)):
        if is_pending and database.execute(f"SELECT COUNT(*) FROM {checks.quoted(table)} WHERE {checks.quoted(column)} IS NOT NULL").fetchone()[0]:
            raise MigrationSafetyError("Se asignó un destino nuevo a una fila histórica.")
    changed = ({"commerce_invoice"} if commerce_pending else set()) | ({"learning_saveditem"} if learning_pending else set())
    for key, value in before["objects"].items():
        if value["table"] not in changed and (key not in after["objects"] or after["objects"][key] != value):
            raise MigrationSafetyError("Cambió un objeto histórico del esquema fuera de lo autorizado.")
    for key in after["objects"].keys() - before["objects"].keys():
        if after["objects"][key]["table"] not in changed | added_tables:
            raise MigrationSafetyError("Se creó un objeto de esquema fuera de lo autorizado.")
    if schema_objects(database, NEW_TABLES | CHANGED_TABLES) != expected:
        raise MigrationSafetyError("El esquema final no coincide con los modelos de las migraciones autorizadas.")
    checks.check_integrity(database)
    return after


def apply(database, connection):
    connection.ensure_connection()
    source = connection.connection
    source.execute("PRAGMA busy_timeout=5000")
    source.execute("PRAGMA locking_mode=EXCLUSIVE")
    source.execute("BEGIN EXCLUSIVE")
    source.execute("COMMIT")
    # Exclusive locking remains held through backup, migration and verification.
    executor, plan, pending = authorized_plan(connection)
    checks.check_integrity(source)
    schema_matches_history(source, pending)
    before = snapshot(source)
    if not plan and not before["admin_metadata"]["missing_content_types"] and not before["admin_metadata"]["missing_permissions"]:
        raise MigrationSafetyError("Las migraciones y sus metadatos ya están completos; no hay nada que cambiar.")
    expected = expected_schema(connection, executor)
    local = (SRC / ".local").resolve()
    folder = local / "backups" / ("commercial-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10])
    if not folder.resolve().is_relative_to(local):
        raise MigrationSafetyError("La ruta de respaldo queda fuera del directorio local.")
    folder.mkdir(parents=True, exist_ok=False)
    backup_path, manifest_path = folder / "before.sqlite3", folder / "verification.json"
    report = {"database": str(database), "backup": str(backup_path), "migrations": [".".join(target) for target in TARGETS if target in pending],
              "status": "backing_up", "before": checks.public_manifest(before)}
    def save_report():
        manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    save_report()
    with sqlite3.connect(backup_path) as backup:
        source.backup(backup)
        checks.check_integrity(backup)
        if snapshot(backup) != before:
            raise MigrationSafetyError("El respaldo SQLite no coincide con la huella de origen.")
    print(f"Respaldo verificado: {backup_path}")
    try:
        if plan:
            executor.migrate(TARGETS)
        preserve_saved_sequence(source, before, pending)
        initialize_admin_metadata()
        after = verify_changes(source, before, pending, expected)
        report.update(status="verified", after=checks.public_manifest(after), historical_rows_unchanged=True,
                      new_tables_empty=True, historical_new_columns_null=True, foreign_key_check="ok", integrity_check="ok",
                      admin_metadata_added={table: len(after["metadata_ids"][table] - before["metadata_ids"][table]) for table in METADATA_TABLES})
        save_report()
        print("Cambios verificados: filas y valores históricos intactos; adiciones exclusivamente autorizadas; FK e integridad correctos.")
        print("Administración verificada: cuatro tipos de contenido y 16 permisos oficiales completos; metadatos anteriores intactos.")
        print(f"Huellas por tabla: {manifest_path}")
    except BaseException as error:
        source.rollback()
        try:
            with checks.connect_readonly(backup_path) as backup:
                backup.backup(source)
            from django.contrib.contenttypes.models import ContentType
            ContentType.objects.clear_cache()
            if snapshot(source) != before:
                raise MigrationSafetyError("La restauración no conservó la huella inicial.")
            checks.check_integrity(source)
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
    parser.add_argument("--apply", action="store_true", help="Aplicar exclusivamente commerce0004 y learning0012 con respaldo y verificación.")
    parser.add_argument("--database", help="Base SQLite existente; permite ensayar una copia sin modificar la principal.")
    args = parser.parse_args()
    database = checks.configure(args.database)
    from django.db import connections
    connection = connections["default"]
    try:
        print(f"Base SQLite: {database}")
        executor, plan, pending = authorized_plan(connection)
        with checks.connect_readonly(database) as readonly:
            checks.check_integrity(readonly)
            schema_matches_history(readonly, pending)
            before = snapshot(readonly)
        print(f"Tablas verificadas: {len(before['tables'])}. FK e integridad: correctos.")
        missing = before["admin_metadata"]
        metadata_pending = bool(missing["missing_content_types"] or missing["missing_permissions"])
        print(f"Metadatos oficiales pendientes: {len(missing['missing_content_types'])} tipos de contenido y {len(missing['missing_permissions'])} permisos.")
        if not plan and not metadata_pending:
            print("commerce0004, learning0012 y sus metadatos de administración ya están completos. No se realizaron cambios.")
        elif args.apply:
            apply(database, connection)
        else:
            if pending:
                print("Pendientes autorizadas: " + ", ".join(".".join(target) for target in TARGETS if target in pending))
            else:
                print("Pendientes únicamente los metadatos oficiales de los cuatro modelos comerciales nuevos.")
            print("Preflight terminado; no se modificó la base ni se creó respaldo.")
    finally:
        connections.close_all()


if __name__ == "__main__":
    try:
        main()
    except MigrationSafetyError as error:
        raise SystemExit(str(error)) from None
    except Exception as error:
        raise SystemExit(f"No se completó el procedimiento ({type(error).__name__}); no se muestran datos ni credenciales.") from None
