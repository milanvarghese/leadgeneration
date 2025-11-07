from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple


BudgetRange = Tuple[int, int]


@dataclass
class Lead:
    """Representation of a potential client lead."""

    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    source: str = "unknown"
    rating: Optional[float] = None
    review_count: Optional[int] = None
    analytics: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)
    estimated_budget: Optional[BudgetRange] = None
    growth_score: Optional[float] = None

    def to_dict(self, include_raw: bool = False) -> Dict[str, Any]:
        """Serialize the lead into a dictionary."""

        data = {
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "phone": self.phone,
            "website": self.website,
            "categories": ", ".join(self.categories),
            "source": self.source,
            "rating": self.rating,
            "review_count": self.review_count,
            "estimated_budget_low": self.estimated_budget[0]
            if self.estimated_budget
            else None,
            "estimated_budget_high": self.estimated_budget[1]
            if self.estimated_budget
            else None,
            "growth_score": self.growth_score,
        }
        if include_raw:
            data["analytics"] = self.analytics
            data["extras"] = self.extras
        return data


def deduplicate(leads: Iterable[Lead]) -> List[Lead]:
    """Remove duplicated leads keeping the highest scoring entry."""

    best_by_key: Dict[str, Lead] = {}
    for lead in leads:
        key = f"{lead.name.lower()}::{(lead.phone or '').strip()}"
        existing = best_by_key.get(key)
        if existing is None:
            best_by_key[key] = lead
            continue
        # Prefer the lead with the higher growth score if available
        existing_score = existing.growth_score or 0
        new_score = lead.growth_score or 0
        if new_score > existing_score:
            best_by_key[key] = lead
    return list(best_by_key.values())
