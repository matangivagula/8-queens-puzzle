# N-Queens GA + WoC: Team Plan

Nov 4, 2026 · @Varshine

## Overview

We solve N-Queens (N = 8 to 256) with a genetic algorithm (GA), then combine many GA runs with Wisdom of Crowds (WoC). Each person writes the report and presentation sections for their own part.

| Deliverable | Due | Notes |
| --- | --- | --- |
| Code + GUI | Nov 9, 2026 | Well-commented; must run on a new dataset for a demo |
| Presentation | Nov 12, 2026 | Built from experiment results |
| Paper | Nov 23, 2026 | 9–10 pages, GUI snapshots included |

### Shared contracts (agree today, before coding)

- **Language:** Python (one repo, one `main.py` entry point)
- **Representation:** list `board` of length N, where `board[c] = r` (column c holds a queen in row r). A permutation, so rows and columns never clash.
- **Fitness:** number of attacking diagonal pairs; 0 = solved. Compute in O(N) using counts on `r+c` and `r-c` diagonals.
- **GA output:** `run_ga(n, params, seed) -> dict` with `best_board`, `best_fitness`, `history` (best fitness per generation), `runtime_s`
- **Test file format:** JSON with `n`, `seed`, and optional `initial_population`
- **Results format:** CSV, one row per run: `n, method, crowd_size, seed, best_fitness, solved, generations, runtime_s`
- **Seeds:** fixed and logged, so every result can be reproduced

## Audrey: Genetic Algorithm Code

Owns `ga.py`: a GA that any N from 8 to 256 can call, returning the dict in the shared contract.

**Code tasks**

- [ ] Random permutation initialization (seeded)
- [ ] O(N) fitness function using diagonal counters
- [ ] Selection: tournament (size 3–5)
- [ ] Crossover: PMX or order crossover (both keep permutations valid; reuse from the TSP project)
- [ ] Mutation: swap two columns; optional min-conflicts local repair
- [ ] Elitism: keep the top 1–5% each generation
- [ ] Stop at fitness 0 or a generation cap
- [ ] Log best fitness per generation in `history`
- [ ] Tune default params per N (population, mutation rate, generation cap)
- [ ] Comment every function

**Hand-off:** working `run_ga()` to Person 2 and Person 3 by end of Friday.

**Report and presentation**

- Problem definition: N-Queens, why the general problem is NP-complete, search space size (N!)
- Representation and fitness function, with the formula
- GA operators and the parameter values chosen, with reasons

## Varshine: Wisdom of Crowds + Integration

Owns `woc.py` and `main.py`: builds the crowd from GA runs, aggregates it into one solution, and wires GA → WoC → results → GUI.

**Code tasks**

- [ ] Run the GA `k` times (crowd size 10–20) with different seeds; keep each run's best board as an "expert"
- [ ] Optionally keep only the top X% of experts by fitness
- [ ] Agreement matrix: `A[c][r]` = how many experts put column c's queen in row r
- [ ] Consensus build: assign rows greedily by highest agreement, skipping rows already used (keeps a permutation)
- [ ] Repair step: min-conflicts or a short GA seeded with the WoC board, to remove leftover diagonal clashes
- [ ] `run_woc(n, crowd_size, seed) -> dict` matching the GA output format
- [ ] `main.py`: load a test file, run GA and GA+WoC, write a row to the results CSV, pass boards to the GUI
- [ ] Build against dummy GA output until Person 1 hands off

**Hand-off:** full pipeline running end to end by Saturday.

**Report and presentation**

- WoC concept and how it applies to N-Queens
- Aggregation method with a small worked example (N = 8)
- Comparison of GA-only vs. GA+WoC, using Person 3's results

## Matangi: Test Data + Experiments + GUI

Owns `generate_data.py`, `experiments.py`, and `gui.py`: creates the datasets, runs every experiment, and shows the solutions visually.

**Test data**

- [ ] Generator writes JSON test files for N = 8, 16, 32, 64, 128, 256 with fixed seeds
- [ ] Document the file format and how it was generated (the assignment requires this in the report)

**Experiments** (check the Project 5 requirements and match them)

| Experiment | Varies | Fixed |
| --- | --- | --- |
| GA vs. GA+WoC | method, N = 8 to 256 | crowd size, GA params |
| Crowd size | k = 5, 10, 20 | N = 64, 128 |
| Expert filtering | top 25%, 50%, 100% of crowd | N = 128 |
| Scalability | N = 8 to 256 | default params |

- [ ] 5–10 seeded trials per setting; report mean and standard deviation
- [ ] Metrics: best fitness, success rate (fitness 0), generations to solve, runtime
- [ ] Plots: runtime vs. N, success rate vs. N, GA convergence curves, GA vs. WoC fitness
- [ ] Cap generations so the full sweep finishes in under a few hours

**GUI** (Python Tkinter or Pygame)

- [ ] Board view with queens drawn and attacking pairs highlighted in red
- [ ] Scale cells down for large N; use a conflict heatmap at N = 128 and 256
- [ ] Side-by-side view: best GA board vs. WoC board
- [ ] Convergence graph (best fitness per generation)
- [ ] Controls: choose N, crowd size, and seed, then click Run
- [ ] Save screenshots for the report

**Report and presentation**

- Test data generation and format
- Experimental setup, results tables, plots, and analysis
- GUI description with snapshots

## Timeline

1. **Wed 11/4:** Agree on the shared contracts, set up the repo, brainstorm.
2. **Thu–Sat 11/5–11/7:** P1 builds the GA, P2 builds WoC on dummy data, P3 builds the generator and GUI skeleton. GA hand-off Friday.
3. **Sun 11/8:** Integrate GA → WoC → GUI; full pipeline runs.
4. **Sun 11/8:** P3 runs the full experiment sweep; everyone fixes bugs and finishes comments. Everyone writes the report.
5. **Mon 11/9:** Submit code.
6. **11/10–11/12:** Each person builds their slides; submit the presentation 11/12.
7. **11/13–11/23:** Each person writes their paper sections; merge, edit, and submit the paper 11/23.

## Report Outline (9–10 pages)

| Section | Owner | Pages |
| --- | --- | --- |
| Abstract + Introduction | All | 1 |
| Problem: N-Queens and NP-completeness | Person 1 | 1.5 |
| GA approach | Person 1 | 1.5 |
| WoC approach | Person 2 | 1.5 |
| Test data generation | Person 3 | 1 |
| Experiments + results | Person 3 | 2 |
| GA vs. WoC discussion | Person 2 | 1 |
| GUI + snapshots | Person 3 | 0.5 |
| Conclusion + references | All | 0.5 |

**Open question:** check the Project 5 assignment for any required experiments not listed here.
