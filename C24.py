from ortools.sat.python import cp_model
import csv
from datetime import datetime  

carbon = 'C24'
pent_sum = 64
hex_sum = 66

file_suffix = f"{pent_sum}_{hex_sum}"

file_name = f"{carbon}_solutions_{file_suffix}.csv"
file_path = f"{carbon}_solutions_{file_suffix}.csv"

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

        # Generate a timestamp
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

        # Define 24 distinct integer variables between 1 and 24
        variables = [model.NewIntVar(1, 24, f"v{i}") for i in range(24)]

        # Enforce distinct values
        model.AddAllDifferent(variables)
        
        # Define the equations as constraints
        constraints = [
            ([19, 20, 21, 22, 23, 24], hex_sum),
            ([1, 2, 3, 4, 5, 6], hex_sum),
            ([5, 8, 15, 9, 4], pent_sum),
            ([4, 9, 16, 10, 3], pent_sum),
            ([3, 10, 17, 11, 2], pent_sum),
            ([2, 11, 18, 12, 1], pent_sum),
            ([1, 12, 13, 7, 6], pent_sum),
            ([6, 7, 14, 8, 5], pent_sum),
            ([14, 8, 15, 22, 21], pent_sum),
            ([15, 9, 16, 23, 22], pent_sum),
            ([16, 10, 17, 24, 23], pent_sum),
            ([17, 11, 18, 19, 24 ], pent_sum),
            ([18, 12, 13, 20, 19], pent_sum),
            ([13, 7, 14, 21, 20], pent_sum),
        ]



        # Add constraints to the model
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
