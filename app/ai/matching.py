"""AI-powered buddy matching engine.

Analyzes user profiles and preferences to compute match scores and
generate human-readable recommendation reasons using LLM.

When the LLM API key is not configured (placeholder value), falls back
to a rule-based engine that computes scores from tag overlap, school
matching, and profile completeness.

Exposes a single public function:
    recommend(current_user, candidates) → list[RecommendationItem]
"""

import logging

from pydantic import BaseModel, Field

from app.ai.agent import create_agent
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

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


# ===== Rule-Based Fallback Engine =====

# Placeholder API key patterns that indicate the LLM is not configured
_PLACEHOLDER_KEYS = {
    "",
    "sk-your-api-key-here",
    "your-api-key-here",
    "sk-your-openai-api-key",
    "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "sk-placeholder",
}


def _is_llm_configured() -> bool:
    """Check whether a real LLM API key has been configured.

    Returns:
        True if the API key looks like a real key (non-empty, non-placeholder).
    """
    key = settings.PDAI_API_KEY.strip()
    return key not in _PLACEHOLDER_KEYS and len(key) >= 20


def _rule_based_match(
    current_user: User, candidates: list[User]
) -> list[MatchResult]:
    """Compute match scores using a deterministic rule-based engine.

    Dimensions (same as the LLM prompt):
    1. Tag overlap — primary signal, each shared tag adds points
    2. School matching — same university > same city > other
    3. Profile completeness — bio filled, major filled, grade filled
    4. Same major/grade bonus for academic affinity

    The score formula is weighted and clamped to [0, 100].
    """
    my_tags = set(tag.strip().lower() for tag in (current_user.tags or []))
    my_uni = (current_user.university or "").strip()
    my_city = _extract_city(my_uni)

    results: list[MatchResult] = []
    for c in candidates:
        score = 30.0  # Base score for being an active user
        reasons: list[str] = []

        # --- Tag overlap (max +40) ---
        their_tags = set(tag.strip().lower() for tag in (c.tags or []))
        common = my_tags & their_tags
        if common and my_tags:
            overlap_ratio = len(common) / max(len(my_tags), 1)
            tag_score = min(40.0, round(overlap_ratio * 40.0, 1))
            score += tag_score
            tag_names = "、".join(sorted(common)[:4])
            reasons.append(f"你们有 {len(common)} 个共同兴趣标签（{tag_names}）")
        elif their_tags:
            reasons.append("你们的兴趣标签各不相同，但可以探索新领域")

        # --- School matching (max +25) ---
        their_uni = (c.university or "").strip()
        if my_uni and their_uni and my_uni == their_uni:
            score += 25
            reasons.append(f"同校 ({my_uni})")
        else:
            their_city = _extract_city(their_uni)
            if my_city and their_city and my_city == their_city:
                score += 15
                reasons.append(f"同城 ({my_city})")

        # --- Profile completeness (max +10) ---
        completeness = 0.0
        if c.bio and len(c.bio.strip()) >= 10:
            completeness += 4.0
        if c.major:
            completeness += 3.0
        if c.grade:
            completeness += 3.0
        score += completeness
        if completeness >= 8:
            reasons.append("资料完善度高，参与积极")

        # --- Same major/grade bonus (max +5) ---
        bonus = 0.0
        if current_user.major and c.major and current_user.major == c.major:
            bonus += 2.5
        if current_user.grade and c.grade and current_user.grade == c.grade:
            bonus += 2.5
        score += bonus
        if bonus >= 4:
            reasons.append("同专业同年级，有共同话题")
        elif bonus >= 2:
            reasons.append("专业或年级相近")

        # Clamp and round
        score = max(0.0, min(100.0, round(score, 1)))

        # Generate reason text
        if not reasons:
            nickname = c.nickname or c.username
            reasons.append(f"{nickname}是潜在的校园搭子人选")
        reason = "；".join(reasons[:3])

        results.append(
            MatchResult(
                candidate_user_id=c.id,
                match_score=score,
                reason=reason,
            )
        )

    # Sort by score descending
    results.sort(key=lambda r: r.match_score, reverse=True)
    return results


def _extract_city(university: str) -> str:
    """Extract a city name from a university string.

    Heuristic: Chinese universities typically contain a city name.
    For others, returns the university name as-is.

    Args:
        university: University name string.

    Returns:
        Extracted city name or empty string.
    """
    city_keywords = [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都",
        "西安", "天津", "重庆", "苏州", "长沙", "郑州", "青岛", "大连",
        "厦门", "福州", "合肥", "沈阳", "哈尔滨", "长春", "济南", "昆明",
        "贵阳", "南宁", "兰州", "乌鲁木齐", "南昌", "太原", "呼和浩特",
        "石家庄", "宁波", "温州", "珠海", "东莞",
    ]
    for city in city_keywords:
        if city in university:
            return city
    # Fallback: use the first 2-3 characters as a rough city indicator
    return university[:2] if len(university) >= 2 else university


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

    # Fall back to rule-based engine when LLM is not configured
    if not _is_llm_configured():
        logger.info(
            "LLM API key not configured — using rule-based matching engine"
        )
        return _rule_based_match(current_user, candidates)

    try:
        agent = create_agent(
            output_type=MatchResultList,
            system_prompt=MATCHING_SYSTEM_PROMPT,
        )
        prompt = _build_candidates_text(current_user, candidates)
        result = await agent.run(prompt)
        # Sort by score descending
        matches = sorted(
            result.data.matches, key=lambda m: m.match_score, reverse=True
        )
        return matches
    except Exception as exc:
        logger.warning(
            "LLM matching failed (%s) — falling back to rule-based engine",
            exc,
        )
        return _rule_based_match(current_user, candidates)
