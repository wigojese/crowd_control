"""THROWAWAY Stage 03 experiment: Candidate R1 in detail and loop C single actions. Run: python3 -I docs/analysis/stage03_exp3_r1_detail.py"""
import os
import importlib.util
from collections import Counter
spec=importlib.util.spec_from_file_location('m',os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage03_numeric_check.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
N0=dict(m.NODES);L0=list(m.LINKS)
nodes=dict(N0);nodes['C']=(270,115)
links=[(a,b,{('B','D'):0.3}.get((a,b),r)) for a,b,r in L0]
m.configure(nodes,links); m.BONUS=6.0
base=m.run(('A','N'),[],trace=True)
print("candidate R1: C=(270,115), B-D rate 0.3, sign bonus 6.0, sockets A,B,C")
print("baseline no-op:",{k:base[k] for k in('arrived','ontime','score','last_arr','blocked_ticks')})
st={}
for s in 'ABC':
    for h in m.HEADS:
        r=m.run((s,h),[],trace=True); st[(s,h)]=r
        diff=sum(1 for a,b in zip(base['walkers'],r['walkers']) if [(d[1],d[2]) for d in a['decisions']]!=[(d[1],d[2]) for d in b['decisions']])
        print(f"  {s}{h}: arrived {r['arrived']:2d} score {r['score']:3d} last {r['last_arr']} blocked {r['blocked_ticks']:4d} walkers whose route differs from baseline {diff}")
print("static placements with >=18:",[k for k,v in st.items() if v['arrived']>=18])
# loop C: starting from each static, best and worst single running action (rotate/move) every 20 ticks
import itertools
acts=[('ROTATE',h) for h in m.HEADS]+[('MOVE',s) for s in 'ABC']
imp=Counter();tot=0;best=None;worse=0
for key,r0 in st.items():
    for t in range(0,600,20):
        for act,arg in acts:
            r=m.run(key,[(t,act,arg)]);tot+=1
            if r['arrived']>r0['arrived']: imp['better']+=1
            elif r['arrived']<r0['arrived']: imp['worse']+=1
            else: imp['same']+=1
            if best is None or r['arrived']>best[0]: best=(r['arrived'],key,t,act,arg)
print("single running action vs same start without it, %d runs:"%tot,dict(imp)," best:",best)
