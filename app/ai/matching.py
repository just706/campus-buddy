"""AI-powered buddy matching engine.

Analyzes user profiles and preferences to compute match scores and
generate human-readable recommendation reasons using LLM.

Exposes a single public function:
    recommend(current_user, candidates) → list[RecommendationItem]
"""

from pydantic import BaseModel, Field

from app.ai.agent import create_agent
from app.models.user import User

# ===== Structured Output Schema =====


class MatchResult(BaseModel):
    """A single AI-scored candidate with explanation."""

    candidate_user_id: int = Field(..., description="The candidate user's database ID")
    match_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="AI match score: 0 = no fit, 100 = perfect match",
    )
    reason: str = Field(
        ..., description="Natural-language explanation of why this is a good match"
    )


class MatchResultList(BaseModel):
    """Wrapper for a list of match results — required for structured output."""

    matches: list[MatchResult] = Field(..., description="List of match results")


# ===== Matching System Prompt =====

MATCHING_SYSTEM_PROMPT = """你是校园搭子匹配助手。你的任务是根据用户画像和需求，评估候选搭子的匹配度。

## 匹配维度
1. **兴趣重合度**（最重要）：比较双方的兴趣标签（tags），标签重合越多分数越高
2. **学校匹配度**：同校优先，同城次之
3. **专业/年级适配**：学习搭子优先同专业或同年级；运动/约饭不受此限制
4. **活跃度**：个人简介（bio）填写完整度暗示参与积极性
5. **综合素质**：根据所有可用信息综合判断

## 评分标准（0-100）
- 90-100：兴趣高度重合+同校，几乎完美匹配
- 70-89：多个兴趣重合或同校，比较合适
- 50-69：有部分交集，可以尝试
- 30-49：交集较少，但不排除可能性
- 0-29：几乎无交集或不适合

## 输出要求
- 为每个候选人输出 match_score（0-100）和一段 15-40 字的中文推荐理由
- 理由要具体，提到共同兴趣或匹配点，不要泛泛而谈"你们很合适"
- 按 match_score 从高到低排序输出

## 注意事项
- 如果候选人没有填写 tags 或 bio，不要打分为 0，而是给予 30-50 的基准分
- 不要泄露任何个人隐私信息（全名、电话等）
"""

# ===== Public API =====


def _build_candidates_text(
    current_user: User, candidates: list[User]
) -> str:
    """Build the user-facing prompt describing the current user and candidates.

    Args:
        current_user: The user requesting recommendations.
        candidates: The list of potential buddy matches.

    Returns:
        A formatted string ready to pass to the LLM.
    """
    def describe(u: User) -> str:
        tags = ", ".join(u.tags) if u.tags else "未填写"
        bio = u.bio or "未填写"
        nickname = u.nickname or u.username
        return (
            f"- ID={u.id}, 昵称={nickname}, 学校={u.university}, "
            f"专业={u.major or '未知'}, 年级={u.grade or '未知'}, "
            f"性别={u.gender or '未知'}, 兴趣标签=[{tags}], 简介={bio}"
        )

    me = describe(current_user)
    them = "\n".join(describe(c) for c in candidates)
    return (
        f"### 当前用户画像\n{me}\n\n"
        f"### 候选搭子列表（共 {len(candidates)} 人）\n{them}"
    )


async def recommend(
    current_user: User,
    candidates: list[User],
) -> list[MatchResult]:
    """Generate AI match recommendations for the current user.

    Args:
        current_user: The user requesting recommendations.
        candidates: The pool of candidate users to evaluate. Must not
            include the current user or users who are already matched.

    Returns:
        A list of MatchResult objects sorted by score descending.

    Raises:
        pydantic_ai.ModelHTTPError: If the LLM API request fails.
        pydantic_ai.UnexpectedModelBehavior: If the model output cannot
            be parsed into the expected structure.
    """
    if not candidates:
        return []

    agent = create_agent(
        output_type=MatchResultList,
        system_prompt=MATCHING_SYSTEM_PROMPT,
    )
    prompt = _build_candidates_text(current_user, candidates)
    result = await agent.run(prompt)
    # Sort by score descending
    matches = sorted(result.data.matches, key=lambda m: m.match_score, reverse=True)
    return matches
