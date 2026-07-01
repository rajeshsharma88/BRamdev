function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.openById('1fZ3qY94NUo0E0ugNWSiq2EfkLoZzt0lz4xBDQWcZoJ8');
    const sheet = ss.getSheets()[0];

    // Add header row if empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['Timestamp', 'Name', 'Phone', 'City', 'Age', 'Product', 'Price', 'ID']);
    }

    sheet.appendRow([
      data.timestamp || new Date().toLocaleString('hi-IN', { timeZone: 'Asia/Kolkata' }),
      data.name,
      data.phone,
      data.city,
      data.age,
      data.product || 'Aarogya Champ',
      data.price || '₹399',
      data.id || Date.now()
    ]);

    return ContentService.createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet() {
  return ContentService.createTextOutput('Alive').setMimeType(ContentService.MimeType.TEXT);
}
