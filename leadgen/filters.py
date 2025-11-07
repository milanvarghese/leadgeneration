from __future__ import annotations

from typing import Iterable, List, Optional

from .models import Lead, BudgetRange

# Keywords that suggest the business values growth and is willing to invest.
GROWTH_KEYWORDS = {
    "growth",
    "marketing",
    "digital",
    "branding",
    "consulting",
    "innovation",
    "strategy",
    "venture",
    "capital",
    "accelerator",
    "coworking",
}

CATEGORY_KEYWORDS = {
    "marketing",
    "consultant",
    "agency",
    "design",
    "development",
    "software",
    "venture",
    "capital",
    "investment",
    "coworking",
    "accelerator",
}


def estimate_growth_score(lead: Lead) -> float:
    """Compute a heuristic growth score between 0 and 1."""

    score = 0.0
    max_score = 6.0

    categories_text = " ".join(lead.categories).lower()
    description_text = (lead.description or "").lower()

    if lead.analytics.get("adclick"):
        score += 1.5
    if lead.website:
        score += 1.0
    if lead.review_count and lead.review_count >= 5:
        score += 1.0
    if lead.rating and lead.rating >= 4.0:
        score += 1.0
    if any(keyword in categories_text for keyword in CATEGORY_KEYWORDS):
        score += 0.8
    if any(keyword in description_text for keyword in GROWTH_KEYWORDS):
        score += 0.7

    normalized = min(score / max_score, 1.0)
    return round(normalized, 3)


def estimate_budget_range(lead: Lead) -> Optional[BudgetRange]:
    """Estimate a project budget range based on the growth score."""

    growth_score = lead.growth_score if lead.growth_score is not None else estimate_growth_score(lead)
    lead.growth_score = growth_score

    if growth_score >= 0.75:
        return (4500, 6500)
    if growth_score >= 0.55:
        return (3200, 5200)
    if growth_score >= 0.4:
        return (2500, 4000)
    if growth_score >= 0.25:
        return (1500, 2800)
    return None


def apply_budget_filter(leads: Iterable[Lead], minimum: int, maximum: int) -> List[Lead]:
    """Filter leads that intersect the desired budget range."""

    filtered: List[Lead] = []
    for lead in leads:
        estimated = estimate_budget_range(lead)
        lead.estimated_budget = estimated
        if estimated is None:
            continue
        low, high = estimated
        if low <= maximum and high >= minimum:
            filtered.append(lead)
    return filtered
