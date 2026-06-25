import re
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (compatible; WebpageChangeNotifier/1.0)"

DATE_TIME_RE = re.compile(
    r"([A-Za-z]{3,9}\.?\s+\d{1,2},\s*\d{4})\s*([\d]{1,2}:[\d]{2}\s*[APMapm.]{2,4})?"
)


def fetch_last_modified_text(url: str, timeout: int = 15) -> str:
    """Fetch a page and extract its 'date modified' footer text.

    Primary strategy targets the OmniUpdate CMS footer pattern used by TTU
    sites: a link to a.cms.omniupdate.com (action=de) containing the date,
    followed by a time string. Falls back to scanning the whole footer for
    a date/time-shaped string.
    """
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    omniupdate_link = soup.find("a", href=re.compile(r"omniupdate\.com.*action=de"))
    if omniupdate_link:
        date_text = omniupdate_link.get_text(strip=True)
        trailing_text = ""
        if omniupdate_link.next_sibling:
            trailing_text = str(omniupdate_link.next_sibling).strip()
        combined = f"{date_text} {trailing_text}".strip()
        if combined:
            return combined

    footer = soup.find("footer") or soup.find(class_=re.compile("footer"))
    search_text = footer.get_text(" ", strip=True) if footer else soup.get_text(" ", strip=True)
    match = DATE_TIME_RE.search(search_text)
    if match:
        return match.group(0).strip()

    raise ValueError(f"Could not find a date-modified marker on {url}")
