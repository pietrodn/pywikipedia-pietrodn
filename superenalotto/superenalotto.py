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
            
    templateFile = codecs.open("modello_superenalotto.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    now = datetime.datetime.utcnow()
    urlo = "http://www.sisal.it/se/se_main/1,4136,se_Default,00.html"
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
    
    numeri = re.search("<TABLE[^>]*>\s*<tr>\s*<td[^>]*>\s*<a[^>]*><nobr><font[^>]*>\s*(\d+)&nbsp;-&nbsp;\s*(\d+)&nbsp;-&nbsp;\s*(\d+)&nbsp;-&nbsp;\s*(\d+)&nbsp;-&nbsp;\s*(\d+)&nbsp;-&nbsp;\s*(\d+)\s*</font>\s*</nobr>\s*</a>\s*</td>\s*</tr>\s*</table>", htmlText)
    jolly = re.search("<td[^>]*background=\"/giochi/se2006/hp2009/img/BTN_JOLLY.gif\"[^>]*>\s*<a[^>]*><font[^>]*><b>(\d+)</b></font></a>\s*</td>", htmlText)
    superstar = re.search("<td[^>]*background=\"/giochi/se2006/hp2009/img/BTN_SUPERSTAR.gif\"[^>]*>\s*<a[^>]*><font[^>]*><b>(\d+)</b></font></a>\s*</td>", htmlText)
    concorso = re.search("<font[^>]*><font[^>]*><b>Concorso n. (\d+) di (.*?) (\d+)/(\d+)/(\d+)</b></font></a>", htmlText)
    montepremiparz = re.search("<td><a[^>]*><font class=testo8[^>]*>Del Concorso</a></td>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*>(.*?) euro</font></a></td>", htmlText)
    jackpot = re.search("<td><a[^>]*><font class=testo8[^>]*>\s*Riporto Jackpot</a>\s*</td>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*>(.*?) euro</font></a></td>", htmlText)
    montepremitot = re.search("<td><a[^>]*><font class=testo8[^>]*><b>Totale</a></td>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*><b>(.*?) euro</font></a></td>", htmlText)
    bloccoQuote = "<tr[^>]*>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*>(.*?)</font></a></td>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*>&quot;%s&quot;</a></td>\s*<td[^>]*><a[^>]*><font class=testo8[^>]*>(.*?)</font></a></td>\s*</tr>"
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Italia: concorso n. " + concorso.group(1) + "/" + concorso.group(5) + " del SuperEnalotto")
    if page.exists() and not force:
        wikipedia.output("Nessuna nuova estrazione. Mi fermo.")
        return
        
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#super-id': concorso.group(1),
        '#dow': concorso.group(2).replace('&igrave;', u'ì'),
        '#giorno': concorso.group(3),
        '#mese': concorso.group(4),
        '#anno': concorso.group(5),
        
        '#num-1': numeri.group(1),
        '#num-2': numeri.group(2),
        '#num-3': numeri.group(3),
        '#num-4': numeri.group(4),
        '#num-5': numeri.group(5),
        '#num-6': numeri.group(6),
        '#num-jolly': jolly.group(1),
        '#num-superstar': superstar.group(1),
        
        '#montepremi-parz': montepremiparz.group(1),
        '#jackpot': jackpot.group(1),
        '#montepremi-tot': montepremitot.group(1),

    }
    
    quotes = ['punti 6', 'punti 5\+', 'punti 5', 'punti 4', 'punti 3', '5 stella', '4 stella', '3 stella', '2 stella', '1 stella', '0 stella']
    for c in quotes:
        match = re.search(bloccoQuote % c, htmlText)
        elencoSostituzioni['#' + c.lower().replace(' ', '-') + '#'] = match.group(2).replace('nessuna', '0')
        elencoSostituzioni['#vincitori-' + c.lower().replace(' ', '-') + '#'] = match.group(1).replace('nessuna', '0')
    
    nuovoTesto = massiveReplace(elencoSostituzioni, modelloVoce)
    
    #page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Utente:BimBot/Sandbox") #DEBUG
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
        page.put(nuovoTesto, u"Bot: Inserisco nuova estrazione del SuperEnalotto")

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
