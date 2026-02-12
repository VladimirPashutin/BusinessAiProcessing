from urllib.parse import parse_qs
import html

DEFAULT_IMAGE_URL = 'https://metaphysica-parfums.com/wp-content/uploads/2025/08/5d903ab13fd79a8c8e8dee91b05fa507.jpg'

def _render(self, defaultPublicationPrompt: str, defaultImagePrompt: str, env, values=None, outputs=None):
    values = values or {}
    outputs = outputs or {}
    defaults = {
        'orgName': '',
        'assortmentName': '',
        'description': '',
        'imageDescription': '',
        'pub_prompt': defaultPublicationPrompt,
        'pub_char_limit': str(env.get("python.max_chars_for_publication", 2500)),
        'img_prompt': defaultImagePrompt,
        'img_token_limit': str(env.get("python.max_tokens_for_describe_image", 500)),
        'imageUrl': DEFAULT_IMAGE_URL,
        'provider_type': '0',  # Default to Mistral
        'seed_org_name': 'Технологии третьего тысячелетия',
    }
    defaults.update({k: v for k, v in values.items() if v is not None})

    def esc(s: str):
        return html.escape(s or '')

    describe_result = outputs.get('describe_result')
    publication_result = outputs.get('publication_result')
    seed_result = outputs.get('seed_result')
    prompt_result = outputs.get('prompt_result')

    page = f"""
    <html><head><title>Debug UI</title><meta charset='utf-8'></head>
    <body>
    <h1>Это страница для отладки</h1>

    <form method="post" action="/debug">
      <h2>Общие параметры</h2>
      <label>Название организации (strictname):<br><input type="text" name="orgName" value="{esc(defaults['orgName'])}" style="width:480px"/></label><br><br>
      <label>Название ассортимента/услуги:<br><input type="text" name="assortmentName" value="{esc(defaults['assortmentName'])}" style="width:480px"/></label><br><br>
      <label>AI Провайдер:<br><select name="provider_type"><option value="0" {'selected' if defaults['provider_type'] == '0' else ''}>Mistral (0)</option><option value="1" {'selected' if defaults['provider_type'] == '1' else ''}>GigaChat (1)</option></select></label><br><br>

      <hr/>
      <h2>Генерация описания изображения</h2>
      <label>URL изображения:<br><input type="text" name="imageUrl" value="{esc(defaults['imageUrl'])}" style="width:640px"/></label><br><br>
      <label>Промпт описания изображения:<br><textarea name="img_prompt" rows="6" style="width:800px">{esc(defaults['img_prompt'])}</textarea></label><br><br>
      <button type="submit" name="action" value="load_prompts">Загрузить промпты</button>
      <button type="submit" name="action" value="save_prompts">Сохранить промпты</button><br><br>
      <label>Лимит токенов:<br><input type="number" name="img_token_limit" value="{esc(defaults['img_token_limit'])}"/></label><br><br>
      <button type="submit" name="action" value="describe">Сгенерировать описание</button>
      {('<h3>Результат описания изображения:</h3><pre style="white-space:pre-wrap;">' + esc(describe_result) + '</pre>') if describe_result else ''}

      <hr/>
      <h2>Генерация публикации</h2>
      <label>Описание ассортимента/услуги:<br><textarea name="description" rows="6" style="width:800px">{esc(defaults['description'])}</textarea></label><br><br>
      <label>Описание изображения (опционально):<br><textarea name="imageDescription" rows="4" style="width:800px">{esc(defaults['imageDescription'])}</textarea></label><br><br>
      <label>Промпт генерации публикации:<br><textarea name="pub_prompt" rows="6" style="width:800px">{esc(defaults['pub_prompt'])}</textarea></label><br><br>
      <button type="submit" name="action" value="load_prompts">Загрузить промпты</button>
      <button type="submit" name="action" value="save_prompts">Сохранить промпты</button><br><br>
      <label>Лимит символов:<br><input type="number" name="pub_char_limit" value="{esc(defaults['pub_char_limit'])}"/></label><br><br>
      <button type="submit" name="action" value="publication">Сгенерировать публикацию</button>
      {('<h3>Результат публикации:</h3><pre style="white-space:pre-wrap;">' + esc(publication_result) + '</pre>') if publication_result else ''}

      {('<h3>Результат работы с промптами:</h3><pre style="white-space:pre-wrap;">' + esc(prompt_result) + '</pre>') if prompt_result else ''}

      <hr/>
      <h2>Тестовые данные</h2>
      <button type="submit" name="action" value="seed_test_data">Очистить и заполнить тестовыми данными</button>
      {('<h3>Результат загрузки тестовых данных:</h3><pre style="white-space:pre-wrap;">' + esc(seed_result) + '</pre>') if seed_result else ''}
      <br><br>
      <label>Организация для обработки изображений:<br><input type="text" name="seed_org_name" value="{esc(defaults['seed_org_name'])}" style="width:480px"/></label><br><br>
      <button type="submit" name="action" value="process_assortment_images">Обработать изображения ассортимента</button>
    </form>

    </body></html>
    """

    self.send_response(200)
    self.send_header('Content-type', 'text/html; charset=utf-8')
    self.end_headers()
    self.wfile.write(page.encode('utf-8'))


def handle_debug_get(self, defaultPublicationPrompt: str, defaultImagePrompt: str, env):
    _render(self, defaultPublicationPrompt, defaultImagePrompt, env)


def handle_debug_post(self, defaultPublicationPrompt: str, defaultImagePrompt: str, env,
                      gen_publication_cb, describe_image_cb, seed_test_data_cb, process_assortment_images_cb,
                      load_prompts_cb, save_prompts_cb):
    length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(length).decode('utf-8') if length > 0 else ''
    form = parse_qs(body)

    action = (form.get('action') or [''])[0]
    values = {
        'orgName': (form.get('orgName') or [''])[0],
        'assortmentName': (form.get('assortmentName') or [''])[0],
        'description': (form.get('description') or [''])[0],
        'imageDescription': (form.get('imageDescription') or [''])[0],
        'pub_prompt': (form.get('pub_prompt') or [defaultPublicationPrompt])[0],
        'pub_char_limit': (form.get('pub_char_limit') or [str(env.get("python.max_chars_for_publication", 2500))])[0],
        'img_prompt': (form.get('img_prompt') or [defaultImagePrompt])[0],
        'img_token_limit': (form.get('img_token_limit') or [str(env.get("python.max_tokens_for_describe_image", 500))])[0],
        'imageUrl': (form.get('imageUrl') or [''])[0],
        'provider_type': (form.get('provider_type') or ['0'])[0],
        'seed_org_name': (form.get('seed_org_name') or ['Технологии третьего тысячелетия'])[0],
    }

    outputs = {}
    try:
        provider_type_int = int(values['provider_type'])
        if action == 'describe':
            res = describe_image_cb(values['orgName'], values['imageUrl'], values['assortmentName'],
                                    values['img_prompt'], int(values['img_token_limit']), provider_type_int)
            outputs['describe_result'] = res or ''
        elif action == 'publication':
            res = gen_publication_cb(values['orgName'], values['assortmentName'], values['description'],
                                     values['imageDescription'] or None, values['pub_prompt'], int(values['pub_char_limit']), provider_type_int)
            outputs['publication_result'] = res or ''
        elif action == 'seed_test_data':
            res = seed_test_data_cb()
            outputs['seed_result'] = res or ''
        elif action == 'process_assortment_images':
            res = process_assortment_images_cb(values['seed_org_name'])
            outputs['seed_result'] = res or ''
        elif action == 'load_prompts':
            pub_prompt, img_prompt, provider_type_int, result_message = load_prompts_cb(values['orgName'])
            values['pub_prompt'] = pub_prompt
            values['img_prompt'] = img_prompt
            values['provider_type'] = str(provider_type_int)
            outputs['prompt_result'] = result_message or ''
        elif action == 'save_prompts':
            res = save_prompts_cb(values['orgName'], values['pub_prompt'], values['img_prompt'], provider_type_int)
            outputs['prompt_result'] = res or ''
    except Exception as e:
        if action == 'publication':
            outputs['publication_result'] = f"Ошибка: {e}"
        elif action == 'seed_test_data':
            outputs['seed_result'] = f"Ошибка: {e}"
        elif action == 'process_assortment_images':
            outputs['seed_result'] = f"Ошибка: {e}"
        elif action == 'load_prompts' or action == 'save_prompts':
            outputs['prompt_result'] = f"Ошибка: {e}"
        else:
            outputs['describe_result'] = f"Ошибка: {e}"

    _render(self, defaultPublicationPrompt, defaultImagePrompt, env, values, outputs)
