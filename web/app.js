(function(){
  const KEYS = [
    {key:'jeonhyeong', label:'전형'},
    {key:'jeonhyeong_inmun', label:'전형·인문'},
    {key:'jeonhyeong_jayeon', label:'전형·자연'},
    {key:'hakgwa', label:'학과'},
  ];
  const state = {key:'jeonhyeong'};

  function loadData(key){
    return new Promise((resolve)=>{
      if(window.__APPDATA__ && window.__APPDATA__[key]) return resolve();
      const s=document.createElement('script');
      s.src=`data/${key}.js`;
      s.onload=()=>resolve();
      s.onerror=()=>resolve();
      document.head.appendChild(s);
    });
  }

  function indexFor(key){ return (window.__APPINDEX__||[]).filter(x=>x.key===key); }

  function renderTabs(){
    const el=document.getElementById('sheetTabs');
    el.innerHTML=KEYS.map(k=>
      `<button class="tab ${k.key===state.key?'active':''}" data-key="${Render.esc(k.key)}">${Render.esc(k.label)}</button>`
    ).join('');
    el.querySelectorAll('.tab').forEach(b=>b.onclick=async()=>{
      state.key=b.dataset.key; renderTabs(); fillRegions();
      await loadData(state.key); runSearch();
      document.getElementById('reportBadge').textContent=`${indexFor(state.key).length}개 전형`;
    });
  }

  function fillRegions(){
    const regions=[...new Set(indexFor(state.key).map(x=>x.region).filter(Boolean))].sort();
    document.getElementById('regionFilter').innerHTML =
      '<option value="">전체</option>'+regions.map(r=>`<option value="${Render.esc(r)}">${Render.esc(r)}</option>`).join('');
  }

  function runSearch(){
    const q=document.getElementById('q').value.trim();
    const region=document.getElementById('regionFilter').value;
    const terms=q.split(/\s+/).filter(Boolean);
    let rows=indexFor(state.key);
    if(region) rows=rows.filter(x=>x.region===region);
    if(terms.length) rows=rows.filter(x=>{
      const hay=`${x.university} ${x.type} ${x.name} ${x.unit||''}`;
      return terms.every(t=>hay.includes(t));
    });
    rows=rows.slice().sort((a,b)=>(b.applied||0)-(a.applied||0)).slice(0,200);
    document.getElementById('resultBody').innerHTML = rows.map(x=>
      `<tr class="clickable" data-id="${Render.esc(x.id)}">
        <td>${Render.esc(x.region)}</td>
        <td><b>${Render.esc(x.university)}</b></td>
        <td>${Render.esc(x.type)} ${Render.esc(x.name)}${x.unit?' · '+Render.esc(x.unit):''}</td>
      </tr>`).join('') || '<tr><td>검색 결과 없음</td></tr>';
    document.querySelectorAll('#resultBody tr.clickable').forEach(tr=>
      tr.onclick=()=>window.App.openDetail(tr.dataset.id));
  }

  window.App = {
    openDetail(id){
      const rec=((window.__APPDATA__||{})[state.key]||[]).find(r=>r.id===id);
      if(!rec) return;
      state.current=rec;
      const el=document.getElementById('detail');
      el.innerHTML = Render.summaryCard(rec) + Render.prefTable(rec);
      el.scrollIntoView({behavior:'smooth'});
      el.querySelectorAll('tbody tr.clickable').forEach(tr=>{
        tr.ondblclick=()=>window.App.openDrill(rec, parseInt(tr.dataset.rank,10));
      });
    },
    openDrill(rec, rank){
      const pref=(rec.preferences||[]).find(p=>p.rank===rank);
      if(!pref) return;
      const target = pref.matchedId
        ? ((window.__APPDATA__||{})[state.key]||[]).find(r=>r.id===pref.matchedId)
        : null;
      const el=document.getElementById('detail');
      el.querySelectorAll('.drillCard').forEach(d=>d.remove());
      const drill=document.createElement('div');
      drill.className='drillCard';
      drill.innerHTML =
        `<div class="card" style="background:#f8fbff">
           <div class="btns"><button class="ghost" id="closeDrill">← 순위표로</button></div>
           <h2 style="margin:0">드릴인: ${Render.esc(rec.university)} ${Render.esc(rec.name)} → ${Render.esc(pref.university)}${pref.label?' '+Render.esc(pref.label):''}</h2>
         </div>` +
        Render.hubSpoke(rec) +
        Render.bidirectional(rec, pref, target);
      el.appendChild(drill);
      drill.scrollIntoView({behavior:'smooth'});
      drill.querySelector('#closeDrill').onclick=()=>drill.remove();
    },
    state, loadData, indexFor,
  };

  async function init(){
    renderTabs(); fillRegions();
    await loadData(state.key); runSearch();
    document.getElementById('q').addEventListener('input', runSearch);
    document.getElementById('regionFilter').addEventListener('change', runSearch);
    document.getElementById('reportBadge').textContent =
      `${indexFor(state.key).length}개 전형`;
  }
  window.App.start = init;
})();
