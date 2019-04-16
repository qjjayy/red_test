## 项目描述
通过解析IDL自动生成PyTest单测框架,
通过Faker库辅助生成部分参数,
并且支持单测参数和单测逻辑的向后兼容

## 安装
```javascript
    pip install pytest
    pip install pyaml
    pip install Faker==1.0.4
    pip install bson
```

## 示例代码
```javascript
from auto_red_test import generate_red_test
from frame import ENV
from handler.stockage_handler import StockageHandler  # 需要单测的handler
import stockage_service.request.ttypes as test_request  # idl的request文件
import stockage_service.StockageService as test_service  # idl的service文件
root_path = ENV['root']  # 项目的根目录
# 第二个参数可以是handler列表，但必须属于同一个service
generate_red_test(root_path, StockageHandler, test_service, test_request)
```
* 自动生成的单测框架如下：
* ![image](https://raw.githubusercontent.com/qjjayy/red_test/master/image/test_red.jpg)

## 补充内容
* 第一次运行会生成request_config.yaml，可以自定义单测方法的参数，用于解决一个单测方法用到多个request的特殊情况，
格式如下：
```javascript
# 配置单测参数
methodA:
  request_A_name: request_A_obj_name
  request_B_name: request_A_obj_name
methodB:
  request_B_name: request_B_obj_name
  request_C_name: request_C_obj_name
```
methodA为单测方法名， request_A_name为请求参数名，request_A_obj_name为请求参数对应的IDL Request名
