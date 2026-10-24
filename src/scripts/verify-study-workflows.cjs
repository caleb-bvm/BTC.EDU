/* Focused browser smoke test. Uses disposable data and prints only a summary. */
const {spawn} = require('node:child_process');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const password = 'StudyQA_42!';
const fixtureCode = String.raw`
import json, os, sys, tempfile, threading
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIRequestHandler
sys.path.insert(0, str(Path.cwd()))
with tempfile.TemporaryDirectory(prefix="study-preview-", dir=Path.cwd() / ".local") as folder:
    os.environ["DJANGO_DB_PATH"] = str(Path(folder) / "preview.sqlite3")
    os.environ["DJANGO_DEBUG"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", verbosity=0)
    from django.test import Client
    from learning.test_collections_practices import CollectionsPracticesTests
    fixture = CollectionsPracticesTests()
    fixture.client = Client()
    fixture.setUp()
    try:
        fixture.saved()
        for actor in (fixture.student, fixture.creator):
            actor.set_password("StudyQA_42!")
            actor.save()
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.servers.basehttp import ThreadedWSGIServer
        from django.core.wsgi import get_wsgi_application
        from django.db import connections
        from django.urls import reverse
        class Quiet(WSGIRequestHandler):
            def log_message(self, *args): pass
        server = make_server("127.0.0.1", 0, StaticFilesHandler(get_wsgi_application()), server_class=ThreadedWSGIServer, handler_class=Quiet)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print("READY " + json.dumps({"base": "http://127.0.0.1:" + str(server.server_port), "practice": reverse("student-practice", args=[fixture.practice.pk]), "editor": reverse("creator-practice", args=[fixture.lesson.pk])}), flush=True)
        sys.stdin.readline()
        server.shutdown()
        thread.join(timeout=10)
        server.server_close()
        connections.close_all()
    finally:
        fixture.doCleanups()
`;

let browser, preview, checks = 0;
const errors = [];
function check(condition, message) {
  checks++;
  if (!condition) throw new Error(message);
}
async function fixture() {
  preview = spawn(process.env.STUDY_QA_PYTHON || path.join(root, '.venv', 'Scripts', 'python.exe'), ['-u', '-c', fixtureCode], {cwd: root, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe']});
  return await new Promise((resolve, reject) => {
    let output = '', error = '';
    const timer = setTimeout(() => reject(new Error('Preview initialization timed out.')), 60000);
    preview.stderr.on('data', data => {error = (error + data).slice(-1500);});
    preview.stdout.on('data', data => {
      output += data.toString();
      const match = output.match(/READY (.+)\r?\n/);
      if (match) {clearTimeout(timer); resolve(JSON.parse(match[1]));}
    });
    preview.on('exit', code => {clearTimeout(timer); if (code) reject(new Error(`Preview failed (${code}): ${error}`));});
  });
}
async function login(page, base, creator = false) {
  await page.goto(base + (creator ? '/crear/entrar/' : '/cuenta/entrar/'));
  await page.locator('input[name=username]').fill(creator ? 'creator@practice.invalid' : 'student@practice.invalid');
  await page.locator('input[name=password]').fill(password);
  await Promise.all([page.waitForURL(url => !url.pathname.endsWith('/entrar/')), page.locator('form button[type=submit]').click()]);
}
async function submit(page, label) {
  await Promise.all([page.waitForNavigation(), page.getByRole('button', {name: label, exact: true}).click()]);
  check((await page.locator('[data-field-error-summary]').count()) === 0, `Unexpected validation error after ${label}`);
}
async function layout(page, width) {
  await page.setViewportSize({width, height: 820});
  check(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `Horizontal overflow at ${width}px`);
}

(async () => {
  try {
    const data = await fixture();
    browser = await chromium.launch({channel: process.env.STUDY_QA_BROWSER || 'chrome', headless: true});
    const student = await browser.newPage({viewport: {width: 1280, height: 900}});
    const educator = await browser.newPage({viewport: {width: 1280, height: 900}});
    for (const page of [student, educator]) {page.setDefaultTimeout(10000); page.on('pageerror', error => {if (errors.length < 5) errors.push(error.message);});}
    await login(student, data.base);
    await student.goto(data.base + '/mi-espacio/?seccion=guardados');
    await student.getByText('Crear una colección', {exact: true}).click();
    await student.locator('#collection-name').fill('Mi proyecto');
    await submit(student, 'Crear colección');
    await student.locator('#saved-collection').selectOption('');
    await submit(student, 'Filtrar');
    await student.getByText('Organizar en colecciones', {exact: true}).click();
    await student.getByLabel('Mi proyecto', {exact: true}).check();
    await submit(student, 'Guardar organización');
    await student.getByText('Organizar en colecciones', {exact: true}).click();
    check(await student.getByLabel('Mi proyecto', {exact: true}).isChecked(), 'Collection membership did not persist.');
    await layout(student, 320);
    const practiceResponse = await student.goto(data.base + data.practice);
    check(practiceResponse.status() === 200 && await student.locator('#id_body').count() === 1, 'Practice form unavailable: ' + (await student.locator('main').innerText()).slice(-400));
    await student.locator('#id_body').fill('Mi primera solución');
    await student.locator('input[type=file]').setInputFiles({name: 'solution.txt', mimeType: 'text/plain', buffer: Buffer.from('Mi proyecto')});
    await submit(student, 'Enviar al educador →');
    check(await student.getByText('Tu entrega está en revisión.', {exact: false}).isVisible(), 'Delivery was not submitted.');
    const download = await student.request.get(data.base + await student.getByRole('link', {name: /Descargar solution/}).getAttribute('href'));
    check(download.status() === 200 && (await download.body()).toString() === 'Mi proyecto', 'Private attachment did not download.');
    await login(educator, data.base, true);
    await educator.goto(data.base + '/crear/alumnos/entregas/');
    await educator.getByRole('link', {name: 'Revisar entrega →', exact: true}).click();
    await educator.getByLabel('Resultado correcto', {exact: true}).check();
    await educator.locator('#id_outcome').selectOption('changes');
    await educator.getByLabel('Retroalimentación y siguiente paso').fill('Explica cómo comprobar tu solución.');
    await submit(educator, 'Enviar revisión →');
    await student.reload();
    check(await student.getByRole('heading', {name: 'Enviar corrección'}).isVisible(), 'Correction form missing.');
    await student.locator('#id_body').fill('Solución corregida y comprobada');
    await submit(student, 'Enviar al educador →');
    await educator.goto(data.base + '/crear/alumnos/entregas/');
    await educator.getByRole('link', {name: 'Revisar entrega →', exact: true}).click();
    await educator.getByLabel('Resultado correcto', {exact: true}).check();
    await educator.getByLabel('Explica cómo probarlo', {exact: true}).check();
    await educator.getByLabel('Retroalimentación y siguiente paso').fill('Todos los criterios cumplidos.');
    await submit(educator, 'Enviar revisión →');
    await student.reload();
    check(await student.getByText('Práctica aprobada.', {exact: false}).isVisible(), 'Approval not visible.');
    check(await student.locator('.practice-attempt').count() === 2, 'Delivery history missing.');
    await layout(student, 320);
    await educator.goto(data.base + data.editor);
    await layout(educator, 320);
    await educator.evaluate(() => {localStorage.setItem('btc-theme', 'dark'); document.documentElement.dataset.theme = 'dark';});
    check(await educator.locator('#id_title').evaluate(el => getComputedStyle(el).backgroundColor !== 'rgb(255, 255, 255)'), 'Dark form uses white background.');
    await educator.goto(data.base + '/crear/alumnos/entregas/');
    await educator.getByText('Gestionar recepción de prácticas', {exact: true}).click();
    await submit(educator, 'Pausar recepción');
    await student.reload();
    check(await student.getByText('El educador ha pausado la recepción.', {exact: false}).isVisible(), 'Pause not visible.');
    check(errors.length === 0, errors.join('; '));
    console.log(JSON.stringify({ok: true, checks, workflows: ['collections', 'private attachment', 'correction', 'approval', 'pause'], widths: [320,1280]}));
  } catch (error) {
    console.error(JSON.stringify({ok: false, checks, error: error.message}));
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    if (preview) {
      preview.stdin.end('\n');
      await new Promise(resolve => preview.exitCode !== null ? resolve() : preview.once('exit', resolve));
    }
  }
})();
