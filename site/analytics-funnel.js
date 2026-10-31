/**
 * Cube Drop booking funnel events (homepage). Requires consent.js (cdTrack).
 */
(function () {
  function track(event, params) {
    if (typeof window.cdTrack === "function") window.cdTrack(event, params || {});
  }

  var lastStep = "";
  var lastWeeks = null;

  window.cdFunnel = {
    track: track,
    postcodeResult: function (area) {
      if (!area || !area.state) return;
      if (area.state === "checking") return;
      track("postcode_check", {
        result: area.state,
        in_service_area: area.state === "yes" ? "yes" : "no",
        area_name: area.name || "",
        postcode: area.postcode || "",
      });
      if (area.state === "yes") track("booking_step", { step: "postcode_ok", step_index: 1 });
    },
    weeksChanged: function (weeks, totalGbp) {
      if (lastWeeks === weeks) return;
      lastWeeks = weeks;
      track("pricing_update", {
        hire_weeks: weeks,
        value: totalGbp,
        currency: "GBP",
      });
    },
    deliverySelected: function (isoDate, weeks) {
      track("select_delivery_date", {
        delivery_date: isoDate,
        hire_weeks: weeks,
      });
      track("booking_step", { step: "delivery_date", step_index: 3 });
    },
    bookingStep: function (step, index) {
      var key = step + ":" + index;
      if (lastStep === key) return;
      lastStep = key;
      track("booking_step", { step: step, step_index: index });
    },
    formAttempt: function (formName) {
      track("form_submit", { form_name: formName, outcome: "attempt" });
    },
    formSuccess: function (formName, extra) {
      track("form_submit", { form_name: formName, outcome: "success" });
      if (formName === "reserve") {
        track("generate_lead", Object.assign({ form: "reserve", currency: "GBP" }, extra || {}));
      } else if (formName === "cancellation_list") {
        track("generate_lead", { form: "cancellation_list" });
      } else if (formName === "waitlist") {
        track("join_waitlist", { form: "waitlist" });
      }
    },
    navClick: function (label, href) {
      track("navigation_click", { link_text: label, link_url: href || "" });
    },
    contactClick: function (type, value, location) {
      track("contact_click", {
        contact_type: type,
        contact_value: value,
        contact_location: location,
      });
    },
    ctaClick: function (name, location) {
      track("cta_click", { cta_name: name, cta_location: location });
    },
  };

  document.addEventListener("click", function (event) {
    var el = event.target.closest("a[href^='tel:'], a[href^='mailto:']");
    if (!el) return;
    var href = el.getAttribute("href") || "";
    var loc = el.closest("header, .hero, footer, .close") ? "header" : "body";
    if (href.indexOf("tel:") === 0) {
      window.cdFunnel.contactClick("phone", href.replace("tel:", ""), loc);
    } else if (href.indexOf("mailto:") === 0) {
      window.cdFunnel.contactClick("email", href.replace("mailto:", ""), loc);
    }
  });

  document.querySelectorAll(".nav-links a, .brand").forEach(function (link) {
    link.addEventListener("click", function () {
      window.cdFunnel.navClick(link.textContent.trim(), link.getAttribute("href") || "");
    });
  });
})();
