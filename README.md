# 🌷 我的个人网站

用 [GitHub Pages](https://pages.github.com/) + Jekyll 搭的作品集和博客，可爱温暖风，支持中英切换。

## 日常怎么改

| 想做什么 | 改哪个文件 |
| --- | --- |
| 改名字、头像、自我介绍、邮箱 | `_config.yml` |
| 加或改作品 | `_data/projects.yml` |
| 写新文章 | 在 `_posts/` 里新建 `年-月-日-标题.md`（参考里面的「小抄」那篇） |
| 换配色 | `assets/css/style.css` 最上面的颜色 |
| 放图片 | 丢进 `assets/img/`，用 `/assets/img/文件名` 引用 |

改完提交到 GitHub，等 1～2 分钟网站就会自动更新。

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
