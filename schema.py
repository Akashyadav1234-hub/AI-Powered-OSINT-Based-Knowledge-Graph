"""
=============================================================
  OSINT Knowledge Graph - Graph Schema (Task C)
  Cybersecurity Major Project
=============================================================

SCHEMA OVERVIEW
---------------
This module defines the professional graph schema used
for the OSINT Knowledge Graph. Each constant below maps
directly to labels and relationship types in Neo4j.

NODE LABELS
-----------
  - IPAddress       : IPv4/IPv6 address observed in OSINT data
  - Domain          : Fully Qualified Domain Name (FQDN)
  - Email           : Email address of a person or service account
  - Person          : Real-world individual (threat actor, victim, admin)
  - Organization    : Company, group, or criminal syndicate
  - ThreatActor     : Named APT group or individual attacker
  - C2Server        : Command & Control infrastructure server
  - Vulnerability   : CVE or 0-day vulnerability
  - Malware         : Malicious software sample or family
  - FileHash        : MD5 / SHA1 / SHA256 hash of a file artifact
  - ASN             : Autonomous System Number (network owner)
  - Geolocation     : Country / City associated with an IP or actor
  - URL             : Specific uniform resource locator
  - Port            : Open network port
  - Certificate     : TLS/SSL certificate (for pivoting)
  - DataBreach      : A recorded data breach incident
  - Credential      : Leaked username/password pair

RELATIONSHIP TYPES
------------------
  - RESOLVES_TO       : Domain -> IPAddress
  - OWNED_BY          : IPAddress/Domain/Email -> Person/Organization
  - ATTRIBUTED_TO     : Malware/C2Server/Attack -> ThreatActor
  - EXPLOITS          : ThreatActor/Malware -> Vulnerability
  - COMMUNICATES_WITH : IPAddress -> C2Server
  - HOSTS             : IPAddress -> Domain/Malware
  - ASSOCIATED_WITH   : Generic link between any two entities
  - LOCATED_IN        : IPAddress/Person -> Geolocation
  - USES              : ThreatActor -> Malware/Tool/C2Server
  - MEMBER_OF         : Person -> Organization/ThreatActor (group)
  - TARGETS           : ThreatActor -> Organization/Vulnerability
  - HAS_HASH          : Malware -> FileHash
  - LEAKED_IN         : Credential/Email -> DataBreach
  - REGISTERED_BY     : Domain -> Person/Organization (WHOIS)
  - PART_OF           : IPAddress -> ASN

NODE PROPERTIES (per label)
----------------------------
  IPAddress:
    - address (STRING, UNIQUE)     : e.g. "192.168.1.1"
    - version (STRING)             : "IPv4" or "IPv6"
    - is_tor_exit (BOOLEAN)
    - is_vpn (BOOLEAN)
    - first_seen (DATE)
    - last_seen  (DATE)
    - confidence_score (FLOAT)     : 0.0 - 1.0

  Domain:
    - fqdn (STRING, UNIQUE)        : e.g. "evil.example.com"
    - registrar (STRING)
    - creation_date (DATE)
    - expiry_date (DATE)
    - confidence_score (FLOAT)

  Email:
    - address (STRING, UNIQUE)     : e.g. "attacker@proton.me"
    - provider (STRING)            : "ProtonMail", "Gmail", etc.
    - is_disposable (BOOLEAN)
    - confidence_score (FLOAT)

  ThreatActor:
    - name (STRING, UNIQUE)        : e.g. "Lazarus Group"
    - aliases (LIST<STRING>)
    - nation_state (STRING)
    - motivation (STRING)          : "Espionage", "Financial", etc.
    - sophistication (STRING)      : "Advanced", "Intermediate", etc.
    - first_seen (DATE)

  Vulnerability:
    - cve_id (STRING, UNIQUE)      : e.g. "CVE-2024-1234"
    - cvss_score (FLOAT)
    - severity (STRING)            : "CRITICAL", "HIGH", "MEDIUM", "LOW"
    - description (STRING)
    - affected_product (STRING)

  Malware:
    - name (STRING, UNIQUE)        : e.g. "WannaCry"
    - family (STRING)              : "Ransomware", "RAT", "Dropper"
    - is_open_source (BOOLEAN)

  C2Server:
    - address (STRING, UNIQUE)     : IP or domain acting as C2
    - protocol (STRING)            : "HTTP", "HTTPS", "DNS", "IRC"
    - framework (STRING)           : "Cobalt Strike", "Metasploit", etc.

  DataBreach:
    - breach_id (STRING, UNIQUE)   : e.g. "breach_adobe_2013"
    - breach_date (DATE)
    - records_leaked (INTEGER)
    - source (STRING)

  Credential:
    - username (STRING)
    - password_hash (STRING)
    - plaintext_password (STRING)  : Only for OSINT/educational use
"""

# ── Node Labels ──────────────────────────────────────────────────────────────
class NodeLabel:
    IP_ADDRESS   = "IPAddress"
    DOMAIN       = "Domain"
    EMAIL        = "Email"
    PERSON       = "Person"
    ORGANIZATION = "Organization"
    THREAT_ACTOR = "ThreatActor"
    C2_SERVER    = "C2Server"
    VULNERABILITY= "Vulnerability"
    MALWARE      = "Malware"
    FILE_HASH    = "FileHash"
    ASN          = "ASN"
    GEOLOCATION  = "Geolocation"
    URL          = "URL"
    PORT         = "Port"
    CERTIFICATE  = "Certificate"
    DATA_BREACH  = "DataBreach"
    CREDENTIAL   = "Credential"


# ── Relationship Types ───────────────────────────────────────────────────────
class RelType:
    RESOLVES_TO       = "RESOLVES_TO"
    OWNED_BY          = "OWNED_BY"
    ATTRIBUTED_TO     = "ATTRIBUTED_TO"
    EXPLOITS          = "EXPLOITS"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    HOSTS             = "HOSTS"
    ASSOCIATED_WITH   = "ASSOCIATED_WITH"
    LOCATED_IN        = "LOCATED_IN"
    USES              = "USES"
    MEMBER_OF         = "MEMBER_OF"
    TARGETS           = "TARGETS"
    HAS_HASH          = "HAS_HASH"
    LEAKED_IN         = "LEAKED_IN"
    REGISTERED_BY     = "REGISTERED_BY"
    PART_OF           = "PART_OF"


# ── Unique Key property for each node label ──────────────────────────────────
NODE_KEY_PROPERTY = {
    NodeLabel.IP_ADDRESS:    "address",
    NodeLabel.DOMAIN:        "fqdn",
    NodeLabel.EMAIL:         "address",
    NodeLabel.PERSON:        "name",
    NodeLabel.ORGANIZATION:  "name",
    NodeLabel.THREAT_ACTOR:  "name",
    NodeLabel.C2_SERVER:     "address",
    NodeLabel.VULNERABILITY: "cve_id",
    NodeLabel.MALWARE:       "name",
    NodeLabel.FILE_HASH:     "hash_value",
    NodeLabel.ASN:           "asn_number",
    NodeLabel.GEOLOCATION:   "name",
    NodeLabel.URL:           "url",
    NodeLabel.PORT:          "port_number",
    NodeLabel.CERTIFICATE:   "fingerprint",
    NodeLabel.DATA_BREACH:   "breach_id",
    NodeLabel.CREDENTIAL:    "username",
}


# ── Cypher: Constraint creation queries (run once on DB setup) ───────────────
CONSTRAINT_QUERIES = [
    "CREATE CONSTRAINT ip_unique IF NOT EXISTS FOR (n:IPAddress) REQUIRE n.address IS UNIQUE",
    "CREATE CONSTRAINT domain_unique IF NOT EXISTS FOR (n:Domain) REQUIRE n.fqdn IS UNIQUE",
    "CREATE CONSTRAINT email_unique IF NOT EXISTS FOR (n:Email) REQUIRE n.address IS UNIQUE",
    "CREATE CONSTRAINT person_unique IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT org_unique IF NOT EXISTS FOR (n:Organization) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT ta_unique IF NOT EXISTS FOR (n:ThreatActor) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT c2_unique IF NOT EXISTS FOR (n:C2Server) REQUIRE n.address IS UNIQUE",
    "CREATE CONSTRAINT vuln_unique IF NOT EXISTS FOR (n:Vulnerability) REQUIRE n.cve_id IS UNIQUE",
    "CREATE CONSTRAINT malware_unique IF NOT EXISTS FOR (n:Malware) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT hash_unique IF NOT EXISTS FOR (n:FileHash) REQUIRE n.hash_value IS UNIQUE",
    "CREATE CONSTRAINT breach_unique IF NOT EXISTS FOR (n:DataBreach) REQUIRE n.breach_id IS UNIQUE",
]
