(() => {
  const panel=document.querySelector('#answers');
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let catalog=null, selection=0;
  const message=panel.querySelector('#answersMessage');
  const locked=panel.querySelector('#answersLocked');
  const library=panel.querySelector('#answersLibrary');
  const detail=panel.querySelector('#answerDetail');
  const grid=panel.querySelector('#answerGrid');
  const subject=panel.querySelector('#answerSubject'), year=panel.querySelector('#answerYear');
  async function api(path,options={}) {
    const response=await fetch('/api/answers/'+path,{cache:'no-store',...options});
    const body=await response.json();
    if(response.status===401){location.href='/login?next=%2F';throw Error('Sign in again.');}
    if(!response.ok)throw Object.assign(Error(body.error||'Could not load answers.'),{locked:body.locked});
    return body;
  }
  function clear(){selection++;catalog=null;grid.replaceChildren();detail.replaceChildren();grid.hidden=false;panel.querySelector('#answerFilters').hidden=false;library.hidden=true;locked.hidden=false;panel.querySelector('#answersPassword').value='';}
  function render(){
    const rows=catalog.papers.filter(p=>(subject.value==='all'||p.subject===subject.value)&&(year.value==='all'||String(p.year)===year.value));
    grid.innerHTML=rows.map(p=>`<article class="card answer-card"><span class="badge">${escape(p.label)}</span><h3>${escape(p.subject)}</h3><p>${p.year}${p.part?' · Paper '+p.part:''}</p><p class="meta">${escape(p.coverage)}</p><button class="answer-open" data-id="${escape(p.id)}">${p.status==='pending'?'View coverage':'Open answers'}</button></article>`).join('')||'<p>No papers match these filters.</p>';
    grid.querySelectorAll('button').forEach(b=>b.onclick=()=>openPaper(b.dataset.id));
  }
  async function load(){
    catalog=await api('index');locked.hidden=true;library.hidden=false;
    message.textContent=catalog.summary;
    subject.innerHTML='<option value="all">All subjects</option>'+[...new Set(catalog.papers.map(p=>p.subject))].map(s=>`<option>${escape(s)}</option>`).join('');
    year.innerHTML='<option value="all">All years</option>'+[...new Set(catalog.papers.map(p=>p.year))].sort((a,b)=>b-a).map(y=>`<option>${y}</option>`).join('');
    render();
  }
  async function status(){
    try{const state=await api('status');if(state.unlocked){if(!catalog)await load();}else{clear();message.textContent='Sign in with Google, then use the shared Answers password. The library locks after two hours.';}}
    catch(e){clear();message.textContent=e.message;}
  }
  async function openPaper(id){
    const ticket=++selection;detail.innerHTML='<p>Loading answers…</p>';
    try{
      const p=await api(id);if(ticket!==selection)return;
      detail.innerHTML=`<div class="card answer-detail"><button id="answerBack">← Back to answer library</button><h3>${escape(p.subject)} · ${p.year}${p.part?' · Paper '+p.part:''}</h3><p class="notice">${escape(p.note)}</p><p><a href="${escape(p.paperPdf)}" target="_blank" rel="noopener">Open question paper PDF ↗</a>${p.pdf?' · <a href="/api/answers/'+id+'.pdf" target="_blank" rel="noopener">Open worked answers PDF ↗</a>':''}</p>${p.sources?.length?'<p>'+p.sources.map(s=>`<a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.title)} ↗</a>`).join(' · ')+'</p>':''}${(p.answers||[]).map(a=>`<details class="answer-item"><summary>${escape(a.ref)}${a.prompt?' · '+escape(a.prompt):''}</summary><div class="answer-body">${escape(a.answer).replace(/\n/g,'<br>')}${a.code?'<pre><code>'+escape(a.code)+'</code></pre>':''}${a.check?'<p class="meta">Check: '+escape(a.check)+'</p>':''}</div></details>`).join('')}${p.references?.length?'<h4>Published answers by question</h4><p class="muted">These links open the publisher’s answers. They are not official board marking schemes. The publisher’s public pages remain public.</p>'+p.references.map(r=>`<details class="answer-item"><summary>${escape(r.question||'Question')} · ${escape(r.questionText.split('\n')[0])}</summary><p>${escape(r.questionText).replace(/\n/g,'<br>')}</p><a href="${escape(r.url)}" target="_blank" rel="noopener noreferrer">Read published solution ↗</a></details>`).join(''):''}</div>`;
      grid.hidden=true;panel.querySelector('#answerFilters').hidden=true;
      detail.querySelector('#answerBack').onclick=()=>{selection++;detail.replaceChildren();grid.hidden=false;panel.querySelector('#answerFilters').hidden=false;};
      detail.scrollIntoView({block:'start',behavior:'smooth'});
    }catch(e){if(e.locked)clear();message.textContent=e.message;detail.replaceChildren();}
  }
  panel.querySelector('#answersUnlock').onsubmit=async event=>{
    event.preventDefault();const input=panel.querySelector('#answersPassword'),button=event.submitter;button.disabled=true;
    try{await api('unlock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:input.value})});input.value='';await load();}
    catch(e){message.textContent=e.message;input.value='';input.focus();}finally{button.disabled=false;}
  };
  panel.querySelector('#answersLock').onclick=async()=>{try{await api('lock',{method:'POST'});clear();message.textContent='Answers are locked.';}catch(e){message.textContent=e.message;}};
  subject.onchange=year.onchange=render;
  document.addEventListener('hsc-tab-change',e=>{if(e.detail==='answers')status();});
  window.addEventListener('pageshow',()=>{if(panel.classList.contains('active'))status();});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&panel.classList.contains('active'))status();});
  setInterval(()=>{if(catalog)status();},60000);
})();
