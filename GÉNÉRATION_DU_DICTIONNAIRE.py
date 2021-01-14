## Ce script ne sert qu'à générer le dictionnaire de numéros sémantiques.
import re
import joblib
import os
from sklearn.metrics.pairwise import cosine_similarity
import xml.etree.ElementTree as ET
os.chdir('/Users/hubertcorriveau/Udem/maitrise')
betterstructure=joblib.load('Archives/Modèles/finalstructure300vector.joblib')

# maintenant qu'on a nos vecteurs, on va utiliser la fonction de mapping:
def buildgoodDict(top, bottom, matchdict):
    '''
    This function selects, based on a iterable of object, a list of possible correspondances and a dictionnary of the said correspondances, which elements should be homologuous, returns such a list, as well as a list with every element listed more than once
    '''
    #matches={key:max({element:value.get(element, 0) for element in bottom}) for key, value in matchdict.items() if key in top}
    # on a un problème avec le max, possiblement à cause du value.get. il faudrait possiblement revoir comment on définit notre fonction (ensemble de tuples?): un test, avant le prochain croisillon
    matches={key:max({(element,value.get(element,0)) for element in bottom}, key=lambda x: x[1])[0] for key, value in matchdict.items() if key in top}

    ##fin du test
    revdict=dict()
    for key,value in matches.items():
        if value in revdict.keys():
            revdict[value].append(key)
        else:
            revdict[value]=[key]
    # now we have a dictionnary of the matches, constrained on the bottom list, aswell as a reverse dict, comprising of all the keys which are mapped to each valu.
    multiple={ key:val for key,val in revdict.items() if len(val)>1} # this is the dictionnary of multiples. key: an element of bottom, value: elements of top
    suredict={max({val:matchdict[val][key] for val in value}.items(), key=lambda x: x[1])[0]:key for key, value in multiple.items()} #il faut revoir la définition du suredict...
    match={key:value for key, value in matches.items() if value not in multiple.keys()}
    match.update(suredict)# now match is a mapping of only sure elements.
    outtop={key for key in matchdict.keys() if key not in match.keys()}
    outbottom={elt for elt in bottom if elt not in match.values()}
    return match, outtop, outbottom

def build_redirection_dict_with_same(top, bottom):
    '''
    top is the name of the top frame, and bottom of the frame which inherits from top.
    this function associates every top frame element to a bottom frame element, taking advantage of the buildgoodDict function. It returns a dictionnary of redirections from top to bottom.
    '''
    toplist=set(betterstructure[top].keys())
    bottomlist=set(betterstructure[bottom].keys())
    match_dict=dict()
    for element in toplist:
        tempo=dict()
        for elt in bottomlist:
            try:
                if element == elt:
                    tempo.update({elt:1})
                else:
                    tempo.update({elt:cosine_similarity(betterstructure[top][element].reshape(1, -1), betterstructure[bottom][elt].reshape(1, -1))[0][0]})
            except KeyError:
                print(elt.lower())
        match_dict.update({element:tempo})
    #match_dict={element:{elt:model.wv.similarity(element.lower(), elt.lower()) for elt in bottom} for element in top} # we build the dictionnary of matches over every value
    match_dict
    redirectiondict=dict()
    test=True
    while test==True:
        out=buildgoodDict(toplist, bottomlist, match_dict)
        redirectiondict.update(out[0])
        toplist=out[1]-set(redirectiondict.keys())
        # top=out[1].union(set(redirectiondict.keys()))
        bottomlist=out[2]-set(redirectiondict.values())
        if toplist==set() or bottomlist==set():
            test=False
    return redirectiondict

build_redirection_dict_with_same('Education_teaching.xml', 'Entity.xml')


On a alors la bonne fonction de redirection pour faire le mapping.
list(betterstructure['Education_teaching.xml'].keys())

# Sketch de fonction pour mettre en place le mappings

## 1. on extrait l'ordre dans la fonction héritée:

k=re.compile('</fen>') # this is a constant, perhaps one might be tempted to name a constant, although I'm not wure
def orderframe(framexml, k) :
    '''
    This function takes as an input the name of the xml file where we can find the frame, as well as a compiled regex k :
    k=re.compile('</fen>')
    and returns an order of the actants based on the lexicographic definition, or ['CHECK'] if no order can be deduced (either if there is no frame element mentionned or if the conjunction 'or' which is present, in which case there might be an alternative set of frame elements (for example, person1 and person2 possibly may be replaced by persons in some frame element) )
    Note that it could be made much more simply, by simply substituing every non alphabetic character by a space, however, the named actants are structured, and the use of a regex allows the structuration to be used.
    INPUT:
    a frame (file name)
    OUTPUT:
    a list of its frame elements, based on the lexicographic order
    '''
    root=ET.parse(framexml).getroot()# we first parse the xml file
    test=root[0].text # test is the text description of the frame
    substring=re.sub('<ex>.*', '', test)# we remove the list of examples from the string
    if ' or ' in substring: # we don't want to deal with alternate realities
        return ['CHECK']
    else:
        substring=re.sub('(^.*?<fen>)|(</fen>.*?<fen>)', ' ', substring)# we remove everything that is not between the markup '<fen> and </fen>'
        a=k.search(substring)# now we look at every instance of the <fen> mark
        if a is None:
            return ['CHECK']# if there are no <fen>, then there is nothing we can do, it must be checked
        else:
            listofFE=substring[:a.start()].strip().split(' ')# if there is at least one <fen> markup, we can split the input at whitespaces
            outlist=list()# we initiate the list of elements
            realactants={child.attrib['name'] for child in root if 'coreType' in child.attrib.keys()}#this is the set of actants according to
            for el in listofFE:
                if el not in outlist and el in realactants:
                    outlist.append(el)
            if outlist == []:
                outlist=['CHECK']
            return outlist


ReOrderframe('Education_teaching.xml')
j=list(a.items())
j.sort(key=lambda x: x[1])
[elt[0] for elt in j]

re.search('allo', 'salloaluallotallo') is not None

def ReOrderframe(framexml):
    '''
    This function aims to extract some order without using the <fen> markups
    '''
    PossibleFrameElements=extract_def_actants(framexml).keys()
    root=ET.parse(framexml).getroot()# we first parse the xml file
    test=root[0].text # test is the text description of the frame
    initial=dict()
    for element in PossibleFrameElements:
        essai=re.search(element,test)
        if essai is not None:
            initial[element]=essai.start()
    out=list(initial.items())
    out.sort(key=lambda x: x[1])
    return [elt[0] for elt in out ]


os.chdir('fndata-1.6/frame')

framedict=dict()
for frame in os.listdir():
    if frame[-4:]=='.xml':
        framedict[frame]=orderframe(frame, k)

#2. Si on a tous les éléments, on les numérote, et thats it-> ça n'arrive juste pas. JAMAIS. NEVER. JAMAás

[frame for frame in framedict.keys() if framedict[frame]!=['CHECK'] and len(framedict[frame])==len(list(betterstructure['Education_teaching.xml'].keys()))]


# # 3. Sinon, on extrait l'ordre dans la fonction parent, on traduit en fonction fille -> boucle: if key in build_redirection_dict_with_same(FCT1FCT2).keys()
#     Ensuite, on insère les éléments au bon endroit -> utilise le meilleur alignement possible ( diminue la distance de Lehvenshtein)
#     Si on a plusieurs options, on regarde les di

frames=[frame for frame in os.listdir() if frame[-4:] =='.xml']
1. on a besoin du dictionnaire des parents.

def buildinheritdict(frames):
    '''
    This section builds a dictionnary of the inheritances. it produces a dictionnary with frames as keys, and a list of the frames they inherit from as value.
    Input:
    - frames: list of frames
    Output:
    - inheritdict: {frame: [frames from which it inherits]}
    '''
    inheritdict=dict()
    for frame in frames:
        data=ET.parse(frame)
        root=data.getroot()
        inheritdict[frame[:-4]]=[]
        for child in root:
            if ('type', 'Inherits from') in child.attrib.items():
                for children in child:
                    inheritdict[frame[:-4]].append(children.text)
    return inheritdict

inheritdict=buildinheritdict(frames)
inheritdict[]
def topstruct(key) :
    '''
    This recursive function takes a key in the inheritance dictionnary, and returns, for each key, the topmost frame from which there is inheritance
    NEEDS:
    inheritdict: the dictionnary of inheritance ( frame : [all the frame from which it inherits])
    '''
    if inheritdict[key] != []: # there is no provision made for the case(s) where a frame inherits from more than one frame, it simply selects one of them
        return topstruct(inheritdict[key][0])
    else:
        return key
topherit=dict()
for key in inheritdict:
    topherit[key]=topstruct(key)
topherit


2. on compare pour chaque paire parent-enfant, l'ordre

def align(newtop, bottom):
    '''
    This function inserts the elements from the top frame into the bottom frame, assuming that the bottom order is preferable.
    Input:
    top: an ordered list of frame elements from the frame which gives inheritance
    bottom: an ordered list of frame elements from the frame which inherits from the top list
    Output:
    a list of bottom frame elements with every element added.
    '''
    if bottom==['CHECK']:# if the bottom structure is not treated, one might want to simply use the top structure
        return newtop# if there is nothing usable in the bottom frame element, we use directly the top list
    else:
        aligned=set(bottom).intersection(set(newtop)) # this is the list of elements present in both the top and the bottom structure.
        if aligned ==set():
            return list(bottom)+list(newtop)
        else:
            alignlist=[(bottom.index(element), element) for element in aligned] # this lists the elements according to their indexes in the bottom list
            alignlist= sorted(alignlist, key=lambda x: x[0] )
            newbottom=[]
            for i in range(len(alignlist)):
                newbottom+=[elt for elt in bottom if (bottom.index(elt)<bottom.index(alignlist[i][1])) and (elt not in newbottom)]# we add every element in bottom that is before the alignlist element.
                newbottom+=[elt for elt in newtop if (newtop.index(elt)<newtop.index(alignlist[i][1])) and (elt not in newbottom) and (elt not in aligned)]# we add every element in top that is before or is the aligned element.
                newbottom.append(alignlist[i][1])
            newbottom+=[elt for elt in bottom if elt not in newbottom]
            newbottom+=[elt[1] for elt in alignlist if elt[1] not in newbottom]
            newbottom+=[elt for elt in newtop if elt not in newbottom]
            return newbottom

def SonDict(frames):
    '''
    This section builds a dictionnary of the inheritances. it produces a dictionnary with frames as keys, and a list of the frames they inherit from as value.
    Input:
    - frames: list of frames
    Output:
    - inheritdict: {frame: [frames from which it inherits]}
    '''
    inheritdict=dict()
    for frame in frames:
        data=ET.parse(frame)
        root=data.getroot()
        inheritdict[frame[:-4]]=[]
        for child in root:
            if ('type', 'Is Inherited by') in child.attrib.items():
                for children in child:
                    inheritdict[frame[:-4]].append(children.text)
    return inheritdict

dominance=SonDict(frames)

dominance


3. on update notre framedict
4. on poursuit.



inheritdict['Gradable_attributes']

framedict

orderframe('Attributes.xml', k)
orderframe('Gradable_attributes.xml', k)

tempodic=build_redirection_dict_with_same('Attributes.xml', 'Gradable_attributes.xml')

[tempodic[fe] for fe in orderframe('Attributes.xml', k)]

align([tempodic[fe] for fe in orderframe('Attributes.xml', k)], orderframe('Attributes.xml',k)
)

topercolate=set(topherit.values())

def percolateFe(topframe, bottomframe):
    '''
    This function acts mainly as a filter to the possible overgeneration (given that some frame may not be represented in inheritance relation), hence, once a frame elements list is generated, there is a risk of over generagion (NOTE: on doit revoir le  travail de traduction en fait  pour contrebalance)
    topframe: the frame from which the bottomframe inherits
    bottomframe: the frame which inherits from the topframe
    OUTPUT:
    a cleaned frame elements list, in order, for the bottom frame (aka, the basis for a dictionnary)
    '''
    top=framedict[topframe+'.xml']# this lists the order of the elements in the top
    if top==['CHECK']:
        return framedict[bottomframe+'.xml']
    else:
        bottom=set(betterstructure[bottomframe+'.xml'].keys())# in order to get the complete and thorough list of possible frame elements for the bottom list.
        tempodict=build_redirection_dict_with_same(topframe+'.xml', bottomframe+'.xml')
        liste=[]
        for elt in top:
            if elt in tempodict.keys():
                liste.append(tempodict[elt])
            else:
                liste.append(elt)
        top=liste
        bottomorder=framedict[bottomframe+'.xml']
        joined=align(top, bottomorder)
        return [elt for elt in joined if elt in bottom]


def DownInheritance(frame):
    '''
    This function goes down the hierarchy, looking at every inheritance relation, recursively
    '''
    if dominance[frame] == []:
        return None
    else:
        for fra in dominance[frame]:
            print(frame, fra)
            framedict[fra]=percolateFe(frame, fra)
            DownInheritance(fra)


for entity in set(topherit.values()):
    DownInheritance(entity)
print('DONE')

len([frame for frame in framedict.keys() if framedict[frame]==['CHECK']])
len(framedict.keys())


framedict.values()



def extract_def_actants(frame):
    '''
    this function extracts the definition of the various frame elements for a given frame, and returns a dictionnary of the said frame elements
    input:
    - a frame name
    output:
    a dictionnary comprising of the frame elements along with their definition
    '''
    out=dict()
    data=ET.parse(frame)
    root=data.getroot()
    for child in root:
        if 'coreType' in child.attrib.keys():
            txt=child[0].text
            txt=re.sub('<[^>]+>','',txt)
            out[child.attrib['name']]=txt
    return out


for element in [frame for frame in framedict.keys() if framedict[frame]==['CHECK']]:
    try:
        framedict[element]=ReOrderframe(element)
    except:
        framedict[element]=['CHECK']
    print('ok')

for entity in set(topherit.values()):
    DownInheritance(entity)

finalframe=dict()
for frame in framedict.keys():
    try:
        finalframe[frame]=align(ReOrderframe(frame), framedict[frame])
    except:
        finalframe[frame]=framedict[frame]

os.getcwd()
import joblib
joblib.dump(finalframe, '../../framedictionnary.joblib')



## tentative pour méthode par fréquence d'apparition dans le corpus.



def align(newtop, bottom):
    '''
    This function inserts the elements from the top frame into the bottom frame, assuming that the bottom order is preferable.
    Input:
    top: an ordered list of frame elements from the frame which gives inheritance
    bottom: an ordered list of frame elements from the frame which inherits from the top list
    Output:
    a list of bottom frame elements with every element added.
    '''
    if bottom==['CHECK']:# if the bottom structure is not treated, one might want to simply use the top structure
        return newtop# if there is nothing usable in the bottom frame element, we use directly the top list
    else:
        aligned=set(bottom).intersection(set(newtop)) # this is the list of elements present in both the top and the bottom structure.
        if aligned ==set():
            return list(bottom)+list(newtop)
        else:
            alignlist=[(bottom.index(element), element) for element in aligned] # this lists the elements according to their indexes in the bottom list
            alignlist= sorted(alignlist, key=lambda x: x[0] )
            newbottom=[]
            for i in range(len(alignlist)):
                newbottom+=[elt for elt in bottom if (bottom.index(elt)<bottom.index(alignlist[i][1])) and (elt not in newbottom)]# we add every element in bottom that is before the alignlist element.
                newbottom+=[elt for elt in newtop if (newtop.index(elt)<newtop.index(alignlist[i][1])) and (elt not in newbottom) and (elt not in aligned)]# we add every element in top that is before or is the aligned element.
                newbottom.append(alignlist[i][1])
            newbottom+=[elt for elt in bottom if elt not in newbottom]
            newbottom+=[elt[1] for elt in alignlist if elt[1] not in newbottom]
            newbottom+=[elt for elt in newtop if elt not in newbottom]
            return newbottom



newtop= ['Profiled_item',
 'Standard_item',
 'Attribute',
 'Degree',
 'Standard_attribute',
 'Profiled_attribute',
 'Comparison_set']

bottom=['Profiled_item',
 'Standard_item',
 'Standard_attribute',
 'Attribute',
 'Profiled_attribute',
 'Place']
align(newtop, bottom)




framedict=joblib.load('framedictionnary.joblib')
os.getcwd()
framedetest='xmls/'+os.listdir('xmls')[0]
Annot=ET.parse(framedetest)
root=Annot.getroot()

dicoFrame=dict()
def extractinfo(root, dicoFrame):
    for element in root.findall('.//{http://framenet.icsi.berkeley.edu}annotationSet[@frameName]'):
        frame=element.attrib['frameName']
        if frame not in dicoFrame.keys():
            dicoFrame[frame]=dict()
        for elt in element.findall(".//{http://framenet.icsi.berkeley.edu}layer[@name='FE']/{http://framenet.icsi.berkeley.edu}*[@name]"):
            FE=elt.attrib['name']
            if FE not in dicoFrame[frame].keys():
                dicoFrame[frame][FE]=1
            else:
                dicoFrame[frame][FE]+=1
    return dicoFrame

dicoFrame=dict()
for element in os.listdir('xmls'):
    if element[-3:]=='xml':
        Annot=ET.parse('xmls/'+element)
        root=Annot.getroot()
        dicoFrame=extractinfo(root, dicoFrame)

dicoFrame

Frame='Verification'

dicoFrame['Verification']

sorted(dicoFrame['Verification'].items(), key=lambda x: x[1] , reverse=True)

framedict['Information.xml']
sorted(framedict['Verification.xml'])

framedict['Verification.xml']

def sortframedict(frame, x):
    if x in framedict[frame+'.xml']:
        return framedict[frame].index(x)
    else:
        return 0

frame

list

framedict[frame]

for frame in ordereddict:
    list=[entry[0] for entry in sorted(sorted(dicoFrame[frame].items(), key=lambda x :sortframedict(frame,x ) , reverse=True), key=lambda x: x[1], reverse=True)]
    align(framedict[frame+'.xml'], list)

align(framedict[frame+'.xml'], list)



framedict=joblib.load('framedictionnary.joblib')

dicoFrame
