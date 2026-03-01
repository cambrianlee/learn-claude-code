"""
对比 anthropic SDK 和直接 HTTP 请求的差异
"""
import os
from dotenv import load_dotenv, find_dotenv
import anthropic

load_dotenv(find_dotenv(), override=True)

api_key = os.getenv("ANTHROPIC_API_KEY")

print("="*70)
print("对比 SDK vs 直接 HTTP")
print("="*70)

# 检查 SDK 版本
print(f"\nAnthropic SDK 版本: {anthropic.__version__}")

# 查看 SDK 客户端的配置
client = anthropic.Anthropic(
    api_key=api_key,
    base_url="https://api.deepseek.com/anthropic"
)

print(f"\nSDK 客户端配置:")
print(f"  base_url: {client.base_url}")
print(f"  api_key: {client.api_key[:20]}...{client.api_key[-10:]}")

# 检查是否有默认 headers
print(f"\nSDK 默认 headers (如果可以访问):")
try:
    if hasattr(client, '_client'):
        print(f"  _client 存在")
        if hasattr(client._client, 'default_headers'):
            print(f"  default_headers: {client._client.default_headers}")
except Exception as e:
    print(f"  无法访问: {e}")

# 测试不同的 API Key 传递方式
print("\n\n" + "="*70)
print("测试不同的初始化方式")
print("="*70)

# 方式 1: 通过 api_key 参数
print("\n【方式 1】client = Anthropic(api_key=key, base_url=url)")
try:
    client1 = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://api.deepseek.com/anthropic"
    )
    response = client1.messages.create(
        model="deepseek-chat",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(f"✅ 成功: {response.content[0].text}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 方式 2: 通过环境变量
print("\n【方式 2】通过环境变量 ANTHROPIC_API_KEY")
try:
    # 先清除 base_url，使用默认
    client2 = anthropic.Anthropic(
        base_url="https://api.deepseek.com/anthropic"
    )
    response = client2.messages.create(
        model="deepseek-chat",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(f"✅ 成功: {response.content[0].text}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 方式 3: 检查 SDK 是否添加了额外的头部
print("\n【方式 3】检查 SDK 是否添加 anthropic-version 等头部")
try:
    import httpx

    # 手动构造请求，模拟 SDK
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    response = httpx.post(
        "https://api.deepseek.com/anthropic/v1/messages",
        headers=headers,
        json={
            "model": "deepseek-chat",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        },
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功: {response.json()['content'][0]['text']}")
    else:
        print(f"❌ 失败: {response.text}")

except Exception as e:
    print(f"❌ 错误: {e}")
