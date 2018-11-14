import requests
import re

class Crawler:
    def __init__(self, store = None, netloc = ""):
        if store == None:
            if netloc == None:
                raise Exception("Either provide a store object or a netloc (page to be searched in) for initialization")
            store = Store(netloc)
        self.store = store

    def crawl(self):
        self.queue = [] #list of uris to be visited
        self.visited = [] #already visited pages
        self.queue.append(self.store.netloc + "/")

        while not len(self.queue) == 0: #crawl
            current_uri = self.queue[0]
            page = self.fetch(current_uri)

            self.visited.append(current_uri)
            del self.queue[0]

            self.store.add(current_uri, self.get_title(page), self.clean(page))

            links = self.get_links(current_uri)
            links = [l for l in links if l not in self.visited]

            print(links)

            self.queue.extend(links)

    def fetch(self, uri):
        response = requests.get(uri)
        if response.status_code == 200 and "text/html;" in response.headers['content-type']:
            return response.text
        else:
            return ""

    def get_links(self, uri, internal_only = True):
        """ Returns list of links"""
        html = self.fetch(uri)

        uri_without_page = ""
        try:
            uri_without_page = re.search("^(https?://.*/).+$",uri).group(1)
        except:
            pass

        links = []
        links.extend(re.findall("href='(.*)'",html))
        links.extend(re.findall('href="(.*)"',html))

        final_links = []
        for link in links:
            if re.match("^http(s)?://", link):
                if internal_only:
                    if re.match(self.store.netloc,link):
                        final_links.append(link)
                else:
                    final_links.append(link)
            elif re.search("/.*/", link):#absolute path
                final_links.append(self.store.netloc+link)
            else:
                final_links.append(uri_without_page+link)

        return final_links

    def get_title(self, html):
        """ Parses title from html"""
        if re.search("<title>(.*)</title>",html):#search doesnt start necessarily in first line like match
            return re.search("<title>(.*)</title>",html).group(1)#capturing parentheses () define part retrived via groups 1
        else:
            return ""

    def clean(self, page):
        try:
            indices = list(re.search("<head>(.|\n)*</head>", page).span())
            page = page[:indices[0]]+page[indices[1]:]
        except: pass

        try:
            indices = list(re.search("<script>(.|\n)*</script>", page).span())
            page = page[:indices[0]]+page[indices[1]:]
        except: pass

        try:
            indices = list(re.search("<style>(.|\n)*</style>", page).span())
            page = page[:indices[0]]+page[indices[1]:]
        except: pass

        #Remove comments
        current_idx = 0
        page1 = ""
        while True:
            try:
                indices = re.search("<!--(.|\n)*?-->", page[current_idx:]).span(0)#gives indeces of first comment match
                page1 += page[current_idx:current_idx+indices[0]]#Add part between comments
                current_idx = current_idx + indices[1]
            except:
                page1 += page[current_idx:]
                break
        page = page1


        #Remove comments
        current_idx = 0
        page1 = ""
        while True:
            try:
                indices = re.search("<.*?>", page[current_idx:]).span(0)#gives indeces of first comment match
                page1 += page[current_idx:current_idx+indices[0]]#Add part between comments
                current_idx = current_idx + indices[1]
            except:
                page1 += page[current_idx:]
                break
        page = page1

        page = page.replace("\t", " ").replace("\n"," ")

        return page
