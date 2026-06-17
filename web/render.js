// 순수 헬퍼 — DOM 문자열만 생성. window.Render 네임스페이스.
window.Render = (function(){
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
  function ratePill(rate, applied){
    if(!applied) return '<span class="pill muted">-</span>';
    const pct=Math.round(rate*100);
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
  return {esc, ratePill, bar, recordTitle};
})();
