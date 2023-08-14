# **Introduction**
此示範程式皆為Python

# DictionaryManager
這是一個簡單的字典管理器程式，使用 SQLite 資料庫儲存字詞資料，並提供搜尋、新增和刪除字詞的功能。它還可以將字詞資料輸出為字典或 JSON 檔案。

`注意!在執行程式前請確保已安裝所需的Python庫:'sqlite3'和'json'`

## 資料庫準備
將您的 SQLite 資料庫檔案複製到程式的根目錄，並確保檔案名稱與程式碼中指定的名稱相符（預設為 `GoingZero.db`）。資料庫需要具有 "sysdict" 表，以便程式可以正確地執行。

###### 初始化方法
"初始化方法":當我們創建 `DictionaryManager` 物件時會被調用。在這個方法中，以下操作被執行：
- 連接到 SQLite 資料庫：使用 `sqlite3.connect()` 方法連接到指定的 SQLite 資料庫檔案。
- 取得列名：使用 `PRAGMA table_info(sysdict)` 查詢 "sysdict" 資料表的列資訊。每個列的資訊都包含在一個 tuple 中，其中包括列名等。
- 將列名存入 `self.DICT`：從列資訊中提取出的列名被添加到 `self.DICT` 列表中。
- 將列名以 JSON 格式寫入檔案：使用 `open()` 函數開啟名為 `detail.json` 的檔案，然後將 `self.DICT` 列表以 JSON 格式寫入檔案中。
```js
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
```

###### search_word方法
"search_word方法":這是主要的搜尋和操作方法，用戶可以透過這個方法來查詢字詞及執行其他操作。該方法包括以下步驟：
- 使用者輸入欲搜尋的字詞 (`find_word`)。
- 使用者選擇輸出資料的格式 (`choice`)，可以是字典或 JSON。
- 使用 SQL 查詢搜尋該字詞的資料，然後根據結果執行不同的處理：
  - 如果找到多筆相同的資料，列出這些資料供用戶選擇。
  - 如果找到一筆資料，直接取得該筆資料。
  - 如果找不到資料，提示用戶是否要新增資料。
- 將查詢結果以字典格式存入 `self.dict_word` 中。
- 根據用戶的選擇，將資料以字典或 JSON 格式輸出到屏幕或檔案。
- 如果用戶想要刪除字詞資料，根據用戶的輸入刪除資料。
- 詢問用戶是否繼續查詢，如果不需要則結束循環。
```js
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
```

###### close方法
"close方法":這個方法用於關閉資料庫連接和游標，以確保資源被正確釋放。
```js
def close(self):
        # 關閉資料庫連接
        self.cursor.close()
        self.conn.close()
```
###### 主程式
- 創建一個 `DictionaryManager` 物件，並指定使用的 SQLite 資料庫檔案為 `'GoingZero.db'`。
- 調用 `search_word` 方法，開始使用者的字詞搜尋和操作。
- 調用 `close` 方法來關閉資料庫連接，確保程式執行完畢後資源被正確釋放。
```js
#主程式部分
# 資料庫檔案的名稱
db_file = 'GoingZero.db'

# 創建 DictionaryManager 物件
manager = DictionaryManager(db_file)

# 開始字詞搜尋和操作
manager.search_word()

# 關閉資料庫連接
manager.close()
```
通過調用相應的方法或去處理結果，並將結果整合成一個字典或將結果以JSON格式寫入名為'detail.json'的文件中

`注意!請確保在執行程式前，將'GoingZero.db'更改為您將使用的database檔名`

# Install
Python適用
```js
pip install sqlite3
```
這個模組提供了對 SQLite 資料庫的存取功能。SQLite 是一個輕量級的嵌入式資料庫，適合用於儲存小型資料集。
```js
pip install json
```
這個模組允許我們讀取和寫入 JSON 格式的資料，該格式常用於儲存和交換結構化的資料。
