#include "dependencies/include/libpq-fe.h"
#include <array>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

class Database;
class QueryResult;

std::ostream&
operator<<(std::ostream& os, const QueryResult& q_result);

// Semplice C++ wrapping del codice di libpq
class QueryResult
{
public:
  explicit QueryResult(PGconn* conn, PGresult* result);

  std::vector<std::string> fields(void) const;
  std::vector<std::vector<std::string>> tuples(void) const;

  friend std::ostream& operator<<(std::ostream& os,
                                  const QueryResult& q_result);

private:
  PGconn* conn;
  PGresult* result;
  int n_tuple;
  int n_fields;

  void check_tuples(void) const;
};

// FIXME: sistemare
std::ostream&
operator<<(std::ostream& os, const QueryResult& q_result)
{
  // Lunghezza massima
  std::vector<int> col_widths(q_result.n_fields, 0);

  for (int i = 0; i < q_result.n_fields; ++i) {
    col_widths[i] = std::string(PQfname(q_result.result, i)).length();

    for (int j = 0; j < q_result.n_tuple; ++j) {
      int width = std::string(PQgetvalue(q_result.result, j, i)).length();
      if (width > col_widths[i]) {
        col_widths[i] = width;
      }
    }
  }

  // Inizio tabella
  for (int i = 0; i < q_result.n_fields; ++i) {
    os << "+";
    for (int w = 0; w < col_widths[i] + 2; ++w) {
      os << "-";
    }
  }
  os << "+" << std::endl;

  for (int i = 0; i < q_result.n_fields; ++i) {
    os << "| " << std::left << std::setw(col_widths[i])
       << PQfname(q_result.result, i) << " ";
  }
  os << "|" << std::endl;

  for (int i = 0; i < q_result.n_fields; ++i) {
    os << "+";
    for (int w = 0; w < col_widths[i] + 2; ++w) {
      os << "-";
    }
  }
  os << "+" << std::endl;

  // Corpo tabella
  for (int i = 0; i < q_result.n_tuple; ++i) {
    for (int j = 0; j < q_result.n_fields; ++j) {
      os << "| " << std::left << std::setw(col_widths[j])
         << PQgetvalue(q_result.result, i, j) << " ";
    }
    os << "|" << std::endl;
  }

  for (int i = 0; i < q_result.n_fields; ++i) {
    os << "+";
    for (int w = 0; w < col_widths[i] + 2; ++w) {
      os << "-";
    }
  }
  os << "+" << std::endl;

  return os;
}

QueryResult::QueryResult(PGconn* _conn, PGresult* _result)
  : conn{ _conn }
  , result{ _result }
{
  check_tuples();

  n_tuple = PQntuples(result);
  n_fields = PQnfields(result);
}

std::vector<std::string>
QueryResult::fields(void) const
{
  std::vector<std::string> headers;

  for (int i = 0; i < n_fields; ++i)
    headers.push_back(std::string(PQfname(result, i)));

  return headers;
}

std::vector<std::vector<std::string>>
QueryResult::tuples(void) const
{
  std::vector<std::vector<std::string>> tuples;

  for (int t = 0; t < n_tuple; ++t) {
    std::vector<std::string> row;

    for (int f = 0; f < n_fields; f++)
      row.push_back(PQgetvalue(result, t, f));

    tuples.push_back(row);
  }

  return tuples;
}

void
QueryResult::check_tuples(void) const
{
  if (PQresultStatus(result) == PGRES_TUPLES_OK)
    return;

  PQclear(result);
  throw std::runtime_error(PQerrorMessage(conn));
}

class Database
{
public:
  Database(const std::string& host,
           unsigned port,
           const std::string& user,
           const std::string& db_name,
           const std::string& password);

  ~Database(void);

  void connect(const std::string& host,
               unsigned port,
               const std::string& user,
               const std::string& db_name,
               const std::string& password);

  void close(void);

  ConnStatusType status(void) const;
  bool is_good(void) const;
  std::string get_error_msg(void);

  QueryResult exec_query(const std::string& sql);
  QueryResult exec_query(const std::string& name,
                         const std::vector<std::string>& parms);

  void prepared_query(const std::string& name,
                      const std::string& sql,
                      int n_parm);

private:
  PGconn* connection;
};

Database::Database(const std::string& host,
                   unsigned port,
                   const std::string& user,
                   const std::string& db_name,
                   const std::string& password)
  : connection{ nullptr }
{
  connect(host, port, user, db_name, password);
}

Database::~Database(void)
{
  close();
}

void
Database::connect(const std::string& host,
                  unsigned port,
                  const std::string& user,
                  const std::string& db_name,
                  const std::string& password)
{
  std::string connect_info =
    "host=\'" + host + "\' port=\'" + std::to_string(port) + "\' user=\'" +
    user + "\' dbname=\'" + db_name + "\' password=\'" + password + "\'";

  if (connection != nullptr)
    PQfinish(connection);

  connection = PQconnectdb(connect_info.c_str());
}

void
Database::close(void)
{
  if (connection != nullptr)
    PQfinish(connection);

  connection = nullptr;
}

ConnStatusType
Database::status(void) const
{
  return PQstatus(connection);
}

bool
Database::is_good(void) const
{
  return status() == CONNECTION_OK;
}

std::string
Database::get_error_msg(void)
{
  return std::string(PQerrorMessage(connection));
}

QueryResult
Database::exec_query(const std::string& sql)
{
  return QueryResult(connection, PQexec(connection, sql.c_str()));
}

QueryResult
Database::exec_query(const std::string& name,
                     const std::vector<std::string>& parms)
{
  const char* parm_values[parms.size()];

  for (std::size_t index = 0; index < parms.size(); ++index)
    parm_values[index] = parms[index].c_str();

  PGresult* result = PQexecPrepared(
    connection, name.c_str(), parms.size(), parm_values, NULL, NULL, 0);

  if (result == nullptr || PQresultStatus(result) != PGRES_TUPLES_OK) {
    throw std::runtime_error(PQerrorMessage(connection));
  }

  return QueryResult(connection, result);
}

void
Database::prepared_query(const std::string& name,
                         const std::string& sql,
                         int n_parm)
{
  PGresult* rs = PQprepare(connection, name.c_str(), sql.c_str(), n_parm, NULL);

  if (rs == nullptr || PQresultStatus(rs) != PGRES_COMMAND_OK)
    throw std::runtime_error(PQerrorMessage(connection));
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////

// FIXME: permettere al prof di inserire la password
Database
init_app(void)
{
  std::cout << "Connessione al database...\n";

  Database db = Database(
    "192.168.0.104", 5432, "postgres", "Easy Travel", "ALu1ym9~fmhv@x~N");

  if (db.is_good()) {
    std::cout << "Connessione avvenuta con successo\n";
    return db;
  }

  std::cout
    << "\nC'e' stato un errore nel tentativo di connettermi al database\n";
  std::cout << "Dettagli errore:\n" << db.get_error_msg() << "\n\n";

  exit(1);
}

// Console
bool
console_input_is_good(void)
{
  bool failed = std::cin.fail();

  if (failed) {
    std::cout << "\nERRORE: Formato non valido\n";
    std::cin.clear();
    std::cin.ignore();
    return false;
  }

  return true;
}

template<typename _Tp>
_Tp
console_input(const std::string& msg)
{
  _Tp result;

  while (true) {
    std::cout << msg;
    std::cin >> result;

    if (!console_input_is_good())
      continue;

    return result;
  }
}

// Query

void
run_query_1(Database& db)
{
  std::cout << "\n\n\n\t<Query 1 - Descrizione>\n";
  std::cout <<
    R"(
Trovare tutti i clienti riportando: Nome, Cognome e email, che hanno effettuato almeno una recensione con un voto
superiore o uguale a x stelle, e specificarne il nome dell'alloggio per cui è stata scritta la recensione, il giudizio 
dato e la motivazione se disponibile, nel caso tale informazione non fosse disponibile sostituire NULL con la stringa
'* Nessuna motivazione fornita'.
)";

  int n_stelle = console_input<int>(
    "\nInserire quante stelle devono avere le recesioni della "
    "query (0 o un numero negativo per non filtrarle): ");

  std::cout << "\n\n"; // Padding
  try {
    std::cout << db.exec_query("Query 1", { std::to_string(n_stelle) });
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}

void
run_query_2(Database& db)
{
  std::cout << "\n\n\n\t<Query 2 - Descrizione>\n";
  std::cout <<
    R"(
Per ciascuna compagnia aerea fornire: il nome della compagnia, il numero di prenotazioni, il numero totale di voli
che sono stati prenotati compagnia aerea, la media prezzi dei voli offerti, il prezzo massimo devi voli offerti
finora, e il prezzo minimo dei voli offerto finora. Filtrare la ricerca in modo da mostrare solo le compagnia con
almeno x voli. In fine si riordini in modo decrescente per numero voli.
)";

  int n_voli = console_input<int>("\nInserire il valore di x: ");

  std::cout << "\n\n"; // Padding
  try {
    std::cout << db.exec_query("Query 2", { std::to_string(n_voli) });
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}

void
run_query_3(Database& db)
{
  std::cout << "\n\n\n\t<Query 3 - Descrizione>\n\n";
  std::cout <<
    R"(
Riportare per ogni agenzia il numero di pacchetti offerti, in media quanto costano i loro pacchetti e la media delle
recensioni ricevute sugli alloggi offerti.
)";

  try {
    std::cout << db.exec_query("Query 3", {});
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}

void
run_query_4(Database& db)
{
  std::cout << "\n\n\n\t<Query 4 - Descrizione>\n";
  std::cout <<
    R"(
Dato un cliente. Per ogni acquisto recuperare: tutte le informazioni della transizione, il totale per il trasporto,
il costo di base del pacchetto a persona, il numero di persone partecipanti e il numero di voli per quel viaggio.
Si includano inoltre anche i casi in cui non hanno prenotato il trasporto attraverso il servizio, e si riporti in quel
caso il valore 0 sia per il totale trasporto che per il numero di voli.

)";

  try {
    std::cout << db.exec_query(
      "SELECT C.EMAIL, D.NOME, D.COGNOME FROM CLIENTE AS C JOIN DATI_CLIENTE "
      "AS D ON C.EMAIL = D.EMAIL_CLIENTE;");
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
    return;
  }

  std::string client_email = console_input<std::string>(
    "\n\nInserire l'email del cliente di cui si vuole visualizzare lo storico "
    "delle transazioni: ");

  try {
    std::cout << db.exec_query("Query 4", { client_email });
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}

void
run_query_5(Database& db)
{
  std::cout << "\n\n\n\t<Query 5 - Descrizione>\n";
  std::cout <<
    R"(
Algoritmo per mostrare i pacchetti: fornita una data, cercare tutti i pacchetti viaggio che si svolgono dopo quella
data. Eliminare i pacchetti che non sono più disponibili (perché già prenotati tutti) dai risultati. Riportare le
seguenti informazioni essenziali: il titolo della descrizione del pacchetto, la data di partenza, la data di ritorno,
il prezzo, il numero di persone, il nome dell'alloggio e la destinazione. In fine si filtri i risultati lasciando
tutti i pacchetti compresi dal prezzo in un intevervallo di prezzo. Ordinarli per data di partenza in ordine crescente.
Filtrare poi in base a un intrevallo di prezzo dei pacchetti viaggio fornito.


)";

  double min = console_input<double>("Prezzo minimo: ");
  double max = console_input<double>("Prezzo massimo: ");
  std::string filter_date =
    console_input<std::string>("A partire da (yy-mm-gg): ");

  try {
    std::cout << db.exec_query(
      "Query 5", { filter_date, std::to_string(min), std::to_string(max)});
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}

void
run_query_6(Database& db)
{
  std::cout << "\n\n\n\t<Query 6 - Descrizione>\n";
  std::cout <<
    R"(
Si trovi tutti i voli da una aeroporto x ad un aeroporto y che attraverso gli scali costano meno del
viaggio diretto. Di ogni volo con scalo si riporti solo il codice del volo di partenza, la data/ora,
il codice del volo di arrivo, la data/ora di arrivo, il numero di scali, il prezzo contando tutti voli
dello scalo, il risparmio (differenza totale con scali e senza scali), il tempo totale di viaggio (
somma dei voli, senza contare le attese al terminale). Nota: il totale prezzo dei voli è per persona. Le
colonne sono state rinominate in modo differente rispetto alla relazione per motivi di spazio.

)";

  try {
    std::cout << db.exec_query(
      "SELECT A.CODICE AS AEROPORTO_CODICE, C.NOME AS UBICAZIONE, C.STATO FROM AEROPORTO AS A JOIN CITTA AS C ON C.ID = A.ID_CITTA;");
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
    return;
  }

  std::string departure = console_input<std::string>("Inserire il codice dell'aerporto di partenza: ");
  std::string destination = console_input<std::string>("Inserire il codice dell'aerporto di arrivo: ");

  try {
    std::cout << db.exec_query(
      "Query 6", { departure, destination});
  } catch (const std::runtime_error& err) {
    std::cout
      << "ERRORE: c'e' stato un errore nel tenativo di eseguire la query :(\n"
      << "\t dettagli: " << err.what();
  }
}


// App
void
main_menu(Database& db)
{
  bool exit = false;

  do {
    // Padding
    std::cout << "\n\n";
    std::cout << "Menu:\n";
    std::cout
      << "\t> Query 1: cerca tutti i clienti che hanno scritto delle "
         "recensioni;\n"
      << "\t> Query 2: recuperare informazioni statistiche sull'andamento "
         "delle compagnie di volo registrate;\n"
      << "\t> Query 3: summary delle varie offerte di viaggio fornite dalle "
         "agenzie registrate;\n"
      << "\t> Query 4: recuperare storico degli acquisti di un cliente;\n"
      << "\t> Query 5: esegui algoritmo di ricerca parametrizzabile;\n"
      << "\t> Query 6: cerca un volo piu' conveniente rispetto a quello "
         "diretto;\n"
      << "\t[!] Per chiudere l'applicazione inserire il valore -1.\n";

    int select = console_input<int>(
      "\nInserire il numero della query che si desidera eseguire: ");

    switch (select) {
      case -1:
        exit = true;
        break;

      case 1:
        run_query_1(db);
        break;

      case 2:
        run_query_2(db);
        break;

      case 3:
        run_query_3(db);
        break;

      case 4:
        run_query_4(db);
        break;

      case 5:
      run_query_5(db);
        break;

      case 6:
        run_query_6(db);
        break;

      default:
        std::cout << "ERORRE: l'opzione selezionata e' inesistente.\n";
        break;
    }

  } while (!exit);
}

void
query(Database& db)
{
  db.prepared_query("Query 1",
                    R"(
        SELECT D.NOME, D.COGNOME, A.NOME, R.GIUDIZIO,
            COALESCE(R.MOTIVAZIONE,'* Nessuna motivazione fornita') AS MOTIVAZIONE
        FROM DATI_CLIENTE AS D
        JOIN CLIENTE AS C
          ON D.EMAIL_CLIENTE = C.EMAIL
        JOIN RECENSIONE AS R
          ON C.EMAIL = R.EMAIL_CLIENTE
        JOIN ALLOGGIO AS A
          ON R.ID_CITTA_ALLOGGIO = A.ID_CITTA
        AND R.NOME_ALLOGGIO = A.NOME
      WHERE GIUDIZIO >= $1::integer;
    )",
                    1);

  db.prepared_query("Query 2",
                    R"(
      SELECT C.NOME AS NOME_COMPAGNIA,
            COUNT(V.CODICE) AS NUMERO_VOLI,
            AVG(V.PREZZO) AS MEDIA_PREZZO_VOLO,
            MAX(V.PREZZO) AS PREZZO_MASSIMO,
            MIN(V.PREZZO) AS PREZZO_MINIMO
        FROM COMPAGNIA C
        JOIN VOLO AS V
          ON C.EMAIL = V.EMAIL_COMPAGNIA
      GROUP BY C.NOME
      HAVING COUNT(V.CODICE) >= $1::integer
      ORDER BY NUMERO_VOLI DESC;
    )",
                    1);

  // Precompilamo anche la query 3, ma senza parametri
  db.prepared_query("Query 3",
                    R"(
          SELECT AGENZIA.DENOMINAZIONE,
            NUMERO_OFFERTE.CONTEGGIO AS NUMERO_PACCHETTI,
            ROUND(MEDIA_PREZZI.MEDIA,2) AS PREZZO_MEDIO,
            ROUND(MEDIA_REC.MEDIA,2) as MEDIA_RECENSIONI
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
  )",
                    0);

  db.prepared_query("Query 4",
                    R"(
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
                WHERE $1::varchar = P.EMAIL_CLIENTE
                  AND P.CODICE_TRANSAZIONE = T.CODICE
                  AND PV.ID = P.ID_PACCHETTO_VIAGGIO
              ) AS DATI_PRENOTAZIONE
            ON INFO_TRASPORTO.CODICE = DATI_PRENOTAZIONE.CODICE;
    )",
                    1);

  db.prepared_query("Query 5",
                    R"(
            SELECT D.TITOLO, 
              DISPONIBILI.PREZZO, 
              DISPONIBILI.NUMERO_PERSONE, 
              DISPONIBILI.DATA_PARTENZA, 
              DISPONIBILI.DATA_RITORNO, 
              DISPONIBILI.NOME_ALLOGGIO, 
              C.NOME AS NOME_CITTA, 
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
                  AND P.DATA_PARTENZA > $1::timestamp
              ) AS DISPONIBILI,
              
              DESCRIZIONE AS D,
              CITTA AS C
              
        WHERE D.ID = DISPONIBILI.ID_DESCRIZIONE
          AND C.ID = DISPONIBILI.ID_CITTA_ALLOGGIO
          AND DISPONIBILI.PREZZO > $2::numeric(7,2)
          AND DISPONIBILI.PREZZO < $3::numeric(7,2)
        ORDER BY DISPONIBILI.DATA_PARTENZA;
  )",
                    3);

  db.prepared_query("Query 6",
                    R"(
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
            DIRETTO.PRIMO_VOLO AS DIRETTO,
            DIRETTO.TIMESTAMP_PARTENZA AS D_PARTENZA,
            DIRETTO.TIMESTAMP_ARRIVO AS D_ARRIVO,
            DIRETTO.TOTALE_PREZZO AS D_PREZZO,
            SCALI.PRIMO_VOLO AS S_PARTENZA_CODICE,
            SCALI.VOLO_ATTUALE AS S_ARRIVO_CODICE,
            V.TIMESTAMP_PARTENZA AS S_PARTENZA,
            SCALI.TIMESTAMP_ARRIVO AS S_ARRIVO,
            SCALI.NUMERO_SCALI AS N_SCALI,
            SCALI.TOTALE_PREZZO AS S_PREZZO,
            SCALI.DURATA_TOTALE_VIAGGIO AS S_DURATA
        FROM
            POSSIBILI_SCALI AS DIRETTO,
            POSSIBILI_SCALI AS SCALI,
            VOLO AS V -- V Serve a ottenere le informazioni del primo volo di partenza
        WHERE
            DIRETTO.NUMERO_SCALI = 0
            AND DIRETTO.AEROPORTO_PARTENZA = $1::varchar
            AND DIRETTO.AEROPORTO_ARRIVO = $2::varchar
            AND DIRETTO.TOTALE_PREZZO > SCALI.TOTALE_PREZZO
            AND SCALI.NUMERO_SCALI > 0
            AND SCALI.AEROPORTO_ARRIVO = DIRETTO.AEROPORTO_ARRIVO
            AND SCALI.PRIMO_VOLO = V.CODICE;
  )",
                    2);
}

int
main(void)
{
  Database easy_travel = init_app();

  try {
    query(easy_travel);
  } catch (std::runtime_error& err) {
    std::cout << "\n\n\nERRORE: c'e' stato un problema nell'inviare la query "
                 "al server. Il programma verra' terminato.\n"
              << err.what() << "\n";
    easy_travel.close();
    exit(1);
  }

  main_menu(easy_travel);

  // Exit
  std::cout << "\n\n\nChiusura della connessione con il database...\n";
  easy_travel.close();
  return 0;
}