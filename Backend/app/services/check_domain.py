

CREDIBLE_DOMAINS = [
    # --- TLD patterns (handle via partial checks in code) ---
    ".gov",          # covers cdc.gov, nih.gov, etc.
    ".edu",          # US educational institutions
    ".ac.",          # academic subdomains in some countries (e.g. .ac.uk)
    ".gov.",         # e.g. .gov.uk, .gov.sg
"mothership.sg",

    # --- International orgs and agencies ---
    "who.int",       # World Health Organization
    "un.org",        # United Nations
    "europa.eu",     # European Union websites
    "imf.org",       # International Monetary Fund
    "worldbank.org", # World Bank
    "oecd.org",      # Organisation for Economic Co-operation and Development
    
    # -- Singapore Government & TLD Patterns --
    ".gov.sg",        # covers moh.gov.sg, mom.gov.sg, etc.
    "gov.sg",         # top-level domain
    ".edu.sg",        # e.g., nus.edu.sg, ntu.edu.sg
    ".ac.sg",         # some academic subdomains
    
    # Specific ministries or agencies (optional if .gov.sg covers them)
    "moh.gov.sg",
    "mom.gov.sg",
    "mas.gov.sg",
    "mha.gov.sg",
    "nea.gov.sg",
    "ica.gov.sg",
    "singstat.gov.sg",
    "police.gov.sg",
    
    # Specific ministries or agencies (optional if .gov.sg covers them)
    "moh.gov.sg",
    "mom.gov.sg",
    "mas.gov.sg",
    "mha.gov.sg",
    "nea.gov.sg",
    "ica.gov.sg",
    "singstat.gov.sg",
    "police.gov.sg",

    # -- Singapore News Outlets --
    "straitstimes.com",
    "mothership.sg",
    "channelnewsasia.com",
    "todayonline.com",
    "zaobao.com.sg",
    "businesstimes.com.sg",

    # --- US government agencies (if you want them explicitly) ---
    "cdc.gov",       # Centers for Disease Control and Prevention
    "nih.gov",       # National Institutes of Health
    "fda.gov",       # Food and Drug Administration
    "epa.gov",       # Environmental Protection Agency
    "ftc.gov",       # Federal Trade Commission
    "consumer.ftc.gov", # sometimes separated
    "usa.gov",       # official US government portal

    # --- Major news outlets / media (English-speaking examples) ---
    "bbc.com",
    "bbc.co.uk",
    "reuters.com",
    "apnews.com",
    "theguardian.com",
    "nytimes.com",
    "washingtonpost.com",
    "cnn.com",
    "npr.org",        # US public radio
    "wsj.com",        # Wall Street Journal
    "bloomberg.com",
    "abcnews.go.com",
    "cbsnews.com",
    "nbcnews.com",
    "latimes.com",

    # --- Fact-checking / watchdog sites ---
    "snopes.com",
    "factcheck.org",
    "politifact.com",
    "fullfact.org",   # UK-based fact-check
    "truthout.org",   # independent, though check editorial stance

    # --- Popular tech/science journals or magazines (examples) ---
    "sciencedirect.com",
    "nature.com",
    "sciencemag.org",
    "nationalgeographic.com",
    "newscientist.com",

    # --- Security/antivirus references (for scam detection, e.g. scanning) ---
    "malwarebytes.com",
    "kaspersky.com",
    "mcafee.com",

    "snopes.com", "factcheck.org", "politifact.com", "reuters.com", "bbc.com",
    "apnews.com", "npr.org", "theguardian.com", "forbes.com", "bloomberg.com"

    # --- Additional TLD patterns or country-specific G/NGOs may follow ---
]

def is_credible(domain: str) -> int:
    domain = domain.lower()
    # Remove "www."
    if domain.startswith("www."):
        domain = domain[4:]
    
    for pattern in CREDIBLE_DOMAINS:
        # if the pattern has a leading dot, e.g. ".gov", we do endswith
        if pattern.startswith("."):
            if domain.endswith(pattern):
                return 1
        else:
            # Instead of exact match, also do endswith for patterns like "straitstimes.com"
            if domain.endswith(pattern):
                return 1
    return -1
