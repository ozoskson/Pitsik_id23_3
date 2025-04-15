from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from db.database import db_init
from models.corpus import Corpus

from schemas.auth import SignUpRequest, UserResponse
from cruds.user_crud import is_user_exists, create_new_user, get_user_access
from schemas.corpus import NewCorpus, CorpusesResponse
from schemas.fuzzy_search import RequestModel
from services.auth import create_jwt_token, get_current_user
from db.get_db import get_db
from services.fuzzy_search.run_search import run_fuzzy_search
from services.text_processing import add_corpus, add_words

db_init()
app = FastAPI(
    title="Нечёткий поиск",
    description="API приложения для алгоритмов Нечёткого поиска",
    debug=True,
)

@app.post("/sign-up/",
          tags=["Аккаунты"],
          summary="Регистрация пользователя")
def register_user(request: SignUpRequest, resp: Response, db: Session = Depends(get_db)):
    """
    Проверяет, не зарегистрирован ли уже пользователь с таким email. Если нет, создает нового пользователя и генерирует
    для него токен. Возвращает данные созданного пользователя.

    Пример запроса:
    {"email": "user@example.com",
    "password": "securepassword123"}

    Пример ответа:
    {"id": 1,
    "email": "user@example.com",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    """
    if is_user_exists(db, request.email):
        return HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")
    new_user = create_new_user(db, request)
    token = create_jwt_token(data={"user_id": new_user.user_id})
    resp.set_cookie(key="access_token", value=token, httponly=True)
    return {"id": new_user.user_id, "email": new_user.email, "token": token}


@app.post("/login/",
          tags=['Аккаунты'],
          summary="Вход в аккаунт")
def login(request: SignUpRequest, resp: Response, db: Session = Depends(get_db)):
    """
    Проверяет существование пользователя с указанным email. Проверяет правильность введенного пароля. Если все верно, генерирует новый токен для пользователя. Возвращает данные пользователя с новым токеном.

    Пример запроса:
    {"email": "user@example.com",
    "password": "securepassword123"}
    Пример ответа:
    {"id": 1,
        "email": "user@example.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    """
    user = get_user_access(db, request)
    if not bool(user):
        return HTTPException(status_code=401, detail="Неправильные данные для входа")
    token = create_jwt_token(data={"user_id": user.user_id})
    resp.set_cookie(key="access_token", value=token, httponly=True)

    return {
        "id": user.user_id,
        "email": user.email,
        "token": token
    }


@app.get(
    "/users/me/",
    response_model=UserResponse,
    tags=["Аккаунты"],
    summary="Получить информацию о текущем пользователе"
)
def read_current_user(current_user=Depends(get_current_user)):
    return current_user


@app.post("/upload_corpus",
          tags=["Corpuses"],
          summary="Загружает корпус текста для индексации и поиска")
def upload_corpus(request: NewCorpus, db: Session = Depends(get_db)):
    corpus = add_corpus(db, request)
    add_words(db, corpus.corpus_id, request.text)
    return {
        "corpus_id": corpus.corpus_id,
        "message": "Corpus uploaded successfully"
    }


@app.get("/corpuses",
         tags=["Corpuses"],
         summary="Получить список корпусов текста",
         response_model=CorpusesResponse)
def get_corpuses(db: Session = Depends(get_db)):
    corpuses = db.query(Corpus).all()
    return {"corpuses": corpuses}


@app.post("/search_algorithm",
          tags=['Fuzzy search'],
          summary="Алгоритмы 'Расширение выборки' и 'Метод N-грамм' для нечёткого поиска")
def search_algorithm(request: RequestModel, db: Session = Depends(get_db)):
    results, elapsed = run_fuzzy_search(request, db)
    if results is False:
        raise HTTPException(status_code=401, detail="Указанный алгоритм не подключён к приложению")
    return {
        "execution_time": elapsed,
        "results": results
    }