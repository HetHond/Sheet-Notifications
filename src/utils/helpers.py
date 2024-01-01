from collections.abc import Iterable


def euro_float(value: str) -> float:
    return float(value.replace(',', '.'))


def flatten(input_arr, output_arr=None):
    if output_arr is None:
        output_arr = []
    for item in input_arr:
        if not isinstance(item, str) and isinstance(item, Iterable):
            flatten(item, output_arr)
        else:
            output_arr.append(item)
    return output_arr


def flatten_iter(iterable):
    for element in iterable:
        if not isinstance(element, str) and isinstance(element, Iterable):
            yield from flatten_iter(element)
        else:
            yield element
            