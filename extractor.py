"""
=============================================================
  OSINT Knowledge Graph - AI Extractor (Task A)
  Uses Google Gemini to extract entity triplets from raw text.
=============================================================
"""

import json
import re
import os
import google.generativeai as genai
from pydantic import BaseModel, field_validator
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

load_dotenv()
console = Console()

# ── Pydantic models for strict validation ────────────────────────────────────

class Entity(BaseModel):
    """Represents a single node in the graph."""
    label: str          # e.g. "IPAddress", "Email", "Domain", "ThreatActor"
    value: str          # The actual value, e.g. "192.168.1.1"
    properties: dict    # Extra metadata extracted by Gemini

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        allowed = {
            "IPAddress", "Domain", "Email", "Person", "Organization",
            "ThreatActor", "C2Server", "Vulnerability", "Malware",
            "FileHash", "ASN", "Geolocation", "URL", "Port",
            "Certificate", "DataBreach", "Credential"
        }
        if v not in allowed:
            raise ValueError(f"Unknown label '{v}'. Must be one of: {allowed}")
        return v


class Triplet(BaseModel):
    """Represents a Subject -> Relationship -> Object triplet."""
    subject: Entity
    relation: str       # e.g. "OWNED_BY", "RESOLVES_TO"
    object: Entity
    confidence: float   # 0.0 - 1.0, Gemini's self-reported confidence

    @field_validator("relation")
    @classmethod
    def validate_relation(cls, v: str) -> str:
        allowed = {
            "RESOLVES_TO", "OWNED_BY", "ATTRIBUTED_TO", "EXPLOITS",
            "COMMUNICATES_WITH", "HOSTS", "ASSOCIATED_WITH", "LOCATED_IN",
            "USES", "MEMBER_OF", "TARGETS", "HAS_HASH", "LEAKED_IN",
            "REGISTERED_BY", "PART_OF"
        }
        if v not in allowed:
            # Fall back to ASSOCIATED_WITH for unknown relations
            return "ASSOCIATED_WITH"
        return v

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, float(v)))


class ExtractionResult(BaseModel):
    """The full output from one Gemini extraction call."""
    triplets: list[Triplet]
    raw_entities: list[Entity]   # standalone entities with no clear relation
    source_summary: str          # Brief Gemini summary of what the text was about


# ── Prompt engineering ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a world-class OSINT (Open Source Intelligence) analyst and cybersecurity expert.

Your task is to analyze raw intelligence text and extract structured knowledge in the form of ENTITY TRIPLETS.

## OUTPUT FORMAT
You MUST respond with ONLY valid JSON. No markdown, no explanation, no code fences.
The JSON must match this exact schema:

{
  "triplets": [
    {
      "subject": {
        "label": "<NodeLabel>",
        "value": "<entity_value>",
        "properties": { "<key>": "<value>" }
      },
      "relation": "<RELATIONSHIP_TYPE>",
      "object": {
        "label": "<NodeLabel>",
        "value": "<entity_value>",
        "properties": { "<key>": "<value>" }
      },
      "confidence": 0.95
    }
  ],
  "raw_entities": [
    {
      "label": "<NodeLabel>",
      "value": "<entity_value>",
      "properties": {}
    }
  ],
  "source_summary": "One sentence describing the intelligence content."
}

## ALLOWED NODE LABELS (use EXACTLY these strings):
IPAddress, Domain, Email, Person, Organization, ThreatActor, C2Server,
Vulnerability, Malware, FileHash, ASN, Geolocation, URL, Port,
Certificate, DataBreach, Credential

## ALLOWED RELATIONSHIP TYPES (use EXACTLY these strings):
RESOLVES_TO, OWNED_BY, ATTRIBUTED_TO, EXPLOITS, COMMUNICATES_WITH,
HOSTS, ASSOCIATED_WITH, LOCATED_IN, USES, MEMBER_OF, TARGETS,
HAS_HASH, LEAKED_IN, REGISTERED_BY, PART_OF

## EXTRACTION RULES:
1. Extract ALL entities you can find: IPs, emails, domains, CVEs, hashes, names, orgs.
2. Create a triplet for EVERY relationship you can infer from the text.
3. For IPs: include version (IPv4/IPv6) in properties.
4. For CVEs: use label "Vulnerability" and cve_id as value.
5. For file hashes: detect type (MD5=32 chars, SHA1=40, SHA256=64) and add hash_type to properties.
6. If an entity appears without a clear partner, put it in raw_entities.
7. confidence is YOUR estimate of how certain this relationship is (0.0 to 1.0).
8. Do NOT hallucinate. Only extract what is in the text.
"""


# ── Extractor class ──────────────────────────────────────────────────────────

class OSINTExtractor:
    """
    Sends raw OSINT text to Gemini and returns validated ExtractionResult.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not found. Set it in .env or pass directly.")

        genai.configure(api_key=key)

        # Use Gemini 1.5 Flash for speed; swap to gemini-1.5-pro for accuracy
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.1,          # Low temperature = more deterministic JSON
                top_p=0.95,
                response_mime_type="application/json",   # Force JSON output mode
            )
        )

    def extract(self, raw_text: str) -> ExtractionResult:
        """
        Main extraction method. Sends text to Gemini, validates, returns result.

        Args:
            raw_text: Any unstructured OSINT text (WHOIS, breach report, forum post, etc.)

        Returns:
            ExtractionResult with validated triplets and entities.
        """
        console.print(Panel(
            f"[bold cyan]Sending {len(raw_text)} characters to Gemini for extraction...[/bold cyan]",
            title="[yellow]OSINT Extractor[/yellow]"
        ))

        user_message = f"""Analyze this OSINT intelligence text and extract all entities and relationships:

--- INTELLIGENCE TEXT START ---
{raw_text}
--- INTELLIGENCE TEXT END ---

Remember: respond with ONLY valid JSON. No other text."""

        try:
            response = self.model.generate_content(user_message)
            raw_json_str = response.text.strip()

            # Safety: strip any accidental markdown fences Gemini might add
            raw_json_str = re.sub(r"^```[a-z]*\n?", "", raw_json_str)
            raw_json_str = re.sub(r"\n?```$", "", raw_json_str)

            # Show raw JSON for debugging
            console.print(Panel(
                Syntax(raw_json_str[:2000], "json", theme="monokai"),
                title="[green]Raw Gemini Output[/green]"
            ))

            parsed = json.loads(raw_json_str)
            result = ExtractionResult(**parsed)

            console.print(f"[bold green]✔ Extracted {len(result.triplets)} triplets "
                          f"and {len(result.raw_entities)} standalone entities.[/bold green]")
            return result

        except json.JSONDecodeError as e:
            console.print(f"[bold red]JSON Parse Error:[/bold red] {e}")
            console.print(f"Raw response was:\n{raw_json_str}")
            raise
        except Exception as e:
            console.print(f"[bold red]Extraction failed:[/bold red] {e}")
            raise

    def extract_batch(self, texts: list[str]) -> list[ExtractionResult]:
        """Process multiple intelligence texts sequentially."""
        results = []
        for i, text in enumerate(texts):
            console.print(f"\n[yellow]Processing text {i+1}/{len(texts)}...[/yellow]")
            results.append(self.extract(text))
        return results
