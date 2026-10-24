// Run the real authoring client against controlled server responses and DOM inputs.
// Usage: node scripts/verify-authoring-forms.cjs [--report .local/forms-report.json]
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/js/forms.js'), 'utf8');
class Element {
  constructor(tagName, attributes = {}, text = '') {
    this.tagName = tagName.toUpperCase(); this.attributes = new Map(Object.entries(attributes));
    this.id = attributes.id || ''; this.name = attributes.name || '';
    this.value = attributes.value || ''; this.disabled = false; this.isConnected = true;
    this.textContent = text; this.children = []; this.listeners = new Map(); this.dataset = {};
    this.className = attributes.class || ''; this.classList = {contains: name => this.className.split(' ').includes(name)};
  }
  setAttribute(name, value) { this.attributes.set(name, value); if (name === 'id') this.id = value; }
  getAttribute(name) { return this.attributes.get(name) || null; }
  hasAttribute(name) { return this.attributes.has(name); }
  removeAttribute(name) { this.attributes.delete(name); }
  addEventListener(name, handler) { this.listeners.set(name, handler); }
  append(...children) { children.forEach(child => {child.parentElement = this; this.children.push(child);}); }
  prepend(child) { child.parentElement = this; this.children.unshift(child); }
  after(child) { const index = this.parentElement.children.indexOf(this); child.parentElement = this.parentElement; this.parentElement.children.splice(index + 1, 0, child); }
  remove() { if (this.parentElement) this.parentElement.children = this.parentElement.children.filter(child => child !== this); this.isConnected = false; }
  focus() { this.focused = true; }
  contains(target) { return this === target || this.children.some(child => child.contains(target)); }
  closest(selector) {
    for (let item = this; item; item = item.parentElement) {
      if (selector === '.studio-field' && item.classList.contains('studio-field')) return item;
      if (selector === 'details' && item.tagName === 'DETAILS') return item;
    }
    return null;
  }
  querySelectorAll(selector) {
    const all = this.children.flatMap(child => [child, ...child.querySelectorAll('*')]);
    if (selector === '*') return all;
    if (selector === 'input,textarea,select,button') return all.filter(item => ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(item.tagName));
    if (selector === '[name=csrfmiddlewaretoken]') return all.filter(item => item.name === 'csrfmiddlewaretoken');
    if (selector === '[aria-invalid]') return all.filter(item => item.hasAttribute('aria-invalid'));
    if (selector === '.field-save-error' || selector === '.form-save-error' || selector === '.errorlist') return all.filter(item => item.classList.contains(selector.slice(1)));
    return [];
  }
  querySelector(selector) {
    if (selector === '.studio-save,[data-save-status],.form-save-status') return this.status || null;
    if (selector === '[name="account_id"]') return this.querySelectorAll('*').find(item => item.name === 'account_id') || null;
    if (selector === 'button[type=submit]') return this.querySelectorAll('*').find(item => item.tagName === 'BUTTON') || null;
    if (selector === 'input:not([type=hidden]),textarea,select') return this.querySelectorAll('*').find(item => ['INPUT', 'TEXTAREA', 'SELECT'].includes(item.tagName) && item.getAttribute('type') !== 'hidden') || null;
    return this.querySelectorAll(selector)[0] || null;
  }
}

function client({preflight} = {}) {
  const form = new Element('form', {'data-dirty-form': ''}); form.action = 'http://localhost/crear/cursos/1/';
  form.checkValidity = () => true;
  const disclosure = new Element('details'); disclosure.open = false;
  const field = new Element('div', {class: 'studio-field'});
  const title = new Element('input', {id: 'id_title', name: 'title', value: 'Texto que quiero conservar'});
  const csrf = new Element('input', {type: 'hidden', name: 'csrfmiddlewaretoken', value: 'initial-token'});
  const identity = new Element('input', {type: 'hidden', name: 'account_id', value: '7'});
  const alwaysDisabled = new Element('input', {name: 'unavailable', value: 'excluded'}); alwaysDisabled.disabled = true;
  const button = new Element('button', {type: 'submit', name: 'action', value: 'save'});
  const status = new Element('p', {class: 'studio-save'});
  field.append(title); disclosure.append(field); form.append(disclosure, csrf, identity, alwaysDisabled, button, status); form.status = status;
  const events = new Map(), requests = [], navigation = [];
  const document = {
    querySelector() {return null;}, querySelectorAll() {return [form];},
    createElement: tag => new Element(tag),
    getElementById: id => form.querySelectorAll('*').find(item => item.id === id) || null,
    addEventListener(name, handler) {events.set('document:' + name, handler);}
  };
  class Snapshot extends Map {
    constructor(current) {super(current.querySelectorAll('input,textarea,select,button').filter(item => item.tagName !== 'BUTTON' && !item.disabled).map(item => [item.name, item.value]));}
    append(key, value) {this.set(key, value);}
  }
  const fetch = (url, options) => new Promise((resolve, reject) => requests.push({url, options, resolve, reject}));
  const window = {fetch, FormData: Snapshot, addEventListener(name, handler) {events.set(name, handler);}};
  if (preflight) window.btcAccountContext = () => preflight({form, csrf});
  let responsePage = null;
  class DOMParser {parseFromString() {assert(responsePage, 'Provide an HTML response fixture'); return responsePage;}}
  vm.runInNewContext(source, {document, window, fetch, FormData: Snapshot, DOMParser, URL,
    location: {href: form.action, origin: 'http://localhost', assign: url => navigation.push(url)}});
  return {form, title, csrf, button, alwaysDisabled, status, requests, navigation, disclosure, field,
    input(value) {title.value = value; form.listeners.get('input')();},
    submit() {return form.listeners.get('submit')({defaultPrevented: false, submitter: button, preventDefault() {}});},
    protectsExit() {let prevented = false; events.get('beforeunload')({preventDefault() {prevented = true;}}); return prevented;},
    htmlPage(page) {responsePage = page;}
  };
}
const jsonResponse = (request, data, status = 200) => request.resolve({ok: status < 400, status, url: request.url,
  headers: {get: () => 'application/json'}, json: async () => data});
const flush = () => new Promise(resolve => setImmediate(resolve));
const verified = [];

async function run() {
  const saved = client(); saved.input('Borrador para guardar');
  const normal = saved.submit();
  assert(saved.title.disabled && saved.button.disabled, 'Inputs are frozen while a request is pending');
  assert.equal(saved.requests[0].options.body.get('title'), 'Borrador para guardar');
  assert.equal(saved.requests[0].options.body.get('action'), 'save');
  assert(!saved.requests[0].options.body.has('unavailable'), 'Previously disabled inputs are not submitted');
  await saved.submit();
  assert.equal(saved.requests.length, 1, 'A second submit cannot duplicate the pending save');
  jsonResponse(saved.requests[0], {redirect: '/crear/cursos/1/'});
  await normal;
  assert.deepEqual(saved.navigation, ['/crear/cursos/1/']);
  assert.equal(saved.protectsExit(), false);
  assert.equal(saved.title.disabled, false);
  assert.equal(saved.alwaysDisabled.disabled, true, 'Previously disabled controls remain disabled');
  verified.push('confirmed save, snapshot, duplicate prevention and disabled-control restoration');

  const invalid = client(); invalid.input('Valor que no debe perderse');
  const rejected = invalid.submit();
  jsonResponse(invalid.requests[0], {errors: ['El orden de la lección ya está ocupado.']}, 400);
  await rejected;
  assert.equal(invalid.title.value, 'Valor que no debe perderse');
  assert.equal(invalid.navigation.length, 0);
  assert.equal(invalid.protectsExit(), true);
  assert.equal(invalid.title.disabled, false);
  const summary = invalid.form.querySelector('.form-save-error');
  assert(summary && summary.focused, 'Validation errors are announced and focused');
  assert(summary.querySelectorAll('*').some(item => item.textContent === 'El orden de la lección ya está ocupado.'));
  verified.push('JSON validation error preserves values, exposes error and allows retry');

  const late = client(); late.input('Versión enviada');
  const pending = late.submit();
  late.input('Cambio posterior a la versión enviada');
  jsonResponse(late.requests[0], {redirect: '/crear/cursos/1/'});
  await pending;
  assert.equal(late.requests[0].options.body.get('title'), 'Versión enviada');
  assert.equal(late.title.value, 'Cambio posterior a la versión enviada');
  assert.equal(late.navigation.length, 0, 'A subsequent input prevents navigation from discarding new work');
  assert.equal(late.protectsExit(), true);
  assert.match(late.status.textContent, /cambios posteriores/);
  verified.push('input after snapshot remains in the form and protects navigation');

  const offline = client(); offline.input('Borrador sin conexión');
  const networkSave = offline.submit();
  offline.requests[0].reject(new Error('Connection lost'));
  await networkSave;
  assert.equal(offline.title.value, 'Borrador sin conexión');
  assert.equal(offline.protectsExit(), true);
  assert.equal(offline.title.disabled, false);
  assert.equal(offline.navigation.length, 0);
  verified.push('connection failure preserves input and restores controls');

  const session = client({preflight: async () => {throw new Error('account-session-changed');}});
  session.input('Trabajo de esta cuenta');
  await session.submit();
  assert.equal(session.requests.length, 0, 'Account mismatch prevents sending the mutation');
  assert.equal(session.title.value, 'Trabajo de esta cuenta');
  assert.equal(session.protectsExit(), true);
  assert.match(session.status.textContent, /sesión o cuenta cambió/);
  assert.equal(session.title.disabled, false);
  verified.push('account mismatch prevents POST and preserves pending work');

  const refreshed = client({preflight: async ({csrf}) => {csrf.value = 'refreshed-token';}});
  refreshed.input('Misma cuenta tras renovar sesión');
  const csrfSave = refreshed.submit();
  await flush();
  assert.equal(refreshed.requests[0].options.body.get('csrfmiddlewaretoken'), 'refreshed-token');
  jsonResponse(refreshed.requests[0], {redirect: '/crear/cursos/1/'});
  await csrfSave;
  verified.push('renewed CSRF token replaces the token in the submitted snapshot');

  const redirectError = client(); redirectError.input('Motivo pendiente');
  redirectError.htmlPage({querySelectorAll(selector) {return selector.startsWith('.errorlist,') ? [new Element('div', {'data-message-level': 'error'}, 'No se pudo autorizar otro intento.')] : [];}});
  const grant = redirectError.submit();
  redirectError.requests[0].resolve({ok: true, status: 200, redirected: true, url: 'http://localhost/crear/evaluaciones/',
    headers: {get: () => 'text/html'}, text: async () => '<div data-message-level="error">No se pudo autorizar otro intento.</div>'});
  await grant;
  assert.equal(redirectError.navigation.length, 0, 'Redirect with an error is not mistaken for a confirmed save');
  assert.equal(redirectError.title.value, 'Motivo pendiente');
  assert.equal(redirectError.protectsExit(), true);
  verified.push('HTML redirect with error preserves the form instead of confirming success');

  const validation = client(); validation.input('Respuesta de una pregunta plegada');
  const error = new Element('ul', {id: 'id_title_error', class: 'errorlist'}, 'Respuesta fuera de rango.');
  const responseField = new Element('div', {class: 'studio-field'});
  const responseInput = new Element('input', {id: 'id_title', name: 'title', 'aria-describedby': 'id_title_help id_title_error'});
  responseField.append(responseInput, error);
  const responseDetails = new Element('details'); responseDetails.append(responseField);
  const label = new Element('label', {for: 'id_title'}, 'Respuesta correcta');
  const responsePage = {
    getElementById: id => id === error.id ? error : null,
    querySelectorAll(selector) {
      if (selector.startsWith('.errorlist,')) return [error];
      return {'details': [responseDetails], 'input,textarea,select': [responseInput], 'label': [label]}[selector] || [];
    }
  };
  validation.htmlPage(responsePage);
  const fieldSave = validation.submit();
  validation.requests[0].resolve({ok: true, status: 200, redirected: false, url: validation.form.action,
    headers: {get: () => 'text/html'}, text: async () => '<form>Controlled invalid field response</form>'});
  await fieldSave;
  assert.equal(validation.title.value, 'Respuesta de una pregunta plegada');
  assert.equal(validation.disclosure.open, true, 'The invalid field is revealed in its details section');
  assert.equal(validation.title.getAttribute('aria-invalid'), 'true');
  assert.match(validation.title.getAttribute('aria-describedby'), /id_title_save_error/);
  const links = validation.form.querySelectorAll('*').filter(item => item.tagName === 'A');
  assert(links.some(link => link.textContent.includes('Respuesta correcta: Respuesta fuera de rango.')));
  links[0].listeners.get('click')({preventDefault() {}});
  assert.equal(validation.title.focused, true);
  verified.push('HTML validation links the error, opens its section and focuses the preserved input');

  const foreign = client(); foreign.input('Contenido protegido');
  const foreignSave = foreign.submit();
  jsonResponse(foreign.requests[0], {redirect: 'https://outside.invalid/'});
  await foreignSave;
  assert.equal(foreign.navigation.length, 0);
  assert.equal(foreign.protectsExit(), true);
  verified.push('external redirect is rejected without losing input');

  const report = {passed: verified.length, failed: 0, verified};
  const reportFlag = process.argv.indexOf('--report');
  if (reportFlag !== -1) fs.writeFileSync(process.argv[reportFlag + 1], JSON.stringify(report, null, 2) + '\n');
  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
}
run().catch(error => {process.stderr.write(error.stack + '\n'); process.exitCode = 1;});
