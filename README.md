# Book library API

Set up database:
MariaDB, user booklibrary, password booklibrary

``` sql
DROP USER IF EXISTS booklibrary;
CREATE USER booklibrary IDENTIFIED BY 'booklibrary';
CREATE DATABASE booklibrary CHARACTER SET utf8mb4 COLLATE UTF8MB4_UNICODE_CI;
GRANT ALL PRIVILEGES ON booklibrary.* TO 'booklibrary';
```