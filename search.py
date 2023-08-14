import sqlite3
import json

class DictionaryManager:
    def __init__(self, db_file):
        # 連接到 SQLite 資料庫
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # 存儲字詞資料的字典
        self.dict_word = {}

        # 儲存列名的列表
        self.DICT = []

        # 獲取 "sysdict" 表的列資訊，並將列名儲存到 self.DICT 列表中
        self.cursor.execute("PRAGMA table_info(sysdict)")
        headlines = self.cursor.fetchall()
        for headline in headlines:
            self.DICT.append(headline[1])

        # 將列名列表以 JSON 格式寫入檔案
        with open('detail.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(self.DICT, ensure_ascii=False) + '\n')

    def search_word(self):
        while True:
            match_found = False

            # 使用者輸入欲搜尋的字詞
            find_word = input('請輸入欲搜尋的字詞：')

            # 使用者選擇輸出格式
            choice = input('若想要輸出字典按 1，若想要輸出 JSON 檔案按 2：')

            try:
                # 在 "sysdict" 表中搜尋符合字詞的資料
                self.cursor.execute(f"SELECT * FROM sysdict WHERE word = '{find_word}'")
                rows = self.cursor.fetchall()

                if len(rows) > 1:
                    print(f"字詞 '{find_word}' 有多個相同的資料 : ")
                    for i, row in enumerate(rows, 1):
                        print(f"{i}. {row}")

                    # 用戶選擇索引
                    sense_choice = int(input("請輸入索引值:"))
                    row = rows[sense_choice - 1]
                elif len(rows) == 1:
                    row = rows[0]
                else:
                    print(f"字典中找不到字詞 '{find_word}'")
                    add_word = input("是否要增加字詞資料？需要輸入 YES，不需要輸入 NO: ")

                    if add_word == 'YES':
                        detail = []
                        for headline in self.DICT[1:]:
                            detail_input = input(f"請輸入 {headline}：")
                            detail.append(detail_input)

                        # 新增字詞資料到資料庫
                        self.cursor.execute(f"INSERT INTO sysdict VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                           tuple([find_word] + detail))
                        self.conn.commit()
                        print(f"已新增字詞 '{find_word}' 的資料")
                    continue

                # 整理資料到字典中
                data = tuple(row[0].split())
                datas = []
                for i in range(len(row[1:])):
                    if isinstance(row[i + 1], str):
                        se = row[i + 1].split()
                    else:
                        se = [row[i + 1]]
                    datas.append(se)
                self.dict_word[data] = datas

                # 根據選擇的格式輸出資料
                dict_find = {}
                detail = self.dict_word[data]
                dict_find[data[0]] = detail
                if choice == '1':
                    print(dict_find)
                elif choice == '2':
                    # 將搜尋到的字詞資料以 JSON 形式寫入檔案
                    with open('detail.json', 'a', encoding='utf-8') as f:
                        json.dump(dict_find, f, ensure_ascii=False)
                        f.write('\n')
                match_found = True

                # 用戶選擇是否刪除資料
                delete_word = input("是否要刪除字詞資料？需要輸入 YES，不需要輸入 NO: ")
                if delete_word == 'YES':
                    # 從資料庫中刪除搜尋到的字詞資料
                    self.cursor.execute(f"DELETE FROM sysdict WHERE word = '{find_word}'")
                    self.conn.commit()
                    print(f"已刪除字詞 '{find_word}' 的資料")

                # 用戶選擇是否繼續查詢
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

# 開始字詞搜尋和操作
manager.search_word()

# 關閉資料庫連接
manager.close()
