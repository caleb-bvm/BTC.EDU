// Exercise the actual add-to-cart client without a network, provider, or browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/js/cart.js'), 'utf8');
class Element {
  constructor(value = '') {this.value = value; this.textContent = ''; this.hidden = false; this.disabled = false; this.attributes = new Map(); this.listeners = new Map(); this.dataset = {};}
  setAttribute(key, value) {this.attributes.set(key, value);}
  removeAttribute(key) {this.attributes.delete(key);}
  addEventListener(key, listener) {this.listeners.set(key, listener);}
}
function client(preflight) {
  const form = new Element(); form.action = '/carrito/anadir/7/'; form.checkValidity = () => true;
  const button = new Element(); button.textContent = 'Añadir al carrito';
  const origin = new Element('12'); const feedback = new Element(); feedback.hidden = true;
  const badge = new Element(); badge.hidden = true; const header = new Element();
  form.querySelector = selector => selector.startsWith('button') ? button : feedback;
  form.parentElement = {querySelector: () => feedback};
  const requests = [], navigation = [];
  class FormData extends Map {constructor() {super([['leccion', origin.value]]);} append(key, value) {this.set(key, value);}}
  const fetch = (url, options) => new Promise((resolve, reject) => requests.push({url, options, resolve, reject}));
  const document = {
    querySelector: () => null,
    querySelectorAll: selector => ({'[data-cart-form]': [form], '[data-cart-count]': [badge], '[data-cart-link]': [header]})[selector] || [],
    addEventListener() {}
  };
  const window = {fetch, FormData}; if (preflight) window.btcAccountContext = preflight;
  vm.runInNewContext(source, {document, window, fetch, FormData, TypeError, location: {assign: value => navigation.push(value)}});
  return {form, button, feedback, origin, badge, header, requests, navigation,
    submit: () => form.listeners.get('submit')({defaultPrevented: false, preventDefault() {}, submitter: button})};
}
const respond = (request, data, status = 200) => request.resolve({ok: status < 400, status, redirected: false,
  headers: {get: () => 'application/json'}, json: async () => data});
const verified = [];
(async () => {
  const first = client(); const pending = first.submit();
  await first.submit();
  assert.equal(first.requests.length, 1, 'A repeated submit cannot duplicate a pending add');
  assert.equal(first.button.disabled, true);
  assert.equal(first.requests[0].options.body.get('leccion'), '12');
  respond(first.requests[0], {ok: true, cart_count: 1, message: 'Añadido al carrito.', redirect: '/carrito/'});
  await pending;
  assert.equal(first.badge.hidden, false, 'The first item reveals the initially hidden counter');
  assert.equal(first.badge.textContent, '1');
  assert.equal(first.header.attributes.get('aria-label'), 'Carrito, 1 artículo');
  assert.equal(first.feedback.hidden, false);
  assert.equal(first.feedback.attributes.get('role'), 'status');
  assert.equal(first.navigation.length, 0, 'Adding never leaves exploration');
  assert.equal(first.button.disabled, false);
  assert.equal(first.button.textContent, 'Añadir al carrito');
  verified.push('first add reveals badge and status, preserves origin, prevents duplicate submission and stays on discovery');

  const invalid = client(); const rejected = invalid.submit();
  respond(invalid.requests[0], {ok: false, cart_count: 0, message: 'Esta opción ya no está disponible.'}, 409);
  await rejected;
  assert.equal(invalid.feedback.hidden, false);
  assert.equal(invalid.feedback.attributes.get('role'), 'alert');
  assert.equal(invalid.feedback.textContent, 'Esta opción ya no está disponible.');
  assert.equal(invalid.origin.value, '12');
  assert.equal(invalid.button.disabled, false);
  assert.equal(invalid.badge.hidden, true);
  verified.push('server validation exposes the reason and preserves selection for retry');

  const offline = client(); const failure = offline.submit();
  offline.requests[0].reject(new TypeError('Offline'));
  await failure;
  assert.equal(offline.feedback.hidden, false);
  assert.match(offline.feedback.textContent, /No pudimos conectar/);
  assert.equal(offline.origin.value, '12');
  assert.equal(offline.button.disabled, false);
  const retry = offline.submit();
  respond(offline.requests[1], {ok: true, cart_count: 2, message: 'Añadido.'});
  await retry;
  assert.equal(offline.header.attributes.get('aria-label'), 'Carrito, 2 artículos');
  assert.equal(offline.feedback.attributes.get('role'), 'status');
  verified.push('connection failure preserves input and a successful retry restores the counter and status');

  const account = client(async () => {throw new Error('account-session-changed');});
  await account.submit();
  assert.equal(account.requests.length, 0, 'Changed account prevents the POST');
  assert.equal(account.feedback.hidden, false);
  assert.match(account.feedback.textContent, /La sesión cambió/);
  assert.equal(account.origin.value, '12');
  assert.equal(account.button.disabled, false);
  verified.push('account mismatch prevents mutation and preserves selection');

  const lostSession = client(); const loginRedirect = lostSession.submit();
  lostSession.requests[0].resolve({ok: true, status: 200, redirected: true, headers: {get: () => 'text/html'}});
  await loginRedirect;
  assert.equal(lostSession.feedback.attributes.get('role'), 'alert');
  assert.match(lostSession.feedback.textContent, /La sesión cambió/);
  assert.equal(lostSession.navigation.length, 0);
  verified.push('login redirect is reported as a session change rather than a successful cart mutation');
  const report = {passed: verified.length, failed: 0, verified};
  const flag = process.argv.indexOf('--report');
  if (flag !== -1) fs.writeFileSync(process.argv[flag + 1], JSON.stringify(report, null, 2) + '\n');
  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
})().catch(error => {process.stderr.write(error.stack + '\n'); process.exitCode = 1;});
