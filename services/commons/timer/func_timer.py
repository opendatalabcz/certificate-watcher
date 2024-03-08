import multiprocessing


class TimerExceptionError(Exception):
    pass


def run_with_timeout(func, timeout, *args, **kwargs):
    """Runs a function with the given timeout. If the function execution exceeds the timeout, raises TimerExceptionError."""

    def wrapper(queue):
        try:
            result = func(*args, **kwargs)
            queue.put(result)
        except Exception as e:
            queue.put(e)

    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=wrapper, args=(queue,))
    process.start()
    process.join(timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimerExceptionError(f"Operation timed out after {timeout} seconds")

    if not queue.empty():
        result = queue.get()
        if isinstance(result, Exception):
            raise result
        return result

    raise TimerExceptionError("Failed to retrieve result from the process")
