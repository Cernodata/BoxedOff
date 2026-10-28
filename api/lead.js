const KINDS = {
  reserve: { label: "Booking request", need: ["name", "phone", "postcode", "deliver", "weeks"] },
  cancel: { label: "Cancellation list", need: ["name", "phone", "date", "weeks"] },
  waitlist: { label: "Out-of-area waitlist", need: ["email"] }
};
const FIELDS = ["name", "phone", "email", "postcode", "area", "deliver", "collect", "date", "weeks", "total"];
const LABELS = {
  name: "Name", phone: "Phone", email: "Email", postcode: "Postcode", area: "Area",
  deliver: "Deliver", collect: "Collect", date: "Day needed", weeks: "Weeks", total: "Guide total"
};

function clean(value) {
  return String(value == null ? "" : value).replace(/[\r\n\t]+/g, " ").trim().slice(0, 200);
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false });
  }

  let body = req.body || {};
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ ok: false }); }
  }

  // Bots fill the hidden "company" field; people never see it.
  if (clean(body.company)) return res.status(200).json({ ok: true });

  const kind = KINDS[body.kind];
  if (!kind) return res.status(400).json({ ok: false });

  const lead = {};
  for (const key of FIELDS) lead[key] = clean(body[key]);
  if (kind.need.some((key) => !lead[key])) return res.status(400).json({ ok: false });
  if (lead.phone && lead.phone.replace(/\D/g, "").length < 10) return res.status(400).json({ ok: false });
  if (lead.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) return res.status(400).json({ ok: false });

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(503).json({ ok: false });

  const lines = FIELDS.filter((field) => lead[field]).map((field) => LABELS[field] + ": " + lead[field]);
  const who = lead.name || lead.email;
  const when = lead.deliver || lead.date;
  const payload = {
    from: process.env.LEAD_FROM || "Cube Drop website <onboarding@resend.dev>",
    to: [process.env.LEAD_TO || "drop@cubedrop.co.uk"],
    subject: kind.label + ": " + who + (when ? ", " + when : ""),
    text: kind.label + "\n\n" + lines.join("\n") + "\n\nSent from the Cube Drop website. Nothing has been charged."
  };
  if (lead.email) payload.reply_to = lead.email;

  try {
    const sent = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!sent.ok) return res.status(502).json({ ok: false });
  } catch {
    return res.status(502).json({ ok: false });
  }
  return res.status(200).json({ ok: true });
};
