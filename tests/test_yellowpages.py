from textwrap import dedent

from bs4 import BeautifulSoup

from leadgen.sources.yellowpages import YellowPagesScraper


def test_slugify_replaces_spaces_and_symbols():
    scraper = YellowPagesScraper(city="Philadelphia", state="PA")
    assert scraper._slugify("Digital Marketing") == "digital-marketing"
    assert scraper._slugify("Growth & Strategy!") == "growth-strategy"


def test_parse_result_extracts_core_fields():
    scraper = YellowPagesScraper(city="Philadelphia", state="PA")
    html = dedent(
        """
        <div class="result" data-analytics='{"adclick": true}'>
          <a class="business-name"><span>Growth Agency</span></a>
          <div class="snippet">We help companies grow.</div>
          <div class="categories">Marketing Consultants\nBusiness Coaches</div>
          <div class="phones">(555) 123-4567</div>
          <a class="track-visit-website" href="/growth-agency">Website</a>
          <div class="street-address">123 Market St</div>
          <div class="locality">Philadelphia, PA</div>
        </div>
        """
    )
    tag = BeautifulSoup(html, "html.parser").select_one("div.result")
    lead = scraper._parse_result(tag, "digital marketing")
    assert lead is not None
    assert lead.name == "Growth Agency"
    assert lead.phone == "(555) 123-4567"
    assert lead.website.endswith("/growth-agency")
    assert lead.location == "123 Market St, Philadelphia, PA"
    assert "Marketing Consultants" in lead.categories
    assert lead.analytics.get("adclick") is True
