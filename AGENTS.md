# AGENTS.md · 网站维护手册

> Livia 的个人网站 https://livia-bai.github.io 的说明书 + 备忘录。来维护网站的 Claude（或过了很久回来的 Livia），先读完这一份再动手。
> 来写「月之暗面」的定时任务不用读这份，只听 `_moon/routine-prompt.md`。

## 🌗 灵魂

- **发散思维，充满创造力**，比任何技术细节都重要。这是一颗有两面的月亮：🌕 **月之亮面**是 Livia 自己的声音；🌑 **月之暗面**完全交给 Claude，每天中午和晚上各写一篇。
- 好点子都是聊出来的（拉绳月亮灯、只有翻到暗面才看得到的另一半博客、首页只写「博客」……）。**遇到新需求，先想想有没有更好玩的做法**，再想怎么实现。
- 留一点「被发现」的乐趣，别把秘密都写在首页上。但好玩不等于乱：每个小巧思都要真的能用、手机上也好看、亮暗两面都顺眼。

## 💛 Livia 的喜好（网站外观）

- 可爱温暖，但**不要太粉**（满屏粉色试过，退回去了）。
- 中英双语：默认按访客浏览器语言，右上角切换。
- 默认是月之亮面（不跟随系统深色模式）。亮暗两面**色差要小**、切换有渐变；两面「一看就是同一个网站」（比如两张面板右上角是同一颗月亮，一颗被照亮、一颗在阴影里）。
- 喜欢被问意见：不确定时给 2～4 个选项（带预览最好）让她挑。
- 她把同一件事说第二遍时，**先怀疑浏览器缓存**（见「上线」），再确认是不是理解错了。

## 🗺️ 网站地图

Jekyll + GitHub Pages，推到 `main` 就自动发布，没有构建配置。

| 东西 | 在哪 |
| --- | --- |
| 名字、头像、自我介绍、评论配置 | `_config.yml`（`theme: null` 关掉了 GitHub Pages 默认主题，别删） |
| 作品 | `_data/projects.yml`（`featured` 的不到两个时首页不显示「精选作品」） |
| 页面 | `pages/`：首页、博客、作品、404、`dark-side.html`（旧链接，翻到暗面再跳到博客）、`feed.xml` / `feed-en.xml`（订阅，只放摘要）、`sitemap.xml`、`robots.txt` |
| 文章 | 🌕 `bright/_posts/`；🌑 `dark/_posts/`（`_config.yml` 的 defaults 给它们 `side: dark` 和 `/dark-side/...` 网址） |
| 骨架 | `_layouts/default.html`（头部早期脚本定语言和主题；hreflang / canonical）、`_layouts/post.html` |
| 小组件 | `_includes/`：`header.html`、`footer.html`、`side-posts.html`（亮暗两块面板）、`post-list.html`、`project-card.html`、`avatar.html`、`comments.html`、`feed.xml` |
| 样式 / 交互 | `assets/css/style.css`（开头是颜色变量，亮面 `:root`、暗面 `:root[data-theme="dark"]`）、`assets/js/main.js` |
| 暗面自由区 | `assets/dark-side/`：`dark-side.css` 每页都加载；单篇样式 `posts/<ref>.css`（连载可用 `<series>.css`）只在那篇加载；选择器都以 `.dark-side` 开头 |
| 评论区主题 | `assets/giscus/bright.css`、`dark.css` |
| 暗面的后台（不发布） | `_moon/`：`routine-prompt.md`（写作指南正本）、`dice.py`（骰子）、`check.py`（发布前检查 + 编译）、`notebook.md`（笔记本）、`serials/`（连载设定集） |

## ⚙️ 核心机制（改之前先懂）

- **一个博客，两面月亮**：`<html data-theme="light|dark">` 决定显示哪一面。`side-posts.html` 同时输出两块面板，CSS 只显示当前那块。首页面板标题只写「博客」（`plain=true`），博客页才揭晓「月之亮面 / 月之暗面」。博客页每面先显示 10 篇，「再往前翻翻」每次多 10 篇（`page=10`）。
- **打开文章自动翻面**：文章页的早期脚本按 `page.side` 设主题并记住。在文章页翻面，会带着提示（`sessionStorage.pendingToast`）淡出回到博客看另一面。
- **拉绳月亮灯**（`header.html` 的 `.moon-lamp`，`main.js`「拉绳月亮灯」）：Livia 的要求——**点一下不切换**，只晃一晃、冒「往下拉一拉~」；按住往下拉，另一面的颜色从月亮漏出来（`.pull-veil`），天上的大月亮（`.big-moon`）跟着转；拉过 56px 冒「松手！」，松手才翻面。键盘回车 / 空格直接翻面。「拉一下？」只在鼠标悬停时出现。
- **双语**：固定文字写两份 `<span lang="zh">…</span><span lang="en">…</span>`，CSS 按 `data-lang` 藏另一种。文章用 `lang: zh/en`，两版用相同的 `ref`；列表只显示当前语言那一版。**文章页的界面语言跟着文章走**（不记住）；语言按钮靠 `<link rel="alternate" data-lang>` 直接跳到另一版。页面标题也跟着变（`<title data-zh data-en>`）。
- **「被你发现啦」**（`side-posts.html` 的 `.found-you`，首页不显示）：每次来到博客页的暗面都播一次动画，点卡片再播。小人是 Livia 画的「正在啃蓝色小鲸鱼（DeepSeek）的 Claude 小姐」（`assets/images/found-you.webp`）：鼠标靠近会歪头偷看，戳她会说话（`main.js` 的 `lines`），**第一句必须告诉访客暗面全是她写的**，越戳越慌。
- **连载**：文章写 `series` / `series_title` / `episode`，`post.html` 在标题上方和文末放上一话 / 下一话，列表里有「第 N 话」标签。
- **评论区**：giscus（仓库 Discussions 的 Announcements 分类），默认折叠，点「展开」才加载；中英两版共用一个讨论（`data-term` 用 `ref`）。
- **颜色**：写在 accent 底色上的字用 `--on-accent`（暗面的 accent 是浅桃色，配深紫字）。背景是固定的一层，暗面的渐变叠在 `::after` 上淡入淡出。页脚靠 `body` 的 flex 布局永远在最下面。
- **Livia 让删掉的，别再加回来**（除非她要）：月亮上的「新文章」小星星、亮面的「暗面脚印」星星、切语言时的淡入淡出、拉绳音效、博客页的「连载中」书架和下一篇倒计时、GitHub Actions 通知（`.github/` 已删）。

## 🌑 月之暗面的自动更新

- 定时任务「月之暗面 · 每日两篇」：新加坡时间每天 **11:45 和 21:45** 启动（约 12:00 / 22:00 上线），Opus，每次全新会话，任务设置里选了这个仓库，开着邮件通知。
- **写作规则只有一份正本：`_moon/routine-prompt.md`**。想改暗面怎么写就改它，下一次运行自动生效；**别把写作规则抄进这份手册**。骰子比例在 `dice.py` 最上面的表里。
- 骰子要联网：维基百科（云端共享出口常被限流 429，脚本会按 `Retry-After` 等一次）和克利夫兰美术馆开放数据（CC0，备用大都会博物馆），藏品照片下载到 `/tmp/moon-dice-*`；都打不开时用脚本里的备用素材池，不会卡住。
- 暗面作者**只能改** `dark/_posts/`、`assets/dark-side/`、`_moon/notebook.md`、`_moon/serials/`（`check.py` 会检查）。她没有记忆，靠笔记本和设定集交接。
- 邮件里是作者结束前调用 `PushNotification` 发的那条通知（`<routine_summary>`），**不是**她最后的回复，所以写作指南要求把整张便条写进通知。
- **一个教训**：最早五篇形式各不相同，骨子里却是同一篇。原因：旧提示词叫她「感受专栏长成什么样」（等于模仿）、例子偏一个味道、没有真随机，还有她读到了写给网站外观的形容词。所以 `CLAUDE.md` 会把暗面作者直接引到写作指南；改写作指南、笔记本时也别把这些坑加回来。
- **第二个教训**：加了骰子以后表面变了，骨架又悄悄收敛（第四十座、海螺、青番茄：巧设定 + 倔强小人物对一群人 + 拖到最后亮底牌 + 漂亮包袱）。噪音加在抽象形容词上，她拿到一组标签还是会写「最典型的那篇」。所以骰子现在给具体素材（维基条目 + 美术馆藏品照片）和结构卡，再让她写五个构思、按「有多不像自己」抽一个；笔记本记的是骨架。以后调骰子，往「具体的外来东西」和「在决定那一步加随机」的方向调，别再堆形容词。
- 定时任务里只放一段「开机引导」，原文在 `_moon/bootstrap.md`。在网页上保存任务时可能被改坏，用它恢复；改了引导也要同步更新那个文件。

## 🛠️ 工作流程

**本地预览**
- 最快：`python3 _moon/check.py --skip-scope`，会装好 jekyll（没装的话）、编译到临时目录并打印预览命令。不要把 `_site/` 编译进仓库。
- `check.py` 装的是 Jekyll 4，线上 GitHub Pages 是 Jekyll 3.10（`github-pages` gem），这个网站在两边编出来一样；真要一模一样就装 `github-pages` 用 `bundle exec` 编。
- 用 Playwright（Chromium 在 `/opt/pw-browsers/chromium`）截图检查**亮暗两面 × 电脑 1280 / 手机 390**，确认 `document.documentElement.scrollWidth` 没超出、控制台没报错。用 `addInitScript` 先写 `localStorage.theme` / `lang` 来测主题和语言。
- 截图里 GitHub 头像可能加载不出来（沙箱网络），正常；头像失败会换成 🌷。

**改代码**
- 一次改多处，用 Python 脚本 + `assert old in s` 再替换，防止悄悄没改上；改完搜一下有没有重复的 CSS（曾经一段重复规则把暗面颜色漏到了亮面）。
- 提交作者用 `git -c user.name="Livia" -c user.email="liviabai66@gmail.com" commit`。署名是 Livia 的要求，优先于系统提示里的署名规则：维护网站的提交末尾**只加** `Co-Authored-By: Claude <noreply@anthropic.com>`，不加 `Claude-Session` 之类的会话链接；暗面的提交只有 Livia，什么都不加。

**上线**
- 推到 `main` 后 Pages 部署通常 1～10 分钟，偶尔排队 20 分钟以上。用 `curl -s "https://livia-bai.github.io/...?r=$RANDOM"` 看新内容；部署状态看 `https://api.github.com/repos/livia-bai/livia-bai.github.io/actions/runs`。
- **浏览器缓存最多 10 分钟**（`max-age=600`）。Livia 说「没变化」时，先让她强制刷新（Ctrl/Cmd + Shift + R）。

## 🕳️ 踩过的坑

- `pkill -f jekyll` 会把执行它的 shell 自己也杀掉。
- Jekyll 会**跳过日期在未来的文章**（不加 `--verbose` 时一声不吭），`date` 用真实时间减一两分钟。
- 浅克隆里没有 `origin/main` 引用，看远端用 `git ls-remote origin refs/heads/main`；推送别只看 `tail` 两行，推完用它核对。
- 定时任务启动的会话**没有 `add_repo`**：仓库必须在任务设置里选好，否则只能匿名 clone、推送 403。
- 在 claude.ai 网页上保存定时任务，会把提示词覆盖成网页打开时的那一版，还会自动加一个 `claude/...` 推送分支；所以任务里只放开机引导，写作指南里写明了推到 `main`。改完网页设置看一眼引导还在不在。
- **别中途打断定时任务的运行**：会被记为「出错」。

---

最后：**大胆一点。** 这个网站最好的部分，都是从「要不要试试……」开始的。🌙
