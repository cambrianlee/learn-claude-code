"""
测试 DeepSeek 流式输出的简单脚本
用于排查问题
"""

import os
from dotenv import load_dotenv, find_dotenv
from anthropic import Anthropic

# 加载环境变量
env_path = find_dotenv()
load_dotenv(env_path, override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
model_id = os.getenv("MODEL_ID", "claude-3-5-sonnet-20241022")

print("🔧 DeepSeek 流式输出测试")
print(f"Base URL: {base_url}")
print(f"Model: {model_id}")
print("="*60)

client = Anthropic(api_key=api_key, base_url=base_url)

# 测试 1: 简单对话（无工具）
print("\n【测试 1】简单对话（检查是否有文本输出）")
print("-"*60)

try:
    with client.messages.stream(
        model=model_id,
        max_tokens=500,
        messages=[{"role": "user", "content": "用一句话介绍你自己"}]
    ) as stream:
        event_count = 0
        text_received = False

        for event in stream:
            event_count += 1
            print(f"事件 {event_count}: type={event.type}")

            if event.type == "text_block":
                if event.delta.text:
                    text_received = True
                    print(f"  📝 文本: {event.delta.text}", end="", flush=True)

        print(f"\n\n统计:")
        print(f"  - 总事件数: {event_count}")
        print(f"  - 是否收到文本: {'✅ 是' if text_received else '❌ 否'}")

except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 2: 带工具的对话
print("\n\n【测试 2】带工具的对话（检查工具调用是否触发）")
print("-"*60)

tools = [
    {
        "name": "test_tool",
        "description": "测试工具",
        "input_schema": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }
    }
]

try:
    with client.messages.stream(
        model=model_id,
        max_tokens=500,
        messages=[{"role": "user", "content": "请调用 test_tool 工具，参数是 'hello'，然后用中文告诉我调用完成了"}],
        tools=tools
    ) as stream:
        event_count = 0
        text_received = False
        tool_call_detected = False
        tool_param_buffer = ""

        for event in stream:
            event_count += 1

            if event.type == "text_block" and event.delta.text:
                text_received = True
                print(f"📝 文本: {event.delta.text}", end="", flush=True)

            elif event.type == "content_block_start":
                if event.content_block.type == "tool_use":
                    tool_call_detected = True
                    print(f"\n🔧 工具调用开始: {event.content_block.name}")

            elif event.type == "content_block_delta":
                if event.delta.type == "input_json_delta":
                    tool_param_buffer += event.delta.partial_json

            elif event.type == "content_block_stop":
                if tool_param_buffer:
                    print(f"   参数: {tool_param_buffer}")
                    tool_param_buffer = ""

        print(f"\n\n统计:")
        print(f"  - 总事件数: {event_count}")
        print(f"  - 是否收到文本: {'✅ 是' if text_received else '❌ 否'}")
        print(f"  - 是否检测到工具调用: {'✅ 是' if tool_call_detected else '❌ 否'}")

except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "="*60)
print("测试完成")
