(function () {
  var root = document.documentElement;

  function getLang() { return root.getAttribute('data-lang') || 'zh'; }

  function setLang(lang) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    try { localStorage.setItem('lang', lang); } catch (e) {}
    var t = document.querySelector('title');
    if (t && t.dataset[lang]) document.title = t.dataset[lang];
    filterPosts();
  }

  // 同一篇文章有多个语言版本时，只显示当前语言那一版（没有对应翻译就显示原文）
  function filterPosts() {
    var lang = getLang();
    document.querySelectorAll('.post-list').forEach(function (list) {
      var groups = {};
      list.querySelectorAll('.post-item').forEach(function (item) {
        var ref = item.getAttribute('data-ref');
        (groups[ref] = groups[ref] || []).push(item);
      });
      Object.keys(groups).forEach(function (ref) {
        var items = groups[ref];
        var match = items.filter(function (i) { return i.getAttribute('data-lang') === lang; })[0] || items[0];
        items.forEach(function (i) { i.classList.toggle('is-hidden', i !== match); });
      });
    });
  }

  var toggle = document.querySelector('.lang-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = getLang() === 'zh' ? 'en' : 'zh';
      // 在文章页切换语言时，如果有翻译版本就直接跳过去
      var link = document.querySelector('.translation-link[data-target-lang="' + next + '"]');
      setLang(next);
      if (link) window.location.href = link.href;
    });
  }

  // ========== 月之暗面 / 月之亮面 ==========
  var toast = document.querySelector('.toast');
  var toastTimer;
  // before + 高亮的名字 + after
  function showToast(before, name, after) {
    if (!toast) return;
    var em = document.createElement('strong');
    em.className = 'toast-name';
    em.textContent = name;
    toast.textContent = '';
    toast.append(before, em, after || '');
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('show'); }, 2000);
  }

  var themeToggle = document.querySelector('.theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      var zh = getLang() === 'zh';
      if (next === 'dark') {
        zh ? showToast('🌑 已切换到', '「月之暗面」') : showToast('🌑 Switched to ', '“the Dark Side of the Moon”');
      } else {
        zh ? showToast('🌕 已切换到', '「月之亮面」') : showToast('🌕 Switched to ', '“the Bright Side of the Moon”');
      }
    });
  }

  // 没手动选过的话，跟着系统的深浅色变化
  try {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      var saved = null;
      try { saved = localStorage.getItem('theme'); } catch (err) {}
      if (!saved) root.setAttribute('data-theme', e.matches ? 'dark' : 'light');
    });
  } catch (e) {}

  setLang(getLang());
})();
