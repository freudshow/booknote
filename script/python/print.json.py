import json
import sys
import pandas as pd

def print_json(obj, indent=0):
    """递归遍历和打印JSON对象"""
    spacing = '  ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{spacing}{key}:")
            print_json(value, indent + 1)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            print(f"{spacing}[{index}]:")
            print_json(item, indent + 1)
    else:
        print(f"{spacing}{obj}")

def extract_json(obj, indent=0):
    """递归遍历和打印JSON对象"""
    spacing = '  ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{spacing}{key}:")
            print_json(value, indent + 1)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            print(f"{spacing}[{index}]:")
            print_json(item, indent + 1)
    else:
        print(f"{spacing}{obj}")

# 从控制台读取文件名参数
if len(sys.argv) != 2:
    print("用法: python script.py <json文件名>")
    sys.exit(1)

file_name = sys.argv[1]

# 从文件中读取JSON数据
with open(file_name, 'r') as file:
    json_data = file.read()

# 将JSON字符串解析为Python对象
parsed_json = json.loads(json_data)

# 调用函数打印键值对
print_json(parsed_json)

df = pd.DataFrame(parsed_json)
