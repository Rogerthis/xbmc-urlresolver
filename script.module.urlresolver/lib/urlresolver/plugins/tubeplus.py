"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from t0mm0.common.net import Net
import urllib2
import urlresolver
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay import Plugin
import xbmcgui

class TubeplusResolver(Plugin, UrlResolver):
    implements = [UrlResolver]
    name = "tubeplus.me"
    
    def __init__(self):
        self.net = Net()

    def get_media_url(self, web_url):
        #get list
        try:
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            common.addon.log_error('tubeplus: got http error %d fetching %s' %
                                    (e.code, web_url))
            return False
            
        r = '"none" href="(.+?)"'
        host_urls = []
        regex = re.finditer(r, html, re.DOTALL)

        for s in regex:
            host_urls.append(s.group(1)) 
        
        #only keep urls we have resolver plugins for
        filtered_urls = urlresolver.filter_urls(host_urls)
        
        l = len(filtered_urls)
        
        #no playable links found
        if l == 0:
            return False

        #1 playable link found - just play it
        elif l == 1:
            return urlresolver.resolve(filtered_urls[0])

        #more than 1 playable link found, let user choose
        else:
            dialog = xbmcgui.Dialog()
            index = dialog.select('Choose your stream', filtered_urls)
            return urlresolver.resolve(filtered_urls[index])
                    
    def valid_url(self, web_url):
        return re.match('http://(www.)?tubeplus.me/player/\d+', web_url)

