/* ===== Server: social platform (reels, home, comments, follows, inbox, stats, moderation) ===== */
(function(){var st=document.createElement('style');st.textContent=
'.rv .rbg.sdm{filter:none!important;background:#0b0710!important}.rv .rbg.sdm i{display:none}.rv .rbg video,.rv .rbg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.rv .rbg img.sdbl{filter:blur(14px) brightness(.8);transform:scale(1.15)}'+
'.sdlk{position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);z-index:4;display:grid;gap:10px;justify-items:center;text-align:center;color:#fff;width:min(260px,80%)}.sdlk b{font-size:17px;text-shadow:0 1px 6px #0008}.sdlk button,.sdcta{border:0;border-radius:999px;padding:11px 20px;background:#ff4696;color:#fff;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;box-shadow:0 6px 18px #0004}'+
'.sdre{height:100%;display:grid;place-content:center;gap:14px;text-align:center;padding:30px;color:#fff;background:linear-gradient(165deg,#2a1440,#0c0816)}.sdre p{opacity:.75;margin:0;font-size:14px}.sdre b{font-size:19px}'+
'.rv .rinf p a.sdtag,.sdcap a.sdtag{color:inherit;font-weight:700;text-decoration:none;cursor:pointer}.rwho b[data-a=who]{cursor:pointer}.sdmute{position:absolute;left:14px;top:calc(env(safe-area-inset-top,0px) + 70px);z-index:4;border:0;border-radius:999px;padding:6px 11px;background:#0007;color:#fff;font-size:12px;font-weight:600;pointer-events:none;opacity:0;transition:opacity .3s}.sdmute.on{opacity:1}'+
'.dt.sdp{position:relative;overflow:hidden;cursor:pointer;align-self:flex-start;height:auto;min-height:0;min-width:0;contain:size;width:31%;aspect-ratio:3/4.3}.dt.sdp *{font-family:inherit}'+'.dt.sdp em{position:absolute;left:8px;bottom:8px;right:8px;color:#fff;font-size:11px;font-weight:600;line-height:1.25;font-style:normal;text-shadow:0 1px 3px #000a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.dt.sdp.lk:after{content:"Subscribers";position:absolute;top:8px;left:8px;padding:3px 8px;border-radius:999px;background:#000a;color:#fff;font-size:10px;font-weight:700}.dt.sdp.ph:before{content:"Photo";position:absolute;top:8px;right:8px;padding:3px 8px;border-radius:999px;background:#fff;color:#1e1033;font-size:10px;font-weight:700}'+
'.dt.sdp.lk.ph:before{display:none}.sdhe{flex:1 0 100%;padding:18px;border-radius:18px;background:#0000000d;font-size:14px;text-align:center;opacity:.8}'+
'.sdib{position:absolute;top:4px;right:2px;min-width:17px;height:17px;padding:0 4px;border-radius:999px;background:#ff2d6f;color:#fff;font:700 10px/17px -apple-system,sans-serif;text-align:center;display:none}.sdib.on{display:block}'+
'.pmed{display:block;width:100%;max-height:62vh;object-fit:contain;border-radius:14px;background:#000;margin:6px 0 10px}.pmed.sdbl{filter:blur(16px);object-fit:cover;height:300px}.sdlkw{position:relative;overflow:hidden;border-radius:14px}.sdlkw .sdlk{top:50%}'+
'.sdcap{margin:0 0 10px;font-size:14px;line-height:1.45;white-space:pre-wrap;word-break:break-word}.sdpa{display:flex;gap:8px;flex-wrap:wrap}.sdpa button{flex:1;min-width:70px;border:0;border-radius:12px;padding:11px 8px;background:#0000000f;color:inherit;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer}.sdpa button.on{background:#ff4696;color:#fff}.sdpa button{display:flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap}.sdpa svg{width:19px;height:19px;flex:none}'+
'.cmr{position:relative}.cmr .cmx{position:absolute;right:0;top:2px;border:0;background:none;color:inherit;opacity:.5;font-size:12px;cursor:pointer;padding:4px}.cmr small.ago{opacity:.55;font-weight:500;margin-left:6px;font-size:11px}'+
'.cav.im{background-size:cover!important;background-position:center!important;color:transparent!important}.rav.im{background-size:cover!important;background-position:center!important}'+
'.cmsg .m small{display:block;opacity:.55;font-size:10px;margin-top:3px}.sdnote{font-size:13px;opacity:.7;text-align:center;margin:10px 0}'+
'.sdrl{display:grid;gap:8px;margin:10px 0}.sdrl .srow2{align-items:flex-start;flex-wrap:wrap;gap:8px 6px}.sdrl .srow2 div{flex:1 0 100%;min-width:0}.sdrl .srow2 small{display:block;opacity:.65;font-size:12px;margin-top:2px;word-break:break-word}.sdrl .srow2 .fpl{margin-left:0}'+
'.tgg button.sdp{background-size:cover!important;background-position:center!important}';
document.head.appendChild(st)})();
function ago(t){var s=Math.max(1,(Date.now()-t)/1000);if(s<60)return 'now';if(s<3600)return Math.floor(s/60)+'m';if(s<86400)return Math.floor(s/3600)+'h';if(s<604800)return Math.floor(s/86400)+'d';return Math.floor(s/604800)+'w'}
function avb(u){return u&&u.avatar?"url('"+SD.abs(u.avatar).replace(/['"()\\\s]/g,encodeURIComponent)+"')":G(hsh((u&&u.handle)||'x')%9)}
function avc(u,cls){var im=u&&u.avatar,nl=cls=='rav';return '<span class="'+cls+(im?' im':'')+'" style="background:'+avb(u)+(im?' center/cover':'')+'">'+(im||nl?'':esc(((u&&u.handle)||'?')[0].toUpperCase()))+'</span>'}
function capH(t){return esc(t||'').replace(/#([A-Za-z0-9_]{2,30})/g,'<a class="sdtag" data-t="$1">#$1</a>')}
function meH(){return SD.session?SD.session.user.handle:''}
function isMe(h){return !!h&&h.toLowerCase()==meH().toLowerCase()}
function goProfile(h){closeSh();if(isMe(h)){if(SD.view){location.hash='';location.reload()}else backMe();return}location.hash='@'+h;location.reload()}
function needIn(){if(SD.session)return true;toast('Sign in to continue');return false}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('.sdtag');if(a){e.preventDefault();e.stopPropagation();tagSheet(a.dataset.t)}},true);
/* pause media when a sheet closes */
new MutationObserver(function(){if(!shEl.classList.contains('on'))shEl.querySelectorAll('video').forEach(function(v){try{v.pause()}catch(e){}})}).observe(shEl,{attributes:true,attributeFilter:['class']});

/* ---------- reels ---------- */
function renderReels(){var el=$('v-disc');if(!el)return;
 if(!SD.reels){el.innerHTML='<div class="rfeed" id="rfeed"><div class="rv"><div class="sdre"><b>Loading posts...</b></div></div></div>';if(!SD.rlBusy)loadReels();return}
 drawReels()}
function loadReels(){SD.rlBusy=1;return SD.get('/api/feed?limit=40').then(function(l){SD.reels=l;SD.rlAt=Date.now();SD.rlBusy=0;drawReels()},function(e){SD.rlBusy=0;SD.reels=[];drawReels();SD.fail(e)})}
function drawReels(){var el=$('v-disc'),L=SD.reels||[];RL.length=0;
 L.forEach(function(v){var r=[v.user.handle,v.caption,v.user.handle+' · Original audio',v.likes,v.comments];r.v=v;RL.push(r)});
 if(!L.length){el.innerHTML='<div class="rfeed" id="rfeed"><div class="rv"><div class="sdre"><b>No posts yet</b><p>Videos and photos from creators show up here.</p><button class="sdcta" id="sdReUp" type="button">Post the first one</button></div></div></div>';
  $('sdReUp').onclick=function(){document.querySelector('.bn [data-v=up]').click()};return}
 var h='<div class="rfeed" id="rfeed">';
 L.forEach(function(v,i){var u=v.user,med;
  if(v.locked)med='<img class="sdbl" alt="" src="'+SD.abs(v.thumb||'')+'">';
  else if(v.kind=='photo')med='<img alt="'+esc(v.caption||'Photo')+'" loading="lazy" src="'+SD.abs(v.url)+'">';
  else med='<video muted loop playsinline preload="none" data-src="'+SD.abs(v.url)+'"'+(v.thumb?' poster="'+SD.abs(v.thumb)+'"':'')+'></video>';
  h+='<article class="rv" data-i="'+i+'" data-id="'+v.id+'"><div class="rbg sdm">'+med+'</div><div class="rsc"></div><div class="rhrt"><svg viewBox="0 0 24 24" fill="#fff"><path d="M12 20s-7.500-4.600-7.500-10.200A4.300 4.300 0 0112 7.500a4.300 4.300 0 017.500 2.300C19.500 15.400 12 20 12 20z"/></svg></div>'+
  (v.locked?'<div class="sdlk"><b>Subscribers only</b><button type="button" data-a="unl">Subscribe to unlock</button></div>':'')+
  (v.kind=='video'&&!v.locked?'<span class="sdmute">Tap for sound</span>':'')+
  '<div class="ract">'+(v.kind=='video'&&!v.locked?'<button data-a="snd" class="sdsb" aria-label="Sound on or off">'+sndIc(SD.rlMuted!==false)+'<small>'+(SD.rlMuted===false?'Sound':'Muted')+'</small></button>':'')+'<button data-a="tip" class="tipb" aria-label="'+(v.mine?'Your tips in Spicy Wallet':'Send a tip')+'"><i class="mi" style="--m:var(--gift)"></i><small>Tip</small></button>'+'<button data-a="like" class="'+(v.liked?'on':'')+'" aria-label="Like">'+heartI+'<b>'+kf(v.likes)+'</b></button><button aria-label="Comments">'+cmtI+'<b>'+v.comments+'</b></button><button aria-label="Share">'+shI+'</button><button data-a="more" aria-label="More options">'+dotsI+'</button></div>'+
  '<div class="rinf"><div class="rwho">'+avc(u,'rav').replace('class="rav','data-a="who" class="rav')+'<b data-a="who">'+esc(u.handle)+'</b>'+(u.premium?VER:'')+(v.mine?'':'<button class="rfl'+(v.following?' on':'')+'" data-a="fol">'+(v.following?'Following':'Follow')+'</button>')+'</div><p>'+capH(v.caption)+'</p></div></article>'});
 el.innerHTML=h+'</div>';
 var feed=$('rfeed');
 feed.querySelectorAll('.rv[data-id]').forEach(function(a){var i=+a.dataset.i,v=L[i],lb=a.querySelector('[data-a=like]'),vid=a.querySelector('video');
  function setL(on){if(!needIn())return;if(on==v.liked)return;v.liked=on;v.likes+=on?1:-1;RL[i][3]=v.likes;lb.classList.toggle('on',on);lb.querySelector('b').textContent=kf(v.likes);
   SD.post('/api/videos/'+v.id+'/like',{on:on}).then(function(r){v.likes=r.likes;lb.querySelector('b').textContent=kf(r.likes)}).catch(SD.fail)}
  lb.onclick=function(e){e.stopPropagation();setL(!v.liked)};
  var tb=a.querySelector('[data-a=tip]');if(tb)tb.onclick=function(e){e.stopPropagation();if(!needIn())return;if(v.mine||isMe(v.user&&v.user.handle)){closeSh();document.querySelector('.bn [data-v=wallet]').click();toast('Tips from fans land in your <b>Spicy Wallet</b>');return}SD.tipTo={h:v.user.handle,n:v.user.name};tipSheet()};
  a.querySelectorAll('[data-a=who]').forEach(function(w){w.onclick=function(e){e.stopPropagation();creatorSheet(v.user.handle)}});
  var ul=a.querySelector('[data-a=unl]');if(ul)ul.onclick=function(e){e.stopPropagation();goProfile(v.user.handle)};
  a.querySelector('[data-a=more]').onclick=function(e){e.stopPropagation();moreSheet(v,function(){a.remove()})};
  a.addEventListener('dblclick',function(){if(v.locked)return;setL(true);var hh=a.querySelector('.rhrt');hh.classList.remove('pop');void hh.offsetWidth;hh.classList.add('pop')});
  if(vid){var tog=function(e){if(e)e.stopPropagation();setSnd(vid.muted,a)};a.querySelector('.rbg').onclick=function(){tog()};var sb=a.querySelector('[data-a=snd]');if(sb)sb.onclick=tog;var mh=a.querySelector('.sdmute');if(mh){mh.style.pointerEvents='auto';mh.style.cursor='pointer';mh.onclick=tog}}
  var f=a.querySelector('[data-a=fol]');if(f)f.onclick=function(e){e.stopPropagation();if(!needIn())return;var on=!f.classList.contains('on');
   SD.post('/api/follow/'+encodeURIComponent(v.user.handle),{on:on}).then(function(){feed.querySelectorAll('.rv[data-id]').forEach(function(b){var j=+b.dataset.i;if(L[j].user.handle==v.user.handle){L[j].following=on;var ff=b.querySelector('[data-a=fol]');if(ff){ff.classList.toggle('on',on);ff.textContent=on?'Following':'Follow'}}});toast(on?'Following <b>'+esc(v.user.handle)+'</b>':'Unfollowed')}).catch(SD.fail)}});
 if(SD.rlIO)SD.rlIO.disconnect();
 SD.rlIO=new IntersectionObserver(function(es){es.forEach(function(en){var a=en.target,v=L[+a.dataset.i],vid=a.querySelector('video');
  if(en.isIntersecting&&en.intersectionRatio>.6&&!$('v-disc').hidden){if(v&&!v.locked&&!a.dataset.seen){a.dataset.seen=1;SD.post('/api/videos/'+v.id+'/view').catch(function(){})}
   if(vid){if(!vid.src)vid.src=vid.dataset.src;vid.muted=SD.rlMuted===true;var p=vid.play();if(p&&p.catch)p.catch(function(){if(!vid.muted){vid.muted=true;sndUI(a,true);var m=a.querySelector('.sdmute');if(m){m.textContent='Tap for sound';m.classList.add('on');setTimeout(function(){m.classList.remove('on')},2200)}var p2=vid.play();if(p2&&p2.catch)p2.catch(function(){})}});sndUI(a,vid.muted)}}
  else if(vid){try{vid.pause()}catch(e){}}})},{threshold:[0,.6,1]});
 feed.querySelectorAll('.rv[data-id]').forEach(function(a){SD.rlIO.observe(a)})}
function goReels(i){document.querySelector('.bn [data-v=disc]').click();setTimeout(function(){var a=document.querySelectorAll('#rfeed .rv')[RL.length?i%RL.length:0];if(a)a.scrollIntoView({block:'start'})},60)}
function reelTo(id){var k=-1;(SD.reels||[]).forEach(function(v,i){if(v.id==id)k=i});if(k>=0){closeSh();goReels(k);return true}return false}
(function(){var nb=document.querySelector('.bn [data-v=disc]');if(nb)nb.addEventListener('click',function(){if(!SD.rlBusy&&(!SD.rlAt||Date.now()-SD.rlAt>45000))loadReels()});
 var vd=$('v-disc');new MutationObserver(function(){if(vd.hidden)vd.querySelectorAll('video').forEach(function(v){try{v.pause()}catch(e){}});else if(SD.rlIO){var f=$('rfeed');if(f)f.querySelectorAll('.rv[data-id]').forEach(function(a){SD.rlIO.unobserve(a);SD.rlIO.observe(a)})}}).observe(vd,{attributes:true,attributeFilter:['hidden']})})();

/* ---------- post viewer, comments, more ---------- */
function syncPost(v){(SD.reels||[]).forEach(function(r,i){if(r.id==v.id){r.likes=v.likes;r.liked=v.liked;r.comments=v.comments;var a=document.querySelector('#rfeed .rv[data-id="'+v.id+'"]');if(a){var lb=a.querySelector('[data-a=like]');lb.classList.toggle('on',!!v.liked);lb.querySelector('b').textContent=kf(v.likes);var cb=a.querySelector('[aria-label=Comments] b');if(cb)cb.textContent=v.comments}}})}
function openPostId(id){SD.get('/api/videos/'+id).then(openPost).catch(SD.fail)}
function openPost(v){var u=v.user||{handle:meH(),name:''},med;
 if(v.locked)med='<div class="sdlkw"><img class="pmed sdbl" alt="" src="'+SD.abs(v.thumb||'')+'"><div class="sdlk"><b>Subscribers only</b><button type="button" id="ppU">Subscribe on @'+esc(u.handle)+'</button></div></div>';
 else if(v.kind=='photo')med='<img class="pmed" alt="'+esc(v.caption||'Photo')+'" src="'+SD.abs(v.url)+'">';
 else med='<video class="pmed" src="'+SD.abs(v.url)+'" controls autoplay playsinline'+(v.thumb?' poster="'+SD.abs(v.thumb)+'"':'')+'></video>';
 openSh('<div class="cth" id="ppW" style="cursor:pointer">'+avc(u,'cav sm')+'<b>@'+esc(u.handle)+'</b></div>'+med+(v.caption?'<p class="sdcap">'+capH(v.caption)+'</p>':'')+
  '<div class="sdpa"><button type="button" id="ppL" aria-label="Like" class="'+(v.liked?'on':'')+'">'+heartI+'<span>'+kf(v.likes)+'</span></button><button type="button" id="ppC" aria-label="Comments">'+cmtI+v.comments+'</button><button type="button" id="ppS" aria-label="Share">'+shI+'</button><button type="button" id="ppM" aria-label="More options">&middot;&middot;&middot;</button></div>',function(){
  $('ppW').onclick=function(){goProfile(u.handle)};
  var pu=$('ppU');if(pu)pu.onclick=function(){goProfile(u.handle)};
  $('ppL').onclick=function(){if(!needIn())return;if(v.locked){toast('Subscribe to like this post');return}var on=!v.liked,b=this;v.liked=on;v.likes+=on?1:-1;b.classList.toggle('on',on);b.querySelector('span').textContent=kf(v.likes);
   SD.post('/api/videos/'+v.id+'/like',{on:on}).then(function(r){v.likes=r.likes;syncPost(v)}).catch(SD.fail)};
  $('ppC').onclick=function(){commentsFor(v)};
  $('ppS').onclick=function(){shareSheet('@'+u.handle+' on Spicy Dollz','@'+u.handle)};
  $('ppM').onclick=function(){moreSheet(v,function(){if(SD.reels)SD.reels=SD.reels.filter(function(x){return x.id!=v.id});var t=document.querySelector('.t[data-vid="'+v.id+'"]');if(t)t.remove();try{vCounts()}catch(e){}})}})}
function cmRow2(c){return '<div class="cmr" data-cid="'+c.id+'">'+avc({handle:c.handle},'cav sm')+'<div><b data-h="'+esc(c.handle)+'" style="cursor:pointer">'+esc(c.handle)+'<small class="ago">'+ago(c.created)+'</small></b><p>'+esc(c.text)+'</p></div>'+(c.mine?'<button class="cmx" type="button" aria-label="Delete comment">Delete</button>':'<button class="cmx" type="button" data-rp="1" aria-label="Report comment">Report</button>')+'</div>'}
function commentsFor(v){if(v.locked){toast('Subscribe to see the comments');return}
 openSh('<h3>Comments <small id="cmN">'+v.comments+'</small></h3><div class="cml" id="cml"><p class="sdnote">Loading...</p></div><form class="cin" id="cmF"><input id="cmI" maxlength="500" placeholder="Add a comment" autocomplete="off" aria-label="Add a comment"><button aria-label="Post comment">'+shI+'</button></form>',function(){
  var box=$('cml');
  function bind(){box.querySelectorAll('.cmr').forEach(function(r){var x=r.querySelector('.cmx'),cid=r.dataset.cid;
   r.querySelector('[data-h]').onclick=function(){creatorSheet(this.dataset.h)};
   x.onclick=function(){if(x.dataset.rp){reportSheet({comment:+cid},'comment');return}SD.del('/api/comments/'+cid).then(function(){r.remove();v.comments=Math.max(0,v.comments-1);$('cmN').textContent=v.comments;syncPost(v)}).catch(SD.fail)}})}
  SD.get('/api/videos/'+v.id+'/comments').then(function(l){v.comments=l.length;$('cmN').textContent=l.length;syncPost(v);box.innerHTML=l.length?l.map(cmRow2).join(''):'<p class="sdnote" id="cmE">No comments yet. Say something nice.</p>';bind();box.scrollTop=1e5}).catch(function(e){box.innerHTML='<p class="sdnote">'+esc(e.message)+'</p>'});
  $('cmF').onsubmit=function(e){e.preventDefault();if(!needIn())return;var inp=$('cmI'),t=inp.value.trim();if(!t)return;inp.disabled=true;
   SD.post('/api/videos/'+v.id+'/comments',{text:t}).then(function(c){inp.disabled=false;inp.value='';var em=$('cmE');if(em)em.remove();box.insertAdjacentHTML('beforeend',cmRow2(c));bind();v.comments++;$('cmN').textContent=v.comments;box.scrollTop=1e5;syncPost(v)}).catch(function(x){inp.disabled=false;SD.fail(x)})}})}
function commentsSheet(i){var r=RL[i];if(r&&r.v)commentsFor(r.v)}
var RPR=['Someone may be under 18','Non-consensual or private content','Stolen or reposted content','Harassment or hate','Spam or scam','Something else'];
function reportSheet(target,what){if(!needIn())return;openSh('<h3>Report '+what+'</h3><p class="sub2">Reports go to the Spicy Dollz moderators. The person is not told who reported them.</p><div class="rsl">'+RPR.map(function(r,i){return '<button type="button" data-r="'+i+'"><b>'+r+'</b></button>'}).join('')+'</div>',function(){
  shEl.querySelectorAll('[data-r]').forEach(function(b){b.onclick=function(){var o=Object.assign({reason:RPR[+b.dataset.r]},target);SD.post('/api/report',o).then(function(){closeSh();toast('<b>Thanks</b> &middot; our moderators will review it')}).catch(SD.fail)}})})}
function blockUser(h,done){if(!needIn())return;SD.post('/api/blocks',{handle:h}).then(function(){closeSh();toast('<b>@'+esc(h)+'</b> blocked');SD.reels=null;SD.rlAt=0;if(!$('v-disc').hidden)renderReels();loadInbox();if(done)done()}).catch(SD.fail)}
function moreSheet(v,removed){var u=v.user||{handle:meH()},mine=v.mine||isMe(u.handle),adm=SD.session&&SD.session.user.role=='admin';
 openSh('<h3>Post options</h3><div class="rsl"><button type="button" data-k="lnk"><b>Copy profile link</b><small>@'+esc(u.handle)+'</small></button>'+
  (mine?'<button type="button" data-k="del"><b>Delete this post</b><small>Removes it for everyone</small></button>':'<button type="button" data-k="rep"><b>Report post</b><small>Send it to moderators</small></button><button type="button" data-k="blk"><b>Block @'+esc(u.handle)+'</b><small>Hide their posts and messages</small></button>')+
  (adm&&!mine?'<button type="button" data-k="rm"><b>Remove post (admin)</b><small>Hide it from the platform</small></button><button type="button" data-k="ban"><b>Suspend @'+esc(u.handle)+' (admin)</b><small>Signs them out and hides their profile</small></button>':'')+'</div>',function(){
  shEl.querySelectorAll('[data-k]').forEach(function(b){b.onclick=function(){var k=b.dataset.k;
   if(k=='lnk'){copyTxt(location.href.split('#')[0]+'#@'+u.handle,function(ok){closeSh();toast(ok?'<b>Link copied</b>':'Could not copy the link')})}
   else if(k=='rep')reportSheet({video:v.id},'post');
   else if(k=='blk')blockUser(u.handle);
   else if(k=='del'||k=='rm'||k=='ban'){if(b.dataset.c!='1'){b.dataset.c='1';b.querySelector('small').textContent='Tap again to confirm';return}
    var p=k=='del'?SD.del('/api/videos/'+v.id):k=='rm'?SD.post('/api/admin/posts/'+v.id+'/remove'):SD.post('/api/admin/users/'+encodeURIComponent(u.handle)+'/ban',{on:true});
    p.then(function(){closeSh();toast(k=='ban'?'<b>@'+esc(u.handle)+'</b> suspended':'Post removed');if(removed)removed();SD.reels=null;SD.rlAt=0}).catch(SD.fail)}}})})}

/* ---------- creators, tags, search ---------- */
function creatorSheet(n){n=String(n||'').replace(/^@/,'');if(!n)return;
 openSh('<p class="sdnote">Loading @'+esc(n)+'...</p>');
 SD.get('/api/users/'+encodeURIComponent(n)).then(function(c){var me=isMe(c.handle),k=c.counts||{};
  openSh('<div class="crh">'+avc(c,'cav big')+'<div><b>'+esc(c.name)+(c.premium?VER:'')+'</b><small>@'+esc(c.handle)+'</small></div></div><div class="crs"><div><b>'+kf(k.followers||0)+'</b><span>followers</span></div><div><b>'+(k.posts||0)+'</b><span>posts</span></div><div><b>'+kf(k.likes||0)+'</b><span>likes</span></div></div>'+
   (c.prof&&c.prof.bio?'<p class="sdcap" style="margin-top:4px">'+esc(c.prof.bio)+'</p>':'')+
   '<div class="cra">'+(me?'':'<button class="cb on" id="crF" type="button">'+(c.following?'Following':'Follow')+'</button>')+'<button class="cb" id="crW" type="button">'+(me?'My profile':'View profile')+'</button>'+(me?'':'<button class="cb" id="crM" type="button">Message</button>')+'</div>'+
   (me?'':'<p class="sdnote"><a href="#" id="crR" style="color:inherit">Report</a> &middot; <a href="#" id="crB" style="color:inherit">'+(c.blocked?'Unblock':'Block')+'</a></p>'),function(){
   var f=$('crF');if(f)f.onclick=function(){if(!needIn())return;var on=!c.following;SD.post('/api/follow/'+encodeURIComponent(c.handle),{on:on}).then(function(){c.following=on;f.textContent=on?'Following':'Follow';toast(on?'Following <b>'+esc(c.handle)+'</b>':'Unfollowed');(SD.reels||[]).forEach(function(v){if(v.user.handle==c.handle)v.following=on})}).catch(SD.fail)};
   $('crW').onclick=function(){goProfile(c.handle)};
   var m=$('crM');if(m)m.onclick=function(){chatWith(c.handle)};
   var r=$('crR');if(r)r.onclick=function(e){e.preventDefault();reportSheet({handle:c.handle},'account')};
   var b=$('crB');if(b)b.onclick=function(e){e.preventDefault();if(c.blocked){SD.del('/api/blocks/'+encodeURIComponent(c.handle)).then(function(){closeSh();toast('<b>@'+esc(c.handle)+'</b> unblocked')}).catch(SD.fail)}else blockUser(c.handle)}})
 }).catch(function(e){closeSh();SD.fail(e)})}
function postGrid(list){return '<div class="tgg">'+list.map(function(v){return '<button type="button" class="sdp" data-id="'+v.id+'" aria-label="Open post by '+esc(v.user.handle)+'" style="background:'+(v.thumb?'url('+SD.abs(v.thumb)+') center/cover':G(hsh(v.id)%9))+'"></button>'}).join('')+'</div>'}
function bindGrid(list){shEl.querySelectorAll('.tgg [data-id]').forEach(function(b){b.onclick=function(){var v=list.filter(function(x){return x.id==b.dataset.id})[0];if(v)openPost(v)}})}
function tagSheet(t){t=String(t||'').replace(/^#/,'');openSh('<h3>#'+esc(t)+'</h3><p class="sdnote">Loading...</p>');
 SD.get('/api/feed?tag='+encodeURIComponent(t)).then(function(l){
  openSh('<h3>#'+esc(t)+'</h3><p class="sub2">'+l.length+' post'+(l.length==1?'':'s')+'</p>'+(l.length?postGrid(l):'<p class="sdnote">No posts with this tag yet. Add #'+esc(t)+' to your caption to start it.</p>'),function(){bindGrid(l)})}).catch(SD.fail)}
function browse(){var inp=$('v-home').querySelector('.sr input'),q=(inp.value||'').trim().replace(/^[#@]/,'');if(!q){inp.focus();toast('Type a creator or #tag');return}
 SD.get('/api/search?q='+encodeURIComponent(q)).then(function(r){var cs=r.creators||[],ts=r.tags||[];
  openSh('<h3>Results for "'+esc(q)+'"</h3>'+(cs.length||ts.length?'<div class="rsl">'+cs.map(function(u){return '<button type="button" data-c="'+esc(u.handle)+'">'+avc(u,'cav sm')+'<b>'+esc(u.name)+'</b><small>@'+esc(u.handle)+'</small></button>'}).join('')+ts.map(function(t){return '<button type="button" data-t="'+esc(t.tag)+'"><span class="cav sm tg">#</span><b>#'+esc(t.tag)+'</b><small>'+t.n+' post'+(t.n==1?'':'s')+'</small></button>'}).join('')+'</div>':'<p class="sub2">No matches. Try another name or tag.</p>'),function(){
   shEl.querySelectorAll('[data-c]').forEach(function(b){b.onclick=function(){creatorSheet(b.dataset.c)}});
   shEl.querySelectorAll('[data-t]').forEach(function(b){b.onclick=function(){tagSheet(b.dataset.t)}})})}).catch(SD.fail)}

/* ---------- home ---------- */
function ringsH(list,empty){if(!list.length)return '<div class="rings"><div class="sdhe">'+empty+'</div></div>';return '<div class="rings">'+list.map(function(u){return '<a class="rg" href="#"><i><b style="background:'+avb(u)+(u.avatar?' center/cover':'')+' !important;filter:none!important"></b></i><span>'+esc(u.handle)+'</span></a>'}).join('')+'</div>'}
function tilesH(list,empty){if(!list.length)return '<div class="hsx"><div class="sdhe">'+empty+'</div></div>';return '<div class="hsx">'+list.map(function(v){return '<div class="dt sdp'+(v.locked?' lk':'')+(v.kind=='photo'?' ph':'')+'" data-id="'+v.id+'" tabindex="0" role="button" aria-label="Post by '+esc(v.user.handle)+'" style="background:'+(v.thumb?'url('+SD.abs(v.thumb)+') center/cover no-repeat':G(hsh(v.id)%9))+' !important;filter:none!important"><em>@'+esc(v.user.handle)+'</em></div>'}).join('')+'</div>'}
function renderHome(d){var hm=$('v-home');if(!hm)return;SD.home=d;
 var h3=[].slice.call(hm.querySelectorAll(':scope > h3')),rg=[].slice.call(hm.querySelectorAll(':scope > .rings, :scope > .hsx'));
 function swap(el,html){var t=document.createElement('div');t.innerHTML=html;var n=t.firstChild;el.parentNode.replaceChild(n,el);return n}
 /* order: [popular rings, top rings, tags hsx, newest rings, row1, row2, row3] */
 if(rg.length<7)return;
 swap(rg[0],tilesH(d.popular,'No posts yet. Tap + to post the first video or photo.'));
 swap(rg[1],ringsH(d.top,'Creators with posts show up here.'));
 swap(rg[2],d.tags.length?'<div class="hsx">'+d.tags.map(function(t,i){var p=pal[(i+1)%pal.length];return '<a class="tg2" href="#" style="background:linear-gradient(160deg,'+p[0]+','+p[1]+')"><span>#'+esc(t.tag)+'</span></a>'}).join('')+'</div>':'<div class="hsx"><div class="sdhe">Add #hashtags to your captions and they show up here.</div></div>');
 swap(rg[3],ringsH(d.newest,'New creators show up here.'));
 for(var i=0;i<3;i++){var r=d.rows[i],hd=h3[h3.length-3+i];if(r){hd.hidden=false;hd.textContent='#'+r.tag;swap(rg[4+i],tilesH(r.posts,''))}else{hd.hidden=true;var e=swap(rg[4+i],'<div class="hsx"></div>');e.hidden=true}}
 hm.querySelectorAll('.dt,.rg,.tg2').forEach(function(x){x.style.cursor='pointer'})}
function loadHome(){SD.get('/api/home').then(renderHome).catch(function(){})}
(function(){var hm=$('v-home');if(!hm)return;
 hm.addEventListener('click',function(e){var a=e.target.closest('.dt[data-id]');if(a){e.preventDefault();e.stopPropagation();var id=a.dataset.id,all=[].concat(SD.home.popular,SD.home.rows.reduce(function(x,r){return x.concat(r.posts)},[])),v=all.filter(function(x){return x.id==id})[0];if(v)openPost(v)}},true);
 hm.addEventListener('keydown',function(e){var a=e.target.closest&&e.target.closest('.dt[data-id]');if(a&&(e.key=='Enter'||e.key==' ')){e.preventDefault();a.click()}});
 var nb=document.querySelector('.bn [data-v=home]');if(nb)nb.addEventListener('click',loadHome);
 loadHome()})();

/* ---------- inbox, chat, notifications ---------- */
function syncCV(){CV.length=0;((SD.ib&&SD.ib.convs)||[]).forEach(function(c){var r=[c.handle,(c.lastMine?'You: ':'')+c.last,ago(c.at),c.unread?1:0,c.folder,c.premium?1:0,c.active?1:0];r.u=c;CV.push(r)})}
function ibBadge(){var b=$('sdIB');if(!b){var nb=document.querySelector('.bn [data-v=inbox]');if(!nb)return;b=document.createElement('span');b.id='sdIB';b.className='sdib';nb.appendChild(b)}var n=(SD.ib&&SD.ib.unread)||0;b.textContent=n>9?'9+':n;b.classList.toggle('on',n>0)}
function loadInbox(){if(!SD.session)return Promise.resolve();return SD.get('/api/inbox').then(function(r){SD.ib=r;syncCV();ibBadge();var v=$('v-inbox');if(v&&!v.hidden&&!(shEl.classList.contains('on')&&$('cm')))renderInbox()}).catch(function(){})}
function ntTxt(n){var a=n.actor?'<b>'+esc(n.actor.handle)+'</b> ':'';return a+esc(n.text||'')}
function ibRows(){var rows='';
 var wl=S.tx[0],walletSub=wl&&wl.t=='in'?'+'+money(wl.a)+' from '+wl.n:'No new tips';
 if(ibF=='main')rows+='<button class="cvr" data-w="wallet"><span class="cav wl"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7.500A2.500 2.500 0 016.500 5H18v3"/><path d="M4 7.500V17a2 2 0 002 2h12.500a1.500 1.500 0 001.500-1.500v-8A1.500 1.500 0 0018.500 8H6.500A2.500 2.500 0 014 7.500z"/></svg></span><div class="cvt"><b>Spicy Wallet'+VER+'</b><small class="'+(S.unread?'bold':'')+'">'+(S.unread?S.unread+' new tip'+(S.unread>1?'s':'')+' · ':'')+esc(walletSub)+'</small></div>'+(S.unread?'<i class="ud"></i>':'')+'</button>';
 if(!SD.ib){if(SD.session&&!SD.ibBusy){SD.ibBusy=1;loadInbox().then(function(){SD.ibBusy=0})}return rows+'<p class="empty">Loading...</p>'}
 if(ibF=='gen'){var ns=SD.ib.notifs||[];if(ibQ=='unread')ns=ns.filter(function(n){return !n.read});
  if(SD.ib.notifs.some(function(n){return !n.read}))setTimeout(function(){SD.post('/api/notifs/read').then(function(){SD.ib.notifs.forEach(function(n){n.read=true});SD.ib.unread=(SD.ib.convs||[]).reduce(function(s,c){return s+c.unread},0);ibBadge()}).catch(function(){})},1500);
  ns.forEach(function(n){rows+='<button class="cvr" data-nt="'+n.id+'">'+avc(n.actor||{handle:'S'},'cav')+'<div class="cvt"><b>'+(n.actor?esc(n.actor.handle):'Spicy Dollz')+'</b><small class="'+(n.read?'':'bold')+'">'+esc(n.text||'')+' · '+ago(n.at)+'</small></div>'+(n.read?'':'<i class="ud"></i>')+'</button>'});
  return rows||'<p class="empty">No notifications yet. Likes, comments, follows and tips show up here.</p>'}
 CV.forEach(function(c,i){if(c[4]!=ibF)return;if(ibQ=='unread'&&!c[3])return;if(ibQ=='active'&&!c[6])return;var u=c.u||{handle:c[0]};
  rows+='<button class="cvr" data-c="'+i+'">'+avc(u,'cav').replace('</span>',(c[6]?'<em class="on"></em>':'')+'</span>')+'<div class="cvt"><b>'+esc(c[0])+(c[5]?VER:'')+'</b><small class="'+(c[3]?'bold':'')+'">'+esc(c[1])+(c[2]?' · '+c[2]:'')+'</small></div>'+(c[3]?'<i class="ud"></i>':'')+'</button>'});
 return rows||'<p class="empty">'+(ibF=='req'?'Message requests from people you don\'t follow show up here.':'No conversations yet. Tap + to message a creator.')+'</p>'}
$('v-inbox').addEventListener('click',function(e){var b=e.target.closest('[data-nt]');if(!b)return;e.stopPropagation();var n=(SD.ib.notifs||[]).filter(function(x){return x.id==b.dataset.nt})[0];if(!n)return;if(n.video)openPostId(n.video);else if(n.actor)creatorSheet(n.actor.handle)},true);
function openChat(i){var c=CV[i];if(c)openChatH(c[0])}
function chatWith(n){closeSh();ibF='main';document.querySelector('.bn [data-v=inbox]').click();renderInbox();setTimeout(function(){openChatH(n)},80)}
function msgH(m){return '<div class="m '+(m.mine?'me':'them')+'" data-mid="'+m.id+'">'+esc(m.text)+'<small>'+ago(m.at)+(m.mine&&m.read?' · Seen':'')+'</small></div>'}
function openChatH(h){if(!needIn())return;var last=0,timer=null;SD.chatH=h;
 openSh('<div class="cth" id="chW" style="cursor:pointer"><span class="cav" id="chA" style="background:'+G(hsh(h)%9)+'">'+esc(h[0].toUpperCase())+'</span><b>'+esc(h)+'</b></div><div class="cmsg" id="cm"><p class="sdnote">Loading...</p></div><form class="cin" id="cf"><input id="ci" maxlength="1000" placeholder="Message…" autocomplete="off" aria-label="Message"><button aria-label="Send">'+shI+'</button></form>',function(){
  var cm=$('cm');$('chW').onclick=function(){creatorSheet(h)};
  function pull(first){if(SD.chatH!=h||!$('cm'))return;SD.get('/api/inbox/'+encodeURIComponent(h)+'?after='+(first?0:last)).then(function(r){if(!$('cm'))return;
   if(first){var a=$('chA');if(a&&r.user.avatar){a.outerHTML=avc(r.user,'cav')}cm.innerHTML=r.messages.length?'':'<p class="sdnote" id="chE">Say hi to @'+esc(h)+'</p>';if(r.blocked){$('ci').disabled=true;$('ci').placeholder='You can\'t message this account'}}
   r.messages.forEach(function(m){if(cm.querySelector('[data-mid="'+m.id+'"]'))return;var e=$('chE');if(e)e.remove();cm.insertAdjacentHTML('beforeend',msgH(m));last=Math.max(last,m.id)});
   if(r.messages.length)cm.scrollTop=1e5;
   if(first)loadInbox()}).catch(function(e){if(first)cm.innerHTML='<p class="sdnote">'+esc(e.message)+'</p>'})}
  pull(true);clearInterval(SD.chT);SD.chT=setInterval(function(){if(!shEl.classList.contains('on')||!$('cm')||SD.chatH!=h){clearInterval(SD.chT);SD.chatH=null;loadInbox();return}if(!document.hidden)pull(false)},4000);
  $('cf').onsubmit=function(e){e.preventDefault();var inp=$('ci'),v=inp.value.trim();if(!v)return;inp.value='';
   SD.post('/api/inbox/'+encodeURIComponent(h),{text:v}).then(function(m){var ee=$('chE');if(ee)ee.remove();if(!cm.querySelector('[data-mid="'+m.id+'"]'))cm.insertAdjacentHTML('beforeend',msgH(m));last=Math.max(last,m.id);cm.scrollTop=1e5}).catch(function(x){inp.value=v;SD.fail(x)})}})}
function newMsg(){if(!needIn())return;var tmr=null;
 openSh('<h3>New message</h3><label class="fl3" for="nmT">To</label><input id="nmT" class="nmi" placeholder="Search a username" autocomplete="off" autocapitalize="none" maxlength="30"><div class="nmc" id="nmC"></div><label class="fl3" for="nmM">Message</label><textarea id="nmM" class="nmi" rows="3" maxlength="1000" placeholder="Write a message"></textarea><p class="err2" id="nmE" role="alert"></p><div class="cra"><button class="cb on" id="nmS" type="button">Send</button></div>',function(){
  var T=$('nmT'),C=$('nmC');
  function sug(list){C.innerHTML=list.filter(function(u){return !isMe(u.handle)}).slice(0,6).map(function(u){return '<button type="button" data-n="'+esc(u.handle)+'">'+esc(u.handle)+'</button>'}).join('');C.querySelectorAll('[data-n]').forEach(function(b){b.onclick=function(){T.value=b.dataset.n;$('nmM').focus()}})}
  sug(((SD.home&&SD.home.top)||[]).concat((SD.ib&&SD.ib.convs)||[]));
  T.oninput=function(){clearTimeout(tmr);var q=T.value.trim().replace(/^@/,'');if(q.length<1)return;tmr=setTimeout(function(){SD.get('/api/search?q='+encodeURIComponent(q)).then(function(r){sug(r.creators||[])}).catch(function(){})},250)};
  $('nmS').onclick=function(){var to=T.value.trim().replace(/^@/,''),m=$('nmM').value.trim(),er=$('nmE');if(!/^[A-Za-z0-9._]{2,30}$/.test(to)){er.textContent='Enter a username (letters, numbers, dot or underscore).';T.focus();return}if(!m){er.textContent='Write a message first.';$('nmM').focus();return}
   this.disabled=true;var bt=this;SD.post('/api/inbox/'+encodeURIComponent(to),{text:m}).then(function(){toast('Message sent to <b>'+esc(to)+'</b>');ibF='main';loadInbox();openChatH(to)}).catch(function(x){bt.disabled=false;er.textContent=x.message})}})}
(function(){var nb=document.querySelector('.bn [data-v=inbox]');if(nb)nb.addEventListener('click',function(){loadInbox()});
 $('v-me').addEventListener('click',function(e){var b=e.target.closest('button');if(b&&b.getAttribute('aria-label')=='Notifications'&&b.closest('.top')){ibF='gen'}},true);
 setInterval(function(){if(!document.hidden&&SD.session)loadInbox()},15000);
 if(SD.session)loadInbox()})();

/* ---------- stats ---------- */
function stTot(m){var t=SD.stats&&SD.stats.totals;return t?(t[m[0]]||0):0}
function stSer(mi,n){var k=SM[mi][0],tot=stTot(SM[mi]),d=(SD.stats&&SD.stats.daily[k])||[],a=[],run=tot;
 d=d.slice(-n);while(d.length<n)d.unshift(0);
 for(var i=n-1;i>=0;i--){a[i]=Math.max(0,run);run-=d[i]}return a}
(function(){var b=$('statBtn');if(!b)return;b.addEventListener('click',function(){SD.get('/api/stats?days=365').then(function(r){SD.stats=r;if(!$('v-stat').hidden){stIx=null;renderStats()}}).catch(SD.fail)})})();

/* ---------- settings ---------- */
SETF['Change Password']=function(){
 openSh('<h3>Change Password</h3><label class="fl3" for="cpO">Current password</label><input id="cpO" class="nmi" type="password" autocomplete="current-password"><label class="fl3" for="cpN">New password</label><input id="cpN" class="nmi" type="password" autocomplete="new-password" placeholder="At least 8 characters"><label class="fl3" for="cpC">Confirm new password</label><input id="cpC" class="nmi" type="password" autocomplete="new-password"><p class="sub2" id="cpE" style="color:#d6336c;min-height:18px;margin:8px 0 0"></p><button class="big" id="cpS">Update password</button>',function(m){
  var E=function(t){m.querySelector('#cpE').textContent=t},V=function(i){return m.querySelector('#'+i).value};
  m.querySelector('#cpS').onclick=function(){if(!V('cpO')){E('Enter your current password.');return}if(V('cpN').length<8){E('New password needs at least 8 characters.');return}if(V('cpN')!==V('cpC')){E('The two new passwords do not match.');return}if(V('cpN')===V('cpO')){E('Choose a password different from the current one.');return}
   var b=this;b.disabled=true;SD.post('/api/auth/password',{old:V('cpO'),new:V('cpN')}).then(function(){closeSh();toast('<b>Password</b> updated')}).catch(function(x){b.disabled=false;E(x.message)})}})};
SETF['Social Sign In']=function(){var on=SD.config&&SD.config.telegram,ln=!!SD.session.telegram;
 openSh('<h3>Social Sign In</h3><p class="sub2">'+(on?(ln?'Telegram is linked. You can sign in with Telegram from your account colour.':'Link Telegram so you can sign in with one tap.'):'Telegram sign in turns on once the platform owner adds a Telegram bot to the server.')+' X and Instagram sign in are not available yet.</p>'+(on?'<button type="button" class="big" id="tgL">'+(ln?'Unlink Telegram':'Link Telegram')+'</button>':''),function(){var b=$('tgL');if(!b)return;
  b.onclick=function(){if(ln){SD.del('/api/auth/telegram/link').then(function(){SD.session.telegram=false;closeSh();toast('Telegram unlinked')}).catch(SD.fail);return}
   SD.telegram({link:true},function(){SD.session.telegram=true;closeSh();toast('<b>Telegram</b> linked')},function(m){toast(m)})}})};
SETF['Blocked Users']=function(){
 function draw(list,msg){openSh('<h3>Blocked Users</h3><p class="sub2">Blocked accounts cannot message you, comment on your posts or follow you, and you won\'t see their posts.</p><div class="phl"><input id="bkI" class="nmi" maxlength="30" placeholder="@username" autocapitalize="none" autocomplete="off"><button type="button" class="fpl" id="bkA">Block</button></div><p class="sub2" id="bkE" style="color:#d6336c;min-height:18px;margin:8px 0">'+(msg||'')+'</p>'+(list.length?list.map(function(u){return '<div class="srow2"><b>@'+esc(u.handle)+'</b><button type="button" class="fpl" data-u="'+esc(u.handle)+'">Unblock</button></div>'}).join(''):'<p class="sub2">You have not blocked anyone.</p>'),function(m){
  function add(){var v=m.querySelector('#bkI').value.replace(/^@/,'').trim();if(v.length<2){draw(list,'Enter a username.');return}if(isMe(v)){draw(list,'You cannot block yourself.');return}
   SD.post('/api/blocks',{handle:v}).then(function(){toast('<b>@'+esc(v)+'</b> blocked');SD.reels=null;SD.rlAt=0;load()}).catch(function(x){draw(list,esc(x.message))})}
  m.querySelector('#bkA').onclick=add;m.querySelector('#bkI').onkeydown=function(e){if(e.key=='Enter')add()};
  m.querySelectorAll('[data-u]').forEach(function(b){b.onclick=function(){var u=b.dataset.u;SD.del('/api/blocks/'+encodeURIComponent(u)).then(function(){toast('<b>@'+esc(u)+'</b> unblocked');load()}).catch(SD.fail)}})})}
 function load(){SD.get('/api/blocks').then(function(l){draw(l)}).catch(SD.fail)}load()};
if(SD.session&&SD.session.user.role=='admin'){var lo=-1;SROWS.forEach(function(r,i){if(r[0]=='Log out')lo=i});SROWS.splice(lo<0?SROWS.length:lo,0,['Moderation','<path fill="currentColor" d="M12 2.500l8 2.800v6.200c0 4.800-3.400 8.700-8 10-4.600-1.300-8-5.200-8-10V5.300z"/>']);
 SETF['Moderation']=function(){
  function load(){SD.get('/api/admin/reports').then(function(l){
   openSh('<h3>Moderation</h3><p class="sub2">'+(l.length?l.length+' open report'+(l.length==1?'':'s'):'No open reports. Reported posts, comments and accounts show up here.')+'</p><div class="sdrl">'+l.map(function(r){return '<div class="srow2" data-r="'+r.id+'"><div><b>'+esc(r.reason)+'</b><small>'+(r.user?'@'+esc(r.user.handle)+(r.user.banned?' (suspended)':''):'')+(r.video?' &middot; '+(r.video.kind=='photo'?'photo':'video')+(r.video.caption?': '+esc(r.video.caption.slice(0,60)):'')+(r.video.removed?' (removed)':''):'')+' &middot; by @'+esc(r.reporter||'?')+' &middot; '+ago(r.at)+'</small></div>'+
    (r.video?'<button type="button" class="fpl" data-k="view">View</button>':'')+(r.video&&!r.video.removed?'<button type="button" class="fpl" data-k="rm">Remove</button>':'')+(r.user&&!r.user.banned?'<button type="button" class="fpl" data-k="ban">Suspend</button>':'')+'<button type="button" class="fpl" data-k="ok">Dismiss</button></div>'}).join('')+'</div>',function(m){
    m.querySelectorAll('[data-r]').forEach(function(row){var r=l.filter(function(x){return x.id==row.dataset.r})[0];row.querySelectorAll('[data-k]').forEach(function(b){b.onclick=function(){var k=b.dataset.k;
     if(k=='view'){var isP=r.video.kind=='photo';openSh('<h3>Reported '+(isP?'photo':'video')+'</h3>'+(isP?'<img class="pmed" alt="" src="'+SD.abs(r.video.url)+'">':'<video class="pmed" controls playsinline src="'+SD.abs(r.video.url)+'"></video>')+'<div class="cra"><button class="cb" id="mdB" type="button">Back to reports</button></div>',function(){$('mdB').onclick=load});return}
     if(k!='ok'&&b.dataset.c!='1'){b.dataset.c='1';b.textContent='Confirm';return}
     var p=k=='rm'?SD.post('/api/admin/posts/'+r.video.id+'/remove'):k=='ban'?SD.post('/api/admin/users/'+encodeURIComponent(r.user.handle)+'/ban',{on:true}):SD.post('/api/admin/reports/'+r.id+'/close');
     p.then(function(){if(k!='ok')SD.post('/api/admin/reports/'+r.id+'/close').catch(function(){});toast(k=='rm'?'Post removed':k=='ban'?'Account suspended':'Report dismissed');load()}).catch(SD.fail)}})})})}).catch(SD.fail)}
  load()}}

/* ---------- profile: real counts, follow, liked, featured ---------- */
if(SD.session){(function(){var V=SD.view,k=(V?V.counts:SD.session.counts)||{},q=function(s){return document.querySelector(s)};
 function counts(k){var st=document.querySelectorAll('#v-me .st2 b');if(st[0])st[0].textContent=vfmt(k.views);if(st[1])st[1].textContent=vfmt(k.followers);if(st[2])st[2].textContent=vfmt(k.likes)}
 counts(k);
 var stw=q('#v-me .st2');if(stw){var dv=stw.querySelectorAll(':scope > div');if(dv[1]){dv[1].style.cursor='pointer';dv[1].onclick=function(){var h=V?V.handle:meH();SD.get('/api/users/'+encodeURIComponent(h)+'/list/followers').then(function(l){openSh('<h3>Followers</h3>'+(l.length?'<div class="rsl">'+l.map(function(u){return '<button type="button" data-c="'+esc(u.handle)+'">'+avc(u,'cav sm')+'<b>'+esc(u.name)+'</b><small>@'+esc(u.handle)+'</small></button>'}).join('')+'</div>':'<p class="sub2">No followers yet.</p>'),function(){shEl.querySelectorAll('[data-c]').forEach(function(b){b.onclick=function(){creatorSheet(b.dataset.c)}})})}).catch(SD.fail)}}}
 var fb=$('fol');if(fb){var on=!!(V&&V.following);var setF=function(o){on=o;fb.classList.toggle('on',o);var p=$('fp'),t=$('ft');if(p)p.textContent=o?'\u2713':'+';if(t)t.textContent=o?'Following':'Follow'};setF(on);
  fb.onclick=function(){if(!V){toast('This is your profile. Fans follow you from your shared link.');return}SD.post('/api/follow/'+encodeURIComponent(V.handle),{on:!on}).then(function(r){setF(r.following);V.counts.followers=r.followers;counts(V.counts)}).catch(SD.fail)}}
 var tip=q('.acts2 .rb');if(tip)tip.addEventListener('click',function(){SD.tipTo=null},true);
 $('v-me').addEventListener('click',function(e){if(e.target.closest('.acts2'))SD.tipTo=null},true);
 var p3=q('.tb[data-p=p3]');if(p3)p3.style.display='none';
 /* liked tab */
 var g4=$('g4');if(g4){g4.innerHTML='';var lt=q('.tb[data-p=p4]');
  var liked=function(){SD.get('/api/me/liked').then(function(l){g4.innerHTML='';l.forEach(function(v){g4.appendChild(vTile(v,v.mine))});var sm=lt&&lt.querySelector('small');if(sm)sm.textContent=l.length;if(!l.length)g4.innerHTML='<p class="sdemp" style="grid-column:1/-1;margin:28px 8px;text-align:center;opacity:.6;font-size:14px">Posts you like show up here.</p>'}).catch(function(){})};
  if(!V){liked();if(lt)lt.addEventListener('click',liked)}}
 /* featured: pinned posts (videos/photos) or uploaded photos */
 var ft=$('ft3');if(ft){var FX=((V?V.featx:SD.session.featx)||[]).concat([null,null,null,null,null,null]).slice(0,6);
  var rawF=function(){var f=SD.session.kv&&SD.session.kv.sd_feat,a=[];try{a=typeof f=='string'?JSON.parse(f):(f||[])}catch(e){}return a.concat([null,null,null,null,null,null]).slice(0,6)};
  var bg=function(it){if(it.img)return 'url('+SD.abs(it.img)+') center/cover';var p=it.post;return p.thumb?'url('+SD.abs(p.thumb)+') center/cover':VGR};
  var tile=function(b,it,i){var lk=it&&it.post&&it.post.locked;b.className=it?'sdfx'+(lk?' fxl':''):'sdfe';
   b.innerHTML=it?'<div class="a" style="background:'+bg(it)+'!important"></div>'+(it.post?(lk?'<em>Locked</em>':it.post.kind=='photo'?'<em>Photo</em>':'<span class="fxp"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/></svg></span><em>'+fmt(it.post.dur)+'</em>'):'')
     :'<div class="a"></div><span class="fxp add">+</span><em>Pin a video</em>';
   b.setAttribute('aria-label',it?(it.post?(it.post.kind=='photo'?'Pinned photo ':'Pinned video ')+(i+1):'Featured photo '+(i+1)):'Empty featured slot '+(i+1)+', tap to pin a video')};
  var view=function(it){if(it.img){openSh('<img class="pmed" alt="Featured photo" src="'+SD.abs(it.img)+'">');return}
   SD.get('/api/videos/'+it.post.id).then(function(p){if(p.locked){toast('Subscribe to unlock this post');return}openPost(p)}).catch(SD.fail)};
  var refresh=function(){return SD.get('/api/session').then(function(r){if(r.user){SD.session.featx=r.featx;SD.session.kv.sd_feat=r.kv.sd_feat;SD.session.videos=r.videos;FX=(r.featx||[]).concat([null,null,null,null,null,null]).slice(0,6);draw()}return r})};
  var save=function(arr,msg){SD.put('/api/kv/sd_feat',{v:arr}).then(refresh).then(function(){closeSh();toast(msg)}).catch(SD.fail)};
  var slot=function(i){SD.get('/api/session').then(function(r){var vids=(r.videos||[]),it=FX[i];
    openSh('<h3>Featured slot '+(i+1)+'</h3><p class="sub2">Pin one of your posts so fans see it first, or upload a photo.</p>'+
     (vids.length?'<div class="fxg">'+vids.map(function(v){return '<button type="button" data-pv="'+v.id+'" aria-label="Pin this post"><div class="a" style="background:'+(v.thumb?'url('+SD.abs(v.thumb)+') center/cover':VGR)+'"></div><em>'+(v.kind=='photo'?'Photo':fmt(v.dur))+'</em></button>'}).join('')+'</div>':'<p class="sub2">You have no posts yet. Tap + in the bottom bar to post a video first.</p>')+
     '<div class="fxa"><button type="button" class="big" data-k="fup">Upload a photo</button>'+(it?'<button type="button" class="lnk" data-k="fview">View</button><button type="button" class="lnk" data-k="frm">Remove from this slot</button>':'')+'</div>',function(){
     shEl.querySelectorAll('[data-pv]').forEach(function(b){b.onclick=function(){var a=rawF();a[i]='v:'+b.dataset.pv;save(a,'<b>Pinned</b> to your featured row')}});
     var up=shEl.querySelector('[data-k=fup]');up.onclick=function(){var inp=document.createElement('input');inp.type='file';inp.accept='image/*';inp.onchange=function(){var f=inp.files&&inp.files[0];if(!f)return;var fd=new FormData();fd.append('file',f);toast('Uploading featured photo...');
       SD.upload('/api/upload/feat?slot='+i,fd).then(refresh).then(function(){closeSh();toast('<b>Featured photo</b> saved')}).catch(SD.fail)};inp.click()};
     var vw=shEl.querySelector('[data-k=fview]');if(vw)vw.onclick=function(){closeSh();view(it)};
     var rm=shEl.querySelector('[data-k=frm]');if(rm)rm.onclick=function(){var a=rawF();a[i]=null;save(a,'Slot cleared')}})}).catch(SD.fail)};
  var draw=function(){ft.innerHTML='';ft.style.display='';
   if(V){var has=FX.filter(Boolean);if(!has.length){ft.style.display='none';var ht=$('hth');if(ht&&ht.parentNode)ht.parentNode.style.display='none';return}
    has.forEach(function(it,i){var b=document.createElement('button');b.type='button';tile(b,it,i);b.onclick=function(){view(it)};ft.appendChild(b)});return}
   FX.forEach(function(it,i){var b=document.createElement('button');b.type='button';tile(b,it,i);b.onclick=function(){slot(i)};ft.appendChild(b)})};
  draw()}
})()}

/* profile photo fallback: send the original file (HEIC or anything the browser can't decode) to the server */
window.sdRawAvatar=function(f){var fd=new FormData();fd.append('file',f);toast('Uploading photo...');
 SD.upload('/api/upload/avatar',fd).then(function(r){var u=SD.abs(r.url),de=document.documentElement;de.style.setProperty('--avu','url("'+u+'")');de.classList.add('hasav');if(SD.session)SD.session.kv.sd_avatar=r.url;try{SDS.setItem('sd_avatar_srv',u)}catch(e){}closeSh();toast('<b>Profile photo</b> updated')}).catch(SD.fail)};
/* in-app browsers (Android WebView inside other apps) often can't open the file picker: detect and explain */
(function(){var WV=/; wv\)|\bAsk\/\d|FBAN|FBAV|Instagram|Line\//.test(navigator.userAgent||'');if(!WV)return;
 var APP='https://www.perplexity.ai/computer/a/spicy-dollz-w_3jVlhhQ7mYvHPH7.DpZw';
 function link(){var h=location.hostname;return (h!='sites.pplx.app'&&/\.pplx\.app$/.test(h))?location.href.split('#')[0]:APP}
 var picked=false;document.addEventListener('change',function(e){if(e.target&&e.target.type=='file')picked=true},true);
 function noPicker(){SD.log('nopicker',navigator.userAgent);var u=link();
  openSh('<h3>Open in Chrome to upload</h3><p class="sub2">Spicy Dollz is open inside another app\'s built-in browser, and that browser can\'t open your photos and videos. Copy the link, open it in Chrome, and sign in with your email and password. Uploading works there.</p><div class="shl"><input id="wvU" readonly value="'+esc(u)+'" aria-label="Link"><button id="wvC" type="button">Copy</button></div>',function(){
   $('wvC').onclick=function(){copyTxt(u,function(ok){$('wvC').textContent=ok?'Copied':'Copy';if(!ok)$('wvU').select()})};$('wvU').onfocus=function(){this.select()}})}
 function watch(){picked=false;var away=false;function h(){if(document.hidden)away=true}document.addEventListener('visibilitychange',h);
  setTimeout(function(){document.removeEventListener('visibilitychange',h);if(!away&&!picked)noPicker()},2000)}
 document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('#upDrop,.phU,[data-k=fup],#upl,#upChg,label[for=avF]');if(t&&!SD.view)watch()},true);
 window.sdWatchPicker=watch})();

(function(){var st=document.createElement('style');st.textContent=
 '.t.sdv .a,:root[data-p] .t.sdv .a{filter:none!important}.t.sdv.lk .a,:root[data-p] .t.sdv.lk .a{filter:blur(14px)!important}'+
 '.ft .sdfx .a,.ft .sdfe .a{filter:none!important}.ft .sdfx .a{position:absolute!important;inset:0!important;width:auto!important;height:auto!important}.ft .sdfx.fxl .a{filter:blur(10px)!important;transform:scale(1.3)}.ft button{position:relative;overflow:hidden}.ft .sdfe .a{background:transparent!important}'+
 '.fxp{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:40px;height:40px;border-radius:50%;background:#0007;color:#fff;display:grid;place-items:center;font:700 22px/1 inherit}.fxp svg{width:20px;height:20px;margin-left:2px}.fxp.add{background:#ffffff8c;color:var(--cy,#ff4696)}'+
 '.fxg{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;max-height:46vh;overflow:auto;margin:12px 0}.fxg button{position:relative;aspect-ratio:3/4;border:0;border-radius:14px;overflow:hidden;padding:0;cursor:pointer;background:#0001}.fxg .a{position:absolute;inset:0}.fxg em{position:absolute;left:6px;bottom:6px;font-style:normal;font-size:11px;font-weight:700;color:#fff;background:#000a;padding:2px 7px;border-radius:99px}'+
 '.fxa{display:grid;gap:8px;margin-top:8px}.sdbal{margin-top:-4px}'+
 '#v-me .tabs{grid-template-columns:none!important;grid-auto-flow:column;grid-auto-columns:1fr}'+
 '.tipb small{display:block;font-size:11px;font-weight:800;margin-top:2px;color:#fff;text-shadow:0 1px 3px #0008}';
 document.head.appendChild(st)})();

/* verified + premium badge: one clean, consistent component */
var VCK='<svg class="sdck" viewBox="0 0 24 24" aria-hidden="true"><path fill="var(--pink,#ff4696)" d="M12 2.2l2.4 1.9 3-.4 1.1 2.8 2.8 1.1-.4 3 1.9 2.4-1.9 2.4.4 3-2.8 1.1-1.1 2.8-3-.4L12 21.8l-2.4-1.9-3 .4-1.1-2.8-2.8-1.1.4-3L2.2 12l1.9-2.4-.4-3 2.8-1.1 1.1-2.8 3 .4z"/><path d="M8.2 12.2l2.6 2.6 5-5.2" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
VER='<span class="sdvb" role="img" aria-label="Verified Spicy Premium creator">'+VCK+'<span class="sdpb"><i></i></span></span>';
(function(){var st=document.createElement('style');st.textContent=
 '.sdvb{display:inline-flex;align-items:center;gap:4px;margin-left:6px;vertical-align:middle;line-height:0;flex:none;position:relative;top:-1px}'+
 '.sdck{width:16px;height:16px;display:block;flex:none}'+
 '.sdpb{display:inline-flex;align-items:center;justify-content:center;height:16px;padding:0 6px;border-radius:999px;background:var(--pink,#ff4696);box-shadow:0 1px 3px #0003}'+
 '.sdpb i{display:block;height:9px;aspect-ratio:420/299;background:#fff;-webkit-mask:var(--wm) center/contain no-repeat;mask:var(--wm) center/contain no-repeat}'+
 '.crh b .sdvb{margin-left:7px}.crh b .sdck{width:18px;height:18px}.crh b .sdpb{height:18px;padding:0 7px}.crh b .sdpb i{height:10px}'+
 '.rwho .sdvb{margin-left:5px;top:0}.rwho .sdck{filter:drop-shadow(0 1px 2px #0006)}'+
 '.crh .cav.big.im{cursor:zoom-in}'+
 '.nmr .vf{width:22px!important;height:22px!important;filter:none!important}';
 document.head.appendChild(st);
 var vf=document.querySelector('.nmr .vf');if(vf)vf.innerHTML=VCK.replace(/^<svg[^>]*>|<\/svg>$/g,'');})();
/* tap a creator's avatar in their panel to see the full photo */
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('.crh .cav.big.im');if(!a)return;var m=/url\(['"]?([^'")]+)/.exec(a.getAttribute('style')||'');if(!m)return;
 var u=decodeURIComponent(m[1]);openSh('<img class="pmed" alt="Profile photo" src="'+esc(u)+'">')});
/* very large balances: shrink the wallet amount to fit its card */
(function(){function fit(){var e=$('wAmt');if(!e)return;e.style.fontSize='';e.style.whiteSpace='nowrap';var fs=parseFloat(getComputedStyle(e).fontSize)||34,n=0;while(e.scrollWidth>e.clientWidth+1&&fs>14&&n<30){fs-=1;e.style.fontSize=fs+'px';n++}}
 var e=$('wAmt');if(e&&window.MutationObserver)new MutationObserver(function(){requestAnimationFrame(fit)}).observe(e,{childList:true,characterData:true,subtree:true});
 window.addEventListener('resize',fit);document.addEventListener('click',function(ev){if(ev.target.closest&&ev.target.closest('.bn [data-v=wallet]'))setTimeout(fit,60)});setTimeout(fit,300)})();
/* avatar frames: true colours, calm motion, sized for phone and desktop */
(function(){var st=document.createElement('style');st.textContent=
 ':root{--avs:96px}@media (min-width:900px){:root{--avs:128px}}'+
 '#avw.av{width:var(--avs)!important;height:var(--avs)!important;flex:none}'+
 '#avw.av.hf{margin:calc(var(--avs)*.04) calc(var(--avs)*.30) calc(var(--avs)*.26) calc(var(--avs)*.16)!important}'+
 '.afr{filter:none!important;mix-blend-mode:normal!important;animation:sdfra 4.5s ease-in-out infinite!important;will-change:transform}'+
 '@keyframes sdfra{0%,100%{transform:scale(1)}50%{transform:scale(1.025)}}'+
 '@media (prefers-reduced-motion:reduce){.afr{animation:none!important}}'+
 '#avw.hf .avc{right:-8%;bottom:-8%}'+
 '#ft3>button{flex:0 0 clamp(104px,30vw,168px)!important;width:clamp(104px,30vw,168px)!important;max-width:168px}'+
 /* one verified check everywhere, always Spicy pink */
 'svg.vk[data-sdck]{width:16px!important;height:16px!important;vertical-align:-3px;flex:none;filter:none!important}svg.vf[data-sdck]{filter:none!important}'+
 '.sdvb .sdpb{background:#ff4696!important}'+'svg[data-sdck] path:first-child,svg.sdck path:first-child{fill:#ff4696!important;stroke:none!important}svg[data-sdck] path+path,svg.sdck path+path{fill:none!important;stroke:#fff!important}svg[data-sdck],svg.sdck{color:#ff4696!important;background:none!important}';
 document.head.appendChild(st)})();
var CKP='<path fill="#ff4696" d="M12 2.2l2.4 1.9 3-.4 1.1 2.8 2.8 1.1-.4 3 1.9 2.4-1.9 2.4.4 3-2.8 1.1-1.1 2.8-3-.4L12 21.8l-2.4-1.9-3 .4-1.1-2.8-2.8-1.1.4-3L2.2 12l1.9-2.4-.4-3 2.8-1.1 1.1-2.8 3 .4z"/><path d="M8.2 12.2l2.6 2.6 5-5.2" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>';
VCK='<svg class="sdck" viewBox="0 0 24 24" aria-hidden="true">'+CKP+'</svg>';
VER='<span class="sdvb" role="img" aria-label="Verified Spicy Premium creator">'+VCK+'<span class="sdpb"><i></i></span></span>';
(function(){function fix(){document.querySelectorAll('svg.vk:not([data-sdck]),svg.vf:not([data-sdck])').forEach(function(s){s.setAttribute('viewBox','0 0 24 24');s.innerHTML=CKP;s.setAttribute('data-sdck','1')})}
 var q=0;fix();if(window.MutationObserver)new MutationObserver(function(){if(q)return;q=requestAnimationFrame(function(){q=0;fix()})}).observe(document.body,{childList:true,subtree:true})})();

/* reels sound: speaker button, remembered choice, sound on whenever the browser allows it */
function sndIc(m){return m?SNDOFF():SNDON()}
function SNDON(){return '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="#fff"/><path d="M15.5 9a4 4 0 010 6M18 6.5a7.5 7.5 0 010 11"/></svg>'}
function SNDOFF(){return '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="#fff"/><path d="M16 9.5l5 5M21 9.5l-5 5"/></svg>'}
function sndUI(a,muted){var b=a&&a.querySelector('[data-a=snd]');if(b)b.innerHTML=sndIc(muted)+'<small>'+(muted?'Muted':'Sound')+'</small>'}
function setSnd(on,a){SD.rlMuted=!on;document.querySelectorAll('#v-disc .rv').forEach(function(r){var v=r.querySelector('video');if(v)v.muted=!on;sndUI(r,!on)});
 var v=a&&a.querySelector('video');if(v&&on&&v.paused){var p=v.play();if(p&&p.catch)p.catch(function(){})}
 var m=a&&a.querySelector('.sdmute');if(m){m.textContent=on?'Sound on':'Muted';m.classList.add('on');setTimeout(function(){m.classList.remove('on')},900)}}
(function(){var st=document.createElement('style');st.textContent='.ract .sdsb svg{width:28px;height:28px;filter:drop-shadow(0 1px 3px #0008)}.ract .sdsb small{display:block;font-size:11px;font-weight:800;color:#fff;margin-top:2px;text-shadow:0 1px 3px #0008}';document.head.appendChild(st)})();
/* upload: dedicated tag field with removable chips */
SD.upTags=SD.upTags||[];
function wireTags(){var box=$('upTags'),inp=$('upTagI');if(!box||!inp||inp.dataset.w)return;inp.dataset.w=1;
 function draw(){box.querySelectorAll('.sdchip').forEach(function(c){c.remove()});SD.upTags.forEach(function(t,i){var c=document.createElement('span');c.className='sdchip';c.innerHTML='#'+esc(t)+'<button type="button" aria-label="Remove tag '+esc(t)+'">&times;</button>';c.querySelector('button').onclick=function(){SD.upTags.splice(i,1);draw()};box.insertBefore(c,inp)});
  inp.placeholder=SD.upTags.length>=10?'10 tags max':(SD.upTags.length?'Add another tag':'Add a tag, then press Enter');inp.disabled=SD.upTags.length>=10}
 function add(raw){var bad=false;String(raw||'').split(/[\s,]+/).forEach(function(t){t=t.replace(/^#+/,'').toLowerCase();if(!t)return;if(!/^[a-z0-9_]{2,30}$/.test(t)){bad=true;return}if(SD.upTags.indexOf(t)<0&&SD.upTags.length<10)SD.upTags.push(t)});inp.value='';draw();if(bad)toast('Tags use 2 to 30 letters, numbers or _')}
 inp.addEventListener('keydown',function(e){if(e.key=='Enter'||e.key==','||e.key==' '){e.preventDefault();add(inp.value)}else if(e.key=='Backspace'&&!inp.value&&SD.upTags.length){SD.upTags.pop();draw()}});
 inp.addEventListener('input',function(){if(/[\s,]/.test(inp.value))add(inp.value)});
 inp.addEventListener('blur',function(){if(inp.value.trim())add(inp.value)});
 $('upTagA').onclick=function(){add(inp.value);inp.focus()};
 box.onclick=function(e){if(e.target===box)inp.focus()};draw()}
(function(){var _ru=renderUpload;renderUpload=function(){_ru.apply(this,arguments);wireTags()};wireTags();
 var st=document.createElement('style');st.textContent='.sdtags{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px;border-radius:16px;background:var(--cfield,#ffffffb8);border:1.5px solid #fff;min-height:48px;cursor:text}'+
 '.sdtags input{flex:1 1 120px;min-width:100px;border:0!important;background:transparent!important;outline:0;font:inherit;font-size:15px;padding:6px 4px;box-shadow:none!important}'+
 '.sdtags #upTagA{border:0;border-radius:999px;padding:7px 14px;font:inherit;font-weight:700;font-size:13px;background:var(--ink,#1e1033);color:#fff;cursor:pointer}'+
 '.sdchip{display:inline-flex;align-items:center;gap:4px;padding:5px 6px 5px 11px;border-radius:999px;background:#ff4696;color:#fff;font-size:13px;font-weight:700}'+
 '.sdchip button{border:0;background:#ffffff40;color:#fff;width:20px;height:20px;border-radius:50%;font-size:14px;line-height:1;cursor:pointer;display:grid;place-items:center;padding:0}'+
 '.sdth{margin:6px 4px 0;font-size:12.5px;opacity:.65}';document.head.appendChild(st)})();
/* admin: download a full backup (database + all uploads) */
if(SD.session&&SD.session.user.role=='admin'){(function(){var lo=-1;SROWS.forEach(function(r,i){if(r[0]=='Log out')lo=i});
 SROWS.splice(lo<0?SROWS.length:lo,0,['Backup','<path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M12 4v11m0 0l-4.5-4.5M12 15l4.5-4.5M5 19.5h14"/>']);
 SETF['Backup']=function(){openSh('<h3>Backup</h3><p class="sub2">Downloads one file with the whole database (accounts, coins, wallets, comments, messages) and every uploaded photo and video. Keep it somewhere safe, and make a new one regularly.</p><button type="button" class="big" id="bkGo">Download backup</button>',function(){
  $('bkGo').onclick=function(){var b=$('bkGo');b.disabled=true;b.textContent='Preparing...';SD.post('/api/admin/backup').then(function(r){var u=SD.abs(r.url),w=null;try{w=window.open(u,'_blank')}catch(e){}
   b.disabled=false;b.textContent='Download backup';if(!w)openSh('<h3>Backup ready</h3><p class="sub2">Open this link within 10 minutes to download.</p><p><a href="'+esc(u)+'" target="_blank" rel="noopener" style="word-break:break-all">'+esc(u)+'</a></p>');else toast('Backup download started in a new tab')}).catch(function(e){b.disabled=false;b.textContent='Download backup';SD.fail(e)})}})};
 try{if(typeof renderSettings=='function')renderSettings()}catch(e){}})()}
