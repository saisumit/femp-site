// Google Ads measurement for femp.ai (account 854-186-9007). Loaded on every page after the gtag.js library.
// Why we measure what we measure: ecom-secretary docs/MARKETING_LEARNINGS.md ("Sign-up tracking").
window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
gtag("js", new Date());
gtag("config", "AW-18590404467", { allow_enhanced_conversions: true });

(() => {
  const SIGNUP = "AW-18590404467/fiaxCJjtib4dEPOezKBF", WHATSAPP = "AW-18590404467/D12VCJvtib4dEPOezKBF";
  const KEY = "femp-ad", from = (new URLSearchParams(location.search).get("from") || "").split(".")[0];
  // An ad lands with ?from=g-… on a plugin page; remember it for this visit so the wishlist form records which ad
  // brought the sign-up (the form's own ?from= says which button was pressed, e.g. "g-sales.jobs-hero").
  let ad = "";
  try {
    if (/^g-/.test(from)) sessionStorage.setItem(KEY, from);
    ad = sessionStorage.getItem(KEY) || "";
  } catch (blocked) { ad = /^g-/.test(from) ? from : ""; }
  if (ad) {
    document.addEventListener("DOMContentLoaded", () => {
      document.querySelectorAll('a[href*="/waitlist/"]').forEach(a => {
        const u = new URL(a.href, location.href), src = u.searchParams.get("from");
        if (src && !src.startsWith("g-")) u.searchParams.set("from", ad + "." + src);
        else if (!src) u.searchParams.set("from", ad);
        a.href = u.pathname + u.search + u.hash;
      });
    });
  }
  // The main conversion ("interested") is any of: opening the wishlist page, tapping "Say hi on WhatsApp", or a saved
  // sign-up. It counts once per ad click, so one person doing all three is still one conversion.
  if (location.pathname.startsWith("/waitlist/")) gtag("event", "conversion", { send_to: SIGNUP });
  // WhatsApp taps also fire their own action, so Google Ads can show how many interested people chose WhatsApp.
  document.addEventListener("click", e => {
    if (e.target.closest && e.target.closest('a[href*="wa.me/"]')) {
      gtag("event", "conversion", { send_to: SIGNUP, transport_type: "beacon" });
      gtag("event", "conversion", { send_to: WHATSAPP, transport_type: "beacon" });
    }
  }, true);
  // Called by the wishlist form once the sign-up is saved. Email and phone go to Google hashed (enhanced conversions).
  window.fempAds = {
    signup(email, phone) {
      gtag("set", "user_data", { email, phone_number: phone });
      gtag("event", "conversion", { send_to: SIGNUP });
    },
  };
})();
