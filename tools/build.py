import csv,json,html,re,os,shutil,collections
from pathlib import Path
from urllib.parse import urlparse, quote, unquote
from content import category_content
from editorial import render as render_editorial
PAGES=[]
QUERY_MAP=collections.defaultdict(list)
for row in csv.DictReader((Path(__file__).resolve().parent.parent/"docs/query_map.csv").open(encoding="utf-8-sig"),delimiter=";"):
 if row["target_url"]:QUERY_MAP[row["target_url"]].append(row)
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'dist'; DATA=ROOT/'data'; DOC=ROOT/'docs'
BASE='/rossantoakru' if os.environ.get('PAGES')=='1' else ''
DOMAIN='https://samfinstat.github.io/rossantoakru' if BASE else 'http://localhost:8000'
BRAND='Россантпак'
ALIASES=json.loads((DATA/'url-aliases.json').read_text())
ALIAS_MAP={x['old']:x['new'] for x in ALIASES}
TELEPHONE='+7 (499) 110-27-82'; EMAIL='order@rossantpack.ru'

def esc(s): return html.escape(str(s or ''),quote=True)
def link(path):return BASE+quote(ALIAS_MAP.get(unquote(path),unquote(path)),safe='/#?=&')

def load():
 return json.loads((DATA/'categories.json').read_text()),json.loads((DATA/'products.json').read_text())

def card(name,path,tag='Направление',sub='Изготовление упаковки на заказ',image=''):
 return f'<a class="tile" href="{esc(link(path))}">{(f'<img class="tile-photo" src="{esc(link(image))}" alt="{esc(name)}" loading="lazy" width="400" height="250">' if image else '<div class="tile-icon" aria-hidden="true">▧</div>')}<span class="eyebrow">{esc(tag)}</span><h3>{esc(name)}</h3><p>{esc(sub)}</p><span class="tile-link">Подробнее <span>↗</span></span></a>'

def template(path,title,desc,h1,content,breadcrumbs=None,schema=None, kind='website'):
 h1_node=BeautifulSoup(content,'html.parser').find('h1')
 if h1_node:h1=h1_node.get_text(' ',strip=True)
 if len(title)>65:
  title=title.split(' | Россантпак')[0]
  if len(title)>65:title=title[:62].rsplit(' ',1)[0]+'…'
 if len(desc)>160:desc=desc[:157].rsplit(' ',1)[0].rstrip('.,:;')+'…'
 breadcrumbs=breadcrumbs or [('Главная','/')]; bcs=''.join(f'<a href="{esc(link(url))}">{esc(t)}</a><span>/</span>' for t,url in breadcrumbs)+f'<span>{esc(h1)}</span>'
 canonical=DOMAIN+quote(ALIAS_MAP.get(unquote(path),unquote(path)),safe='/'); pageuri=link(path); scripts=[{'@context':'https://schema.org','@type':'Organization','name':BRAND,'url':'https://rossantpack.ru','telephone':TELEPHONE,'email':EMAIL,'address':{'@type':'PostalAddress','addressCountry':'RU','addressRegion':'Московская область','addressLocality':'Дедовск','streetAddress':'Центральная пл., д. 1','postalCode':'143530'}}]
 if schema:scripts.append(schema)
 scripts.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':DOMAIN+url} for i,(name,url) in enumerate(breadcrumbs+[(h1,path)])]})
 h1_node=BeautifulSoup(content,'html.parser').find('h1')
 if h1_node:h1=h1_node.get_text(' ',strip=True)
 PAGES.append({'url':path,'title':title,'description':desc,'h1':h1,'canonical':canonical,'publish_ready':False})
 jsonld='\n'.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False).replace('<','\\u003c')+'</script>' for x in scripts)
 queries=QUERY_MAP.get(path,[])
 query_html='<ul>'+''.join('<li>'+esc(x['query'])+' <small>('+esc(x['status'])+')</small></li>' for x in queries[:30])+'</ul>'
 headings=BeautifulSoup(content,'html.parser').find_all(['h2','h3'])
 heading_html='<ul>'+''.join('<li>'+x.name.upper()+': '+esc(x.get_text(' ',strip=True))+'</li>' for x in headings)+'</ul>'
 seo=f'<details class="seo-details"><summary>SEO страницы · посмотреть</summary><p><b>URL:</b> {esc(path)}</p><p><b>Title:</b> {esc(title)}</p><p><b>Description:</b> {esc(desc)}</p><p><b>H1:</b> {esc(h1)}</p><p><b>Canonical:</b> {esc(canonical)}</p><p>Прототип: <b>noindex</b>. Всего запросов: {len(queries)}. Назначение предварительное, проверка выдачи не проведена.</p><h3>Заголовки страницы</h3>{heading_html}<h3>Запросы (первые 30)</h3>{query_html}<a href="{link('/review-data/query_map.csv')}" download>Скачать всю карту запросов</a></details>'
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canonical)}"><link rel="icon" href="{link('/assets/favicon.svg')}"><link rel="stylesheet" href="{link('/assets/style.css')}">{jsonld}</head><body><a class="skip-link" href="#main">Перейти к содержимому</a><div class="topbar"><div class="wrap top-inner"><span>Производство упаковки под задачи бизнеса</span><a href="tel:+74991102782">{TELEPHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div></div><header class="header"><div class="wrap nav"><a class="logo" href="{link('/')}"><span class="logo-shape">◈</span>РОССАНТ<span>ПАК</span><small>ЭФФЕКТИВНЫЕ УПАКОВОЧНЫЕ РЕШЕНИЯ</small></a><button class="menu-button" id="menu" aria-label="Открыть меню" aria-expanded="false" aria-controls="links">☰</button><nav id="links" class="navlinks"><a href="{link('/product/')}">Каталог</a><a href="{link('/manufacture/')}">Производство</a><a href="{link('/services/')}">Услуги</a><a href="{link('/materials/')}">Материалы</a><a href="{link('/contacts/')}">Контакты</a></nav><a class="btn btn-dark nav-cta" href="{link('/request/')}">Рассчитать проект <span>↗</span></a></div></header><main id="main"><div class="wrap"><div class="breadcrumbs">{bcs}</div></div>{content}</main><aside class="wrap seo-panel" aria-label="SEO-паспорт">{seo}</aside><footer><div class="wrap footer-grid"><div><div class="footer-logo">РОССАНТ<span>ПАК</span></div><p>Изготовление упаковки на заказ. Проектная и серийная продукция.</p><p class="muted">Демонстрационная версия для согласования. Не является действующим интернет-магазином.</p></div><div><b>Каталог</b><a href="{link('/product/lozhementy/')}">Ложементы</a><a href="{link('/product/korobki/')}">Коробки</a><a href="{link('/product/plastikovaya-upakovka/')}">Пластиковая упаковка</a><a href="{link('/product/purpose/')}">По назначению</a></div><div><b>Связаться</b><a href="{link('/articles/')}">Статьи об упаковке</a><a href="tel:+74991102782">{TELEPHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><p>Московская область, Дедовск, Центральная пл., д. 1</p><a href="{link('/seo/')}">SEO-карта прототипа</a></div></div></footer><script src="{link('/assets/app.js')}"></script></body></html>'''

def write(path,s):
 p=OUT/unquote(path).lstrip('/');p=p/'index.html' if path.endswith('/') else p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(line.rstrip() for line in s.splitlines())+'\n',encoding='utf-8')

def section_intro(title,text,light=False):return f'<section class="intro {"soft" if light else ""}"><div class="wrap"><span class="eyebrow">РОССАНТПАК / ПРОИЗВОДСТВО</span><h1>{esc(title)}</h1><p class="lead">{esc(text)}</p><div class="intro-actions"><a class="btn btn-primary" href="{link("/request/")}">Запросить расчёт <span>↗</span></a><a class="btn btn-outline" href="{link("/product/")}">Весь каталог</a></div></div></section>'

def blocks(heading,para,items):return f'<section class="section"><div class="wrap"><div class="section-kicker">О решении</div><h2>{esc(heading)}</h2><p class="section-intro">{esc(para)}</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],sub=x.get('summary','Подбор решения под проект')) for x in items)+'</div></div></section>'

def checklist(name):return f'''<section class="section pale"><div class="wrap split"><div><span class="eyebrow">ИНЖЕНЕРНЫЙ ПОДХОД</span><h2>Что нужно для расчёта</h2><p>Стоимость и конструкция зависят от изделия, материала, размеров, объёма партии и условий применения. Укажите исходные параметры — подготовим предметный запрос для отдела продаж.</p><a class="btn btn-dark" href="{link('/request/')}?product={esc(quote(name))}">Запросить расчёт ↗</a></div><div class="steps"><div><b>01</b><span>Фото, чертёж или описание изделия</span></div><div><b>02</b><span>Габариты и технические требования</span></div><div><b>03</b><span>Тираж, условия перевозки и срок</span></div><div><b>04</b><span>Способ связи для уточнения деталей</span></div></div></div></section>'''

def cat_page(cat,cats,products):
 name=cat['name'];path=cat['path'];children=[x for x in cats if x['path']!=path and x.get('parent')==path];goods=[x for x in products if x.get('category')==path]; near=[x for x in cats if x.get('parent')==cat.get('parent') and x['path']!=path][:4]
 intro=cat.get('summary') or f'{name} для защитной, транспортной или презентационной упаковки. Изделия подбираются по размерам, форме продукции и условиям применения; стоимость рассчитывается по запросу.'
 content=section_intro(name,intro)
 if children:content+=blocks('Виды и варианты',f'Выберите направление в категории «{name}».',children)
 if goods:content+=f'<section class="section"><div class="wrap"><div class="section-kicker">Изделия</div><h2>Примеры продукции</h2><p class="section-intro">Примеры из ранее сохранённого каталога. Характеристики и возможность повторного изготовления уточняются по запросу.</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],'Карточка изделия',x.get('excerpt','Параметры под заказ'),x.get('image','')) for x in goods)+'</div></div></section>'
 content+=category_content(cat,link)
 if near:content+=blocks('Смежные направления','Для комплексного проекта могут потребоваться дополнительные упаковочные элементы.',near)
 content+=checklist(name)
 title=f'{name} на заказ | Россантпак';desc=cat.get('tagline') or intro
 desc=desc+' Изготовление по размерам изделия, подбор конструкции и расчёт партии в Россантпак.'
 ancestors=[];p=cat.get('parent');seen=set();by={x['path']:x for x in cats}
 while p and p not in seen:
  seen.add(p); x=by.get(p)
  if not x:break
  ancestors.insert(0,(x['name'],p));p=x.get('parent')
 write(path,template(path,title,desc,name,content,[('Главная','/'),('Каталог','/product/')]+ancestors,{'@context':'https://schema.org','@type':'CollectionPage','name':name,'url':DOMAIN+path}))

def product_page(p,cats):
 name=p['name'];path=p['path'];cat=next((x for x in cats if x['path']==p['category']),None);raw=p.get('html','');soup=BeautifulSoup(raw,'html.parser');txt=soup.get_text(' ',strip=True);desc=p.get('description') or f'{name}: характеристики и варианты исполнения. Заказ партии и подбор под тубус по техническим параметрам.'
 clean=sanitize_html(raw)
 if not clean:
  topic=cat['name'] if cat else 'Упаковка'
  clean=f'<h2>{esc(name)}: подбор исполнения</h2><p>В каталоге сохранён пример «{esc(name)}» из направления «{esc(topic)}». Его можно использовать как отправную точку для технического задания. Размеры, материал и комплектацию конкретного заказа необходимо согласовать отдельно.</p>'
  if cat:clean+=category_content(cat,link).replace('<section class="section"><div class="wrap prose">','').replace('</div></section>','')
 image=p.get('image','')
 visual=f'<img class="product-photo" src="{esc(link(image))}" alt="{esc(name)}" width="600" height="450">' if image else '<div class="pack-drawing"><div></div><span>ФОТО УТОЧНЯЕТСЯ</span></div>'
 body=section_intro(name,desc)+f'<section class="section"><div class="wrap product-layout"><div class="visual-card">{visual}<small>'+('Фото из сохранённого каталога Россантпак' if image else 'Фото изделия отсутствует в доступных источниках')+'</small></div><article class="prose"><span class="eyebrow">ПРИМЕР ПРОДУКЦИИ</span><h2>Описание и характеристики</h2>'+clean+f'</article></div></section>'+checklist(name)
 title=p.get('title') or f'{name} | Россантпак'
 schema={'@context':'https://schema.org','@type':'Product','name':name,'description':desc,'brand':{'@type':'Brand','name':BRAND},'url':DOMAIN+quote(path,safe='/')}
 if image:schema['image']='https://samfinstat.github.io/rossantoakru'+quote(image,safe='/')
 write(path,template(path,title,desc,name,body,[('Главная','/'),('Каталог','/product/'),(cat['name'],cat['path'])] if cat else None,schema,kind='product'))

def sanitize_html(raw):
 soup=BeautifulSoup(raw,'html.parser')
 for node in soup(['script','style','iframe','object','embed','form','input','button']):node.decompose()
 for node in soup.find_all(['h2','h3']):
  text=node.get_text(' ',strip=True)
  clean=re.sub(r'\s*[—–-]?\s*от\s+\d[\d\s,.]*\s*(?:₽|руб\w*).*$','',text,flags=re.I)
  if clean!=text:node.clear();node.string=clean
 seen_headings=set()
 for node in soup.find_all(['h2','h3']):
  text=node.get_text(' ',strip=True)
  if text.casefold() in seen_headings:
   node.clear();node.string='Условия заказа: '+text[:1].lower()+text[1:]
  seen_headings.add(text.casefold())
 for node in list(soup.find_all(['p','li','tr'])):
  if node.parent is None:continue
  text=node.get_text(' ',strip=True)
  if re.search(r'(?:\d[\d\s,.]*\s*(?:руб|₽)|в наличии)',text,re.I):
   if node.name=='tr':node.decompose()
   else:node.clear();node.string='Стоимость и возможность изготовления уточняются по размерам изделия, комплектации и объёму партии.'

 allowed={'h2','h3','p','table','thead','tbody','tr','th','td','ul','ol','li','strong','em','b','br','a'}
 for node in list(soup.find_all(True)):
  if node.name not in allowed:node.unwrap();continue
  href=node.get('href','');node.attrs={}
  if node.name=='table':node['class']='specs'
  if node.name=='a':
   parsed=urlparse(href)
   if parsed.netloc in ('rossantpack.ru','www.rossantpack.ru') or (not parsed.scheme and href.startswith('/')):
    target=unquote(parsed.path)
    if target in KNOWN:node['href']=link(target)+('#'+parsed.fragment if parsed.fragment else '')
    else:node.unwrap()
   else:node.unwrap()
 return str(soup)

def build():
 if OUT.exists():shutil.rmtree(OUT)
 OUT.mkdir(); shutil.copytree(ROOT/'site'/'assets',OUT/'assets');(OUT/'.nojekyll').write_text('')
 global KNOWN
 cats,products=load();KNOWN={x['path'] for x in cats+products}|{'/','/product/','/manufacture/','/services/','/materials/','/contacts/','/request/'}
 rootcats=[x for x in cats if x.get('parent')=='/product/'];hero='''<section class="hero"><div class="wrap hero-flex"><div><span class="eyebrow light">ПРОЕКТИРУЕМ · ПРОИЗВОДИМ · ПОСТАВЛЯЕМ</span><h1>Упаковка на заказ <em>под ваше изделие</em></h1><p>Изготовление ложементов, коробок и пластиковой упаковки под параметры изделий. Конструкция и материалы — под задачи защиты, хранения и презентации.</p><div class="hero-buttons"><a class="btn btn-primary" href="'''+link('/request/')+'''">Рассчитать упаковку ↗</a><a class="btn btn-glass" href="'''+link('/product/')+'''">Смотреть каталог</a></div><div class="micro">Производство под заказ · Подбор по техническому заданию</div></div><div class="hero-art"><div class="art-box art-a"></div><div class="art-box art-b"></div><div class="art-insert"></div><span class="art-label">ИНДИВИДУАЛЬНАЯ КОНСТРУКЦИЯ</span></div></div></section>'''
 home=hero+blocks('Каталог упаковочных решений','Разделы сгруппированы по типу изделия; в отдельном каталоге можно выбрать упаковку по назначению.',rootcats)+'''<section class="section pale"><div class="wrap"><span class="eyebrow">ОТ ЗАДАЧИ К ИЗДЕЛИЮ</span><h2>Производство под параметры вашего товара</h2><div class="benefits"><div><b>01</b><h3>Изучаем задачу</h3><p>Габариты, форма, вес и условия использования продукции.</p></div><div><b>02</b><h3>Предлагаем конструкцию</h3><p>Подбираем материал и расположение изделия внутри упаковки.</p></div><div><b>03</b><h3>Согласовываем выпуск</h3><p>Уточняем тираж, комплектацию и параметры производства.</p></div></div></div></section>'''+checklist('Упаковка на заказ')
 write('/',template('/','Производство упаковки на заказ — ложементы, коробки | Россантпак','Россантпак: изготовление ложементов, коробок и пластиковой упаковки на заказ. Разработка конструкций, подбор материалов, расчёт производства.','Упаковка на заказ',home))
 content=section_intro('Каталог упаковки','Выберите тип упаковочного изделия или решение по назначению. Каждая категория содержит техническое описание и возможность запроса расчёта.')+blocks('Основные направления','Каталог построен по группам продукции, материалам и задачам применения.',rootcats)
 write('/product/',template('/product/','Каталог упаковки на заказ — изделия и материалы | Россантпак','Каталог упаковочной продукции: ложементы, коробки, пластиковая упаковка, крышки для тубусов и защитные решения.','Каталог упаковки',content))
 for c in cats:cat_page(c,cats,products)
 for p in products:product_page(p,cats)
 for alias in ALIASES:
  name=alias['name'];path=alias['old']
  body=f'<section class="section"><div class="wrap"><h1>{esc(name)}: прежний адрес</h1><p>Актуальное описание и запрос расчёта доступны в основной карточке.</p><a class="btn btn-primary" href="{esc(link(alias["new"]))}">Открыть карточку</a></div></section>'
  write(path,template(path,name+' — прежний адрес | Россантпак','Переход к основной карточке: '+name,name,body))
 render_editorial(globals())
 name='Производство упаковки на заказ';desc='Разработка конструкций и изготовление упаковки под размеры и условия использования изделий.'
 body=section_intro(name,desc)+blocks('Что изготавливаем','Выберите тип упаковки для вашего проекта.',rootcats)+checklist(name)
 write('/manufacture/',template('/manufacture/',name+' | Россантпак',desc,name,body))

 contact=f'<section class="section"><div class="wrap"><h1>Контакты</h1><div class="contact-grid"><div class="contact-box"><h2>Отдел продаж</h2><p><a href="tel:+74991102782">{TELEPHONE}</a></p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><p>Пн. – Пт.: 9:00–18:00</p></div><div class="contact-box"><h2>Адрес</h2><p>143530, Московская область, г. Дедовск, Центральная площадь, д. 1, этаж 1, помещ. 1</p><a class="btn btn-outline" href="{link('/request/')}">Подготовить запрос</a></div></div></div></section>'
 write('/contacts/',template('/contacts/','Контакты отдела продаж | Россантпак','Контакты компании Россантпак: телефон, email отдела продаж, адрес в Дедовске и время работы.','Контакты',contact))
 form=f'''<section class="section"><div class="wrap form-layout"><div><span class="eyebrow">ЗАПРОС ДЛЯ ОТДЕЛА ПРОДАЖ</span><h1>Рассчитать упаковку</h1><p class="lead">Опишите изделие и нужную упаковку. Демо-форма создаёт письмо в вашей почтовой программе; серверная отправка и интеграция с Битрикс24 будут подключены после согласования.</p><ul class="simple-list"><li>Изделие и размеры</li><li>Материал или условия применения</li><li>Планируемое количество</li><li>Контакт для уточнений</li></ul></div><form id="quote-form" class="quote-form"><label>Что нужно изготовить<input name="product" placeholder="Например, ложемент из EVA" required></label><label>Ваше имя<input name="name" placeholder="Как к вам обращаться" required></label><label>Email для ответа<input name="email" type="email" placeholder="name@company.ru" required></label><label>Количество, шт.<input name="quantity" placeholder="Планируемый тираж"></label><label>Описание изделия и требования<textarea name="details" rows="5" placeholder="Размеры, материал, условия перевозки..."></textarea></label><button class="btn btn-primary" type="submit">Сформировать письмо ↗</button><p class="form-note">Отправка заявки на сервер в демоверсии отключена. После нажатия откроется черновик письма; отправить его нужно самостоятельно.</p></form></div></section>'''
 write('/request/',template('/request/','Запросить расчёт упаковки | Россантпак','Запрос расчёта упаковки: укажите изделие, размеры, материал, тираж и технические требования.','Рассчитать упаковку',form))
 counts=collections.Counter(x['status'] for x in csv.DictReader((DOC/'query_map.csv').open(encoding='utf-8-sig'),delimiter=';'))
 seo=section_intro('SEO-паспорт проекта','Структура, таблица ключевых запросов, техническое SEO и управление статусами. Этот раздел предназначен только для согласования.')+f'<section class="section"><div class="wrap"><div class="stats"><div><b>{sum(counts.values())}</b><span>запросов в Topvisor</span></div><div><b>{len(cats)}</b><span>категорий и направлений</span></div><div><b>{len(products)}</b><span>карточек из источников</span></div></div><h2>Материалы для проверки</h2><ul><li><a href="{link('/review-data/query_map.csv')}" download>Карта всех поисковых запросов</a></li><li><a href="{link('/review-data/site_tree.csv')}" download>Структура и SEO-паспорта страниц</a></li><li><a href="{link('/review-data/audit.md')}">Аудит и результаты доработки</a></li></ul><p>Классификация — первичная, не заменяет региональную проверку выдачи и ручную оценку пересечений кластеров.</p></div></section>'
 write('/seo/',template('/seo/','SEO-карта прототипа Россантпак','Рабочая SEO-карта сайта, структура категорий, карта запросов и технические требования.','SEO-паспорт',seo))
 write('/404.html',template('/404.html','Страница не найдена | Россантпак','Запрошенная страница не найдена. Перейдите в каталог упаковочных решений.','Страница не найдена','<section class="section"><div class="wrap"><h1>Страница не найдена</h1><a class="btn btn-primary" href="'+link('/product/')+'">В каталог</a></div></section>'))
 (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n# Review mode. Remove disallow only when approved and canonical URLs point to production.\n',encoding='utf-8')
 (OUT/'site-manifest.json').write_text(json.dumps({'pages':len(list(OUT.rglob('index.html'))),'categories':len(cats),'products':len(products),'semantics':sum(counts.values()),'status':'review'},ensure_ascii=False,indent=2),encoding='utf-8')
 export_review()
 print('Built:',len(list(OUT.rglob('index.html'))),'pages, categories',len(cats),'products',len(products),'queries',sum(counts.values()))
def export_review():
 with (DOC/'site_tree.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=['url','title','description','h1','canonical','publish_ready'],delimiter=';',lineterminator='\n');writer.writeheader();writer.writerows(PAGES)
 dest=OUT/'review-data';dest.mkdir(exist_ok=True)
 for filename in ['query_map.csv','site_tree.csv','audit.md','technical-seo.md','migration.md']:
  if (DOC/filename).exists():shutil.copyfile(DOC/filename,dest/filename)
 # A review export, deliberately NOT a public sitemap claiming indexability.
 (dest/'url-inventory.json').write_text(json.dumps([p['url'] for p in PAGES],ensure_ascii=False,indent=2))
if __name__=='__main__':build()