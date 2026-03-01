"""
测试 LangChain 的 OpenAI 兼容接口如何处理流式 + 工具调用
"""

import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 加载环境变量
env_path = find_dotenv()
load_dotenv(env_path, override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

print("="*80)
print("LangChain OpenAI 兼容接口 - 流式 + 工具调用测试")
print("="*80)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print()

# 定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    return f"{city}今天晴天，温度25°C"

tools = [get_weather]

# 初始化模型（使用 DeepSeek 的 OpenAI 兼容接口）
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com",
    temperature=0,
    streaming=True
)

# 绑定工具
llm_with_tools = llm.bind_tools(tools)

# ============================================================================
# 测试 1: 检查 ChatGenerationChunk 的结构
# ============================================================================
print("\n" + "="*80)
print("【测试 1】流式输出 - 检查每个 chunk 的结构")
print("="*80)

query = "北京今天天气怎么样？"
print(f"\n用户查询: {query}\n")
print("流式响应 chunks:")

tool_call_chunks = []
text_chunks = []

for chunk in llm_with_tools.stream([{"role": "user", "content": query}]):
    # chunk 本身就是 AIMessageChunk
    msg = chunk

    # 检查是否有文本内容
    if hasattr(msg, 'content') and msg.content:
        text_chunks.append(str(msg.content))
        print(f"[文本] {msg.content}")

    # 检查是否有工具调用
    if hasattr(msg, 'tool_call_chunks') and msg.tool_call_chunks:
        for tc in msg.tool_call_chunks:
            tool_call_chunks.append(tc)
            print(f"[工具片段] name={tc.get('name')}, args={tc.get('args')}, index={tc.get('index')}, id={tc.get('id')}")

print(f"\n\n统计:")
print(f"  文本 chunks: {len(text_chunks)}")
print(f"  工具调用 chunks: {len(tool_call_chunks)}")

# ============================================================================
# 测试 2: 检查工具调用是否自动累积
# ============================================================================
print("\n\n" + "="*80)
print("【测试 2】工具调用参数累积分析")
print("="*80)

# 按 index 分组工具调用片段
tool_calls_by_index = {}
for tc in tool_call_chunks:
    index = tc.get('index', 0)
    if index not in tool_calls_by_index:
        tool_calls_by_index[index] = {
            'id': tc.get('id'),
            'name': tc.get('name'),
            'args_chunks': []
        }
    if tc.get('args'):
        tool_calls_by_index[index]['args_chunks'].append(tc.get('args'))

print("\n按 index 分组的工具调用:")
for index, info in tool_calls_by_index.items():
    print(f"\n  工具调用 #{index}:")
    print(f"    ID: {info['id']}")
    print(f"    Name: {info['name']}")
    print(f"    参数片段数: {len(info['args_chunks'])}")
    print(f"    参数片段:")
    for i, arg_chunk in enumerate(info['args_chunks']):
        print(f"      [{i}] {repr(arg_chunk)}")

    # 尝试拼接参数
    full_args = ''.join(info['args_chunks'])
    print(f"    拼接后的参数: {full_args}")

# ============================================================================
# 测试 3: 检查是否有最终完整的工具调用
# ============================================================================
print("\n\n" + "="*80)
print("【测试 3】检查是否有完整的工具调用对象")
print("="*80)

query2 = "上海今天天气怎么样？"
print(f"\n用户查询: {query2}\n")

for chunk in llm_with_tools.stream([{"role": "user", "content": query2}]):
    msg = chunk

    # 检查是否有 tool_calls（完整对象）
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        print(f"[完整工具调用] {msg.tool_calls}")
    elif hasattr(msg, 'tool_call_chunks') and msg.tool_call_chunks:
        print(f"[工具片段] 有 {len(msg.tool_call_chunks)} 个片段")

# ============================================================================
# 测试 4: 使用 astream_events（LangChain 的更高级流式 API）
# ============================================================================
print("\n\n" + "="*80)
print("【测试 4】使用 astream_events - LangChain 的高级流式 API")
print("="*80)

query3 = "深圳今天天气怎么样？"
print(f"\n用户查询: {query3}\n")

async def test_astream_events():
    event_count = 0
    async for event in llm_with_tools.astream_events(
        [{"role": "user", "content": query3}],
        version="v1"
    ):
        event_count += 1

        # 只打印相关事件
        if event['event'] in ['on_chat_model_start', 'on_chat_model_stream', 'on_chat_model_end']:
            print(f"\n[{event['event']}]")
            if 'chunks' in event['data']:
                for chunk in event['data']['chunks']:
                    if hasattr(chunk, 'content') and chunk.content:
                        print(f"  文本: {chunk.content}")
                    if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                        print(f"  完整工具调用: {chunk.tool_calls}")
                    if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                        print(f"  工具片段: {len(chunk.tool_call_chunks)} 个")

        if event['event'] == 'on_tool_start':
            print(f"\n[工具开始执行] {event['data']['input']}")

        if event['event'] == 'on_tool_end':
            print(f"[工具执行完成] {event['data']['output']}")

        if event_count > 100:  # 限制输出
            break

import asyncio
asyncio.run(test_astream_events())

print("\n\n" + "="*80)
print("测试完成")
print("="*80)

# ============================================================================
# 总结
# ============================================================================
print("\n\n" + "="*80)
print("【总结】LangChain 是否自动处理工具调用累积？")
print("="*80)

print("""
从测试结果可以看到：

1. tool_call_chunks vs tool_calls:
   - tool_call_chunks: 流式过程中的片段（需要自己累积）
   - tool_calls: 完整的工具调用对象（如果有）

2. LangChain 的处理:
   ❌ 不会自动累积 tool_call_chunks 的参数
   ❌ 你需要自己按 index 累积 args 片段
   ❌ 需要自己判断工具调用何时结束

3. 相比 Anthropic SDK:
   Anthropic SDK 有明确的事件类型（content_block_start/stop）
   LangChain + OpenAI 接口仍然需要你处理 chunk 的累积

结论: 使用 LangChain + OpenAI 兼容接口，**仍然需要自己处理工具调用的累积**！
""")
