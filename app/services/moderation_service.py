"""Content moderation business logic.

Wraps the AI moderation engine with grading strategy and fallback behavior.
Used internally by post_service and (later) chat_service — no standalone API.
"""

import logging

from app.ai.moderation import ModerationResult, moderate

logger = logging.getLogger(__name__)


class ModerationDecision:
    """Post-moderation decision after applying grading thresholds.

    Attributes:
        result: The raw AI moderation result.
        action: Final handling action — 'pass', 'flag', or 'block'.
    """

    def __init__(self, result: ModerationResult, action: str):
        self.result = result
        self.action = action


# ===== Grading Thresholds =====
# Based on PRD Section 4.4:
#   confidence < 30% → pass freely
#   30%-70% → flag for review
#   > 70% → block if violation, pass if not

HIGH_CONFIDENCE = 0.7
LOW_CONFIDENCE = 0.3


async def moderate_content(
    content: str,
    context: str = "",
) -> ModerationDecision:
    """Run AI moderation on the given content and produce a decision.

    Grading strategy:
        - If the model is highly confident (>70%) AND reports a violation
          → block.
        - If the model is highly confident AND reports no violation → pass.
        - If confidence is moderate (30%-70%) → flag for manual review.
        - If confidence is low (<30%) → pass (unreliable verdict).

    Falls back to a permissive pass if the AI call fails (timeout, API error).

    Args:
        content: The text to moderate.
        context: A hint like "post body" or "chat message".

    Returns:
        A ModerationDecision with an action of 'pass', 'flag', or 'block'.
    """
    try:
        result: ModerationResult = await moderate(content, context)
    except Exception as exc:
        logger.warning("Moderation AI call failed, defaulting to pass: %s", exc)
        return ModerationDecision(
            result=ModerationResult(
                is_violation=False,
                violation_type="none",
                confidence=0.0,
                reason="AI moderation unavailable, auto-passed",
                suggestion="pass",
            ),
            action="pass",
        )

    # Apply grading thresholds
    if result.is_violation and result.confidence >= HIGH_CONFIDENCE:
        action = "block"
    elif result.confidence < LOW_CONFIDENCE:
        action = "pass"
    elif LOW_CONFIDENCE <= result.confidence < HIGH_CONFIDENCE:
        action = "flag"
    else:
        # Confident that it's NOT a violation
        action = "pass"

    return ModerationDecision(result=result, action=action)
