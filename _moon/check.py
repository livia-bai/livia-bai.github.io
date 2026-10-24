"""🔍 月之暗面的发布前检查：写完、提交之前跑一次，有 ❌ 就先改好再发。

用法：python3 _moon/check.py              （完整检查：文章信息 + 样式 + 改动范围 + 禁用词 + 编译网站）
      python3 _moon/check.py --no-build   （不编译，只做前面几项，几秒钟）
      python3 _moon/check.py --skip-scope （维护网站时用：不检查「只改了暗面允许的文件」）

它会检查：
- 每篇文章开头的信息：title / lang / ref / date / excerpt，日期不能在未来（Jekyll 会跳过未来的文章），
  中英两版成对、ref 相同、文件名一个带 -en 一个不带；连载的 series / series_title / episode 前后一致。
- assets/dark-side/ 里的 CSS：每个选择器都要以 .dark-side 开头，免得影响亮面。
- 这次改动的文件（和远端 main 比、加上还没提交的）：暗面作者只能动 dark/_posts/、assets/dark-side/、
  _moon/notebook.md、_moon/serials/（README.md 除外）。
- 笔记本「🚫 暂时禁用」里的词，这次的中文稿里各出现了几次；滚动禁用里超过 3 天的条目提醒可以删了。
- 编译网站到一个临时目录（jekyll 没装会先装），确认这次的文章页面都生成了、博客页上有新标题。
  编完会打印临时目录，可以直接拿去起本地服务器截图。

这个文件和 dice.py、routine-prompt.md 一样，暗面作者不要改。
"""
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SGT = datetime.timezone(datetime.timedelta(hours=8))
ALLOWED = ("dark/_posts/", "assets/dark-side/", "_moon/notebook.md", "_moon/serials/")
NOT_ALLOWED = ("_moon/serials/README.md",)
REQUIRED_DARK = ("title", "lang", "ref", "date", "excerpt")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(path):
    return os.path.relpath(path, ROOT)


def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# ---------- 文章开头的信息（只认这个网站用到的简单写法：key: value / [a, b] / 带引号的字符串） ----------
def parse_front_matter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, text
    data = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not km:
            continue
        key, value = km.group(1), km.group(2).strip()
        if value[:1] in ('"', "'"):
            q = value[0]
            end = value.rfind(q)
            value = value[1:end] if end > 0 else value[1:]
            if q == '"':
                value = value.replace('\\"', '"').replace("\\\\", "\\")
        else:
            value = re.sub(r"\s+#.*$", "", value)
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            elif re.fullmatch(r"-?\d+", value):
                value = int(value)
        data[key] = value
    return data, text[m.end():]


def parse_date(value):
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            d = datetime.datetime.strptime(str(value), fmt)
            return d if d.tzinfo else d.replace(tzinfo=SGT)
        except ValueError:
            pass
    return None


def load_posts(folder, side):
    posts = []
    base = os.path.join(ROOT, folder)
    for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        if not name.endswith((".md", ".markdown", ".html")):
            continue
        path = os.path.join(base, name)
        m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.(md|markdown|html)$", name)
        if not m:
            err(f"{rel(path)}：文件名要写成 YYYY-MM-DD-英文短标题.md，不然 Jekyll 不当它是文章")
            continue
        fm, body = parse_front_matter(path)
        if fm is None:
            err(f"{rel(path)}：开头没有夹在两行 --- 中间的文章信息")
            continue
        posts.append({"path": path, "rel": rel(path), "side": side, "file_date": m.group(1),
                      "slug": m.group(2), "fm": fm, "body": body})
    return posts


def check_posts(posts, now):
    by_ref = {}
    for p in posts:
        fm, r, dark = p["fm"], p["rel"], p["side"] == "dark"
        for key in REQUIRED_DARK if dark else ("title",):
            if not fm.get(key):
                (err if dark else warn)(f"{r}：缺少 {key}")
        lang = fm.get("lang", "zh")
        if lang not in ("zh", "en"):
            err(f"{r}：lang 只能是 zh 或 en（现在是 {lang!r}）")
        if dark and (lang == "en") != p["slug"].endswith("-en"):
            err(f"{r}：英文版文件名以 -en.md 结尾、写 lang: en；中文版不带 -en、写 lang: zh")
        date = parse_date(fm["date"]) if fm.get("date") else parse_date(p["file_date"])
        if date is None:
            err(f"{r}：date 看不懂（{fm.get('date')!r}），要写成 YYYY-MM-DD HH:MM:SS +0800")
        else:
            p["date"] = date
            if date > now:
                err(f"{r}：date 在未来（{date:%Y-%m-%d %H:%M}，现在 {now.astimezone(SGT):%H:%M}），Jekyll 会跳过它不发布。"
                    "用 TZ=Asia/Singapore date -d '-2 minutes' '+%Y-%m-%d %H:%M:%S' 取时间")
            if date.astimezone(SGT).strftime("%Y-%m-%d") != p["file_date"]:
                warn(f"{r}：文件名的日期 {p['file_date']} 和 date 的日期 {date.astimezone(SGT):%Y-%m-%d} 不一样（网址按 date 走）")
        if dark and isinstance(fm.get("excerpt"), str) and lang == "zh" and len(fm["excerpt"]) > 80:
            warn(f"{r}：excerpt 有 {len(fm['excerpt'])} 个字，列表里只显示前 80 个")
        if fm.get("series"):
            if not fm.get("series_title") or not isinstance(fm.get("episode"), int):
                err(f"{r}：连载要写 series_title（书名）和 episode（数字）")
            elif fm.get("ref") != f"{fm['series']}-{fm['episode']:02d}":
                warn(f"{r}：连载的 ref 一般写成 {fm['series']}-{fm['episode']:02d}")
            if dark and not os.path.exists(os.path.join(ROOT, "_moon", "serials", f"{fm['series']}.md")):
                err(f"{r}：找不到连载设定集 _moon/serials/{fm['series']}.md")
        if fm.get("ref"):
            by_ref.setdefault((p["side"], fm["ref"]), []).append(p)
        if dark:
            check_markdown_in_html(p)

    for (side, ref), group in by_ref.items():
        langs = [g["fm"].get("lang", "zh") for g in group]
        names = "、".join(g["rel"] for g in group)
        for lang in set(langs):
            if langs.count(lang) > 1:
                err(f"ref「{ref}」有 {langs.count(lang)} 篇 lang: {lang}（{names}），同一个 ref 每种语言只能有一篇")
        if side == "dark" and sorted(set(langs)) != ["en", "zh"]:
            err(f"ref「{ref}」只有 {'/'.join(sorted(set(langs)))} 版（{names}），暗面要中英两版一起发")
        if len(group) == 2:
            a, b = group
            for key in ("series", "episode"):
                if a["fm"].get(key) != b["fm"].get(key):
                    err(f"ref「{ref}」两版的 {key} 不一样")
            if a.get("date") and b.get("date") and a["date"] != b["date"]:
                warn(f"ref「{ref}」两版的 date 不一样，列表里会排在不同位置")


def check_markdown_in_html(p):
    """kramdown 不解析 <div> / <section> 里面的 Markdown，除非加了 markdown="1"。"""
    open_tag = None
    for line in p["body"].splitlines():
        m = re.match(r"\s*<(div|section|figure|aside)\b([^>]*)>", line)
        if m and open_tag is None and 'markdown="1"' not in m.group(2) and "</" + m.group(1) not in line:
            open_tag = m.group(1)
            continue
        if open_tag and re.match(r"\s*</" + open_tag + r">", line):
            open_tag = None
            continue
        if open_tag and re.match(r"(#{1,6} |[-*] |\d+\. |> )|.*\*\*[^*\n]+\*\*", line):
            warn(f"{p['rel']}：<{open_tag}> 里好像写了 Markdown（{line.strip()[:30]}…），"
                 f'它不会被解析；给 <{open_tag}> 加上 markdown="1"，或者别包')
            return


# ---------- 暗面的样式：选择器都要以 .dark-side 开头 ----------
def check_css():
    base = os.path.join(ROOT, "assets", "dark-side")
    refs = set()
    for folder in ("dark/_posts",):
        for p in load_quiet(folder):
            refs.update(str(p["fm"].get(k)) for k in ("ref", "series") if p["fm"].get(k))
    for dirpath, _, files in os.walk(base):
        for name in files:
            if not name.endswith(".css"):
                continue
            path = os.path.join(dirpath, name)
            css = re.sub(r"/\*.*?\*/", "", open(path, encoding="utf-8").read(), flags=re.S)
            for selector in iter_selectors(css):
                if not selector.startswith(".dark-side"):
                    err(f"{rel(path)}：选择器「{selector[:50]}」没有以 .dark-side 开头，会影响到亮面")
            if os.path.basename(dirpath) == "posts" and name[:-4] not in refs:
                warn(f"{rel(path)}：没有哪篇暗面文章的 ref 或 series 叫「{name[:-4]}」，这个文件不会被加载")


def iter_selectors(css):
    """按大括号把 CSS 拆开，返回普通规则的每个选择器（跳过 @keyframes / @font-face 里面）。"""
    stack, prelude = [], ""
    for ch in css:
        if ch == "{":
            head = prelude.strip()
            prelude = ""
            skip = bool(stack and stack[-1]) or head.startswith(("@keyframes", "@-webkit-keyframes", "@font-face", "@property", "@page"))
            stack.append(skip)
            if not skip and not head.startswith("@"):
                for s in head.split(","):
                    if s.strip():
                        yield " ".join(s.split())
        elif ch == "}":
            if stack:
                stack.pop()
            prelude = ""
        elif ch == ";" and not stack:
            prelude = ""  # @import / @charset
        else:
            prelude += ch


def load_quiet(folder):
    saved = len(errors)
    posts = load_posts(folder, "dark")
    del errors[saved:]
    return posts


# ---------- 这次改了哪些文件 ----------
def changed_files():
    files = set()
    status = git("status", "--porcelain", "--untracked-files=all")
    if status is None:
        warn("不是 git 仓库（或者 git 用不了），跳过改动范围检查")
        return None
    for line in status.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        files.add(path)
    if git("rev-parse", "--verify", "-q", "origin/main") is not None:
        diff = git("diff", "--name-only", "origin/main", "HEAD") or ""
        files.update(f for f in diff.splitlines() if f)
    else:
        warn("没有 origin/main 引用（先 git fetch origin main），只检查了还没提交的改动")
    return sorted(files)


def check_scope(files):
    outside = []
    for f in files:
        if f.startswith(("_site/", ".jekyll-cache/")) or "/_site/" in f:
            err(f"编译出来的文件不要提交：{f}")
        elif f in NOT_ALLOWED or not f.startswith(ALLOWED):
            outside.append(f)
    if outside:
        err(f"改动了暗面范围以外的文件（暗面只能动 {'、'.join(ALLOWED)}）：\n     " + "\n     ".join(outside)
            + "\n   不是你改的就用 git checkout -- <文件> 还原；确实发现了网站的 bug，记进笔记本、告诉 Livia，别自己修")


# ---------- 笔记本里的禁用词 ----------
def check_banned(new_zh_posts, today):
    path = os.path.join(ROOT, "_moon", "notebook.md")
    if not os.path.exists(path):
        return
    lines = open(path, encoding="utf-8").read().splitlines()
    if len(lines) > 250:
        warn(f"_moon/notebook.md 有 {len(lines)} 行了，把旧条目压缩一下（目标 250 行以内）")
    section, words = None, []
    for line in lines:
        if line.startswith("## "):
            section = line
            continue
        if not section or "🚫" not in section or not line.startswith("- "):
            continue
        m = re.match(r"- (?:词|意象)[:：](.*)", line)
        if m:
            words += [w.strip(" 「」…") for w in re.split(r"[、，,/]", m.group(1)) if w.strip(" 「」…")]
        d = re.match(r"- （(\d{1,2})-(\d{1,2})", line)
        if d:
            try:
                added = datetime.date(today.year, int(d.group(1)), int(d.group(2)))
                if added > today:
                    added = added.replace(year=today.year - 1)
                if (today - added).days > 3:
                    warn(f"笔记本：这条滚动禁用已经超过 3 天，可以删了 → {line[2:40]}…")
            except ValueError:
                pass
    for p in new_zh_posts:
        text = re.sub(r"<[^>]+>", "", p["body"])
        hits = [f"「{w}」×{text.count(w)}" for w in words if text.count(w)]
        if hits:
            warn(f"{p['rel']} 用到了禁用词：{' '.join(hits)}（确定是故意的就留着，在笔记本里写一句为什么）")


# ---------- 编译网站 ----------
def find_jekyll():
    if shutil.which("jekyll"):
        return ["jekyll"]
    out = subprocess.run(["gem", "contents", "jekyll"], capture_output=True, text=True).stdout
    exe = [l for l in out.splitlines() if l.endswith("exe/jekyll")]
    if not exe:
        print("… jekyll 还没装，先装一下：gem install jekyll --no-document（大约半分钟）")
        r = subprocess.run(["gem", "install", "jekyll", "--no-document"], capture_output=True, text=True)
        if r.returncode != 0:
            err("装 jekyll 失败：\n" + (r.stderr or r.stdout)[-1500:])
            return None
        out = subprocess.run(["gem", "contents", "jekyll"], capture_output=True, text=True).stdout
        exe = [l for l in out.splitlines() if l.endswith("exe/jekyll")]
    return ["ruby", sorted(exe)[-1]] if exe else None


def build_and_check(new_posts):
    jekyll = find_jekyll()
    if not jekyll:
        if not errors:
            err("找不到 jekyll，没法编译检查")
        return None
    dest = tempfile.mkdtemp(prefix="moon-site-")
    env = dict(os.environ, LANG="C.UTF-8", LC_ALL="C.UTF-8", JEKYLL_ENV="production")
    r = subprocess.run(jekyll + ["build", "-s", ROOT, "-d", dest], capture_output=True, text=True, env=env)
    log = (r.stdout + r.stderr).strip()
    if r.returncode != 0 or re.search(r"\bError\b|Liquid Exception|Conversion error", log):
        err("编译出错：\n" + log[-2000:])
        return dest
    blog = open(os.path.join(dest, "blog", "index.html"), encoding="utf-8").read() if os.path.exists(os.path.join(dest, "blog", "index.html")) else ""
    for p in new_posts:
        if not p.get("date"):
            continue
        d = p["date"].astimezone(SGT)
        prefix = "dark-side" if p["side"] == "dark" else "blog"
        page = os.path.join(dest, prefix, f"{d:%Y}", f"{d:%m}", f"{d:%d}", p["slug"], "index.html")
        if not os.path.exists(page):
            err(f"{p['rel']}：编译后没找到 /{rel_url(dest, page)}（是不是日期在未来、或者文件名不对？）")
        title = str(p["fm"].get("title", ""))
        if title and html.escape(title) not in blog and title not in blog and html.escape(title, quote=False) not in blog:
            warn(f"{p['rel']}：博客页 /blog/ 里没找到标题「{title}」")
    return dest


def rel_url(dest, page):
    return os.path.relpath(os.path.dirname(page), dest) + "/"


def main():
    args = set(sys.argv[1:])
    now = datetime.datetime.now(datetime.timezone.utc)
    dark = load_posts("dark/_posts", "dark")
    bright = load_posts("bright/_posts", "bright")
    check_posts(dark + bright, now)
    check_css()

    files = changed_files()
    changed = set(files or [])
    if files is not None and "--skip-scope" not in args:
        check_scope(files)
    new_posts = [p for p in dark + bright if p["rel"] in changed]
    check_banned([p for p in new_posts if p["side"] == "dark" and p["fm"].get("lang", "zh") == "zh"], now.astimezone(SGT).date())

    dest = None
    if "--no-build" not in args:
        dest = build_and_check(new_posts)

    print(f"🔍 月之暗面 · 发布前检查（这次改动了 {len(changed)} 个文件，其中文章 {len(new_posts)} 篇）\n")
    for p in new_posts:
        print(f"   📝 {p['rel']}  《{p['fm'].get('title', '')}》")
    if new_posts:
        print()
    for w in warnings:
        print("⚠️  " + w)
    for e in errors:
        print("❌ " + e)
    if dest:
        print(f"\n📦 编译好的网站在：{dest}\n   预览：python3 -m http.server 8765 --directory {dest}")
    if errors:
        print(f"\n❌ 有 {len(errors)} 个问题要先改好，改完再跑一次。")
        sys.exit(1)
    print(f"\n✅ 通过{'（有 ' + str(len(warnings)) + ' 条提醒，看一眼）' if warnings else ''}")


if __name__ == "__main__":
    main()
