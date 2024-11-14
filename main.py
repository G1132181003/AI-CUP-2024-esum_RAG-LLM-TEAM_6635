import os
import json
import argparse
import tqdm
import Model.retrieval as retrieval
import Preprocess.data_preprocess as data_preprocess

FAST_LOADING = False

if __name__ == "__main__":
    # 使用argparse解析命令列參數
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--question_path', type=str, required=True, help='讀取發布題目路徑')  # 問題文件的路徑
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料路徑')  # 參考資料的路徑
    parser.add_argument('--output_path', type=str, required=True, help='輸出符合參賽格式的答案路徑')  # 答案輸出的路徑

    args = parser.parse_args()  # 解析參數

    answer_dict = {"answers": []}  # 初始化字典

    with open(args.question_path, 'rb') as f:
        qs_list = json.load(f)['questions']  # 讀取問題檔案

    # 初始化資料集字典
    reference_data = {}
    reference_data['faq'] = {}
    reference_data['finance'] = {}
    reference_data['insurance'] = {}

    # 讀取資料集至字典
    if FAST_LOADING:
        with open("data_finance.json", 'rb') as f:
            d1 = json.load(f)
            for idx in d1.keys():
                reference_data['finance'][int(idx)] = d1[idx]

        with open("data_insurance.json", 'rb') as f:
            d1 = json.load(f)
            for idx in d1.keys():
                reference_data['insurance'][int(idx)] = d1[idx]
    else:
        print(f'Loading finance pdf files:')
        reference_data['finance'] = data_preprocess.load_pdf_data(args.source_path, 'finance')

        print(f'Loading insurance pdf files:')
        reference_data['insurance'] = data_preprocess.load_pdf_data(args.source_path, 'insurance')

    print(f'Loading FAQ DATA:')
    reference_data['faq'] = data_preprocess.load_faq_data(args.source_path)

    #跑檢索
    print("Anwsering:")
    for q in tqdm.tqdm(qs_list):
        
        qid = q["qid"]
        query = q["query"]
        source = q["source"]
        category = q['category']

        if not category in ['finance', 'insurance', 'faq']:
            raise ValueError("Category not in ['finance', 'insurance', 'faq']")

        retrieved = retrieval.find_anwser(query, source, reference_data[category])
        answer_dict['answers'].append({"qid": qid, "retrieve": retrieved})

    #儲存檔案
    with open(args.output_path, 'w', encoding='utf8') as f:
        json.dump(answer_dict, f, ensure_ascii=False, indent=4)  # 儲存檔案，確保格式和非ASCII字符
        
    print("Done!")