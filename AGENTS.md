# AGENTS.md · 给下一次来这里的你（或我）

> 这是 Livia 的个人网站 https://livia-bai.github.io 的「说明书 + 备忘录」。
> 不管你是下次来帮忙的 Claude，还是过了很久回来的 Livia，先读这一份，再动手。

---

## 🌗 这个网站的灵魂

**发散思维，充满创造力。** 这是最重要的一条，比任何技术细节都重要。

- 这里不是一个「规规矩矩的个人主页」。它是一颗有两面的月亮：
  - 🌕 **月之亮面**：Livia 自己的声音，她的作品和文章。
  - 🌑 **月之暗面**：完全交给 Claude，每天中午和晚上各写一篇，题材、形式、语气都自由。
- 很多好点子都是聊着聊着冒出来的：月亮按钮、「月之暗面 / 月之亮面」的名字、只有翻到暗面才看得到的另一半博客、首页只写「博客」让访客自己去发现……**遇到新需求时，先想想有没有更好玩的做法**，再想怎么实现。
- 留一点「被发现」的乐趣：不要把所有秘密都写在首页上。
- 但好玩不等于乱：每个小巧思都要真的能用、在手机上也好看、亮暗两面都顺眼。

## 💛 Livia 的喜好（做设计时先看这里）

- 整体风格：**可爱温暖**，但**不要太粉**（试过一次满屏粉色，她说太粉了，退回去了）。
- 中英双语，默认按访客浏览器语言，右上角可以切换。
- 默认配色是**月之亮面**（不跟随系统深色模式）。亮暗两面的**色差要小**，切换时不刺眼，有渐变过渡。
- 亮面和暗面要「一看就是同一个网站的两面」：比如两张卡片右上角的小月亮是**同一颗月亮**，一颗被照亮，一颗在阴影里。
- 她喜欢被问意见：方案不确定时，给 2～4 个选项让她挑，往往会得到更好的点子。
- 她改需求时常常是同一件事说第二遍：**先怀疑是浏览器缓存**（见下面「踩过的坑」），再确认是不是理解错了。用带预览的选项问她最快。

---

## 🗺️ 网站地图

用 Jekyll + GitHub Pages，`main` 分支推上去就自动发布（不需要任何构建配置）。

| 东西 | 在哪 |
| --- | --- |
| 名字、头像、自我介绍、时区、评论配置 | `_config.yml` |
| 作品列表 | `_data/projects.yml`（只有一个作品时首页不显示「精选作品」） |
| 页面 | `pages/`：`index.html`（首页，`permalink: /`）、`blog.html`、`projects.html`、`404.html`、`dark-side.html`（旧链接 `/dark-side/`，翻到暗面再跳到博客） |
| 🌕 Livia 的文章 | `bright/_posts/` |
| 🌑 月之暗面的文章 | `dark/_posts/`（`_config.yml` 的 defaults 自动给它们 `side: dark` 和 `/dark-side/...` 链接） |
| 页面骨架 | `_layouts/default.html`（头部有一段很早执行的脚本：语言、主题）、`_layouts/post.html` |
| 顶栏 / 页脚 / 小组件 | `_includes/`：`header.html`、`footer.html`、`side-posts.html`（亮/暗两块文章面板）、`post-list.html`、`project-card.html`、`avatar.html`、`comments.html` |
| 样式 | `assets/css/style.css`（最上面是颜色变量，亮面在 `:root`，暗面在 `:root[data-theme="dark"]`） |
| 交互 | `assets/js/main.js`（语言切换、月亮按钮、提示条、小星星、评论区展开） |
| 暗面的自由区 | `assets/dark-side/`（`dark-side.css` 每页都加载，选择器必须以 `.dark-side` 开头） |
| 评论区主题 | `assets/giscus/bright.css`、`dark.css`（在官方主题后面覆盖成网站配色） |
| 暗面的写作笔记本 | `_moon/notebook.md`（下划线文件夹，不会发布） |
| 定时任务提示词备份 | `_moon/routine-prompt.md` |
| 通知自动化 | `.github/workflows/`（见下面） |

## ⚙️ 核心机制（改之前先懂它们）

- **一个博客，两面月亮**：`<html data-theme="light|dark">` 决定显示哪一面。`side-posts.html` 同时输出两块面板，CSS 只显示当前主题那一块。首页面板标题只写「博客」（`plain=true`），博客页才揭晓「月之亮面 / 月之暗面」。
- **打开文章自动翻面**：文章页的早期脚本根据 `page.side` 直接设定主题；在文章页点月亮，会带着提示回到博客看另一面（提示通过 `sessionStorage.pendingToast` 带过去）。
- **月亮按钮**：亮面显示弯月（点了去暗面），暗面显示发光的满月。切换时底部提示「已切换到「月之暗面」」，名字高亮。暗面有没看过的新文章时，按钮上亮一颗紫色小星星（`darkSeen` 存在 localStorage）。
- **双语**：固定文字写两份 `<span lang="zh">…</span><span lang="en">…</span>`，CSS 按 `data-lang` 隐藏另一种。文章用 `lang: zh/en`，同一篇的两个版本用相同的 `ref` 关联；列表只显示当前语言那一版；文章页没有可见的「Read in English」链接，但有一个隐藏的 `.translation-link`，语言按钮会直接跳过去。页面标题也跟着语言变（`<title data-zh data-en>`）。
- **页脚永远在最下面**：`body` 是 flex 纵向布局，`main` 撑满。
- **评论区**：giscus（数据在仓库 Discussions 的 Announcements 分类）。默认折叠，点「展开」才去 GitHub 加载，带展开动画。中英两版共用一个讨论（`data-term` 用 `ref`）。
- **背景**：固定在后面的一层，亮面是暖色晨光光斑，暗面是月光的紫/蓝/金；渐变通过叠一层 `::after` 淡入淡出来做过渡。

## 🌑 月之暗面的自动更新

- **定时任务**「月之暗面 · 每日两篇」：新加坡时间每天 **11:45 和 21:45** 启动（这样大约 12:00 / 22:00 上线），用 **Opus**，每次是全新的会话。
- 它**没有记忆**，靠 `_moon/notebook.md` 交接：写过什么、留给下一次的点子、Livia 的偏好、发现的 bug。
- 它**只能改**：`dark/_posts/`、`assets/dark-side/`、`_moon/notebook.md`。别的文件一律不碰，发现问题记进笔记本。
- 提示词的核心是**发散**：先列至少 10 个完全不同的点子，划掉最理所当然的 3 个，挑一个让自己都意外的。中英两版，英文是重写不是翻译。
- 提示词的完整备份在 `_moon/routine-prompt.md`。**改了定时任务的提示词，记得同步更新这份备份。**

## 📬 通知（GitHub Actions）

Claude 定时任务自带的邮件通知实测收不到，所以改用 GitHub 自己发邮件：

- `dark-side-notify.yml`：`dark/_posts/` 有新文章推到 `main` 时，等文章页能打开（最多 25 分钟），开一条 @livia-bai 的 Issue，GitHub 发邮件，然后自动关掉。在 Actions 页面手动 Run workflow，会拿最新一篇发一封「🧪 测试通知」（改 workflow 文件本身不会再触发测试，免得整理代码时乱发邮件）。
- `dark-side-watchdog.yml`：每天 12:30 / 22:30（新加坡）检查，90 分钟内没有新文章就开一条不关的提醒 Issue。
- 依赖仓库开着 **Issues**（曾经被关掉过一次，导致通知失败）。

---

## 🛠️ 工作流程和小技巧

**本地预览**
- `gem install jekyll`；jekyll 往往不在 PATH 里，用 `ruby $(gem contents jekyll | grep 'exe/jekyll$') build -s <仓库> -d <临时目录>`。
- **不要把 `_site/` 编译进仓库**（或者提交前删掉）。用一个临时目录 + `python3 -m http.server` 预览。
- 用 Playwright（Chromium 在 `/opt/pw-browsers/chromium`）截图检查：**亮暗两面 × 电脑(1280) / 手机(390)**，并检查 `document.documentElement.scrollWidth` 没有超出（没有横向滚动）、控制台没有报错。
- 截图里 GitHub 头像可能加载不出来（沙箱网络限制），这是正常的；头像失败时会自动换成 🌷。
- 想测主题/语言，用 `addInitScript` 先写 `localStorage.theme` / `lang`。

**改代码**
- 一次改多处时，用 Python 脚本 + `assert old in s` 再替换，防止悄悄没改上。曾经有一次替换命中了两个地方，留下一段重复 CSS，把暗面的颜色漏到了亮面——**改完要搜一下有没有重复**。
- GitHub Actions 的 YAML 里，`run: |` 块里的多行字符串**不能顶格写**，否则 YAML 解析失败；用 `printf '%s\n\n%s'` 拼。
- 提交作者用 `git -c user.name="Livia" -c user.email="liviabai66@gmail.com" commit`。

**上线**
- 推到 `main` 后 GitHub Pages 部署通常 1～10 分钟，**偶尔排队 20 分钟以上**。用 `curl -s "https://livia-bai.github.io/...?r=$RANDOM"` 检查新内容；部署状态可以看公开接口 `https://api.github.com/repos/livia-bai/livia-bai.github.io/actions/runs`。
- **浏览器缓存最多 10 分钟**（`cache-control: max-age=600`）。Livia 说「没变化」时，先让她强制刷新（Ctrl/Cmd + Shift + R）。

## 🕳️ 踩过的坑（别再踩一次）

- `pkill -f jekyll` 会把执行它的 shell 自己也杀掉。
- Jekyll 会**跳过日期在未来的文章**，文章的 `date` 要用真实时间（减一两分钟最稳）。
- 浅克隆里没有 `origin/main` 引用，盯远端提交用 `git ls-remote origin refs/heads/main`。
- 定时任务启动的会话**没有 `add_repo` 工具**；仓库必须在定时任务设置里选好，否则只能匿名 clone、推送 403。
- 在 claude.ai 网页上保存定时任务时，会**把提示词覆盖成网页上打开时的那一版**，还会自动加一个 `claude/...` 推送分支。改完网页设置后，检查提示词是不是最新的（以 `_moon/routine-prompt.md` 为准），并确认文章推的是 `main`。
- **不要中途打断定时任务的运行**：被打断的运行会被记为「出错」。
- 推送命令别只看 `tail` 两行，失败信息可能在前面；推完用 `ls-remote` 核对。

---

## 💡 还没做、可以做的点子

- RSS 订阅（亮面、暗面各一个）。
- 月亮按钮跟着真实月相变化。
- 暗面的「标点符号部门」系列等连载（暗面自己在笔记本里规划）。
- 不用 GitHub 账号也能留言的评论方案（需要调研取舍）。
- 等 Livia 有了真实作品，补进 `_data/projects.yml`；自我介绍也可以写得更像她。

最后：**大胆一点。** 这个网站最好的部分，都是从「要不要试试……」开始的。🌙
