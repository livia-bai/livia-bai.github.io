# 🌷 我的个人网站

用 [GitHub Pages](https://pages.github.com/) + Jekyll 搭的作品集和博客，可爱温暖风，支持中英切换。

## 日常怎么改

| 想做什么 | 改哪个文件 |
| --- | --- |
| 改名字、头像、自我介绍、邮箱 | `_config.yml` |
| 加或改作品 | `_data/projects.yml` |
| 写新文章 | 在 `_posts/` 里新建一个 `.md` 文件，见下面「怎么发一篇新文章」 |
| 换配色 | `assets/css/style.css` 最上面的颜色 |
| 放图片 | 丢进 `assets/img/`，用 `/assets/img/文件名` 引用 |

改完提交到 GitHub，等 1～2 分钟网站就会自动更新。

## ✍️ 怎么发一篇新文章

**最简单的方法：直接在 GitHub 网页上操作**

1. 打开仓库，进入 `_posts` 文件夹，点右上角 **Add file → Create new file**
2. 文件名按这个格式写：`年-月-日-英文短标题.md`，比如 `2026-11-01-my-first-trip.md`
3. 内容最上面写一段「文章信息」，夹在两行 `---` 中间：

   ```yaml
   ---
   title: "文章标题"
   lang: zh          # 中文写 zh，英文写 en
   tags: [日常]
   ---
   ```

4. 下面空一行开始写正文，写完点 **Commit changes**，等 1～2 分钟就上线了

**正文用 Markdown 写，常用的几个：**

| 写法 | 效果 |
| --- | --- |
| `## 小标题` | 小标题 |
| `**加粗**` | **加粗** |
| `[文字](https://链接)` | 链接 |
| `![图片说明](/assets/img/图片.png)` | 插入图片（图片先上传到 `assets/img/`） |
| `> 一段引用` | 引用块 |
| `- 内容` | 列表 |

**写诗：** 想让每一行都单独换行，就把诗放进 `<div class="poem">诗的内容</div>` 里，参考 `_posts` 里的《那我也是树吗》。

**同一篇文章写中英两版：** 建两个文件，各自写 `lang: zh` / `lang: en`，再给它们写上一样的 `ref: 随便起个名字`。博客列表会按访客选的语言显示对应的那一版，文章页上也会出现「Read in English / 阅读中文版」的链接。

**同一天发了好几篇，想调顺序：** 在文章信息里加一行 `date: 2026-11-01 20:00:00 +0800`，时间越晚越靠前。

**删掉文章：** 在 GitHub 上打开那个文件，点右上角 `⋯` → **Delete file**，再点 Commit。

## 中英双语怎么用

- 页面上的固定文字都写成两份：`<span lang="zh">中文</span><span lang="en">English</span>`
- 文章开头写 `lang: zh` 或 `lang: en`
- 同一篇文章的两个语言版本写上相同的 `ref: 名字`，列表里就只显示访客当前语言的那一版

## 在自己电脑上预览（可选）

```bash
gem install jekyll
jekyll serve
# 打开 http://localhost:4000
```
