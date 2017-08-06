#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Aggiorna gli elenchi offline di it.wikibooks"""

import re, wikipedia, catlib, MySQLdb

def main():
    args = wikipedia.handleArgs()
    serialBegin = 1 # Da dove deve cominciare? default=1
    all = False
    database = 'itwikibooks_p';
    for currentArgument in args:
        if currentArgument.startswith("-db:"):
            database = currentArgument[4:] # Se l'utente dice da dove deve cominciare, lo memorizza
        if currentArgument.startswith("-always"):
            all = True

    cat_elenchi = catlib.Category(wikipedia.getSite(code='it', fam='wikibooks'), "Categoria:Elenchi generati offline")
    queryreg = re.compile("\|query\s*=\s*<source lang=\"sql\">(.*?)</source>", re.DOTALL)
    elencoreg = re.compile("\|\s*elenco\s*=\s*(.*?)\s*\}\}", re.DOTALL)
    datareg = re.compile("\|\s*data\s*=\s*(.*)")
    db = MySQLdb.connect(host='localhost', user='DumpBot', passwd='', db=database)
    db.set_character_set('utf8')

    for i in cat_elenchi.articles():
        wikipedia.output(">>>>> " + i.title() + " <<<<<")
        oldtxt = i.get()

        match = re.search(queryreg, oldtxt)
        if not match or match.lastindex < 1:
        	continue
        query = match.group(1)
        wikipedia.output(query)

        if not all:
            choice = wikipedia.inputChoice(u"Procedo?",  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
        else:
            choice = 'y'
        if choice in ['A', 'a']:
            all = True
            choice = 'y'
        if choice in ['Y', 'y']:
            cur = db.cursor()
            cur.execute(query)
            results = cur.fetchall()
            cur.close()

            nuovoelenco = ''
            for j in results:
                nuovoelenco = nuovoelenco + j[0] + '\n'

            nuovoelenco = nuovoelenco.decode('utf-8')
            #wikipedia.output(nuovoelenco)
            newtxt = re.sub(elencoreg, u"|elenco=\n" + nuovoelenco + u"\n}}", oldtxt)

            newtxt = re.sub(datareg, u"|data={{subst:CURRENTDAY}} {{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}", newtxt)
            wikipedia.showDiff(oldtxt, newtxt)
            wikipedia.setAction(u'Aggiorno elenco')
            i.put_async(newtxt)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
