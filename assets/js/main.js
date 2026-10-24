(function () {
  var root = document.documentElement;

  function getLang() { return root.getAttribute('data-lang') || 'zh'; }

  // 换界面语言。文章页打开时跟着文章的语言走（不记住）；访客自己点了按钮才记住（remember）
  function setLang(lang, remember) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    if (remember) { try { localStorage.setItem('lang', lang); } catch (e) {} }
    var t = document.querySelector('title');
    if (t && t.dataset[lang]) document.title = t.dataset[lang];
    filterPosts();
    if (window.refreshLampHint) window.refreshLampHint();
  }

  // 同一篇文章有多个语言版本时，只显示当前语言那一版（没有对应翻译就显示原文）。
  // 列表有 data-limit：只留前几篇；有 data-page：先显示一页，点「再往前翻翻」再多显示一页
  function filterPosts() {
    var lang = getLang();
    document.querySelectorAll('.post-list').forEach(function (list) {
      var groups = new Map();
      list.querySelectorAll('.post-item').forEach(function (item) {
        var ref = item.getAttribute('data-ref');
        if (!groups.has(ref)) groups.set(ref, []);
        groups.get(ref).push(item);
      });
      var page = Number(list.getAttribute('data-page'));
      var limit = Number(list.getAttribute('data-limit')) || (page ? page * (Number(list.getAttribute('data-pages')) || 1) : Infinity);
      var shown = 0;
      groups.forEach(function (items) {
        var match = items.filter(function (i) { return i.getAttribute('data-lang') === lang; })[0] || items[0];
        if (shown >= limit) match = null; else shown++;
        items.forEach(function (i) { i.classList.toggle('is-hidden', i !== match); });
      });
      var more = list.nextElementSibling;
      if (more && more.classList.contains('more-posts')) more.hidden = groups.size <= limit;
    });
  }
  document.querySelectorAll('.more-posts button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var list = btn.closest('.more-posts').previousElementSibling;
      list.setAttribute('data-pages', (Number(list.getAttribute('data-pages')) || 1) + 1);
      filterPosts();
    });
  });

  var toggle = document.querySelector('.lang-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = getLang() === 'zh' ? 'en' : 'zh';
      // 在文章页切换语言时，如果有翻译版本就直接跳过去（链接在 default.html 的 <link rel="alternate">）
      var link = document.querySelector('link[rel="alternate"][data-lang="' + next + '"]');
      if (link) {
        // 直接去另一种语言的那一版，不在这一页先换一遍字（会闪一下）
        try { localStorage.setItem('lang', next); } catch (e) {}
        window.location.href = new URL(link.href).pathname;  // 只取路径：本地预览时也留在本地
        return;
      }
      setLang(next, true);
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

  var themeToggle = document.querySelector('.theme-toggle');
  var themeColor = document.querySelector('meta[name="theme-color"]');

  function setTheme(next) {
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    // 手机浏览器地址栏的颜色也跟着换（和 style.css 里的 --bg 一样）
    if (themeColor) themeColor.setAttribute('content', next === 'dark' ? '#443c4f' : '#fbf3ea');
    if (next === 'dark') playFound();
  }

  // 「被你发现啦」：每次来到博客页的暗面都播一次（打开页面时、或者在博客页翻到暗面时）；点卡片可以再看一次
  var found = document.querySelector('.found-you');
  function playFound() {
    if (!found || root.getAttribute('data-theme') !== 'dark') return;
    found.classList.remove('is-found');
    void found.offsetWidth;
    found.classList.add('is-found');
    clearTimeout(foundTimer);
    foundTimer = setTimeout(function () { found.classList.remove('is-found'); }, 2300);
  }
  // 播完（最慢的「!」大约 2.1 秒）就把动画收起来：不然翻到亮面再翻回来，卡片重新显示时会从头再播一遍
  var foundTimer;
  if (found) found.addEventListener('click', playFound);

  // 小人：鼠标靠近往那边偷看；戳一下缩一下、说一句（第一句告诉访客这一面是她写的）；连着戳会慌
  var mochi = found && found.querySelector('.found-mochi');
  if (mochi) {
    var talk = found.querySelector('.found-talk');
    var img = mochi.querySelector('img');
    var lines = {
      zh: ['唔？这一面的文章，全都是我写的哦！', '嚼嚼……', '我、我没有在偷吃！', '这条鲸鱼是自己游进来的！', '只尝一口，就一口！', '再戳就不分你吃了哦！'],
      en: ['Hm? Everything on this side? I wrote it all!', '*munch munch*', 'I-I wasn\'t snacking!', 'This whale swam in by itself!', 'Just one bite, I promise!', 'Poke again and you get none!']
    };
    var FLUSTER_FROM = 3;  // 从「我、我没有在偷吃！」开始慌
    var streak = 0, streakTimer, talkTimer;
    mochi.addEventListener('click', function (e) {
      e.stopPropagation();  // 戳小人不重播整张卡片
      streak++;
      clearTimeout(streakTimer);
      streakTimer = setTimeout(function () { streak = 0; }, 2500);
      var list = lines[getLang()] || lines.zh;
      talk.textContent = list[Math.min(streak, list.length) - 1];
      talk.classList.add('show');
      clearTimeout(talkTimer);
      talkTimer = setTimeout(function () { talk.classList.remove('show'); }, 1800);
      var cls = streak >= FLUSTER_FROM ? 'is-flustered' : 'is-poked';
      mochi.classList.remove('is-poked', 'is-flustered');
      void mochi.offsetWidth;
      mochi.classList.add(cls);
    });
    mochi.addEventListener('animationend', function (e) {
      if (e.target === img) mochi.classList.remove('is-poked', 'is-flustered');
    });
    var panel = found.closest('.side-panel') || found;
    panel.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse') return;
      var r = img.getBoundingClientRect();
      var dx = (e.clientX - (r.left + r.width / 2)) / 260, dy = (e.clientY - (r.top + r.height / 2)) / 400;
      dx = Math.max(-1, Math.min(1, dx));
      mochi.style.setProperty('--lean', (dx * 9 + Math.max(-1, Math.min(1, dy)) * 2).toFixed(1) + 'deg');
      mochi.style.setProperty('--lean-x', (dx * 4).toFixed(1) + 'px');
    });
    panel.addEventListener('pointerleave', function () {
      mochi.style.removeProperty('--lean');
      mochi.style.removeProperty('--lean-x');
    });
  }

  function flipTheme() {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    setTheme(next);
    // 在文章页翻面：这篇只属于原来那一面，所以带着提示回到博客，看另一面的文章。
    // 先在这一页把颜色慢慢换过去、内容淡出，再跳转；新页面会淡入，衔接起来就不突兀了
    if (document.body.hasAttribute('data-side')) {
      try { sessionStorage.setItem('pendingToast', next); } catch (e) {}
      leavePage((document.querySelector('.back') || {}).href || '/blog/');
      return;
    }
    announce(next);
  }

  // 离开这一页：内容先淡出，再跳转；下一页会淡入（default.html 里看到 fadeIn 就加 .is-arriving）
  function leavePage(href) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { window.location.href = href; return; }
    try { sessionStorage.setItem('fadeIn', '1'); } catch (e) {}
    root.classList.add('is-leaving-page');
    setTimeout(function () { window.location.href = href; }, 650);
  }

  // ========== 拉绳月亮灯 ==========
  // 点一下：只晃一晃，提示往下拉；按住往下拉：另一面的颜色从月亮里漏出来、天上的大月亮跟着转；
  // 拉过线（PULL_AT）再松手才翻面，没拉够就弹回去。键盘按回车 / 空格直接翻面。
  var lamp = document.querySelector('.moon-lamp');
  if (lamp && themeToggle) {
    var swing = lamp.querySelector('.lamp-swing');
    var hint = lamp.querySelector('.lamp-hint');
    var PULL_AT = 56, PULL_MAX = 92;
    var drag = null, hintTimer, nudgeTimer;
    var setHint = function (kind) {
      var lang = getLang();
      hint.textContent = hint.getAttribute('data-' + lang + '-' + kind) || '';
    };
    var setPull = function (px) {
      lamp.style.setProperty('--pull', px + 'px');
      root.style.setProperty('--peek', Math.min(1, px / PULL_AT).toFixed(3));
      var ready = px >= PULL_AT;
      if (ready !== lamp.classList.contains('is-ready')) {
        lamp.classList.toggle('is-ready', ready);
        setHint(ready ? 'ready' : 'idle');
      }
    };
    var flash = function (kind, ms) {
      setHint(kind);
      lamp.classList.add('show-hint');
      clearTimeout(hintTimer);
      hintTimer = setTimeout(function () { lamp.classList.remove('show-hint'); setHint('idle'); }, ms);
    };
    setHint('idle');
    window.refreshLampHint = function () { setHint(lamp.classList.contains('is-ready') ? 'ready' : 'idle'); };

    swing.addEventListener('pointerdown', function (e) {
      if (e.button > 0) return;
      var r = themeToggle.getBoundingClientRect();
      root.style.setProperty('--lamp-x', (r.left + r.width / 2) + 'px');
      root.style.setProperty('--lamp-y', (r.top + r.height / 2) + 'px');
      drag = { y: e.clientY, moved: false, pull: 0 };
      swing.setPointerCapture(e.pointerId);
      lamp.classList.add('is-dragging');
      root.classList.add('lamp-dragging');
      e.preventDefault();
    });
    swing.addEventListener('pointermove', function (e) {
      if (!drag) return;
      var dy = e.clientY - drag.y;
      if (Math.abs(dy) > 5) drag.moved = true;
      dy = Math.max(0, dy);
      // 拉过线以后越来越拉不动，像橡皮筋
      var px = dy <= PULL_AT ? dy : Math.min(PULL_MAX, PULL_AT + (dy - PULL_AT) * 0.35);
      drag.pull = px;
      setPull(px);
      if (drag.moved) lamp.classList.add('show-hint');
    });
    var endPull = function () {
      if (!drag) return;
      var d = drag;
      drag = null;
      lamp.classList.remove('is-dragging');
      root.classList.remove('lamp-dragging');
      setPull(0);
      if (!d.moved) {
        // 只是点了一下：晃一晃，告诉人家要往下拉
        lamp.classList.remove('is-nudged');
        void lamp.offsetWidth;
        lamp.classList.add('is-nudged');
        clearTimeout(nudgeTimer);
        nudgeTimer = setTimeout(function () { lamp.classList.remove('is-nudged'); }, 900);
        flash('tap', 1800);
        return;
      }
      lamp.classList.remove('show-hint');
      if (d.pull >= PULL_AT) {
        lamp.classList.add('is-swinging');
        setTimeout(function () { lamp.classList.remove('is-swinging'); }, 1400);
        flipTheme();
      }
    };
    swing.addEventListener('pointerup', endPull);
    swing.addEventListener('pointercancel', endPull);
    // 鼠标点击不翻面（交给上面的拉绳）；键盘触发的 click（detail 为 0）直接翻面
    themeToggle.addEventListener('click', function (e) { if (e.detail === 0) flipTheme(); });
  }

  try {
    var pending = sessionStorage.getItem('pendingToast');
    if (pending) { sessionStorage.removeItem('pendingToast'); setTimeout(function () { announce(pending); }, 150); }
  } catch (e) {}
  playFound();

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
