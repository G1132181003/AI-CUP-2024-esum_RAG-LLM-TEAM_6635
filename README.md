main.py

1. 讀取題目 json 檔案
2. 使用 data_preprocess.py 之函數，讀取資料集至參考資料字典
3. 使用 retrieval.py 之函數，回答問題。
4. 儲存答案

data_finance.json & data_insurance.json

預處理過的pdf資料，將main.py中的 FAST_LOADING 改為 True
來改為讀取同一目錄下的 data_finance.json & data_insurance.json
減少預處理時間。