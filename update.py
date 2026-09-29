import json,os,time,datetime as d,urllib.request as u
K=os.environ["FINNHUB_KEY"]
def g(p):
    time.sleep(1.1)
    try: return json.load(u.urlopen(f"https://finnhub.io/api/v1/{p}&token={K}",timeout=20))
    except Exception: return None
rd=lambda f:list(dict.fromkeys(open(f).read().split()))
W,U=rd("watchlist.txt"),rd("universe.txt")
PRI=set(W[:11])
POS="beat surge soar jump upgrade record raise growth win partnership approval expands strong rally".split()
NEG="miss plunge fall drop downgrade lawsuit probe cut weak recall halt dilution offering warning".split()
now=d.date.today();fr=(now-d.timedelta(7)).isoformat()
ea=g(f"calendar/earnings?from={now}&to={now+d.timedelta(45)}") or {}
E={e["symbol"]:e["date"] for e in ea.get("earningsCalendar",[])}
cl=lambda v,a,b:max(a,min(b,v))
def rating(x):
    return "Strong Buy" if x>=8.5 else "Buy" if x>=7 else "Hold" if x>=5 else "Sell" if x>=3.5 else "Strong Sell"
def rec(s):
    q=g(f"quote?symbol={s}")
    if not q or not q.get("c"): return None
    r={"s":s,"p":q["c"],"chg":q.get("dp") or 0,"sent":0,"pri":s in PRI,"earn":E.get(s)}
    n=g(f"company-news?symbol={s}&from={fr}&to={now}") or []
    for a in n[:12]:
        t=a.get("headline","").lower()
        r["sent"]+=sum(w in t for w in POS)-sum(w in t for w in NEG)
    r["news"]=[{"h":a["headline"],"u":a["url"],"src":a.get("source",""),"t":a.get("datetime",0)} for a in n[:3]]
    rc=g(f"stock/recommendation?symbol={s}");an=rc[0] if rc else None
    r["an"]={k:an.get(k,0) for k in("strongBuy","buy","hold","sell","strongSell")} if an else None
    a=2.0
    if an:
        t=sum(r["an"].values())
        if t: a=(((2*an["strongBuy"]+an["buy"]-an["sell"]-2*an["strongSell"])/(2*t))+1)/2*4
    m=(cl(r["chg"],-5,5)+5)/10*2.5
    nw=(cl(r["sent"],-3,3)+3)/6*2.5
    c=.5
    if r["earn"] and 0<=(d.date.fromisoformat(r["earn"])-now).days<=14: c=1
    r["score"]=round(m+a+nw+c,1);r["rating"]=rating(r["score"])
    return r
wl=sorted([x for x in map(rec,W) if x],key=lambda r:-r["score"])
un=[x for x in map(rec,U) if x]
pool=un+[r for r in wl if r["p"]<50]
T=[(0,1),(1,5),(5,10),(10,25),(25,50)]
tiers=[{"label":f"${lo} – ${hi}","stocks":sorted([r for r in pool if lo<=r["p"]<hi],key=lambda r:-r["score"])[:10]} for lo,hi in T]
mk=[{"h":a["headline"],"u":a["url"],"src":a.get("source","")} for a in (g("news?category=general") or [])[:6]]
json.dump({"updated":d.datetime.utcnow().isoformat()+"Z","market":mk,"watchlist":wl,"tiers":tiers},open("data.json","w"))
