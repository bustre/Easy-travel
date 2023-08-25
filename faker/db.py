from faker import Faker
import random
from datetime import datetime, timedelta
from faker_airtravel import AirTravelProvider

## Utilizzo Transform e LLLAMA
# Use a pipeline as a high-level helper
#from transformers import pipeline
#pipe = pipeline("text-generation", model="openlm-research/open_llama_3b_v2")

fake = Faker()
fake_airlines = Faker()
fake_airlines.add_provider(AirTravelProvider)
Faker.seed(0)

# Impostazioni generali
sqlFile = open("data.sql","w")
numeroClienti = 0
numeroCompagnie = 0
numeroBagagli = 0
numeroCittà = 0
numeroTranzazioni = 0


# Strutture dati
def random_faker():
    loc = ["fr_FR", "it_IT", "de_DE", "us_US"]
    return Faker(loc[random.randint(0, len(loc)-1)])

class Cliente:
    def __sex(self):
        p = random.randint(0,100)

        if p < 49:
            return "'F'"
        elif p < 52:
            return "'NULL'"
        else:
            return "'M'"

    def __phone(self):
        p = random.randint(0,100)

        if p < 2:
            return "NULL"
        else:
            return "'"+ fake.phone_number()+"'"

    def __init__(self):
        fake = random_faker()
        self.username = fake.unique.user_name()
        self.nome = fake.first_name()
        self.cognome = fake.last_name()
        self.password = fake.password(random.randint(8,24))
        self.email = fake.unique.email()
        self.dataIscrizione =  datetime.combine(fake.date_between(start_date='-5y', end_date='now'), fake.time_object())
        self.dataNascita = fake.date_between(start_date='-50y', end_date='-10y')
        self.sesso = self.__sex()
        self.telefono = fake.phone_number()

    def __str__(self):
        str_dati = f"INSERT INTO DatiCliente VALUES ('{self.username}', '{self.nome}', '{self.cognome}', '{self.dataNascita}', {self.sesso}, {self.telefono}); "
        str_cliente = f"INSERT INTO Cliente VALUES ('{self.username}', '{self.password}', '{self.email}', '{self.dataIscrizione}'); "
        return str_dati + str_cliente

class Compagnia:
    def __init__(self):
        self.nome = fake_airlines.airline()
        self.username = self.nome.replace(" ", "_")
        self.password = fake_airlines.password(24)
        self.dataIscrizione =  datetime.combine(fake_airlines.date_between(start_date='-5y', end_date='now'), fake_airlines.time_object())
        self.email = "support@" + self.nome.replace(" ", "") + ".com"
        self.ICAO = fake_airlines.airport_icao()

    def __hash__(self):
        return hash(self.nome)
    
    def __eq__(self,value):
        return self.nome == value.nome

    def __str__(self):
        return f"INSERT INTO Compagnia VALUES ('{self.username}', '{self.password}', '{self.email}', '{self.dataIscrizione}', '{self.nome}', '{self.ICAO}');"

class InformazioniBagaglio:
    def __init__(self,id):
        self.id = id

        mano = random.randint(1,12)
        stiva = random.randint(1,25)

        if mano < 3:
            self.bagaglioMano = "NULL"
        else:
            self.bagaglioMano = "'"+str(mano)+"'"

        if stiva < 5:
            self.bagaglioStiva = "NULL"
        else:
            self.bagaglioStiva = "'"+str(stiva)+"'"
    
    def __hash__(self) -> int:
        return hash(self.bagaglioMano) + hash(self.bagaglioStiva)
    
    def __eq__(self, __value: object) -> bool:
        return self.bagaglioMano == __value.bagagliMano and self.bagaglioStiva == __value.bagaglioStiva

    def __str__(self):
        return f"INSERT INTO InformazioniBagagli VALUES ('{self.id}', {self.bagaglioMano}, {self.bagaglioStiva});"

class Città:
    def __init__(self, id):
        fake = random_faker()
        self.id = id
        self.nome = fake.city()
        self.stato = fake.current_country()
    
    def __hash__(self):
        return hash(self.nome)
    
    def __eq__(self, __value: object) -> bool:
        return self.nome == __value.nome

    def __str__(self):
        return f"INSERT INTO Città VALUES ('{self.id}','{self.nome}', '{self.stato}');"

class Transazione:
    def __circuitoRandom(self):
        circuiti = ["Visa"]
        return circuiti[random.randint(0,len(circuiti)-1)]

    def __bancaRandom(self):
        banche = ["Hamlin, Hamlin & McGill (HHM)", "TrustWave", "FirstChoiceFinance", "SafeInvestment", "RisparmiSicuri"]
        return banche[random.randint(0,len(banche)-1)]

    def __init__(self, importo, timestamp):
        self.codice = str.upper(fake.unique.pystr(min_chars=16, max_chars=16))
        self.banca = self.__bancaRandom()
        self.importo = importo
        self.circuito = self.__circuitoRandom()
        self.timestamp = timestamp


    def __str__(self):
        return f"INSERT INTO Transazione VALUES ('{self.codice}', '{self.banca}', '{self.importo}', '{self.circuito}', '{self.timestamp}');"

class Polizza:
    def __init__(self, id, titolo, descrizione) -> None:
        self.id = id
        self.titolo = titolo
        self.descrizione = descrizione

    def __str__(self) -> str:
        return "INSERT INTO Polizza VALUES('{self.id}','{self.titolo}',{self.descrizione});"

class PacchettoViaggio:
    def __init__(self, id, usernameAgenzia, idPolizza, idDescrizione, idCittàAlloggio, nomeAlloggio):
        self.id = id
        self.prezzo = random.uniform(400, 1700)
        self.numeroPersone = random.randint(1,4)
        self.disponibilità = random.randrange(3,8)
        self.dataPartenza = fake.date_between(start_date='-4y', end_date='+1y')
        self.dataRitorno = self.dataPartenza + timedelta(days=random.randint(3,14))
        self.usernameAgenzia = usernameAgenzia
        self.idPolizza = idPolizza
        self.idDescrizione = idDescrizione
        self.idCittàAlloggio = idCittàAlloggio
        self.nomeAlloggio = nomeAlloggio
    
    def __str__(self) -> str:
        pass #return f"INSERT INTO PacchettoViaggio VALUES('{self.id}', )"

## Generazione dati
print("Generazione dati...")

listaClienti = [
    Cliente() for i in range(0,numeroClienti)
    ]
listaCompagnie = [
    Compagnia() for i in range(0,numeroCompagnie)
    ]
listaBagagli = [
    InformazioniBagaglio(i) for i in range(0,numeroBagagli)
    ]
listaCittà = [
    Città(i) for i in range(0,numeroCittà)
]

listaPolizza = [
    Polizza(1, "Polizza di Viaggio Completa",open("polizze/full.txt","r").read()),
    Polizza(2, "Polizza di Viaggio Covid19",open("polizze/covid19.txt","r").read()),
    Polizza(3, "Polizza di Viaggio per Animali Domestici", open("polizze/pet.txt","r").read()),
    Polizza(0, "Polizza di Viaggio Base", open("polizze/base.txt","r").read())
]

# Da derivare
listaTransazioni = [
    Transazione(0,0) for i in range(0,numeroTranzazioni)
]

## Remove duplicate
print("Fix limiti Faker...")
listaCompagnie = list(set(listaCompagnie))
listaBagagli = list(set(listaBagagli))
listaCittà = list(set(listaCittà))

## Scrittura
print("Scrittura dati...")
for x in listaClienti:
    sqlFile.write(str(x))

for x in listaCompagnie:
    sqlFile.write(str(x))

for x in listaBagagli:
    sqlFile.write(str(x))

for x in listaCittà:
    sqlFile.write(str(x))

for x in listaTransazioni:
    sqlFile.write(str(x))

print("Lavoro terminato")
# Terminazione
sqlFile.close()