// Femp waitlist → Google Sheet. Lives in the sheet's Apps Script (Extensions → Apps Script) and is
// deployed as a web app (Execute as: me, Who has access: Anyone). The femp.ai waitlist form posts
// here first, as text/plain so the browser sends no CORS preflight; the server copy is best-effort.
// After editing: Deploy → Manage deployments → edit → New version (the /exec URL stays the same).
/** @OnlyCurrentDoc  (asks for access to this sheet only, not all of Drive) */
const NOTIFY = "saisumit@femp.ai";
const HEADERS = ["Joined", "Email", "Phone", "Store", "Platforms", "From", "Updated", "Wants"];
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function setup() {
  const book = SpreadsheetApp.getActiveSpreadsheet();
  book.rename("Femp waitlist");
  const sheet = book.getSheets()[0];
  sheet.setName("Signups");
  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight("bold");
  sheet.setFrozenRows(1);
  MailApp.getRemainingDailyQuota(); // asks for the email permission now, not on the first signup
}

function doGet() {
  return reply({ ok: true });
}

function doPost(e) {
  let body;
  try {
    body = JSON.parse((e && e.postData && e.postData.contents) || "{}");
  } catch (err) {
    return reply({ ok: false, error: "Something went wrong. Try again in a minute." });
  }
  // The hidden "leave empty" field is a bot trap, but browser autofill can fill it for real people,
  // so a filled one is still saved (flagged in From) and only skips the email.
  const flagged = Boolean(body.company);
  const email = clip(body.email, 254).toLowerCase();
  const phone = clip(body.phone, 32);
  if (!EMAIL.test(email)) return reply({ ok: false, error: "Enter your email address." });
  if (phone.replace(/\D/g, "").length < 6) return reply({ ok: false, error: "Enter your WhatsApp number with the country code." });
  if (body.consent !== true) return reply({ ok: false, error: "Tick the box so we can contact you about early access." });
  const store = clip(body.store, 300);
  const platforms = (Array.isArray(body.platforms) ? body.platforms : []).slice(0, 12).map((p) => clip(p, 30)).join(", ");
  const wants = (Array.isArray(body.wants) ? body.wants : []).slice(0, 8).map((w) => clip(w, 120)).join(", ");
  const source = (flagged ? "flagged: hidden field filled · " : "") + clip(body.source, 100);

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  let added = false;
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getRange(1, 8).getValue() !== "Wants") sheet.getRange(1, 8).setValue("Wants").setFontWeight("bold");
    const now = new Date();
    const last = sheet.getLastRow();
    const emails = last > 1 ? sheet.getRange(2, 2, last - 1, 1).getValues().map((r) => String(r[0]).toLowerCase()) : [];
    const at = emails.indexOf(email);
    if (at >= 0) {
      sheet.getRange(at + 2, 3, 1, 6).setValues([[cell(phone), cell(store), cell(platforms), cell(source), now, cell(wants)]]);
    } else {
      sheet.appendRow([now, cell(email), cell(phone), cell(store), cell(platforms), cell(source), now, cell(wants)]);
      added = true;
    }
  } finally {
    lock.releaseLock();
  }
  if (added && !flagged) {
    try {
      MailApp.sendEmail(NOTIFY, `Femp waitlist: ${email}`,
        `Email: ${email}\nPhone: ${phone}\nWants: ${wants || "-"}\nStore: ${store || "-"}\nPlatforms: ${platforms || "-"}\nFrom: ${source || "-"}\n\n${SpreadsheetApp.getActiveSpreadsheet().getUrl()}`);
    } catch (err) {
      console.error(err); // the signup is saved; a failed email shouldn't fail it
    }
  }
  return reply({ ok: true });
}

function clip(value, max) {
  return String(value == null ? "" : value).trim().slice(0, max);
}

// Values starting with = + - @ would be read as formulas; a leading ' keeps them as text.
function cell(value) {
  return /^[=+\-@]/.test(value) ? "'" + value : value;
}

function reply(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}
