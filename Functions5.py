import os
import sys
import xml.etree.ElementTree as ET
import re
import operator ##important for the argmax to work
import joblib
framedictionnary=joblib.load('testfinaldict.joblib')


# newd
#structure={(69, 75): [(0, 0)], (81, 89): [(0, 0)]}
def connection(structure):
    """
    !TO BE TESTED, go to !## ARCHIVED ##! at the end of the document if need to be restored.
    This function takes the dictionnary of syntactic annotations and returns a boolean True if connected, False if not.
    Furthermore, it returns a dictionnary of all the connected groups within the structure, with keys as indices and values as a list of element with a final element, either False bool or a tuple (True, X), where X is the boolean stating whether there is a unique node which is ungoverned.

    Dependencies:
        standard library
        checkclus function (to fix the case where there are many ungoverned nodes)

    Variables used:
    Input:
        Structure: the dictionary of syntaxic information (output of syntano), without the names
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
                                if elem[0] in tocheck:
                                    tocheck.remove(elem[0])
                                # except ValueError:
                                #     print('ERREUR')
                                test=True
                if el in parentdict.keys():
                    for elem in parentdict[el]:#elem = parentdict[el][0]
                        if elem not in dictionnaire[i]:
                            dictionnaire[i].append(elem)
                            if elem in tocheck:
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

def checkclus(value, structure, parentdict):
    """
    This function takes as input a connected graph which is not a tree, and check whether the non-treeness is attribuable to the presence of an englobing span, such that the englobing span is connected to the target, and
    Dependencies:
        Standard library
    Variables:
    Input:
        value: a list of nodes which are connected
        structure: the list of annotations
        parentdict: the dictionnary of governors
    Intermediate:
    Output:
        headdict
    """
    # we initiate our variables
    englobing=dict()
    headdict=dict()
    for element in value:
        englist=[el for el in value if type(el)==tuple and type(element)==tuple and el[0]<=element[0]<=element[1]<=el[1] and el!=element] # list of elements that englobe the elt element (including itself) (!? Est-ce que ça devrait pas plutôt etre el for el in L'ensemble des annotations? ce serait plus général que des annotations imbriquées...)
        #englist.remove(element) # we take out the element
        if englist != []: # If something englobes an element
            englobing[element]=englist # we build a dictionnary of imbrications, with the element as key, and the list of englobing elements as value
    for key,value in englobing.items():# Iterating over every embedded structure, we check for a unique ungoverned node. If there are multiple ungoverned nodes the problem is not solved
        for val in value:
            bool=False
            if val not in parentdict.keys():
                if bool==True:
                    bool=False
                    headdict[key]=val
                    break
                else:
                    headdict[key]=val
                    bool=True
            else:
                if len(parentdict[val]) > 1:
                    bool=False
                    if key in headdict.keys():
                        del headdict[key]
                    break
    return headdict

def goodselect(clusterdict, parentdict):
    """
    This function makes redirection from the list of clusters and the parents.
    a line is repeated multiple times, fixing an obscure bug
    to test with
    clusterdict={(34, 51): [(34, 40), (42, 51)],
     (8, 51): [(27, 32), (34, 51), (34, 40), (42, 51), (8, 15)]}
     parentdict={(0, 1): [(3, 6)],
      (8, 51): [(3, 6)],
      (8, 15): [(27, 32)],
      (34, 51): [(27, 32)],
      (34, 40): [(42, 51)]}
    """
    outdict=dict()
    for key in clusterdict.keys():
        gout=dict()
        gout=selectinnermost(key, clusterdict, parentdict, gout)
        gout=selectinnermost(key, clusterdict, parentdict, gout)
        gout=selectinnermost(key, clusterdict, parentdict, gout)
        outdict.update(gout)
    return outdict

def selectinnermost(element, cluster, syntax,dico):
    """
    this function is the recursive part for goodselect
    """
    testset=[el for el in cluster[element] if el in cluster.keys() and el not in dico.keys()]
    if testset ==[]:
        out=list({dico[elt] for elt in cluster[element] if elt in dico.keys()}.union({elt for elt in cluster[element] if elt not in syntax.keys()}))
        if out != []:
            dico[element]=out[0]
    else:
        for elt in testset:
            dico.update(selectinnermost(elt, cluster, syntax, dico))
    return dico


def selecthead(subset, parentdict):
    """
    !?!? Perhaps it does not need to be a function?
    A REVOIR- je vais la caller juste une fois, et faire une redirection
    This function takes as an input a set of elements which must be connected, and a dictionnary consisting of the parents of each element.
    it returns the unique element such that it is undominated.
    Dependencies:
        Standard Library
    Variables:
    Input:
        subset: a connected subgraph
        parentdict: mapping (child -> [parentnode(s)])
    Output:
        an element or None
    """
    undominated = [el for el in subset if el not in parentdict.keys()] # the list of undominated nodes
    if undominated != [] and len(undominated)==1: # assessing that it is a singleton list
        return undominated[0]


def cluster(structure, subset, text, dico):
    """
    TO CHECK:
    Est-ce qu'on a besoin de tout ce qu'il y a dans dico? sinon, on pourrait se limiter à dico[1]


    TESTME: a la génération il va falloir renvoyer un flag pour les structures de données qui ont été annotées!!!
    dico: dictionnaire des groupes (sortie de connection).
    This function takes a structure and a span corresponding to an annotated cluster, and check for connectedness. if it is not connected, it ensures that everything is connected, using the mel'čukian form for 'and', assuming that the first member of the compound is the most salient item.
    Dependencies:
        selecthead
        Standard Library
    Variables:
    Input:
        structure: the annotation structure (a dictionnary)
        subset: a span comprising of various disjoint structures (!?!)
        text: the text of the sentence
        dico: a dictionnary of all the groups (connected,dictionnaire,parentdict), connected a boolean; dictionnaire a dictionary of the clusters and parentdict the parents dictionary)
    Intermediate:
    Output:
        toreturn: a connected structure
    """
    ClusterDictionnary=dico[1] # we select the dictionnary of clusters
    groups=dict()
    to_conj={key for key in structure.keys() if subset[0]<=key[0]<=key[1]<=subset[1]} # the set of annotated elements in the subset
    subdict=dict()
    subspans=dict()
    for k,v in ClusterDictionnary.items():
        subdict[k]=[] # We initiate an empty substructure for each cluster
        for elt in v:
            if elt in to_conj:
                subdict[k].append(elt) # we list the elements in the annotated elements in the substructure. ; LIST/Set comprehension should be used instead?
        if subdict[k]==[]:
            del subdict[k] # cleaning the empty structures.
    for key,value in subdict.items(): # Looking at all elements associated to a key in subdict, we find the enclosing span
        subspans[key]=(min([val[0] for val in value]),max([val[1] for val in value]))
    if len(subspans.keys())==1: # if there is only a span, the function cannot do anything, so it returns nothing.
        return {}
    text= ' '*subset[0]+text[subset[0]:subset[1]+1]+' '*(len(text)-subset[1]-1)# We only keep what's in the relevant subspan, and replace any element on the string outside with spaces.
    for value in subspans.values():
        text= text[:value[0]]+' '*(value[1]-value[0]+1)+text[value[1]+1:] # We take off every annonated thing, replacing with spaces.
    if ' and ' in text: # If and is a conjunction in the span
        k=list(subspans.items())# we list the elements in the subspan
        k.sort(key=lambda x : x[1][0]) # We sort the spans in order, left-to-right
        newlt=[((k+[None])[i],([None]+k)[i])for i in range(len(k)+1)] # newlt is a list of tuple consisting of subsequent elements in k.
        finalt=[(elt[0][0], elt[1][0]) for elt in [j for j in newlt if type(j[0]) == tuple and type(j[1])==tuple]] # building a consequent ordering
        headdict=dict()
        toreturn=dict()
        for key,value in subdict.items():
            substruct={cle:structure[cle] for cle in value}
            headdict[key]=selecthead(substruct, dico[2])
        for element in finalt:
            toreturn[headdict[element[0]]]=('and',headdict[element[1]])
    elif ' or ' in text: # exactly as with 'and '
        k=list(subspans.items())
        k.sort(key=lambda x : x[1][0]) # k a la forme de tuples (index, span, en ordre croissant de span)
        newlt=[((k+[None])[i],([None]+k)[i])for i in range(len(k)+1)]
        finalt=[(elt[0][0], elt[1][0]) for elt in [j for j in newlt if type(j[0]) == tuple and type(j[1])==tuple]] # on ordonne nos groupes en ordre de span, et présente les tuple de manière conséquente
        headdict=dict()
        toreturn=dict()
        for key,value in subdict.items():
            substruct={cle:structure[cle] for cle in value}
            headdict[key]=selecthead(substruct, dico[2])
        for element in finalt:
            toreturn[headdict[element[0]]]=('or',headdict[element[1]])
    else: # if none of the above holds, we cancel
        return {}
    return toreturn

def FrameCheck(Frame):
    """ this function takes as an input the name of a frame and
    returns a dictionnary of all the frame elements along with their type.
    It assumes that the frames are in a folder named 'fndata-1.6/frame/'

    Dependencies:
        XML ElementTree
        Standard Library
    Input:
        Frame: A string, the name of a frame
    Output:
        A dictionnary of the frame elements with their types

    Note that an ad-hoc frame has been created, named Test35, since there is at least one annotation to such a frame

    """
    path = "fndata-1.6/frame/"+Frame+".xml"
    framedata = ET.parse(path)
    frameroot = framedata.getroot()
    elements = dict()
    for elt in frameroot.iter():
        if 'coreType' in elt.attrib.keys():
            elements[elt.attrib['name']] = elt.attrib['coreType']
    return elements

def rootParse(element):
    """ This function parses a text annotation, returns a list of all the sentences.
    Dependencies:
        XML ElementTree
        Standard Library
    Input:
        element: an Etree object
    Output:
        a list of sentences (Etree object)

    """
    liste=list()
    for elt in element.findall(".//{http://framenet.icsi.berkeley.edu}sentence"):
        liste.append(elt)
    return liste

def getframes():
    """
    Works under MacOSX, probably on linux, although it is not tested on Windows.
    There has been a previous version using more complicated algo.

    This function returns the list of frames, (a list of strings, by scanning
    Check the commented section for an upgrade.
    Dependencies:
        Os
        Standard Library
    Input: None
    Output:
        The list of annotated frames
    """
    frames=list()
    for elt in [frame for frame in os.listdir('fndata-1.6/frame/') if frame[-3:]=='xml']:
        frames.append(elt[:-4])#we append to the list of frames every frame name (encoded in an xml file)
    return frames




def syntano(AS):
    """
    This function takes as an input an annotation Set (AS), and returns the syntactic annotations
    Dependencies:
        ElementTree
        Standard Library
        clean_relatives
    Input:
        AS: an annotation set
    Output:
    (RENAME ME)    annotationdict : a dictionary of semantic annotations
        syntaxdict: a dictionary of syntactic annotations
    """
    sentence=AS.find(".//{http://framenet.icsi.berkeley.edu}text").text # this is the textual information
    j=AS.findall(".//{http://framenet.icsi.berkeley.edu}annotationSet[@frameName]")# j consists of all annotattes elements associated with a frame name.
    syntaxdict=dict() # initiation the syntax dict
    reverselist=list()
    annotationdict=dict() # Initiating the annotation dict
    annotationdict['text']=sentence
    for element in j: # to every annotated element:
        lemma=element.attrib['luName'] # we keep the lemma( Lexical unit Name)
        frame=element.attrib['frameName'] # we keep the frame
        frameDict=FrameCheck(frame)#returns the dictionnary of frame elements
        targetDict=element.find(".//{http://framenet.icsi.berkeley.edu}label[@name='Target']").attrib #returns the entry for the target, we want to use 'start' and 'end'
        targetRange=(int(targetDict['start']),int(targetDict['end'])) # yields the span of the target
        entry=(targetRange, lemma, frame)
        Sannot=element.findall(".//{http://framenet.icsi.berkeley.edu}layer[@name='GF']/{http://framenet.icsi.berkeley.edu}label[@name]")
        Sactantslist=list()
        for anno in Sannot:
            actants=anno.attrib #annotations dictionnary, we want to keep the span and the name of the relation
            if actants['name'] != 'Head':
                Sactantslist.append(((int(actants['start']), int(actants['end'])), actants['name'])) # we make a tuple with the annotation ( (start, end) , 'frame:type:relation Name' ), and add it to a list
            else: # we want to reverse the realtion 'head'
                reverselist.append(((int(actants['start']), int(actants['end'])),targetRange))
        if Sactantslist != []:
            syntaxdict[entry[0]]=Sactantslist
        else:
            syntaxdict[entry[0]]=[((0,0),0)]
        ###
        annot=element.findall(".//{http://framenet.icsi.berkeley.edu}layer[@name='FE']/{http://framenet.icsi.berkeley.edu}label[@name]")
        actantslist=list()
        #finaldel=set()
        for anno in annot:# now it is time for the semantic annotations
            actants=anno.attrib #dictionnaire des annotations, start, end et name sont d'intéret
            if 'start' in actants.keys():
                actantslist.append(((int(actants['start']), int(actants['end'])), frameDict[actants['name']]+':'+actants['name'])) # we make a tuple with the annotation ( (start, end) , 'frame:type:relation Name' ), and add it to a list
            else:
                actantslist.append((actants['itype'], frameDict[actants['name']]+':'+actants['name']))# If there is a Null instanciation, we want to be aware of it
        todelete=clean_relatives(element, actantslist)# we must clean the relative clauses, wiping them off the structure (as they are present twice)
        actantslist=[el for el in actantslist if el[0] not in todelete]
        annotationdict[entry]=actantslist
        # we reverse the relations in reverselist to add to the syntax dictionary:
    reversedict={ent[0]:[] for ent in reverselist}
    for key, value in reversedict.items():
        reversedict[key]=[(ent[1],'rHead') for ent in reverselist if ent[0]==key]
    for key in reversedict.keys():
        syntaxdict[key]=reversedict[key]
    return annotationdict, syntaxdict


def clean_relatives(target, actantslist):
    """
    COMMENTS SHOULD BE TRANSLATED

    this function takes as an input a target annotation and the list of actants and returns the list of annotations to delete, based on relative-antecedent relation
    It assumes the following:
    For every annotation to the same frame element, if every word is annotated to either relative clause or antecedent, it will remove the antecedent
    if no relative pronoun is annotated, it will remove everything that is not an antecedent
    If only a relative pronoun is annotated, it removes the relative pronoun and keeps not-annotated words
    Dependencies:
        ElementTree
        Standard Library
    Input:
        target: an Element Tree Object, to check for relative clause
        actantslist: a list of its actants
    Output:
        A list of entries to be removed, being deemed superfluous
    """
    test=target.find("{http://framenet.icsi.berkeley.edu}layer[@name='Other']") # On travaille sur le target, et on regarde la catégorie 'Other'
    if test != None:# si le other existe
        rellist=test.findall("{http://framenet.icsi.berkeley.edu}label[@name='Rel']") # on trouve les annotations de relatives
        reltuple={(int(k.attrib['start']),int(k.attrib['end'])) for k in rellist}# on en fait un ensemble
        antlist=test.findall("{http://framenet.icsi.berkeley.edu}label[@name='Ant']") #idem pour les antécédents
        anttuple={(int(k.attrib['start']),int(k.attrib['end'])) for k in antlist}
        toflush=list() # on crée une liste de trucs a flusher
        fetocheck=dict() # on fait un dictionnaire de trucs a flusher
        actantdict=dict(actantslist) # on crée un dictionnaire a partir de nos actants, par défaut la conversion place le span en tuples
        revdict=dict()
        for value in actantdict.values():
            revdict[value]=[key for key in actantdict.keys() if actantdict[key]==value]
        for ent in reltuple:# pour tous les pronoms relatifs, on vérifie si il existe quelque part dans la liste d'actants, et on l'ajoute a fetocheck
            if ent in actantdict.keys():
                fetocheck[ent]=actantdict[ent]
            else:# si le pronom n'est pas annoté dans les actants, on le met dans une liste de trucs a flusher
                toflush.append(ent)
        for ent in anttuple: # pour les antécédents, si il est dans 'les actants, on ajoute a fetocheck'
            if ent in actantdict.keys():
                fetocheck[ent]=actantdict[ent]
        annots=dict() #on initialise un dictionnaire d'annotations.
        for key,val in fetocheck.items(): # on itere sur fetocheck, qui consiste en un dictionnaire ; les clés sont les spans, et les valeurs sont les valeurs d'annotation
            if key in anttuple:
                annots[key]='Ant'
            else:
                annots[key]='Rel'
        # on a alors deux dictionnaires: les annotations ant et rel, ainsi que l'annotation des frame elements.
        toflush=list()
        tokeep=list()
        for item in revdict.values():
            if len(item) >1:
                testset={ annots[element] for element in item if element in annots.keys()}
                if 'Ant' in testset:
                    antecedents={key for key in annots.keys() if annots[key]=='Ant' and key in item}
                    toflush.append({elt for elt in item if elt not in antecedents})
                elif 'Rel' in testset:
                    relatives={key for key in annots.keys() if annots[key]=='Rel' and key in item}
                    toflush.append(relatives)
        bigflush=list()
        for element in toflush:
            if type(element) == set:
                for ent in element:
                        bigflush.append(ent)
            elif type(element)== tuple:
                bigflush.append(element)
        bigflush=set(bigflush)
        bigflush
    else:
        bigflush=[]
    return bigflush
#
# lemmatiser(semanno, fullConnect[2], clusterSem, annotated)
#
# input=semanno
# parents=fullConnect[2]
# clusters=clusterSem
# liste=annotated


def lemmatiser(input, parents, clusters, liste): #parents est là pour rester, mais d'ici là, il ne fait rien.
    """
    FIX ME: parents est mutable (c'est une liste; quand on lui passe lemmatiser, parents devient le mal incarné)
    On cherche à lemmatiser la sortie de la fonction annotations.
        Comme entrée, on a un dictionnaire:{
        text : 'phrase cible'
        (range, target1_lemmatisé) : [
                                        (range1, frame:type:frameElement1 ),
                                        (range2, frame:type:frameElement2 ),
                                        ...
                                        ]
        (range, target2_lemmatisé) : [
                                        (range1, frame:type:frameElement1 ),
                                        (range2, frame:type:frameElement2 ),
                                        ...
                                        ]
        etc.
        }
        on veut comme sortie, au lieu de 'range' dans les annotations(dans la liste), juste le lemme.
        -> on va parcourir le dictionnaire, les clés nous donnent la lemmatisation de chacun.
        -> si on n'a pas de lemmatisation, on va prendre 'phrase cible'[range] comme lemme. (AKA pas lemmatisé)
            -> si le range inclut d'autres spans, on va faire un selecthead avant, évidemment!!!

        -> on va également désambiguiser les lemmes. si dans nos annotations, il y a deux fois un meme lemme,
        on va les nommer 1-'lemme' et 2-'lemme', dans l'ordre dans lequel ils apparaissent. (doit etre fait avant les autres opérations.)

    """
    lemmas=dict()
    for key in input.keys():
        if key != 'text': #on ne veut pas de la phrase entière
            if key[1] not in lemmas.values():
                lemmas[key[0]]= '"'+re.sub('[.]', '_', key[1])+'"' # REGEX here to prevent the use of dots in Mate.
            else:
                i=1
                while '"'+key[1]+'":'+str(i) in lemmas.values():
                    i +=1
                if '"'+key[1]+'":'+str(i) not in lemmas.values():
                    lemmas[key[0]] = '"'+re.sub('[.]', '_', key[1])+'":'+str(i)
    to_lemma=[el for el in liste if el not in lemmas.keys()]
    redirect=goodselect(clusters, parents)
    for element in to_lemma:
        if element in clusters.keys():# if what we're looking at qualifies as an embedding span.
            try:
                reference=redirect[element]
                if reference in lemmas.keys():# si la tête de cluster est déjà lemmatisée
                    lemmas[element]=lemmas[reference]
                else:#si reference est pas dans les lemmes
                    lemme='"'+input['text'][reference[0]:reference[1]+1]+'"'
                    if lemme not in lemmas.values():
                        lemmas[element]='"'+re.sub(r'"', r'\"', lemme )+'"'
                    else:
                        i=1
                        while '"'+lemme+'":'+str(i) in lemmas.values():
                            i +=1
                        lemmas[element] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
            except:# si on n'arrive pas a avoir un cluster convenable, on va prendre le texte
                lemme='"'+input['text'][element[0]:element[1]+1]+'"'
                if lemme not in lemmas.values():
                    lemmas[element]='"'+re.sub(r'"', r'\"', lemme )+'"'
                else:
                    i=1
                    while '"'+lemme+'":'+str(i) in lemmas.values():
                        i +=1
                    lemmas[element] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
        else: #si on n'a pas un cluster:
            lemme='"'+input['text'][element[0]:element[1]+1]+'"'
            if lemme not in lemmas.values():
                lemmas[element]='"'+re.sub(r'"', r'\"', lemme )+'"'
            else:
                i=1
                while '"'+lemme+'":'+str(i) in lemmas.values():
                    i +=1
                if '"'+lemme+'":'+str(i) not in lemmas.values():
                    lemmas[element] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
    # for value in input.values():
    #     if type(value) != str:#reject the text of the sentence
    #         for element in value:
    #             if element[0] in clusters.keys():# if what we're looking at qualifies as an embedding span.
    #                 reference=selecthead(element[0], parents)
    #                 if reference is not None:# si on a une tête de cluster
    #                     if reference in lemmas.keys():# si la tête de cluster est déjà lemmatisée
    #                         lemmas[element[0]]=lemmas[reference]
    #                     else:
    #                         lemme='"'+input['text'][reference[0][0]:reference[0][1]+1]+'"'
    #                         if lemme not in lemmas.values():
    #                             lemmas[reference[0]]='"'+re.sub(r'"', r'\"', lemme )+'"'
    #                         else:
    #                             i=1
    #                             while '"'+lemme+'":'+str(i) in lemmas.values():
    #                                 i +=1
    #                             if '"'+lemme+'":'+str(i) not in lemmas.values():
    #                                 lemmas[reference[0]] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
    #                 else:# si on n'arrive pas a avoir un cluster convenable, on va prendre le texte
    #                     lemme='"'+input['text'][element[0][0]:element[0][1]+1]+'"'
    #                     if lemme not in lemmas.values():
    #                         lemmas[element[0]]='"'+re.sub(r'"', r'\"', lemme )+'"'
    #                     else:
    #                         i=1
    #                         while '"'+lemme+'":'+str(i) in lemmas.values():
    #                             i +=1
    #                         if '"'+lemme+'":'+str(i) not in lemmas.values():
    #                             lemmas[element[0]] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
    #             else: #si on n'a pas un cluster:
    #                 if type(element[0])== tuple:# en fait c'est ici qu'on doit ajouter une condition sur les spans englobants
    #                     if element[0] not in lemmas.keys():
    #                         lemme='"'+input['text'][element[0][0]:element[0][1]+1]+'"'
    #                         if lemme not in lemmas.values():
    #                             lemmas[element[0]]='"'+re.sub(r'"', r'\"', lemme )+'"'
    #                         else:
    #                             i=1
    #                             while '"'+lemme+'":'+str(i) in lemmas.values():
    #                                 i +=1
    #                             if '"'+lemme+'":'+str(i) not in lemmas.values():
    #                                 lemmas[element[0]] = '"'+re.sub(r'"', r'\"', lemme )+'":'+str(i)
    return lemmas


def returndictRsem(listofspans):
    """
    INPUT: an iterable containing all spans
    This function returns the a dictionnary with keys the spans and values the list of embedded structures (excluding the key)
    """
    entrydict=dict()
    for span in listofspans:
        nlist=[value for value in listofspans if span[0]<=value[0]<=value[1]<=span[1] and value != span ]
        if nlist!= []:
            entrydict[span]=nlist
    return entrydict

#
#
# synannotations=({'text': 'In the mid-1980s , Wynn began plans to reinvigorate Las Vegas with a new resort .',
#   ((30, 34), 'plan.n', 'Purpose'): [((36, 60), 'Core:Goal'),
#    ((62, 78), 'Core:Means'),
#    ((19, 22), 'Core:Agent')],
#   ((39, 50), 'reinvigorate.v', 'Rejuvenation'): [((19, 22), 'Core:Agent'),
#    ((52, 60), 'Core:Entity'),
#    ((62, 78), 'Peripheral:Means')],
#   ((69, 71), 'new.a', 'Age'): [((69, 71), 'Core:Age'),
#    ((73, 78), 'Core:Entity')],
#   ((0, 1),
#    'in.prep',
#    'Temporal_collocation'): [((3, 15), 'Core:Landmark_period'), ((19, 78),
#     'Core:Trajector_event')],
#   ((24, 28), 'begin.v', 'Activity_start'): [((19, 22), 'Core:Agent'),
#    ((30, 78), 'Core:Activity')]},
#  {(30, 34): [((36, 60), 'Dep'), ((62, 78), 'Dep'), ((19, 22), 'Ext')],
#   (39, 50): [((19, 22), 'Ext'), ((52, 60), 'Obj'), ((62, 78), 'Dep')],
#   (69, 71): [((0, 0), 0)],
#   (0, 1): [((3, 15), 'Obj'), ((19, 78), 'Ext')],
#   (24, 28): [((19, 22), 'Ext'), ((30, 78), 'Obj')],
#   (73, 78): [((69, 71), 'rHead')]})

def Retest(synannotations):
    """
    !! important: modifier la lemmatisation pour faire en sorte que ce ne soit pas le cluster entier, mais seulement ce qui est nécessaire.
    Once it will be working, we must uncomment the part referring to cluster function
    This function takes as an input the output of the function synannotations (namely the semantic annotations dictionary and its syntactic counterpart)
    - important: il faut flagger les sorties de CLUSTER pour s'assurer qu'il n'y ait pas de bogue dans le code.
    cette fonction est la réécriture moins chaotique de la suivante (makeRsem)
    """
    #ÉTAPE 1 : lister nos clusters en annotation sémantique
    # - fonction returndictRsem:
    # notre fonction nécessite une liste de spans, alors on va transformer nos annotations sémantiques.
    semanno=synannotations[0] # nos annotations sémantiques
    liste=[key[0] for key in semanno.keys() if key != 'text'] # on a la liste de toutes nos valeurs de clé
    for value in semanno.values():
        if type(value)!=str:
            for val in value:
                if type(val[0]) == tuple:
                    liste.append(val[0]) # on ajoute les tuples annotés
    annotated=set(liste) # Annotated consists of every element which is either a target or a FE in the semantic annotations.
    clusterSem=returndictRsem(annotated) # This lists the various clusters in a dictionnary
    #ÉTAPE 2: pour chaque cluster: regarder les noeuds qui le compose, vérifier qu'ils soient connectés.
    synanno=synannotations[1]
    newd=dict() # This is a structure that shows the syntax without the relations
    for key, value in synanno.items(): # on retire les types de relation, pour simplifier le code
        newd[key]=[val[0] for val in value if type(val[0])==tuple and val[0] !=(0,0)]
    fullConnect=connection(newd) #fullConnect is the connection dictionnary based on the syntactic structure
    redirection=dict()
    tor=list()
    lemmasdict=lemmatiser(semanno, fullConnect[2], clusterSem, annotated) # fullConnect[2], clusterSem et annotated: c'est temporarire on lemmatise avant de modifier les entrées, ça va être plus simple.
    for key, value in clusterSem.items():
        # dans la valeur, on a une liste de spans, sans plus. on devrait interroger les dictionnaires d'annotations syntaxique!
        # on va prendre les valeurs d'annotation syntaxique (connection ne prend que ce genre d'entrée)?
        ensemble={}
        for val in value:
            if val in synanno.keys():
                ensemble[val]=[elt[0] for elt in synanno[val]]
            else:
                for elt in [k for k in synanno.keys() if val in synanno[k]]:
                    ensemble[elt]=[el[0] for el in synanno[elt]]
        conn_test=connection(dict(ensemble)) # on obtient plein d'infos syntaxiques sur l'annotation d'un cluster
        if len(conn_test[1].keys()) == 1:# il faut décider comment on réfère a notre tête synt.
            try:
                redirection[key]=conn_test[1][0][-1][-1]
            except:
                pass
            # try:
            #     redirection[key]=conn_test[1][0][-1][-1] # devrait être le bon élément; à revérifier
            # except:
            #     print(key)
            #     print(conn_test)
        else:# si on a des éléments disjoints.
            tor.append(cluster(synanno, key, semanno['text'], fullConnect)) # this will produce a dictionnary of addition one must do to solve
    for key in redirection.keys():
        for k in semanno.keys(): # on doit conditionner davantage!!!
                for elt in semanno[k]:
                    if elt[0] ==key:
                        torep=(redirection[key],elt[1])
                        semanno[k].remove(elt)
                        semanno[k].append(torep)
    semdictkey=dict()
    for key in semanno.keys():
        semdictkey[key[0]]=key
    for element in tor: # on est rendus à traiter l'ajout d'annotations à notre structure pour les connections.
        if element != {}:
            i=1# on se fait un incrémenteur
            for key, val in element.items():
                if key in semdictkey.keys():
                    semanno[semdictkey[key]].append((str(val[0])+str(i), 'shouldwork'))
                else:
                    semanno[key]=[(val[0]+str(i), 'shouldwork')]
                semanno[val[0]+str(i)]=(val[1], 'SHOULDWORK')
                i+=1# on incrémente pour s'assurer d'avoir des connecteurs distincts.
    return semanno, lemmasdict


def tograph(annots, lemmas):
    """
        this is an attempt to build a Rsem for the annotated sentence
    """
    sent='structure Sem s001 {\n S:1{\n text="'+annots['text']+'"\n'
    sentence=str()
    main=str()
    for key in annots.keys():
        if key != 'text':
            if type(key) == tuple:
                    if key[0] in lemmas.keys():
                        sentence=sentence+lemmas[key[0]]+' {\n'
                        main=lemmas[key[0]]
                    else:
                        sentence=sentence+ '"CHECK'+ str(key[0])+'" {\n'
                        main=str(key[0])
            elif type(key)==str :
                sentence=sentence+'"'+key+'" {\n'
                main=key
            i=1
            for element in annots[key]:
                if element is not None:
                    if type(element[0])==tuple:
                        sentence += ' '+str(i)+'->'+lemmas[element[0]]+'\n'
                        sent +=lemmas[element[0]]+'{}\n'
                    elif element[0] not in ['CNI', 'DNI', 'INI']:
                        sentence+=' '+str(i)+'->"'+str(element[0])+'"\n'
                        sent +=str(element[0])+'{}\n'
                    i+=1
            sentence+='}\n'
    if main == "":
        return None
    else:
        sentence= sentence+ ' main ->'+main+'\n}\n}'
        return sent+sentence
#
# def V2tograph(annots, lemmas):
#     """
#         this is an attempt to build a Rsem for the annotated sentence
#     """
#     sent='structure Sem s001 {\n S:1{\n text="'+annots['text']+'"\n'
#     sentence=str()
#     main=str()
#     for key in annots.keys():
#         if key != 'text':
#             if type(key) == tuple:
#                 frameactuel=key[2]
#                 if key[0] in lemmas.keys():
#                     sentence=sentence+lemmas[key[0]]+' {\n'
#                     main=lemmas[key[0]]
#                 else:
#                     sentence=sentence+ '"CHECK'+ str(key[0])+'" {\n'
#                     main=str(key[0])
#             i=1
#             dolast=[]
#             for element in annots[key]:
#                 if element is not None:
#                     if type(element[0])==tuple: # on élimine
#                         try:
#                             sentence +=' '+str(framedictionnary[frameactuel+'.xml'].index(element[1].split(':')[1])+1)+"->"+lemmas[element[0]]+'\n'# ici on doit insérer le numéro de l'actant; on retrouve l'info dans?
#                         except:
#                             dolast.append(element)
#                         sent+=lemmas[element[0]]+'{}\n'
#                     elif element[0] not in ['CNI', 'DNI', 'INI']:
#                             try:
#                                 sentence+=' '+str(i)+'->"'+str(element[0])+'"\n'
#                                 sent +=str(element[0])+'{}\n'
#                                 i+=1
#                             except:
#                                 print(str(key))
#                                 print(str(element))
#             if dolast !=[]:
#                 i=0
#                 for element in annots[key]:
#                     try:
#                         i=max(i, framedictionnary[frameactuel+'.xml'].index(element[1].split(':')[1])+1)
#                     except:
#                         pass
#                 i+=1
#                 for element in dolast:
#                     sentence+='"'+str(i)+lemmas[element[0]]+'\n'
#                     i+=1
#             sentence+='}\n'
#     if main == "":
#         return None
#     else:
#         sentence= sentence+ ' main ->'+main+'\n}\n}'
#         return sent+sentence

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


# # # # ## this is a   test block. We will have to check the structure Las Vegas was no longer a small pioneer settlement
os.chdir('/Users/hubertcorriveau/Udem/maitrise')
# path='xmls/Miscellaneous__IranRelatedQuestions.xml'
# data=ET.parse(path)
# root=data.getroot()
# sentences=rootParse(root)
# i=0
# bol=True
# while bol:
#     if sentences[i].attrib['ID']=="4097441":
#         print(str(i))
#         bol= False
#     else:
#         i+=1
# del i
# del bol
# test=sentences[223]
# synannotations=syntano(test)
# synannotations
#
# Retest(syntano(test))
#
#
# semanno
# fullConnect[2]
# clusterSem
# annotated
#
# {el for el in annotated if 0<= el[0]<= el[1]<=6}
#
#
# selecthead({el for el in annotated if 8<= el[0]<= el[1]<=51}, fullConnect[2])
#
# lemmasdict
# # # # # # ##
#
# LOF=getframes()
# k=list()
# for f in LOF:
#     for key, value in FrameCheck(f).items():
#         k.append((key, value))
#
# len(LOF)
#
# fdict={t:FrameCheck(t) for t in LOF}
#
# import json
# fh=open('framedict', 'w')
# json.dump(fdict,fh)
# fh.close()
#
# for
#
# # file=open('LOF', 'a+')
#
# for line in k:
#     file.write(str(line))
# file.close()
# test=FrameCheck(LOF[1])
#
# test.items()




##! ARCHIVED !##


#This first version does not work with our current Syntano version
#
# def connection(structure):
#     """
#     This function takes the dictionnary of syntactic annotations and returns a boolean True if connected, False if not.
#     Furthermore, it returns a dictionnary of all the connected groups within the structure, with keys as indices and values as a list of element with a final element, either False bool or a tuple (True, X), where X is the boolean stating whether there is a unique node which is ungoverned.
#
#     Dependencies:
#         standard library
#         checkclus function (to fix the case where there are many ungoverned nodes)
#
#     Variables used:
#     Input:
#         Structure: the dictionary of syntaxic information (output of syntano)
#     Intermediate variables:
#
#     Output:
#         connected : A boolean assessing wheter the entire structure is connected (True) or not (False)
#         dictionnaire: A dictionnary with indices as keys and a list of syntactic elements as values. The last item of this list is either a tuple (True, X) or False, with X being the unique ungoverned node
#         parentdict: a dictionnary associating each node(key) to its governor (value)
#     """
#     # initialise the output structures:
#     dictionnaire=dict()
#     parentdict=dict()
#     # building the parent dictionary, through iteration over our structure:
#     for key, value in structure.items():
#         for val in value:
#             if val not in parentdict.keys():
#                 parentdict[val] = [key]
#             else:
#                 parentdict[val].append(key)
#     #sanity check (preventing bad behaviour from the function):
#     if (0,0) in parentdict.keys():
#         del parentdict[(0,0)]
#     tocheck=set(parentdict.keys()).union(set(structure.keys())) # tocheck comprises of all nodes
#     numofannots=len(tocheck) # the number of items that must belong to a connected graph is the number of nodes
#     tocheck=list(tocheck) # Changing the set to a list, for iteration
#     i=0 # this index will be for index assignment
#     while len(dictionnaire.keys()) < numofannots:
#         if tocheck == []: # checking whether we've assigned every item to a subgraph
#             break
#         element=tocheck[0]
#         dictionnaire[i]=[element] # [slowly] building a list with all connected elements
#         tocheck.remove(element) # limiting the size of our buffer
#         # loop: checks every annotated element for connection with the target; (!! May be suboptimal !!)
#         test=True
#         while test:
#             test=False
#             for el in dictionnaire[i]:
#                 if el in structure.keys():
#                     if structure[el] != []:
#                         for elem in structure[el]:
#                             if elem not in dictionnaire[i] and elem != (0,0):
#                                 dictionnaire[i].append(elem)
#                                 tocheck.remove(elem)
#                                 test=True
#                 if el in parentdict.keys():
#                     for elem in parentdict[el]:
#                         if elem not in dictionnaire[i]:
#                             dictionnaire[i].append(elem)
#                             tocheck.remove(elem)
#                             test=True
#         i+=1 #once every connected element has been assigned, we increment, and go to the next group.
#     for key,value in dictionnaire.items(): # iterating on the dictionary to check for the dominant node.
#         sub=[elem for elem in value if elem not in parentdict.keys()] # list of non-governed
#         if len(sub) == 1:
#             dictionnaire[key].append((True,sub[0]))
#         elif len(sub) >=2:
#             hd=checkclus(value, structure, parentdict) # if there are two or more dominant nodes, use checkclus to see wheter it might be attributed to embedded structures
#             for k,v in hd.items():
#                 if type(v) is tuple:
#                     dictionnaire[key].append((True, v))
#         else:
#             dictionnaire[key].append((False, value[0])) # If there are no dominant node, we append the boolean 'False' in a tuple, with a (almost random) node
#     if len(set(dictionnaire.keys())) == 1: # yields a boolean 'true' if it is connected, false otherwise.
#         connected=True
#     else:
#         connected=False
#     return connected,dictionnaire,parentdict
