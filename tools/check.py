"""Acceptance checks over the complete rendered site, no external requests."""
import csv,json,re,sys,collections
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from classify import match
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'dist';errors=[];titles=collections.defaultdict(list);h1s=collections.defaultdict(list)
files=list(OUT.rglob('*.html'));urls=set();count=0
passports={}
for bucket in range(16):passports.update(json.loads((OUT/f'assets/seo-passports-{bucket}.json').read_text())['pages'])
passport_queries=json.loads((OUT/'assets/seo-queries.json').read_text())
for f in files:
 rel=f.relative_to(OUT).as_posix();url='/'+rel.removesuffix('index.html');urls.add(unquote(url))
 s=BeautifulSoup(f.read_text(),'html.parser')
 record=passports.get(unquote(url))
 if not record:errors.append(f'{rel}: missing full SEO passport')
 else:
  expected=record['expected']
  for key,selector,attribute in [('description','meta[name="description"]','content'),('canonical','link[rel="canonical"]','href'),('robots','meta[name="robots"]','content'),('og_title','meta[property="og:title"]','content'),('og_description','meta[property="og:description"]','content'),('og_image','meta[property="og:image"]','content')]:
   node=s.select_one(selector);actual=node.get(attribute,'') if node else ''
   if expected[key]!=actual:errors.append(f'{rel}: passport {key} differs from HTML')
  if expected['title']!=s.title.get_text() or expected['h1']!=s.h1.get_text(' ',strip=True):errors.append(f'{rel}: passport text mismatch')
  if not record['production']['canonical'].startswith('https://rossantpack.ru/'):errors.append(f'{rel}: missing production canonical plan')

 for selector in ['h1','title','meta[name="description"]','link[rel="canonical"]','meta[name="robots"]']:
  if len(s.select(selector))!=1:errors.append(f'{rel}: expected exactly one {selector}')
 if not s.select_one('.seo-details'):errors.append(f'{rel}: missing SEO inspector')
 if s.select_one('meta[name="robots"]').get('content')!='noindex,nofollow':errors.append(f'{rel}: missing review noindex')
 titles[s.title.get_text()].append(rel);h1s[s.h1.get_text(' ',strip=True)].append(rel)
 heading_counts=collections.Counter(x.get_text(' ',strip=True).casefold() for x in s.find('main').find_all(['h2','h3']))
 if any(n>1 for n in heading_counts.values()):errors.append(f'{rel}: duplicate H2/H3')
 inspector=s.select_one('.seo-details')
 if inspector and f'<b>H1:</b> {s.h1.get_text(" ",strip=True)}' not in str(inspector):errors.append(f'{rel}: inspector H1 mismatch')
 for node in s.select('script[type="application/ld+json"]'):
  try:
   data=json.loads(node.string or node.get_text());raw=json.dumps(data)
   if any('"'+x+'"' in raw for x in ['Offer','AggregateOffer','price','aggregateRating','review']):errors.append(f'{rel}: unverified commercial schema')
  except ValueError:errors.append(f'{rel}: invalid JSON-LD')
 for el in s.select('[href],img[src],script[src]'):
  value=el.get('href') or el.get('src');u=urlsplit(value)
  if u.scheme or u.netloc:continue
  path=unquote(u.path)
  if path.startswith('/rossantoakru/'):path=path[len('/rossantoakru'):]
  target=(OUT/path.lstrip('/')) if path.startswith('/') else (f.parent/path)
  if path.endswith('/') or target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(f'{rel}: missing {value}')
  elif u.fragment and target.suffix=='.html':
   dest=s if target==f else BeautifulSoup(target.read_text(),'html.parser')
   if not dest.find(id=unquote(u.fragment)):errors.append(f'{rel}: missing fragment {value}')
  count+=1
 if re.search(r'(?:\d[\d\s,.]*\s*(?:руб|₽)|в наличии|TSolution|Stack trace|Fatal error|/home/o143039)',s.get_text(' ',strip=True),re.I):errors.append(f'{rel}: source price, availability or error leaked')
 for el in s.select('article.prose [style],article.prose script,article.prose iframe'):
  errors.append(f'{rel}: unsafe source markup')
 for el in s.select('article.prose *'):
  if any(k.startswith('on') for k in el.attrs):errors.append(f'{rel}: event handler in source')
for title,paths in titles.items():
 if len(paths)>1:errors.append('Duplicate title: '+title)
for title,paths in h1s.items():
 if len(paths)>1:errors.append('Duplicate H1: '+title)
products=json.loads((ROOT/'data/products.json').read_text());cats=json.loads((ROOT/'data/categories.json').read_text())
for row in products+cats:
 if unquote(row['path']) not in urls:errors.append('Lost catalogue URL '+row['path'])
legacy=json.loads((ROOT/'data/source/catalog-2026-11-05.json').read_text())
for row in legacy:
 if unquote(row['path']) not in urls:errors.append('Lost archive URL '+row['path'])
with (ROOT/'data/source/topvisor.csv').open(encoding='utf-8-sig',newline='') as f:source=[r for r in list(csv.reader(f,delimiter=';'))[2:] if r and r[0].strip()]
with (ROOT/'docs/query_map.csv').open(encoding='utf-8-sig',newline='') as f:mapped=list(csv.DictReader(f,delimiter=';'))
if len(source)!=3182 or len(mapped)!=len(source):errors.append('Query count changed')
for a,b in zip(source,mapped):
 if a[0]!=b['query'] or a[1:6]!=[b[k] for k in ['broad','quoted','exact_morph','bracket','bracket_exact']]:errors.append('Query or metric changed: '+a[0])
 if b['target_url'] and b['target_url'] not in urls:errors.append('Query target missing: '+b['target_url'])
expected_queries=collections.defaultdict(list)
for r in mapped:
 if r['target_url']:expected_queries[r['target_url']].append([r[k] for k in ['query','broad','quoted','exact_morph','bracket','bracket_exact','status','intent','comment']])
if dict(expected_queries)!=passport_queries:errors.append('SEO passport query frequencies or assignments changed')
if set(passports)!=urls:errors.append('SEO passport coverage mismatch')
examples={'коробка с ложементом':'/product/korobki/korobki-s-lozhementom/','подарочная коробка с ложементом':'/product/korobki/podarochnye-korobki-s-lozhementom/','пластиковый ложемент':'/product/lozhementy/lozhementy-iz-plastika1/','ложемент без материала':'/product/lozhementy/','ложемент из eva':'/product/lozhementy/lozhementy-iz-materiala-eva/','eva вставки в кейс':'/product/lozhementy/lozhementy-iz-materiala-eva/','упаковка для духов':'/product/purpose/upakovka-dlya-dukhov/','упаковка для косметики':'/product/purpose/upakovka-dlya-kosmetiki-7763/','крышки для банок':'','как выбрать ложемент':''}
for q,expected in examples.items():
 if match(q)[0]!=expected:errors.append('Wrong intent: '+q)
if 'Disallow: /' not in (OUT/'robots.txt').read_text():errors.append('Review robots missing')
report={'html_pages':len(files),'categories':len(cats),'products':len(products),'queries':len(mapped),'seo_passports':len(passports),'internal_references_checked':count,'errors':errors,'status':'PASS' if not errors else 'FAIL'}
(ROOT/'docs/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(errors))
