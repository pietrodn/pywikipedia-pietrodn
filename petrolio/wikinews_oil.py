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
            
    templateFile = codecs.open("modello_wikinews_oil.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    urlo = "http://www.nymex.com/index.aspx"
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
    
    prezzoCL = re.search("<span id=\"LastCL\".*?>(.*?)</span>", htmlText).group(1)
    changeCL = re.search("<span id=\"ChangeCL\".*?>(<font.*?>)?(.*?)(</font>)?</span>", htmlText).group(2)
    
    prezzoBZ = re.search("<span id=\"LastBZ\".*?>(.*?)</span>", htmlText).group(1)
    changeBZ = re.search("<span id=\"ChangeBZ\".*?>(<font.*?>)?(.*?)(</font>)?</span>", htmlText).group(2)
    
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#CL_curr': prezzoCL,
        '#CL_diff': changeCL,
                
        '#BZ_curr': prezzoBZ,
        '#BZ_diff': changeBZ,
    }
    
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    #nuovoTesto = re.sub('\|- - - -', '|N.D.', nuovoTesto) # Per quando i dati non sono disponibili
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Template:Dati petrolio/Auto")
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
        page.put(nuovoTesto, u"Bot: Aggiorno prezzi petrolio")

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
