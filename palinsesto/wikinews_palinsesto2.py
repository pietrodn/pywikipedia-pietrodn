#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, re, codecs

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
            
    templateFile = codecs.open("modello_palinsesto2.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    pags = {
        'rai1': 'Rai 1',
        'rai2': 'Rai 2',
        'rai3': 'Rai 3',
        'rete4': 'Rete 4',
        'can5': 'Canale 5',
        'ita1': 'Italia 1',
        'la7': 'La7',
        'mtv': 'MTV',
        'retea': 'All Music',
    }
    pagineHtml = {}
    elencoSostituzioni = {}
    urlBase = 'http://tv.lospettacolo.it/canale.asp?miopar=%s_0'
    for i in pags:
        urlo = urlBase % i
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
                
        elencoSostituzioni['#programmi'] = getProgramList(pagineHtml[i])
        elencoSostituzioni['#rete'] = pags[i]
        newtext = massiveReplace(elencoSostituzioni, modelloVoce)
        
        page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Template:ProgrammiTV/" + pags[i])
        wikipedia.output(">>>>> " + page.title() + " <<<<<")
        if page.exists():
            oldtext = page.get()
        else:
            oldtext = ""
        wikipedia.showDiff(oldtext, newtext)
        if not all:
            choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
        else:
            choice = 'y'
        if choice in ['A', 'a']:
            all = True
            choice = 'y'
        if choice in ['Y', 'y']:
            page.put(newtext, u"Bot: Aggiorno palinsesto TV")
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Template:ProgrammiTV")
    wikipedia.output(">>>>> " + page.title() + " <<<<<")
    oldtext = page.get()
    newtext = re.sub("<!-- @@BOT_DATE_BEGIN@@ -->.*?<!-- @@BOT_DATE_END@@ -->", "<!-- @@BOT_DATE_BEGIN@@ -->{{subst:#time:H:i, l j F Y|{{subst:LOCALTIMESTAMP}}}}<!-- @@BOT_DATE_END@@ -->", oldtext)
    wikipedia.showDiff(oldtext, newtext)
    if not all:
        choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
    else:
        choice = 'y'
    if choice in ['A', 'a']:
        all = True
        choice = 'y'
    if choice in ['Y', 'y']:
        page.put(newtext, u"Bot: Aggiorno palinsesto TV")
            
def massiveReplace(dict, text):
    # Dato un testo ed un dizionario di sostituzioni, usa la funzione string.replace per il "find and replace"
    for k in dict:
        text = text.replace(k, dict[k])
    return text

def getProgramList(htmlText):
    rawList = re.findall("<p class='cellatv'>\s*h: <b>(\d+:\d+)</b>\s*-\s*(.*?) <b>(<[Aa].*?>)?(.*?)(</[Aa]>)?</b><br />(.*?)(<br>)?\s*</p>", htmlText)
    programList = u''
    for i in rawList:
        programList += '|- style="{{ColoriTV|' + unicode(i[1], 'latin-1') + '}}" |\n|' + unicode(i[0], 'latin-1') + '\n| style="font-size:smaller;" |' + unicode(i[1], 'latin-1') + '\n|' + unicode(i[3], 'latin-1')
        if i[5]!='':
            programList += '<br /><small>' + unicode(i[5], 'latin-1') + '</small>'
        programList += '\n'
    
    return programList
    
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
