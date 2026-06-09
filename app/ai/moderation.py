"""AI-powered content moderation engine.

Scans user-generated content (post text, chat messages) for policy
violations and returns structured moderation decisions with a confidence
score that drives automated handling.

Exposes a single public function:
    moderate(content, context) → ModerationResult
"""

from pydantic import BaseModel, Field

from app.ai.agent import create_agent

# ===== Structured Output Schema =====


class ModerationResult(BaseModel):
    """Structured moderation verdict for a piece of content."""

    is_violation: bool = Field(..., description="Whether the content violates policy")
    violation_type: str = Field(
        default="none",
        description="Violation category: none, spam, harassment, porn, violence, "
        "privacy_leak, phishing, or other",
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="How confident the model is in this verdict (0-1)",
    )
    reason: str = Field(
        default="",
        description="Brief explanation of the verdict in Chinese",
    )
    suggestion: str = Field(
        default="pass",
        description="Recommended action: pass, flag, or block",
    )


# ===== Moderation System Prompt =====

MODERATION_SYSTEM_PROMPT = """你是校园内容安全审核助手。你的任务是对用户发布的内容进行合规检查。

## 违规类型
- **spam**：广告、垃圾信息、重复刷屏
- **harassment**：人身攻击、辱骂、霸凌、骚扰言论
- **porn**：色情低俗内容、性暗示、裸露描述
- **violence**：暴力威胁、恐怖主义、自残引导
- **privacy_leak**：泄露真实姓名、电话号码、身份证号、住址等个人隐私
- **phishing**：钓鱼链接、虚假诱导信息
- **other**：其他不适合校园平台的违规内容

## 判断标准
- 如果内容属于正常的社交、学习、生活交流，判定为 is_violation=false, confidence>=0.9
- 如果内容明确包含上述违规类型，判定为 is_violation=true, confidence>=0.85
- 如果内容处于灰色地带（如轻微调侃但不算攻击），判定为 is_violation=false, confidence=0.5-0.7

## 处理建议(suggestion)
- **pass**：is_violation=false 且 confidence>=0.7，直接放行
- **flag**：confidence 在 0.3-0.7 之间，或内容处于灰色地带，标记为需人工复审
- **block**：is_violation=true 且 confidence>=0.7，自动屏蔽

## 注意事项
- 校园场景下，对学习相关内容的审核应宽松（如讨论考试题不算违规）
- 对真正的攻击和骚扰零容忍
- 中文语境下的网络用语要结合上下文判断，不要误杀
- reason 和 suggestion 字段即使不违规也要填写
"""

# ===== Public API =====


async def moderate(
    content: str,
    context: str = "",
) -> ModerationResult:
    """Scan content for policy violations.

    Args:
        content: The text content to review (post body, message text, etc.).
        context: Optional context hint (e.g. "post title", "chat message")
            to help the model interpret the content.

    Returns:
        A ModerationResult with violation status, confidence, and
        recommended action.

    Raises:
        pydantic_ai.ModelHTTPError: If the LLM API request fails.
        pydantic_ai.UnexpectedModelBehavior: If the model output cannot
            be parsed into the expected structure.
    """
    agent = create_agent(
        output_type=ModerationResult,
        system_prompt=MODERATION_SYSTEM_PROMPT,
    )

    prompt_parts = ["请审核以下内容：", f"```\n{content}\n```"]
    if context:
        prompt_parts.insert(1, f"上下文类型：{context}\n")

    prompt = "\n".join(prompt_parts)
    result = await agent.run(prompt)
    return result.data
