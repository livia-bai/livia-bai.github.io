"""读一篇月之暗面文章，输出 title / excerpt / url，给通知用的 workflow 读取。

用法：eval "$(python3 post_info.py dark/_posts/2026-10-23-shipping-forecast.md)"
输出三行 shell 变量赋值（已经转义好，可以直接 eval）。
"""
import os
import re
import shlex
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()

front = {}
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if m:
    for line in m.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            value = value.split(" #")[0].strip().strip('"').strip("'")
            front[key.strip()] = value

# 和 _config.yml 里的 permalink 一致：/dark-side/:year/:month/:day/:title/
name = os.path.basename(path)[:-3]
year, month, day, slug = name[:4], name[5:7], name[8:10], name[11:]
url = f"https://livia-bai.github.io/dark-side/{year}/{month}/{day}/{slug}/"

print(f"title={shlex.quote(front.get('title', slug))}")
print(f"excerpt={shlex.quote(front.get('excerpt', ''))}")
print(f"url={shlex.quote(url)}")
