(()=>{const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const list=()=>{const D=window.D;if(!D)return[];const all=[...D.watchlist,...D.tiers.flatMap(t=>t.stocks)];
 return [...new Map(all.map(r=>[r.s,r])).values()].filter(r=>r.score>=8.5&&r.sent>=1).sort((a,b)=>b.score-a.score)};
document.querySelector('header').insertAdjacentHTML('beforeend','<button class="ch" id="bell">🔔 Alerts <b id="bn">0</b></button>');
document.body.insertAdjacentHTML('beforeend','<div id="am" style="display:none;position:fixed;inset:0;background:#0009;z-index:90;padding:16px;overflow:auto"><div class="box" style="max-width:520px;margin:auto"><div class="row"><h2 style="margin:0">🔔 High-conviction signals</h2><button class="ch" id="ac">Close</button></div><div id="al"></div></div></div>');
setInterval(()=>document.getElementById('bn').textContent=list().length,3000);
document.getElementById('bell').onclick=()=>{const a=list();document.getElementById('al').innerHTML=(a.length?a.map(r=>`<div class="card" style="margin-top:8px"><b>${esc(r.s)}</b> · $${r.p.toFixed(2)} · <b>${r.score}/10 (${r.rating})</b>
<div class="e">This stock currently ranks as a high-conviction signal: strong score, positive recent news${r.an?`, ${r.an.strongBuy+r.an.buy} analyst buy ratings`:''}${r.earn?`, earnings ${esc(r.earn)}`:''}.</div>${r.news.map(n=>`<a href="${esc(n.u)}" target="_blank" rel="noopener">${esc(n.h)}</a>`).join('')}</div>`).join(''):'<p class="m">No high-conviction signals right now.</p>')+'<p class="m">Algorithmic signal only. Not financial advice; do your own research.</p>';document.getElementById('am').style.display='block'};
document.getElementById('ac').onclick=()=>document.getElementById('am').style.display='none';})();
