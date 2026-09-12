from typing import List, Dict, Any
import requests
from urllib.parse import urljoin

class ESCOClient:
    def __init__(self, base_url: str, timeout: int = 12):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def search_occupations(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not text.strip():
            return []

        # ESCO web-service API search endpoint.
        url = urljoin(self.base_url, "search")
        params = {
            "text": text.strip(),
            "language": "en",
            "type": "occupation",
            "selectedVersion": "1.2.1",
            "limit": limit,
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        results = payload.get("_embedded", {}).get("results", [])
        output = []
        for item in results[:limit]:
            output.append({
                "title": item.get("preferredLabel") or item.get("title") or "",
                "uri": item.get("uri", ""),
                "description": item.get("description", ""),
            })
        return output

    def occupation_context(self, titles: List[str]) -> str:
        snippets = []
        for title in titles[:5]:
            results = self.search_occupations(title, limit=2)
            for r in results[:1]:
                if r["title"]:
                    snippets.append(f'{r["title"]}: {r.get("description","")}')
        return "\n".join(snippets)
