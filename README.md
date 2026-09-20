# Deadlock Prevention ML Research Prototype

Reproducible Python 3.11 prototype combining a discrete resource-allocation simulator, wait-for graph cycle detection, Banker safety checks, recovery, and leakage-free state features with scikit-learn preventive allocators.

## Run
```bash
python -m pip install -r requirements.txt
python scripts/run_all.py
pytest -q
```
This creates `results/dataset.csv`, `results/metrics.csv`, and
`results/allocator_experiments.csv`; plots are written under
`results/plots/` and fitted models under `models/`. The dataset label is
computed from the current state only; `future_horizon` is configurable in
`config.yaml` and retained as an experiment parameter. Seeds make runs
repeatable. The allocator comparison CSV explicitly marks its compact
deterministic benchmark rows as such; they are reporting-interface baselines,
not trace-derived production measurements.

## Guide
Processes have maximum claims, current allocations, and remaining needs. Naive allocation grants immediately; Banker tentatively grants then rolls back unsafe requests. The wait-for graph links a process to any holder of a resource it still needs; strongly connected components identify circular deadlocks. Recovery aborts cycle victims and returns their allocations. Features contain only state variables available before an allocation, preventing temporal leakage. Logistic regression, decision tree, and random forest provide interpretable baselines; `PreventiveAllocator` blocks requests whose predicted risk exceeds a threshold, except after a configurable starvation bound.

Foundational references: Dijkstra (1965), “Solution of a problem in concurrent programming control”; Coffman et al. (1971), “System deadlocks.” Add verified DOI/BibTeX entries before publication.
