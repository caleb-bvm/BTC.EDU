/* Browser review against preview-commercial.py, with disposable accounts and data.
 * Run with Playwright available on NODE_PATH; no packages are installed here.
 * Optional: NAVIGATION_QA_PYTHON, NAVIGATION_QA_BROWSER, --capture, --fixture-only,
 * --focused-reader-only, --auth-only, --short-menu-only, --catalog-only, --date=YYYY-MM-DD.
 * Results go to the console. An optional --report .local/name.json writes only
 * a brief summary inside the Git-ignored local directory; raw matrices stay in memory.
 */
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {chromium} = require('playwright');

const root = path.resolve(__dirname, '..');
const python = process.env.NAVIGATION_QA_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const date = process.argv.find(value => value.startsWith('--date='))?.slice(7) || new Intl.DateTimeFormat('en-CA', {timeZone: 'America/El_Salvador'}).format(new Date());
if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('Use --date=YYYY-MM-DD.');
const capture = process.argv.includes('--capture');
const fixtureOnly = process.argv.includes('--fixture-only');
const focusedReaderOnly = process.argv.includes('--focused-reader-only');
const catalogOnly = process.argv.includes('--catalog-only');
const shortMenuOnly = process.argv.includes('--short-menu-only');
const authOnly = process.argv.includes('--auth-only') || shortMenuOnly;
const evidenceDirectory = path.join(root, 'docs', 'evidence');
const reportIndex = process.argv.indexOf('--report');
const reportArgument = reportIndex < 0 ? null : process.argv[reportIndex + 1];
if (reportIndex >= 0 && (!reportArgument || reportArgument.startsWith('--'))) throw new Error('Use --report .local/name.json.');
const resultPath = reportArgument ? path.resolve(root, reportArgument) : null;
if (resultPath) {
  const relative = path.relative(path.join(root, '.local'), resultPath);
  if (!relative || relative === '..' || relative.startsWith('..' + path.sep) || path.isAbsolute(relative) || path.extname(resultPath) !== '.json') {
    throw new Error('Optional summaries must be JSON files inside src/.local/, outside versioned evidence.');
  }
}
const password = 'OverhaulQA_42!';

// The existing fixture owns its TemporaryDirectory. Returning from this small
// stdin-controlled server lets that context close its connections and clean up.
// There is deliberately no recursive-delete fallback in this verifier.
const previewWrapper = String.raw`
import json, os, sys, threading
from pathlib import Path
from unittest.mock import patch
from wsgiref.simple_server import WSGIRequestHandler, make_server

sys.path.insert(0, str(Path.cwd()))
from django.core.management import call_command as original_command

def command(name, *args, **kwargs):
    if name != "runserver":
        return original_command(name, *args, **kwargs)
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    from django.core.servers.basehttp import ThreadedWSGIServer
    from django.core.wsgi import get_wsgi_application
    from django.urls import reverse
    from content.models import Course
    from creators.models import CreatorProfile

    for state in ("pending", "suspended"):
        person = get_user_model().objects.create_user(
            "navigation-" + state + "@demo.invalid", "OverhaulQA_42!",
            account_type="creator", first_name="Navegación " + state)
        CreatorProfile.objects.create(user=person, status=state,
            display_name="Educador " + state, bio="Cuenta temporal para revisar navegación.",
            specialty="Prueba de navegación", feedback="Estado preparado exclusivamente para esta comprobación.")

    class QuietHandler(WSGIRequestHandler):
        def log_message(self, *args):
            pass

    course = Course.objects.get(pk=1)
    tutorial = Course.objects.filter(current_version__kind="tutorial").first()
    version = course.current_version
    lesson = version.chapters.first().lessons.order_by("position", "pk").first()
    application = StaticFilesHandler(get_wsgi_application())
    server = make_server("127.0.0.1", 0, application, server_class=ThreadedWSGIServer, handler_class=QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    metadata = {"baseUrl": "http://127.0.0.1:" + str(server.server_port),
        "database": str(settings.DATABASES["default"]["NAME"]),
        "coursePath": reverse("course-version", args=[course.pk, version.number]),
        "lessonPath": reverse("version-lesson", args=[course.pk, version.number, lesson.pk]),
        "creatorCoursePath": reverse("creator-course", args=[course.pk])}
    if tutorial:
        metadata["tutorialPath"] = reverse("course-version", args=[tutorial.pk, tutorial.current_version.number])
    print("NAVIGATION_READY " + json.dumps(metadata), flush=True)
    try:
        sys.stdin.readline()
    finally:
        server.shutdown()
        thread.join(timeout=10)
        server.server_close()
        print("NAVIGATION_SERVER_STOPPED", flush=True)

with patch("django.core.management.call_command", command):
    from scripts import preview_commercial
`;

// The source uses a hyphen in its filename, so import it through importlib.
const pythonSource = previewWrapper.replace('    from scripts import preview_commercial', String.raw`    import importlib.util
    spec = importlib.util.spec_from_file_location("navigation_commercial_preview", Path.cwd() / "scripts" / "preview-commercial.py")
    preview = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preview)
    preview.run()
print("NAVIGATION_PREVIEW_CLEANED", flush=True)`);

let preview;
let browser;
let fixture;
let previewOutput = '';
let previewError = '';
let checkCount = 0;
let failureCount = 0;
let measuredPages = 0;
const failures = [];
const browserErrors = [];

function check(name, passed, details = {}) {
  checkCount++;
  if (!passed) {
    failureCount++;
    if (failures.length < 10) failures.push({name, ...details});
  }
}

function startPreview() {
  return new Promise((resolve, reject) => {
    preview = spawn(python, ['-u', '-c', pythonSource], {cwd: root, windowsHide: true, stdio: ['pipe', 'pipe', 'pipe']});
    const timeout = setTimeout(() => reject(new Error('The disposable preview did not become ready within 180 seconds.')), 180000);
    preview.stdout.on('data', data => {
      previewOutput += data.toString();
      const line = previewOutput.split(/\r?\n/).find(value => value.startsWith('NAVIGATION_READY '));
      if (line && !fixture) {
        try {
          fixture = JSON.parse(line.slice('NAVIGATION_READY '.length));
          clearTimeout(timeout);
          const database = path.resolve(fixture.database);
          const localDirectory = path.join(root, '.local') + path.sep;
          if (!database.startsWith(localDirectory) || !path.basename(path.dirname(database)).startsWith('commercial-preview-')) throw new Error('The preview database is not inside its disposable fixture directory.');
          resolve(fixture);
        } catch (error) { reject(error); }
      }
    });
    preview.stderr.on('data', data => { previewError += data.toString(); });
    preview.once('error', error => { clearTimeout(timeout); reject(error); });
    preview.once('exit', code => {
      clearTimeout(timeout);
      if (!fixture) reject(new Error(`Disposable preview exited before readiness (${code}). ${previewError.slice(-1500)}`));
    });
  });
}

async function closePreview() {
  if (!preview || preview.exitCode !== null) return;
  const exited = new Promise(resolve => preview.once('exit', resolve));
  preview.stdin.end('stop\n');
  let timeout;
  await Promise.race([
    exited,
    new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('The preview did not stop gracefully.')), 20000); }),
  ]).finally(() => clearTimeout(timeout));
}

async function login(page, role) {
  if (role === 'visitor') return;
  const creator = role !== 'student';
  await page.goto(fixture.baseUrl + (creator ? '/crear/entrar/' : '/cuenta/entrar/'));
  const email = role === 'student' ? 'lucia@demo.invalid' : role === 'creator' ? 'ana@demo.invalid' : `navigation-${role}@demo.invalid`;
  await page.locator('#id_username').fill(email);
  await page.locator('#id_password').fill(password);
  await Promise.all([page.waitForURL(url => !url.pathname.endsWith('/entrar/')), page.locator('button[type="submit"]').click()]);
}

async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

async function openMenu(page) {
  await page.locator('.nav-toggle').click();
  await settle(page);
}

async function snapshot(page) {
  return page.evaluate(() => {
    const sidebar = document.querySelector('#academy-navigation');
    const header = document.querySelector('.app-header');
    const navigation = sidebar?.querySelector('.primary-navigation') || sidebar?.querySelector('nav');
    const rectangle = element => {
      if (!element) return null;
      const {x, y, width, height} = element.getBoundingClientRect();
      return {x, y, width, height};
    };
    const account = document.querySelector('.account-header-photo');
    return {
      url: location.pathname,
      sidebar: rectangle(sidebar), header: rectangle(header),
      sidebarDisplay: sidebar && getComputedStyle(sidebar).display,
      scrollHeight: sidebar?.scrollHeight,
      globalLinks: [...(navigation?.querySelectorAll('a') || [])].map(anchor => ({text: anchor.textContent.trim(), href: new URL(anchor.href).pathname, height: anchor.getBoundingClientRect().height, current: anchor.getAttribute('aria-current')})),
      secondaryLinks: [...(sidebar?.querySelectorAll('.secondary-navigation a') || [])].map(anchor => ({text: anchor.textContent.trim(), href: new URL(anchor.href).pathname})),
      sidebarLabels: [...(sidebar?.querySelectorAll('a') || [])].map(anchor => anchor.textContent.trim()),
      contextualSidebar: Boolean(sidebar?.querySelector('.task-navigation, .course-context')),
      account: rectangle(account),
      accountVisible: Boolean(account && getComputedStyle(account).display !== 'none' && account.getBoundingClientRect().width),
      horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 1,
      expanded: document.querySelector('.nav-toggle')?.getAttribute('aria-expanded'),
      activeTheme: document.documentElement.dataset.theme,
    };
  });
}

async function screenshot(page, label) {
  if (!capture) return;
  const name = `navegacion-${label}-${date}.png`;
  await page.screenshot({path: path.join(evidenceDirectory, name), fullPage: false, animations: 'disabled'});
}

async function keyboardReview(page) {
  const sidebar = page.locator('#academy-navigation');
  await openMenu(page);
  check('mobile-dialog-semantics', await sidebar.evaluate(element => Boolean(element.closest('[role="dialog"][aria-modal="true"], dialog[open]'))));
  check('focus-enters-menu', await sidebar.evaluate(element => element.contains(document.activeElement)));
  const focusable = sidebar.locator('a[href], button:not([disabled]), [tabindex="0"]').filter({visible: true});
  const count = await focusable.count();
  if (count) {
    await focusable.last().focus();
    await page.keyboard.press('Tab');
    check('tab-wraps-inside-menu', await sidebar.evaluate(element => element.contains(document.activeElement)));
    await focusable.first().focus();
    await page.keyboard.press('Shift+Tab');
    check('shift-tab-wraps-inside-menu', await sidebar.evaluate(element => element.contains(document.activeElement)));
  }
  check('background-cannot-take-focus', await page.evaluate(() => {
    document.querySelector('.academy-workbench a, .academy-workbench button')?.focus();
    return document.querySelector('#academy-navigation').contains(document.activeElement);
  }));
  await page.keyboard.press('Escape');
  check('escape-closes-and-restores-focus', await page.evaluate(() => !document.body.classList.contains('nav-open') && document.activeElement === document.querySelector('.nav-toggle') && document.querySelector('.nav-backdrop').hidden));
  await openMenu(page);
  await page.mouse.click(388, 150);
  check('backdrop-closes-menu', await page.evaluate(() => !document.body.classList.contains('nav-open')));
  await openMenu(page);
  const close = sidebar.locator('button').filter({visible: true});
  if (await close.count()) {
    await close.first().click();
    check('visible-close-control', await page.evaluate(() => !document.body.classList.contains('nav-open')));
  } else check('visible-close-control', false);
  await openMenu(page);
  await page.setViewportSize({width: 1440, height: 900});
  await settle(page);
  check('resize-clears-modal-state', await page.evaluate(() => !document.body.classList.contains('nav-open') && document.querySelector('.nav-backdrop').hidden && !document.querySelector('.academy-workbench').inert));
  await page.setViewportSize({width: 390, height: 844});
  await settle(page);
  check('resize-back-keeps-menu-closed', await page.evaluate(() => document.querySelector('.nav-toggle').getAttribute('aria-expanded') === 'false' && getComputedStyle(document.querySelector('#academy-navigation')).display === 'none'));
}

async function focusedReaderReview(page) {
  await page.setViewportSize({width: 390, height: 844});
  const response = await page.goto(fixture.baseUrl + fixture.lessonPath);
  check('reader-route-loads', response.status() === 200, {status: response.status()});
  await page.locator('[data-reader-focus]').click();
  await openMenu(page);
  const mobile = await snapshot(page);
  check('focused-reader-menu-is-visible', mobile.sidebarDisplay !== 'none' && mobile.sidebar.width > 0 && mobile.expanded === 'true', {viewport: {width: 390, height: 844}, state: mobile});
  if (!focusedReaderOnly) await screenshot(page, 'lector-enfocado-movil');
  await page.keyboard.press('Escape');
  check('focused-reader-survives-mobile-menu-escape', await page.evaluate(() => document.body.classList.contains('reader-focused') && !document.body.classList.contains('nav-open')));
  await page.setViewportSize({width: 1440, height: 900});
  await settle(page);
  await openMenu(page);
  const desktop = await snapshot(page);
  check('focused-reader-desktop-menu-is-visible', desktop.sidebarDisplay !== 'none' && desktop.sidebar.width > 0 && desktop.sidebar.width <= 320 && desktop.expanded === 'true', {viewport: {width: 1440, height: 900}, state: desktop});
  check('focused-reader-desktop-dialog-focus', await page.locator('#academy-navigation').evaluate(element => element.getAttribute('aria-modal') === 'true' && element.contains(document.activeElement)));
  await screenshot(page, 'lector-enfocado-escritorio');
  await page.keyboard.press('Escape');
  check('focused-reader-survives-desktop-menu-escape', await page.evaluate(() => document.body.classList.contains('reader-focused') && !document.body.classList.contains('nav-open') && document.activeElement === document.querySelector('.nav-toggle')));
  await page.keyboard.press('Escape');
  check('second-escape-exits-focused-reader', await page.evaluate(() => !document.body.classList.contains('reader-focused') && !document.body.classList.contains('nav-open') && !document.querySelector('.academy-workbench').inert));
}

async function authenticationReview() {
  if (!shortMenuOnly) {
  const context = await browser.newContext({viewport: {width: 1440, height: 900}});
  const page = await context.newPage();
  page.on('pageerror', error => browserErrors.push({role: 'visitor', message: error.message}));
  const routes = ['/cuenta/entrar/', '/cuenta/registro/', '/cuenta/recuperar/', '/cuenta/recuperar/enviada/', '/crear/entrar/', '/crear/registro/', '/crear/recuperar/', '/crear/recuperar/enviada/'];
  await page.goto(fixture.baseUrl + routes[0]);
  for (const theme of ['light', 'dark']) {
    await page.evaluate(value => localStorage.setItem('btc-edu-theme', value), theme);
    for (const viewport of [{width: 1440, height: 900}, {width: 320, height: 760}]) {
      await page.setViewportSize(viewport);
      for (const route of routes) {
        const response = await page.goto(fixture.baseUrl + route);
        await settle(page);
        const state = await page.evaluate(() => {
          const auth = document.querySelector('.auth-page');
          const {x, width} = auth?.getBoundingClientRect() || {};
          return {authPageCount: document.querySelectorAll('.auth-page').length, sidebarCount: document.querySelectorAll('#academy-navigation').length,
            toggleCount: document.querySelectorAll('.nav-toggle').length, horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 1,
            activeTheme: document.documentElement.dataset.theme, x, width};
        });
        check('auth-route-loads', response.status() === 200, {route, viewport, theme, status: response.status()});
        check('auth-uses-one-shared-page', state.authPageCount === 1, {route, viewport, theme});
        check('auth-has-no-sidebar-or-toggle', state.sidebarCount === 0 && state.toggleCount === 0, {route, viewport, theme});
        check('auth-fits-viewport', !state.horizontalOverflow && state.x >= 0 && state.x + state.width <= viewport.width + 1, {route, viewport, theme, state});
        check('auth-theme-applied', state.activeTheme === theme, {route, viewport, theme});
        measuredPages++;
        if (theme === 'light' && viewport.width === 320 && route === '/cuenta/entrar/') await screenshot(page, 'acceso-estudiante-movil');
        if (theme === 'dark' && viewport.width === 1440 && route === '/crear/entrar/') await screenshot(page, 'acceso-educador-escritorio');
      }
    }
  }
  const studentTarget = '/carrito/?desde=navegacion';
  await page.goto(fixture.baseUrl + '/cuenta/entrar/?next=' + encodeURIComponent(studentTarget));
  check('student-login-keeps-next-field', await page.locator('input[name="next"]').inputValue() === studentTarget);
  const signupUrl = await page.locator('.login-note a[href*="/cuenta/registro/"]').getAttribute('href');
  check('student-signup-link-keeps-next', new URL(signupUrl, fixture.baseUrl).searchParams.get('next') === studentTarget);
  await page.goto(new URL(signupUrl, fixture.baseUrl).href);
  check('student-signup-keeps-next-field', await page.locator('input[name="next"]').inputValue() === studentTarget);
  const backToLogin = await page.locator('.login-note a[href*="/cuenta/entrar/"]').getAttribute('href');
  check('student-signup-return-keeps-next', new URL(backToLogin, fixture.baseUrl).searchParams.get('next') === studentTarget);
  await page.goto(fixture.baseUrl + '/cuenta/entrar/?next=' + encodeURIComponent(studentTarget));
  await page.locator('#id_username').fill('lucia@demo.invalid');
  await page.locator('#id_password').fill(password);
  await Promise.all([page.waitForURL(url => !url.pathname.endsWith('/entrar/')), page.locator('button[type="submit"]').click()]);
  check('student-login-returns-to-next', new URL(page.url()).pathname + new URL(page.url()).search === studentTarget);
  await page.setViewportSize({width: 1440, height: 900});
  await page.goto(fixture.baseUrl + fixture.lessonPath);
  await page.evaluate(() => window.scrollTo(0, 500));
  await settle(page);
  const outline = await page.evaluate(() => {
    const panel = document.querySelector('.reader-outline').getBoundingClientRect(), header = document.querySelector('.app-header').getBoundingClientRect();
    return {top: panel.top, bottom: panel.bottom, headerBottom: header.bottom, scrollY, viewportHeight: innerHeight};
  });
  check('sticky-outline-stays-below-header', outline.scrollY >= 400 && outline.top >= outline.headerBottom && outline.bottom <= outline.viewportHeight + 1, {state: outline});
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.locator('a[href="#lesson-finish"]').click();
  await settle(page);
  check('lesson-finish-anchor-stays-visible', await page.evaluate(() => document.querySelector('#lesson-finish').getBoundingClientRect().top >= document.querySelector('.app-header').getBoundingClientRect().bottom), {viewport: {width: 1440, height: 900}});
  await page.setViewportSize({width: 390, height: 844});
  await page.goto(fixture.baseUrl + fixture.lessonPath + '#lesson-finish');
  await settle(page);
  check('lesson-finish-anchor-stays-visible', await page.evaluate(() => document.querySelector('#lesson-finish').getBoundingClientRect().top >= document.querySelector('.app-header').getBoundingClientRect().bottom), {viewport: {width: 390, height: 844}});
  await page.goto(fixture.baseUrl + fixture.coursePath);
  check('enrolled-course-community-is-local', await page.locator('.course-section-links a[href*="/aprendizaje/comunidad/"]').count() === 1);
  await context.close();
  }

  const creatorContext = await browser.newContext({viewport: {width: 390, height: 360}});
  const creatorPage = await creatorContext.newPage();
  creatorPage.on('pageerror', error => browserErrors.push({role: 'creator', message: error.message}));
  const creatorTarget = '/crear/contenido/?tipo=curso';
  await creatorPage.goto(fixture.baseUrl + '/crear/entrar/?next=' + encodeURIComponent(creatorTarget));
  const creatorNext = await creatorPage.locator('input[name="next"]').inputValue();
  check('creator-login-keeps-next-field', creatorNext === creatorTarget, {expected: creatorTarget, actual: creatorNext});
  await creatorPage.locator('#id_username').fill('ana@demo.invalid');
  await creatorPage.locator('#id_password').fill(password);
  await Promise.all([creatorPage.waitForURL(url => !url.pathname.endsWith('/entrar/')), creatorPage.locator('button[type="submit"]').click()]);
  const creatorDestination = new URL(creatorPage.url()).pathname + new URL(creatorPage.url()).search;
  check('creator-login-returns-to-next', creatorDestination === creatorTarget, {expected: creatorTarget, actual: creatorDestination});
  await openMenu(creatorPage);
  const short = await snapshot(creatorPage);
  check('short-menu-fills-available-height', Math.abs(short.sidebar.height - (360 - short.sidebar.y)) < 2, {state: short});
  check('short-menu-does-not-compress-links', short.globalLinks.length >= 5 && short.globalLinks.every(link => link.height >= 48), {links: short.globalLinks});
  check('short-menu-scrolls-internally', await creatorPage.locator('#academy-navigation').evaluate(element => element.scrollHeight > element.clientHeight && getComputedStyle(element).overflowY === 'auto'));
  const lastLink = creatorPage.locator('#academy-navigation .secondary-navigation a').last();
  await lastLink.focus();
  check('short-menu-last-destination-is-reachable', await lastLink.evaluate(element => {
    const item = element.getBoundingClientRect(), panel = document.querySelector('#academy-navigation').getBoundingClientRect();
    return document.activeElement === element && item.top >= panel.top - 1 && item.bottom <= panel.bottom + 1;
  }));
  await creatorPage.keyboard.press('Tab');
  check('short-menu-tab-returns-to-close', await creatorPage.locator('.nav-close').evaluate(element => document.activeElement === element && element.getBoundingClientRect().top >= document.querySelector('#academy-navigation').getBoundingClientRect().top));
  await creatorPage.keyboard.press('Tab');
  const firstFocus = await creatorPage.locator('#academy-navigation .primary-navigation a').first().evaluate(element => {
    const item = element.getBoundingClientRect(), heading = document.querySelector('.sidebar-mobile-heading').getBoundingClientRect();
    return {focused: document.activeElement === element, top: item.top, bottom: item.bottom, headingBottom: heading.bottom};
  });
  check('short-menu-first-link-focus-is-not-obscured', firstFocus.focused && firstFocus.top >= firstFocus.headingBottom - 1, {state: firstFocus});
  await screenshot(creatorPage, 'altura-corta-movil');
  await creatorPage.keyboard.press('Escape');
  check('short-menu-closes-with-escape', await creatorPage.evaluate(() => !document.body.classList.contains('nav-open') && document.activeElement === document.querySelector('.nav-toggle')));
  measuredPages++;
  await creatorPage.setViewportSize({width: 390, height: 844});
  await creatorPage.goto(fixture.baseUrl + fixture.creatorCoursePath + '?seccion=informacion');
  const title = creatorPage.locator('form[data-dirty-form] input[name="title"]').first();
  await title.fill((await title.inputValue()) + ' · revisión sin guardar');
  let dialogType = '';
  creatorPage.once('dialog', async dialog => { dialogType = dialog.type(); await dialog.dismiss(); });
  await openMenu(creatorPage);
  await creatorPage.locator('#academy-navigation a[href="/crear/estadisticas/"]').click();
  await settle(creatorPage);
  check('dirty-form-opens-native-beforeunload', dialogType === 'beforeunload', {dialogType});
  check('cancelled-navigation-keeps-editor-and-focus', await creatorPage.evaluate(() => location.pathname.startsWith('/crear/cursos/') && !document.body.classList.contains('nav-open') && document.activeElement === document.querySelector('.nav-toggle') && !document.querySelector('.academy-workbench').inert));
  await creatorContext.close();
}

async function reviewRole(role) {
  const context = await browser.newContext({viewport: {width: 1440, height: 900}});
  const page = await context.newPage();
  page.on('pageerror', error => browserErrors.push({role, message: error.message}));
  await login(page, role);
  const routes = role === 'visitor' ? ['/explorar/', '/cursos/', '/recursos/'] : role === 'student' ? ['/explorar/', '/mi-espacio/', '/facturas/', '/aprendizaje/comunidad/', '/aprendizaje/avisos/', '/cuenta/ajustes/', fixture.lessonPath] : role === 'creator' ? ['/crear/', '/crear/contenido/', fixture.creatorCoursePath, '/crear/preguntas/', '/crear/estadisticas/', '/crear/cuenta/', '/explorar/'] : ['/crear/solicitud/', '/crear/cuenta/', '/crear/cuenta/ayuda/'];
  const sizes = [{width: 1440, height: 900}, {width: 1200, height: 768}, {width: 390, height: 844}, {width: 320, height: 760}];
  await page.goto(fixture.baseUrl + routes[0]);
  let baselineLinks;
  for (const theme of ['light', 'dark']) {
    await page.evaluate(value => localStorage.setItem('btc-edu-theme', value), theme);
    for (const size of sizes) {
      await page.setViewportSize(size);
      let baselineGeometry;
      for (const route of routes) {
        const response = await page.goto(fixture.baseUrl + route);
        await settle(page);
        check('route-loads', response.status() === 200, {role, route, theme, viewport: size, status: response.status()});
        const closed = await snapshot(page);
        if (role !== 'visitor') check('account-visible', closed.accountVisible && closed.account.x >= 0 && closed.account.x + closed.account.width <= size.width + 1, {role, route, theme, viewport: size});
        if (size.width <= 900) await openMenu(page);
        const state = await snapshot(page);
        check('requested-theme-applied', state.activeTheme === theme, {role, route, theme, viewport: size});
        const links = {primary: state.globalLinks.map(({text, href}) => ({text, href})), secondary: state.secondaryLinks};
        baselineLinks ||= links;
        check('global-navigation-stable', JSON.stringify(links) === JSON.stringify(baselineLinks), {role, route, theme, viewport: size});
        check('no-account-or-help-in-sidebar', state.sidebarLabels.every(label => !/^(mi cuenta|ayuda)(\b|$)/i.test(label)), {role, route});
        check('no-contextual-sidebar', !state.contextualSidebar, {role, route});
        check('no-horizontal-overflow', !state.horizontalOverflow, {role, route, theme, viewport: size});
        check('sidebar-fills-visible-height', state.sidebar && Math.abs(state.sidebar.height - (size.height - state.sidebar.y)) <= 2, {role, route, theme, viewport: size, sidebar: state.sidebar});
        if (state.sidebar) {
          baselineGeometry ||= state.sidebar;
          check('sidebar-geometry-stable', Math.abs(state.sidebar.width - baselineGeometry.width) < 1 && Math.abs(state.sidebar.height - baselineGeometry.height) < 1 && Math.abs(state.sidebar.y - baselineGeometry.y) < 1, {role, route, theme, viewport: size});
        }
        check('links-keep-uniform-height', state.globalLinks.length > 0 && state.globalLinks.every(link => Math.abs(link.height - state.globalLinks[0].height) < 1 && link.height >= 44), {role, route, viewport: size});
        if (role === 'pending' || role === 'suspended') check('unapproved-creator-has-no-authoring-links', state.globalLinks.every(link => !/^\/crear\/(contenido|cursos|archivos|estadisticas|preguntas)\//.test(link.href)), {role, route});
        measuredPages++;
        if (role === 'student' && route === '/mi-espacio/' && theme === 'light' && size.width === 1440) await screenshot(page, 'estudiante-escritorio');
        if (role === 'student' && route === '/mi-espacio/' && theme === 'light' && size.width === 390) await screenshot(page, 'estudiante-movil');
        if (role === 'creator' && route === '/crear/contenido/' && theme === 'dark' && size.width === 1440) await screenshot(page, 'educador-oscuro-escritorio');
        if (role === 'pending' && route === '/crear/solicitud/' && theme === 'light' && size.width === 320) await screenshot(page, 'solicitud-movil');
      }
    }
  }
  if (role !== 'visitor') {
    await page.setViewportSize({width: 320, height: 760});
    await page.goto(fixture.baseUrl + routes[0]);
    const accountPath = role === 'student' ? '/cuenta/ajustes/' : '/crear/cuenta/';
    await Promise.all([page.waitForURL(url => url.pathname === accountPath), page.locator('.account-header-photo').click()]);
    check('account-opens-at-320px', new URL(page.url()).pathname === accountPath, {role});
  }
  if (role === 'student') {
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(fixture.baseUrl + '/mi-espacio/');
    await settle(page);
    await keyboardReview(page);
    await focusedReaderReview(page);
  }
  console.log(`Navigation review completed: ${role}`);
  await context.close();
}

async function catalogReview() {
  const destinations = [
    {path: '/cursos/', label: 'Cursos'},
    {path: '/tutoriales/', label: 'Tutoriales'},
    {path: '/recursos/', label: 'Recursos'},
  ];
  for (const role of ['visitor', 'student', 'creator', 'pending', 'suspended']) {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.on('pageerror', error => browserErrors.push({role, message: error.message}));
    await login(page, role);
    if (role === 'suspended') {
      for (const destination of destinations) {
        await page.goto(fixture.baseUrl + destination.path);
        check('suspended-creator-keeps-permitted-destinations', new URL(page.url()).pathname === '/crear/solicitud/' && await page.locator('#academy-navigation .secondary-navigation').count() === 0, {role, route: destination.path});
      }
      await context.close();
      continue;
    }
    await page.goto(fixture.baseUrl + '/cursos/');
    for (const theme of ['light', 'dark']) {
      await page.evaluate(value => localStorage.setItem('btc-edu-theme', value), theme);
      for (const size of [{width: 1440, height: 900}, {width: 320, height: 760}]) {
        await page.setViewportSize(size);
        let baseline;
        for (const destination of destinations) {
          const response = await page.goto(fixture.baseUrl + destination.path);
          await settle(page);
          check('catalog-opens', response.status() === 200, {role, route: destination.path, theme, viewport: size});
          check('catalog-has-its-own-title', (await page.locator('h1').innerText()) === destination.label, {role, route: destination.path});
          check('catalog-tabs-not-duplicated', await page.locator('nav[aria-label="Tipos de contenido"]').count() === 0, {role, route: destination.path});
          check('compare-only-belongs-to-courses', await page.locator('.catalog-compare').count() === (destination.label === 'Cursos' ? 1 : 0), {role, route: destination.path});
          check('filters-stay-in-their-catalog', await page.locator('#catalog form').getAttribute('action') === destination.path, {role, route: destination.path});
          if (size.width <= 900) await openMenu(page);
          const state = await snapshot(page);
          const paths = await page.locator('#academy-navigation a').evaluateAll(links => links.map(link => new URL(link.href).pathname));
          check('three-direct-catalog-destinations', destinations.every(item => paths.includes(item.path)) && !paths.includes('/explorar/'), {role, route: destination.path});
          check('correct-catalog-is-selected', await page.locator('#academy-navigation a[aria-current="page"]').getAttribute('href') === destination.path, {role, route: destination.path});
          baseline ||= state.sidebar;
          check('catalog-sidebar-geometry-stable', Math.abs(state.sidebar.height - baseline.height) < 1 && Math.abs(state.sidebar.width - baseline.width) < 1, {role, route: destination.path});
          check('catalog-no-overflow', !state.horizontalOverflow, {role, route: destination.path, viewport: size});
          measuredPages++;
          if (role === 'student' && theme === 'light' && destination.label === 'Cursos') await screenshot(page, `catalogos-${size.width === 320 ? 'movil' : 'escritorio'}`);
        }
      }
    }
    if (role === 'visitor') {
      await page.setViewportSize({width: 1440, height: 900});
      await page.goto(fixture.baseUrl + fixture.tutorialPath);
      check('tutorial-detail-selects-tutorials', await page.locator('#academy-navigation a[aria-current="page"]').getAttribute('href') === '/tutoriales/');
      await page.goto(fixture.baseUrl + '/recursos/?q=Planifica');
      check('resource-search-keeps-material', (await page.locator('#catalog').innerText()).includes('Planifica tu semana de estudio'));
      check('resources-do-not-show-course-cards', await page.locator('#catalog .academy-card').count() === 1);
      await page.goto(fixture.baseUrl + '/tutoriales/?q=Organiza');
      check('tutorial-search-keeps-tutorial', (await page.locator('#catalog').innerText()).includes('Organiza una práctica guiada'));
      const target = await page.locator('.tutorial-list a').first().getAttribute('href');
      check('tutorial-card-preserves-return', new URL(target, fixture.baseUrl).searchParams.get('volver') === '/tutoriales/?q=Organiza');
      await page.goto(new URL(target, fixture.baseUrl).href);
      check('tutorial-return-keeps-search', await page.locator('.breadcrumbs a').first().getAttribute('href') === '/tutoriales/?q=Organiza');
    }
    if (role === 'creator') {
      await page.setViewportSize({width: 390, height: 360});
      await page.goto(fixture.baseUrl + '/crear/');
      await openMenu(page);
      const sidebar = page.locator('#academy-navigation');
      await sidebar.locator('a[href="/recursos/"]').focus();
      check('all-catalog-links-reachable-in-short-menu', await sidebar.evaluate(element => {
        const active = document.activeElement.getBoundingClientRect();
        const frame = element.getBoundingClientRect();
        return active.bottom <= frame.bottom + 1 && active.top >= frame.top && element.scrollHeight > element.clientHeight;
      }));
      await page.keyboard.press('Escape');
      check('short-catalog-menu-closes', await page.locator('.nav-toggle').getAttribute('aria-expanded') === 'false');
    }
    await context.close();
    console.log(`Catalog review completed: ${role}`);
  }
}

(async () => {
  if (capture) fs.mkdirSync(evidenceDirectory, {recursive: true});
  try {
    await startPreview();
    console.log('Disposable navigation preview ready.');
    if (!fixtureOnly) {
      const launch = {headless: true};
      if (process.env.NAVIGATION_QA_BROWSER) launch.executablePath = process.env.NAVIGATION_QA_BROWSER;
      else launch.channel = 'chrome';
      browser = await chromium.launch(launch);
      if (catalogOnly) {
        await catalogReview();
      } else if (authOnly) {
        await authenticationReview();
      } else if (focusedReaderOnly) {
        const context = await browser.newContext({viewport: {width: 1440, height: 900}});
        const page = await context.newPage();
        page.on('pageerror', error => browserErrors.push({role: 'student', message: error.message}));
        await login(page, 'student');
        await page.evaluate(() => localStorage.setItem('btc-edu-theme', 'dark'));
        await focusedReaderReview(page);
        await context.close();
      } else {
        for (const role of ['visitor', 'student', 'creator', 'pending', 'suspended']) await reviewRole(role);
      }
      check('no-browser-script-errors', browserErrors.length === 0, {errors: browserErrors});
    }
  } catch (error) {
    check('review-completes', false, {error: error.message || String(error)});
  } finally {
    if (browser) await browser.close();
    try { await closePreview(); }
    catch (error) {
      check('preview-stops-gracefully', false, {error: error.message});
      if (preview && preview.exitCode === null) preview.kill();
    }
    const cleaned = !fixture || !fs.existsSync(path.dirname(fixture.database));
    check('temporary-data-cleaned', cleaned);
    const briefFailure = failure => ({
      name: failure.name, role: failure.role, route: failure.route,
      error: failure.error ? String(failure.error).split('\n')[0].slice(0, 400) : undefined,
    });
    const report = {date, passed: failureCount === 0,
      summary: {checks: checkCount, failures: failureCount, measuredPages},
      fixture: {disposableDatabase: true, cleaned, serverStopped: preview?.exitCode !== null},
      ...(failures.length ? {failures: failures.slice(0, 10).map(briefFailure)} : {}),
      ...(browserErrors.length ? {browserErrors: browserErrors.slice(0, 10).map(item => ({role: item.role, message: item.message.slice(0, 400)}))} : {}),
    };
    if (resultPath && !fixtureOnly) {
      fs.mkdirSync(path.dirname(resultPath), {recursive: true});
      fs.writeFileSync(resultPath, JSON.stringify(report, null, 2) + '\n');
    }
    console.log(JSON.stringify({...report, ...(resultPath ? {resultPath} : {})}));
    process.exitCode = failureCount ? 1 : 0;
  }
})();
