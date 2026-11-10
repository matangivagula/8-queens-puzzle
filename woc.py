import random
from ga import NQueensGA

CROWD_SIZE = 30
CROWD_GENS = 30
CROWD_POP = 50
SEED_BOARDS = 10


def build_crowd(solver, params, seed):
    # Start with GA settings, then change the settings that make each crowd member intentionally small and inexpensive to run.
    crowd_params = dict(params or {})
    crowd_params.update(max_generations=CROWD_GENS,
                        population_size=min(CROWD_POP, crowd_params.get("population_size", CROWD_POP)))
    crowd, evals = [], 0

    # Run independent searches to find the best so that they become experts
    for i in range(CROWD_SIZE):
        r = solver.run_ga(crowd_params, seed=seed * 1000 + i)
        crowd.append((r["best_fitness"], r["best_board"]))
        evals += r["fitness_evaluations"]
    return crowd, evals


def consensus_board(solver, experts, rng):
    n = solver.n

    # votes[column][row] records how many experts placed a queen in that position. 
    votes = [[0] * n for _ in range(n)]
    for _, board in experts:
        for c in solver.open_columns:
            votes[c][board[c]] += 1

    # The diagonal maps let us penalize choices that would create attacks while the remaining columns are filled.
    board = solver._board_template.copy()
    sums, diffs = {}, {}
    used_rows = set()
    for c, r in enumerate(board):
        if r is not None:
            used_rows.add(r)
            sums[c + r] = sums.get(c + r, 0) + 1
            diffs[r - c] = diffs.get(r - c, 0) + 1

    # Fill the columns the experts agree on most first. 
    columns = sorted(solver.open_columns, key=lambda c: (-max(votes[c]), rng.random()))
    for c in columns:
        best_key, best_row = None, None
        for r in solver.open_rows:
            if r in used_rows:
                continue
        # Prefer the row with the most votes, the fewest diagonal clashes, and random choice when both are tied.
            key = (-votes[c][r], sums.get(c + r, 0) + diffs.get(r - c, 0), rng.random())
            if best_key is None or key < best_key:
                best_key, best_row = key, r

        # Reserve the selected row and update the diagonal counts so later columns can avoid conflicts
        board[c] = best_row
        used_rows.add(best_row)
        sums[c + best_row] = sums.get(c + best_row, 0) + 1
        diffs[best_row - c] = diffs.get(best_row - c, 0) + 1
    return board


def wisdom_of_crowds(solver, expert_fraction, params=None, seed=0):
    if not 0 < expert_fraction <= 1:
        raise ValueError("expert_fraction must be in (0, 1]")

    # Skip WoC when there are too few movable columns to search or when the fixed queens already attack each other.
    if len(solver.open_columns) < 2 or solver._fixed_diagonal_conflict:
        return [], 0

    # Create and rank the crowd.
    crowd, evals = build_crowd(solver, params, seed)
    crowd.sort(key=lambda s: s[0])
    k = min(len(crowd), max(2, round(len(crowd) * expert_fraction)))
    experts = crowd[:k]

    # Keeps the best expert unchanged, then add several boards assembled from the experts' votes.
    rng = random.Random(seed)
    seeds = [experts[0][1]]
    seeds += [consensus_board(solver, experts, rng) for _ in range(SEED_BOARDS - 1)]

    # Validate every generated board. also checks for fixed queens and the row-permutation rule were preserved.
    for b in seeds:
        solver.score_board(b) 
    return seeds, evals


def run_woc_ga(solver, expert_fraction, params=None, seed=0):
    seeds, crowd_evals = wisdom_of_crowds(solver, expert_fraction, params, seed)
    result = solver.run_ga(params, seed=seed, initial_population=seeds)

    # Add WoC-specific metrics to distinguish the crowd's cost from main GA's cost
    result["crowd_evaluations"] = crowd_evals
    result["total_evaluations"] = crowd_evals + result["fitness_evaluations"]
    result["start_fitness"] = result["history"][0]
    return result

def run_woc(n, crowd_size=10, expert_pct=0.25, seed=0, params=None, fixed_queens=()):
    """Top-level convenience function so gui.py and external modules can call WoC directly."""
    solver = NQueensGA(n, fixed_queens)
    return run_woc_ga(solver, expert_fraction=expert_pct, params=params, seed=seed)