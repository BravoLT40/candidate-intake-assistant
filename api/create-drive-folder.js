export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  const { scriptUrl, category, folderName, candidateName, notesContent } = req.body || {};

  if (!scriptUrl || !scriptUrl.startsWith('http')) {
    return res.status(400).json({
      success: false,
      error: 'Google Apps Script Web App URL is not configured. Please paste your script URL in settings.'
    });
  }

  try {
    const response = await fetch(scriptUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, folderName, candidateName, notesContent }),
      redirect: 'follow'
    });

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Drive Bridge Serverless Error: ' + error.message
    });
  }
}
