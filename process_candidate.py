#!/usr/bin/env python3
"""
Candidate Intake Assistant - Bravo LT CLI
Parses Bravotizer JSON and generates:
1. Bravo LT formatted Title headline
2. Drive folder name: 'first last | skill | skill | skill | Country'
3. Drive folder path recommendations
4. Salesforce Lightning pre-filled Contact URL
"""

import json
import re
import sys
import urllib.parse
from pathlib import Path

KNOWN_DRIVE_FOLDERS = [
    "Project Manager - Healthcare (Non-IT)",
    "Software Developer",
    "UX Designer",
    "Bissell | Utility Team | Project Resumes",
    "Supplier Performance Analyst",
    "Electronic Engineers",
    "CX/DX",
    "Azure Engineer",
    "Data Engineer",
    "Delivery Manager"
]

def find_email(data: dict) -> str:
    contact = data.get("contact") or {}
    contact_info = data.get("contact_info") or {}
    unknown_contact = (data.get("unknown") or {}).get("contact_info") or {}
    candidates = [
        contact.get("email"),
        contact_info.get("email"),
        unknown_contact.get("email"),
        (data.get("unknown") or {}).get("email"),
        data.get("email")
    ]
    for c in candidates:
        if c and isinstance(c, str) and "@" in c:
            return c.strip()
    raw = json.dumps(data)
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw)
    if match:
        return match.group(0)
    return ""

def find_phone(data: dict) -> tuple:
    """Finds (phone, mobile). Uses any phone number listed for phone."""
    contact = data.get("contact") or {}
    contact_info = data.get("contact_info") or {}
    unknown_contact = (data.get("unknown") or {}).get("contact_info") or {}

    phone_val = ""
    mobile_val = ""

    # Check mobile specifically
    for c in [contact.get("mobile"), contact_info.get("mobile"), unknown_contact.get("mobile"), data.get("mobile")]:
        if c and isinstance(c, str) and any(ch.isdigit() for ch in c):
            mobile_val = c.strip()
            break

    # Check phone specifically
    for c in [contact.get("phone"), contact.get("phone_number"), contact.get("cell"), contact.get("telephone"),
              contact_info.get("phone"), unknown_contact.get("phone"), data.get("phone")]:
        if c and isinstance(c, str) and any(ch.isdigit() for ch in c):
            phone_val = c.strip()
            break

    # Fallback to any phone found
    if not phone_val and mobile_val:
        phone_val = mobile_val
    elif not mobile_val and phone_val:
        mobile_val = phone_val
    elif not phone_val and not mobile_val:
        raw = json.dumps(data)
        match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw)
        if match:
            phone_val = match.group(0)
            mobile_val = phone_val

    return phone_val, mobile_val

def find_linkedin(data: dict) -> str:
    contact = data.get("contact") or {}
    contact_info = data.get("contact_info") or {}
    unknown_contact = (data.get("unknown") or {}).get("contact_info") or {}
    candidates = [
        contact.get("linkedin"),
        contact_info.get("linkedin"),
        unknown_contact.get("linkedin"),
        data.get("linkedin")
    ]
    for c in candidates:
        if c and isinstance(c, str) and "linkedin" in c.lower():
            link = c.strip()
            return f"https://{link}" if not link.startswith("http") else link
    raw = json.dumps(data)
    match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', raw)
    if match:
        link = match.group(0)
        return f"https://{link}" if not link.startswith("http") else link
    return ""

def find_address(data: dict) -> str:
    contact = data.get("contact") or {}
    contact_info = data.get("contact_info") or {}
    unknown_contact = (data.get("unknown") or {}).get("contact_info") or {}
    candidates = [
        contact.get("address"),
        contact.get("location"),
        contact_info.get("address"),
        unknown_contact.get("address"),
        data.get("address"),
        data.get("location")
    ]
    for c in candidates:
        if c and isinstance(c, str) and len(c.strip()) > 3:
            return c.strip()
    return ""

def extract_state(address: str) -> str:
    if not address:
        return ""
    match = re.search(r'\b([A-Z]{2})\b\s+\d{5}', address)
    if match:
        return match.group(1)
    match = re.search(r',\s*([A-Za-z\s]+)\s+\d{5}', address)
    if match:
        name = match.group(1).strip()
        state_map = {"Michigan": "MI", "Ohio": "OH", "Illinois": "IL", "New York": "NY", "Texas": "TX", "California": "CA"}
        return state_map.get(name, name[:2].upper())
    return ""

def extract_country(address: str, work_auth: str = "USC") -> str:
    if work_auth in ["USC", "Green Card", "H-1B", "TN"]:
        return "US"
    if address:
        if re.search(r'\b[A-Z]{2}\b\s+\d{5}', address) or "Grand Rapids" in address or "USA" in address:
            return "US"
        if "Canada" in address:
            return "CA"
        if "India" in address:
            return "IN"
    return "US"

def get_clean_role_title(data: dict) -> str:
    candidates = []
    if data.get("suggested_level"): candidates.append(data["suggested_level"])
    if data.get("role"): candidates.append(data["role"])
    for sr in data.get("suggested_roles", []):
        if isinstance(sr, dict) and sr.get("role"):
            candidates.append(sr["role"])
    for pe in data.get("professional_experience", [])[:2]:
        if isinstance(pe, dict) and pe.get("title"):
            candidates.append(pe["title"])

    for c in candidates:
        if not c: continue
        s = str(c).strip()
        if re.match(r'^L\d+$', s, re.IGNORECASE): continue
        if s.lower() in ["agnostic", "general", "unknown", "n/a", "none"]: continue
        return s
    return "Candidate"

def extract_top_skills(data: dict) -> list:
    skills = []

    # 1. Role or Primary Discipline (skip L1-L8 / agnostic, extract clean title or acronym)
    role_str = get_clean_role_title(data)
    if role_str and role_str != "Candidate":
        match_acronym = re.search(r'\(([A-Z]{2,6})\)', role_str)
        if match_acronym:
            skills.append(match_acronym.group(1))
        elif "scrum master" in role_str.lower():
            skills.append("Scrum Master")
        elif "data engineer" in role_str.lower():
            skills.append("Data Engineer")
        elif "azure" in role_str.lower():
            skills.append("Azure Engineer")
        elif "developer" in role_str.lower():
            skills.append("Software Developer")
        else:
            skills.append(re.split(r'[-/|]', role_str)[0].strip()[:20])

    # 2. Key Certifications
    certs = data.get("certifications", [])
    for c in certs:
        c_name = c.get("name", "") if isinstance(c, dict) else str(c)
        for cert_tag in ["PMP", "SAFe", "CSM", "RTE", "AWS", "Azure", "GCP", "Six Sigma", "CISSP", "ITIL"]:
            if cert_tag in c_name and not any(cert_tag.lower() == s.lower() for s in skills):
                skills.append("LSS" if cert_tag == "Six Sigma" else cert_tag)
                break
        if len(skills) >= 4:
            break

    # 3. Technical Tools
    tools_str = data.get("technical_experience", {}).get("primary_tools", "")
    if tools_str:
        for tool in [t.strip() for t in tools_str.split(",")]:
            cleaned = tool.split("(")[0].strip()
            if cleaned and not any(cleaned.lower() in s.lower() for s in skills):
                skills.append(cleaned)
            if len(skills) >= 4:
                break

    # 4. Core Competencies fallback
    comps = data.get("unknown", {}).get("core_competencies", [])
    for comp in comps:
        c_str = str(comp).strip()
        acronym = re.search(r'\(([A-Z]{2,6})\)', c_str)
        tag = acronym.group(1) if acronym else re.split(r'[-/|]', c_str)[0].strip()
        if tag and not any(tag.lower() == s.lower() for s in skills):
            skills.append(tag[:18])

    selected = []
    for s in skills:
        if s not in selected:
            selected.append(s)
        if len(selected) == 3:
            break

    while len(selected) < 3:
        selected.append("General")

    return selected[:3]

def format_drive_folder_name(data: dict, work_auth: str = "USC") -> str:
    name = data.get("name", "").strip()
    skills = extract_top_skills(data)
    addr = find_address(data)
    country = extract_country(addr, work_auth)
    return f"{name} | {' | '.join(skills)} | {country}"

def format_bravo_title(data: dict, work_auth: str = "USC") -> str:
    name = data.get("name", "").strip()
    parts = [name]
    
    certs = data.get("certifications", [])
    cert_tags = []
    for c in certs:
        c_name = c.get("name", "") if isinstance(c, dict) else str(c)
        if "PMP" in c_name and "PMP" not in cert_tags:
            cert_tags.append("PMP")
        elif "SAFe" in c_name and "SAFe" not in cert_tags:
            cert_tags.append("SAFe")
        elif ("CSM" in c_name or "Scrum Master" in c_name) and "CSM" not in cert_tags:
            cert_tags.append("CSM")
        elif "Six Sigma" in c_name and "LSS" not in cert_tags:
            cert_tags.append("LSS")
    
    role = get_clean_role_title(data)
    if role and role != "Candidate":
        parts.append(role)
        
    parts.extend(cert_tags[:2])
    
    addr = find_address(data)
    state = extract_state(addr)
    if state:
        parts.append(state)
        
    if work_auth:
        parts.append(work_auth)
        
    return " | ".join(parts)

def recommend_drive_folder(data: dict) -> str:
    texts = []
    if data.get("role"): texts.append(data["role"])
    if data.get("suggested_level"): texts.append(data["suggested_level"])
    for sr in data.get("suggested_roles", []):
        if isinstance(sr, dict) and sr.get("role"):
            texts.append(sr["role"])
    for pe in data.get("professional_experience", [])[:3]:
        if isinstance(pe, dict) and pe.get("title"):
            texts.append(pe["title"])

    combined = " ".join(texts).lower()

    if any(k in combined for k in ["scrum", "agile", "delivery", "release train", "rte", "program manager"]):
        return "Delivery Manager"
    if any(k in combined for k in ["data", "analytics", "bi "]):
        return "Data Engineer"
    if any(k in combined for k in ["azure", "aws", "cloud", "devops"]):
        return "Azure Engineer"
    if any(k in combined for k in ["ux", "ui", "design"]):
        return "UX Designer"
    if any(k in combined for k in ["healthcare", "supplier"]):
        return "Project Manager - Healthcare (Non-IT)"
    if any(k in combined for k in ["developer", "software", "full stack"]):
        return "Software Developer"
        
    return "Software Developer"

def build_salesforce_url(
    data: dict,
    title: str,
    work_auth: str = "USC",
    drive_folder_url: str = "",
    key_notes: str = "",
    sf_domain: str = "bravolt.lightning.force.com"
) -> str:
    name = data.get("name", "").strip()
    name_parts = name.split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    email = find_email(data)
    phone, mobile = find_phone(data)
    linkedin = find_linkedin(data)
        
    params = [
        f"FirstName={urllib.parse.quote(first_name)}",
        f"LastName={urllib.parse.quote(last_name)}",
        f"Title={urllib.parse.quote(title)}",
        f"Email={urllib.parse.quote(email)}",
        f"Phone={urllib.parse.quote(phone)}",
        f"MobilePhone={urllib.parse.quote(mobile)}",
        f"Contact_Type__c={urllib.parse.quote('Candidate')}",
        f"Work_Authorization__c={urllib.parse.quote(work_auth)}",
    ]
    
    if linkedin:
        params.append(f"LinkedIn_Profile__c={urllib.parse.quote(linkedin)}")
    if drive_folder_url:
        params.append(f"Resume_URL__c={urllib.parse.quote(drive_folder_url)}")
    if key_notes:
        params.append(f"Key_Notes__c={urllib.parse.quote(key_notes)}")
        
    query_str = ",".join(params)
    return f"https://{sf_domain}/lightning/o/Contact/new?defaultFieldValues={query_str}"

def process_file(json_path: str, notes_path: str = None, work_auth: str = "USC"):
    path = Path(json_path)
    if not path.exists():
        print(f"Error: File {json_path} not found.")
        sys.exit(1)
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    notes = ""
    if notes_path and Path(notes_path).exists():
        with open(notes_path, "r", encoding="utf-8") as f:
            notes = f.read()
            
    title = format_bravo_title(data, work_auth)
    recommended_folder = recommend_drive_folder(data)
    folder_name = format_drive_folder_name(data, work_auth)
    name = data.get("name", "")
    email = find_email(data)
    phone, mobile = find_phone(data)
    linkedin = find_linkedin(data)
    
    print("\n" + "=" * 65)
    print(f"  BRAVO LT CANDIDATE INTAKE: {name.upper()}")
    print("=" * 65)
    print(f"\n[1] Suggested Salesforce Title Headline:\n    {title}")
    print(f"\n[2] Google Drive Target Path:")
    print(f"    Parent: Candidates > Technology > {recommended_folder}")
    print(f"    Folder: {folder_name}")
    print(f"\n[3] Candidate Contact Info:")
    print(f"    Email:    {email if email else 'N/A'}")
    print(f"    Phone:    {phone if phone else 'N/A'}")
    print(f"    Mobile:   {mobile if mobile else 'N/A'}")
    print(f"    LinkedIn: {linkedin if linkedin else 'N/A'}")
    
    sf_url = build_salesforce_url(data, title, work_auth, key_notes=notes)
    print(f"\n[4] Salesforce Lightning Pre-Fill URL:")
    print(f"    {sf_url}")
    print("\n" + "=" * 65)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_candidate.py <path_to_bravotizer_json> [notes_file] [work_auth]")
    else:
        notes_file = sys.argv[2] if len(sys.argv) > 2 else None
        auth = sys.argv[3] if len(sys.argv) > 3 else "USC"
        process_file(sys.argv[1], notes_file, auth)
