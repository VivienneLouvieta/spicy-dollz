
/* ===== Server: wallet sync, real videos, creator profiles ===== */
function wSync(w){if(!w)return;for(var k in w)S[k]=w[k]}
function tgt(){if(SD.tipTo)return SD.tipTo;return SD.view?{h:SD.view.handle,n:SD.view.name}:ME}
function vfmt(n){n=n||0;return n>=1000?(n/1000).toFixed(n>=10000?0:1).replace('.0','')+'K':''+n}
var VGR='linear-gradient(165deg,#ff9fc6,#c9b3ff)';(function(){var st=document.createElement('style');st.textContent='.t.sdv{overflow:hidden}.t.sdv .a{display:block!important}.t.sdv .sh{display:block!important;background:linear-gradient(transparent,#000a)!important}.t.sdv:not(.lk) .du,.t.sdv:not(.lk) .vw{color:#fff!important;text-shadow:0 1px 3px #0009!important}.t.sdv.lk .lc{color:#fff!important}.t.sdv.lk .lc i{background:#fff}#sdTest{position:fixed;right:14px;top:calc(env(safe-area-inset-top,0px) + 36px);z-index:60;padding:6px 12px;border-radius:999px;background:#1e1033;color:#fff;font:600 11.5px -apple-system,BlinkMacSystemFont,sans-serif;pointer-events:none;white-space:nowrap;box-shadow:0 4px 14px #0003}';document.head.appendChild(st)})();
function vTile(v,owner){var lock=v.aud!='all',prem=v.aud=='prem';
 var d=document.createElement('div');d.className='t'+(v.thumb?' sdv':'')+(lock?' lk':'');d.dataset.l=lock?1:0;d.dataset.vid=v.id;
 d.innerHTML='<div class="a" style="background:'+(v.thumb?'url('+SD.abs(v.thumb)+') center/cover':VGR)+'"></div><span class="cw">'+(prem?'Premium':(Date.now()-v.created<3*86400000?'New':''))+'</span><span class="sh"></span><span class="du">'+fmt(v.dur)+'</span><span class="vw"><svg viewBox="0 0 24 24"><use href="#eye"/></svg>'+vfmt(v.views)+'</span><div class="lc"><i><b class="lci"></b></i>Subscribers<br>only</div>'+(lock?'<span class="ulk"></span>':'');
 if(!d.querySelector('.cw').textContent)d.querySelector('.cw').remove();
 if(v.kind=='photo'){var du=d.querySelector('.du');if(du)du.textContent='Photo'}
 d.onclick=function(){SD.get('/api/videos/'+v.id).then(function(p){if(p.locked){toast('Subscribe to unlock this post');return}openPost(p)}).catch(SD.fail)};
 return d}
function vEmpty(g,txt){var el=$(g);if(!el)return;if(!el.querySelector('.t')){el.innerHTML='<p class="sdemp" style="grid-column:1/-1;margin:28px 8px;text-align:center;opacity:.6;font-size:14px">'+txt+'</p>'}else{var e=el.querySelector('.sdemp');if(e)e.remove()}}
function vCounts(){var a=$('g1').querySelectorAll('.t').length,b=$('g2').querySelectorAll('.t').length,t1=document.querySelector('.tb[data-p=p1] small'),t2=document.querySelector('.tb[data-p=p2] small');if(t1)t1.textContent=a;if(t2)t2.textContent=b;var t5=document.querySelector('.tb[data-p=p5] small');if(t5)t5.textContent=$('g5').querySelectorAll('.t').length;
 var mine=!SD.view;vEmpty('g1',mine?'No videos yet. Tap + to post your first one.':'No videos yet.');vEmpty('g2',mine?'Premium videos (2:00 or longer) show up here.':'No premium videos yet.');vEmpty('g5',mine?'Photos you post show up here. Your profile photo is not included.':'No photos yet.')}
function addVid(v,owner,top){var g=$(v.kind=='photo'?'g5':v.aud=='prem'?'g2':'g1'),e=g.querySelector('.sdemp');if(e)e.remove();var d=vTile(v,owner);if(top)g.insertBefore(d,g.firstChild);else g.appendChild(d);return d}
function loadVideos(list,owner){$('g1').innerHTML='';$('g2').innerHTML='';$('g5').innerHTML='';(list||[]).forEach(function(v){addVid(v,owner,false)});vCounts();sync()}
if(SD.session){
 if(SD.view){(function(V){
  var q=function(s){return document.querySelector(s)};
  q('#v-me .tt').textContent='@'+V.handle;q('#v-me .nm').textContent=V.name;q('#v-me .hn').textContent='@'+V.handle;document.title='Spicy Dollz · '+V.name;
  var bio=q('#v-me .bio');bio.textContent='';(V.prof.bio||'').split('\n').forEach(function(l,i){if(i)bio.appendChild(document.createElement('br'));bio.appendChild(document.createTextNode(l))});bio.classList.remove('empty');if(!(V.prof.bio||'').trim())bio.style.display='none';
  var K=['linkme','instagram','x','telegram','tiktok'];document.querySelectorAll('#v-me .soc .sc').forEach(function(a,i){var u=(V.prof.l||{})[K[i]];if(u){a.href=u;a.target='_blank';a.rel='noopener noreferrer';a.classList.remove('empty');a.style.display=''}else{a.removeAttribute('href');a.style.display='none'}});if(!Object.keys(V.prof.l||{}).length){var so=q('#v-me .soc');if(so)so.style.display='none'}
  var de=document.documentElement;if(V.avatar){de.style.setProperty('--avu','url("'+SD.abs(V.avatar)+'")');de.classList.add('hasav')}else{de.classList.remove('hasav');de.style.removeProperty('--avu')}
  var av=$('avw'),fr=av&&av.querySelector('.afr');if(fr)fr.remove();if(av){av.classList.remove('hf','sq');av.setAttribute('aria-label',V.name)}
  var ban=q('.ban'),bu=V.banner?SD.abs(V.banner):(V.banKey&&/^b\d+$/.test(V.banKey)?BI[+V.banKey.slice(1)-1]:null);if(ban){if(bu){ban.style.background='url('+bu+') center/cover no-repeat';ban.style.animation='none';ban.classList.add('img')}else{ban.style.background='';ban.style.animation='';ban.classList.remove('img')}}
  var vf=q('.nmr .vf');if(vf)vf.style.display=V.premium?'':'none';var sp=$('spb');if(sp)sp.hidden=!V.premium;var nm=q('.nmr .nm');if(nm){nm.removeAttribute('style');nm.className='nm'}
  var st=document.querySelectorAll('#v-me .st2 b'),views=0;V.videos.forEach(function(x){views+=x.views||0});if(st[0])st[0].textContent=vfmt(views);if(st[1])st[1].textContent=vfmt(V.subscribers);if(st[2])st[2].textContent='0';
  ['#ft3','#v-me .hdl','#avw .avc','#setBtn','#statBtn','.tb[data-p=p3]','.tb[data-p=p4]','#bsb'].forEach(function(s){var e=q(s);if(e)e.style.display='none'});
  $('v-me').addEventListener('click',function(e){var t=e.target;if(t.closest('#avw')||t.closest('.bio')||(t.closest('.soc .sc')&&!t.closest('.soc .sc').getAttribute('href'))){e.preventDefault();e.stopImmediatePropagation()}},true);
  var avin=$('avF');if(avin)avin.disabled=true;
  loadVideos(V.videos,false);
  var bkb=q('#v-me .top [aria-label=Back]');if(bkb){bkb.setAttribute('aria-label','Back to my profile');bkb.title='Back to my profile';bkb.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();location.hash='';location.reload()},true)}
 })(SD.view)}
 else loadVideos(SD.session.videos,true);
 /* keep the wallet fresh: incoming tips and subscribers */
 setInterval(function(){if(document.hidden)return;SD.get('/api/wallet').then(function(w){var n=(S.tx[0]||{}).d;wSync(w);badge();mallBal();if((w.tx[0]||{}).d!==n&&!$('v-wallet').hidden&&!shEl.classList.contains('on'))renderWallet()}).catch(function(){})},20000);
 window.sdAfterUploadFail=function(k){if(k=='sd_upban'){S.ban='sd';save();applyBan();try{renderMall()}catch(e){}}};
 if(SD.config.payments=='test'){var tb=document.createElement('div');tb.id='sdTest';tb.textContent='Test payments';tb.title='Payments are free until Stripe is connected';tb.hidden=true;document.body.appendChild(tb);var vm=$('v-mall');new MutationObserver(function(){tb.hidden=vm.hidden}).observe(vm,{attributes:true,attributeFilter:['hidden']})}
}
