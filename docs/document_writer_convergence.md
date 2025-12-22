# Writer Convergence and Termination

This document defines convergence and termination semantics for Writer. It is declarative only; no runtime changes are introduced.

## A. Definition of Convergence

- A Writer task converges only when the Critic returns `ACCEPT`.
- Convergence is binary: either ACCEPT or not; no partial acceptance exists.
- Once ACCEPT is returned, no further refinement is requested and the output is final and immutable for that task.
- Only the Critic can declare convergence.

## B. Bounded Retry Guarantee

- Writer execution is bounded by a finite retry limit `N`.
- Each retry is a full draft or refine attempt.
- Retry limits are enforced by the controller / dispatcher, not by Writer logic itself.
- Exceeding the retry limit terminates the attempt; no escalation or silent continuation occurs.

## C. Termination Conditions

- **Accepted**: Critic returns ACCEPT; output is final.
- **Rejected (Non-Convergent)**: Retry limit exceeded without an ACCEPT; no acceptable output produced.
- **Invalid Execution**: Schema or protocol violations halt execution. Silent continuation is forbidden.

## D. Responsibility Boundaries

- Writer does not track retry counts, decide when to stop, or handle global failure.
- Termination decisions belong to the controller / dispatcher and the application orchestration layer.
- Writer correctness is local to a single task attempt.

## E. Non-Goals

- Writer does not guarantee quality beyond critic acceptance.
- Writer does not enforce stylistic consistency across sections.
- Writer does not ensure global document coherence or optimality.
- Convergence concerns protocol completion, not perfection.
