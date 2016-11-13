PREFIX   = '/video/webisodes'
FEATURE_PREFIX = '%s/youtube' % PREFIX

SECTION_TITLE = 'YouTube'

BASE_URL = 'http://www.youtube.com'
ICON = 'youtube-icon.png'

import tools

####################################################################################################################
@route(FEATURE_PREFIX)
def MainMenu(title, url, thumb=''):

    oc = ObjectContainer(title2=title)
    if not thumb:
        thumb = HTML.ElementFromURL(url).xpath('//meta[@property="og:image"]/@content')[0]

    oc.add(DirectoryObject(key=Callback(YouTubeVideos, title="%s Videos" %title, url=url+'/videos?flow=list'), title="%s Videos" %title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
    oc.add(DirectoryObject(key=Callback(PlaylistYouTube, title="%s PlayLists" %title, url=url), title="%s PlayLists" %title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    oc.add(DirectoryObject(key=Callback(tools.EditShow, url=url, title=title), title="Edit this Show", summary="Click here to edit this YouTube Show"))

    return oc
####################################################################################################################
# This function creates a list of playlists for a YouTube user or channel
@route(FEATURE_PREFIX + '/playlistyoutube')
def PlaylistYouTube(title, url, json_url=''):

    oc = ObjectContainer(title2=title)
    pl_url = url + '/playlists?sort=dd&view=1'
    (content, more_json) = YTcontent(pl_url, json_url)
    data = HTML.ElementFromString(content)

    for playlist in data.xpath('//li[contains(@class, "grid-item")]'):
        pl_title = playlist.xpath('.//div[@class="yt-lockup-content"]/h3/a/@title')[0]
        pl_url = playlist.xpath('.//div[@class="yt-lockup-content"]/h3/a/@href')[0]
        pl_url = BASE_URL + pl_url
        try: pl_thumb = playlist.xpath('.//img/@src')[0]
        except: pl_thumb = playlist.xpath('.//img/@data-thumb')[0]
        pl_desc = playlist.xpath('.//span[@class="formatted-video-count-label"]//text()')[0]
        oc.add(DirectoryObject(key=Callback(YouTubeVideos, title=pl_title, url=pl_url),
            title = pl_title,
            summary = pl_desc,
            thumb = Resource.ContentsOfURLWithFallback(url=pl_thumb, fallback=ICON)
        ))

    # Check to see if there are any further results available.
    if more_json:
        oc.add(NextPageObject(
            key = Callback(PlaylistYouTube, title = title, url = url, json_url = more_json), 
            title = L("Next Page ...")
        ))

    if len(oc) < 1:
        return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
    else:
        return oc

####################################################################################################################
# This function will produce results from a playlist or user/channel video page
@route(FEATURE_PREFIX + '/youtubevideos', pl_only=bool)
def YouTubeVideos(title, url, json_url='', pl_only=False):

    oc = ObjectContainer(title2=title)
    (content, more_json) = YTcontent(url, json_url)
    data = HTML.ElementFromString(content)
    if 'PL' in url:
        video_list = data.xpath('//table[@id="pl-video-table"]//tr')
    else:
        video_list = data.xpath('//li[contains(@class, "feed-item-container")]')

    for video in video_list:
        video_url = video.xpath('.//a/@href')[0].split('&')[0]
        if not video_url.startswith('http://'):
            video_url = BASE_URL + video_url
        try: video_title = video.xpath('./@data-title')[0]
        except: video_title = video.xpath('.//a/@title')[0]
        try: thumb = video.xpath('.//img/@data-thumb')[0]
        except: thumb = video.xpath('.//img/@src')[0]
        try: duration = Datetime.MillisecondsFromString(video.xpath('.//div[@class="timestamp"]/span//text()')[0])
        except:
            try: duration = Datetime.MillisecondsFromString(video.xpath('.//span[@class="video-time"]//text()')[0])
            except: duration = 0

        oc.add(VideoClipObject(
            url = video_url,
            title = video_title,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
            duration = duration
        ))

    # List deletion and image add options here
    if pl_only:
        oc.add(DirectoryObject(key=Callback(tools.EditShow, url=url, title=title), title="Edit this Show", summary="Click here to edit this YouTube Show"))

    # Check to see if there are any further results available.
    if more_json:
        oc.add(NextPageObject(
            key = Callback(YouTubeVideos, title = title, url = url, json_url = more_json, pl_only=False), 
            title = L("Next Page ...")
        ))
    
    if len(oc) < 1:
        return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this show or playlist right now'))
    else:
        return oc

#############################################################################################################################
# This function pulls the content and next page json url and is used by both YouTube sections above
@route(FEATURE_PREFIX + '/ytcontent')
def YTcontent(url, json_url=''):
  
    # If it is a second page then we use the json we pulled from the first page for content and to find the next page
    load_more = ''
    if json_url:
        try:
            json = JSON.ObjectFromURL(json_url)
            content = json['content_html']
            load_more = json['load_more_widget_html'].strip()
        except:
            return ObjectContainer(header=L('URL Error'), message=L('Unable to access the next page URL.'))
    else:
        try:
            content = HTTP.Request(url, cacheTime=CACHE_1HOUR).content
        except:
            return ObjectContainer(header=L('URL Error'), message=L('Unable to access the URL for this show.'))
      
    # Check to see if there are any further results available.
    try: more_videos = HTML.ElementFromString(content).xpath('//button[contains(@class, "load-more-button")]/@data-uix-load-more-href')[0]
    except:
        try: more_videos = HTML.ElementFromString(load_more).xpath('//@data-uix-load-more-href')[0]
        except: more_videos = None
    
    if more_videos:
        json_url = 'https://www.youtube.com' + more_videos
    else:
        json_url = None

    return (content, json_url)

