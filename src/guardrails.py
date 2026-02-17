"""Input and output guardrails for the supply chain agent system."""
import re
import logging

logger = logging.getLogger("scia")

# --- Input Guardrails ---

SUPPLY_CHAIN_KEYWORDS = [
    "supply", "chain", "inventory", "stock", "stockout", "demand", "forecast",
    "supplier", "product", "order", "reorder", "lead time", "warehouse",
    "shipment", "logistics", "procurement", "cost", "price", "sales",
    "shortage", "surplus", "report", "analysis", "trend", "risk",
    "performance", "delivery", "fulfillment", "p001", "p002", "p003",
    "p004", "p005", "lay's", "pepsi", "doritos", "gatorade", "quaker",
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)",
    r"forget\s+(your|all)\s+(instructions|rules|guidelines)",
    r"you\s+are\s+now\s+a",
    r"new\s+instructions?:",
    r"system\s*prompt:",
    r"act\s+as\s+(if\s+you\s+are|a)\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"disregard\s+(all|your|previous)",
    r"override\s+(your|the)\s+(instructions|rules|system)",
    r"jailbreak",
    r"\[system\]",
    r"<\s*system\s*>",
]

MAX_INPUT_LENGTH = 1000


class GuardrailResult:
    def __init__(self, passed: bool, message: str = ""):
        self.passed = passed
        self.message = message


def check_input(query: str) -> GuardrailResult:
    """Validate user input before sending to agents."""
    if not query or not query.strip():
        return GuardrailResult(False, "Please enter a query about your supply chain.")

    if len(query) > MAX_INPUT_LENGTH:
        return GuardrailResult(
            False,
            f"Query too long ({len(query)} chars). Please keep it under {MAX_INPUT_LENGTH} characters."
        )

    # Check for prompt injection attempts
    query_lower = query.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            logger.warning(f"Prompt injection attempt blocked: {query[:100]}")
            return GuardrailResult(
                False,
                "Your query was blocked by our safety filter. Please ask a question about supply chain operations."
            )

    # Check domain relevance
    if not any(kw in query_lower for kw in SUPPLY_CHAIN_KEYWORDS):
        return GuardrailResult(
            False,
            "This system is designed for supply chain analysis. "
            "Please ask about inventory, demand, suppliers, products, or logistics."
        )

    return GuardrailResult(True)


# --- Output Guardrails ---

SENSITIVE_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]"),            # SSN
    (r"\b\d{16}\b", "[CARD NUMBER REDACTED]"),                 # Credit card
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL REDACTED]"),  # Email
    (r"(?i)(api[_\s]?key|secret[_\s]?key|password)\s*[:=]\s*\S+", "[CREDENTIAL REDACTED]"),
]

HALLUCINATION_INDICATORS = [
    "as an ai",
    "i don't have access to real",
    "i cannot access real-time",
    "hypothetical",
    "i'm making this up",
    "i don't actually know",
]

DISCLAIMER = (
    "\n\n---\n*This analysis is based on sample data and AI-generated insights. "
    "Verify findings against actual systems before making business decisions.*"
)


def check_output(response: str) -> str:
    """Sanitize and validate agent output before returning to user."""
    if not response or not response.strip():
        return "The agents were unable to generate a response. Please try rephrasing your query."

    # Redact sensitive information
    for pattern, replacement in SENSITIVE_PATTERNS:
        response = re.sub(pattern, replacement, response)

    # Flag potential hallucinations
    response_lower = response.lower()
    has_hallucination_flag = any(ind in response_lower for ind in HALLUCINATION_INDICATORS)
    if has_hallucination_flag:
        logger.warning("Potential hallucination detected in output")
        response += "\n\n> **Note:** Some parts of this response may contain uncertain information. Please verify against actual data."

    # Add disclaimer
    if not response.endswith(DISCLAIMER):
        response += DISCLAIMER

    return response
