# 利用 LoongArch Archlinux 系统构建 openSUSE LoongArch 基本系统和包管理器

## 目前的思路：

1. 利用 Archlinux 尝试构建 zypper 包管理器 ✌
2. 利用 Archlinux 中的 rpm 工具集构建 openSUSE 的 base system 并打包 ✌
3. 利用 LoongArch Archlinux 系统构建 base system 包，并使用 zypper 安装基本系统和内核 🤏
    - base-system 完成度：
        - `aaa-base`
        - `acct`
        - `acpi`
        - `acpi_call` （等待第二阶段测试） 📌
        - `acpid`
        - `attr`
        - `autogen`
        - `acl`
        - `tar`
4. 尝试在新世界启动 LoongArch 系统 🤏
5. 原生系统打包和测试 🤏
