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

-- Adding an entry to the Bruker table
INSERT INTO Bruker (epostadresse, passordhash, fornavn, etternavn)
VALUES ('demo@demomail.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'D', 'Emo');

INSERT INTO Bruker (epostadresse, passordhash, fornavn, etternavn)
VALUES ('test@testmail.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'T', 'Est');

-- Adding an entry to the Sesjon table
INSERT INTO Sesjon (sesjonsID, epostadresse)
VALUES ('0', 'demo@demomail.com');

INSERT INTO Sesjon (sesjonsID, epostadresse)
VALUES ('1', 'test@testmail.com');

-- Adding entries to the Dikt table
INSERT INTO Dikt (dikt, epostadresse)
VALUES ('Skroenebok 1.', 'demo@demomail.com');
INSERT INTO Dikt (dikt, epostadresse)
VALUES ('Skroenebok 2. Vittighetenes tilbakekomst!', 'demo@demomail.com');
INSERT INTO Dikt (dikt, epostadresse)
VALUES ('Skroenebok 3. Atter en vits!', 'demo@demomail.com');
INSERT INTO Dikt (dikt, epostadresse)
VALUES ('Skroenebok 4. Den siste latter', 'test@testmail.com');

COMMIT;
