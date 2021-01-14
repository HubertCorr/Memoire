#!/usr/bin/env python3


os.getcwd()
import xml.etree.ElementTree as ET
import re
import os #don't know if it is really useful, we'll see later on
import sys #to write the structure elegantly or not...
os.chdir('/Users/hubertcorriveau/Udem/maitrise')
# from Functions4annotated import *
from Functions5 import *


for i in range(len(sentences)):
    #print('j')
    if re.search('Wynn began plans to reinvigorate Las Vegas', sentences[i][0].text) is not None:
        print( "SENTENCE"+str(i)+" : "+sentences[i][0].text)


[key[0] for key in syntano(sentences[123])[0].keys() if key!='text



syntano(sentences[123])

re.search('slow', struct[0]['text'])
struct=syntano(sentences[123])
for key, value in struct[0].items():
    if key !='text':
        print(struct[0]['text'][key[0][0]:key[0][1]+1])
        for element in value:
            if type(element[0])==tuple:
                print('->'+struct[0]['text'][element[0][0]:element[0][1]+1])
            else:
                print( '->'+str(element[0]))
for key, value in struct[1].items():
    if key !='text' and value !=[((0,0),0)]:
        print('\n'+struct[0]['text'][key[0]:key[1]+1]+':')
        for element in value:
            if type(element[0])==tuple:
                print('->'+struct[0]['text'][element[0][0]:element[0][1]+1])
            else:
                print( '->'+str(element[0]))




print(V2tograph(Retest(syntano(sentence))[0], Retest(syntano(sentence))[1


data=ET.parse('xmls/ANC__HistoryOfLasVegas.xml')
root=data.getroot()
sentences=rootParse(root)
sentence=sentences[7]
k=annotations(sentence)
k['text']
print(tograph(k,lemmatiser(k)))
l=syntax(sentence)


Retest(syntano(sentence))

syntano(sentence)[1]
help('Functions5.py')

syntano(sentence)[0]

syntano(sentence)[1]
 [elt for elt in syntano(sentence)[0].values() if type(elt)==list]
testlist=[]
for element in syntano(sentence)[0].values():
        if type(element)==list:
            for el in element:
                if type(el[0])==tuple:
                    testlist.append(el[0])
testlist=set(testlist)
testlist



Retest(syntano(sentence))
syntano(sentence)[1]
synanno=syntano(sentence)[1]
newd=dict() # dum
for key, value in synanno.items(): # on retire les types de relation, pour simplifier le code
    newd[key]=[val[0] for val in value if type(val[0])==tuple and val[0] !=(0,0)]
connection(newd)
newd



def V2tograph(annots, lemmas):
    """
        this is an attempt to build a Rsem for the annotated sentence
        IT should be integrated to Functions5.py, replacing the previous version.
    """
    sent='structure Sem s001 {\n S:1{\n  text="'+annots['text']+'"\n'
    sentence=str()
    main=str()
    for key in annots.keys():
        if key != 'text':
            if type(key) == tuple:
                frameactuel=key[2]
                if key[0] in lemmas.keys():
                    sentence=sentence+'  '+lemmas[key[0]]+'{\n'
                    main=lemmas[key[0]]
                else:
                    sentence=sentence+ '"CHECK'+ str(key[0])+'" {\n'
                    main=str(key[0])
            i=1
            dolast=[]
            for element in annots[key]:
                if element is not None:
                    if type(element[0])==tuple: # on élimine
                        try:
                            sentence+='   '+str(framedictionnary[frameactuel+'.xml'].index(element[1].split(':')[1])+1)+'-> '+lemmas[element[0]]+'\n'# ici on doit insérer le numéro de l'actant; on retrouve l'info dans?
                        except:
                            dolast.append(element)
                        sent+='  '+lemmas[element[0]]+'{}\n'
                    elif element[0] not in ['CNI', 'DNI', 'INI']:
                            try:
                                sentence+='   '+str(i)+'-> "'+str(element[0])+'"\n'
                                sent +=str(element[0])+':{}\n'
                                i+=1
                            except:
                                print(str(key))
                                print(str(element))
            if dolast !=[]:
                i=0
                for element in annots[key]:
                    try:
                        i=max(i, framedictionnary[frameactuel+'.xml'].index(element[1].split(':')[1])+1)
                    except:
                        pass
                i+=1
                for element in dolast:
                    sentence+='   '+str(i)+'-> '+lemmas[element[0]]+'\n'
                    i+=1
            sentence+='  }\n'
    if main == "":
        return None
    else:
        sentence= sentence+ ' main-> '+main+'\n}\n}'
        return sent+sentence


## test: si ça marche, on remplace dans functions5
def connection(structure):
    """
    This function takes the dictionnary of syntactic annotations and returns a boolean True if connected, False if not.
    Furthermore, it returns a dictionnary of all the connected groups within the structure, with keys as indices and values as a list of element with a final element, either False bool or a tuple (True, X), where X is the boolean stating whether there is a unique node which is ungoverned.

    Dependencies:
        standard library
        checkclus function (to fix the case where there are many ungoverned nodes)

    Variables used:
    Input:
        Structure: the dictionary of syntaxic information (output of syntano)
    Intermediate variables:

    Output:
        connected : A boolean assessing wheter the entire structure is connected (True) or not (False)
        dictionnaire: A dictionnary with indices as keys and a list of syntactic elements as values. The last item of this list is either a tuple (True, X) or False, with X being the unique ungoverned node
        parentdict: a dictionnary associating each node(key) to its governor (value)
    """
    # initialise the output structures:
    dictionnaire=dict()
    parentdict=dict()
    # building the parent dictionary, through iteration over our structure:
    for key, value in structure.items():
        for val in value:
            if val not in parentdict.keys():
                parentdict[val] = [key]
            else:
                parentdict[val].append(key)
    #sanity check (preventing bad behaviour from the function):
    if (0,0) in parentdict.keys():
        del parentdict[(0,0)]
    tocheck=set(parentdict.keys()).union(set(structure.keys())) # tocheck comprises of all nodes
    numofannots=len(tocheck) # the number of items that must belong to a connected graph is the number of nodes
    tocheck=list(tocheck) # Changing the set to a list, for iteration
    i=0 # this index will be for index assignment
    while len(dictionnaire.keys()) < numofannots:
        if tocheck == []: # checking whether we've assigned every item to a subgraph
            break
        element=tocheck[0]
        dictionnaire[i]=[element] # [slowly] building a list with all connected elements
        tocheck.remove(element) # limiting the size of our buffer
        # loop: checks every annotated element for connection with the target; (!! May be suboptimal !!)
        test=True
        while test:
            test=False
            for el in dictionnaire[i]: #el=dictionnaire[i][0]
                if el in structure.keys():
                    if structure[el] != []:
                        for elem in structure[el]:
                            if elem[0] not in dictionnaire[i] and elem[0] != (0,0):
                                dictionnaire[i].append(elem[0])
                                tocheck.remove(elem[0])
                                test=True
                if el in parentdict.keys():
                    for elem in parentdict[el]:#elem = parentdict[el][0]
                        if elem not in dictionnaire[i]:
                            dictionnaire[i].append(elem)
                            tocheck.remove(elem)
                            test=True
        i+=1 #once every connected element has been assigned, we increment, and go to the next group.
    for key,value in dictionnaire.items(): # iterating on the dictionary to check for the dominant node.
        sub=[elem for elem in value if elem not in parentdict.keys()] # list of non-governed
        if len(sub) == 1:
            dictionnaire[key].append((True,sub[0]))
        elif len(sub) >=2:
            hd=checkclus(value, structure, parentdict) # if there are two or more dominant nodes, use checkclus to see wheter it might be attributed to embedded structures
            for k,v in hd.items():
                if type(v) is tuple:
                    dictionnaire[key].append((True, v))
        else:
            dictionnaire[key].append((False, value[0])) # If there are no dominant node, we append the boolean 'False' in a tuple, with a (almost random) node
    if len(set(dictionnaire.keys())) == 1: # yields a boolean 'true' if it is connected, false otherwise.
        connected=True
    else:
        connected=False
    return connected,dictionnaire,parentdict
# ça semble marcher!

dotlist=list()
liste=os.listdir('xmls/')
liste.remove('NTI__LibyaCountry1.xml')

file = 'NTI__Iran_Chemical.xml'
problist=list()
listestr=list()
for file in liste:
    path='xmls/'+file
    print(path)
    data=ET.parse(path)
    root=data.getroot()
    sentences=rootParse(root)
    for elt in sentences:
        # k=annotations(elt)
        #k=syntax(elt)
        # print(k['text'])
        #dotlist.append(tograph(k,lemmatiser(k)))
        try:
            annots=Retest(syntano(elt))
            listestr.append(V2tograph(annots[0], annots[1]))
        except:
            problist.append((path, elt[0].text))

os.getcwd()
os.mkdir('strs16dec')


for i in range(len(listestr)):
    if listestr[i] is not None:
        NAME='strs16dec/testout'+str(i)+'.str'
        with open(NAME, 'w') as f:
            f.write(listestr[i])
problist
print(listestr[161])
os.mkdir('tryfunc6')
for i in range(len(listestr)):
    if listestr[i] is not None:
        NAME='tryfunc6/testout'+str(i)+'.str'
        fh=open(NAME, 'w+')
        fh.write(listestr[i])
        fh.close()
len(listestr)

listestr

path
Retest(syntano(elt))

dotlist
len(dotlist)
# ========= pour test =======
data=ET.parse('fndata-1.6/fulltext/NTI__LibyaCountry1.xml')
#os.mkdir('norel')
for i in range(len(dotlist)):
    NAME='norel/testout'+str(i)+'.dot'
    fh=open(NAME, 'w+')
    fh.write(dotlist[i])
    fh.close()


print(re.sub(r'"', r'\"', string ))

os.mkdir()

for i in range(len(listestr)):
    if listestr[i] is not None:
        NAME='cinqmille/testout'+str(i)+'.str'
        fh=open(NAME, 'w+')
        fh.write(listestr[i])
        fh.close()

os.mkdir('syntax')
for i in range(len(dotlist)):
    NAME='syntax/testout'+str(i)+'.dot'
    fh=open(NAME, 'w+')
    fh.write(dotlist[i])
    fh.close()


### tests
it={1,2,3}
for elt in it:
    print(str(elt))
###


368 semble ok...; il faudrait mettre des guillemets


sent='The last visitor was then- U.S. Rep . Bill Richardson of New Mexico , who went to help a pair of U.S. oilmen in diplomatic trouble '
sent[21:67]

"""
*** trouver comment trouver les noeuds communicativement dominants
faire 5000 Rsem.



7231! (sans la lybie)



Problèmes:

NTI Lybia 1 : je n'arrivais pas à générer; il va falloir se pencher sur le problème


***

Pour les cas de semi-annotations: choisir juste l'antécédent (flusher ce qui est annoté comme 'rel' ou pas annoté comme 'ant')
pour les autres, il faudrait re

* envoyer le tout à Lotcha


- documenter le tout!!!!!
- pour la désambiguisation, il faudrait faire une fct qui vérifie si un cycle est présent, et si oui, on flushe la structure, quitte à la corriger manuellement. (ma solution attribue le même poids à chaque élément du cycle, ce qui n'est pas très utile.)
- Pour les conjonctions, comme on travaille en Mel'čuk, il faudrait mettre (arbre précédent)-> and -> arbre suivant; il faut une règle générale en cas d'arbres disjoints pour former la structure complète.
- après, on devrait pouvoir tout réussir!

considérer mettre les frames en place de sémantèmes et de prendre les frame elements comme lexicalisation possible -> le framanticon a été fait !!!




-> mettre les éléments du framanticon entre guillemets
-> tester voir si notre cas de Half century fonctionne at large
-> me faire des fonctions de test avec des assert qui valident la fonction en des points connus.

"""



"""
- réécrire la fonction connection pour la simplifier avec une compréhension de liste.
check!

- revoir la structure testout 420 pour voir ce qui se passe avec le cluster, (À RÉPARER)
- mettre des guillemets partout, check
- ne pas oublier l'accolade fermante, check
- mettre une espace avant chaque chiffre-> check-ish (ne semble pas fonctionner très bien...) : fonctionne mais Mate n'en veut pas il me semble...


- élaguer automatiquement les structures sans annotation sémantique... -> il faudrait revoir la fonction annots pour supprimer les structures vides d'annotation sémantique.

- Pour la semaine prochaine:
    faire un plan général
    - trouver une façon d'évaluer l'implémentation ( pour donner une note quelconque )

- Pour le 20 mai:
    - écrire entre 5 et 10 pages du mémoire
    - regarder 150 structures; noter les différents bugs et appliquer les correctifs


- même chose que la semaine passée
    - lire sur BLEU et voir si ça pourrait être une métrique appropriée (voir les travaux de simon mille entre autres)

- Écrire sur BLEU et ROUGE
- Terminer ma correction de bugs
- Écrire 10-15 pages
- rv jeudi 9h

- régler le bug d'ici vendredi 18h


- modifier le style pour inclure une numérotation automatique ( aller dans le panneau de styles ) - regarder le vidéo
- valider 200 structures FAIT
- écrire 5 à 10 pages
    - boucler la section d'évaluation

- gosser avec les frames -> finalement semble inopérant, étant donné la quantité de termes non annotés. (ou alors il va falloir faire un hybridanticon, avec un mélange de frames et d'élémnents textuels)

- avoir qqc à regarder concrètement la semaine prochaine pour le RV
 mercredi 17 à 9h

- formulaire de prolongation
- faire un dossier partagé
- préparer un protocole d'évaluation pour le word2vec de frames


- voir ce qu'on pourrait faire comme corpus pour réentraîner le modèle vectoriel; idéalement un corpus de linguistique
- évaluer le matching ( il faudrait faire des paires etc. )

POUR le corpus


https://catalog.ldc.upenn.edu/LDC2013T12


On a toujours un problème avec le dictionnaire de mapping FE-> numéro d'actant: pour Evaluative_comparison, il y a le défaut de mal ordonnancer les profiled_attribute vs Standard_attribute

- il faut re-générer le dictionnaire pour voir si ces problèmes sont toujours là, étant donné qu'il y avait un bug avec la fonction Align;
    - si le problème persiste, on utilise l'algo de sélection par fréquence, puis le dictionnaire pour les FE absents
    - le problème persiste; il va falloir que l'on ajuste le tir, voir une fois la correction faite; ( on pourrait repasser sur les frames à la main dans le pire scénario)

- On a aussi le problème des relatives: un numéro apparait!
"""


####### framanticon ####

import os
import xml.etree.ElementTree as ET
os.chdir('/Users/hubertcorriveau/Udem/maitrise')
import re

framanticon=dict()
liste=os.listdir('fndata-1.6/frame')
for element in liste:
    if element[-4:] != '.xml':
        liste.remove(element)
    else:
        structure=ET.parse('fndata-1.6/frame/'+element)
        root=structure.getroot()
        framanticon[element[:-4]]=[elt.attrib['name'] for elt in root.findall('{http://framenet.icsi.berkeley.edu}lexUnit')]

framanticon_text='framanticon { \n'
for key, val in framanticon.items():
    string='\n'+key+' {'
    for elt in val:
        string+=' lex='+re.sub('[.]','_', elt)
    string+=' }'
    framanticon_text+=string
framanticon_text += '\n}'

out=open('framanticon', 'w+')
out.write(framanticon_text)
out.close()



## faire attention aux structures de
