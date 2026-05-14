import streamlit as st
import pandas as pd
import json
import os
import uuid
from moviepy.editor import VideoFileClip

# 全局美化配置
st.set_page_config(
    page_title="全国景区留言评价系统",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {background-color: #f8fafc;}
    .stButton>button {border-radius: 10px; padding: 6px 12px;}
    .stTextInput>div>div>input {border-radius: 8px;}
    .stTextArea>div>div>textarea {border-radius: 8px;}
    .stSelectbox>div>div {border-radius: 8px;}
    .css-18e3th9 {padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 创建文件夹
os.makedirs("videos", exist_ok=True)

# 数据文件
USER_FILE = "users.json"
MSG_FILE = "messages.json"
COMMENT_FILE = "comments.json"
COLLECT_FILE = "collects.json"
TOP_VIDEO_FILE = "top_video.json"

# 加载用户
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": {"pwd":"123456", "avatar":"👑", "is_admin":True}}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 留言
def load_messages():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=[
        "mid","用户名","头像","省份","景区名称","景区等级",
        "评价等级","星级","留言内容","视频路径","点赞数","授权同意","是否上景区首页"
    ])

def save_messages(df):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, ensure_ascii=False, indent=2)

# 评论
def load_comments():
    if os.path.exists(COMMENT_FILE):
        with open(COMMENT_FILE, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=["mid","cid","用户名","头像","内容"])

def save_comments(df):
    with open(COMMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(df.to_dict("records"), f, ensure_ascii=False, indent=2)

# 收藏
def load_collects():
    if os.path.exists(COLLECT_FILE):
        with open(COLLECT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_collects(data):
    with open(COLLECT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 景区置顶视频
def load_top_video():
    if os.path.exists(TOP_VIDEO_FILE):
        with open(TOP_VIDEO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_top_video(data):
    with open(TOP_VIDEO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 初始化
if "users" not in st.session_state:
    st.session_state.users = load_users()
if "message_list" not in st.session_state:
    st.session_state.message_list = load_messages()
if "comment_list" not in st.session_state:
    st.session_state.comment_list = load_comments()
if "collect_data" not in st.session_state:
    st.session_state.collect_data = load_collects()
if "top_video_data" not in st.session_state:
    st.session_state.top_video_data = load_top_video()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page_tab" not in st.session_state:
    st.session_state.page_tab = "首页"

# ===================== 全国景区数据 =====================
scenic_dict = {
    "北京市": {
        "5A":{"故宫博物院":"https://pic.616pic.com/ys_bnew_img/00/63/34/63340a81580438028.jpg","八达岭长城":"https://img2.baidu.com/it/u=3948841419,3829733300&fm=253&fmt=auto","颐和园":"https://img2.baidu.com/it/u=2952279672,3829693239&fm=253&fmt=auto","天坛公园":"https://img2.baidu.com/it/u=1290380920,3104292323&fm=253&fmt=auto"},
        "4A":{"北京欢乐谷":"https://pic.rmb.bdstatic.com/bjh/111.jpeg","南锣鼓巷":"https://pic.rmb.bdstatic.com/bjh/222.jpeg","什刹海":"https://pic.rmb.bdstatic.com/bjh/333.jpeg"},
        "3A":{"香山公园":"https://pic.rmb.bdstatic.com/bjh/444.jpeg","玉渊潭公园":"https://pic.rmb.bdstatic.com/bjh/555.jpeg"}
    },
    "天津市": {
        "5A":{"盘山":"https://pic.rmb.bdstatic.com/bjh/tj1.jpeg","古文化街":"https://pic.rmb.bdstatic.com/bjh/tj2.jpeg"},
        "4A":{"天津水上公园":"https://pic.rmb.bdstatic.com/bjh/tj3.jpeg","意大利风情街":"https://pic.rmb.bdstatic.com/bjh/tj4.jpeg"},
        "3A":{"黄崖关长城":"https://pic.rmb.bdstatic.com/bjh/tj5.jpeg"}
    },
    "河北省": {
        "5A":{"承德避暑山庄":"https://pic.rmb.bdstatic.com/bjh/hb1.jpeg","白洋淀":"https://pic.rmb.bdstatic.com/bjh/hb2.jpeg","野三坡":"https://pic.rmb.bdstatic.com/bjh/hb3.jpeg"},
        "4A":{"山海关":"https://pic.rmb.bdstatic.com/bjh/hb4.jpeg","清东陵":"https://pic.rmb.bdstatic.com/bjh/hb5.jpeg"},
        "3A":{"狼牙山":"https://pic.rmb.bdstatic.com/bjh/hb6.jpeg"}
    },
    "山西省": {
        "5A":{"五台山":"https://pic.rmb.bdstatic.com/bjh/sx1.jpeg","云冈石窟":"https://pic.rmb.bdstatic.com/bjh/sx2.jpeg","平遥古城":"https://pic.rmb.bdstatic.com/bjh/sx3.jpeg"},
        "4A":{"乔家大院":"https://pic.rmb.bdstatic.com/bjh/sx4.jpeg","绵山":"https://pic.rmb.bdstatic.com/bjh/sx5.jpeg"},
        "3A":{"壶口瀑布":"https://pic.rmb.bdstatic.com/bjh/sx6.jpeg"}
    },
    "内蒙古": {
        "5A":{"呼伦贝尔草原":"https://pic.rmb.bdstatic.com/bjh/nm1.jpeg","响沙湾":"https://pic.rmb.bdstatic.com/bjh/nm2.jpeg"},
        "4A":{"满洲里套娃景区":"https://pic.rmb.bdstatic.com/bjh/nm3.jpeg","克什克腾石林":"https://pic.rmb.bdstatic.com/bjh/nm4.jpeg"},
        "3A":{"阿尔山天池":"https://pic.rmb.bdstatic.com/bjh/nm5.jpeg"}
    },
    "辽宁省": {
        "5A":{"沈阳故宫":"https://pic.rmb.bdstatic.com/bjh/ln1.jpeg","大连老虎滩":"https://pic.rmb.bdstatic.com/bjh/ln2.jpeg","千山":"https://pic.rmb.bdstatic.com/bjh/ln3.jpeg"},
        "4A":{"棒棰岛":"https://pic.rmb.bdstatic.com/bjh/ln4.jpeg","本溪水洞":"https://pic.rmb.bdstatic.com/bjh/ln5.jpeg"},
        "3A":{"兴城古城":"https://pic.rmb.bdstatic.com/bjh/ln6.jpeg"}
    },
    "吉林省": {
        "5A":{"长白山":"https://pic.rmb.bdstatic.com/bjh/jl1.jpeg","伪满皇宫":"https://pic.rmb.bdstatic.com/bjh/jl2.jpeg","净月潭":"https://pic.rmb.bdstatic.com/bjh/jl3.jpeg"},
        "4A":{"松花湖":"https://pic.rmb.bdstatic.com/bjh/jl4.jpeg","向海湿地":"https://pic.rmb.bdstatic.com/bjh/jl5.jpeg"},
        "3A":{"高句丽古迹":"https://pic.rmb.bdstatic.com/bjh/jl6.jpeg"}
    },
    "黑龙江省": {
        "5A":{"太阳岛":"https://pic.rmb.bdstatic.com/bjh/hlj1.jpeg","五大连池":"https://pic.rmb.bdstatic.com/bjh/hlj2.jpeg","镜泊湖":"https://pic.rmb.bdstatic.com/bjh/hlj3.jpeg"},
        "4A":{"雪乡":"https://pic.rmb.bdstatic.com/bjh/hlj4.jpeg","亚布力":"https://pic.rmb.bdstatic.com/bjh/hlj5.jpeg"},
        "3A":{"漠河北极村":"https://pic.rmb.bdstatic.com/bjh/hlj6.jpeg"}
    },
    "上海市": {
        "5A":{"东方明珠":"https://img2.baidu.com/it/u=1829897233,2234326223&fm=253&fmt=auto","上海迪士尼":"https://img2.baidu.com/it/u=3694474112,3719001133&fm=253&fmt=auto","上海科技馆":"https://pic.rmb.bdstatic.com/bjh/sh1.jpeg"},
        "4A":{"豫园":"https://pic.rmb.bdstatic.com/bjh/sh2.jpeg","静安寺":"https://pic.rmb.bdstatic.com/bjh/sh3.jpeg","朱家角":"https://pic.rmb.bdstatic.com/bjh/sh4.jpeg"},
        "3A":{"锦江乐园":"https://pic.rmb.bdstatic.com/bjh/sh5.jpeg","鲁迅公园":"https://pic.rmb.bdstatic.com/bjh/sh6.jpeg"}
    },
    "江苏省": {
        "5A":{"中山陵":"https://pic.rmb.bdstatic.com/bjh/js1.jpeg","苏州园林":"https://pic.rmb.bdstatic.com/bjh/js2.jpeg","周庄":"https://pic.rmb.bdstatic.com/bjh/js3.jpeg","灵山大佛":"https://pic.rmb.bdstatic.com/bjh/js4.jpeg"},
        "4A":{"同里古镇":"https://pic.rmb.bdstatic.com/bjh/js5.jpeg","瘦西湖":"https://pic.rmb.bdstatic.com/bjh/js6.jpeg"},
        "3A":{"夫子庙":"https://pic.rmb.bdstatic.com/bjh/js7.jpeg"}
    },
    "浙江省": {
        "5A":{"杭州西湖":"https://img2.baidu.com/it/u=2743938493,3203349393&fm=253&fmt=auto","千岛湖":"https://img2.baidu.com/it/u=2932242213,3833437139&fm=253&fmt=auto","雁荡山":"https://pic.rmb.bdstatic.com/bjh/zj1.jpeg","普陀山":"https://pic.rmb.bdstatic.com/bjh/zj2.jpeg","乌镇":"https://img2.baidu.com/it/u=1293423009,2779900213&fm=253&fmt=auto"},
        "4A":{"西塘":"https://pic.rmb.bdstatic.com/bjh/zj3.jpeg","鲁迅故里":"https://pic.rmb.bdstatic.com/bjh/zj4.jpeg","莫干山":"https://pic.rmb.bdstatic.com/bjh/zj5.jpeg"},
        "3A":{"大明山":"https://pic.rmb.bdstatic.com/bjh/zj6.jpeg","南浔":"https://pic.rmb.bdstatic.com/bjh/zj7.jpeg"}
    },
    "安徽省": {
        "5A":{"黄山":"https://img2.baidu.com/it/u=1276873720,3040443712&fm=253&fmt=auto","九华山":"https://pic.rmb.bdstatic.com/bjh/ah1.jpeg","西递宏村":"https://img2.baidu.com/it/u=3948744418,2903222099&fm=253&fmt=auto","天柱山":"https://pic.rmb.bdstatic.com/bjh/ah2.jpeg"},
        "4A":{"三河古镇":"https://pic.rmb.bdstatic.com/bjh/ah3.jpeg","齐云山":"https://pic.rmb.bdstatic.com/bjh/ah4.jpeg"},
        "3A":{"采石矶":"https://pic.rmb.bdstatic.com/bjh/ah5.jpeg"}
    },
    "福建省": {
        "5A":{"武夷山":"https://pic.rmb.bdstatic.com/bjh/fj1.jpeg","鼓浪屿":"https://pic.rmb.bdstatic.com/bjh/fj2.jpeg","土楼":"https://pic.rmb.bdstatic.com/bjh/fj3.jpeg"},
        "4A":{"三坊七巷":"https://pic.rmb.bdstatic.com/bjh/fj4.jpeg","太姥山":"https://pic.rmb.bdstatic.com/bjh/fj5.jpeg"},
        "3A":{"清源山":"https://pic.rmb.bdstatic.com/bjh/fj6.jpeg"}
    },
    "江西省": {
        "5A":{"庐山":"https://pic.rmb.bdstatic.com/bjh/jx1.jpeg","井冈山":"https://pic.rmb.bdstatic.com/bjh/jx2.jpeg","三清山":"https://pic.rmb.bdstatic.com/bjh/jx3.jpeg","婺源":"https://pic.rmb.bdstatic.com/bjh/jx4.jpeg"},
        "4A":{"滕王阁":"https://pic.rmb.bdstatic.com/bjh/jx5.jpeg","龙虎山":"https://pic.rmb.bdstatic.com/bjh/jx6.jpeg"},
        "3A":{"仙女湖":"https://pic.rmb.bdstatic.com/bjh/jx7.jpeg"}
    },
    "山东省": {
        "5A":{"泰山":"https://pic.rmb.bdstatic.com/bjh/sd1.jpeg","三孔":"https://pic.rmb.bdstatic.com/bjh/sd2.jpeg","崂山":"https://pic.rmb.bdstatic.com/bjh/sd3.jpeg"},
        "4A":{"蓬莱阁":"https://pic.rmb.bdstatic.com/bjh/sd4.jpeg","刘公岛":"https://pic.rmb.bdstatic.com/bjh/sd5.jpeg"},
        "3A":{"微山湖":"https://pic.rmb.bdstatic.com/bjh/sd6.jpeg"}
    },
    "河南省": {
        "5A":{"龙门石窟":"https://pic.rmb.bdstatic.com/bjh/hn1.jpeg","少林寺":"https://pic.rmb.bdstatic.com/bjh/hn2.jpeg","云台山":"https://pic.rmb.bdstatic.com/bjh/hn3.jpeg"},
        "4A":{"清明上河园":"https://pic.rmb.bdstatic.com/bjh/hn4.jpeg","老君山":"https://pic.rmb.bdstatic.com/bjh/hn5.jpeg"},
        "3A":{"龙潭大峡谷":"https://pic.rmb.bdstatic.com/bjh/hn6.jpeg"}
    },
    "湖北省": {
        "5A":{"黄鹤楼":"https://pic.rmb.bdstatic.com/bjh/hub1.jpeg","三峡大坝":"https://pic.rmb.bdstatic.com/bjh/hub2.jpeg","神农架":"https://pic.rmb.bdstatic.com/bjh/hub3.jpeg"},
        "4A":{"武当山":"https://pic.rmb.bdstatic.com/bjh/hub4.jpeg","东湖":"https://pic.rmb.bdstatic.com/bjh/hub5.jpeg"},
        "3A":{"清江画廊":"https://pic.rmb.bdstatic.com/bjh/hub6.jpeg"}
    },
    "湖南省": {
        "5A":{"张家界":"https://pic.rmb.bdstatic.com/bjh/hun1.jpeg","衡山":"https://pic.rmb.bdstatic.com/bjh/hun2.jpeg","岳阳楼":"https://pic.rmb.bdstatic.com/bjh/hun3.jpeg"},
        "4A":{"凤凰古城":"https://pic.rmb.bdstatic.com/bjh/hun4.jpeg","东江湖":"https://pic.rmb.bdstatic.com/bjh/hun5.jpeg"},
        "3A":{"桃花源":"https://pic.rmb.bdstatic.com/bjh/hun6.jpeg"}
    },
    "广东省": {
        "5A":{"长隆":"https://pic.rmb.bdstatic.com/bjh/gd1.jpeg","白云山":"https://pic.rmb.bdstatic.com/bjh/gd2.jpeg","丹霞山":"https://pic.rmb.bdstatic.com/bjh/gd3.jpeg"},
        "4A":{"西樵山":"https://pic.rmb.bdstatic.com/bjh/gd4.jpeg","开平碉楼":"https://pic.rmb.bdstatic.com/bjh/gd5.jpeg"},
        "3A":{"圭峰山":"https://pic.rmb.bdstatic.com/bjh/gd6.jpeg"}
    },
    "广西": {
        "5A":{"桂林漓江":"https://pic.rmb.bdstatic.com/bjh/gx1.jpeg","德天瀑布":"https://pic.rmb.bdstatic.com/bjh/gx2.jpeg","阳朔西街":"https://pic.rmb.bdstatic.com/bjh/gx3.jpeg"},
        "4A":{"龙脊梯田":"https://pic.rmb.bdstatic.com/bjh/gx4.jpeg","两江四湖":"https://pic.rmb.bdstatic.com/bjh/gx5.jpeg"},
        "3A":{"银子岩":"https://pic.rmb.bdstatic.com/bjh/gx6.jpeg"}
    },
    "海南省": {
        "5A":{"亚龙湾":"https://pic.rmb.bdstatic.com/bjh/hainan1.jpeg","天涯海角":"https://pic.rmb.bdstatic.com/bjh/hainan2.jpeg","南山":"https://pic.rmb.bdstatic.com/bjh/hainan3.jpeg"},
        "4A":{"蜈支洲岛":"https://pic.rmb.bdstatic.com/bjh/hainan4.jpeg","分界洲岛":"https://pic.rmb.bdstatic.com/bjh/hainan5.jpeg"},
        "3A":{"椰田古寨":"https://pic.rmb.bdstatic.com/bjh/hainan6.jpeg"}
    },
    "重庆市": {
        "5A":{"大足石刻":"https://pic.rmb.bdstatic.com/bjh/cq1.jpeg","武隆喀斯特":"https://pic.rmb.bdstatic.com/bjh/cq2.jpeg"},
        "4A":{"黑万盛":"https://pic.rmb.bdstatic.com/bjh/cq3.jpeg","金佛山":"https://pic.rmb.bdstatic.com/bjh/cq4.jpeg"},
        "3A":{"长寿湖":"https://pic.rmb.bdstatic.com/bjh/cq5.jpeg"}
    },
    "四川省": {
        "5A":{"九寨沟":"https://img2.baidu.com/it/u=3948744418,2903222099&fm=253&fmt=auto","都江堰":"https://img2.baidu.com/it/u=2734421429,2922343239&fm=253&fmt=auto","峨眉山":"https://pic.rmb.bdstatic.com/bjh/sc1.jpeg","乐山大佛":"https://pic.rmb.bdstatic.com/bjh/sc2.jpeg"},
        "4A":{"剑门关":"https://pic.rmb.bdstatic.com/bjh/sc3.jpeg","蜀南竹海":"https://pic.rmb.bdstatic.com/bjh/sc4.jpeg","碧峰峡":"https://pic.rmb.bdstatic.com/bjh/sc5.jpeg"},
        "3A":{"窦圌山":"https://pic.rmb.bdstatic.com/bjh/sc6.jpeg","七里峡":"https://pic.rmb.bdstatic.com/bjh/sc7.jpeg"}
    },
    "贵州省": {
        "5A":{"黄果树":"https://pic.rmb.bdstatic.com/bjh/gz1.jpeg","梵净山":"https://pic.rmb.bdstatic.com/bjh/gz2.jpeg","千户苗寨":"https://pic.rmb.bdstatic.com/bjh/gz3.jpeg"},
        "4A":{"荔波小七孔":"https://pic.rmb.bdstatic.com/bjh/gz4.jpeg","镇远古镇":"https://pic.rmb.bdstatic.com/bjh/gz5.jpeg"},
        "3A":{"青岩古镇":"https://pic.rmb.bdstatic.com/bjh/gz6.jpeg"}
    },
    "云南省": {
        "5A":{"丽江古城":"https://pic.rmb.bdstatic.com/bjh/yn1.jpeg","大理古城":"https://pic.rmb.bdstatic.com/bjh/yn2.jpeg","石林":"https://pic.rmb.bdstatic.com/bjh/yn3.jpeg","玉龙雪山":"https://pic.rmb.bdstatic.com/bjh/yn4.jpeg"},
        "4A":{"洱海":"https://pic.rmb.bdstatic.com/bjh/yn5.jpeg","束河古镇":"https://pic.rmb.bdstatic.com/bjh/yn6.jpeg"},
        "3A":{"黑龙潭":"https://pic.rmb.bdstatic.com/bjh/yn7.jpeg","彝人古镇":"https://pic.rmb.bdstatic.com/bjh/yn8.jpeg"}
    },
    "西藏": {
        "5A":{"布达拉宫":"https://pic.rmb.bdstatic.com/bjh/xz1.jpeg","大昭寺":"https://pic.rmb.bdstatic.com/bjh/xz2.jpeg","巴松措":"https://pic.rmb.bdstatic.com/bjh/xz3.jpeg"},
        "4A":{"纳木错":"https://pic.rmb.bdstatic.com/bjh/xz4.jpeg","羊卓雍措":"https://pic.rmb.bdstatic.com/bjh/xz5.jpeg"},
        "3A":{"鲁朗林海":"https://pic.rmb.bdstatic.com/bjh/xz6.jpeg"}
    },
    "陕西省": {
        "5A":{"兵马俑":"https://img2.baidu.com/it/u=3723533109,2276479399&fm=253&fmt=auto","华山":"https://img2.baidu.com/it/u=1972633232,3821031299&fm=253&fmt=auto","大雁塔":"https://pic.rmb.bdstatic.com/bjh/sxsh1.jpeg","华清池":"https://pic.rmb.bdstatic.com/bjh/sxsh2.jpeg"},
        "4A":{"法门寺":"https://pic.rmb.bdstatic.com/bjh/sxsh3.jpeg","金丝峡":"https://pic.rmb.bdstatic.com/bjh/sxsh4.jpeg"},
        "3A":{"壶口瀑布":"https://pic.rmb.bdstatic.com/bjh/sxsh5.jpeg","柞水溶洞":"https://pic.rmb.bdstatic.com/bjh/sxsh6.jpeg"}
    },
    "甘肃省": {
        "5A":{"莫高窟":"https://pic.rmb.bdstatic.com/bjh/gs1.jpeg","麦积山":"https://pic.rmb.bdstatic.com/bjh/gs2.jpeg","崆峒山":"https://pic.rmb.bdstatic.com/bjh/gs3.jpeg"},
        "4A":{"鸣沙山月牙泉":"https://pic.rmb.bdstatic.com/bjh/gs4.jpeg","张掖丹霞":"https://pic.rmb.bdstatic.com/bjh/gs5.jpeg"},
        "3A":{"扎尕那":"https://pic.rmb.bdstatic.com/bjh/gs6.jpeg"}
    },
    "青海省": {
        "5A":{"青海湖":"https://pic.rmb.bdstatic.com/bjh/qh1.jpeg","茶卡盐湖":"https://pic.rmb.bdstatic.com/bjh/qh2.jpeg"},
        "4A":{"塔尔寺":"https://pic.rmb.bdstatic.com/bjh/qh3.jpeg","坎布拉":"https://pic.rmb.bdstatic.com/bjh/qh4.jpeg"},
        "3A":{"孟达天池":"https://pic.rmb.bdstatic.com/bjh/qh5.jpeg"}
    },
    "宁夏": {
        "5A":{"沙湖":"https://pic.rmb.bdstatic.com/bjh/nx1.jpeg","沙坡头":"https://pic.rmb.bdstatic.com/bjh/nx2.jpeg"},
        "4A":{"镇北堡影视城":"https://pic.rmb.bdstatic.com/bjh/nx3.jpeg","贺兰山":"https://pic.rmb.bdstatic.com/bjh/nx4.jpeg"},
        "3A":{"六盘山":"https://pic.rmb.bdstatic.com/bjh/nx5.jpeg"}
    },
    "新疆": {
        "5A":{"天山天池":"https://pic.rmb.bdstatic.com/bjh/xj1.jpeg","喀纳斯":"https://pic.rmb.bdstatic.com/bjh/xj2.jpeg","吐鲁番葡萄沟":"https://pic.rmb.bdstatic.com/bjh/xj3.jpeg"},
        "4A":{"赛里木湖":"https://pic.rmb.bdstatic.com/bjh/xj4.jpeg","那拉提":"https://pic.rmb.bdstatic.com/bjh/xj5.jpeg"},
        "3A":{"火焰山":"https://pic.rmb.bdstatic.com/bjh/xj6.jpeg"}
    }
}

# 登录注册
def auth_page():
    st.markdown("# 🏞️ 全国景区留言评价平台（视频版）")
    st.markdown("#### 支持文字+视频留言 · 高赞自动上景区官方区")
    tab1, tab2 = st.tabs(["🔐 登录账号", "📝 注册新用户"])

    with tab1:
        un = st.text_input("用户名")
        pw = st.text_input("密码", type="password")
        if st.button("登录", type="primary", use_container_width=True):
            if un in st.session_state.users and st.session_state.users[un]["pwd"] == pw:
                st.session_state.logged_in = True
                st.session_state.current_user = un
                st.rerun()
            else:
                st.error("账号或密码错误，请重试")

    with tab2:
        new_un = st.text_input("设置用户名")
        new_pw = st.text_input("设置密码", type="password")
        avatar = st.selectbox("选择头像",["👤","👦","👧","🧑","👨","👩","🦸","🧙"])
        if st.button("立即注册", use_container_width=True):
            if not new_un or not new_pw:
                st.warning("用户名和密码不能为空")
            elif new_un in st.session_state.users:
                st.error("用户名已被注册，请换一个")
            else:
                st.session_state.users[new_un] = {"pwd":new_pw,"avatar":avatar,"is_admin":False}
                save_users(st.session_state.users)
                st.success("注册成功！请前往登录")

# 主页面
def main():
    user_info = st.session_state.users[st.session_state.current_user]
    is_admin = user_info.get("is_admin", False)
    current_user = st.session_state.current_user

    # 顶部导航栏
    top_left, top_mid, top_right = st.columns([4,4,2])
    with top_left:
        st.markdown(f"# 🏞️ 全国景区留言 | {user_info['avatar']} {current_user}")
    with top_mid:
        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            if st.button("🏠 首页", use_container_width=True):
                st.session_state.page_tab = "首页"
                st.rerun()
        with nav2:
            if st.button("❤️ 我的收藏", use_container_width=True):
                st.session_state.page_tab = "收藏"
                st.rerun()
        with nav3:
            if st.button("📤 我的发布", use_container_width=True):
                st.session_state.page_tab = "发布"
                st.rerun()
    with top_right:
        if st.button("退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

    st.divider()

    # ========== 首页 ==========
    if st.session_state.page_tab == "首页":
        # 筛选景区
        st.subheader("📍 筛选景区")
        col1, col2, col3 = st.columns(3)
        with col1:
            pro = st.selectbox("选择省份", list(scenic_dict.keys()))
        with col2:
            level_type = st.selectbox("景区等级", ["5A","4A","3A"])
        with col3:
            key = st.text_input("🔍 搜索景区名称")

        spot_dict = scenic_dict[pro][level_type]
        spot_list = list(spot_dict.keys())
        filter_scenic = [s for s in spot_list if key in s]
        spot = st.selectbox("选择具体景区", filter_scenic)

        # 景区官方推荐视频
        st.subheader("🎬 景区官方推荐视频（高赞自动入选）")
        top_key = f"{pro}_{level_type}_{spot}"
        if top_key in st.session_state.top_video_data:
            top_vid_path = st.session_state.top_video_data[top_key]
            if os.path.exists(top_vid_path):
                st.video(top_vid_path)
                st.info("✅ 此视频点赞最高且作者授权，已自动进入景区官方介绍区")
        else:
            st.info("暂无高赞授权视频，快来发布吧！")

        st.image(spot_dict[spot], caption=f"{spot}（{level_type}景区）", use_column_width=True)
        st.divider()

        # 发表评价（含视频时长限制：最长60秒）
        st.subheader("✍️ 发表评价（文字+视频，视频最长60秒）")
        colA, colB = st.columns(2)
        with colA:
            grade = st.radio("总体评价", ["好评", "一般", "差评"], horizontal=True)
        with colB:
            star = st.radio("星级打分", ["⭐⭐⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐","⭐⭐","⭐"], horizontal=True)

        msg = st.text_area("写下你的游玩体验", height=120)
        uploaded_video = st.file_uploader("上传景区视频（MP4，≤60秒）", type=["mp4"])
        agree_auth = st.checkbox("✅ 同意授权：点赞最高自动上传至景区官方介绍区")

        video_path = ""
        if uploaded_video is not None:
            # 限制视频时长
            temp_vid = uploaded_video
            clip = VideoFileClip(temp_vid)
            duration = clip.duration
            clip.close()
            if duration > 60:
                st.error("❌ 视频超过60秒，请裁剪后重新上传！")
            else:
                unique_name = str(uuid.uuid4()) + ".mp4"
                save_path = os.path.join("videos", unique_name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_video.read())
                video_path = save_path
                st.success(f"✅ 视频上传成功，时长：{round(duration,1)}秒")

        if st.button("提交留言", type="primary", use_container_width=True):
            if not msg.strip() and not video_path:
                st.warning("请输入文字或上传视频至少一项")
            else:
                mid = len(st.session_state.message_list) + 1
                new = pd.DataFrame({
                    "mid":[mid],"用户名":[current_user],"头像":[user_info["avatar"]],
                    "省份":[pro],"景区名称":[spot],"景区等级":[level_type],
                    "评价等级":[grade],"星级":[star],"留言内容":[msg],
                    "视频路径":[video_path],"点赞数":[0],"授权同意":[agree_auth],"是否上景区首页":[False]
                })
                st.session_state.message_list = pd.concat([st.session_state.message_list, new], ignore_index=True)
                save_messages(st.session_state.message_list)

                # 自动更新高赞视频到景区首页
                area_key = f"{pro}_{level_type}_{spot}"
                area_df = st.session_state.message_list[
                    (st.session_state.message_list["省份"]==pro) &
                    (st.session_state.message_list["景区名称"]==spot) &
                    (st.session_state.message_list["授权同意"]==True) &
                    (st.session_state.message_list["视频路径"]!="")
                ]
                if not area_df.empty:
                    top_idx = area_df["点赞数"].idxmax()
                    top_video_path = area_df.loc[top_idx, "视频路径"]
                    st.session_state.top_video_data[area_key] = top_video_path
                    save_top_video(st.session_state.top_video_data)
                st.success("🎉 发布成功！")
                st.rerun()

        st.divider()
        # 全部留言
        st.subheader("📋 全部用户评价")
        filter_eva = st.selectbox("筛选评价", ["全部","好评","一般","差评"])
        df = st.session_state.message_list
        if filter_eva != "全部":
            df = df[df["评价等级"] == filter_eva]
        render_messages(df, current_user, is_admin)

    # ========== 我的收藏 ==========
    elif st.session_state.page_tab == "收藏":
        st.subheader("❤️ 我的收藏")
        collect_mids = st.session_state.collect_data.get(current_user, [])
        collect_df = st.session_state.message_list[st.session_state.message_list["mid"].isin(collect_mids)]
        if collect_df.empty:
            st.info("你还没有收藏任何留言")
        else:
            render_messages(collect_df, current_user, is_admin)

    # ========== 我的发布 ==========
    elif st.session_state.page_tab == "发布":
        st.subheader("📤 我的发布")
        my_df = st.session_state.message_list[st.session_state.message_list["用户名"] == current_user]
        if my_df.empty:
            st.info("你还没有发布任何留言")
        else:
            render_messages(my_df, current_user, is_admin)

    # 管理员后台
    if is_admin:
        st.divider()
        st.subheader("⚙️ 管理员后台")
        tabA, tabB, tabC = st.tabs(["用户管理","清空留言","清空评论"])
        with tabA:
            st.json(st.session_state.users)
        with tabB:
            if st.button("⚠️ 一键清空全部留言", type="primary", use_container_width=True):
                st.session_state.message_list = pd.DataFrame(columns=[
                    "mid","用户名","头像","省份","景区名称","景区等级",
                    "评价等级","星级","留言内容","视频路径","点赞数","授权同意","是否上景区首页"
                ])
                save_messages(st.session_state.message_list)
                st.rerun()
        with tabC:
            if st.button("⚠️ 一键清空所有评论", type="primary", use_container_width=True):
                st.session_state.comment_list = pd.DataFrame(columns=["mid","cid","用户名","头像","内容"])
                save_comments(st.session_state.comment_list)
                st.rerun()

# 统一渲染留言组件
def render_messages(df, current_user, is_admin):
    for idx, row in df.iterrows():
        mid = int(row["mid"])
        with st.container(border=True):
            colA, colB, colC, colD = st.columns([5,1,1,1])
            with colA:
                st.markdown(f"""
                **{row['头像']} {row['用户名']} | {row['景区名称']}({row['景区等级']}) | {row['评价等级']} {row['星级']}**
                {row['留言内容']}
                """)
                if row["视频路径"] and os.path.exists(row["视频路径"]):
                    st.video(row["视频路径"])
                if row["授权同意"]:
                    st.success("✅ 已授权：高赞自动上景区官方区")

            # 点赞
            with colB:
                if st.button(f"👍 {row['点赞数']}", key=f"like_{mid}"):
                    global_df = st.session_state.message_list
                    global_df.loc[global_df["mid"]==mid, "点赞数"] += 1
                    save_messages(global_df)
                    st.rerun()
            # 收藏
            with colC:
                collects = st.session_state.collect_data.get(current_user, [])
                if mid in collects:
                    if st.button("⭐已收藏", key=f"coll_{mid}"):
                        collects.remove(mid)
                        st.session_state.collect_data[current_user] = collects
                        save_collects(st.session_state.collect_data)
                        st.rerun()
                else:
                    if st.button("☆收藏", key=f"coll_{mid}"):
                        collects.append(mid)
                        st.session_state.collect_data[current_user] = collects
                        save_collects(st.session_state.collect_data)
                        st.rerun()
            # 删除
            with colD:
                if is_admin or row["用户名"] == current_user:
                    if st.button("🗑️", key=f"del_{mid}"):
                        st.session_state.message_list = st.session_state.message_list[st.session_state.message_list["mid"] != mid]
                        save_messages(st.session_state.message_list)
                        st.rerun()

            # 评论区
            st.markdown("---")
            st.write("💬 评论区")
            cmts = st.session_state.comment_list[st.session_state.comment_list["mid"] == mid]
            for _, cr in cmts.iterrows():
                st.markdown(f"{cr['头像']} **{cr['用户名']}**：{cr['内容']}")
                if is_admin or cr["用户名"] == current_user:
                    if st.button("删除评论", key=f"delc_{cr['cid']}"):
                        st.session_state.comment_list = st.session_state.comment_list.drop(_).reset_index(drop=True)
                        save_comments(st.session_state.comment_list)
                        st.rerun()
            cmt_text = st.text_input("写下评论", key=f"cmt_{mid}")
            if st.button("发送评论", key=f"sendc_{mid}"):
                if cmt_text.strip():
                    cid = len(st.session_state.comment_list) + 1
                    new_cmt = pd.DataFrame({"mid":[mid],"cid":[cid],"用户名":[current_user],"头像":[st.session_state.users[current_user]["avatar"]],"内容":[cmt_text]})
                    st.session_state.comment_list = pd.concat([st.session_state.comment_list, new_cmt], ignore_index=True)
                    save_comments(st.session_state.comment_list)
                    st.rerun()

# 程序入口
if not st.session_state.logged_in:
    auth_page()
else:
    main()
