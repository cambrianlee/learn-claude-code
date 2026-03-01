"""
诊断 DeepSeek API Key 问题
"""
import os
import requests
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
env_path = find_dotenv()
load_dotenv(env_path, override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
model_id = os.getenv("MODEL_ID")

print("="*70)
print("DeepSeek API 诊断")
print("="*70)
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"Base URL: {base_url}")
print(f"Model: {model_id}")
print()

# 测试 1: OpenAI 兼容接口（使用 Authorization: Bearer）
print("\n【测试 1】OpenAI 兼容接口")
print("URL: https://api.deepseek.com/v1/chat/completions")
print("认证: Authorization: Bearer <key>")
print("-"*70)

try:
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        },
        timeout=10
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ OpenAI 兼容接口认证成功！")
        print(f"响应: {response.json()['choices'][0]['message']['content']}")
    else:
        print(f"❌ 失败")
        print(f"响应: {response.text}")

except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 2: Anthropic 兼容接口（使用 x-api-key）
print("\n\n【测试 2】Anthropic 兼容接口")
print("URL: https://api.deepseek.com/anthropic/v1/messages")
print("认证: x-api-key: <key>")
print("-"*70)

try:
    response = requests.post(
        "https://api.deepseek.com/anthropic/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "deepseek-chat",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        },
        timeout=10
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ Anthropic 兼容接口认证成功！")
        print(f"响应: {response.json()['content'][0]['text']}")
    else:
        print(f"❌ 失败")
        print(f"响应: {response.text}")

except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 3: 尝试使用 anthropic SDK
print("\n\n【测试 3】使用 anthropic SDK")
print("-"*70)

try:
    import anthropic

    client = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://api.deepseek.com/anthropic"
    )

    response = client.messages.create(
        model="deepseek-chat",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )

    print("✅ SDK 调用成功！")
    print(f"响应: {response.content[0].text}")

except Exception as e:
    print(f"❌ SDK 错误: {e}")

print("\n" + "="*70)
print("诊断完成")
print("="*70)
print("\n💡 结论：")
print("如果测试 1 和 2 都返回 401，说明这个 API Key 不是 DeepSeek 的")
print("你需要去 https://platform.deepseek.com 获取 DeepSeek 专用 API Key")
