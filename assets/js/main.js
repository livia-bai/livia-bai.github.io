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

  // 同一篇文章有多个语言版本时，只显示当前语言那一版（没有对应翻译就显示原文）；列表有 data-limit 时只留前几篇
  function filterPosts() {
    var lang = getLang();
    document.querySelectorAll('.post-list').forEach(function (list) {
      var groups = {};
      list.querySelectorAll('.post-item').forEach(function (item) {
        var ref = item.getAttribute('data-ref');
        (groups[ref] = groups[ref] || []).push(item);
      });
      var limit = Number(list.getAttribute('data-limit')) || Infinity, shown = 0;
      Object.keys(groups).forEach(function (ref) {
        var items = groups[ref];
        var match = items.filter(function (i) { return i.getAttribute('data-lang') === lang; })[0] || items[0];
        if (shown >= limit) match = null; else shown++;
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

  function announce(theme) {
    var zh = getLang() === 'zh';
    if (theme === 'dark') {
      zh ? showToast('🌑 已切换到', '「月之暗面」') : showToast('🌑 Switched to ', '“the Dark Side of the Moon”');
    } else {
      zh ? showToast('🌕 已切换到', '「月之亮面」') : showToast('🌕 Switched to ', '“the Bright Side of the Moon”');
    }
  }

  // 月之暗面有新文章、而你还没翻过去看时，月亮按钮上亮一颗小星星
  var themeToggle = document.querySelector('.theme-toggle');
  var latestDark = themeToggle ? Number(themeToggle.getAttribute('data-latest-dark')) || 0 : 0;
  function updateNewMark() {
    if (!themeToggle || !latestDark) return;
    var seen = 0;
    try { seen = Number(localStorage.getItem('darkSeen')) || 0; } catch (e) {}
    if (root.getAttribute('data-theme') === 'dark') {
      try { localStorage.setItem('darkSeen', String(latestDark)); } catch (e) {}
      seen = latestDark;
    }
    var fresh = Date.now() / 1000 - latestDark < 7 * 24 * 3600;
    themeToggle.classList.toggle('has-new', fresh && latestDark > seen);
  }

  function setTheme(next) {
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    updateNewMark();
  }

  function flipTheme() {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    setTheme(next);
    // 在文章页翻面：这篇只属于原来那一面，所以带着提示回到博客，看另一面的文章
    if (document.body.hasAttribute('data-side')) {
      try { sessionStorage.setItem('pendingToast', next); } catch (e) {}
      window.location.href = (document.querySelector('.back') || {}).href || '/blog/';
      return;
    }
    announce(next);
  }

  if (themeToggle) themeToggle.addEventListener('click', flipTheme);

  try {
    var pending = sessionStorage.getItem('pendingToast');
    if (pending) { sessionStorage.removeItem('pendingToast'); setTimeout(function () { announce(pending); }, 150); }
  } catch (e) {}
  updateNewMark();

  // ========== 评论区（giscus）==========
  var mount = document.querySelector('.giscus-mount');
  function giscusTheme() {
    return mount.getAttribute(root.getAttribute('data-theme') === 'dark' ? 'data-theme-dark' : 'data-theme-bright');
  }
  function giscusLang() { return getLang() === 'zh' ? 'zh-CN' : 'en'; }
  var loaded = false;
  function loadGiscus() {
    if (loaded) return;
    loaded = true;
    var g = document.createElement('script');
    g.src = 'https://giscus.app/client.js';
    g.async = true;
    g.crossOrigin = 'anonymous';
    var attrs = {
      'data-repo': mount.dataset.repo, 'data-repo-id': mount.dataset.repoId,
      'data-category': mount.dataset.category, 'data-category-id': mount.dataset.categoryId,
      'data-mapping': 'specific', 'data-term': mount.dataset.term, 'data-strict': '1',
      'data-reactions-enabled': '1', 'data-emit-metadata': '0', 'data-input-position': 'top',
      'data-theme': giscusTheme(), 'data-lang': giscusLang()
    };
    Object.keys(attrs).forEach(function (k) { g.setAttribute(k, attrs[k]); });
    mount.appendChild(g);
  }
  // 留言区默认收起；点一下展开时才从 GitHub 加载
  var comments = document.querySelector('.comments');
  var commentsToggle = document.querySelector('.comments-toggle');
  if (mount && comments && commentsToggle) {
    commentsToggle.addEventListener('click', function () {
      var open = !comments.classList.contains('is-open');
      comments.classList.toggle('is-open', open);
      commentsToggle.setAttribute('aria-expanded', String(open));
      if (open) loadGiscus();
    });
    // giscus 加载好之后，把「取信中」的小提示藏起来
    window.addEventListener('message', function (e) {
      if (e.origin === 'https://giscus.app') comments.classList.add('is-loaded');
    });
  }
  function updateGiscus() {
    var frame = document.querySelector('iframe.giscus-frame');
    if (frame && frame.contentWindow) {
      frame.contentWindow.postMessage({ giscus: { setConfig: { theme: giscusTheme(), lang: giscusLang() } } }, 'https://giscus.app');
    }
  }
  if (toggle) toggle.addEventListener('click', updateGiscus);

  setLang(getLang());
})();
