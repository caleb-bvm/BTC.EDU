// Exercise the real progress client with controlled responses, without a browser.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../static/js/learning.js', import.meta.url), 'utf8');
class Element {
  constructor(value = '') {
    this.value = value;
    this.textContent = '';
    this.hidden = false;
    this.disabled = false;
    this.attributes = new Map();
    this.classes = new Set();
    this.events = new Map();
    this.classList = {contains: key => this.classes.has(key), add: key => this.classes.add(key),
      remove: key => this.classes.delete(key), toggle: (key, enabled) => enabled ? this.classes.add(key) : this.classes.delete(key)};
  }
  setAttribute(key, value) { this.attributes.set(key, value); }
  getAttribute(key) { return this.attributes.get(key); }
  removeAttribute(key) { this.attributes.delete(key); }
  addEventListener(key, listener) { this.events.set(key, listener); }
}

function client() {
  const form = new Element();
  form.setAttribute('action', '/progress/');
  const status = new Element();
  status.textContent = 'Initial hint';
  const revision = new Element('0');
  const lesson = new Element('12');
  const completion = new Element('complete');
  const reload = new Element();
  const retry = new Element();
  const next = new Element();
  reload.hidden = retry.hidden = next.hidden = true;
  const fields = {'[data-progress-status]': status, '[name="revision"]': revision, '[name="lesson"]': lesson,
    '[data-completion]': completion, '[data-progress-reload]': reload, '[data-progress-retry]': retry};
  form.querySelector = selector => fields[selector];
  const counts = [new Element(), new Element()];
  const percentages = [new Element(), new Element()];
  const meters = [new Element(), new Element()];
  const finished = new Element();
  const current = new Element();
  const heading = new Element();
  const requests = [];
  const document = {
    querySelector: selector => ({'[data-progress-form]': form, '[data-completion-next]': next,
      '[data-current-lesson-state]': current, '[data-completion-heading]': heading, '[data-course-finished]': finished})[selector] || null,
    querySelectorAll: selector => ({'[data-progress-count]': counts, '[data-progress-percentage]': percentages, '[data-course-progress]': meters})[selector] || [],
  };
  class FormData extends Map {
    constructor() { super([['lesson', lesson.value], ['revision', revision.value]]); }
  }
  vm.runInNewContext(source, {document, FormData, TypeError, window: {}, fetch: (url, options) => new Promise((resolve, reject) => requests.push({url, options, resolve, reject}))});
  return {form, status, revision, completion, reload, retry, next, requests, counts, percentages, meters, finished,
    submit: action => form.events.get('submit')({preventDefault() {}, submitter: {value: action}})};
}

const flush = () => new Promise(resolve => setImmediate(resolve));
const result = (request, data, status = 200) => request.resolve({ok: status === 200, status, redirected: false,
  headers: {get: () => 'application/json'}, json: async () => data});
const saved = (revision, completed, is_completed) => ({saved: true, revision, completed, total: 4, is_completed, message: 'Saved'});

const first = client();
assert.equal(first.requests[0].options.body.get('action'), 'position');
assert.equal(first.completion.disabled, true);
result(first.requests[0], saved(1, 0, false));
await flush();
assert.equal(first.status.textContent, 'Initial hint', 'Automatic position saves stay quiet');
assert.equal(first.revision.value, 1);
assert.equal(first.completion.disabled, false);

first.submit('complete');
first.submit('complete');
assert.equal(first.requests.length, 2, 'A pending request prevents duplicate submissions');
assert.equal(first.requests[1].options.body.get('revision'), 1);
result(first.requests[1], saved(2, 1, true));
await flush();
assert.equal(first.next.hidden, false);
assert.equal(first.completion.value, 'incomplete');
assert.deepEqual(first.percentages.map(item => item.textContent), ['25%', '25%']);
assert.deepEqual(first.meters.map(item => item.value), [1, 1]);

first.submit('incomplete');
result(first.requests[2], {saved: false, message: 'Newer progress exists'}, 409);
await flush();
assert.equal(first.revision.value, 2, 'Conflicts preserve the last confirmed revision');
assert.equal(first.completion.value, 'incomplete', 'Failed requests do not change completion');
assert.equal(first.reload.hidden, false);
assert.equal(first.retry.hidden, true);
first.submit('complete');
assert.equal(first.requests.length, 3, 'A conflict requires reloading before another mutation');

const recovery = client();
recovery.requests[0].reject(new TypeError('Offline'));
await flush();
assert.equal(recovery.status.classList.contains('save-error'), true);
assert.equal(recovery.retry.hidden, false);
recovery.submit('position');
result(recovery.requests[1], saved(1, 0, false));
await flush();
assert.equal(recovery.status.textContent, 'Saved', 'Successful recovery removes the previous error message');
assert.equal(recovery.status.classList.contains('save-error'), false);
assert.equal(recovery.retry.hidden, true);

console.log('Verified: quiet position save, confirmed completion, duplicate prevention, conflict protection and successful recovery.');
