import pickle
import numpy as np
import re

class Store:
    """ Search index. For administration of data"""
    def __init__(self, netloc = ""):
        self.terms = {} #search-terms to URIs and frequency (netloc)
        self.pages = {} #uri's to text, title ...
        self.netloc = netloc#root domain searched in

    def empty(self):
        if len(self.pages) == 0:
            return True
        else: return False

    def add(self, uri = None, title=None, code=None, search_term = None, frequency=None, teaser = ""):
        """ Adds  uri title and code"""
        if uri and title and code:
            self.pages[uri] = {"title": title, "code": code}
        elif search_term and uri and frequency:
            self.terms[search_term] = {"uri":uri, "frequency": frequency, "teaser":teaser}
        else:
            raise Exception("Either provide uri, title and code or search_term, uri and frequency")

    def search(self, search_terms):
        """ Allows to search for several search-strings and returns ranked results.
        Returns: Sorted list of URI, titles and teasers. Sorting takes into account if all terms"""
        results = {}

        #search_term, frequency to be added to dictionary!?
        for uri, v in self.pages.items():
            title = v["title"]
            code = v["code"]
            for term in search_terms:
                frequency = len(re.findall(term, code))
                if frequency >= 1:
                    start, end = re.search(term, code).span()
                    teaser = code[start-10 if start-10 >=0 else 0 : end+10 if end+10<=len(code) else len(code)]

                    try: results[uri]
                    except: results[uri] = []
                    results[uri].append([term, frequency, teaser])
                    #self.add(search_term = term, uri=uri, frequency = frequency, teaser = teaser)

        search_terms_found = [len(v) for k, v in results.items()]#How many search terms contained?
        frequencies = [res[0][1] for res in list(results.values())]#Frequencies

        score = np.array(search_terms_found) + 0.1 * np.array(frequencies) #secret formula

        final_results = [list_item for score, list_item in
                         sorted(zip(score,list(results.items())), reverse = True)]#sort by score

        return final_results

    def save(self):
        """ Saves data """
        filehandler = open("pickled_stuff","wb")#TODO find reasonable naming convention
        pickle.dump(self, filehandler)
        filehandler.close()

    def load(self):
        filehandler = open("pickled_stuff","rb")
        self.__dict__.update(pickle.load(filehandler).__dict__)
        filehandler.close()
