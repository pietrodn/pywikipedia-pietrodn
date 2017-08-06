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
            
    templateFile = codecs.open("modello_wikinews_petrol.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    urlo = "http://www.prezzibenzina.it/"
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
    bloccoTipo = '<!--.*?--><td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*<td.*?>(.*?)</td>\s*</tr>'
    data = re.search('<th.*?>Indice dei prezzi &euro;/L\. nazionali del (.*?)<br/>', htmlText)
    verde = re.search('<tr><th.*?>Benzina</th>' + bloccoTipo, htmlText)
    diesel = re.search('<tr><th.*?>Diesel</th>' + bloccoTipo, htmlText)
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#data': data.group(1),
        
        '#verde_Agip': verde.group(2),
        '#verde_API': verde.group(3),
        '#verde_Erg': verde.group(4),
        '#verde_Esso': verde.group(5),
        '#verde_Ip': verde.group(6),
        '#verde_Q8': verde.group(7),
        '#verde_Shell': verde.group(8),
        '#verde_Tamoil': verde.group(9),
        '#verde_Total': verde.group(10),
        
        '#diesel_Agip': diesel.group(2),
        '#diesel_API': diesel.group(3),
        '#diesel_Erg': diesel.group(4),
        '#diesel_Esso': diesel.group(5),
        '#diesel_Ip': diesel.group(6),
        '#diesel_Q8': diesel.group(7),
        '#diesel_Shell': diesel.group(8),
        '#diesel_Tamoil': diesel.group(9),
        '#diesel_Total': diesel.group(10),
    }
    
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    nuovoTesto = re.sub('\|- - - -', '|N.D.', nuovoTesto) # Per quando i dati non sono disponibili
    
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
