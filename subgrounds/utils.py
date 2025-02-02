from itertools import filterfalse
from functools import reduce, partial
from typing import Any, Callable, Optional, Tuple, TypeVar

from pipe import map, traverse, where

def flatten(t):
  return [item for sublist in t for item in sublist]


def identity(x):
  return x


T = TypeVar('T')
U = TypeVar('U')


def fst(tup: Tuple[T, U]) -> T:
  return tup[0]


def snd(tup: Tuple[T, U]) -> U:
  return tup[1]

# ================================================================
# Set utility functions
# ================================================================
def intersection(
  l1: list[T],
  l2: list[T],
  key: Callable[[T], Any] = identity,
  combine: Callable[[T, T], T] = lambda x, _: x
) -> list[T]:
  l1_keys, l2_keys = list(l1 | map(key)), list(l2 | map(key))
  l2_in_l1 = list(filter(lambda x: key(x) in l1_keys, l2))
  l1_in_l2 = list(filter(lambda x: key(x) in l2_keys, l1))
  l2_in_l1.sort(key=key)
  l1_in_l2.sort(key=key)

  return list(zip(l1_in_l2, l2_in_l1) | map(lambda tup: combine(tup[0], tup[1])))


def rel_complement(
  l1: list[T],
  l2: list[T],
  key: Callable[[T], Any] = identity
) -> list[T]:
  l2_keys = list(l2 | map(key))
  return list(filterfalse(lambda x: key(x) in l2_keys, l1))


def sym_diff(
  l1: list[T],
  l2: list[T],
  key: Callable[[T], Any] = identity
) -> list[T]:
  return rel_complement(l1, l2, key) + rel_complement(l2, l1, key)


def union(
  l1: list[T],
  l2: list[T],
  key: Callable[[T], Any] = identity,
  combine: Callable[[T, T], T] = lambda x, _: x
) -> list[T]:
  return rel_complement(l1, l2, key) + intersection(l1, l2, key, combine) + rel_complement(l2, l1, key)


# ================================================================
# Misc
# ================================================================
def filter_none(items: list[Optional[T]]) -> list[T]:
  return list(filter(None, items))


def loop_generator(items: list):
  while True:
    for item in items:
      yield item


# ================================================================
# Dictionary related utility functions
# ================================================================
def extract_data(keys: list[str], data: dict[str, Any] | list[dict[str, Any]]) -> list[Any] | Any:
  def f(keys: list[str], data: dict | list | Any):
    match keys:
      case []:
        return data
      case [name, *rest]:
        match data:
          case dict():
            return f(rest, data[name])
          case list():
            return list(data | map(lambda row: f(rest, row[name])))
          case None:
            return None
          case _:
            raise Exception(f"extract_data: unexpected state! path = {keys}, data = {data}")

  match data:
    case dict():
      return f(keys, data)
    case list():
      for doc_data in data:
        try:
          return f(keys, doc_data)
        except KeyError:
          continue
      raise Exception(f'extract_data: not found! path = {keys}, data = {data}')
    case _:
      raise Exception('extract_data: data is not dict or list')


def flatten_dict(data: dict, keys: list[str] = []) -> dict:
  """ Takes a dictionary containing key-value pairs where all values are of type
  other than `list` and flattens it such that all key-value pairs in nested dictionaries
  are now at depth 1.

  Args:
    data (dict): Dictionary containing non-list values
    keys (list[str], optional): Keys of `data` if `data` is a nested `dict` (`len(keys)` == depth of `data`). Defaults to [].

  Returns:
    dict: Flat dictionary containing all key-value pairs in `data` and its nested dictionaries
  """
  flat_dict = {}
  for key, value in data.items():
    match value:
      case dict():
        flat_dict = flat_dict | flatten_dict(value, [*keys, key])
      case value:
        flat_dict['_'.join([*keys, key])] = value
  
  return flat_dict


def contains_list(data: dict | list | str | int | float | bool) -> bool:
  """ Returns `True` if `data` contains a value of type `list` in its nested data
  and `False` otherwise

  Args:
    data (dict | list | str | int | float | bool): Data

  Returns:
    bool: `True` if `data` contains a list, `False` otherwise
  """
  match data:
    case list():
      return True
    case dict():
      return any(data.values() | map(contains_list))
    case set():
      return any(data | map(contains_list))
    case str() | int() | float() | bool():
      return False


def columns_of_json(data: dict, keys: list[str] = []) -> list[str]:
  columns = []
  for key, value in data.items():
    match value:
      case dict():
        columns.append(columns_of_json(value, [*keys, key]))
      case list():
        columns.append(reduce(union, value | map(partial(columns_of_json, keys=[*keys, key])) | map(lambda x: list(x | traverse)), []))
      case value:
        columns.append('_'.join([*keys, key]))
  
  return columns
