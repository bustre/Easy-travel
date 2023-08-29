#include "dependencies/include/libpq-fe.h"
#include <cstdio>
#include <fstream>
#include <iostream>

#define PG_HOST "127.0.0.1"
#define PG_USER "postgres"
#define PG_DB   "test"
#define PG_PORT 5432
#define PG_PASS "password"

int main (int argc, char *argv[])
{
  std::cout << "BOOT APP" << std::endl;

  char conninfo [250];
  sprintf(conninfo , "user =%s password =%s dbname =%s hostaddr =%s port =%d",
    PG_USER , PG_PASS , PG_DB , PG_HOST , PG_PORT);
  
  PGconn * conn = PQconnectdb (conninfo);

  if (PQstatus(conn) != CONNECTION_OK)
  {
    std::cout << "BAD!" << std::endl;
    exit(1);
  }

  PQfinish(conn);

  std::cout << "Hello world!" << std::endl;
  return 0;
}
