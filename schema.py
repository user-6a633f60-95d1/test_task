from contextlib import asynccontextmanager
from functools import partial
from databases import Database

import strawberry
from strawberry.types import Info
from fastapi import FastAPI
from strawberry.fastapi import BaseContext, GraphQLRouter

from settings import Settings
from services.book_service import BookService
from persistent.book_repository import BookRepository


class Context(BaseContext):
    db: Database

    def __init__(
        self,
        db: Database,
    ) -> None:
        self.db = db


@strawberry.type
class Author:
    name: str


@strawberry.type
class Book:
    title: str
    author: Author


@strawberry.type
class Query:

    @strawberry.field
    async def books(
        self,
        info: Info[Context, None],
        author_ids: list[int] | None = [],
        search: str | None = None,
        limit: int | None = None,
    ) -> list[Book]:
        repository = BookRepository(db=info.context.db)
        result = await BookService().fetch_books(
            repository=repository,
            author_ids=author_ids,
            search=search,
            limit=limit
        )
        return [
                Book(title=book['title'], author=Author(name=book['name']))
            for book in result
            ]


CONN_TEMPLATE = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
settings = Settings()  # type: ignore
db = Database(
    CONN_TEMPLATE.format(
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        port=settings.DB_PORT,
        host=settings.DB_SERVER,
        name=settings.DB_NAME,
    ),
)

@asynccontextmanager
async def lifespan(
    app: FastAPI,
    db: Database,
):
    async with db:
        yield
    await db.disconnect()

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(  # type: ignore
    schema,
    context_getter=partial(Context, db),
)

app = FastAPI(lifespan=partial(lifespan, db=db))
app.include_router(graphql_app, prefix="/graphql")
