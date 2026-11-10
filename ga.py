import argparse
import json
import random
import time
from dataclasses import dataclass
from operator import itemgetter


@dataclass(frozen=True)
class GASettings:
    #The default GA parameters
    population_size: int = 100 #100 candidate boards in each gen
    max_generations: int = 500 #Stop after at most 500 gens
    mutation_rate: float = 0.2 #Each new child board will have 20% chance of having 2 moveable queens swap rows
    tournament_size: int = 5 #To select parent randomly sample 5 boards
    elites: int = 2 #Carry 2 best boards into next gen

    def __post_init__(self):
        #Settings that would leave the GA unable to run
        for name in ("population_size", "max_generations", "tournament_size", "elites"):
            if type(getattr(self, name)) is not int:
                raise ValueError(f"{name} must be an integer.")
        if self.population_size < 2 or self.max_generations < 0:
            raise ValueError("population_size must be at least 2 and max_generations nonnegative.")
        if not 1 <= self.tournament_size <= self.population_size:
            raise ValueError("tournament_size must be between 1 and population_size.")
        if not 0 <= self.elites < self.population_size:
            raise ValueError("elites must be nonnegative and smaller than population_size.")
        if type(self.mutation_rate) not in (int, float) or not 0 <= self.mutation_rate <= 1:
            raise ValueError("mutation_rate must be between 0 and 1.")


class NQueensGA:
#Solve one puzzle repeatedly with different seeds or GA settings
    def __init__(self, n, fixed_queens):
        #Set up the fixed board and the rows and columns the GA can change
        if type(n) is not int or n < 1:
            raise ValueError("n must be a positive integer.")

        self.n = n
        self._board_template = [None] * n
        used_rows = set()
        used_sums = set()
        used_differences = set()
        self._fixed_diagonal_conflict = False
        for square in fixed_queens:
            if not isinstance(square, (list, tuple)) or len(square) != 2:
                raise ValueError("Each fixed queen must be a [column, row] pair.")
            column, row = square
            if any(type(index) is not int or not 0 <= index < n for index in square):
                raise ValueError("Fixed queen coordinates must be integers between 0 and n - 1.")
            if self._board_template[column] is not None or row in used_rows:
                raise ValueError("Fixed queens must occupy distinct columns and rows.")
            if column + row in used_sums or row - column in used_differences:
                self._fixed_diagonal_conflict = True
            self._board_template[column] = row
            used_rows.add(row)
            used_sums.add(column + row)
            used_differences.add(row - column)

        self.open_columns = tuple(c for c in range(n) if self._board_template[c] is None)
        self.open_rows = tuple(r for r in range(n) if r not in used_rows)

    def _expand_board(self, movable_rows):
       #Combine the movable queen positions with the fixed queens to build the full board
        board = self._board_template.copy()
        for column, row in zip(self.open_columns, movable_rows):
            board[column] = row
        return board

    def _encode_seed_board(self, board):
        #Validate a full board from WoC, then keep only its movable rows
        if (
            len(board) != self.n
            or any(type(row) is not int for row in board)
            or set(board) != set(range(self.n))
        ):
            raise ValueError("Each initial board must be a full permutation of rows 0 to n - 1.")
        for column, fixed_row in enumerate(self._board_template):
            if fixed_row is not None and board[column] != fixed_row:
                raise ValueError("Initial boards must preserve all fixed queens.")
        return [board[column] for column in self.open_columns]

    def _count_conflicts(self, board):
        #Count diagonal attacking pairs in O(N), including fixed queens
        sum_counts = [0] * (2 * self.n - 1)
        difference_counts = [0] * (2 * self.n - 1)
        conflicts = 0
        for column, row in enumerate(board):
            diagonal_sum = column + row
            diagonal_difference = row - column + self.n - 1
            #Each earlier queen on either diagonal contributes one new pair
            conflicts += sum_counts[diagonal_sum] + difference_counts[diagonal_difference]
            sum_counts[diagonal_sum] += 1
            difference_counts[diagonal_difference] += 1
        return conflicts

    def score_board(self, board):
        #Check a full board against the puzzle and return its diagonal conflicts
        self._encode_seed_board(board)
        return self._count_conflicts(board)

    @staticmethod
    def _order_crossover(parent1, parent2, rng):
        #Keep a slice from parent 1 and fill gaps in parent 2's order
        start, end = sorted(rng.sample(range(len(parent1)), 2))
        segment = parent1[start:end + 1]
        used_rows = set(segment)
        remaining = [row for row in parent2 if row not in used_rows]
        return remaining[:start] + segment + remaining[start:]

    @staticmethod
    def _swap_mutation(chromosome, rng):
        #Swap two rows assigned to movable columns
        i, j = rng.sample(range(len(chromosome)), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

    def run_ga(self, params=None, *, seed=None, initial_population=()):
        settings = GASettings(**(params if params is not None else {}))
        rng = random.Random(seed)
        started = time.perf_counter()
        population = [self._encode_seed_board(board) for board in initial_population]
        if len(population) > settings.population_size:
            raise ValueError("initial_population cannot exceed population_size.")

        while len(population) < settings.population_size:
            population.append(rng.sample(self.open_rows, len(self.open_rows)))

        #Store each score beside its chromosome so elites keep their scores.
        by_fitness = itemgetter(0)
        scored = [(self._count_conflicts(self._expand_board(rows)), rows) for rows in population]
        evaluations = len(scored)
        best_fitness, best_rows = min(scored, key=by_fitness)
        history = [best_fitness]

        #Zero or one movable column leaves exactly one possible permutation.
        can_search = len(self.open_columns) >= 2 and not self._fixed_diagonal_conflict
        for _ in range(settings.max_generations):
            if best_fitness == 0 or not can_search:
                break

            scored.sort(key=by_fitness)
            next_generation = scored[:settings.elites]
            while len(next_generation) < settings.population_size:
                parent1 = min(rng.sample(scored, settings.tournament_size), key=by_fitness)[1]
                parent2 = min(rng.sample(scored, settings.tournament_size), key=by_fitness)[1]
                child = self._order_crossover(parent1, parent2, rng)
                if rng.random() < settings.mutation_rate:
                    self._swap_mutation(child, rng)
                fitness = self._count_conflicts(self._expand_board(child))
                next_generation.append((fitness, child))
                evaluations += 1

            scored = next_generation
            current_fitness, current_rows = min(scored, key=by_fitness)
            if current_fitness < best_fitness:
                best_fitness, best_rows = current_fitness, current_rows
            history.append(best_fitness)

        if best_fitness == 0:
            status = "solved"
        elif not can_search:
            status = "proven_unsolvable"
        else:
            status = "budget_exhausted"

        return {
            "best_board": self._expand_board(best_rows),
            "best_fitness": best_fitness,
            "history": history,
            "runtime_s": time.perf_counter() - started,
            "solved": best_fitness == 0,
            "status": status,
            "generations": len(history) - 1,
            "fitness_evaluations": evaluations,
        }


def load_test_file(filename):
    #Load a puzzle JSON object for the command line or the experiment runner."""
    with open(filename, encoding="utf-8") as file:
        puzzle = json.load(file)
    if not isinstance(puzzle, dict) or not {"n", "fixed_queens"} <= puzzle.keys():
        raise ValueError("The test file must contain an object with n and fixed_queens.")
    if not isinstance(puzzle["fixed_queens"], list):
        raise ValueError("fixed_queens must be a list of [column, row] pairs.")
    return puzzle


def main():
    #Run GA from the command line and print the result as JSON
    parser = argparse.ArgumentParser(description="Run the N-Queens Completion genetic algorithm.")
    parser.add_argument("test_file", help="Path to the puzzle JSON file.")
    args = parser.parse_args()

    try:
        puzzle = load_test_file(args.test_file)
        solver = NQueensGA(puzzle["n"], puzzle["fixed_queens"])
        result = solver.run_ga(
            params=puzzle.get("ga_params"),
            seed=puzzle.get("seed"),
            initial_population=puzzle.get("initial_population", ()),
        )
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()