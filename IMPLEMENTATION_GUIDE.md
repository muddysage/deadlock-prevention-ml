# Plain-language implementation guide

## What the prototype does

The prototype models processes competing for several resource types where each
type can have multiple identical instances. A process has a maximum claim, its
current allocation, and its remaining need. `State.available` is the inventory
not currently held.

## Event flow

Behavior generators produce explicit request events. `ResourceManager` applies
them and appends a result event to an in-memory log, including whether the
request was granted and why. This makes a run auditable and makes future
replay straightforward.

## Safety and recovery

The naive allocator grants any request that fits. Banker tentatively grants a
request, searches for an ordering in which every process can finish, and rolls
back if no ordering exists. The wait-for graph links blocked processes to
holders; strongly connected components identify circular waits. Recovery aborts
cycle members and returns their allocations.

## Data and models

Each dataset row contains a run ID and time. Runs—not individual rows—are split
into train, validation, and test sets, preventing temporal siblings from
leaking across partitions. Labels are produced at the chosen future horizon
from the simulator state, while features use only information available at the
decision time. Three standard models are trained. Threshold policies can
override a denial after a configurable starvation bound.

## Reproduction

Install `requirements.txt`, edit `config.yaml`, then run
`python scripts/run_all.py`. Outputs are placed in `results/`, plots in
`results/plots/`, and models in `models/`. Run `python -m pytest -q` for the
regression suite. The CSV files are the authoritative numerical results.
