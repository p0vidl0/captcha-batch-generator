import signal
import multiprocessing as mp
import itertools
import time

from lib import captcha_image

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
MAX_WORKERS = 12

def worker(first_bits):
    for i in itertools.product(first_bits, ALPHABET, ALPHABET, ALPHABET):
        code = ''.join(i)
        captcha_image(code)
        print(code + ' generated')

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

if __name__ == "__main__":
    pool = mp.Pool(MAX_WORKERS, init_worker)
    results = pool.map_async(worker, ALPHABET)

    try:
        print("Waiting 1 second")
        time.sleep(1)

    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
        pool.join()

    else:
        print("Quitting normally")
        pool.close()
        pool.join()

