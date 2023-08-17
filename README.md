# **Introduction**
此示範程式皆為Python

# **search.py**
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

# **server.py**
這是一個基於Flask的簡單Web應用程式，用於查詢存儲在SQLite資料庫中的字典資料。使用者可以提交一個包含要查詢的字詞和輸出選項的POST請求，然後應用程式會回傳符合查詢的字典資料。

`注意!在執行程式前請確保已安裝所需的Python庫:'sqlite3'、'json'、'requests'和''flask`

## 資料庫準備
將您的 SQLite 資料庫檔案複製到程式的根目錄，並確保檔案名稱與程式碼中指定的名稱相符（預設為 `GoingZero.db`）。資料庫需要具有 "sysdict" 表，以便程式可以正確地執行。

###### 初始化Flask web 應用程式
初始化 Flask Web 應用程序是為了創建一個可用於處理 Web 請求和響應的應用程序實例。在初始化過程中，您可以進行各種配置和設置，以確保應用程序在運行時具備所需的功能和行為。
```js
app = Flask(__name__)
```
###### 定義處理請求 favicon.ico 的路由
這段代碼定義了一個路由 /favicon.ico，用於處理請求 favicon.ico 的情況。在這裡，我們簡單地返回一個空響應和 404 狀態碼，表示找不到該文件。

```js
@app.route('/favicon.ico')
def favicon():
    return '', 404
```
###### 定義處理 POST 請求的搜尋功能的路由
"search方法":用於處理根路徑 / 的 POST 請求。該方法包括以下步驟：
- 連接到 SQLite 數據庫，並創建游標對象 cursor。
- 從請求中獲取數據並進行處理：
  - 從 POST 請求的 JSON 數據中獲取要搜索的單詞和用戶的選擇。
  - 執行 SQL 查詢以檢索與請求單詞匹配的行。
  - 將結果轉換為字典和列表的形式。
- 根據用戶的選擇返回結果：
  - 如果選擇為 1，將結果作為 JSON 數據返回給客戶端。
  - 如果選擇為 2，將結果寫入名為 detail.json 的 JSON 文件中，並返回一個表示寫入成功的 JSON 響應。
- 最後關閉數據庫連接和游標：
  - 在 finally 中關閉數據庫連接和游標。

```js
  # 定義處理 POST 請求的搜尋功能的路由
@app.route('/', methods=['POST'])
def search():
    # 連接到 SQLite 資料庫
    conn = sqlite3.connect('GoingZero1.db')
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
```
###### 啟動 Flask 應用程序
- 在腳本執行時，通過調用 app.run() 啟動 Flask 應用程序。
- 指定主機為 0.0.0.0，表示可以從任何 IP 地址訪問應用程序。
- 指定端口號為 5050。
```js
# 在執行腳本時啟動 Flask 應用程式
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
```


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
