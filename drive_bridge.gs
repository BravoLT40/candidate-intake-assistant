/**
 * Bravo LT - Google Drive Candidate Folder Auto-Creator
 * 
 * Works via BOTH:
 * 1. Background API (POST) - if deployed with "Who has access: Anyone"
 * 2. Browser Direct (GET)  - works even if Bravo LT restricts access to "Within Bravo LT"
 */

function createFolderLogic(categoryName, folderName, candidateName, notesContent) {
  categoryName = categoryName || "Delivery Manager";
  candidateName = candidateName || "Candidate";

  if (!folderName) {
    throw new Error("Missing folderName parameter");
  }

  // 1. Locate the target Category folder under "Technology"
  var targetParent = null;
  var techFolders = DriveApp.getFoldersByName("Technology");
  while (techFolders.hasNext()) {
    var tf = techFolders.next();
    var subFolders = tf.getFoldersByName(categoryName);
    if (subFolders.hasNext()) {
      targetParent = subFolders.next();
      break;
    }
  }

  // Fallback: search for category folder directly anywhere in Drive
  if (!targetParent) {
    var catFolders = DriveApp.getFoldersByName(categoryName);
    if (catFolders.hasNext()) {
      targetParent = catFolders.next();
    } else {
      techFolders = DriveApp.getFoldersByName("Technology");
      if (techFolders.hasNext()) {
        targetParent = techFolders.next().createFolder(categoryName);
      } else {
        targetParent = DriveApp.getRootFolder();
      }
    }
  }

  // 2. Check if candidate folder already exists
  var existingFolders = targetParent.getFoldersByName(folderName);
  var candidateFolder;
  if (existingFolders.hasNext()) {
    candidateFolder = existingFolders.next();
  } else {
    candidateFolder = targetParent.createFolder(folderName);
  }

  // 3. Create formatted Google Doc for screening notes if provided
  var docUrl = "";
  if (notesContent && notesContent.trim().length > 0) {
    var docTitle = candidateName + " - Screening Brief";
    var existingDocs = candidateFolder.getFilesByName(docTitle);
    if (!existingDocs.hasNext()) {
      var doc = DocumentApp.create(docTitle);
      var body = doc.getBody();
      body.appendParagraph("Bravo LT Candidate Screening Brief").setHeading(DocumentApp.ParagraphHeading.HEADING1);
      body.appendParagraph("Candidate: " + candidateName);
      body.appendParagraph("Folder: " + folderName);
      body.appendParagraph("Date: " + new Date().toLocaleDateString());
      body.appendHorizontalRule();
      body.appendParagraph(notesContent);
      doc.saveAndClose();

      var docFile = DriveApp.getFileById(doc.getId());
      docFile.moveTo(candidateFolder);
      docUrl = docFile.getUrl();
    } else {
      docUrl = existingDocs.next().getUrl();
    }
  }

  return {
    success: true,
    folderUrl: candidateFolder.getUrl(),
    folderId: candidateFolder.getId(),
    folderName: folderName,
    category: categoryName,
    docUrl: docUrl
  };
}

// 1. POST handler (used by server.py / API)
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var res = createFolderLogic(data.category, data.folderName, data.candidateName, data.notesContent);
    return ContentService.createTextOutput(JSON.stringify(res))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// 2. GET handler (used directly in browser with active Google login)
function doGet(e) {
  var p = e.parameter || {};
  if (p.action === "create" && p.folderName) {
    try {
      var res = createFolderLogic(p.category, p.folderName, p.candidateName, p.notesContent);
      
      // If requested as JSON redirect or simple HTML page
      var html = '<!DOCTYPE html><html><head><meta charset="utf-8">' +
        '<title>Folder Created</title>' +
        '<script>window.location.href = "' + res.folderUrl + '";</script>' +
        '</head><body style="font-family:sans-serif;text-align:center;padding:50px;">' +
        '<h2>✅ Folder Created in Google Drive!</h2>' +
        '<p><b>' + res.folderName + '</b></p>' +
        '<p><a href="' + res.folderUrl + '">Click here if not redirected automatically</a></p>' +
        '</body></html>';
        
      return HtmlService.createHtmlOutput(html);
    } catch (err) {
      return HtmlService.createHtmlOutput('<h2 style="color:red;">Error creating folder: ' + err.toString() + '</h2>');
    }
  }

  return ContentService.createTextOutput(JSON.stringify({
    status: "ok",
    message: "Bravo LT Drive Bridge is operational"
  })).setMimeType(ContentService.MimeType.JSON);
}
