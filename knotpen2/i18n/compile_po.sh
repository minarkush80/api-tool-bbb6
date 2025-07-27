#!/bin/bash

# 使用 readlink -f 获取脚本的绝对路径（兼容符号链接）
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

# 切换到脚本所在目录
cd "$SCRIPT_DIR" || exit

echo -en "zh_CN" > ./default_lang.txt

# 编译两个 mo 文件
msgfmt -o locales/en_US/LC_MESSAGES/knotpen2.mo locales/en_US/LC_MESSAGES/knotpen2.po
msgfmt -o locales/zh_CN/LC_MESSAGES/knotpen2.mo locales/zh_CN/LC_MESSAGES/knotpen2.po
