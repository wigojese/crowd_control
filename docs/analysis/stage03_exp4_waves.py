"""THROWAWAY Stage 03 experiment: Two-wave schedules: when does a running action matter. Run: python3 -I docs/analysis/stage03_exp4_waves.py"""
import os
import importlib.util
from collections import Counter
spec=importlib.util.spec_from_file_location('m',os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage03_numeric_check.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
N0=dict(m.NODES);L0=list(m.LINKS)
nodes=dict(N0);nodes['C']=(270,115);links=[(a,b,{('B','D'):0.3}.get((a,b),r)) for a,b,r in L0]
m.configure(nodes,links);m.BONUS=6.0
def study(label,sched):
    m.SCHEDULE[:]=sched
    st={(s,h):m.run((s,h),[]) for s in 'AB' for h in m.HEADS}
    sa={k:v['arrived'] for k,v in st.items()}
    bestst=max(sa.values())
    acts=[('ROTATE',h) for h in m.HEADS]+[('MOVE',s) for s in 'AB']
    best=(0,None)
    for key in st:
        for t in range(0,600,20):
            for act,arg in acts:
                a=m.run(key,[(t,act,arg)])['arrived']
                if a>best[0]: best=(a,(key,t,act,arg))
    # two actions: start A/E-ish? search start x two times with fixed action set (coarser)
    best2=(0,None)
    for key in st:
        for t1 in range(0,400,40):
            for a1 in acts:
                for t2 in range(t1+80,640,40):
                    for a2 in acts:
                        a=m.run(key,[(t1,a1[0],a1[1]),(t2,a2[0],a2[1])])['arrived']
                        if a>best2[0]: best2=(a,(key,t1,a1,t2,a2))
    print(f"{label}: static {sa}\n   best static {bestst}; best with 1 running action {best}; best with 2 {best2}")
print()
study("conflicting waves: F-wave 12 at t=0, second F-wave 8 at tick 300 (15 s)",[(0,'A','F',[('C',7),('F',3),('I',2)]),(300,'A','F',[('C',4),('F',3),('I',1)])])
study("conflicting waves, second wave at tick 360 (18 s)",[(0,'A','F',[('C',7),('F',3),('I',2)]),(360,'A','F',[('C',4),('F',3),('I',1)])])
