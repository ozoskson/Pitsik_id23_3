from time import time

from sqlalchemy.orm import Session

from schemas.fuzzy_search import RequestModel
from services.fuzzy_search.query_expansion import query_expansion_algorithm
from services.fuzzy_search.ngram import ngram_method


def run_fuzzy_search(request: RequestModel, db: Session):
    """
    Измеряет время выполнения алгоритма поиска и возвращает результаты.
    В зависимости от значения request.algorithm выбирается алгоритм:
      - "expansion" для алгоритма расширения выборки,
      - "ngram" для метода N-грамм.
    При указании неизвестного алгоритма возвращается False.
    """
    start = time()
    if request.algorithm == "expansion":
        result = query_expansion_algorithm(request.word, request.corpus_id, db)
    elif request.algorithm == "ngram":
        result = ngram_method(request.word, request.corpus_id, db)
    else:
        result = False
    end = time()
    return result, end - start