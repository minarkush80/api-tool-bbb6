#!/bin/bash

# 使用 readlink -f 获取脚本的绝对路径（兼容符号链接）
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

# 切换到脚本所在目录
cd "$SCRIPT_DIR" || exit

xgettext -d knotpen2 -o locales/knotpen2.pot ../*.py --from-code=UTF-8
mkdir -p locales/{zh_CN,en_US}/LC_MESSAGES
msginit -i locales/knotpen2.pot -o locales/zh_CN/LC_MESSAGES/knotpen2.po -l zh_CN
msginit -i locales/knotpen2.pot -o locales/en_US/LC_MESSAGES/knotpen2.po -l en_US
