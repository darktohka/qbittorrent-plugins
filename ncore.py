#VERSION: 1.2
#AUTHORS: Derzsi Dániel (daniel@tohka.us)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

try:
    from urllib import urlencode, unquote
    from urllib2 import build_opener, HTTPCookieProcessor
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlencode, unquote, urlparse, parse_qs
    from urllib.request import build_opener, HTTPCookieProcessor

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

from novaprinter import prettyPrinter
import os

class ncore(object):
    # EDIT YOUR CREDENTIALS HERE
    username = 'your_username'
    password = 'your_password'
    MAX_PAGE_NUMBER = 10

    # Internal values
    login_data = {'nev': username, 'pass': password,
                  'set_lang': 'hu', 'submitted': '1'}
    session_cookie = 'PHPSESSID'
    url = 'https://ncore.pro'
    name = 'nCore'

    supported_categories = {
        'all': 'xvid_hun,xvid,dvd_hun,dvd,dvd9_hun,dvd9,hd_hun,hd,xvidser_hun,xvidser,dvdser_hun,dvdser,hdser_hun,hdser,mp3_hun,mp3,lossless_hun,lossless,clip,game_iso,game_rip,console,iso,misc,mobil,ebook_hun,ebook,xxx_xvid,xxx_dvd,xxx_imageset,xxx_hd',
        'movies': 'xvid_hun,xvid,dvd_hun,dvd,dvd9_hun,dvd9,hd_hun,hd',
        'tv': 'xvidser_hun,xvidser,dvdser_hun,dvdser,hdser_hun,hdser',
        'music': 'mp3_hun,mp3,lossless_hun,lossless,clip',
        'games': 'game_iso,game_rip,console',
        'software': 'iso,misc,mobil',
        'books': 'ebook_hun,ebook'
    }

    def sign_in(self, query=''):
        # Check if we have set credentials
        if self.username == 'your_username' or self.password == 'your_password':
            self.handle_error('You have not updated your credentials before installing the plugin', query)
            return False

        # Init the cookie handler.
        jar = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(jar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        # Sign in.
        url_cookie = self.opener.open(self.url + '/login.php', urlencode(self.login_data).encode('utf-8'))

        # Verify cookies
        cookie_names = [cookie.name for cookie in jar]

        if self.session_cookie not in cookie_names:
            self.handle_error('Could not log in. PHP session cookie missing', query)
            return False

        # Check if we haven't been sent back to the login page
        login_page = url_cookie.read().decode('utf-8')

        if 'login.php' in login_page:
            self.handle_error('Could not log in. Your credentials are invalid! Please wait 5 minutes between attempts', query)
            return False

        return True

    class NCoreParser(HTMLParser):

        def __init__(self, results, url, count=-1):
            HTMLParser.__init__(self)
            self.results = results
            self.url = url
            self.count = count
            self.key = None
            self.nextData = None
            self.torrent = None

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            className = attrs.get('class')

            if tag == 'link' and 'href' in attrs:
                queries = parse_qs(urlparse(attrs['href']).query)

                if queries.get('key'):
                    self.key = queries['key'][0]

            if tag == 'div' and className == 'box_torrent':
                self.torrent = {'engine_url': self.url}

            if not self.torrent:
                return

            if tag == 'a':
                link = attrs.get('href')

                if 'title' in attrs:
                    name = attrs['title']

                    # In case the torrents have to be put into order
                    if self.count > 0:
                        name = '{}. {}'.format(self.count, name)
                        self.count += 1

                    self.torrent['name'] = name
                    self.torrent['desc_link'] = self.url + '/' + link
                    self.torrent['link'] = self.url + '/' + \
                        link.replace('details', 'download') + \
                        '&key=' + self.key
                elif link and 'peers' in link:
                    self.nextData = 'seeds' if 'seeds' not in self.torrent else 'leech'
            elif tag == 'div' and className:
                if className.startswith('box_meret'):
                    self.nextData = 'size'
                elif className.startswith('box_feltolto'):
                    self.handle_torrent_end()

        def handle_data(self, data):
            if self.nextData:
                self.torrent[self.nextData] = data
                self.nextData = None

        def handle_torrent_end(self):
            if not self.torrent:
                return

            prettyPrinter(self.torrent)
            self.results.append(self.torrent)
            self.torrent = None

    def search(self, what, cat='all'):
        if not self.sign_in(what):
            return

        what = what.strip()
        page = 1
        count = 1
        category = self.supported_categories[cat]

        while page <= self.MAX_PAGE_NUMBER:
            results = []

            if what == '.':
                url = '{}/torrents.php?miszerint=fid&hogyan=DESC&tipus=kivalasztottak_kozott&kivalasztott_tipus={}&oldal={}'.format(
                    self.url, category, page)
            else:
                # Disable sorting
                url = '{}/torrents.php?miszerint=seeders&hogyan=DESC&tipus=kivalasztottak_kozott&mire={}&kivalasztott_tipus={}&oldal={}'.format(
                    self.url, what, category, page)
                count = -1

            request = self.opener.open(url)
            data = request.read().decode('utf-8')

            parser = self.NCoreParser(results, self.url, count)
            parser.feed(data)
            parser.close()

            count = parser.count

            if not results:
                break

            page += 1

    def handle_error(self, error, search_query):
        current_file = os.path.realpath(__file__)

        prettyPrinter({
            'seeds': 0,
            'size': '0',
            'leech': 0,
            'engine_url': self.url,
            'link': 'https://ncore.pro',
            'desc_link': 'https://github.com/darktohka/qbittorrent-plugins/blob/master/README.md',
            'name': "nCore error: {}. Please edit file: '{}' to set your username and password. Your search was: '{}'".format(error, current_file, unquote(search_query))
        })
