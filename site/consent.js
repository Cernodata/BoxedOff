(function () {
  // Add the IDs here when the accounts exist. Nothing loads, and no banner shows, while both are empty.
  var GA_ID = ""; // Google Analytics 4, e.g. "G-XXXXXXXXXX"
  var META_PIXEL_ID = ""; // Meta Pixel, e.g. "123456789012345"

  var KEY = "cd-consent";
  var VERSION = 1;
  var MAX_AGE_DAYS = 365;
  var hasAnalytics = Boolean(GA_ID);
  var hasMarketing = Boolean(META_PIXEL_ID);
  var loaded = { analytics: false, marketing: false };

  function read() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || "null");
      if (!saved || saved.v !== VERSION) return null;
      if (Date.now() - saved.ts > MAX_AGE_DAYS * 864e5) return null;
      return saved;
    } catch (err) {
      return null;
    }
  }

  function write(choice) {
    var saved = { v: VERSION, ts: Date.now(), analytics: Boolean(choice.analytics), marketing: Boolean(choice.marketing) };
    try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (err) {}
    return saved;
  }

  function loadScript(src) {
    var s = document.createElement("script");
    s.async = true;
    s.src = src;
    document.head.appendChild(s);
  }

  function loadAnalytics(choice) {
    if (!hasAnalytics || loaded.analytics) return;
    loaded.analytics = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "granted",
      ad_storage: choice.marketing ? "granted" : "denied",
      ad_user_data: choice.marketing ? "granted" : "denied",
      ad_personalization: "denied"
    });
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
    loadScript("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID));
  }

  function loadMarketing() {
    if (!hasMarketing || loaded.marketing) return;
    loaded.marketing = true;
    var fbq = window.fbq = function () {
      fbq.callMethod ? fbq.callMethod.apply(fbq, arguments) : fbq.queue.push(arguments);
    };
    if (!window._fbq) window._fbq = fbq;
    fbq.push = fbq;
    fbq.loaded = true;
    fbq.version = "2.0";
    fbq.queue = [];
    fbq("init", META_PIXEL_ID);
    fbq("track", "PageView");
    loadScript("https://connect.facebook.net/en_US/fbevents.js");
  }

  function apply(choice) {
    if (loaded.analytics) {
      window.gtag("consent", "update", {
        ad_storage: choice.marketing ? "granted" : "denied",
        ad_user_data: choice.marketing ? "granted" : "denied"
      });
    }
    if (choice.analytics) loadAnalytics(choice);
    if (choice.marketing) loadMarketing();
  }

  function clearTrackingCookies() {
    var host = location.hostname;
    var domains = ["", host, "." + host, "." + host.split(".").slice(-3).join("."), "." + host.split(".").slice(-2).join(".")];
    document.cookie.split(";").forEach(function (pair) {
      var name = pair.split("=")[0].trim();
      if (!/^(_ga|_gid|_gat|_fbp|_fbc)/.test(name)) return;
      domains.forEach(function (domain) {
        document.cookie = name + "=; Max-Age=0; path=/" + (domain ? "; domain=" + domain : "");
      });
    });
  }

  // Lets the page report a booking request as a conversion, only where consent allows.
  window.cdTrack = function (event, params) {
    var saved = read();
    if (!saved) return;
    if (saved.analytics && typeof window.gtag === "function") window.gtag("event", event, params || {});
    if (saved.marketing && typeof window.fbq === "function") {
      if (event === "generate_lead") window.fbq("track", "Lead");
      else window.fbq("trackCustom", event);
    }
  };

  var banner;

  function row(id, title, detail, checked) {
    return '<label class="cc-row" for="' + id + '"><input type="checkbox" id="' + id + '"' + (checked ? " checked" : "") + '>' +
      '<span><strong>' + title + '</strong>' + detail + '</span></label>';
  }

  function build(saved) {
    banner = document.createElement("section");
    banner.className = "cc";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-label", "Cookie choices");
    var choice = saved || { analytics: false, marketing: false };
    var uses = [hasAnalytics ? "see how the site is used" : "", hasMarketing ? "measure our adverts" : ""].filter(Boolean).join(" and ");
    banner.innerHTML =
      '<div class="cc-inner">' +
        '<p class="cc-title">Cookies, briefly.</p>' +
        '<p class="cc-text">Can we use cookies to ' + uses + '? Nothing is set unless you say yes. ' +
          '<a href="cookies.html">Cookie policy</a>.</p>' +
        '<div class="cc-choose" hidden>' +
          (hasAnalytics ? row("cc-analytics", "Analytics", " Google Analytics. Which pages are read, so we can improve them.", choice.analytics) : "") +
          (hasMarketing ? row("cc-marketing", "Marketing", " Meta Pixel. Whether our Facebook and Instagram adverts work.", choice.marketing) : "") +
        '</div>' +
        '<div class="cc-actions">' +
          '<button type="button" class="cc-btn" data-cc="reject">Reject all</button>' +
          '<button type="button" class="cc-btn" data-cc="accept">Accept all</button>' +
          '<button type="button" class="cc-link" data-cc="choose">Choose</button>' +
          '<button type="button" class="cc-btn" data-cc="save" hidden>Save choices</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(banner);
    banner.addEventListener("click", function (event) {
      var action = event.target.getAttribute("data-cc");
      if (!action) return;
      if (action === "choose") {
        banner.querySelector(".cc-choose").hidden = false;
        banner.querySelector('[data-cc="save"]').hidden = false;
        event.target.hidden = true;
        var first = banner.querySelector(".cc-choose input");
        if (first) first.focus();
        return;
      }
      var next;
      if (action === "accept") next = { analytics: true, marketing: true };
      else if (action === "reject") next = { analytics: false, marketing: false };
      else {
        var a = banner.querySelector("#cc-analytics");
        var m = banner.querySelector("#cc-marketing");
        next = { analytics: Boolean(a && a.checked), marketing: Boolean(m && m.checked) };
      }
      decide(next);
    });
  }

  function decide(next) {
    var before = read();
    var saved = write(next);
    close();
    var withdrawn = before && ((before.analytics && !saved.analytics) || (before.marketing && !saved.marketing));
    if (withdrawn) {
      clearTrackingCookies();
      location.reload();
      return;
    }
    apply(saved);
  }

  function open() {
    close();
    build(read());
    document.body.classList.add("cc-open");
    var first = banner.querySelector("button");
    if (first) first.focus();
  }

  function close() {
    if (banner) banner.remove();
    banner = null;
    document.body.classList.remove("cc-open");
  }

  function init() {
    var settings = document.querySelectorAll("[data-cookie-settings]");
    if (!hasAnalytics && !hasMarketing) {
      settings.forEach(function (el) { el.hidden = true; });
      return;
    }
    settings.forEach(function (el) {
      el.hidden = false;
      el.addEventListener("click", open);
    });
    var saved = read();
    if (saved) apply(saved);
    else {
      build(null);
      document.body.classList.add("cc-open");
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
