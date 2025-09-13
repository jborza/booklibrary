# booklibrary-spring

Spring Boot (Java) port of the Flask booklibrary app (domain subset).

## Quick start (PostgreSQL)
1. Ensure PostgreSQL database and user:
```
CREATE DATABASE booklibrary;
CREATE USER booklibrary WITH PASSWORD 'booklibrary';
GRANT ALL PRIVILEGES ON DATABASE booklibrary TO booklibrary;
```
2. From repository root:
```
cd booklibrary-spring
../gradlew bootRun   # or ./gradlew bootRun if wrapper copied
```
3. Test:
```
curl http://localhost:8080/ping/
```
Should return:
```
{"status":"ok"}
```

## H2 Dev Profile
```
./gradlew bootRun --args='--spring.profiles.active=dev'
```

## Sample Book Creation
Insert an author first (psql):
```
INSERT INTO authors(name, surname, surname_first) VALUES ('Isaac', 'Asimov', 'Asimov, Isaac');
```
Create a book:
```
curl -X POST http://localhost:8080/books/api \
  -H "Content-Type: application/json" \
  -d '{"title":"The Foundation","authorId":1,"status":"to read","tags":"sci-fi"}'
```

Search:
```
curl 'http://localhost:8080/books/api/search?q=foundation'
```

## Future Work
- Implement real cover downloader
- Provider-based recommendations
- Pagination + sorting parameters
- OpenAPI / Swagger docs
- Additional fields (genres, language, year)
