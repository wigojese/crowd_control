"""THROWAWAY Stage 03 experiment: Worked junction examples used in docs/RULES.md. Run: python3 -I docs/analysis/stage03_exp5_worked_examples.py"""
import os
import importlib.util
spec=importlib.util.spec_from_file_location('m',os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage03_numeric_check.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
N0=dict(m.NODES);L0=list(m.LINKS)
def show(tag,rows):
    print(tag)
    for r in rows: print("   ",r)
print("REV0 (spec as written)")
m.BONUS=4.0
show("W1 Commuter->F at B, sign B/S, no queue (cols: edge, travel s, crowd s, loop s, sign s, cost)",m.explain('B','F','C',prev='A',sign=('B','S')))
show("W2 Follower->F at B, sign B/E, 5 waiting on BD, 0 tokens",m.explain('B','F','F',prev='A',sign=('B','E'),queue_ahead={'BD':5},tokens={'BD':0.0}))
show("W3 Independent->F at B, sign B/S",m.explain('B','F','I',prev='A',sign=('B','S')))
show("W4 Commuter->G at C, sign C/W (favours CA,CB), no queue",m.explain('C','G','C',prev='A',sign=('C','W')))
show("W5 Commuter->F at C came A,B,C (loop penalty on CA? hist=[A,B])",m.explain('C','F','C',hist=['A','B'],prev='B',sign=None))
nodes=dict(N0);nodes['C']=(270,115);links=[(a,b,{('B','D'):0.3}.get((a,b),r)) for a,b,r in L0]
m.configure(nodes,links);m.BONUS=6.0
print("\nR1 candidate (C=(270,115), B-D 0.3/s, bonus 6.0)")
show("W6 Follower->F at A, sign A/E",m.explain('A','F','F',sign=('A','E')))
show("W7 Commuter->F at A, sign A/E",m.explain('A','F','C',sign=('A','E')))
show("W8 Independent->F at A, sign A/E",m.explain('A','F','I',sign=('A','E')))
print("\nR1 with two sockets A,B: static + single running action")
from collections import Counter
st={}
for s in 'AB':
    for h in m.HEADS: st[(s,h)]=m.run((s,h),[])
print(" static:"," ".join(f"{s}{h}:{r['arrived']}" for (s,h),r in st.items()))
acts=[('ROTATE',h) for h in m.HEADS]+[('MOVE',s) for s in 'AB']
imp=Counter();tot=0;best=None
for key,r0 in st.items():
    for t in range(0,600,20):
        for act,arg in acts:
            r=m.run(key,[(t,act,arg)]);tot+=1
            imp['better' if r['arrived']>r0['arrived'] else 'worse' if r['arrived']<r0['arrived'] else 'same']+=1
            if best is None or r['arrived']>best[0]: best=(r['arrived'],key,t,act,arg)
print(" single running action vs same start without it, %d runs:"%tot,dict(imp)," best:",best)
# one concrete loop-C story: start B/E? find a start that fails and a rescuing action
for key,r0 in st.items():
    if r0['arrived']<18:
        for t in range(0,600,20):
            for act,arg in acts:
                r=m.run(key,[(t,act,arg)])
                if r['arrived']>=18: print(" rescue example: start",key,"arrived",r0['arrived'],"-> action",(t,act,arg),"arrived",r['arrived']); break
            else: continue
            break
        break
