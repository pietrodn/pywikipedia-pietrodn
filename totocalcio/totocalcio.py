#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, re, time, codecs

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
            
    templateFile = codecs.open("modello_totocalcio.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    urlo = "http://www.calcio.sisal.it/pages/totocalcio/ultimo.xwb"
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
    
    concorso = re.search("<h2>Concorso n. (\d+) di (.*?) (\d+) (.*?) (\d+)</h2>", htmlText)
    montepremi = re.search("<tr>\s*<th[^>]*>Il Montepremi</th>\s*</tr>\s*<tr>\s*<TD[^>]*>\s*Del Concorso \(premi a punteggio\)\s*</TD>\s*<TD>\s*EUR\s*</TD>\s*<TD>\s*(.*?)\s*</TD>\s*</tr>\s*<tr>\s*<TD[^>]*>\s*Riporto Jackpot conc\. precedente\s*</TD>\s*<TD>\s*EUR\s*</TD>\s*<TD[^>]*>\s*(.*?)\s*</TD>\s*</tr>\s*<tr\s*>\s*<TD[^>]*>\s*Montepremi totale del concorso\s*</TD>\s*<TD>\s*EUR\s*</TD>\s*<TD[^>]*>\s*(.*?)\s*</TD>\s*</tr>", htmlText, re.I)
    montepremi9 = re.search("<tr>\s*<th[^>]*>Il Montepremi \"Il9\"</th>\s*</tr>\s*<tr>\s*<TD[^>]*>\s*Del Concorso \(premi a punteggio\)\s*</TD>\s*<TD>\s*EUR\s*</TD>\s*<TD>\s*(.*?)\s*</TD>\s*</tr>\s*<tr>\s*<TD[^>]*>\s*Riporto Jackpot conc\. precedente\s*</TD>\s*<TD>\s*EUR\s*</TD>\s*<TD[^>]*>\s*(.*?)\s*</TD>\s*</tr>\s*<tr>\s*<TD[^>]*>\s*Montepremi totale del concorso 9\s*</TD>\s*<TD>\s*EUR\s*</td>\s*<TD[^>]*>\s*(.*?)\s*</TD>\s*</tr>", htmlText, re.I)
    bloccoQuote = "<tr>\s*<td>\s*(.*?)\s*</td>\s*<td>\"%s\"</td>\s*<td[^>]*>\s*(.*?)\s*</td>\s*</tr>"
    bloccoPartita = "<tr[^>]*>\s*<td[^>]*>\s*<b>\s*%s\s*</b>\s*</td>\s*<td[^>]*>\s*(.*?)\s*</td>\s*<td[^>]*>\s*(.*?)\s*</td>\s*<td[^>]*>\s*<b>\s*(\d+)\s*-\s*(\d+)&nbsp;\s*</b>\s*</td>\s*<td[^>]*>\s*<b>\s*([12X])&nbsp;\s*</b>\s*</td>\s*</tr>"
    jackpotFuturi = re.search("<table.*?>\s*<tr>\s*<th[^>]*>\s*Jackpot prossimo concorso\s*</th>\s*</tr>\s*<tr>\s*<th[^>]*>.*?</th>\s*</tr>\s*<tr>\s*<td[^>]*><h2><b>14</b></h2></td>\s*<td[^>]*><h1>(.*?)<font[^>]*>.*?</font></h1></td>\s*</tr>\s*</table>", htmlText, re.I)
    
    page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), "Italia: concorso n. " + concorso.group(1) + "/" + concorso.group(5) + " del Totocalcio")
    if page.exists() and not force:
        wikipedia.output("Nessuna nuova estrazione. Mi fermo.")
        return
        
    elencoSostituzioni = { # Sostituisce le variabili nel modello
        '#super-id': concorso.group(1),
        '#dow': concorso.group(2).replace('&igrave;', u'ì'),
        '#giorno': concorso.group(3),
        '#mese': concorso.group(4),
        '#anno': concorso.group(5),
        
        '#montepremi-parz': montepremi.group(1),
        '#jackpot': montepremi.group(2),
        '#montepremi-tot': montepremi.group(3),
        
        '#9-montepremi-parz': montepremi9.group(1),
        '#9-jackpot': montepremi9.group(2),
        '#9-montepremi-tot': montepremi9.group(3),
    }
    
    try:
        elencoSostituzioni['#futuro-jackpot'] = jackpotFuturi.group(1)
    except:
        elencoSostituzioni['#futuro-jackpot'] = '-'
        
    try:
        elencoSostituzioni['#9-futuro-jackpot'] = jackpotFuturi.group(2)
    except:
        elencoSostituzioni['#9-futuro-jackpot'] = '-'
        
    partite = range(1, 15)
    for p in partite:
        match = re.search(bloccoPartita % p, htmlText, re.I)
        elencoSostituzioni['#sq-' + str(p) + 'a'] = match.group(1).capitalize()
        elencoSostituzioni['#sq-' + str(p) + 'b'] = match.group(2).capitalize()
        elencoSostituzioni['#res-' + str(p) + 'a'] = match.group(3)
        elencoSostituzioni['#res-' + str(p) + 'b'] = match.group(4)
        elencoSostituzioni['#ok-' + str(p)] = match.group(5)
                
    quotes = [9, 12, 13, 14]
    for c in quotes:
        match = re.search(bloccoQuote % c, htmlText, re.I)
        elencoSostituzioni['#vincitori-' + str(c)] = match.group(1).replace('nessuna', '0')
        elencoSostituzioni['#euro-' + str(c)] = match.group(2).replace('-', '0')
        
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
        page.put(nuovoTesto, u"Bot: Inserisco nuova estrazione del Totocalcio")

def massiveReplace(dict, text):
    # Dato un testo ed un dizionario di sostituzioni, esegue il "find and replace"
    for k in dict:
        text = text.replace(k, dict[k])
    return text

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()