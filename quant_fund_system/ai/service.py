"""AI 报告与分析服务。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request

from quant_fund_system.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


@dataclass
class AIService:
    """基于 OpenAI 兼容接口的简单文本生成服务。"""

    api_key: str = OPENAI_API_KEY
    base_url: str = OPENAI_BASE_URL
    model: str = OPENAI_MODEL

    def _chat(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            return (
                "AI 功能未启用：请先配置 OPENAI_API_KEY。"
                "当前返回基于规则模板，建议配置后再获取更智能的解释。"
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }
        req = request.Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return f"AI 请求失败：{exc}"

        choices = data.get("choices", [])
        if not choices:
            return "AI 返回为空，请检查 OPENAI_BASE_URL 与 OPENAI_MODEL 是否正确。"
        return str(choices[0].get("message", {}).get("content", "")).strip() or "AI 返回为空。"

    def generate_daily_report(self, payload: dict[str, Any]) -> str:
        system_prompt = (
            "你是A股量化基金投研助理。请用中文输出简洁专业日报，"
            "包含：策略结果、组合风险、回测表现、执行建议。"
        )
        user_prompt = f"请基于以下JSON生成日报：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        return self._chat(system_prompt, user_prompt)

    def analyze_factor(self, payload: dict[str, Any]) -> str:
        system_prompt = (
            "你是量化因子研究员。请分析IC与分层结果，输出：有效性结论、"
            "失效风险、下一步改进建议。"
        )
        user_prompt = f"请基于以下因子数据分析：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        return self._chat(system_prompt, user_prompt)

    def generate_risk_alert(self, payload: dict[str, Any]) -> str:
        system_prompt = (
            "你是量化风控官。请识别风险超限并给出具体行动建议，"
            "输出包括：风险等级、触发原因、建议动作。"
        )
        user_prompt = f"请基于以下风险数据生成告警：\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
        return self._chat(system_prompt, user_prompt)
