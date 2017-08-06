#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, datetime, re, time, codecs

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
    for currentArgument in args:
        if currentArgument.startswith("-always"):
            all = True
            
    templateFile = codecs.open("modello_wikinews_petrol2.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    urlo = "http://www.newstreet.it/prezzi_benzina_gasolio.html"
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
    bloccoTipo = '<td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td></tr>'
    data = re.search('<td.*?><b>Prezzi di riferimento con servizio \(&euro;/litro\) al (.*?)</b></td>', htmlText)
    benzina = re.search('<tr><td.*?><div.*? class="titoliRubriche"><b>Benzina</b></td>' + bloccoTipo, htmlText)
    diesel = re.search('<tr><td.*?><div.*? class="titoliRubriche"><b>Diesel</b></td>' + bloccoTipo, htmlText)
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#data': data.group(1),
        
        '#benzina_Agip': benzina.group(1),
        '#benzina_API': benzina.group(2),
        '#benzina_Erg': benzina.group(3),
        '#benzina_Esso': benzina.group(4),
        '#benzina_Ip': benzina.group(5),
        '#benzina_Q8': benzina.group(6),
        '#benzina_Shell': benzina.group(7),
        '#benzina_Tamoil': benzina.group(8),
        '#benzina_Total': benzina.group(9),

        '#diesel_Agip': diesel.group(1),
        '#diesel_API': diesel.group(2),
        '#diesel_Erg': diesel.group(3),
        '#diesel_Esso': diesel.group(4),
        '#diesel_Ip': diesel.group(5),
        '#diesel_Q8': diesel.group(6),
        '#diesel_Shell': diesel.group(7),
        '#diesel_Tamoil': diesel.group(8),
        '#diesel_Total': diesel.group(9),
    }
    
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    #nuovoTesto = re.sub('\|- - - -', '|N.D.', nuovoTesto) # Per quando i dati non sono disponibili
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Template:Benzina/Auto")
    if page.exists():
        oldtext = page.get()
    else:
        oldtext = ""
    wikipedia.showDiff(oldtext, nuovoTesto)
    if not all:
        choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
    else:
        choice = 'y'
    if choice in ['A', 'a']:
        all = True
        choice = 'y'
    if choice in ['Y', 'y']:
        page.put(nuovoTesto, u"Bot: Aggiorno prezzi benzina")

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
