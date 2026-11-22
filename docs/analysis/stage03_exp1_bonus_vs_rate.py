"""THROWAWAY Stage 03 experiment: Grid: sign bonus vs B-D rate on CC-L01 rev0. Run: python3 -I docs/analysis/stage03_exp1_bonus_vs_rate.py"""
import os
import importlib.util,sys,itertools
spec=importlib.util.spec_from_file_location('m',os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage03_numeric_check.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def setrate(a,b,r):
    for e in (a+b,b+a):
        x=m.EDGES[e];m.EDGES[e]=(x[0],x[1],x[2],r)
orig={e:v for e,v in m.EDGES.items()}
def reset():
    for e,v in orig.items(): m.EDGES[e]=v
def evalcfg(bonus,rbd,rde=1.2):
    reset(); m.BONUS=bonus; setrate('B','D',rbd); setrate('D','E',rde)
    base=m.run(('B','W'),[])  # W at B favours nothing: the "no-op" placement
    st={(s,h):m.run((s,h),[]) for s in 'BC' for h in m.HEADS}
    arr=[v['arrived'] for v in st.values()]
    return base['arrived'],base['last_arr'],max(arr),min(arr),sum(1 for v in st.values() if v['passed'])
print("bonus  r_BD | baseline(arr,last_tick) | static best  worst  #pass/8")
for bonus in (4,6,8,9,10,12):
    for rbd in (1.6,1.2,1.0,0.8,0.6):
        b,l,mx,mn,np_=evalcfg(bonus,rbd)
        print(f"{bonus:5} {rbd:5} | {b:2d} {l} | {mx:2d} {mn:2d} {np_}")
