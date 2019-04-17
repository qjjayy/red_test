#!/usr/bin/env python
# -*- coding:utf-8 -*-
import collections
LIST_COUNT = 2


def replace_dict(from_dict, to_dict):
    _replace_dict(None, from_dict, to_dict)


def replace_param(attr_name, attr_type, from_dict, to_dict):
    replace_func = _REPLACE_FUNC[attr_type]
    return replace_func(attr_name, from_dict, to_dict)


def _replace_item(attr_name, from_dict, to_dict):
    to_dict[attr_name] = from_dict[attr_name]


def _replace_list(attr_name, from_dict, to_dict):
    from_list = from_dict[attr_name]
    to_list = to_dict[attr_name]

    if len(from_list) == 0:
        to_dict[attr_name] = from_dict[attr_name]
        return

    from_type = __get_value_type(from_list[0])
    to_type = __get_value_type(to_list[0])
    if from_type == to_type:
        if from_type == 'dict':
            for i in range(LIST_COUNT):
                replace_param(None, from_type, from_list[i], to_list[i])
        else:
            to_dict[attr_name] = from_dict[attr_name]


def _replace_dict(attr_name, from_dict, to_dict):
    if attr_name:
        inner_from_dict = from_dict[attr_name]
        inner_to_dict = to_dict[attr_name]

        first_key = inner_to_dict.keys()[0]
        if first_key.endswith('***') or not (
           type(first_key) == unicode or type(first_key) == str):
            to_dict[attr_name] = from_dict[attr_name]
            return
    else:
        inner_from_dict = from_dict
        inner_to_dict = to_dict

    for key, value in inner_to_dict.items():
        if key in inner_from_dict.keys():
            from_type = __get_value_type(inner_from_dict[key])
            to_type = __get_value_type(value)
            if from_type == to_type:
                replace_param(key, from_type, inner_from_dict, inner_to_dict)
            elif inner_from_dict[key] is None:  # 弥补None导致类型不符的特殊情况
                inner_to_dict[key] = inner_from_dict[key]


_REPLACE_FUNC = {
    'default': _replace_item,
    'list': _replace_list,
    'dict': _replace_dict,
}


def __get_value_type(value):
    if type(value) == list or type(value) == set:
        return 'list'
    elif type(value) == dict or type(value) == collections.OrderedDict:
        return 'dict'
    else:
        return 'default'
