from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import random
import os
from translations import translations
from routes.comments import comments_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'filesystem'

# 注册评论蓝图
app.register_blueprint(comments_bp, url_prefix='/comments')

def get_translations(lang='zh'):
    return translations.get(lang, translations['zh'])

# 新闻风格模板
news_styles = {
    "official": {
        "prefix": ["据新华社报道", "记者获悉", "权威部门通报"],
        "suffix": ["相关部门正在进一步调查中", "事态发展备受关注", "后续进展将持续关注"],
        "tone": "严肃",
        "credibility_markers": ["多位目击者证实", "专家分析指出", "根据可靠消息", "有关部门已介入调查", "现场视频显示"],
        "narrative_hooks": ["这一事件引发了广泛关注", "此事可能对未来产生深远影响", "相关调查仍在进行中", "事件背后的原因值得深思", "这一现象并非孤例"]
    },
    "tabloid": {
        "prefix": ["震惊！", "独家爆料！", "重磅消息！"],
        "suffix": ["网友炸锅了！", "到底是怎么回事？", "更多猛料即将曝光！"],
        "tone": "夸张",
        "credibility_markers": ["知情人士透露", "爆料人提供的照片显示", "多个社交媒体账号已证实", "据圈内人士透露", "有人已拍到现场视频"],
        "narrative_hooks": ["这一消息引爆网络", "事件反转不断", "更多内幕正在挖掘中", "相关当事人拒绝回应", "网友纷纷猜测事件真相"]
    },
    "conspiracy": {
        "prefix": ["神秘事件！", "惊人发现！", "揭秘！"],
        "suffix": ["真相令人震惊", "背后有更大阴谋？", "这究竟意味着什么？"],
        "tone": "神秘",
        "credibility_markers": ["一份被删除的文件显示", "匿名线人冒险提供的信息", "被主流媒体忽略的证据", "神秘目击者描述", "一段模糊但关键的录音"],
        "narrative_hooks": ["这可能只是冰山一角", "更大的真相正在浮出水面", "有人不希望这个消息传播", "多起类似事件显示出某种模式", "这或许能解释之前的神秘现象"]
    }
}

# 事件发展模板
event_developments = {
    "follow_up": ["最新进展", "事件升级", "突发情况"],
    "reaction": ["各方反应", "舆论发酵", "连锁效应"],
    "conclusion": ["事件真相", "官方回应", "最终结果"]
}

# 图片描述词库
image_descriptions = {
    "international": ["一张卫星拍摄的秘密基地照片", "一枚火箭升空的壮观画面", "两国领导人在谈判桌前的紧张对峙"],
    "gossip": ["一张明星与神秘人共进晚餐的偷拍照片", "一个机器人与人类牵手的模糊画面", "外星人出现在红毯上的惊人瞬间"],
    "tech": ["一台巨大时间机器的实验室照片", "一只智能宠物狗的宣传海报", "一个程序员一脸震惊的搞笑表情"],
    "social": ["一架UFO悬停在城市上空的夜景", "一条街头巷尾传闻中的怪兽剪影", "一个宠物狗失踪的寻狗启事"],
    "daily": ["一位大妈手持扫帚怒视无人机的搞笑画面", "一只流浪猫偷吃邻居饭菜的偷拍照", "快递员被一群狗追赶的混乱场面"]
}

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
MAX_HISTORY = 50

def generate_news(category=None, custom_word=None, style=None, is_follow_up=False):
    if not category or category not in categories:
        category = random.choice(list(categories.keys()))
    c = categories[category]
    
    if not style or style not in news_styles:
        style = random.choice(list(news_styles.keys()))
    s = news_styles[style]
    
    # 生成基础新闻元素
    subject = random.choice(c['subjects'])
    action = random.choice(c['actions'])
    topic = custom_word or random.choice(c['topics'])
    outcome = random.choice(c['outcomes'])
    hint = random.choice(c['hints'])
    
    # 设置具体场景和时间
    locations = ["边境小镇", "某大都市", "偏远山区", "沿海渔村", "繁华商圈", "高科技园区"]
    times = ["深夜", "清晨", "午夜时分", "黄昏时分", "凌晨时分", "正午时分"]
    weather = ["大雾弥漫", "电闪雷鸣", "艳阳高照", "细雨绵绵", "月朗星稀"]
    background = f"2025年3月5日{random.choice(times)}，{random.choice(locations)}{random.choice(weather)}。"
    
    # 添加目击者证词和细节描述
    witnesses = ["一位不愿透露姓名的当地居民", "多名目击群众", "一位自称内部人士的网友", "现场围观的路人"]
    details = ["现场一片混乱", "引发群众围观", "造成交通堵塞", "引起广泛关注", "场面十分罕见"]
    witness_account = f"{random.choice(witnesses)}称，{subject}{action}{topic}时，{random.choice(details)}。"
    
    # 添加可信度标记和叙事钩子
    credibility_marker = random.choice(s['credibility_markers'])
    narrative_hook = random.choice(s['narrative_hooks'])
    
    # 加入情绪化细节和伪证据
    emotions = ["恐慌情绪迅速蔓延", "引发群众热议", "社交媒体炸锅", "专家们争相发表看法", "各方反应强烈"]
    evidences = [
        "社交媒体上流传的视频显示，现场出现了诡异的现象",
        "多个目击者提供的照片佐证了这一说法",
        "知情人士透露，这可能只是更大事件的开始",
        "据未经证实的消息，类似事件已在多地发生"
    ]
    development = f"{random.choice(emotions)}。{random.choice(evidences)}。"
    
    # 制造悬念，遗漏关键信息
    mysteries = [
        "究竟是巧合还是蓄意为之？",
        "背后是否隐藏着不为人知的秘密？",
        "这会是一个新的开始吗？",
        "真相很快就会浮出水面"
    ]
    conclusion = f"{narrative_hook}。{random.choice(mysteries)}"
    
    # 根据风格组装新闻内容
    if style == "official":
        news = f"{random.choice(s['prefix'])}，{background}\n{witness_account}\n{development}\n{conclusion}。{random.choice(s['suffix'])}"
    elif style == "tabloid":
        news = f"{random.choice(s['prefix'])}，{background}\n{witness_account}究竟是怎么回事？\n{development}\n{conclusion}！{random.choice(s['suffix'])}"
    else:  # conspiracy
        news = f"{random.choice(s['prefix'])}，{background}\n{witness_account}\n有人质疑这背后隐藏着不为人知的秘密！\n{development}\n{conclusion}？{random.choice(s['suffix'])}"
    
    # 处理后续报道
    if is_follow_up:
        dev_type = random.choice(list(event_developments.keys()))
        dev_content = random.choice(event_developments[dev_type])
        news = f"【{dev_content}】{news}"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成更多关键词和情感分析
    keywords = [topic, subject]
    if random.random() > 0.5:
        keywords.append(random.choice(['争议', '热点', '真相', '内幕', '爆料']))
    
    # 根据内容生成更合适的情感倾向
    if "震惊" in news or "爆料" in news or "揭秘" in news:
        sentiment = random.choice(['震惊', '愤怒', '怀疑'])
    elif "调查" in news or "分析" in news:
        sentiment = random.choice(['中性', '思考', '好奇'])
    else:
        sentiment = random.choice(['积极', '中性', '消极'])
    
    news_item = {
        "category": category,
        "style": style,
        "headline": f"{news} [生成于 {timestamp}]",
        "comment": random.choice(comments),
        "image_desc": random.choice(image_descriptions[category]),
        "keywords": keywords,
        "heat": random.randint(50, 150),  # 提高热度基数
        "sentiment": sentiment,
        "believe": 0,
        "not_believe": 0,
        "event_id": str(int(datetime.now().timestamp()))  # 添加唯一的事件ID
    }
    
    # 只有登录用户才保存历史记录
    if 'username' in session and session['username'] != 'guest':
        try:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"{session['username']}|{news_item['category']}|{news_item['headline']}|{news_item['comment']}|{news_item['style']}|{news_item['image_desc']}\n")
        except Exception as e:
            print(f"Error saving history: {e}")
    
    return news_item

def get_user_history(username, page=1, per_page=5):
    if not os.path.exists(HISTORY_FILE):
        return [], 0
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
    
    user_history = []
    for line in all_lines:
        parts = line.strip().split('|')
        if len(parts) >= 6 and parts[0] == username:
            user_history.append({
                "category": parts[1],
                "headline": parts[2],
                "comment": parts[3],
                "style": parts[4],
                "image_desc": parts[5]
            })
    
    user_history.reverse()
    total_pages = (len(user_history) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return user_history[start:end], total_pages

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = request.args.get('lang', 'zh')
    t = get_translations(lang)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash(t['password_mismatch'])
            return redirect(url_for('register'))
        
        # 简单的用户名检查
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.split('|')[0] == username:
                        flash(t['username_exists'])
                        return redirect(url_for('register'))
        
        session['username'] = username
        flash(t['register_success'])
        return redirect(url_for('index'))
    return render_template('register.html', translations=t)

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = request.args.get('lang', 'zh')
    t = get_translations(lang)
    if request.method == 'POST':
        username = request.form.get('username')
        session['username'] = username
        flash(t['login_success'])
        return redirect(url_for('index'))
    return render_template('login.html', translations=t)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))



@app.route('/generate_one', methods=['POST'])
def generate_one():
    category = request.form.get('category')
    custom_word = request.form.get('custom_word')
    style = request.form.get('style')
    is_follow_up = request.form.get('is_follow_up') == '1'
    news = generate_news(category, custom_word, style, is_follow_up)
    return news

def load_comments(event_id):
    comments = []
    if os.path.exists('comments.txt'):
        try:
            with open('comments.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 4 and parts[0] == str(event_id):
                        comments.append({
                            'username': parts[1],
                            'comment': parts[2],
                            'timestamp': parts[3]
                        })
        except Exception as e:
            print(f"Error loading comments: {e}")
    return comments

@app.context_processor
def utility_processor():
    return dict(load_comments=load_comments)

@app.route('/', methods=['GET', 'POST'])
def index():
    lang = request.args.get('lang', 'zh')
    t = get_translations(lang)
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        category = request.form.get('category')
        custom_word = request.form.get('custom_word')
        style = request.form.get('style')
        news = generate_news(category, custom_word, style)
        news_list = [news]
    else:
        news_list = [generate_news() for _ in range(3)]
    
    history = []
    total_pages = 0
    if 'username' in session:
        history, total_pages = get_user_history(session['username'], page)
    
    return render_template('index.html', news_list=news_list, history=history, page=page, total_pages=total_pages, translations=t)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)