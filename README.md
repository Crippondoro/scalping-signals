0) Si consiglia di avere installato Visual Studio Code per poter modificare a piacimento alcuni parametri.
   Bisogna avere installato Python.
   Bisogna installare le seguenti librerie tramite CMD:
       - pip install yfinance
       - pip install tk (se non già installato con python)
   Il programma è impostato per movimenti favorevoli con almeno 2 volte lo spread per avere più margine (righe 60 e 62 del codice). E' possibile aumentarlo o diminuirlo a 1 dal codice.
2) Vai su Yahoo Finance e cerca ciò che vuoi monitorare, stock o commodities. Prendi il simbolo, per esempio per Natgas è NG=F, per il Brent è BZ=F, per Bitcoin is BTC-USD etc...
   Il prezzo potrebbe variare leggermente dalla vostra piattaforma ma i movimenti sono gli stessi.
4) Clicca su aggiungi e inserisci il simbolo
5) inserisci lo spread di piattaforma che utilizzi
6) clicca su Show
7) il programma aggiorna il prezzo e i dati ogni 10 secondi. Può essere più lento a seconda della connessione

___________________________________________________________

Zip con exe scaricabile da qui:

https://drive.google.com/file/d/1gAH5qFCGeyHF3i_U-ibM-MlCfYtIS84M/view?usp=sharing

1) estrarre lo zip
2) lanciare l'exe dalla sottocartella "dist"

___________________________________________________________

!!!! AGGIORNAMENTO V10  !!!!

Introdotti nuovi indicatori e aggiustati quelli esistenti:
- EMA (5)
- EMA (40)
- RSI (5)
- RSI (20)
- STOCASTICO

Introdotta la possibilità di caricare un file di testo con assets e spread per evitare di doverli aprire manualmente uno alla volta, vedi file asset.txt

___________________________________________________________

!!!! VARIANTE BOT TELEGRAM !!!!

La base è uguale al V10.
Con questa variante è possibile ricevere aggiornamenti su Telegram quando lo stato degli assets monitorati cambia da NEUTRAL a BUY o SELL. In questo modo se non siete davanti al pc per qualsiasi motivo potete comunque rimanere aggiornati.

1) per creare il proprio telegram Bot ci vogliono 5 minuti.
2) apri Telegram e cerca BotFather con la lente d'ingrandimento.
3) apri la chat con BotFather e digita /newbot. Dai un nome al bot. Fatto questo ti darà un codice token univoco per il tuo bot. Salvalo da qualche parte. Sarà il YUOR_TELEGRAM_BOT_TOKEN.
4) Ora ti serve il YOUR_CHAT_ID. Per ottenerlo manda un messaggio nella chat del tuo BOT.
5) Fatto questo vai al seguente indirizzo per recuperare l'ID:
https://api.telegram.org/bot<YUOR_TELEGRAM_BOT_TOKEN>/getUpdates
6) nella pagina che visualizzerete ci sarà una voce ID composto da diversi numeri. Salvate il codice insieme al token id.
7) Apri il codice in Visual Studio Code o con il blocco note e sostituisci i due codici all'interno del codice alle voci YUOR_TELEGRAM_BOT_TOKEN e YOUR_CHAT_ID
8) Se non l'hai ancora fatto installa le librerie necessarie per avviare il programma:
   - pip install yfinance
   - pip install python-telegram-bot
9) Al momento dell'avvio del programma riceverai un messaggio su telegram: SCALPING SIGNAL PROGRAM AVVIATO
10) Ora carica dal txt o manualmente gli asset che vuoi seguire. Quando passeranno di stato da NEUTRAL a BUY o SELL riceverai un messaggio sulla chat del bot come questo:

Status changed: NEUTRAL -> SELL

Asset: ETH-USD
Spread: 0.0001
Price: 2493.4641
EMA(5): 2492.993
Median Bollinger: 2490.707
EMA(40): 2490.422
RSI(5) 70/30: 64.559
RSI(20) 70/30: 58.489
Stochastic (K/D) 80/20: 56.121 / 48.650
Update Time: 2024-02-10 16:00:36

Sono solo indicazioni per individuare un possibile punto per lo scalping. Apri il grafico e valuta comunque la situazione.

________________________________________________________

DISCLAIMER: IL PROGRAMMA DOVREBBE FORNIRE UTILI INDICAZIONI DI ACQUISTO / VENDITA MA NON GARANTISCE IL SUCCESSO DELL'OPERAZIONE.
