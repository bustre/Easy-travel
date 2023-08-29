import string
from faker import Faker
import random
from datetime import datetime, timedelta
from faker_airtravel import AirTravelProvider

random.seed(2042383, version=2)

fake = Faker()
fake_airlines = Faker()
fake_airlines.add_provider(AirTravelProvider)
Faker.seed(0)

# Impostazioni generali
sqlFile = open("data.sql","w")
numeroClienti = 30
numeroCompagnie = 3
numeroBagagli = 10
numeroCittà = 30
numeroPacchetti = 15
numeroAgenzie = 3
numeroAlloggi = int(numeroPacchetti * 0.50) # Gli alloggi sono il 60 % dei pacchetti
n_acquisti = 30


### Strutture dati
def random_faker():
    loc = ["it_IT"]
    return Faker(loc[random.randint(0, len(loc)-1)])

class Cliente:
    def __sex(self):
        p = random.uniform(0,100)

        if p < 49:
            self.nome = self.fake.first_name_female()
            return "'F'"
        elif p < 51:
            self.nome = self.fake.first_name_nonbinary()
            return "NULL"
        else:
            self.nome = self.fake.first_name_male()
            return "'M'"

    def __phone(self):
            return  "+39" + " " + fake.msisdn()[0:9]
    
    def __randomEmail(self):
        p = random.randint(0,100)

        if (p <= 2):
            return fake.unique.email()
        elif (p <= 60):
            return self.nome + "." + self.cognome + random.choice(["@email.com", "@fastmail.org", "@lambda.mail.it"])
        else:
            return self.cognome + str(p) + "@" + self.cognome + random.choice(["@email.com", "@fastmail.org", "@lambda.mail.it"])
        

    def __init__(self):
        fake = random_faker()
        self.fake = fake
        self.name = ""   
        self.sesso = self.__sex()
        self.cognome = fake.last_name()
        self.password = fake.password(random.randint(8,24))
        self.email = self.__randomEmail()
        self.data_iscrizione =  datetime.combine(fake.date_between(start_date='-5y', end_date='-4y'), fake.time_object())
        self.data_nascita = fake.date_between(start_date='-50y', end_date='-22y')

        self.telefono = self.__phone()

    def __hash__(self) -> int:
        return hash(self.email)
    
    def __eq__(self, __value: object) -> bool:
        return self.email == __value.email

    def __str__(self):
        str_dati = f"INSERT INTO Dati_Cliente VALUES ('{self.email}', '{self.nome}', '{self.cognome}', '{self.data_nascita}', {self.sesso}, '{self.telefono}');\n"
        str_cliente = f"INSERT INTO Cliente VALUES ('{self.email}', '{self.password}', '{self.data_iscrizione}');\n"
        return str_dati + str_cliente

class Compagnia:
    def __randomName(self):
        nomi_compagnie_di_linea = [
            "AirLink Express",
            "RoadRunner Airlines",
            "AquaJet Ferries",
            "MetroWings Airlines",
            "CloudHopper Airways",
            "HighFlyer Airlines",
            "RiverRide Cruises",
            "StarSail Ferries",
            "SkySprint Airlines",
            "EcoVoyage Cruises",
        ]

        p = random.randint(0,len(nomi_compagnie_di_linea)-1)
        return nomi_compagnie_di_linea[p]

    def __init__(self):
        self.nome = self.__randomName()
        self.password = fake_airlines.password(24)
        self.dataIscrizione =  datetime.combine(fake_airlines.date_between(start_date='-5y', end_date='-3y'), fake_airlines.time_object())
        self.email = "team@" + self.nome.replace(" ", "") + ".com"
        self.ICAO = fake_airlines.airport_icao()

    def __hash__(self):
        return hash(self.email)
    
    def __eq__(self,value):
        return self.email == value.email

    def __str__(self):
        return f"INSERT INTO Compagnia VALUES ('{self.email}', '{self.password}', '{self.dataIscrizione}', '{self.nome}', '{self.ICAO}');\n"

class InformazioniBagagli:
    def __init__(self,id,force_to_be_good=0):
        self.id = id

        if force_to_be_good == 0:
            mano = 0
        else:
            mano = random.randint(1,12)

        if force_to_be_good == 0:
            stiva = random.randint(10,20)
        else:
            stiva = random.randint(1,12)

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
        return self.bagaglioMano == __value.bagaglioMano and self.bagaglioStiva == __value.bagaglioStiva

    def __str__(self):
        return f"INSERT INTO INFORMAZIONI_BAGAGLI VALUES ('{self.id}', {self.bagaglioMano}, {self.bagaglioStiva});\n"

external_strange_unique_counter = 0
class Descrizione:

    def __hash__(self) -> int:
        return hash(self.id)

    def __init__(self, id, titolo, body, tipologia, luogo="") -> None:
        self.id = id
        self.tipologia = tipologia
        self.luogo = luogo
        self.titolo = titolo.replace("'","''")
        self.body = body.replace("'","''")

    def __eq__(self, __value: object) -> bool:
        return self.titolo == __value.titolo and self.body == __value.body

    def __str__(self) -> str:
        return f"INSERT INTO DESCRIZIONE VALUES ({self.id}, '{self.titolo}', '{self.body}');\n"

class Polizza:
    def __init__(self, id, titolo, descrizione) -> None:
        self.id = id
        self.titolo = titolo
        self.descrizione = descrizione.replace("'","''")

    def __str__(self) -> str:
        return f"INSERT INTO Polizza VALUES({self.id},'{self.titolo}','{self.descrizione}');\n"

class Città:
    def __init__(self, id):
        fake = random_faker()
        self.id = id
        self.nome = fake.city().replace("'","''")
        self.stato = fake.current_country().replace("United States", "Stati Uniti").replace("Italy","Italia").replace("France", "Francia").replace("Germany", "Germania")
    
    def __hash__(self):
        return hash(self.nome)
    
    def __eq__(self, __value: object) -> bool:
        return self.nome == __value.nome

    def __str__(self):
        return f"INSERT INTO Citta VALUES ('{self.id}','{self.nome}', '{self.stato}');\n"

class Alloggio:
    def __randomScelta(self):
        alloggi_vacanze = [
            ("Hotel", "The Royal Palm Resort"),
            ("Casa", "Villetta Solemar"),
            ("Appartamento", "Appartamento La Terrazza"),
            ("Suite", "Suite Belle Époque"),
            ("Hotel", "Grand Hotel Belvedere"),
            ("Casa", "Casa Vista Mare"),
            ("Appartamento", "Appartamento Dolce Vita"),
            ("Suite", "Suite Paradiso Blu"),
            ("Hotel", "Hotel Montagna Magica"),
            ("Casa", "Casa delle Querce"),
            ("Appartamento", "Appartamento Serenità"),
            ("Suite", "Suite Luna di Miele"),
            ("Hotel", "Hotel Aurora"),
            ("Casa", "Casa delle Stelle Cadenti"),
            ("Appartamento", "Appartamento Sogni d'Oro"),
            ("Suite", "Suite Etoile"),
            ("Hotel", "Hotel La Cascata"),
            ("Casa", "Casa dei Ciliegi"),
            ("Appartamento", "Appartamento L'Orizzonte"),
            ("Suite", "Suite Nebbia Mattutina"),
            ("Hotel", "Hotel L'Oasi"),
            ("Casa", "Casa dell'Ulivo"),
            ("Appartamento", "Appartamento del Sole"),
            ("Suite", "Suite Notte Stellata"),
            ("Hotel", "Hotel Panorama"),
            ("Casa", "Casa del Bosco"),
            ("Appartamento", "Appartamento Dolce Luna"),
            ("Suite", "Suite Fiore di Loto"),
            ("Hotel", "Hotel Le Vigne"),
            ("Casa", "Casa dei Gabbiani"),
            ("Appartamento", "Appartamento La Brezza"),
            ("Suite", "Suite dei Sogni"),
            ("Hotel", "Hotel Alpino"),
            ("Casa", "Casa del Laghetto"),
            ("Appartamento", "Appartamento Vista Incantata"),
            ("Suite", "Suite Incanto del Lago"),
        ]

        self.tipologia, self.nome = random.choice(alloggi_vacanze)
        self.nome = self.nome.replace("'","''")

    def __randomStar(self):
        y = random.randint(0,5)

        if y == 0 or (self.tipologia != "Hotel" and self.tipologia != "Suite"):
            return "NULL"
        else:
            return "'"+str(y)+"'"

    def __hash__(self) -> int:
        return hash(self.id_città)
    
    def __eq__(self, __value: object) -> bool:
        return self.id_città == __value.id_città and self.nome == __value.nome

    def __init__(self, id_città, id_descrizione) -> None:
        self.__randomScelta()
        self.id_città = id_città
        self.valore_atteso = random.uniform(0,5)
        self.stelle = self.__randomStar()
        self.id_descrizione = id_descrizione
        self.inidirizzo = random.choice([
            "Via Garibaldi 25",
            "Corso Vittorio Emanuele 68",
            "Via Dante Alighieri 42",
            "Via Leonardo da Vinci 105",
            "Via Giuseppe Verdi 71",
            "Via Alessandro Volta 56",
            "Piazza San Marco 7",
            "Via Cavour 33",
            "Corso Italia 92",
            "Via Roma 120",
            "Via Manzoni 78",
            "Via Carducci 60",
            "Via Montenapoleone 15",
            "Via della Repubblica 50",
            "Via dei Mille 95",
            "Piazza Duomo 1",
            "Corso Buenos Aires 123",
            "Via Garofalo 37",
            "Via Giotto 29",
            "Piazza Navona 10",
        ])

    def __str__(self) -> str:
        return f"INSERT INTO ALLOGGIO VALUES ({self.id_città}, '{self.nome}', {self.stelle}, '{self.tipologia}', {self.id_descrizione}, '{self.inidirizzo}');\n"

class Agenzia:
    def __randomName(self):
        agenzie_di_viaggio = agenzie_di_viaggio = [
            "Viaggi Serendipità",
            "Odissea Esplorativa",
            "Viaggi Nell'Immaginario",
            "Destinazioni Affascinanti",
            "Itinerari Incantati",
            "Avventure nel Mondo",
            "Viaggi Verso l'Ignoto",
            "Turismo Magico",
            "Orizzonti Inusuali",
            #"Viaggi di Sogni",
            #"Viaggi nel Tempo e Nello Spazio",
            "Svela il Mondo",
            "Destinazioni Segrete",
            "Turismo EcoAvventura",
            "Viaggi Nella Cultura",
            "Viaggi Visionari",
            "Sogni Senza Confini",
            #"Viaggi di Ogni Sfumatura",
            "Oltre le Frontiere",
            "Viaggi Stellari",
            "Esplorazioni Infiniti",
            "Turismo EcoRispettoso",
            #"Viaggi Culturalmente",
            "Destinazioni da Sogno",
            "Scoperte Nell'Eden",
            "Turismo Rurale Magico",
            "Viaggi Stile un Tuoi",
            "Viaggi nel Mondo Rotante",
            "Destinazioni Incantate",
            "Esperienze Immersive",
            "Turismo Sostenibile",
            "Viaggi Culturali Mistiche",
            "Giro del Mondo Senza Fine",
            "Viaggi Unici",
            "Esplora il Mondo Segreto",
            "Viaggi nel Futuro Antico",
            "Sogno di Destinazioni",
            "Viaggi dei Desideri",
            "Turismo Edenico",
            #"Viaggi di Lusso Sartoriale",
        ]

        return agenzie_di_viaggio[random.randint(0,len(agenzie_di_viaggio)-1)].replace("'","''")
    
    def __init__(self, idCittà) -> None:
        self.denominazione = self.__randomName()
        self.password = fake.password(random.randint(16,24))
        self.email = "support@" + self.denominazione.replace(" ","") + ".com"
        self.data_iscrizione = datetime.combine(fake.date_between(start_date='-5y', end_date='-1y'), fake.time_object())
        self.id_città = idCittà
        self.indirizzo = random.choice([
            "Via Manzoni 55",
            "Viale dei Fiori 14",
            "Corso Italia 33",
            "Via Roma 72",
            "Piazza del Popolo 6",
            "Via Dante Alighieri 23",
            "Via Garibaldi 98",
            "Via Leonardo da Vinci 40",
            "Via Milano 17",
            "Via Verdi 8",
            "Piazza San Marco 5",
            "Corso Vittorio Emanuele 77",
            "Via Cavour 21",
            "Via Montenapoleone 10",
            "Via Carducci 31",
            "Via della Repubblica 61",
            "Piazza Duomo 2",
            "Corso Buenos Aires 47",
            "Via Garofalo 19",
            "Viale Mazzini 37",
            "Via Giotto 28",
        ])

    def __hash__(self) -> int:
        return hash(self.email)
    
    def __eq__(self, __value: object) -> bool:
        return self.email == __value.email

    def __str__(self) -> str:
        return f"INSERT INTO AGENZIA VALUES ('{self.email}', '{self.password}', '{self.data_iscrizione}', '{self.denominazione}', {self.id_città}, '{self.indirizzo}');\n"

class Aeroporto:
    def __init__(self, città) -> None:
        self.codice = ''.join(random.choice(string.ascii_letters) for _ in range(4)).upper()
        self.id_città = città

    def __hash__(self) -> int:
        return hash(self.codice)
    
    def __eq__(self, __value: object) -> bool:
        return self.codice == __value.codice
    
    def __str__(self) -> str:
        return f"INSERT INTO AEROPORTO VALUES ('{self.codice}', '{self.id_città}');\n"

class Transazione:
    def __circuitoRandom(self):
        circuiti = [
            "BancaNet Connect",
            "FinanzaLink",
            "MonetaSecure",
            "TransaFondo",
            "PagamentiPlus",
            "CapitalNet",
            "MoneyMover",
            "SecureTransact",
            "CashFlow Connect",
            "TrustFund Express",
            "BancaLink Global",
            "MonetaFlow",
            "PayGuard Pro",
            "FinanzaTrust",
            "EasyExchange",
            "CapitalCrossing",
            "FinanzaSwift",
            "MonetaShield",
            "CashWave",
            "SecurePay Connect"
        ]
        return circuiti[random.randint(0,len(circuiti)-1)]

    def __bancaRandom(self):
        banche = [
            "Hamlin, Hamlin & McGill (HHM)",
            "TrustWave",
            "FirstChoiceFinance",
            "SafeInvestment",
            "RisparmiSicuri",
            "Banca del Futuro",
            "TrustBank",
            "UniCassa",
            "CapitalSecure",
            "EcoCredit",
            "FinanzaProgress",
            "SavingsFirst",
            "GlobalTrust Bank",
            "SecureSavings",
            "Prosperity Bank",
            "GreenFinance",
            "Liberty Bank",
            "InnovaBank",
            "HarborTrust",
            "NexaFinance",
            "TransactTrust",
            "SmartBank",
            "LibraBank",
            "Sunrise Savings",
            "WealthLink Bank"
        ]

        return banche[random.randint(0,len(banche)-1)]

    def __init__(self, importo, timestamp):
        self.codice = str.upper(fake.unique.pystr(min_chars=16, max_chars=16))
        self.banca = self.__bancaRandom()
        self.importo = importo
        self.circuito = self.__circuitoRandom()
        self.timestamp = timestamp

    def __hash__(self) -> int:
        return hash(self.codice)
    
    def __eq__(self, __value: object) -> bool:
        return self.codice == __value.codice

    def __str__(self):
        return f"INSERT INTO TRANSAZIONE VALUES ('{self.codice}', '{self.banca}', {self.importo}, '{self.circuito}', '{self.timestamp}');\n"

class Volo:
    def __randomClass(self,tipologia, force):
        tipologie_di_volo = [
            ("Economy", 1.0),
            ("Economy Standard", 1.0),
            ("Premium Economy", 1.2),
            ("Business", 1.5),
            ("Prima Classe", 2.0),
            ("Economy Plus", 1.1),
            ("Business Deluxe", 1.8)
        ]

    
        if force == -1:
            self.tipologia, self.prezzo = tipologie_di_volo[random.randint(0, len(tipologie_di_volo)-1)]
            self.prezzo *= round(random.uniform(40, 80),2)
        else:
            self.tipologia, self.prezzo = tipologia, force

    def __randomCheckin(self):
        lcheckin = ['Online', 'Aeroporto']

        self.checkin = lcheckin[random.randint(0, len(lcheckin)-1)]

    def __init__(self, codice, email, partenza, arrivo, tpartenza, tarrivo, id_bagagli, force=-1, tipologia=None) -> None:
        self.codice = codice
        self.email = email
        self.__randomClass(tipologia, force)
        self.__randomCheckin()
        self.partenza = partenza
        self.arrivo = arrivo
        self.tpartenza = tpartenza
        self.tarrivo = tarrivo
        self.id_bagagli = id_bagagli

    def __str__(self) -> str:
        return f"INSERT INTO VOLO VALUES({self.codice}, '{self.tipologia}', '{self.checkin}', {self.prezzo}, '{self.email}', '{self.partenza}', '{self.tpartenza}', '{self.arrivo}', '{self.tarrivo}', {self.id_bagagli});\n"

class PacchettoViaggio:
    def __init__(self, id, emailAgenzia, idPolizza, idDescrizione, idCittàAlloggio, nomeAlloggio):
        self.id = id
        self.prezzo = round(random.uniform(400, 1400),2)
        if self.prezzo > 800:
            self.tipologia = "Costoso"
        else:
            self.tipologia = "Economy"
        self.numeroPersone = random.randint(1,4)
        self.disponibilità = random.randrange(1,8)
        self.disponibilità_exec = self.disponibilità # Trucchetto per evitare di usare un pacchetto troppe volte :D
        self.dataPartenza = fake.date_between(start_date='-4y', end_date='+1y')
        self.dataRitorno = self.dataPartenza + timedelta(days=random.randint(3,14))
        self.Agenzia = emailAgenzia
        self.idPolizza = idPolizza
        self.idDescrizione = idDescrizione
        self.idCittàAlloggio = idCittàAlloggio
        self.nomeAlloggio = nomeAlloggio
    
    def __str__(self) -> str:
        return f"INSERT INTO PACCHETTO_VIAGGIO VALUES({self.id}, {self.prezzo}, {self.numeroPersone}, {self.disponibilità}, '{self.dataPartenza}', '{self.dataRitorno}', '{self.Agenzia}', {self.idPolizza}, {self.idDescrizione}, {self.idCittàAlloggio}, '{self.nomeAlloggio}');\n"

class Prenotazione:
    def __init__(self, codice_transizione, cliente, max_persone, id_viaggio, inizio, fine) -> None:
        self.codice_transizione = codice_transizione
        self.numero_persone = random.randint(1,max_persone)
        self.id_viaggio = id_viaggio
        self.cliente = cliente
        self.inizio = inizio
        self.fine = fine 

    def __str__(self) -> str:
        return f"INSERT INTO PRENOTAZIONE VALUES('{self.codice_transizione}', '{self.cliente.email}', {self.numero_persone}, {self.id_viaggio});\n"

class InformazioniTrasporto:
    def __init__(self, codice_transizione, lista_voli, n_persone) -> None:
        self.codice_transizione = codice_transizione
        self.prezzo_totale = round(sum([volo.prezzo * n_persone for volo in lista_voli]),2)
    
    def __str__(self) -> str:
        return f"INSERT INTO INFORMAZIONI_TRASPORTO VALUES ('{self.codice_transizione}', '{self.prezzo_totale}');\n"

class TrattaVolo:
    def __init__(self, codice_transizione, codice_volo, tipologia) -> None:
        self.codice_transizione = codice_transizione
        self.codice_volo = codice_volo
        self.tipologia = tipologia # "Andata", ritorno

    def __str__(self) -> str:
        return f"INSERT INTO {self.tipologia} VALUES ('{self.codice_transizione}', {self.codice_volo});\n"

class Recensione:
    __reviews = [
            ("Non è stato male, ma potrebbe migliorare.", 3),
            ("Vacanza fantastica! Non vedo l'ora di tornare.", 5),
            ("Mi aspettavo di più, non è stato all'altezza delle aspettative.", 2),
            ("Luogo tranquillo e suggestivo, ideale per staccare la spina.", 4),
            ("Un'esperienza deludente, non consigliato.", 1),
            ("Mi sono divertito molto, ottimo rapporto qualità-prezzo.", 4),
            ("Luogo incantevole ma il servizio era mediocre.", 3),
            ("Una vacanza indimenticabile, tutto perfetto!", 5),
            ("Non male, ma ci sono stati alcuni problemi.", 3),
            ("Un posto meraviglioso, mi sono sentito come in paradiso.", 5),
            ("Non ci tornerei mai, un'esperienza terribile.", 0),
            ("Un luogo decente per il prezzo che abbiamo pagato.", 3),
            ("Vacanza piacevole ma c'è spazio per il miglioramento.", 4),
            ("Un soggiorno deludente, non era come me lo aspettavo.", 2),
            ("Questo posto ha superato di gran lunga le mie aspettative!", 5),
            ("Un'esperienza terribile, non consigliato a nessuno.", 1),
            ("Vacanza tranquilla in un ambiente bellissimo.", 4),
            ("Mi sono divertito molto, un'esperienza indimenticabile.", 5),
            ("Non era male, ma c'era sicuramente margine per migliorare.", 3),
            ("Un posto tranquillo e rilassante, perfetto per staccare la spina.", 4),
            ("Non era esattamente come me lo aspettavo, ma comunque piacevole.", 3),
            ("Vacanza da sogno! Lo raccomanderei a tutti.", 5),
            ("Servizio scadente e strutture vecchie, delusione totale.", 1),
            ("Soggiorno piacevole in un ambiente incantevole.", 4),
            ("Non vale il prezzo che abbiamo pagato, esperienza deludente.", 2),
            ("Un'esperienza davvero fantastica, torneremo sicuramente.", 5),
            ("Il personale era gentile, ma le stanze avevano bisogno di manutenzione.", 3),
            ("Una vacanza da sogno, tutto era perfetto!", 5),
            ("Sicuramente c'è spazio per miglioramenti, ma nel complesso ok.", 3),
            ("Luogo incantevole e tranquillo, ideale per una fuga romantica.", 4),
            ("Non ero entusiasta, ma alla fine è stata una buona esperienza.", 3),
            ("Vacanza da sogno, il paradiso sulla terra.", 5),
            ("Non era terribile ma avevamo aspettative più alte.", 3),
            ("Un'esperienza incantevole, consigliato a tutti.", 5),
            ("Strutture vecchie e sporche, non tornerò mai più.", 1),
            ("Un luogo davvero affascinante, ideale per rilassarsi.", 4),
            ("Mi aspettavo di più, ma alla fine è stata comunque una buona esperienza.", 3),
            ("Vacanza fantastica, servizio impeccabile.", 5),
            ("Non è stato terribile ma c'erano alcuni problemi.", 3),
            ("Un'esperienza indimenticabile, lo raccomanderei a tutti.", 5),
            ("Soggiorno deludente, non all'altezza delle aspettative.", 2),
            ("Un posto davvero suggestivo, ideale per rilassarsi.", 4),
            ("Non ci tornerei mai, è stata una delusione totale.", 1),
            ("Servizio eccellente, vacanza perfetta.", 5),
            ("Non male, ma c'erano alcune carenze.", 3),
            ("Un'esperienza meravigliosa, torneremo sicuramente.", 5),
            ("Strutture vecchie ma personale cordiale.", 3),
            ("Vacanza da sogno in un luogo paradisiaco.", 5),
            ("Non era esattamente come me lo aspettavo, ma comunque decente.", 3),
            ("Soggiorno piacevole, ma servizio lento.", 4),
            ("Servizio scadente e cibo mediocre, delusione totale.", 2)
        ]

    def __random(self,valore_atteso):

        result = []
        for y,x in self.__reviews:
            if valore_atteso-1 <= x <= valore_atteso+1:
                result.append((y,x))
        
        self.motivazione, self.giudizio = random.choice(result)
        if random.uniform(0,100) < 60:
            self.motivazione = "NULL"
        else:
            self.motivazione = "'" + self.motivazione.replace("'","''") + "'"


    def __init__(self, id, email_cliente, data, id_città, nome_alloggio, valore_atteso) -> None:
        self.id = id
        self.giudizio = 0
        self.email_cliente = email_cliente
        self.data = data + timedelta(days=random.randint(0,30))
        self.motivazione = "NULL"
        self.__random(valore_atteso)
        self.id_città = id_città
        self.nome_alloggio = nome_alloggio

    def __str__(self) -> str:
        return f"INSERT INTO RECENSIONE VALUES ({self.id}, {self.giudizio}, {self.motivazione}, '{self.email_cliente}', '{self.data}', {self.id_città}, '{self.nome_alloggio}');\n"

def FiltraPacchetti(lista):
    tmp = []
    for x in lista:
        if x.disponibilità_exec > 0:
            tmp.append(x)
    return tmp

def FiltraClienti(lista_clienti, pacchetto, lista_prenotazioni):
    tmp = []

    for x in lista_clienti:
        if x.data_iscrizione.date() < pacchetto.dataPartenza:
            già_viaggio = False
            for p in lista_prenotazioni:
                if p.cliente.email == x.email and (p.inizio <= pacchetto.dataPartenza <= p.fine or p.inizio <= pacchetto.dataRitorno <= p.fine):
                    già_viaggio = True
            if not già_viaggio:
                tmp.append(x)
    return tmp

def CreaAeroporto(lista, idCittà):
    result = Aeroporto(idCittà)
    for x in lista:
        if x.codice == result.codice:
            result = CercaAeroporto(lista,idCittà)
    return result

def CercaAeroporto(lista, idCittà):
    result = None
    for x in lista:
        if x.id_città == idCittà:
            result = x
            break
    if type(result) == type(None):
        result = CreaAeroporto(lista,idCittà)
        lista.append(result)
    
    return lista, result

def CittàRandom(lista, skip_id):
    x = random.choice(lista)
    if x.id != skip_id:
        return x
    else:
        return CittàRandom(lista, skip_id)
    
def TrovaAlloggio(lista, id):
    for x in lista:
        if x.id_città == id:
            return x

## Generazione dati
print("Generazione dati di base...")

lista_clienti = [
    Cliente() for i in range(0,numeroClienti)
    ]
lista_clienti = list(set(lista_clienti))

lista_compagnie = [
    Compagnia() for i in range(0,numeroCompagnie)
    ]
lista_compagnie = list(set(lista_compagnie))

lista_bagagli = [
    InformazioniBagagli(i,i%2) for i in range(0,numeroBagagli)
    ]
lista_bagagli = list(set(lista_bagagli))

lista_città = [
    Città(i) for i in range(0,numeroCittà)
]
lista_città = list(set(lista_città))

lista_polizze = [
    Polizza(1, "Polizza di Viaggio Completa",open("polizze/full.txt","r").read()),
    Polizza(2, "Polizza di Viaggio Covid19",open("polizze/covid19.txt","r").read()),
    Polizza(3, "Polizza di Viaggio Pets", open("polizze/pet.txt","r").read()),
    Polizza(0, "Polizza di Viaggio Base", open("polizze/base.txt","r").read())
]

alloggi = [
    ("Hotel Bella Vista", "Un hotel di lusso con vista panoramica sulla baia.", "Hotel", "Mare"),
    ("Casa delle Montagne", "Una casa accogliente nelle Alpi con vista sulle montagne.", "Casa", "Montagna"),
    ("Suite di lusso al centro", "Una suite elegante nel cuore della città.", "Suite", "Città"),
    ("Appartamento sul mare", "Un appartamento affacciato sulla spiaggia di sabbia bianca.", "Appartamento", "Mare"),
    ("Chalet di montagna", "Un accogliente chalet di legno nelle montagne.", "Casa", "Montagna"),
    ("Hotel Elegante", "Un hotel di lusso nel centro della città.", "Hotel", "Città"),
    ("Suite vista mare", "Una suite di lusso con vista panoramica sul mare.", "Suite", "Mare"),
    ("Appartamento nel centro storico", "Un appartamento nel cuore della città antica.", "Appartamento", "Città"),
    ("Villa tranquilla", "Una villa spaziosa con giardino, perfetta per una vacanza rilassante.", "Casa", "Città"),
    ("Resort sulla spiaggia", "Un resort a cinque stelle direttamente sulla spiaggia.", "Hotel", "Mare"),
    ("Appartamento moderno", "Un appartamento moderno con una vista panoramica sulla città.", "Appartamento", "Città"),
    ("Chalet di montagna accogliente", "Un chalet di montagna con camino per una fuga invernale.", "Casa", "Montagna"),
    ("Suite di lusso con jacuzzi", "Una suite di lusso con jacuzzi privata.", "Suite", "Città"),
    ("Appartamento vista mare", "Un appartamento con vista sul mare e accesso diretto alla spiaggia.", "Appartamento", "Mare"),
    ("Hotel nel centro storico", "Un affascinante hotel nel cuore del centro storico.", "Hotel", "Città"),
    ("Villa sulle colline", "Una villa con piscina immersa nelle colline toscane.", "Casa", "Campagna")
]

viaggi = [
    ("Rilassati al Mare", "Goditi una vacanza rilassante al mare con spiagge di sabbia dorata e acque cristalline.", "mare"),
    ("Esplora una Città Vibrante", "Scopri una città piena di vita, con monumenti storici, ristoranti gourmet e vita notturna vivace.", "città"),
    ("Avventura in Montagna", "Fai trekking tra le montagne, respira l'aria fresca e ammira panorami mozzafiato.", "montagna"),
    ("Vacanza Culturale", "Immergiti nella cultura locale con visite a musei, gallerie d'arte e siti storici.", "città"),
    ("Rilassamento al Mare", "Trascorri giornate di puro relax sulla spiaggia e rilassati in resort di lusso.", "mare"),
    ("Esplorazione Urbana", "Passeggia per le strade affollate, assapora la cucina locale e scopri segreti nascosti della città.", "città"),
    ("Escursioni in Montagna", "Affronta escursioni impegnative e conquista le vette più alte.", "montagna"),
    ("Viaggio Enogastronomico", "Delizia il tuo palato con prelibatezze locali e degusta vini pregiati.", "città"),
    ("Divertimento in Spiaggia", "Partecipa a sport acquatici, feste in spiaggia e attività all'aperto.", "mare"),
    ("Arte e Cultura Urbana", "Esplora gallerie d'arte contemporanea, teatri e quartieri culturali.", "città"),
    ("Relax Costiero", "Goditi il suono delle onde e le brezze marine in un tranquillo rifugio sulla costa.", "mare"),
    ("Esplorazione Storica", "Scopri la storia antica della regione visitando siti archeologici e castelli medievali.", "città"),
    ("Sfide in Montagna", "Affronta percorsi avventurosi, arrampicate su roccia e gite in bicicletta in montagna.", "montagna"),
    ("Viaggio Gastronomico", "Assaggia la cucina locale attraverso tour culinari guidati e lezioni di cucina.", "città"),
    ("Spiaggia e Sport Acquatici", "Pratica sport acquatici come il surf, il nuoto e il kayak nelle acque cristalline.", "mare"),
    ("Vita Notturna Cittadina", "Esperienza notti indimenticabili con club, bar e spettacoli in città.", "città"),
    ("Percorsi Panoramici in Montagna", "Segui percorsi panoramici tra valli e cime montane mozzafiato.", "montagna"),
    ("Esperienza Teatrale", "Assisti a spettacoli teatrali, concerti e opere d'arte in città culturali.", "città"),
    ("Soggiorno di Lusso in Riva al Mare", "Vivi in ​​un resort di lusso con servizio personalizzato a due passi dalla spiaggia.", "mare"),
    ("Esplorazione Architettonica", "Ammira l'architettura unica delle città con edifici storici e moderni.", "città"),
    ("Ski e Neve", "Scia sulle piste innevate e rilassati in accoglienti chalet di montagna.", "montagna"),
    ("Cultura e Musica", "Immergiti nella scena musicale e culturale della città con concerti e festival.", "città"),
    ("Resort All-Inclusive", "Goditi un soggiorno senza pensieri in un resort all-inclusive con tutte le comodità.", "mare"),
    ("Tour Enologici", "Esplora le cantine locali e degusta i migliori vini e prodotti tipici della regione.", "città"),
    ("Avventure Subacquee", "Scopri il mondo sottomarino con immersioni subacquee e snorkeling.", "mare"),
    ("Arte Moderna e Contemporanea", "Visita musei d'arte moderna e contemporanea nelle città d'avanguardia.", "città"),
    ("Relax Termale in Montagna", "Rilassati nelle sorgenti termali naturali in un ambiente di montagna sereno.", "montagna"),
    ("Scoperta Storica e Religiosa", "Esplora siti storici e luoghi di culto in città ricche di storia.", "città"),
    ("Spiaggia e Yoga", "Rigenera corpo e mente con lezioni di yoga sulla spiaggia al sorgere del sole.", "mare"),
    ("Avventura in Montagna Estiva", "Esplora le montagne durante l'estate con escursioni e sport all'aperto.", "montagna"),
]


lista_agenzie = [
    Agenzia(random.choice(lista_città).id) for i in range(0,numeroAgenzie)
]
lista_agenzie = list(set(lista_agenzie))

lista_descrizioni_pacchetti = [
    Descrizione(0, titolo, testo, "", luogo) for  titolo, testo, luogo in viaggi
]

lista_descrizioni_alloggi = [
    Descrizione(0, titolo,testo,tipologia, luogo) for titolo, testo, tipologia, luogo in alloggi
]

for _,x in enumerate(lista_descrizioni_pacchetti):
    x.id = _

for _,x in enumerate(lista_descrizioni_alloggi):
    x.id = _ + len(lista_descrizioni_pacchetti) 

lista_alloggi = [
    Alloggio(
        random.choice(lista_città).id,
        lista_descrizioni_alloggi[i].id
    ) for i in range(0,len(lista_descrizioni_alloggi)-1)
]
lista_alloggi = list(set(lista_alloggi))

def random_pair(luogo, lista_descrizioni_p):
    filtrati = []
    for x in lista_descrizioni_p:
        if x.luogo.upper() == luogo.upper():
            filtrati.append(x)

    return random.choice(filtrati)

def search_descrizione(id):
    for x in lista_descrizioni_alloggi:
        if x.id == id:
            return x

# Generazione dati e relazioni 
print("Generazione dati e relazioni")
lista_pacchetti = []
for i in range(0,numeroPacchetti):
    alloggio = random.choice(lista_alloggi)
    lista_pacchetti.append(PacchettoViaggio(
        i,
        random.choice(lista_agenzie).email,
        random.choice(lista_polizze).id,
        random_pair(search_descrizione(alloggio.id_descrizione).luogo, lista_descrizioni_pacchetti).id,
        alloggio.id_città,
        alloggio.nome
    ))

## union
lista_descrizioni = lista_descrizioni_pacchetti + lista_descrizioni_alloggi
del lista_descrizioni_alloggi
del lista_descrizioni_pacchetti

lista_transizioni = []
lista_voli_partenza = []
lista_voli_ritorno = []
lista_aeroporti = []
lista_prenotazioni = []
lista_tratte = []
lista_info_trasporto = []
lista_recensioni = []

voli_counter = 0
recensioni_counter = 0
counter_descrizioni = 0
tmp_pacchetti = lista_pacchetti

for j in range(0,n_acquisti):
    tmp_pacchetti = FiltraPacchetti(tmp_pacchetti)

    try:
        target = random.choice(tmp_pacchetti)
        vittima = random.choice(FiltraClienti(lista_clienti,target,lista_prenotazioni))

        ##### VOLI
        lista_aeroporti, partenza_aeroporto = CercaAeroporto(lista_aeroporti, CittàRandom(lista_città, target.idCittàAlloggio).id)
        lista_aeroporti, arrivo_aeroporto = CercaAeroporto(lista_aeroporti, target.idCittàAlloggio)
    except Exception as e:
        print("ERRORE skip creazione acquisto\n", str(e))
        continue
    

    target.disponibilità_exec -= 1
    t_partenza = datetime.combine(target.dataPartenza, fake.time_object())
    delta = timedelta(hours=random.randint(1,10))
    t_arrivo = t_partenza + delta

    bagagli = random.choice(lista_bagagli).id

    volo_andata = Volo(
            voli_counter,
            random.choice(lista_compagnie).email,
            partenza_aeroporto.codice,
            arrivo_aeroporto.codice,
            t_partenza,
            t_arrivo,
            bagagli
        )

    voli_counter += 1
    lista_voli_partenza.append(volo_andata)

    t_partenza = datetime.combine(target.dataRitorno, fake.time_object())
    t_arrivo = t_partenza + delta

    volo_ritorno = Volo(
            voli_counter,
            random.choice(lista_compagnie).email,
            arrivo_aeroporto.codice,
            partenza_aeroporto.codice,
            t_partenza,
            t_arrivo,
            bagagli,
            volo_andata.prezzo,
            volo_andata.tipologia
        )

    voli_counter += 1
    lista_voli_ritorno.append(volo_ritorno)

    ### ACQUISTO
    tran = Transazione(
        0,
        datetime.combine(target.dataPartenza, fake.time_object()) - timedelta(days=random.randint(8,31)),
    )

    pren = Prenotazione(tran.codice, vittima, target.numeroPersone, target.id, target.dataPartenza, target.dataRitorno)
    lista_prenotazioni.append(pren)

    tran.importo = round((volo_andata.prezzo + volo_ritorno.prezzo + target.prezzo) * pren.numero_persone,2)
    lista_transizioni.append(tran)

    ### Informazioni trasporto
    info_trasp = InformazioniTrasporto(tran.codice, [volo_andata, volo_ritorno], pren.numero_persone)
    lista_info_trasporto.append(info_trasp)

    ### Tratte
    lista_tratte.append(
        TrattaVolo(
            tran.codice,
            volo_andata.codice,
            "andata"
        )
    )

    lista_tratte.append(
        TrattaVolo(
            tran.codice,
            volo_ritorno.codice,
            "ritorno"
        )
    )

    ## Recensione
    if (random.uniform(0,100) <= 60):
        lista_recensioni.append(
            Recensione(
                recensioni_counter,
                vittima.email,
                target.dataRitorno,
                target.idCittàAlloggio,
                target.nomeAlloggio,
                TrovaAlloggio(lista_alloggi,target.idCittàAlloggio).valore_atteso
            )
        )

        recensioni_counter += 1


    ### Relaizione
    n_acquisti = n_acquisti-1

## Scrittura
print("Scrittura di tutti i dati generati...")
for x in lista_clienti:
    sqlFile.write(str(x))

for x in lista_compagnie:
    sqlFile.write(str(x))

for x in lista_bagagli:
    sqlFile.write(str(x))

for x in lista_città:
    sqlFile.write(str(x))

for x in lista_agenzie:
    sqlFile.write(str(x))

for x in lista_polizze:
    sqlFile.write(str(x))

for x in lista_descrizioni:
    sqlFile.write(str(x))

for x in lista_alloggi:
    sqlFile.write(str(x))

for x in lista_pacchetti:
    sqlFile.write(str(x))

for x in lista_aeroporti:
    sqlFile.write(str(x))

for x in lista_voli_partenza:
    sqlFile.write(str(x))

for x in lista_voli_ritorno:
    sqlFile.write(str(x))

for x in lista_transizioni:
    sqlFile.write(str(x))

for x in lista_prenotazioni:
    sqlFile.write(str(x))

for x in lista_info_trasporto:
    sqlFile.write(str(x))

for x in lista_tratte:
    sqlFile.write(str(x))

for x in lista_recensioni:
    sqlFile.write(str(x))

# Termina il lavoro
print("Lavoro terminato! :D")
sqlFile.close()