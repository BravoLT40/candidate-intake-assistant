# Bravo LT - Candidate Intake Assistant

A rapid candidate onboarding tool for Bravo LT that bridges:
1. **Bravotizer JSON** (`https://rbt.bravolt.com/`)
2. **Google Drive** (`Candidates > Technology > [Folder]`)
3. **Salesforce Contact** (`Account: Recruits`, `Contact Type: Candidate`)

---

## Google Drive Folder Naming Convention

All candidate folders adhere to the exact format:
```text
first last | skill | skill | skill | Country
```

*Example (Jude Pagel):*
```text
Jude Pagel | Scrum Master | SAFe | Six Sigma | US
```

The app automatically selects the top 3 high-impact skills (from certifications, role discipline, and primary tools) and country code (`US`), and allows you to adjust any skill on the fly using interactive inputs.

---

## Automatic Google Drive Folder Creation

The assistant can create the folder directly in your Google Drive with a single click:

1. Click **"📁 Drive Auto-Create Setup"** in the top header.
2. Click **"📋 Copy Apps Script Code"**.
3. Open [script.google.com](https://script.google.com) while signed into your Bravo LT Google account, create a new project, and paste the code from [`drive_bridge.gs`](file:///Users/billosborn/.gemini/antigravity/scratch/candidate-intake-assistant/drive_bridge.gs).
4. Click **Deploy > New deployment > Web app** (Execute as: *Me*, Who has access: *Anyone*).
5. Paste your deployed Web App URL into the assistant.

Once configured, clicking **"⚡ Automatically Create Folder in Google Drive"** will:
- Locate the correct category folder under `Candidates > Technology` (e.g. `Delivery Manager`).
- Create the formatted folder: `first last | skill | skill | skill | Country`.
- Automatically save a Google Doc with your Gemini screening notes inside the folder.
- Retrieve the live folder URL and plug it straight into your Salesforce Contact creation link.

---

## How to Run

Launch the local web server:
```bash
python3 /Users/billosborn/.gemini/antigravity/scratch/candidate-intake-assistant/server.py
```
Open `http://localhost:8505` in your browser.

Or use the CLI:
```bash
python3 /Users/billosborn/.gemini/antigravity/scratch/candidate-intake-assistant/process_candidate.py \
  /Users/billosborn/Downloads/Jude_Pagel_Resume_Data_BravoLT.json
```
