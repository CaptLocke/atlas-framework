/* Atlas dashboard runtime.
   CANONICAL COPY. Every template inlines this file verbatim inside
   <script id="atlas-base-js">. Edit here, then run
   `python3 system/tests/dashboards/render.py --sync`.

   Safety: dashboard data comes from emails, documents, and meetings, so it is
   untrusted text. Everything is rendered with textContent / createElement,
   never parsed as HTML markup. No network calls, no connectors. Browser storage is used
   only for UI conveniences (theme, remembered filter) and is optional. */
(function () {
  "use strict";
  var N = (window.Atlas = {});
  N.meta = {};

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
  /* A ref is {id, title}. Renders the title; with record_base_url set, the title links to the record file. */
  N.ref = function (r) {
    if (!r) return null;
    if (typeof r === "string") r = { id: r };
    var text = r.title || N.idName(r.id);
    var base = N.meta.record_base_url;
    if (base && /^https:\/\//.test(base) && r.id && /^[a-z]+\/[a-z0-9][a-z0-9-]*$/.test(r.id)) {
      return h("a", { class: "ref", href: base + r.id + ".md", target: "_blank", rel: "noopener noreferrer" }, text);
    }
    return h("span", { class: "ref" }, text);
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

  /* ---- Building blocks ---- */
  N.chip = function (text, tone) { return text ? h("span", { class: "chip", "data-tone": tone || null }, text) : null; };
  N.status = function (v) { return N.chip(N.label(v), N.tone(v)); };
  N.empty = function (text) { return h("p", { class: "empty" }, text); };
  N.more = function (key) {
    var n = (N.meta.truncated || {})[key];
    if (!n) return null;
    return h("p", { class: "more" }, n + " more not shown here. Ask Atlas in chat to see them.");
  };
  N.total = function (key, shown) { return shown + ((N.meta.truncated || {})[key] || 0); };

  /* opts: {id, title, note, count, key, body} */
  N.section = function (o) {
    var hid = o.id + "-h";
    return h("section", { class: "sec", id: o.id, "aria-labelledby": hid },
      h("div", { class: "sec-head" }, h("div", null,
        h("h2", { id: hid }, o.title, o.count != null ? h("span", { class: "count", "aria-label": o.count + " items" }, String(o.count)) : null),
        o.note ? h("p", { class: "sec-note" }, o.note) : null)),
      h("div", { class: "sec-body" }, o.body, o.key ? N.more(o.key) : null));
  };

  /* opts: {tone, title, id, meta:[...], text, insight, nextStep, aside:[...], attrs} */
  N.item = function (o) {
    var metas = N.list(o.meta).filter(function (x) { return x != null && x !== ""; })
      .map(function (x) { return h("span", null, x); });
    var props = { class: "item", "data-tone": o.tone || null };
    if (o.attrs) for (var k in o.attrs) props[k] = o.attrs[k];
    return h("li", props,
      h("div", { class: "item-main" },
        h("p", { class: "item-title" }, o.title),
        o.text ? h("p", { class: "item-text" }, N.rich(o.text)) : null,
        metas.length ? h("p", { class: "item-meta" }, metas) : null,
        o.insight ? h("p", { class: "item-insight" }, N.rich(o.insight)) : null,
        o.nextStep ? h("p", { class: "item-insight" }, h("b", null, "Next step: "), N.rich(o.nextStep)) : null,
        o.extra || null,
        o.id ? N.rid(o.id) : null),
      o.aside && N.list(o.aside).some(Boolean) ? h("div", { class: "item-aside" }, o.aside) : null);
  };
  N.items = function (nodes, emptyText) {
    nodes = N.list(nodes);
    return nodes.length ? h("ul", { class: "items" }, nodes) : N.empty(emptyText || "Nothing here right now.");
  };

  /* Segmented filter. options: [{value, label}] ; remembers the choice per page. */
  N.segmented = function (name, options, initial, onChange) {
    var key = (N.meta.dashboard || "page") + ":" + name;
    var saved = N.store.get(key);
    var current = options.some(function (o) { return o.value === saved; }) ? saved : initial;
    var buttons = options.map(function (o) {
      return h("button", { type: "button", "data-value": o.value, "aria-pressed": String(o.value === current),
        onclick: function () {
          current = o.value; N.store.set(key, current);
          buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-value") === current)); });
          onChange(current);
        } }, o.label);
    });
    var group = h("div", { class: "seg", role: "group", "aria-label": name }, buttons);
    setTimeout(function () { onChange(current); }, 0);
    return group;
  };
  N.search = function (label, onInput) {
    var id = "q-" + Math.random().toString(36).slice(2, 8);
    return h("div", { class: "search" },
      h("label", { class: "visually-hidden", for: id }, label),
      h("input", { id: id, type: "search", placeholder: label, autocomplete: "off",
        oninput: function (e) { onInput(e.target.value.trim().toLowerCase()); } }));
  };
  N.bar = function (fraction, label) {
    if (typeof fraction !== "number" || isNaN(fraction)) return null;
    var pct = Math.max(0, Math.min(1, fraction)) * 100;
    return h("div", { class: "bar", role: "img", "aria-label": label || Math.round(pct) + "% complete" },
      h("span", { style: "width:" + pct.toFixed(1) + "%" }));
  };
  N.facts = function (pairs) {
    var rows = pairs.filter(function (p) { return p && p[1] != null && p[1] !== "" && !(Array.isArray(p[1]) && !p[1].length); });
    return rows.length ? h("dl", { class: "facts" }, rows.map(function (p) { return h("div", null, h("dt", null, p[0]), h("dd", null, p[1])); })) : null;
  };

  /* ---- Theme preference (auto / light / dark) ---- */
  var THEMES = ["auto", "light", "dark"];
  function applyTheme(t) {
    if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
    else document.documentElement.removeAttribute("data-theme");
  }
  N.themeButton = function () {
    var t = N.store.get("theme") || "auto";
    if (THEMES.indexOf(t) === -1) t = "auto";
    applyTheme(t);
    var btn = h("button", { type: "button", class: "theme-btn" });
    function label() { btn.textContent = "Theme: " + t; btn.setAttribute("aria-label", "Color theme: " + t + ". Activate to change."); }
    btn.addEventListener("click", function () {
      t = THEMES[(THEMES.indexOf(t) + 1) % THEMES.length];
      N.store.set("theme", t); applyTheme(t); label();
    });
    label();
    return btn;
  };
  applyTheme(N.store.get("theme") || "auto");

  /* The Atlas mark: two long blades and two short ones around a disc, drawn in --star. */
  var LOGO = [
    "M20.25 352.566L140.031 193.844C141.398 192.035 143.48 190.906 145.738 190.75C148 190.594 150.215 191.422 151.816 193.023L181.555 222.762C183.156 224.363 183.988 226.582 183.828 228.84C183.672 231.102 182.543 233.184 180.734 234.547L22.016 354.328C21.512 354.707 20.809 354.656 20.367 354.211C19.922 353.77 19.875 353.066 20.25 352.566Z",
    "M355.539 21.555L234.996 179.496C233.617 181.301 231.527 182.426 229.262 182.574C226.996 182.727 224.777 181.895 223.172 180.289L195.113 152.23C193.508 150.625 192.672 148.402 192.824 146.137C192.977 143.871 194.098 141.781 195.902 140.406L353.844 19.863C354.324 19.496 355.004 19.539 355.43 19.969C355.859 20.395 355.906 21.074 355.539 21.555Z",
    "M258.582 262.406L196.883 232.992C195.02 232.105 193.703 230.363 193.352 228.328C193.004 226.293 193.664 224.215 195.121 222.754L223.184 194.695C224.641 193.238 226.719 192.578 228.758 192.926C230.793 193.277 232.531 194.594 233.418 196.457L262.832 258.156C263.414 259.375 263.164 260.828 262.211 261.785C261.254 262.738 259.801 262.988 258.582 262.406Z",
    "M118.082 112.582L179.781 141.996C181.645 142.887 182.961 144.625 183.313 146.66C183.664 148.695 183.004 150.773 181.543 152.234L153.484 180.293C152.023 181.754 149.945 182.414 147.91 182.063C145.875 181.711 144.137 180.395 143.246 178.531L113.832 116.832C113.25 115.613 113.5 114.16 114.453 113.203C115.41 112.25 116.863 112 118.082 112.582Z",
    "M135.297 187.918a52.625 52.625 0 1 0 105.25 0a52.625 52.625 0 1 0-105.25 0Z"
  ];
  function logo() {
    var ns = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 375 375"); svg.setAttribute("aria-hidden", "true");
    LOGO.forEach(function (d) { var p = document.createElementNS(ns, "path"); p.setAttribute("d", d); svg.appendChild(p); });
    return svg;
  }

  /* The standard refresh marker: when this page was last refreshed, flagged when older
     than meta.stale_after_hours (from the contract). Staleness is the one thing measured against the
     viewer's clock: it is about how old the page is when someone opens it. */
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
    var stale = N.isStale(), state = !N.meta.generated_at ? "none" : stale ? "stale" : "fresh";
    return h("p", { class: "mast-fresh", "data-stale": stale ? "1" : null },
      h("span", { class: "signal", "data-state": state, "aria-hidden": "true" }),
      h("time", { datetime: N.meta.generated_at || null }, N.refreshedText()),
      stale ? N.chip("May be out of date", "warn") : null);
  };

  /* Links on a page only ever open another dashboard: the nav row, and names of other pages in text.
     NAV_ORDER fixes the order so every page lists them the same way. */
  var NAV_ORDER = ["daily-brief", "work-board", "week-ahead", "goals", "people", "decisions-risks", "records", "about-you", "control-center", "atlas-guide"];
  N.navLinks = function () {
    return N.list(N.meta.nav).filter(function (n) { return n && n.url && /^https:\/\//.test(n.url); })
      .sort(function (a, b) {
        var ia = NAV_ORDER.indexOf(a.name), ib = NAV_ORDER.indexOf(b.name);
        return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
      });
  };
  /* The name of another dashboard, linked when its URL is known (plain text otherwise). */
  N.pageLink = function (name, text) {
    var n = N.navLinks().filter(function (x) { return x.name === name; })[0];
    text = text || (n && n.title) || name;
    return n && n.name !== N.meta.dashboard ? h("a", { href: n.url, target: "_blank", rel: "noopener noreferrer" }, text) : text;
  };

  /* Every page's header: title, subtitle, headline (meta.headline, else the page's own lede), stat cards.
     opts: {title, subtitle, lede, stats:[[value,label]]} */
  N.masthead = function (o) {
    var nav = N.navLinks();
    return h("header", { class: "mast" },
      h("div", { class: "mast-top" },
        h("p", { class: "mast-who" }, logo(), "Atlas"),
        N.refreshed()),
      h("h1", null, o.title),
      o.subtitle ? h("p", { class: "mast-sub" }, o.subtitle) : null,
      (N.meta.headline || o.lede) ? h("p", { class: "mast-lede" }, N.rich(N.meta.headline || o.lede)) : null,
      o.stats && o.stats.length ? h("ul", { class: "mast-stats" }, o.stats.map(function (s) {
        return h("li", { class: "stat" }, h("b", null, String(s[0])), h("span", null, s[1]));
      })) : null,
      nav.length ? h("nav", { class: "mast-nav", "aria-label": "Other Atlas pages" }, nav.map(function (n) {
        return h("a", { href: n.url, target: "_blank", rel: "noopener noreferrer", "aria-current": n.name === N.meta.dashboard ? "page" : null }, n.title || n.name);
      })) : null);
  };

  /* Footer: the Atlas version on the left, the theme button on the right. */
  N.footer = function () {
    return h("footer", { class: "foot" },
      h("p", null, N.meta.atlas_version ? "Atlas " + N.meta.atlas_version : "Atlas"),
      h("p", { class: "chips" }, N.themeButton()));
  };

  /* Notices: a label and an icon per level, so a warning reads as one at a glance. */
  var NOTICE = { warn: "Needs attention:", error: "Problem:", info: "Note:" };
  var NOTICE_ICON = {
    warn: ["M12 3.5 2.5 20h19L12 3.5z", "M12 10v4.5", "M12 17.4v.1"],
    error: ["M12 2.75a9.25 9.25 0 1 0 0 18.5 9.25 9.25 0 0 0 0-18.5z", "M12 7.5v6", "M12 16.6v.1"],
    info: ["M12 2.75a9.25 9.25 0 1 0 0 18.5 9.25 9.25 0 0 0 0-18.5z", "M12 11v5.5", "M12 7.6v.1"]
  };
  function noticeIcon(level) {
    var ns = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true"); svg.setAttribute("class", "notice-icon");
    NOTICE_ICON[level].forEach(function (d) { var p = document.createElementNS(ns, "path"); p.setAttribute("d", d); svg.appendChild(p); });
    return svg;
  }

  /* Render a page. build(data, main) appends sections to main and may return masthead options. */
  N.page = function (defaults, build) {
    var data = N.load();
    var app = document.getElementById("app");
    N.meta = (data && data.meta) || {};
    if (N.meta.locale) document.documentElement.setAttribute("lang", N.meta.locale);
    if (N.meta.title) document.title = N.meta.title;
    var main = h("main", { id: "main" });
    var mastOpts = { title: N.meta.title || defaults.title };
    if (!data) {
      mastOpts.subtitle = "Waiting for data";
      main.appendChild(N.empty("This page has no data yet. Ask Atlas in chat to refresh it."));
    } else {
      try {
        var extra = build(data, main) || {};
        for (var k in extra) mastOpts[k] = extra[k];
      } catch (e) {
        main.appendChild(h("div", { class: "error-box", role: "alert" }, "Part of this page couldn't be displayed. Ask Atlas in chat to refresh it."));
        if (window.console) console.error(e);
      }
    }
    var notices = N.list(N.meta.notices);
    add(app, [
      h("a", { class: "skip", href: "#main" }, "Skip to content"),
      h("div", { class: "wrap" },
        N.masthead(mastOpts),
        notices.length ? h("ul", { class: "notices", "aria-label": "Notices" }, notices.map(function (n) {
          var level = NOTICE[n.level] ? n.level : "warn";
          return h("li", { class: "notice", "data-level": level, role: level === "error" ? "alert" : null },
            noticeIcon(level),
            h("p", null, h("b", null, NOTICE[level] + " "), N.rich(n.text)));
        })) : null,
        main,
        N.footer())
    ]);
  };
})();
