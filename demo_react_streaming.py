"""
ReAct 循环 + 流式输出 的完整示例
演示如何在一个循环中处理工具调用和流式的 Final Answer
"""

from anthropic import Anthropic
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv, find_dotenv

# 加载 .env 文件，并打印路径
env_path = find_dotenv()
print(f"📁 加载 .env 文件: {env_path}")
load_dotenv(env_path, override=True)  # 使用 override=True 确保覆盖系统环境变量

class Text2SQLReActAgent:
    """基于 ReAct 的 Text2SQL Agent，支持流式输出"""

    def __init__(self, api_key: Optional[str] = None):
        # 从环境变量读取配置
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        base_url = os.getenv("ANTHROPIC_BASE_URL")
        self.model_id = os.getenv("MODEL_ID", "claude-3-5-sonnet-20241022")

        # 初始化客户端（支持自定义 base_url 用于兼容其他 API）
        if base_url:
            self.client = Anthropic(api_key=api_key, base_url=base_url)
        else:
            self.client = Anthropic(api_key=api_key)

        self.max_iterations = 10  # 增加迭代次数
        self.conversation_history = []

        # 添加系统提示，要求模型输出思考过程
        self.system_prompt = """你是一个专业的数据库查询助手。

重要要求：
1. 在调用工具之前，先简要说明你的思考过程
2. 获得查询结果后，必须用清晰的中文总结答案
3. 不要只调用工具而不输出任何文字

按照以下步骤工作：
1. 思考并说明需要查询什么
2. 调用工具获取数据库信息
3. 执行 SQL 查询
4. 用中文总结结果"""

        # 定义可用工具
        self.tools = [
            {
                "name": "get_tables",
                "description": "获取数据库中所有表的列表",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_table_schema",
                "description": "获取指定表的结构（列名、数据类型）",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "要查询的表名"
                        }
                    },
                    "required": ["table_name"]
                }
            },
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

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """执行工具调用（这里是模拟的）"""

        if tool_name == "get_tables":
            # 模拟返回数据库表列表
            return json.dumps({
                "tables": ["users", "orders", "products", "order_items"]
            }, ensure_ascii=False)

        elif tool_name == "get_table_schema":
            table_name = tool_input.get("table_name")
            # 模拟返回表结构
            schemas = {
                "users": [{"column": "id", "type": "int"}, {"column": "name", "type": "varchar"}, {"column": "email", "type": "varchar"}],
                "orders": [{"column": "id", "type": "int"}, {"column": "user_id", "type": "int"}, {"column": "total_amount", "type": "decimal"}],
                "products": [{"column": "id", "type": "int"}, {"column": "name", "type": "varchar"}, {"column": "price", "type": "decimal"}],
            }
            return json.dumps(schemas.get(table_name, []), ensure_ascii=False)

        elif tool_name == "execute_sql":
            query = tool_input.get("query")
            # 模拟执行 SQL 并返回结果
            return json.dumps({
                "query": query,
                "results": [
                    {"product_name": "iPhone 15", "sales": 1500000},
                    {"product_name": "MacBook Pro", "sales": 1200000},
                    {"product_name": "AirPods", "sales": 800000},
                ]
            }, ensure_ascii=False)

        return f"未知工具: {tool_name}"

    def process_streaming_response(self, user_message: str):
        """
        处理流式响应，自动识别工具调用和最终答案
        """

        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        for iteration in range(self.max_iterations):
            print(f"\n{'='*60}")
            print(f"第 {iteration + 1} 轮迭代")
            print(f"{'='*60}\n")

            tool_calls = []
            text_output = []
            current_tool = None
            tool_input_buffer = ""
            event_types_seen = set()  # 记录收到的事件类型
            debug_events = []  # 记录调试信息

            # 发起请求并流式读取响应
            with self.client.messages.stream(
                model=self.model_id,
                max_tokens=2048,  # 增加 token 限制
                system=self.system_prompt,  # 添加系统提示
                messages=self.conversation_history,
                tools=self.tools
            ) as stream:

                for event in stream:
                    event_types_seen.add(event.type)

                    # ========== 关键判断逻辑 ==========

                    # 同时支持 Anthropic 原生和 DeepSeek 兼容格式
                    if event.type == "text_block":
                        # Anthropic 原生格式
                        if event.delta.text:
                            text_output.append(event.delta.text)
                            # 实时输出给用户
                            print(event.delta.text, end="", flush=True)

                    elif event.type == "text":
                        # DeepSeek 兼容格式 - 文本直接在 event.text
                        if hasattr(event, 'text') and event.text:
                            text_output.append(event.text)
                            # 实时输出给用户
                            print(event.text, end="", flush=True)

                    elif event.type == "content_block_start":
                        # 工具调用开始
                        if event.content_block.type == "tool_use":
                            print(f"\n\n🔧 [检测到工具调用] {event.content_block.name}")
                            current_tool = {
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                                "input": {}
                            }

                    elif event.type == "content_block_delta":
                        # 工具调用参数增量
                        if event.delta.type == "input_json_delta":
                            tool_input_buffer += event.delta.partial_json

                    elif event.type == "content_block_stop":
                        # 工具调用结束，解析参数
                        if current_tool:
                            try:
                                current_tool["input"] = json.loads(tool_input_buffer)
                                tool_calls.append(current_tool)
                                print(f"   参数: {json.dumps(current_tool['input'], ensure_ascii=False)}\n")
                            except json.JSONDecodeError:
                                print(f"   ⚠️  参数解析失败")

                            # 重置
                            current_tool = None
                            tool_input_buffer = ""

            # ========== 响应处理完毕，判断下一步 ==========

            print(f"\n[调试] 本轮迭代结束:")
            print(f"  - 收到的事件类型: {event_types_seen}")
            print(f"  - 文本输出: {len(text_output)} 个片段")
            print(f"  - 工具调用: {len(tool_calls)} 个")

            # 如果有 text 相关事件但没收到文本，打印调试信息
            if any("text" in t.lower() for t in event_types_seen) and len(text_output) == 0:
                print(f"\n[详细调试] 检测到 text 事件但未捕获到文本:")
                for i, debug in enumerate(debug_events):
                    print(f"  事件 {i+1}:")
                    print(f"    type: {debug['type']}")
                    print(f"    has_delta: {debug['has_delta']}")
                    print(f"    delta_type: {debug['delta_type']}")
                    if debug['has_delta']:
                        print(f"    delta 实际值: {debug.get('delta_value', 'N/A')}")

            # 保存助手的响应到历史
            assistant_message = {"role": "assistant", "content": []}

            if text_output:
                assistant_message["content"].append({
                    "type": "text",
                    "text": "".join(text_output)
                })
                print(f"  - 文本内容长度: {len(''.join(text_output))}")

            if tool_calls:
                # 有工具调用 - 执行并继续循环
                for tool_call in tool_calls:
                    # 添加工具调用到助手消息
                    assistant_message["content"].append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": tool_call["name"],
                        "input": tool_call["input"]
                    })

                    # 执行工具
                    print(f"⚡ [执行工具] {tool_call['name']}")
                    result = self.execute_tool(tool_call["name"], tool_call["input"])
                    print(f"📊 [工具结果] {result}\n")

                    # 添加工具结果到历史
                    self.conversation_history.append(assistant_message)
                    self.conversation_history.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_call["id"],
                                "content": result
                            }
                        ]
                    })

                # 继续下一轮迭代
                continue

            else:
                # 没有工具调用 - 这是 Final Answer，结束
                self.conversation_history.append(assistant_message)
                print(f"\n\n{'='*60}")
                print("✅ [完成] 获得最终答案，ReAct 循环结束")
                print(f"{'='*60}\n")
                break

def main():
    """主函数"""
    # 打印配置信息
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model_id = os.getenv("MODEL_ID", "claude-3-5-sonnet-20241022")

    print("🔧 配置信息：")
    print(f"   API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"   Base URL: {base_url}")
    print(f"   Model ID: {model_id}")
    print("="*60)

    agent = Text2SQLReActAgent()

    print("\n🤖 Text2SQL ReAct Agent（支持流式输出）")
    print("="*60)

    user_query = "请查询销售额最高的前3个产品及其销售额，最后用简洁的中文总结结果"

    print(f"\n👤 用户查询: {user_query}\n")

    agent.process_streaming_response(user_query)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 运行失败: {e}")
        print("\n💡 提示：请确保已设置 ANTHROPIC_API_KEY 环境变量")
