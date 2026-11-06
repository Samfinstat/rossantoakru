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

// Per-page technical SEO review. Read-only: never changes SEO tags or sends a request.
(() => {
  const base = document.body.dataset.base || '';
  let path = decodeURI(location.pathname);
  if (base && path.startsWith(base + '/')) path = path.slice(base.length);
  path = path.replace(/index\.html$/, '');
  if (document.title === 'Страница не найдена | Россантпак') path='/404.html';
  const bucket = Array.from(path).reduce((n,c)=>n+c.codePointAt(0),0)%16;
  const fallback = document.querySelector('.seo-details');
  if (!fallback) return;
  const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const button = el('button','SEO страницы','seo-launcher'); button.type = 'button'; button.setAttribute('aria-label','SEO страницы'); button.setAttribute('aria-haspopup','dialog'); button.setAttribute('aria-controls','seo-dialog');
  const modal = el('dialog',undefined,'seo-dialog'); modal.id = 'seo-dialog'; modal.setAttribute('aria-labelledby','seo-dialog-title');
  const header = el('div',undefined,'seo-dialog-header'); const titleBox = el('div'); titleBox.append(el('p','РАБОЧИЙ ПАСПОРТ СТРАНИЦЫ','eyebrow'));
  const title = el('h2','SEO страницы'); title.id = 'seo-dialog-title'; titleBox.append(title);
  const close = el('button','×','seo-close'); close.type = 'button'; close.setAttribute('aria-label','Закрыть SEO страницы');
  const body = el('div',undefined,'seo-dialog-body'); header.append(titleBox,close); modal.append(header,body); document.body.append(button,modal);
  let files;
  function load() { if (!files) files = Promise.all(['seo-passports-'+bucket+'.json','seo-queries.json'].map(name => fetch(base+'/assets/'+name).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();}))).catch(e=>{files=null;throw e;}); return files; }
  const badge = (label,type='plan') => el('span',label,'seo-badge '+type);
  function table(headers) { const wrap=el('div',undefined,'seo-table-wrap'), t=el('table',undefined,'seo-table'), head=el('thead'),tr=el('tr'),rows=el('tbody');headers.forEach(h=>{const th=el('th',h);th.scope='col';tr.append(th);});head.append(tr);t.append(head,rows);wrap.append(t);return {wrap,rows}; }
  function row(target,label,status,value,plan) { const tr=el('tr'),th=el('th',label),s=el('td'),v=el('td');th.scope='row';s.append(status);v.append(el('div',value === '' || value == null ? 'Не задано' : String(value)));if(plan)v.append(el('p','Для запуска: '+plan,'seo-plan-text'));tr.append(th,s,v);target.append(tr); }
  function section(label) { const s=el('section',undefined,'seo-block');s.append(el('h3',label));body.append(s);return s; }
  function detail(label,open=false) { const d=el('details',undefined,'seo-disclosure'); d.open=open;d.append(el('summary',label));body.append(d);return d; }
  function compare(actual,expected,required=true) { if (required && (actual==='' || actual==null || Array.isArray(actual)&&!actual.length)) return badge('Не задано','issue');return JSON.stringify(actual)===JSON.stringify(expected)?badge('HTML совпадает','ok'):badge('Отличается от сборки','issue'); }
  function render(record,queries) {
    body.replaceChildren(); title.textContent='SEO · '+record.name;
    const kinds={product:'Карточка товара',category:'Раздел каталога',article:'Статья',service:'Услуга',material:'Материал',utility:'Служебная страница',redirect:'Прежний адрес',error:'Страница ошибки',page:'Страница сайта'};
    body.append(el('p','Режим: review. Проверяем HTML открытой страницы относительно последней сборки. Это не подтверждение индексации, HTTP-ответов сервера или готовности к запуску.','seo-notice'));
    body.append(el('p',(kinds[record.kind]||record.kind)+' · '+record.path,'seo-path'));
    if(location.search)body.append(el('p','Открыт URL с параметрами. Паспорт относится к основному пути; правила для поиска, сортировки и фильтров нужно настроить отдельно.','seo-notice'));
    const expected=record.expected, prod=record.production;
    const meta=selector=>document.head.querySelector(selector)?.getAttribute('content')||'';
    const h1s=Array.from(document.querySelectorAll('main h1'));
    const types=[];let invalid=0;
    document.head.querySelectorAll('script[type="application/ld+json"]').forEach(n=>{try{const v=JSON.parse(n.textContent);[...(Array.isArray(v)?v:[v])].forEach(x=>{if(x['@type'])types.push(x['@type']);});}catch{invalid++;}});
    const checks=table(['Настройка','Проверка HTML','Текущее значение и требование']);
    const values=[
      ['Title',document.title,expected.title,'Сохранить согласованный уникальный Title.'],
      ['Description',meta('meta[name="description"]'),expected.description,'Сохранить уникальное описание этой страницы.'],
      ['H1: количество',h1s.length,expected.h1_count,'Один основной H1.'],
      ['H1',h1s.map(x=>x.innerText.trim().replace(/\s+/g,' ')).join(' | '),expected.h1,'Сохранить название и назначение страницы.'],
      ['Robots',meta('meta[name="robots"]'),expected.robots,prod.robots],
      ['Canonical',document.head.querySelector('link[rel="canonical"]')?.getAttribute('href')||'',expected.canonical,prod.canonical+' — плановый адрес; проверить доступность и карту миграции.'],
      ['OG title',meta('meta[property="og:title"]'),expected.og_title,expected.title],
      ['OG description',meta('meta[property="og:description"]'),expected.og_description,expected.description],
      ['OG URL',meta('meta[property="og:url"]'),expected.og_url,prod.canonical],
      ['OG type',meta('meta[property="og:type"]'),expected.og_type,expected.og_type],
      ['OG image',meta('meta[property="og:image"]'),expected.og_image,prod.og_image?'Добавить абсолютный URL. Предлагаемый файл: '+prod.og_image+'. Подтвердить изображение и путь после переноса.':'Подобрать изображение страницы и задать абсолютный URL.']
    ];
    values.forEach(([name,actual,planned,note])=>row(checks.rows,name,compare(actual,planned),actual,note));
    row(checks.rows,'JSON-LD: типы и синтаксис',invalid?badge('Ошибка JSON','issue'):compare(types,expected.schema_types),invalid?'Некорректных блоков: '+invalid:types.join(', '),'Проверить свойства и актуальность значений валидатором; наличие типов не означает право на расширенный результат.');
    section('Настройки этой страницы').append(checks.wrap);
    const plan=table(['Параметр','Статус','Что необходимо сделать']);
    const plans=[
      ['HTTP и HTTPS',prod.http+'. Проверить ответ по конечному URL, без цепочки переходов и soft 404.'],
      ['Индексация',record.kind==='redirect'?'Настроить постоянный серверный редирект; noindex не заменяет 301.':prod.robots+'. Проверить также HTTP-заголовок X-Robots-Tag.'],
      ['XML sitemap',prod.sitemap?'После приёмки включить '+prod.canonical+' в XML-карту: только конечный канонический URL с HTTP 200.':'Не включать эту страницу в XML-карту индексируемых URL.'],
      ['robots.txt','Настроить в корне рабочего хоста. Для индексируемых URL разрешить обход. Чтобы робот увидел noindex, не запрещать обход этой страницы. Файл в /rossantoakru/ не управляет всем github.io.'],
      ['Миграция и дубли',record.redirects_from.length?'Настроить HTTP 301 с '+record.redirects_from.join(', ')+' на '+prod.canonical:record.kind==='redirect'?'Этот адрес должен возвращать HTTP 301 на '+prod.canonical:'Сверить прежний URL и назначение; при изменении адреса настроить один HTTP 301 на согласованный аналог. Для этой страницы отдельные прежние адреса пока не зафиксированы.'],
      ['Параметры URL','UTM не включать в canonical и sitemap. Поиск, сортировку и фильтры разбирать по назначению: поисковую выдачу закрыть от индексации; страницы пагинации не сводить автоматически к первой.'],
      ['Перелинковка',record.parent?'Родительский раздел: '+record.parent+'. Проверить хлебные крошки, переход в раздел и ссылки на связанные решения.':'Проверить доступность из меню, хлебные крошки и ссылки на тематические разделы.'],
      ['Мобильная версия и скорость','Проверить читаемость, кнопки, отсутствие обрезки; оценить LCP, INP и CLS на рабочем сайте. Измерения производительности этим паспортом не выполняются.'],
      ['Вебмастеры','После запуска проверить URL, выбранный canonical и индексацию в Яндекс Вебмастере / Google Search Console. Отправка sitemap не гарантирует индексацию.']
    ];
    if(record.kind==='product')plans.splice(6,0,['Product и коммерческие данные','Сверить название, артикул, материал, размеры и бренд с товаром. Без подтверждённых offers, review или aggregateRating текущий Product не считать готовым расширенным сниппетом. Не добавлять фиктивные цену, наличие или отзывы.'],['Контент товара',record.content_status==='source_text'?'Есть исходное описание: сверить характеристики и полноту перед запуском.':'Использовано редакционное описание задачи: дополнить проверенными характеристиками товара.'],['Фото товара',record.photo_status==='source_photo'?'Есть исходная фотография: подтвердить соответствие товару и право использования.':'Нет подтверждённой товарной фотографии: заменить иллюстрацию направления реальным фото.']);
    if(record.kind==='category')plans.splice(6,0,['Настройки раздела','Проверить набор товаров/подразделов, смысловые H2/H3, интент запросов и пересечения с соседними разделами. CollectionPage отражает раздел; ItemList добавлять только по реальным видимым элементам.']);
    plans.forEach(([k,v])=>row(plan.rows,k,badge('План / проверить'),v));section('Техническое задание к рабочему запуску').append(plan.wrap);
    const structure=detail('Структура H2 / H3');const current=Array.from(document.querySelectorAll('main h2,main h3')).map(x=>({level:x.tagName,text:x.innerText.trim().replace(/\s+/g,' ')}));
    structure.append(compare(current,record.headings,false));const list=el('ol');current.forEach(x=>list.append(el('li',x.level+' · '+x.text)));if(!current.length)structure.append(el('p','Дополнительных заголовков нет.'));structure.append(list);
    const images=detail('Изображения и ALT');const it=table(['Изображение','ALT / загрузка','Проверка']);document.querySelectorAll('main img[src]').forEach(img=>{const tr=el('tr');tr.append(el('td',img.getAttribute('src')),el('td',(img.getAttribute('alt')||'ALT не задан')+' · loading='+(img.getAttribute('loading')||'auto')),el('td',img.complete?(img.naturalWidth?'Загружено':'Не загружено / ошибка'):'Ожидает загрузки'));it.rows.append(tr);});images.append(it.wrap,el('p','ALT должен описывать изображение. Lazy load ниже первого экрана; основное фото загружать без задержки. Плановые пути изображений после переноса нужно подтвердить.','seo-help'));
    const assigned=queries[record.path]||[];querySection('Запросы этой страницы',assigned,record.path,true);
    if(!assigned.length)body.append(el('p','Индивидуальные запросы этой странице пока не назначены. Это задача для кластеризации; частотности не подставляются из другого раздела.','seo-notice'));
    if(record.parent&&(queries[record.parent]||[]).length)querySection('Запросы родительского раздела — только контекст',queries[record.parent],record.parent,false);
    body.append(el('p','Источник: исходная выгрузка Topvisor. Регион не указан, период замера требует подтверждения. Назначение запросов предварительное; требуется проверка выдачи и пересечений. «Нет данных» означает пустую ячейку источника, 0 — исходное нулевое значение.','seo-help'));
    if(record.source)section('Происхождение сведений о товаре').append(el('p',record.source));
    const docs=section('Общие документы');[['Техническое SEO','technical-seo.md'],['Карта миграции','migration.md']].forEach(([name,file])=>{const a=el('a',name);a.href=base+'/review-data/'+file;docs.append(a);});
    function querySection(label,items,url,open) { const d=detail(label+' · '+items.length,open);d.append(el('p',url,'seo-path'));if(!items.length){d.append(el('p','Назначенных запросов нет.'));return;}const qt=table(['Запрос','Базовая','В кавычках','«!»','«[]»','«[!]»','Статус']);items.forEach(item=>{const tr=el('tr');item.slice(0,6).forEach((v,i)=>tr.append(el('td',v===''?'Нет данных':v,i?'seo-number':'')));tr.append(el('td',({provisional:'Предварительно',review:'Проверить',informational:'Информационный',exclude:'Исключён'})[item[6]]||item[6]));qt.rows.append(tr);});d.append(qt.wrap); }
  }
  async function open() {if(!modal.open)modal.showModal();document.body.classList.add('seo-modal-open');body.replaceChildren(el('p','Загружаю паспорт страницы…','seo-notice'));try{const [data,queries]=await load();const record=data.pages[path]||(document.title===data.pages["/404.html"]?.expected.title?data.pages["/404.html"]:null);if(!record)throw Error('Нет паспорта для '+path);render(record,queries);}catch{body.replaceChildren(el('p','Не удалось загрузить полный паспорт. Закройте окно и повторите; краткий SEO-паспорт доступен внизу страницы.','seo-notice'));}}
  button.addEventListener('click',open);fallback.querySelector('summary').addEventListener('click',e=>{e.preventDefault();open();});close.addEventListener('click',()=>modal.close());
  modal.addEventListener('close',()=>{document.body.classList.remove('seo-modal-open');});
  modal.addEventListener('click',e=>{if(e.target===modal){const r=modal.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)modal.close();}});
})();
