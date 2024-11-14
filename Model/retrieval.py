
from sentence_transformers import SentenceTransformer, util
import torch
import voyageai

# VOYAGE API KEY，數天後將被手動銷毀。
API_KEY_VOYAGE = "pa-4YVXyz_kKtxD4INpBOXFb64HTWho8ThrSBuOGpCnvGo"

NAME_EMBEDDING = "TencentBAC/Conan-embedding-v1"
NAME_RE_RANKER = 'rerank-2'

device = 'cpu'
if torch.cuda.is_available():
    device = 'cuda:0'
elif torch.backends.mps.is_available():
    device = 'mps'

voyage = voyageai.Client(API_KEY_VOYAGE)
conan_encoder = SentenceTransformer(NAME_EMBEDDING, device=device)

def embedding_select(query: str, sentences: list[str], top_k: int = 50) -> list[int]:
    '''
    使用conan embedding進行語意搜尋，
    傳回最優的k個chuck的idx
    '''
    passage_embeddings = conan_encoder.encode(
        sentences,
        batch_size=2,
        device=device
        #show_progress_bar=True
    )

    question_embedding = conan_encoder.encode(
        query,
        batch_size=1,
        device=device
    )

    hits = util.semantic_search(
        question_embedding,
        passage_embeddings,
        top_k=top_k
    )[0]

    return [int(good_elem['corpus_id']) for good_elem in hits]

def rerank_select(query: str, sentences: list[str], easy_search_dict: dict[str,int], top_k: int = 1) -> list[int]:
    '''
    使用voyage rerank重排sentences中的chuck
    傳回重排後的sentences的chuck的idx
    '''
    reranking = voyage.rerank(query, sentences, model=NAME_RE_RANKER, top_k=top_k)

    result = []

    for r in reranking.results:
        result.append(easy_search_dict[r.document])
        continue

    return result

def find_anwser(query: str, source: list[int], data: dict[int, list[str]]) -> int:
    '''
    Keyword args:
    query -- 題目
    source -- 可能符合的選項，含編號的list[int]
    data -- 處理過的資料集，key值為編號，value值為該資料的chuck清單。

    上半部分將source各編號對應的chuck合併成一個list:
        1. 將每個資料的所有chuck，全部合併在一個list: sentences
        2. 計算sentences_range，確定sentences的那些範圍屬於哪個檔案
    下半部分，將該list傳給模型並取得結果:
        1. conan embedding模型，透過語意篩選答案
        2. voyage rerank模型，將篩選之結果進行重排
        3. 找回最優chuck隸屬的編號
        4. 傳回答案
    
    '''
    sentences = []
    sentences_range = [0]

    for source_id in source:
        sentences += data[source_id]

        range_idx = len(data[source_id]) + sentences_range[-1]
        sentences_range.append(range_idx)
    sentences_range.pop(0)

    semantic_result = embedding_select(query, sentences)

    sentences_for_rerank = [sentences[idx] for idx in semantic_result]
    fast_search_dict = {sentences[idx] : idx for idx in semantic_result}
    anwser_sentences_idx = rerank_select(query, sentences_for_rerank, fast_search_dict)[0]

    for idx, range_idx in enumerate(sentences_range):
        if anwser_sentences_idx < range_idx:
            anwser = source[idx]
            break

    return anwser
