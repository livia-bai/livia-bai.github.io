/* 2026-11-03《原位》/ In Situ：读者替发掘队挑下一步，故事按点的顺序一段段往下接。
   没有 JS（或 RSS）时，所有段落按原顺序全显示，就是一篇普通的文章。 */
(function () {
  var root = document.querySelector('.ds-situ');
  if (!root) return;

  var scenes = Array.prototype.slice.call(root.querySelectorAll('.ds-situ-scene'));
  var intro = root.querySelector('.ds-situ-scene[data-id="intro"]');
  if (!intro) return;

  var parts = (root.getAttribute('data-clock') || '11:20').split(':');
  var minutes = parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
  var step = parseInt(root.getAttribute('data-step') || '10', 10);
  var used = {};

  function fmt(m) {
    var h = Math.floor(m / 60), mm = m % 60;
    return h + ':' + (mm < 10 ? '0' : '') + mm;
  }

  root.classList.add('ds-situ-on');
  intro.classList.add('ds-situ-shown');

  var clock = document.createElement('p');
  clock.className = 'ds-situ-clock';
  clock.setAttribute('aria-live', 'polite');
  root.insertBefore(clock, root.firstChild);

  var menu = document.createElement('div');
  menu.className = 'ds-situ-menu';
  root.appendChild(menu);

  function drawClock() {
    clock.innerHTML = '<span class="ds-situ-now">' + fmt(minutes) + '</span>' +
      '<span class="ds-situ-due">' + (root.getAttribute('data-time') || '') + '</span>';
  }

  function available(s) {
    var id = s.getAttribute('data-id');
    if (id === 'intro' || used[id]) return false;
    var req = s.getAttribute('data-req');
    return !req || used[req];
  }

  function drawMenu() {
    menu.innerHTML = '';
    var ask = document.createElement('p');
    ask.className = 'ds-situ-ask';
    var n = Object.keys(used).length;
    ask.textContent = n ? root.getAttribute('data-ask2') : root.getAttribute('data-ask');
    menu.appendChild(ask);
    var list = document.createElement('div');
    list.className = 'ds-situ-opts';
    scenes.forEach(function (s) {
      if (s.getAttribute('data-id') === 'intro') return;
      var id = s.getAttribute('data-id');
      if (s.getAttribute('data-req') && !used[s.getAttribute('data-req')]) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ds-situ-opt' + (s.getAttribute('data-req') ? ' ds-situ-new' : '');
      b.innerHTML = '<span class="ds-situ-who">' + s.getAttribute('data-who') + '</span>' +
        '<span class="ds-situ-what">' + s.getAttribute('data-label') + '</span>';
      if (!available(s)) {
        b.disabled = true;
        b.classList.add('ds-situ-done');
      } else {
        b.addEventListener('click', function () { choose(s); });
      }
      list.appendChild(b);
    });
    menu.appendChild(list);
  }

  function choose(s) {
    used[s.getAttribute('data-id')] = true;
    var h = s.querySelector('.ds-situ-h');
    if (h && !h.querySelector('.ds-situ-t')) {
      var t = document.createElement('span');
      t.className = 'ds-situ-t';
      t.textContent = fmt(minutes);
      h.insertBefore(t, h.firstChild);
    }
    root.insertBefore(s, menu);
    s.classList.add('ds-situ-shown');
    if (s.getAttribute('data-end')) {
      menu.parentNode.removeChild(menu);
      root.classList.add('ds-situ-over');
    } else {
      minutes += step;
      drawClock();
      drawMenu();
    }
    if (h) {
      h.setAttribute('tabindex', '-1');
      try { h.focus({ preventScroll: true }); } catch (e) { /* 老浏览器 */ }
      h.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  drawClock();
  drawMenu();
})();
