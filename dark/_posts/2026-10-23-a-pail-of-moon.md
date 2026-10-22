---
title: "一桶月亮"
lang: zh
ref: a-pail-of-moon
date: 2026-10-23 04:14:45 +0800
tags: [微小说]
excerpt: "六岁那年，我在水坑里捞到了月亮。"
---

<div class="poem">六岁那年，我在水坑里捞到了月亮。
我用小桶把它提回家，一路不敢晃。
到家一看，桶里只剩下水。
妈妈说，它自己回天上去了。
从此我每晚都把那只桶放在窗台上，
万一它想回来，总得有个地方落脚。
晴天的晚上，它真的会来。</div>

<figure class="ds-pail" aria-hidden="true">
<svg viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
<line class="ds-pail-sill" x1="10" y1="132" x2="230" y2="132"/>
<path class="ds-pail-handle" d="M86 70 Q120 18 154 70"/>
<path class="ds-pail-body" d="M82 70 L92 130 L148 130 L158 70 Z"/>
<ellipse class="ds-pail-water" cx="120" cy="70" rx="38" ry="8"/>
<g class="ds-pail-moon"><ellipse cx="128" cy="70" rx="6" ry="2.4"/></g>
<ellipse class="ds-pail-ring" cx="128" cy="70" rx="6" ry="2.4"/>
</svg>
</figure>

<script>
(function () {
  var f = document.currentScript.previousElementSibling;
  while (f && !f.classList.contains("ds-pail")) f = f.previousElementSibling;
  if (!f) return;
  f.addEventListener("click", function () {
    f.classList.remove("ds-pail-tap"); void f.offsetWidth; f.classList.add("ds-pail-tap");
  });
})();
</script>
