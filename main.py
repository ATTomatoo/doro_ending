import os
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="Doro互动故事插件",
    description="基于Nonebot2的Doro互动故事游戏",
    usage="输入 /doro 开始游戏，然后通过 /选择 <选项> 进行选择",
    type="application",
    homepage="https://github.com/ttq7/doro_ending",
)

# 故事数据
STORY_DATA = {
    "start": {
        "text": "欢迎来到Doro的世界！\n当前状态：迷茫的年轻人",
        "options": {
            "A": {"text": "读书", "next": "study"},
            "B": {"text": "打工", "next": "work"},
            "C": {"text": "认识陌生人", "next": "meet"},
            "D": {"text": "随机冒险", "next": [
                {"node": "study", "probability": 0.25},
                {"node": "work", "probability": 0.25},
                {"node": "meet", "probability": 0.25},
                {"node": "hidden_tunnel", "probability": 0.25}
            ]}
        }
    },
    # 读书分支（5层深度）
    "study": {
        "text": "图书馆的霉味中，你发现：\nA.考研真题 B.发光菌菇 C.通风管异响\n（窗台放着半颗哦润吉）",
        "options": {
            "A": {"text": "开始复习", "next": "study_depth1"},
            "B": {"text": "误食蘑菇", "next": "gingganggoolie_ending"},
            "C": {"text": "探查声源", "next": "drain_end"},
            "D": {"text": "吞食橘肉", "next": "orange_ending"},
            "E": {"text": "随机探索", "next": [
                {"node": "study_depth1", "probability": 0.3},
                {"node": "gingganggoolie_ending", "probability": 0.2},
                {"node": "drain_end", "probability": 0.2},
                {"node": "orange_ending", "probability": 0.3}
            ]}
        }
    },
    "study_depth1": {
        "text": "连续熬夜第七天：\nA.真题出现幻觉涂鸦 B.钢笔漏墨 C.听见歌声",
        "options": {
            "A": {
                "text": "研究涂鸦",
                "next": [
                    {"node": "study_depth2_art", "probability": 0.7},
                    {"node": "jingshenhunluan_ending", "probability": 0.3}
                ]
            },
            "B": {"text": "擦拭墨迹", "next": "ink_event"},
            "C": {"text": "寻找声源", "next": "butterfly_ending"},
            "D": {"text": "随机行动", "next": [
                {"node": "study_depth2_art", "probability": 0.2},
                {"node": "jingshenhunluan_ending", "probability": 0.2},
                {"node": "ink_event", "probability": 0.2},
                {"node": "butterfly_ending", "probability": 0.4}
            ]}
        }
    },
    "study_depth2_art": {
        "text": "涂鸦开始蠕动：\nA.跟随舞蹈 B.拍照上传 C.撕毁书页",
        "options": {
            "A": {
                "text": "模仿动作",
                "next": [
                    {"node": "shadow_ending", "probability": 0.6},
                    {"node": "butterfly_ending", "probability": 0.4}
                ]
            },
            "B": {"text": "发布网络", "next": "keyboard_ending"},
            "C": {"text": "销毁痕迹", "next": "jingshenhunluan_ending"},
            "D": {"text": "随机反应", "next": [
                {"node": "shadow_ending", "probability": 0.2},
                {"node": "butterfly_ending", "probability": 0.2},
                {"node": "keyboard_ending", "probability": 0.3},
                {"node": "jingshenhunluan_ending", "probability": 0.3}
            ]}
        }
    },
    "ink_event": {
        "text": "墨水形成漩涡：\nA.触碰黑液 B.泼水冲洗 C.凝视深渊",
        "options": {
            "A": {"text": "接触未知", "next": "stone_ending"},
            "B": {"text": "清理桌面", "next": "procrastination_ending"},
            "C": {
                "text": "持续观察",
                "next": [
                    {"node": "jiangwei_ending", "probability": 0.8},
                    {"node": "clouds_ending", "probability": 0.2}
                ]
            },
            "D": {"text": "随机处置", "next": [
                {"node": "stone_ending", "probability": 0.2},
                {"node": "procrastination_ending", "probability": 0.2},
                {"node": "jiangwei_ending", "probability": 0.3},
                {"node": "clouds_ending", "probability": 0.3}
            ]}
        }
    },
    "study_depth3_madness": {
        "text": "你的笔记开始扭曲：\nA.继续解题 B.逃向天台 C.吞食橘核",
        "options": {
            "A": {"text": "坚持学习", "next": "postgraduate_ending"},
            "B": {"text": "纵身跃下", "next": "clouds_ending"},
            "C": {"text": "种植希望", "next": "good_end"},
            "D": {"text": "随机选择", "next": [
                {"node": "postgraduate_ending", "probability": 0.2},
                {"node": "clouds_ending", "probability": 0.3},
                {"node": "good_end", "probability": 0.5}
            ]}
        }
    },
    # 打工分支（6层深度）
    "work": {
        "text": "人才市场三个招聘点：\nA.福报大厂 B.摸鱼公司 C.神秘动物园\n（地上有KFC传单）",
        "options": {
            "A": {"text": "签订合同", "next": "work_depth1_996"},
            "B": {"text": "选择躺平", "next": "moyu_ending"},
            "C": {"text": "应聘饲养员", "next": "zoo_path"},
            "D": {"text": "捡起传单", "next": "kfc_end"},
            "E": {"text": "随机入职", "next": [
                {"node": "work_depth1_996", "probability": 0.2},
                {"node": "moyu_ending", "probability": 0.2},
                {"node": "zoo_path", "probability": 0.3},
                {"node": "kfc_end", "probability": 0.3}
            ]}
        }
    },
    "work_depth1_996": {
        "text": "入职第三周：\nA.继续内卷 B.安装摸鱼插件 C.出现幻觉",
        "options": {
            "A": {
                "text": "拼命加班",
                "next": [
                    {"node": "race_ending", "probability": 0.7},
                    {"node": "postgraduate_ending", "probability": 0.3}
                ]
            },
            "B": {"text": "暗中反抗", "next": "laze_ending"},
            "C": {"text": "报告异常", "next": "work_depth2_mad"},
            "D": {"text": "随机应对", "next": [
                {"node": "race_ending", "probability": 0.2},
                {"node": "postgraduate_ending", "probability": 0.2},
                {"node": "laze_ending", "probability": 0.3},
                {"node": "work_depth2_mad", "probability": 0.3}
            ]}
        }
    },
    "work_depth2_mad": {
        "text": "HR递来药丸：\nA.红色提神丸 B.蓝色遗忘剂 C.彩色致幻剂",
        "options": {
            "A": {
                "text": "吞下红丸",
                "next": [
                    {"node": "sloth_ending", "probability": 0.6},
                    {"node": "race_ending", "probability": 0.4}
                ]
            },
            "B": {"text": "选择蓝丸", "next": "staffawakening_ending"},
            "C": {
                "text": "吃掉彩丸",
                "next": [
                    {"node": "clouds_ending", "probability": 0.7},
                    {"node": "soviet_ending", "probability": 0.3}
                ]
            },
            "D": {"text": "随机服药", "next": [
                {"node": "sloth_ending", "probability": 0.2},
                {"node": "race_ending", "probability": 0.2},
                {"node": "staffawakening_ending", "probability": 0.3},
                {"node": "clouds_ending", "probability": 0.3}
            ]}
        }
    },
    "zoo_path": {
        "text": "园长分配区域：\nA.熊猫馆 B.极地馆 C.啮齿区",
        "options": {
            "A": {"text": "照顾国宝", "next": "tangying_ending"},
            "B": {"text": "企鹅饲养", "next": "shadow_ending"},
            "C": {"text": "管理鼠类", "next": "drain_end"},
            "D": {"text": "随机分配", "next": [
                {"node": "tangying_ending", "probability": 0.2},
                {"node": "shadow_ending", "probability": 0.3},
                {"node": "drain_end", "probability": 0.5}
            ]}
        }
    },
    # 社交分支（5层深度）
    "meet": {
        "text": "神秘人Doro出现：\nA.分享橘子 B.查看相册 C.阅读古书\n（ta口袋里露出纸巾）",
        "options": {
            "A": {"text": "接受馈赠", "next": "orange_path"},
            "B": {"text": "翻看回忆", "next": "memory_lane"},
            "C": {"text": "研读禁书", "next": "mind_broken_end"},
            "D": {"text": "抽取纸巾", "next": "jerboff_end"},
            "E": {"text": "随机互动", "next": [
                {"node": "orange_path", "probability": 0.2},
                {"node": "memory_lane", "probability": 0.2},
                {"node": "mind_broken_end", "probability": 0.3},
                {"node": "jerboff_end", "probability": 0.3}
            ]}
        }
    },
    "orange_path": {
        "text": "橘子散发微光：\nA.独自吃完 B.种下果核 C.分享他人",
        "options": {
            "A": {
                "text": "沉迷美味",
                "next": [
                    {"node": "orange_ending", "probability": 0.8},
                    {"node": "good_end", "probability": 0.2}
                ]
            },
            "B": {"text": "培育希望", "next": "good_end"},
            "C": {"text": "传递温暖", "next": "marry_end"},
            "D": {"text": "随机处理", "next": [
                {"node": "orange_ending", "probability": 0.3},
                {"node": "good_end", "probability": 0.3},
                {"node": "marry_end", "probability": 0.4}
            ]}
        }
    },
    "memory_lane": {
        "text": "泛黄照片中的你：\nA.高考考场 B.童年小床 C.空白页面",
        "options": {
            "A": {"text": "重温噩梦", "next": "gaokao_ending"},
            "B": {"text": "触摸画面", "next": "dream_end"},
            "C": {"text": "撕下白纸", "next": "takeoff_failed_end"},
            "D": {"text": "随机回忆", "next": [
                {"node": "gaokao_ending", "probability": 0.2},
                {"node": "dream_end", "probability": 0.3},
                {"node": "takeoff_failed_end", "probability": 0.5}
            ]}
        }
    },
    # 所有33个结局节点（保持原始ID和内容）
    "drain_end": {
        "text": "在潮湿阴暗的下水道，你与Doro分享着发霉的哦润吉，四周弥漫着神秘又诡异的气息...",
        "image": "1bb22576b2e253fae6b2ddca27cd3384.jpg",
        "is_end": True,
        "secret": {"🔑": "找到鼠王钥匙可解锁隐藏剧情"}
    },
    "postgraduate_ending": {
        "text": "录取通知书如期而至，可发际线也在悄然变化，未来的学术之路在眼前展开...",
        "image": "postgraduate_ending.png",
        "is_end": True
    },
    "procrastination_ending": {
        "text": "在拖延的时光里，你意外发现了最高效的生产力，原来时间也有它奇妙的魔法...",
        "image": "procrastination_ending.png",
        "is_end": True
    },
    "takeoff_failed_end":{
        "text": "你决定把白纸撕掉，但你发现你无法从白纸中解开它...",
        "image": "takeoff_failed_end.png",
        "is_end": True
    },
    "mind_broken_end":{
        "text": "你决定阅读禁书，但你发现你无法从禁书中解开它...",
        "image": "mind_broken_end.png",
        "is_end": True
    },
    "staffawakening_ending":{
        "text": "你坐在办公室里，盯着Excel表格，感觉自己像一台没有感情的机器...",
        "image": "staffawakening_ending.png",
        "is_end": True
    },
    "laze_ending":{
        "text": "你决定做懒人，但你发现你无法从懒人中解开它...",
        "image": "laze_ending.png",
        "is_end": True
    },
    "gaokao_ending":{
        "text": "高考成绩公布后，你决定投奔你的梦想，但你发现你的计划并不太现实...",
        "image": "gaokao_ending.png",
        "is_end": True
    },
    "race_ending": {
        "text": "在仓鼠轮中奋力奔跑，可永动机的梦想终究破灭，疲惫与无奈涌上心头...",
        "image": "neijuan_ending.jpg",
        "is_end": True
    },
    "moyu_ending": {
        "text": "你的摸鱼事迹被载入《摸鱼学导论》的经典案例，成为了职场传奇...",
        "image": "moyu_ending.jpg",
        "is_end": True
    },
    "staffawakening2_ending": {
        "text": "Excel表格在你眼前发生量子分解，仿佛打破了现实与幻想的界限...",
        "image": "staffawakening2_ending.png",
        "is_end": True
    },
    # 幻想系结局
    "butterfly_ending": {
        "text": "你变成了一只蝴蝶，翅膀上Doro的花纹闪烁着神秘光芒，在奇幻世界中自由飞舞...",
        "image": "butterfly_ending.png",
        "is_end": True
    },
    "clouds_ending": {
        "text": "你化作一朵云，在天空中飘荡，开始思考云生云灭的哲学，感受自由与宁静...",
        "image": "clouds_ending.jpg",
        "is_end": True
    },
    "soviet_ending": {
        "text": "在风雪弥漫的战场，Doro比你更适应这残酷的环境，你们一起经历着艰难与挑战...",
        "image": "bad_ending.jpeg",
        "is_end": True
    },
    "tangying_ending": {
        "text": "作为熊猫饲养员，你受到游客喜爱，他们甚至为你众筹哦润吉自由，生活充满温暖与惊喜...",
        "image": "tangying_ending.jpg",
        "is_end": True
    },
    "stone_ending": {
        "text": "你变成了一块石头，静静躺在河边，看着河水潺潺流过，记忆在时光中沉淀...",
        "image": "stone_ending.png",
        "is_end": True
    },
    "sloth_ending": {
        "text": "变成树懒的你，在树上享受着悠闲时光，光合作用效率达到树懒巅峰，生活惬意又自在...",
        "image": "sloth_ending.jpg",
        "is_end": True
    },
    # 元叙事结局
    "gingganggoolie_ending": {
        "text": "服用灵感菇后，小人儿在你眼前忙碌编排着你的命运，奇幻与荒诞交织...",
        "image": "gingganggoolie_ending.png",
        "is_end": True
    },
    "jingshenhunluan_ending": {
        "text": "阅读破旧书籍时，书页间的Doro似乎在嘲笑你的理智，精神世界陷入混乱...",
        "image": "jingshenhunluan_ending.jpeg",
        "is_end": True
    },
    "jiangwei_ending": {
        "text": "你的表情包在二维宇宙中迅速扩散，成为了虚拟世界的热门话题，开启新的次元之旅...",
        "image": "jiangwei_ending.jpeg",
        "is_end": True
    },
    "keyboard_ending": {
        "text": "右手变成键盘后，每个按键都像是灵魂的墓碑，诉说着无奈与挣扎...",
        "image": "bad_ending.png",
        "is_end": True
    },
    "kfc_end": {
        "text": "在疯狂星期四，KFC的美味验证了宇宙真理，快乐与满足在此刻绽放...",
        "image": "abd814eba4fa165f44f3e16fb93b3a72.png",
        "is_end": True
    },
    # 特殊交互结局
    "dream_end": {
        "text": "小笨床仿佛拥有魔力，逐渐吞噬现实维度，带你进入奇妙梦境...",
        "image": ["dream_ending.png"],
        "is_end": True,
        "trigger": ["三次选择睡觉选项"]
    },
    "shadow_ending": {
        "text": "你成为社畜们的集体潜意识，在黑暗中默默观察着职场的风云变幻...",
        "image": "shadow_ending.png",
        "is_end": True,
        "callback": ["corpse_cycle"]
    },
    "good_end": {
        "text": "你和Doro携手找到了量子态的幸福，生活充满了彩虹般的色彩与希望...",
        "image": "good_end.png",
        "is_end": True,
        "condition": ["解锁5个普通结局"]
    },
    "orange_ending": {
        "text": "哦润吉的魔力完成了对你的精神同化，你沉浸在它的甜蜜世界中无法自拔...",
        "image": "orange_ending.png",
        "is_end": True,
        "secret_path": ["在所有分支找到隐藏橘子"]
    },
    "marry_end": {
        "text": "❤️ 触发【登记结局】",
        "image": "marry_ending.png",
        "is_end": True
    },
    "indolent_ending":{
        "text": "你变成了一条鱼，生活在公司办公司的鱼缸里...",
        "image": "indolent_ending.png",
        "is_end": True
    },
    # 新增连接节点
    "hidden_tunnel": {
        "text": "狭窄的通风管通向未知的地方，你似乎能闻到不同的气息：\nA.下水道的潮湿异味  B.办公室鱼缸的清新水汽  C.KFC后厨的诱人香味",
        "options": {
            "A": {"text": "继续爬行探索", "next": "drain_end"},
            "B": {"text": "跳入鱼缸冒险", "next": "indolent_ending"},
            "C": {"text": "寻找美食之旅", "next": "kfc_end"}
        }
    }
}

# 存储每个用户的游戏状态，key为用户ID，value为当前故事节点
user_game_state = {}

# 图片目录路径，相对于当前文件所在目录下的 images 文件夹
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

# 开始游戏命令
doro_start = on_command("doro", aliases={"hello七七"}, priority=5, block=True)

@doro_start.handle()
async def handle_doro_start(bot: Bot, event: Event):
    user_id = str(event.get_user_id())
    user_game_state[user_id] = "start"
    data = STORY_DATA["start"]
    msg = data["text"] + "\n"
    options = data.get("options", {})
    for key, opt in options.items():
        msg += f"{key}. {opt['text']}\n"
    await doro_start.send(msg)

# 选择命令
choose = on_command("选择", priority=5, block=True)

@choose.handle()
async def handle_choose(bot: Bot, event: Event, args: Message = CommandArg()):
    user_id = str(event.get_user_id())
    if user_id not in user_game_state:
        await choose.finish("你还没有开始游戏，请输入 /doro 开始。")
        return

    choice = args.extract_plain_text().strip().upper()  # 提取参数并转为大写
    current_node = user_game_state[user_id]
    data = STORY_DATA.get(current_node, {})

    options = data.get("options", {})
    if choice not in options:
        await choose.finish("无效选择，请重新输入。")
        return

    next_node = options[choice]["next"]
    if isinstance(next_node, list):  # 随机选项
        rand = random.random()
        cumulative = 0.0
        for item in next_node:
            cumulative += item["probability"]
            if rand <= cumulative:
                next_node = item["node"]
                break

    next_data = STORY_DATA.get(next_node)
    if not next_data:
        await choose.finish("故事节点错误，请联系管理员。")
        return

    user_game_state[user_id] = next_node

    # 构造消息文本（包含故事描述和选项）
    msg = next_data["text"] + "\n"
    next_options = next_data.get("options", {})
    for key, opt in next_options.items():
        msg += f"{key}. {opt['text']}\n"

    # 如果有对应图片，可以发送
    default_image_path = os.path.join(IMAGE_DIR, f"{next_node}.jpg")
    if os.path.exists(default_image_path):
        await choose.send(MessageSegment.image(f"file://{default_image_path}"))

    # 发送文本消息    
    await choose.send(msg)

    # 如果节点中指定了图片，则发送这些图片
    if "image" in next_data:
        if isinstance(next_data["image"], list):
            for img_file in next_data["image"]:
                image_path = os.path.join(IMAGE_DIR, img_file)
                if os.path.exists(image_path):
                    img_seg = MessageSegment.image(f"file://{image_path}")
                    await choose.send(img_seg)
                else:
                    await choose.send(f"图片 {img_file} 不存在。")
        else:
            image_path = os.path.join(IMAGE_DIR, next_data["image"])
            if os.path.exists(image_path):
                img_seg = MessageSegment.image(f"file://{image_path}")
                await choose.send(img_seg)
            else:
                await choose.send(f"图片 {next_data['image']} 不存在。")

    # 判断是否为结束节点
    if next_data.get("is_end", False):
        await choose.send("故事结束。")
        # 删除用户状态，方便重新开始游戏
        user_game_state.pop(user_id, None)
    else:
        # 展示选项列表（如果存在）
        if "options" in next_data:
            options_text = ""
            for key, opt in next_data["options"].items():
                options_text += f"{key}. {opt['text']}\n"
            await choose.send(options_text)
