import csv,json,re,collections
from pathlib import Path
from bs4 import BeautifulSoup
BASE=Path(__file__).resolve().parent.parent;D=BASE/'data';DOC=BASE/'docs'
major=[('lozhementy','Ложементы'),('korobki','Коробки'),('plastikovaya-upakovka','Пластиковая упаковка'),('kryshki-dlya-tubusov','Крышки для тубусов'),('porolonovye-ruki','Поролоновые руки'),('purpose','Упаковка по назначению')]
sub={
 'lozhementy': [('lozhementy-iz-porolona','Ложементы из поролона'),('lozhementy-iz-penopolietilenov','Ложементы из вспененного полиэтилена'),('lozhementy-iz-izolona','Ложементы из изолона'),('lozhementy-iz-plastika1','Ложементы из пластика'),('lozhementy-iz-materiala-eva','Ложементы из EVA'),('lozhementy-iz-kartona','Ложементы из картона'),('lozhementy-iz-penoplasta','Ложементы из пенопласта'),('lozhementy-dlya-keysov','Ложементы для кейсов')],
 'korobki': [('gofrokoroba','Гофрокороба'),('kartonnye-korobki','Картонные коробки'),('korobki-iz-mikrogofrokartona','Коробки из микрогофрокартона'),('korobki-iz-perepletnogo-kartona','Коробки из переплётного картона'),('korobki-s-lozhementom','Коробки с ложементом'),('podarochnye-korobki-s-lozhementom','Подарочные коробки с ложементом')],
 'plastikovaya-upakovka': [('blisternaya-upakovka','Блистерная упаковка'),('vakuumnaya-formovka','Вакуумная формовка'),('korreksy','Коррексы'),('lozhementy-iz-plastika','Пластиковые ложементы'),('tubusy','Пластиковые тубусы')],
 'kryshki-dlya-tubusov': [('zhestyanye','Жестяные крышки для тубусов'),('plastikovye','Пластиковые крышки для тубусов')],
 'purpose': [('vkladyshi-dlya-upakovki','Вкладыши для упаковки'),('voennaya-upakovka','Военная упаковка'),('zashchitnaya-upakovka','Защитная упаковка'),('individualnaya-upakovka','Индивидуальная упаковка'),('kombinirovannaya-upakovka','Комбинированная упаковка'),('nakladki-dlya-serverov','Накладки для серверов'),('podarochnaya-upakovka','Подарочная упаковка'),('profili-iz-penoplasta','Профили из пенопласта'),('transportnaya-upakovka','Транспортная упаковка'),('ugolki-iz-penoplasta','Уголки из пенопласта'),('udaroprochnaya-upakovka','Ударопрочная упаковка'),('upakovka-dlya-aviaperevozok-upakovka-dlya-aviatsionnykh-izdeliy-dlya-aviatsii-na-zakaz','Упаковка для авиаперевозок'),('upakovka-dlya-ampul','Упаковка для ампул'),('upakovka-dlya-bokalov-1535','Упаковка для бокалов'),('zaglushki-vstavki-ugolki469','Заглушки, вставки, уголки'),('upakovka-dlya-dukhov','Упаковка для духов'),('upakovka-dlya-zerkal','Упаковка для зеркал'),('upakovka-dlya-kalyanov','Упаковка для кальянов'),('upakovka-dlya-keramiki','Упаковка для керамики'),('upakovka-dlya-kosmetiki-7763','Упаковка для косметики'),('upakovka-dlya-krupnogabaritnykh-gruzov-i-tovarov','Упаковка для крупногабаритных грузов'),('novogodnyaya-upakovka394','Новогодняя упаковка'),('upakovka-dlya-meditsinskikh-izdeliy9560','Упаковка для медицинских изделий'),('upakovka-dlya-santekhniki-9530','Упаковка для сантехники'),('upakovka-dlya-svetilnikov','Упаковка для светильников'),('upakovka-dlya-stomatologii9142','Упаковка для стоматологии'),('upakovka-dlya-ukrasheniy','Упаковка для украшений'),('upakovka-dlya-flakonov','Упаковка для флаконов'),('upakovka-dlya-khrupkogo7733','Упаковка для хрупкого'),('upakovka-dlya-chasov','Упаковка для часов'),('upakovka-iz-tverdogo-penoplasta','Упаковка из твёрдого пенопласта'),('upakovka-kompyuterov','Упаковка компьютеров'),('upakovka-mikroskhem','Упаковка микросхем'),('flokirovannaya-upakovka','Флокированная упаковка')]
}
cats=[]
for slug,name in major:
 path=f'/product/{slug}/';cats.append({'name':name,'path':path,'parent':'/product/'})
 for sl,n in sub.get(slug,[]):cats.append({'name':n,'path':path+sl+'/','parent':path})
(D/'categories.json').write_text(json.dumps(cats,ensure_ascii=False,indent=2))
with open('/mnt/data/reference/Kryshki_tubusov_01_Tovary.csv',encoding='utf-8-sig',newline='') as f: content={row['IE_XML_ID']:row['IE_DETAIL_TEXT'] for row in csv.DictReader(f,delimiter=';')}
with open('/mnt/data/reference/Kryshki_tubusov_02_SEO.csv',encoding='utf-8-sig',newline='') as f:
 pro=[]
 for row in csv.DictReader(f,delimiter=';'):
  if not row.get('URL','').startswith('https://rossantpack.ru/'):continue
  path=row['URL'].replace('https://rossantpack.ru','');parent=path.rsplit('/',2)[0]+'/'
  pro.append({'id':row['IE_XML_ID'],'name':row['ELEMENT_PAGE_TITLE'] or row['IE_NAME'],'path':path,'category':parent,'title':row['ELEMENT_META_TITLE'],'description':row['ELEMENT_META_DESCRIPTION'],'html':content.get(row['IE_XML_ID'],'')})
(D/'products.json').write_text(json.dumps(pro,ensure_ascii=False,indent=2))
with open('/mnt/data/Россантпак все запросы.csv',encoding='cp1251',newline='') as f:rows=list(csv.reader(f,delimiter=';'))
header=['id','query','broad','quoted','exact_morph','bracket','bracket_exact','target_url','cluster','status','intent','comment']
pat=[(p,terms) for p,terms in [('lozhementy',[r'ложемент',r'ложемант']),('korobki',[r'короб',r'гофро',r'картонн']),('plastikovaya-upakovka',[r'блистер',r'коррекс',r'вакуумн.*формов',r'пластиков.*упаков',r'тубус']),('kryshki-dlya-tubusov',[r'крышк.*тубус',r'крышк.*туб']),('porolonovye-ruki',[r'поролонов.*рук',r'поролонов.*перчат']),('purpose',[r'упаков',r'вкладыш',r'вставк',r'профил',r'уголк'])]]
exceptions=[r'работ[ауы]|ваканс|своими руками|как сделать|чертеж бесплатно|скачать|фото бесплатно|авито|озон|wildberries|купить одну|1 шт|шаблон для печати|реферат|определение слова']
rowsout=[]
for i,row in enumerate(rows[2:],1):
 if not row or not row[0].strip():continue
 q=row[0].strip();l=q.lower();cat=None
 if re.search(r'крышк.{0,20}тубус|тубус.{0,20}крышк',l):cat='kryshki-dlya-tubusov'
 if not cat:
  for p,terms in pat:
   if any(re.search(t,l) for t in terms):cat=p;break
 target=f'/product/{cat}/' if cat else ''
 if cat=='lozhementy':
  for t,slug in [(r'поролон','lozhementy-iz-porolona'),(r'пенополиэтилен|ппэ|вспененн','lozhementy-iz-penopolietilenov'),(r'изолон','lozhementy-iz-izolona'),(r'\bэва\b|\beva\b','lozhementy-iz-materiala-eva'),(r'пенопласт','lozhementy-iz-penoplasta'),(r'картон','lozhementy-iz-kartona'),(r'кейс','lozhementy-dlya-keysov')]:
   if re.search(t,l):target+=slug+'/';break
 if cat=='korobki':
  for t,slug in [(r'микрогофр','korobki-iz-mikrogofrokartona'),(r'гофр','gofrokoroba'),(r'переплёт|переплет','korobki-iz-perepletnogo-kartona'),(r'ложемент','korobki-s-lozhementom'),(r'подарочн','podarochnye-korobki-s-lozhementom'),(r'картон','kartonnye-korobki')]:
   if re.search(t,l):target+=slug+'/';break
 if cat=='plastikovaya-upakovka':
  for t,slug in [(r'блистер','blisternaya-upakovka'),(r'коррекс','korreksy'),(r'вакуум','vakuumnaya-formovka'),(r'тубус','tubusy')]:
   if re.search(t,l):target+=slug+'/';break
 if cat=='kryshki-dlya-tubusov':
  for t,slug in [(r'жестян|металлическ','zhestyanye'),(r'пластиков|пэт','plastikovye')]:
   if re.search(t,l):target+=slug+'/';break
 if cat=='purpose':
  for item in cats:
   if item['parent']=='/product/purpose/' and any(w in l for w in item['name'].lower().replace('упаковка для','').replace('упаковка','').split() if len(w)>4):target=item['path'];break
 non=re.search('|'.join(exceptions),l);info=re.search(r'(^как |^что такое|^для чего|^из чего|^виды |^разница |^отличие |^применение |^размеры |^плотность )',l)
 status='exclude' if non else ('informational' if info else ('review' if not cat else 'provisional'))
 intent='информационный' if info else 'коммерческий' if target else 'не определён'
 rowsout.append([i,q]+(row[1:6]+['']*5)[:5]+[target,cat or 'Без категории',status,intent,'Автоматическое предварительное назначение; проверить SERP и интент'])
with (DOC/'query_map.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(header);w.writerows(rowsout)
with (DOC/'site_tree.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['type','url','h1','parent','index_candidate']);w.writerows([['category',x['path'],x['name'],x['parent'],'yes'] for x in cats]);w.writerows([['product',x['path'],x['name'],x['category'],'yes'] for x in pro])
(D/'summary.json').write_text(json.dumps({'total_queries':len(rowsout),'query_status':dict(collections.Counter(r[9] for r in rowsout)),'categories':len(cats),'products':len(pro)},ensure_ascii=False,indent=2))
print('Prepared',len(cats),'cats',len(pro),'products',len(rowsout),'queries',collections.Counter(r[9] for r in rowsout))