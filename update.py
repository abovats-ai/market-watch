import json,os,time,datetime as d,urllib.request as u
K=os.environ["FINNHUB_KEY"]
def g(p):
    time.sleep(1.1)
    try: return json.load(u.urlopen(f"https://finnhub.io/api/v1/{p}&token={K}",timeout=20))
    except Exception: return None
rd=lambda f:list(dict.fromkeys(open(f).read().split())) if os.path.exists(f) else []
W,U,H=rd("watchlist.txt"),rd("universe.txt"),set(rd("halal.txt"))
PRI=set(W[:11])
MK="revenueGrowthTTMYoy epsGrowthTTMYoy grossMarginTTM operatingMarginTTM netProfitMarginTTM roeTTM roiTTM roaTTM currentRatioQuarterly quickRatioQuarterly totalDebt/totalEquityQuarterly netInterestCoverageTTM pfcfShareTTM psTTM pbQuarterly dividendYieldIndicatedAnnual payoutRatioTTM 13WeekPriceReturnDaily 26WeekPriceReturnDaily 52WeekPriceReturnDaily 10DayAverageTradingVolume".split()
try: prev={r["s"]:r for r in json.load(open("data.json"))["_all"]}
except Exception: prev={}
POS="beat surge soar jump upgrade record raise growth win partnership approval expands strong rally".split()
NEG="miss plunge fall drop downgrade lawsuit probe cut weak recall halt dilution offering warning".split()
now=d.date.today();fr=(now-d.timedelta(7)).isoformat()
ea=g(f"calendar/earnings?from={now}&to={now+d.timedelta(45)}") or {}
E={e["symbol"]:e["date"] for e in ea.get("earningsCalendar",[])}
cl=lambda v,a,b:max(a,min(b,v))
G=[("Semis",["semiconductor"]),("Tech",["technology","software","communication","media","internet","telecom"]),("Health",["health","pharma","biotech","life sciences"]),("Energy",["energy","oil","gas","coal","utilit"]),("Finance",["bank","financ","insurance","capital markets"]),("Industrials",["machinery","aerospace","industr","transport","airline","auto","construction","electrical","building","trading","logistic"]),("Consumer",["retail","consumer","food","beverage","hotel","leisure","restaurant","textile"]),("Materials",["metal","mining","chemical","material"])]
def grp(i):
    i=(i or "").lower()
    return next((n for n,k in G if any(x in i for x in k)),"Other")
HARAM="bank financ insurance tobacco casino gambl alcohol brew wine distill".split()
def rating(x): return "Strong Buy" if x>=8.5 else "Buy" if x>=7 else "Hold" if x>=5 else "Sell" if x>=3.5 else "Strong Sell"
START=time.time()
def rec(s):
    if time.time()-START>3000: return prev.get(s)
    q=g(f"quote?symbol={s}")
    if not q or not q.get("c"): return None
    o=prev.get(s,{});pf=o.get("prof")
    if not pf or "mx" not in pf or (now-d.date.fromisoformat(pf["ts"])).days>7:
        p=g(f"stock/profile2?symbol={s}") or {};m=(g(f"stock/metric?symbol={s}&metric=all") or {}).get("metric",{})
        pf={"name":p.get("name",s),"ind":p.get("finnhubIndustry",""),"hi":m.get("52WeekHigh"),"lo":m.get("52WeekLow"),"pe":m.get("peTTM"),"beta":m.get("beta"),"mx":{k:m.get(k) for k in MK},"x":{k:p.get(k) for k in ("exchange","country","currency","marketCapitalization","shareOutstanding","ipo")},"ts":str(now)}
    r={"s":s,"p":q["c"],"chg":q.get("dp") or 0,"sent":0,"pri":s in PRI,"earn":E.get(s),"prof":pf,"deep":o.get("deep"),"sec":grp(pf["ind"]),"hist":(o.get("hist",[])+[q["c"]])[-96:]}
    r["halal"]="yes" if s in H else "no" if any(x in (pf["ind"]+pf["name"]).lower() for x in HARAM) else "check"
    stale=not o.get("nts") or time.time()-o["nts"]>21600 or s in PRI or abs(r["chg"])>=5
    if stale:
        n=g(f"company-news?symbol={s}&from={fr}&to={now}") or []
        for a in n[:12]:
            t=a.get("headline","").lower();r["sent"]+=sum(w in t for w in POS)-sum(w in t for w in NEG)
        r["news"]=[{"h":a["headline"],"u":a["url"],"src":a.get("source",""),"t":a.get("datetime",0)} for a in n[:3]]
        rc=g(f"stock/recommendation?symbol={s}");an0=rc[0] if rc else None
        r["an"]={k:an0.get(k,0) for k in("strongBuy","buy","hold","sell","strongSell")} if an0 else None
        r["nts"]=time.time()
    else:
        r["sent"],r["news"],r["an"],r["nts"]=o.get("sent",0),o.get("news",[]),o.get("an"),o["nts"]
    an=r["an"]
    a=1.75
    if an:
        t=sum(r["an"].values())
        if t: a=(((2*an["strongBuy"]+an["buy"]-an["sell"]-2*an["strongSell"])/(2*t))+1)/2*3.5
    tr=.5
    if pf["hi"] and pf["lo"] and pf["hi"]>pf["lo"]: tr=cl((r["p"]-pf["lo"])/(pf["hi"]-pf["lo"]),0,1)
    c=1 if r["earn"] and 0<=(d.date.fromisoformat(r["earn"])-now).days<=14 else .5
    r["score"]=round(a+(cl(r["chg"],-5,5)+5)/10*2+(cl(r["sent"],-3,3)+3)/6*2.5+tr+c,1);r["rating"]=rating(r["score"])
    return r
wl=sorted([x for x in map(rec,W) if x],key=lambda r:-r["score"])
un=[x for x in map(rec,U) if x]
allr=list({r["s"]:r for r in un+wl}.values())
pool=[r for r in allr if r["p"]<70]
T=[(0,1),(1,5),(5,10),(10,25),(25,70)]
tiers=[{"label":f"${lo} – ${hi}","stocks":sorted([r for r in pool if lo<=r["p"]<hi],key=lambda r:-r["score"])[:12]} for lo,hi in T]
def deep(r):
    o=r.get("deep")
    if o and time.time()-o["ts"]<86400: return
    s=r["s"]
    e=g(f"stock/earnings?symbol={s}&limit=4") or []
    it=(g(f"stock/insider-transactions?symbol={s}&from={now-d.timedelta(90)}&to={now}") or {}).get("data",[])
    pe=g(f"stock/peers?symbol={s}") or []
    r["deep"]={"ts":time.time(),"beats":sum(1 for x in e if x.get("actual") is not None and x.get("estimate") is not None and x["actual"]>x["estimate"]),"n":len(e),"sur":[x.get("surprisePercent") for x in e],"ib":sum(1 for x in it if x.get("transactionCode")=="P"),"is":sum(1 for x in it if x.get("transactionCode")=="S"),"peers":pe[:6]}
for r in {r["s"]:r for r in [x for x in wl if x["pri"]]+[x for t in tiers for x in t["stocks"]]+wl[:25]}.values():
    if time.time()-START<3000: deep(r)
EV=[("Rate cuts",["rate cut","cuts rates","cut interest"],{"Tech":1,"Semis":1,"Health":1,"Industrials":1}),("Rate/inflation pressure",["rate hike","hot inflation","inflation rises","inflation jumps"],{"Tech":-1,"Semis":-1}),("Tariffs",["tariff"],{"Semis":-1,"Industrials":-1,"Consumer":-1}),("Chip export limits",["export control","chip ban","chip curb","export restriction"],{"Semis":-1}),("Oil spike",["oil surge","oil jumps","crude jumps","oil prices rise"],{"Energy":1,"Industrials":-1}),("Oil drop",["oil plunge","oil falls","crude falls","oil prices fall"],{"Energy":-1,"Industrials":1}),("AI demand",["ai demand","data center","ai spending","ai boom"],{"Semis":1,"Tech":1}),("Conflict/sanctions",["war ","sanction","missile","ceasefire"],{"Energy":1,"Consumer":-1}),("Recession fears",["recession","layoffs","job cuts"],{"Consumer":-1,"Industrials":-1,"Tech":-1})]
gn=g("news?category=general") or []
mk=[{"h":a["headline"],"u":a["url"],"src":a.get("source","")} for a in gn[:8]]
ev=[]
for a in gn[:40]:
    t=a["headline"].lower()
    for nm,ks,imp in EV:
        if any(k in t for k in ks):
            top=lambda sg:[r["s"] for r in sorted([r for r in pool if imp.get(r["sec"])==sg],key=lambda r:-r["score"])[:6]]
            ev.append({"name":nm,"h":a["headline"],"u":a["url"],"src":a.get("source",""),"up":top(1),"dn":top(-1)});break
    if len(ev)>=6:break
brk=[{"s":r["s"],"chg":r["chg"],"sent":r["sent"]} for r in allr if abs(r["chg"])>=8 or abs(r["sent"])>=4]
json.dump({"updated":d.datetime.utcnow().isoformat()+"Z","market":mk,"events":ev,"breaking":brk,"watchlist":wl,"tiers":tiers,"_all":allr},open("data.json","w"))
