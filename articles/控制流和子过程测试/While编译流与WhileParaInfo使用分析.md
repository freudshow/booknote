# While 编译流与 `WhileParaInfo` 使用分析

## 1. 分析结论

当前 While 编译流生成控制流编译计划时，主要使用以下两类信息：

1. While 元件中的 `ControlFlowInfo`；
2. 画布中实际存在的控制流连线。

用户在 `WhileParaInfo` 中配置的 `Link`、`Dev`、`Reg`、`LoopMode` 和 `MaxIterations`，当前不会参与 `ControlFlowMutationPlan` 的生成，也不会改变 While 的分支目标、执行顺序或循环回跳目标。

`WhileParaInfo` 当前在编译相关流程中有两种用途：

- 编译校验阶段：只判断 `WhileParaInfo` 对象是否存在，用于识别新 While 协议并跳过旧协议的条件输入连接检查；
- 编译计划应用阶段：根据编译结果回写 `ContinueNextID` 和 `ExitNextID`。

因此，对“用户设置的 `WhileParaInfo` 是否被用到编译流”的准确回答是：

> **对象是否存在会影响一项兼容性校验；其中的用户配置字段目前没有参与 While 控制流编译计划的生成。**

本分析基于源码静态检查，未修改代码，也未执行构建或回归测试。

## 2. While 元件的参数结构

While 元件在 `ElementControlFlowWhile` 中创建两组参数：

### 2.1 `ControlFlowInfo`

该参数描述控制流协议，包含：

- 控制流类型 `Kind`，值为 `ControlFlowKind.While`；
- Body 分支；
- Exit 分支；
- While 条件表达式；
- 控制流目标和表达式等结构化编译信息。

While 的默认输出端口为：

| 分支 | 端口 |
| --- | ---: |
| Body | 0 |
| Exit | 1 |

源码位置：

- `LogicEngineConfigTool/Elements/ElementControlFlowWhile.cs:42-102`

### 2.2 `WhileParaInfo`

`WhileParaInfo` 由 While 元件作为第二个参数创建，主要字段如下：

| 字段 | 默认值 | 当前作用 |
| --- | ---: | --- |
| `Link` | `-1` | 实时库链路配置，参与参数校验 |
| `Dev` | `-1` | 实时库设备配置，参与参数校验 |
| `Reg` | `-1` | 实时库寄存器配置，参与参数校验 |
| `ContinueNextID` | `-1` | Body 分支目标，由编译计划应用后同步 |
| `ExitNextID` | `-1` | Exit 分支目标，由编译计划应用后同步 |
| `MaxIterations` | `200` | 最大迭代次数配置 |
| `LoopMode` | `1` | 循环模式：`ConditionYX` 或 `MaxIterations` |

字段定义位置：

- `LogicEngineConfigTool/Models/ControlFlowModels.cs:102-117`

需要注意：While 条件表达式不在 `WhileParaInfo` 中，而在 `ControlFlowInfo.Expressions` 中。

## 3. 编译流的实际处理过程

控制流编译入口位于：

- `LogicEngineConfigTool/Services/ControlFlow/ControlFlowCompilationService.cs:28-81`

整体流程为：

```text
规范化任务图
    -> 提取控制流描述
    -> 校验控制流描述和表达式
    -> 构建结构化区域
    -> 线性化生成 ControlFlowMutationPlan
    -> 校验编译计划
```

### 3.1 提取统一控制流协议

编译器通过兼容性提取器读取 `ControlFlowInfo`，主要读取：

- `Kind`；
- `JoinNextID`；
- `EntryNextID`；
- `LoopBackNextID`；
- `ExitNextID`；
- `Expressions`；
- `Branches`。

分支信息还包括分支类型、顺序、端口号、兼容性标签、表达式和目标 ID。

源码位置：

- `LogicEngineConfigTool/Services/ControlFlow/CompatibilityControlFlowExtractor.cs:65-117`

### 3.2 实际控制流连线优先决定分支目标

提取器会读取画布中实际的控制流边，将源端口映射到目标元件 ID：

- `CompatibilityControlFlowExtractor.cs:303-316`

如果元件协议中的分支目标与画布实际连线不一致，物理连线优先，并可能产生 `CFG020` 警告：

- `CompatibilityControlFlowExtractor.cs:119-160`

因此，While 的 Body 和 Exit 入口最终主要由实际控制流连线决定，而不是由 `WhileParaInfo.ContinueNextID` 或 `WhileParaInfo.ExitNextID` 作为输入决定。

### 3.3 While 的结构化编译

编译器要求 While 至少具有：

- 一个 Body 分支；
- 一个 Exit 分支。

对应校验位于：

- `LogicEngineConfigTool/Services/ControlFlow/ControlFlowCompilationService.cs:243-265`

线性化阶段根据控制流描述、分支目标和结构化区域信息生成编译计划，涉及：

- Join 目标；
- Body/Entry 目标；
- LoopBack 目标；
- Exit 目标；
- 条件表达式。

对应逻辑位于：

- `LogicEngineConfigTool/Services/ControlFlow/ExecutionLinearizer.cs:322-372`
- `ExecutionLinearizer.cs:441-464`

## 4. `WhileParaInfo` 在编译阶段的实际使用

### 4.1 只判断对象是否存在

编译校验中存在如下判断：

```csharp
bool isNewWhileProtocol = descriptor.Kind == ControlFlowKind.While
    && element.Params != null
    && element.Params.Any(param => param.Value is WhileParaInfo);
```

源码位置：

- `LogicEngineConfigTool/Services/ControlFlow/ControlFlowCompilationService.cs:299-308`

如果 `WhileParaInfo` 存在，编译器跳过旧协议下的条件输入端口检查；如果不存在，则继续检查输入端口 0 是否存在条件连接：

- `ControlFlowCompilationService.cs:305-338`

这说明编译器使用了 `WhileParaInfo` 的**类型存在性**，但没有读取其字段值。

### 4.2 具体字段没有参与编译计划生成

在当前控制流编译路径中，没有读取以下字段来生成 `ControlFlowMutationPlan`：

- `Link`；
- `Dev`；
- `Reg`；
- `LoopMode`；
- `MaxIterations`；
- `ContinueNextID`；
- `ExitNextID`。

因此，这些字段不会直接改变：

- 元件线性执行顺序；
- 普通 `NextID`；
- Body 或 Exit 分支入口；
- LoopBack 目标；
- Join 或 Exit 目标。

特别是：

- `LoopMode` 不会改变编译器采用的循环结构；
- `MaxIterations` 不会在当前编译器中生成最大迭代限制；
- `Link`、`Dev`、`Reg` 不会被转换成控制流条件表达式。

## 5. 编译计划应用阶段的使用

虽然编译阶段不读取 `WhileParaInfo` 的具体字段，但 `ControlFlowPlanApplier` 在应用编译计划时会同步 While 参数：

- `LogicEngineConfigTool/Services/ControlFlow/ControlFlowPlanApplier.cs:82-90`
- `ControlFlowPlanApplier.cs:220-248`

同步结果为：

```text
WhileParaInfo.ContinueNextID = 编译后 Body 分支目标
WhileParaInfo.ExitNextID     = 编译后 Exit 分支目标
```

这两个字段是**编译结果的回写字段**，而不是编译输入字段。即：

```text
ControlFlowInfo + 实际控制流连线
    -> ControlFlowMutationPlan
    -> 回写 ContinueNextID / ExitNextID
```

而不是：

```text
WhileParaInfo
    -> 生成 While 控制流编译计划
```

如果计划应用前用户手工修改了这两个字段，应用编译计划时仍会根据实际 Body/Exit 分支目标覆盖它们。并且这两个字段在属性编辑器中是只读的：

- `LogicEngineConfigTool/Views/ElementPropertyEditorFactory.cs:1225-1235`

## 6. 用户配置的保存、显示和校验用途

当前 `WhileParaInfo` 的用户配置并非完全没有用途，但用途主要在 UI、保存和参数校验侧。

### 6.1 `LoopMode`

`LoopMode` 用于：

- 在 `ConditionYX` 和 `MaxIterations` 之间选择模式；
- 决定实时库选择器的类型限制；
- 决定 `MaxIterations` 编辑框是否启用；
- 进行枚举值合法性校验。

相关位置：

- `LogicEngineConfigTool/Views/ElementPropertyEditorFactory.cs:1241-1250`
- `ElementPropertyEditorFactory.cs:1273-1286`
- `LogicEngineConfigTool/Services/WhileParameterValidationService.cs:24-28`

### 6.2 `MaxIterations`

`MaxIterations` 可以在 UI 中编辑，并在最大迭代模式下进行范围校验，当前范围为 `1..100000`：

- `LogicEngineConfigTool/Services/WhileParameterValidationService.cs:36-44`

但是，目前没有证据表明它被控制流编译器转换为实际循环次数限制。

### 6.3 `Link`、`Dev`、`Reg`

这三个字段会被保存并参与 While 参数校验。在 `ConditionYX` 模式下，校验服务会使用它们查询实时库参数：

- `LogicEngineConfigTool/Services/WhileParameterValidationService.cs:30-75`

但该查询和校验结果不会进入当前 `ControlFlowMutationPlan` 的控制流结构生成逻辑。

## 7. 字段作用汇总

| 字段 | 用户可配置 | UI/保存/校验使用 | 控制流编译输入 | 编译后回写 |
| --- | --- | --- | --- | --- |
| `Link` | 是 | 是 | 否 | 否 |
| `Dev` | 是 | 是 | 否 | 否 |
| `Reg` | 是 | 是 | 否 | 否 |
| `LoopMode` | 是 | 是 | 否 | 否 |
| `MaxIterations` | 是 | 是 | 否 | 否 |
| `ContinueNextID` | 否，UI 只读 | 是 | 否 | 是 |
| `ExitNextID` | 否，UI 只读 | 是 | 否 | 是 |

## 8. 与 DoWhile 的区别

当前 `WhileParaInfo` 的兼容性判断明确限定为：

```csharp
descriptor.Kind == ControlFlowKind.While
```

因此：

- While 会检查 `WhileParaInfo` 是否存在；
- DoWhile 不使用这项 `WhileParaInfo` 判断；
- DoWhile 使用 `ControlFlowInfo` 和 `Entry/Repeat/Exit` 分支协议。

## 9. 测试覆盖情况

当前 `LogicEngineConfigTool.RegressionTests` 没有 While 专项覆盖，搜索不到以下专项引用：

- `WhileParaInfo`；
- `ElementControlFlowWhile`；
- `ControlFlowKind.While`；
- `ContinueNextID`；
- `LoopMode`；
- `MaxIterations`。

现有回归 fixture 主要覆盖 IF 控制流，例如：

- `LogicEngineConfigTool.RegressionTests/Fixtures/IF-YT.baseline.json`
- `LogicEngineConfigTool.RegressionTests/Fixtures/multi.if.baseline.json`

因此，目前没有回归测试验证：

- While 编译后 `ContinueNextID` 和 `ExitNextID` 的写回；
- `LoopMode` 是否影响实际执行；
- `MaxIterations` 是否限制实际循环次数；
- `Link/Dev/Reg` 是否被运行时执行器消费。

## 10. 后续实现关注点

如果产品要求用户设置的 `WhileParaInfo` 真正参与 While 执行，需要进一步明确并实现以下链路：

1. 定义 `LoopMode` 与运行时循环判断之间的映射；
2. 在 `ConditionYX` 模式下，将 `Link/Dev/Reg` 转换为可执行的条件读取逻辑；
3. 在 `MaxIterations` 模式下，将 `MaxIterations` 转换为可执行的迭代计数逻辑；
4. 明确这些参数应进入 `ControlFlowInfo`、编译计划，还是由运行时执行器直接读取；
5. 增加 While fixture 和回归测试，验证编译、计划应用、序列化以及实际执行结果。

在未完成上述链路前，`WhileParaInfo` 更接近“参数模型、UI 编辑模型和编译结果同步模型”，而不是当前控制流编译器的完整输入模型。

## 11. While 编译递归与栈溢出风险分析

### 11.1 结论

当前 While 编译流不会因为正常的 While 回边产生编译阶段无限递归，也不会在正常规模的 While 图上直接导致栈溢出。

While 的 Body 回边只是被转换为控制流编译结果中的跳转元数据，例如 continuation 和 `LoopBackNextID`，不会使编译器重新执行 While 或无限展开同一个 While。

但是，编译器中仍存在一般性的递归深度风险：

- `ExecutionLinearizer.EmitRegion` 使用递归处理嵌套控制流区域；
- `StableDataScheduler.VisitData` 使用递归处理数据依赖前驱。

如果输入包含极深的合法嵌套控制流或极长的数据依赖链，理论上仍可能因为 .NET 调用栈耗尽而触发 `StackOverflowException`。

因此需要区分：

> **While 回边本身不会造成无限递归；极深图结构可能造成有限递归深度过大。**

本节结论来自源码静态检查，当前未进行深度压力测试，也未实际复现栈溢出。

### 11.2 编译调用链不执行运行时 While

当前编译调用链为：

```text
TransactionalConfigSaveService.Save
    -> ControlFlowCompilationService.CompileAll
    -> ControlFlowCompilationService.Compile
        -> 图规范化
        -> 控制流提取
        -> 控制流校验
        -> 结构化区域构建
        -> 执行顺序线性化
        -> 编译计划校验
    -> ControlFlowPlanApplier.Apply
```

编译阶段只对有限图进行分析并生成 `ControlFlowMutationPlan`，不会按照 While 条件实际运行循环，也不会在编译阶段重复执行循环体。

相关源码位置：

- `LogicEngineConfigTool/Services/ControlFlow/TransactionalConfigSaveService.cs:37-105`
- `LogicEngineConfigTool/Services/ControlFlow/ControlFlowCompilationService.cs:28-81`

### 11.3 While 回边不会重新进入 `EmitRegion`

`ExecutionLinearizer.EmitRegion` 是递归方法：

- `LogicEngineConfigTool/Services/ControlFlow/ExecutionLinearizer.cs:112-203`
- 递归调用位置：`ExecutionLinearizer.cs:172`

While Body 分支会被识别为循环回边：

```csharp
var branchContinuation = IsLoopBackBranch(descriptor.Kind, branch.Kind)
    ? header
    : join;
```

其中 `header` 是 While 控制头 ID，主要用于生成后续跳转目标。它表示编译结果中的：

```text
While Body 区域结束 -> While Header
```

而不是：

```text
编译 While
    -> 递归编译 Body
    -> 再次递归编译 While
    -> 无限递归
```

While/FOR Body 分支被识别为回边的位置：

- `ExecutionLinearizer.cs:451-464`

### 11.4 编译器中的环检测和去重机制

当前代码包含多层保护，避免控制流回边或数据依赖环被无限遍历。

#### 控制头递归保护

`ExecutionLinearizer` 使用 `_activeControls` 记录当前递归路径上的控制头：

- 字段定义：`ExecutionLinearizer.cs:41-43`
- 检查位置：`ExecutionLinearizer.cs:144-156`

如果同一控制头在当前递归路径上被再次进入，编译器报告 `CFG041`：

```text
Recursive or irreducible control region detected.
```

随后停止继续深入，而不是无限递归。

#### 元件发射去重

`ExecutionLinearizer._emitted` 防止同一个元件被重复加入线性化结果：

- `ExecutionLinearizer.cs:34`
- `ExecutionLinearizer.cs:287-299`

编译结束时还会校验计划是否覆盖每个元件且没有重复：

- `ControlFlowCompilationService.cs:494-521`

#### 分支区域显式栈遍历

`CollectOwnedBranch` 不使用调用栈递归，而是使用 `Stack<int>` 和 `HashSet<int>`：

- `ExecutionLinearizer.cs:208-284`

它会在以下情况停止处理当前节点：

- 到达 Join；
- 到达当前控制头；
- 节点不在允许区域内；
- 节点已经访问过。

因此，While 的 `Body -> While Header` 回边不会让该区域收集算法无限循环。

#### 结构化区域显式栈和 BFS

`StructuredRegionBuilder.CollectUntil` 使用显式栈和访问集合：

- `StructuredRegionBuilder.cs:271-334`

`StructuredRegionBuilder.Reachable` 使用 BFS 和结果字典去重：

- `StructuredRegionBuilder.cs:397-431`

这些算法可以处理包含回边的有限图，不会因为访问同一节点而无限遍历。

#### 数据依赖环检测

`StableDataScheduler.VisitData` 递归访问数据前驱：

- `LogicEngineConfigTool/Services/ControlFlow/StableDataScheduler.cs:53-100`

它使用：

- `result`：记录已经完成访问的节点；
- `visiting`：记录当前递归路径上的节点。

当某个节点已经存在于 `visiting` 中时，说明发现数据依赖环，编译器报告 `CFG040` 并返回，而不是继续递归。

### 11.5 仍然存在的栈深度风险

环检测只能避免逻辑上的无限重复，不能限制合法递归的深度。

#### 极深嵌套控制流

类似下面的结构会增加 `EmitRegion` 的调用深度：

```text
While 1
    -> If 1
        -> While 2
            -> If 2
                -> While 3
                    -> ...
```

不同控制头组成的合法嵌套不会触发 `_activeControls` 的“同一控制头重入”检查，但递归层数可能持续增加。嵌套深度足够大时，仍可能导致调用栈耗尽。

#### 极长数据依赖链

类似下面的无环数据依赖链会增加 `VisitData` 的递归深度：

```text
Data1 -> Data2 -> Data3 -> ... -> DataN
```

即使不存在数据依赖环，链条足够长时仍可能触发栈溢出。

当前代码没有发现针对这两类递归的显式深度限制，也没有发现 `StackOverflowException` 专项捕获或测试。

### 11.6 编译无限递归与运行时无限循环的区别

编译器不会执行运行时 While，因此以下问题属于运行时风险，而不是编译器递归风险：

- 循环条件始终为真；
- `MaxIterations` 没有被下游运行时消费；
- Body 直接连接回 While 自身且运行时未正确先判断条件；
- Exit 目标错误地指向循环体内部；
- 非法的 `LoopBackNextID` 或 `ExitNextID` 指向回环节点。

当前结构化检查能够发现部分结构错误，例如：

- Body/Exit 分支数量错误：`CFG058`；
- 循环体为空：`CFG031`；
- While 控制头不能支配 Body 入口：`CFG032`；
- 控制区域递归或不可约：`CFG041`；
- 编译计划没有覆盖所有元件或存在重复：`CFG060`。

但从现有源码检查来看，仍未发现对以下情况的完整约束：

- Body 不能直接指向 While Header；
- Exit 必须位于循环区域外；
- Body 和 Exit 目标不能相同；
- `LoopBackNextID` 必须是合法回边；
- `ExitNextID` 必须是循环外出口；
- `LoopBackNextID` 必须与 While Body 语义一致。

如果这些异常拓扑被编译并被下游运行时直接执行，可能形成运行时无限循环，但这与编译阶段的 C# 栈溢出是不同问题。

### 11.7 风险汇总

| 场景 | 编译无限递归 | 编译栈溢出 | 运行时无限循环 |
| --- | ---: | ---: | ---: |
| 正常 While Body 回到 While Header | 否 | 否 | 取决于运行时条件 |
| While 回边重复区域收集 | 否，有访问集合保护 | 否 | 不适用 |
| 同一控制头递归重入 | 否，报告 `CFG041` | 通常否 | 不适用 |
| 数据依赖环 | 否，报告 `CFG040` | 通常否 | 不适用 |
| 极深嵌套 While/If/For | 否 | 理论上可能 | 不适用 |
| 极长无环数据依赖链 | 否 | 理论上可能 | 不适用 |
| `MaxIterations` 未被运行时消费 | 不适用 | 不适用 | 可能 |
| Exit 指向循环体内部 | 不适用 | 不适用 | 可能 |

### 11.8 测试覆盖情况

当前回归测试中没有 While 专项 fixture，也没有覆盖：

- While Body 回边；
- `LoopBackNextID`；
- `ContinueNextID`；
- `ExitNextID`；
- 多层嵌套 While；
- 深层控制流压力；
- 深层数据依赖压力；
- `StackOverflowException` 隔离进程测试。

因此，目前只能根据源码确认：正常 While 回边不会造成编译器无限递归；尚不能通过测试确定深层嵌套的最大安全深度，也不能宣称极深输入一定不会栈溢出。

如需进一步验证，建议增加：

1. 最小 While Body/Exit 回边回归测试，检查 `LoopBackNextID`、分支目标和线性化结果；
2. 独立进程深度压力测试，逐步增加嵌套 While 或数据依赖链深度，记录编译成功的最大深度以及是否出现 `StackOverflowException`；
3. 异常拓扑测试，验证 Body 直连 Header、Exit 指向循环体内部、Body/Exit 指向同一目标等情况是否被拒绝。


## 12. 本次 While 栈溢出问题的实际原因与修复

### 12.1 本次修改内容

本次修改涉及两个文件。

#### 1. `ExecutionLinearizer.cs`：固定 While Body/Exit 的入口语义

在 `CreateControlMutation` 生成 `BranchMutation` 时，While 的 `Body` 和 `Exit` 分支现在直接使用分支描述中的 `item.NextID`。这样严格遵循 While 元件对用户暴露的端口语义：

```text
输出端口 0 -> 循环体所在语句块的首个元件
输出端口 1 -> 循环退出所在语句块的首个元件
```

随后编译计划应用阶段会把两个分支入口分别回写为：

```text
ContinueNextID = Body 分支目标
ExitNextID     = Exit 分支目标
```

While 循环体末尾回到 While 头元件的语义没有改变，`LoopBackNextID` 仍然指向 While 头元件。因此三个字段分别表示：

```text
ContinueNextID = 循环体首元件 ID
LoopBackNextID = While 头元件 ID
ExitNextID     = 循环退出块首元件 ID
```

#### 2. `VisualEditorViewModel.cs`：修复保存后调试打印的无限递归

保存配置后，`SaveToFile` 会调用 `PrintSyntaxSequence` 输出控制流调试信息。该函数沿 `NextID` 打印线性链，并递归展开 `ControlFlowInfo.Branches`。

旧逻辑在每次递归调用中重新创建 `sequencePath`。本次改为由外层调用传入并在递归层之间共享同一个集合；递归返回时通过 `finally` 移除本层加入的节点。遇到当前路径中已经出现的节点时，输出回边信息并停止展开。

### 12.2 为什么会发生栈溢出

本次实际导致栈溢出的路径不是 `ExecutionLinearizer.EmitRegion`，而是保存后的调试打印函数 `PrintSyntaxSequence`。

典型 While 编译结果为：

```text
While Header
    Body 分支 -> Body 首元件 -> ... -> While Header
    Exit 分支 -> Exit 块首元件 -> ...
```

Body 尾部回到 While Header 是正确的控制流回边。但旧版打印函数每层递归都创建新的访问集合，实际调用过程变成：

```text
Print(Header, 集合 A)
    -> Print(BodyStart, 集合 B)
        -> 沿 NextID 到 Header
            -> Print(Header, 集合 C)
                -> 再次展开 Body
                    -> Print(BodyStart, 集合 D)
                        -> 再次到 Header
                            -> ...
```

因为每层都有自己的集合，内层调用看不到外层已经访问过的 While Header。Header 因而被反复当作新节点展开，最终耗尽 .NET 调用栈并触发 `StackOverflowException`。

这也是问题容易被误认为“While 编译器处理循环时无限递归”的原因：无限递归发生在保存流程中，并且紧接在编译计划应用之后；但实际调用链是调试打印，不是 While 控制流计划生成。

### 12.3 修复后的执行路径

修复后，所有递归层共享同一个 `sequencePath`：

```text
Print(Header, 集合 S)
    S = { Header }
    -> 展开 Body
        Print(BodyStart, 集合 S)
            -> 沿 NextID 再次到 Header
                Header 已存在于 S
                输出“回边 -> ID=Header”
                返回，不再展开 While Body
```

函数退出时只移除本层加入的节点，因此集合表示的是当前递归路径，而不是整个打印过程的全局集合：

- 当前路径再次遇到 While Header：判定为回边并停止递归；
- 另一个互不嵌套的分支后续访问同一汇合点：不会被前一个分支永久屏蔽。

### 12.4 与编译器本身的关系

源码中 `ExecutionLinearizer` 已有 `_activeControls`、`_emitted`、`CollectOwnedBranch` 的访问集合/去重保护，`StructuredRegionBuilder` 也使用显式栈和访问集合。因此，本次修复不能简单概括为“给 While 编译器增加防递归”，而应准确描述为：

1. 修正 While Body/Exit 分支入口，使其遵循端口目标语义；
2. 修正保存后调试打印的递归访问路径，使 While 回边不会被反复展开。

编译器仍然存在极深嵌套控制流或极长数据依赖链导致调用栈耗尽的理论风险，但那是有限递归深度过大问题，与本次由 While 回边触发的无限递归不同。

### 12.5 验证边界与后续测试

已完成源码差异核对，确认：

- While Body/Exit 分支目标直接取端口目标 `item.NextID`；
- `ContinueNextID`、`ExitNextID` 分别由 Body/Exit 分支目标回写；
- `LoopBackNextID` 保持 While 头元件语义；
- `PrintSyntaxSequence` 在递归层之间共享 `sequencePath`，并在 `finally` 中清理路径节点。

完整运行时回归尚未通过：回归程序要求仓库根目录存在 `documents/ltudevlib.json`，当前只有已跟踪的 `documents/配置文件/ltudevlib.json`，不能未经授权复制或重命名，因此程序在完整新元件测试前以退出码 1 终止。

后续应增加 While 专项回归，至少验证：

1. 输出端口 0 对应 Body 首元件；
2. 输出端口 1 对应 Exit 首元件；
3. `ContinueNextID`、`ExitNextID`、`LoopBackNextID` 的回写值；
4. Body 尾部回到 While Header 时 Header 只在线性化结果中出现一次；
5. 保存调试打印遇到回边后返回，不发生栈溢出。
