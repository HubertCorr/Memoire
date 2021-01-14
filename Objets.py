"""
Objectification: Ce fichier essaie de mettre de l'ordre dans les fonctions et dans le Main, afin de clarifier la structure du code. ( par le changement en POO)
"""
class structure():
    """
    This class reprensents a general structure, sentences or substrings of the sentence
    It is made to unify our way to select the main node, whether it is a sentence, or simply a span.
    It will have the following attributes:
    - range: a range of values for characters. ( I.e. (0, end of sentence) for a sentence, or the span of the cluster for a cluster .
    - annotations: a (sub)set of annotations
    - main : the most proeminent node, by semantics, or in last resort by syntax.
    - clusterdict: a dictionary of clusters inside the structure.
    - allspans: the list of all spans present inside the annotation ( mainly present to generalize the cluster function)
    - subclusters: a set oc
    """
    def selectMain(self):
        """
        This function selects the main element from the structure, assuming that everything have been cleared.
        """
        pass
    def extract(self):
        """
        This function extracts all spans and 
        """
        pass


class sentence(structure):
    """
    This class is a sentence.
    """
    #attributes:
    """
    Comme attributs, on aura l'ensemble des termes annotés et le texte
    - lu: set of LU objects
    - id:  son id.
    - texte: l'énoncé
    - annotations: l'ensemble des termes annotés
    - lemmas : dict [tuple, lemma ]
    - redirections: dict [tuple, tuple]
    - affined: bool ( si on a nettoyé l'objet)
    - rel_ant: dict ( rel:ant -> par span)
    - allspans( utile pour nos clusters par la suite... )
    """
    text=str()

    #methods:
    """
    comme méthode(s):
    - parse_from_xml() : parse le xml, et retourne les annotations[brutes]
    - affine() : prend les annotations brutes, et en fait une version plus propre <- la méthode la plus complexe.
    - to_mate(): renvoie une string en format Mate
    """
    def parse_from_xml(self, AS, prefix):
        """
        This function takes as an input the xml structure and updates every field according to the annotation, without further treatment.
        Input:
        AS : an XML.etree.elementTree object (annotation set)
        prefix: a constant string for parsing the xml, using Etree.
        Output: none, updates the object.
        """
        self.text=AS.find(prefix+'text').text# we update the text string.
        annotations=AS.findall(prefix+'annotationSet[@frameName]')
        self.annotations={}
        self.allspans={}
        for lu in annotations:
            span=(lu.find('.//'+prefix+"label[@name='Target']").attrib['start'], lu.find('.//'+prefix+"label[@name='Target']").attrib['end'])# we select the span of the target
            lexical_unit=LU(lemma=lu.attrib['luName'], frame=lu.attrib['frameName'], lu_id=lu.attrib['ID'], span=span) # we build the lexical unit
            self.allspans.add(span) # update the list of spans
            semannots=lu.findall('.//'+prefix+"layer[@name='FE']/"+prefix+'label[@name]')# select the list of semantics annotations
            for element in semannots:
                if 'start' in element.attrib: # the semantic frames that are not a Null instanciation
                    span=(element.attrib['start'], element.attrib['end'])
                    self.allspans.add(span)# we add the span to the list of spans
                    lexical_unit.add_semantics(span, element.attrib['name'])# the lexical_unit's annotation is updated.
                else:
                    lexical_unit.add_semantics(element.attrib['itype'], element.attrib['name'])
            syntannots= lu.findall('.//'+prefix+"layer[@name='GF']/"+prefix+'label[@name]')
            for element in syntannots:
                if element['name']!='head':
                    lexical_unit.add_syntax((element.attrib['start'], element.attrib['end']), element.attrib['name'] )
                else:
                    if element['name'] == 'head':
                        toreverse.add( (element.attrib['start'], element.attrib['end']), (lu.find('.//'+prefix+"label[@name='Target']").attrib['start'], lu.find('.//'+prefix+"label[@name='Target']").attrib['end']) )
            rel_annots= lu.findall('.//'+prefix+"layer[@name='Other']/"+prefix+'label[@name]')
            for element in rel_annots:
                rel_ant.add((element.attrib['start'], element.attrib['end'], element.attrib['name']))

            self.annotations.add(lexical_unit)# we add the lexical unit in our structure.
        for element in toreverse: #iterating over every 'head' GF, and cleaning it
            i=False# an indicator whether we have to create the LU manually
            for elt in annotations:
                if elt.span==element[0]:
                    elt.add_syntax(element[1], 'rhead')# updating the syntax
                    i=True
                    break
            if i==False:# if no element can be updated, we simply add an Ad Hoc LU in our annotations.
                self.annotations.add(LU(span=element[0], syntax={(element[1],'rhead')}))

    # def get_main(self): MOVED TO STRUCTURE CLASS
    #     """
    #     This function will return the main LU from the set of annotations
    #     """
    #     pass

    # def resolve_clusters(self): MOVED TO STRUCTURE CLASS
    #     """
    #     This function will take a cluster, and return its head
    #     """
    #     pass

    def redirect_cluster(self, redirectionDict):
        """
        this function takes the redirectionDict, and scans through all LUs to redirect accordingly.
        """
        for lu in self.annotations:
            synchange=set()
            for element in lu.syntax:
                if element[0] in redirectionDict.keys():
                    synchange.add((element[0], redirectionDict[element[0]], element[1]))
            for element in synchange:
                lu.remove_syntax(element[0])
                lu.add_syntax((element[1], element[2]))
            semchange=set()
            for element in lu.semantics:
                if element[0] in redirectionDict.keys():
                    semchange.add((element[0], redirectionDict[element[0]], element[1]))
            for element in semchange:
                lu.remove_semantics(element[0])
                lu.add_semantics(element[1],element[2])
    def lemmatiser(self):
        """
        This function will first build a dictionnary of all the lemmas, and then transform the LUs accordingly
        First step: extract lemmas
        """
        lemmas=dict()
        for lu in annotations: # this extracts the lemmas from the annotations( 1st pass)
            if lu.lemma not in lemmas.values():
                lemmas[lu.span]=lu.lemma
            else:#if there already is an instance of this lemma
                i=1
                while lu.lemma+':'+str(i) in lemmas.values():
                    i+=1
                lemmas[lu.span]=lu.lemma+':'+str(i)
            # here there is code to build a lemma's dictionnary (span: lemma)
        ## second step: extract textual lemmas from the rest of the structure; to do so, we take all spans, remove the one in the lemmas' keys, and
        restofspans={span for span in allspans if span not in lemmas.keys()}
        for span in restofspans:
            if re.escape(self.text[span[0]:span[1]+1]) not in lemmas.values():
                lemmas[span]=re.escape(self.text[span[0]:span[1]+1])
            else:
                i=1
                while re.escape(self.text[span[0]:span[1]+1]+':'+str(i)) in lemmas.values():
                    i+=1
                lemmas[lu.span]=re.escape(self.text[span[0]:span[1]+1]+':'+str(i))
        ### step 2: transform our entries by their lemmatized counterparts.
        for lu in self.annotations:
            lu.set_lemma(lemmas[lu.span])
            lu.semantics=dict({( value, lemmas[key] ) for key,value in lu.semantics.items() if type(key)==tuple}.union({( value, key) for key,value in lu.semantics.items() if type(key)!=tuple}))
            lu.syntax=dict({( value, lemmas[key]) for key,value in lu.syntax.items()})
class LU():
    """
    This class is for an annotated LU
    """
    """
    Comme attributs, on aura:
    - l'id de la phrase auquel l'unité est associée
    - son id.
    - le lemme
    - son span
    - le frame associé
    - un dict ( semantics ): span: rôle sémantique
    - un dict( syntax ): span: rôle syntaxique
    """

    """
    comme méthodes, on aura:
    - set_lemma()
    -
    """
    def __init__(self, lemma=None, span=None, frame=None, lu_id=None, sent_id=None, syntax=None, semantics=None):
        self.id=lu_id
        self.sent_id=sent_id
        self.lemma=lemma
        self.frame = frame
        self.syntax=set()
        self.semantics=set()
        if syntax is not None:
            self.syntax=syntax
        if semantics is not None:
            self.semantics=semantics
    def __repr__(self):
        rep=str(self.lemma)+':'
        for key, value in self.semantics.items():
            rep+="  "+str(value)+'->'+str(key)
        return rep
    def get_lemma(self):
        return self.lemma
    def set_lemma(self, lemma):
        self.lemma=lemma
    def add_semantics(self, span, role):
        self.semantics.add((span, role))
    def remove_semantics(self, span=None, role=None):
        if span is not None:
            if span in self.semantics.keys():
                del self.semantics[span]
        if span is None and role is not None:
            testlist=[key for key in self.semantics.keys() if self.semantics[key]==role]
            if testlist !=[]:
                del self.semantics[testlist[0]]
    def add_syntax(self, span, role):
        self.syntax.add((span,role))
    def remove_syntax(self, span=None, role=None):
        if span is not None:
            if span in self.syntax.keys():
                del self.syntax[id]
        if span is None and role is not None:
            testlist=[key for key in self.syntax.keys() if self.syntax[key]==role]
            if testlist !=[]:
                del self.syntax[testlist[0]]






test=LU('Ramaquar')
test.add_semantics('123', 'popo')

test.set_lemma('rastaquouère')
