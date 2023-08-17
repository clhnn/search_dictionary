import requests
import json

def test_url(url, data=None):
    headers = {'Content-Type': 'application/json'}

    try:
        # 嘗試發送 POST 請求至指定的 URL
        response = requests.post(url, data=json.dumps(data), headers=headers)
        
        # 如果收到 200 OK 的回應
        if response.status_code == 200:
            print("URL 可存取。")
            print("回應內容：")
            
            # 解碼回應內容，處理中文編碼
            response.encoding = 'utf-8'
            decoded_content = response.text.encode().decode('unicode_escape')
            print(decoded_content)
            
        else:
            # 若回應狀態碼不是 200，顯示回應狀態碼
            print(f"URL 不可存取。狀態碼：{response.status_code}")
    except requests.exceptions.RequestException as e:
        # 若發生連線錯誤，顯示錯誤訊息
        print(f"URL 不可存取。錯誤訊息：{str(e)}")

# 要測試的 URL
url_to_test = "http://127.0.0.1:5050"
# 要傳送的資料
data_to_send = {"word": "懶惰蟲","choice":"1"}
# 測試指定的 URL 和資料
test_url(url_to_test, data=data_to_send)



