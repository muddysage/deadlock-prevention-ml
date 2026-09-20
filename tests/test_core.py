from deadlocklab.simulator import random_state,State,Process
from deadlocklab.graph import has_deadlock
from deadlocklab.allocator import bankers_safe, banker_request
def test_safe():
 s=State([1,1],[Process(0,[1,1],[0,0],[1,1])]); assert bankers_safe(s)
def test_cycle():
 s=State([0,0],[Process(0,[1,1],[1,0],[0,1]),Process(1,[1,1],[0,1],[1,0])]); assert has_deadlock(s)

def test_banker_denies_unsafe_request():
 s=State([1,0],[
     Process(0,[1,1],[0,1],[1,0]),
     Process(1,[1,1],[0,0],[1,1]),
 ])
 assert not banker_request(s,1,[1,0])
 assert s.available == [1,0]
