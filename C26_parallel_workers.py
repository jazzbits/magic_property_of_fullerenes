#!/usr/bin/env python3
from ortools.sat.python import cp_model
import csv
from datetime import datetime
import multiprocessing as mp
import os
import pandas as pd

# ==============================================================
# Configuration
# ==============================================================

fullerene = 'C26'
pent_sum = 67
hex_sum = 83
file_suffix = f"{pent_sum}_{hex_sum}"

WORK_DIR = r"YOUR_WORKING_DIRECTORY_PATH"
CSV_DIR = os.path.join(WORK_DIR, "csv")
os.makedirs(CSV_DIR, exist_ok=True)

# ==============================================================
# Collector class
# ==============================================================

class AllSolutionsCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, csv_writer, fixed_v1):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.csv_writer = csv_writer
        self.solution_number = 0
        self.fixed_v1 = fixed_v1

        # CSV header
        header = ["Solution #", "Timestamp"] + [f"v{i+1}" for i in range(len(variables))]
        self.csv_writer.writerow(header)

    def on_solution_callback(self):
        solution = tuple(self.Value(var) for var in self.variables)
        self.solution_number += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [v1={self.fixed_v1}] Solution {self.solution_number}: {solution}")
        self.csv_writer.writerow([self.solution_number, timestamp] + list(solution))

# ==============================================================
# Worker function
# ==============================================================

def solve_fixed_v1(v1_value):
    file_name = f"solutions_C26_{file_suffix}_v1_{v1_value}.csv"
    file_path = os.path.join(CSV_DIR, file_name)

    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        model = cp_model.CpModel()

        variables = [model.NewIntVar(1, 26, f"v{i+1}") for i in range(26)]
        model.AddAllDifferent(variables)
        model.Add(variables[0] == v1_value)

        constraints = [
            ([5,6,7,16,17,18], hex_sum),
            ([8,9,10,11,20,21], hex_sum),
            ([12,13,14,15,23,24], hex_sum),
            ([1,2,4,5,6], pent_sum),
            ([1,2,3,10,9], pent_sum),
            ([1,6,7,8,9], pent_sum),
            ([17,18,19,25,26], pent_sum),
            ([7,8,18,19,20], pent_sum),
            ([19,20,21,22,26], pent_sum),
            ([11,12,21,22,23], pent_sum),
            ([3,10,11,12,13], pent_sum),
            ([2,3,4,13,14], pent_sum),
            ([4,5,14,15,16], pent_sum),
            ([15,16,17,24,25], pent_sum),
            ([22,23,24,25,26], pent_sum),
        ]

        for indices, value in constraints:
            model.Add(sum(variables[i - 1] for i in indices) == value)

        solver = cp_model.CpSolver()
        solver.parameters.enumerate_all_solutions = True

        collector = AllSolutionsCollector(variables, csv_writer, v1_value)
        solver.Solve(model, collector)

        return (v1_value, collector.solution_number, file_path)

def merge_and_check_unique():
    print("\n🔄 Merging all worker CSV files...")

    # Collect CSV files in the directory
    csv_files = [os.path.join(CSV_DIR, f) for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    if not csv_files:
        print("⚠️ No CSV files found in:", CSV_DIR)
        return

    # Load and merge all CSVs
    df_list = []
    for file in csv_files:
        df = pd.read_csv(file)
        df["source_file"] = os.path.basename(file)
        df_list.append(df)

    combined = pd.concat(df_list, ignore_index=True)

    # Save combined file
    combined_file = os.path.join(WORK_DIR, f"solutions_{fullerene}_{file_suffix}_combined.csv")
    combined.to_csv(combined_file, index=False)

    print(f"✅ Combined CSV saved: {combined_file}")
    print(f"Total solutions (including possible duplicates): {len(combined)}")

    # Drop duplicates based on all variable columns (ignore Solution#/Timestamp/source)
    variable_cols = [col for col in combined.columns if col.startswith("v")]
    unique = combined.drop_duplicates(subset=variable_cols)
    duplicate_count = len(combined) - len(unique)

    print(f"Unique solutions: {len(unique)}")
    print(f"Duplicate solutions: {duplicate_count}")

    # Optionally, save unique-only file
    unique_file = os.path.join(WORK_DIR, f"solutions_{fullerene}_{file_suffix}_unique.csv")
    unique.to_csv(unique_file, index=False)
    print(f"✅ Unique solutions saved: {unique_file}")

# ==============================================================
# Main function
# ==============================================================

def main():
    print(f"\n🔄 Parallel solver started using {os.cpu_count()} CPU cores.")
    print("Each core handles a unique fixed value of v1 (1–26).")

    with mp.Pool(processes=min(26, os.cpu_count())) as pool:
        results = pool.map(solve_fixed_v1, range(1, 27))

    total = sum(r[1] for r in results)
    print(f"\n✅ Total Solutions Found: {total}")
    print("Partial results saved under:", CSV_DIR)

if __name__ == "__main__":
    mp.freeze_support()
    main()
    merge_and_check_unique()
    # ==========================================
    # Write 'done' text file at the end
    # ==========================================
    done_file = os.path.join(WORK_DIR, "DONE.txt")
    with open(done_file, "w") as f:
        f.write("Search space has been fully exhausted.\n")
        f.write("All solver workers completed.\n")
        f.write("All CSV files merged.\n")
        f.write("Program finished successfully.\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n🟩 DONE file created: {done_file}")
