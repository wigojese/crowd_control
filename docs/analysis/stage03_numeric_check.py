#!/usr/bin/env python3
"""Stage 03 THROWAWAY numeric check of CC-RULESET-01 plus loop C.
Not engine code. Pure standard library. Run: python3 -I docs/analysis/stage03_numeric_check.py
Implements the tick order in docs/SIMULATION_EVENTS.md so numbers in docs/RULES.md can be reproduced.
"""
import math, heapq, itertools, sys, json
DT=0.05; TICKS=640; DEADLINE_TICK=600
NODES={'A':(180,50),'B':(92,145),'C':(262,155),'D':(120,286),'E':(254,290),'F':(106,470),'G':(266,475)}
LINKS=[('A','B',3.0),('A','C',3.0),('B','C',3.0),('B','D',1.6),('C','E',3.0),('D','E',1.2),('D','F',3.0),('E','G',3.0),('F','G',3.0)]
PROF={'C':dict(sign=.8,crowd=.35,speed=38.0),'F':dict(sign=1.0,crowd=.9,speed=34.0),'I':dict(sign=.35,crowd=.2,speed=42.0)}
DIRV={'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}; HEADS=['N','E','S','W']
SIGN_RADIUS=90.0; DOT_MIN=0.65; BONUS=4.0; LOOP_PEN=6.0; REEVAL=10
LOCK=80; HOLD=10
def dist(a,b): return math.dist(NODES[a],NODES[b])
EDGES={}  # id -> (from,to,len,rate)
for a,b,r in LINKS:
    EDGES[a+b]=(a,b,dist(a,b),r); EDGES[b+a]=(b,a,dist(a,b),r)
OUT={n:sorted(e for e,v in EDGES.items() if v[0]==n) for n in NODES}
def sp(src):  # dijkstra on lengths
    d={n:1e18 for n in NODES}; d[src]=0; pq=[(0,src)]
    while pq:
        c,u=heapq.heappop(pq)
        if c>d[u]: continue
        for e in OUT[u]:
            v=EDGES[e][1]; nd=c+EDGES[e][2]
            if nd<d[v]: d[v]=nd; heapq.heappush(pq,(nd,v))
    return d
SPD={n:sp(n) for n in NODES}
def configure(nodes=None,links=None):
    """Experiment hook: replace the graph in place (module-level dicts are mutated)."""
    if nodes: NODES.clear(); NODES.update(nodes)
    if links is not None: LINKS[:]=links
    EDGES.clear()
    for a,b,r in LINKS:
        EDGES[a+b]=(a,b,dist(a,b),r); EDGES[b+a]=(b,a,dist(a,b),r)
    OUT.clear(); OUT.update({n:sorted(e for e,v in EDGES.items() if v[0]==n) for n in NODES})
    SPD.clear(); SPD.update({n:sp(n) for n in NODES})
def favoured(node,head):
    out=[]
    for e in OUT[node]:
        a,b,L,_=EDGES[e]; ux=(NODES[b][0]-NODES[a][0])/L; uy=(NODES[b][1]-NODES[a][1])/L
        if ux*DIRV[head][0]+uy*DIRV[head][1]>=DOT_MIN: out.append(e)
    return out
SCHEDULE=[(0,'A','F',[('C',7),('F',3),('I',2)]),(40,'A','G',[('C',4),('F',3),('I',1)])]
def make_walkers():
    W=[];i=0
    for tick,origin,dest,mix in SCHEDULE:
        for p,n in mix:
            for _ in range(n): W.append(dict(id=i,prof=p,origin=origin,dest=dest,spawn=tick,state='UNSPAWNED',node=None,edge=None,t=0.0,hist=[],q=None,qtick=0,lasteval=-99,arr=None,blocked=0,alive=0,prev=None,decisions=[])); i+=1
    return W
def run(sign_state, commands, trace=False):
    """sign_state: None or (slot,heading) at Start. commands: list of (tick,'ROTATE',heading) or (tick,'MOVE',slot)."""
    W=make_walkers(); tokens={e:min(1.0,max(1.0,v[3])) for e,v in EDGES.items()}
    fifo={e:[] for e in EDGES}
    sign=dict(slot=None,head=None,active=False,lock_until=-1,drop_at=None,pending=None)
    if sign_state: sign.update(slot=sign_state[0],head=sign_state[1],active=True)
    cmds=sorted(commands); ci=0; blocked_total=0; person_total=0; log=[]; sign_actions=0; changed=False
    for t in range(TICKS):
        changed=False
        # 1 commands
        if sign['pending'] and sign['drop_at']==t:
            sign.update(slot=sign['pending'],active=True,lock_until=t+LOCK,pending=None,drop_at=None); changed=True
        while ci<len(cmds) and cmds[ci][0]==t:
            _,act,arg=cmds[ci]; ci+=1
            if t<sign['lock_until'] or sign['pending'] or sign['slot'] is None: log.append((t,'REJECT',act)); continue
            if act=='ROTATE': sign['head']=arg; sign['lock_until']=t+LOCK; changed=True; sign_actions+=1
            if act=='MOVE' and arg!=sign['slot']:
                sign['pending']=arg; sign['drop_at']=t+HOLD; sign['active']=False; changed=True; sign_actions+=1
        # 2 spawn
        for w in W:
            if w['state']=='UNSPAWNED' and w['spawn']==t: w['state']='NEEDS'; w['node']=w['origin']
        # 3 refill
        for e,v in EDGES.items(): tokens[e]=min(max(1.0,v[3]*1.0),tokens[e]+v[3]*DT)
        # 4 decisions
        for w in W:
            due=w['state']=='NEEDS' or (w['state']=='QUEUED' and (t-w['lasteval']>=REEVAL or (changed and w['node'] in (sign['slot'],)) or changed))
            if not due: continue
            p=PROF[w['prof']]; best=None
            for e in OUT[w['node']]:
                a,b,L,r=EDGES[e]
                if w['prev'] is not None and b==w['prev'] and len(OUT[w['node']])>1: continue
                rem=(L+SPD[b][w['dest']])/p['speed']
                ahead=len([x for x in fifo[e] if x[0]!=w['id']]) if w['q']!=e else fifo[e].index(next(x for x in fifo[e] if x[0]==w['id']))
                qw=max(0.0,ahead+1-tokens[e])/r
                loop=LOOP_PEN if b in w['hist'][-3:] else 0.0
                bonus=BONUS if (sign['active'] and sign['slot']==w['node'] and dist(sign['slot'],w['node'])<=SIGN_RADIUS and e in favoured(sign['slot'],sign['head'])) else 0.0
                cost=rem+p['crowd']*qw+loop-p['sign']*bonus
                if best is None or cost<best[0]-1e-12 or (abs(cost-best[0])<=1e-12 and e<best[1]): best=(cost,e,bonus)
            e=best[1]
            if w['q']!=e:
                if w['q']: fifo[w['q']]=[x for x in fifo[w['q']] if x[0]!=w['id']]
                fifo[e].append((w['id'],t)); w['q']=e
            w['state']='QUEUED'; w['lasteval']=t
            w['decisions'].append((t,w['node'],e,round(best[0],2),best[2]))
        # 5 service
        entered=set()
        for e in sorted(EDGES):
            while tokens[e]>=1.0 and fifo[e]:
                wid,_=fifo[e].pop(0); w=W[wid]; tokens[e]-=1.0
                w.update(state='ON_EDGE',edge=e,t=0.0,q=None); w['hist'].append(w['node']); w['prev']=w['node']; entered.add(wid)
        # 6/7 movement + arrivals
        for w in W:
            if w['state']=='ON_EDGE' and w['id'] not in entered:
                a,b,L,_=EDGES[w['edge']]; w['t']+=PROF[w['prof']]['speed']*DT/L
                if w['t']>=1.0:
                    w['node']=b; w['edge']=None
                    if b==w['dest']: w['state']='ARRIVED'; w['arr']=t+1
                    else: w['state']='NEEDS'
        # 8 metrics
        for w in W:
            if w['state'] in('QUEUED','NEEDS','ON_EDGE'): person_total+=1; w['alive']+=1
            if w['state']=='QUEUED': w['blocked']+=1; blocked_total+=1
    arrived=[w for w in W if w['state']=='ARRIVED']
    ontime=[w for w in arrived if w['arr']<=DEADLINE_TICK]
    dr=len(arrived)/20; otr=len(ontime)/max(1,len(arrived)); cs=blocked_total/max(1,person_total)
    score=round(100*(.7*dr+.2*otr+.1*(1-min(1,max(0,cs)))))
    res=dict(arrived=len(arrived),ontime=len(ontime),blocked_ticks=blocked_total,person_ticks=person_total,score=score,passed=len(arrived)>=16,sign_actions=sign_actions,
             last_arr=max((w['arr'] for w in arrived),default=None))
    if trace: res['walkers']=W
    return res
def explain(node,dest,prof,hist=(),prev=None,sign=None,queue_ahead=None,tokens=None):
    """Cost breakdown for one decision. sign=(slot,heading) or None. queue_ahead={edge:n} walkers already waiting."""
    p=PROF[prof]; rows=[]; queue_ahead=queue_ahead or {}; tokens=tokens or {}
    for e in OUT[node]:
        a,b,L,r=EDGES[e]
        if prev is not None and b==prev and len(OUT[node])>1: rows.append((e,'excluded: reverses previous edge'));continue
        rem=(L+SPD[b][dest])/p['speed']; ahead=queue_ahead.get(e,0); tk=tokens.get(e,1.0)
        qw=max(0.0,ahead+1-tk)/r; loop=LOOP_PEN if b in list(hist)[-3:] else 0.0
        bonus=BONUS if (sign and sign[0]==node and dist(sign[0],node)<=SIGN_RADIUS and e in favoured(sign[0],sign[1])) else 0.0
        cost=rem+p['crowd']*qw+loop-p['sign']*bonus
        rows.append((e,round(rem,2),round(p['crowd']*qw,2),loop,round(-p['sign']*bonus,2),round(cost,2)))
    return rows
if __name__=='__main__':
    print("Truth table: favoured edges (dot >= %.2f)"%DOT_MIN)
    for n in 'BC':
        for h in HEADS: print(f"  sign at {n} heading {h}: {favoured(n,h)}")
    base=run(None,[]); print("\nNO SIGN baseline:",base)
    print("\nStatic placements (placed before Start, never touched):")
    stat={}
    for s in 'BC':
        for h in HEADS:
            r=run((s,h),[]); stat[(s,h)]=r; print(f"  {s}/{h}: arrived {r['arrived']:2d} ontime {r['ontime']:2d} score {r['score']:3d} blocked_ticks {r['blocked_ticks']:4d} last_arr_tick {r['last_arr']} pass={r['passed']}")
    # single running action search
    best=[]; allr=[]
    acts=[('ROTATE',h) for h in HEADS]+[('MOVE','B'),('MOVE','C')]
    for s in 'BC':
        for h in HEADS:
            for t in range(0,600,10):
                for act,arg in acts:
                    r=run((s,h),[(t,act,arg)]); allr.append(((s,h,t,act,arg),r))
    allr.sort(key=lambda x:(-x[1]['arrived'],-x[1]['score']))
    print("\nSingle running action search: %d runs"%len(allr))
    from collections import Counter
    print("  arrived distribution:",sorted(Counter(r['arrived'] for _,r in allr).items()))
    print("  top 5:"); [print("   ",k,v['arrived'],v['score']) for k,v in allr[:5]]
    print("  worst 3:"); [print("   ",k,v['arrived'],v['score']) for k,v in allr[-3:]]
