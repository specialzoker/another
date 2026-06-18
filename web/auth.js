// 입장 게이트 — 박스플롯 앱과 동일한 Supabase 검증 방식.
window.Auth = (function(){
  const SUPABASE_URL = 'https://qctffhrkhuaquciinblj.supabase.co';
  const SUPABASE_KEY = 'sb_publishable_4FZ0r-MqFdCjN4a1tRvLIQ_UmJVx0mj';
  const EDGE_FN_URL  = SUPABASE_URL + '/functions/v1/validate-key';
  const STORE_KEY    = 'gate_entry';

  let _adminMode = false, _adminToken = null;

  function $(id){ return document.getElementById(id); }
  function setStatus(msg){ var e=$('gateStatus'); if(e) e.textContent = msg||''; }
  function setErr(msg){ var e=$('gateErr'); if(e) e.textContent = msg||''; }

  function reveal(name){
    try{ localStorage.setItem(STORE_KEY, JSON.stringify({name:name||'', ts:Date.now()})); }catch(e){}
    document.body.classList.remove('locked');
    var tag=$('schoolTag'); if(tag) tag.textContent = name||'';
    if(window.App && typeof window.App.start==='function' && !window.App._started){
      window.App._started = true;
      window.App.start();
    }
  }

  function togglePw(){
    var inp=$('keyInput'); inp.type = inp.type==='password'?'text':'password';
  }

  function toggleAdminMode(){
    _adminMode = !_adminMode;
    $('keyWrap').classList.toggle('hidden', _adminMode);
    $('adminWrap').classList.toggle('hidden', !_adminMode);
    $('gateBtn').textContent = _adminMode ? '관리자 로그인' : '확인';
    $('gateBtn').onclick = _adminMode ? doAdminLogin : doLogin;
    $('adminToggle').textContent = _adminMode ? '← 학교 키 로그인' : '관리자 로그인';
    $('gateSub').textContent = _adminMode ? '관리자 이메일과 비밀번호를 입력하세요' : '학교 고유 키를 입력하세요';
    setErr(''); setStatus('');
  }

  async function doLogin(){
    var key = $('keyInput').value.trim();
    setErr('');
    if(!key){ setErr('키를 입력해주세요.'); return; }
    var btn=$('gateBtn'); btn.disabled=true;
    try{
      setStatus('⏳ 확인 중...');
      var res = await fetch(EDGE_FN_URL, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ key: key })
      });
      var data = await res.json();
      if(!res.ok){ setErr(data.error || '유효하지 않은 키입니다.'); setStatus(''); return; }
      reveal(data.school ? data.school.sch_name : '');
    }catch(e){ setErr('연결 오류: ' + e.message); setStatus(''); }
    finally{ btn.disabled=false; }
  }

  async function doAdminLogin(){
    var email = $('adminEmail').value.trim();
    var pw = $('adminPw').value;
    setErr('');
    if(!email || !pw){ setErr('이메일과 비밀번호를 입력해주세요.'); return; }
    var btn=$('gateBtn'); btn.disabled=true;
    try{
      setStatus('⏳ 관리자 인증 중...');
      var res = await fetch(SUPABASE_URL + '/auth/v1/token?grant_type=password', {
        method:'POST', headers:{'Content-Type':'application/json','apikey':SUPABASE_KEY},
        body: JSON.stringify({ email: email, password: pw })
      });
      if(!res.ok){ setErr('이메일 또는 비밀번호가 올바르지 않습니다.'); setStatus(''); return; }
      var authData = await res.json();
      _adminToken = authData.access_token;
      reveal('관리자');
    }catch(e){ setErr('연결 오류: ' + e.message); setStatus(''); }
    finally{ btn.disabled=false; }
  }

  async function doResetPw(){
    var pw=$('newPw').value, pw2=$('newPw2').value, err=$('resetErr');
    err.textContent='';
    if(pw.length<6){ err.textContent='비밀번호는 6자 이상이어야 합니다.'; return; }
    if(pw!==pw2){ err.textContent='비밀번호가 일치하지 않습니다.'; return; }
    try{
      var res = await fetch(SUPABASE_URL + '/auth/v1/user', {
        method:'PUT',
        headers:{'Content-Type':'application/json','apikey':SUPABASE_KEY,'Authorization':'Bearer '+_adminToken},
        body: JSON.stringify({ password: pw })
      });
      if(!res.ok){ err.textContent='변경 실패. 링크가 만료되었을 수 있습니다.'; return; }
      $('resetView').classList.add('hidden'); $('loginView').classList.remove('hidden');
      _adminToken=null; alert('✅ 비밀번호가 변경되었습니다. 다시 로그인해주세요.');
    }catch(e){ err.textContent='오류: '+e.message; }
  }

  function logout(){
    try{ localStorage.removeItem(STORE_KEY); }catch(e){}
    location.reload();
  }

  function checkRecovery(){
    var hash = new URLSearchParams(window.location.hash.substring(1));
    if(hash.get('type')==='recovery'){
      _adminToken = hash.get('access_token');
      $('resetView').classList.remove('hidden');
      $('loginView').classList.add('hidden');
      history.replaceState(null,'',window.location.pathname);
    }
  }

  function boot(){
    checkRecovery();
    var saved=null;
    try{ saved = JSON.parse(localStorage.getItem(STORE_KEY)||'null'); }catch(e){}
    if(saved){ reveal(saved.name); }
  }

  document.addEventListener('DOMContentLoaded', boot);

  return { doLogin: doLogin, doAdminLogin: doAdminLogin, toggleAdminMode: toggleAdminMode,
           togglePw: togglePw, doResetPw: doResetPw, logout: logout };
})();
