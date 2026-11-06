(() => {
  const base = document.body.dataset.base || '';
  const menu = document.getElementById('menu'), nav = document.getElementById('links');
  const toggle = document.getElementById('catalog-toggle'), panel = document.getElementById('catalog-panel');
  function catalog(open) { panel.hidden = !open; toggle.setAttribute('aria-expanded', String(open)); }
  function mobile(open) { nav.classList.toggle('open', open); menu.setAttribute('aria-expanded', String(open)); menu.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню'); menu.textContent = open ? '✕' : '☰'; }
  menu.addEventListener('click', () => { catalog(false); mobile(!nav.classList.contains('open')); });
  toggle.addEventListener('click', () => { mobile(false); catalog(panel.hidden); });
  document.getElementById('catalog-close').addEventListener('click', () => { catalog(false); toggle.focus(); });
  document.addEventListener('click', e => { if (!panel.contains(e.target) && !toggle.contains(e.target)) catalog(false); });
  const input = document.getElementById('site-search'), results = document.getElementById('search-results');
  let index, pending;
  async function getIndex() { if (!pending) pending = fetch(base + '/assets/search-index.json').then(r => { if (!r.ok) throw Error('search'); return r.json(); }).catch(e => { pending = null; throw e; }); return index || (index = await pending); }
  function matches(data, query) { const words = query.toLocaleLowerCase('ru').trim().split(/\s+/); return data.filter(x => words.every(w => x.name.toLocaleLowerCase('ru').includes(w))); }
  function resultLink(item) { const a = document.createElement('a'); a.href = item.url; const title = document.createElement('span'); title.textContent = item.name; const tag = document.createElement('small'); tag.textContent = item.kind; a.append(title, tag); return a; }
  let version = 0;
  input.addEventListener('input', async () => {
    const v = ++version, q = input.value.trim(); results.replaceChildren(); results.hidden = q.length < 2; if (results.hidden) return;
    try { const data = await getIndex(); if (v !== version) return; const found = matches(data,q); found.slice(0,7).forEach(x => results.append(resultLink(x))); if (!found.length) { const p = document.createElement('p'); p.textContent = 'По вашему запросу ничего не найдено. Попробуйте другое название.'; results.append(p); } }
    catch { if (v === version) results.textContent = 'Поиск временно недоступен. Откройте каталог.'; }
  });
  input.addEventListener('keydown', e => { if (e.key === 'ArrowDown') { const a = results.querySelector('a'); if (a) { e.preventDefault(); a.focus(); } } });
  document.addEventListener('click', e => { if (!e.target.closest('.site-search')) results.hidden = true; });
  const query = new URLSearchParams(location.search).get('q');
  if (query && location.pathname === base + '/product/') {
    input.value = query; const section = document.createElement('section'); section.id = 'catalog-search-view'; section.className = 'wrap'; const h = document.createElement('h2'); h.textContent = 'Поиск: ' + query; const status = document.createElement('p'); status.className = 'search-summary'; status.setAttribute('role','status'); status.textContent = 'Ищем в каталоге…'; const list = document.createElement('div'); list.className = 'search-list'; section.append(h,status,list); document.getElementById('main').prepend(section);
    getIndex().then(data => { const found = matches(data,query); status.textContent = found.length ? 'Найдено: ' + found.length : 'Ничего не найдено. Попробуйте другое название или выберите раздел каталога ниже.'; found.forEach(x => list.append(resultLink(x))); }).catch(() => { status.textContent = 'Поиск временно недоступен. Выберите раздел каталога ниже.'; });
  }
  const dialog = document.getElementById('image-dialog');
  document.querySelectorAll('[data-zoom]').forEach(button => button.addEventListener('click', () => { const source = button.querySelector('img'); const image = dialog.querySelector('img'); image.src = source.src; image.alt = source.alt; dialog.showModal(); }));
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { const wasOpen = !panel.hidden; catalog(false); mobile(false); results.hidden = true; if (wasOpen) toggle.focus(); } });
  const form = document.getElementById('quote-form'); if (!form) return;
  const product = new URLSearchParams(location.search).get('product'); if (product) form.elements.product.value = product;
  function letter() { const d = new FormData(form); return ['Здравствуйте! Прошу рассчитать изготовление упаковки.','','Продукция: '+d.get('product'),'Имя: '+d.get('name'),'Email: '+d.get('email'),'Тираж: '+(d.get('quantity')||'не указан'),'Описание: '+(d.get('details')||'не указано')].join('\n'); }
  form.addEventListener('submit', e => { e.preventDefault(); if (form.reportValidity()) location.href = 'mailto:order@rossantpack.ru?subject='+encodeURIComponent('Расчёт упаковки — '+form.elements.product.value)+'&body='+encodeURIComponent(letter()); });
  const preview = document.createElement('pre'); preview.className = 'form-feedback'; preview.hidden = true; preview.tabIndex = 0; preview.setAttribute('aria-label','Текст подготовленного запроса');
  const button = document.createElement('button'); button.type = 'button'; button.className = 'btn btn-outline'; button.textContent = 'Показать текст запроса';
  const status = document.createElement('p'); status.setAttribute('role','status'); form.append(button,preview,status);
  button.addEventListener('click', () => { if (!form.reportValidity()) return; preview.textContent = letter(); preview.hidden = false; preview.focus(); status.textContent = 'Текст готов. Скопируйте его и отправьте на order@rossantpack.ru. Заявка пока не отправлена.'; });
})();
