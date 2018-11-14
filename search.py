from server.webserver import Webserver, App
import webbrowser

from crawler import *
from store import*

class SearchEngine(App):
    """
    Webanwendung zum Suchen eines Begriffs
    """

    def register_routes(self):#called by server
        self.add_route('', self.search_interface)  # there is only one route for everything... no prefix

    def search_interface(self, request, response, pathmatch=None):
        result1, result2, result3 = "","",""
        search_term = ""

        if 'search_term' in request.params:  # check if parameter is given (key). originally comes from html form
            try:  # calculate
                search_term = request.params['search_term']
            except (ValueError, TypeError):
                result1 = "Bitte einen gültigen Suchbegriff eingeben"

        if not hasattr(self, "s"):
            self.s = Store(netloc= "http://vm009.rz.uos.de")

        if not hasattr(self, "c"):
            self.c = Crawler(self.s)
        if self.s.empty():
            try:
                self.s.load()
            except:
                self.c.crawl()
        results = self.s.search(search_term.split())
        results.extend(["","",""])
        print(results)
        result1, result2, result3 = results[0:3]
        response.send_template('templates/search_engine/search.tmpl', {'result1':result1, 'result2':result2, 'result3': result3})


if __name__ == '__main__':
    print("check1")
    s = Webserver(8040)
    s.add_app(SearchEngine(prefix=''))
    s.serve()
    webbrowser.open_new_tab("http://localhost:8020/")
