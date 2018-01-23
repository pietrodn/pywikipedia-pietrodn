#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, datetime, re, codecs
import time

codiciStazioni = [
    'LIMG',
    'LIEA',
    'LIBA',
    'LIQB',
    'LIPA',
    'LIBD',
    'LIPB',
    'LIBW',
    'LIPE',
    'LIPL',
    'LIMK',
    'LIBR',
    'LIEE',
    'LIMN',
    'LIBS',
    'LIEB',
    'LIEC',
    'LIEF',
    'LIMU',
    'LIQK',
    'LICC',
    'LICZ',
    'LIPC',
    'LIQJ',
    'LICO',
    'LIBC',
    'LIED',
    'LIVD',
    'LIRX',
    'LICE',
    'LIPY',
    'LIPF',
    'LIRQ',
    'LIEN',
    'LIPK',
    'LIVF',
    'LIRH',
    'LICL',
    'LIMJ',
    'LIBV',
    'LIMQ',
    'LIRM',
    'LIRS',
    'LIBG',
    'LIRG',
    'LIQC',
    'LICD',
    'LIRL',
    'LIBU',
    'LIBN',
    'LIMZ',
    'LIBH',
    'LICF',
    'LIML',
    'LIMC',
    'LIMY',
    'LIQO',
    'LIBE',
    'LIBQ',
    'LIRK',
    'LIRN',
    'LIEO',
    'LIME',
    'LIVP',
    'LICP',
    'LICJ',
    'LICG',
    'LIMP',
    'LIMV',
    'LIMT',
    'LIVR',
    'LIRZ',
    'LIBP',
    'LIMS',
    'LIRP',
    'LIQZ',
    'LIBZ',
    'LIRE',
    'LICX',
    'LIQR',
    'LICR',
    'LIPR',
    'LIRA',
    'LIRF',
    'LIRU',
    'LIPQ',
    'LIBY',
    'LIVE',
    'LIQW',
    'LIVO',
    'LIBT',
    'LIMF',
    'LICT',
    'LIRT',
    'LIPS',
    'LIPH',
    'LIVT',
    'LIPI',
    'LICU',
    'LIPZ',
    'LIPX',
    'LIPT',
    'LIRB',
    'LIRV',
    'LIMH',
]

nd = "n.d."

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
            
    templateFile = codecs.open("modello_meteo.txt", "r", "utf-8")
    modelloVoce = templateFile.read() # Legge il modello della pagina
    templateFile.close()
    
    urlo = "http://www.meteoam.it/modules/tempoInAtto/infoStazione.php?icao=%s"
    replacements = {}
    for i in codiciStazioni:
        try:
            htmlText = pageText(urlo % i)
        except urllib2.HTTPError:
            try:
                wikipedia.output(u"Errore del server. Aspetto 10 secondi... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
                time.sleep(10)
                htmlText = pageText(urlo)
            except urllib2.HTTPError:
                wikipedia.output(u"Errore del server. Chiudo.")
                return
        match = re.search('<div class="titolo">Informazioni meteorologiche/climatologiche per (.*?)</div>', htmlText)
        nomeLocalita = unicode(match.group(1))
        wikipedia.output(nomeLocalita + " (" + i + ")")
        nuvoloMatch = re.search(u'<b>Nuvolosità</b></font></td>\s*<td.*?>\s*.*?\s*</td>\s*<td .*?>\s*<p .*?><img .*? alt\s*="(.*?)" .*?>\s*</td>', htmlText)
        ventoMatch = re.search(u'<b>Vento</b></font></td>\s*<td.*?>\s*.*?\s*</td>\s*<td .*?>\s*<p .*?><img .*? alt\s*="Vento (.*?)( Direzione (.*?))?" .*?>\s*</td>', htmlText)
        maxMatch = re.search(u'<td .*?>\s*<font .*?><b>Temperatura</b></font>\s*<p><font .*?><b>&nbsp;Max</b></font></td>\s*<td.*?>\s*.*?\s*</td>\s*<td .*?><b>\s*<font .*?>([+-]?\s*\d+)</font></b></td>', htmlText)
        minMatch = re.search(u'<td .*?>\s*<font .*?><b>Temperatura</b></font>\s*<p><font .*?><b>&nbsp;Min</b></font></td>\s*<td.*?>\s*.*?\s*</td>\s*<td .*?><b>\s*<font .*?>([+-]?\s*\d+)</font></b></td>', htmlText)
        if nuvoloMatch!=None:
            replacements['#tempo-' + nomeLocalita + '#'] = iconaTempo(nuvoloMatch.group(1))
        else:
            replacements['#tempo-' + nomeLocalita + '#'] = nd
        if ventoMatch!=None:
            replacements['#intensita-' + nomeLocalita + '#'] = ventoMatch.group(1)
            if ventoMatch.group(2)!=None:
                replacements['#vento-' + nomeLocalita + '#'] = ventoMatch.group(3)
            elif ventoMatch.group(2)==None and ventoMatch.group(1)=="variabile":
                replacements['#vento-' + nomeLocalita + '#'] = "variabile"
                replacements['#intensita-' + nomeLocalita + '#'] = "debole"
            else:
                replacements['#vento-' + nomeLocalita + '#'] = nd
        else:
            replacements['#vento-' + nomeLocalita + '#'] = nd
            replacements['#intensita-' + nomeLocalita + '#'] = nd
        if maxMatch!=None:
            replacements['#max-' + nomeLocalita + '#'] = maxMatch.group(1)
        else:
            replacements['#max-' + nomeLocalita + '#'] = nd
        if minMatch!=None:
            replacements['#min-' + nomeLocalita + '#'] = minMatch.group(1)
        else:
            replacements['#min-' + nomeLocalita + '#'] = nd
            
    nuovoTesto = massiveReplace(replacements, modelloVoce)
    
    page = wikipedia.Page(wikipedia.Site('it', 'wikinews'), 'Template:Pagina principale/Secondo piano/Meteo')
    vecchioTesto = page.get()
    wikipedia.showDiff(vecchioTesto, nuovoTesto)
    if not all:
        choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
    else:
        choice = 'y'
    if choice in ['A', 'a']:
        all = True
        choice = 'y'
    if choice in ['Y', 'y']:
        page.put(nuovoTesto, u"Bot: Aggiorno meteo")
        
        
def massiveReplace(dict, text):
    # Dato un testo ed un dizionario di sostituzioni, usa la funzione Python replace per il "find and replace"
    for k in dict:
        text = text.replace(k, dict[k])
    return text

def iconaTempo(stringa):
    if "Cielo sereno" in stringa:
        return "{{Sereno}}"
    elif "Cielo poco nuvoloso" in stringa:
        return "{{PocoNuvoloso}}"
    elif "Cielo nuvoloso" or "Cielo molto nuvoloso" in stringa:
        return "{{Nuvoloso}}"
    else:
        return stringa
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()