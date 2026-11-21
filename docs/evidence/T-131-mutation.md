# T-131 — Mutation-testing baseline

**Date:** 2026-11-21  
**Tool:** mutmut 3.8 (`source_paths` is the renamed `paths_to_mutate`)

## What the weekly job measures

`.github/workflows/mutation.yml` mutates `src/roboprobe/selection/` and
`src/roboprobe/oracles/` (37 files, 5281 mutants on this commit) and uploads
`mutants/mutmut-cicd-stats.json` as an HTML summary. It is not a pull-request check.

`scripts/prepare_mutmut_layout.sh` copies repo data next to `backend/` because
mutmut runs pytest with cwd `backend/mutants`, which makes `Path(__file__).parents[N]`
land one directory higher than in a normal checkout.

Kill rate = (killed + timeout) / (killed + timeout + survived). Skipped mutants
are excluded. Target from the task: at least 70 %.

## Smoke baseline (not the full tree)

Filtered run of `roboprobe.selection.baselines.random.*` only, after the stats pass:

| | |
|--|--|
| killed | 22 |
| survived | 5 |
| timeout | 0 |
| kill rate | 81.5 % |

The other generated mutants were not executed in this session. The weekly workflow
is what records the full-tree rate.
