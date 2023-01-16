# 載入對應的函式庫
import os
import re
import matplotlib.pyplot as plt
import cv2
import mysql.connector
from fuzzywuzzy import process
from google.cloud import vision
from PIL import Image
from flask import *
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

YOUR_SERVICE = 'cgi10105.json'

access_token = 'Your_access_token'
Channel_secret = 'Your_Channel_secret'
line_bot_api = LineBotApi(access_token)  # 輸入 你的 Channel access token
handler = WebhookHandler(Channel_secret)  # 輸入 你的 Channel secret

app = Flask(__name__)
with open('card_picture_url.json', encoding="utf-8") as f:
    card_picture_url = json.load(f)

# 輸入 Cloud SQL 帳號密碼
connection = mysql.connector.connect(host='mysql_host',
                                     database='credit_card',
                                     user='user_name',
                                     password='user_password')
my_cursor = connection.cursor()

# 輸入 postgresql 帳號密碼
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://luke4995:*******@******:******/invoice'
db = SQLAlchemy(app)



# 定義 LIFF ID
liff_id_for_submit = '***'
liff_id_for_cancel = '***'


# LIFF靜態頁面
@app.route('/submit')
def page():
    return render_template('card_insert_form.html', liffid=liff_id_for_submit)


@app.route('/cancel')
def cancel_page():
    return render_template('card_cancel_form.html', liffid=liff_id_for_cancel)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理來自 line_bot_api.reply_message 的 Message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    sql_cmd = "select * from aneka where uid='" + user_id + "'"
    query_data = db.engine.execute(sql_cmd)
    if len(list(query_data)) == 0:
        sql_cmd = "insert into aneka (uid) values('" + user_id + "');"
        db.engine.execute(sql_cmd)
    elif msg[:1] == "K":
        string = msg
        characters = "K"

        for x in range(len(characters)):
            string = string.replace(characters[x], "")
            credit_card_name = string
        card = {
            '上海銀行': [
                '小小兵回饋卡', '簡單卡', '小小兵分期卡', 'teresacard悠遊極緻卡'
            ],
            '土地銀行': [
                'icash2.0聯名鈦金卡', '極緻卡'
            ],
            '中國信託': [
                '中油聯名卡', 'allme卡', 'linepay信用卡', 'yahoo聯名卡', '商旅鈦金卡'
            ],
            '元大銀行': [
                '鑽金一卡通聯名卡', '鑽金智富icash聯名卡', '元大證券icash聯名卡', '世界卡'
            ],
            '王道銀行': [
                '低碳生活卡', 'funnow聯名卡', 'camacafevisa聯名卡'
            ],
            '台中銀行': [
                'mysense悠遊御璽卡', 'jcb哆啦a夢晶緻卡', 'jcb悠遊加油晶緻卡'
            ],
            '台北富邦': [
                'jpoints卡', 'momo卡', 'ju卡', 'openpossible聯名卡', '鑽保卡', '數位生活卡'
            ],
            '台新銀行': [
                '玫瑰giving卡', 'flygo卡', '街口聯名卡', '太陽卡', '旺卡'
            ],
            '台灣企銀': [
                '永續生活悠遊卡', '永續生活一卡通', '藝fun悠遊御璽卡', '銀色之愛卡', '宜蘭悠遊認同卡'
            ],
            '樂天銀行': [
                '台灣樂天信用卡', '樂虎卡', '樂天桃猿聯名卡'
            ],
            '永豐銀行': [
                'dawho現金回饋信用卡', 'sport卡', '現金回饋卡', '55688聯名卡', '幣倍卡'
            ],
            '玉山銀行': [
                'pi拍錢包信用卡', '家樂福悠遊聯名卡', '數位e卡輕時尚版', '數位e卡寵生活版', 'ubear信用卡'
            ],
            '兆豐銀行': [
                '宇宙明星bt21信用卡', 'e秒刷鈦金卡', 'megaone 一卡通聯名卡', '利多御璽卡', 'gogoro聯名卡'
            ],
            '合作金庫': [
                '卡娜赫拉悠遊聯名卡環保綠', 'i享樂生活卡', 'i運動卡', '樂活卡', '卡娜赫拉icash聯名卡夢想藍'
            ],
            '安泰銀行': [
                '悠遊分期卡', '悠遊鈦金卡', 'jcb晶緻卡'
            ],
            '花旗銀行': [
                '花旗現金回饋plus鈦金卡', '饗樂生活卡', 'pchomeprime聯名卡'
            ],
            '星展銀行': [
                'eco永續卡', '飛行世界商務卡'
            ],
            '美國運通': [
                '信用白金卡'
            ],
            '高雄銀行': [
                '高雄going鈦金卡'
            ],
            '國泰世華': [
                'CUBE卡', '蝦皮購物聯名卡', '台塑聯名卡', '現金回饋御璽卡'
            ],
            '將來銀行': [
                'visa簽帳金融卡'
            ],
            '第一銀行': [
                'ileo信用卡', 'livinggreen綠活卡', '義享天地聯名卡', 'icash聯名卡', '一卡通聯名卡'
            ],
            '凱基銀行': [
                '魔buy悠遊鈦金卡', '魔fun悠遊御璽卡', '現金回饋悠遊御璽卡'
            ],
            '渣打銀行': [
                '現金回饋御璽卡', 'theshoppingcard分期卡', '優先理財無限卡'
            ],
            '華南銀行': [
                'sny信用卡', 'i網購生活卡', '超鑽現金回饋卡', 'openpoint超級點數聯名卡', '嘟嘟房聯名卡'
            ],
            '華泰商銀': [
                'jcb晶緻卡'
            ],
            '陽信銀行': [
                '陽信jcb哆啦a夢晶緻卡', 'mastercard一卡通聯名鈦金卡', '悠遊visa金融卡', 'visa曜晶卡'
            ],
            '新光銀行': [
                'ou點點卡', '寰宇現金回饋卡', '悠遊聯名晶緻卡', '分期7卡', '無限卡'
            ],
            '滙豐銀行': [
                '現金回饋御璽卡', '匯鑽卡'
            ],
            '彰化銀行': [
                'my購卡', 'my樂現金回饋卡', 'jcb哆啦a夢悠遊晶緻卡'
            ],
            '臺灣銀行': [
                '一卡通鈦金商旅卡', '一卡通導盲犬認同卡', '祝福認同卡'
            ],
            '遠東商銀': [
                '遠東樂家卡', '快樂信用卡悠遊', 'bankee信用卡', 'cestmoi旅遊悠遊卡'
            ],
            '聯邦銀行': [
                '賴點一卡通御璽卡', 'jcb吉鶴卡', '綠卡', '幸福M卡', '微風悠遊聯名卡'
            ],
            'linebank': [
                '簽帳金融卡'
            ],
            '日盛銀行': [
                'allpass卡', '無限卡'
            ]
        }
        pattern = r'[A-Za-z]'

        b_name = []
        for j in card.keys():
            b_name.append(j)
            try:
                input_name = credit_card_name
                # print(bank, type(bank))
                if len(input_name) < 4:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='有誤,請至少輸入銀行名稱前四字'))
                    continue
                else:
                    input_name = input_name.replace(' ', '')
                    for i in input_name:
                        if '\u4e00' >= i >= '\u9fa5':
                            for T in re.findall(pattern, i):
                                t = T.lower()
                                input_name = input_name.replace(T, t)
                                after_name = input_name
                        else:
                            bank_name = input_name

                    # process.extractOne(‘stringA’,stringlist)/ 比較stringA與stringlist中的所有item，回傳最高分item與分數，格式(item,score)
                    bank_winner = process.extractOne(bank_name, b_name)
                    # print(bankwinner)
                    if bank_winner[1] <= 70:
                        # print('didn\'t have this bank! or have wrong text')
                        continue
                    else:
                        # print("信用卡所屬銀行: ", bankwinner[0])
                        # 開始選取上面選擇銀行所屬信用卡
                        pick_bank = bank_winner[0]
                        cd_name = []
                        for k in card[pick_bank]:
                            cd_name.append(k)
                        # print(pick_bank, '支援卡種:', cd_name)
                        # recommend = (pick_bank+'支援卡種:'+cd_name)
                        card_name = ""
                        for number, r in enumerate(cd_name):
                            card_name += f"第{number + 1}筆資料\n{r}\n"
                        txt_1 = '支援卡種:'
                        txt_1 += "\n" + card_name
                        recommend_message = [  # 串列
                            TextSendMessage(  # 傳送文字
                                text=pick_bank
                            ),
                            TextSendMessage(  # 傳送文字
                                text=txt_1
                            )
                        ]
                        line_bot_api.reply_message(event.reply_token, recommend_message)
                        break
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無效名稱, 請重新輸入"))
    elif msg == "優惠通路推薦":
        text1 = '''
1. 從資料庫資料裡選出該通路前三優惠,通路名稱前以X做為指令,例如輸入:X高鐵。
2. 從您個人卡片與阿內卡信用卡資料庫交叉比對裡選出該通路前三優惠,通路名稱前以M做為指令,例如輸入:M高鐵。
                '''
        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == '懶人推薦':
        try:
            message = TextSendMessage(
                text='請選擇以下功能',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="無腦萬用卡", text="無腦萬用卡")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="我就宅神卡", text="我就宅神卡")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="影音伴娛樂", text="影音伴娛樂")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '卡片管理':
        try:
            message = TextSendMessage(
                text='請選擇以下功能',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="新增個人卡片", text="新增個人卡片")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="刪除個人卡片", text="刪除個人卡片")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="查詢個人卡片", text="查詢個人卡片")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '新增個人卡片':
        insert_card(event, user_id)
    elif msg == '刪除個人卡片':
        cancel_card(event, user_id)
    elif msg == '查詢個人卡片':
        search_card(event, user_id)
    elif msg[:1] == '+':
        string = msg
        characters = "+"
        try:
            for x in range(len(characters)):
                insert_card_name = string.replace(characters[x], "")
                sql_cmd = "insert into card_table (bid, card_name) values('" + user_id + "','" + insert_card_name + "');"
                db.engine.execute(sql_cmd)
                text1 = "您的卡片新增成功，資料如下："
                text1 += "\n卡片名稱：" + insert_card_name
                insert_card_name_message = TextSendMessage(  # 顯示新增卡片資料
                    text=text1
                )
                line_bot_api.reply_message(event.reply_token, insert_card_name_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

    elif msg[:1] == 'X':  # 從資料庫資料裡選出該通路前三優惠
        string = msg
        characters = "X"
        for x in range(len(characters)):
            insert_card_name = string.replace(characters[x], "")

            def cards_top_discount(card_list, chose_channel):
                select_top_query = """SELECT concat(n.發卡銀行, n.別名)
                FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                WHERE r.通路名稱 = %s
                ORDER BY r.加總回饋 DESC
                LIMIT 3"""
                my_cursor.execute(select_top_query, (chose_channel,))
                top_reward = my_cursor.fetchall()
                top_bank_name = [i[0] for i in top_reward]
                # 檢查使用者卡片是否在top 3之一，如果有，就在最後一行顯示出：您已持有此卡！
                recommend_list = list()
                for i in top_bank_name:
                    if i in card_list:
                        select_query = """SELECT r.加總回饋, 
                        CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
                        CONCAT('評等：', n.信用卡評分, '顆星'), 
                        CONCAT('最高回饋：', r.加總回饋, '%'), 
                        CONCAT('回饋上限說明：', r.回饋上限說明),
                        CONCAT('備註：', r.備註), 
                        CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址, '。\n您已持有此卡！')
                        FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                        WHERE r.通路名稱 = %s AND concat(n.發卡銀行, n.別名) = %s"""
                        my_cursor.execute(select_query, (chose_channel, i))
                        recommend_list.append(my_cursor.fetchall()[0])
                    else:
                        select_query = """SELECT r.加總回饋, 
                        CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
                        CONCAT('評等：', n.信用卡評分, '顆星'), 
                        CONCAT('最高回饋：', r.加總回饋, '%'), 
                        CONCAT('回饋上限說明：', r.回饋上限說明),
                        CONCAT('備註：', r.備註),
                        CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址)
                        FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                        WHERE r.通路名稱 = %s AND concat(n.發卡銀行, n.別名) = %s"""
                        my_cursor.execute(select_query, (chose_channel, i))
                        recommend_list.append(my_cursor.fetchall()[0])

                return recommend_list

            # 模擬使用者丟進來的資料
            cards_top_discount_list = (cards_top_discount([""], insert_card_name))

            card_a1 = cards_top_discount_list[0][1]
            card_a10 = card_a1[3:]
            card_a2 = cards_top_discount_list[0][2]
            card_a11 = card_a2[3:]
            card_a3 = cards_top_discount_list[0][3]
            card_a4 = cards_top_discount_list[0][4]
            card_a5 = cards_top_discount_list[0][5]
            card_a6 = card_a5[7:]
            card_a7 = cards_top_discount_list[0][-1]
            card_a8 = card_a7[15:]
            url_1 = card_picture_url[card_a10+card_a11]

            card_b1 = cards_top_discount_list[1][1]
            card_b10 = card_b1[3:]
            card_b2 = cards_top_discount_list[1][2]
            card_b11 = card_b2[3:]
            card_b3 = cards_top_discount_list[1][3]
            card_b4 = cards_top_discount_list[1][4]
            card_b5 = cards_top_discount_list[1][5]
            card_b6 = card_b5[7:]
            card_b7 = cards_top_discount_list[1][-1]
            card_b8 = card_b7[15:]
            url_2 = card_picture_url[card_b10 + card_b11]

            card_c1 = cards_top_discount_list[2][1]
            card_c10 = card_c1[3:]
            card_c2 = cards_top_discount_list[2][2]
            card_c11 = card_c2[3:]
            card_c3 = cards_top_discount_list[2][3]
            card_c4 = cards_top_discount_list[2][4]
            card_c5 = cards_top_discount_list[2][5]
            card_c6 = card_c5[7:]
            card_c7 = cards_top_discount_list[2][-1]
            card_c8 = card_c7[15:]
            url_3 = card_picture_url[card_c10 + card_c11]

            try:
                message = [  # 串列
                    TextSendMessage(  # 傳送文字
                        text="以下是" + insert_card_name + "通路前三名優惠哦~"
                    ),
                    TemplateSendMessage(
                        alt_text=insert_card_name + '前三名優惠',
                        template=CarouselTemplate(
                            columns=[
                                CarouselColumn(
                                    thumbnail_image_url=url_1,
                                    title=card_a10+card_a11,
                                    text=card_a4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_a3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_a6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_a8
                                        ),

                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url=url_2,
                                    title=card_b10+card_b11,
                                    text=card_b4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_b3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_b6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_b8
                                        ),

                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url=url_3,
                                    title=card_c10+card_c11,
                                    text=card_c4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_c3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_c6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_c8
                                        ),

                                    ]
                                ),
                            ]
                        )
                    )
                ]
                line_bot_api.reply_message(event.reply_token, message)
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

    elif msg[:1] == 'M':  # 從User資料庫與信用卡資料庫交叉比對裡選出該通路前三優惠
        string = msg
        characters = "M"
        for x in range(len(characters)):
            insert_card_name = string.replace(characters[x], "")
            sql_cmd = "select * from card_table where bid= '" + user_id + "'"
            query_data = db.engine.execute(sql_cmd)
            card_data = list(query_data)
            # print(len(card_data))
            card_name = ""
            for number, r in enumerate(card_data):
                card_name += r[2] + '\t'
            list_4 = card_name.split()
            list_5 = list_4

            def top_bank_list(chose_channel):
                card_my_cursor = connection.cursor()
                select_top_query = """SELECT CONCAT(n.發卡銀行, n.別名)
                FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                WHERE r.通路名稱 = %s
                ORDER BY r.加總回饋 DESC
                LIMIT 3"""
                card_my_cursor.execute(select_top_query, (chose_channel,))
                top_reward = card_my_cursor.fetchall()
                top_bank_name = [i[0] for i in top_reward]
                return top_bank_name

            def user_cards(card_list, chose_channel):
                result_list = list()
                for each_card in card_list:
                    # 下sql指令， %s 分別放入使用者丟進來的 card_list 和 chose_channel
                    sql_select_query = """SELECT r.加總回饋, 
                    CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
                    CONCAT('評等：', n.信用卡評分, '顆星'), 
                    CONCAT('最高回饋：', r.加總回饋, '%'), 
                    CONCAT('回饋上限說明：', r.回饋上限說明),  
                    CONCAT('備註：', r.備註),
                    CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址)
                    FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                    WHERE CONCAT(n.發卡銀行, n.別名) = %s 
                    AND r.通路名稱 = %s"""
                    my_cursor.execute(sql_select_query, (each_card, chose_channel))
                    each_reward = my_cursor.fetchall()
                    result_list.append(each_reward)

                # chose_channel 通路前三高優惠的卡名
                top_bank_name = top_bank_list(chose_channel)
                # 從全資料庫前三高優惠中，去掉跟 card_list 重複的卡
                union_card = list(set(top_bank_name).difference(card_list))
                union_card.sort(key=top_bank_name.index)

                recommend_list = list()
                for i in union_card:
                    select_query = """SELECT r.加總回饋, 
                    CONCAT('【阿內卡優惠推薦】銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
                    CONCAT('評等：', n.信用卡評分, '顆星'), 
                    CONCAT('最高回饋：', r.加總回饋, '%'), 
                    CONCAT('回饋上限說明：', r.回饋上限說明),
                    CONCAT('備註：', r.備註), 
                    CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址)
                    FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
                    WHERE r.通路名稱 = %s AND CONCAT(n.發卡銀行, n.別名) = %s"""
                    my_cursor.execute(select_query, (chose_channel, i))
                    recommend_list.append(my_cursor.fetchall()[0])

                # 使用者手上的卡的優惠排名
                result_list = [i[0] for i in result_list]
                card_rank = sorted(result_list, reverse=True)

                # count_not_zero 先把使用者手上有幾張大於0的張數抓出來
                count_not_zero = 0
                for i in card_rank:
                    if i[0] > 0:
                        count_not_zero += 1

                # 使用者有三張以上的卡，且有三張以上優惠>0
                if len(card_rank) >= 3 and count_not_zero >= 3:
                    return card_rank[0:3]
                # 使用者有兩張以上的卡，且有一張以上優惠>0
                elif len(card_rank) >= 2 and 0 < count_not_zero <= 2:
                    answer = card_rank[0:count_not_zero]
                    answer += recommend_list[0:3 - count_not_zero]
                    return answer
                # 使用者只有一張卡，且優惠>0
                elif len(card_rank) >= 1 and count_not_zero >= 1:
                    card_rank += recommend_list
                    return card_rank
                else:
                    return recommend_list[0:3]

            cards_top_discount_list = (user_cards(list_5, insert_card_name))
            # print(cards_top_discount_list)
            card_a1 = cards_top_discount_list[0][1]
            card_a2 = cards_top_discount_list[0][2]
            card_a3 = cards_top_discount_list[0][3]
            card_a4 = cards_top_discount_list[0][4]
            card_a5 = cards_top_discount_list[0][5]
            card_a6 = card_a5[7:]
            card_a7 = cards_top_discount_list[0][-1]
            card_a8 = card_a7[15:]

            card_b1 = cards_top_discount_list[1][1]
            card_b2 = cards_top_discount_list[1][2]
            card_b3 = cards_top_discount_list[1][3]
            card_b4 = cards_top_discount_list[1][4]
            card_b5 = cards_top_discount_list[1][5]
            card_b6 = card_b5[7:]
            card_b7 = cards_top_discount_list[1][-1]
            card_b8 = card_b7[15:]

            card_c1 = cards_top_discount_list[2][1]
            card_c2 = cards_top_discount_list[2][2]
            card_c3 = cards_top_discount_list[2][3]
            card_c4 = cards_top_discount_list[2][4]
            card_c5 = cards_top_discount_list[2][5]
            card_c6 = card_c5[7:]
            card_c7 = cards_top_discount_list[2][-1]
            card_c8 = card_c7[15:]

            if len(card_data) > 0:
                message = [  # 串列
                    TextSendMessage(  # 傳送文字
                        text="以下是" + insert_card_name + "通路前三名優惠哦~"
                    ),
                    TemplateSendMessage(
                        alt_text=insert_card_name + '前三名優惠',
                        template=CarouselTemplate(
                            columns=[
                                CarouselColumn(
                                    thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                                    title=card_a1,
                                    text=card_a2 + "\n" + card_a4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_a3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_a6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_a8
                                        ),

                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                                    title=card_b1,
                                    text=card_b2 + "\n" + card_b4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_b3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_b6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_b8
                                        ),

                                    ]
                                ),
                                CarouselColumn(
                                    thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                                    title=card_c1,
                                    text=card_c2 + "\n" + card_c4,
                                    actions=[
                                        PostbackTemplateAction(
                                            label=card_c3,
                                            data='action=sell&item=披薩'
                                        ),
                                        MessageTemplateAction(
                                            label='回饋上限說明',
                                            text=card_c6
                                        ),
                                        URITemplateAction(
                                            label='信用卡官網連結',
                                            uri=card_c8
                                        ),

                                    ]
                                ),
                            ]
                        )
                    )
                ]
                line_bot_api.reply_message(event.reply_token, message)
            else:
                # 沒有卡片記錄
                no_card_message = TextSendMessage(
                    text='您目前沒有新增卡片記錄哦！'
                )
                line_bot_api.reply_message(event.reply_token, no_card_message)

    elif msg[:1] == '@':  # 處理LIFF傳回的刪除FORM資料
        cancel_form(event, msg, user_id)
    elif msg[:2] == '##':  # 處理LIFF傳回的新增FORM資料
        insert_form(event, msg, user_id)
    elif msg == "影音伴娛樂":
        c1 = [('影音拌娛樂', '銀行：凱基銀行', '卡名：魔FUN悠遊御璽卡',
               '影音娛樂平均分數：33.5%',
               '信用卡優惠詳情以官網公告為主：https://www.kgibank.com.tw/zh-tw/personal/credit-card/list/more-fun-visa-signature-card')]
        msg_a1 = c1[0][1]
        msg_a4 = msg_a1[3:]  # name
        msg_a5 = c1[0][2]
        msg_a6 = msg_a5[3:]  # 卡name
        msg_a7 = c1[0][3]
        msg_a8 = c1[0][4]
        msg_a9 = msg_a8[15:]
        message = TemplateSendMessage(
            alt_text='影音伴娛樂',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://images.contentstack.io/v3/assets/blt4ca32b8be67c85f8/blt3cc7211a605173b3/623447ea815d0316181c5523/image_(1).png?width=256&disable=upscale&fit=bounds&auto=webp',
                        title=msg_a4 + msg_a6,
                        text=msg_a7,
                        actions=[
                            URIAction(
                                label='信用卡官網',
                                uri=msg_a9
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=披薩'
                            ),
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif msg == "我就宅神卡":
        c2 = [('我就宅神卡', '銀行：新光銀行', '卡名：OU點點卡',
               '外送平台平均優惠：22%', '網路購物平均優惠：15.8%', '超商平均優惠：12.75%',
               '信用卡優惠詳情以官網公告為主：https://www.skbank.com.tw/campaign/skbankOU/')]
        msg_a1 = c2[0][1]
        msg_a4 = msg_a1[3:]  # name
        msg_a5 = c2[0][2]
        msg_a6 = msg_a5[3:]  # 卡name
        msg_a7 = c2[0][3]
        msg_a8 = c2[0][4]
        msg_a9 = c2[0][5]
        msg_a10 = c2[0][6]
        msg_a11 = msg_a10[15:]
        message = TemplateSendMessage(
            alt_text='我就宅神卡',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://www.skbank.com.tw/skbank_resource/leap_do/cc_main_picture/1655106028742/OU01.png',
                        title=msg_a4 + msg_a6,
                        text=msg_a7 + "\n" + msg_a8 + "\n" + msg_a9,
                        actions=[
                            URIAction(
                                label='信用卡官網',
                                uri=msg_a11
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=披薩'
                            ),
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    elif msg == "無腦萬用卡":
        c3 = [('無腦萬用卡', '銀行：凱基銀行', '卡名：魔BUY悠遊鈦金卡',
               '外送平台平均優惠：8%', '影音娛樂平均優惠：3%', '網路購物平均優惠:6.96%', '行動支付平均優惠：5.35%',
               '超商平均優惠：8%',
               '信用卡優惠詳情以官網公告為主：https://www.kgibank.com.tw/zh-tw/personal/credit-card/list/more-buy-credit-card')]
        msg_a1 = c3[0][1]
        msg_a4 = msg_a1[3:]  # name
        msg_a5 = c3[0][2]
        msg_a6 = msg_a5[3:]  # 卡name
        msg_a7 = c3[0][3]
        msg_a8 = c3[0][4]
        msg_a9 = c3[0][5]
        msg_a10 = c3[0][6]
        msg_a12 = c3[0][8]
        msg_a13 = msg_a12[15:]
        message = TemplateSendMessage(
            alt_text='無腦萬用卡',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://images.contentstack.io/v3/assets/blt4ca32b8be67c85f8/blt114d8a9efec6527a/623447d32da66c041dc27b42/image.png',
                        title=msg_a4 + msg_a6,
                        text=msg_a7 + "\n" + msg_a8 + "\n" + msg_a9 + "\n" + msg_a10,
                        actions=[
                            URIAction(
                                label='信用卡官網',
                                uri=msg_a13
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=披薩'
                            ),
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    elif msg == '理財':
        vava_carousel(event)
    elif msg == '理財小教室':
        sendConfirm(event)
    elif msg == '投資理財宣導':
        sendImgMap(event)
    elif msg == '呼叫阿內卡':
        flexmessage(event)
    elif msg == '三大發卡組織比較':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://i.imgur.com/KUvsUyt.png',
                preview_image_url='https://i.imgur.com/KUvsUyt.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        finally:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '信用紀錄':
        try:
            message = TextSendMessage(
                text="透過每次的信用卡消費並在每次帳單支付時都能全額繳清付款，這些都會反映在個人的信用聯徵評等分數之中，而這些分數也會影響未來進行貸款等需要以信用作為基準的服務。"
            )
            line_bot_api.reply_message(event.reply_token, message)
        finally:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '循環利息':
        try:
            message = TextSendMessage(
                text="循環信用是持卡人沒全額付清信用卡帳單時會開啟的功能，而啟動循環信用就要支付循環利息及違約金。"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '申請資格':
        try:
            message = TextSendMessage(
                text="正卡年齡需滿20歲，附卡15歲,身分雙證件（如身分證）,申請時附上適合的財力證明。"
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '保險宣導':
        try:
            video_message = VideoSendMessage(
                original_content_url='https://i.imgur.com/9NFqI9S.mp4',
                preview_image_url='https://i.imgur.com/lLUglvf.png'
            )
            line_bot_api.reply_message(event.reply_token, video_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '蝦皮購物':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://i.imgur.com/MpLLozl.png',
                preview_image_url='https://i.imgur.com/MpLLozl.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '星巴克':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://i.imgur.com/vmVXCHx.png',
                preview_image_url='https://i.imgur.com/vmVXCHx.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '熊貓':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://www.beurlife.com/wp-content/uploads/2019/10/FB-foodpanda-20221006.png',
                preview_image_url='https://www.beurlife.com/wp-content/uploads/2019/10/FB-foodpanda-20221006.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '優步':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://www.beurlife.com/wp-content/uploads/2019/10/FB-UberEats-20221006.png',
                preview_image_url='https://www.beurlife.com/wp-content/uploads/2019/10/FB-UberEats-20221006.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '家樂福':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://i.imgur.com/FoKh0HP.png',
                preview_image_url='https://i.imgur.com/FoKh0HP.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '大潤發':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://picture-original.fevercdn.com/page-rt-mart-202219-9139967c-f983-49d3-b690-397b6249fe3e.jpg',
                preview_image_url='https://picture-original.fevercdn.com/page-rt-mart-202219-9139967c-f983-49d3-b690-397b6249fe3e.jpg'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '網家':
        try:
            image_message = ImageSendMessage(
                original_content_url='https://i.imgur.com/Db3jWOm.png',
                preview_image_url='https://i.imgur.com/Db3jWOm.png'
            )
            line_bot_api.reply_message(event.reply_token, image_message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '留在原地':
        try:
            message = [  # 串列
                StickerSendMessage(  # 傳送貼圖
                    package_id='789',
                    sticker_id='10855'
                ),
                TextSendMessage(  # 傳送文字
                    text="可輸入『阿內卡指令』哦~"
                ),
                ImageSendMessage(  # 傳送圖片
                    original_content_url="https://i.imgur.com/yfJ9BmI.png",
                    preview_image_url="https://i.imgur.com/yfJ9BmI.png"
                )
            ]
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

    elif msg == '信用卡優惠':
        try:
            message = TextSendMessage(
                text='請選擇商家及通路優惠',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="蝦皮購物", text="蝦皮購物")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="星巴克", text="星巴克")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="熊貓", text="熊貓")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="Ubereats", text="優步")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="家樂福", text="家樂福")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="大潤發", text="大潤發")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="pchome", text="網家")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
    elif msg == '信用卡指南':
        try:
            message = TextSendMessage(
                text='請選擇以下功能',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=MessageAction(label="三大發卡組織比較", text="三大發卡組織比較")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="信用紀錄", text="信用紀錄")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="循環利息", text="循環利息")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="申請資格", text="申請資格")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="投資理財宣導", text="投資理財宣導")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="保險宣導", text="保險宣導")
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def insert_card(event, user_id):  # 新增卡片
    try:
        sql_cmd = "select * from card_table where bid='" + user_id + "'"
        query_data = db.engine.execute(sql_cmd)
        if len(list(query_data)) >= 0:
            message = TemplateSendMessage(
                alt_text='新增卡片',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                            title='手動新增卡片',
                            text="手動輸入新增範例:\n+中國信託英雄聯盟卡",
                            actions=[
                                URIAction(
                                    label='使用說明',
                                    uri='https://hackmd.io/@tTXrmXXUQtGZ_F0EsvAcxg/SyOqN6aLs'
                                ),
                                URITemplateAction(
                                    label='新增卡片',
                                    uri='https://liff.line.me/' + liff_id_for_submit
                                ),
                                PostbackTemplateAction(
                                    label='↑↑↑↑',
                                    data='action=sell&item=披薩'
                                ),
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                            title='拍照或相簿新增',
                            text='相片尺吋規格請參照使用說明',
                            actions=[
                                CameraAction(
                                    label='拍照'
                                ),
                                CameraRollAction(
                                    label='相簿',
                                ),
                                PostbackTemplateAction(
                                    label='↑↑↑↑',
                                    data='action=sell&item=飲料'
                                ),
                            ]
                        )
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def search_card(event, user_id):  # 查詢卡片
    try:
        sql_cmd = "select * from card_table where bid= '" + user_id + "'"
        query_data = db.engine.execute(sql_cmd)
        card_data = list(query_data)
        card_name = ""
        for number, r in enumerate(card_data):
            card_name += f"第{number + 1}筆資料\n{r[2]}\n"
            # print(card_name)
        if len(card_data) > 0:
            message = [
                TextSendMessage(  # 顯示卡片資料
                    text=card_name
                ),
                TemplateSendMessage(  # 顯示確認視窗
                    alt_text='有需要刪除卡片嗎?',
                    template=ConfirmTemplate(
                        text='有需要刪除卡片嗎?',
                        actions=[
                            MessageTemplateAction(  # 按鈕選項
                                label='是',
                                text='刪除卡片'
                            ),
                            MessageTemplateAction(
                                label='否',
                                text='歡迎再使用其他功能哦~'
                            )
                        ]
                    )
                )
            ]
        else:  # 沒有卡片記錄
            message = TextSendMessage(
                text='您目前沒有新增卡片記錄哦！'
            )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def cancel_card(event, user_id):  # 處理刪除卡片
    try:
        sql_cmd = "select * from card_table where bid='" + user_id + "'"
        query_data = db.engine.execute(sql_cmd)
        if len(list(query_data)) > 0:
            message = TemplateSendMessage(
                alt_text="刪除卡片",
                template=ButtonsTemplate(
                    thumbnail_image_url='https://i.imgur.com/cdcDtAA.png',
                    title='刪除卡片',
                    text='一卡握在手生活好幫手',
                    actions=[
                        URITemplateAction(label='刪除卡片', uri='https://liff.line.me/' + liff_id_for_cancel)
                        # 開啟LIFF讓使用者輸入訂房資料
                    ]
                )
            )
        else:  # 沒有卡片記錄
            message = TextSendMessage(
                text='您目前沒有新增卡片記錄哦！'
            )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def insert_form(event, msg, user_id):  # 處理LIFF傳回的新增FORM資料
    try:
        flist = msg[2:].split('/')  # 去除前三個「#」字元再分解字串
        roomtype = flist[0]  # 取得輸入資料
        sql_cmd = "insert into card_table (bid, card_name) values('" + user_id + "','" + roomtype + "');"
        db.engine.execute(sql_cmd)
        text1 = "您的卡片新增成功，資料如下："
        text1 += "\n卡片名稱：" + roomtype
        message = TextSendMessage(  # 顯示新增卡片資料
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def cancel_form(event, msg, user_id):  # 處理LIFF傳回的刪除FORM資料
    try:
        flist = msg[1:].split('/')  # 去除前三個「#」字元再分解字串
        # print(flist)
        card_name = flist[0]  # 取得輸入資料
        # print(card_name)
        sqlcmd = "delete from card_table where card_name like ('" + card_name + "') and bid=('" + user_id + "');"
        db.engine.execute(sqlcmd)
        text1 = "您的卡片刪除成功，資料如下："
        text1 += "\n卡片名稱：" + card_name
        message = TextSendMessage(  # 顯示卡片資料
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


@handler.add(MessageEvent)
def opencv_message(event):
    if (event.message.type == "image"):
        send_image = line_bot_api.get_message_content(event.message.id)
        userid = event.source.user_id
        path = userid + '.jpg'
        with open(path, 'wb') as fd:
            for photo in send_image.iter_content():
                fd.write(photo)
            # cv2 讀入圖片
            img = cv2.resize(cv2.imread(path, 1), (900, 540))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            canny = cv2.Canny(gray, 30, 150, apertureSize=3, L2gradient=0)
            # cv2.imshow("canny_image", canny)
            ret, binary = cv2.threshold(canny, 127, 255, cv2.THRESH_BINARY)
            # cv2.imshow("binary",binary )
            binary_dilate = cv2.dilate(binary, None, iterations=15)
            binary_erode = cv2.erode(binary_dilate, None, iterations=15)
            # cv2.imshow("binary_erode", binary_erode )

            contours, hierarchy = cv2.findContours(binary_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # print("contours 数量：", len(contours))

            contourslist = []
            for i in range(len(contours)):
                x, y, w, h = cv2.boundingRect(contours[i])
                if w > 200:
                    contourslist.append((i, w))
                else:
                    pass

            # print('篩選完的結果:', contourslist)
            sort_contourslist = sorted(contourslist, key=lambda x: x[1])
            # print('篩選且排序完的結果:', sort_contourslist)

            external_img = cv2.drawContours(img.copy(), contours, sort_contourslist[len(sort_contourslist) - 1][0],
                                            (0, 255, 0),
                                            1)  # 不是0就是1
            # cv2.imshow("external_img", external_img)

            # 存成新圖片
            x, y, w, h = cv2.boundingRect(contours[sort_contourslist[len(sort_contourslist) - 1][0]])
            new_image = external_img[y:y + h, x:x + w]  # 先用y确定高，再用x确定宽
            image = cv2.resize(new_image, (600, 380))  # 改大一點比較好看到
            # cv2.imshow("resized_with_external_image", image)

            cv2.waitKey(0)
            cv2.destroyAllWindows()
            cv2.waitKey(1)

            cv2.imwrite("external.jpg", image)

            # 讀入external.jpg
            YOUR_PIC = 'external.jpg'
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = YOUR_SERVICE
            client = vision.ImageAnnotatorClient()

            with open(YOUR_PIC, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)

            response = client.text_detection(image=image)

            # 將抓到資料存進response_list
            response_list = []
            for i in response.text_annotations:
                response_list.append(i)

            # 過濾掉str type, 只留下數字資料存入just_int
            just_int = []
            for j in response_list:
                try:
                    int(j.description)
                    just_int.append(j)
                except ValueError as error:
                    pass

            im = Image.open(YOUR_PIC)
            # plt.imshow(im)

            # 建立一個data list來放卡號
            finallist = []
            for text in just_int:
                #     print(text)
                a = [(v.x, v.y) for v in text.bounding_poly.vertices]
                a.append(a[0])
                x, y = zip(*a)
                if 140 > max(x) - min(x) > 40 and len(text.description) == 4:  # 篩選出卡好的條件(框選的寬度 & 字串長度)
                    # print("辨識結果:", text.description)
                    finallist.append(text.description)
                    plt.plot(x, y, color='blue')

            # print('最終結果:', finallist)

            cardnumber = ''
            for i in range(2):  # 只取前面8碼
                cardnumber += finallist[i]

            # print('card_number:', cardnumber)
            try:
                card_number_dict = {"中國信託linepay卡": "41823087", "中國信託英雄聯盟卡": "52468939",
                                    "國泰世華cube卡": "51571328", "玉山銀行ubear卡": "55893666",
                                    "玉山銀行pi卡": "52425559",
                                    "台新銀行gogo卡": "41476350", "台新銀行街口聯名卡": "35695879",
                                    "富邦銀行J卡(Line points回饋)": "35696962",
                                    "富邦銀行數位生活卡": "52410845", "花旗銀行現金回饋plus卡": "54080589",
                                    "永豐銀行55688卡": "51992302", "永豐銀行幣倍卡": "55884300",
                                    "永豐銀行大戶卡": "46965605",
                                    "第一銀行ileo卡": "52413149", "將來銀行將將卡": "40400999",
                                    "LineBank簽帳金融卡": "40400808",
                                    "富邦銀行MoMo卡": "52410878", "富邦銀行J卡(現金回饋)": "35696961",
                                    "渣打銀行現金回饋卡": "43772262",
                                    "元大銀行鑽金卡": "46115899", "土地銀行icash2.0聯名卡": "51584205",
                                    "土地銀行麟洋卡": "49070834", "聯邦銀行微風聯名卡": "51795191",
                                    "星展銀行eco永續卡": "54836820",
                                    "聯邦銀行聯邦幸福M卡": "51570938", "新光銀行寰宇現金回饋卡": "48898888",
                                    "台新銀行Richart簽帳金融卡": "46672606", "永豐銀行DAWHO簽帳金融卡": "52364601",
                                    "匯豐銀行匯豐簽帳金融卡": "48479446", "凱基銀行魔FUN悠遊御璽卡": "46190500"}
                list_of_key = list(card_number_dict.keys())
                list_of_value = list(card_number_dict.values())
                user_id = event.source.user_id
                card_name = list_of_value.index(cardnumber)
                card_name_msg = (list_of_key[card_name])
                sql_cmd = "insert into card_table (bid, card_name) values('" + user_id + "','" + card_name_msg + "');"
                db.engine.execute(sql_cmd)
                text1 = "您的卡片新增成功，資料如下："
                text1 += "\n卡片名稱：" + card_name_msg
                message = TextSendMessage(  # 顯示訂房資料
                    text=text1
                )
                line_bot_api.reply_message(event.reply_token, message)
                # plt.show()
                # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=card_name_msg))
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="阿內卡目前沒提供這張信用卡服務哦~"))


def sendImgMap(event):  # 圖片地圖
    try:
        imagemap_message = ImagemapSendMessage(
            base_url='https://i.imgur.com/hzykiYu.png',
            alt_text='投資理財宣導',
            base_size=BaseSize(height=1040, width=1040),
            video=Video(
                original_content_url='https://i.imgur.com/8ECzu5B.mp4',
                preview_image_url='https://i.imgur.com/eNspzma.png',
                area=ImagemapArea(
                    x=0, y=0, width=1040, height=585
                ),
                external_link=ExternalLink(  # 影片結束後的連結
                    link_uri='https://www.fsc.gov.tw/ch/index.jsp',
                    label='查看更多…',
                ),
            ),
            actions=[
                URIImagemapAction(  # 超連結
                    link_uri='https://www.instagram.com/heyegg0219/',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=1040
                    )
                ),
                MessageImagemapAction(  # 文字訊息
                    text='戳錯地方囉~再戳一次~！',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=1040
                    )
                )
            ]
        )
        line_bot_api.reply_message(event.reply_token, imagemap_message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def sendConfirm(event):  # 確認樣板
    try:
        message = TemplateSendMessage(
            alt_text='理財小教室',
            template=ConfirmTemplate(
                text='提供各大網站搜尋,投資一定有風險,基金投資有賺有賠,申購前應詳閱公開說明書,實際活動優惠以各家銀行公布為主',
                actions=[
                    MessageTemplateAction(  # 按鈕選項
                        label='前往',
                        text='理財'
                    ),
                    MessageTemplateAction(
                        label='留在原地',
                        text='留在原地'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def vava_carousel(event):  # 轉盤樣板
    try:
        message = TemplateSendMessage(
            alt_text='理財',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://money.udn.com/static/img/moneyudn.jpg',
                        title='經濟日報',
                        text='將國內、全球、兩岸、財經、產業、觀點、股市、企管經營等資訊與分析，提供最新最精闢的新聞內容。',
                        actions=[
                            URIAction(
                                label='官網連結',
                                uri='https://money.udn.com/money/index?from=edn_header'
                            ),
                            URITemplateAction(
                                label='經濟日報理財網',
                                uri='https://money.udn.com/money/cate/5592?from=edn_navibar'
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=披薩'
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://www.cnyes.com/static/anue-og-image.png',
                        title='鉅亨網',
                        text='掌握全球經濟趨勢、股市即時訊息、國際政經、時事及匯率等相關財經新聞',
                        actions=[
                            URIAction(
                                label='官網連結',
                                uri='https://www.cnyes.com/'
                            ),
                            URITemplateAction(
                                label='鉅亨理財網',
                                uri='https://news.cnyes.com/news/cat/tw_money'
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=飲料'
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://cpx.cbc.gov.tw/Content/image/CBC_LOGO.png',
                        title='中央銀行',
                        text='提供政令宣導、金融教育宣導、金融統計數據',
                        actions=[
                            URIAction(
                                label='官網連結',
                                uri='https://www.cbc.gov.tw/tw/mp-1.html'
                            ),
                            URITemplateAction(
                                label='中央銀行匯率',
                                uri='https://www.cbc.gov.tw/tw/lp-645-1.html'
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=飲料'
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://webpro.twse.com.tw/WebPortal/resources/images/twse-fb-logo-600x315.png',
                        title='臺灣證劵交易所',
                        text='為臺灣證券集中交易市場的經營機構，由臺灣證券交易所股份有限公司持有,提供國內外證劵服務',
                        actions=[
                            URIAction(
                                label='官網連結',
                                uri='https://www.twse.com.tw/zh/'
                            ),
                            URITemplateAction(
                                label='臺灣投資指南',
                                uri='https://www.twse.com.tw/zh/page/focus/investing-guide.html'
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=飲料'
                            ),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/Cxb3gpX.png',
                        title='區塊客全球中文區塊鏈加密幣資訊網站',
                        text='於2017 年4 月正式成立，旨在廣泛整理全球區塊鏈資訊，增進全球中文閱聽眾及投資人對區塊鏈趨勢的了解。',
                        actions=[
                            URIAction(
                                label='官網連結',
                                uri='https://blockcast.it/'
                            ),
                            URITemplateAction(
                                label='應用介紹',
                                uri='https://blockcast.it/category/application/'
                            ),
                            PostbackTemplateAction(
                                label='↑↑↑↑',
                                data='action=sell&item=飲料'
                            ),
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))


def flexmessage(event):
    try:
        flex_message = FlexSendMessage(
            alt_text='呼叫阿內卡',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://i.imgur.com/EK5BAFj.png",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "label": "Action",
                        "uri": "https://linecorp.com/"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "image",
                                    "url": "https://i.imgur.com/EjfTyRX.jpg",
                                    "gravity": "bottom",
                                    "size": "sm",
                                    "aspectRatio": "4:3"
                                },
                                {
                                    "type": "image",
                                    "url": "https://i.imgur.com/HkJgtip.jpg",
                                    "margin": "md",
                                    "size": "sm",
                                    "aspectRatio": "4:3",
                                    "aspectMode": "cover"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "信用卡指南",
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#080808FF",
                                    "flex": 1,
                                    "align": "center",
                                    "gravity": "top",
                                    "action": {
                                        "type": "message",
                                        "text": "信用卡指南"
                                    },
                                    "contents": []
                                },
                                {
                                    "type": "separator"
                                },
                                {
                                    "type": "text",
                                    "text": "信用卡優惠",
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#0C0B0BFF",
                                    "flex": 2,
                                    "align": "center",
                                    "gravity": "center",
                                    "action": {
                                        "type": "message",
                                        "text": "信用卡優惠"
                                    },
                                    "contents": []
                                },
                                {
                                    "type": "separator"
                                },
                                {
                                    "type": "text",
                                    "text": "理財小教室",
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#070606FF",
                                    "flex": 2,
                                    "align": "center",
                                    "gravity": "center",
                                    "action": {
                                        "type": "message",
                                        "text": "理財小教室"
                                    },
                                    "contents": []
                                },
                                {
                                    "type": "separator"
                                },
                                {
                                    "type": "text",
                                    "text": "數位帳戶",
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#0E0D0DFF",
                                    "flex": 1,
                                    "align": "center",
                                    "gravity": "bottom",
                                    "action": {
                                        "type": "uri",
                                        "uri": "https://hackmd.io/@tTXrmXXUQtGZ_F0EsvAcxg/B1xk80nSj"
                                    },
                                    "contents": []
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "uri",
                                "label": "點我看使用說明",
                                "uri": "https://hackmd.io/@tTXrmXXUQtGZ_F0EsvAcxg/ry6IBO2Hs"
                            },
                            "color": "#2083E3FF"
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤'))


if __name__ == "__main__":
    app.run()
