"""Lexical mapping only. Regional SERP clustering remains a separate review."""
import csv,json,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
P='/product/'
PURPOSE={
'ампул':'upakovka-dlya-ampul','бокал':'upakovka-dlya-bokalov-1535','парфюм|дух[иоа]':'upakovka-dlya-dukhov','косметик':'upakovka-dlya-kosmetiki-7763','зеркал':'upakovka-dlya-zerkal','кальян':'upakovka-dlya-kalyanov','керамик':'upakovka-dlya-keramiki','крупногабарит':'upakovka-dlya-krupnogabaritnykh-gruzov-i-tovarov','новогодн':'novogodnyaya-upakovka394','медицин':'upakovka-dlya-meditsinskikh-izdeliy9560','сантехник':'upakovka-dlya-santekhniki-9530','светильник':'upakovka-dlya-svetilnikov','стоматолог':'upakovka-dlya-stomatologii9142','украшен|ювелир':'upakovka-dlya-ukrasheniy','флакон':'upakovka-dlya-flakonov','хрупк':'upakovka-dlya-khrupkogo7733',r'\bчас(ы|ов|ам)\b':'upakovka-dlya-chasov','компьютер':'upakovka-kompyuterov','микросхем':'upakovka-mikroskhem','флок':'flokirovannaya-upakovka','сервер':'nakladki-dlya-serverov','военн':'voennaya-upakovka','авиа':'upakovka-dlya-aviaperevozok-upakovka-dlya-aviatsionnykh-izdeliy-dlya-aviatsii-na-zakaz','маркетплейс':'upakovka-dlya-marketpleysov','уголк.*пенопласт|пенопласт.*уголк':'ugolki-iz-penoplasta','профил.*пенопласт|пенопласт.*профил':'profili-iz-penoplasta','ударопрочн':'udaroprochnaya-upakovka','транспортн':'transportnaya-upakovka','защитн':'zashchitnaya-upakovka','комбинирован':'kombinirovannaya-upakovka','индивидуальн':'individualnaya-upakovka','подарочн':'podarochnaya-upakovka','заглушк':'zaglushki-vstavki-ugolki469','пенопласт':'upakovka-iz-tverdogo-penoplasta','вкладыш|вставк':'vkladyshi-dlya-upakovki'}
def match(q):
 q=q.lower().replace('ё','е');status='provisional';comment='Лексическое назначение; проверить выдачу Москвы/МО';target=''
 if re.search(r'ваканс|\bработа\b|реферат|скачать|своими руками|авито|шаблон для печати',q):return '', 'exclude','Исключённый','Нецелевой или самостоятельное изготовление'
 if re.search(r'^(как |что такое|для чего|из чего|виды |разница |отличие |применение |плотность )',q):return '', 'informational','Информационный','Тема статьи; URL после проверки интента'
 rules=[]
 if 'крышк' in q:
  if 'тубус' not in q:return '', 'review','Не определён','Не подтверждено назначение крышки для тубуса'
  target=P+'kryshki-dlya-tubusov/';rules=[('жестян|металл','zhestyanye'),('пластик|пэт','plastikovye')]
 elif re.search('короб|гофрокороб',q):
  target=P+'korobki/';rules=[('подарочн.*ложемент|ложемент.*подарочн','podarochnye-korobki-s-lozhementom'),('ложемент','korobki-s-lozhementom'),('микрогофр','korobki-iz-mikrogofrokartona'),('переплет','korobki-iz-perepletnogo-kartona'),('гофр','gofrokoroba'),('картон','kartonnye-korobki')]
 elif re.search('ложемент|ложемант|вкладыш.*кейс|вставк.*кейс',q):
  target=P+'lozhementy/';rules=[('поролон','lozhementy-iz-porolona'),(r'\beva\b|\bэва\b','lozhementy-iz-materiala-eva'),('пенополиэтилен|ппэ|вспененн','lozhementy-iz-penopolietilenov'),('изолон','lozhementy-iz-izolona'),('пластик','lozhementy-iz-plastika1'),('пенопласт','lozhementy-iz-penoplasta'),('картон','lozhementy-iz-kartona'),('кейс','lozhementy-dlya-keysov')]
 elif re.search('поролонов.*рук|поролонов.*перчат|рук.*болельщик',q):target=P+'porolonovye-ruki/'
 elif re.search('блистер|коррекс|вакуумн.*формов|тубус|пластиков.*упаков',q):
  target=P+'plastikovaya-upakovka/';rules=[('блистер','blisternaya-upakovka'),('коррекс','korreksy'),('вакуум','vakuumnaya-formovka'),('тубус','tubusy')]
 elif re.search('упаков|вкладыш|вставк|профил|уголк|заглушк',q):
  target=P+'purpose/';hits=[v for k,v in PURPOSE.items() if re.search(k,q)]
  if hits:target+=hits[0]+'/'
  if len(hits)>1:status='review';comment='Несколько назначений: '+', '.join(hits)+'; проверить интент'
 for pattern,slug in rules:
  if re.search(pattern,q):target+=slug+'/';break
 if not target:return '', 'review','Не определён','Нет точного правила; ручное назначение'
 if re.search(r'купить (одн|1\b)|\b1 шт\b|озон|wildberries|ozon|розниц',q):status='review';comment='Возможный розничный интент; проверить предложение'
 return target,status,'Коммерческий',comment

def main():
 with (ROOT/'data/source/topvisor.csv').open(encoding='utf-8-sig',newline='') as f:raw=list(csv.reader(f,delimiter=';'))
 records=[]
 for i,row in enumerate(raw[2:],1):
  if not row or not row[0].strip():continue
  target,status,intent,comment=match(row[0]);records.append([i,row[0]]+(row[1:6]+['']*5)[:5]+[target,target.split('/')[2] if target else '',status,intent,comment])
 with (ROOT/'docs/query_map.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f,delimiter=';',lineterminator='\n');w.writerow(['id','query','broad','quoted','exact_morph','bracket','bracket_exact','target_url','cluster','status','intent','comment']);w.writerows(records)
 summary={'total_queries':len(records),'query_status':dict(collections.Counter(x[9] for x in records)),'categories':len(json.loads((ROOT/'data/categories.json').read_text())),'products':len(json.loads((ROOT/'data/products.json').read_text())),'method':'lexical_preliminary','region':'unspecified_in_source'}
 (ROOT/'data/summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
