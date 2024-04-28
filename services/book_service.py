from persistent.book_repository import BookRepository


class BookService:
    async def fetch_books(
        self,
        repository: BookRepository,
        author_ids: list[int] | None = [],
        search: str | None = None,
        limit: int | None = None
    ):
        result = await repository.fetch_books(
            author_ids=author_ids,
            search=search,
            limit=limit
        )
        return result