# 推薦使用者手上最優惠卡前三
import mysql.connector
connection = mysql.connector.connect(host='host_IP', 
                                     database='database_name',
                                     user='user_name',
                                     password='user_password')
my_cursor = connection.cursor()

# 使用者選擇通路，撈取全資料庫的前三高優惠
def top_bank_list(chose_channel):
    my_cursor = connection.cursor()
    select_top_query = """SELECT CONCAT(n.發卡銀行, n.別名)
    FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
    WHERE r.通路名稱 = %s
    ORDER BY r.加總回饋 DESC
    LIMIT 3"""
    my_cursor.execute(select_top_query, (chose_channel, ))
    top_reward = my_cursor.fetchall()
    top_bank_name = [i[0] for i in top_reward]    
    return top_bank_name

# 推薦使用者手上最優惠卡前三名
def user_cards(card_list, chose_channel):    
    result_list = list()
    for each_card in card_list:
        # 下sql指令， %s 分別放入使用者丟進來的 card_list 和 chose_channel
        sql_select_query = """SELECT r.加總回饋, 
        CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
        CONCAT('評等：', n.信用卡評分, '顆星'), 
        CONCAT('最高回饋：', r.加總回饋, '%'), 
        IF(r.回饋上限說明, CONCAT('回饋上限說明：', r.回饋上限說明), ''), 
        IF(r.備註, CONCAT('備註：', r.備註), ''), 
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
        CONCAT('【阿內卡優惠推薦】\n銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
        CONCAT('評等：', n.信用卡評分, '顆星'), 
        CONCAT('最高回饋：', r.加總回饋, '%'), 
        IF(r.回饋上限說明, CONCAT('回饋上限說明：', r.回饋上限說明), ''), 
        IF(r.備註, CONCAT('備註：', r.備註), ''), 
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
        if i[0]>0:
            count_not_zero += 1
    
    # 使用者有三張以上的卡，且有三張以上優惠>0
    if len(card_rank)>=3 and count_not_zero>=3:
        return card_rank[0:3]
    # 使用者有兩張以上的卡，且有一張以上優惠>0
    elif len(card_rank)>=2 and 0<count_not_zero<=2:
        answer = card_rank[0:count_not_zero]
        answer += recommend_list[0:3-count_not_zero]
        return answer
    # 使用者只有一張卡，且優惠>0
    elif len(card_rank)>=1 and count_not_zero>=1:
        card_rank += recommend_list
        return card_rank        
    else:
        return recommend_list[0:3]

# 模擬使用者傳送進來的資料
print(user_cards(['華南銀行sny信用卡', '玉山銀行pi拍錢包信用卡', '中國信託allme卡'], "7-11"))



# 推薦全資料庫最優惠卡前三名
def cards_top_discount(card_list, chose_channel):
    # 先用 top_bank_name 函式找出 chose_channel 通路的前三高優惠之「卡名」
    top_bank_name = top_bank_list(chose_channel)
    recommend_list = list()
    # 檢查使用者卡片是否在top 3之一，如果有，就在最後一行顯示出：您已持有此卡！
    for i in top_bank_name:
        if i in card_list:
            select_query = """SELECT r.加總回饋, 
            CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
            CONCAT('評等：', n.信用卡評分, '顆星'), 
            CONCAT('最高回饋：', r.加總回饋, '%'), 
            IF(r.回饋上限說明, CONCAT('回饋上限說明：', r.回饋上限說明), ''), 
            IF(r.備註, CONCAT('備註：', r.備註), ''), 
            CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址, '。\n您已持有此卡！')
            FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
            WHERE r.通路名稱 = %s AND CONCAT(n.發卡銀行, n.別名) = %s"""
            my_cursor.execute(select_query, (chose_channel, i))
            recommend_list.append(my_cursor.fetchall()[0])
        else:
            select_query = """SELECT r.加總回饋, 
            CONCAT('銀行：', n.發卡銀行), CONCAT('卡名：', n.卡名), 
            CONCAT('評等：', n.信用卡評分, '顆星'), 
            CONCAT('最高回饋：', r.加總回饋, '%'), 
            IF(r.回饋上限說明, CONCAT('回饋上限說明：', r.回饋上限說明), ''), 
            IF(r.備註, CONCAT('備註：', r.備註), ''), 
            CONCAT('信用卡優惠詳情以官網公告為主：', n.信用卡網址)
            FROM CARD_NAME n JOIN CREDIT_CARD_REWARD r ON n.卡名 = r.卡名
            WHERE r.通路名稱 = %s AND CONCAT(n.發卡銀行, n.別名) = %s"""
            my_cursor.execute(select_query, (chose_channel, i))
            recommend_list.append(my_cursor.fetchall()[0])
    
    return recommend_list
    
# 模擬使用者丟進來的資料
print(cards_top_discount(['華南銀行sny信用卡', '玉山銀行pi拍錢包信用卡', '中國信託allme卡'], "7-11")) 
