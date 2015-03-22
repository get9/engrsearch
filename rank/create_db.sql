CREATE TABLE IF NOT EXISTS urls (
    hash TEXT PRIMARY KEY,
    url TEXT
);
CREATE TABLE IF NOT EXISTS linkgraph (
    url TEXT,
    outlink TEXT,
    FOREIGN KEY(url) REFERENCES urls(hash),
    FOREIGN KEY(outlink) REFERENCES urls(hash),
    UNIQUE(url, outlink)
);
