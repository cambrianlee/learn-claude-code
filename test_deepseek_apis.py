"""
测试 DeepSeek 的两个接口：
1. OpenAI 兼容接口：https://api.deepseek.com
2. Anthropic 兼容接口：https://api.deepseek.com/anthropic
"""

import os
import json
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
env_path = find_dotenv()
load_dotenv(env_path, override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

print("="*70)
print("DeepSeek API 对比测试")
print("="*70)
print(f"API Key: {api_key[:15]}...{api_key[-6:]}")
print()

# ============================================================================
# 测试 1: OpenAI 兼容接口
# ============================================================================
print("\n" + "="*70)
print("【测试 1】OpenAI 兼容接口")
print("Base URL: https://api.deepseek.com")
print("="*70)

try:
    from openai import OpenAI

    client_openai = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    print("\n📤 请求结构:")
    request_openai = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个简短的助手"},
            {"role": "user", "content": "用一句话介绍你自己"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    print(json.dumps(request_openai, ensure_ascii=False, indent=2))

    print("\n📥 响应结构:")
    response_openai = client_openai.chat.completions.create(**request_openai)

    # 打印响应结构
    response_dict_openai = response_openai.model_dump()
    print(json.dumps(response_dict_openai, ensure_ascii=False, indent=2))

    print(f"\n✅ 成功！")
    print(f"   内容: {response_openai.choices[0].message.content}")
    print(f"   模型: {response_openai.model}")
    print(f"   Token 使用: {response_openai.usage}")

except Exception as e:
    print(f"❌ 失败: {e}")

# ============================================================================
# 测试 2: Anthropic 兼容接口
# ============================================================================
print("\n" + "="*70)
print("【测试 2】Anthropic 兼容接口")
print("Base URL: https://api.deepseek.com/anthropic")
print("="*70)

try:
    import anthropic

    client_anthropic = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://api.deepseek.com/anthropic"
    )

    print("\n📤 请求结构:")
    request_anthropic = {
        "model": "deepseek-chat",
        "max_tokens": 100,
        "system": "你是一个简短的助手",
        "messages": [{
            "role": "user",
            "content": "用一句话介绍你自己"
        }]
    }
    print(json.dumps(request_anthropic, ensure_ascii=False, indent=2))

    print("\n📥 响应结构:")
    response_anthropic = client_anthropic.messages.create(**request_anthropic)

    # 打印响应结构
    response_dict_anthropic = response_anthropic.model_dump()
    print(json.dumps(response_dict_anthropic, ensure_ascii=False, indent=2))

    print(f"\n✅ 成功！")
    print(f"   内容: {response_anthropic.content[0].text}")
    print(f"   模型: {response_anthropic.model}")
    print(f"   Token 使用: {response_anthropic.usage}")

except Exception as e:
    print(f"❌ 失败: {e}")

# ============================================================================
# 测试 3: 流式输出对比
# ============================================================================
print("\n" + "="*70)
print("【测试 3】流式输出对比")
print("="*70)

# OpenAI 兼容接口流式输出
print("\n--- OpenAI 兼容接口流式输出 ---")
try:
    print("📤 流式响应:")
    stream_openai = client_openai.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "数到 5"}],
        stream=True,
        max_tokens=50
    )

    chunks = []
    for chunk in stream_openai:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            chunks.append(content)
            print(content, end="", flush=True)

    print(f"\n\n   收到 {len(chunks)} 个 chunks")
    print(f"   类型: {type(stream_openai)}")

except Exception as e:
    print(f"❌ 失败: {e}")

# Anthropic 兼容接口流式输出
print("\n--- Anthropic 兼容接口流式输出 ---")
try:
    print("📤 流式响应:")
    with client_anthropic.messages.stream(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "数到 5"}],
        max_tokens=50
    ) as stream:
        events = []
        for event in stream:
            events.append({"type": event.type})
            if event.type == "text":
                print(event.text, end="", flush=True)

    print(f"\n\n   收到 {len(events)} 个事件")
    print(f"   事件类型: {set(e['type'] for e in events)}")

except Exception as e:
    print(f"❌ 失败: {e}")

# ============================================================================
# 测试 4: 工具调用对比
# ============================================================================
print("\n" + "="*70)
print("【测试 4】工具调用对比")
print("="*70)

# 定义工具
tools_openai = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

tools_anthropic = [
    {
        "name": "get_weather",
        "description": "获取天气信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    }
]

# OpenAI 兼容接口工具调用
print("\n--- OpenAI 兼容接口工具调用 ---")
try:
    response_tools_openai = client_openai.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
        tools=tools_openai
    )

    print("✅ 工具调用响应:")
    print(json.dumps(response_tools_openai.model_dump(), ensure_ascii=False, indent=2))

except Exception as e:
    print(f"❌ 失败: {e}")

# Anthropic 兼容接口工具调用
print("\n--- Anthropic 兼容接口工具调用 ---")
try:
    response_tools_anthropic = client_anthropic.messages.create(
        model="deepseek-chat",
        max_tokens=1024,
        messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
        tools=tools_anthropic
    )

    print("✅ 工具调用响应:")
    print(json.dumps(response_tools_anthropic.model_dump(), ensure_ascii=False, indent=2))

except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*70)
print("测试完成")
print("="*70)
