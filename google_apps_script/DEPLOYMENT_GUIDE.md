# 🚀 Deploy Bravo LT Candidate Intake to Your Team (Option 1)

This deployment runs **100% inside your Bravo LT Google Workspace**. 
Your colleagues don't need to install anything. They just bookmark a single link in Chrome.

---

### Step 1: Open Google Apps Script
1. Go to [script.google.com](https://script.google.com) while signed into your `@bravolt.com` account.
2. Click **+ New Project** in the top left.
3. Name the project: **`Bravo LT Candidate Intake`**.

---

### Step 2: Add `Code.gs`
1. You will see an open file named `Code.gs`.
2. Delete whatever template code is inside it.
3. Open [`Code.gs`](file:///Users/billosborn/.gemini/antigravity/scratch/candidate-intake-assistant/google_apps_script/Code.gs) from this folder, copy all contents, and paste it into `Code.gs`.

---

### Step 3: Add `Index.html`
1. In the left sidebar of Google Apps Script, click the **+** (plus icon) next to **Files**.
2. Select **HTML**.
3. Name the file: **`Index`** (Google will automatically name it `Index.html`).
4. Delete any template HTML inside it.
5. Open [`Index.html`](file:///Users/billosborn/.gemini/antigravity/scratch/candidate-intake-assistant/google_apps_script/Index.html) from this folder, copy all contents, and paste it into `Index.html`.
6. Click the **Save** disk icon (or press `Cmd + S`).

---

### Step 4: Deploy for Your Team
1. In the top right corner, click the blue **Deploy** button > **New deployment**.
2. Click the gear icon next to "Select type" and choose **Web app**.
3. Set the fields:
   * **Description:** `Candidate Intake Assistant`
   * **Execute as:** `Me (your email)` *(Recommended: this ensures folders are created with your Drive permissions even if a recruiter doesn't have admin access)*
   * **Who has access:** `Anyone within Bravo LT` (or `Anyone with Google account`)
4. Click **Deploy**.
5. Google will ask you to **Authorize access**:
   * Click **Review permissions**.
   * Choose your Bravo LT Google account.
   * If you see *"Google hasn't verified this app"*, click **Advanced** > **Go to Bravo LT Candidate Intake (unsafe)** > **Allow**.
6. Copy the **Web app URL** (it will look like `https://script.google.com/a/macros/bravolt.com/s/.../exec`).

---

### Step 5: Share with Your Colleagues!
* Send that link via Slack/Teams or email to your recruiters and delivery team.
* Tell them to bookmark it as **"Candidate Intake"**.
* Every recruiter who opens the link can immediately:
  1. Drag-and-drop or paste their Bravotizer JSON.
  2. Paste Gemini screening notes.
  3. Click **"⚡ Automatically Create Folder & Brief in Google Drive"** (runs natively with zero 401 errors!).
  4. Click **"🚀 Open Pre-Filled Contact in Salesforce"** to create the contact in 2 seconds.
