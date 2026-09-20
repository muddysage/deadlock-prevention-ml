import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from deadlocklab.experiments import run
from deadlocklab.plots import plot_metrics
if __name__=="__main__":
    print(run()); plot_metrics("results/metrics.csv","results/plots/metrics.png")
