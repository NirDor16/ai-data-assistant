CREATE DATABASE IF NOT EXISTS ai_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ai_user'@'localhost'
IDENTIFIED BY 'Nirdor2002';

ALTER USER 'ai_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'Nirdor2002';

GRANT ALL PRIVILEGES ON ai_project.* TO 'ai_user'@'localhost';

FLUSH PRIVILEGES;
