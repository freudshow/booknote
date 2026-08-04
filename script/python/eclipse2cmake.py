#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eclipse2cmake.py  —  Eclipse CDT (.project / .cproject) → CMakeLists.txt 转换器

支持:
  * Eclipse CDT Managed Build 工程 (.cproject)
  * GNU ARM Eclipse / GNU MCU Eclipse 交叉编译插件 (ilg.gnuarmeclipse.*)
  * 通用 CDT GNU 工具链 (cdt.managedbuild.tool.gnu.*)

从 .cproject 中提取每个构建配置(Configuration)的:
  - 目标类型 (可执行 / 静态库 / 动态库) 与 目标名
  - 交叉工具链前缀、C/C++ 编译器命令
  - 头文件搜索路径 (-I)
  - 预处理宏定义 (-D)
  - 库 (-l) 与库搜索路径 (-L)
  - 优化等级、ARM 目标(-mcpu/-march/-mfpu/-mfloat-abi)、其它编译/链接标志
  - 源文件目录 (sourceEntries；缺省时递归收集常见源码后缀)

用法:
  python3 eclipse2cmake.py [工程目录] [选项]

常用选项:
  -o, --output FILE     输出文件名 (默认: 工程目录/CMakeLists.txt)
  -c, --config NAME     只导出指定配置(如 ReleaseC0)。缺省导出全部配置,
                        通过 CMake 变量 BUILD_CONFIG 选择。
  --list                仅列出 .cproject 中的所有配置后退出
  --stdout              输出到标准输出而非文件
  --force               覆盖已存在的输出文件

示例:
  python3 eclipse2cmake.py .                       # 转换当前目录工程
  python3 eclipse2cmake.py /path/proj -c ReleaseC0 # 只导出 ReleaseC0 配置
  python3 eclipse2cmake.py . --list                # 查看有哪些配置
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# 枚举值 → 编译标志 的映射表 (GNU ARM Eclipse 插件)
# ---------------------------------------------------------------------------
OPT_LEVEL_MAP = {
    "optimization.level.none": "-O0",
    "optimization.level.optimize": "-O1",
    "optimization.level.more": "-O2",
    "optimization.level.most": "-O3",
    "optimization.level.size": "-Os",
    "optimization.level.debug": "-Og",
    # 通用 CDT
    "gnu.c.optimization.level.none": "-O0",
    "gnu.c.optimization.level.optimize": "-O1",
    "gnu.c.optimization.level.more": "-O2",
    "gnu.c.optimization.level.most": "-O3",
    "gnu.c.optimization.level.size": "-Os",
    "gnu.cpp.compiler.optimization.level.none": "-O0",
    "gnu.cpp.compiler.optimization.level.optimize": "-O1",
    "gnu.cpp.compiler.optimization.level.more": "-O2",
    "gnu.cpp.compiler.optimization.level.most": "-O3",
    "gnu.cpp.compiler.optimization.level.size": "-Os",
}

DEBUG_LEVEL_MAP = {
    "debugging.level.none": "",
    "debugging.level.minimal": "-g1",
    "debugging.level.default": "-g",
    "debugging.level.max": "-g3",
}

# ARM 家族 (-mcpu)
ARM_MCPU_RE = re.compile(r"arm\.target\.mcpu\.([A-Za-z0-9_.\-+]+)$")
# ARM 架构 (-march)
ARM_ARCH_RE = re.compile(r"arm\.target\.arch\.([A-Za-z0-9_.\-+]+)$")
# FPU 单元 (-mfpu)
ARM_FPU_RE = re.compile(r"arm\.target\.fpu\.unit\.([A-Za-z0-9_.\-+]+)$")
# Float ABI (-mfloat-abi)
ARM_FLOATABI_RE = re.compile(r"arm\.target\.fpu\.abi\.([A-Za-z0-9_.\-+]+)$")
# 指令集 thumb/arm
ARM_INSTR_RE = re.compile(r"arm\.target\.instructionset\.([A-Za-z0-9_.\-+]+)$")


def strip_ns(tag):
    """去掉 XML 命名空间前缀。"""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def resolve_eclipse_vars(value, proj_name):
    """
    把 Eclipse 路径变量转换为 CMake 变量。
      ${workspace_loc:/ProjName/xxx}      -> ${CMAKE_SOURCE_DIR}/xxx
      ${workspace_loc:/${ProjName}/xxx}   -> ${CMAKE_SOURCE_DIR}/xxx
      ${ProjDirPath}/xxx                  -> ${CMAKE_SOURCE_DIR}/xxx
    并去掉包裹的引号。
    """
    if value is None:
        return ""
    v = value.strip()
    # 去掉 XML 反转义后可能残留的引号
    v = v.strip('"').strip()

    # 关键: 先把嵌套的 ${ProjName} 展开为真实工程名, 避免其内部的 '}'
    # 打断后面对 ${workspace_loc:...} 的花括号配对。
    v = v.replace("${ProjName}", proj_name)

    # ${workspace_loc:/<proj>/rest}  ->  ${CMAKE_SOURCE_DIR}/rest
    def repl_wsloc(m):
        inner = m.group(1).lstrip("/")
        parts = inner.split("/", 1)
        if parts and parts[0] == proj_name:
            rest = parts[1] if len(parts) > 1 else ""
        else:
            rest = inner
        return "${CMAKE_SOURCE_DIR}/" + rest if rest else "${CMAKE_SOURCE_DIR}"

    v = re.sub(r"\$\{workspace_loc:([^}]*)\}", repl_wsloc, v)
    v = v.replace("${ProjDirPath}", "${CMAKE_SOURCE_DIR}")
    v = v.replace("${workspace_loc}", "${CMAKE_SOURCE_DIR}")
    # 收尾: 多余的引号
    v = v.replace('"', "").strip()
    # 规整重复斜杠(保留前导 ${...} 及 :// )
    v = re.sub(r"(?<!:)//+", "/", v)
    return v


class Configuration:
    """一个 CDT 构建配置的抽象。"""

    def __init__(self, name):
        self.name = name
        self.artifact_name = ""
        self.artifact_type = "exe"       # exe / staticLib / sharedLib
        self.prefix = ""                 # 交叉工具链前缀
        self.c_compiler = "gcc"
        self.cpp_compiler = "g++"
        self.include_paths = []          # -I
        self.defines = []                # -D
        self.libs = []                   # -l
        self.lib_paths = []              # -L
        self.c_flags = []
        self.cpp_flags = []
        self.common_flags = []           # 优化/arch/fpu 等公共标志
        self.linker_flags = []
        self.post_build = ""

    def all_c_flags(self):
        return self.common_flags + self.c_flags

    def all_cpp_flags(self):
        return self.common_flags + self.cpp_flags


def parse_arm_and_optimization(superclass, value, cfg):
    """把 ARM/优化/调试 类枚举选项翻译为编译标志, 累加到 cfg.common_flags。"""
    sc = superclass or ""
    val = value or ""

    # 优化等级
    for key, flag in OPT_LEVEL_MAP.items():
        if val.endswith(key) or sc.endswith(key):
            if flag and flag not in cfg.common_flags:
                cfg.common_flags.append(flag)
            return True

    # 调试等级
    for key, flag in DEBUG_LEVEL_MAP.items():
        if val.endswith(key):
            if flag and flag not in cfg.common_flags:
                cfg.common_flags.append(flag)
            return True

    # ARM -mcpu
    m = ARM_MCPU_RE.search(val)
    if m:
        cfg.common_flags.append("-mcpu=" + m.group(1))
        return True
    # ARM -march
    m = ARM_ARCH_RE.search(val)
    if m:
        cfg.common_flags.append("-march=" + m.group(1))
        return True
    # -mfpu
    m = ARM_FPU_RE.search(val)
    if m and "abi" not in val:
        cfg.common_flags.append("-mfpu=" + m.group(1))
        return True
    # -mfloat-abi
    m = ARM_FLOATABI_RE.search(val)
    if m:
        cfg.common_flags.append("-mfloat-abi=" + m.group(1))
        return True
    # thumb / arm 指令集
    m = ARM_INSTR_RE.search(val)
    if m:
        iset = m.group(1)
        if iset == "thumb":
            cfg.common_flags.append("-mthumb")
        elif iset == "arm":
            cfg.common_flags.append("-marm")
        return True

    return False


# 布尔类 -f 选项的常见映射(仅在 value="true" 时启用)
BOOL_FLAG_MAP = {
    "optimization.signedchar": "-fsigned-char",
    "optimization.functionsections": "-ffunction-sections",
    "optimization.datasections": "-fdata-sections",
    "optimization.nocommon": "-fno-common",
    "optimization.noinlinefunctions": "-fno-inline-functions",
    "optimization.freestanding": "-ffreestanding",
    "optimization.nobuiltin": "-fno-builtin",
    "optimization.PIC": "-fPIC",
    "warnings.allwarn": "-Wall",
    "warnings.extrawarn": "-Wextra",
    "warnings.pedantic": "-pedantic",
    "warnings.toerrors": "-Werror",
}


def parse_bool_flag(superclass, value, cfg):
    if (value or "").lower() != "true":
        return False
    sc = superclass or ""
    for key, flag in BOOL_FLAG_MAP.items():
        if sc.endswith(key):
            if flag not in cfg.common_flags:
                cfg.common_flags.append(flag)
            return True
    return False


def artifact_type_from_string(s):
    s = s or ""
    if "staticLib" in s:
        return "staticLib"
    if "sharedLib" in s:
        return "sharedLib"
    return "exe"


def parse_option(opt, cfg, proj_name):
    """解析单个 <option> 节点。"""
    sc = opt.get("superClass", "") or opt.get("id", "")
    vtype = opt.get("valueType", "")
    value = opt.get("value", "")

    # 列表类
    listvals = [lv.get("value", "") for lv in opt if strip_ns(lv.tag) == "listOptionValue"]

    if vtype == "includePath":
        for v in listvals:
            rv = resolve_eclipse_vars(v, proj_name)
            if rv and rv not in cfg.include_paths:
                cfg.include_paths.append(rv)
        return
    if vtype == "definedSymbols":
        for v in listvals:
            v = (v or "").strip()
            if v and v not in cfg.defines:
                cfg.defines.append(v)
        return
    if vtype == "libs":
        for v in listvals:
            v = (v or "").strip()
            if v and v not in cfg.libs:
                cfg.libs.append(v)
        return
    if vtype == "libPaths":
        for v in listvals:
            rv = resolve_eclipse_vars(v, proj_name)
            if rv and rv not in cfg.lib_paths:
                cfg.lib_paths.append(rv)
        return
    if vtype == "stringList":
        # 可能是额外的链接对象/标志
        for v in listvals:
            rv = resolve_eclipse_vars(v, proj_name)
            if rv:
                cfg.linker_flags.append(rv)
        return

    # 工具链前缀 / 编译器命令
    if sc.endswith("command.prefix"):
        cfg.prefix = value or cfg.prefix
        return
    if sc.endswith("option.command.c"):
        cfg.c_compiler = value or cfg.c_compiler
        return
    if sc.endswith("option.command.cpp"):
        cfg.cpp_compiler = value or cfg.cpp_compiler
        return

    # 其它编译/链接标志 (string 类型)
    if vtype == "string" or (not vtype and value):
        if sc.endswith("c.compiler.other"):
            _extend_flags(cfg.c_flags, value)
            return
        if sc.endswith("cpp.compiler.other"):
            _extend_flags(cfg.cpp_flags, value)
            return
        if sc.endswith("c.linker.other") or sc.endswith("cpp.linker.other"):
            _extend_flags(cfg.linker_flags, value)
            return
        # 语言标准
        if "std" in sc and value.startswith("-std"):
            _extend_flags(cfg.common_flags, value)
            return

    # 枚举: 优化 / ARM / 调试
    if vtype == "enumerated":
        parse_arm_and_optimization(sc, value, cfg)
        return

    # 布尔: -f 类
    if vtype == "boolean":
        parse_bool_flag(sc, value, cfg)
        return


def _extend_flags(target, value):
    if not value:
        return
    for tok in value.split():
        tok = tok.strip()
        if tok and tok not in target:
            target.append(tok)


def parse_tool(tool, cfg, proj_name):
    for opt in tool:
        if strip_ns(opt.tag) == "option":
            parse_option(opt, cfg, proj_name)


def parse_configuration(config_elem, proj_name):
    """解析 <configuration> 节点为 Configuration 对象。"""
    cfg = Configuration(config_elem.get("name", "default"))
    cfg.artifact_name = config_elem.get("artifactName", "") or proj_name
    cfg.artifact_type = artifact_type_from_string(config_elem.get("buildArtefactType", ""))
    cfg.post_build = config_elem.get("postbuildStep", "") or ""

    # artifactName 里可能含 ${ProjName}
    cfg.artifact_name = cfg.artifact_name.replace("${ProjName}", proj_name)

    # 遍历 folderInfo/toolChain/tool
    for folder in config_elem.iter():
        tag = strip_ns(folder.tag)
        if tag == "toolChain":
            # toolChain 级 option (前缀/优化/arm 等常挂在这里)
            for opt in folder:
                if strip_ns(opt.tag) == "option":
                    parse_option(opt, cfg, proj_name)
        elif tag == "tool":
            parse_tool(folder, cfg, proj_name)

    return cfg


def parse_cproject(cproject_path, proj_name):
    tree = ET.parse(cproject_path)
    root = tree.getroot()
    configs = []
    for cfg_elem in root.iter():
        if strip_ns(cfg_elem.tag) == "configuration":
            # 只取 cdtBuildSystem 下真正的 configuration(带 artifactName/name)
            if cfg_elem.get("name") and cfg_elem.get("buildProperties") is not None:
                configs.append(parse_configuration(cfg_elem, proj_name))
    # 去重(按 name)
    seen = set()
    uniq = []
    for c in configs:
        if c.name not in seen:
            seen.add(c.name)
            uniq.append(c)
    return uniq


def get_project_name(project_dir):
    pfile = os.path.join(project_dir, ".project")
    if os.path.isfile(pfile):
        try:
            tree = ET.parse(pfile)
            for el in tree.getroot().iter():
                if strip_ns(el.tag) == "name":
                    if el.text and el.text.strip():
                        return el.text.strip()
        except ET.ParseError:
            pass
    return os.path.basename(os.path.abspath(project_dir)) or "project"


# ---------------------------------------------------------------------------
# CMake 生成
# ---------------------------------------------------------------------------
def cmake_list(items, indent="        "):
    return "\n".join(indent + i for i in items)


def gen_config_block(cfg, is_multi):
    """为单个配置生成 CMake 片段(内含目标定义)。"""
    lines = []
    tgt = cfg.artifact_name or "app"

    # 交叉编译器
    if cfg.prefix:
        lines.append('    set(CMAKE_C_COMPILER   "{}{}")'.format(cfg.prefix, cfg.c_compiler))
        lines.append('    set(CMAKE_CXX_COMPILER "{}{}")'.format(cfg.prefix, cfg.cpp_compiler))
        lines.append("")

    # 编译标志
    if cfg.all_c_flags():
        lines.append('    set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} {}")'.format(" ".join(cfg.all_c_flags())))
    if cfg.all_cpp_flags():
        lines.append('    set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} {}")'.format(" ".join(cfg.all_cpp_flags())))
    if cfg.linker_flags:
        lines.append('    set(CMAKE_EXE_LINKER_FLAGS "${{CMAKE_EXE_LINKER_FLAGS}} {}")'.format(" ".join(cfg.linker_flags)))
    if lines and lines[-1] != "":
        lines.append("")

    # 目标定义
    if cfg.artifact_type == "staticLib":
        lines.append("    add_library({} STATIC ${{SOURCES}})".format(tgt))
    elif cfg.artifact_type == "sharedLib":
        lines.append("    add_library({} SHARED ${{SOURCES}})".format(tgt))
    else:
        lines.append("    add_executable({} ${{SOURCES}})".format(tgt))
    lines.append("")

    # 头文件路径
    if cfg.include_paths:
        lines.append("    target_include_directories({} PRIVATE".format(tgt))
        lines.append(cmake_list(cfg.include_paths))
        lines.append("    )")
        lines.append("")

    # 宏定义
    if cfg.defines:
        lines.append("    target_compile_definitions({} PRIVATE".format(tgt))
        lines.append(cmake_list(cfg.defines))
        lines.append("    )")
        lines.append("")

    # 库搜索路径
    if cfg.lib_paths:
        lines.append("    target_link_directories({} PRIVATE".format(tgt))
        lines.append(cmake_list(cfg.lib_paths))
        lines.append("    )")
        lines.append("")

    # 链接库
    if cfg.libs:
        lines.append("    target_link_libraries({} PRIVATE".format(tgt))
        lines.append(cmake_list(cfg.libs))
        lines.append("    )")
        lines.append("")

    # 目标输出名
    if tgt != cfg.artifact_name and cfg.artifact_name:
        lines.append('    set_target_properties({} PROPERTIES OUTPUT_NAME "{}")'.format(tgt, cfg.artifact_name))
        lines.append("")

    # postbuild (如 strip)
    if cfg.post_build:
        pb = cfg.post_build.replace("${ProjName}", cfg.artifact_name)
        lines.append("    # Eclipse postbuildStep: {}".format(pb))
        lines.append("    add_custom_command(TARGET {} POST_BUILD".format(tgt))
        lines.append('        COMMAND {}'.format(pb))
        lines.append('        COMMENT "Post-build step from Eclipse")')
        lines.append("")

    return "\n".join(lines)


def generate_cmake(proj_name, configs, selected=None, source_exts=None):
    if source_exts is None:
        source_exts = ["c", "cc", "cpp", "cxx", "C", "s", "S", "asm"]

    out = []
    out.append("# ============================================================")
    out.append("# CMakeLists.txt  (由 eclipse2cmake.py 从 Eclipse CDT 工程生成)")
    out.append("# 工程名: {}".format(proj_name))
    out.append("# 源工程: .project / .cproject")
    out.append("# ============================================================")
    out.append("cmake_minimum_required(VERSION 3.13)")
    out.append("")

    # 交叉编译时通常需要在 project() 前设定编译器; 这里把编译器设定放进
    # 各配置块, 并将 project() 声明为 NONE 后再 enable 语言, 以兼容交叉工具链。
    out.append("# 交叉编译: 编译器在下方各配置块中按 .cproject 设定。")
    out.append("project({} C CXX ASM)".format(proj_name))
    out.append("")

    # 源文件收集
    exts_glob = " ".join('"${{CMAKE_SOURCE_DIR}}/src/*.{}"'.format(e) for e in source_exts)
    out.append("# ------------------------------------------------------------")
    out.append("# 源文件收集")
    out.append("#   默认递归收集 src/ 下的源码。如工程源码不在 src/,")
    out.append("#   请修改下面的 GLOB 根路径。")
    out.append("# ------------------------------------------------------------")
    globs = "\n".join(
        '    "${{CMAKE_SOURCE_DIR}}/src/*.{ext}"\n'
        '    "${{CMAKE_SOURCE_DIR}}/src/**/*.{ext}"'.format(ext=e) for e in source_exts
    )
    out.append("file(GLOB_RECURSE SOURCES")
    out.append(globs)
    out.append(")")
    out.append("")
    out.append("if(NOT SOURCES)")
    out.append('    message(WARNING "未在 ${CMAKE_SOURCE_DIR}/src 下找到源文件, 请检查路径。")')
    out.append("endif()")
    out.append("")

    # 配置选择
    if selected is not None:
        cfgs = [c for c in configs if c.name == selected]
        if not cfgs:
            raise SystemExit("找不到配置: {} (可用: {})".format(
                selected, ", ".join(c.name for c in configs)))
        out.append("# ------------------------------------------------------------")
        out.append("# 配置: {}".format(selected))
        out.append("# ------------------------------------------------------------")
        out.append(gen_config_block(cfgs[0], is_multi=False))
    else:
        # 多配置: 用 BUILD_CONFIG 变量选择
        default = configs[0].name if configs else "default"
        out.append("# ------------------------------------------------------------")
        out.append("# 多构建配置: 用 -DBUILD_CONFIG=<名称> 选择 (默认 {})".format(default))
        out.append("# 可选: {}".format(", ".join(c.name for c in configs)))
        out.append("# ------------------------------------------------------------")
        out.append('set(BUILD_CONFIG "{}" CACHE STRING "选择要构建的 Eclipse 配置")'.format(default))
        out.append('set_property(CACHE BUILD_CONFIG PROPERTY STRINGS {})'.format(
            " ".join(c.name for c in configs)))
        out.append("")
        first = True
        for c in configs:
            kw = "if" if first else "elseif"
            first = False
            out.append('{}(BUILD_CONFIG STREQUAL "{}")'.format(kw, c.name))
            out.append('    message(STATUS "构建配置: {}")'.format(c.name))
            out.append(gen_config_block(c, is_multi=True))
        out.append('else()')
        out.append('    message(FATAL_ERROR "未知 BUILD_CONFIG=${BUILD_CONFIG}")')
        out.append("endif()")

    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(
        description="把 Eclipse CDT (.project/.cproject) 工程转换为 CMakeLists.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("project_dir", nargs="?", default=".",
                    help="Eclipse 工程目录 (含 .cproject), 默认当前目录")
    ap.add_argument("-o", "--output", help="输出文件 (默认 <工程>/CMakeLists.txt)")
    ap.add_argument("-c", "--config", help="只导出指定配置(如 ReleaseC0)")
    ap.add_argument("--list", action="store_true", help="仅列出所有配置后退出")
    ap.add_argument("--stdout", action="store_true", help="输出到标准输出")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的输出文件")
    args = ap.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    cproject = os.path.join(project_dir, ".cproject")
    if not os.path.isfile(cproject):
        sys.exit("错误: 在 {} 下找不到 .cproject 文件".format(project_dir))

    proj_name = get_project_name(project_dir)
    configs = parse_cproject(cproject, proj_name)

    if not configs:
        sys.exit("错误: .cproject 中未解析到任何构建配置")

    if args.list:
        print("工程名: {}".format(proj_name))
        print("配置数: {}".format(len(configs)))
        for c in configs:
            print("  - {:20s} 目标={:12s} 类型={:9s} 前缀={}".format(
                c.name, c.artifact_name, c.artifact_type, c.prefix or "(无)"))
        return

    text = generate_cmake(proj_name, configs, selected=args.config)

    if args.stdout:
        sys.stdout.write(text)
        return

    out_path = args.output or os.path.join(project_dir, "CMakeLists.txt")
    if os.path.exists(out_path) and not args.force:
        sys.exit("错误: {} 已存在。用 --force 覆盖或 -o 指定其它文件。".format(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("已生成: {}".format(out_path))
    print("工程: {}  配置: {}".format(
        proj_name, args.config or "全部({})".format(len(configs))))


if __name__ == "__main__":
    main()
