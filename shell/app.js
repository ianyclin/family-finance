/* 家庭理財白話手冊 — 外殼腳本
   沒有任何外部相依。所有 localStorage 存取都包 try/catch；
   讀不到值時一律當作「沒填過」，畫面照常顯示。 */
(function () {
  "use strict";

  var NS = "ff:";
  var DESKTOP = "(min-width: 1024px)";

  /* ---------- localStorage（壞掉也不能拖垮頁面） ---------- */
  function lsGet(key) {
    try {
      return window.localStorage.getItem(NS + key);
    } catch (e) {
      return null;
    }
  }
  function lsSet(key, value) {
    try {
      window.localStorage.setItem(NS + key, value);
    } catch (e) {
      /* 無痕模式或配額滿：放棄保存，不影響閱讀 */
    }
  }
  function lsDel(key) {
    try {
      window.localStorage.removeItem(NS + key);
    } catch (e) {
      /* 同上 */
    }
  }

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }
  function scopeOf(el) {
    var sec = el.closest ? el.closest("section.chapter") : null;
    return (sec && sec.id) || "doc";
  }
  function isDesktop() {
    return window.matchMedia && window.matchMedia(DESKTOP).matches;
  }

  /* ---------- 1. ul.checks：加真正的 checkbox 並記住 ---------- */
  function initChecks() {
    var counters = {};
    each(document.querySelectorAll("ul.checks > li"), function (li) {
      if (li.querySelector('input[type="checkbox"]')) return;
      var scope = scopeOf(li);
      counters[scope] = (counters[scope] || 0) + 1;
      var key = "chk:" + scope + ":" + counters[scope];

      // 用 span + aria-labelledby，不用 <label>：清單項目裡可能有章節連結，
      // 包在 label 裡點連結會順手勾掉框。
      var text = document.createElement("span");
      text.className = "check-text";
      text.id = "chk-text-" + scope + "-" + counters[scope];
      while (li.firstChild) text.appendChild(li.firstChild);

      var box = document.createElement("input");
      box.type = "checkbox";
      box.id = "chk-" + scope + "-" + counters[scope];
      box.setAttribute("aria-labelledby", text.id);
      box.checked = lsGet(key) === "1";
      li.classList.toggle("is-done", box.checked);

      box.addEventListener("change", function () {
        li.classList.toggle("is-done", box.checked);
        if (box.checked) lsSet(key, "1");
        else lsDel(key);
      });

      li.appendChild(box);
      li.appendChild(text);
    });
  }

  /* ---------- 2. td.blank：可填、可記 ---------- */
  function initBlanks() {
    var counters = {};
    each(document.querySelectorAll("td.blank"), function (td) {
      var scope = scopeOf(td);
      counters[scope] = (counters[scope] || 0) + 1;
      var key = "blank:" + scope + ":" + counters[scope];

      // 可編輯的是格子裡的 span，不是 td。
      // 把 role="textbox" 放在 td 上會蓋掉它的 cell 角色，
      // 螢幕閱讀器讀這張表就會少一格。
      if (td.querySelector(".blank-input")) return;
      var field = document.createElement("span");
      field.className = "blank-input";
      field.setAttribute("contenteditable", "true");
      field.setAttribute("spellcheck", "false");
      field.setAttribute("role", "textbox");
      field.setAttribute("aria-label", blankLabel(td));
      field.style.display = "block";
      field.style.minHeight = "1.4em";
      while (td.firstChild) field.appendChild(td.firstChild);

      var saved = lsGet(key);
      if (saved) field.textContent = saved;
      td.appendChild(field);

      var timer = null;
      function save() {
        var v = field.textContent.replace(/\s+$/, "");
        if (v) lsSet(key, v);
        else lsDel(key);
      }
      field.addEventListener("input", function () {
        if (timer) window.clearTimeout(timer);
        timer = window.setTimeout(save, 400);
      });
      // 樣式表的 :focus 規則掛在 td 上，換成 span 後這裡自己補上。
      field.addEventListener("focus", function () {
        field.style.background = "var(--teal-soft)";
        field.style.outline = "2px solid var(--teal)";
      });
      field.addEventListener("blur", function () {
        field.style.background = "";
        field.style.outline = "";
        if (timer) window.clearTimeout(timer);
        save();
      });
    });
  }

  function blankLabel(td) {
    var row = td.closest ? td.closest("tr") : null;
    var th = row ? row.querySelector("th") : null;
    return th ? th.textContent.trim() + "：填寫欄" : "填寫欄";
  }

  /* ---------- 3. 章節完成度：側欄 ↔ 健檢進度表 ---------- */
  var doneInputs = {}; // chapterId -> [input, ...]

  function registerDone(chId, input) {
    if (!doneInputs[chId]) doneInputs[chId] = [];
    doneInputs[chId].push(input);
    input.checked = lsGet("done:" + chId) === "1";
    input.addEventListener("change", function () {
      setDone(chId, input.checked);
    });
  }

  function setDone(chId, value) {
    if (value) lsSet("done:" + chId, "1");
    else lsDel("done:" + chId);
    each(doneInputs[chId] || [], function (other) {
      if (other.checked !== value) other.checked = value;
    });
  }

  function initNavDone() {
    each(document.querySelectorAll(".sitenav input[data-ch]"), function (input) {
      registerDone(input.getAttribute("data-ch"), input);
    });
  }

  function initCheckupTable() {
    each(document.querySelectorAll("table.checkup-table tbody tr"), function (row, i) {
      var cells = row.querySelectorAll("td");
      if (!cells.length) return;
      var cell = cells[cells.length - 1];
      if (cell.querySelector('input[type="checkbox"]')) return;
      var link = row.querySelector('a[href^="#ch-"]');
      var chId = link ? link.getAttribute("href").slice(1) : "checkup-" + (i + 1);
      var box = document.createElement("input");
      box.type = "checkbox";
      box.setAttribute("data-ch", chId);
      box.setAttribute("aria-label", rowLabel(row) + " 完成");
      cell.classList.add("done-cell");
      cell.appendChild(box);
      registerDone(chId, box);
    });
  }

  function rowLabel(row) {
    var first = row.querySelector("th, td");
    return first ? first.textContent.trim() : "本列";
  }

  /* ---------- 4. 頂端列「第 N 章／共 M」＋ 側欄目前章節 ---------- */
  function initWhere() {
    var out = document.querySelector(".topbar .where");
    var sections = document.querySelectorAll("section.chapter");
    if (!sections.length) return;

    var root = document.querySelector("[data-total-chapters]");
    var total = root ? root.getAttribute("data-total-chapters") : String(sections.length);
    var navItems = document.querySelectorAll(".sitenav .nav-item");
    var lastId = null;

    function label(sec) {
      var n = sec.getAttribute("data-num");
      if (sec.getAttribute("data-stage") === "8") return "附錄";
      if (n === "0") return "導讀";
      return "第 " + String(parseInt(n, 10) || "?") + " 章";
    }

    function update() {
      var top = 0;
      try {
        top = parseFloat(
          getComputedStyle(document.documentElement).getPropertyValue("--topbar-h")
        ) || 52;
      } catch (e) {
        top = 52;
      }
      var current = sections[0];
      each(sections, function (sec) {
        if (sec.getBoundingClientRect().top <= top + 8) current = sec;
      });
      if (current.id === lastId) return;
      lastId = current.id;
      if (out) out.textContent = label(current) + "／共 " + total;
      each(navItems, function (item) {
        item.classList.toggle("is-current", item.getAttribute("data-ch") === current.id);
      });
    }

    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(update, {
        rootMargin: "-52px 0px -60% 0px",
        threshold: [0, 1],
      });
      each(sections, function (sec) {
        io.observe(sec);
      });
    } else {
      window.addEventListener("scroll", update, { passive: true });
    }
    window.addEventListener("hashchange", update);
    update();
  }

  /* ---------- 5. 抽屜式目錄 ---------- */
  function initDrawer() {
    var nav = document.querySelector(".sitenav");
    var btn = document.querySelector(".toc-btn");
    var scrim = document.querySelector(".scrim");
    var closeBtn = document.querySelector(".nav-close");
    if (!nav || !btn) return;

    function open() {
      if (isDesktop()) return;
      nav.classList.add("is-open");
      if (scrim) scrim.classList.add("is-open");
      btn.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
      var first = nav.querySelector(".nav-close, a, input");
      if (first) first.focus();
    }
    function close(returnFocus) {
      nav.classList.remove("is-open");
      if (scrim) scrim.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
      if (returnFocus) btn.focus();
    }

    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function () {
      if (nav.classList.contains("is-open")) close(true);
      else open();
    });
    if (closeBtn) closeBtn.addEventListener("click", function () { close(true); });
    if (scrim) scrim.addEventListener("click", function () { close(false); });
    nav.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a") && !isDesktop()) close(false);
    });
    document.addEventListener("keydown", function (e) {
      if (!nav.classList.contains("is-open")) return;
      if (e.key === "Escape") {
        close(true);
        return;
      }
      if (e.key !== "Tab") return;
      // 抽屜開著時把焦點關在抽屜裡
      var items = nav.querySelectorAll("button, a[href], input");
      if (!items.length) return;
      var first = items[0];
      var last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
    // 手機開著抽屜時轉成桌機寬度：把狀態收乾淨，免得 body 卡住不能捲
    if (window.matchMedia) {
      var mq = window.matchMedia(DESKTOP);
      var onChange = function (ev) { if (ev.matches) close(false); };
      if (mq.addEventListener) mq.addEventListener("change", onChange);
      else if (mq.addListener) mq.addListener(onChange);
    }
  }

  /* ---------- 6. dfn 名詞浮層 ---------- */
  function initTerms() {
    var data = {};
    var el = document.getElementById("glossary-json");
    if (!el) return;
    try {
      data = JSON.parse(el.textContent || "{}");
    } catch (e) {
      return; // 名詞表壞了就完全不加互動
    }

    var pop = null;
    var opener = null;

    function build() {
      pop = document.createElement("div");
      pop.className = "term-pop";
      pop.setAttribute("role", "dialog");
      pop.setAttribute("aria-label", "名詞解釋");
      pop.setAttribute("tabindex", "-1");
      var close = document.createElement("button");
      close.type = "button";
      close.className = "term-close";
      close.textContent = "關閉";
      close.addEventListener("click", function () { hide(true); });
      var word = document.createElement("span");
      word.className = "term-word";
      var def = document.createElement("span");
      def.className = "term-def";
      pop.appendChild(close);
      pop.appendChild(word);
      pop.appendChild(def);
      document.body.appendChild(pop);
      pop._word = word;
      pop._def = def;
    }

    function show(dfn, term) {
      if (!pop) build();
      pop._word.textContent = term;
      pop._def.textContent = data[term];
      pop.style.visibility = "hidden";
      pop.classList.add("is-open");
      var r = dfn.getBoundingClientRect();
      var top = r.bottom + window.pageYOffset + 6;
      var left = r.left + window.pageXOffset;
      var maxLeft = document.documentElement.clientWidth - pop.offsetWidth - 12;
      if (left > maxLeft) left = Math.max(12, maxLeft);
      pop.style.top = top + "px";
      pop.style.left = left + "px";
      pop.style.visibility = "";
      if (opener) opener.setAttribute("aria-expanded", "false");
      opener = dfn;
      dfn.setAttribute("aria-expanded", "true");
      pop.focus();
    }

    function hide(returnFocus) {
      if (!pop) return;
      pop.classList.remove("is-open");
      pop.style.top = "-9999px";
      if (opener) {
        opener.setAttribute("aria-expanded", "false");
        if (returnFocus) opener.focus();
        opener = null;
      }
    }

    each(document.querySelectorAll("dfn[data-term]"), function (dfn) {
      var term = dfn.getAttribute("data-term");
      if (!Object.prototype.hasOwnProperty.call(data, term)) return; // 名詞表沒有這個詞就不加互動
      dfn.setAttribute("data-has-def", "1");
      dfn.setAttribute("tabindex", "0");
      dfn.setAttribute("role", "button");
      dfn.setAttribute("aria-expanded", "false");
      dfn.addEventListener("click", function () {
        if (opener === dfn) hide(true);
        else show(dfn, term);
      });
      dfn.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (opener === dfn) hide(true);
          else show(dfn, term);
        }
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && opener) hide(true);
    });
    document.addEventListener("click", function (e) {
      if (!opener) return;
      if (e.target === opener || (e.target.closest && (e.target.closest("dfn") === opener || e.target.closest(".term-pop")))) return;
      hide(false);
    });
    window.addEventListener("resize", function () { if (opener) hide(false); });
  }

  /* ---------- 起動 ---------- */
  function boot() {
    initChecks();
    initBlanks();
    initNavDone();
    initCheckupTable();
    initWhere();
    initDrawer();
    initTerms();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
