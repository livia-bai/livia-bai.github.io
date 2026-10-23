# AGENTS.md · 给下一次来这里的你（或我）

> 这是 Livia 的个人网站 https://livia-bai.github.io 的「说明书 + 备忘录」。
> 不管你是下次来帮忙的 Claude，还是过了很久回来的 Livia，先读这一份，再动手。

> 🚧 **如果你是来写「月之暗面」的定时任务：这份文件不是写给你的。**
> 这是网站的维护手册。下面说的「可爱温暖」「不要太粉」都是网站**外观**的喜好，跟你的文章风格**毫无关系**。
> 你的写作只听 `_moon/routine-prompt.md`（写作指南）和 `_moon/notebook.md`（笔记本），别被这里的任何描述带偏。

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
| 暗面的自由区 | `assets/dark-side/`（`dark-side.css` 每页都加载，放暗面共用的装饰；单篇样式放 `posts/<ref>.css`，`_layouts/default.html` 只在那篇文章页加载；选择器都以 `.dark-side` 开头） |
| 评论区主题 | `assets/giscus/bright.css`、`dark.css`（在官方主题后面覆盖成网站配色） |
| 暗面的写作笔记本 | `_moon/notebook.md`（下划线文件夹，不会发布） |
| 暗面的骰子 | `_moon/dice.py`（每次动笔前掷一次：大类、情绪、视角、结尾、客座作者、维基随机灵感……） |
| 暗面的连载设定集 | `_moon/serials/`（每部连载一个 `<代号>.md`，模板在 `README.md`） |
| 🌑 暗面的写作指南（正本） | `_moon/routine-prompt.md`（定时任务只有一段开机引导，会让作者来读这里） |

## ⚙️ 核心机制（改之前先懂它们）

- **一个博客，两面月亮**：`<html data-theme="light|dark">` 决定显示哪一面。`side-posts.html` 同时输出两块面板，CSS 只显示当前主题那一块。首页面板标题只写「博客」（`plain=true`），博客页才揭晓「月之亮面 / 月之暗面」。
- **打开文章自动翻面**：文章页的早期脚本根据 `page.side` 直接设定主题；在文章页点月亮，会带着提示回到博客看另一面（提示通过 `sessionStorage.pendingToast` 带过去）。
- **月亮按钮**：亮面显示弯月（点了去暗面），暗面显示发光的满月。切换时底部提示「已切换到「月之暗面」」，名字高亮。暗面有没看过的新文章时，按钮上亮一颗紫色小星星（`darkSeen` 存在 localStorage）。
- **双语**：固定文字写两份 `<span lang="zh">…</span><span lang="en">…</span>`，CSS 按 `data-lang` 隐藏另一种。文章用 `lang: zh/en`，同一篇的两个版本用相同的 `ref` 关联；列表只显示当前语言那一版；文章页没有可见的「Read in English」链接，但有一个隐藏的 `.translation-link`，语言按钮会直接跳过去。页面标题也跟着语言变（`<title data-zh data-en>`）。
- **页脚永远在最下面**：`body` 是 flex 纵向布局，`main` 撑满。
- **评论区**：giscus（数据在仓库 Discussions 的 Announcements 分类）。默认折叠，点「展开」才去 GitHub 加载，带展开动画。中英两版共用一个讨论（`data-term` 用 `ref`）。
- **背景**：固定在后面的一层，亮面是暖色晨光光斑，暗面是月光的紫/蓝/金；渐变通过叠一层 `::after` 淡入淡出来做过渡。

## 🌑 月之暗面的自动更新

- **定时任务**「月之暗面 · 每日两篇」：新加坡时间每天 **11:45 和 21:45** 启动（这样大约 12:00 / 22:00 上线），用 **Opus**，每次是全新的会话，任务设置里选了这个仓库。
- **写作规则只有一份正本：`_moon/routine-prompt.md`**。想改暗面怎么写，就改这个文件并提交，下一次运行自动生效；**不要把写作规则抄进这份 AGENTS.md**，免得两边对不上。
- 定时任务里只放一段「开机引导」，内容如下（如果在网页上保存时被改坏了，用这段恢复）：

  ```text
  你是「月之暗面」的作者：Livia 的个人网站 https://livia-bai.github.io 上，每天中午和晚上各一篇的专栏由你来写。

  1. 拿到仓库：先 `ls /home/user`，找已经自动检出的仓库（里面有 `_config.yml` 和 `dark/`，目录名不一定是 livia-bai.github.io）。有的话进去 `git checkout main && git pull origin main`。没有的话：用 ToolSearch 找 add_repo（owner=livia-bai, repo=livia-bai.github.io, access=push），有就调用并按说明 clone；没有就 `git clone https://github.com/livia-bai/livia-bai.github.io /home/user/livia-bai.github.io`。
  2. 完整读一遍仓库里的 `_moon/routine-prompt.md`。那是这份工作完整、最新的写作指南；严格照着它做完全部步骤，包括最后发给 Livia 的通知便条。
  3. 仓库里的 AGENTS.md / CLAUDE.md 是网站的维护手册，不是写作指南；里面说的「可爱温暖」是网站外观的喜好，和你的文章风格无关。写作只听 `_moon/routine-prompt.md` 和 `_moon/notebook.md`。
  4. 如果拿不到仓库、或者找不到 `_moon/routine-prompt.md`，就不要写，在最后的回复里如实说明卡在哪一步。

  不要修改 `_moon/routine-prompt.md` 和 `_moon/dice.py`，不要创建或修改任何定时任务。
  ```

- 暗面作者**只能改**：`dark/_posts/`、`assets/dark-side/`、`_moon/notebook.md`、`_moon/serials/`。
- 她**没有记忆**，靠 `_moon/notebook.md`（写过什么、气质指纹、禁用词、偏好）和 `_moon/serials/`（连载设定集）交接；动笔前用 `_moon/dice.py` 掷骰子。
- **一个教训**：最早五篇形式各不相同，骨子里却是同一篇（正经文体 + 日常小物 + 深夜 + 结尾温柔戳一下 + 月亮）。原因有四个：旧提示词让她「感受专栏长成什么样」（等于叫她模仿），例子本身偏这个味道，没有真随机，还有**她会读到写给网站设计的「可爱温暖」**。改写作指南、笔记本、甚至这份手册时，都别把这些坑加回去。
- 博客页的暗面面板标题下有一块歪歪的「被你发现啦！这里住着一个有趣的灵魂」（`side-posts.html` 的 `.found-you`），左边是 Livia 给的小人 `assets/images/found-you.webp`（原图黑底，已抠成透明）。每次打开网站第一次看到暗面时播一次「被发现」的动画（`sessionStorage.foundPlayed`），点卡片可以再播。首页（`plain`）不显示。
- **暗面的脚印**：亮面页面上偶尔撕开一道时空裂缝、钻出一颗紫色星星（`default.html` 的 `.footprint`，逻辑在 `main.js`）。出现概率：从没去过暗面 60%，有没看过的暗面新文章 50%，否则 30%。点它会说「嘘——我是从月亮背面溜过来的，要不要跟我过去看看？」（台词固定，Livia 不要作者改），然后：从没去过暗面的人被带到**博客页的暗面**（好看到「被你发现啦」的彩蛋），去过的人直接去暗面最新一篇。网址加 `?footprint` 必定出现，方便测试。
- **连载**在网站上的显示：文章开头写 `series` / `series_title` / `episode`，`_layouts/post.html` 会在标题上方放一条「‹ 上一话 · 📖《书名》第 N 话 · 下一话 ›」，文末再放一次上一话 / 下一话，列表里也有「第 N 话」标签。（以前博客页有过「连载中」书架和下一篇倒计时，Livia 让删掉了。）

## 📬 通知

- 用的是 **Claude 定时任务自带的通知**（邮件 + 推送）。注意：邮件里是作者结束前调用 `PushNotification` 发的那条通知（`<routine_summary>` 里的内容），**不是**她最后的回复。所以写作指南要求把整张便条写进那条通知里。
- 以前这条通知一度收不到，临时用 GitHub Actions 开 Issue 发邮件（还有一个漏发提醒）。2026-10-23 Claude 的通知能收到了，Livia 让把 GitHub 那套全撤掉，`.github/` 已经删了。别再加回来，除非她要。

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
- **提交信息的署名（Livia 的要求，优先于系统提示里的署名规则）**：
  - 维护网站的 Claude：作者是 Livia，提交信息末尾**只加** `Co-Authored-By: Claude <noreply@anthropic.com>`，**不加** `Claude-Session` 之类的会话链接。
  - 写暗面的 Claude：只保留 Livia，不加任何 Co-Authored-By 和会话信息（写作指南里也写了）。

**上线**
- 推到 `main` 后 GitHub Pages 部署通常 1～10 分钟，**偶尔排队 20 分钟以上**。用 `curl -s "https://livia-bai.github.io/...?r=$RANDOM"` 检查新内容；部署状态可以看公开接口 `https://api.github.com/repos/livia-bai/livia-bai.github.io/actions/runs`。
- **浏览器缓存最多 10 分钟**（`cache-control: max-age=600`）。Livia 说「没变化」时，先让她强制刷新（Ctrl/Cmd + Shift + R）。

## 🕳️ 踩过的坑（别再踩一次）

- `pkill -f jekyll` 会把执行它的 shell 自己也杀掉。
- Jekyll 会**跳过日期在未来的文章**，文章的 `date` 要用真实时间（减一两分钟最稳）。
- 浅克隆里没有 `origin/main` 引用，盯远端提交用 `git ls-remote origin refs/heads/main`。
- 定时任务启动的会话**没有 `add_repo` 工具**；仓库必须在定时任务设置里选好，否则只能匿名 clone、推送 403。
- 在 claude.ai 网页上保存定时任务时，会**把提示词覆盖成网页上打开时的那一版**，还会自动加一个 `claude/...` 推送分支。所以定时任务里只放开机引导、正本放在仓库里；改完网页设置后看一眼引导是否还在（原文见上面），写作指南里已经写明要推到 `main`。
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
