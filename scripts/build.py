import sys
import requests
import yaml
import os
import re
from datetime import datetime

DEFAULT_URL = "https://github.com/liuzq2002/Adguard-Home-For-Magisk-Mod/blob/main/Adguardhome/bin/AdGuardHome.yaml"

# 获取参数
yaml_url = sys.argv[1] if sys.argv[1] else DEFAULT_URL
input_version = sys.argv[2]
input_description = sys.argv[3]

# 转换 raw URL
if "github.com" in yaml_url and "/blob/" in yaml_url:
    yaml_url = yaml_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

print(f"Downloading YAML from: {yaml_url}")

# 下载 YAML
response = requests.get(yaml_url)
response.raise_for_status()
data = yaml.safe_load(response.text)

# 提取 user_rules
rules = data.get("user_rules", [])
if not isinstance(rules, list):
    raise Exception("user_rules not found or invalid format")

# 获取版本号
def get_latest_version():
    try:
        tags = requests.get(
            f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/releases/latest"
        )
        if tags.status_code != 200:
            return "0.0.1"
        latest = tags.json()["tag_name"].replace("v", "")
        x, y, z = map(int, latest.split("."))
        return f"{x}.{y}.{z+1}"
    except:
        return "0.0.1"

if input_version:
    version = input_version
else:
    version = get_latest_version()

# 描述处理
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

if input_description:
    description = input_description.strip()
else:
    description = f"Generated automatically. Version: {version} Time: {now}"

repo_name = os.environ["GITHUB_REPOSITORY"].split("/")[-1]
repo_url = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}"

# 生成 rules.txt
with open("rules.txt", "w", encoding="utf-8") as f:
    f.write("!\n")
    f.write("! Title: Custom AdGuard DNS filter\n")
    f.write(f"! Description: {description}\n")
    f.write(f"! Version: {version}\n")
    f.write(f"! Homepage: {repo_url}\n")
    f.write(f"! Last modified: {now}\n")
    f.write("!\n")
    f.write(f"! Compiled by @{repo_name} v{version}\n")
    f.write("!\n")
    for rule in rules:
        f.write(f"{rule}\n")

print("rules.txt generated.")

# 向 GitHub Actions 输出 version
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"version={version}\n")
