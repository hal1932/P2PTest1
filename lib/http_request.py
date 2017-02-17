# encoding: utf-8
import requests
import requests.exceptions
import grequests
import threading


STATUS_OK = 200
STATUS_NOT_FOUND = 404


ConnectionError = requests.exceptions.ConnectionError
ConnectTimeout = requests.exceptions.ConnectTimeout


def get_sync(url, params=None, timeout=None, ignore_error=False):
    kwargs = {}
    if timeout is not None:
        kwargs['timeout'] = (timeout, timeout)
    if params is not None:
        kwargs['params'] = params

    try:
        response = requests.get(url, **kwargs)
        return response.status_code, response.text
    except:
        if not ignore_error:
            raise

    return 0, ''


def gets_sync(urls, params=None, timeout=None):
    kwargs = {}
    if timeout is not None:
        kwargs['timeout'] = (timeout, timeout)
    if params is not None:
        kwargs['params'] = params

    tmp = {'errors': {}}
    errors_lock = threading.Lock()

    def _exception_handler(req, ex):
        with errors_lock:
            tmp['errors'][req.url] = ex

    request_set = (grequests.get(url, **kwargs) for url in urls)
    response_set = grequests.map(request_set, exception_handler=_exception_handler)

    result = {}
    for response in response_set:
        if response is not None:
            result[response.url] = (response.status_code, response.content)
    for url, error in tmp['errors'].items():
        result[url] = (0, error)

    return result


def post_sync(url, data, timeout=None):
    kwargs = {}
    if timeout is not None:
        kwargs['timeout'] = (timeout, timeout)

    response = requests.post(url, data, **kwargs)
    return response.status_code, response.text
