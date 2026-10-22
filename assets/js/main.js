(function () {
  var root = document.documentElement;

  function getLang() { return root.getAttribute('data-lang') || 'zh'; }

  function setLang(lang) {
    root.setAttribute('data-lang', lang);
    root.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
    try { localStorage.setItem('lang', lang); } catch (e) {}
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

  setLang(getLang());
})();
