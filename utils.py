def euro_float(value: str) -> float:
    return float(value.replace(',', '.'))


def flatten(input_list):
    flat_list = []
    for item in input_list:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list
