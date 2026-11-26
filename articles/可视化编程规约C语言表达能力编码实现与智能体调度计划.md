# 可视化编程规约 C 语言表达能力：编码实现计划与智能体调度协议

> 日期：2026-11-26
>
> 配套设计方案：[可视化编程规约 C 语言表达能力演进方案](可视化编程规约C语言表达能力演进方案.md)
>
> 配套 Wave 0 共享契约：`D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/`

---

## 文档定位

本文把演进方案拆解为一套**可直接交付轻量模型（如 Gemini Hydrogen 等快速小模型）并行编码、并由主控编程智能体统一调度与验收**的工程落地手册，包含两部分：

1. **第一部分（第 1～7 章）**：覆盖 P0～P6 的完整分层编码实现计划，细化到模块目录、文件、核心接口、避坑约束和可执行的交付测试。
2. **第二部分（第 8～13 章）**：面向主控编程智能体的调度分配方案，包含模型分级路由、并行波次 DAG、上下文与 KV-Cache 预算、**防降智与主动开新窗口交接协议**、L1～L3 自动门禁，以及 Wave 1 可直接派发的标准任务单模板。

---

# 第一部分：面向轻量模型的分层编码实现计划

## 1. 所有轻量模型必须遵守的工程防呆红线

轻量模型在复杂工程中容易出错的根因通常有四类：猜接口、用错语言版本语法、并发改共享工程文件、缺少可执行验收标准。因此，所有原子任务统一执行以下硬约束：

| 约束维度 | 强制规则 | 目的 |
| --- | --- | --- |
| **任务粒度** | 每个原子任务只写 **1～3 个新文件**、核心代码 **150～400 行** + 独立单元测试 | 防止轻量模型上下文过载或漏掉边界分支 |
| **C# 兼容边界** | 严格限定 **C# 7.3 / .NET Framework 4.8**；禁止文件级 `namespace`、`record`、`init`、`[]` 集合表达式、`string?`、原始字符串；使用 Allman 独占行大括号、4 空格缩进、完整中文 XML 注释 | 适配经典非 SDK `.csproj`，确保 `MSBuild.exe` 零语法报错 |
| **C99 兼容边界** | 严格遵循 **C99**；桌面宿主编译强制 `-std=c99 -Wall -Wextra -Werror -pedantic`；`vcl_package` / `vcl_verify` / `vcl_vm` 不直接 `#include` 嵌入式平台头（通过接口注入）；扫描执行期严禁 `malloc` | 保证同一套 C 源码既能在桌面宿主对拍，又能直接进入 ARM 产品构建 |
| **共享文件隔离** | 轻量模型**严禁直接修改** `LogicEngineConfigTool.csproj`、`LogicEngineConfigTool.RegressionTests.csproj`、`Program.cs`、`VisualEditorViewModel.cs`、`logic_visual_programming.c`、`.cproject` | 消除并行写冲突；由主控智能体在波次汇聚点统一登记与接线 |
| **临时文件隔离** | 所有测试临时文件与 C 宿主编译产物一律放在仓库根 `temp/<task-id>/`；严禁读写 `visualconfig/work/`；运行 Python 校验时加 `-B` 避免生成 `__pycache__` | 严格遵守仓库临时目录规则 |
| **Legacy 零回归** | 不修改既有 `TransactionalConfigSaveService`、`CommonFunctions` 与 `c%02d57.json` 的存量语义 | 保证现场已有配置与回归用例不受影响 |

---

## 2. 阶段 P0：存量基线与安全加固（M01，门槛 G0）

> 可与 P1/P2 离线原型并行推进。

| 任务号 | 负责模块与目标文件 | 实现细节 | 交付测试与通过标准 |
| --- | --- | --- | --- |
| **T0.1** | 双端兼容矩阵（`contracts/legacy/compat_matrix.json`） | 按产品构建（C0/C1）、40 个固件注册 `Type`、参数键及已知差异（`YK/YT Method=3`、`DEBUG_PRINT PrintEdge=4`、`ALGO_INTEGRAL IntervalUnit` 缺失、计次 `WHILE` 回边）建立三态清单（`Supported` / `Rejected` / `Unknown`） | Python Schema 检查：40 个固件元件与 49 个桌面生产元件全覆盖 |
| **T0.2** | 固件跳转与越界加固（`linuxttu/src/logicengine/logic_visual_programming.c`、`elements/element_flow.c`） | 1) 在 `VisualProg_ValidateTask` 补充校验 `IF`（`TrueNextID`/`FalseNextID`）、`SWITCH`（`Cases[].NextID`/`DefaultNextID`）、`WHILE`（`ContinueNextID`/`ExitNextID`）目标必须为 `-1` 或已注册 `0..499`；<br>2) `VisualProg_TaskThread` 访问 `arrIdToIndex[nextId]` 前先判 `nextId >= 0 && nextId < LOGIC_MAX_ELEMENTS_PER_TASK` | C 宿主单测：注入 `TrueNextID=999`、`nextId=500`、指向不存在元件 ID 的 JSON，验证加载返回 `-1` 且不启线程 |
| **T0.3** | 固件超限拒绝与表达式失败拦截（`logic_visual_programming.c`、`elements/element_arithmetic.c`） | 1) `ParseLogicTasksFromJson` 中 `elemCount > 500` 改为释放并返回 `-1`（不再静默截断）；<br>2) `Expression_ParseConfig` 中 `get_newEvaluatorKSH` 返回 `NULL` 时返回 `1` 拒绝加载 | C 宿主单测：501 元件配置与非法表达式配置加载均被拒绝，且原有活动上下文不受影响 |
| **T0.4** | 桌面既有回归基线冻结 | 在 `visualconfig` 根目录运行 Debug 构建、无参全量回归及独立专题套件 | `MSBuild.exe` 与全套 `RegressionTests.exe`（无参 + `--single-file-editor-snapshot-only` + `--control-flow-jump-only` + `--realtime-storage-order-only` + `--new-elements-memory-only`）全部退出码 `0` |

---

## 3. 阶段 P1：共享契约冻结（M00，门槛 G1 — 已生成 Wave 0 基线）

> **原则**：共享契约由主控/架构师先行冻结，轻量模型严格照表实现，不自行发明字段名、操作码或错误码。

Wave 0 契约已落盘于 `D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/`：

| 任务号 | 权威文件 | 已冻结内容 | 验收方式 |
| --- | --- | --- | --- |
| **T1.1** | `grammar_p2.ebnf`<br>`types_and_errors.json` | P2 文法与 8 级优先级、4 类 P2 标量（`bool/i32/u32/f64`）与 3 类 P3 预留标量、10 条显式转换规则、故障检查 4 级优先级（取消 → 截止期 → 步数 → 动态检查）、11 个运行错误码（`OK(0)`～`HOST_FAILURE(11)`）及 10 个阶段诊断码 | `python -B contracts/vcl/v1/validate_contracts.py` 退出码 `0` |
| **T1.2** | `opcodes_p2.json`<br>`package_schema_v1.json` | 51 条按类型拆分的明确 `u16` 操作码（避免栈机多态推断，大幅降低小模型出错率）、基本块边界空栈约定、P2 前向无环跳转约束及严格禁止未知字段的 JSON Schema | 同上 |
| **T1.3** | `profile_offline_p2.json` | 离线档案 `offline-reference-p2`：允许版本白名单、`binary64` 浮点纪律（禁 `fastMath`/`fmaFusion`）、前端/容器/运行全部正数上限 | 同上 |
| **T1.4** | `sample_packages_p2.json`<br>`golden_vectors_p2.json` | 3 个手工构造并经脚本模拟验证的合法最小包（`pkg_p2_weighted_clamp`、`pkg_p2_div_by_a`、`pkg_p2_branch_merge_init`）、6 个畸形负例包（含 `P2-06B`、未知 opcode、后向跳转、欠栈、`P2-09` 未初始化汇合、自报资源偏小）及 22 条 P2 黄金向量 | 脚本独立验证全部合法/畸形包并运行 `P2-01`～`P2-08` 断言全部通过 |

---

## 4. 阶段 P2：最小纵向贯通（离线纯 `SCRIPT` 端到端，门槛 G2）

> **目标**：贯通“源工程 → 前端 → 后端 → C 独立验证器 → C VM ↔ C# 参考解释器对拍”，零真实设备输出。拆分为 **14 个原子任务**。

### 4.1 源工程与快照（M02，`LogicEngineConfigTool/Services/Vcl/Source/`）

- **T2.01 — 源工程模型与规范化摘要（`VclSourceModels.cs`、`VclSourceDigest.cs`）**
  - 定义 `VclSourceProject`（`Format = "vcl-source"`、`SchemaVersion = "1.0"`、`DocumentId`、`SemanticInputs`、`EditorView`）、`VclSourceSnapshot`（深拷贝不可变快照）、`VclScriptBlock`。
  - `VclSourceDigest.ComputeSha256(VclSourceSnapshot)`：仅对 `SemanticInputs` 按规范化 UTF-8（键名 Ordinal 排序、集合按稳定 ID 排序、脚本保留原换行与注释）计算 SHA-256，**显式排除 `EditorView`**。
  - **交付测试**：`VclSourceDigestTests.cs` —— 仅挪动坐标不改变摘要；改一个脚本字符、参数类型或能力档案摘要必变；重复计算 10 次结果严格一致。
- **T2.02 — 源工程原子读写与导出缓存检查（`VclSourceProjectStore.cs`）**
  - `OpenSource(byte[] bytes)`：开启 `DuplicatePropertyNameHandling.Error`，拒绝含 `$type` 或未知 `SchemaVersion` 的输入。
  - `SaveSource(VclSourceProject draft, string path)`：允许保存含语法错误的草稿；写同目录 `.tmp` → 回读校验结构与 `DocumentId` → `File.Replace` / `File.Move`。
  - `VclExportCacheValidator`：核对导出包中的 `SourceDigest` 与当前源快照摘要是否匹配，不匹配报 `VCL_SRC_STALE_EXPORT_DIGEST`（覆盖 `P2-06A`）。
  - **交付测试**：`VclSourceStoreTests.cs` —— 错误脚本保存再打开无损；模拟替换失败不破坏原文件；修改脚本后拒绝发布旧包。

### 4.2 VCL 语言前端（M03，`LogicEngineConfigTool/Services/Vcl/Language/`）

- **T2.03 — 统一诊断、UTF-8 偏移映射与词法分析器（`VclDiagnostic.cs`、`VclToken.cs`、`VclLexer.cs`）**
  - `VclDiagnostic` 严格对齐 `types_and_errors.json` 的 `diagnosticSchema`。
  - `Utf8SpanMapper.ToUtf16Span(string source, int startByte, int endByte)` 将 UTF-8 左闭右开字节区间精准转为 WPF 的 UTF-16 `(StartChar, Length)`。
  - `VclLexer`：强制检查 `maxSourceBytes` 与 `maxTokens`；识别 P2 关键字、ASCII 标识符、`.` 固定小数点字面量、`//` 与非嵌套 `/* */` 注释（允许 UTF-8）；对 `++`/`--`/`+=` 等报 `VCL_LEX_UNSUPPORTED_OPERATOR`。
  - **交付测试**：`VclLexerTests.cs` —— 含中文注释后的精确 UTF-8 与 UTF-16 偏移、超字节/超 Token 限额拒绝、未闭合块注释与非法运算符报错。
- **T2.04 — P2 递归下降语法分析器与 AST（`VclAst.cs`、`VclParser.cs`）**
  - 严格按 `grammar_p2.ebnf` 的 8 级优先级解析，左结合二元运算，限制 `maxAstDepth`（默认 64）。
  - 禁止表达式内赋值、链式赋值与尾随 Token；遇到 P3 保留关键字（如 `for`/`while`/`switch`/`in`）报 `VCL_SYN_UNSUPPORTED_CONSTRUCT`，不回落旧 `ExpressionParser`。
  - **交付测试**：`VclParserTests.cs` —— 断言 `1 + 2 * 3` 树结构、`if/else` 嵌套、超深度拒绝、非法表达式赋值拒绝。
- **T2.05 — 符号绑定、静态类型检查与确定赋值分析（`VclTypedIr.cs`、`VclSemanticAnalyzer.cs`）**
  - 产出不可变 `TypedProgram` / `TypedFunction` / `TypedSymbol` / `TypedRegion` / `TypedExpression`。
  - 核心校验：禁止变量遮蔽（`VCL_SEM_SHADOWING_FORBIDDEN`）；禁止给形参赋值（`VCL_SEM_IMMUTABLE_TARGET`）；严格检查类型与显式转换表（覆盖 `P2-05`）；静态检查覆盖短路右侧（`false && unknown_name()` 报 `VCL_SEM_UNKNOWN_SYMBOL`），但**不对短路死分支里的 `i32(1)/i32(0)` 报错**；`if/else` 汇合点对已初始化局部变量取**交集**（`P2-08` 通过、`P2-09` 报 `VCL_SEM_UNINITIALIZED_LOCAL`）；`i32(-2147483648)` 按数学有符号值检查范围；所有可达路径必须有 `return`。
  - **交付测试**：`VclSemanticTests.cs` —— 完整跑通 `golden_vectors_p2.json` 中全部 `CompileError` 用例及 `P2-08`、`P2-SEM-SHORT-CIRCUIT-OK`。

### 4.3 脚本签名与稳定端口迁移（M04-P2，`LogicEngineConfigTool/Services/Vcl/GraphBridge/`）

- **T2.06 — `SCRIPT` 签名模型与变更预览（`VclSignatureModels.cs`、`ScriptSignatureMigrationPlanner.cs`）**
  - 持久化 `ParameterId (Guid) ↔ PortId (int)` 映射；实现纯函数 `PreviewSignatureChange(oldSig, newSig, existingConnections)`，产出 `Retained / Added / Removed / ConflictingConnections` 变更计划，绝不直接改活模型。
  - 仅改名或换序且类型不变时保留原 `PortId` 与连线；删除参数或变更类型时将冲突连线列入 `ConflictingConnections`。
  - **交付测试**：`ScriptSignatureMigrationTests.cs` —— 改名保线、换序保线、改类型报冲突、删参数列断线、输入对象零修改。

### 4.4 编译器后端与执行包编码（M05，`LogicEngineConfigTool/Services/Vcl/Compiler/`）

- **T2.07 — 控制流降级、字节码发射与资源估算（`VclBytecodeEmitter.cs`、`VclResourceEstimator.cs`）**
  - 将 `TypedProgram` 降级为前向基本块并严格按 `opcodes_p2.json` 发射指令；保证所有基本块出入口栈为空；将 `&&`/`||` 展开为短路条件跳转块；删除不可达块；记录多对多 `VclSourceMapEntry`。
  - 按 `profile_offline_p2.json` 核算 `TotalInstructions`、`TotalConstants`、`MaxLocalSlots`、`MaxOperandStackDepth`；超限报 `VCL_BE_RESOURCE_LIMIT_EXCEEDED`。
  - **交付测试**：`VclBackendTests.cs` —— 菱形 `if/else`、短路展开、栈平衡检查、多次编译及打乱无语义集合顺序后输出字节 100% 一致。
- **T2.08 — 执行包规范 JSON 序列化（`VclPackageSerializer.cs`）**
  - 输出严格符合 `package_schema_v1.json` 的 UTF-8 JSON（无 `$type`、字段顺序固定、`f64` 按 `CultureInfo.InvariantCulture` 规范文本编码、P2 `Bindings` 必须为空数组）。
  - **交付测试**：`VclPackageSerializerTests.cs` —— 对 `P2-01` 编译结果通过 `validate_contracts.py` 验证，独立输出外部文件字节 SHA-256。

### 4.5 C# 独立语义参考解释器（M08-Sim，`LogicEngineConfigTool/Services/Vcl/Simulation/`）

- **T2.09 — 受检算术与语义解释器（`VclCheckedMath.cs`、`VclReferenceInterpreter.cs`）**
  - 直接解释 `TypedProgram`（不调用字节码或 C VM），作为独立语言预言机。
  - 精确实现受检 `i32`/`u32` 算术、`INT32_MIN / -1`、`INT32_MIN % -1`、向零截断、`f64` 除 `±0.0` 报 `DIV_ZERO`、非有限浮点报 `NUMERIC_OVERFLOW`、浮点转整数先判有限再截断再判闭区间。
  - 输出 `VclExecutionTrace`（返回值、`branchTrace`、错误码）。
  - **交付测试**：`VclReferenceInterpreterTests.cs` —— 跑通 `golden_vectors_p2.json` 全部可执行语义用例。

### 4.6 C 端独立验证器与栈式虚拟机（M06 + M07，`linuxttu/src/logicengine/vm/`）

> 在 `linuxttu/src/logicengine/vm/host_tests/` 下维护独立桌面 C99 测试入口，产物全部输出至 `temp/vcl_c_host/`。

- **T2.10 — C 端受限 JSON 容器解码器（`vcl_types.h`、`vcl_error.h`、`vcl_package.h`、`vcl_package.c`）**
  - 定义固定宽度带标签值槽 `vcl_value_t`（`vcl_type_t tag` + `union { bool b; int32_t i32; uint32_t u32; double f64; }`）、错误码枚举与可故障注入分配器 `vcl_allocator_t`。
  - 实现严格有界容器解码：强制总字节上限、UTF-8 校验、JSON 嵌套深度上限、禁止重复键、禁止尾随数据、禁止未知顶层/内层键、严格区分整数/布尔/字符串常量编码；失败时释放全部候选分配。
  - **交付测试**：`test_vcl_package.c` —— 加载 `sample_packages_p2.json` 全部合法包成功；覆盖截断 JSON、重复键、尾部垃圾、超深度、所有 `alloc` 点逐一注入失败均零泄漏。
- **T2.11 — C 端独立验证器（`vcl_verify.h`、`vcl_verify.c`）**
  - 唯一构造入口 `vcl_verify_package(raw, profile, alloc, &verified, &diag)`，产出不透明只读句柄 `vcl_verified_program_t`。
  - 完整实现：版本/能力白名单检查 → 指令/操作数/跳转目标检查（P2 禁止 `target_pc <= pc`）→ 不可达块拒绝 → 基本块边界空栈 + 逐指令栈类型模拟 + 局部变量确定赋值交集 → 防溢出重算资源并与包自报值及 `profile` 对比 → 拒绝 P2 非空 `Bindings`。
  - **交付测试**：`test_vcl_verify.c` —— 跑通 `sample_packages_p2.json` 中 3 个合法包通过 + 6 个畸形负例包按精确 `(stage, code, pc)` 拒绝 + 分配失败零泄漏。
- **T2.12 — C 端类型化栈式 VM（`vcl_vm.h`、`vcl_vm.c`）**
  - `vcl_vm_init_workspace(verified, alloc, &ws)` 预分配全部槽与栈；`vcl_vm_run_cycle(verified, ws, &ctx, &limits, &result)` **内部严禁 `malloc`**。
  - 指令前严格按序检查：取消标志 → 单调 `now >= deadline` → 扣减步骤预算（按 `opcodes_p2.json` 成本表）→ 指令受检执行（使用无符号/边界预判避免任何 C 有符号溢出 UB）。
  - **交付测试**：`test_vcl_vm.c` —— 跑通 `sample_packages_p2.json` 对应的 `P2-01`～`P2-04B`、`P2-07A`（20 步成功）、`P2-07B`（19 步 `STEP_BUDGET`）、`P2-08-TRUE`/`FALSE`，以及假时钟 `DEADLINE`、取消优先于超时/步数、受检算术边界。

### 4.7 WPF 草稿编辑与跨端对拍（M08-UI + M12）

- **T2.13 — WPF `SCRIPT` 草稿编辑与离线仿真窗体（`Views/Vcl/ScriptEditorWindow.xaml(.cs)`、`ViewModels/Vcl/ScriptEditorViewModel.cs`）**
  - 打开时深拷贝 `VclScriptBlock`；“检查”仅显示诊断并按 `Utf8SpanMapper` 高亮源码；“离线仿真”在后台 `Task` 运行 `VclReferenceInterpreter` 并回 UI 线程展示轨迹和“记录式输出，不发设备命令”标记；“保存源工程”与“导出离线执行包”分按钮隔离；取消/关闭零污染。
  - **交付测试**：`VclEditorUiTests.cs`（STA 线程无头断言）—— 取消零污染、错误脚本允许保存草稿但禁止导出、文档切换丢弃过期异步结果。
- **T2.14 — 跨端对拍运行器与 G2 门槛验收（`linuxttu/src/logicengine/vm/host_tests/vcl_host_cli.c`、`LogicEngineConfigTool.RegressionTests/VclP2CrossCheckTests.cs`）**
  - 编译桌面 C CLI 宿主 `temp/vcl_c_host/vcl_host_cli`；C# 测试读取 `golden_vectors_p2.json`，逐例比对 **(1) C# 语义参考解释器** 与 **(2) C# 编译器导出包 → C `vcl_host_cli` 独立验证执行**。
  - **G2 放行命令**：
    ```powershell
    MSBuild.exe LogicEngineConfigTool/LogicEngineConfigTool.sln /t:Build /p:Configuration=Debug /p:Platform="Any CPU"
    LogicEngineConfigTool.RegressionTests/bin/Debug/LogicEngineConfigTool.RegressionTests.exe --vcl-p2-only
    LogicEngineConfigTool.RegressionTests/bin/Debug/LogicEngineConfigTool.RegressionTests.exe
    ```

---

## 5. 阶段 P3：核心语言表达能力（数组、函数、循环与图形桥接，门槛 G3）

| 任务号 | 所属模块 | 实现细节 | 交付测试 |
| --- | --- | --- | --- |
| **T3.01** | M00 契约 | 新增 `opcodes_p3.json`、`profile_offline_p3.json`、`golden_vectors_p3.json`（含 `allocate_one`、跨函数共享预算、`u64` 十进制字符串精确往返、循环超限与畸形循环回边包） | `validate_contracts_p3.py` 退出码 `0` |
| **T3.02** | M03 前端（类型与函数） | 扩展 `i64/u64/f32`、无符号位运算（`u32/u64` 逻辑右移、左移失位检查）、一维定长数组 `in T name[N]`（常量下标越界编译拒绝、禁止逃逸）、多函数与 DFS 无环调用图检查（拒绝直接/间接递归） | `VclP3TypeAndCallTests.cs` |
| **T3.03** | M03 前端（控制流） | 扩展 `switch`（整数、case 去重、无贯穿、默认空分支）、`for`/`while`/`do-while`、`@max_iterations(N)`、`break`/`continue` 归属与目标绑定 | `VclP3ControlFlowTests.cs` |
| **T3.04** | M05 后端 | 扩展多函数表、`CALL(u32)`、数组读取 `ARR_LOAD_*`、循环唯一准入检查块（进入第 `max+1` 次才报 `LOOP_LIMIT`）、`for` 中 `continue` 精确落向迭代段 | `VclP3BackendTests.cs` |
| **T3.05** | M04 图形桥接 | 实现 `GraphToTypedProgram.cs`：仅接受 `CompleteEditorGraph` 与白名单元件契约；复用规范化、区域分析与 `CompilationSourceOrder`；拒绝 `DataType_all` 宽位掩码与未知效果元件 | `VclGraphBridgeTests.cs`（菱形图 vs 等价文本语义一致；失败不改活图与历史栈） |
| **T3.06** | M06 C 验证器 | 扩展 `vcl_verify.c`：调用图无环与峰值帧计算；独立证明循环嵌套与唯一准入点（禁止外部跳入循环体或循环内重置计数）；数组维度防溢出计算 | `test_vcl_verify_p3.c`（间接递归、绕过准入点伪造回边、数组乘法溢出全部拒绝） |
| **T3.07** | M07 C VM + M08 解释器 | 双端实现调用帧栈（共享父任务步骤预算与截止期，调用绝不重置预算）、`i64/u64/f32` 受检算术与位运算、数组 `BOUNDS` 与 `LOOP_LIMIT` 精确边界 | `test_vcl_vm_p3.c` + `VclP3RefInterpTests.cs` |
| **T3.08** | M08 WPF | `SCRIPT` 支持定长数组端口编辑、多函数诊断定位与 P3 仿真回放 | `VclP3UiTests.cs` |
| **T3.09** | M12 集成（G3） | `golden_vectors_p3.json` 全量双端对拍（含 `allocate_one` 5 组输入向量、跨函数共享预算、`u64` 最大值往返） + 既有全量回归 | `--vcl-p3-only` + 无参全量回归均退出码 `0` |

---

## 6. 阶段 P4：设备领域接口、快照、功能块与非阻塞输出（门槛 G4）

| 任务号 | 所属模块 | 实现细节（`linuxttu/src/logicengine/vm/`） | 交付测试 |
| --- | --- | --- | --- |
| **T4.01** | M09 调度器 | `vcl_scheduler.c/.h`：`CLOCK_MONOTONIC` 绝对节拍 `r(k)=r(0)+k*T`；`pthread_cond_timedwait` 可唤醒休眠；禁止同任务重入，错过节拍计 `missedTick` 并跳到下一未过期节拍 | `test_vcl_scheduler.c`（假时钟：墙钟回拨不影响预算、错过节拍不补跑、5ms 内响应停止） |
| **T4.02** | M09 快照 | `vcl_snapshot.c/.h`：原子构建不可变输入快照（值、品质、单调接收时间、可选源时标、更新序号）；缺失标 `UNKNOWN` 不伪造为 `0`；有界重读失败则本轮失败 | `test_vcl_snapshot.c`（坏品质、陈旧过期、点间时差超限、读锁超时） |
| **T4.03** | M09 状态事务与宿主框架 | `vcl_state.c/.h`、`vcl_host.c/.h`：每轮拷贝 `state` 工作副本；`StepInstance` 校验 `(generation, task, instanceId, typeVersion)` 与单轮最多 step 一次；实例 `dt` 基于上次成功提交时刻，超 `maxDt` 报 `INVALID_DT` | `test_vcl_state.c`（失败 2 轮后第 3 轮恢复按上次成功算 `dt`、超 `maxDt` 拒绝补算、重复 step 报错） |
| **T4.04** | M09 首批功能块 | `vcl_host_blocks.c` 实现 3 类纯内核功能块（不调旧 `Execute` 虚表）：持续时间定时器、PI 调节（抗饱和/死区/品质检查）、时间积分（首轮仅建基线/受检 `dt`/溢出检查） | `test_vcl_blocks.c` + C# 参考模型逐轮对拍 |
| **T4.05** | M10 输出仲裁与命令账本 | `vcl_effects.c/.h`：物理对象键归一、唯一写者检查、优先级+TTL 仲裁（冲突拒绝）；同步提交边界复核权限与容量，释放给单一分派器；六态账本（`NOT_SENT/ACCEPTED/SENT/CONFIRMED/FAILED/UNKNOWN`）非阻塞入队 | `test_vcl_effects.c`（别名冲突、队列满 `QUEUE_FULL`、在途请求不可取消、超时转 `UNKNOWN` 不重发、旧代次拦截） |
| **T4.06** | M10 影子适配与出口封堵 | `vcl_platform_adapter.c` 接入 `linuxttu` 实时库与日志；封堵影子模式下 `CommonYkOperation`、`gat_remoteParaFunc`、`SetValueByRealNo` 等所有直接出口 | 影子联测 1000 轮：意图完整记录且真实驱动调用次数恒为 `0` |
| **T4.07** | M12 影子验收（G4） | 10 万轮软件状态回放；ARM 交叉编译进入产品构建，在目标板实测峰值内存、P99/最大扫描延迟及对其余业务影响 | 输出目标板实测报告与正式 `Profile` 限额 |

---

## 7. 阶段 P5～P6：热加载生命周期、有限投运与按需扩展（门槛 G5）

| 任务号 | 所属模块 | 实现细节 | 交付测试 |
| --- | --- | --- | --- |
| **T5.01** | M11 协调器与 `READY` 屏障 | `vcl_lifecycle.c/.h`：单协调器入口、一次性不可变字节与 SHA-256 核验、`PREPARING → READY`（候选线程停在屏障且零输出权限）；第 N 任务失败只清理候选 | `test_vcl_lifecycle_prepare.c` |
| **T5.02** | M11 协作停旧与代次切换 | `READY → QUIESCING → ACTIVATED_OBSERVING → COMMITTED`：旧任务有界停止，超时隔离标 `ISOLATED_FAULT`（禁强杀、禁激活候选）；同步锁内切换 `activeGeneration` 并撤旧预约 | `test_vcl_lifecycle_switch.c` |
| **T5.03** | M11 受控状态迁移 | `vcl_migration.c/.h`：按 `(taskStableId, instanceStableId, type, stateSchemaVersion, configDigest)` 决定迁移或复位（默认复位，禁 `memcpy(privateData)`）；动作账本独立保留 | `test_vcl_migration.c` |
| **T5.04** | M11 持久记录与监听重构 | 区分 `VERIFIED / ACTIVATED_UNCONFIRMED / COMMITTED` 持久记录与掉电恢复；`VisualProgramming_Thread` 重构为**先建 inotify 监听再初次对账** + 周期巡检 + watch 重建 | `test_vcl_recovery.c` |
| **T5.05** | M12 综合演练（G5） | 1000 次重载/拒绝/回退组合测试、最终点表与保护闭锁核对、现场六步投运及人工回退演练 | 产出 G5 现场交付包与签认记录 |
| **P6** | 按需扩展 | 按场景收益逐项引入 `struct`/枚举 → 二维数组 → 受限字符串 → `retain` → 紧凑二进制包 → 可选离线 C 代码生成 | 每项独立走契约更新、双端对拍与兼容回归 |

---

# 第二部分：编程智能体（Orchestrator）对轻量模型的分配与管理协议

## 8. 角色分级与模型路由矩阵

| 角色层级 | 适用模型 | 分配职责 | 严禁越权项 |
| --- | --- | --- | --- |
| **Tier-0 主控编排与集成者** | 强推理模型（或人类架构师） | 维护 `contracts/vcl/v1/` 契约、按波次生成任务包、统一登记共享工程文件（`.csproj`/`Program.cs`/`.cproject`/`logic_visual_programming.c`）、运行 L1～L3 门禁、仲裁跨端对拍分歧 | 不手写大批重复样板代码 |
| **Tier-1 中等模型** | 中等编码模型 | `T2.05`（类型与确定赋值）、`T2.11`/`T3.06`（C 独立验证与循环回边证明）、`T3.05`（图桥接）、`T4.05`（输出同步事务）、`T5.01`～`T5.04`（热加载并发状态机） | 不跳过门禁直接合入 |
| **Tier-2 轻量小模型** | 轻量快模型（如 Gemini Hydrogen 等） | `T0.1`～`T0.3`、`T2.01`～`T2.04`、`T2.06`～`T2.10`、`T2.12`～`T2.14`、`T3.02`～`T3.04`、`T3.07`～`T3.08`、`T4.01`～`T4.04`、全量单元测试与夹具补齐 | 禁止修改共享工程文件；禁止自由修改契约枚举/操作码；禁止单次改动超过 3 个生产文件 |

---

## 9. 并行波次调度图（P2 贯通执行拓扑）

同一波次内的所有任务**写路径完全互不相交**，主控智能体可并发拉起多个轻量模型；每波结束必须经过主控执行的**集成屏障（Barrier）**才能进入下一波：

```text
Wave 0 [已完成 — Tier-0]
  └── contracts/vcl/v1/（文法、错误码、51 条 Opcode、Schema、Profile、手工包、22 条 P2 黄金向量）
        │  [屏障 B0：python -B contracts/vcl/v1/validate_contracts.py 退出码 0]
        ▼
Wave 1 [4 路并行 — 全部 Tier-2 轻量模型，零写路径重叠]
  ├── Worker-1A: T2.01 + T2.02 -> Services/Vcl/Source/* + VclSource*Tests.cs
  ├── Worker-1B: T2.03         -> Services/Vcl/Language/VclDiagnostic/VclToken/VclLexer.cs + VclLexerTests.cs
  ├── Worker-1C: T2.06         -> Services/Vcl/GraphBridge/* + ScriptSignatureMigrationTests.cs
  └── Worker-1D: T2.10         -> linuxttu/src/logicengine/vm/vcl_types/error/package.* + test_vcl_package.c
        │  [屏障 B1：主控登记 .csproj -> MSBuild + GCC -Werror -> 4 组单测全绿]
        ▼
Wave 2 [3 路并行]
  ├── Worker-2A (Tier-2): T2.04 -> Services/Vcl/Language/VclAst/VclParser.cs + VclParserTests.cs
  ├── Worker-2B (Tier-1): T2.11 -> linuxttu/src/logicengine/vm/vcl_verify.* + test_vcl_verify.c
  └── Worker-2C (Tier-2): T2.12 -> linuxttu/src/logicengine/vm/vcl_vm.* + test_vcl_vm.c
        │  [屏障 B2：主控登记 -> C 端独立通过 3 合法包 + 6 畸形包 + P2-01..08 断言；C# Parser 全绿]
        ▼
Wave 3 [1 路核心]
  └── Worker-3A (Tier-1): T2.05 -> Services/Vcl/Language/VclTypedIr/VclSemanticAnalyzer.cs + VclSemanticTests.cs
        │  [屏障 B3：前端全量静态语义与 P2-05/08/09 测试全绿]
        ▼
Wave 4 [3 路并行 — 全部 Tier-2 轻量模型]
  ├── Worker-4A: T2.07 + T2.08 -> Services/Vcl/Compiler/* + VclBackend/SerializerTests.cs
  ├── Worker-4B: T2.09         -> Services/Vcl/Simulation/* + VclReferenceInterpreterTests.cs
  └── Worker-4C: T2.13         -> Views/Vcl/* + ViewModels/Vcl/* + VclEditorUiTests.cs
        │  [屏障 B4：编译导出包通过 Schema，参考解释器通过全部 P2 黄金向量]
        ▼
Wave 5 [联调验收]
  └── Worker-5A (Tier-2): T2.14 -> vcl_host_cli.c + VclP2CrossCheckTests.cs
        │  [G2 放行：MSBuild + GCC -Werror + --vcl-p2-only 跨端全绿 + 默认无参全量回归退出码 0]
```

---

## 10. 上下文预算、KV-Cache 复用与主动开新窗口协议

轻量模型（如 Gemini Hydrogen 等快速小模型）在长会话中极易出现三类系统性失效：**注意力稀释导致“降智”**（忘规则、漏边界、改 A 坏 B）、**历史报错锚定**（反复围绕错误代码打转）以及 **KV-Cache 前缀失效**（每轮重新 Prefill 导致延迟与成本飙升）。主控智能体和 Worker 必须把“短窗口 + 静态前缀 + 磁盘交接”作为强制运行纪律，而不是等到上下文爆掉才被动压缩。

### 10.1 窗口上下文硬预算（Worker 与主控分别设限）

| 角色 | 初始输入上限 | 单窗口轮次/调用上限 | 触发主动换新窗的硬阈值 | 严禁带入窗口的内容 |
| --- | --- | --- | --- | --- |
| **Tier-2 轻量 Worker** | **≤ 12K tokens**（只读上下文硬限 3～5 个文件、总计 ≤ 600 行） | **1 次生成 + 最多 2 次定点修复**（总工具调用 ≤ 10 次） | 上下文占用 **≥ 45%** 或 **≥ 24K tokens**，或 2 次修复未通过 | 整份演进方案、知识库全文、`VisualEditorViewModel.cs` 全文、全量构建/回归日志、上一个任务的对话记录 |
| **Tier-1 中等 Worker** | **≤ 20K tokens**（只读文件 ≤ 6 个） | **1 次生成 + 最多 2 次定点修复**（总工具调用 ≤ 16 次） | 上下文占用 **≥ 50%** 或 **≥ 48K tokens**，或出现改 A 坏 B | 无关模块的源码、全量历史 diff、超过 120 行的原始终端日志 |
| **Tier-0 主控编排者** | **≤ 24K tokens**（从磁盘 `state.json` 恢复） | **1 个 Wave（含 1 个集成屏障）= 1 个独立窗口** | 每过 1 个集成屏障（`B0/B1/B2...`）、累计处理 ≥ 2 次跨模块排障、或上下文占用 **≥ 55%** | 轻量模型的长段草稿推理过程、完整编译成功日志、已归档波次的细节 |

> **核心原则**：**1 个原子任务 = 1 个全新 Worker 窗口（1 Task = 1 Fresh Session）**；**1 个 Wave 波次 = 1 个主控窗口**。绝不在同一个轻量模型窗口里做完 `T2.03` 再顺手做 `T2.04`。

### 10.2 KV-Cache 友好型三层 Prompt 排布（避免缓存未命中）

推理引擎的 Prefix KV-Cache 只有在**开头的 token 序列逐字节完全一致**时才能命中。主控组装发给轻量模型的上下文时，必须严格遵守“**越稳定越靠前，越易变越靠后**”的三层顺序：

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 1：绝对静态前缀（KV-Cache 跨任务/跨轮次共享核心 — 逐字节不变）         │
│   · 直接加载固定文件：                                                    │
│     - C# Worker: contracts/vcl/v1/prompts/prefix_csharp_v1.txt          │
│     - C99 Worker: contracts/vcl/v1/prompts/prefix_c99_v1.txt            │
│   · 禁止出现当前时间、随机 task/run ID、动态目录树或变动版本号               │
├─────────────────────────────────────────────────────────────────────────┤
│ Layer 2：任务只读契约切片（同一任务生成 + 修复轮次内逐字节冻结）             │
│   · 按固定文件名排序只灌入本任务真正依赖的最小契约切片                       │
│   · 例：T2.03 只给 grammar_p2.ebnf + VCL_LEX_* 片段，不灌 51 条 opcode    │
│   · 修复轮次严禁改动或重排 Layer 1 与 Layer 2，保证修复轮 100% 命中前缀缓存  │
├─────────────────────────────────────────────────────────────────────────┤
│ Layer 3：易变尾部（永远放在最末 — 允许每轮变化）                            │
│   · 本次 task_id、allowed_write_paths、具体验收要求                       │
│   · 修复轮次仅追加“截断后的前 1～3 条精准编译/断言错误（≤ 60 行 / ≤ 2K）”   │
└─────────────────────────────────────────────────────────────────────────┘
```

- **同波次同类任务复用前缀**：Wave 1 中 3 个 C# 轻量模型共享完全相同的 `prefix_csharp_v1.txt`，可按相同前缀顺序依次或并发提交，最大化服务端前缀缓存命中率。
- **严禁把日志塞进前缀或全量贴出**：MSBuild 与 GCC 输出必须由主控先用脚本过滤，**只保留最前 1～3 条 `error` 行及对应 5 行代码上下文**再放到 Layer 3 末尾。

### 10.3 主动开启新窗口的 6 条强制触发条件

只要命中下列任意一条，智能体（无论是主控还是 Worker）**必须主动停止当前窗口并开启全新窗口继续**，不尝试在污染的旧上下文中“硬扛”：

1. **原子任务切换（强制）**：一个 `T*.*` 任务通过验收或被终止后，开始下一个任务前必须开启全新 Worker 窗口。
2. **波次与集成屏障切换（强制）**：主控每完成一个集成屏障（`B0 → B1 → B2 → ...`），将状态写入 `temp/vcl-orchestrator/state.json` 后，主动开启新主控窗口启动下一波次。
3. **2 次修复未过或触发模型升级（强制）**：轻量模型对同一任务修复 2 次仍失败时，**立即销毁该脏窗口**，切到新窗口（升级给 Tier-1，或拆分任务后给新 Tier-2）。新窗口只喂“磁盘当前代码 + 精炼后的失败事实 + 最小契约”，彻底丢弃旧窗口里的错误推理链与废弃尝试，消除“错误锚定效应”。
4. **上下文/日志膨胀越界（强制）**：Worker 窗口达到 45%（或 24K tokens）、主控达到 55%、或单次工具输出意外超过 300 行污染历史时，立刻摘要落盘并开新窗。
5. **检测到“降智”特征（立即止损）**：一旦观察到以下任意信号，不等满 2 次重试直接换新窗：
   - 重复写出同一个 C# 7.3 / C99 禁用语法或编译错误；
   - 修复错误 A 后把上一轮刚修好的错误 B 重新改坏（震荡循环）；
   - 自行编造契约中不存在的字段名、opcode、诊断码或试图改动 `forbidden_paths`；
   - 开始“偷懒省略”（输出 `// ... 其余逻辑同上`、`TODO`）或机械复读提示词。
6. **跨语言或跨角色切换（强制）**：从 C#（`.NET 4.8`）切到 C99（`linuxttu`），或从“编码实现”切到“独立审查 / 写破坏性测试用例”时，必须开启新窗口，避免语言习惯和实现者盲区串味。

### 10.4 跨窗口无损交接协议（磁盘状态机 + 冷启动模板）

因为窗口生命周期短，**一切跨窗口事实都必须落在磁盘上，绝不依赖对话记忆**。主控智能体统一在 `D:/repo/dfe/LinuxApp/visualconfig/temp/vcl-orchestrator/` 下维护以下轻量化状态文件（全部位于 `temp/` 内，符合仓库临时文件规则）：

- `state.json`：记录当前波次、每个 `T*.*` 的状态（`pending / running / passed / retry1 / escalated`）、已过屏障、最近失败摘要和下一待派发任务列表。
- `handoff/<task-id>_clean_restart.md`：换新窗时生成的极简交接单（硬限 ≤ 80 行），固定只写 4 项：
  1. 本任务精确目标与允许写路径；
  2. 磁盘上已有代码文件路径（让新窗口直接读取当前源码，不复述旧聊天记录）；
  3. 当前唯一待解决的 1～3 条真实编译/断言失败事实；
  4. 1 句话标明“上一窗口已验证行不通的错误方向（避免重踩）”。

**主控主动开启新窗口的两种执行方式**：
- **支持子会话 / 工作流工具的环境**：主控直接通过独立子会话 / 工作流新节点拉起全新空上下文窗口，每个 `T*.*` 节点天然隔离；主控自身到达屏障或 55% 阈值时，写入 `state.json` 后主动提示用户新开主控窗口并附下面冷启动指令。
- **手工多窗口协同环境**：智能体在命中 §10.3 任一触发条件时，**主动暂停后续编码**，把状态写入 `temp/vcl-orchestrator/state.json` 或 `handoff/`，并在回复末尾明确输出一段可直接复制的**新窗口冷启动指令**：

```text
请从磁盘恢复 VCL 编排进度，不要依赖历史聊天：
1. 读取 D:/repo/dfe/LinuxApp/visualconfig/temp/vcl-orchestrator/state.json；
2. 读取 D:/repo/booknote/articles/可视化编程规约C语言表达能力编码实现与智能体调度计划.md 第 9～11 章；
3. 按 state.json 中的 next_action 继续执行（当前阶段：<Wave X / Barrier BX / Escalated Task T*.*>）。
```

---

## 11. 主控智能体的四级自动门禁与失败升级协议

轻量模型返回后，主控智能体必须按顺序执行以下机械校验，**不采信模型口头宣称“已完成”**：

1. **L1 越界与静态卫生门禁**
   - 检查 `git status --short` 与 `git diff --name-only`：所有改动必须严格落在任务单 `allowed_write_paths` 内；触碰共享文件或 `work/` 时直接还原并打回。
   - 静态扫描：C# 禁止出现文件级 `namespace`、`record`、`string?`、`CommonFunctions.ReadFromJson`、`TODO`/省略占位注释；C 禁止在 `vcl_vm.c` 热路径出现 `malloc`/`calloc`/`realloc`。
   - 核对仓库根目录不存在 `temp/<task-id>/` 与 `temp/vcl-orchestrator/` 之外的新增临时文件或 `__pycache__`。
2. **L2 主控统一登记与严格编译门禁**
   - 由主控把新增 `.cs` 注册进 `LogicEngineConfigTool.csproj` / `LogicEngineConfigTool.RegressionTests.csproj`，并在 `Program.cs` 中注册 `--vcl-*` 入口（对未知 `--vcl-*` 子参数显式返回退出码 `1`，避免旧 `Program.cs` 未知参数静默穿透）。
   - C# 要求 `MSBuild.exe` 0 Error 且无新增 Warning；C 要求 `-std=c99 -Wall -Wextra -Werror -pedantic` 0 Warning。
3. **L3 模块单测与跨端对拍门禁**
   - 运行任务专属测试入口，核对实际退出码 `0` 与打印的通过用例数。
   - 在波次汇聚点运行 C# 参考解释器 vs C 宿主 `vcl_host_cli` 黄金向量对拍。
4. **受控重试、换窗止损与模型升级策略（防死循环）**
   - **第 1 次失败**（编译错误 / 单测断言失败 / 缺 XML 注释）：主控先检查原 Worker 窗口是否触发 §10.3 降智或 45% 预算阈值——未超限则**保持 Layer 1 + Layer 2 逐字节不变**，仅在尾部追加最前 1～3 条真实错误（≤ 60 行）发回原窗口做定点修复，充分利用 KV-Cache；若已超预算或出现降智信号，则直接写 `handoff/` 开新窗。
   - **第 2 次失败**（原地打转或引入新错）：**强制关闭旧窗口**并写极简 `handoff/<task-id>_clean_restart.md`——属复杂逻辑问题则在新窗口**升级派给 Tier-1 中等模型**；属任务范围偏大则由主控一分为二、分别开新窗口派给 Tier-2。
   - **跨端对拍分歧**（两端各自单测通过但结果不一致）：由 **Tier-0 主控**在新审查上下文中对照 `contracts/vcl/v1/` 裁定哪端违约或补充契约用例，严禁私自修改黄金向量迁就错误实现。

---

## 12. Wave 1 可直接派发的标准任务包（4 个轻量模型开箱即用）

主控智能体派发以下 4 份任务单时，必须为每个任务开启**独立新窗口**，按 `Layer 1 (kv_cache_prefix) → Layer 2 (read_only_context) → Layer 3 (task_packet)` 顺序组装输入：

### 任务包 1：`T2.01 + T2.02`（M02 源工程模型、摘要与原子读写）

```yaml
task_id: "T2.01_T2.02"
wave: 1
model_tier: "Tier-2"
session_policy:
  fresh_window_required: true
  kv_cache_prefix_file: "contracts/vcl/v1/prompts/prefix_csharp_v1.txt"
  max_input_tokens: 12000
  max_repair_turns: 2
  reset_window_on: ["context>=45%", "degradation_signal", "repair_turns>2"]
repo_root: "D:/repo/dfe/LinuxApp/visualconfig"
temp_dir: "D:/repo/dfe/LinuxApp/visualconfig/temp/T2.01_T2.02"
allowed_write_paths:
  - "LogicEngineConfigTool/Services/Vcl/Source/VclSourceModels.cs"
  - "LogicEngineConfigTool/Services/Vcl/Source/VclSourceDigest.cs"
  - "LogicEngineConfigTool/Services/Vcl/Source/VclSourceProjectStore.cs"
  - "LogicEngineConfigTool.RegressionTests/VclSourceTests.cs"
forbidden_paths:
  - "work/**"
  - "LogicEngineConfigTool/LogicEngineConfigTool.csproj"
  - "LogicEngineConfigTool.RegressionTests/LogicEngineConfigTool.RegressionTests.csproj"
  - "LogicEngineConfigTool.RegressionTests/Program.cs"
read_only_context:
  - "contracts/vcl/v1/types_and_errors.json"
  - "contracts/vcl/v1/profile_offline_p2.json"
  - "LogicEngineConfigTool/Services/ControlFlow/TransactionalConfigSaveService.cs (仅读行 355-435 原子替换段)"
requirements:
  - "C# 7.3 / .NET Framework 4.8，块级 namespace LogicEngineConfigTool.Services.Vcl.Source，Allman 大括号，完整中文 XML 注释。"
  - "定义 VclSourceProject(Format='vcl-source', SchemaVersion='1.0', DocumentId, SemanticInputs, EditorView)、VclSourceSnapshot(不可变深拷贝)、VclScriptBlock(BlockId, Name, LanguageVersion, SourceText, Signature)。"
  - "VclSourceDigest.ComputeSha256(VclSourceSnapshot) 只覆盖 SemanticInputs 的规范化 UTF-8（键名 Ordinal 排序、集合按稳定 ID 排序、脚本保留原始换行与注释），显式排除 EditorView。"
  - "VclSourceProjectStore.OpenSource(byte[]) 启用 DuplicatePropertyNameHandling.Error，拒绝含 $type 属性（VCL_SRC_FORBIDDEN_DOLLAR_TYPE）和未知 SchemaVersion（VCL_SRC_UNSUPPORTED_SCHEMA）。"
  - "VclSourceProjectStore.SaveSource(draft, path) 允许保存含语法错误的草稿；写同目录 .tmp -> 回读校验结构与 DocumentId -> File.Replace/File.Move（不支持替换时不退化为非原子覆盖）。"
  - "提供 VclExportCacheValidator.ValidateFreshness(currentSnapshot, packageSourceDigest)，不匹配时报 VCL_SRC_STALE_EXPORT_DIGEST。"
  - "在 VclSourceTests.Run() 中使用 temp/T2.01_T2.02 下的临时文件完成全部正反测试并在 finally 清理。"
```

### 任务包 2：`T2.03`（M03 统一诊断、UTF-8 映射与词法分析器）

```yaml
task_id: "T2.03"
wave: 1
model_tier: "Tier-2"
session_policy:
  fresh_window_required: true
  kv_cache_prefix_file: "contracts/vcl/v1/prompts/prefix_csharp_v1.txt"
  max_input_tokens: 12000
  max_repair_turns: 2
  reset_window_on: ["context>=45%", "degradation_signal", "repair_turns>2"]
repo_root: "D:/repo/dfe/LinuxApp/visualconfig"
temp_dir: "D:/repo/dfe/LinuxApp/visualconfig/temp/T2.03"
allowed_write_paths:
  - "LogicEngineConfigTool/Services/Vcl/Language/VclDiagnostic.cs"
  - "LogicEngineConfigTool/Services/Vcl/Language/VclToken.cs"
  - "LogicEngineConfigTool/Services/Vcl/Language/VclLexer.cs"
  - "LogicEngineConfigTool.RegressionTests/VclLexerTests.cs"
forbidden_paths:
  - "work/**"
  - "LogicEngineConfigTool/LogicEngineConfigTool.csproj"
  - "LogicEngineConfigTool.RegressionTests/LogicEngineConfigTool.RegressionTests.csproj"
  - "LogicEngineConfigTool.RegressionTests/Program.cs"
read_only_context:
  - "contracts/vcl/v1/grammar_p2.ebnf"
  - "contracts/vcl/v1/types_and_errors.json"
  - "contracts/vcl/v1/profile_offline_p2.json"
requirements:
  - "C# 7.3 / .NET Framework 4.8，块级 namespace LogicEngineConfigTool.Services.Vcl.Language，Allman 大括号，完整中文 XML 注释。"
  - "VclDiagnostic 含 Stage/Code/Severity/MessageArgs/StartByte/EndByte；Utf8SpanMapper.ToUtf16Span 精准换算含中文注释源码的 UTF-8 字节区间到 UTF-16 字符区间。"
  - "VclLexer.Tokenize(string source, VclFrontendLimits limits) 强制检查 maxSourceBytes（VCL_LEX_SOURCE_TOO_LARGE）与 maxTokens（VCL_LEX_TOKEN_LIMIT）。"
  - "按 grammar_p2.ebnf 识别全部 P2 关键字、P3 保留字（标记 ReservedKeyword 供 Parser 报能力错误）、ASCII 标识符、整数/小数（仅 '.'）、// 与非嵌套 /* */ 注释、运算符与分隔符；对 ++/--/+=/-=/*=//=/%= 报 VCL_LEX_UNSUPPORTED_OPERATOR；对未闭合块注释报 VCL_LEX_UNTERMINATED_COMMENT。"
  - "在 VclLexerTests.Run() 中断言：合法 P2 样例、中文注释后偏移精准换算、超字节/超 Token 拒绝、非法运算符与未闭合注释诊断码。"
```

### 任务包 3：`T2.06`（M04-P2 `SCRIPT` 签名模型与稳定端口变更规划）

```yaml
task_id: "T2.06"
wave: 1
model_tier: "Tier-2"
session_policy:
  fresh_window_required: true
  kv_cache_prefix_file: "contracts/vcl/v1/prompts/prefix_csharp_v1.txt"
  max_input_tokens: 10000
  max_repair_turns: 2
  reset_window_on: ["context>=45%", "degradation_signal", "repair_turns>2"]
repo_root: "D:/repo/dfe/LinuxApp/visualconfig"
temp_dir: "D:/repo/dfe/LinuxApp/visualconfig/temp/T2.06"
allowed_write_paths:
  - "LogicEngineConfigTool/Services/Vcl/GraphBridge/VclSignatureModels.cs"
  - "LogicEngineConfigTool/Services/Vcl/GraphBridge/ScriptSignatureMigrationPlanner.cs"
  - "LogicEngineConfigTool.RegressionTests/ScriptSignatureMigrationTests.cs"
forbidden_paths:
  - "work/**"
  - "LogicEngineConfigTool/LogicEngineConfigTool.csproj"
  - "LogicEngineConfigTool.RegressionTests/LogicEngineConfigTool.RegressionTests.csproj"
  - "LogicEngineConfigTool.RegressionTests/Program.cs"
read_only_context:
  - "contracts/vcl/v1/types_and_errors.json"
  - "LogicEngineConfigTool/Models/ElementModel.cs (仅读 InputModel / OutputModel 字段定义，勿全读)"
requirements:
  - "C# 7.3 / .NET Framework 4.8，块级 namespace LogicEngineConfigTool.Services.Vcl.GraphBridge，Allman 大括号，完整中文 XML 注释。"
  - "定义 ScriptParameterDef(Guid ParameterId, int PortId, string Name, VclScalarType Type)、ScriptSignature(ReturnType, IReadOnlyList<ScriptParameterDef> Parameters)、ScriptPortConnection(int PortId, int SourceElemId, int SourcePortId) 及 SignatureChangePlan。"
  - "实现纯函数 PreviewSignatureChange(oldSig, newSig, connections)：不修改任何输入对象；ParameterId 相同且 Type 不变（即使改名或调换顺序）进入 Retained 并保持原 PortId；新增 ParameterId 分配未占用的最小非负 PortId 进入 Added；被删 ParameterId 进入 Removed，若存在已连线则加入 ConflictingConnections；Type 变更时已有连线进入 ConflictingConnections 且 RequiresUserConfirmation = true。"
  - "在 ScriptSignatureMigrationTests.Run() 中验证改名保线、换序保线、改类型报冲突、删参数列断线、PortId 唯一稳定以及输入对象零修改。"
```

### 任务包 4：`T2.10`（M06-C 受限 JSON 容器解码器）

```yaml
task_id: "T2.10"
wave: 1
model_tier: "Tier-2"
session_policy:
  fresh_window_required: true
  kv_cache_prefix_file: "contracts/vcl/v1/prompts/prefix_c99_v1.txt"
  max_input_tokens: 14000
  max_repair_turns: 2
  reset_window_on: ["context>=45%", "degradation_signal", "repair_turns>2"]
repo_root: "D:/repo/dfe/LinuxApp/linuxttu"
temp_dir: "D:/repo/dfe/LinuxApp/visualconfig/temp/T2.10"
allowed_write_paths:
  - "src/logicengine/vm/vcl_types.h"
  - "src/logicengine/vm/vcl_error.h"
  - "src/logicengine/vm/vcl_package.h"
  - "src/logicengine/vm/vcl_package.c"
  - "src/logicengine/vm/host_tests/test_vcl_package.c"
forbidden_paths:
  - "src/logicengine/logic_visual_programming.c"
  - ".cproject"
read_only_context:
  - "D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/types_and_errors.json"
  - "D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/opcodes_p2.json"
  - "D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/package_schema_v1.json"
  - "D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/profile_offline_p2.json"
  - "D:/repo/dfe/LinuxApp/visualconfig/contracts/vcl/v1/sample_packages_p2.json"
requirements:
  - "严格 C99，独立可编译（不依赖任何 prjcfg.h / json-c 外部库或板级头；内置轻量有界递归下降 JSON 扫描解码器），编译选项 -std=c99 -Wall -Wextra -Werror -pedantic 必须 0 警告。"
  - "所有动态分配统一经注入的 vcl_allocator_t { void* (*alloc)(void*, size_t); void (*free)(void*, void*); void* ctx; } 完成；任何错误路径必须释放已分配内存，保证零泄漏。"
  - "严格校验：总字节 <= maxPackageBytes（VCL_PKG_TOO_LARGE）、合法 UTF-8（VCL_PKG_INVALID_UTF8）、嵌套深度 <= maxJsonDepth（VCL_PKG_DEPTH_EXCEEDED）、禁止重复键（VCL_PKG_DUPLICATE_KEY）、禁止尾部多余字符（VCL_PKG_TRAILING_DATA）、禁止未知字段（VCL_PKG_SCHEMA_VIOLATION）、整数位拒绝浮点/布尔/字符串、f64 字符串拒绝 NaN/Inf（VCL_PKG_INVALID_NUMBER_ENCODING）。"
  - "在 test_vcl_package.c 中实现计数分配器（支持第 k 次分配注入失败），测试加载 sample_packages_p2.json 中的 3 个合法包，覆盖全部 7 类畸形 JSON 负例，并逐一注入分配失败断言 outstanding_allocs == 0。"
```

---

## 13. 集成屏障 B1 执行清单（Wave 1 完成后由主控运行）

1. 运行 `git status --short` 核对 4 个轻量模型均未越界修改禁止路径；
2. 将 `T2.01/T2.02`、`T2.03`、`T2.06` 新增 `.cs` 登记到 `LogicEngineConfigTool.csproj` 与 `LogicEngineConfigTool.RegressionTests.csproj`，在 `Program.cs` 注册 `--vcl-wave1-only`（并拒绝未知 `--vcl-*` 参数）；
3. 编译并运行 C# 侧：
   ```powershell
   MSBuild.exe LogicEngineConfigTool/LogicEngineConfigTool.sln /t:Build /p:Configuration=Debug /p:Platform="Any CPU"
   LogicEngineConfigTool.RegressionTests/bin/Debug/LogicEngineConfigTool.RegressionTests.exe --vcl-wave1-only
   ```
4. 编译并运行 C 侧（产物落在 `temp/vcl_c_host/`）：
   ```powershell
   gcc -std=c99 -Wall -Wextra -Werror -pedantic -I D:/repo/dfe/LinuxApp/linuxttu/src/logicengine/vm `
       D:/repo/dfe/LinuxApp/linuxttu/src/logicengine/vm/vcl_package.c `
       D:/repo/dfe/LinuxApp/linuxttu/src/logicengine/vm/host_tests/test_vcl_package.c `
       -o D:/repo/dfe/LinuxApp/visualconfig/temp/vcl_c_host/test_vcl_package.exe
   D:/repo/dfe/LinuxApp/visualconfig/temp/vcl_c_host/test_vcl_package.exe
   ```
5. 全部退出码 `0` 后，更新 `temp/vcl-orchestrator/state.json`（标记 Wave 1 与 B1 完成），**主动关闭本主控窗口并开启全新主控窗口**，按第 9 节拓扑拉起 **Wave 2（`T2.04`、`T2.11`、`T2.12`）**。
