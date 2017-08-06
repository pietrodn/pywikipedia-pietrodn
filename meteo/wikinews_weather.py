#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import wikipedia
import urllib2, datetime, re, time

def pageText(url):
    request = urllib2.Request(url)
    user_agent = 'BimBot/1.0'
    request.add_header("User-Agent", user_agent)
    response = urllib2.urlopen(request)
    text = response.read()
    response.close()
    return text
 
def main():
    pagesDict = {'Template:Weather_World_C/Auto': "http://tools.wikimedia.de/~skenmy/wnweather/overlays/%d%b%y-%H-C-world",
                'Template:Weather_World_F/Auto': "http://tools.wikimedia.de/~skenmy/wnweather/overlays/%d%b%y-%H-F-world",
    }
    args = wikipedia.handleArgs()
    all = False
    for currentArgument in args:
        if currentArgument.startswith("-always"):
            all = True
    
    for pageName in pagesDict:
        formatUrl = pagesDict[pageName]
        now = datetime.datetime.utcnow()
        urlo = now.strftime(formatUrl)
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
                
        htmlText = re.sub("Wikinews Weather Service", "Servizio Meteo di Wikinotizie", htmlText)
        htmlText = re.sub("World Map", r"Mondo", htmlText)
        htmlText = re.sub("''\d{2}:\d{2} UTC .*? .*? .*?''</span>", "''{{subst:LOCALDAY}} {{subst:LOCALMONTHNAME}} {{subst:LOCALYEAR}}, {{subst:LOCALHOUR}}:00 [[w:CET|<span style=\"color:white; text-decoration:underline;\">CET</span>]] ({{subst:CURRENTHOUR}}:00 [[w:UTC|<span style=\"color:white; text-decoration:underline;\">UTC</span>]])''</span>", htmlText)
         
        page = wikipedia.Page(wikipedia.getSite(code='it', fam='wikinews'), pageName)
        if page.exists():
            oldtext = page.get()
        else:
            oldtext = ""
        wikipedia.showDiff(oldtext, htmlText)
        
        if not all:
            choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
        else:
            choice = 'y'
        if choice in ['A', 'a']:
            all = True
            choice = 'y'
        if choice in ['Y', 'y']:
            page.put(htmlText, u"Bot: Aggiorno il meteo")
 
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
