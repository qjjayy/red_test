#!/usr/bin/env python
# -*- coding:utf-8 -*-
TAP = "    "


def format_dict(dict_string):
    """格式化dict"""
    item_list = [item for item in dict_string]
    tap_deep = 0
    line_length = 0

    for i in range(len(item_list)):
        line_length += 1
        if line_length > 100:
            j = i
            while (j > 0 and not (
                   item_list[j] == "," and
                   item_list[j + 1] == " " and
                   item_list[j + 2] == "\"")):
                j -= 1
            add_return_after(item_list, j + 1, tap_deep)
            line_length = (tap_deep - 1) * 4 + (i - j)

        if item_list[i] == "{":
            tap_deep += 1
            add_return_before(item_list, i + 1, tap_deep)
            line_length = tap_deep * 4 + 1
        elif item_list[i] == "}":
            add_return_after(item_list, i - 1, tap_deep - 1)
            line_length = (tap_deep - 1) * 4 + 1
            tap_deep -= 1

    return ''.join(item_list)


def add_return_after(item_list, j, tap_deep):
    item_list[j] += "\n"
    for i in range(tap_deep):
        item_list[j] += TAP


def add_return_before(item_list, j, tap_deep):
    for i in range(tap_deep):
        item_list[j] = TAP + item_list[j]
    item_list[j] = "\n" + item_list[j]
