DROP TABLE IF EXISTS Cliente CASCADE;

DROP TABLE IF EXISTS Dati_Cliente CASCADE;

DROP TABLE IF EXISTS Compagnia CASCADE;

DROP TABLE IF EXISTS Informazioni_Bagagli CASCADE;

DROP TABLE IF EXISTS Polizza CASCADE;

DROP TABLE IF EXISTS Descrizione CASCADE;

DROP TABLE IF EXISTS Città CASCADE;

DROP TABLE IF EXISTS Alloggio CASCADE;

DROP TABLE IF EXISTS Agenzia CASCADE;

DROP TABLE IF EXISTS Aeroporto CASCADE;

DROP TABLE IF EXISTS Transazione CASCADE;

DROP TABLE IF EXISTS Volo CASCADE;

DROP TABLE IF EXISTS Pacchetto_Viaggio CASCADE;

DROP TABLE IF EXISTS Prenotazione CASCADE;

DROP TABLE IF EXISTS Informazione_Trasporto CASCADE;

DROP TABLE IF EXISTS Ritorno CASCADE;

DROP TABLE IF EXISTS Andata CASCADE;

DROP TABLE IF EXISTS Recensione CASCADE;

DROP TYPE IF EXISTS genere;

CREATE TYPE genere AS ENUM(
    'M',
    'F'
);

CREATE TABLE Dati_Cliente(   
    Email varchar(40) PRIMARY KEY,
    Nome varchar(20) NOT NULL,
    Cognome varchar(20) NOT NULL,
    Data_Nascita date NOT NULL,
    Sesso genere,
    telefono varchar(20)
);

CREATE TABLE Cliente(
    Email varchar(40) PRIMARY KEY,
    PASSWORD varchar(24) NOT NULL,
    Data_Iscrizione timestamp NOT NULL,
    CHECK (
        LENGTH(PASSWORD) BETWEEN 8 AND 24
    ),
    FOREIGN KEY(email) REFERENCES Dati_Cliente(email) ON
    DELETE
        CASCADE ON
        UPDATE
            CASCADE
);

CREATE TABLE Compagnia(
    Email varchar(40) PRIMARY KEY,
    PASSWORD varchar(24) NOT NULL,
    Data_Iscrizione timestamp NOT NULL,
    Nome varchar(40) NOT NULL,
    ICAO char(4) NOT NULL,
    CHECK (
        LENGTH(PASSWORD) BETWEEN 8 AND 24
    )
);

CREATE TABLE Informazioni_Bagagli (
    ID INTEGER PRIMARY KEY,
    Bagaglio_Mano NUMERIC(
        2,
        0
    ),
    Bagaglio_Stiva NUMERIC(
        2,
        0
    ),
    CHECK (
        Bagaglio_Mano >= 0
            AND Bagaglio_Stiva >= 0
    )
);

CREATE TABLE Polizza(
    ID INTEGER PRIMARY KEY,
    Descrizione varchar(400) NOT NULL,
    Titolo varchar(20) NOT NULL
);

CREATE TABLE Descrizione(
    ID INTEGER PRIMARY KEY,
    Titolo varchar(20) NOT NULL,
    Testo varchar(400) NOT NULL
);

CREATE TABLE Città(
    ID INTEGER PRIMARY KEY,
    Nome varchar(25) NOT NULL,
    Stato varchar(25) NOT NULL
);

CREATE TABLE Alloggio(
    ID_Città integer,
    Nome varchar(25),
    Stelle integer,
    Tipologia varchar(10) NOT NULL,
    ID_Descrizione integer NOT NULL,
    Indirizzo varchar(40) NOT NULL,
    PRIMARY KEY(
        ID_Città,
        Nome
    ),
    FOREIGN KEY(ID_Città) REFERENCES Città(ID) ON
    DELETE
        NO ACTION ON
        UPDATE
            CASCADE,
            FOREIGN KEY(ID_Descrizione) REFERENCES Descrizione(ID) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE,
                    CHECK (
                        Stelle >= 1
                            AND Stelle <= 5
                    )
);

CREATE TABLE Agenzia(
    Email varchar(40) PRIMARY KEY,
    PASSWORD varchar(24) NOT NULL,
    DATA_Iscrizione timestamp NOT NULL,
    Denominazione varchar(40) NOT NULL,
    ID_Città integer NOT NULL,
    Indirizzo varchar(40) NOT NULL,
    CHECK (
        LENGTH(PASSWORD) BETWEEN 8 AND 24
    ),
    FOREIGN KEY(ID_Città) REFERENCES Città(ID) ON
    DELETE
        NO ACTION ON
        UPDATE
            CASCADE
);

CREATE TABLE Aeroporto(
    Codice varchar(4) PRIMARY KEY,
    ID_Città integer NOT NULL,
    FOREIGN KEY(ID_Città) REFERENCES Città(ID) ON
    DELETE
        NO ACTION ON
        UPDATE
            CASCADE
);

CREATE TABLE Transazione(
    Codice varchar(16) PRIMARY KEY,
    Banca varchar(20) NOT NULL,
    Importo NUMERIC(
        5,
        2
    ) NOT NULL,
    Circuito varchar(10) NOT NULL,
    Timestamp timestamp NOT NULL,
    CHECK (
        Importo >= 0
        AND LENGTH(Codice) = 16
    )
);

CREATE TABLE Volo(
    Codice INTEGER PRIMARY KEY,
    Classe varchar(10) NOT NULL,
    CHECK_In varchar(10) NOT NULL,
    Prezzo NUMERIC(
        5,
        2
    ) NOT NULL,
    email_Compagnia varchar(40) NOT NULL,
    Aeroporto_Partenza varchar(4) NOT NULL,
    Timestamp_Partenza timestamp NOT NULL,
    Aeroporto_Arrivo varchar(4) NOT NULL,
    Timestamp_Arrivo timestamp NOT NULL,
    ID_Bagagli integer NOT NULL,
    FOREIGN KEY(email_Compagnia) REFERENCES Compagnia(email) ON
    DELETE
        CASCADE ON
        UPDATE
            CASCADE,
            FOREIGN KEY(Aeroporto_Partenza) REFERENCES Aeroporto(Codice) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE,
                    FOREIGN KEY(Aeroporto_Arrivo) REFERENCES Aeroporto(Codice) ON
                    DELETE
                        NO ACTION ON
                        UPDATE
                            CASCADE,
                            FOREIGN KEY(ID_Bagagli) REFERENCES Informazioni_Bagagli(ID) ON
                            DELETE
                                NO ACTION ON
                                UPDATE
                                    CASCADE,
                                    CHECK (
                                        Prezzo >= 0 AND Timestamp_Partenza < Timestamp_Arrivo
                                    )
);

CREATE TABLE Pacchetto_Viaggio(
    ID integer PRIMARY key,
    Prezzo NUMERIC(
        5,
        2
    ) NOT NULL,
    Numero_Persone integer NOT NULL,
    Disponibilità integer NOT NULL,
    Data_Ritorno date NOT NULL,
    Data_Partenza date NOT NULL,
    email_Agenzia varchar(40) NOT NULL,
    ID_Polizza integer NOT NULL,
    ID_Descrizione integer NOT NULL,
    ID_Città_Alloggio integer NOT NULL,
    Nome_Alloggio varchar(25) NOT NULL,
    FOREIGN KEY(email_Agenzia) REFERENCES Agenzia(email) ON
    DELETE
        NO ACTION ON
        UPDATE
            CASCADE,
            FOREIGN KEY(ID_Polizza) REFERENCES Polizza(ID) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE,
                    FOREIGN KEY(ID_Descrizione) REFERENCES Descrizione(ID) ON
                    DELETE
                        NO ACTION ON
                        UPDATE
                            CASCADE,
                            FOREIGN KEY(
                                ID_Città_Alloggio,
                                Nome_Alloggio
                            ) REFERENCES Alloggio(
                                ID_Città,
                                nome
                            ) ON
                            DELETE
                                NO ACTION ON
                                UPDATE
                                    CASCADE,
                                    CHECK (
                                        Disponibilità >= 1
                                            AND Numero_Persone >= 1
                                    )
);

CREATE TABLE Prenotazione(
    Codice_Transazione varchar(16) PRIMARY KEY,
    NumeroPersone NUMERIC(
        2,
        0
    ) NOT NULL,
    ID_Pacchetto_Viaggio integer NOT NULL,
    check( length(Codice_Transazione) = 16),
    FOREIGN KEY(Codice_Transazione) REFERENCES Transazione(Codice) ON
    DELETE
        NO action ON
        UPDATE
            CASCADE,
            FOREIGN KEY(ID_Pacchetto_Viaggio) REFERENCES Pacchetto_Viaggio(ID) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE,
                    CHECK (
                        NumeroPersone >= 1
                    )
);

CREATE TABLE Informazione_Trasporto(
    Codice_Transazione varchar(16) PRIMARY key,
    Prezzo_Totale NUMERIC(
        5,
        2
    ) NOT NULL,
    FOREIGN KEY(
        Codice_Transazione
    ) REFERENCES Prenotazione(
        Codice_Transazione
    ) ON
    DELETE
        NO action ON
        UPDATE
            CASCADE,
            CHECK (
                Prezzo_Totale >= 0 AND length(Codice_Transazione) = 16
            )
);

CREATE TABLE Ritorno(
    Codice_Transazione varchar(16),
    Codice_Volo integer,
    PRIMARY KEY(
        Codice_Transazione,
        Codice_Volo
    ),
    check( length(Codice_Transazione) = 16),
    FOREIGN KEY(
        Codice_Transazione
    ) REFERENCES Informazione_Trasporto(
        Codice_Transazione
    ) ON
    DELETE
        NO action ON
        UPDATE
            CASCADE,
            FOREIGN KEY(Codice_Volo) REFERENCES Volo(Codice) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE
);

CREATE TABLE Andata(
    Codice_Transazione varchar(16),
    Codice_Volo integer,
    PRIMARY KEY(
        Codice_Transazione,
        Codice_Volo
    ),check( length(Codice_Transazione) = 16),
    FOREIGN KEY(
        Codice_Transazione
    ) REFERENCES Informazione_Trasporto(
        Codice_Transazione
    ) ON
    DELETE
        NO action ON
        UPDATE
            CASCADE,
            FOREIGN KEY(Codice_Volo) REFERENCES Volo(Codice) ON
            DELETE
                NO ACTION ON
                UPDATE
                    CASCADE
);

CREATE TABLE Recensione(
    ID integer,
    Giudizio NUMERIC(
        1,
        0
    ) NOT NULL,
    Motivazione varchar(200),
    email_Cliente varchar(40) NOT NULL,
    ID_Città integer NOT NULL,
    Nome_Alloggio varchar(25) NOT NULL,
    PRIMARY KEY(ID),
    FOREIGN KEY(email_Cliente) REFERENCES Cliente(email) ON
    DELETE
        CASCADE ON
        UPDATE
            CASCADE,
            FOREIGN KEY(
                ID_Città,
                Nome_Alloggio
            ) REFERENCES Alloggio(
                ID_Città,
                Nome
            ) ON
            DELETE
                CASCADE ON
                UPDATE
                    CASCADE,
                    CHECK (
                        Giudizio >= 0
                            AND Giudizio <= 5
                    )
);
