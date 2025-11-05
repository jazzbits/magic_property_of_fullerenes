from ortools.sat.python import cp_model
import csv
from datetime import datetime  

fullerene = 'C26'
pent_sum = 66
hex_sum = 87

file_suffix = f"{pent_sum}_{hex_sum}"

file_name = f"solutions_{fullerene}_{file_suffix}.csv"
file_path = f"solutions_{fullerene}_{file_suffix}.csv"

class AllSolutionsCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, csv_writer):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.csv_writer = csv_writer
        self.solution_number = 0

        # Write CSV header 
        header = ["Solution #", "Timestamp"] + [f"v{i+1}" for i in range(len(variables))]
        self.csv_writer.writerow(header)

    def on_solution_callback(self):
        solution = tuple(self.Value(var) for var in self.variables)
        self.solution_number += 1

        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Print solution 
        print(f"[{file_suffix}_{timestamp}] ✅ Solution {self.solution_number}: {solution}")

        # Write solution to CSV 
        self.csv_writer.writerow([self.solution_number, timestamp] + list(solution))

    def print_summary(self):
        print(f"\n✅ Total Solutions Found: {self.solution_number}")

def find_all_solutions():
    # Create CSV file to store solutions
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)

        # Create the model
        model = cp_model.CpModel()

        # Define 26 distinct integer variables between 1 and 26
        variables = [model.NewIntVar(1, 26, f"v{i+1}") for i in range(26)]

        # Enforce distinct values
        model.AddAllDifferent(variables)

        constraints = [
            # Hexagons
            ([5, 6, 7, 16, 17, 18], hex_sum),
            ([8, 9, 10, 11, 20, 21], hex_sum),
            ([12, 13, 14, 15, 23, 24], hex_sum),

            # Pentagons
            ([1, 2, 4, 5, 6], pent_sum),
            ([1, 2, 3, 10, 9], pent_sum),
            ([1, 6, 7, 8, 9], pent_sum),
            ([17, 18, 19, 25, 26], pent_sum),
            ([7, 8, 18, 19, 20], pent_sum),
            ([19, 20, 21, 22, 26], pent_sum),
            ([11, 12, 21, 22, 23], pent_sum),
            ([3, 10, 11, 12, 13], pent_sum),
            ([2, 3, 4, 13, 14], pent_sum),
            ([4, 5, 14, 15, 16], pent_sum),
            ([15, 16, 17, 24, 25], pent_sum),
            ([22, 23, 24, 25, 26], pent_sum),
        ]

        for indices, value in constraints:
            model.Add(sum(variables[i - 1] for i in indices) == value)

        # Create the solver
        solver = cp_model.CpSolver()
        
        # Solution collector with CSV writer
        solution_collector = AllSolutionsCollector(variables, csv_writer)

        # Set solver to enumerate all solutions
        solver.parameters.enumerate_all_solutions = True

        # Print statement 
        print(f"\n🔄 [{file_suffix}] Solver is working... Please wait for solutions.")

        # Solve and collect solutions
        solver.Solve(model, solution_collector)

        # Print summary
        solution_collector.print_summary()

if __name__ == "__main__":
    find_all_solutions()
    print(f"\n✅ Solutions have been written to '{file_name}'")


