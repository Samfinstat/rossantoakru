import csv,json,html,re,os,shutil,collections
from pathlib import Path
from urllib.parse import urlparse, quote, unquote
from content import category_content
from editorial import render as render_editorial
from home import render as render_home
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


def illustration_for(text):
 text=text.lower()
 for keys,asset in [(('krysh','крыш','caps'),'caps'),(('porolonovye-ruki','руки','рук болель'),'hands'),(('lozhem','ложем','foam'),'foam'),(('korob','короб'),'boxes'),(('plastik','пластик','тубус','блистер','коррекс'),'plastic'),(('material','материал'),'materials'),(('manufact','производ','services','услуг','расч','контакт'),'process')]:
  if any(k in text for k in keys):return '/assets/design/'+asset+'.webp'
 return '/assets/design/hero.webp'

def picture(asset,alt,css='section-photo',eager=False):
 return f'<img class="{css}" src="{esc(link(asset))}" alt="{esc(alt)}" width="960" height="720" loading="{"eager" if eager else "lazy"}" decoding="async">'

def menu_html(current):
 cats,_=load();roots=[c for c in cats if c.get('parent')=='/product/']
 groups=''.join('<div class="menu-group"><a class="menu-group-title" href="'+link(c['path'])+'">'+esc(c['name'])+' →</a>'+''.join('<a href="'+link(x['path'])+'">'+esc(x['name'])+'</a>' for x in cats if x.get('parent')==c['path'])+'</div>' for c in roots)
 links=[('Ложементы','/product/lozhementy/'),('Коробки','/product/korobki/'),('Пластиковая упаковка','/product/plastikovaya-upakovka/'),('Крышки','/product/kryshki-dlya-tubusov/'),('Поролоновые руки','/product/porolonovye-ruki/'),('Производство','/manufacture/'),('Услуги','/services/'),('Материалы','/materials/'),('Контакты','/contacts/')]
 direct=''.join('<a '+('aria-current="page" ' if current.startswith(url) else '')+'href="'+link(url)+'">'+name+'</a>' for name,url in links)
 return f'<header class="header"><div class="wrap head-main"><a class="logo" href="{link("/")}" aria-label="Россантпак — главная"><img src="{link("/assets/logo.svg")}" width="250" height="47" alt="Россантпак"></a><button class="catalog-button" id="catalog-toggle" aria-expanded="false" aria-controls="catalog-panel"><span class="catalog-icon" aria-hidden="true"></span> Каталог</button><form class="site-search" action="{link("/product/")}" role="search"><label class="sr-only" for="site-search">Поиск упаковки</label><input id="site-search" name="q" placeholder="Найти упаковку или материал" autocomplete="off"><button aria-label="Найти" type="submit">⌕</button><div id="search-results" class="search-results" hidden aria-live="polite"></div></form><a class="head-phone" href="tel:+74991102782">{TELEPHONE}<small>Отдел продаж</small></a><a class="btn btn-primary head-cta" href="{link("/request/")}">Запросить расчёт →</a><button class="menu-button" id="menu" aria-label="Открыть меню" aria-expanded="false" aria-controls="links">☰</button></div><nav id="links" class="wrap navlinks" aria-label="Основные разделы">{direct}</nav><div id="catalog-panel" class="catalog-panel" hidden><div class="wrap catalog-panel-inner"><div class="catalog-panel-heading"><a href="{link("/product/")}">Весь каталог упаковки →</a><button id="catalog-close" aria-label="Закрыть каталог">✕</button></div><div class="catalog-groups">{groups}</div></div></div></header>'

def card(name,path,tag='Направление',sub='Изготовление упаковки на заказ',image='',illustration=''):
 actual=bool(image);image=image or illustration or illustration_for(path+' '+name)
 return f'<a class="tile {"product-tile" if actual else "direction-tile"}" href="{esc(link(path))}"><div class="tile-media">{picture(image,name,"tile-photo")}<span class="media-note">{"Фото изделия" if actual else "Иллюстрация решения"}</span></div><div class="tile-copy"><span class="eyebrow">{esc(tag)}</span><h3>{esc(name)}</h3><p>{esc(sub)}</p><span class="tile-link">Подробнее <span aria-hidden="true">→</span></span></div></a>'

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
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canonical)}"><link rel="icon" href="{link('/assets/favicon.svg')}"><link rel="stylesheet" href="{link('/assets/style.css')}">{jsonld}</head><body data-base="{BASE}"><a class="skip-link" href="#main">Перейти к содержимому</a>{menu_html(path)}<main id="main"><div class="wrap"><div class="breadcrumbs">{bcs if path!="/" else ""}</div></div>{content}</main><aside class="wrap seo-panel" aria-label="SEO-паспорт">{seo}</aside><footer><div class="wrap footer-grid"><div><a class="footer-logo" href="{link('/')}"><img src="{link('/assets/logo.svg')}" width="250" height="47" alt="Россантпак"></a><p>Изготовление упаковки на заказ. Проектная и серийная продукция.</p><p class="muted">Демонстрационная версия для согласования. Не является действующим интернет-магазином.</p></div><div><b>Каталог</b><a href="{link('/product/lozhementy/')}">Ложементы</a><a href="{link('/product/korobki/')}">Коробки</a><a href="{link('/product/plastikovaya-upakovka/')}">Пластиковая упаковка</a><a href="{link('/product/purpose/')}">По назначению</a></div><div><b>Связаться</b><a href="{link('/articles/')}">Статьи об упаковке</a><a href="tel:+74991102782">{TELEPHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><p>Московская область, Дедовск, Центральная пл., д. 1</p><a href="{link('/seo/')}">SEO-карта прототипа</a></div></div></footer><dialog id="image-dialog" aria-label="Изображение изделия"><button class="lightbox-close" aria-label="Закрыть изображение">✕</button><img alt=""></dialog><script src="{link('/assets/app.js')}"></script></body></html>'''

def write(path,s):
 p=OUT/unquote(path).lstrip('/');p=p/'index.html' if path.endswith('/') else p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(line.rstrip() for line in s.splitlines())+'\n',encoding='utf-8')

def section_intro(title,text,light=False):
 return f'<section class="intro"><div class="wrap intro-grid"><div><span class="eyebrow">РОССАНТПАК · УПАКОВОЧНЫЕ РЕШЕНИЯ</span><h1>{esc(title)}</h1><p class="lead">{esc(text)}</p><div class="intro-actions"><a class="btn btn-primary" href="{link("/request/")}">Запросить расчёт →</a><a class="text-link" href="{link("/product/")}">Весь каталог →</a></div></div><figure class="intro-figure">{picture(illustration_for(title),title,eager=True)}<figcaption>Иллюстрация решения</figcaption></figure></div></section>'

def blocks(heading,para,items):return f'<section class="section"><div class="wrap"><div class="section-kicker">О решении</div><h2>{esc(heading)}</h2><p class="section-intro">{esc(para)}</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],sub=x.get('summary','Подбор решения под проект')) for x in items)+'</div></div></section>'

def checklist(name):
 return f'<section class="section quote-section"><div class="wrap quote-block"><div class="quote-image">{picture("/assets/design/process.webp","Подбор конструкции и материалов упаковки")}<span class="media-note">Иллюстрация процесса</span></div><div class="quote-copy"><span class="eyebrow">НАЧНЁМ С ВАШЕЙ ЗАДАЧИ</span><h2>Подберём упаковку для вашего изделия</h2><p>Пришлите фото или чертёж, размеры и планируемый тираж. Эти данные помогут обсудить конструкцию, материал и комплектацию.</p><div class="quote-chips"><span>Фото или чертёж</span><span>Размеры</span><span>Тираж</span></div><a class="btn btn-primary" href="{link("/request/")}?product={esc(quote(name))}">Запросить расчёт →</a><a class="quote-phone" href="tel:+74991102782">{TELEPHONE}</a></div></div></section>'

def cat_page(cat,cats,products):
 name=cat['name'];path=cat['path'];children=[x for x in cats if x['path']!=path and x.get('parent')==path];goods=[x for x in products if x.get('category')==path]; near=[x for x in cats if x.get('parent')==cat.get('parent') and x['path']!=path][:4]
 intro=cat.get('summary') or f'{name} для защитной, транспортной или презентационной упаковки. Изделия подбираются по размерам, форме продукции и условиям применения; стоимость рассчитывается по запросу.'
 content=section_intro(name,intro)
 if children:content+=blocks('Виды и варианты',f'Выберите направление в категории «{name}».',children)
 if goods:content+=f'<section class="section"><div class="wrap"><div class="section-kicker">Изделия</div><h2>Примеры продукции</h2><p class="section-intro">Примеры из ранее сохранённого каталога. Характеристики и возможность повторного изготовления уточняются по запросу.</p><div class="cardgrid">'+''.join(card(x['name'],x['path'],'Карточка изделия',x.get('excerpt','Параметры под заказ'),x.get('image','')) for x in goods)+'</div></div></section>'
 content+=category_content(cat,link,picture,illustration_for)
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
 name=p['name'];path=p['path'];cat=next((x for x in cats if x['path']==p['category']),None);desc=p.get('description') or f'{name}: варианты исполнения и подбор под параметры изделия.'
 clean=sanitize_html(p.get('html',''))
 if not clean:clean=f'<p>Размеры, материал и комплектация согласуются для конкретного проекта. Отправьте параметры изделия и планируемое количество для обсуждения исполнения.</p>'
 image=p.get('image','');visual=image or illustration_for(p['category'])
 parsed=BeautifulSoup(clean,'html.parser');rows=[]
 for tr in parsed.select('tr'):
  cells=tr.find_all(['td','th'])
  if len(cells)==2 and cells[0].get_text(strip=True) and cells[1].get_text(strip=True):
   k,v=[x.get_text(' ',strip=True) for x in cells]
   if len(k)<70 and len(v)<160:rows.append((k,v))
 for li in parsed.select('li'):
  value=li.get_text(' ',strip=True)
  if ':' in value:
   k,v=[x.strip() for x in value.split(':',1)]
   if k.lower() in ('материал','цвет','размер','размеры','плотность','диаметр','высота','толщина','исполнение') and v and len(v)<100 and not any(a.lower()==k.lower() for a,b in rows):rows.append((k,v))
 rows=rows[:4]
 if not rows:rows=[('Направление',cat['name'] if cat else 'Упаковка'),('Исполнение','По параметрам вашего проекта'),('Расчёт партии','После уточнения размеров и тиража')]
 spec='<dl class="product-specs">'+''.join('<div><dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd></div>' for k,v in rows)+'</dl>'
 body=f'<section class="product-section"><div class="wrap"><div class="product-card"><div class="product-gallery"><button class="gallery-main" data-zoom="{esc(link(visual))}" aria-label="Увеличить изображение: {esc(name)}">{picture(visual,name,"product-photo",True)}<span class="zoom-hint">Увеличить →</span></button><p class="photo-caption">'+('Фото изделия из каталога Россантпак' if image else 'Иллюстрация направления. Фото этого изделия уточняется.')+f'</p></div><div class="product-info"><a class="eyebrow" href="{link(p["category"])}">{esc(cat["name"] if cat else "Упаковка")}</a><h1>{esc(name)}</h1><p class="product-lead">{esc(desc)}</p>{spec}<div class="product-order"><strong>Изготовление под ваш проект</strong><p>Стоимость рассчитывается по конструкции, материалу и объёму партии.</p><a class="btn btn-primary" href="{link("/request/")}?product={esc(quote(name))}">Запросить расчёт →</a><a class="text-link" href="tel:+74991102782">Обсудить по телефону</a></div></div></div><div class="product-details"><div class="description-head"><span class="eyebrow">ОБ ИЗДЕЛИИ</span><h2>Описание и характеристики</h2></div><details class="product-description"><summary>Читать полное описание <span aria-hidden="true">+</span></summary><article class="prose">{clean}</article></details></div></div></section>'
 related=[x for x in load()[1] if x['category']==p['category'] and x['path']!=path][:4]
 if related:body+=f'<section class="section related"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">СРАВНИТЕ ВАРИАНТЫ</span><h2>Из этого же направления</h2></div><a class="text-link" href="{link(p["category"])}">В раздел →</a></div><div class="cardgrid four">'+''.join(card(x['name'],x['path'],'Изделие','Параметры под ваш проект',x.get('image','')) for x in related)+'</div></div></section>'
 body+=checklist(name)
 title=p.get('title') or f'{name} | Россантпак';schema={'@context':'https://schema.org','@type':'Product','name':name,'description':desc,'brand':{'@type':'Brand','name':BRAND},'url':DOMAIN+quote(path,safe='/')}
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
 rootcats=[x for x in cats if x.get('parent')=='/product/']
 home=render_home(globals(),rootcats,products)
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

 contact=section_intro('Контакты','Обсудим конструкцию, материалы и параметры вашего проекта.')+f'<section class="section"><div class="wrap"><div class="contact-grid"><div class="contact-box"><h2>Отдел продаж</h2><p><a href="tel:+74991102782">{TELEPHONE}</a></p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><p>Пн. – Пт.: 9:00–18:00</p></div><div class="contact-box"><h2>Адрес</h2><p>143530, Московская область, г. Дедовск, Центральная площадь, д. 1, этаж 1, помещ. 1</p><a class="btn btn-outline" href="{link('/request/')}">Подготовить запрос</a></div></div></div></section>'
 write('/contacts/',template('/contacts/','Контакты отдела продаж | Россантпак','Контакты компании Россантпак: телефон, email отдела продаж, адрес в Дедовске и время работы.','Контакты',contact))
 form=f'''<section class="section"><div class="wrap form-layout"><div><span class="eyebrow">ЗАПРОС ДЛЯ ОТДЕЛА ПРОДАЖ</span><h1>Рассчитать упаковку</h1><p class="lead">Опишите изделие и нужную упаковку. Форма подготовит письмо для отдела продаж: вы сможете открыть его в своей почтовой программе или скопировать текст.</p><ul class="simple-list"><li>Изделие и размеры</li><li>Материал или условия применения</li><li>Планируемое количество</li><li>Контакт для уточнений</li></ul><figure class="request-visual">{picture("/assets/design/process.webp","Подготовка запроса на упаковку")}<figcaption>Иллюстрация подготовки проекта</figcaption></figure></div><form id="quote-form" class="quote-form"><label>Что нужно изготовить<input name="product" placeholder="Например, ложемент из EVA" required></label><label>Ваше имя<input name="name" placeholder="Как к вам обращаться" required></label><label>Email для ответа<input name="email" type="email" placeholder="name@company.ru" required></label><label>Количество, шт.<input name="quantity" placeholder="Планируемый тираж"></label><label>Описание изделия и требования<textarea name="details" rows="5" placeholder="Размеры, материал, условия перевозки..."></textarea></label><button class="btn btn-primary" type="submit">Сформировать письмо →</button><p class="form-note">Отправка заявки на сервер в демоверсии отключена. После нажатия откроется черновик письма; отправить его нужно самостоятельно.</p></form></div></section>'''
 write('/request/',template('/request/','Запросить расчёт упаковки | Россантпак','Запрос расчёта упаковки: укажите изделие, размеры, материал, тираж и технические требования.','Рассчитать упаковку',form))
 counts=collections.Counter(x['status'] for x in csv.DictReader((DOC/'query_map.csv').open(encoding='utf-8-sig'),delimiter=';'))
 seo=section_intro('SEO-паспорт проекта','Структура, таблица ключевых запросов, техническое SEO и управление статусами. Этот раздел предназначен только для согласования.')+f'<section class="section"><div class="wrap"><div class="stats"><div><b>{sum(counts.values())}</b><span>запросов в Topvisor</span></div><div><b>{len(cats)}</b><span>категорий и направлений</span></div><div><b>{len(products)}</b><span>карточек из источников</span></div></div><h2>Материалы для проверки</h2><ul><li><a href="{link('/review-data/query_map.csv')}" download>Карта всех поисковых запросов</a></li><li><a href="{link('/review-data/site_tree.csv')}" download>Структура и SEO-паспорта страниц</a></li><li><a href="{link('/review-data/audit.md')}">Аудит и результаты доработки</a></li></ul><p>Классификация — первичная, не заменяет региональную проверку выдачи и ручную оценку пересечений кластеров.</p></div></section>'
 write('/seo/',template('/seo/','SEO-карта прототипа Россантпак','Рабочая SEO-карта сайта, структура категорий, карта запросов и технические требования.','SEO-паспорт',seo))
 write('/404.html',template('/404.html','Страница не найдена | Россантпак','Запрошенная страница не найдена. Перейдите в каталог упаковочных решений.','Страница не найдена','<section class="section"><div class="wrap"><h1>Страница не найдена</h1><a class="btn btn-primary" href="'+link('/product/')+'">В каталог</a></div></section>'))
 (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n# Review mode. Remove disallow only when approved and canonical URLs point to production.\n',encoding='utf-8')
 (OUT/'site-manifest.json').write_text(json.dumps({'pages':len(list(OUT.rglob('index.html'))),'categories':len(cats),'products':len(products),'semantics':sum(counts.values()),'status':'review'},ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/"assets/search-index.json").write_text(json.dumps([{'name':x['name'],'url':link(x['path']),'kind':'Раздел' if x in cats else 'Изделие'} for x in cats+products],ensure_ascii=False))
 export_review()
 from seo_passport import generate
 generate(ROOT,OUT,BASE)
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