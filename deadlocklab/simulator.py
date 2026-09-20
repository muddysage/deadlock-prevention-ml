from dataclasses import dataclass
from typing import List
import random
@dataclass
class Process:
    pid:int; max_claim:List[int]; allocation:List[int]; need:List[int]; phase:str="running"; wait_age:int=0
@dataclass
class State:
    available:List[int]; processes:List[Process]; t:int=0
    def clone(self): return State(self.available[:],[Process(p.pid,p.max_claim[:],p.allocation[:],p.need[:],p.phase,p.wait_age) for p in self.processes],self.t)
def random_state(n=6,resources=3,seed=0,deadlock_rate=.2):
    r=random.Random(seed); total=[r.randint(3,8) for _ in range(resources)]; ps=[]
    for i in range(n):
        mx=[r.randint(1,total[j]) for j in range(resources)]; a=[r.randint(0,mx[j]//2) for j in range(resources)]
        ps.append(Process(i,mx,a,[mx[j]-a[j] for j in range(resources)]))
    used=[sum(p.allocation[j] for p in ps) for j in range(resources)]; av=[max(0,total[j]-used[j]) for j in range(resources)]
    if r.random()<deadlock_rate and n>=2 and resources>=2:
        ps[0].allocation[:2]=[1,0]; ps[0].need[:2]=[0,1]; ps[1].allocation[:2]=[0,1]; ps[1].need[:2]=[1,0]; av[:2]=[0,0]
    return State(av,ps)
