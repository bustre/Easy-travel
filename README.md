# Progetto basi di dati

## Link veloci
- [Relazione](relazione/relazione.pdf)

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
    - [-] N° Operazioni; se viene in mente altro aggiugnere
- ### Progettazione concettuale
    - [x] ER concettuale
    - [x] Tabella entità
    - [x] Tabella relazioni
- ### Progettazione logica
    - [x] Analisi
    - [x] ER logico (o ristrutturato)
    - [x] Schema relazionale + vincoli esprimibili
    - [x] Regole aziendali
- ### Requisiti progetto
    - [x] Implementazione DB
    - [x] Inserire dati (generare la maggior parte con faker + cvs import)
    - [x] Querry SQL
    - [x] Indice
    - [x] Software C++
- ### Cose in più (se possibile)
    - [] Transizioni 
    - [] Trigger

#### Problemi
    - Provare a usare immagini SVG