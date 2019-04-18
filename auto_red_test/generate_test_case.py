#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    通过解析IDL自动生成Pytest单测框架,
    通过fake辅助生成部分参数,
    并且支持单测参数和单测逻辑的向后兼容;
"""
import os
import inspect
import collections
import json
import yaml
import re
from dictdiffer import diff
from thrift_fake import fake_request_param
from dict_format_print import format_dict
from dict_replace import replace_dict

TAP = '    '


def __to_underscore(str_item):
    return ''.join('_%s' % c if c.isupper() else c
                   for c in str_item).strip('_').lower()


def __get_need_test_methods_from_handler(test_handler):
    """从指定Handler获取需要测试的方法（包含一些非IDL的方法，后面会处理掉）"""
    need_test_methods = list()
    for name, obj in inspect.getmembers(test_handler):
        if inspect.ismethod(obj) and not re.search('gen_idl', obj.__func__.func_code.co_filename):
            need_test_methods.append(name)
    return need_test_methods


def __get_service_info_from_thrift(root_path, idl_service, need_test_methods):
    """从指定IDL_Service和request_config配置表中，获取测试方法和Request的映射表"""
    customized_request_config = yaml.load(
        open(os.path.join(root_path, 'test_red', 'request_config.yaml')))

    method_request = collections.OrderedDict()

    idl_method_request = dict([
        (name[:-5], obj) for name, obj in inspect.getmembers(idl_service)
        if inspect.isclass(obj) and '_args' in name])

    for method_name in need_test_methods:
        if customized_request_config and method_name in customized_request_config:
            method_request[method_name] = customized_request_config[method_name]
        elif method_name in idl_method_request:
            try:
                request_obj_name = idl_method_request[method_name].thrift_spec[2][3][0].__name__
                method_request[method_name] = {__to_underscore(request_obj_name): request_obj_name}
            except Exception:
                print 'invalid method name: ' + method_name

    return method_request


def __get_request_info_from_thrift(idl_request, method_request):
    """从指定IDL_Request中，获取测试Request名和Request类的映射表"""
    request_name_obj = collections.OrderedDict()

    request_name__obj_name = collections.OrderedDict()
    for request_config in method_request.values():
        request_name__obj_name.update(request_config)

    request_obj_name__obj = dict([
        (name, obj)for name, obj in inspect.getmembers(idl_request) if inspect.isclass(obj)])

    for name, obj_name in request_name__obj_name.items():
        request_name_obj[name] = request_obj_name__obj[obj_name]
    return request_name_obj


def __get_existed_requests_param(root_path):
    """获取已经写过的单测参数，以支持后面的复写，从而支持单测参数的向后兼容"""
    existed_requests_param = dict()
    if os.path.exists(os.path.join(
            root_path, 'test_red', 'test_handler', 'requests_param.py')):
        import test_red.test_handler.requests_param as existed_param
        for name, obj in inspect.getmembers(existed_param):
            if name != '__builtins__' and type(obj) == dict:
                existed_requests_param[name] = obj
    return existed_requests_param


def __get_existed_handler_methods(root_path):
    """获取已经写过的单测方法的逻辑，以支持后面的复写，从而支持单测逻辑的向后兼容"""
    existed_handler_methods = dict()
    if os.path.exists(os.path.join(
            root_path, 'test_red', 'test_handler', 'test_methods.py')):
        with open(os.path.join(
                root_path, 'test_red', 'test_handler', 'test_methods.py'), 'r') as f:
            whole_file = f.readlines()
            prev_name = ''
            for line_index in range(len(whole_file)):
                if whole_file[line_index] == '@exception_decorate\n':
                    end_index = whole_file[line_index + 1].index('(')
                    name = whole_file[line_index + 1][4: end_index]
                    existed_handler_methods[name] = line_index
                    if prev_name:
                        prev_line_index = existed_handler_methods[prev_name]
                        existed_handler_methods[prev_name] = whole_file[
                            prev_line_index: line_index]
                    prev_name = name
            if prev_name:
                prev_line_index = existed_handler_methods[prev_name]
                existed_handler_methods[prev_name] = whole_file[
                    prev_line_index:]

    return existed_handler_methods


def __write_test_first(root_path):
    """构建单测的第一层架构"""
    if not os.path.exists(os.path.join(root_path, 'test_red')):
        os.mkdir(os.path.join(root_path, 'test_red'))

        with open(os.path.join(
                root_path, 'test_red', '__init__.py'), 'w') as f:
            print 'Create root __init__ --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            f.writelines(contents)

        with open(os.path.join(
                root_path, 'test_red', 'conftest.py'), 'w') as f:
            print 'Create root conftest --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            contents.append('# 创建单测环境\n')
            contents.append('import pytest\n\n\n')

            contents.append('@pytest.fixture(scope=\'session\', autouse=True)\n')
            contents.append('def global_action():\n')
            contents.append(TAP + '# mock database\n')
            contents.append(TAP + 'pass\n')
            f.writelines(contents)

        with open(os.path.join(
                root_path, 'test_red', 'request_config.yaml'), 'w') as f:
            print 'Create root request_config --------------------'
            contents = list()
            contents.append('# 配置单测参数\n')
            f.writelines(contents)


def __write_test_second(root_path):
    """构建单测的第二层架构"""
    if not os.path.exists(os.path.join(root_path, 'test_red', 'test_handler')):
        os.mkdir(os.path.join(root_path, 'test_red', 'test_handler'))

        with open(os.path.join(
                root_path, 'test_red', 'test_handler', '__init__.py'), 'w') as f:
            print 'Create __init__ --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            f.writelines(contents)

        with open(os.path.join(
                root_path, 'test_red', 'test_handler', 'create_context.py'), 'w') as f:
            print 'Create create_context --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            contents.append('# 创建方法级别的单测数据环境\n\n\n')
            contents.append('def create_data_context():\n')
            contents.append(TAP + 'pass\n')
            f.writelines(contents)

        with open(os.path.join(
                root_path, 'test_red', 'test_handler', 'conftest.py'), 'w') as f:
            print 'Create conftest --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            contents.append('from redrpc import red_context\n')
            contents.append('from fixture_requests import *\n')
            contents.append('from create_context import create_data_context\n\n\n')

            contents.append('@pytest.fixture(scope=\'function\', autouse=True)\n')
            contents.append('def handler_context():\n')
            contents.append(TAP + 'return red_context.get().gen_thrift_context()\n\n\n')

            contents.append('@pytest.fixture(scope=\'function\', autouse=True)\n')
            contents.append('def test_data_context():\n')
            contents.append(TAP + 'create_data_context()\n')
            contents.append(TAP + 'yield\n')
            contents.append(TAP + 'destroy_data_context()\n\n\n')

            contents.append('def destroy_data_context():\n')
            contents.append(TAP + 'pass\n')
            f.writelines(contents)

        with open(os.path.join(
                root_path, 'test_red', 'test_handler', 'exception_decorator.py'), 'w') as f:
            print 'Create exception_decorator --------------------'
            contents = list()
            contents.append('#!/usr/bin/env python\n')
            contents.append('# -*- coding:utf-8 -*-\n')
            contents.append('import decorator\n\n\n')

            contents.append('def exception_decorate(func):\n')
            contents.append(TAP + 'def wrapper(func, *args, **kwargs):\n')
            contents.append(TAP + TAP + 'try:\n')
            contents.append(TAP + TAP + TAP + 'func(*args, **kwargs)\n')
            contents.append(TAP + TAP + 'except Exception as exc:\n')
            contents.append(TAP + TAP + TAP + 'print exc.message\n')
            contents.append(TAP + TAP + TAP + 'assert False\n')
            contents.append(TAP + 'return decorator.decorator(wrapper, func)\n')
            f.writelines(contents)


def __write_request_params(root_path, request_name_obj, existed_requests_param):
    """复写单测参数，支持向后兼容"""

    with open(os.path.join(
            root_path, 'test_red', 'test_handler', 'requests_param.py'), 'w') as f:
        print 'Create test params --------------------'
        requests_param = list()
        requests_param.append('#!/usr/bin/env python\n')
        requests_param.append('# -*- coding:utf-8 -*-\n')
        for name, obj in request_name_obj.items():
            param_name = name + '_params'
            request_param = fake_request_param(obj)
            if param_name in existed_requests_param:
                existed_request_param = existed_requests_param[param_name]
                replace_dict(existed_request_param, request_param)
                if existed_request_param != request_param:
                    print 'Change test params of ' + name
                    print list(diff(existed_request_param, request_param))
            else:
                print 'Create test params of ' + name

            request_param = json.dumps(request_param)
            request_param = request_param.replace('false', 'False')
            request_param = request_param.replace('true', 'True')
            request_param = request_param.replace('null', 'None')
            requests_param.append(
                param_name + ' = ' + format_dict(request_param) + '\n\n')
        f.writelines(requests_param)


def __write_pytest_request(root_path, idl_request, request_name_obj):
    """复写pytest_request_fixture"""
    with open(os.path.join(
            root_path, 'test_red', 'test_handler', 'fixture_requests.py'), 'w') as f:
        pytest_requests = list()
        pytest_requests.append('#!/usr/bin/env python\n')
        pytest_requests.append('# -*- coding:utf-8 -*-\n')
        pytest_requests.append('import pytest\n')
        pytest_requests.append('from doraemon.thrift import wrap_struct\n')
        pytest_requests.append('from test_red.test_handler.requests_param import *\n')
        pytest_requests.append('from ' + idl_request.__name__ + ' import *\n\n\n')
        for name, obj in request_name_obj.items():
            method_decorator = '@pytest.fixture(params=[' + name + '_params])\n'
            method_header = 'def ' + name + '(request):\n'
            method_content = TAP + 'request = request.param\n'
            method_content += TAP + 'return wrap_struct(request, ' + obj.__name__ + ')\n'
            pytest_requests.append(method_decorator + method_header + method_content + '\n\n')
        f.writelines(pytest_requests)


def __write_test_methods(root_path, method_request, existed_handler_methods):
    """复写单测逻辑，支持向后兼容"""
    with open(os.path.join(
            root_path, 'test_red', 'test_handler', 'test_methods.py'), 'w') as f:
        print 'Create test methods --------------------'
        handler_methods = list()
        handler_methods.append('#!/usr/bin/env python\n')
        handler_methods.append('# -*- coding:utf-8 -*-\n')
        handler_methods.append('from handler import Handler\n')
        handler_methods.append('from exception_decorator import exception_decorate\n')
        handler_methods.append('handler_object = Handler()\n\n\n')
        for method_name, request_config in method_request.items():
            test_method_name = 'test_' + method_name

            if test_method_name in existed_handler_methods:
                handler_methods.extend(existed_handler_methods[test_method_name])
            else:
                print 'Create test method: ' + method_name
                request_names = request_config.keys()
                method_decorator = '@exception_decorate\n'
                method_header = (
                    'def ' + test_method_name + '(handler_context, '
                    + ', '.join(request_names) + '):\n')
                method_content = TAP + 'result = handler_object.' + method_name + '(\n'
                method_content += TAP + TAP + 'handler_context,\n'
                method_content += TAP + TAP + request_names[0] + ')\n'
                method_content += TAP + 'assert result is not None\n'
                handler_methods.append(method_decorator + method_header + method_content + '\n\n')
        f.writelines(handler_methods)


def generate_red_test(root_path, test_handlers, test_service, test_request):
    """自动生成Red Test"""
    __write_test_first(root_path)
    __write_test_second(root_path)

    if type(test_handlers) is not list:
        test_handlers = [test_handlers]
    need_test_methods = list()
    for handler in test_handlers:
        need_test_methods.extend(__get_need_test_methods_from_handler(handler))

    method_request = __get_service_info_from_thrift(root_path, test_service, need_test_methods)
    request_name_obj = __get_request_info_from_thrift(test_request, method_request)
    existed_requests_param = __get_existed_requests_param(root_path)
    existed_handler_methods = __get_existed_handler_methods(root_path)

    __write_request_params(root_path, request_name_obj, existed_requests_param)
    __write_pytest_request(root_path, test_request, request_name_obj)
    __write_test_methods(root_path, method_request, existed_handler_methods)


# if __name__ == '__main__':
#     # 测试案例
#     import os
#     import sys
#     sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
#     from frame import ENV
#     from handler.route_handler import RouteHandler
#     import interlogistics_service.request.ttypes as test_request
#     import interlogistics_service.InterlogisticService as test_service
#     generate_red_test(ENV['root'], RouteHandler, test_service, test_request)
