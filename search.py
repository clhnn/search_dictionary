import sqlite3
import json

class DictionaryManager:
    def __init__(self, db_file):
        # 連接到 SQLite 資料庫
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        self.dict_word = {}  # 儲存字詞相關的字典資料
        self.DICT_keys = []   # 儲存資料庫表的欄名

        # 取得資料庫表 'sysdict' 的欄名資訊
        self.cursor.execute("PRAGMA table_info(sysdict)")
        headlines = self.cursor.fetchall()
        for headline in headlines:
            self.DICT_keys.append(headline[1])

        # 將欄名以 JSON 格式寫入檔案
        with open('detail.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(self.DICT_keys, ensure_ascii=False) + '\n')

    def lookup(self, word):
        # 執行 SQL 查詢來查找符合指定單詞的字典項目
        self.cursor.execute(f"SELECT * FROM sysdict WHERE word = '{word}'")
        # 擷取所有的查詢結果
        rows = self.cursor.fetchall()

        # 建立一個字典來存儲查詢結果的所有字典項目
        dictElms = dict()
        dictElms['word'] = word
        records = []

        # 迭代每一個查詢結果的行
        for row in rows:
            # 確認字典的鍵的數量與行的長度相同
            assert len(self.DICT_keys) == len(row)
            record = dict()

            # 迭代字典的鍵和行中的值，並將它們匹配起來
            for (key, value) in zip(self.DICT_keys, row):
                # 忽略 'word' 鍵，因為它已經存在於 dictElms 中
                if key == 'word':
                    continue
                # 將鍵和值添加到記錄中
                record[key] = value

            # 添加記錄到字典項目的列表中
            records.append(record)

        # 將字典項目的單詞和記錄存儲為字典
        dictElms['entries'] = records
        # 將字典轉換為 JSON 字符串
        jlogs = json.dumps(dictElms, indent=4, ensure_ascii=False)
        # 輸出 JSON 字符串
        print(jlogs)
        # 返回 JSON 字符串
        return jlogs

    def search_word(self):
        while True:
            # 使用者輸入欲搜尋的字詞
            find_word = input('請輸入欲搜尋的字詞：')
            choice = input('若想要輸出字典按 1，若想要輸出 JSON 檔案按 2：')

            try:
                self.cursor.execute(f"SELECT * FROM sysdict WHERE word = '{find_word}'")
                rows = self.cursor.fetchall()

                if len(rows) > 1:
                    print(f"字詞 '{find_word}' 有多個相同的資料 : ")
                    for i, row in enumerate(rows, 1):
                        print(f"{i}. {row}")

                    sense_choice = int(input("請輸入索引值:"))
                    row = rows[sense_choice - 1]
                elif len(rows) == 1:
                    row = rows[0]
                else:
                    print(f"字典中找不到字詞 '{find_word}'")
                    add_word = input("是否要增加字詞資料？需要輸入 YES，不需要輸入 NO: ")

                    if add_word == 'YES':
                        detail = []
                        for headline in self.DICT_keys[1:]:
                            detail_input = input(f"請輸入 {headline}：")
                            detail.append(detail_input)

                        self.cursor.execute(f"INSERT INTO sysdict VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                           tuple([find_word] + detail))
                        self.conn.commit()
                        print(f"已新增字詞 '{find_word}' 的資料")
                    continue

                data = tuple(row[0].split())
                datas = []
                for i in range(len(row[1:])):
                    if isinstance(row[i + 1], str):
                        se = row[i + 1].split()
                    else:
                        se = [row[i + 1]]
                    datas.append(se)
                self.dict_word[data] = datas

                dict_find = {}
                detail = self.dict_word[data]
                dict_find[data[0]] = detail
                if choice == '1':
                    print(dict_find)
                elif choice == '2':
                    with open('detail.json', 'a', encoding='utf-8') as f:
                        json.dump(dict_find, f, ensure_ascii=False)
                        f.write('\n')

                delete_word = input("是否要刪除字詞資料？需要輸入 YES，不需要輸入 NO: ")
                if delete_word == 'YES':
                    self.cursor.execute(f"DELETE FROM sysdict WHERE word = '{find_word}'")
                    self.conn.commit()
                    print(f"已刪除字詞 '{find_word}' 的資料")

                diff = input('是否要繼續查詢？需要輸入 YES，不需要輸入 NO：')
                if diff == 'NO':
                    break

            except sqlite3.Error as e:
                print(f'資料庫錯誤：{e}')

    def close(self):
        # 關閉資料庫連接
        self.cursor.close()
        self.conn.close()

# 資料庫檔案的名稱
db_file = 'GoingZero.db'

# 創建 DictionaryManager 物件
manager = DictionaryManager(db_file)

# 查詢指定單字
manager.lookup("懶惰蟲")

# 開始字詞搜尋和操作
manager.search_word()

# 關閉資料庫連接
manager.close()
