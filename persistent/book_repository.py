class BookRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def fetch_books(
        self,
        author_ids: list[int] | None = [],
        search: str | None = None,
        limit: int | None = None
    ):
        sql_query_string = self.build_sql(
            author_ids=author_ids,
            search=search,
            limit=limit
        )

        result = await self.db.fetch_all(sql_query_string)
        return result

    def build_sql(
        self,
        author_ids: list[int] | None = [],
        search: str | None = None,
        limit: int | None = None
    ):
        query_base = """
            SELECT books.id, books.title, authors.id, authors.name
            FROM books
            JOIN authors ON books.author_id = authors.id
        """
        query_conditions = []
        if author_ids:
            ids = ', '.join(map(str, author_ids))
            query_conditions.append(f"author_id IN ({ids})")
        
        if search:
            query_conditions.append(f"title LIKE '%{search}%'")

        if query_conditions:
            query_conditions_str = " AND ".join(query_conditions)
            query_base += f" WHERE {query_conditions_str}"

        if limit:
            query_base += f" LIMIT {limit}"

        return query_base