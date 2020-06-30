import requests
import os
from pprint import pprint
import random
import re
import time
import uuid
import functools
from tqdm import tqdm
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from json.decoder import JSONDecodeError


IGNORE_LOGGING = False
uuid_match = re.compile('([0-9a-f\-]+)$', re.I)

def debug(message):
    if not IGNORE_LOGGING:
        pprint(message)


def info(message):
    if not IGNORE_LOGGING:
        pprint(message)


def warn(message):
    if not IGNORE_LOGGING:
        pprint(message)


def error(message):
    if not IGNORE_LOGGING:
        pprint(message)


def fatal(message):
    if not IGNORE_LOGGING:
        pprint(message)


def uuid_search(text):
    return uuid_match.search(text).group(0)


def _process(url, **kwargs):
    kwargs['url'] = f'{HOST}{url}'
    headers = kwargs.get('headers', {})
    headers.update({
        'Authorization': f'Bearer {TOKEN}'
    })
    kwargs['headers'] = headers

    return kwargs


def request(method, url, **kwargs):
    return requests.request(method, **_process(url, **kwargs))


def get(url, **kwargs):
    return request('get', url, **kwargs)

def post(url, **kwargs):
    return request('post', url, **kwargs)

def delete(url, **kwargs):
    return request('delete', url, **kwargs)

def patch(url, **kwargs):
    return request('patch', url, **kwargs)

def put(url, **kwargs):
    return request('put', url, **kwargs)

def assert_2xx(response):
    if int(response.status_code) // 100 != 2:
        try:
            info(response.json())
        except JSONDecodeError:
            info(response.text)
        raise ValueError('Status code is not 2xx')


def sleep(seconds):
    time.sleep(seconds)


def repeat(job, repeats, workers=None):
    @functools.wraps(job)
    def wrapped_job(_):
        return job()

    workers = multiprocessing.cpu_count() if workers is None else workers

    with ThreadPoolExecutor(max_workers=workers) as executor:
        ret_iter = executor.map(wrapped_job, range(repeats))
        ret = list(tqdm(ret_iter, total=repeats))

    return ret


def wait_until(test, ignore_except=True, wait=0.05):
    global IGNORE_LOGGING
    IGNORE_LOGGING = ignore_except
    while True:
        try:
            if test():
                break
        except:
            if not ignore_except:
                IGNORE_LOGGING = False
                raise
        finally:
            sleep(wait)
    IGNORE_LOGGING = False


def wait_until_count(counter, total_count, ignore_except=True, wait=0.05):
    global IGNORE_LOGGING
    IGNORE_LOGGING = ignore_except
    pbar = tqdm(total=total_count)
    while True:
        try:
            count = counter()
            pbar.update(count - pbar.n)
            if count >= total_count:
                break
        except:
            if not ignore_except:
                pbar.close()
                IGNORE_LOGGING = False
                raise
        finally:
            time.sleep(wait)

    IGNORE_LOGGING = False
    pbar.close()


def yes(msg = 'Continue'):
    answer = input(f'{msg} [y/n]: ')
    return answer in ('y', 'Y', 'yes')


@contextmanager
def benchmark(title=''):
    before = time.perf_counter()
    try:
        yield before
    finally:
        after = time.perf_counter()
        BENCHMARK = '\033[0;32mBENCHMARK\033[0m'
        print(f'[{BENCHMARK}] {title}: {after - before} sec')
