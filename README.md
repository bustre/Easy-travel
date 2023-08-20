# Progetto basi di dati

## Branch
- relazione: dedicato a tutte le attività strettamente correlate con la stesura della relazione
- software: dedicato allo sviluppo del programma
- main: per il merge degli stage più importanti del progetto

## Comandi principali (git)
- ### Prima di ogni attività sincronizzarsi
    git pull origin main software relazione
- ### Selezionare il branch (attenzione non bisogna avere file in attesa del commit)
    git checkout \<nomeramo\>
- ### Push delle attività al repo
    git push origin main software relazione

## Stato attività
- ### Abstract
    - [x] Abstract
- ### Analisi requisiti
    - [x] Descrizione
    - [x] Dizionario termini
    - [x] N° Operazioni
- ### Progettazione concettuale
    - [] ER concettuale
    - [] Tabella entità
    - [] Tabella relazioni
- ### Progettazione logica
    - [] Analisi
    - [] ER logico (o ristrutturato)
    - [] Schema relazionale + vincoli esprimibili
    - [] Regole aziendali
- ### Requisiti progetto
    - [] Implementazione DB
    - [] Inserire dati (generare la maggior parte con faker + cvs import)
    - [] Querry SQL
    - [] Indice
    - [] Software C++
- ### Cose in più (se possibile)
    - [] Transizioni 
    - [] Trigger
