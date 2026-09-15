/* 投資專篇《隔離人性》— 外殼行為
   不載入任何外部程式庫。三件事：名詞浮層、目錄標示目前位置、列印前收掉浮層。
   任何一段壞掉都不影響閱讀：全部包在 try/catch 或存在性檢查裡。 */
(function () {
  "use strict";

  function each(list, fn) {
    for (var i = 0; i < list.length; i++) fn(list[i], i);
  }

  /* ---------- 1. 名詞浮層 ----------
     解釋的來源有兩個，依序取：dfn 的 title 屬性（組裝腳本填的），
     或內嵌的 terms-json（組裝腳本從 concept 段落抽出的句子）。 */
  function initTerms() {
    var data = {};
    var el = document.getElementById("terms-json");
    if (el) {
      try {
        data = JSON.parse(el.textContent || "{}");
      } catch (e) {
        data = {};
      }
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

    function show(dfn, text) {
      if (!pop) build();
      pop._word.textContent = (dfn.textContent || "").trim();
      pop._def.textContent = text;
      pop.style.visibility = "hidden";     // 先量寬度，避免在舊位置閃一下
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
        if (returnFocus && opener.focus) opener.focus();
        opener = null;
      }
    }

    each(document.querySelectorAll("dfn"), function (dfn) {
      var text = dfn.getAttribute("title") || data[dfn.id] || data[(dfn.textContent || "").trim()];
      if (!text) return;                   // 沒有解釋就完全不加互動
      dfn.removeAttribute("title");        // 換成浮層，避免瀏覽器原生提示重複
      dfn.setAttribute("data-has-def", "1");
      dfn.setAttribute("tabindex", "0");
      dfn.setAttribute("role", "button");
      dfn.setAttribute("aria-expanded", "false");
      dfn.addEventListener("click", function () {
        if (opener === dfn) hide(true); else show(dfn, text);
      });
      dfn.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (opener === dfn) hide(true); else show(dfn, text);
        }
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") hide(true);
    });
    document.addEventListener("click", function (e) {
      if (!pop || !opener) return;
      if (pop.contains(e.target) || opener.contains(e.target)) return;
      hide(false);
    });
    window.addEventListener("beforeprint", function () { hide(false); });
  }

  /* ---------- 2. 目錄標示目前這一節 ---------- */
  function initToc() {
    var links = document.querySelectorAll(".toc a[href^='#']");
    if (!links.length || !("IntersectionObserver" in window)) return;
    var map = {};
    each(links, function (a) {
      var id = a.getAttribute("href").slice(1);
      if (id) map[id] = a.parentNode;
    });
    var io = new IntersectionObserver(function (entries) {
      each(entries, function (en) {
        var li = map[en.target.id];
        if (!li) return;
        if (en.isIntersecting) {
          each(document.querySelectorAll(".toc li.is-current"), function (x) {
            x.classList.remove("is-current");
          });
          li.classList.add("is-current");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    each(document.querySelectorAll("section.part[id]"), function (s) { io.observe(s); });
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    try { initTerms(); } catch (e) { /* 名詞浮層壞掉不影響閱讀 */ }
    try { initToc(); } catch (e) { /* 目錄標示壞掉不影響閱讀 */ }
  });
})();
