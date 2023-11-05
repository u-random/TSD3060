PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Bruker (
    epostadresse TEXT PRIMARY KEY,
    passordhash TEXT NOT NULL,
    fornavn TEXT NOT NULL,
    etternavn TEXT NOT NULL
);
CREATE TABLE Sesjon (
    sesjonsID TEXT PRIMARY KEY,
    epostadresse TEXT,
    FOREIGN KEY(epostadresse) REFERENCES Bruker(epostadresse)
);
CREATE TABLE Dikt (
    diktID INTEGER PRIMARY KEY AUTOINCREMENT,
    dikt TEXT NOT NULL,
    epostadresse TEXT,
    FOREIGN KEY(epostadresse) REFERENCES Bruker(epostadresse)
);
DELETE FROM sqlite_sequence;
COMMIT;
