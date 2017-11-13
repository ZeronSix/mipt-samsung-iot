"""JSON data parser that checks if it corresponds to the protocol."""
import json


def _parser_hook(pairs):
    lst = []
    for key, value in pairs:
        lst.append((key, value))
    return lst


def _list_to_dict(pairs):
    d = dict()
    for key, value in pairs:
        if type(value) is list:
            d[key] = _list_to_dict(value)
        else:
            d[key] = value
    return d


def _check_protocol(data, template):
    # TODO: Check whether template is OK
    if len(template) < len(data):
        raise KeyError("Found unknown key: '{}'".format(data[len(template)][0]))

    existing_keys = set()
    for i in range(len(template)):
        if i == len(data):
            raise KeyError("Missing key: '{}'".format(template[i][0]))
        if data[i][0] in existing_keys:
            raise KeyError("Repeated key: '{}'".format(data[i][0]))
        if template[i][0] != data[i][0]:
            raise KeyError("Wrong key order or possible unknown key: expected '{}', got '{}'".format(template[i][0],
                                                                                                     data[i][0]))
        if not isinstance(template[i][1], type(data[i][1])):
            raise TypeError("Wrong type: expected '{}', got '{}'".format(type(template[i][1]),
                                                                     type(data[i][1])))

        existing_keys.add(data[i][0])
        if isinstance(data[i][1], list):
            _check_protocol(data[i][1], template[i][1])


def safe_parse(data_str, template_str):
    data = json.loads(data_str, object_pairs_hook=_parser_hook)
    template = json.loads(template_str, object_pairs_hook=_parser_hook)
    _check_protocol(data, template)

    return _list_to_dict(data)
