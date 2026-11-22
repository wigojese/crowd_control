"""THROWAWAY Stage 03 experiment: Grid for candidate R1 (C moved, sockets A,B,C). Run: python3 -I docs/analysis/stage03_exp2_r1_grid.py"""
import os
import importlib.util,itertools
spec=importlib.util.spec_from_file_location('m',os.path.join(os.path.dirname(os.path.abspath(__file__)),'stage03_numeric_check.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
N0=dict(m.NODES);L0=list(m.LINKS)
nodes=dict(N0);nodes['C']=(270,115)
rows=[]
for rbd,rde,rce,bonus in itertools.product((0.3,0.4,0.5),(0.5,1.2),(3.0,1.0),(4.0,6.0,9.0)):
    links=[(a,b,{('B','D'):rbd,('D','E'):rde,('C','E'):rce}.get((a,b),r)) for a,b,r in L0]
    m.configure(nodes,links); m.BONUS=bonus
    base=m.run(('A','N'),[])
    st={(s,h):m.run((s,h),[]) for s in 'ABC' for h in m.HEADS}
    arr=sorted(v['arrived'] for v in st.values())
    rows.append((rbd,rde,rce,bonus,base['arrived'],arr[0],arr[-1],sum(1 for v in st.values() if v['passed'])))
print("r_BD r_DE r_CE bonus | baseline | worst best #pass/12")
for r in rows:
    flag="  <== interesting" if (r[4]<=17 and r[6]>=r[4]+2) else ""
    print(f"{r[0]:4} {r[1]:4} {r[2]:4} {r[3]:4} | {r[4]:3d} | {r[5]:3d} {r[6]:3d} {r[7]:2d}{flag}")
