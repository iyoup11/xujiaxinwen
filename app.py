from flask import Flask, render_template, request
import random
from datetime import datetime
import os

app = Flask(__name__)

# 词库
categories = {
    "international": {
        "hints": ["传闻", "据外媒猜测", "有人爆料"],
        "subjects": ["某大国", "某岛国", "某联盟"],
        "actions": ["疑似试射", "可能挑衅", "被传介入"],
        "topics": ["秘密武器", "太空竞赛", "贸易纠纷"],
        "outcomes": ["邻国慌了", "全球热议", "真相成谜"]
    },
    "gossip": {
        "hints": ["传闻", "圈内爆料", "网友猜测"],
        "subjects": ["某小鲜肉", "某女神", "某老戏骨"],
        "actions": ["疑似恋上", "可能卷入", "被拍到与"],
        "topics": ["机器人", "富二代", "外星人"],
        "outcomes": ["粉丝炸锅", "公司沉默", "热搜炸了"]
    },
    "tech": {
        "hints": ["据传", "有人猜", "业内消息"],
        "subjects": ["某AI", "某太空公司", "某实验室"],
        "actions": ["疑似失控", "可能发明", "被传测试"],
        "topics": ["时间机器", "智能宠物", "伦理漏洞"],
        "outcomes": ["程序员懵逼", "争议不断", "未来未知"]
    },
    "social": {
        "hints": ["据说", "有人称", "街头传言"],
        "subjects": ["某小区", "某城市", "某路人"],
        "actions": ["疑似遇到", "可能引发", "被传发现"],
        "topics": ["怪声", "UFO", "失踪宠物"],
        "outcomes": ["居民傻眼", "网友笑喷", "官方未回应"]
    },
    "daily": {
        "hints": ["据说", "邻居爆料", "有人称"],
        "subjects": ["某大妈", "某小伙", "某楼下"],
        "actions": ["疑似搞乱", "可能发现", "被传教训"],
        "topics": ["无人机", "流浪猫", "快递员"],
        "outcomes": ["街坊笑翻", "全网热议", "结局意外"]
    }
}

comments = [
    "哈哈哈，这也太离谱了吧！",
    "真的假的？我信了！",
    "这新闻一看就是假的，笑死我了。",
    "天啊，吓我一跳，还以为是真的！",
    "这标题绝了，点个赞！"
]

HISTORY_FILE = "history.txt"
MAX_HISTORY = 50  # 增加历史记录上限，以便分页

def generate_news(category=None, custom_word=None):
    if not category or category not in categories:
        category = random.choice(list(categories.keys()))
    c = categories[category]
    news = f"{random.choice(c['hints'])}{random.choice(c['subjects'])}{random.choice(c['actions'])}{custom_word or random.choice(c['topics'])}{random.choice(c['outcomes'])}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_item = {
        "category": category,
        "headline": f"{news} [生成于 {timestamp}]",
        "comment": random.choice(comments)
    }
    
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{news_item['category']}|{news_item['headline']}|{news_item['comment']}\n")
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > MAX_HISTORY:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines[-MAX_HISTORY:])
    
    return news_item

@app.route('/', methods=['GET', 'POST'])
def index():
    news_list = []
    history = []
    page = int(request.args.get('page', 1))
    per_page = 5  # 每页显示 5 条
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            all_history = []
            for line in f:
                if line.strip():
                    cat, head, comm = line.strip().split("|", 2)
                    all_history.append({"category": cat, "headline": head, "comment": comm})
            start = (page - 1) * per_page
            end = start + per_page
            history = all_history[start:end]
            total_pages = (len(all_history) + per_page - 1) // per_page
    else:
        total_pages = 1
    
    if request.method == 'POST':
        category = request.form.get('category')
        custom_word = request.form.get('custom_word')
        for _ in range(3):
            news = generate_news(category, custom_word)
            news_list.append(news)
    return render_template('index.html', news_list=news_list, history=history, page=page, total_pages=total_pages)

@app.route('/generate_one', methods=['POST'])
def generate_one():
    category = request.form.get('category')
    custom_word = request.form.get('custom_word')
    news = generate_news(category, custom_word)
    return news

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)