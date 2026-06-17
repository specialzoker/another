// 순수 헬퍼 — DOM 문자열만 생성. window.Render 네임스페이스.
window.Render = (function(){
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
  function ratePill(rate, applied){
    if(!applied) return '<span class="pill muted">-</span>';
    const pct=Math.round((rate||0)*100);
    const cls = pct>=60?'good':pct>=30?'ok':pct>0?'warn':'bad';
    return `<span class="pill ${cls}">${pct}%</span>`;
  }
  function bar(rate){
    const pct=Math.round((rate||0)*100);
    return `<div class="bar"><i style="width:${pct}%"></i></div>`;
  }
  function recordTitle(r){
    const unit = r.unit?` · ${esc(r.unit)}`:'';
    return `${esc(r.university)} · ${esc(r.type)} ${esc(r.name)}${unit}`;
  }
  function summaryCard(r){
    const g=r.grades||{}; const c=r.count||{};
    const kpi=(label,val)=>`<div class="kpi"><span>${label}</span><strong>${val==null?'-':val}</strong></div>`;
    const gr=(v)=>v==null?null:Number(v).toFixed(2);
    return `<div class="card">
      <h2>${recordTitle(r)}</h2>
      <div class="kpis">
        ${kpi('사례수', `${c.applied} <small style="font-size:13px;color:#64748b">[${c.accepted}]</small>`)}
        ${kpi('합격률', `${Math.round((r.rate||0)*100)}%`)}
        ${kpi('내신 최고', gr(g.best))}
        ${kpi('내신 평균', gr(g.avg))}
        ${kpi('내신 최저', gr(g.worst))}
      </div>
    </div>`;
  }
  function prefTable(r){
    const rows=(r.preferences||[]).map(p=>`
      <tr class="clickable" data-rank="${p.rank}">
        <td class="rank" style="font-weight:800;color:#1d4ed8">${p.rank}</td>
        <td><b>${esc(p.university)}</b>${p.label?' · '+esc(p.label):''}</td>
        <td style="text-align:right">${p.applied}</td>
        <td style="text-align:right">${p.accepted}</td>
        <td style="width:160px">${bar(p.rate)} <small>${Math.round((p.rate||0)*100)}%</small></td>
        <td>${p.matchedId?'<span class="pill ok">상세</span>':'<span class="pill muted">역방향 없음</span>'}</td>
      </tr>`).join('');
    return `<div class="card">
      <h2>같이 지원한 전형 (지망순) — 행 더블클릭 시 상세</h2>
      <div class="scroll">
        <table><thead><tr>
          <th>지망</th><th>대학 · 전형</th><th style="text-align:right">지원</th>
          <th style="text-align:right">합격</th><th>합격률</th><th></th>
        </tr></thead><tbody>${rows||'<tr><td colspan="6">데이터 없음</td></tr>'}</tbody></table>
      </div>
    </div>`;
  }
  function hubSpoke(rec){
    const prefs=(rec.preferences||[]).slice(0,8);
    const W=720,H=360,cx=W/2,cy=H/2;
    const maxApplied=Math.max(1,...prefs.map(p=>p.applied));
    let edges='',nodes='';
    prefs.forEach((p,i)=>{
      const ang=(-Math.PI/2)+(i*2*Math.PI/prefs.length);
      const x=cx+Math.cos(ang)*240, y=cy+Math.sin(ang)*140;
      const w=1+ (p.applied/maxApplied)*9;
      edges+=`<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="#93c5fd" stroke-width="${w.toFixed(1)}" stroke-opacity="0.8"/>`;
      nodes+=`<g><circle cx="${x}" cy="${y}" r="30" fill="#eff6ff" stroke="#1d4ed8"/>
        <text x="${x}" y="${y-2}" text-anchor="middle" font-size="11" font-weight="700" fill="#0f3b75">${esc(p.university)}</text>
        <text x="${x}" y="${y+13}" text-anchor="middle" font-size="10" fill="#475569">${p.applied}명</text></g>`;
    });
    return `<div class="card"><h2>교차지원 흐름도</h2>
      <svg viewBox="0 0 ${W} ${H}" width="100%" style="max-height:380px">
        ${edges}
        <circle cx="${cx}" cy="${cy}" r="42" fill="#1d4ed8"/>
        <text x="${cx}" y="${cy-3}" text-anchor="middle" font-size="12" font-weight="800" fill="#fff">${esc(rec.university)}</text>
        <text x="${cx}" y="${cy+14}" text-anchor="middle" font-size="10" fill="#dbeafe">${esc(rec.name).slice(0,8)}</text>
        ${nodes}
      </svg></div>`;
  }
  function bidirectional(rec, pref, target){
    const aToB = rec.count.applied? pref.applied/rec.count.applied : 0;
    let revText='<span class="pill muted">역방향 데이터 없음</span>';
    if(target){
      const back=(target.preferences||[]).find(p=>p.matchedId===rec.id);
      const bToA = (back && target.count.applied)? back.applied/target.count.applied : 0;
      revText = back
        ? `${esc(target.university)} 지원자 중 <b>${Math.round(bToA*100)}%</b>가 ${esc(rec.university)}에도 지원`
        : revText;
    }
    return `<div class="card"><h2>양방향 비교</h2>
      <p>${esc(rec.university)} ${esc(rec.name)} 지원자 중 <b>${Math.round(aToB*100)}%</b>가
         ${esc(pref.university)} ${esc(pref.label)}에도 지원</p>
      ${bar(aToB)}
      <p style="margin-top:14px">${revText}</p>
    </div>`;
  }
  return {esc, ratePill, bar, recordTitle, summaryCard, prefTable, hubSpoke, bidirectional};
})();
