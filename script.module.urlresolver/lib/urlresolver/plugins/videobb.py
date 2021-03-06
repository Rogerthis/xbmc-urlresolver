import re
from t0mm0.common.net import Net
import urllib2
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class VideobbResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "videobb"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()


    def get_media_url(self, web_url):
        #find video_id
        r = re.search('(?:/e/|/video/|v=)([0-9a-zA-Z]+)', web_url)
        if r:
            video_id = r.group(1)
        else:
            common.addon.log_error('videobb: video_id not found')
            return False

        #grab json info for this video
        json_url = 'http://videobb.com/player_control/settings.php?v=%s' % \
                                                                    video_id
        try:
            json = self.net.http_GET(json_url).content
        except urllib2.URLError, e:
            common.addon.log_error('videobb: got http error %d fetching %s' %
                                    (e.code, api_url))
            return False
            
        #find highest quality URL
        max_res = [240, 480, 99999][int(self.get_setting('q'))]
        r = re.finditer('"l".*?:.*?"(.+?)".+?"u".*?:.*?"(.+?)"', json)
        chosen_res = 0
        stream_url = False
        if r:
            for match in r:
                res, url = match.groups()
                res = int(res.strip('p'))
                if res > chosen_res and res <= max_res:
                    stream_url = url.decode('base-64')
                    chosen_res = res
        else:
            common.addon.log_error('videobb: stream url not found')
            return False

        return stream_url
       
        
    def valid_url(self, web_url):
        return re.match('http://(www.)?videobb.com/' + 
                        '(e/|video/|watch_video.php\?v=)' +
                        '[0-9A-Za-z]+', web_url)

    
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting label="Highest Quality" id="VideobbResolver_q" '
        xml += 'type="enum" values="240p|480p|Maximum" default="2" />\n'
        return xml
