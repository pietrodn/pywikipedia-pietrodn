#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, wikipedia
import pagegenerators
from add_text import add_text

def main():
    args = wikipedia.handleArgs()
    all = False
    genFactory = pagegenerators.GeneratorFactory()
    
    for currentArgument in args:   
        if currentArgument.startswith("-always"):
            all = True
        else:
            generator = genFactory.handleArg(currentArgument)
              
    # Check if pages on which the bot should work are specified.
    if not generator:
        raise NoEnoughData('You have to specify which pages the script has to work on!')
    
    # Main Loop
    for i in generator:
        attenzioneIo = False # Dubbio su "I", che può essere articolo determinativo italiano o pronome personale inglese
        titolo = i.title()
        wikipedia.output(">>>>> " + titolo + " <<<<<")
          
        nuovoTitolo = re.sub("^(The |A |An |Il |Lo |La |I |Gli |Le |L'|Uno |Una |Un'|Un )([A-Z0-9].*)", r"{{DEFAULTSORT:\2, \1}}", titolo)
        if titolo == nuovoTitolo:
            wikipedia.output("Non c'è nessun articolo. Prossima pagina...")
            continue
        
        if re.search("^I ", titolo):
            attenzioneIo = True
                
        nuovoTitolo = re.sub("[ ']\}\}", "}}", nuovoTitolo) # Toglie spazi, apostrofi...
        
        try:
            oldtext = i.get()
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"%s is a redirect, I'll ignore it." % i.title())
            continue
        
        if re.search("\{\{DEFAULTSORT:", oldtext):
            wikipedia.output("C'è già un DEFAULTSORT. Prossima pagina...")
            continue
            
        newtext = add_text(page = i, addText = nuovoTitolo, putText = False, oldTextGiven = oldtext)[1]
        wikipedia.showDiff(oldtext, newtext)
        if not all or attenzioneIo:
            choice = wikipedia.inputChoice(u"Modificare?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
        else:
            choice = 'y'
        if choice in ['A', 'a']:
            all = True
            choice = 'y'
        if choice in ['Y', 'y']:
            i.put_async(newtext, comment="Aggiungo: " + nuovoTitolo)    
        
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()