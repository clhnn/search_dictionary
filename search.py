import sqlite3
import json

conn = sqlite3.connect('GoingZero1.db')
cursor = conn.cursor()

dict_word = {}
DICT = []
cursor.execute("PRAGMA table_info(sysdict)")
headlines = cursor.fetchall()
for headline in headlines:
    DICT.append(headline[1])
with open('detail.json', 'a', encoding='utf-8') as f:
    f.write(json.dumps(DICT, ensure_ascii=False) + '\n')

while True:
    match_found = False
    find_word = input('請輸入欲搜尋的字詞：')
    choice = input('若想要輸出字典按 1，若想要輸出 JSON 檔案按 2：')

    try:
        cursor.execute(f"SELECT * FROM sysdict WHERE word = '{find_word}'")
        rows = cursor.fetchall()
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
                for headline in DICT[1:]:
                    detail_input = input(f"請輸入 {headline}：")
                    detail.append(detail_input)
                cursor.execute(f"INSERT INTO sysdict VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               tuple([find_word] + detail))
                conn.commit()
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
        dict_word[data] = datas

        dict_find = {}
        detail = dict_word[data]
        dict_find[data[0]] = detail
        if choice == '1':
            print(dict_find)
        elif choice == '2':            
            with open('detail.json', 'a', encoding='utf-8') as f:
                json.dump(dict_find, f, ensure_ascii=False)
                f.write('\n')
        match_found = True

        delete_word = input("是否要刪除字詞資料？需要輸入 YES，不需要輸入 NO: ")
        if delete_word == 'YES':
            cursor.execute(f"DELETE FROM sysdict WHERE word = '{find_word}'")
            conn.commit()
            print(f"已刪除字詞 '{find_word}' 的資料")

        diff = input('是否要繼續查詢？需要輸入 YES，不需要輸入 NO：')
        if diff == 'NO':
            break

    except sqlite3.Error as e:
        print(f'資料庫錯誤：{e}')

cursor.close()
conn.close()