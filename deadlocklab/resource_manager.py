from .events import Event
class ResourceManager:
    """Event-sourced manager: every attempted request/release is logged."""
    def __init__(self,state): self.state=state; self.log=[]
    def apply(self,event,allocator=None):
        from .allocator import naive_allocate
        ok = naive_allocate(self.state,event.pid,list(event.vector)) if event.kind=="request" else self._release(event)
        self.log.append(Event(event.time,event.run_id,event.pid,event.kind,event.vector,ok,"granted" if ok else "denied"))
        return ok
    def _release(self,e):
        p=self.state.processes[e.pid]
        if any(x>y for x,y in zip(e.vector,p.allocation)): return False
        self.state.available=[x+y for x,y in zip(self.state.available,e.vector)]
        p.allocation=[x-y for x,y in zip(p.allocation,e.vector)]
        return True
