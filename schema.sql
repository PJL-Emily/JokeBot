CREATE TABLE tasks (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    title TEXT NOT NULL,
    deadline DATE NOT NULL,
    isFinished BINARY DEFAULT 0,
    detail TEXT
);

CREATE TABLE choices (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL,
    usr_text TEXT NOT NULL,
    sys_reply TEXT NOT NULL
);

CREATE TABLE current_state (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    state ENUM("general", "task", "deadline", "joke") DEFAULT "general",
    step INT DEFAULT 0
);

CREATE TABLE jokes (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    content TEXT NOT NULL
);