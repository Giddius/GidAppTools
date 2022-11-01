CREATE TABLE IF NOT EXISTS "Person" (
    "id" INTEGER PRIMARY KEY,
    "name" TEXT UNIQUE NOT NULL,
    "country" INTEGER NOT NULL REFERENCES "Country" ("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "Country" (
    "id" INTEGER PRIMARY KEY,
    "name" TEXT UNIQUE NOT NULL,
    "short_name" TEXT UNIQUE NOT NULL,
    "population_thousands" INTEGER NOT NULL
);

INSERT
    OR IGNORE INTO "Country" (
        "id",
        "name",
        "short_name",
        "population_thousands"
    )
VALUES
    (0, "Austria", "AUT", 8000),
    (1, "Germany", "GER", 80000),
    (2, "Great Britain", "GB", 67000);

INSERT
    OR IGNORE INTO "Person" ("name", "country")
VALUES
    ("Tom", 2),
    ("Fritz", 1),
    ("Wolfgang", 0),
    ("Peter", 0);