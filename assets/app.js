(()=>{const m=document.getElementById('menu'),n=document.getElementById('links');if(m&&n)m.addEventListener('click',()=>{const state=n.classList.toggle('open');m.setAttribute('aria-expanded',String(state));m.textContent=state?'✕':'☰'});const f=document.getElementById('quote-form');if(f){const p=new URLSearchParams(location.search).get('product');if(p)f.elements.product.value=p;f.addEventListener('submit',e=>{e.preventDefault();if(!f.reportValidity())return;const fields=new FormData(f);const body=['Здравствуйте! Прошу рассчитать изготовление упаковки.','','Продукция: '+fields.get('product'),'Имя: '+fields.get('name'),'Email: '+fields.get('email'),'Тираж: '+(fields.get('quantity')||'не указан'),'Описание: '+(fields.get('details')||'не указано'),'','Страница: '+location.href].join('\n');location.href='mailto:order@rossantpack.ru?subject='+encodeURIComponent('Расчёт упаковки — '+fields.get('product'))+'&body='+encodeURIComponent(body)})}})();(() => {
  const form = document.getElementById('quote-form');
  if (!form) return;
  const preview = document.createElement('pre');
  preview.className = 'form-feedback'; preview.hidden = true; preview.tabIndex = 0;
  preview.setAttribute('aria-label', 'Текст подготовленного запроса');
  const button = document.createElement('button'); button.type = 'button';
  button.className = 'btn btn-outline'; button.textContent = 'Показать текст запроса';
  const status = document.createElement('p'); status.setAttribute('role', 'status');
  form.append(button, preview, status);
  button.addEventListener('click', () => {
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    preview.textContent = ['Здравствуйте! Прошу рассчитать изготовление упаковки.',
      'Продукция: ' + data.get('product'), 'Имя: ' + data.get('name'),
      'Email: ' + data.get('email'), 'Количество: ' + (data.get('quantity') || 'не указано'),
      'Требования: ' + (data.get('details') || 'не указаны')].join('\n');
    preview.hidden = false; preview.focus();
    status.textContent = 'Текст готов. Скопируйте его и отправьте на order@rossantpack.ru. Заявка пока не отправлена.';
  });
  const source = new URLSearchParams(location.search).get('product');
  if (source) form.elements.product.value = source;
})();
