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
    "design",
    "development",
    "creative",
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
    "branding",
    "creative",
    "studio",
    "strategy",
}


def estimate_growth_score(lead: Lead) -> float:
    """Compute a heuristic growth score between 0 and 1."""

    score = 0.0
    max_score = 1.65

    categories_text = " ".join(lead.categories).lower()
    description_text = (lead.description or "").lower()

    # A business investing in ads is a strong indicator of a higher budget.
    if lead.analytics.get("adclick"):
        score += 0.25

    # Having a website or listed phone number means they are market ready.
    if lead.website:
        score += 0.35
    if lead.phone:
        score += 0.1

    # Reviews and rating show maturity and likely marketing spend.
    if lead.review_count:
        if lead.review_count >= 20:
            score += 0.3
        elif lead.review_count >= 10:
            score += 0.25
        elif lead.review_count >= 5:
            score += 0.2
        else:
            score += 0.1
    if lead.rating:
        if lead.rating >= 4.5:
            score += 0.25
        elif lead.rating >= 4.0:
            score += 0.2
        elif lead.rating >= 3.5:
            score += 0.15

    if lead.categories:
        score += 0.1  # Simply being categorized means they completed the listing.
    if any(keyword in categories_text for keyword in CATEGORY_KEYWORDS):
        score += 0.25
    if description_text:
        score += 0.1
    if any(keyword in description_text for keyword in GROWTH_KEYWORDS):
        score += 0.25

    normalized = min(score / max_score, 1.0)
    return round(normalized, 3)


def estimate_budget_range(lead: Lead) -> Optional[BudgetRange]:
    """Estimate a project budget range based on the growth score."""

    growth_score = lead.growth_score if lead.growth_score is not None else estimate_growth_score(lead)
    lead.growth_score = growth_score

    if growth_score >= 0.65:
        return (4500, 6500)
    if growth_score >= 0.45:
        return (3200, 5200)
    if growth_score >= 0.35:
        return (2600, 4000)
    if growth_score >= 0.25:
        return (1800, 3000)
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
