/* Nova dashboard runtime.
   CANONICAL COPY. Every template inlines this file verbatim inside
   <script id="nova-base-js">. Edit here, then run
   `python3 system/tests/dashboards/render.py --sync`.

   Safety: dashboard data comes from emails, documents, and meetings, so it is
   untrusted text. Everything is rendered with textContent / createElement,
   never parsed as HTML markup. No network calls, no connectors. Browser storage is used
   only for UI conveniences (theme, remembered filter) and is optional. */
(function () {
  "use strict";
  var N = (window.Nova = {});
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
    get: function (k) { try { return window.localStorage.getItem("nova:" + k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem("nova:" + k, v); } catch (e) { /* ignore */ } }
  };

  /* ---- Data ---- */
  N.load = function () {
    var node = document.getElementById("nova-data");
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

  /* ---- Record references ---- */
  var ID_RE = /\[\[([a-z]+\/[a-z0-9][a-z0-9-]*)\]\]/g;
  N.rid = function (id) {
    if (!id) return null;
    var text = "[[" + id + "]]";
    var base = N.meta.record_base_url;
    if (base && /^https:\/\//.test(base) && /^[a-z]+\/[a-z0-9][a-z0-9-]*$/.test(id)) {
      return h("a", { class: "rid", href: base + id + ".md", target: "_blank", rel: "noopener noreferrer", title: "Open the record file" }, text);
    }
    return h("code", { class: "rid", title: "Record ID: mention it in chat to ask Nova about it" }, text);
  };
  /* A file path in the user's repository (not a record), e.g. a prep note or profile file. */
  N.path = function (p) { return p ? h("code", { class: "rid", title: "File in your Nova repository" }, p) : null; };
  /* A ref is {id, title}. Renders the title followed by its ID. */
  N.ref = function (r, opts) {
    if (!r) return null;
    if (typeof r === "string") return N.rid(r);
    return h("span", { class: "ref" }, r.title || r.id, r.id && !(opts && opts.noId) ? [" ", N.rid(r.id)] : null);
  };
  N.refs = function (list) {
    list = N.list(list);
    var out = [];
    list.forEach(function (r, i) { if (i) out.push(", "); out.push(N.ref(r)); });
    return out;
  };
  N.name = function (r) { return r ? (typeof r === "string" ? r : r.title || r.id) : ""; };
  /* Plain text with [[type/slug]] mentions styled as IDs. */
  N.rich = function (text) {
    if (text == null) return null;
    text = String(text);
    var out = [], last = 0, m;
    ID_RE.lastIndex = 0;
    while ((m = ID_RE.exec(text))) {
      if (m.index > last) out.push(text.slice(last, m.index));
      out.push(N.rid(m[1]));
      last = m.index + m[0].length;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  };

  /* ---- Building blocks ---- */
  N.chip = function (text, tone) { return text ? h("span", { class: "chip", "data-tone": tone || null }, text) : null; };
  N.status = function (v) { return N.chip(N.label(v), N.tone(v)); };
  N.empty = function (text) { return h("p", { class: "empty" }, text); };
  N.more = function (key) {
    var n = (N.meta.truncated || {})[key];
    if (!n) return null;
    return h("p", { class: "more" }, n + " more not shown here. Ask Nova in chat to see them.");
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

  var STAR = "M12 1.5c.5 5.6 4.9 10 10.5 10.5-5.6.5-10 4.9-10.5 10.5C11.5 16.9 7.1 12.5 1.5 12 7.1 11.5 11.5 7.1 12 1.5z";
  function star() {
    var ns = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 24 24"); svg.setAttribute("aria-hidden", "true");
    var p = document.createElementNS(ns, "path"); p.setAttribute("d", STAR); svg.appendChild(p);
    return svg;
  }

  /* The standard refresh marker: when this page was last refreshed and by what, flagged when older
     than meta.stale_after_hours (from the contract). Staleness is the one thing measured against the
     viewer's clock: it is about how old the page is when someone opens it. */
  N.refreshedText = function () {
    var at = N.meta.generated_at;
    if (!at) return "Not refreshed yet";
    var by = N.meta.generated_by, who = "";
    if (by === "chat") who = " in chat";
    else if (by && /^routine:/.test(by)) who = " by the " + by.slice(8).replace(/-/g, " ") + " run";
    return "Refreshed " + N.weekday(at) + ", " + N.time(at) + who;
  };
  N.isStale = function () {
    var at = Date.parse(N.meta.generated_at || ""), limit = N.meta.stale_after_hours;
    return !isNaN(at) && typeof limit === "number" && limit > 0 && (Date.now() - at) / 36e5 > limit;
  };
  N.refreshed = function () {
    var stale = N.isStale();
    return h("p", { class: "mast-fresh", "data-stale": stale ? "1" : null },
      h("time", { datetime: N.meta.generated_at || null }, N.refreshedText()),
      stale ? N.chip("May be out of date", "warn") : null);
  };

  /* opts: {title, subtitle, lede, stats:[[value,label]]} */
  N.masthead = function (o) {
    var nav = N.list(N.meta.nav).filter(function (n) { return n && n.url && /^https:\/\//.test(n.url); });
    return h("header", { class: "mast" },
      h("div", { class: "mast-top" },
        h("p", { class: "mast-who" }, star(), N.meta.user_display_name ? "Nova for " + N.meta.user_display_name : "Nova"),
        N.refreshed()),
      h("h1", null, o.title),
      o.subtitle ? h("p", { class: "mast-sub" }, o.subtitle) : null,
      o.lede ? h("p", { class: "mast-lede" }, N.rich(o.lede)) : null,
      o.stats && o.stats.length ? h("ul", { class: "mast-stats" }, o.stats.map(function (s) {
        return h("li", null, h("b", null, String(s[0])), s[1]);
      })) : null,
      nav.length ? h("nav", { class: "mast-nav", "aria-label": "Other Nova pages" }, nav.map(function (n) {
        return h("a", { href: n.url, target: "_blank", rel: "noopener noreferrer", "aria-current": n.name === N.meta.dashboard ? "page" : null }, n.title || n.name);
      })) : null);
  };

  N.footer = function () {
    var at = N.meta.generated_at;
    return h("footer", { class: "foot" },
      h("p", null, (at ? "Refreshed " + N.dateY(at) + ", " + N.time(at) : "Not refreshed yet") + " · Ask Nova in chat to change anything"),
      h("p", { class: "chips" }, N.meta.nova_version ? h("span", null, "Nova " + N.meta.nova_version) : null, N.themeButton()));
  };

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
      main.appendChild(N.empty("This page has no data yet. Ask Nova in chat to refresh it."));
    } else {
      try {
        var extra = build(data, main) || {};
        for (var k in extra) mastOpts[k] = extra[k];
      } catch (e) {
        main.appendChild(h("div", { class: "error-box", role: "alert" }, "Part of this page couldn't be displayed. Ask Nova in chat to refresh it."));
        if (window.console) console.error(e);
      }
    }
    var notices = N.list(N.meta.notices);
    add(app, [
      h("a", { class: "skip", href: "#main" }, "Skip to content"),
      h("div", { class: "wrap" },
        N.masthead(mastOpts),
        notices.length ? h("ul", { class: "notices", "aria-label": "Notices" }, notices.map(function (n) {
          return h("li", { class: "notice", "data-level": n.level || "warn" }, N.rich(n.text));
        })) : null,
        main,
        N.footer())
    ]);
  };
})();
