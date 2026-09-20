"""Naive, Banker and recovery policies for multiple-instance resources."""
def naive_allocate(state,pid,req):
    p=state.processes[pid]
    if len(req)!=len(state.available) or any(x<0 or x>p.need[j] or x>state.available[j] for j,x in enumerate(req)): return False
    state.available=[a-x for a,x in zip(state.available,req)]
    p.allocation=[a+x for a,x in zip(p.allocation,req)]; p.need=[n-x for n,x in zip(p.need,req)]
    return True
def safety_sequence(state):
    work=state.available[:]; finish=[False]*len(state.processes); seq=[]
    while True:
        found=False
        for i,p in enumerate(state.processes):
            if not finish[i] and all(p.need[j]<=work[j] for j in range(len(work))):
                work=[work[j]+p.allocation[j] for j in range(len(work))]; finish[i]=True; seq.append(p.pid); found=True
        if not found: break
    return (all(finish),seq)
def bankers_safe(state): return safety_sequence(state)[0]
def banker_request(state,pid,req):
    p=state.processes[pid]
    if any(x<0 or x>p.need[j] or x>state.available[j] for j,x in enumerate(req)): return False
    old=(state.available[:],p.allocation[:],p.need[:])
    naive_allocate(state,pid,req)
    if bankers_safe(state): return True
    state.available[:],p.allocation[:],p.need[:]=old; return False
def detect_and_recover(state):
    from .graph import deadlocked
    victims=deadlocked(state)
    for pid in victims:
        p=state.processes[pid]; state.available=[a+x for a,x in zip(state.available,p.allocation)]
        p.allocation=[0]*len(p.allocation); p.phase="aborted"
    return victims
