# 流式输出 + 工具调用：anthropic vs LangChain

## 你的问题痛点

在使用 LangChain 的 ReAct 循环做 text2sql 时：

```
用户查询
    ↓
┌─────────────────────────────────────┐
│  同一个接口调用（stream=True）       │
├─────────────────────────────────────┤
│  ??? 是工具调用还是 Final Answer？   │
│  ??? chunk 的结构是什么？            │
│  ??? 如何判断工具调用完成？          │
└─────────────────────────────────────┘
```

**核心问题**：LangChain 的流式输出中，工具调用和文本输出的判断不够清晰。

---

## anthropic 的解决方案

### 1. 明确的事件类型

anthropic 的流式响应有**明确的 `event.type`**：

```python
for event in stream:
    if event.type == "text_block":
        # ← 纯文本输出（Final Answer 或思考）
        print(event.delta.text)

    elif event.type == "content_block_start":
        # ← 工具调用开始
        if event.content_block.type == "tool_use":
            print(f"调用工具: {event.content_block.name}")

    elif event.type == "content_block_delta":
        # ← 工具调用参数片段
        if event.delta.type == "input_json_delta":
            # 累积参数片段

    elif event.type == "content_block_stop":
        # ← 工具调用结束
        # 解析完整参数，执行工具
```

### 2. 清晰的状态机

```
content_block_start → content_block_delta (多次) → content_block_stop
     ↓                      ↓                          ↓
  工具名信息            参数片段累积               工具调用完成
```

### 3. 与文本输出完全分离

```
流式响应 =
    ├─ text_block 事件         → 用户看到的文本
    └─ content_block_* 事件    → 程序处理的工具调用
```

---

## 对比：LangChain vs anthropic

| 特性 | LangChain | anthropic SDK |
|------|-----------|---------------|
| **事件类型** | 混在一起，需要额外判断 | 明确的 `event.type` |
| **工具调用识别** | 通过 chunk 类型判断 | `content_block_start` 明确标记 |
| **参数累积** | 需要自己处理 | `input_json_delta` 自动提供 |
| **状态判断** | 模糊 | 清晰的开始/结束事件 |
| **代码复杂度** | 高 | 低 |

---

## 实际代码对比

### LangChain 方式（模糊）

```python
for chunk in stream:
    if chunk.tool_calls:
        # 工具调用片段，但不知道是开始还是结束
        # 需要自己维护状态
        pass
    elif chunk.content:
        # 文本输出
        pass
```

### anthropic 方式（清晰）

```python
for event in stream:
    if event.type == "content_block_start":
        # 工具调用开始 - 明确的信号
        pass
    elif event.type == "content_block_stop":
        # 工具调用结束 - 明确的信号
        pass
    elif event.type == "text_block":
        # 文本输出 - 与工具调用完全分离
        pass
```

---

## 为什么 anthropic 更好？

1. **设计清晰**：事件类型从一开始就是为了区分工具和文本设计的
2. **状态明确**：每个阶段都有对应的事件类型
3. **易于处理**：不需要额外的状态管理逻辑
4. **官方支持**：这是 SDK 原生支持的，不是 hack

---

## 建议

如果你：
- 需要在 ReAct 循环中同时支持流式输出和工具调用
- 希望代码清晰、易于维护
- 不想花时间处理 chunk 的复杂状态判断

**直接使用 anthropic SDK**，不要用 LangChain 的封装。

我已经为你创建了两个示例：
- `demo_streaming_tools.py` - 基础的流式+工具演示
- `demo_react_streaming.py` - 完整的 ReAct 循环实现

设置 API Key 后可以直接运行：
```bash
export ANTHROPIC_API_KEY=your-key-here
python demo_react_streaming.py
```
