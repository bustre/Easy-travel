-- Trovare tutti i clienti riportando: Nome, Cognome e email, che hanno effettuato almeno una recensione con un voto
-- superiore o uguale a x stelle, e specificarne il nome dell'alloggio per cui è stata scritta la recensione, il giudizio 
-- dato e la motivazione se disponibile, nel caso tale informazione non fosse disponibile sostituire NULL con la stringa
-- '* Nessuna motivazione fornita'. Per l'esempio x = 3

SELECT D.NOME, D.COGNOME, A.NOME, R.GIUDIZIO,
       COALESCE(R.MOTIVAZIONE,'* Nessuna motivazione fornita')
  FROM DATI_CLIENTE AS D
  JOIN CLIENTE AS C
    ON D.EMAIL_CLIENTE = C.EMAIL
  JOIN RECENSIONE AS R
    ON C.EMAIL = R.EMAIL_CLIENTE
  JOIN ALLOGGIO AS A
    ON R.ID_CITTA_ALLOGGIO = A.ID_CITTA
   AND R.NOME_ALLOGGIO = A.NOME
 WHERE GIUDIZIO >= 3;
 
 
-- Per ciascuna compagnia aerea fornire: il nome della compagnia, il numero di prenotazioni, il numero totale di voli
-- che sono stati prenotati compagnia aerea, la media prezzi dei voli offerti, il prezzo massimo devi voli offerti
-- finora, e il prezzo minimo dei voli offerto finora. In fine si riordini in modo decrescente per numero voli.

SELECT C.NOME AS NOME_COMPAGNIA,
       COUNT(V.CODICE) AS NUMERO_VOLI,
       AVG(V.PREZZO) AS MEDIA_PREZZO_VOLO,
       MAX(V.PREZZO) AS PREZZO_MASSIMO,
       MIN(V.PREZZO) AS PREZZO_MINIMO
  FROM COMPAGNIA C
  JOIN VOLO AS V
    ON C.EMAIL = V.EMAIL_COMPAGNIA
 GROUP BY C.NOME
HAVING COUNT(V.CODICE) > 10
 ORDER BY NUMERO_VOLI DESC;
 
 
-- Riportare per ogni agenzia il numero di pacchetti offerti, in media quanto costano i loro pacchetti e la media delle
-- recensioni ricevute sugli alloggi offerti

SELECT AGENZIA.DENOMINAZIONE,
       NUMERO_OFFERTE.CONTEGGIO AS NUMERO_PACCHETTI,
       MEDIA_PREZZI.MEDIA AS PREZZO_MEDIO,
       MEDIA_REC.MEDIA as MEDIA_RECENSIONI
  FROM
        (SELECT EMAIL_AGENZIA AS EMAIL,
               COUNT(*) AS CONTEGGIO
          FROM PACCHETTO_VIAGGIO
         GROUP BY EMAIL_AGENZIA
       ) AS NUMERO_OFFERTE,
       
        (SELECT EMAIL_AGENZIA AS EMAIL,
               AVG(PACCHETTO_VIAGGIO.PREZZO) AS MEDIA
          FROM PACCHETTO_VIAGGIO
         GROUP BY EMAIL_AGENZIA
       ) AS MEDIA_PREZZI,

        (SELECT EMAIL_AGENZIA AS EMAIL,
               AVG(R.GIUDIZIO) AS MEDIA
          FROM RECENSIONE AS R
          JOIN PACCHETTO_VIAGGIO AS P
            ON P.ID_CITTA_ALLOGGIO = R.ID_CITTA_ALLOGGIO
           AND P.NOME_ALLOGGIO = R.NOME_ALLOGGIO
         GROUP BY P.EMAIL_AGENZIA
       ) AS MEDIA_REC,
       AGENZIA

 WHERE NUMERO_OFFERTE.EMAIL = MEDIA_PREZZI.EMAIL
   AND MEDIA_PREZZI.EMAIL = MEDIA_REC.EMAIL
   AND MEDIA_REC.EMAIL = AGENZIA.EMAIL;
   
   
-- Dato un cliente. Per ogni acquisto recuperare: tutte le informazioni della transizione, il totale per il trasporto,
-- il costo di base del pacchetto a persona, il numero di persone partecipanti e il numero di voli per quel viaggio.
-- Si includano inoltre gli utenti che non hanno prenotato il trasporto attraverso il servizio, e si riporti in quel
-- caso il valore 0 sia per il totale trasporto che per il numero di voli.
-- Cliente per l'esempio: Annibale.Boezio@fastmail.org.
 
SELECT DATI_PRENOTAZIONE.CODICE, 
       DATI_PRENOTAZIONE.NUMERO_PERSONE AS NUMERO_PARTECIPANTI, 
       DATI_PRENOTAZIONE.BANCA, 
       DATI_PRENOTAZIONE.IMPORTO, 
       DATI_PRENOTAZIONE.CIRCUITO, 
       DATI_PRENOTAZIONE.DATAORA, 
       DATI_PRENOTAZIONE.PREZZO AS PREZZO_PACCHETTO, 
       COALESCE(INFO_TRASPORTO.PREZZO_TOTALE, 
           0) AS TOTALE_TRASPORTO, 
       COALESCE(INFO_TRASPORTO.VOLI_TOTALI, 
           0) AS VOLI_PRESI 
  FROM 
        (SELECT I.CODICE_TRANSAZIONE AS CODICE,      
               I.PREZZO_TOTALE, 
               DATI_VOLI.VOLI_TOTALI 
          FROM 
                (SELECT ANDATA_RITORNO.CODICE_TRANSAZIONE,   
                       COUNT(*) AS VOLI_TOTALI 
                  FROM 
                        (SELECT * 
                          FROM ANDATA 
                     UNION ALL SELECT * 
                          FROM RITORNO
                       ) AS ANDATA_RITORNO 
                 GROUP BY ANDATA_RITORNO.CODICE_TRANSAZIONE
               ) AS DATI_VOLI, 
               INFORMAZIONI_TRASPORTO AS I 
         WHERE I.CODICE_TRANSAZIONE = DATI_VOLI.CODICE_TRANSAZIONE 
       ) AS INFO_TRASPORTO 

 RIGHT JOIN 
        (SELECT T.CODICE, 
               T.DATAORA, 
               T.IMPORTO, 
               T.CIRCUITO, 
               T.BANCA, 
               P.NUMERO_PERSONE, 
               PV.PREZZO 
          FROM PRENOTAZIONE AS P, 
               TRANSAZIONE AS T, 
               PACCHETTO_VIAGGIO AS PV 
         WHERE 'Annibale.Boezio@fastmail.org' = P.EMAIL_CLIENTE
           AND P.CODICE_TRANSAZIONE = T.CODICE
           AND PV.ID = P.ID_PACCHETTO_VIAGGIO
       ) AS DATI_PRENOTAZIONE
    ON INFO_TRASPORTO.CODICE = DATI_PRENOTAZIONE.CODICE;
    

-- Algoritmo per mostrare i pacchetti: fornita una data, cercare tutti i pacchetti viaggio che si svolgono dopo quella
-- data. Eliminare i pacchetti che non sono più disponibili (perché già prenotati tutti) dai risultati. Riportare le
-- seguenti informazioni essenziali: il titolo della descrizione del pacchetto, la data di partenza, la data di ritorno,
-- il prezzo, il numero di persone, il nome dell'alloggio e la destinazione.
-- Esempio con 11-04-2022. Ordinarli per data di partenza in ordine crescente.
 
SELECT D.TITOLO, 
       DISPONIBILI.PREZZO, 
       DISPONIBILI.NUMERO_PERSONE, 
       DISPONIBILI.DATA_PARTENZA, 
       DISPONIBILI.DATA_RITORNO, 
       DISPONIBILI.NOME_ALLOGGIO, 
       C.NOME, 
       C.STATO

  FROM 
        (SELECT P.ID, 
               P.PREZZO, 
               P.NUMERO_PERSONE, 
               P.DATA_PARTENZA, 
               P.DATA_RITORNO, 
               P.ID_DESCRIZIONE, 
               P.ID_CITTA_ALLOGGIO, 
               P.NOME_ALLOGGIO 
     
          FROM 
                (SELECT ID_PACCHETTO_VIAGGIO AS ID, 
                       COUNT(*) AS PRENOTAZIONI_TOTALI 
                  FROM PRENOTAZIONE 
                 GROUP BY ID_PACCHETTO_VIAGGIO
               ) AS CONTEGGIO_PRENOTAZIONI, 
               PACCHETTO_VIAGGIO AS P 
         WHERE P.ID = CONTEGGIO_PRENOTAZIONI.ID
           AND P.DISPONIBILITA > CONTEGGIO_PRENOTAZIONI.PRENOTAZIONI_TOTALI  
           AND P.DATA_PARTENZA > '11-04-2021'
       ) AS DISPONIBILI,
       
       DESCRIZIONE AS D,
       CITTA AS C
       
 WHERE D.ID = DISPONIBILI.ID_DESCRIZIONE
   AND C.ID = DISPONIBILI.ID_CITTA_ALLOGGIO
 ORDER BY DISPONIBILI.DATA_PARTENZA;
 

-- Si trovi tutti i voli da una aeroporto x ad un aeroporto y che attraverso gli scali costano meno del
-- viaggio diretto. Di ogni volo con scalo si riporti solo il codice del volo di partenza, la data/ora,
-- il codice del volo di arrivo, la data/ora di arrivo, il numero di scali, il prezzo contando tutti voli
-- dello scalo, il risparmio (differenza totale con scali e senza scali), il tempo totale di viaggio (
-- somma dei voli, senza contare le attese al terminale). Nota: il totale prezzo dei voli è per persona.
-- Nell'esempio: x.codice = 'EOCM' e y.codice = 'PQAS'

WITH RECURSIVE POSSIBILI_SCALI(
    PRIMO_VOLO, -- Tiene traccia della partenza
    VOLO_ATTUALE,
    AEROPORTO_PARTENZA,
    TIMESTAMP_PARTENZA,
    AEROPORTO_ARRIVO,
    TIMESTAMP_ARRIVO,
    NUMERO_SCALI,
    TOTALE_PREZZO,
    DURATA_TOTALE_VIAGGIO
) AS (
    (
        SELECT
            VOLO.CODICE AS PRIMO_VOLO,
            VOLO.CODICE AS VOLO_ATTUALE,
            AEROPORTO_PARTENZA,
            TIMESTAMP_PARTENZA,
            AEROPORTO_ARRIVO,
            TIMESTAMP_ARRIVO,
            0 AS NUMERO_SCALI,
            CAST(
                VOLO.PREZZO AS NUMERIC(
                    7,
                    2
                )
            ) AS TOTALE_PREZZO,
            (TIMESTAMP_ARRIVO - TIMESTAMP_PARTENZA) AS DURATA_TOTALE_VIAGGIO
        FROM
            VOLO
    )
    UNION
    ALL --Ricorsione
    (
        SELECT
            POSSIBILI_SCALI.PRIMO_VOLO,
            SUCCESSIVO.CODICE AS VOLO_ATTUALE,
            SUCCESSIVO.AEROPORTO_PARTENZA,
            SUCCESSIVO.TIMESTAMP_PARTENZA,
            SUCCESSIVO.AEROPORTO_ARRIVO,
            SUCCESSIVO.TIMESTAMP_ARRIVO,
            POSSIBILI_SCALI.NUMERO_SCALI + 1 AS NUMERO_SCALI,
            CAST(
                POSSIBILI_SCALI.TOTALE_PREZZO + SUCCESSIVO.PREZZO AS NUMERIC(
                    7,
                    2
                )
            ) AS TOTALE_PREZZO,
            (
                POSSIBILI_SCALI.DURATA_TOTALE_VIAGGIO + (
                    SUCCESSIVO.TIMESTAMP_ARRIVO - SUCCESSIVO.TIMESTAMP_PARTENZA
                )
            ) AS DURATA_TOTALE_VIAGGIO
        FROM
            VOLO AS SUCCESSIVO,
            POSSIBILI_SCALI
        WHERE
            SUCCESSIVO.AEROPORTO_PARTENZA = POSSIBILI_SCALI.AEROPORTO_ARRIVO
            AND SUCCESSIVO.TIMESTAMP_PARTENZA > POSSIBILI_SCALI.TIMESTAMP_ARRIVO
    )
) -- Nota: tra le tuple di possibili_scali ci sono anche i voli diretti
SELECT
    DIRETTO.PRIMO_VOLO AS DIRETTO_CODICE,
    DIRETTO.TIMESTAMP_PARTENZA AS DIRETTO_PARTENZA,
    DIRETTO.TIMESTAMP_ARRIVO AS DIRETTO_ARRIVO,
    DIRETTO.TOTALE_PREZZO AS DIRETTO_PREZZO,
    SCALI.PRIMO_VOLO AS SCALO_PARTENZA_CODICE,
    SCALI.VOLO_ATTUALE AS SCALO_ARRIVO_CODICE,
    V.TIMESTAMP_PARTENZA AS SCALO_PARTENZA,
    SCALI.TIMESTAMP_ARRIVO AS SCALO_ARRIVO,
    SCALI.NUMERO_SCALI,
    SCALI.TOTALE_PREZZO AS SCALO_PREZZO,
    SCALI.DURATA_TOTALE_VIAGGIO
FROM
    POSSIBILI_SCALI AS DIRETTO,
    POSSIBILI_SCALI AS SCALI,
    VOLO AS V -- V Serve a ottenere le informazioni del primo volo di partenza
WHERE
    DIRETTO.NUMERO_SCALI = 0
    AND DIRETTO.AEROPORTO_PARTENZA = 'EOCM'
    AND DIRETTO.AEROPORTO_ARRIVO = 'PQAS'
    AND DIRETTO.TOTALE_PREZZO > SCALI.TOTALE_PREZZO
    AND SCALI.NUMERO_SCALI > 0
    AND SCALI.AEROPORTO_ARRIVO = DIRETTO.AEROPORTO_ARRIVO
    AND SCALI.PRIMO_VOLO = V.CODICE;
