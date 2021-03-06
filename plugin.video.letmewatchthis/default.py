'''
    letmewatchthis XBMC Addon
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
'''

import re
import string
import sys
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
import urlresolver
import xbmcgui

addon = Addon('plugin.video.letmewatchthis', sys.argv)
net = Net()

base_url = 'http://www.letmewatchthis.ch'

mode = addon.queries['mode']
play = addon.queries.get('play', None)

if play:
    try:
        addon.log_debug('fetching %s' % play)
        html = net.http_GET(play).content
    except urllib2.URLError, e:
        html = ''
        addon.log_error('got http error %d fetching %s' %
                        (e.code, web_url))
    
    links = {}
    for l in re.finditer('class="movie_version".+?quality_(.+?)>.+?url=(.+?)&domain=(.+?)&.+?"version_veiws">(.+?)</', html, re.DOTALL):
        q, url, host, views = l.groups()
        verified = l.group(0).find('star.gif') > -1
        link =  host.decode('base-64')
        if verified:
            link += ' [verified]'
        link += ' (%s)' % views.strip()
        links[url.decode('base-64')] = link
    

    playable = urlresolver.filter_urls(links.keys())
    
    if playable:
        readable = []
        for p in playable:
            readable.append(links[p])
        
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose your stream', readable)
        stream_url = urlresolver.resolve(playable[index])
    else:
        addon.log_error('no playable streams found')
        stream_url = False

    addon.resolve_url(stream_url)

elif mode == 'browse':
    browse = addon.queries.get('browse', False)
    letter = addon.queries.get('letter', False)
    section = addon.queries.get('section', '')
    page = addon.queries.get('page', 1)
    if letter:
        url = '%s/?letter=%s&sort=alphabet&page=%s&%s' % (base_url, letter, 
                                                          page, section)
        try:
            addon.log_debug('fetching %s' % url)
            html = net.http_GET(url).content
        except urllib2.URLError, e:
            html = ''
            addon.log_error('got http error %d fetching %s' %
                            (e.code, web_url))

        r = 'class="index_item.+?href="(.+?)".+?src="(.+?)".+?alt="Watch (.+?)"'
        regex = re.finditer(r, html, re.DOTALL)
        for s in regex:
            url, thumb, title = s.groups()
            addon.add_directory({'mode': 'series', 
                                 'url': base_url + url}, 
                                 title, 
                                 img=thumb)
        if html.find('> >> <'):
            addon.add_directory({'mode': 'browse', 
                                 'section': section,
                                 'page': int(page) + 1,
                                 'letter': letter}, 'Next Page')
        

    else:
            addon.add_directory({'mode': 'browse', 
                                 'section': section,
                                 'letter': '123'}, '#')
            for l in string.uppercase:
                addon.add_directory({'mode': 'browse', 
                                     'section': section,
                                     'letter': l}, l)
        
elif mode == 'series':
    url = addon.queries['url']
    try:    
        addon.log_debug('fetching %s' % url)
        html = net.http_GET(url).content
    except urllib2.URLError, e:
        html = ''
        addon.log_error('got http error %d fetching %s' %
                        (e.code, web_url))
                        
    regex = re.search('movie_thumb"><img src="(.+?)"', html)
    if regex:
        img = regex.group(1)
    else:
        addon.log_error('couldn\'t find image')
        img = ''
    
    seasons = re.search('tv_container(.+?)<div class="clearer', html, re.DOTALL)    
    if not seasons:
        addon.log_error('couldn\'t find seasons')
    else:
        for season in seasons.group(1).split('<h2>'):
            r = re.search('<a.+?>(.+?)</a>', season)
            if r:
                season_name = r.group(1)
            else:
                season_name = 'Unknown Season'
                addon.log_error('couldn\'t find season title')

            r = '"tv_episode_item".+?href="(.+?)">(.*?)</a>'
            episodes = re.finditer(r, season, re.DOTALL)
            for ep in episodes:
                url, title = ep.groups()
                title = re.sub('<[^<]+?>', '', title.strip())
                title = re.sub('\s\s+' , ' ', title)
                addon.add_video_item(base_url + url, {'title': '%s %s' % 
                                                 (season_name, title)}, img=img)


elif mode == 'main':
    addon.add_directory({'mode': 'browse', 'section': 'tv'}, 'TV')
    addon.add_directory({'mode': 'resolver_settings'}, 'Resolver Settings', 
                        is_folder=False)

elif mode == 'resolver_settings':
    urlresolver.display_settings()


if not play:
    addon.end_of_directory()


