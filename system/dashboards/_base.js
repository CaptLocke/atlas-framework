/* Atlas dashboard runtime.
   THE ONLY COPY. Templates hold a placeholder in their base script element,
   and system/tools/render.py puts this file there when it builds a
   page.

   Safety: dashboard data comes from emails, documents, and meetings, so it is
   untrusted text. Everything is rendered with textContent / createElement,
   never parsed as HTML markup. No network calls, no connectors. A live page reads its
   data from its own artifact database, through the viewer's runtime (N.page), and its
   buttons write requests there (N.request). Browser storage is used only for UI
   conveniences (theme, remembered filter) and is optional. */
(function () {
  "use strict";
  var N = (window.Atlas = {});
  N.meta = {};
  N.live = null;   /* {db, requests} while a live page is connected to its database */

  var LABELS = {
    i_owe: "I owe", waiting_on: "Waiting on",
    open: "Open", done: "Done", dropped: "Dropped", slipped: "Slipped",
    high: "High", medium: "Medium", low: "Low",
    on_track: "On track", at_risk: "At risk", off_track: "Off track", unknown: "Not assessed",
    proposed: "Proposed", active: "Active", paused: "Paused", cancelled: "Cancelled",
    made: "Made", reversed: "Reversed", superseded: "Superseded",
    potential: "Potential", resolved: "Resolved",
    draft: "Draft", achieved: "Achieved", missed: "Missed",
    meeting: "Meeting", one_on_one: "1:1", deadline: "Deadline", milestone: "Milestone", occurrence: "Event",
    ok: "OK", partial: "Partial", failed: "Failed", skipped_away: "Skipped (away)",
    skipped_paused: "Skipped (paused)", early_exit: "Nothing new", never_run: "Not run yet",
    pending: "Pending", approved: "Approved", rejected: "Rejected", executed: "Done", expired: "Expired",
    confirmed: "Confirmed", stated: "You said this", observed: "Observed", researched: "Researched",
    uploaded: "From your documents", inferred: "Inferred",
    ready: "Prep ready", planned: "Prep coming", none: "No prep", not_needed: "No prep needed",
    manager: "Manager", report: "Report", peer: "Peer", stakeholder: "Stakeholder", customer: "Customer",
    vendor: "Vendor", partner: "Partner", external: "External", other: "Other",
    task_group: "Task group", project: "Project", initiative: "Initiative", program: "Program",
    quarter: "Quarter", half: "Half-year", year: "Year", multi_year: "Multi-year"
  };
  N.label = function (v) {
    if (v == null) return "";
    return LABELS[v] || String(v).replace(/_/g, " ").replace(/^./, function (c) { return c.toUpperCase(); });
  };
  N.tones = {
    danger: ["slipped", "off_track", "failed", "high", "active_risk", "error", "missed"],
    warn: ["at_risk", "partial", "medium", "pending", "potential", "proposed", "warn"],
    ok: ["on_track", "ok", "done", "achieved", "made", "resolved", "confirmed", "stated", "ready", "executed"],
    accent: ["early_exit", "open", "active", "planned"]
  };
  N.tone = function (v) {
    for (var t in N.tones) if (N.tones[t].indexOf(v) !== -1) return t;
    return null;
  };

  /* ---- DOM helpers ---- */
  function add(el, c) {
    if (c == null || c === false || c === "") return;
    if (Array.isArray(c)) { for (var i = 0; i < c.length; i++) add(el, c[i]); return; }
    el.appendChild(typeof c === "object" ? c : document.createTextNode(String(c)));
  }
  function h(tag, props) {
    var el = document.createElement(tag);
    if (props) {
      for (var k in props) {
        var v = props[k];
        if (v == null || v === false) continue;
        if (k === "class") el.className = v;
        else if (k === "text") el.textContent = v;
        else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? "" : v);
      }
    }
    for (var i = 2; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  N.h = h;
  N.add = add;

  /* ---- Browser storage (optional; never required) ---- */
  N.store = {
    get: function (k) { try { return window.localStorage.getItem("atlas:" + k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem("atlas:" + k, v); } catch (e) { /* ignore */ } }
  };

  /* ---- Data ---- */
  N.load = function () {
    var node = document.getElementById("atlas-data");
    var raw = node ? node.textContent.trim() : "";
    if (!raw || raw.indexOf("{{") === 0) return null;
    try { return JSON.parse(raw); } catch (e) { return null; }
  };
  N.list = function (v) { return Array.isArray(v) ? v : []; };

  /* ---- Dates. Date-only values are calendar days; datetimes carry an offset. ---- */
  function dateOnly(s) { return typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s); }
  function toDate(s) { return dateOnly(s) ? new Date(s + "T12:00:00Z") : new Date(s); }
  function fmt(s, opts) {
    if (!s) return "";
    var d = toDate(s);
    if (isNaN(d.getTime())) return String(s);
    opts.timeZone = dateOnly(s) ? "UTC" : (N.meta.timezone || undefined);
    try { return new Intl.DateTimeFormat(N.meta.locale || undefined, opts).format(d); }
    catch (e) { return String(s); }
  }
  N.date = function (s) { return fmt(s, { month: "short", day: "numeric" }); };
  N.dateY = function (s) { return fmt(s, { year: "numeric", month: "short", day: "numeric" }); };
  N.weekday = function (s) { return fmt(s, { weekday: "short", month: "short", day: "numeric" }); };
  N.dayName = function (s) { return fmt(s, { weekday: "long" }); };
  N.longDate = function (s) { return fmt(s, { weekday: "long", year: "numeric", month: "long", day: "numeric" }); };
  N.time = function (s) { return dateOnly(s) ? "" : fmt(s, { hour: "numeric", minute: "2-digit" }); };
  N.dateTime = function (s) { return dateOnly(s) ? N.date(s) : fmt(s, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }); };
  N.dayKey = function (s) {
    if (!s) return null;
    if (dateOnly(s)) return s;
    var d = new Date(s);
    if (isNaN(d.getTime())) return null;
    try {
      return new Intl.DateTimeFormat("en-CA", { timeZone: N.meta.timezone || undefined, year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
    } catch (e) { return s.slice(0, 10); }
  };
  N.daysFromToday = function (s) {
    var k = N.dayKey(s), today = N.meta.as_of;
    if (!k || !today) return null;
    return Math.round((Date.parse(k + "T00:00:00Z") - Date.parse(today + "T00:00:00Z")) / 86400000);
  };
  N.rel = function (s) {
    var n = N.daysFromToday(s);
    if (n == null) return "";
    if (n === 0) return "today";
    if (n === 1) return "tomorrow";
    if (n === -1) return "yesterday";
    return n > 0 ? "in " + n + " days" : -n + " days ago";
  };
  N.due = function (s) {
    if (!s) return "No date";
    var n = N.daysFromToday(s);
    if (n == null) return "Due " + N.date(s);
    if (n < 0) return (n === -1 ? "1 day" : -n + " days") + " overdue";
    if (n === 0) return "Due today";
    if (n === 1) return "Due tomorrow";
    return "Due " + N.date(s);
  };

  /* ---- Record references ----
     Pages never show record IDs, [[type/slug]] mentions, inbox entry numbers, or file paths: they are
     noise to the reader. The data still carries them (contracts, search, troubleshooting). */
  var ID_RE = /\[\[([a-z]+\/[a-z0-9][a-z0-9-]*)\]\]/g;
  N.rid = function () { return null; };
  N.path = function () { return null; };
  /* A readable name for a bare ID: "sources/2026-10-13-brightline-agenda-thread" -> "Brightline agenda thread". */
  N.idName = function (id) {
    var parts = String(id || "").split("/"), type = parts.length > 1 ? parts[0] : "";
    var s = parts.pop().replace(/^\d{4}-\d{2}-\d{2}-/, "").replace(/-/g, " ");
    if (!s) return "";
    if (type === "people" || type === "organizations") return s.replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return s.charAt(0).toUpperCase() + s.slice(1);
  };
  /* A ref is {id, title}. Renders the title as plain text (links on a page only ever open another dashboard). */
  N.ref = function (r) {
    if (!r) return null;
    if (typeof r === "string") r = { id: r };
    return h("span", { class: "ref" }, r.title || N.idName(r.id));
  };
  N.refs = function (list) {
    list = N.list(list);
    var out = [];
    list.forEach(function (r, i) { if (i) out.push(", "); out.push(N.ref(r)); });
    return out;
  };
  N.name = function (r) { return r ? (typeof r === "string" ? r : r.title || r.id) : ""; };
  /* Plain text with [[type/slug]] mentions: a citation in brackets is dropped; a mention used as a word
     becomes the record's readable name. */
  N.rich = function (text) {
    if (text == null) return null;
    if (typeof text !== "string") return text;  /* already built nodes (e.g. text with a page link) */
    var M = "\\[\\[[a-z]+\\/[a-z0-9][a-z0-9-]*\\]\\]";
    return String(text)
      .replace(new RegExp("\\s*\\(\\s*" + M + "(?:\\s*[,;]\\s*" + M + ")*\\s*\\)", "g"), "")
      .replace(ID_RE, function (_, id) { return N.idName(id); })
      .replace(/\s+([.,;:!?)])/g, "$1")
      .replace(/\s{2,}/g, " ")
      .trim();
  };

  /* ---- Icons: inline strokes on a 24px grid, decorative (aria-hidden) ---- */
  var SVGNS = "http://www.w3.org/2000/svg";
  var ICONS = {
    check: ["M5 12.5l4.5 4.5L19 7.5"],
    chevron: ["M6 9l6 6 6-6"],
    search: ["M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z", "M20 20l-4.8-4.8"],
    sun: ["M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M12 2v2", "M12 20v2", "M4.9 4.9l1.4 1.4", "M17.7 17.7l1.4 1.4", "M2 12h2", "M20 12h2", "M4.9 19.1l1.4-1.4", "M17.7 6.3l1.4-1.4"],
    moon: ["M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"],
    copy: ["M9 9h10v10H9z", "M5 15V5h10"]
  };
  N.icon = function (name, cls) {
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("class", "atl-icon" + (cls ? " " + cls : ""));
    if (name === "check") svg.setAttribute("style", "stroke-width:2.2");
    (ICONS[name] || []).forEach(function (d) { var p = document.createElementNS(SVGNS, "path"); p.setAttribute("d", d); svg.appendChild(p); });
    return svg;
  };

  /* ---- Status: always a word plus a color. Tones: bad, warn, good, info, accent, neutral. ---- */
  var OLD_TONE = { danger: "bad", warn: "warn", ok: "good", accent: "info", muted: "neutral" };
  N.toneOf = function (v) { var t = N.tone(v); return t ? OLD_TONE[t] : "neutral"; };
  N.badge = function (text, tone) {
    if (!text) return null;
    tone = OLD_TONE[tone] || tone || "neutral";
    return h("span", { class: "atl-badge" + (tone !== "neutral" ? " atl-badge--" + tone : "") }, text);
  };
  N.dot = function (tone) {
    tone = OLD_TONE[tone] || tone;
    return h("span", { class: "atl-dot" + (tone && tone !== "neutral" ? " atl-dot--" + tone : ""), "aria-hidden": "true" });
  };
  /* Kept for user dashboards: a chip is a badge. */
  N.chip = function (text, tone) { return N.badge(text, tone); };
  N.status = function (v) { return N.badge(N.label(v), N.toneOf(v)); };

  N.empty = function (text) { return h("p", { class: "empty" }, text); };
  N.more = function (key) {
    var n = (N.meta.truncated || {})[key];
    if (!n) return null;
    return h("p", { class: "more" }, n + " more not shown here. Ask Atlas in chat to see them.");
  };
  N.total = function (key, shown) { return shown + ((N.meta.truncated || {})[key] || 0); };

  /* ---- Buttons ---- */
  /* opts: {label, variant: primary|secondary|ghost, check, onClick, ariaLabel} */
  N.button = function (o) {
    return h("button", { type: "button", class: "atl-btn atl-btn--" + (o.variant || "secondary"), onclick: o.onClick || null, "aria-label": o.ariaLabel || null },
      o.check ? N.icon("check") : null, h("span", null, o.label));
  };

  /* ---- Toast: one at a time, five seconds, optional Undo ---- */
  var toastEl = null, toastTimer = null;
  N.toast = function (message, onUndo) {
    if (toastEl && toastEl.parentNode) toastEl.parentNode.removeChild(toastEl);
    clearTimeout(toastTimer);
    var msg = h("span", null, "");
    toastEl = h("div", { class: "atl-toast", role: "status", "aria-live": "polite" }, msg,
      onUndo ? h("button", { type: "button", class: "atl-toast__undo", onclick: function () { hide(); onUndo(); } }, "Undo") : null);
    function hide() { if (toastEl && toastEl.parentNode) toastEl.parentNode.removeChild(toastEl); }
    document.body.appendChild(toastEl);
    setTimeout(function () { msg.textContent = message; }, 50);   /* text after the live region exists, so it's announced */
    toastTimer = setTimeout(hide, 5000);
  };

  /* ---- Requests for Atlas. A page can't change a record: a button copies a ready request
     to paste into the Atlas chat, and says so. The list changes when Atlas refreshes the page. ---- */
  N.copyText = function (text, anchor) {
    function fallback() {
      var box = h("textarea", { class: "atl-copybox", readonly: true, rows: String(Math.min(8, String(text).split("\n").length + 1)), "aria-label": "Text to paste in your Atlas chat" });
      box.value = text;
      var holder = anchor && anchor.parentNode;
      if (holder) {
        var old = holder.querySelector(".atl-copybox");
        if (old) old.parentNode.removeChild(old);
        holder.appendChild(box);
      }
      box.focus(); box.select();
      N.toast("Copy the selected text and paste it in your Atlas chat.");
    }
    try {
      navigator.clipboard.writeText(text).then(function () { N.toast("Copied. Paste it in your Atlas chat."); }, fallback);
    } catch (e) { fallback(); }
  };
  /* Page data comes from emails and documents, so it is cleaned before it lands in chat: control characters
     and line breaks become spaces, and each piece is capped. Quote every data piece with N.quote, and add the
     record or inbox ID with N.withId: Atlas acts on the record the ID names, and the quoted text is only a
     reminder of which one (system/rules/governance.md, N7). */
  function clean(s, max) {
    s = String(s == null ? "" : s).replace(/[\u0000-\u001f\u007f-\u009f\u2028\u2029]+/g, " ").replace(/\s+/g, " ").trim();
    return s.length > max ? s.slice(0, max - 1).trim() + "…" : s;
  }
  N.clean = function (s) { return clean(s, 200); };
  N.quote = function (title) { return "“" + clean(title, 200).replace(/[“”"]/g, "'") + "”"; };
  N.withId = function (text, id) { return text + (id ? " (" + clean(id, 120) + ")" : ""); };
  /* A request button: label on the button; text, built with N.quote and N.withId, is what lands in chat. */
  N.request = function (label, text, variant, check, live) {
    if (live && N.live && LIVE_KINDS[live.kind] && live.target) return liveRequest(label, text, variant, check, live);
    var btn = N.button({ label: label, variant: variant, check: check });
    btn.addEventListener("click", function (e) { e.stopPropagation(); N.copyText(clean(text, 600), btn); });
    return btn;
  };

  /* On a live page, a button for one of these kinds writes a request row instead of copying text;
     Atlas applies it at its next routine run or chat and sets its state (plans: live pages).
     live: {kind, target (record ID), quoted (the title, a reminder only), due (move_date)} */
  var LIVE_KINDS = { mark_done: 1, mark_received: 1, move_date: 1 };
  var CLOSES = { mark_done: 1, mark_received: 1 };   /* kinds whose item leaves the page once applied */
  var REQUEST_STATE = {
    queued: "Saved. Atlas does this at its next run or chat",
    applied: "Done",
    waiting_chat: "Waiting for your next chat",
    needs_chat: "Atlas will ask you about this in chat"
  };
  /* What a button shows for the newest request of its own kind on its record: {badge, tone} in place
     of the button, or {note} beside it. An applied Move the date gives the button back: the item stays. */
  N.requestView = function (row, kind) {
    if (!row || !REQUEST_STATE[row.state] && row.state !== "refused") return {};
    if (row.state === "refused") return { note: row.note ? "Atlas couldn't do this: " + clean(row.note, 160) : "Atlas couldn't do this." };
    if (row.state === "applied" && !CLOSES[kind]) return {};
    return { badge: REQUEST_STATE[row.state], tone: row.state === "applied" ? "good" : "neutral" };
  };
  /* The newest request per record and kind, from a snapshot's rows ([{target, kind, created, state}]). */
  N.latestRequests = function (rows) {
    var out = {};
    N.list(rows).forEach(function (v) {
      if (!v || typeof v.target !== "string" || typeof v.kind !== "string") return;
      var key = v.target + "|" + v.kind;
      if (!out[key] || String(v.created) > String(out[key].created)) out[key] = v;
    });
    return out;
  };
  function today() {
    var t = new Date(), p = function (n) { return (n < 10 ? "0" : "") + n; };
    return t.getFullYear() + "-" + p(t.getMonth() + 1) + "-" + p(t.getDate());
  }
  function liveRequest(label, text, variant, check, spec) {
    var holder = h("span", { class: "atl-request", onclick: function (e) { e.stopPropagation(); } });
    var view = N.requestView(N.live.requests[spec.target + "|" + spec.kind], spec.kind);
    if (view.badge) { holder.appendChild(N.badge(view.badge, view.tone)); return holder; }
    function save(args) {
      var id = spec.kind + "-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
      N.live.db.collection("requests").doc(id).set({
        kind: spec.kind, target: clean(spec.target, 120), quoted: clean(spec.quoted, 1000), args: args || {},
        created: new Date().toISOString(), state: "queued"
      }).then(function () {
        N.toast("Saved. Atlas will do this at its next run or chat.");
      }, function () {
        N.copyText(clean(text, 600), holder);   /* couldn't save: fall back to the chat request */
      });
    }
    var btn = N.button({ label: label, variant: variant, check: check });
    holder.appendChild(btn);
    if (view.note) holder.appendChild(h("span", { class: "atl-request__note" }, view.note));
    btn.addEventListener("click", function () {
      if (spec.kind !== "move_date") { btn.disabled = true; save(); return; }
      var input = h("input", { type: "date", class: "atl-input", min: today(), "aria-label": "New due date for " + clean(spec.quoted, 80), value: spec.due || "" });
      var ok = N.button({ label: "Save date", variant: "primary", onClick: function () { if (input.value) { ok.disabled = true; save({ due: input.value }); } } });
      var cancel = N.button({ label: "Cancel", variant: "ghost", onClick: function () { holder.textContent = ""; holder.appendChild(btn); btn.focus(); } });
      holder.textContent = "";
      add(holder, [input, ok, cancel]);
      input.focus();
    });
    return holder;
  }

  /* ---- Sections: a display heading with its count, a note, optional tools on the right ---- */
  /* opts: {id, title, note, count, key, body, tools} */
  N.section = function (o) {
    var hid = o.id + "-h";
    return h("section", { class: "sec", id: o.id, "aria-labelledby": hid },
      h("div", { class: "sec-head" },
        h("h2", { id: hid }, o.title, o.count != null ? h("span", { class: "count sec-count", "aria-label": o.count + " items" }, String(o.count)) : null),
        o.tools ? h("div", { class: "sec-tools" }, o.tools) : null,
        o.note ? h("p", { class: "sec-note" }, o.note) : null),
      h("div", { class: "sec-body" }, o.body, o.key ? N.more(o.key) : null));
  };

  /* ---- Lists ---- */
  /* A bordered list; children are rows and group headers. */
  N.listBox = function (children, emptyText) {
    children = N.list(children).filter(Boolean);
    return children.length ? h("ul", { class: "atl-list" }, children) : N.empty(emptyText || "Nothing here right now.");
  };
  N.group = function (text) { return h("li", { class: "atl-group overline", role: "presentation" }, text); };

  /* One item in a list: status dot, title, meta line, a badge, an action that stays visible, and
     details that expand in place. opts: {title, meta:[...], tone, badge:[text, tone] | node,
     action: node | [nodes], detail: () => nodes (built on first open), search: extra text} */
  var rowSeq = 0;
  N.row = function (o) {
    var id = "row-" + (++rowSeq);
    var metas = N.list(o.meta).filter(function (x) { return x != null && x !== ""; });
    var metaNode = metas.length ? h("span", { class: "atl-row__meta" }, metas.map(function (m, i) { return [i ? " · " : "", m]; })) : null;
    var text = h("span", { class: "atl-row__text" }, h("span", { class: "atl-row__title" }, o.title), metaNode);
    var badge = Array.isArray(o.badge) ? N.badge(o.badge[0], o.badge[1]) : o.badge || null;
    var expandable = typeof o.detail === "function";
    var main = expandable
      ? h("button", { type: "button", class: "atl-row__main", "aria-expanded": "false", "aria-controls": id }, N.dot(o.tone), text, N.icon("chevron", "atl-row__chev"))
      : h("div", { class: "atl-row__main" }, N.dot(o.tone), text);
    var detail = expandable ? h("div", { class: "atl-row__detail", id: id, hidden: true }) : null;
    var li = h("li", { class: "atl-row" },
      h("div", { class: "atl-row__line" }, main,
        badge || o.action ? h("div", { class: "atl-row__end" }, badge, o.action || null) : null),
      detail);
    if (expandable) {
      var built = false;
      main.addEventListener("click", function () {
        var open = main.getAttribute("aria-expanded") !== "true";
        if (open && !built) { add(detail, o.detail()); built = true; }
        main.setAttribute("aria-expanded", String(open));
        detail.hidden = !open;
      });
    }
    li._search = [typeof o.title === "string" ? o.title : li.textContent, metas.join(" "), o.search || ""].join(" ").toLowerCase();
    return li;
  };

  /* What goes inside an expanded row or a card. opts: {facts:[[label, value]], text, blocks:[{heading, nodes}],
     body:[{heading,text}], body_truncated, links:[ref], dates, actions:[nodes]} */
  N.detail = function (o) {
    var facts = N.list(o.facts).map(function (p) { return p && !Array.isArray(p) && p.label ? [p.label, p.value] : p; })
      .filter(function (p) { return p && p[1] != null && p[1] !== "" && !(Array.isArray(p[1]) && !p[1].length); });
    var body = N.list(o.body).filter(function (s) { return s && s.text; });
    var links = N.list(o.links).filter(Boolean);
    return [
      o.text ? h("p", null, N.rich(o.text)) : null,
      N.list(o.blocks).filter(function (b) { return b && b.nodes; }).map(function (b) {
        return h("div", { class: "detail-block" }, b.heading ? h("h4", null, b.heading) : null, b.nodes);
      }),
      facts.length ? h("dl", { class: "facts" }, facts.map(function (p) { return h("div", null, h("dt", null, p[0]), h("dd", null, typeof p[1] === "object" ? p[1] : N.rich(String(p[1])))); })) : null,
      body.map(function (s) { return h("div", { class: "detail-block" }, s.heading ? h("h4", null, s.heading) : null, h("p", { class: "detail-text" }, N.rich(s.text))); }),
      o.body_truncated ? h("p", { class: "detail-note" }, "There's more in this record than fits here. Ask Atlas in chat to see all of it.") : null,
      links.length ? h("div", { class: "detail-block" }, h("h4", null, "Linked"), h("p", null, links.map(function (x, i) { return [i ? ", " : "", N.name(x)]; }))) : null,
      o.dates ? h("p", { class: "detail-note" }, o.dates) : null,
      N.list(o.actions).filter(Boolean).length ? h("div", { class: "atl-actions" }, o.actions) : null
    ];
  };
  N.para = function (text) { return text ? h("p", null, N.rich(text)) : null; };
  N.lines = function (items) { items = N.list(items).filter(Boolean); return items.length ? h("ul", { class: "detail-list" }, items.map(function (x) { return h("li", null, x); })) : null; };
  N.datesLine = function (created, updated) {
    return [created ? "Created " + N.dateY(created) : null, updated ? "Updated " + N.dateY(updated) : null].filter(Boolean).join(" · ");
  };
  /* Extra facts from a record's panel data (details: [{label, value}]) not already shown. */
  N.mergeDetails = function (pairs, extra) {
    var out = [], seen = {};
    N.list(pairs).forEach(function (p) { if (p && p[1] != null && p[1] !== "") { out.push({ label: p[0], value: p[1] }); seen[p[0]] = 1; } });
    N.list(extra).forEach(function (x) { if (x && x.label && !seen[x.label] && x.value != null && x.value !== "") out.push({ label: x.label, value: x.value }); });
    return out.slice(0, 16);
  };

  /* ---- Cards ---- */
  /* opts: {eyebrow:[text, tone] | node, title, detail, body, actions:[nodes], attrs} */
  N.card = function (o) {
    var props = { class: "atl-card" };
    if (o.attrs) for (var k in o.attrs) props[k] = o.attrs[k];
    var eyebrow = Array.isArray(o.eyebrow) ? N.badge(o.eyebrow[0], o.eyebrow[1]) : o.eyebrow || null;
    var acts = N.list(o.actions).filter(Boolean);
    var el = h("article", props,
      eyebrow ? h("div", { class: "atl-card__eyebrow chips" }, eyebrow) : null,
      h("h3", { class: "atl-card__title" }, o.title),
      o.detail ? h("p", { class: "atl-card__detail" }, o.detail) : null,
      o.body ? h("div", { class: "atl-card__body" }, o.body) : null,
      acts.length ? h("div", { class: "atl-card__actions" }, acts) : null);
    el._search = [typeof o.title === "string" ? o.title : "", el.textContent].join(" ").toLowerCase();
    return el;
  };

  /* ---- Tabs: underlined, live counts. Plain #token links open a tab (#commitments). ---- */
  /* items: [{id, label, count, warn}] ; onChange(id). Returns {el, set(id), count(id, n, warn)} */
  N.tabs = function (items, initial, onChange) {
    var current = initial;
    var hashId = (location.hash || "").replace(/^#/, "");
    if (items.some(function (t) { return t.id === hashId; })) current = hashId;
    var btns = {}, counts = {};
    var el = h("div", { class: "atl-tabs", role: "tablist" }, items.map(function (t) {
      counts[t.id] = h("span", { class: "atl-tab__count" + (t.warn ? " atl-tab__count--warn" : "") }, String(t.count != null ? t.count : ""));
      if (t.count == null) counts[t.id].hidden = true;
      btns[t.id] = h("button", { type: "button", role: "tab", id: "tab-" + t.id, "aria-controls": "panel-" + t.id, class: "atl-tab",
        onclick: function () { set(t.id, true); } }, t.label, counts[t.id]);
      return btns[t.id];
    }));
    el.addEventListener("keydown", function (e) {
      var ids = items.map(function (t) { return t.id; }), i = ids.indexOf(current), next;
      if (e.key === "ArrowRight") next = ids[(i + 1) % ids.length];
      else if (e.key === "ArrowLeft") next = ids[(i + ids.length - 1) % ids.length];
      else if (e.key === "Home") next = ids[0];
      else if (e.key === "End") next = ids[ids.length - 1];
      else return;
      set(next, true); btns[next].focus(); e.preventDefault();
    });
    function set(id, user) {
      current = id;
      items.forEach(function (t) {
        var on = t.id === id;
        btns[t.id].className = "atl-tab" + (on ? " atl-tab--current" : "");
        btns[t.id].setAttribute("aria-selected", String(on));
        btns[t.id].tabIndex = on ? 0 : -1;
      });
      if (user) { try { history.replaceState(null, "", "#" + id); } catch (e) { /* ignore */ } }
      onChange(id, user);
    }
    return { el: el, current: function () { return current; }, set: set, start: function () { set(current, false); },
      count: function (id, n, warn) {
        var c = counts[id]; if (!c) return;
        c.textContent = String(n); c.hidden = n == null;
        c.className = "atl-tab__count" + (warn ? " atl-tab__count--warn" : "");
      } };
  };

  /* ---- Segmented control: two to four options; remembers the choice per page. ---- */
  N.segmented = function (name, options, initial, onChange) {
    var key = (N.meta.dashboard || "page") + ":" + name;
    var saved = N.store.get(key);
    var current = options.some(function (o) { return o.value === saved; }) ? saved : initial;
    var buttons = options.map(function (o) {
      return h("button", { type: "button", "data-value": o.value, "aria-pressed": String(o.value === current),
        class: "atl-seg__btn" + (o.value === current ? " atl-seg__btn--on" : ""),
        onclick: function () {
          current = o.value; N.store.set(key, current);
          buttons.forEach(function (b) {
            var on = b.getAttribute("data-value") === current;
            b.setAttribute("aria-pressed", String(on)); b.className = "atl-seg__btn" + (on ? " atl-seg__btn--on" : "");
          });
          onChange(current);
        } }, o.label);
    });
    var group = h("div", { class: "atl-seg", role: "group", "aria-label": name }, buttons);
    setTimeout(function () { onChange(current); }, 0);
    return group;
  };

  /* ---- Find on this page ---- */
  var searchSeq = 0;
  N.search = function (label, onInput) {
    var id = "q-" + (N.meta.dashboard || "page") + "-" + (++searchSeq);
    return h("div", { class: "atl-search" },
      h("label", { class: "visually-hidden", for: id }, label),
      N.icon("search"),
      h("input", { id: id, type: "search", placeholder: label, autocomplete: "off",
        oninput: function (e) { onInput(e.target.value.trim().toLowerCase()); } }));
  };
  N.matches = function (el, q) { return !q || String(el._search || el.textContent || "").toLowerCase().indexOf(q) !== -1; };

  N.bar = function (fraction, label, tone) {
    if (typeof fraction !== "number" || isNaN(fraction)) return null;
    var pct = Math.max(0, Math.min(1, fraction)) * 100;
    return h("div", { class: "bar", role: "img", "data-tone": tone || null, "aria-label": label || Math.round(pct) + "% complete" },
      h("span", { style: "width:" + pct.toFixed(1) + "%" }));
  };
  N.facts = function (pairs) {
    var rows = pairs.filter(function (p) { return p && p[1] != null && p[1] !== "" && !(Array.isArray(p[1]) && !p[1].length); });
    return rows.length ? h("dl", { class: "facts" }, rows.map(function (p) { return h("div", null, h("dt", null, p[0]), h("dd", null, p[1])); })) : null;
  };

  /* ---- Older building blocks, kept for user dashboards ---- */
  N.item = function (o) {
    var metas = N.list(o.meta).filter(function (x) { return x != null && x !== ""; }).map(function (x) { return h("span", null, x); });
    var props = { class: "item", "data-tone": o.tone || null };
    if (o.attrs) for (var k in o.attrs) props[k] = o.attrs[k];
    return h("li", props,
      h("div", { class: "item-main" },
        h("p", { class: "item-title" }, o.title),
        o.text ? h("p", { class: "item-text" }, N.rich(o.text)) : null,
        metas.length ? h("p", { class: "item-meta" }, metas) : null,
        o.insight ? h("p", { class: "item-insight" }, N.rich(o.insight)) : null,
        o.nextStep ? h("p", { class: "item-insight" }, h("b", null, "Next step: "), N.rich(o.nextStep)) : null,
        o.extra || null),
      o.aside && N.list(o.aside).some(Boolean) ? h("div", { class: "item-aside" }, o.aside) : null);
  };
  N.items = function (nodes, emptyText) {
    nodes = N.list(nodes);
    return nodes.length ? h("ul", { class: "items" }, nodes) : N.empty(emptyText || "Nothing here right now.");
  };
  /* The record drawer is gone: rows expand in place. These keep older user dashboards working:
     N.clickable adds a "Details" toggle that shows a view's content under the card instead of in a drawer. */
  N.recordPanel = function () { return { el: h("span", { hidden: true }), open: function () {}, add: function (v) { return v; }, get: function () { return null; } }; };
  N.clickable = function (card, panel, view) {
    if (!card || !view) return card;
    var box = h("div", { class: "atl-row__detail", hidden: true }), built = false;
    var btn = h("button", { type: "button", class: "atl-btn atl-btn--ghost", "aria-expanded": "false" }, "Details");
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = btn.getAttribute("aria-expanded") !== "true";
      if (open && !built) {
        add(box, N.detail({ text: view.summary, facts: view.details,
          blocks: N.list(view.sections).filter(Boolean).map(function (s) { return { heading: s.heading, nodes: s.nodes }; }),
          body: view.body, body_truncated: view.body_truncated, links: view.links, dates: view.dates }));
        built = true;
      }
      btn.setAttribute("aria-expanded", String(open)); box.hidden = !open;
    });
    var host = card.querySelector && card.querySelector(".item-main") || card;
    host.appendChild(h("div", { class: "atl-actions" }, btn)); host.appendChild(box);
    return card;
  };
  N.openTitle = function (text) { return text; };
  /* The old page header, for user dashboards that build their own: title, subtitle, lead, stat tiles. */
  N.masthead = function (o) {
    o = o || {};
    var stats = o.stats && o.stats.length ? N.statTiles(o.stats.map(function (s, i) { return Array.isArray(s) ? { key: "s" + i, value: s[0], label: s[1] } : s; })) : null;
    return h("div", { class: "page-head" }, h("h1", { class: "page-title" }, o.title),
      o.subtitle ? h("p", { class: "date-line" }, o.subtitle) : null,
      (N.meta.headline || o.lede || o.lead) ? h("p", { class: "lead" }, N.rich(N.meta.headline || o.lede || o.lead)) : null,
      stats ? stats.el : null);
  };

  /* ---- Theme: follows the system until the viewer picks; the toggle switches light and dark ---- */
  function applyTheme(t) {
    if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
    else document.documentElement.removeAttribute("data-theme");
  }
  function isDark() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t === "dark";
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  N.themeButton = function () {
    var btn = h("button", { type: "button", class: "atl-icon-btn" });
    function paint() {
      var dark = isDark();
      while (btn.firstChild) btn.removeChild(btn.firstChild);
      btn.appendChild(N.icon(dark ? "sun" : "moon"));
      btn.setAttribute("aria-pressed", String(dark));
      btn.setAttribute("aria-label", "Dark theme");
    }
    btn.addEventListener("click", function () { var t = isDark() ? "light" : "dark"; N.store.set("theme", t); applyTheme(t); paint(); });
    paint();
    return btn;
  };
  applyTheme(N.store.get("theme") || "auto");

  /* The Atlas mark, inline so it takes --accent. */
  var LOGO = [
    "M20.25 352.566L140.031 193.844C141.398 192.035 143.48 190.906 145.738 190.75C148 190.594 150.215 191.422 151.816 193.023L181.555 222.762C183.156 224.363 183.988 226.582 183.828 228.84C183.672 231.102 182.543 233.184 180.734 234.547L22.016 354.328C21.512 354.707 20.809 354.656 20.367 354.211C19.922 353.77 19.875 353.066 20.25 352.566Z",
    "M355.539 21.555L234.996 179.496C233.617 181.301 231.527 182.426 229.262 182.574C226.996 182.727 224.777 181.895 223.172 180.289L195.113 152.23C193.508 150.625 192.672 148.402 192.824 146.137C192.977 143.871 194.098 141.781 195.902 140.406L353.844 19.863C354.324 19.496 355.004 19.539 355.43 19.969C355.859 20.395 355.906 21.074 355.539 21.555Z",
    "M258.582 262.406L196.883 232.992C195.02 232.105 193.703 230.363 193.352 228.328C193.004 226.293 193.664 224.215 195.121 222.754L223.184 194.695C224.641 193.238 226.719 192.578 228.758 192.926C230.793 193.277 232.531 194.594 233.418 196.457L262.832 258.156C263.414 259.375 263.164 260.828 262.211 261.785C261.254 262.738 259.801 262.988 258.582 262.406Z",
    "M118.082 112.582L179.781 141.996C181.645 142.887 182.961 144.625 183.313 146.66C183.664 148.695 183.004 150.773 181.543 152.234L153.484 180.293C152.023 181.754 149.945 182.414 147.91 182.063C145.875 181.711 144.137 180.395 143.246 178.531L113.832 116.832C113.25 115.613 113.5 114.16 114.453 113.203C115.41 112.25 116.863 112 118.082 112.582Z",
    "M135.297 187.918a52.625 52.625 0 1 0 105.25 0a52.625 52.625 0 1 0-105.25 0Z"
  ];
  N.logo = function () {
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", "0 0 375 375"); svg.setAttribute("aria-hidden", "true"); svg.setAttribute("class", "atl-logo");
    LOGO.forEach(function (d) { var p = document.createElementNS(SVGNS, "path"); p.setAttribute("d", d); svg.appendChild(p); });
    return svg;
  };

  /* ---- Sync status: when the page was refreshed. Staleness is the one thing measured
     against the viewer's clock (meta.stale_after_hours, from the contract). ---- */
  N.refreshedText = function () {
    var at = N.meta.generated_at;
    if (!at) return "Not refreshed yet";
    return "Refreshed " + N.weekday(at) + ", " + N.time(at);
  };
  N.isStale = function () {
    var at = Date.parse(N.meta.generated_at || ""), limit = N.meta.stale_after_hours;
    return !isNaN(at) && typeof limit === "number" && limit > 0 && (Date.now() - at) / 36e5 > limit;
  };
  N.refreshed = function () {
    var stale = N.isStale();
    return h("p", { class: "atl-sync", "data-stale": stale ? "1" : null },
      N.dot(!N.meta.generated_at ? "neutral" : stale ? "warn" : "good"),
      h("time", { datetime: N.meta.generated_at || null }, N.refreshedText()),
      stale ? N.badge("May be out of date", "warn") : null);
  };

  /* ---- Navigation: the same three pages everywhere. Links only ever open another dashboard. ---- */
  var NAV = [["daily-brief", "Today"], ["commitments", "Work"], ["control-center", "Guide"]];
  N.navLinks = function () {
    var order = NAV.map(function (x) { return x[0]; });
    return N.list(N.meta.nav).filter(function (n) { return n && n.url && /^https:\/\//.test(n.url); })
      .sort(function (a, b) {
        var ia = order.indexOf(a.name), ib = order.indexOf(b.name);
        return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
      });
  };
  N.pageUrl = function (name, token) {
    var n = N.navLinks().filter(function (x) { return x.name === name; })[0];
    return n ? n.url + (token ? "#" + token : "") : null;
  };
  /* The name of another dashboard, linked when its URL is known; token opens a tab or section there. */
  N.pageLink = function (name, text, token) {
    var url = name !== N.meta.dashboard ? N.pageUrl(name, token) : null;
    var n = N.navLinks().filter(function (x) { return x.name === name; })[0];
    text = text || (n && n.title) || name;
    return url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, text) : text;
  };
  N.header = function () {
    var links = {};
    N.navLinks().forEach(function (n) { links[n.name] = n; });
    var items = NAV.map(function (x) {
      var cur = x[0] === N.meta.dashboard, n = links[x[0]];
      var label = (n && n.title) || x[1];
      if (cur) return h("span", { class: "atl-nav__item atl-nav__item--current", "aria-current": "page" }, label);
      return n ? h("a", { class: "atl-nav__item", href: n.url, target: "_blank", rel: "noopener noreferrer" }, label) : null;
    }).filter(Boolean);
    return h("header", { class: "atl-header" },
      h("div", { class: "atl-header__inner" },
        h("div", { class: "atl-header__brand" }, N.logo(), h("span", { class: "atl-wordmark" }, "Atlas")),
        items.length ? h("nav", { class: "atl-nav", "aria-label": "Atlas pages" }, items) : null,
        h("div", { class: "atl-header__trailing" }, N.refreshed(), N.themeButton())));
  };

  /* ---- Stat tiles. Each is a readout, a filter (onSelect: chosen again clears it), or a link (href). ----
     stats: [{key, value, label | [singular, plural], tone, href (another page), jump (a section id here), hint, filter: true}] ; onSelect(key | null) */
  N.statTiles = function (stats, onSelect) {
    var selected = null, tiles = {};
    function label(s) { return Array.isArray(s.label) ? (Number(s.value) === 1 ? s.label[0] : s.label[1]) : s.label; }
    function paint() { for (var k in tiles) { tiles[k].classList.toggle("atl-stat--selected", k === selected); tiles[k].setAttribute("aria-pressed", String(k === selected)); } }
    var el = h("ul", { class: "atl-stats" }, N.list(stats).filter(Boolean).map(function (s) {
      var num = h("span", { class: "atl-stat__num" + (s.tone === "bad" && Number(s.value) > 0 ? " atl-stat__num--bad" : "") }, String(s.value));
      var lab = h("span", { class: "atl-stat__label" }, label(s));
      var node;
      if (s.href) node = h("a", { class: "atl-stat atl-stat--action", href: s.href, target: "_blank", rel: "noopener noreferrer" }, num, lab, h("span", { class: "atl-stat__hint" }, s.hint || "View"));
      else if (s.jump) node = h("a", { class: "atl-stat atl-stat--action", href: "#" + s.jump }, num, lab, h("span", { class: "atl-stat__hint" }, s.hint || "View"));
      else if (s.filter && onSelect) {
        node = h("button", { type: "button", class: "atl-stat atl-stat--action", "aria-pressed": "false",
          onclick: function () { selected = selected === s.key ? null : s.key; paint(); onSelect(selected, s); } }, num, lab);
        tiles[s.key] = node;
      } else node = h("div", { class: "atl-stat" }, num, lab);
      return h("li", null, node);
    }));
    return { el: el, clear: function () { selected = null; paint(); }, selected: function () { return selected; },
      select: function (k) { selected = k; paint(); } };
  };

  /* Notices: a label and an icon per level, so a warning reads as one at a glance. */
  var NOTICE = { warn: "Needs attention:", error: "Problem:", info: "Note:" };
  var NOTICE_ICON = {
    warn: ["M12 3.5 2.5 20h19L12 3.5z", "M12 10v4.5", "M12 17.4v.1"],
    error: ["M12 2.75a9.25 9.25 0 1 0 0 18.5 9.25 9.25 0 0 0 0-18.5z", "M12 7.5v6", "M12 16.6v.1"],
    info: ["M12 2.75a9.25 9.25 0 1 0 0 18.5 9.25 9.25 0 0 0 0-18.5z", "M12 11v5.5", "M12 7.6v.1"]
  };
  function noticeIcon(level) {
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true"); svg.setAttribute("class", "notice-icon");
    NOTICE_ICON[level].forEach(function (d) { var p = document.createElementNS(SVGNS, "path"); p.setAttribute("d", d); svg.appendChild(p); });
    return svg;
  }

  N.footer = function () {
    return h("footer", { class: "foot" },
      h("p", null, N.meta.atlas_version ? "Atlas " + N.meta.atlas_version : "Atlas"),
      h("p", null, "To change anything here, ask Atlas in chat."));
  };

  /* ---- Render a page ----
     build(data, main) appends sections to main and returns the page head:
       {title, dateLine (or subtitle), lead, stats:[...], onStat(key, stat)} */
  var resizeBound = false, hashDone = false;
  function paint(defaults, build, data, waiting) {
    var app = document.getElementById("app");
    app.textContent = "";
    N.meta = (data && data.meta) || N.liveMeta || {};
    if (N.meta.locale) document.documentElement.setAttribute("lang", N.meta.locale);
    if (N.meta.title) document.title = N.meta.title;
    var main = h("main", { id: "main" });
    var head = { title: N.meta.title || defaults.title };
    if (!data) {
      waiting = waiting || WAITING.none;
      head.dateLine = waiting[0];
      main.appendChild(waiting[2] ? h("div", { class: "error-box", role: "status" }, waiting[1]) : N.empty(waiting[1]));
    } else {
      try {
        var extra = build(data, main) || {};
        for (var k in extra) head[k] = extra[k];
      } catch (e) {
        main.appendChild(h("div", { class: "error-box", role: "alert" }, "Part of this page couldn't be displayed. Ask Atlas in chat to refresh it."));
        if (window.console) console.error(e);
      }
    }
    var lead = N.meta.headline || head.lead || head.lede;   /* "lede": older templates */
    var stats = head.stats && head.stats.length ? N.statTiles(head.stats.map(function (s, i) {
      return Array.isArray(s) ? { key: "s" + i, value: s[0], label: s[1] } : s;   /* older [value, label] pairs */
    }), head.onStat) : null;
    if (stats && head.onStatsReady) head.onStatsReady(stats);
    var notices = N.list(N.meta.notices);
    var headerEl = N.header();
    add(app, [
      h("a", { class: "skip", href: "#main" }, "Skip to content"),
      headerEl,
      h("div", { class: "wrap" },
        h("div", { class: "page-head" },
          h("h1", { class: "page-title" }, head.title),
          head.dateLine || head.subtitle ? h("p", { class: "date-line" }, head.dateLine || head.subtitle) : null,
          lead ? h("p", { class: "lead" }, N.rich(lead)) : null,
          stats ? stats.el : null),
        notices.length ? h("ul", { class: "notices", "aria-label": "Notices" }, notices.map(function (n) {
          var level = NOTICE[n.level] ? n.level : "warn";
          return h("li", { class: "notice", "data-level": level, role: level === "error" ? "alert" : null },
            noticeIcon(level), h("p", null, h("b", null, NOTICE[level] + " "), N.rich(n.text)));
        })) : null,
        main,
        N.footer())
    ]);
    /* Sticky bars sit under the header, whatever height it wraps to. */
    function setHeaderH() { var hd = document.querySelector(".atl-header"); if (hd) document.documentElement.style.setProperty("--header-h", hd.offsetHeight + "px"); }
    setHeaderH();
    if (!resizeBound) { window.addEventListener("resize", setHeaderH); resizeBound = true; }
    /* A plain #token opens that section (tabs handle their own). */
    var t = (location.hash || "").replace(/^#/, "");
    if (data && !hashDone) {
      hashDone = true;
      if (t && /^[\w.~-]+$/.test(t)) { var target = document.getElementById(t); if (target && target.scrollIntoView) setTimeout(function () { target.scrollIntoView(); }, 0); }
    }
  }

  /* [date line, message, shown as a problem] for a page with nothing to show yet. */
  var WAITING = {
    none: ["Waiting for data", "This page has no data yet. Ask Atlas in chat to refresh it."],
    loading: ["Loading", "Loading your latest information…"],
    empty: ["Waiting for data", "Atlas fills this page at its next run. To fill it now, ask Atlas in chat to refresh it."],
    unavailable: ["Can't load right now", "This page couldn't load its information. Open it in Claude while signed in to see your latest work. If it keeps happening, ask Atlas in chat to refresh it.", true]
  };

  /* A page renders once from its embedded data. A live page (embedded meta.live) renders from its
     database instead: one document per contract section in "sections" ({data}), plus the open
     requests, and renders again whenever either changes. Nothing is fetched over the network:
     the viewer's runtime holds the database. */
  /* A live page's data from its section rows ([{id, data}]) and the embedded meta, or null when it has none. */
  N.assemble = function (rows, liveMeta) {
    var d = {}, any = false;
    N.list(rows).forEach(function (r) { if (r && typeof r.id === "string" && r.doc && Object.prototype.hasOwnProperty.call(r.doc, "data")) { d[r.id] = r.doc.data; any = true; } });
    if (!any) return null;
    var m = {}, k;
    for (k in (liveMeta || {})) m[k] = liveMeta[k];
    for (k in (d.meta || {})) m[k] = d.meta[k];
    d.meta = m;
    return d;
  };

  /* What a viewer has open or typed, so a live re-render can put it back: the expanded rows (by title),
     the find text and the chosen stat tile. Tabs keep themselves (the address) and so do segmented
     choices (browser storage). */
  function uiState() {
    var open = [], q = document.querySelector(".atl-search input"), tile = -1;
    document.querySelectorAll('.atl-row__main[aria-expanded="true"] .atl-row__title').forEach(function (t) { open.push(t.textContent); });
    document.querySelectorAll(".atl-stat").forEach(function (el, i) { if (el.getAttribute("aria-pressed") === "true") tile = i; });
    return { open: open, q: q ? q.value : "", tile: tile, y: window.scrollY };
  }
  function restoreUi(st) {
    if (st.tile >= 0) { var tiles = document.querySelectorAll(".atl-stat"); if (tiles[st.tile] && tiles[st.tile].click) tiles[st.tile].click(); }
    var q = document.querySelector(".atl-search input");
    if (q && st.q) { q.value = st.q; q.dispatchEvent(new Event("input")); }
    if (st.open.length) document.querySelectorAll(".atl-row__main").forEach(function (b) {
      var t = b.querySelector(".atl-row__title");
      if (t && st.open.indexOf(t.textContent) !== -1 && b.getAttribute("aria-expanded") !== "true") b.click();
    });
    window.scrollTo(0, st.y);
  }

  N.page = function (defaults, build) {
    var data = N.load();
    if (!(data && data.meta && data.meta.live)) { paint(defaults, build, data); return; }
    N.liveMeta = data.meta;
    paint(defaults, build, null, WAITING.loading);
    var failed = false;
    function unavailable() { failed = true; N.live = null; paint(defaults, build, null, WAITING.unavailable); }
    var runtime = window.claude;
    if (!runtime || typeof runtime.use !== "function") { unavailable(); return; }
    runtime.use("db").then(function (db) {
      if (!db) { unavailable(); return; }
      var sections = null, requests = {}, timer = null;
      function render() {
        clearTimeout(timer);
        timer = setTimeout(function () {
          if (failed || !sections) return;
          /* a date being picked would be lost: wait until it's saved or cancelled */
          if (document.querySelector(".atl-request input")) { timer = setTimeout(render, 1000); return; }
          var d = N.assemble(sections, N.liveMeta);
          if (!d) { N.live = null; paint(defaults, build, null, WAITING.empty); return; }
          N.live = { db: db, requests: requests };
          var st = uiState();
          paint(defaults, build, d);
          restoreUi(st);
        }, 120);
      }
      db.collection("sections").onSnapshot(function (snap) {
        sections = snap.docs.map(function (doc) { return { id: doc.id, doc: doc.data() }; });
        render();
      }, unavailable);
      db.collection("requests").onSnapshot(function (snap) {
        var latest = N.latestRequests(snap.docs.map(function (doc) { return doc.data(); }));
        for (var key in requests) delete requests[key];
        for (key in latest) requests[key] = latest[key];
        render();
      }, function () { /* without requests the page still shows its sections */ });
    }, unavailable);
  };
})();
