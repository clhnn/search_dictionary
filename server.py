import sqlite3
import json
from flask import Flask, request, jsonify

# 初始化 Flask web 應用程式
app = Flask(__name__)

# 定義處理請求 favicon.ico 的路由
@app.route('/favicon.ico')
def favicon():
    return '', 404

# 定義處理 POST 請求的搜尋功能的路由
@app.route('/', methods=['POST'])
def search():
    # 連接到 SQLite 資料庫
    conn = sqlite3.connect('GoingZero.db')
    cursor = conn.cursor()

    # 初始化字典和串列來儲存資料
    dict_word = {}  # 儲存與特定單字相關的字典資料
    DICT_keys = []  # 儲存資料庫表的欄名

    # 使用 PRAGMA 取得資料庫表 'sysdict' 的欄名資訊
    cursor.execute("PRAGMA table_info(sysdict)")
    headlines = cursor.fetchall()

    # 提取欄名並將其儲存在 DICT_keys 串列中
    for headline in headlines:
        DICT_keys.append(headline[1])

    # 從請求中取得 JSON 資料
    data = request.json
    find_word = data['word']    # 要搜尋的單字
    choice = data['choice']     # 使用者的選擇

    try:
        # 執行查詢以檢索 'word' 符合請求單字的列
        cursor.execute(f"SELECT * FROM sysdict WHERE word = '{find_word}'")
        rows = cursor.fetchall()

        dictElms = dict()
        dictElms['word'] = find_word
        records = []
        for row in rows:
            assert len(DICT_keys) == len(row)
            record = dict()
            for (key, value) in zip(DICT_keys, row):
                if key == 'word':
                    continue
                record[key] = value

            records.append(record)

        dictElms['entries'] = records
        jlogs = json.dumps(dictElms, indent=4, ensure_ascii=False)
        
        # 根據使用者的選擇，將資料回傳為 JSON 或寫入 JSON 檔案
        if choice == '1':
            return jsonify(jlogs)
        elif choice == '2':
            with open('detail.json', 'a', encoding='utf-8') as f:
                f.write(jlogs)
            return jsonify({'message': 'JSON 檔案輸出成功'})

    finally:
        # 關閉資料庫連接和游標
        cursor.close()
        conn.close()

# 在執行腳本時啟動 Flask 應用程式
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)



