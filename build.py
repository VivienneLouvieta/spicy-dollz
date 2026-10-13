#!/usr/bin/env python3
"""Builds public/index.html from the original prototype + server integration patches."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "original" / "Spicy-Dollz-Profile.html"
html = SRC.read_text()

def rep(s, old, new, count=1):
    n = s.count(old)
    if n != count:
        raise SystemExit(f"expected {count} match(es), found {n}: {old[:90]!r}")
    return s.replace(old, new)

def rrep(s, pat, new, flags=re.S):
    m = list(re.finditer(pat, s, flags))
    if len(m) != 1:
        raise SystemExit(f"regex expected 1 match, found {len(m)}: {pat[:90]!r}")
    return s[:m[0].start()] + new + s[m[0].end():]

# ---- split scripts ----
parts = re.split(r"(<script>|</script>)", html)
# parts: [pre, <script>, s0, </script>, mid, <script>, s1, </script>, mid2, <script>, s2, </script>, post]
assert len(parts) == 13, len(parts)
pre, s0, mid1, auth, mid2, main, post = parts[0], parts[2], parts[4], parts[6], parts[8], parts[10], parts[12]
assert "Storage.prototype" in s0

PHI = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="4.5" width="17" height="15" rx="3"/><circle cx="9" cy="10" r="1.8"/><path d="M20.5 16l-5-5-8.5 8.5"/></svg>'
_n = 0
def _tabs(x):
    global _n
    k1 = '<i class="lki" aria-hidden="true"></i><small>15</small></button>'
    k2 = '<div class="pnl" id="p2"><div class="gd" id="g2"></div></div>'
    if k1 in x:
        _n += 1
        x = x.replace(k1, k1 + '\n  <button class="tb" data-p="p5" aria-label="Photos" title="Photos">' + PHI + '<small>0</small></button>', 1)
        assert k2 in x
        x = x.replace(k2, k2 + '\n <div class="pnl" id="p5"><div class="gd" id="g5"></div></div>', 1)
    return x
pre, mid1, mid2, post = _tabs(pre), _tabs(mid1), _tabs(mid2), _tabs(post)
assert _n == 1, _n
boot = (ROOT / "client" / "boot.js").read_text()
extra = (ROOT / "client" / "app-server.js").read_text() + "\n" + (ROOT / "client" / "social.js").read_text()

# ================= AUTH SCRIPT =================
a = auth
a = rep(a, "var ACC={};try{ACC=JSON.parse(localStorage.getItem('sd_accts')||'{}')||{}}catch(e){ACC={}}", "var ACC={};")
a = rep(a, "c.querySelector('[data-forgot]').onclick=function(){toast('Password reset needs an account server. This prototype does not send emails.')};",
        "c.querySelector('[data-forgot]').onclick=function(){var em=c.querySelector('#e'+i).value.trim();if(!em){toast('Type your email first, then tap Forgot password.');c.querySelector('#e'+i).focus();return}SD.post('/api/auth/forgot',{email:em,returnUrl:location.href}).then(function(r){toast(r.message)}).catch(function(x){toast(x.message)})};")
a = rrep(a, r"c\.querySelectorAll\('\.soc'\)\.forEach\(function\(b\)\{b\.onclick=function\(\)\{var p=b\.dataset\.s.*?c\.classList\.add\('ok'\)\}\}\);",
         "c.querySelectorAll('.soc').forEach(function(b){b.onclick=function(){toast(b.dataset.s+' sign in needs '+b.dataset.s+' app keys on the server. Use email for now.')}});")
a = rep(a, "function ok(k,nm){go.disabled=false;go.textContent=up?'Create account':'Sign in';who=nm;via='email';akey=k;abase=ACC[k].base;",
        "function ok(k,nm,bs){go.disabled=false;go.textContent=up?'Create account':'Sign in';who=nm;via='email';akey=k;abase=bs;")
a = rrep(a, r"var email=e\.value\.trim\(\)\.toLowerCase\(\);\n    if\(up\)\{var dup=.*?ok\(k,ACC\[k\]\.name\)\}\)\}",
 "var email=e.value.trim().toLowerCase();\n"
 "    if(up){SD.post('/api/auth/signup',{name:n.value.trim(),email:email,password:p.value,base:t0(i),adult:a.checked}).then(function(r){SD.signedIn(r);ok(r.user.id,r.user.name,r.user.base)}).catch(function(x){var f=(x.data||{}).field;fail(SD.h(x.message),f=='name'?n:f=='password'?p:f=='adult'?null:e)})}\n"
 "    else{SD.post('/api/auth/login',{id:email,password:p.value,base:t0(i)}).then(function(r){SD.signedIn(r);ok(r.user.id,r.user.name,r.user.base)}).catch(function(x){var d=x.data||{};if(d.code=='wrong_base'){var bi=tIdx(d.base);fail('This account was created in <b>'+THEMES[bi].name+'</b>. Sign in from the '+THEMES[bi].name+' card. <button type=\"button\" class=\"lnk\" data-goto=\"'+bi+'\">Open '+THEMES[bi].name+'</button>');return}fail(SD.h(x.message),p)})}")
a = rep(a, "Prototype. Accounts stay only in this browser.", "Your account is stored on the Spicy Dollz server.")
TGI = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="12" fill="#29A9EB"/><path fill="#fff" d="M5.4 11.8l11.1-4.3c.5-.2 1 .1.8.9l-1.9 8.9c-.1.6-.5.8-1 .5l-2.9-2.1-1.4 1.3c-.2.2-.3.3-.6.3l.2-2.9 5.3-4.8c.2-.2 0-.3-.3-.1l-6.6 4.1-2.8-.9c-.6-.2-.6-.6.1-.9z"/></svg>'
a = rep(a, "<button class=\"soc\" type=\"button\" data-s=\"Google\">'+G+'Google</button>", "<button class=\"soc\" type=\"button\" data-s=\"Telegram\">" + TGI.replace("'", "\\'") + "Telegram</button>")
a = rep(a, "c.querySelectorAll('.soc').forEach(function(b){b.onclick=function(){toast(",
        "c.querySelectorAll('.soc').forEach(function(b){b.onclick=function(){if(b.dataset.s=='Telegram'){SD.telegram({base:t0(i),adult:c.querySelector('#a'+i).checked},function(r){who=r.user.name;via='telegram';akey=r.user.id;abase=r.user.base;c.querySelector('[data-h]').textContent=r.created?'Account created':'You are in';c.querySelector('[data-p]').textContent=r.created?'Welcome to Spicy Dollz, '+r.user.name+'. You signed up with Telegram.':'Welcome back, '+r.user.name+'.';c.classList.add('ok')},function(m){toast(m)});return}toast(")
a = a.replace("localStorage.", "SDS.")
assert "localStorage" not in a

# ================= MAIN SCRIPT =================
m = main
m = rep(m, "if(x&&x!='you'&&x!='guest'){n=x;h=x.replace(/[^A-Za-z0-9._]/g,'')||'user'}", "if(x&&x!='you'&&x!='guest'){n=x;h=a.h||x.replace(/[^A-Za-z0-9._]/g,'')||'user'}")
# subscription state + button
m = rep(m, "try{if(localStorage.getItem('sd_sub')=='1')setSub(true,false);}catch(e){}", "if(SD.view&&SD.view.subscribedUntil)setSub(true,false);")
m = rep(m, "sb.onclick=function(){if(subOn){setSub(false,true);return}subSheet()};",
        "sb.onclick=function(){if(!SD.view){toast('This is your own profile. Fans subscribe from your shared link.');return}if(subOn){SD.post('/api/unsubscribe',{to:tgt().h}).then(function(){setSub(false,true)}).catch(SD.fail);return}subSheet()};")
# receive tip sheet: no fake money
m = rrep(m, r"<button class=\"big\" id=\"sim\">Simulate an incoming tip \(demo\)</button>.*?closeSh\(\)\}\}\)\}\n else if\(a=='send'\)",
 "<button class=\"big\" id=\"sim\">Copy my profile link</button>',function(){$('sim').onclick=function(){copyTxt(location.href.split('#')[0]+'#@'+ME.h,function(ok){toast(ok?'<b>Profile link copied</b>':'Copy did not work on this device')})}})}\n else if(a=='send')")
# withdraw
m = rep(m, "$('kS').innerHTML=n>S.coins/100?'Not enough balance'", "$('kS').innerHTML=n>Math.min(S.coins,S.earned||0)/100?'You can withdraw up to '+money(Math.min(S.coins,S.earned||0)/100)+' of earnings'")
m = rrep(m, r"\$\('kGo'\)\.onclick=function\(\)\{var n=parseFloat\(v\)\|\|0;if\(n<10\|\|n>S\.coins/100\+1e-9\)return;.*?requested'\)\}",
 "$('kGo').onclick=function(){var n=parseFloat(v)||0;if(n<10||n>Math.min(S.coins,S.earned||0)/100+1e-9)return;SD.post('/api/wallet/withdraw',{usd:n,token:po.token,net:po.net,addr:po.addr}).then(function(r){wSync(r.wallet);mallBal();closeSh();renderWallet();toast('Withdrawal of <b>'+money(n)+'</b> in <b>'+po.token+'</b> ('+po.net+') requested &middot; pending review')}).catch(SD.fail)}")
# convert
m = rrep(m, r"if\(!dir\)\{if\(amt>S\.usd\)\{toast\('Not enough balance'\);return\}.*?added'\)\}",
 "if(!dir){if(amt>S.usd){toast('Not enough balance');return}SD.post('/api/wallet/convert',{dir:0,amt:amt}).then(function(r){wSync(r.wallet);closeSh();renderWallet();mallBal();toast('<b>+'+amt*100+'</b> '+SDI+' added')}).catch(SD.fail)}")
m = rrep(m, r"else\{if\(amt<=0\|\|amt>S\.coins\)\{toast\('Not enough <i class=\"sdz\" role=\"img\" aria-label=\"Spicy Dollz\"></i>'\);return\}S\.coins-=amt;.*?converted to <b>'\+money\(amt/100\)\+'</b>'\)\}",
 "else{if(amt<=0||amt>S.coins){toast('Not enough '+SDI);return}SD.post('/api/wallet/convert',{dir:1,amt:amt}).then(function(r){wSync(r.wallet);closeSh();renderWallet();mallBal();toast('<b>'+amt.toLocaleString('en-US')+' '+SDI+'</b> converted to <b>'+money(amt/100)+'</b>')}).catch(SD.fail)}")
# subscribe sheet
m = rep(m, "openSh('<h3>Subscribe to @'+ME.h+'</h3>", "openSh('<h3>Subscribe to @'+esc(tgt().h)+'</h3>")
m = rep(m, "S.coins-=C;S.tx.unshift({k:'subout',t:'out',n:'@'+ME.h+'',a:9,c:C,d:Date.now(),m:'One month'});save();mallBal();renderWallet();closeSh();setSub(true,true)",
        "SD.post('/api/subscribe',{to:tgt().h}).then(function(r){wSync(r.wallet);mallBal();renderWallet();closeSh();setSub(true,true)}).catch(SD.fail)")
# tip sheet
m = rep(m, "openSh('<h3>Send a tip</h3><p class=\"sub2\">to @'+ME.h+' &middot;", "openSh('<h3>Send a tip</h3><p class=\"sub2\">to @'+esc(tgt().h)+' &middot;")
m = rep(m, "$('tg').onclick=function(){addTip('you',amt/100,'Tip from profile');closeSh()}",
        "$('tg').onclick=function(){if(!SD.view){toast('You can\\'t tip yourself. Share your profile link so fans can tip you.');return}SD.post('/api/tip',{to:tgt().h,coins:amt,note:'Tip from profile'}).then(function(r){wSync(r.wallet);mallBal();closeSh();toast('<b>'+amt.toLocaleString('en-US')+' '+SDI+'</b> tip sent to @'+esc(tgt().h))}).catch(SD.fail)}")
# tx label for sent tips
m = rep(m, "x.k=='subout'?'Subscription':", "x.k=='subout'?'Subscription':x.k=='tipout'?'Tip sent':")
# mall: top-up pack -> checkout
m = rrep(m, r"if\(mTab==1&&mSel!=null\)\{S\.coins\+=PK\[mSel\]\[0\];.*?added to your Spicy Wallet'\)\}",
 "if(mTab==1&&mSel!=null){var pk=PK[mSel];b.disabled=true;SD.pay({kind:'pack',i:mSel},function(r,test){wSync(r.wallet);mallBal();badge();toast('<b>+'+pk[0]+' '+SDI+'</b> added to your Spicy Wallet'+(test?' (test payment)':''))});setTimeout(function(){b.disabled=false},1500)}")
# frame purchase
m = rrep(m, r"if\(!frOk\(fi\)\)\{if\(S\.coins<f\[1\]\)\{toast\('Not enough <i class=\"sdz\" role=\"img\" aria-label=\"Spicy Dollz\"></i> &middot; top up first'\);return\}S\.coins-=f\[1\];S\.own\.push\('f'\+fi\);S\.tx\.unshift\(\{[^}]*\}\)\}\n   S\.fr=fi;save\(\);mallBal\(\);applyFrame\(\);toast\('<b>'\+f\[0\]\+'</b> is now on your profile photo'\);renderMall\(\);\$\('m2'\)\.click\(\);m\.querySelectorAll\('\.fcx'\)\[fi\]\.click\(\)\}",
 "var finF=function(){S.fr=fi;save();mallBal();applyFrame();toast('<b>'+f[0]+'</b> is now on your profile photo');renderMall();$('m2').click();m.querySelectorAll('.fcx')[fi].click()};\n   if(!frOk(fi)){if(S.coins<f[1]){toast('Not enough '+SDI+' &middot; top up first');return}SD.post('/api/wallet/buy',{item:'f'+fi}).then(function(r){wSync(r.wallet);finF()}).catch(SD.fail);return}finF()}")
# banner purchase
m = rrep(m, r"if\(!bOwn\(bi\)\)\{if\(S\.coins<BANP\)\{toast\('Not enough '\+SDI\+' &middot; top up first'\);return\}S\.coins-=BANP;S\.own\.push\('b'\+bi\);S\.tx\.unshift\(\{[^}]*\}\)\}\n   S\.ban=bKey\(bi\);save\(\);applyBan\(\);toast\('<b>'\+bn\[0\]\+'</b> is now your profile banner'\);renderMall\(\);\$\('m3'\)\.click\(\);m\.querySelectorAll\('\.bcx'\)\[bi\]\.click\(\)\}",
 "var finB=function(){S.ban=bKey(bi);save();applyBan();toast('<b>'+bn[0]+'</b> is now your profile banner');renderMall();$('m3').click();m.querySelectorAll('.bcx')[bi].click()};\n   if(!bOwn(bi)){if(S.coins<BANP){toast('Not enough '+SDI+' &middot; top up first');return}SD.post('/api/wallet/buy',{item:'b'+bi}).then(function(r){wSync(r.wallet);finB()}).catch(SD.fail);return}finB()}")
# premium purchase + cancel
m = rrep(m, r"function buyPremium\(\)\{var p=PLANS\[mPl\];if\(premOn\(\)\)\{toast\('Spicy Premium is already active'\);return\}.*?mallBal\(\)\}",
 "function buyPremium(){var p=PLANS[mPl];if(premOn()){toast('Spicy Premium is already active');return}SD.pay({kind:'premium',i:mPl},function(r,test){wSync(r.wallet);S.th=S.th||base();save();setPremium(true,true);renderMall();$('m4').click();mallBal();if(test)toast('<b>Spicy Premium</b> activated (test payment)')})}")
m = rep(m, "pc.onclick=function(){S.prem=0;save();setPremium(false,true);renderMall();$('m4').click()}",
        "pc.onclick=function(){if(pc.dataset.c!='1'){pc.dataset.c='1';pc.textContent='Tap again to cancel';return}SD.post('/api/premium/cancel').then(function(r){wSync(r.wallet);setPremium(false,true);renderMall();$('m4').click()}).catch(SD.fail)}")
# video upload -> server
m = rrep(m, r"function postVideo\(\)\{.*?\}\nrenderUpload\(\);",
 "function postVideo(){if(!up.file)return;var go=$('upGo'),cap=$('upCap').value.trim(),aud=up.aud,prem=aud=='prem';\n"
 " var fd=new FormData();fd.append('file',up.file);fd.append('caption',cap);fd.append('aud',aud);fd.append('dur',String(up.dur||0));if(up.thumb)fd.append('thumb',up.thumb);\n"
 " go.disabled=true;go.textContent='Uploading 0%';\n"
 " SD.upload('/api/videos',fd,function(p){go.textContent=p<1?'Uploading '+Math.round(p*100)+'%':'Processing...'}).then(function(v){\n"
 "  if(up.url)URL.revokeObjectURL(up.url);if(SD.view){location.hash='';location.reload();return}addVid(v,true,true);vCounts();sync();toast('<b>Video posted</b> &middot; '+(aud=='all'?'public':aud=='subs'?'subscribers only':'premium'));\n"
 "  up={file:null,url:'',thumb:'',dur:0,aud:'all'};renderUpload();\n"
 "  document.querySelector('.bn [data-v=me]').click();document.querySelector('.tb[data-p='+(prem?'p2':'p1')+']').click();window.scrollTo({top:document.getElementById('v-me').querySelector('.tabs').offsetTop-20,behavior:'smooth'})\n"
 " }).catch(function(e){go.disabled=false;go.textContent='Post video';SD.fail(e)})}\nrenderUpload();")
# banner upload: size limit is enforced by server now; keep GIF check client side
# rename via server
m = rrep(m, r"function renameMe\(nn\)\{.*?return ''\}",
 "function renameMe(nn,hh){var a={};try{a=JSON.parse(localStorage.getItem('sd_auth')||'{}')||{}}catch(e){}a.n=nn;a.h=hh;try{localStorage.setItem('sd_auth',JSON.stringify(a))}catch(e){}\n"
 " ME.n=nn;ME.h=hh;\n"
 " var q=function(x){return document.querySelector(x)};q('#v-me .tt').textContent='@'+ME.h;q('#v-me .nm').textContent=ME.n;q('#v-me .hn').textContent='@'+ME.h;document.title='Spicy Dollz · '+ME.n;\n"
 " try{renderInbox()}catch(e){}try{renderMall()}catch(e){}return ''}")
m = rep(m, "if(nn!==ME.n){var rr=renameMe(nn);if(rr){$('epE').textContent=rr;return}}P.bio=$('epB').value.trim();P.l=l;save();render();closeSh();toast('<b>Profile</b> saved')}",
        "var fin=function(){P.bio=$('epB').value.trim();P.l=l;save();render();closeSh();toast('<b>Profile</b> saved')};if(nn!==ME.n){$('epS').disabled=true;SD.patch('/api/me',{name:nn}).then(function(r){renameMe(r.name,r.handle);fin()}).catch(function(x){$('epS').disabled=false;$('epE').textContent=x.message});return}fin()}")
# photos + videos in the upload view
m = rep(m, "<span class=\"syne\">New video</span>", "<span class=\"syne\">New post</span>")
m = rep(m, "<b>Select a video</b><small>MP4 or MOV from your device</small><input type=\"file\" id=\"upFile\" accept=\"video/*\" hidden>",
        "<b>Select a video or photo</b><small>MP4, MOV, WebM, JPG, PNG or WebP from your device</small><input type=\"file\" id=\"upFile\" accept=\"video/*,image/*\" hidden>")
m = rep(m, "<span class=\"dchip\" id=\"upDur\"></span></div><button class=\"lnk\" id=\"upChg\">Change video</button>",
        "<span class=\"dchip\" id=\"upDur\"></span><img id=\"upImg\" alt=\"Selected photo\" hidden style=\"display:block;width:100%;max-height:420px;object-fit:contain;border-radius:14px;background:#000\"></div><button class=\"lnk\" id=\"upChg\">Change file</button>")
m = rep(m, "<textarea id=\"upCap\" maxlength=\"150\" rows=\"3\" placeholder=\"Write a caption…\"></textarea>", "<textarea id=\"upCap\" maxlength=\"300\" rows=\"3\" placeholder=\"Write a caption… add #hashtags so people can find it\"></textarea>")
m = rep(m, "<button class=\"big\" id=\"upGo\" disabled>Post video</button>", "<button class=\"big\" id=\"upGo\" disabled>Post</button>")
m = rep(m, "up.file=file;up.url=URL.createObjectURL(file);var vid=$('upVid');vid.src=up.url;$('upDrop').hidden=true;$('upPrev').hidden=false;",
        "up.file=file;up.url=URL.createObjectURL(file);var vid=$('upVid'),im=$('upImg');$('upDrop').hidden=true;$('upPrev').hidden=false;up.kind=/^image\\//.test(file.type)?'photo':'video';\n"
        "  if(up.kind=='photo'){vid.removeAttribute('src');vid.hidden=true;$('upDur').hidden=true;im.hidden=false;im.src=up.url;up.dur=0;up.thumb='';chk();return}vid.hidden=false;$('upDur').hidden=false;im.hidden=true;vid.src=up.url;")
m = rep(m, "if(up.aud=='prem'&&up.file&&up.dur<120){ok=false;",
        "if(up.aud=='prem'&&up.kind=='photo'){ok=false;msg='Premium is for long videos. Pick \"Everyone\" or \"Subscribers only\" for photos.'}\n else if(up.aud=='prem'&&up.file&&up.dur<120){ok=false;")
m = rep(m, "if(!up.file)msg='Select a video to continue.';", "if(!up.file)msg='Select a video or photo to continue.';")
m = rep(m, "toast('<b>Video posted</b> &middot; '", "SD.reels=null;SD.rlAt=0;try{loadHome()}catch(e){}toast('<b>Posted</b> &middot; '")
m = rep(m, "go.textContent='Post video';SD.fail(e)", "go.textContent='Post';SD.fail(e)")
m = rep(m, "Sample figures for the prototype", "Updated live from your posts")
# robust picker + phone formats
m = rep(m, "$('v-up').addEventListener('click',function(e){if(e.target.closest&&e.target.closest('#upDrop')&&!e.target.closest('input'))$('upFile').click()});",
        "$('v-up').addEventListener('click',function(e){if(e.target.closest&&e.target.closest('#upDrop')&&!e.target.closest('input')){e.preventDefault();SD.log('pick','upload');$('upFile').click()}});")
m = rep(m, "up.kind=/^image\\//.test(file.type)?'photo':'video';",
        "up.kind=(/^image\\//.test(file.type)||/\\.(heic|heif|jpe?g|png|webp|gif|avif)$/i.test(file.name||''))?'photo':'video';SD.log('chosen',up.kind+' '+(file.type||'?')+' '+file.size);\n"
        "  im.onerror=function(){im.hidden=true;$('upHint').textContent='Preview not available for this photo. You can still post it.'};")
m = rep(m, "vid.onerror=function(){toast('This video could not be read');up.file=null;chk()}};",
        "vid.onerror=function(){if(!up.file)return;up.dur=0;up.thumb='';vid.hidden=true;$('upDur').hidden=true;chk();$('upHint').textContent='This browser cannot preview '+esc(up.file.name||'this video')+', but you can still post it.'}};")
m = rep(m, "toast('This image could not be read. Try a JPG or PNG.')};if(url)im.src=url;else im.onerror();",
        "window.sdRawAvatar(f)};if(url)im.src=url;else im.onerror();")
m = rep(m, "function pick(){var f=inp.files&&inp.files[0];if(!f)return;", "var lastPick=null;function pick(){var f=inp.files&&inp.files[0];if(!f||f===lastPick)return;lastPick=f;setTimeout(function(){lastPick=null},1500);SD.log('chosen','avatar '+(f.type||'?')+' '+f.size);")
# tips from reels / creator sheets target that creator
m = rep(m, "$('tg').onclick=function(){if(!SD.view){toast(", "$('tg').onclick=function(){if(!SD.view&&!SD.tipTo){toast(")
m = rep(m, "shareSheet(RL[j][0]+': '+RL[j][1],'reel-'+(j+1))", "shareSheet('@'+RL[j][0]+' on Spicy Dollz','@'+RL[j][0])")
# own-profile ISNEW logic: every server account is a real account
# reels/profile tip: show balance + top up
m = rep(m, "goes straight to her Spicy Wallet</p>", "goes straight to her Spicy Wallet</p><p class=\"sub2 sdbal\">Your balance: <b>'+S.coins.toLocaleString('en-US')+' '+SDI+'</b> &middot; <button type=\"button\" class=\"lnk\" id=\"tpW\">Top up</button></p>")
m = rep(m, "$('tc').querySelectorAll('button').forEach(function(b){b.onclick=function(){amt=+b.dataset.a;",
        "$('tpW').onclick=function(){closeSh();document.querySelector('.bn [data-v=wallet]').click()};$('tc').querySelectorAll('button').forEach(function(b){b.onclick=function(){amt=+b.dataset.a;")
m = rep(m, "toast('<b>'+amt.toLocaleString('en-US')+' '+SDI+'</b> tip sent to @'+esc(tgt().h))}).catch(SD.fail)}",
        "toast('<b>'+amt.toLocaleString('en-US')+' '+SDI+'</b> tip sent to @'+esc(tgt().h))}).catch(function(x){if(x.status==402){closeSh();document.querySelector('.bn [data-v=wallet]').click();toast('Top up your Spicy Wallet to send this tip')}else SD.fail(x)})}")
# photos tab routing after posting
m = rep(m, "(prem?'p2':'p1')", "(v.kind=='photo'?'p5':prem?'p2':'p1')")
# dedicated tags field in the upload form
m = rep(m, "placeholder=\"Write a caption… add #hashtags so people can find it\"></textarea>'+",
        "placeholder=\"Write a caption…\"></textarea>'+\n '<label class=\"fl3\" for=\"upTagI\">Tags</label><div class=\"sdtags\" id=\"upTags\"><input id=\"upTagI\" maxlength=\"30\" placeholder=\"Add a tag, then press Enter\" autocomplete=\"off\" autocapitalize=\"off\" enterkeyhint=\"done\"><button type=\"button\" id=\"upTagA\" aria-label=\"Add tag\">Add</button></div><p class=\"sdth\" id=\"upTagH\">Up to 10 tags so people can find your post. Letters, numbers and _ only.</p>'+")
m = rep(m, "fd.append('caption',cap);", "fd.append('caption',cap);fd.append('tags',(SD.upTags||[]).join(','));")
m = rep(m, "up={file:null,url:'',thumb:'',dur:0,aud:'all'};renderUpload();", "up={file:null,url:'',thumb:'',dur:0,aud:'all'};SD.upTags=[];renderUpload();")
m = m.replace("localStorage.", "SDS.")
assert "localStorage" not in m
# append server integration inside the main IIFE
idx = m.rstrip().rfind("})();")
m = m[:idx] + extra + "\n" + m[idx:]

out = (pre + "<script>\n" + boot + "\n</script>" + mid1.lstrip("\n").replace("", "", 0)
       + '<script type="text/x-sd">' + a + "</script>" + mid2
       + '<script type="text/x-sd">' + m + "</script>" + post)
out = out.replace("<title>", "<title>", 1)
(ROOT / "public").mkdir(exist_ok=True)
(ROOT / "public" / "index.html").write_text(out)
print("built", len(out))
