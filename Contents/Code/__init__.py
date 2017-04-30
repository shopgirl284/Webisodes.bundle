TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

RSS_ICON = 'rss-feed-icon.png'
YOUTUBE_ICON = 'youtube-icon.png'
VIMEO_ICON = 'vimeo-icon.png'
DAILYMOTION_ICON = 'dailymotion-icon.png'

###################################################################################################
# Set up containers for all possible objects
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR 

    #This Checks to see if there is a list of shows
    if Dict['MyShows'] == None:
        Dict["MyShows"] = []
    else:
        Log(Dict['MyShows'])

###################################################################################################
# This Main Menu provides a section for each type of show. It is hardcoded in since the types of show have to be set and preprogrammed in
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

def MainMenu():

    oc = ObjectContainer()
  
    oc.add(DirectoryObject(key=Callback(OtherSections, title="Vimeo Shows", show_type='vimeo'), title="Vimeo Shows", thumb=R(VIMEO_ICON)))
    oc.add(DirectoryObject(key=Callback(OtherSections, title="YouTube Shows", show_type='youtube'), title="YouTube Shows", thumb=R(YOUTUBE_ICON)))
    oc.add(DirectoryObject(key=Callback(OtherSections, title="Daily Motion Shows", show_type='dailymotion'), title="Daily Motion Shows", thumb=R(DAILYMOTION_ICON)))
    oc.add(DirectoryObject(key=Callback(LiveMenu, title="Live Feeds"), title="Live Feeds"))
    oc.add(DirectoryObject(key=Callback(rss.MainMenu), title="RSS Feeds", thumb=R(RSS_ICON)))
    oc.add(DirectoryObject(key=Callback(tools.MainMenu), title="Channel Tools", thumb=R(ICON), summary="Click here to for reset options, extras and special instructions"))

    return oc
#############################################################################################################################
# This is a function lists the shows for each show type other than RSS feeds (html shows)
@route(PREFIX + '/othersections')
def OtherSections(title, show_type):
    oc = ObjectContainer(title2=title)
    section_title = title.split()[0]
    shows = Dict["MyShows"]
    for show in shows:
        if show['type'] == show_type:
            try: title = show["name"]
            except: title = ''
            thumb = show["thumb"]
            url = show["url"]
            try:
                page = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
            except:
                oc.add(DirectoryObject(key=Callback(tools.URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL - %s" %url, summary="The URL entered for this show was either incorrect or not in the proper format for use with this channel."))
                continue

            try: description = page.xpath("//head//meta[@name='description']//@content")[0] 
            except: description = '' 
            if not title:
                # YouTube change the format of its playlist urls from @property="og:title" to @name="title", others use @name="title"
                try: title = page.xpath('//head//meta[@property="og:title" or @name="title"]//@content')[0] 
                except: 
                    try: title = page.xpath('//title/text()')[0] 
                    except: title = 'No title found' 
            if not thumb:
                try: thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
                # this is for youtube playlists images  
                except:
                    try: thumb = page.xpath('//div[@class="pl-header-thumb"]/img/@src')[0]
                    except: thumb = R(ICON)
            if not thumb.startswith('http'):
                thumb = 'http:' + thumb
            # here we send the different types of shows to be processed
            # YouTube shows
            if show_type == 'youtube':
                if '=PL' in url:
                    oc.add(DirectoryObject(key=Callback(youtube.YouTubeVideos, title=title, url=url, pl_only=True), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
                else:
                    oc.add(DirectoryObject(key=Callback(youtube.MainMenu, title=title, url=url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
            # Daily Motion shows
            elif show_type == 'dailymotion':
                vid_type = 'user'
                try:
                    dm_id = page.xpath('//head//meta[@property="al:ios:url"]//@content')[0].split('channel/')[1].split('/')[0]
                    oc.add(DirectoryObject(key=Callback(dailymotion.MainMenu, title=title, url=url, vid_type=vid_type, dm_id=dm_id, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
                # Playlist do not have the ID in the meta tags, so pull if from the url
                except:
                    try:
                        dm_id = url.split('playlist/')[1].split('_')[0]
                        vid_type = 'playlist'
                        oc.add(DirectoryObject(key=Callback(dailymotion.DailyMotionVideo, title=title, url=url, vid_type=vid_type, dm_id=dm_id, pl_only=True), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
                    except:
                        # Need this except if both id pulls fail since this is necessary for daily motion videos
                        Log('The id pull failed for %s for Daily Motion' %url)
                        oc.add(DirectoryObject(key=Callback(tools.URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL - %s" %url, summary="The URL entered for this show was either incorrect or not in the proper format for use with this channel."))
            # Vimeo shows
            # Vimeo shows are sent to the RSS feed section since they use xml
            else:
                oc.add(DirectoryObject(key=Callback(rss.ShowRSS, title=title, url=url, show_type=show_type, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))

    oc.objects.sort(key = lambda obj: obj.title)

    oc.add(InputDirectoryObject(key=Callback(tools.AddShow, show_type=show_type), title="Add A New %s Show" %section_title, summary="Click here to add a new show for the %s section" %section_title, thumb=R(ICON), prompt="Enter the full URL (including http://) for the show you would like to add"))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no shows to list right now.")
    else:
        return oc
#############################################################################################################################
# This is a function lists the shows for each show type other than RSS feeds (html shows)
@route(PREFIX + '/livemenu')
def LiveMenu(title):
    oc = ObjectContainer(title2=title)
    shows = Dict["MyShows"]
    for show in shows:
        if show['type'] == 'live':
            thumb = show["thumb"]
            title = show["name"]
            oc.add(DirectoryObject(key=Callback(LiveFeeds, m3u8=show["url"], title=title, thumb=thumb), title=title, thumb=thumb))

    oc.objects.sort(key = lambda obj: obj.title)
    oc.add(InputDirectoryObject(key=Callback(tools.AddShow, show_type="live"), title="Add A New Live Feed", summary="Click here to add a new Live Feed", thumb=R(ICON), prompt="Enter the full URL (including http://) for the live feed you would like to add"))

    if len(oc) < 1:
        return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
    else:
        return oc

####################################################################################################
# This function will produce a live feed listing and additions
@route(PREFIX + '/livefeeds')
def LiveFeeds(title, m3u8, thumb):

    oc = ObjectContainer(title2=title)
    oc.add(mediaobjects.CreateLiveObject(title=title, m3u8_url=m3u8, thumb=thumb))
    oc.add(DirectoryObject(key=Callback(tools.EditShow, url=m3u8, title=title), title="Edit Show", summary="Click here to edit this Live Feed"))
    return oc

###################################################################################################
# Import all of the files that have the functions for the various sections/website options of the channel

import youtube
import dailymotion
import tools
import rss
import mediaobjects
