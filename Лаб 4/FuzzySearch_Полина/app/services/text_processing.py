import re
from typing import Any, Generator

from sqlalchemy.orm import Session

from models.corpus import Corpus
from models.word import Word


def split_text(text: str) -> Generator[str, Any, None]:
    """
    Разбивает текст на слова, удаляя знаки препинания.
    Возвращает генератор, который выдаёт слова в нижнем регистре.
    """
    pattern = re.compile(r'\b\w+\b', re.UNICODE)
    return (match.group().lower() for match in pattern.finditer(text))


def add_corpus(db: Session, request: Corpus):
    new_corpus = Corpus(corpus_name=request.corpus_name)
    db.add(new_corpus)
    db.commit()
    db.refresh(new_corpus)
    return new_corpus


def add_words(db: Session, corpus_id: int, text: str):
    words = split_text(text)
    # Можно добавить фильтрацию для удаления пустых строк или нежелательных символов
    for word in words:
        if word:  # если слово не пустое
            new_word = Word(corpus_id=corpus_id, word=word)
            db.add(new_word)
            # db.refresh(new_word)
    db.commit()
