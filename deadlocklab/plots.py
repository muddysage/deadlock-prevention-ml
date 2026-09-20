import os
def plot_metrics(csv_path="results/metrics.csv", out="plots/metrics.png"):
    import csv, matplotlib.pyplot as plt
    rows=list(csv.DictReader(open(csv_path))); names=[r["model"] for r in rows]
    vals=[[float(r[c]) for r in rows] for c in ("accuracy","precision","recall","f1")]
    fig,ax=plt.subplots(figsize=(7,4)); x=range(len(names)); w=.2
    for i,(label,v) in enumerate(zip(("accuracy","precision","recall","f1"),vals)): ax.bar([q+w*i for q in x],v,w,label=label)
    ax.set_xticks([q+1.5*w for q in x],names); ax.set_ylim(0,1); ax.legend(); fig.tight_layout()
    os.makedirs(os.path.dirname(out),exist_ok=True); fig.savefig(out,dpi=140); plt.close(fig)
