"""Build per-page review records from rendered HTML, preserving source frequencies."""
import csv,json
from collections import defaultdict
from urllib.parse import urlsplit,unquote,quote
from bs4 import BeautifulSoup

PRODUCTION='https://rossantpack.ru'

def generate(root,out,base):
 products={p['path']:p for p in json.loads((root/'data/products.json').read_text())}
 cats={p['path']:p for p in json.loads((root/'data/categories.json').read_text())}
 aliases={p['old']:p['new'] for p in json.loads((root/'data/url-aliases.json').read_text())}
 records={};queries=defaultdict(list)
 for r in csv.DictReader((root/'docs/query_map.csv').open(encoding='utf-8-sig'),delimiter=';'):
  if r['target_url']:queries[r['target_url']].append([r[k] for k in ['query','broad','quoted','exact_morph','bracket','bracket_exact','status','intent','comment']])
 for file in sorted(out.rglob('*.html')):
  rel=file.relative_to(out).as_posix();path='/'+rel.removesuffix('index.html')
  soup=BeautifulSoup(file.read_text(),'html.parser');main=soup.select_one('main');product=products.get(path)
  kind='product' if product else 'category' if path in cats or path=='/product/' else 'article' if path.startswith('/articles/') and path!='/articles/' else 'service' if path.startswith('/services/') else 'material' if path.startswith('/materials/') else 'page'
  if path in aliases:kind='redirect'
  elif path=='/404.html':kind='error'
  elif path in ['/seo/','/request/']:kind='utility'
  def meta(selector,attr='content'):
   el=soup.select_one(selector);return el.get(attr,'') if el else ''
  schemas=[]
  for el in soup.select('script[type="application/ld+json"]'):
   schemas.append(json.loads(el.get_text()))
  image=main.select_one('.product-photo') or main.select_one('img[src]')
  asset=image.get('src','') if image else ''
  if base and asset.startswith(base+'/'):asset=asset[len(base):]
  canonical_path=aliases.get(path,path)
  canonical=PRODUCTION+quote(canonical_path,safe='/')
  indexable=kind not in ['redirect','error','utility']
  parents=[]
  if product:parents=[product['category']]
  elif path in cats and cats[path].get('parent'):parents=[cats[path]['parent']]
  record={'path':path,'kind':kind,'name':soup.h1.get_text(' ',strip=True),'parent':parents[0] if parents else '',
   'expected':{'title':soup.title.get_text(),'description':meta('meta[name="description"]'),'h1':soup.h1.get_text(' ',strip=True),'h1_count':len(main.select('h1')),'robots':meta('meta[name="robots"]'),'canonical':meta('link[rel="canonical"]','href'),'og_title':meta('meta[property="og:title"]'),'og_description':meta('meta[property="og:description"]'),'og_url':meta('meta[property="og:url"]'),'og_type':meta('meta[property="og:type"]'),'og_image':meta('meta[property="og:image"]'),'schema_types':[x.get('@type','') for x in schemas]},
   'production':{'canonical':canonical,'robots':'index,follow — только после приёмки' if indexable else 'noindex,follow' if kind!='redirect' else 'HTTP 301 вместо HTML-страницы','http':'301 → '+canonical if kind=='redirect' else '404 для несуществующего адреса' if kind=='error' else '200 OK','sitemap':indexable,'og_image':PRODUCTION+quote(unquote(asset),safe='/') if asset else ''},
   'headings':[{'level':x.name.upper(),'text':x.get_text(' ',strip=True)} for x in main.select('h2,h3')],
   'images':[{'src':x.get('src',''),'alt':x.get('alt','')} for x in main.select('img[src]')],
   'content_status':product.get('content_status','') if product else '',
   'photo_status':product.get('photo_status','') if product else '',
   'source':product.get('source','') if product else '',
   'redirects_from':[old for old,new in aliases.items() if new==path]}
  records[path]=record
 for bucket in range(16):
  payload={'version':1,'mode':'review','production_origin':PRODUCTION,'pages':{k:v for k,v in records.items() if sum(map(ord,k))%16==bucket}}
  (out/f'assets/seo-passports-{bucket}.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
 (out/'assets/seo-queries.json').write_text(json.dumps(dict(queries),ensure_ascii=False,separators=(',',':')))
 print('SEO passports:',len(records),'query assignments:',sum(map(len,queries.values())))
