import time


class Timer:
    def __init__(self, func=None, identifier=None):
        self.func = func
        self.identifier = identifier

    def __call__(self, *args, **kwargs):
        if self.func is not None:
            start_time = time.time()
            result = self.func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(
                f"Function '{self.func.__name__}' took {elapsed_time:.4f} seconds to execute."
            )
            return result
        return None

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        print(
            f"Block of code: {self.identifier or ''} took {elapsed_time:.4f} seconds to execute."
        )
