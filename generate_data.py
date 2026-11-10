import json
import random
import os

def generate_test_dataset(output_dir="data", sizes=[8, 16, 32, 64, 128, 256], seeds_per_size=5):
    # generates JSON test files following the format - n: int, seed: int, description: info
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    generated_files = []
    for n in sizes:
        for trial_idx in range(seeds_per_size):
            seed_val = 1000 * n + trial_idx
            random.seed(seed_val)
            # Team schema
            data = {
                "n": n,
                "seed": seed_val,
                "description": f"N-Queens test dataset for N={n}, trial={trial_idx + 1}"
            }
            filename = os.path.join(output_dir, f"n{n}_seed{seed_val}.json")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            generated_files.append(filename)
    sample_data = {
        "n": 8,
        "seed": 42,
        "description": "Default sample dataset for quick testing and GUI demonstration"
    }
    with open("sampledata.json", "w") as f:
        json.dump(sample_data, f, indent=4)
    print(
        f"Successfully generated {len(generated_files)} dataset files in '{output_dir}/' and created 'sampledata.json'.")
if __name__ == "__main__":
    generate_test_dataset()