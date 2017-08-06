#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, datetime, re, time, codecs

mesi = {'gennaio':  '01',
        'febbraio': '02',
        'marzo':    '03',
        'aprile':   '04',
        'maggio':   '05',
        'giugno':   '06',
        'luglio':   '07',
        'agosto':   '08',
        'settembre':'09',
        'ottobre':  '10',
        'novembre': '11',
        'dicembre': '12',
}

def pageText(url):
    request = urllib2.Request(url)
    user_agent = 'BimBot/1.0'
    request.add_header("User-Agent", user_agent)
    response = urllib2.urlopen(request)
    text = response.read()
    response.close()
    return text
 
def main():
    args = wikipedia.handleArgs()
    all = False
    force = False
    for currentArgument in args:
        if currentArgument.startswith("-always"):
            all = True
        if currentArgument.startswith("-force"):
            force = True
            
    templateFile = codecs.open("modello_lotto.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    urlo = "http://www.lottomaticaitalia.it/lotto/estrazioni/estrazioni_ultime.do"
    wikipedia.output(u'Prendo la pagina dal server...')
    try:
        htmlText = pageText(urlo)
    except urllib2.HTTPError:
        try:
            wikipedia.output(u"Errore del server. Aspetto 10 secondi... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
            time.sleep(10)
            htmlText = pageText(urlo)
        except urllib2.HTTPError:
            wikipedia.output(u"Errore del server. Chiudo.")
            return
    htmlText = htmlText.decode('utf-8')
    bloccoTipo = '<tr[^>]*>\s*<td[^>]*>\s*%s\s*</td>\s*<td[^>]*>\s*(\d{1,2})\s*</td>\s*<td[^>]*>\s*(\d{1,2})\s*</td>\s*<td[^>]*>\s*(\d{1,2})\s*</td>\s*<td[^>]*>\s*(\d{1,2})\s*</td>\s*<td[^>]*>\s*(\d{1,2})\s*</td>\s*</tr>'
    data = re.search('<h4>ESTRAZIONE - \s*(.*?) (\d{1,2}) (.*?) (\d+)\s*</h4>', htmlText)
    nazionale = re.search(bloccoTipo % 'Nazionale', htmlText)
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Estrazione del Lotto, " + data.group(1) + " " + str(int(data.group(2))) + " " + data.group(3) + " " + data.group(4))
    if page.exists() and not force:
        wikipedia.output("Nessuna nuova estrazione. Mi fermo.")
        return
        
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#dow': data.group(1),
        '#giorno': data.group(2),
        '#nomemese': data.group(3),
        '#mese': mesi[data.group(3)],
        '#anno': data.group(4),
        
        '#nazionale-1': nazionale.group(1),
        '#nazionale-2': nazionale.group(2),
        '#nazionale-3': nazionale.group(3),
        '#nazionale-4': nazionale.group(4),
        '#nazionale-5': nazionale.group(5),

    }
    
    cities = ['Bari', 'Cagliari', 'Firenze', 'Genova', 'Milano', 'Napoli', 'Palermo', 'Roma', 'Torino', 'Venezia']
    for c in cities:
        match = re.search(bloccoTipo % c, htmlText)
        for i in range(1,6):
            elencoSostituzioni['#' + c.lower() + '-' + str(i)] = match.group(i)
            
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    #nuovoTesto = re.sub('\|- - - -', '|N.D.', nuovoTesto) # Per quando i dati non sono disponibili
    
    #page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Utente:BimBot/Sandbox")
    wikipedia.output(">>>>> " + page.title() + " <<<<<")
    try:
        vecchioTesto = page.get()
    except wikipedia.NoPage:
        vecchioTesto = ''
    wikipedia.showDiff(vecchioTesto, nuovoTesto)
    if not all:
        choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
    else:
        choice = 'y'
    if choice in ['A', 'a']:
        all = True
        choice = 'y'
    if choice in ['Y', 'y']:
        page.put(nuovoTesto, u"Bot: Inserisco nuova estrazione del Lotto")

def massiveReplace(dict, text):
    # Dato un testo ed un dizionario di sostituzioni, usa le regex per il "find and replace"
    for k in dict:
        text = re.sub(k, dict[k], text)
    return text

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
