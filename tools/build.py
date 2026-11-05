import csv,json,html,re,os,shutil,collections
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'dist'; DATA=ROOT/'data'; DOC=ROOT/'docs'
DOMAIN='https://rossantpack.ru'; BRAND='Россантпак'; BASE='/rossantoakru' if os.environ.get('PAGES')=='1' else ''
TELEPHONE='+7 (499) 110-27-82'; EMAIL='order@rossantpack.ru'

def esc(s): return html.escape(str(s or ''),quote=True)
def link(path):return BASE+path

def load():
 return json.loads((DATA/'categories.json').read_text()),json.loads((DATA/'products.json').read_text())

def card(name,path,tag='Направление',sub='Изготовление упаковки на заказ'):
 return f'<a class="tile" href="{esc(link(path))}"><div class="tile-icon">▧</div><span class="eyebrow">{esc(tag)}</span><h3>{esc(name)}</h3><p>{esc(sub)}</p><span class="tile-link">Подробнее <span>↗</span></span></a>'

def template(path,title,desc,h1,content,breadcrumbs=None,schema=None, kind='website'):
 breadcrumbs=breadcrumbs or [('Главная','/')]; bcs=''.join(f'<a href="{esc(link(url))}">{esc(t)}</a><span>/</span>' for t,url in breadcrumbs)+f'<span>{esc(h1)}</span>'
 canonical=DOMAIN+path; pageuri=link(path); scripts=[{'@context':'https://schema.org','@type':'Organization','name':BRAND,'url':DOMAIN,'telephone':TELEPHONE,'email':EMAIL,'address':{'@type':'PostalAddress','addressCountry':'RU','addressRegion':'Московская область','addressLocality':'Дедовск','streetAddress':'Центральная пл., д. 1','postalCode':'143530'}}]
 if schema:scripts.append(schema)
 scripts.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':name,'item':DOMAIN+url} for i,(name,url) in enumerate(breadcrumbs+[(h1,path)])]})
 jsonld='\n'.join('<script type="application/ld+json">'+json.dumps(x,ensure_ascii=False).replace('<','\\u003c')+'</script>' for x in scripts)
 seo=f'<details class="seo-details"><summary>SEO страницы · посмотреть</summary><p><b>URL:</b> {esc(path)}</p><p><b>Title:</b> {esc(title)}</p><p><b>Description:</b> {esc(desc)}</p><p><b>H1:</b> {esc(h1)}</p><p><b>Canonical:</b> {esc(canonical)}</p><p>Прототип: <b>noindex</b>. Значения нужно проверить перед запуском.</p></details>'
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canonical)}"><link rel="icon" href="{link('/assets/favicon.svg')}"><link rel="stylesheet" href="{link('/assets/style.css')}">{jsonld}</head><body><div class="topbar"><div class="wrap top-inner"><span>Производство упаковки под задачи бизнеса</span><a href="tel:+74991102782">{TELEPHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div></div><header class="header"><div class="wrap nav"><a class="logo" href="{link('/')}"><span class="logo-shape">◈</span>РОССАНТ<span>ПАК</span><small>ЭФФЕКТИВНЫЕ УПАКОВОЧНЫЕ РЕШЕНИЯ</small></a><button class="menu-button" id="menu" aria-expanded="false" aria-controls="links">☰</button><nav id="links" class="navlinks"><a href="{link('/product/')}">Каталог</a><a href="{link('/manufacture/')}">Производство</a><a href="{link('/services/')}">Услуги</a><a href="{link('/materials/')}">Материалы</a><a href="{link('/contacts/')}">Контакты</a></nav><a class="btn btn-dark nav-cta" href="{link('/request/')}">Рассчитать проект <span>↗</span></a></div></header><main><div class="wrap"><div class="breadcrumbs">{bcs}</div></div>{content}</main><footer><div class="wrap footer-grid"><div><div class="footer-logo">РОССАНТ<span>ПАК</span></div><p>Изготовление упаковки на заказ. Проектная и серийная продукция.</p><p class="muted">Демонстрационная версия для согласования. Не является действующим интернет-магазином.</p></div><div><b>Каталог</b><a href="{link('/product/lozhementy/')}">Ложементы</a><a href="{link('/product/korobki/')}">Коробки</a><a href="{link('/product/plastikovaya-upakovka/')}">Пластиковая упаковка</a><a href="{link('/product/purpose/')}">По назначению</a></div><div><b>Связаться</b><a href="tel:+74991102782">{TELEPHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><p>Московская область, Дедовск, Центральная пл., д. 1</p><a href="{link('/seo/')}">SEO-карта прототипа</a></div></div></footer><script src="{link('/assets/app.js')}"></script></body></html>'''

def write(path,s):
 p=OUT/path.lstrip('/');p=p/'index.html' if path.endswith('/') else p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')

def section_intro(title,text,light=False):return f'<section class="intro {"soft" if light else ""}"><div class="wrap"><span class="eyebrow">РОССАНТПАК / ПРОИЗВОДСТВО</span><h1>{esc(title)}</h1><p class="lead">{esc(text)}</p><div class="intro-actions"><a class="btn btn-primary" href="{link("/request/")}">Запросить расчёт <span>↗</span></a><a class="btn btn-outline" href="{link("/product/")}">Весь каталог</a></div></div></section>'

def blocks(heading,para,items):return f'<section class="section"><div class="wrap"><div class="section-kicker">О решении</div><h2>{esc(heading)}</h2><p class="section-intro">{esc(para)}</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],sub=x.get('summary','Подбор решения под проект')) for x in items)+'</div></div></section>'

def checklist(name):return f'''<section class="section pale"><div class="wrap split"><div><span class="eyebrow">ИНЖЕНЕРНЫЙ ПОДХОД</span><h2>Что нужно для расчёта</h2><p>Стоимость и конструкция зависят от изделия, материала, размеров, объёма партии и условий применения. Укажите исходные параметры — подготовим предметный запрос для отдела продаж.</p><a class="btn btn-dark" href="{link('/request/')}?product={esc(name)}">Запросить расчёт ↗</a></div><div class="steps"><div><b>01</b><span>Фото, чертёж или описание изделия</span></div><div><b>02</b><span>Габариты и технические требования</span></div><div><b>03</b><span>Тираж, условия перевозки и срок</span></div><div><b>04</b><span>Способ связи для уточнения деталей</span></div></div></div></section>'''

def cat_page(cat,cats,products):
 name=cat['name'];path=cat['path'];children=[x for x in cats if x['path']!=path and x.get('parent')==path];goods=[x for x in products if x.get('category')==path]; near=[x for x in cats if x.get('parent')==cat.get('parent') and x['path']!=path][:4]
 intro=cat.get('summary') or f'{name} для защитной, транспортной или презентационной упаковки. Изделия подбираются по размерам, форме продукции и условиям применения; стоимость рассчитывается по запросу.'
 content=section_intro(name,intro)
 if children:content+=blocks('Виды и варианты',f'Выберите направление в категории «{name}».',children)
 if goods:content+=f'<section class="section"><div class="wrap"><div class="section-kicker">Изделия</div><h2>Примеры продукции</h2><p class="section-intro">Подтверждённые позиции старого каталога. Совместимость и возможность изготовления согласовываются по чертежу.</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],'Карточка изделия',x.get('excerpt','Параметры под заказ')) for x in goods)+'</div></div></section>'
 content+=f'''<section class="section"><div class="wrap prose"><h2>Изготовление {esc(name.lower())} на заказ</h2><p>{esc(intro)} При выборе конструкции важно учитывать размеры изделия, требуемую жёсткость и способ размещения в наружной таре. Для промышленной и транспортной упаковки отдельно рассматривают допустимые нагрузки и характер перевозки.</p><h3>Подбор конструкции и материала</h3><p>Техническое решение зависит от геометрии продукции, особенностей сборки, необходимости амортизации и внешнего оформления. Для расчёта подготовьте чертёж или образец, количество и требования к комплектации.</p><h3>Как получить стоимость</h3><p>На сайте нет автоматической корзины и публичной цены, поскольку параметры проекта согласовываются индивидуально. Отправьте заявку и технические данные, чтобы обсудить подходящее исполнение.</p></div></section>'''
 if near:content+=blocks('Смежные направления','Для комплексного проекта могут потребоваться дополнительные упаковочные элементы.',near)
 content+=checklist(name)
 title=f'{name} на заказ — изготовление и производство | Россантпак' if len(name)<50 else f'{name} — производство на заказ | Россантпак';desc=f'{name}: разработка и изготовление упаковки под размеры изделий. Выбор материала, конструкции и партии. Запросить расчёт у Россантпак.'
 ancestors=[];p=cat.get('parent');seen=set();by={x['path']:x for x in cats}
 while p and p not in seen:
  seen.add(p); x=by.get(p)
  if not x:break
  ancestors.insert(0,(x['name'],p));p=x.get('parent')
 write(path,template(path,title,desc,name,content,[('Главная','/'),('Каталог','/product/')]+ancestors,{'@context':'https://schema.org','@type':'CollectionPage','name':name,'url':DOMAIN+path}))

def product_page(p,cats):
 name=p['name'];path=p['path'];cat=next((x for x in cats if x['path']==p['category']),None);raw=p.get('html','');soup=BeautifulSoup(raw,'html.parser');txt=soup.get_text(' ',strip=True);desc=p.get('description') or f'{name}: характеристики и варианты исполнения. Заказ партии и подбор под тубус по техническим параметрам.'
 parts=[]
 for node in soup.find_all(['h2','h3','p','table']):
  if node.find_parent(['table','p','h2','h3']):continue
  if node.name in ('h2','h3'):parts.append(f'<{node.name}>{esc(node.get_text(" ",strip=True))}</{node.name}>')
  elif node.name=='p':
   text=node.get_text(' ',strip=True)
   if text:parts.append('<p>'+esc(text)+'</p>')
  elif node.name=='table':
   rows=[]
   for tr in node.find_all('tr'):
    tds=tr.find_all('td');
    if len(tds)>=2:rows.append(f'<tr><th>{esc(tds[0].get_text(" ",strip=True))}</th><td>{esc(tds[1].get_text(" ",strip=True))}</td></tr>')
   if rows:parts.append('<table class="specs">'+''.join(rows)+'</table>')
 body=section_intro(name,desc)+f'<section class="section"><div class="wrap product-layout"><div class="visual-card"><div class="pack-drawing"><div></div><span>ИЗДЕЛИЕ НА ЗАКАЗ</span></div><small>Схематическая иллюстрация — не фотография товара</small></div><article class="prose"><span class="eyebrow">КАРТОЧКА ПРОДУКЦИИ</span><h2>Описание и характеристики</h2>'+''.join(parts[:75])+f'</article></div></section>'+checklist(name)
 title=p.get('title') or f'{name} — заказать изготовление | Россантпак';schema={'@context':'https://schema.org','@type':'Product','name':name,'description':desc,'brand':{'@type':'Brand','name':BRAND},'url':DOMAIN+path}
 write(path,template(path,title,desc,name,body,[('Главная','/'),('Каталог','/product/'),(cat['name'],cat['path'])] if cat else None,schema,kind='product'))

def build():
 if OUT.exists():shutil.rmtree(OUT)
 OUT.mkdir(); shutil.copytree(ROOT/'site'/'assets',OUT/'assets');(OUT/'.nojekyll').write_text('')
 cats,products=load();rootcats=[x for x in cats if x.get('parent')=='/product/'];hero='''<section class="hero"><div class="wrap hero-flex"><div><span class="eyebrow light">ПРОЕКТИРУЕМ · ПРОИЗВОДИМ · ПОСТАВЛЯЕМ</span><h1>Упаковка, которая <em>работает</em> на ваш продукт</h1><p>Изготовление ложементов, коробок и пластиковой упаковки под параметры изделий. Конструкция и материалы — под задачи защиты, хранения и презентации.</p><div class="hero-buttons"><a class="btn btn-primary" href="'''+link('/request/')+'''">Рассчитать упаковку ↗</a><a class="btn btn-glass" href="'''+link('/product/')+'''">Смотреть каталог</a></div><div class="micro">Производство под заказ · Подбор по техническому заданию</div></div><div class="hero-art"><div class="art-box art-a"></div><div class="art-box art-b"></div><div class="art-insert"></div><span class="art-label">ИНДИВИДУАЛЬНАЯ КОНСТРУКЦИЯ</span></div></div></section>'''
 home=hero+blocks('Каталог упаковочных решений','Разделы сгруппированы по типу изделия; в отдельном каталоге можно выбрать упаковку по назначению.',rootcats)+'''<section class="section pale"><div class="wrap"><span class="eyebrow">ОТ ЗАДАЧИ К ИЗДЕЛИЮ</span><h2>Производство под параметры вашего товара</h2><div class="benefits"><div><b>01</b><h3>Изучаем задачу</h3><p>Габариты, форма, вес и условия использования продукции.</p></div><div><b>02</b><h3>Предлагаем конструкцию</h3><p>Подбираем материал и расположение изделия внутри упаковки.</p></div><div><b>03</b><h3>Согласовываем выпуск</h3><p>Уточняем тираж, комплектацию и параметры производства.</p></div></div></div></section>'''+checklist('Упаковка на заказ')
 write('/',template('/','Производство упаковки на заказ — ложементы, коробки | Россантпак','Россантпак: изготовление ложементов, коробок и пластиковой упаковки на заказ. Разработка конструкций, подбор материалов, расчёт производства.','Упаковка на заказ',home))
 content=section_intro('Каталог упаковки','Выберите тип упаковочного изделия или решение по назначению. Каждая категория содержит техническое описание и возможность запроса расчёта.')+blocks('Основные направления','Каталог построен по группам продукции, материалам и задачам применения.',rootcats)
 write('/product/',template('/product/','Каталог упаковки на заказ — изделия и материалы | Россантпак','Каталог упаковочной продукции: ложементы, коробки, пластиковая упаковка, крышки для тубусов и защитные решения.','Каталог упаковки',content))
 for c in cats:cat_page(c,cats,products)
 for p in products:product_page(p,cats)
 for path,name,desc in [('/manufacture/','Производство упаковки на заказ','Разработка упаковочных решений под форму, размер и задачи применения изделий.'),('/services/','Услуги производства упаковки','Подготовка упаковки под техническое задание: выбор материалов, резка и изготовление деталей.'),('/materials/','Материалы для упаковки','Поролон, ППЭ, изолон, EVA, пластик, картон и пенопласт: выбор материала зависит от задач упаковки.')]:
  b=section_intro(name,desc)+blocks('Посмотреть виды упаковки','Выберите подходящие материалы и конструкции.',rootcats[:5])+checklist(name)
  write(path,template(path,f'{name} | Россантпак',desc,name,b))
 contact=f'<section class="section"><div class="wrap"><h1>Контакты</h1><div class="contact-grid"><div class="contact-box"><h2>Отдел продаж</h2><p><a href="tel:+74991102782">{TELEPHONE}</a></p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><p>Пн. – Пт.: 9:00–18:00</p></div><div class="contact-box"><h2>Адрес</h2><p>143530, Московская область, г. Дедовск, Центральная площадь, д. 1, этаж 1, помещ. 1</p><a class="btn btn-outline" href="{link('/request/')}">Подготовить запрос</a></div></div></div></section>'
 write('/contacts/',template('/contacts/','Контакты отдела продаж | Россантпак','Контакты компании Россантпак: телефон, email отдела продаж, адрес в Дедовске и время работы.','Контакты',contact))
 form=f'''<section class="section"><div class="wrap form-layout"><div><span class="eyebrow">ЗАПРОС ДЛЯ ОТДЕЛА ПРОДАЖ</span><h1>Рассчитать упаковку</h1><p class="lead">Опишите изделие и нужную упаковку. Демо-форма создаёт письмо в вашей почтовой программе; серверная отправка и интеграция с Битрикс24 будут подключены после согласования.</p><ul class="simple-list"><li>Изделие и размеры</li><li>Материал или условия применения</li><li>Планируемое количество</li><li>Контакт для уточнений</li></ul></div><form id="quote-form" class="quote-form"><label>Что нужно изготовить<input name="product" placeholder="Например, ложемент из EVA" required></label><label>Ваше имя<input name="name" placeholder="Как к вам обращаться" required></label><label>Email для ответа<input name="email" type="email" placeholder="name@company.ru" required></label><label>Количество, шт.<input name="quantity" placeholder="Планируемый тираж"></label><label>Описание изделия и требования<textarea name="details" rows="5" placeholder="Размеры, материал, условия перевозки..."></textarea></label><button class="btn btn-primary" type="submit">Сформировать письмо ↗</button><p class="form-note">Отправка заявки на сервер в демоверсии отключена. После нажатия откроется черновик письма; отправить его нужно самостоятельно.</p></form></div></section>'''
 write('/request/',template('/request/','Запросить расчёт упаковки | Россантпак','Запрос расчёта упаковки: укажите изделие, размеры, материал, тираж и технические требования.','Рассчитать упаковку',form))
 counts=collections.Counter(x['status'] for x in csv.DictReader((DOC/'query_map.csv').open(encoding='utf-8-sig'),delimiter=';'))
 seo=section_intro('SEO-паспорт проекта','Структура, таблица ключевых запросов, техническое SEO и управление статусами. Этот раздел предназначен только для согласования.')+f'<section class="section"><div class="wrap"><div class="stats"><div><b>{sum(counts.values())}</b><span>запросов в Topvisor</span></div><div><b>{len(cats)}</b><span>категорий и направлений</span></div><div><b>{len(products)}</b><span>подтверждённых карточек</span></div></div><h2>Материалы для проверки</h2><p>В репозитории: <code>docs/query_map.csv</code>, <code>docs/site_tree.csv</code>, <code>docs/technical-seo.md</code>, <code>docs/migration.md</code>.</p><p>Классификация — первичная, не заменяет региональную проверку выдачи и ручную оценку пересечений кластеров.</p></div></section>'
 write('/seo/',template('/seo/','SEO-карта прототипа Россантпак','Рабочая SEO-карта сайта, структура категорий, карта запросов и технические требования.','SEO-паспорт',seo))
 write('/404.html',template('/404.html','Страница не найдена | Россантпак','Запрошенная страница не найдена. Перейдите в каталог упаковочных решений.','Страница не найдена','<section class="section"><div class="wrap"><h1>Страница не найдена</h1><a class="btn btn-primary" href="'+link('/product/')+'">В каталог</a></div></section>'))
 (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n# Review mode. Remove disallow only when approved and canonical URLs point to production.\n',encoding='utf-8')
 (OUT/'site-manifest.json').write_text(json.dumps({'pages':len(list(OUT.rglob('index.html'))),'categories':len(cats),'products':len(products),'semantics':sum(counts.values()),'status':'review'},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Built:',len(list(OUT.rglob('index.html'))),'pages, categories',len(cats),'products',len(products),'queries',sum(counts.values()))
if __name__=='__main__':build()