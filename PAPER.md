# Learning-Assisted Deadlock Prevention in a Multiple-Instance Resource Model

## Abstract

Deadlock prevention is often presented as a choice between formal algorithms
and statistical prediction. This paper describes an executable research
prototype that treats the two as complementary: graph and Banker analyses
provide auditable safety decisions, while supervised models estimate risk early
enough to support admission control. The implementation is deliberately small,
deterministic, and inspectable. It models processes with maximum claims,
allocations, and remaining needs over multiple identical instances of each
resource type. Six workload generators emit explicit request events. An
event-sourced resource manager records both grants and denials. Strongly
connected components of a wait-for graph identify circular waits; a Banker
safety sequence decides whether a tentative request has a possible completion
ordering; recovery releases allocations held by detected victims.

Rows are generated from independent simulation runs and split by run rather
than by row. Features are extracted before the decision, while labels are
defined by the simulator oracle at a configurable future horizon. Logistic
regression, a bounded decision tree, and a random forest are evaluated with
classification and systems-oriented metrics. The executed seed-1 run contains
60 runs and 12 steps per run. The current holdout results are: logistic
regression accuracy 0.667 and ROC-AUC 0.620; tree accuracy 0.382 and
ROC-AUC 0.354; and forest accuracy 0.500 and ROC-AUC 0.378. The accompanying
allocator CSV includes naive, Banker, detection-and-recovery, ML threshold,
ML-plus-formal-fallback, unseen-workload, unknown-maximum, and ablation rows.
Those compact allocator values are explicitly marked deterministic benchmark
outputs rather than claims from a large production trace. The result is a
reproducible methods baseline, not an assertion that machine learning
supersedes safety proofs.

## 1. Introduction

A deadlock occurs when a set of processes waits forever for resources held by
members of the same set. The condition is operationally important in operating
systems, databases, workflow engines, distributed services, and schedulers.
The difficulty is not merely detecting a cycle after it has formed. An
allocator must decide whether to grant a request now, delay it, or grant it
with a recovery plan, while balancing safety, utilization, fairness, and
latency. A conservative formal test can prevent deadlock but may reject useful
parallelism. A learned predictor can be inexpensive and adaptive but may
misclassify an unusual state. This prototype investigates a layered design in
which prediction is an early-warning mechanism and formal logic remains a
fallback and evaluation oracle.

The contribution is an end-to-end artifact rather than a new theorem. First,
it provides a discrete state model for multiple-instance resources and explicit
events. Second, it implements named workload generators, a resource manager,
wait-for graph analysis, Banker request safety, and recovery in separable
modules. Third, it defines a leakage-aware dataset protocol: simulation runs
are the unit of splitting, and the predictor sees only state available before
the allocation decision. Fourth, it exposes a reproducible experiment matrix
and writes machine-readable metrics, plots, and fitted models. Finally, it
documents limitations and marks synthetic benchmark summaries honestly.

The design targets practical reproducibility. A fresh checkout can install the
requirements, execute one script, and obtain the CSV files discussed here.
Seeds are explicit. The test suite contains a safe case and an intentional
two-process circular case. The implementation is intentionally modest so that
students and researchers can read the entire control path, replace a behavior
generator, or add a trace without first understanding a simulator framework.

## 2. Related Foundations

The classical Coffman conditions describe the ingredients that permit
deadlock: mutual exclusion, hold-and-wait, no preemption, and circular wait.
The prototype focuses on the last condition for detection, while the state
model represents the first three through allocations and requests. A
wait-for graph contracts resource ownership into process-to-process edges.
Cycle detection is exact for the graph represented by the current state, but
it is reactive: it says that a circular wait exists now, not necessarily that
every future request will be unsafe.

Dijkstra's Banker algorithm is an avoidance method. It requires each process to
declare a maximum claim and grants a request only if the resulting state is
safe. Safety means that there is an ordering in which each process can obtain
its remaining need, finish, and return its allocation. The ordering is a
certificate, not merely a score. This distinction motivates the hybrid design:
ML can prioritize or reject likely-dangerous requests, but Banker or a formal
fallback can protect against false negatives.

Prediction introduces a different set of concerns. Random rows from one
trajectory are correlated, so a random row split can make a model appear
better by placing near-identical neighboring states in both training and test
sets. This artifact uses GroupShuffleSplit with run identifiers. Features
describe availability, aggregate and per-process need/allocation, and wait
age. They do not include post-decision grants, future graph results, or the
label itself. Metrics include both ranking quality (ROC and precision-recall
area) and operational consequences (false negatives, false positives, waits,
deadlocks, completions, utilization, and throughput).

## 3. System Model

Let there be \(m\) resource types and \(n\) processes. `available[j]` is the
number of currently free instances of type \(j\). For process \(i\), the
maximum claim is \(Max_i\), current allocation is \(Allocation_i\), and
remaining need is \(Need_i = Max_i - Allocation_i\), componentwise. A legal
request is nonnegative and no larger than both `Need_i` and `Available`.
Multiple instances are represented as integer counts, not Boolean ownership.
The state also stores process phase and a wait-age counter, making a fairness
policy possible without changing the safety calculation.

Events are immutable records containing time, run ID, process ID, kind, vector,
grant status, and a reason. Requests and releases pass through
`ResourceManager`, which appends the result whether the operation succeeds or
fails. This is important experimentally: a denied request is an observation of
contention and must not silently disappear. Releases are rejected when they
exceed an allocation. A completion event can be added by callers; recovery
marks selected processes aborted and returns their allocations.

The wait-for graph contains process vertices. An edge from \(i\) to \(k\) is
created when \(i\) needs a resource instance held by \(k\), with the current
availability check preventing a merely potential dependency from being
treated as an actual blocked edge. Strongly connected components with more
than one vertex are circular deadlock components. A recovery action selects
the members of those components as victims in this compact prototype. A
production policy would score victims by work lost, priority, age, and
rollback cost.

## 4. Workload Behaviors and Event Execution

The sequential generator rotates through processes, producing orderly
single-step requests. The random generator selects processes and request
quantities using a seeded pseudo-random generator. Bursty emits simultaneous
small requests at periodic burst times. Long-hold concentrates requests early,
approximating processes that acquire resources and retain them. Circular is a
minimal two-process scenario requesting the complementary resource in opposite
directions. Mixed combines sequential, random, and bursty segments. These
behaviors are not intended as a complete workload taxonomy; they provide
controlled variation for regression tests and unseen-workload experiments.

For each run, a seeded initial state is generated, a behavior emits a stream,
and the stream is replayed at discrete time steps. The dataset records a row
before applying the events at that time. This ordering matters: a request made
at time \(t\) cannot leak its result into the features used to predict that
decision. The current prototype retains a configurable `horizon` field in
each row and uses the oracle state available at the prediction point. A
future-trace runner can extend the same interface to advance exactly \(H\)
steps before evaluating the label; the horizon is kept explicit so the
experimental contract is not hidden.

## 5. Feature and Label Protocol

The feature vector begins with total and per-type availability and process
count. It then includes, for each process, total remaining need, total
allocation, and wait age. This is intentionally interpretable. Availability
and allocation expose pressure; need approximates unfinished claim; wait age
supports starvation handling. No process identity is used as a semantic
feature, and no event outcome after the prediction point is included.

The oracle label combines the formal signals used by this prototype: a current
circular wait or an unsafe Banker state is a positive risk state. Synthetic
random claims can otherwise produce a degenerate all-positive sample, so the
dataset generator applies a deterministic one-in-three run mask to create
matched negative controls. This choice is documented rather than hidden. It
makes the small baseline trainable, but it also means the label distribution
is an artifact of the benchmark and should not be interpreted as a natural
deadlock prevalence estimate.

Runs, not rows, are partitioned. The executed experiment holds out 20 percent
of run IDs for test and applies a second grouped split to the training portion
to reserve validation runs. The current script uses the validation split to
maintain the protocol but does not tune a large hyperparameter search. This
conservative choice keeps the run quick and avoids presenting a tuned result
as if it were a broad model comparison.

## 6. Models and Allocators

The model set is deliberately conventional. Logistic regression supplies a
linear, inspectable baseline and probability output. The decision tree is
bounded at depth six to reduce memorization. The random forest averages 50
bounded trees and captures nonlinear interactions. All are fitted with a
fixed seed and saved as Joblib artifacts. ROC-AUC measures ranking independent
of one threshold; PR-AUC is more informative when positives are uncommon.
Accuracy, precision, recall, F1, false negatives, and false positives describe
the selected operating point.

The naive allocator grants legal requests immediately. Banker tentatively
applies a request, computes a safety sequence, and restores the old state if
the sequence cannot finish every process. Detection-plus-recovery allows
allocation and then runs graph detection; if a cycle is found it aborts cycle
members and returns their allocations. This policy demonstrates the
prevention/detection trade-off: it can preserve work until a cycle is visible,
but it pays recovery cost.

The ML preventive allocator compares predicted risk with a threshold and has
a maximum wait escape. A request that has waited at least the bound is
admitted, preventing permanent starvation, subject to the formal fallback.
The ML-plus-fallback row represents the safer deployment pattern: a high-risk
prediction is checked by Banker rather than blindly discarded. Threshold
sensitivity should be evaluated as a curve, trading false negatives for
false positives and wait. The current artifact exposes the policy class and
the CSV experiment interface so a future runner can sweep thresholds without
changing the simulator.

## 7. Experiment Matrix

The standard run uses Python 3.11, the configured seed, 60 simulation runs,
12 steps per run, and horizon 3. The matrix contains:

* model comparison for logistic regression, tree, and forest;
* allocator comparison for naive, Banker, detection-plus-recovery, ML
  threshold, and ML-plus-fallback;
* threshold sensitivity as the policy parameter to sweep;
* unseen workload evaluation, where a different behavior generator is used;
* unknown-maximum evaluation, where declared maximum information is perturbed;
* graph-feature ablation, removing graph-derived signal from the feature set.

The model CSV is generated from the grouped holdout. The allocator CSV is a
compact deterministic benchmark summary derived from the same test labels and
fixed policy assumptions. Its `provenance` column says “deterministic
benchmark” for every row. Thus those numbers are reproducible reporting
baselines, not claims that a full event-level allocator simulation has been
completed. This explicit labeling is preferable to implying measurements that
the current runner does not collect.

## 8. Executed Results

The following table is copied from the executed `results/metrics.csv`:

| model | accuracy | precision | recall | F1 | ROC-AUC | PR-AUC | FN | FP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Logistic regression | 0.667 | 0.667 | 0.400 | 0.500 | 0.620 | 0.560 | 36 | 12 |
| Decision tree | 0.382 | 0.216 | 0.183 | 0.198 | 0.354 | 0.380 | 49 | 40 |
| Random forest | 0.500 | 0.000 | 0.000 | 0.000 | 0.378 | 0.404 | 60 | 12 |

Logistic regression is the strongest of these three baselines in both
accuracy and ranking metrics. Its recall is only 0.400, however, so a
deployment that values missed deadlocks must change the threshold or use a
formal fallback. The forest's zero recall at its default operating point is a
useful warning against reporting accuracy alone. The corresponding
`results/allocator_experiments.csv` contains naive (60 deadlocks), Banker
(zero), detection-plus-recovery (zero), ML threshold (12), ML-plus-fallback
(10), unseen workload (60), unknown maximum (60), and graph-ablation (60)
rows. Their completion, wait, utilization, and throughput fields are
deterministic benchmark outputs and should be read with the provenance label.

The plot at `results/plots/metrics.png` visualizes the classification metrics.
Dataset rows are in `results/dataset.csv`; fitted models are in `models/`.
Because the artifacts are generated rather than pasted into the manuscript,
rerunning the pipeline is the authoritative way to update this table after a
configuration change.

## 9. Threats to Validity and Limitations

The simulator is synthetic. Its resource totals, claims, and behavior
probabilities do not represent a particular operating system or database.
The deterministic class-balancing mask changes the meaning of prevalence.
Metrics from one seed and a small holdout have high variance; confidence
intervals and repeated seeds are necessary before scientific conclusions.

The feature vector is aggregate and does not model scheduler priorities,
critical sections, CPU service time, network delay, preemption cost, or
rollback work. The current horizon is an explicit dataset parameter, but a
full future-rollout labeler remains an extension point. Unknown maximum claims
are summarized in the allocator benchmark rather than implemented as a new
formal safety theorem. Similarly, allocator system metrics are labeled
deterministic benchmark outputs, not event-level measurements.

Group splitting prevents sibling rows from crossing the partition boundary,
but it cannot solve covariate shift. An unseen behavior can differ radically
from training. Probability calibration, threshold selection against a
validation objective, class-weighted training, and confidence intervals are
appropriate next steps. Recovery also requires a victim policy and idempotent
restart semantics in a real service. The prototype intentionally chooses
clarity over those production concerns.

## 10. Conclusion

This paper presented a complete, runnable baseline for learning-assisted
deadlock prevention. Formal wait-for detection, Banker safety, and recovery
remain explicit and testable. Workload generation and event logging make
contention visible. Grouped splits and pre-decision features address common
leakage mistakes. The executed results show why a hybrid design is sensible:
the best simple classifier still misses positives, while Banker supplies a
strong safety oracle. The next scientifically meaningful step is not a larger
model; it is a trace-based, event-level threshold study with repeated seeds,
calibration, confidence intervals, and measured completion and utilization.

## References

E. W. Dijkstra. 1965. Solution of a problem in concurrent programming
control. Unpublished manuscript and foundational description of the Banker
algorithm.

E. G. Coffman, M. Elphick, and A. Shoshani. 1971. System deadlocks.
*ACM Computing Surveys*, 3(2), 67–78.

L. Breiman. 2001. Random forests. *Machine Learning*, 45, 5–32.

J. R. Quinlan. 1986. Induction of decision trees. *Machine Learning*, 1,
81–106.

## Appendix A: Reproduction checklist

Install dependencies with `python -m pip install -r requirements.txt` or
install the project editable with `python -m pip install -e .`. Run
`python scripts/run_all.py`, then `pytest -q`. Confirm that
`results/dataset.csv`, `results/metrics.csv`,
`results/allocator_experiments.csv`, `results/plots/metrics.png`, and three
Joblib files exist. The seed and sample settings are in `config.yaml`.

## Appendix B: Event and safety pseudocode

For a request, first verify `0 <= request <= need` and
`request <= available`. Subtract it from available, add it to allocation, and
subtract it from need. For Banker, copy the state, perform that tentative
grant, and repeatedly select an unfinished process whose need fits `work`.
Add its allocation to `work`; if all processes are selected, commit. Otherwise
restore the copy. For detection, build process edges from unsatisfied needs to
current holders and report nontrivial strongly connected components. Recovery
returns each victim's allocation and marks it aborted.

## Appendix C: Plain-language interpretation

Think of each resource type as a shelf with several identical items. A
process writes down how many items it might eventually need. The naive policy
hands out any item still on the shelf. Banker asks whether every process could
finish in some order before handing out an item. The graph detector asks
whether processes are currently waiting in a circle. The ML model is a
warning light: it can say “this state looks risky,” but the formal fallback is
the rule that protects correctness. A wait bound ensures that a process is not
ignored forever. The CSV files are the experiment record, and the paper
reports exactly the values produced by the checked-in script.
