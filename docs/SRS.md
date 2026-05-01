# Software Requirements Specification (SRS)
## OSINT Knowledge Graph — AI-Powered Cybersecurity Platform
**Version:** 1.0 | **Date:** 2024 | **Team Size:** 3 Members

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the functional and non-functional requirements of the **OSINT Knowledge Graph** system — an AI-powered platform that automates extraction of cybersecurity entities from unstructured intelligence text and visualises them as an interactive relationship graph.

### 1.2 Scope
The system accepts raw OSINT (Open Source Intelligence) text such as WHOIS lookups, breach reports, threat intelligence feeds, and forum posts. It uses **Google Gemini** for Named Entity Recognition (NER) and **Neo4j** graph database for persistent storage. A **Flask REST API** exposes all operations to a browser-based frontend with 5 interactive screens.

### 1.3 Definitions
| Term | Definition |
|---|---|
| OSINT | Open Source Intelligence — publicly available information used in cybersecurity |
| NER | Named Entity Recognition — AI extraction of entities from text |
| Triplet | Subject → Relation → Object — the atomic unit of graph knowledge |
| IOC | Indicator of Compromise — artefacts (IPs, hashes, domains) associated with threats |
| APT | Advanced Persistent Threat — nation-state or sophisticated threat actor |
| C2 | Command and Control server — attacker-controlled infrastructure |

### 1.4 References
- Google Gemini API Documentation
- Neo4j 5.x Graph Database Documentation
- MITRE ATT&CK Framework (for relationship taxonomy)

---

## 2. Overall Description

### 2.1 System Perspective
The OSINT KG is a standalone web application with three tiers:
- **Presentation tier:** HTML/CSS/JS SPA with D3.js graph visualisation
- **Business logic tier:** Flask REST API + Gemini NER pipeline + Pydantic validation
- **Data tier:** Neo4j graph database (bolt protocol)

### 2.2 User Classes
| User | Description |
|---|---|
| Security Analyst | Primary user — ingests reports, queries entities, pivots on IOCs |
| Threat Intelligence Lead | Reviews threat actor profiles and C2 infrastructure |
| Student/Researcher | Explores OSINT relationships for academic research |

### 2.3 Operating Environment
- Python 3.10+ runtime
- Neo4j 5.x (local or AuraDB cloud)
- Google Gemini API (internet connectivity required for NER)
- Modern browser (Chrome 90+, Firefox 88+)
- Deployable on Google Cloud Run via Docker

---

## 3. Functional Requirements

### FR-01: Text Ingestion
- The system SHALL accept raw OSINT text up to 10,000 characters via the web interface.
- The system SHALL send text to the Gemini API for entity extraction.
- The system SHALL validate the API response against a strict Pydantic schema before storage.

### FR-02: Entity Extraction
- The system SHALL extract entities of at least 15 types including: IPAddress, Domain, Email, ThreatActor, C2Server, Malware, Vulnerability, FileHash.
- The system SHALL extract Subject → Relation → Object triplets with confidence scores.
- The system SHALL handle malformed API responses gracefully without crashing.

### FR-03: Graph Storage
- The system SHALL use MERGE queries to prevent duplicate nodes.
- The system SHALL apply unique constraints on all node label key properties.
- The system SHALL store relationship confidence scores as edge properties.

### FR-04: Graph Visualisation
- The system SHALL display all nodes and relationships as a force-directed interactive graph.
- The system SHALL colour-code nodes by entity type.
- The system SHALL support drag, zoom, and pan interactions.

### FR-05: Entity Search
- The system SHALL search for entities by value and return connected entities up to depth 4.
- The system SHALL display hop distance for each result.

### FR-06: Threat Intelligence
- The system SHALL display all ThreatActor nodes and their full relationship profiles.
- The system SHALL list all C2 servers and their associated threat actors.

### FR-07: Dashboard and Reports
- The system SHALL display real-time counts of nodes by label and relationships by type.
- The system SHALL provide a coverage report with bar chart distribution.

---

## 4. Non-Functional Requirements

| ID | Type | Requirement |
|---|---|---|
| NFR-01 | Performance | API responses for ingestion must complete within 30 seconds |
| NFR-02 | Performance | Graph visualisation must render within 3 seconds for ≤500 nodes |
| NFR-03 | Security | All API keys must be stored in `.env` files, never in source code |
| NFR-04 | Reliability | The system must handle Gemini API failures with clear error messages |
| NFR-05 | Maintainability | All modules must have docstrings and follow PEP 8 |
| NFR-06 | Portability | Must run on any system with Docker installed |
| NFR-07 | Testability | Minimum 15 unit tests covering all critical modules |

---

## 5. Use Case Diagrams

### 5.1 Actors
- **Analyst** — primary system user
- **Gemini API** — external AI service
- **Neo4j** — external data store

### 5.2 Use Cases

```
┌─────────────────────────────────────────────────────────────┐
│                  OSINT Knowledge Graph System               │
│                                                             │
│  ┌──────────┐    ───── UC1: Ingest OSINT Text ──────────    │
│  │          │   /                                           │
│  │          │── ──── UC2: View Knowledge Graph ─────────   │
│  │ Analyst  │   \                                           │
│  │          │    ───── UC3: Search Entity ────────────      │
│  │          │   /                                           │
│  │          │── ──── UC4: View Threat Actor Profile ──      │
│  │          │   \                                           │
│  └──────────┘    ───── UC5: Export Report ─────────────     │
│                                                             │
│  ┌──────────┐                                               │
│  │  Gemini  │ ←── UC1 extends (NER extraction)             │
│  │   API    │                                               │
│  └──────────┘                                               │
│                                                             │
│  ┌──────────┐                                               │
│  │  Neo4j   │ ←── UC1, UC2, UC3, UC4 (CRUD operations)     │
│  └──────────┘                                               │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Detailed Use Cases

**UC1 — Ingest OSINT Text**
- Actor: Analyst
- Precondition: Analyst has raw intelligence text
- Main Flow: Analyst pastes text → clicks Analyze → system sends to Gemini → validates JSON → MERGEs into Neo4j → displays triplets
- Alternative: If Gemini fails, system displays error and allows retry
- Postcondition: Entities stored in graph, triplets displayed on screen

**UC2 — View Knowledge Graph**
- Actor: Analyst
- Precondition: At least one ingestion has been performed
- Main Flow: Analyst navigates to Graph View → system queries Neo4j → renders D3 force graph → Analyst can drag/zoom/pan nodes
- Postcondition: Visual graph rendered in browser

**UC3 — Search Entity**
- Actor: Analyst
- Precondition: Entity exists in graph
- Main Flow: Analyst enters IP/domain/name → selects depth → clicks Search → system runs Cypher → displays connected entities with hop count
- Postcondition: Related entities shown in list with distance

**UC4 — View Threat Actor Profile**
- Actor: Analyst
- Precondition: ThreatActor node exists in graph
- Main Flow: Analyst navigates to Threat Intel → selects actor → system queries all relationships → displays profile card with C2 servers, tools, targets
- Postcondition: Full actor profile rendered

**UC5 — View Reports**
- Actor: Analyst
- Main Flow: Analyst navigates to Reports → system aggregates stats → displays bar charts of node/rel distributions
- Postcondition: Coverage report rendered

---

## 6. Data Flow Diagram

### 6.1 DFD Level 0 (Context Diagram)

```
                    ┌─────────────────────────────────────┐
                    │                                     │
  Raw OSINT Text    │                                     │   Structured
 ─────────────────▶│     OSINT KNOWLEDGE GRAPH           │──────────────▶ Entities
                    │         SYSTEM                      │   & Relations
  Queries           │                                     │
 ─────────────────▶│                                     │   Graph Data
                    │                                     │──────────────▶ (D3 visual)
  API Credentials   │                                     │
 ─────────────────▶│                                     │   Reports &
                    │                                     │──────────────▶ Statistics
                    └─────────────────────────────────────┘
                                   │         ▲
                                   │         │
                            ┌──────▼─────────┴──────┐
                            │   External Services   │
                            │  - Google Gemini API  │
                            │  - Neo4j Database     │
                            └───────────────────────┘
```

### 6.2 DFD Level 1 (System Decomposition)

```
               Raw Text
                  │
                  ▼
         ┌────────────────┐    JSON prompt    ┌─────────────┐
         │  1.0 Text      │──────────────────▶│  Gemini API │
         │  Ingestion     │◀──────────────────│  (external) │
         └────────────────┘   Triplets JSON   └─────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  2.0 Pydantic  │  validates schema
         │  Validation    │  rejects bad JSON
         └────────────────┘
                  │
            validated triplets
                  │
         ┌────────────────┐   Cypher MERGE    ┌─────────────┐
         │  3.0 Graph     │──────────────────▶│   Neo4j     │
         │  Storage       │◀──────────────────│  Database   │
         └────────────────┘   query results   └─────────────┘
                  │                                   │
          ┌───────┤                                   │
          │       │                                   │
          ▼       ▼                                   │
 ┌──────────┐ ┌──────────┐                            │
 │ 4.0 API  │ │ 5.0      │◀───────────────────────────┘
 │ REST     │ │ Frontend │
 │ Layer    │ │ SPA      │
 └──────────┘ └──────────┘
```

---

## 7. UML Class Diagram

```
┌─────────────────────────────┐
│       OSINTExtractor        │
├─────────────────────────────┤
│ - model: GenerativeModel    │
│ - api_key: str              │
├─────────────────────────────┤
│ + extract(text) → Result    │
│ + extract_batch(texts) →    │
│     list[Result]            │
└────────────┬────────────────┘
             │ produces
             ▼
┌─────────────────────────────┐
│      ExtractionResult       │
├─────────────────────────────┤
│ + triplets: list[Triplet]   │
│ + raw_entities: list[Entity]│
│ + source_summary: str       │
└────────────────┬────────────┘
                 │ contains
    ┌────────────┼────────────┐
    ▼            │            ▼
┌──────────┐     │    ┌──────────┐
│ Entity   │     │    │ Triplet  │
├──────────┤     │    ├──────────┤
│+ label   │     │    │+ subject │→ Entity
│+ value   │     │    │+ relation│
│+properties│    │    │+ object  │→ Entity
└──────────┘     │    │+confidence│
                 │    └──────────┘
                 │
                 ▼
┌─────────────────────────────┐
│      DatabaseManager        │
├─────────────────────────────┤
│ - driver: Driver            │
│ - database: str             │
├─────────────────────────────┤
│ + setup_constraints()       │
│ + ingest_extraction_result()│
│ + find_related_entities()   │
│ + get_threat_actor_profile()│
│ + get_all_c2_infrastructure()│
│ + clear_database()          │
└─────────────────────────────┘
```

---

## 8. Pointed Features (Unique Selling Points)

1. **AI-first entity extraction** — Uses Gemini's JSON mode with `response_mime_type="application/json"` for guaranteed structured output, eliminating brittle regex-based parsers.

2. **Idempotent graph ingestion** — All nodes use `MERGE` not `CREATE`, so the same intelligence text can be re-analyzed without creating duplicates.

3. **Confidence scoring** — Every relationship carries a `confidence` property (0.0–1.0), allowing analysts to filter low-confidence intelligence.

4. **Professional OSINT schema** — 17 node types and 15 relationship types modelled after the MITRE ATT&CK framework, making this enterprise-grade.

5. **Live D3 force graph** — Interactive browser-based graph visualisation with drag, zoom, and colour-coded nodes — no external tools required.

6. **Pydantic validation layer** — All Gemini output is validated before touching the database, preventing corrupt or hallucinated data from being stored.

7. **Cloud-ready deployment** — Docker + Gunicorn + Cloud Run deployment with a single `gcloud run deploy` command.

---

## 9. Appendix: Technology Matrix

| Component | Technology | Justification |
|---|---|---|
| Backend language | Python 3.11 | Widest AI/ML library ecosystem |
| AI engine | Google Gemini 1.5 Flash | Free tier, JSON output mode, low latency |
| Graph DB | Neo4j 5.x | Industry standard for knowledge graphs |
| API framework | Flask 3.x | Lightweight, easy to test, REST-native |
| Validation | Pydantic 2.x | Type-safe, fast, integrates with FastAPI-style APIs |
| Frontend | Vanilla JS + D3 v7 | No build step, minimal dependencies |
| Testing | pytest + unittest.mock | Industry standard, mocks external APIs |
| Deployment | Docker + GCR | Portable, production-grade, free tier available |
| CI/CD | GitHub Actions | Free for public repos, auto-runs on push |
