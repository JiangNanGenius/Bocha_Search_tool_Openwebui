"""
title: 🔍 Bocha综合搜索工具集 - 中文网页搜索、英文网页搜索、AI智能搜索
author: JiangNanGenius
Github: https://github.com/JiangNanGenius
version: 2.1.1
license: MIT
"""

import os
import requests
import json
from pydantic import BaseModel, Field
import asyncio
from typing import Callable, Any
from urllib.parse import urlparse
import unicodedata
import re
from bs4 import BeautifulSoup


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )


class Tools:
    class Valves(BaseModel):
        BOCHA_API_KEY: str = Field(
            default="YOUR_BOCHA_API_KEY",
            description="🔑 Bocha AI API密钥 (用于中文搜索和AI搜索)",
        )
        LANGSEARCH_API_KEY: str = Field(
            default="YOUR_LANGSEARCH_API_KEY",
            description="🗝️ LangSearch API密钥 (用于英文搜索)",
        )
        CHINESE_WEB_SEARCH_ENDPOINT: str = Field(
            default="https://api.bochaai.com/v1/web-search",
            description="🇨🇳 中文网页搜索API端点",
        )
        ENGLISH_WEB_SEARCH_ENDPOINT: str = Field(
            default="https://api.langsearch.com/v1/web-search",
            description="🌐 英文网页搜索API端点（LangSearch）",
        )
        AI_SEARCH_ENDPOINT: str = Field(
            default="https://api.bochaai.com/v1/ai-search",
            description="🤖 AI智能搜索API端点",
        )
        CHINESE_SEARCH_COUNT: int = Field(
            default=10,
            description="🇨🇳 中文搜索结果数量 (1-10)",
        )
        ENGLISH_SEARCH_COUNT: int = Field(
            default=10,
            description="🌐 英文搜索结果数量 (1-10)",
        )
        AI_SEARCH_COUNT: int = Field(
            default=10,
            description="🤖 AI搜索结果数量 (1-50)",
        )
        CITATION_LINKS: bool = Field(
            default=True,
            description="🔗 是否发送引用链接和元数据",
        )
        FRESHNESS: str = Field(
            default="noLimit",
            description="⏰ 搜索时间范围 (noLimit, oneDay, oneWeek, oneMonth, oneYear)",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def search_chinese_web(
        self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        🇨🇳 中文网页搜索工具
        专门用于搜索中文网页内容，使用Bocha中文搜索端点，提供准确的中文搜索结果和摘要
        :param query: 中文搜索关键词
        :return: 返回中文网页搜索结果
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(f"🔍 正在进行中文网页搜索: {query}")

        headers = {
            "Authorization": f"Bearer {self.valves.BOCHA_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "freshness": self.valves.FRESHNESS,
            "summary": True,  # 显示摘要
            "count": self.valves.CHINESE_SEARCH_COUNT,
        }

        try:
            await emitter.emit("⏳ 正在连接中文搜索服务器...")
            resp = requests.post(
                self.valves.CHINESE_WEB_SEARCH_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            source_context_list = []
            counter = 1

            if "data" in data and "webPages" in data["data"]:
                web_pages = data["data"]["webPages"]
                if "value" in web_pages and isinstance(web_pages["value"], list):
                    await emitter.emit(
                        f"📄 正在处理 {len(web_pages['value'])} 个中文网页结果..."
                    )
                    for item in web_pages["value"]:
                        url = item.get("url", "")
                        snippet = item.get("snippet", "")
                        summary = item.get("summary", "")
                        name = item.get("name", "")
                        site_name = item.get("siteName", "")
                        date_published = item.get("datePublished", "")

                        source_context_list.append(
                            {
                                "content": summary or snippet,
                                "title": f"📄 {name}",
                                "url": url,
                                "site_name": f"🌐 {site_name}" if site_name else "",
                                "date_published": (
                                    f"📅 {date_published}" if date_published else ""
                                ),
                                "source_type": "🇨🇳 中文网页",
                            }
                        )

                        if __event_emitter__ and self.valves.CITATION_LINKS:
                            await __event_emitter__(
                                {
                                    "type": "citation",
                                    "data": {
                                        "document": [summary or snippet],
                                        "metadata": [
                                            {
                                                "source": url,
                                                "title": f"📄 {name}",
                                            }
                                        ],
                                        "source": {
                                            "name": f"🇨🇳 {name}",
                                            "url": url,
                                            "type": "webpage",
                                        },
                                    },
                                }
                            )
                        counter += 1

            await emitter.emit(
                status="complete",
                description=f"✅ 中文网页搜索完成，找到 {len(source_context_list)} 个结果",
                done=True,
            )
            return json.dumps(source_context_list, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            error_details = {
                "error": str(e),
                "type": "❌ 中文网页搜索错误",
                "endpoint": self.valves.CHINESE_WEB_SEARCH_ENDPOINT,
                "api_key_used": "BOCHA_API_KEY",
                "payload": payload,
            }
            await emitter.emit(
                status="error",
                description=f"❌ 中文网页搜索出错: {str(e)}",
                done=True,
            )
            return json.dumps(error_details, ensure_ascii=False)

    async def search_english_web(
        self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        🌐 英文网页搜索工具
        专门用于搜索英文网页内容，使用LangSearch英文搜索端点，提供准确的英文搜索结果和摘要
        :param query: 英文搜索关键词
        :return: 返回英文网页搜索结果
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(f"🔍 正在进行英文网页搜索: {query}")

        headers = {
            "Authorization": f"Bearer {self.valves.LANGSEARCH_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "freshness": self.valves.FRESHNESS,
            "summary": True,  # 显示摘要
            "count": self.valves.ENGLISH_SEARCH_COUNT,
        }

        try:
            await emitter.emit("⏳ 正在连接英文搜索服务器...")
            resp = requests.post(
                self.valves.ENGLISH_WEB_SEARCH_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            source_context_list = []
            counter = 1

            if "data" in data and "webPages" in data["data"]:
                web_pages = data["data"]["webPages"]
                if "value" in web_pages and isinstance(web_pages["value"], list):
                    await emitter.emit(
                        f"📄 正在处理 {len(web_pages['value'])} 个英文网页结果..."
                    )
                    for item in web_pages["value"]:
                        url = item.get("url", "")
                        snippet = item.get("snippet", "")
                        summary = item.get("summary", "")
                        name = item.get("name", "")
                        site_name = item.get("siteName", "")
                        date_published = item.get("datePublished", "")

                        source_context_list.append(
                            {
                                "content": summary or snippet,
                                "title": f"📄 {name}",
                                "url": url,
                                "site_name": f"🌐 {site_name}" if site_name else "",
                                "date_published": (
                                    f"📅 {date_published}" if date_published else ""
                                ),
                                "source_type": "🌐 英文网页",
                            }
                        )

                        if __event_emitter__ and self.valves.CITATION_LINKS:
                            await __event_emitter__(
                                {
                                    "type": "citation",
                                    "data": {
                                        "document": [summary or snippet],
                                        "metadata": [
                                            {
                                                "source": url,
                                                "title": f"📄 {name}",
                                            }
                                        ],
                                        "source": {
                                            "name": f"🌐 {name}",
                                            "url": url,
                                            "type": "webpage",
                                        },
                                    },
                                }
                            )
                        counter += 1

            await emitter.emit(
                status="complete",
                description=f"✅ 英文网页搜索完成，找到 {len(source_context_list)} 个结果",
                done=True,
            )
            return json.dumps(source_context_list, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            error_details = {
                "error": str(e),
                "type": "❌ 英文网页搜索错误",
                "endpoint": self.valves.ENGLISH_WEB_SEARCH_ENDPOINT,
                "api_key_used": "LANGSEARCH_API_KEY",
                "payload": payload,
            }
            await emitter.emit(
                status="error",
                description=f"❌ 英文网页搜索出错: {str(e)}",
                done=True,
            )
            return json.dumps(error_details, ensure_ascii=False)

    async def search_ai_intelligent(
        self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        🤖 AI智能搜索工具
        使用AI技术提供智能搜索结果，包含AI生成的答案、总结和追问问题
        支持多模态搜索结果（网页、图片、模态卡等）
        :param query: 搜索查询关键词
        :return: 返回AI智能搜索结果，包含AI生成的答案
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit(f"🤖 正在进行AI智能搜索: {query}")

        headers = {
            "Authorization": f"Bearer {self.valves.BOCHA_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "freshness": self.valves.FRESHNESS,
            "answer": True,  # 启用AI生成答案
            "stream": False,  # 非流式响应
            "count": self.valves.AI_SEARCH_COUNT,
        }

        try:
            await emitter.emit("⏳ 正在连接AI智能搜索服务器...")
            resp = requests.post(
                self.valves.AI_SEARCH_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            source_context_list = []
            ai_answers = []
            follow_up_questions = []
            counter = 1

            await emitter.emit("🧠 AI正在分析搜索结果...")

            if "messages" in data:
                for msg in data["messages"]:
                    msg_role = msg.get("role", "")
                    msg_type = msg.get("type", "")
                    content_type = msg.get("content_type", "")
                    content = msg.get("content", "")

                    # 处理网页搜索结果
                    if (
                        msg_role == "assistant"
                        and msg_type == "source"
                        and content_type == "webpage"
                    ):
                        try:
                            content_obj = json.loads(content)
                            if "value" in content_obj and isinstance(
                                content_obj["value"], list
                            ):
                                await emitter.emit(
                                    f"📄 正在处理 {len(content_obj['value'])} 个AI搜索结果..."
                                )
                                for item in content_obj["value"]:
                                    url = item.get("url", "")
                                    snippet = item.get("snippet", "")
                                    summary = item.get("summary", "")
                                    name = item.get("name", "")
                                    site_name = item.get("siteName", "")
                                    date_published = item.get("datePublished", "")

                                    source_context_list.append(
                                        {
                                            "content": summary or snippet,
                                            "title": f"📄 {name}",
                                            "url": url,
                                            "site_name": (
                                                f"🌐 {site_name}" if site_name else ""
                                            ),
                                            "date_published": (
                                                f"📅 {date_published}"
                                                if date_published
                                                else ""
                                            ),
                                            "source_type": "🤖 AI智能搜索",
                                        }
                                    )

                                    if __event_emitter__ and self.valves.CITATION_LINKS:
                                        await __event_emitter__(
                                            {
                                                "type": "citation",
                                                "data": {
                                                    "document": [summary or snippet],
                                                    "metadata": [
                                                        {
                                                            "source": url,
                                                            "title": f"📄 {name}",
                                                        }
                                                    ],
                                                    "source": {
                                                        "name": f"🤖 {name}",
                                                        "url": url,
                                                        "type": "webpage",
                                                    },
                                                },
                                            }
                                        )
                                    counter += 1
                        except json.JSONDecodeError:
                            pass

                    # 处理AI生成的答案
                    elif (
                        msg_role == "assistant"
                        and msg_type == "answer"
                        and content_type == "text"
                    ):
                        ai_answers.append(f"🤖 {content}")
                        await emitter.emit(f"✨ AI生成了第 {len(ai_answers)} 个回答...")

                    # 处理追问问题
                    elif (
                        msg_role == "assistant"
                        and msg_type == "follow_up"
                        and content_type == "text"
                    ):
                        follow_up_questions.append(f"💭 {content}")
                        await emitter.emit(
                            f"💡 AI建议了第 {len(follow_up_questions)} 个追问问题..."
                        )

            # 组合结果
            result = {
                "search_results": source_context_list,
                "ai_answers": ai_answers,
                "follow_up_questions": follow_up_questions,
                "summary": {
                    "total_results": len(source_context_list),
                    "ai_answers_count": len(ai_answers),
                    "follow_up_count": len(follow_up_questions),
                    "search_type": "🤖 AI智能搜索",
                },
            }

            await emitter.emit(
                status="complete",
                description=f"🎉 AI智能搜索完成！找到 {len(source_context_list)} 个结果，生成 {len(ai_answers)} 个AI答案，{len(follow_up_questions)} 个追问建议",
                done=True,
            )
            return json.dumps(result, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            error_details = {
                "error": str(e),
                "type": "❌ AI智能搜索错误",
                "endpoint": self.valves.AI_SEARCH_ENDPOINT,
                "api_key_used": "BOCHA_API_KEY",
                "payload": payload,
            }
            await emitter.emit(
                status="error",
                description=f"❌ AI智能搜索出错: {str(e)}",
                done=True,
            )
            return json.dumps(error_details, ensure_ascii=False)
