# encoding: utf-8
import itertools


def find(sequence, predicate):
    filtered = itertools.ifilter(predicate, sequence)
    try:
        return next(filtered)
    except StopIteration:
        return None


def exists(sequence, predicate):
    return find(sequence, predicate) is not None
