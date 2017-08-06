#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Lo script prende le immagini di WikiLovesMonuments
# specificate in una data categoria di Wikimedia Commons
# (passata da riga di comando) e le salva raggruppate per monumento.
# Le cartelle create hanno come nome l'ID del monumento.
#
# Esempio:
# python scarica_monumenti.py -cat:"Images_from_Wiki_Loves_Monuments_2012_in_Italy" -path:"~/Downloads/WLM"
#
# Altro esempio: scorro la categoria a partire dalla lettera "D".
# python scarica_monumenti.py -cat:"Images_from_Wiki_Loves_Monuments_2012_in_Italy|D" -path:"~/Downloads/WLM"
#
# Autore: Pietro De Nicolao (Pietrodn)

import wikipedia, pagegenerators, re, os

def downloadImage(basePath, id, title, fileUrl):
	# Giusto per sicurezza...
	title = title.replace(os.sep, '-')
	id = id.replace(os.sep, '-')
	
	# Ottengo i path della directory e del file locali
	dirPath = os.path.normpath(os.path.expanduser(basePath + '/' + id))
	filePath = dirPath + '/' + title
	
	if not os.path.exists(filePath):
		if not os.path.isdir(dirPath):
			# Se l'albero della directory è incompleto, creo ciò che manca
			wikipedia.output(u"Creo directory: " + dirPath)
			os.makedirs(dirPath)
	
		op=wikipedia.MyURLopener
		remotefile = op.open(fileUrl)
		wikipedia.output(u"Scaricherò in: " + filePath);
		
		# Salvo l'immagine
		localfile = open(filePath, "wb")
		localfile.write(remotefile.read())
		localfile.close()
	else:
		wikipedia.output(u"Il file esiste già: " + filePath);

def main():
	wikipedia.setSite(wikipedia.getSite(u'commons', u'commons'))
	all = False
	
	# Gestione argomenti e path
	args = wikipedia.handleArgs()
	genf = pagegenerators.GeneratorFactory();
	basePath = ''
	for arg in args:
		if arg.startswith('-path:'):
			basePath = arg[len('-path:'):]
		else:
			genf.handleArg(arg)
    
    # Faccio caricare il generatore in modo asincrono (maggior efficienza):
    # richiede i testi di più pagine alla volta.
	gen = pagegenerators.PreloadingGenerator(pagegenerators.ImageGenerator(genf.getCombinedGenerator()))
	
	for img in gen:
		wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
						 % img.title())
		fileUrl = img.fileUrl()
		text = img.get()
		
		# Cerco di trovare autore della foto e ID dell'immagine.
		# Se non ci riesco, passo alla prossima.
		m = re.search(r'\|\s*author\s*=\s*\[\[[Uu]ser:[^|]+\|([^\]]+)\]\]', text)
		if not m:
			wikipedia.output("Errore: autore non trovato!")
			continue
		author = m.group(1)
		
		m = re.search(r"\{\{\s*[Mm]onumento[ _]italiano\s*\|\s*([^\}]+)\s*\}\}", text)
		if not m:
			wikipedia.output("Errore: autore non trovato!")
			continue
		id = m.group(1)
		
		# Nome del file
		title = img.titleWithoutNamespace()
		title = re.sub(r"(\.[A-Za-z]+)$", r" foto di " + author + r"\1", title)
		
		if not all:
			choice = wikipedia.inputChoice(u"Scaricare?",
				['Yes', 'No', 'All', "Quit"],
				['y', 'N', 'a', 'q'], 'N')
		else:
			choice = 'y'
		if choice in ['A', 'a']:
			all = True
			choice = 'y'
		if choice in ['Y', 'y']:
			# Scarica il file
			downloadImage(basePath, id, title, fileUrl)
		elif choice in ['Q', 'q']:
			return
		
if __name__ == "__main__":
	try:
		main()
	finally:
		wikipedia.stopme()