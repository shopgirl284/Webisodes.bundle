PREFIX   = '/video/webisodes'
FEATURE_PREFIX = '%s/rss' % PREFIX

ICON = 'rss-feed-icon.png'

NAMESPACES = {'feedburner': 'http://rssnamespace.org/feedburner/ext/1.0'}
NAMESPACES2 = {'media': 'http://search.yahoo.com/mrss/'}
NAMESPACE_SMIL = {'smil': 'http://www.w3.org/2005/SMIL21/Language'}

import tools
import mediaobjects

####################################################################################################################
@route(FEATURE_PREFIX)
def MainMenu():

    oc = ObjectContainer(title2='RSS Feeds')
  
    shows = Dict["MyShows"]
    for show in shows:
        if show['type'] == 'rss':
            url = show["url"]
            thumb = show["thumb"]
            try:
                rss_page = XML.ElementFromURL(url)
                title = rss_page.xpath("//channel/title//text()")[0]
            except:
                oc.add(DirectoryObject(key=Callback(tools.URLError, url=url, show_type='rss'), title="Invalid or Incompatible URL", thumb=R('no-feed.png'), summary="The URL was either entered incorrectly or is incompatible with this channel."))
                continue
            # sometimes the description is blank and it gives an error, so we added this as a try
            try: description = rss_page.xpath("//channel/description//text()")[0]
            except: description = ''
            if not thumb:
                try: thumb = rss_page.xpath("//channel/image/url//text()")[0]
                except: thumb = R(ICON)
            oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type='rss', thumb=thumb), title=title, summary=description, thumb=thumb))

    oc.objects.sort(key = lambda obj: obj.title)

    oc.add(InputDirectoryObject(key=Callback(tools.AddShow, show_type='rss'), title="Add A RSS Feed", summary="Click here to add a new RSS Feed", thumb=R(ICON), prompt="Enter the full URL (including http://) for the RSS Feed you would like to add"))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no RSS feeds to list right now.")
    else:
        return oc
########################################################################################################################
# This is for producing items in a RSS Feeds.  We try to make most things optional so it accepts the most feed formats
# But each feed must have a title, date, and either a link or media_url
@route(PREFIX + '/showrss')
def ShowRSS(title, url, show_type, thumb):

# The ProduceRSS try above tells us if the RSS feed is the correct format. so we do not need to put this function's data pull in a try/except
    oc = ObjectContainer(title2=title)
    feed_title = title
    if show_type == 'vimeo':
        rss_url = url + '/videos/rss'
    else:
        rss_url = url
    xml = XML.ElementFromURL(rss_url)

    for item in xml.xpath('//item'):
        # All Items must have a title
        title = item.xpath('./title//text()')[0]
        # Try to pull the link for the item
        try: link = item.xpath('./link//text()')[0]
        except: link = None
        # Get the original link for feedburner feeds since they may have a Plex URL service
        try: link = item.xpath('./feedburner:origLink//text()', namespaces=NAMESPACES)[0]
        except: link = link
        # Test the link for a URL service
        if link:
            url_test = URLTest(link)
        else:
            url_test = 'false'
        # Feeds from archive.org load faster using the CreateObject() function versus the URL service.
        # Using CreateObject for Archive.org also catches items with no media and allows for feed that may contain both audio and video items
        if link and 'archive.org' in link:
            (link, url_test) = ArchiveFeeds(link)
      
        # Get media type for item
        try: media_type = item.xpath('.//media:content/@type', namespaces=NAMESPACES2)[0]
        except:
            try: media_type = item.xpath('.//enclosure/@type')[0]
            except: media_type = None
        #Log('the value of media_type is %s' %media_type)

        # If there is not a URL service, try to pull media url for the item
        if url_test == 'false':
            try:
                # First check for multiple media items
                medias = item.xpath('.//media:content', namespaces=NAMESPACES2)
                Log('the value of medias is %s' %medias)
                if len(medias) >1:
                    (media_url, media_type) = GetBestMedia(medias)
                # Otherwise pull the one media url
                else: media_url = item.xpath('.//media:content/@url', namespaces=NAMESPACES2)[0]
            except:
                try: media_url = item.xpath('.//enclosure/@url')[0]
                except: media_url = None
        else:
            media_url = None
        #Log("the value of media url is %s" %media_url)
        
        # Fix archive.org issue where it is using https instead of http sometimes for the media urls
        if media_url and media_url.startswith('https://archive.org/'):
            media_url = media_url.replace('https://', 'http://')
    
        # theplatform stream links are SMIL, despite being referenced in RSS as the underlying mediatype
        if media_url and 'link.theplatform.com' in media_url:
            media_url = GetSMIL(media_url)
    
        # If there in not a url service or media_url produced No URL service object and go to next entry
        if url_test == 'false' and not media_url:
            Log('The url test failed and returned a value of %s' %url_test)
            oc.add(DirectoryObject(key=Callback(URLNoService, title=title),title="No URL Service or Media Files for Video", thumb=R('no-feed.png'), summary='There is not a Plex URL service or link to media files for %s.' %title))
    
        else: 
            # Collect all other optional data for item
            try: date = item.xpath('./pubDate//text()')[0]
            except: date = None
            try: item_thumb = item.xpath('./media:thumbnail//@url', namespaces=NAMESPACES2)[0]
            except: item_thumb = None
            try:
                # The description actually contains pubdate, link with thumb and description so we need to break it up
                epDesc = item.xpath('./description//text()')[0]
                (summary, new_thumb) = SummaryFind(epDesc)
                if new_thumb:
                    item_thumb = new_thumb
            except:
                summary = None
            # Not having a value for the summary causes issues
            if not summary:
                summary = 'no summary'
            if item_thumb:
                thumb = item_thumb

            if url_test == 'true':
                # Build Video or Audio Object for those with a URL service
                # The date that go to the CreateObject() have to be processed separately so only process those with a URL service here
                if date:
                    date = Datetime.ParseDate(date)
                # Changed to reflect webisodes version should only apply if a video in added to the audio section by mistake
                if show_type == 'audio' or (media_type and 'audio' in media_type):
                    # I was told it was safest to use an album object and not a track object here since not sure what we may encounter
                    # But was getting errors with an AlbumObject so using TrackObject instead
                    # NEED TO TEST THIS WITH AN AUDIO SITE THAT HAS A URL SERVICE
                    oc.add(TrackObject(
                        url = link, 
                        title = title, 
                        summary = summary, 
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON)), 
                        originally_available_at = date
                    ))
                else:
                    oc.add(VideoClipObject(
                        url = link, 
                        title = title, 
                        summary = summary, 
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(ICON)), 
                        originally_available_at = date
                    ))
                oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)
            else:
                # Send those that have a media_url to the CreateObject function to build the media objects
                if '.m3u8' in media_url:
                    oc.add(mediaobjects.CreateLiveObject(title=title, m3u8_url=media_url, thumb=thumb))
                elif 'audio' in media_type:
                    oc.add(mediaobjects.CreateAudioObject(url=media_url, media_type=media_type, title=title, summary=summary, originally_available_at=date, thumb=thumb))
                else:
                    oc.add(mediaobjects.CreateVideoObject(url=media_url, media_type=media_type, title=title, summary=summary, originally_available_at=date, thumb=thumb))

    # Additional directories for deleting a show and adding images for a show
    # Moved to top since some feeds can be very long
    oc.add(DirectoryObject(key=Callback(tools.EditShow, url=url, title=feed_title), title="Edit %s" %feed_title, summary="Click here to edit this feed"))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos to display for this RSS feed right now.")      
    else:
        return oc

#############################################################################################################################
# This function breaks content from an RSS feed into pubdate, link with thumb and description 
@route(PREFIX + '/summaryfind')
def SummaryFind(epDesc):
  
    html = HTML.ElementFromString(epDesc)
    description = html.xpath('//p//text()')
    summary = ' '.join(description)
    if 'Tags:' in summary:
        summary = summary.split('Tags:')[0]
    try:
        item_thumb = html.cssselect('img')[0].get('src')
    except:
        item_thumb = None
    return (summary, item_thumb)

############################################################################################################################
# This is a function to test if there is a Plex URL service for  given url. 
#       if URLTest(url) == "true":
@route(PREFIX + '/urltest')
def URLTest(url):
    if URLService.ServiceIdentifierForURL(url) is not None:
        url_good = 'true'
    else:
        url_good = 'false'
    return url_good

############################################################################################################################
# This function is to show a directory for videos that do not have a URL service or a media stream URL value. 
# This way a directory entry for each incompatible URLs is shown, so any bad entries will still be listed with an explanation
@route(PREFIX + '/urlnoservice')
def URLNoService(title):
    return ObjectContainer(header="Error", message='There is no Plex URL service or media file link for the %s feed entry. A Plex URL service or a link to media files in the feed entry is required for this channel to create playable media. If all entries for this feed give this error, you can use the Delete button shown at the end of the feed entry listings to remove this feed' %title)

############################################################################################################################
# This function creates an error message for RSS Feed entries that have an unsupported media type and keeps a section of feeds
# from giving an error for the entire list of entries
@route(PREFIX + '/urlunsupported')
def URLUnsupported(url, title):
    return ObjectContainer(header="Error", message='The media for the %s feed entry is of a type that is not supported. If you get this error with all entries for this feed, you can use the Delete option shown at the end of the feed entry listings to remove this feed from the channel' %title)

#############################################################################################################################
# this function checks for Archive feeds and converts them to pull the media instead of using the URL service
# With Archive.org there is an issue where it is using https instead of http sometimes for the links and media urls
# and when this happens it causes errors so we have to check those urls here and change them
# Feeds from archive.org load faster using the CreateObject() function versus the URL service.
# Using CreateObject for Archive.org also catches items with no media and allows for feed that may contain both audio and video items
# If archive.org is sent to URL service, adding #video to the end of the link makes it load faster
@route(PREFIX + '/archivefeeds')
def ArchiveFeeds(link):
    
    link = link.replace('https://', 'http://')
    url_test = URLTest(link)
        
    # Feeds from archive.org load faster using the CreateObject() function versus the URL service.
    # Using CreateObject for Archive.org also catches items with no media and allows for feed that may contain both audio and video items
    # If archive.org is sent to URL service, adding #video to the end of the link makes it load faster
    #Log('the real value of url test for %s is %s' %(link, url_test))
    if link and 'archive.org' in link:
        url_test = 'false'

    return(link, url_test)
#############################################################################################################################
# this functions gets the best quality media stream for feeds that have multiple options
@route(PREFIX + '/getbestmedia')
def GetBestMedia(medias):

    # We try to pull the enclosure or the highest bitrate media:content. If no bitrate, the first one is taken.
    # There is too much variety in the way quality is specified to pull all and give quality options
    # This code can be added to only return media of type audio or video - [contains(@type,"video") or contains(@type,"audio")]
    bitrate = 0
    media_url = None
    media_type = None
    for media in medias:
        try: new_bitrate = int(media.get('bitrate', default=0))
        except: new_bitrate = 0
        if new_bitrate > bitrate:
            bitrate = new_bitrate
            media_url = media.get('url')
            #Log("taking media url %s with bitrate %s"  %(media_url, str(bitrate)))
            media_type = media.get('type')
            
    return(media_url, media_type)

#############################################################################################################################
# this functions gets the media url from the smil for link.platform feeds
# theplatform stream links are SMIL, despite being referenced in RSS as the underlying mediatype
@route(PREFIX + '/getsmil')
def GetSMIL(media_url):

    try: smil = XML.ElementFromURL(media_url)
    except: smil = None
    if smil:
        try:
            media_url = smil.xpath('//smil:video/@src', namespaces=NAMESPACE_SMIL)[0]
        except Exception as e:
            Log("Found theplatform.com link, but couldn't resolve stream: " + str(e))
            media_url = None
    else: media_url = None

    return media_url
#############################################################################################################################
# this checks to see if the RSS feed is a YouTube playlist. Currently this plugin does not work with YouTube Playlist
# THIS IS NOT BEING USED
@route(PREFIX + '/checkplaylist')
def CheckPlaylist(url):
    show_rss=''
    if url.find('playlist')  > -1:
        show_rss = 'play'
    else:
        show_rss = 'good'
    return show_rss
