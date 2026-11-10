import os
import csv
import json
import statistics
import matplotlib.pyplot as plt
from ga import NQueensGA, load_test_file, run_ga
from woc import run_woc_ga, run_woc

def run_experiment_sweep(data_dir="data", out_csv="results.csv", runs=5):
    # Executes benchmark sweep across all generated JSON datasets.
    if not os.path.exists(data_dir):
        print(f"Directory '{data_dir}' not found. Run generate_data.py first.")
        return

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".json")]
    files.sort()
    cols = ["puzzle", "n", "method", "solved", "avg_best", "min_best", "std_best", "avg_gens", "avg_time_s"]
    rows = []
    print(f"Starting experiments across {len(files)} dataset files.")

    for path in files:
        with open(path, 'r') as f:
            data = json.load(f)
        n = data.get("n", 8)
        base_seed = data.get("seed", 42)
        fixed_queens = data.get("fixed_queens", [])
        solver = NQueensGA(n, fixed_queens)
        for method in ["GA", "GA and WoC"]:
            res_list = []
            for r in range(runs):
                seed = base_seed + r
                if method == "GA":
                    res = solver.run_ga(seed=seed)
                else:
                    res = run_woc_ga(solver, expert_fraction=0.25, seed=seed)
                res_list.append(res)
            best_fits = [x["best_fitness"] for x in res_list]
            solved_count = sum(1 for x in res_list if x["solved"])
            row = {
                "puzzle": os.path.basename(path),
                "n": n,
                "method": method,
                "solved": f"{solved_count}/{runs}",
                "avg_best": round(statistics.mean(best_fits), 2),
                "min_best": min(best_fits),
                "std_best": round(statistics.stdev(best_fits), 2) if runs > 1 else 0.0,
                "avg_gens": round(statistics.mean(x["generations"] for x in res_list), 1),
                "avg_time_s": round(statistics.mean(x["runtime_s"] for x in res_list), 3)
            }
            rows.append(row)
            print(
                f"[{method}] N={n} Solved: {row['solved']} Avg Best: {row['avg_best']} Avg Time: {row['avg_time_s']}s")
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nExperiment finished. Results saved to '{out_csv}'.")

if __name__ == "__main__":
    run_experiment_sweep()