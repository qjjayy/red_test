#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import uuid
import collections
from bson import ObjectId
from faker import Faker
from faker_config import faker_config


# 为了减少依赖，从Thrift中拷贝过来
class TType(object):
    STOP = 0
    VOID = 1
    BOOL = 2
    BYTE = 3
    I08 = 3
    DOUBLE = 4
    I16 = 6
    I32 = 8
    I64 = 10
    STRING = 11
    UTF7 = 11
    STRUCT = 12
    MAP = 13
    SET = 14
    LIST = 15
    UTF8 = 16
    UTF16 = 17

fake = Faker()
LIST_COUNT = 2
MAP_COUNT = 2


INT_CONFIG = collections.OrderedDict()
UNICODE_CONFIG = collections.OrderedDict()
for fake_function, param_names in faker_config.get('int').items():
    for param_name in param_names:
        INT_CONFIG[param_name] = fake_function
for fake_function, param_names in faker_config.get('unicode').items():
    for param_name in param_names:
        UNICODE_CONFIG[param_name] = fake_function


def fake_request_param(request_type):
    return _fake_struct(
        request_type.__name__, (request_type, request_type.thrift_spec))


def fake_param(attr_name, target_ttype, ttype_conf):
    fake_func = _DUMPS_FUNC[target_ttype]
    return fake_func(attr_name, ttype_conf)


def _fake_bool(attr_name, ttype_conf):
    return fake.boolean()


def _fake_int(attr_name, ttype_conf):
    ret = __special_int_fake(attr_name)
    if ret:
        return ret
    return fake.random_int(min=0, max=10)


def _fake_float(attr_name, ttype_conf):
    return fake.pyfloat(left_digits=2, right_digits=3, positive=True)


def _fake_unicode(attr_name, ttype_conf):
    ret = __special_unicode_fake(attr_name)
    if ret:
        return ret
    return unicode(fake.pystr(max_chars=5) + '***')


def _fake_list(attr_name, ttype_conf):
    target_type = ttype_conf[0]
    thrift_spec = ttype_conf[1]
    return [fake_param(attr_name, target_type, thrift_spec) for i in range(LIST_COUNT)]


def _fake_set(attr_name, ttype_conf):
    return set(_fake_list(attr_name, ttype_conf))


def _fake_map(attr_name, ttype_conf):
    key_ttype = ttype_conf[0]
    key_ttype_conf = ttype_conf[1]
    value_ttype = ttype_conf[2]
    value_ttype_conf = ttype_conf[3]
    ret = collections.OrderedDict()
    for i in range(MAP_COUNT):
        tkey = fake_param(attr_name, key_ttype, key_ttype_conf)
        tvalue = fake_param(attr_name, value_ttype, value_ttype_conf)
        ret[tkey] = tvalue
    return ret


def _fake_struct(attr_name, ttype_conf):
    ret = collections.OrderedDict()
    struct_spec = ttype_conf[1]
    for spec in struct_spec:
        if spec:
            attr_target_type = spec[1]
            attr_name = spec[2]
            attr_ttype_conf = spec[3]
            attr_default = spec[4]
            if attr_default is not None:
                value = attr_default
            else:
                value = fake_param(attr_name, attr_target_type, attr_ttype_conf)
            ret[attr_name] = value
    return ret


_DUMPS_FUNC = {
    TType.BOOL: _fake_bool,
    TType.BYTE: _fake_int,
    TType.I08: _fake_int,
    TType.I16: _fake_int,
    TType.I32: _fake_int,
    TType.I64: _fake_int,
    TType.DOUBLE: _fake_float,
    TType.STRING: _fake_unicode,
    TType.LIST: _fake_list,
    TType.SET: _fake_set,
    TType.MAP: _fake_map,
    TType.STRUCT: _fake_struct
}


def __special_int_fake(attr_name):
    for config_name, fake_func in INT_CONFIG.items():
        if config_name in attr_name:
            if fake_func == 'date_time_this_month':
                ret = getattr(fake, fake_func)(after_now=True)
                ret = int(time.mktime(ret.timetuple()))
            else:
                ret = getattr(fake, fake_func)()
            return ret


def __special_unicode_fake(attr_name):
    for config_name, fake_func in UNICODE_CONFIG.items():
        if config_name in attr_name:
            if fake_func == 'uuid':
                ret = str(uuid.uuid4())
            elif fake_func == 'object_id':
                ret = str(ObjectId())
            else:
                ret = getattr(fake, fake_func)()
            return ret
