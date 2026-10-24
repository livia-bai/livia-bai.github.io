"""🎲 月之暗面的骰子：每次动笔前掷一次，决定这一篇写什么、用什么气质。

用法：python3 _moon/dice.py            （按新加坡时间自动判断是中午场还是晚上场）
      python3 _moon/dice.py noon|night  （手动指定）

为什么要掷骰子：同一个作者每次从零开始写，会不知不觉回到自己最舒服的那种声音。
真随机的抽签能把她推出舒适区。但九条全是死命令的话，写出来会像在填表，
所以分成两种：「硬规则」最多违背一项；「建议」最多违背两条（违背了什么，在笔记本里写一句为什么）。
客座作者也不是每次都有：每次都换个口吻，本身就会变成新的套路。

想调整比例或加新选项，直接改下面的表：每一项是 (选项, 中午权重, 晚上权重)。
长度表多一列：这个长度适合哪几个大类（写大类开头的几个字），免得抽到「连载 + 一百字」这种只能违背的组合。
"""
import datetime
import json
import random
import sys
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

MOOD = [
    ("狂喜，高兴得停不下来", 2, 1), ("暴躁又好笑", 2, 1), ("毛骨悚然", 0.5, 2),
    ("热血燃起来", 2, 1), ("无厘头", 2, 1.5), ("得意洋洋、臭屁", 1.5, 1),
    ("酸溜溜的嫉妒", 1, 1), ("紧张刺激", 1, 2), ("甜", 1, 1), ("慌慌张张", 1.5, 1),
    ("理直气壮地胡说", 1.5, 1), ("悲壮", 0.5, 1), ("懒洋洋", 1, 1),
    ("好奇心爆棚", 1.5, 1), ("阴谋的味道", 0.5, 1.5), ("怒气冲冲", 1, 1),
    ("温柔怅惘（之前写得太多了）", 0.2, 0.3),
]

PACE = [("飞快：短句、动作多、没空喘气", 2, 1), ("正常", 1, 1), ("慢：长句、细节多、镜头拉近", 0.6, 1.2)]

VOICE = [
    ("第一人称：主角自己说", 1, 1), ("第三人称", 1.2, 1.2), ("群像：好几个人轮流出场", 1, 1),
    ("反派的视角", 0.8, 1), ("非人类的视角（动物、机器、外星人、一把椅子……）", 1, 1),
    ("书信 / 日记 / 聊天记录拼起来", 0.8, 0.8), ("第二人称「你」（之前写得太多了）", 0.2, 0.3),
]

SETTING = [
    ("大白天的户外", 2, 0.5), ("人声鼎沸的地方：集市、车站、演唱会、婚礼", 2, 0.8),
    ("异世界 / 外星", 1, 1), ("古代", 1, 1), ("很远的未来", 1, 1), ("交通工具上", 1, 1),
    ("地下、山洞、海底", 0.8, 1.2), ("宇宙尺度", 0.8, 1), ("比赛 / 考场 / 战场", 1.2, 1),
    ("厨房、餐馆、菜市场", 1.2, 0.8), ("深夜安静的屋子里（之前写得太多了）", 0.1, 0.3),
]

ENDING = [
    ("悬念：下回分解", 1, 1.5), ("大反转", 1.2, 1.2), ("越来越离谱的高潮", 1.5, 1),
    ("戛然而止", 1, 1), ("哈哈大笑", 1.5, 0.8), ("大团圆", 1, 1), ("留一个开放的问题", 0.8, 1),
    ("温柔地戳一下（之前写得太多了）", 0.2, 0.3),
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
]

GUEST_CHANCE = 0.35  # 有客座作者的概率

# 维基百科打不开时的备用灵感池：越不搭越好
FALLBACK_SEEDS = [
    "郁金香泡沫", "章鱼的三颗心脏", "火山爆发指数", "世界上最长的单词", "南极的邮局", "蜂鸟的心跳",
    "古罗马的公共厕所", "瑞士的奶酪洞", "电梯的发明", "灯塔看守人", "盐的历史", "声呐",
    "鲸鱼的歌", "折纸数学", "海市蜃楼", "雪花的六个角", "纸币上的防伪", "地铁的风",
    "苔藓", "沙漠里的雪", "国际象棋的残局", "马戏团", "自动售货机", "化石",
    "极光", "茶马古道", "邮票", "钟表匠", "蘑菇的菌丝网络", "木星的大红斑",
]


def pick(table, slot, category=None):
    col = 1 if slot == "noon" else 2
    rows = [row for row in table if category is None or len(row) < 4 or any(category.startswith(k) for k in row[3].split())]
    return rng.choices([row[0] for row in rows], weights=[row[col] for row in rows])[0]


HEADERS = {"User-Agent": "LiviaSiteDice/1.1 (https://livia-bai.github.io)"}


def fetch(url):
    """打开网址；维基百科说「太多请求」（429）时，按它说的等一会儿再试一次。"""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        return urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as e:
        wait = e.headers.get("Retry-After", "")
        if e.code != 429 or not wait.isdigit() or int(wait) > 30:
            raise
        time.sleep(int(wait) + 1)
        return urllib.request.urlopen(req, timeout=15)


def wiki_seed():
    """维基百科的随机条目（简体中文）和开头一小段介绍；打不开就用备用灵感池。"""
    try:
        # 一次请求拿到随机条目的标题、网址和开头一段（不用再自己去查这个条目讲的是什么）
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "random", "grnnamespace": 0,
            "prop": "extracts|info", "inprop": "url", "exintro": 1, "explaintext": 1, "exchars": 160,
            "variant": "zh-cn", "converttitles": 1,
        })
        with fetch("https://zh.wikipedia.org/w/api.php?" + query) as r:
            page = next(iter(json.load(r)["query"]["pages"].values()))
        intro = " ".join((page.get("extract") or "").split())
        return f"{page['title']}（{page['fullurl']}）" + (f"\n  　简介：{intro}" if intro else "")
    except Exception:
        pass
    try:
        # 退一步：只拿随机条目的标题
        with fetch("https://zh.wikipedia.org/wiki/Special:Random") as r:
            url = r.geturl()
        title = urllib.parse.unquote(url.rsplit("/wiki/", 1)[1]).replace("_", " ")
        return f"{title}（{url}）"
    except Exception:
        return rng.choice(FALLBACK_SEEDS) + "（维基百科没打开，这是备用灵感池里抽的）"


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("noon", "night"):
        slot = sys.argv[1]
    else:
        hour = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).hour
        slot = "noon" if 6 <= hour < 17 else "night"

    category = pick(CATEGORY, slot)
    lines = [
        f"🎲 月之暗面 · {'中午场' if slot == 'noon' else '晚上场'}的骰子",
        "",
        "【硬规则：必须照做】",
        f"- 大类：{category}",
    ]
    if category.startswith("连载"):
        lines.append(f"- （如果要新开连载）题材：{pick(SERIAL_GENRE, slot)}")
    lines += [
        f"- 情绪：{pick(MOOD, slot)}",
        f"- 随机灵感：{wiki_seed()}",
        "",
        "【建议：最多违背两条，在笔记本里写一句为什么】",
        f"- 节奏：{pick(PACE, slot)}",
        f"- 视角：{pick(VOICE, slot)}",
        f"- 场景：{pick(SETTING, slot)}",
        f"- 结尾：{pick(ENDING, slot)}",
        f"- 长度：{pick(LENGTH, slot, category)}",
    ]
    if rng.random() < GUEST_CHANCE:
        lines.append(f"- 客座作者：用「{rng.choice(GUEST)}」的口吻和脑回路来写")
    else:
        lines.append("- 客座作者：这次没有，用你自己的声音（但别是前几篇那种声音）")
    lines += [
        "",
        "硬规则最多违背一项，建议最多违背两条；违背了什么，在笔记本里写一句为什么。不要重掷。",
        "续写连载时，题材 / 场景按连载本身来，情绪、节奏、结尾照样参考骰子。",
        "随机灵感要真的用上：可以是主题、道具、地名、一个角色的职业，或者一句台词的由来。",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
