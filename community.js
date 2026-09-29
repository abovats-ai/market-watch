import {initializeApp} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {getAuth,signInAnonymously,signInWithEmailAndPassword,onAuthStateChanged,signOut} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import {getFirestore,doc,getDoc,setDoc,updateDoc,deleteDoc,onSnapshot,collection,query,orderBy,limit,addDoc,serverTimestamp} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import {CFG,JOIN_CODE,OWNER_EMAIL} from "./config.js";
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const st=document.createElement('style');st.textContent=`
#gate{position:fixed;inset:0;background:var(--bg);z-index:99;display:flex;align-items:center;justify-content:center;padding:16px}
.box{background:var(--c);border:1px solid var(--b);border-radius:14px;padding:22px;width:100%;max-width:340px;display:grid;gap:10px}
.box input{margin:0}.pb{padding:10px;border:0;border-radius:8px;background:var(--a);color:#fff;font-weight:600;cursor:pointer}.err{color:var(--r);font-size:12px}
#fab{position:fixed;right:16px;bottom:16px;z-index:50;width:52px;height:52px;border-radius:50%;border:0;background:var(--a);color:#fff;font-size:22px;cursor:pointer;display:none}
#cp{position:fixed;right:12px;bottom:76px;width:min(360px,calc(100% - 24px));height:60vh;background:var(--c);border:1px solid var(--b);border-radius:14px;z-index:50;display:none;flex-direction:column;overflow:hidden}
#cp .h{display:flex;gap:6px;padding:8px;border-bottom:1px solid var(--b)}#ms,#ml{flex:1;overflow:auto;padding:8px;font-size:13px}
.msg{margin-bottom:8px}.msg .m{margin-left:6px}.x{cursor:pointer;color:var(--r);margin-left:6px}
#cf{display:flex;gap:6px;padding:8px;border-top:1px solid var(--b)}#cf input{margin:0}`;document.head.append(st);
document.body.insertAdjacentHTML('beforeend',`<div id="gate"><div class="box"><h2 style="margin:0">Join Market Watch</h2>
<input id="gn" placeholder="Your name" maxlength="24"><input id="gc" placeholder="Join code" inputmode="numeric">
<input id="go" type="password" placeholder="Owner password" style="display:none"><div class="err" id="ge"></div>
<button class="pb" id="gj">Join</button><a href="#" id="gt" style="text-align:center">Owner login</a></div></div>
<button id="fab">💬</button><div id="cp"><div class="h"><button class="ch on" id="t1">Chat</button><button class="ch" id="t2" style="display:none">Members</button><span style="flex:1"></span><button class="ch" id="lo">Leave</button></div>
<div id="ms"></div><div id="ml" style="display:none"></div><div id="cf"><input id="ci" placeholder="Message…" maxlength="300"><button class="pb" id="cs">Send</button></div></div>`);
const app=initializeApp(CFG),au=getAuth(app),db=getFirestore(app);let isOwner=false,unsub=[];
let ownerMode=false;
$('#gt').onclick=e=>{e.preventDefault();ownerMode=!ownerMode;$('#gn').style.display=$('#gc').style.display=ownerMode?'none':'';$('#go').style.display=ownerMode?'':'none';$('#gj').textContent=ownerMode?'Owner login':'Join'};
$('#gj').onclick=async()=>{$('#ge').textContent='';try{
 if(ownerMode){await signInWithEmailAndPassword(au,OWNER_EMAIL,$('#go').value);return}
 const n=$('#gn').value.trim();if(!n)return $('#ge').textContent='Enter your name';
 if($('#gc').value.trim()!==JOIN_CODE)return $('#ge').textContent='Wrong code';
 const u=(au.currentUser||(await signInAnonymously(au)).user);
 await setDoc(doc(db,'members',u.uid),{name:n,joinedAt:serverTimestamp(),banned:false});
}catch(e){$('#ge').textContent=e.code=='permission-denied'?'You have been removed.':'Could not join: '+(e.code||e.message)}};
onAuthStateChanged(au,async u=>{unsub.forEach(f=>f());unsub=[];$('#fab').style.display='none';$('#cp').style.display='none';
 if(!u){$('#gate').style.display='flex';return}
 isOwner=u.email===OWNER_EMAIL;
 if(!isOwner){const s=await getDoc(doc(db,'members',u.uid));if(!s.exists()){$('#gate').style.display='flex';return}
  unsub.push(onSnapshot(doc(db,'members',u.uid),d=>{if(d.exists()&&d.data().banned){kick()}}))}
 $('#gate').style.display='none';$('#fab').style.display='block';$('#t2').style.display=isOwner?'':'none';chat(u)});
function kick(){unsub.forEach(f=>f());$('#fab').style.display=$('#cp').style.display='none';$('#gate').style.display='flex';$('.box').innerHTML='<h2>Removed</h2><p>The owner has removed you from this site.</p>'}
function chat(u){
 unsub.push(onSnapshot(query(collection(db,'messages'),orderBy('at','desc'),limit(100)),s=>{const a=[];s.forEach(d=>a.unshift([d.id,d.data()]));
  $('#ms').innerHTML=a.map(([id,m])=>`<div class="msg"><b>${esc(m.name)}</b>${m.owner?' <span class="tag">Owner</span>':''}<span class="m e">${m.at?new Date(m.at.toMillis()).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}):''}</span>${isOwner?`<span class="x" data-d="${id}">✕</span>`:''}<div>${esc(m.text)}</div></div>`).join('');$('#ms').scrollTop=1e9},()=>{}));
 if(isOwner)unsub.push(onSnapshot(collection(db,'members'),s=>{$('#ml').innerHTML=`<div class="m">${s.size} member(s)</div>`+s.docs.map(d=>{const m=d.data();return `<div class="row msg"><span>${esc(m.name)} ${m.banned?'<span class="dn">(kicked)</span>':''}</span><button class="ch" data-k="${d.id}" data-b="${m.banned?0:1}">${m.banned?'Unkick':'Kick'}</button></div>`}).join('')}));
 window._name=async()=>isOwner?'Owner':(await getDoc(doc(db,'members',u.uid))).data().name;
}
$('#ms').onclick=e=>{const d=e.target.dataset.d;if(d)deleteDoc(doc(db,'messages',d))};
$('#ml').onclick=e=>{const k=e.target.dataset.k;if(k)updateDoc(doc(db,'members',k),{banned:e.target.dataset.b=='1'})};
const send=async()=>{const t=$('#ci').value.trim();if(!t)return;$('#ci').value='';const u=au.currentUser;
 try{await addDoc(collection(db,'messages'),{uid:u.uid,name:await window._name(),owner:isOwner,text:t,at:serverTimestamp()})}catch(e){}};
$('#cs').onclick=send;$('#ci').onkeydown=e=>{if(e.key=='Enter')send()};
$('#fab').onclick=()=>{const p=$('#cp');p.style.display=p.style.display=='flex'?'none':'flex'};
$('#t1').onclick=()=>{$('#ms').style.display='';$('#ml').style.display='none';$('#cf').style.display='flex'};
$('#t2').onclick=()=>{$('#ms').style.display='none';$('#ml').style.display='';$('#cf').style.display='none'};
$('#lo').onclick=()=>signOut(au);
