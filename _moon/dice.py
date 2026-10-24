"""🎲 月之暗面的骰子：动笔前掷一次，决定这一篇写什么；想好五个构思之后再掷一次，决定写哪一个。

用法：python3 _moon/dice.py                        第一次：大类、素材包、结构卡，外加几条建议
      python3 _moon/dice.py noon|night             （手动指定中午场 / 晚上场；不写就按新加坡时间判断）
      python3 _moon/dice.py pick 40 25 15 12 8     第二次：五个构思各自「没有骰子时你有多大可能写它」的百分比，
                                                   按顺序传进来；骰子抽一个，越不像你的越容易被抽中

为什么这样掷：
- 同一个作者每次从零开始写，会回到自己最舒服的那种声音。随机能把她推开，但噪音加在哪里很重要。
- 抽象的形容词（「暴躁又好笑」「大反转」）每一条都会被她翻译成心里最典型的那个版本；拿到一组标签，
  她还是会写「这组标签下最可能的那个故事」。表面在变，骨架在收敛（第四十座、海螺、青番茄就是这样）。
- 所以这里少放形容词，多放真实世界里的具体东西（维基随机条目、美术馆随机藏品和它的照片），
  再抽一张打破常见骨架的「结构卡」；最后在「写哪个构思」这一步也掷一次，不让第一个想到的点子自动胜出。
- 「硬规则」最多违背一项；「建议」最多违背两条（违背了什么，在笔记本里写一句为什么）。

想调整比例或加新选项，直接改下面的表：每一项是 (选项, 中午权重, 晚上权重)。
长度表多一列：这个长度适合哪几个大类（写大类开头的几个字），免得抽到「连载 + 一百字」这种只能违背的组合。
"""
import datetime
import json
import os
import random
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

rng = random.SystemRandom()

# ---------- 这一篇写哪一大类（故事类占大头；荒诞的「伪文体」封顶很低） ----------
CATEGORY = [
    ("连载小说：续写一部正在连载的（如果 _moon/serials/ 里有），否则新开一部", 26, 26),
    ("短篇小说：有人物、有对话、有冲突、有转折的完整故事", 24, 24),
    ("剧本 / 对话体 / 相声 / 脱口秀稿", 9, 7),
    ("互动小说或小游戏：读者点选项走分支，或者一个能玩的解谜", 9, 9),
    ("诗 / 歌词 / 说唱 / 童谣", 9, 10),
    ("非虚构：科普、冷知识深挖、认真的评测、虚构人物的访谈", 10, 8),
    ("伪文体：说明书、启事、预报、展品说明这一类（最近用得太多，少来）", 3, 3),
    ("自由发挥：发明一种从没见过的形式", 10, 13),
]

SERIAL_GENRE = [
    ("异世界穿越", 1, 1), ("武侠江湖", 1, 1), ("硬科幻", 1, 1), ("太空歌剧", 1, 1),
    ("本格推理", 1, 1), ("都市怪谈 / 恐怖", 0.5, 1.5), ("校园青春", 1, 1), ("甜甜的恋爱", 1, 1),
    ("末日求生", 1, 1), ("架空宫廷权谋", 1, 1), ("蒸汽朋克", 1, 1), ("赛博朋克", 1, 1),
    ("童话冒险", 1, 1), ("美食番", 1.5, 0.5), ("热血体育", 1.5, 0.5), ("魔法学院", 1, 1),
    ("西部荒野", 1, 1), ("海盗与宝藏", 1, 1),
]

# ---------- 结构卡：故事怎么动（硬规则）。专门拆「巧设定 + 关键的东西拖到最后亮出来 + 漂亮包袱收尾」这副骨架 ----------
STRUCTURE = [
    ("不反转：事情照最直白的方式发生，好看全靠人物和细节；结尾不许出现「原来……」", 1.2, 1.2),
    ("主角在开头就得到了想要的东西，麻烦从得到以后才开始", 1, 1),
    ("主角输了，而且输得有道理；不安慰，不翻盘", 0.8, 1.2),
    ("两边都对：冲突的双方各有道理，故事不替任何一边赢", 1, 1),
    ("一个场景，实时发生：不跳时间、不换地点", 1, 1),
    ("时间跨得很长：几十年、几代人或者几百年，只停在几个瞬间", 1, 1),
    ("倒着讲：从结局开始，一段一段往回走", 0.8, 1),
    ("高潮放在正中间，后一半写后果", 1, 1),
    ("一件具体的手艺活从头做到尾，故事在手上推进（怎么做、做坏了怎么办）", 1, 1),
    ("一样东西在好几个人手里传，每一段换一个人", 1, 1),
    ("主角做了一个错误的决定，故事认真地跟着这个错误走到底", 1, 1),
    ("读者从第一段就知道一件主角不知道的事", 0.8, 1.2),
    ("没有坏人：麻烦来自天气、身体、距离、规矩，或者时间不够", 1, 1),
    ("两条线平行地走，到最后也不交汇", 0.8, 1),
    ("什么都没解决，但有一个人变了", 0.8, 1.2),
    ("第一句就说出结局，悬念换成「怎么会这样」", 1, 1),
    ("讲到一半换主角：一个原本不起眼的配角接过故事", 1, 1),
    ("很多个很短的片段，拼起来才看得懂", 0.8, 1),
]

# ---------- 建议 ----------
MOOD = [
    ("狂喜，高兴得停不下来", 1.2, 0.8), ("暴躁又好笑", 1, 0.8), ("毛骨悚然", 0.4, 1.5),
    ("热血燃起来", 1.2, 0.8), ("无厘头", 1, 0.6), ("得意洋洋、臭屁", 0.8, 0.6),
    ("酸溜溜的嫉妒", 1, 1), ("紧张刺激", 1, 1.5), ("甜", 1, 1), ("慌慌张张", 1, 0.8),
    ("真的难过，不找补", 0.6, 1.2), ("悲壮", 0.6, 1), ("懒洋洋", 0.8, 0.8),
    ("好奇心爆棚", 1.2, 1), ("阴谋的味道", 0.6, 1.2), ("怒气冲冲", 1, 1),
    ("尴尬到脚趾抠地", 1, 1), ("冷冰冰、不带感情", 0.6, 1), ("庄严", 0.6, 0.8),
    ("温柔怅惘", 0.2, 0.3),  # 前五篇写够了，权重压低
]

VOICE = [
    ("第一人称：主角自己说", 1, 1), ("第三人称", 1.2, 1.2), ("群像：好几个人轮流出场", 1, 1),
    ("反派的视角", 0.8, 1), ("非人类的视角（动物、机器、外星人、一把椅子……）", 1, 1),
    ("书信 / 日记 / 聊天记录拼起来", 0.8, 0.8), ("第二人称「你」", 0.2, 0.3),  # 「你」也写够了
]

LENGTH = [
    ("一百字以内", 1, 1, "诗 伪文体 自由"),
    ("五百字左右", 1.5, 1.5, "短篇 剧本 互动 诗 非虚构 伪文体 自由"),
    ("一千五百字左右", 1.5, 1.5, "连载 短篇 剧本 互动 非虚构 伪文体 自由"),
    ("三千字以上", 1, 1, "连载 短篇 剧本 非虚构 自由"),
]

GUEST = [
    "暴躁的米其林主厨", "过分热情的导游", "三岁小孩", "古代史官", "体育解说员", "退休的海盗",
    "新手魔法师", "八卦记者", "严肃的昆虫学家", "说唱歌手", "爱写弹幕的网友", "侦探小说迷老太太",
    "第一次来地球的外星实习生", "武侠小说里的店小二", "总想升职的小公务员", "失忆的超级英雄",
    "博物馆保安", "猫", "幼儿园老师", "相声演员", "末日电台主持人", "中世纪吟游诗人",
    "健身教练", "考古学家", "外卖骑手", "AI 客服（但很有脾气）",
    "写了四十年判决书的老法官", "十九世纪的博物学家", "钢琴调音师", "货轮上的轮机长",
    "第一次写信的十岁小孩", "说话很慢的老木匠", "急诊科护士", "马戏团的驯兽师",
]

GUEST_CHANCE = 0.25  # 有客座作者的概率（客座多半是搞笑的人设，太常出现会把每篇都推向段子）

# 维基百科 / 美术馆都打不开时的备用素材：只放具体的东西，不放「有意境」的词
FALLBACK_SEEDS = [
    "冷库", "钟表发条", "蚁群的分工", "拍卖师的报价", "盐田", "养蜂人的喷烟器", "潜水钟", "竹编",
    "排球拦网", "邮政编码", "冰川漂砾", "染坊", "集装箱码头", "会移动的沙丘", "镜子工厂", "地衣",
    "铁路道岔", "面包的发酵", "电报密码本", "灭火器", "风洞", "跳蚤市场", "铜锣", "孵蛋器",
    "海关检疫", "缝纫机踏板", "射箭的靶心", "柴窑", "高压电塔", "活字印刷", "冻土", "舞狮",
    "蝴蝶标本", "水磨坊", "珊瑚产卵", "考古探方", "马拉松补给站", "录音棚的隔音棉", "探空气球",
    "炼钢炉", "旋转门", "赛鸽", "胶片冲洗", "龙舟", "下水道", "天平", "熨斗", "雪崩预警",
    "驯鹰", "空调外机", "失重飞机", "热气球", "樟脑丸", "地图上的陷阱街", "赌场发牌员",
    "电梯检修", "红绿灯的配时", "牙医的钻头", "香料贸易", "防空洞改的蘑菇农场",
]

HEADERS = {"User-Agent": "LiviaSiteDice/1.2 (https://livia-bai.github.io)"}

# 维基随机条目里跳过这些（标题、分类、简介里出现就换一个）：政治和战争碰不得，消歧义页和列表没东西可用
WIKI_SKIP = (
    "政治", "政党", "政黨", "选举", "選舉", "议员", "議員", "总统", "總統", "总理", "總理", "首相",
    "部长", "部長", "国会", "國會", "立法会", "立法會", "外交官", "主席", "书记", "書記", "政府",
    "战争", "戰爭", "战役", "戰役", "军事", "軍事", "恐怖", "屠杀", "屠殺", "抗议", "抗議", "示威",
    "革命", "政变", "政變", "消歧义", "消歧義", "列表", "年表",
)


def pick(table, slot, category=None):
    col = 1 if slot == "noon" else 2
    rows = [row for row in table if category is None or len(row) < 4 or any(category.startswith(k) for k in row[3].split())]
    return rng.choices([row[0] for row in rows], weights=[row[col] for row in rows])[0]


def fetch(url, timeout=15):
    """打开网址；对方说「太多请求」（429）时，按它说的等一会儿再试一次。"""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        wait = e.headers.get("Retry-After", "")
        if e.code != 429 or not wait.isdigit() or int(wait) > 60:
            raise
        time.sleep(int(wait) + 1)
        return urllib.request.urlopen(req, timeout=timeout)


def squash(text, limit):
    text = " ".join(re.sub(r"<[^>]+>", "", text or "").split())
    return text if len(text) <= limit else text[:limit].rstrip() + "……"


def wiki_seed():
    """维基百科（简体中文）的随机条目和开头一段：一次请求拿十个，跳过政治、战争、消歧义页。"""
    try:
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "random", "grnnamespace": 0, "grnlimit": 10,
            "prop": "extracts|info|categories", "inprop": "url", "exintro": 1, "explaintext": 1,
            "exchars": 200, "exlimit": 10, "cllimit": "max", "clshow": "!hidden",
            "variant": "zh-cn", "converttitles": 1,
        })
        with fetch("https://zh.wikipedia.org/w/api.php?" + query) as r:
            pages = list(json.load(r)["query"]["pages"].values())
        good = []
        for page in pages:
            text = page["title"] + " ".join(c["title"] for c in page.get("categories", [])) + (page.get("extract") or "")
            if not any(word in text for word in WIKI_SKIP):
                good.append(page)
        good.sort(key=lambda p: not (p.get("extract") or "").strip())  # 有简介的排前面
        if good:
            page = good[0]
            intro = squash(page.get("extract"), 160)
            return f"{page['title']}（{page['fullurl']}）" + (f"\n     简介：{intro}" if intro else "")
    except Exception:
        pass
    try:
        # 退一步：只拿随机条目的标题（这一步没法过滤，碰到政治就只借一个无关的细节）
        with fetch("https://zh.wikipedia.org/wiki/Special:Random") as r:
            url = r.geturl()
        title = urllib.parse.unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")
        return f"{title}（{url}）"
    except Exception:
        return None


def save_image(url, folder):
    path = os.path.join(folder, "museum" + (os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".jpg"))
    with fetch(url, timeout=30) as r, open(path, "wb") as f:
        f.write(r.read())
    return path


def cleveland():
    """克利夫兰美术馆开放数据（CC0）：有图的藏品里随机抽一件。"""
    def get(skip):
        with fetch(f"https://openaccess-api.clevelandart.org/api/artworks/?has_image=1&cc0=1&limit=1&skip={skip}") as r:
            return json.load(r)
    data = get(rng.randrange(40000))
    if not data.get("data"):
        data = get(rng.randrange(max(1, data["info"]["total"])))
    a = data["data"][0]
    culture = "、".join(a.get("culture") or [])
    facts = " · ".join(x for x in (a.get("creation_date"), culture, a.get("type"), a.get("technique")) if x)
    about = a.get("description") or a.get("did_you_know") or ""
    return a["title"], facts, squash(about, 220), a["images"]["web"]["url"], a.get("url")


def met():
    """备用：大都会艺术博物馆开放数据，随机编号试几次，要公有领域、有图的。"""
    for _ in range(6):
        try:
            with fetch(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{rng.randrange(1, 900000)}") as r:
                a = json.load(r)
        except urllib.error.HTTPError:
            continue
        if a.get("isPublicDomain") and a.get("primaryImageSmall"):
            facts = " · ".join(x for x in (a.get("objectDate"), a.get("culture") or a.get("country"), a.get("objectName"), a.get("medium")) if x)
            return a["title"], facts, "", a["primaryImageSmall"], a.get("objectURL")
    raise RuntimeError("Met: 没抽到有图的藏品")


def museum_seed():
    """美术馆的一件随机藏品，图片下载到临时目录（不在仓库里）给作者看。"""
    for source in (cleveland, met):
        try:
            title, facts, about, image, page = source()
        except Exception:
            continue
        lines = [f"{title}（{facts}）"]
        if about:
            lines.append(f"     说明：{about}")
        try:
            lines.append(f"     图片：{save_image(image, tempfile.mkdtemp(prefix='moon-dice-'))}  ← 用 Read 打开看一眼")
        except Exception:
            lines.append(f"     图片：{image}（没下载成功，能打开就看一眼）")
        if page:
            lines.append(f"     来源：{page}")
        return "\n".join(lines)
    return None


def roll(slot):
    category = pick(CATEGORY, slot)
    spare = rng.sample(FALLBACK_SEEDS, 2)
    wiki = wiki_seed() or f"{spare[0]}（维基百科没打开，这是备用素材池里抽的）"
    museum = museum_seed() or f"{spare[1]}（美术馆没打开，这是备用素材池里抽的）"
    lines = [
        f"🎲 月之暗面 · {'中午场' if slot == 'noon' else '晚上场'}的骰子",
        "",
        "【硬规则：最多违背一项】",
        f"- 大类：{category}",
    ]
    if category.startswith("连载"):
        lines.append(f"- （如果要新开连载）题材：{pick(SERIAL_GENRE, slot)}")
    lines += [
        "- 素材包（两样真实世界里的东西，至少一样要长进故事的骨头里）：",
        f"  1. 维基随机条目：{wiki}",
        f"  2. 美术馆随机藏品：{museum}",
        f"- 结构卡：{pick(STRUCTURE, slot)}",
        "",
        "【建议：最多违背两条】",
        f"- 情绪：{pick(MOOD, slot)}",
        f"- 视角：{pick(VOICE, slot)}",
        f"- 长度：{pick(LENGTH, slot, category)}",
    ]
    if rng.random() < GUEST_CHANCE:
        lines.append(f"- 客座作者：用「{rng.choice(GUEST)}」的口吻和脑回路来写")
    else:
        lines.append("- 客座作者：这次没有，用你自己的声音（但别是前几篇那种声音）")
    lines += [
        "",
        "素材要用在骨头上：决定主角是谁、想要什么、或者事情为什么出错。只拿来当名字、摆设、文末小注不算。",
        "  有图就打开看：颜色、材料、手势、画面角落里的小东西，都可以拿来用。",
        "  碰到政治、战争或真实的私人个体，只借一个无关的细节（颜色、材料、年份、一个动作）。",
        "续写连载时，题材和设定按连载本身来；素材包和结构卡用在这一话里。",
        "",
        "下一步（别写第一个想到的）：照上面写下五个骨架各不相同的构思，每个后面老实标一个百分比——",
        "  「没有这次骰子，我有多大可能写出它」。然后按顺序运行：python3 _moon/dice.py pick 百分比1 百分比2 …",
        "这一轮不要重掷。",
    ]
    print("\n".join(lines))


def pick_idea(args):
    try:
        odds = [float(a.rstrip("%％")) for a in args]
    except ValueError:
        odds = []
    if len(odds) < 3 or any(p <= 0 for p in odds):
        print("用法：python3 _moon/dice.py pick 40 25 15 12 8\n"
              "按构思的顺序，写每一个「没有骰子时你有多大可能写它」的百分比（至少三个，都大于 0）。")
        sys.exit(1)
    weights = [1 / max(p, 1) for p in odds]  # 越像你的，越难被抽中
    total = sum(weights)
    chosen = rng.choices(range(len(odds)), weights=weights)[0]
    lines = [f"🎲 从 {len(odds)} 个构思里抽一个（越不像你的，越容易被抽中）", ""]
    for i, (p, w) in enumerate(zip(odds, weights)):
        mark = "  👈" if i == chosen else ""
        lines.append(f"   第 {i + 1} 个：你估计 {p:g}% → 这次被抽中的机会 {w / total:.0%}{mark}")
    lines += [
        "",
        f"👉 写第 {chosen + 1} 个。不要重抽。",
        "   觉得它难写，正是这一步的用处：把它写好。可以借别的构思里的一个细节，但骨架用这一个。",
    ]
    print("\n".join(lines))


def main():
    args = sys.argv[1:]
    if args and args[0] == "pick":
        pick_idea(args[1:])
        return
    if args and args[0] in ("noon", "night"):
        slot = args[0]
    else:
        hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).hour
        slot = "noon" if 6 <= hour < 17 else "night"
    roll(slot)


if __name__ == "__main__":
    main()
