"""Merge retained public-source extracts without altering their source records."""
import json,re,hashlib
from pathlib import Path
from urllib.parse import unquote,urlsplit
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
ps=json.loads((ROOT/'data/products.json').read_text());by={unquote(p['path']):p for p in ps}
source=json.loads((ROOT/'data/source/product-content.json').read_text())
for p in source:
 target=by.get(unquote(p['path']))
 if target and p.get('html') and not target.get('html'):
  target['html']=p['html'];target['text_source']=p['url'];target['source_http_status']=p['http_status']
extra=json.loads((ROOT/'data/source/foam-extra.json').read_text())
for p in extra:
 path=unquote(p['path'])
 if path in by:continue
 x={'path':path,'category':p['category'],'name':p['name'],'html':p.get('html',''),'image_source':p.get('image_source',''),'image':p.get('image',''),'source':'Публичный список поролоновых ложементов 06.11.2026','verification':'catalog_listing','publish_ready':False}
 x['description']=p['name']+'. Изготовление по размерам изделия и комплектации. Материал, тираж и условия заказа уточняются при расчёте.'
 if p.get('html'):x.update(text_source='https://rossantpack.ru'+p['path'],source_http_status=p.get('http_status'))
 by[path]=x
for x in by.values():
 x['path']=unquote(x['path'])
 if not x.get('image') and x.get('image_source'):
  u=x['image_source'];name=hashlib.sha256(u.encode()).hexdigest()[:16]+Path(urlsplit(u).path).suffix
  if (ROOT/'site/assets/products'/name).exists():x['image']='/assets/products/'+name
 x['content_status']='source_text' if x.get('html') else 'editorial_brief_needs_product_specs'
 x['photo_status']='source_photo' if x.get('image') else 'missing'
(ROOT/'data/products.json').write_text(json.dumps(list(by.values()),ensure_ascii=False,indent=2))
print('Products',len(by),'source texts',sum(bool(p.get('html')) for p in by.values()),'photos',sum(bool(p.get('image')) for p in by.values()))
