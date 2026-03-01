"""
演示 anthropic SDK 如何区分流式输出中的工具调用和文本输出

关键点：anthropic 的流式响应有明确的事件类型，
可以准确判断当前是在调用工具还是输出文本
"""

from anthropic import Anthropic
import json

# 初始化客户端（需要设置 ANTHROPIC_API_KEY 环境变量）
client = Anthropic()

# 定义一个示例工具
tools = [
    {
        "name": "execute_sql",
        "description": "执行 SQL 查询并返回结果",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要执行的 SQL 查询语句"
                }
            },
            "required": ["query"]
        }
    }
]

def demo_streaming_with_tools():
    """
    演示如何在流式输出中区分工具调用和文本输出
    """

    user_query = "请帮我查询销售额最高的前5个产品"

    print("=" * 60)
    print("开始流式输出...\n")

    # 启用流式输出
    with client.messages.stream(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_query}],
        tools=tools
    ) as stream:

        current_tool_use = None
        tool_use_buffer = ""

        for event in stream:
            # 关键：通过 event.type 判断当前事件的类型
            event_type = event.type

            if event_type == "text_block":
                # ========== 文本输出（Final Answer 或思考过程） ==========
                print(f"[文本输出] {event.delta.text or ''}", end="", flush=True)

            elif event_type == "content_block_start":
                # ========== 工具调用开始 ==========
                if event.content_block.type == "tool_use":
                    print(f"\n[工具调用开始] 工具名: {event.content_block.name}")
                    print(f"[工具调用开始] ID: {event.content_block.id}")
                    current_tool_use = {
                        "id": event.content_block.id,
                        "name": event.content_block.name,
                        "input": {}
                    }

            elif event_type == "content_block_delta":
                # ========== 工具调用参数增量 ==========
                if event.delta.type == "input_json_delta":
                    # 累积工具调用的参数
                    tool_use_buffer += event.delta.partial_json
                    print(f"[工具参数] 收到数据片段: {event.delta.partial_json}")

            elif event_type == "content_block_stop":
                # ========== 工具调用结束 ==========
                if current_tool_use:
                    try:
                        # 解析完整的工具调用参数
                        current_tool_use["input"] = json.loads(tool_use_buffer)
                        print(f"\n[工具调用完成] 完整参数: {json.dumps(current_tool_use, ensure_ascii=False)}")

                        # 这里可以执行工具调用
                        # result = execute_tool(current_tool_use)

                        # 清空缓冲区
                        tool_use_buffer = ""
                        current_tool_use = None
                    except json.JSONDecodeError as e:
                        print(f"[错误] JSON 解析失败: {e}")

            elif event_type == "message_stop":
                print("\n\n[消息完成] 整个响应结束")

            elif event_type == "message_start":
                print("[消息开始] 收到响应")

            elif event_type == "message_delta":
                # 可以在这里获取 token 使用情况
                if hasattr(event.delta, 'usage') and event.delta.usage:
                    print(f"\n[Token使用] {event.delta.usage}")

            else:
                print(f"[其他事件] {event_type}")

if __name__ == "__main__":
    # 这个示例需要设置 ANTHROPIC_API_KEY 环境变量
    # export ANTHROPIC_API_KEY=your-key-here
    try:
        demo_streaming_with_tools()
    except Exception as e:
        print(f"\n运行失败（可能需要设置 API Key）: {e}")
        print("\n提示：export ANTHROPIC_API_KEY=your-key-here")
