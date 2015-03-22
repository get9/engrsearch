CREATE TABLE IF NOT EXISTS urls (
    hash INTEGER PRIMARY KEY,
    url TEXT
);
CREATE TABLE IF NOT EXISTS linkgraph (
    url INTEGER,
    outlink INTEGER,
    FOREIGN KEY(url) REFERENCES urls(hash),
    FOREIGN KEY(outlink) REFERENCES urls(hash),
    UNIQUE
);
