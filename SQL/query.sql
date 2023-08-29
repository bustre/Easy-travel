-- Trovare tutti i clienti riportando: Nome, Cognome e email, che hanno effettuato almeno una recensione con il voto
-- superiore a 3 stelle, e specificarne il nome dell'alloggio per cui è stata scritta la recensione, il giudizio dato e
-- la motivazione se disponibile

SELECT DATI_CLIENTE.NOME,
       DATI_CLIENTE.COGNOME,
       NOME_ALLOGGIO,
       R.GIUDIZIO,
       R.MOTIVAZIONE
  FROM DATI_CLIENTE
  JOIN CLIENTE AS C
    ON DATI_CLIENTE.EMAIL = C.EMAIL
  JOIN RECENSIONE AS R
    ON C.EMAIL = R.EMAIL_CLIENTE
  JOIN ALLOGGIO AS A
    ON R.ID_CITTA_ALLOGGIO = A.ID_CITTA
   AND R.NOME_ALLOGGIO = A.NOME
 WHERE GIUDIZIO > 3;
 
-- Per ciascuna compagnia aerea fornire: il nome della compagnia, il numero di prenotazioni, il numero totale di voli
-- che sono stati prenotati compagnia aerea, la media prezzi dei voli offerti, il prezzo massimo devi voli offerti
-- finora, e il prezzo minimo dei voli offerto finora,

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
 ORDER BY NUMEROVOLI DESC;
 
-- Dato un cliente. Per ogni acquisto recuperare: tutte le informazioni della transizione, il totale per il trasporto, 
-- il costo di base del pacchetto a persona, il numero di persone partecipanti e il numero di voli per quel viaggio.
-- Cliente per l'esempio: Renzo.Camanni@email.com

SELECT P.NUMEROPERSONE AS NUMERO_PARTECIPANTI,
       T.CODICE,
       T.BANCA,
       T.IMPORTO,
       T.CIRCUITO,
       T.DATAORA,
       I.PREZZO_TOTALE AS TOTALE_TRASPORTO,
       PV.PREZZO AS PREZZO_PACCHETTO,
       DATI_VOLI.VOLI_TOTALI AS VOLI_PRESI
  FROM
        (SELECT ANDATA_RITORNO.CODICE_TRANSAZIONE,
               COUNT(*) AS VOLI_TOTALI
          FROM
                (SELECT *
                  FROM ANDATA
                 UNION SELECT *
                  FROM RITORNO
               ) AS ANDATA_RITORNO

         GROUP BY ANDATA_RITORNO.CODICE_TRANSAZIONE
       ) AS DATI_VOLI,

       PRENOTAZIONE AS P,
       TRANSAZIONE AS T,
       INFORMAZIONI_TRASPORTO AS I,
       PACCHETTO_VIAGGIO AS PV

 WHERE 'Renzo.Camanni@email.com' = P.EMAIL_CLIENTE
   AND P.CODICE_TRANSAZIONE = T.CODICE
   AND T.CODICE = I.CODICE_TRANSAZIONE
   AND I.CODICE_TRANSAZIONE = DATI_VOLI.CODICE_TRANSAZIONE
   AND PV.ID = P.ID_PACCHETTO_VIAGGIO;

 
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
   

-- Algoritmo di ricerca per i pacchetti: fornita una data, cercare tutti i pacchetti viaggio che si svolgono dopo quella
-- data. Eliminare i pacchetti che non sono più disponibili (perché già prenotati tutti) dai risultati. Riportare le
-- seguenti informazioni esenziali: il titolo della descrizione del pacchetto, la data di partenza, la data di ritorno,
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
