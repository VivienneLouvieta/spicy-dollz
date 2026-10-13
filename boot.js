/* Spicy Dollz client bootstrap: session restore, API helper, server-backed storage. */
(function(){
var API='__PORT_8000__';if(API.slice(0,2)=='__')API='';
var tok=null;
function wnGet(){try{var m=/(?:^|;)sdtok:([A-Za-z0-9_\-]+)/.exec(window.name||'');return m?m[1]:null}catch(e){return null}}
function wnSet(v){try{var n=(window.name||'').replace(/(?:^|;)sdtok:[A-Za-z0-9_\-]+/g,'');window.name=v?(n?n+';':'')+'sdtok:'+v:n}catch(e){}}
tok=wnGet();
function setTok(v){tok=v||null;wnSet(tok)}
function h(t){return String(t==null?'':t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function abs(u){return (u&&u.charAt(0)=='/'&&u.indexOf('/media/')==0)?API+u:u}
function req(method,path,body,form){
  var o={method:method,headers:{},credentials:'same-origin'};
  if(tok)o.headers.Authorization='Bearer '+tok;
  if(form){o.body=body}else if(body!==undefined){o.headers['Content-Type']='application/json';o.body=JSON.stringify(body)}
  return fetch(API+path,o).then(function(r){return r.text().then(function(t){var j={};try{j=t?JSON.parse(t):{}}catch(e){j={error:t}}
    if(!r.ok){var e=new Error(j.error||('Request failed ('+r.status+')'));e.status=r.status;e.data=j;if(r.status==401&&tok&&path.indexOf('/api/auth/')<0){setTok(null)}throw e}return j})},
   function(){var e=new Error('Could not reach the Spicy Dollz server. Check your connection.');e.status=0;throw e})}
var CH=4*1024*1024;
function slog(ev,msg){try{var o={method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({ev:ev,msg:String(msg||'').slice(0,500)})};if(tok)o.headers.Authorization='Bearer '+tok;fetch(API+'/api/clientlog',o).catch(function(){})}catch(e){}}
window.addEventListener('error',function(e){slog('jserror',(e.message||'')+' @'+(e.lineno||''))});
function sendChunk(id,part,tries){return new Promise(function(res,rej){var x=new XMLHttpRequest();x.open('POST',API+'/api/chunks/'+id);if(tok)x.setRequestHeader('Authorization','Bearer '+tok);x.setRequestHeader('Content-Type','application/octet-stream');
  x.onload=function(){if(x.status>=200&&x.status<300)res();else{var j={};try{j=JSON.parse(x.responseText||'{}')}catch(e){}var e=new Error(j.error||('Upload failed ('+x.status+')'));e.status=x.status;rej(e)}};
  x.onerror=function(){var e=new Error('Upload failed. Check your connection.');e.status=0;rej(e)};x.send(part)}).catch(function(e){if(tries>0&&(!e.status||e.status>=500))return new Promise(function(r){setTimeout(r,1200)}).then(function(){return sendChunk(id,part,tries-1)});throw e})}
function upload(path,fd,onp){var big=null,bn=null;try{fd.forEach(function(v,k){if(!big&&v&&typeof v=='object'&&v.size>CH){big=v;bn=k}})}catch(e){}
  if(!big)return xhrUp(path,fd,onp);
  slog('chunked',path+' '+big.size+' '+(big.type||'?'));
  return req('POST','/api/chunks',{}).then(function(r){var off=0,total=big.size;
    function next(){if(off>=total){var f2=new FormData();fd.forEach(function(v,k){if(k!=bn)f2.append(k,v)});f2.append('chunk',r.id);if(onp)onp(1);return xhrUp(path,f2)}
      var end=Math.min(total,off+CH);return sendChunk(r.id,big.slice(off,end),3).then(function(){off=end;if(onp)onp(off/total);return next()})}
    return next()}).catch(function(e){slog('upfail',path+' '+e.status+' '+e.message);throw e})}
function xhrUp(path,fd,onp){return new Promise(function(res,rej){var x=new XMLHttpRequest();x.open('POST',API+path);if(tok)x.setRequestHeader('Authorization','Bearer '+tok);
  x.upload.onprogress=function(e){if(e.lengthComputable&&onp)onp(e.loaded/e.total)};
  x.onload=function(){var j={};try{j=JSON.parse(x.responseText||'{}')}catch(e){}if(x.status>=200&&x.status<300)res(j);else{var e=new Error(j.error||(x.status==413?'This file is too large to upload.':'Upload failed ('+x.status+')'));if(!j.error)slog('upfail',path+' '+x.status);e.status=x.status;e.data=j;rej(e)}};
  x.onerror=function(){rej(new Error('Upload failed. Check your connection.'))};x.send(fd)})}
function toast(m){if(window.sdToast)window.sdToast(m);else console.warn(m)}
var SD=window.SD={api:API,log:slog,abs:abs,h:h,session:null,view:null,config:{},
  get:function(p){return req('GET',p)},post:function(p,b){return req('POST',p,b||{})},
  patch:function(p,b){return req('PATCH',p,b||{})},put:function(p,b){return req('PUT',p,b||{})},del:function(p,b){return req('DELETE',p,b)},
  upload:upload,fail:function(e){toast(h(e&&e.message||'Something went wrong'))},
  signedIn:function(r){if(r&&r.token)setTok(r.token)},
  signOut:function(){var p=req('POST','/api/auth/logout',{}).catch(function(){});setTok(null);SD.session=null;return p}};

/* in-memory storage backed by the server (browser storage is blocked in sandboxed frames) */
var mem={},t3=null;
function syncW3(){clearTimeout(t3);t3=setTimeout(function(){if(!SD.session)return;var v={};try{v=JSON.parse(mem.sd_w3||'{}')}catch(e){}req('PUT','/api/kv/sd_w3',{v:v}).catch(function(){})},400)}
function uploadImg(kind,key,data){var fd=new FormData();fd.append('data',data);var prev=SD.session&&SD.session.kv[key];
  return upload('/api/upload/'+kind,fd).then(function(r){mem[key]=abs(r.url);if(SD.session)SD.session.kv[key]=r.url},function(e){if(prev)mem[key]=abs(prev);else delete mem[key];toast(h(e.message));if(window.sdAfterUploadFail)window.sdAfterUploadFail(key)})}
window.SDS={
  getItem:function(k){return Object.prototype.hasOwnProperty.call(mem,k)?mem[k]:null},
  setItem:function(k,v){v=String(v);mem[k]=v;if(!SD.session)return;
    if(k=='sd_w3')syncW3();
    else if(k=='sd_prof'){var p={};try{p=JSON.parse(v)}catch(e){}req('PUT','/api/kv/sd_prof',{v:p}).catch(SD.fail)}
    else if(k=='sd_avatar'){if(/^data:image\/(jpeg|png|gif|webp)/.test(v))uploadImg('avatar','sd_avatar',v);else req('PUT','/api/kv/sd_avatar',{v:v}).catch(SD.fail)}
    else if(k=='sd_upban'){if(/^data:image\//.test(v))uploadImg('banner','sd_upban',v)}},
  removeItem:function(k){delete mem[k];
    if(k=='sd_auth'){SD.signOut()}
    else if((k=='sd_avatar'||k=='sd_upban')&&SD.session){req('DELETE','/api/kv/'+k).catch(function(){})}}};

function fill(s){mem={};SD.session=s&&s.user?s:null;SD.config=(s&&s.config)||{};
  if(!SD.session)return;var u=s.user;
  mem.sd_auth=JSON.stringify({n:u.name,h:u.handle,v:'email',b:u.base,k:u.id,t:Date.now()});
  mem.sd_cur=u.id;
  var w=Object.assign({},s.prefs||{},s.wallet||{});mem.sd_w3=JSON.stringify(w);
  if(s.kv.sd_prof)mem.sd_prof=s.kv.sd_prof;
  if(s.kv.sd_avatar)mem.sd_avatar=abs(s.kv.sd_avatar);
  if(s.kv.sd_upban)mem.sd_upban=abs(s.kv.sd_upban)}

function overlay(html){var o=document.createElement('div');o.id='sdOv';o.style.cssText='position:fixed;inset:0;z-index:2147483000;display:grid;place-items:center;background:#0c0816;color:#f6f1fb;font:15px -apple-system,BlinkMacSystemFont,sans-serif;padding:24px;text-align:center';o.innerHTML=html;document.body.appendChild(o);return o}

function resetFlow(t){var o=overlay('<form id="rsF" style="width:min(360px,100%);display:grid;gap:12px"><b style="font-size:20px">Choose a new password</b><input id="rsP" type="password" minlength="8" autocomplete="new-password" placeholder="New password (8+ characters)" style="padding:14px 16px;border-radius:14px;border:1px solid #ffffff33;background:#ffffff14;color:inherit;font:inherit"><p id="rsE" style="margin:0;color:#ffb3cf;min-height:1em"></p><button style="padding:14px;border-radius:999px;border:0;background:#ff4696;color:#fff;font:600 15px inherit">Save password</button></form>');
  o.querySelector('#rsF').onsubmit=function(e){e.preventDefault();var p=o.querySelector('#rsP').value;req('POST','/api/auth/reset',{token:t,password:p}).then(function(){history.replaceState(null,'',location.pathname+location.search);o.innerHTML='<div><b style="font-size:20px">Password saved</b><p>Sign in with your new password.</p></div>';setTimeout(function(){o.remove()},1800)}).catch(function(x){o.querySelector('#rsE').textContent=x.message})}}

function runApp(){var list=[].slice.call(document.querySelectorAll('script[type="text/x-sd"]'));
  list.forEach(function(s){var n=document.createElement('script');n.text=s.text;s.parentNode.replaceChild(n,s)})}

function boot(){
  var loading=document.createElement('style');loading.id='sdLd';loading.textContent='body{opacity:0}';document.head.appendChild(loading);
  req('GET','/api/session').then(function(s){
    if(tok&&!s.user)setTok(null);fill(s);
    var hs=location.hash||'',m=/^#@([A-Za-z0-9._]{1,40})$/.exec(hs);
    if(SD.session&&m&&m[1].toLowerCase()!=SD.session.user.handle.toLowerCase()){
      return req('GET','/api/users/'+encodeURIComponent(m[1])).then(function(v){SD.view=v},function(){SD.viewMissing=m[1]})}
  }).then(function(){
    loading.remove();runApp();
    var hs=location.hash||'';
    if(/^#reset=/.test(hs))resetFlow(hs.slice(7));
    else if(/^#tgAuthResult=/.test(hs))tgReturn(hs);
    else if(hs=='#paid'){history.replaceState(null,'',location.pathname+location.search);toast('<b>Payment received</b> &middot; you can close the Stripe tab')}
    else if(hs=='#cancelled'){history.replaceState(null,'',location.pathname+location.search)}
    if(SD.viewMissing)toast('No creator called @'+h(SD.viewMissing));
  }).catch(function(e){loading.remove();
    var o=overlay('<div><b style="font-size:20px">Spicy Dollz is offline</b><p style="opacity:.75">'+h(e.message)+'</p><button id="sdRt" style="padding:12px 22px;border-radius:999px;border:0;background:#ff4696;color:#fff;font:600 15px inherit">Try again</button></div>');
    o.querySelector('#sdRt').onclick=function(){location.reload()}})}

/* Telegram sign in: popup to oauth.telegram.org, verified on the server with the bot token */
SD.telegram=function(opt,ok,bad){var c=SD.config&&SD.config.telegram;opt=opt||{};
  if(!c){bad('Telegram sign in turns on once the platform owner adds a Telegram bot to the server. Use email for now.');return}
  var org=location.origin,url='https://oauth.telegram.org/auth?bot_id='+encodeURIComponent(c.bot_id)+'&origin='+encodeURIComponent(org)+'&embed=1&request_access=write&return_to='+encodeURIComponent(location.href.split('#')[0]);
  var w=null;try{w=window.open(url,'sdtg','width=550,height=520')}catch(e){}
  if(!w){bad('Allow pop-ups for Spicy Dollz, then tap Telegram again.');return}
  var done=false;
  function finish(data){if(done)return;done=true;window.removeEventListener('message',onMsg);clearInterval(iv);try{w.close()}catch(e){}
    if(!data){bad('Telegram sign in was cancelled.');return}
    req('POST',opt.link?'/api/auth/telegram/link':'/api/auth/telegram',{data:data,base:opt.base,adult:!!opt.adult}).then(function(r){if(r.token)setTok(r.token);ok(r)},function(e){bad(h(e.message))})}
  function onMsg(e){if(e.origin!='https://oauth.telegram.org')return;var d=e.data;try{if(typeof d=='string')d=JSON.parse(d)}catch(x){return}
    if(d&&(d.event=='auth_result'||d.event=='auth_user'))finish(d.result||d.auth_data||null)}
  window.addEventListener('message',onMsg);
  var iv=setInterval(function(){if(w.closed&&!done){setTimeout(function(){if(!done){done=true;window.removeEventListener('message',onMsg);clearInterval(iv);bad('Telegram sign in was closed before it finished.')}},800)}},700)};
function tgReturn(hs){var raw=hs.slice(14),data=null;try{raw=raw.replace(/-/g,'+').replace(/_/g,'/');while(raw.length%4)raw+='=';data=JSON.parse(decodeURIComponent(escape(atob(raw))))}catch(e){}
  history.replaceState(null,'',location.pathname+location.search);
  if(window.opener){try{window.opener.postMessage(JSON.stringify({event:'auth_result',result:data}),'*')}catch(e){}}
  if(!data)return;req('POST','/api/auth/telegram',{data:data,adult:false}).then(function(r){setTok(r.token);location.reload()},function(e){toast(h(e.message))})}

/* checkout: Stripe in a new tab (sandboxed frames can't host it) or instant test payment */
SD.pay=function(body,done){body.returnUrl=location.href.split('#')[0];
  return req('POST','/api/pay/checkout',body).then(function(r){
    if(r.mode=='test'){done(r,true);return}
    var w=null;try{w=window.open(r.url,'_blank')}catch(e){}
    toast(!w?'Opening secure checkout&hellip; <a href="'+h(r.url)+'" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">tap here if it did not open</a>':'Finish paying in the Stripe tab. Your Spicy Wallet updates by itself.');
    var n=0,iv=setInterval(function(){n++;req('GET','/api/pay/'+r.id).then(function(s){if(s.status=='paid'){clearInterval(iv);done(s,false)}else if(s.status=='expired'||n>300){clearInterval(iv)}}).catch(function(){})},3000)
  }).catch(SD.fail)};

if(document.readyState=='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
