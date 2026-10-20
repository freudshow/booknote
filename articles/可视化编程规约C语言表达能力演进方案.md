# 可视化编程规约达到 C 语言同等表达能力 — 演进方案

> 日期：2026-09-25
> 范围：上位机 `LogicEngineConfigTool`（本仓库）+ 嵌入式固件 `D:\repo\dfe\LinuxApp\linuxttu\src\logicengine`
> 说明：本文基于双端代码逐文件核查后撰写，所有"现状"均有代码位置可循。

---

## 一、现状基线（基于代码核查的事实）

### 1.1 上位机（LogicEngineConfigTool，WPF / .NET Framework 4.8 / C# 7.3）

- 已有 50+ 种元件：IO（YX/YC/YK/YT）、算术、比较、逻辑、定时器、PI、变化检测、时段，以及控制流五件套 `IF / SWITCH / WHILE / FOR / DO_WHILE`（`LogicEngineConfigTool/Models/ElementModel.cs` 的 `ElementTypesEnum`）。
- 已有一条**结构化控制流编译流水线**：图规范化 → 结构化区域 → 数据依赖调度 → 线性化 → 生成 `NextID`（`LogicEngineConfigTool/Services/ControlFlow/`：`ControlFlowCompilationService`、`ExecutionLinearizer`、`StructuredRegionBuilder` 等）。
- FOR 的初始化/条件/步进已经是**文本表达式**（`Models/ControlFlowModels.cs` 的 `ForExpressionInfo`；`Elements/ElementControlFlowFor.cs`）。
- 表达式子语言已有 C# 解析器做 AST 校验（`Models/ExpressionSyntax.cs`、`Services/ExpressionParser.cs`），支持算术/关系/逻辑/位运算、约 30 个数学函数、`#点号` 与 `#(链,设,寄)` 实时库引用、对实时库点的赋值。
- 端口已有类型枚举 `PortDataTypeEnum`（bool/s8/u8/s16/u16/s32/u32/s64/u64/f32/f64），但计算元件实际多以 double 传输。
- 验证手段：`LogicEngineConfigTool.RegressionTests` 回归可执行程序 + `Fixtures/*.baseline.json`，但只有"编译/保存/读回"级别的验证，无运行语义仿真。

### 1.2 固件（e9361app：`D:\repo\dfe\LinuxApp\linuxttu\src\logicengine`，C + pthread + json-c，ARM Linux 用户态）

> 注：该目录是权威主版本树。`D:\repo\dfe\linuxttu\src\logicengine` 为旧副本，仅 `elements/element_compare.c` 落后（主版本已实现与上位机对齐的 `COMPARE_PRECISION` 精度量化比较，见 `GetS64ValByPrecision`）。以下结论均以主版本树复核。

- 元件虚表插件架构（`logic_element_base.h` 的 `t_ElementVtbl`），端口值/参数统一 `double`，每元件 16 入 16 出 32 参数，500 元件/任务（`LOGIC_MAX_ELEMENTS_PER_TASK`）。
- 执行模型：每任务一个 pthread，**每周期从 0 号元件沿 `NextID` 链执行**；IF 在 `Execute` 内改写自身 `config.nextId` 完成跳转（`logic_visual_programming.c` 的 `VisualProg_TaskThread`；`elements/element_flow.c` 的 `If_Execute`）。
- **固件只注册了 `IF`，SWITCH/WHILE/FOR/DO_WHILE 全部缺失**（`logic_engine_v2.c` 的 `LogicEngineV2_RegisterBaseElements`）——上位机已能画的图，固件当前跑不了。
- 表达式由成熟的 `eval.c` 求值（`src/protocol/DataCalculation/eval.c`）：词法→AST→求值，文法注释齐全；覆盖全部算术/关系/逻辑/位运算、数学函数表（`pow/sin/…/max/min`）、对实时库点的赋值、`#id` / `#(l,d,r)` 引用；**但没有命名变量、无数组、无语句、无函数定义**。
- 数据空间：全局实时库点（`GetValueByRealNo/SetValueByRealNo` + `FastGetRtdbNo` 映射）+ 系统参数表 `ga_syspara`。
- 具备成熟的 JSON 配置热加载：inotify 监听 + MD5 稳定窗 + `/tmp` 快照 + 加载失败保留旧配置回退（`logic_visual_programming.c` 的 `VisualProg_TryReloadConfig` 等）。

### 1.3 一句话概括

**表达式层已接近 C 表达式的 80%；语句层固件只有 if；数据层只有 double 全局点；过程抽象（函数）为零。** 双端还有一个隐患：C# 解析器与 C 求值器是两套手工维护的文法，存在漂移风险。

---

## 二、目标定义：工业控制语境下的"与 C 同等"

严格等价 C 的全部能力（指针、任意内存、预处理器、union、无限制递归）既无必要，也与"可静态校验、执行确定、可在线热加载"的工业运行时目标冲突。建议把目标定义为三个抽象层级齐备：

| C 的能力维度 | 目标规约 | 说明 |
|---|---|---|
| **图灵完备的控制流** | ✅ 必须 | if/else、switch、while/do/for、break/continue、有界 goto/状态机 |
| **数据抽象** | ✅ 必须 | 命名变量、定长数组、类型化整数（位宽/符号）、bool/f32/f64；struct 次之 |
| **过程抽象** | ✅ 必须 | 函数定义、参数、返回值、局部作用域、子程序复用；**递归禁止或限深** |
| 与设备/系统交互 | ✅ 保留并强化 | YC/YX/YK/YT、参数表、定时器、PI、时间、品质位——这些是比 C 更贴领域的"FFI" |
| 指针/内存别名、预处理器、字符串自由处理、union、无界递归 | ❌ 明确不做 | 以数组下标 + 边界检查 + 限深调用替代；换取确定性与可验证性 |

---

## 三、差距分析

| C 能力 | 上位机现状 | 固件现状 | 差距等级 |
|---|---|---|---|
| 算术/逻辑/位运算表达式 | 有校验器 | eval.c 全支持 | 小 |
| 三元 `?:`、`++/--`、复合赋值 | 无 | 无 | 中 |
| if/else | 有 | **仅此一项** | — |
| switch / while / do / for | 有图编译 | **未注册、无法执行** | 大 |
| break/continue/return | 无 | 无 | 大 |
| 命名局部/静态变量 | 无 | 无（只能蹭实时库点） | 大 |
| 数组 | 仅 MAX/MIN 固定点表 | 无 | 大 |
| 结构体/枚举/字符串 | 无 | 无 | 中（按需） |
| 类型系统 | 端口有类型枚举 | 实际全 double | 中 |
| 函数/子程序/复用 | 无 | 无 | 大 |
| 模块/库 | 无 | 无 | 中 |
| 每周期执行预算（防死循环） | 无 | 无（真死循环会卡死任务线程） | 安全缺口 |

---

## 四、总体方案：统一 IR + 双端，图形与脚本同源（推荐）

三条路线对比：

1. **继续"加元件"**：变量、数组、函数靠 `double` 端口连线表达 → 连线爆炸、数组/结构体无法表达、每加一种语义双端各改一遍，天花板很低。❌
2. **上位机生成 C → 现场编译 → dlopen**：表达力最强，但现场工具链、签名安全、实时性、与现有 JSON 下装运维体系冲突 → 只适合作离线仿真后端，**不作主路线**。
3. **图形 + 脚本混合、统一向字节码 IR 收敛** ✅（推荐）：

```text
 ┌──────────────────────── 上位机 (C#) ────────────────────────┐
 │  图形元件 (现状)        脚本块元件 SCRIPT (新)                │
 │       │                        │                            │
 │       ▼                        ▼                            │
 │  结构化控制流编译器       VCL 文本解析器 (单一文法)            │
 │       └──────────┬─────────────┘                            │
 │                  ▼                                          │
 │        类型检查 / 静态校验 (越界、未初始化、预算、栈深)         │
 │                  ▼                                          │
 │         VCL IR (函数表+指令+常量池+变量槽)  ── JSON/二进制    │
 │                  │                    ▲                     │
 │           C# 仿真器(影子点表回放)      │ 反编译回图形           │
 └──────────────────┼────────────────────┼─────────────────────┘
                    ▼                    │
        c{link}57.json (带版本号)         │
 ┌──────────────── 固件 (C) ────────────┼─────────────────────┐
 │        VCL VM: 加载器 + 解释器 ◀──────┘                     │
 │        指令预算/栈预算/边界检查/异常安全态                    │
 │  FFI: yc/yx/yk/yt/para/定时器/PI/时间/日志 (现有元件 Execute) │
 │  Legacy 适配器: 老 JSON 元件链 (现有 NextID 引擎保留)         │
 └─────────────────────────────────────────────────────────────┘
```

三个关键决策：

1. **定义 VCL（Visual Control Language）**：一个 C 子集的命令式语言，图形与文本只是它的两种编辑视图。每个 `LogicTask` 等价于一个周期调用的 `void task(void)` 函数。
2. **新增脚本块元件 `SCRIPT`**：元件内部是一段 VCL 代码，其输入/输出端子由函数签名自动生成；复杂算法不再需要把表达式拆成几十个元件。简单逻辑继续用图形画，保护用户既有习惯。
3. **固件引入小型 VM，现有元件全部 FFI 化；老 NextID 引擎作为 legacy 适配器保留**。新老配置通过 JSON 版本号共存，热加载失败回退机制原样复用。

---

## 五、VCL 语言与 IR 设计要点

### 5.1 类型

`bool / i32 / u32 / i64 / u64 / f32 / f64`；定长一维（后期二维）数组；`struct`（P3）；字符串仅提供定长缓冲内建，不开放字符指针。全局变量显式声明，可绑定实时库点（保留 Link/Dev/Reg 符号，加载时由 `FastGetRtdbNo` 解析），未绑定的全局变量落 VM 静态槽。

### 5.2 语句

块、`if/else`、`switch`、`while/do/for`、`break/continue`、`return`、表达式语句（赋值沿用 eval.c 已有的 `点 = 值` 语义并扩展到变量/数组元素）。

### 5.3 表达式

直接以 `eval.c` 文法注释为基线扩展：命名变量、下标 `a[i]`、三元、`++/--`、复合赋值；数学函数表原样保留。

### 5.4 函数与库

纯 VCL 函数（传值、一个返回值、局部作用域、调用层级与帧大小静态可算）；禁用递归（需要递归算法时用数组 + 显式栈 + 循环实现，控制策略本就是状态机风格）。函数库随配置下发、可跨任务复用，解决当前"复用只能复制任务"的问题。

### 5.5 IR（约 20 条指令）

`CONST / LOAD / STORE / ALU / JMP / JZ / JNZ / CALL / RET / FFI / IDXLOAD / IDXSTORE / SWITCH` 等；配套常量池、函数表、类型表、变量槽表、FFI 序号表。序列化先沿用缩进 JSON（可读、可 diff、与现有运维一致），后期加紧凑二进制选项。IR 必须可反编译回图形/文本。

### 5.6 FFI（领域能力，即规约强于裸 C 的部分）

`yc_get / yc_set、yx_get、yk_exec、yt_exec、para_get/set、ton/tof/tp/overtime/period、pi、rtc_now、quality_get、log/event`——由现有 `elements/element_*.c` 的 Execute 包装注册。

---

## 六、双端改造内容

### 6.1 上位机

- 新增 SCRIPT 元件 + 脚本编辑器（语法高亮、错误波浪线直接复用 `ExpressionParser` 的 AST/diagnostic 基础）；函数库管理窗口；全局/局部变量表编辑器；数组变量声明。
- 图形 lower 到 VCL AST 的代码生成器（结构化区域编译器的输出已是结构化的，接 AST 很自然）；AST 反编译器供"文本→图形"同步。
- 类型系统与静态校验：类型兼容、未初始化、常量下标越界、调用深度、**每周期循环步数预算与栈帧预算**估算，超限拒绝保存。
- C# 版 VM 仿真器：影子点表回放，替代目前"编译通过≈正确"的验证现状。
- **文法单一来源**：用一份文法定义生成/约束双端，并建立表达式黄金用例集，根治两套解析器漂移。

### 6.2 固件（新增 `src/logicengine/vm/`，C99、无动态分配依赖）

- IR 加载器、解释器；每任务保留一个 pthread，每周期调用任务入口函数；周期内设**指令条数预算（watchdog），超限即中止本轮、输出安全态并告警**——顺带补上现有 IF 链全无死循环保护的缺口。
- 数组边界检查、除零/NaN 策略沿用现状、帧深硬上限；内存全部来自配置声明的静态槽池。
- 现有 `element_*.c` 注册为 FFI；老配置走 legacy 适配器，逻辑零改动继续跑。
- 热加载（inotify/MD5/快照/失败保留旧配置）完全复用 `logic_visual_programming.c` 既有机制。

---

## 七、分期路线（每期独立可交付、可回退）

| 阶段 | 内容 | 交付价值 |
|---|---|---|
| **P0 补齐控制流（低风险起步）** | 固件补注册并实现 SWITCH/WHILE/FOR/DO_WHILE 的 NextID 执行 + 循环步数保护；建立 C#/C 表达式黄金用例对拍（含 `element_compare.c` 精度量化行为） | 不新增概念，先让现有图形范式达到"结构化控制完备"，并锁住双端语义一致性 |
| **P1 变量与脚本** | VCL 0.1：命名变量、全局变量表、三元/复合赋值/自增减；SCRIPT 元件（无函数无数组）；固件最小 VM；上位机编辑器+类型检查 | 画布复杂度立刻下降，算法可写可读；新老引擎并存 |
| **P2 过程抽象** | 函数库 + CALL/RETURN + 局部作用域 + break/continue + 一维数组；元件全面 FFI 化，VM 成为主执行路径 | 复用、封装、复杂策略（状态机、排序、多点巡检）成为可能，达成核心目标 |
| **P3 完备化** | struct、受限字符串、二维数组；IR 紧凑二进制；可选 C 代码生成后端（上位机离线仿真 / 高性能网关掉线编译） | 能力收尾与性能/带宽优化 |

每一期的验收都跑同一套黄金向量：**C 参考实现 ↔ C# 仿真器 ↔ 固件 VM 三方对拍**，并保留现有回归工程和存量 JSON 样例不动。

---

## 八、需要拍板的决策点

1. **终态形态**：纯图形加元件 vs 图形+脚本混合——本方案推荐后者，这是工作量与表达力天花板的根本取舍。
2. **老 NextID 引擎去留**：建议作为 legacy 适配器长期保留（现场存量配置多），P2 后再评估退役。
3. **递归**：建议直接禁止（静态检查拒绝），工业策略用循环+显式栈更可验证。
4. **struct / 字符串范围**：若近期策略只涉及数值与状态字（位运算 i32/u32 已覆盖），可压到 P3。
5. **目标硬件边界**：当前是 ARM Linux 用户态（可 malloc），VM 方案无压力；若未来要求同一下装格式跑裸机单片机，需要再定义一个资源受限子集。

---

## 九、涉及代码索引

| 主题 | 位置 |
|---|---|
| 元件类型枚举/端口/参数模型 | `LogicEngineConfigTool/Models/ElementModel.cs` |
| 控制流模型 | `LogicEngineConfigTool/Models/ControlFlowModels.cs` |
| 表达式 AST/解析器 | `LogicEngineConfigTool/Models/ExpressionSyntax.cs`、`Services/ExpressionParser.cs` |
| 控制流编译流水线 | `LogicEngineConfigTool/Services/ControlFlow/` |
| 回归测试 | `LogicEngineConfigTool.RegressionTests/Program.cs`、`Fixtures/` |
| 固件引擎（权威树） | `D:\repo\dfe\LinuxApp\linuxttu\src\logicengine\` |
| 固件元件注册表 | `logicengine/logic_engine_v2.c`（`LogicEngineV2_RegisterBaseElements`） |
| 固件任务线程/NextID 调度/热加载 | `logicengine/logic_visual_programming.c` |
| 固件元件基类/虚表 | `logicengine/logic_element_base.h`、`elements/element_base.c` |
| IF 元件（跳转语义参考） | `logicengine/elements/element_flow.c` |
| 表达式求值器（文法基线） | `src/protocol/DataCalculation/eval.c` |
| 精度比较（主版本新增） | `logicengine/elements/element_compare.c` |
| 控制流算法文档 | `documents/结构化流程图编译与NextID生成算法.md`、`documents/IF控制流NextID计算算法说明.md` |

> 注：`D:\repo\dfe\linuxttu` 为旧副本，勿作为改造基线；仅 `element_compare.c` 存在版本差异，其余文件 MD5 一致。
