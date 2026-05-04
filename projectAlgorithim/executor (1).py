"""
Algorithm Executor
Safely executes user-provided code in a restricted namespace and measures runtime.
"""

import time
import copy
import traceback


class AlgorithmExecutor:
    """
    Compiles and runs the user's algorithm, injecting an `arr` variable
    and measuring wall-clock execution time.
    """

    SAFE_BUILTINS = {
        "len": len, "range": range, "enumerate": enumerate, "zip": zip,
        "map": map, "filter": filter, "sorted": sorted, "reversed": reversed,
        "list": list, "tuple": tuple, "set": set, "dict": dict,
        "int": int, "float": float, "str": str, "bool": bool,
        "abs": abs, "min": min, "max": max, "sum": sum,
        "round": round, "print": print,
        "__import__": __import__,       # allow math / random imports
    }

    def time_it(self, code: str, arr: list, repeats: int = 10) -> float | None:
        """
        Execute the user's algorithm with `arr` as input.
        Returns the *median* wall-clock time in seconds, or None on error.
        """
        try:
            compiled = compile(code, "<user_code>", "exec")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in your code:\n{e}") from e

        times = []
        for _ in range(repeats):
            ns = {
                "__builtins__": self.SAFE_BUILTINS,
                "arr": copy.deepcopy(arr),
            }
            try:
                exec(compiled, ns)                   # define the function
            except Exception as e:
                raise ValueError(f"Error during code definition:\n{e}") from e

            # Find the first callable that isn't a built-in
            func = None
            for name, obj in ns.items():
                if callable(obj) and name not in self.SAFE_BUILTINS \
                        and not name.startswith("__"):
                    func = obj
                    break

            if func is None:
                raise ValueError(
                    "No callable function found. "
                    "Make sure you define a function (e.g. def my_algorithm(arr):)."
                )

            test_arr = copy.deepcopy(arr)
            t0 = time.perf_counter()
            try:
                func(test_arr)
            except Exception as e:
                raise ValueError(f"Runtime error in your algorithm:\n{e}") from e
            t1 = time.perf_counter()
            times.append(t1 - t0)

        times.sort()
        return times[len(times) // 2]   # median
