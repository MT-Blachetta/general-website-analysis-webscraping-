import urllib
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import re
import nltk
import nltk.tokenize
#from textblob import TextBlob                           Vielleicht kann der Serveradministrator dieses Paket nachinstallieren
#from textblob_aptagger import PerceptronTagger
import signal
import time

# ! Tragen sie nach belieben print(...) Anweisungen ein welche den Programmablauf dokumentieren, suchen sie auch nach Fehlern

def all_in(check, base): # Typ =: ( 'check' = Liste mit Elementen die alle in 'base' enthalten sein sollen , 'base' = list | set | string in dem gesucht wird) 
    for elm in check:
        if elm not in base:
            return False
    print('ALL IN')
    return True

def one_in(check, base): # Typ =: ( 'check' = Liste mit Elementen von dem eines in 'base' enthalten sein soll , 'base' = list | set | string in dem gesucht wird) 
    for elm in check:
        if elm in base:
            return True
    return False

def count_all(duplicates,ratio=True,rounded=0): # Typ =: ( 'duplicates' = Liste die doppelte Einträge enthalten sollte, 'ratio' = relativer Anteil in Prozent eines Elementes in 'duplicates' mit ausgeben ?, 'rounded' = um wieviele Nachkommastellen soll 'ratio' gerundet sein ? )
    freq = {}
    #assert( isinstance(duplicates,list))
    
    if(ratio):
    
        d_size = len(duplicates)
        #if d_size == 0: d_size = 1

        for k in duplicates:
            num = freq.setdefault(k,[0,0])
            freq[k][0] = num[0]+1

        if(rounded):

            for k in freq.keys():
                freq[k][1] = str( round(100*freq[k][0]/d_size,rounded) )+' %'
                freq[k] = tuple(freq[k])
        else: 
            
            for k in freq.keys():
                freq[k][1] = str(100*freq[k][0]/d_size)+' %'
                freq[k] = tuple(freq[k])
    
    else:
         for k in duplicates:
            num = freq.setdefault(k,0)
            freq[k] = num+1
    
    return freq # OUTPUT =: dictionary mit den Elementen von 'duplicates' und ihrer Anzahl (absolut+relativ)


class attr_node():
    def __init__(self, tag):
        self.tagname = tag.name
        self.attr_list = list( tag.attrs.keys() )
        self.values = [ (atr,tag.attrs[atr]) for atr in self.attr_list ]
        self.attribute = tag.attrs

class htmlstring():
    def __init__(self, navStr):
        self.text = str(navStr)
        top = navStr
        self.path = []

        while(top.name != '[document]'):
            top = top.parent
            idx = len ( top.find_previous_siblings(top.name) )
            self.path.append( top.name+'_'+str(idx) )
            
        self.path = tuple( path[::-1] )
        
        
class page():
        
    def __init__(self,bs):
       
        for tg in bs.findAll(['script','link','style']): tg.decompose()
        satz = re.compile('[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ ?[.!?"]')

        # Attribute
        atr_node = bs(attrs=True)
        self.attributes = {}
        for atr in atr_node:
            top = atr
            idx = len ( top.find_previous_siblings(top.name) )
            path = [top.name+'_'+str(idx)]
            
            while(top.name != '[document]'):
                top = top.parent
                idx = len ( top.find_previous_siblings(top.name) )
                path.append( top.name+'_'+str(idx) )
            
            path = tuple( path[::-1] )
            self.attributes[path] = attr_node(atr)
            
        self.tagtree = list ( self.attributes.keys() ) # Datenstruktur mit Jedem KnotenPFAD als Sequenz im Tupel kodiert

        slist = [txt for txt in bs.get_text().split('\n') if re.search('\w+',txt)]
        filtered = [ tok for tok in bs.get_text().split('\n') if re.search(satz,tok) ]
        text = ' '.join(slist)

        #self.blob = TextBlob( ' '.join(filtered) )
        #self.blob = TextBlob(text)
        self.pagetext = '\n'.join(slist)
        self.sentences = nltk.tokenize.sent_tokenize( ' '.join(filtered) )
    
    #self.words
    
    def words_of_sents(self): # Liste von Listen (Sätze) mit Wörtern eines Satzes
        return [ nltk.tokenize.word_tokenize(s) for s in self.sentences ]
        #wordsPerSent = filter(lambda w: w.strip() and w.strip()[0].isalnum(), wordsPerSent               
    def words(self): # Liste aller Wörter auf der Seite  
        all_words = nltk.tokenize.word_tokenize(self.pagetext)
        all_words = filter(lambda w: re.search('[a-zA-Z][a-zA-Z]+',w) , all_words )
        return list(all_words)
    
    def matchWordsInSent(self,positive,negative=[]): # OUT: Alle Sätze welche alle Wörter der der Liste positive und keines von negative beinhalten
        return [ ' '.join(s) for s in self.words_of_sents() if all_in(positive,s) and not set(s)&set(negative) ]
    def wordFilter(self,positive,negative): # Sind alle Wörter der Liste positive und keines von negative im Seitentext -> True  
        return all_in(positive,self.words()) and not set(self.words())&set(negative)
    def matchInSent(self,positive,negative='-#@'): # Alle Sätze die den Teilstring positive beinhalten aber nicht negative
        return [ s for s in self.sentences if positive in s and not negative in s ]
    def matchInText(self,positive,negative=[]): # Prüft ob irgendein Teilstring aus Liste 'positive' im Text ist aber keines aus negative
        return one_in(positive,self.pagetext) and not one_in(negative,self.pagetext)
    

#word = filter(None,word)---------------------------------------------------------------------------------------

class Timeout(): # Diese Funktion ist notwendig da die Websuche sonst hängen bleiben kann
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass
 
    def __init__(self, sec):
        self.sec = sec
 
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)
 
    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm
 
    def raise_timeout(self, *args):
        raise Timeout.Timeout()


def decode_html(r): # Das ist alles was ein Programm tun kann um die Kodierung einer Html Seite zu finden, alles andere würde algorithmisch die Bytefolge auf eine konkrete Gruppe von Kodierungen prüfen
    ct = r.info()['Content-Type'].split('=') # schaue im Content Type des http headers
    raw = r.read() # sichere den html Quellcode
    if len(ct) == 2: # Hat der HTTP Header eine Kodierungsangabe so folgt sie nach dem '=' Zeichen
        return raw.decode(ct[1]) # versuche die Kodierung aus dem Header zu verwenden
    else: 
        inhtml = BeautifulSoup(raw,'lxml') # Jetzt wird zusätzlich die HTML Seite geparst um nach Kodierungsinfos im Meta-Tag zu suchen
        test = inhtml.find(attrs={'encoding':True})
        if(test):
            return raw.decode(test['encoding'])
        else:
            test = inhtml.find('meta',attrs={'charset':True})
            if(test): return raw.decode(test['charset'])
            else: return raw # wenn nichts gefunden wurde so wird der reine unkodierte Quelltext zurückgegeben

#url = 'http://ruhr-uni-bochum.de'

#base_url = "www.ruhr-uni-bochum.de"

class webscrape():
    def __init__(self):
        self.pages = None # dictionary von allen besuchten Seiten als key mit ihren BeatifulSoup Dokument 
        self.extern_links = None # dictionary mit allen besuchten Seiten und eine Liste ihrer externen (nicht mit Homepage URL) Links
        self.treeIndex = None # Liste mit allen Webseiten als Tupel (URL,[linkURL's...]) die über eine Anzahl von Klicks aus der Homepage erreicht werden können welche dem Index der Liste entspricht
        # z. B. ard.de ist Homepage die in treeIndex[0] steht und auf ard.de/kinder/ARD_Kinder/3275060/index.html direkt verlinkt die in der Tupelliste von treeIndex[1] zu finden wäre
        self.visited = None # Liste aller besuchten und gesammelten Seiten während der Suche
        self.errors = None # Liste aller Seiten bei der ein Fehler aufgetreten ist welcher in errors[k][1] steht
        self.no_html = None # Liste aller Seiten die kein HTML enthielten
        self.bad_url = None # URL's der Liste waren ungültig
        self.depth = None # Tiefe der Suche: wie weit wurden die Hyperlinks auf den Seiten weiterverfolgt (Zälung wie weit Vorwärts von einer Seite gegangen wurde) 

def breath_search(url,base_url,max_depth): # 'url' ist die vollständige URL der Homepage von der alle durch Link erreichbaren Seiten gesucht werden, base_url ist eine Liste mit Teilstrings einer URL die in den Links der zur Homepage besuchenden Seiten enthalten sein muss damit diese HyperLink-URL auf der Seite als 'interner Link' angeklickt und geladen wird. wenn z.B. 'facebook.de'in base_url ist werden auch solche Links weiterverfolgt und nicht als externer Link verzeichnet. max_depth gibt an wie weit gesucht werden soll. Es werden zuerst alle Seiten durchgegangen welche über einen Klick zu erreichen sind dann erst diejenigen welche zwei Klicks benötigen u.s.w

    errors = []
    bad_url = []
    no_html = []
    extern_links = {}
    pages = {}
    depth = 0

    html = urllib.request.urlopen(url).read()
    print('HOMEPAGE: ' + url )
    html = html.decode('utf-8')
    bs = BeautifulSoup(html,'lxml')
    pages[ url ] = bs
    refsA = set ( [ a['href'].strip(' \n') for a in bs('a',href = re.compile('https?:') ) ] )
    refsB = set( [ url+a['href'] for a in bs('a',href=re.compile('^\/\w+') ) ]  )
    nodes = set ( [ lin for lin in refsA if one_in(base_url,lin) ] ) | refsB
    extern_links [ url ] = refsA - nodes
    treeIndex = [ [ (url,nodes) ] ]
    level = treeIndex[0]
    visited = [url]

    #allRef = [ site for lv in level for site in lv[1] ]  

    while ( level and depth < max_depth ):



        next_level = []

        for link in level:
            if ( not all_in(link[1] ,visited) ):

                for site in link[1]:
                    site = site.split('#')[0]   
                    if site not in visited:
                        visited.append( site )
                        try:
# ACHTUNG !!! Hier bei 'Timeout( )' stellt man ein wie lange das Pragramm auf eine zu ladende Website wartet bis es abbricht mit #'exeption' und einen Timeout Fehler für die Seite einträgt. Der Wert ist die Anzahl Sekunden. Soll es schnell gehen trage einen # Wert von etwa 5 (Sekunden) ein. Diese Funktion ist nötig da die Suche sonst hängen bleibt oder zu lange dauert. 
                            with Timeout(13):
                                req = urllib.request.urlopen(site) 
                                if 'html' in req.info()['Content-Type']:
                                    html = decode_html(req)
                                    print('load: ' + site )
                                    #try:
                                        #html = html.decode('utf-8')
                                        #bs = BeautifulSoup(html,'lxml')
                                    #except UnicodeDecodeError as e:
                                        #print(e)"""
                                    bs = BeautifulSoup(html,'lxml') 
                                        
                                    pages[ site ] = bs
                                    refsA = set ( [ a['href'].strip(' \n') for a in bs('a',href = re.compile('https?:') ) ] )
                                    refsB = set( [ site+a['href'] for a in bs('a',href=re.compile('^\/\w+') ) ]  )
                                    nodes = set ( [ lin for lin in refsA if one_in(base_url,lin) ] ) | refsB
                                    extern_links [ site ] = refsA - nodes
                                    refs = refsA | refsB
                                    print("Hyperlinks All: "+ str(len(refs)) + "  intern/extern: "+str(len(nodes))+'/'+str(len(extern_links[site])) )
                                    next_level.append( (site,nodes) )
                                else: no_html.append( (site,req.info()['Content-Type']) )
                        #ok



                        except Timeout.Timeout:
                            errors.append( (site,'TIMEOUT') )
                        
                        except UnicodeEncodeError:
                            bad_url.append(site)                           
                        
                        except urllib.error.URLError as e:
                            errors.append( (site,'URLError',e.reason) )
                        except urllib.error.HTTPError as e:
                            errors.append( (site,'HTTPError',e.reason,e.code) )


        level = next_level

        if(level):
            treeIndex.append( next_level )
        else: print('Liste neuer Weblinks (next level) leer ' + str(level) ) 
    #allRef = [ site for lv in level for site in lv[1] ]
        depth += 1
        print('\nDEPTH '+str(depth) )
    print('maximal depth reached')
    results = webscrape()
    results.pages = pages
    results.extern_links = extern_links
    results.treeIndex = treeIndex
    results.visited = visited
    results.errors = errors
    results.no_html = no_html
    results.bad_url = bad_url
    results.depth = depth
    
    return results