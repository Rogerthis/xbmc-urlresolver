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

"""
RogerThis - 16/8/2011
Site: http://www.vidxden.com , http://www.divxden.com & http://www.vidbux.com
vidxden hosts both avi and flv videos
In testing there seems to be a timing issue with files coming up as not playable.
This happens on both the addon and in a browser.
"""

import re
import urllib
import urllib2
from t0mm0.common.net import Net

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class VidxdenResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vidxden"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()



    def get_media_url(self, web_url):
        
        """
        unpack_js and base36encode are from t0mm0's quick and dirty solution
        """
        
        def __unpack_js(p, k):
            '''emulate js unpacking code'''
            for x in range(len(k) - 1, -1, -1):
                if k[x]:
                    p = re.sub('\\b%s\\b' % __base36encode(x), k[x], p)
            return p
    
        
        def __base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
            """Convert positive integer to a base36 string. (from wikipedia)"""
            if not isinstance(number, (int, long)):
                raise TypeError('number must be an integer')
         
            # Special case for zero
            if number == 0:
                return alphabet[0]
     
            base36 = ''
     
            sign = ''
            if number < 0:
                sign = '-'
                number = - number
 
            while number != 0:
                number, i = divmod(number, len(alphabet))
                base36 = alphabet[i] + base36
 
            return sign + base36
        
        print web_url
        """ Human Verification """
        try:
            
            '''
            html = self.net.http_GET(web_url).content
            fcodenm=re.search('name="fname" type="hidden" value="(.+?)"',html).group(1)
            fcodeid=re.search('name="id" type="hidden" value="(.+?)"',html).group(1)
            self.net.http_POST(web_url, form_data={'op': 'download1','usr_login': ' ',
                                        'id': fcodeid, 'fname': fcodenm,'referer' : ' ',
                                        'method_free':'Continue to Video'})
            html = self.net.http_GET(web_url).content
            '''
            
            html = self.net.http_GET(web_url).content
            fcodenm=re.search('name="fname" type="hidden" value="(.+?)"',html).group(1)
            fcodeid=re.search('name="id" type="hidden" value="(.+?)"',html).group(1)
            values = {'op': 'download1','usr_login': ' ', 'id': fcodeid, 'fname': fcodenm,'referer' : ' ', 'method_free':'Continue to Video'}
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }
            data = urllib.urlencode(values)
            req = urllib2.Request(web_url, data, headers)
            response = urllib2.urlopen(req)
            html = response.read()
            
        except urllib2.URLError, e:
            common.addon.log_error('vidxden: got http error %d fetching %s' %
                                  (e.code, web_url))
            return False
        
             
        p = re.search('return p}.+?\'(.+?);\',',html).group(1)
        k0 = re.search('s1(.+?).split',html)
        if not k0:
            k0 = re.search('value(.+?).split',html).group(1)
            k1 = 'value' + str(k0)
        else:
            k1 = 's1' + str(k0.group(1))

        k = k1.split('|')
        
        decrypted_data = __unpack_js(p, k)
        print decrypted_data
        """ First checks for a flv url, then the if statement is for the avi url """
        r = re.search('file.+?\'.+?\'(.+?)\'.+?;s1', decrypted_data)
        if not r:
            r = re.search('src="(.+?)"', decrypted_data)
        if r:
            play_url = r.group(1)
        else:
            common.addon.log_error('movshare: stream url not found')
            return False

        print play_url
        final_url = play_url.replace('\\','') # couldn't find a better way to remove the leading backslash from the flv url
        print final_url
        return final_url
        
        

        
    def valid_url(self, web_url):
        return re.match('http://(?:www.)?(vidxden|divxden|vidbux).com/', web_url)
