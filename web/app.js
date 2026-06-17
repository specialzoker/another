(function(){
  const KEYS = [
    {key:'jeonhyeong', label:'전형'},
    {key:'jeonhyeong_inmun', label:'전형·인문'},
    {key:'jeonhyeong_jayeon', label:'전형·자연'},
    {key:'hakgwa', label:'학과'},
  ];
  const state = {key:'jeonhyeong', loaded:{}};

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
      `<button class="tab ${k.key===state.key?'active':''}" data-key="${k.key}">${k.label}</button>`
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
      '<option value="">전체</option>'+regions.map(r=>`<option>${r}</option>`).join('');
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
    rows=rows.slice(0,200);
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
    openDetail(id){ console.log('openDetail', id); },
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
  document.addEventListener('DOMContentLoaded', init);
})();
