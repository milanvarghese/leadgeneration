from leadgen.filters import apply_budget_filter, estimate_budget_range, estimate_growth_score
from leadgen.models import Lead


def build_lead(**kwargs):
    defaults = dict(
        name="Test Lead",
        categories=["Marketing Consultants"],
        analytics={"adclick": True},
        website="https://example.com",
        review_count=12,
        rating=4.2,
    )
    defaults.update(kwargs)
    return Lead(**defaults)


def test_estimate_growth_score_scaling():
    lead = build_lead(description="We help companies grow with digital marketing")
    score = estimate_growth_score(lead)
    assert 0.7 <= score <= 1.0


def test_estimate_budget_range_high_score():
    lead = build_lead()
    lead.growth_score = 0.8
    budget = estimate_budget_range(lead)
    assert budget == (4500, 6500)


def test_apply_budget_filter_filters_outside_range():
    lead_inside = build_lead()
    lead_outside = build_lead(name="Low Budget", analytics={}, review_count=0, rating=2.0)
    leads = apply_budget_filter([lead_inside, lead_outside], minimum=3000, maximum=5000)
    assert len(leads) == 1
    assert leads[0].name == "Test Lead"
