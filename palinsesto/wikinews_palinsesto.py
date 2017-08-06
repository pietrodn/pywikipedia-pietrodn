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
            
    templateFile = codecs.open("modello_palinsesto.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    fasceOrarie = ['mattina', 'pomeriggio', 'sera']
    pagineHtml = {}
    elencoSostituzioni = {}
    urlBase = "http://city.corriere.it/tv/tv.php?fascia="
    for i in fasceOrarie:
        urlo = urlBase + i
        print urlo
        wikipedia.output(u'Prendo la pagina dal server...')
        try:
            pagineHtml[i] = pageText(urlo)
        except urllib2.HTTPError:
            try:
                wikipedia.output(u"Errore del server. Aspetto 10 secondi... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
                time.sleep(10)
                pagineHtml[i] = pageText(urlo)
            except urllib2.HTTPError:
                wikipedia.output(u"Errore del server. Chiudo.")
                return
                
        elencoSostituzioni['#rai1-' + i] = getProgramList('RAI 1', pagineHtml[i])
        elencoSostituzioni['#rai2-' + i] = getProgramList('RAI 2', pagineHtml[i])
        elencoSostituzioni['#rai3-' + i] = getProgramList('RAI 3', pagineHtml[i])
        elencoSostituzioni['#rete4-' + i] = getProgramList('RETE 4', pagineHtml[i])
        elencoSostituzioni['#canale5-' + i] = getProgramList('CANALE 5', pagineHtml[i])
        elencoSostituzioni['#italia1-' + i] = getProgramList('ITALIA 1', pagineHtml[i])
        elencoSostituzioni['#la7-' + i] = getProgramList('LA7', pagineHtml[i])
    
    
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Template:ProgrammiTV")
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
        page.put(nuovoTesto, u"Bot: Aggiorno palinsesto TV")

def massiveReplace(dict, text):
    # Dato un testo ed un dizionario di sostituzioni, usa le regex per il "find and replace"
    for k in dict:
        text = text.replace(k, dict[k])
    return text

def getProgramList(chan, htmlText):
    chanMatch = re.search('(?s)<td class="shadow-tl".*?>\s*' + chan + '.*?<div class="programmi_dati">\s*(.*?)\s*</td>', htmlText)
    rawHtml = chanMatch.group(1)
    rawList = re.findall('<strong>\s*(\d+:\d+)\s*</strong>\s*(.*?)\s*<br />', rawHtml)
    programList = u''
    for i in rawList:
        programList = programList + '|-\n|' + unicode(i[0], 'latin-1') + '\n|' + unicode(i[1], 'latin-1') + '\n'
    return programList
    
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
