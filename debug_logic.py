from __future__ import annotations

import uuid

import psycopg2 as ps


def generate_publication_debug(get_provider, org_name: str, assortment_name: str, description: str,
                               image_description: str | None, prompt: str, char_limit: int,
                               provider_type: int = 0) -> str | None:
    return get_provider(provider_type).generate_publication(
        org_name, assortment_name, description, image_description, prompt, char_limit
    )


def describe_image_debug(get_provider, load_file_metadata, store_file_metadata, org_name: str,
                         image_url: str, assortment_name: str, prompt: str, token_limit: int,
                         provider_type: int = 0) -> str | None:
    file_metadata = load_file_metadata(image_url)
    result, new_metadata = get_provider(provider_type).describeImage(
        org_name, image_url, assortment_name, prompt, token_limit, file_metadata=file_metadata
    )
    if new_metadata:
        store_file_metadata(image_url, new_metadata)
    return result


def _get_org_id(cursor, db_schema: str, org_name: str):
    if org_name is None or org_name.strip() == "":
        raise Exception("Не задано название организации")
    cursor.execute(
        "SELECT id FROM " + db_schema + ".organization WHERE strictname = %s",
        (org_name,),
    )
    org_row = cursor.fetchone()
    if org_row is None:
        raise Exception(f"Организация не найдена: {org_name}")
    return org_row[0]


def _find_org_prompt(cursor, db_schema: str, org_id, prompt_kind: int):
    cursor.execute(
        "SELECT p.id, p.fcontent, p.ai_provider, ap.fname "
        "FROM " + db_schema + ".org_ai_plans op "
        "INNER JOIN " + db_schema + ".ai_plans ap ON op.plan_name = ap.fname "
        "INNER JOIN " + db_schema + ".prompts p ON ap.prompt_id = p.id "
        "WHERE op.org_id = %s AND p.kind = %s "
        "ORDER BY ap.fname LIMIT 1",
        (org_id, prompt_kind),
    )
    return cursor.fetchone()


def _upsert_org_prompt(cursor, db_schema: str, org_id, prompt_kind: int, prompt_text: str,
                       provider_type: int):
    existing_prompt = _find_org_prompt(cursor, db_schema, org_id, prompt_kind)
    if existing_prompt is not None:
        cursor.execute(
            "UPDATE " + db_schema + ".prompts SET fcontent = %s, ai_provider = %s WHERE id = %s",
            (prompt_text, provider_type, str(existing_prompt[0])),
        )
        return "updated"

    prompt_id = str(uuid.uuid4())
    plan_name = f"debug_prompt_{org_id}_{prompt_kind}_{uuid.uuid4().hex[:8]}"
    cursor.execute(
        "INSERT INTO " + db_schema + ".prompts(id, fcontent, kind, ai_provider) VALUES(%s, %s, %s, %s)",
        (prompt_id, prompt_text, prompt_kind, provider_type),
    )
    cursor.execute(
        "INSERT INTO " + db_schema + ".ai_plans(prompt_id, dtype, fname, cron_expression) VALUES(%s, %s, %s, %s)",
        (prompt_id, "DebugPromptPlan", plan_name, None),
    )
    cursor.execute(
        "INSERT INTO " + db_schema + ".org_ai_plans(org_id, plan_name) VALUES(%s, %s)",
        (org_id, plan_name),
    )
    return "created"


def load_org_prompts_debug(get_connection_string, db_schema_key: str, env,
                           default_publication_prompt: str, default_image_prompt: str,
                           org_name: str):
    conn = ps.connect(get_connection_string())
    try:
        db_schema = env.get(db_schema_key, "business_ai")
        with conn.cursor() as cursor:
            org_id = _get_org_id(cursor, db_schema, org_name)
            image_prompt = _find_org_prompt(cursor, db_schema, org_id, 0)
            publication_prompt = _find_org_prompt(cursor, db_schema, org_id, 1)
    finally:
        conn.close()

    loaded_custom = []
    if image_prompt is not None:
        loaded_custom.append("описание изображения")
    if publication_prompt is not None:
        loaded_custom.append("публикация")

    provider_type = 0
    if publication_prompt is not None and publication_prompt[2] is not None:
        provider_type = int(publication_prompt[2])
    elif image_prompt is not None and image_prompt[2] is not None:
        provider_type = int(image_prompt[2])

    publication_value = publication_prompt[1] if publication_prompt is not None and publication_prompt[1] else default_publication_prompt
    image_value = image_prompt[1] if image_prompt is not None and image_prompt[1] else default_image_prompt

    if len(loaded_custom) == 0:
        message = "Кастомные промпты не найдены. Загружены значения по умолчанию."
    else:
        message = "Загружены кастомные промпты: " + ", ".join(loaded_custom)
        if len(loaded_custom) == 1:
            message += ". Для второго типа загружено значение по умолчанию."
    return publication_value, image_value, provider_type, message


def save_org_prompts_debug(get_connection_string, db_schema_key: str, env, org_name: str,
                           publication_prompt: str, image_prompt: str, provider_type: int) -> str:
    conn = ps.connect(get_connection_string())
    try:
        db_schema = env.get(db_schema_key, "business_ai")
        with conn.cursor() as cursor:
            org_id = _get_org_id(cursor, db_schema, org_name)
            publication_result = _upsert_org_prompt(
                cursor, db_schema, org_id, 1, publication_prompt, provider_type
            )
            image_result = _upsert_org_prompt(
                cursor, db_schema, org_id, 0, image_prompt, provider_type
            )
        conn.commit()
    finally:
        conn.close()

    return (
        "Промпты сохранены. "
        f"Публикация: {publication_result}. "
        f"Описание изображения: {image_result}."
    )
