from sqlalchemy.orm import Session

from models.word import Word


def ngram_method(query: str, corpus_id: int, db: Session, n: int = 3):
    """
    Метод N-грамм:
    Для каждого слова из корпуса вычисляется коэффициент Жаккара для N-грамм между запросом и словом.
    При этом, если длина строки меньше n, используется вся строка как единый n-грамм.
    "Расстояние" определяется как 1 - коэффициент Жаккара.
    Результаты сортируются по возрастанию расстояния.
    """
    results = []
    candidate_entries = db.query(Word).filter(Word.corpus_id == corpus_id).all()
    # Определяем эффективное n для запроса: не больше длины запроса
    effective_n = min(n, len(query)) if query else n
    query_ngrams = {query[i:i+effective_n] for i in range(len(query)-effective_n+1)} if len(query) >= effective_n else {query}
    for entry in candidate_entries:
        candidate_word = entry.word
        effective_n_candidate = min(effective_n, len(candidate_word)) if candidate_word else effective_n
        candidate_ngrams = {candidate_word[i:i+effective_n_candidate] for i in range(len(candidate_word)-effective_n_candidate+1)} if len(candidate_word) >= effective_n_candidate else {candidate_word}
        union = query_ngrams.union(candidate_ngrams)
        intersection = query_ngrams.intersection(candidate_ngrams)
        jaccard_similarity = len(intersection) / len(union) if union else 0
        distance = 1 - jaccard_similarity
        results.append({"word": candidate_word, "distance": distance})
    results.sort(key=lambda x: x["distance"])
    return results