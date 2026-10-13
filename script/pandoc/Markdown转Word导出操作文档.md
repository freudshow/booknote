# Markdown 转 Word（.docx）完整操作文档

本文档记录如何将 `测试方案.md`（Markdown）导出为 Word 文档，并确保：
1. HTML/Markdown 表格全部导出为 **Word 原生表格**（`<w:tbl>`），而不是"行 + 分割线（`---`）"文本形式；
2. 所有表格的边框**全部画全（all borders）**：外边框 + 内部横线/竖线。

主要工具为 **pandoc**（已验证环境已安装 `pandoc`）。文档末尾附上用到的 Python 脚本全文，供再次使用或调整。

---

## 1. 环境与工具

| 工具 | 用途 |
|---|---|
| pandoc | Markdown → Word 转换 |
| Python 3 | 修改参考文档 styles.xml（加边框）、重新打包 docx |
| WinRAR / 或 PowerShell Expand-Archive | 解压/查看 docx 内容（验证用） |

路径约定（按本仓库实际使用）：
- Markdown 源文件：`documents/测试方案.md`
- 导出 Word 文件：`documents/可视化组态配置工具测试方案.docx`
- 参考文档（reference.docx，用于定制表格样式）：由 pandoc 内置模板导出，放在临时目录

---

## 2. 一次性准备：生成"全边框"参考文档

Word 的表格边框由 `word/styles.xml` 中 `Table` 样式的 `<w:tblBorders>` 决定。pandoc 默认的 `Table` 样式**只有表头底边框**，其余边框不显示。因此需生成一个修改过边框的参考文档（reference.docx），供后续每次导出使用。

### 2.1 导出 pandoc 默认参考文档模板

```powershell
# 在任意目录执行，生成 pandoc 内置 reference.docx 模板
pandoc -o ref.docx --print-default-data-file reference.docx
```

> 更稳妥的方式（无需 --print-default-data-file）：
> ```powershell
> pandoc -o ref.docx --print-default-data-file=reference.docx
> ```
> 两者等价，二选一即可。

### 2.2 解压参考文档

docx 本质是一个 zip 包。将其解压后修改 `word/styles.xml`。

```powershell
# 复制一份并改扩展名为 .zip，再用资源管理器/PowerShell 解压
Copy-Item ref.docx ref.zip
Expand-Archive ref.zip -DestinationPath refdir
# 实际结构为 refdir/word/styles.xml
```

（也可直接用 WinRAR / 7-Zip 打开 ref.docx 并提取 word/styles.xml，改完再拖回替换。）

### 2.3 在 Table 样式中加入全部边框

打开 `refdir/word/styles.xml`，找到 `Table` 样式（`w:styleId="Table"`）。在其中的 `<w:tblPr>` 开始标签（`<w:tblPr>`）之后，插入如下 `<w:tblBorders>`：

```xml
<w:tblBorders>
  <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>
  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>
</w:tblBorders>
```

各子元素含义：
- `top` / `left` / `bottom` / `right`：表格**外边框**（上、左、下、右）；
- `insideH`：**内部横线**（行与行之间的分隔线）；
- `insideV`：**内部竖线**（列与列之间的分隔线）；
- `w:val="single"`：实线；
- `w:sz="4"`：线宽 0.5 磅（可依需要调大，如 `8`）；
- `w:color="000000"`：黑色（可改为其他颜色）。

> 手工编辑原件很繁琐，推荐直接用 3.3 节的 Python 脚本自动插入，避免改错位置。

### 2.4 重新打包为参考文档

修改完成后，把解压目录重新打包成 `.docx`。注意：`[Content_Types].xml` 应位于 zip 首位，否则个别 Word 版本可能报错。详见 3.3 节 `repack.py`。

---

## 3. 自动脚本（推荐）

以下三个 Python 脚本可一步完成：改边框、重新打包。脚本可直接放入临时工作目录运行。

### 3.1 `add_borders.py` — 给 Table 样式加全部边框

```python
import os, re, shutil, zipfile

SRC_DIR = r"C:\Users\floyd\AppData\Local\Temp\opencode\refdir\unz"
STYLES = os.path.join(SRC_DIR, "word", "styles.xml")

with open(STYLES, "r", encoding="utf-8") as f:
    styles = f.read()

# The full border set to inject into <w:tblPr> of the Table style
table_borders = (
    '      <w:tblBorders>\n'
    '        <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '        <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '        <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '        <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '        <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
    '      </w:tblBorders>\n'
)

# Find the Table style block
idx = styles.index('styleId="Table"')
start = styles.rindex('<w:style', 0, idx)
end = styles.index('</w:style>', idx)
block = styles[start:end + 11]

# Insert tblBorders right after the opening <w:tblPr> within the Table style
new_block = None
m = re.search(r'(<w:tblPr>)', block)
if m:
    insert_at = m.end()
    new_block = block[:insert_at] + "\n" + table_borders + block[insert_at:]
else:
    raise RuntimeError("tblPr not found in Table style")

styles = styles[:start] + new_block + styles[end + 11:]

with open(STYLES, "w", encoding="utf-8") as f:
    f.write(styles)

print("Table style updated with all borders")
```

### 3.2 `repack.py` — 把解压目录重新打包为 .docx

```python
import os, zipfile

SRC_DIR = r"C:\Users\floyd\AppData\Local\Temp\opencode\refdir\unz"
OUT = r"C:\Users\floyd\AppData\Local\Temp\opencode\ref_bordered.docx"

# Repackage the docx - order matters: [Content_Types].xml first, then _rels, then word
def add_dir(zf, base, path=""):
    entries = sorted(os.listdir(base))
    for e in entries:
        full = os.path.join(base, e)
        rel = (path + "/" + e).lstrip("/")
        if os.path.isdir(full):
            add_dir(zf, full, rel)
        else:
            zf.write(full, rel)

if os.path.exists(OUT):
    os.remove(OUT)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    # ensure [Content_Types].xml is first
    zf.write(os.path.join(SRC_DIR, "[Content_Types].xml"), "[Content_Types].xml")
    # then _rels contents, then everything else
    rels_dir = os.path.join(SRC_DIR, "_rels")
    if os.path.isdir(rels_dir):
        for e in sorted(os.listdir(rels_dir)):
            zf.write(os.path.join(rels_dir, e), "_rels/" + e)
    # everything except [Content_Types].xml and _rels/ (already added)
    for root, dirs, files in os.walk(SRC_DIR):
        for d in list(dirs):
            if d == "_rels" and os.path.normpath(root) == os.path.normpath(SRC_DIR):
                dirs.remove(d)
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, SRC_DIR)
            if rel == "[Content_Types].xml":
                continue
            if rel.startswith("_rels"):
                continue
            zf.write(full, rel)

print("repackaged:", OUT, os.path.getsize(OUT))
```

### 3.3 使用步骤（汇总）

```powershell
# 1) 生成参考模板并解压
python -c "import shutil"  # 可选校验 python 可用
pandoc -o ref.docx --print-default-data-file reference.docx
Copy-Item ref.docx ref.zip
Expand-Archive ref.zip -DestinationPath refdir

# 2) 修改 styles.xml：把 refdir/word/styles.xml 复制到解压根 refdir\unz（按脚本 SRC_DIR 约定）
#    实际脚本中 SRC_DIR 直接指向 refdir\unz\word\styles.xml 所在目录
#    若目录名不同，先修改脚本里的 SRC_DIR 路径

# 3) 运行加边框脚本 + 重新打包
python add_borders.py
python repack.py   # 生成 ref_bordered.docx
```

> 说明：脚本中 `SRC_DIR` / `OUT` 是写死的临时路径。换成自己的环境时，请同步修改这两个变量。`add_borders.py` 要求 `SRC_DIR/word/styles.xml` 存在；`repack.py` 把 `SRC_DIR` 整个目录打包成 `OUT`。

---

## 4. 导出 Word 文档（核心命令）

参考文档准备好后，每次导出都执行下面一条命令即可：

```powershell
# 工作目录：仓库根目录 D:\repo\dfe\LinuxApp\visulconfig
pandoc "documents/测试方案.md" `
  -o "documents/可视化组态配置工具测试方案.docx" `
  --reference-doc="C:\path\to\ref_bordered.docx" `
  --toc `
  --toc-depth=2
```

参数说明：
- `documents/测试方案.md`：**输入**的 Markdown 源文件；
- `-o documents/可视化组态配置工具测试方案.docx`：**输出** Word 文件路径；
- `--reference-doc=...`：指定带全边框 Table 样式的参考文档（关键！不加则边框不全）；
- `--toc`：生成**目录**；
- `--toc-depth=2`：目录显示到二级标题。

> 若使用 CMD（非 PowerShell），把反引号 `` ` `` 换成 `^`，或直接写成一行。

### 4.1 表格导出保证

pandoc 默认会把标准 Markdown 管道表格（`| 列1 | 列2 |`）转换为 Word **原生表格**（`<w:tbl>`），不会产生"行 + 分割线（`---`）"文本形式。前提是 Markdown 中的表格是**标准管道表格**。若表格写成多行文本形式，pandoc 会当作普通文本处理，从而出现"行 + 分割线"。因此请保证源 `.md` 中表格为规范管道表格。

---

## 5. 导出结果验证（可选）

可用 PowerShell 解压导出的 docx，检查表格是否为原生表格且边框完整：

```powershell
# 解压导出文档
Copy-Item "documents/可视化组态配置工具测试方案.docx" verify.zip
Expand-Archive verify.zip -DestinationPath verify

# 检查：统计原生表格数量 <w:tbl>
$xml = Get-Content "verify/word/document.xml" -Raw -Encoding UTF8
"原生表格数 (w:tbl): " + ([regex]::Matches($xml, '<w:tbl>')).Count

# 检查：Table 样式中是否有全部边框定义（应看到 insideH/insideV 等）
$styles = Get-Content "verify/word/styles.xml" -Raw -Encoding UTF8
$styles.Contains('<w:insideH') -and $styles.Contains('<w:insideV')

# 检查：可见文本中是否残留 "---" 分割线（应为 0）
$clean = [regex]::Replace($xml, '<[^>]+>', ' ')
"字面 '---' 数量: " + ([regex]::Matches($clean, '---')).Count
```

---

## 6. 用到的命令速查（复制即用）

**一次性准备参考文档（含脚本）：**
```powershell
pandoc -o ref.docx --print-default-data-file reference.docx
Copy-Item ref.docx ref.zip
Expand-Archive ref.zip -DestinationPath refdir
python add_borders.py
python repack.py
```

**每次导出：**
```powershell
pandoc "documents/测试方案.md" -o "documents/可视化组态配置工具测试方案.docx" --reference-doc="C:\path\to\ref_bordered.docx" --toc --toc-depth=2
```

**验证：**
```powershell
Copy-Item "documents/可视化组态配置工具测试方案.docx" verify.zip
Expand-Archive verify.zip -DestinationPath verify
```

---

## 7. 常见问题

| 问题 | 原因 / 解决 |
|---|---|
| 导出后表格没有边框 | 未使用 `--reference-doc`，或参考文档 Table 样式没加 `w:tblBorders`；改用带边框的参考文档重新导出 |
| 表格显示为"行 + 分割线（`---`）" | 源 Markdown 表格不是标准管道表格；把表格写成 `\| 列1 \| 列2 \|` 形式 |
| 重新打包后 Word 提示损坏 | `[Content_Types].xml` 未放在 zip 首位；改用第 3.2 节的 `repack.py` |
| 改边框后没生效 | 确认改的是 `word/styles.xml` 中 `styleId="Table"` 的 `tblPr`，且改完重新打包、重新导出 |
| 想要更粗/彩色边框 | 调整 `w:sz`（线宽）与 `w:color`（颜色）值 |

---

*文档生成时间：2026-09-03*
