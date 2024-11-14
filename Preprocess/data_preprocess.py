
import re
import pdfplumber  # 用於從PDF文件中提取文字的工具
import tqdm
import json
import glob

def read_pdf(pdf_loc, page_infos: list = None) -> str:
    '''
    來自玉山baseline範例程式
    將pdf文件中的純文字取下
    傳回pdf純文字
    '''

    pdf = pdfplumber.open(pdf_loc)  # 打開指定的PDF文件

    # TODO: 可自行用其他方法讀入資料，或是對pdf中多模態資料（表格,圖片等）進行處理

    # 如果指定了頁面範圍，則只提取該範圍的頁面，否則提取所有頁面
    pages = pdf.pages[ [0]:page_infos[1]] if page_infos else pdf.pages
    pdf_text = ''
    for _, page in enumerate(pages):  # 迴圈遍歷每一頁
        text = page.extract_text()  # 提取頁面的文本內容
        if text:
            pdf_text += text
    pdf.close()  # 關閉PDF文件

    return pdf_text  # 返回萃取出的文本

def pdf_text_to_part(pdf_text: str) -> list[str]:
    '''
    透過re library，使用正規表達式，將pdf_text以句號 "。" 與冒號 "：" 分割成list[str]
    由於分割後，可能有空字串，因此使用filter過濾掉空字串
    傳回過濾後的清單
    '''
    x = re.split('[。：]', pdf_text.replace("\n",""))
    x = list(filter(lambda y: y, x))
    return x

def load_faq_data(reference_dir):
    '''
    讀取FAQ資料集，並套上對話框架，也許一問一答能契合題目之問句。
    '''
    result = {}

    with open(reference_dir + '\\faq\\pid_map_content.json', 'rb') as f:
        loaded_faq_data = json.load(f)  # 讀取問題檔案

        for idx,val in loaded_faq_data.items():

            _ = []
            for faq in val:
                _.append("小明問道: " + faq['question'] + '\n神奇海螺答道: ' + '\n'.join(faq['answers']))

            result[int(idx)] = _

    return result
    

def load_pdf_data(reference_dir: str, category: str) -> dict[int, list[str]]:
    '''
    讀取pdf資料集，使用baseline之read_pdf讀取純文字，
    再使用pdf_text_to_part，將純文字做chucking，切成小塊的區塊。
    並將各個pdf編號與其對應的chuck，存入字典並傳回。
    '''

    result = {}

    for pdf_path in tqdm.tqdm(glob.glob(reference_dir + '\\' + category + '\\*.pdf')):
        pdf_content = read_pdf(pdf_path)

        pdf_id = int(pdf_path.split('\\')[-1].removesuffix('.pdf'))

        parts = pdf_text_to_part(pdf_content)
        result[pdf_id] = parts

    return result