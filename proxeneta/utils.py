import time


def timecall(fn):
    before_execution_time = time.time()
    ret = fn()
    elapsed_time = time.time() - before_execution_time
    return elapsed_time, ret


def chunks(iterable, number):
    size = round(len(iterable) / number) + 1
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]
