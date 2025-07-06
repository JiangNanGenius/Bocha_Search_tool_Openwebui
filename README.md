
# 🔍 Bocha综合搜索工具集

Bocha综合搜索工具集是一个功能强大的Python库，集成了中文网页搜索、英文网页搜索和AI智能搜索能力，帮助开发者轻松获取多语言、多模态的网络信息。

## ✨ 主要功能

- **🇨🇳 中文网页搜索**：使用Bocha AI API端点，提供准确的中文网页搜索结果和摘要
- **🌐 英文网页搜索**：集成LangSearch API，专注于英文网页内容的搜索与提取
- **🤖 AI智能搜索**：利用AI技术生成智能答案、总结和追问问题，支持多模态搜索结果

## 📋 安装指南

```bash
pip install requests pydantic beautifulsoup4
```

## 🔧 使用方法

### 1. 初始化工具

```python
from bocha_search import Tools

# 创建搜索工具实例
search_tools = Tools()
```

### 2. 配置API密钥和参数

```python
# 配置API密钥（必需）
search_tools.valves.BOCHA_API_KEY = "你的Bocha API密钥"
search_tools.valves.LANGSEARCH_API_KEY = "你的LangSearch API密钥"

# 可选配置
search_tools.valves.CHINESE_SEARCH_COUNT = 10  # 中文搜索结果数量(1-10)
search_tools.valves.ENGLISH_SEARCH_COUNT = 10  # 英文搜索结果数量(1-10)
search_tools.valves.AI_SEARCH_COUNT = 20       # AI搜索结果数量(1-50)
search_tools.valves.FRESHNESS = "oneMonth"     # 搜索时间范围(noLimit, oneDay, oneWeek, oneMonth, oneYear)
search_tools.valves.CITATION_LINKS = True      # 是否发送引用链接和元数据
```

### 3. 执行搜索

#### 中文网页搜索

```python
import asyncio

async def chinese_search_demo():
    query = "人工智能最新发展趋势"
    
    # 定义事件处理函数（可选）
    async def event_handler(event):
        if event["type"] == "status":
            print(f"状态更新: {event['data']['description']}")
        elif event["type"] == "citation":
            print(f"引用信息: {event['data']['source']['title']} - {event['data']['source']['url']}")
    
    # 执行搜索
    result = await search_tools.search_chinese_web(
        query=query,
        __event_emitter__=event_handler
    )
    
    # 处理结果
    results = json.loads(result)
    for item in results:
        print(f"\n标题: {item['title']}")
        print(f"来源: {item['site_name']} {item['date_published']}")
        print(f"摘要: {item['content'][:150]}...")
        print(f"链接: {item['url']}")

# 运行搜索
asyncio.run(chinese_search_demo())
```

#### 英文网页搜索

```python
async def english_search_demo():
    query = "latest advances in quantum computing"
    
    result = await search_tools.search_english_web(query=query)
    results = json.loads(result)
    
    # 处理英文搜索结果...

asyncio.run(english_search_demo())
```

#### AI智能搜索

```python
async def ai_search_demo():
    query = "比较中美在人工智能领域的发展策略"
    
    result = await search_tools.search_ai_intelligent(query=query)
    ai_results = json.loads(result)
    
    # 打印AI生成的答案
    print("AI智能回答:")
    for answer in ai_results["ai_answers"]:
        print(answer)
    
    # 打印相关搜索结果
    print("\n相关搜索结果:")
    for item in ai_results["search_results"][:3]:  # 只显示前3个结果
        print(f"\n标题: {item['title']}")
        print(f"摘要: {item['content'][:150]}...")
    
    # 打印追问问题
    print("\n追问建议:")
    for question in ai_results["follow_up_questions"]:
        print(question)

asyncio.run(ai_search_demo())
```

## 📊 返回结果格式

### 中文/英文网页搜索结果
```json
[
  {
    "content": "搜索结果摘要内容...",
    "title": "📄 网页标题",
    "url": "https://example.com/article",
    "site_name": "🌐 网站名称",
    "date_published": "📅 2023-11-15",
    "source_type": "🇨🇳 中文网页"
  },
  // ...更多结果
]
```

### AI智能搜索结果
```json
{
  "search_results": [...],  // 类似网页搜索结果的列表
  "ai_answers": [
    "🤖 AI生成的详细回答内容..."
  ],
  "follow_up_questions": [
    "💭 相关的追问问题1?",
    "💭 相关的追问问题2?"
  ],
  "summary": {
    "total_results": 10,
    "ai_answers_count": 1,
    "follow_up_count": 3,
    "search_type": "🤖 AI智能搜索"
  }
}
```

## ⚠️ 错误处理

当搜索过程中发生错误时，将返回包含错误信息的JSON字符串：

```json
{
  "error": "错误描述信息",
  "type": "❌ 中文网页搜索错误",
  "endpoint": "https://api.bochaai.com/v1/web-search",
  "api_key_used": "BOCHA_API_KEY",
  "payload": {...}
}
```

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交PR或Issue来帮助改进这个项目！

## 👨‍💻 作者信息

- **作者**: JiangNanGenius
- **GitHub**: [https://github.com/JiangNanGenius](https://github.com/JiangNanGenius)

---

**注意**: 使用本工具需要有效的Bocha API和LangSearch API密钥。请确保遵守各API提供商的使用条款和限制。
