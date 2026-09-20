import networkx as nx
def wait_for_graph(state):
    g=nx.DiGraph(); g.add_nodes_from(p.pid for p in state.processes)
    for p in state.processes:
        for q in state.processes:
            if p.pid!=q.pid and any(n>0 and q.allocation[j]>0 and state.available[j]==0 for j,n in enumerate(p.need)): g.add_edge(p.pid,q.pid)
    return g
def deadlocked(state):
    g=wait_for_graph(state); return sorted(x for c in nx.strongly_connected_components(g) if len(c)>1 for x in c)
def has_deadlock(state): return bool(deadlocked(state))
