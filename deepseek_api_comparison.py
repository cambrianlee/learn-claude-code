"""
最终对比测试 - DeepSeek 两个接口的实际差异
使用直接 HTTP 请求（避免 SDK 问题）
"""

import os
import json
from dotenv import load_dotenv, find_dotenv
import requests

load_dotenv(find_dotenv(), override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

print("="*80)
print("DeepSeek 两个接口的完整对比")
print("="*80)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

# ============================================================================
# 对比维度 1: 基础信息
# ============================================================================
print("\n" + "="*80)
print("【维度 1】基础信息对比")
print("="*80)

comparison = {
    "OpenAI 兼容接口": {
        "Base URL": "https://api.deepseek.com",
        "端点": "/v1/chat/completions",
        "认证头": "Authorization: Bearer <api_key>",
        "SDK": "openai SDK",
        "API 标准": "OpenAI Chat Completions API"
    },
    "Anthropic 兼容接口": {
        "Base URL": "https://api.deepseek.com/anthropic",
        "端点": "/v1/messages",
        "认证头": "x-api-key: <api_key>",
        "SDK": "anthropic SDK",
        "API 标准": "Anthropic Messages API"
    }
}

for name, info in comparison.items():
    print(f"\n【{name}】")
    for key, value in info.items():
        print(f"  {key}: {value}")

# ============================================================================
# 对比维度 2: 请求结构
# ============================================================================
print("\n\n" + "="*80)
print("【维度 2】请求结构对比")
print("="*80)

# OpenAI 兼容接口请求
openai_request = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 50,
    "stream": False
}

print("\n【OpenAI 兼容接口】请求结构:")
print(json.dumps(openai_request, ensure_ascii=False, indent=2))

# Anthropic 兼容接口请求
anthropic_request = {
    "model": "deepseek-chat",
    "max_tokens": 50,
    "system": "你是一个助手",  # system 是独立参数
    "messages": [{
        "role": "user",
        "content": [{"type": "text", "text": "你好"}]  # content 是对象数组
    }]
}

print("\n【Anthropic 兼容接口】请求结构:")
print(json.dumps(anthropic_request, ensure_ascii=False, indent=2))

# ============================================================================
# 对比维度 3: 响应结构
# ============================================================================
print("\n\n" + "="*80)
print("【维度 3】响应结构对比（实际测试）")
print("="*80)

# 测试 OpenAI 兼容接口
print("\n【OpenAI 兼容接口】响应:")
response_openai = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    },
    json=openai_request
).json()

print(json.dumps(response_openai, ensure_ascii=False, indent=2))

# 测试 Anthropic 兼容接口
print("\n\n【Anthropic 兼容接口】响应:")
response_anthropic = requests.post(
    "https://api.deepseek.com/anthropic/v1/messages",
    headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    },
    json=anthropic_request
).json()

print(json.dumps(response_anthropic, ensure_ascii=False, indent=2))

# ============================================================================
# 对比维度 4: 关键差异总结
# ============================================================================
print("\n\n" + "="*80)
print("【维度 4】关键差异总结")
print("="*80)

differences = [
    {
        "特性": "System Prompt 位置",
        "OpenAI": "在 messages 数组中，role='system'",
        "Anthropic": "独立的 system 参数"
    },
    {
        "特性": "Content 结构",
        "OpenAI": "字符串：\"content\": \"文本\"",
        "Anthropic": "对象数组：\"content\": [{\"type\": \"text\", \"text\": \"文本\"}]"
    },
    {
        "特性": "响应结构",
        "OpenAI": "{ choices: [{ message: { role, content } }] }",
        "Anthropic": "{ content: [{ type: \"text\", text: \"文本\" }] }"
    },
    {
        "特性": "Token 计数",
        "Openai": "usage.prompt_tokens, usage.completion_tokens",
        "Anthropic": "usage.input_tokens, usage.output_tokens"
    },
    {
        "特性": "认证方式",
        "OpenAI": "Bearer token",
        "Anthropic": "x-api-key header"
    },
    {
        "特性": "停止序列参数",
        "OpenAI": "stop (字符串或数组)",
        "Anthropic": "stop_sequences (字符串数组)"
    }
]

for diff in differences:
    print(f"\n{diff['特性']}:")
    print(f"  OpenAI:   {diff.get('OpenAI', diff.get('Openai'))}")
    print(f"  Anthropic: {diff['Anthropic']}")

# ============================================================================
# 对比维度 5: 工具调用差异
# ============================================================================
print("\n\n" + "="*80)
print("【维度 5】工具调用结构差异")
print("="*80)

print("\n【OpenAI 兼容接口】工具定义:")
openai_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市"}
            },
            "required": ["city"]
        }
    }
}
print(json.dumps(openai_tool, ensure_ascii=False, indent=2))

print("\n\n【Anthropic 兼容接口】工具定义:")
anthropic_tool = {
    "name": "get_weather",
    "description": "获取天气",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市"}
        },
        "required": ["city"]
    }
}
print(json.dumps(anthropic_tool, ensure_ascii=False, indent=2))

print("\n\n【工具调用响应结构】:")
print("OpenAI: tool_calls[].function.arguments (JSON 字符串)")
print("Anthropic: content[].input (JSON 对象)")

# ============================================================================
# 对比维度 6: 流式输出事件类型
# ============================================================================
print("\n\n" + "="*80)
print("【维度 6】流式输出事件类型")
print("="*80)

print("\n【OpenAI 兼容接口】:")
print("  - ChatCompletionChunk (每次返回)")
print("  - delta.content (文本增量)")

print("\n【Anthropic 兼容接口】:")
print("  - message_start (开始)")
print("  - content_block_start (内容块开始)")
print("  - content_block_delta (内容增量)")
print("  - text 事件 (type='text', text=内容) ← 你遇到的关键点！")
print("  - input_json (工具参数增量)")
print("  - content_block_stop (内容块结束)")
print("  - message_stop (结束)")

# ============================================================================
# 对比维度 7: 使用建议
# ============================================================================
print("\n\n" + "="*80)
print("【维度 7】使用建议")
print("="*80)

recommendations = {
    "使用 OpenAI 兼容接口": [
        "已有 OpenAI SDK 代码，想快速迁移",
        "需要兼容多个 LLM 提供商",
        "使用 LangChain 等框架",
        "需要更广泛的生态支持"
    ],
    "使用 Anthropic 兼容接口": [
        "使用 Claude Code 等 Anthropic 工具",
        "需要 Anthropic SDK 的高级功能",
        "正在使用 Anthropic SDK 并想切换到 DeepSeek",
        "需要更细粒度的事件控制（如你的 ReAct 场景）"
    ]
}

for scenario, reasons in recommendations.items():
    print(f"\n{scenario}:")
    for reason in reasons:
        print(f"  ✅ {reason}")

print("\n" + "="*80)
print("对比完成")
print("="*80)
