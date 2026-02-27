#!/usr/bin/env python3
"""
Example script: Using QSAR LLM API programmatically

This script demonstrates how to interact with QSAR LLM backend
without using the web interface.

Requirements:
- QSAR LLM server running (python app.py)
- Optional: QSAR Toolbox WebAPI running for full functionality

Usage:
    python3 example_api_usage.py
"""

import requests
import json
import sys
from typing import Dict, Optional

# Configuration
QSAR_LLM_URL = "http://localhost:8000"
TIMEOUT = 60  # seconds


class QSARLLMClient:
    """Client for QSAR LLM API"""

    def __init__(self, base_url: str = QSAR_LLM_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def check_status(self) -> Dict:
        """Check server and QSAR Toolbox status"""
        try:
            resp = self.session.get(f"{self.base_url}/api/status", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return {"error": str(e)}

    def check_toolbox_health(self) -> Dict:
        """Get detailed QSAR Toolbox health check"""
        try:
            resp = self.session.get(f"{self.base_url}/api/toolbox/health", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"⚠️  Health check unavailable: {e}")
            return {"error": str(e)}

    def chat(
        self,
        query: str,
        language: str = "es",
        profiling: bool = True,
        read_across: bool = True,
        aquatic: bool = True,
        mutagen: bool = True,
    ) -> Dict:
        """
        Send chat query to QSAR LLM

        Args:
            query: User query (e.g., "Analiza glifosato CAS 1071-83-6")
            language: Response language (es, en, pt)
            profiling: Enable structural profiling
            read_across: Enable read-across predictions
            aquatic: Check aquatic toxicity
            mutagen: Check mutagenicity (Ames)

        Returns:
            Dict with 'message' and optional 'data' fields
        """
        payload = {
            "query": query,
            "language": language,
            "options": {
                "profiling": profiling,
                "readAcross": read_across,
                "aquatic": aquatic,
                "mutagen": mutagen,
            },
        }

        try:
            resp = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"❌ Chat error: {e}")
            return {"error": str(e)}

    def search_substance(self, identifier: str) -> Dict:
        """Search for substance in QSAR Toolbox"""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/toolbox/search",
                params={"q": identifier},
                timeout=10,
            )
            if resp.ok:
                return resp.json()
            else:
                return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            print(f"⚠️  Search failed: {e}")
            return {"error": str(e)}

    def run_profiling(self, cas: str, profilers: Optional[list] = None) -> Dict:
        """Run structural profiling for a substance"""
        if profilers is None:
            profilers = ["mutagenicity", "aquatic_toxicity", "skin_sensitization"]

        payload = {"cas": cas, "profilers": profilers}

        try:
            resp = self.session.post(
                f"{self.base_url}/api/toolbox/profile",
                json=payload,
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"⚠️  Profiling failed: {e}")
            return {"error": str(e)}

    def get_pubchem_data(self, identifier: str) -> Dict:
        """Get chemical data from PubChem"""
        try:
            resp = self.session.get(
                f"{self.base_url}/api/pubchem",
                params={"q": identifier},
                timeout=10,
            )
            if resp.ok:
                return resp.json()
            else:
                return {"error": f"Not found"}
        except Exception as e:
            print(f"⚠️  PubChem lookup failed: {e}")
            return {"error": str(e)}


def main():
    """Example usage"""
    print("=" * 60)
    print("QSAR LLM API Example Client")
    print("=" * 60)

    # Initialize client
    client = QSARLLMClient(QSAR_LLM_URL)

    # 1. Check server status
    print("\n1. Checking server status...")
    status = client.check_status()
    if "error" not in status:
        print(f"   ✓ Backend: Online")
        print(f"   ✓ QSAR Toolbox: {status.get('toolbox_connected', False)}")
        if not status.get("toolbox_connected") and status.get("toolbox_error"):
            print(f"   ℹ️  {status.get('toolbox_error')}")
    else:
        print(f"   ❌ Error: {status['error']}")
        return

    # 2. Check QSAR Toolbox health
    print("\n2. Checking QSAR Toolbox health...")
    health = client.check_toolbox_health()
    if "status" in health:
        print(f"   Status: {health['status']}")
        checks = health.get("checks", {})
        if checks.get("connectivity"):
            print(f"   ✓ Connectivity OK")
        if checks.get("version"):
            print(f"   ✓ Version: {checks['version']}")
        if checks.get("profilers"):
            print(f"   ✓ Profilers available")
        if checks.get("substances"):
            print(f"   ✓ Substance search available")

    # 3. PubChem lookup
    print("\n3. Testing PubChem data retrieval...")
    pubchem = client.get_pubchem_data("1071-83-6")  # Glyphosate
    if "error" not in pubchem:
        print(f"   ✓ Found: {pubchem.get('iupac', 'N/A')}")
        print(f"     Formula: {pubchem.get('formula', 'N/A')}")
        print(f"     MW: {pubchem.get('mw', 'N/A')}")
    else:
        print(f"   ⚠️  {pubchem['error']}")

    # 4. Search QSAR Toolbox (if available)
    print("\n4. Searching QSAR Toolbox...")
    search = client.search_substance("1071-83-6")  # Glyphosate
    if "error" not in search:
        print(f"   ✓ Found in Toolbox")
    else:
        print(f"   ℹ️  Not found or Toolbox unavailable")

    # 5. Run profiling (if QSAR Toolbox available)
    print("\n5. Running structural profiling...")
    profile = client.run_profiling("1071-83-6")
    if "error" not in profile:
        print(f"   ✓ Profiling completed")
        alerts = profile.get("alerts", [])
        if alerts:
            print(f"     Found {len(alerts)} alerts")
    else:
        print(f"   ℹ️  Profiling unavailable (Toolbox not connected)")

    # 6. Main chat example
    print("\n6. Running chat analysis...")
    print("   Query: 'Analiza glifosato CAS 1071-83-6'")
    response = client.chat(
        "Proporciona un análisis regulatorio del glifosato CAS 1071-83-6",
        language="es",
    )

    if "error" not in response:
        print("\n   Response:")
        message = response.get("message", "")
        # Print first 500 chars
        preview = message[: 300].replace("\n", "\n   ")
        print(f"   {preview}...")
        print(f"\n   Connected to Toolbox: {response.get('toolbox_connected', False)}")
    else:
        print(f"   ❌ Error: {response['error']}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
