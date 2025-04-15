from sqlalchemy.orm import Session

from models.word import Word


def query_expansion_algorithm(query: str, corpus_id: int, db: Session):
    """
    Алгоритм расширения выборки:
    Извлекает все слова из корпуса. Если слово содержит запрос (без учёта регистра),
    "расстояние" определяется как разница длин между словом и запросом;
    если нет – к этой разнице добавляется штраф (например, +5).
    Результаты сортируются по возрастанию расстояния.
    """
    results = []
    candidate_entries = db.query(Word).filter(Word.corpus_id == corpus_id).all()
    for entry in candidate_entries:
        candidate_word = entry.word
        if query.lower() in candidate_word.lower():
            distance = abs(len(candidate_word) - len(query))
        else:
            distance = abs(len(candidate_word) - len(query)) + 5  # штраф за отсутствие вхождения
        results.append({"word": candidate_word, "distance": distance})
    results.sort(key=lambda x: x["distance"])
    return results