"""Experiment runner: plain GA vs GA + Wisdom of Crowds.

Usage:  python main.py puzzle.json [more.json ...] [--runs 10] [--csv woc_results.csv]
Puzzle files use the GA's format: {"n": 32, "fixed_queens": [[col, row], ...], "ga_params": {...}}
"""
import argparse
import csv
import statistics

from ga import NQueensGA, load_test_file
from woc import run_woc_ga

# compared against the plain GA
EXPERT_FRACTIONS = [0.10, 0.20, 0.30, 0.40, 0.50]
# same seeds for every method
BASE_SEED = 42                                


def run_one(solver, fraction, params, seed):
    if fraction == 0:
        result = solver.run_ga(params, seed=seed)
        result["total_evaluations"] = result["fitness_evaluations"]
        result["start_fitness"] = result["history"][0]
        return result
    return run_woc_ga(solver, fraction, params, seed)


def run_experiments(files, runs, out_csv):
    cols = ["puzzle", "n", "method", "solved", "avg_best", "min_best", "std_best",
            "avg_start", "avg_gens", "avg_ga_evals", "avg_total_evals", "avg_time_s"]
    rows = []
    print(f"{'Puzzle':<18}{'Method':<12}{'Solved':>7}{'AvgBest':>9}{'AvgStart':>9}"
          f"{'AvgGens':>8}{'TotEvals':>10}{'Time(s)':>8}")
    for path in files:
        puzzle = load_test_file(path)
        solver = NQueensGA(puzzle["n"], puzzle["fixed_queens"])
        params = puzzle.get("ga_params")
        for fraction in [0.0] + EXPERT_FRACTIONS:
            label = "GA" if fraction == 0 else f"GA+WoC {fraction:.0%}"
            res = [run_one(solver, fraction, params, BASE_SEED + r) for r in range(runs)]
            best = [x["best_fitness"] for x in res]
            row = dict(
                puzzle=path.split("/")[-1], n=solver.n, method=label,
                solved=f"{sum(x['solved'] for x in res)}/{runs}",
                avg_best=round(statistics.mean(best), 2), min_best=min(best),
                std_best=round(statistics.stdev(best), 2) if runs > 1 else 0,
                avg_start=round(statistics.mean(x["start_fitness"] for x in res), 2),
                avg_gens=round(statistics.mean(x["generations"] for x in res), 1),
                avg_ga_evals=round(statistics.mean(x["fitness_evaluations"] for x in res)),
                avg_total_evals=round(statistics.mean(x["total_evaluations"] for x in res)),
                avg_time_s=round(statistics.mean(x["runtime_s"] for x in res), 2))
            rows.append(row)
            print(f"{row['puzzle']:<18}{label:<12}{row['solved']:>7}{row['avg_best']:>9}"
                  f"{row['avg_start']:>9}{row['avg_gens']:>8}{row['avg_total_evals']:>10}"
                  f"{row['avg_time_s']:>8}", flush=True)
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Compare plain GA with GA + Wisdom of Crowds.")
    parser.add_argument("puzzles", nargs="+", help="puzzle JSON files")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--csv", default="woc_results.csv")
    args = parser.parse_args()
    run_experiments(args.puzzles, args.runs, args.csv)


if __name__ == "__main__":
    main()