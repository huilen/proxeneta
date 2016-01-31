import time


def timecall(fn):
    before_execution_time = time.time()
    ret = fn()
    elapsed_time = time.time() - before_execution_time
    return elapsed_time, ret
