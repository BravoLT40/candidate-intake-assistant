/**
 * Bravo LT - Candidate Intake Assistant
 * Hosted directly in Google Workspace via Google Apps Script
 */

function doGet(e) {
  var template = HtmlService.createTemplateFromFile('Index');
  return template.evaluate()
    .setTitle('Bravo LT - Candidate Intake Assistant')
    .setFaviconUrl('https://ssl.gstatic.com/docs/doclist/images/drive_2022q3_32dp.png')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Server-side function called directly from the web interface
 * via google.script.run (zero API tokens, zero 401 errors, zero CORS issues).
 */
function createDriveCandidateFolder(data) {
  try {
    var categoryName = data.category || "Delivery Manager";
    var folderName = data.folderName;
    var candidateName = data.candidateName || "Candidate";
    var notesContent = data.notesContent || "";

    if (!folderName) {
      throw new Error("Missing folderName parameter");
    }

    // 1. Locate the target Category folder under "Technology"
    var targetParent = null;

    // Look for Technology folder first
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

    // 3. Create formatted Google Doc for screening notes inside the folder
    var docUrl = "";
    if (notesContent && notesContent.trim().length > 0) {
      var docTitle = candidateName + " - Screening Brief";
      var existingDocs = candidateFolder.getFilesByName(docTitle);
      if (!existingDocs.hasNext()) {
        var doc = DocumentApp.create(docTitle);
        var body = doc.getBody();
        body.appendParagraph("Bravo LT Candidate Screening Brief").setHeading(DocumentApp.ParagraphHeading.HEADING1);
        body.appendParagraph("Candidate: " + candidateName);
        body.appendParagraph("Target Folder: " + folderName);
        body.appendParagraph("Date Processed: " + new Date().toLocaleDateString());
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

  } catch (error) {
    return {
      success: false,
      error: error.toString()
    };
  }
}
