TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

RSS_ICON = 'rss-feed-icon.png'
YOUTUBE_ICON = 'youtube-icon.png'
VIMEO_ICON = 'vimeo-icon.png'
DAILYMOTION_ICON = 'dailymotion-icon.png'

SHOW_DATA = 'data.json'
NAMESPACES = {'feedburner': 'http://rssnamespace.org/feedburner/ext/1.0'}
NAMESPACES2 = {'media': 'http://search.yahoo.com/mrss/'}
NAMESPACE_SMIL = {'smil': 'http://www.w3.org/2005/SMIL21/Language'}

YouTube_URL = 'http://www.youtube.com'
VIMEO_URL = 'http://vimeo.com/'
DAILYMOTION_URL = 'http://www.dailymotion.com/'

http = 'http:'

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
  oc.add(DirectoryObject(key=Callback(SectionRSS, title="RSS Feeds"), title="RSS Feeds", thumb=R(RSS_ICON)))
  oc.add(DirectoryObject(key=Callback(SectionTools, title="Channel Tools"), title="Channel Tools", thumb=R(ICON), summary="Click here to for reset options, extras and special instructions"))

  return oc
#########################################################################################################################
# For RSS Feeds (xml data pulls)
@route(PREFIX + '/sectionrss')
def SectionRSS(title):

  oc = ObjectContainer(title2=title)
  shows = Dict["MyShows"]
  for show in shows:
    if show['type'] == 'rss':
      url = show["url"]
      thumb = show["thumb"]
      try:
        rss_page = XML.ElementFromURL(url)
        title = rss_page.xpath("//channel/title//text()")[0]
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type='rss'), title="Invalid or Incompatible URL", summary="The URL was either entered incorrectly or is incompatible with this channel."))
        continue
      # sometimes the description is blank and it gives an error, so we added this as a try
      try: description = rss_page.xpath("//channel/description//text()")[0]
      except: description = ''
      if not thumb:
        try: thumb = rss_page.xpath("//channel/image/url//text()")[0]
        except: thumb = R(RSS_ICON)
      oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type='rss', thumb=thumb), title=title, summary=description, thumb=thumb))
        
  oc.objects.sort(key = lambda obj: obj.title)

  oc.add(InputDirectoryObject(key=Callback(AddShow, show_type='rss'), title="Add A RSS Feed", summary="Click here to add a new RSS Feed", thumb=R(ICON), prompt="Enter the full URL (including http://) for the RSS Feed you would like to add"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no RSS Feed shows to list right now.")
  else:
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
      thumb = show["thumb"]
      url = show["url"]
      try:
        page = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
        # YouTube change the format of its playlist urls from @property="og:title" to @name="title", others use @name="title"
        #title = page.xpath('//head//meta[@property="og:title" or @name="title"]//@content')[0]
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL - %s" %url, summary="The URL entered for this show was either incorrect or not in the proper format for use with this channel."))
        continue

      title = page.xpath('//head//meta[@property="og:title" or @name="title"]//@content')[0] 
      description = page.xpath("//head//meta[@name='description']//@content")[0] 
      if not thumb:
        try: thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
        # this is for youtube playlists images  
        except:
            try: thumb = page.xpath('//div[@class="pl-header-thumb"]/img/@src')[0]
            except: thumb = R(ICON)
        if not thumb.startswith('http'):
          thumb = http + thumb
      # here we send the different types of shows to be processed
      # YouTube shows
      if show_type == 'youtube':
        if '=PL' in url:
          oc.add(DirectoryObject(key=Callback(YouTubeVideos, title=title, url=url, pl_only=True), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
        else:
          oc.add(DirectoryObject(key=Callback(YouTubeSections, title=title, url=url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
      # Daily Motion shows
      elif show_type == 'dailymotion':
        vid_type = 'user'
        try:
          dm_id = page.xpath('//head//meta[@property="al:ios:url"]//@content')[0].split('channel/')[1].split('/')[0]
          oc.add(DirectoryObject(key=Callback(DailyMotionSections, title=title, url=url, vid_type=vid_type, dm_id=dm_id, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
        # Playlist do not have the ID in the meta tags, so pull if from the url
        except:
          try:
            dm_id = url.split('playlist/')[1].split('_')[0]
            vid_type = 'playlist'
            oc.add(DirectoryObject(key=Callback(DailyMotionVideo, title=title, url=url, vid_type=vid_type, dm_id=dm_id, pl_only=True), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))
          except:
            # Need this except if both id pulls fail since this is necessary for daily motion videos
            Log('The id pull failed for %s for Daily Motion' &url)
            oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL - %s" %url, summary="The URL entered for this show was either incorrect or not in the proper format for use with this channel."))
      # Vimeo shows
      # Vimeo shows are sent to the RSS feed section since they use xml
      else:
        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type=show_type, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb), summary=description))

  oc.objects.sort(key = lambda obj: obj.title)

  oc.add(InputDirectoryObject(key=Callback(AddShow, show_type=show_type), title="Add A New %s Show" %section_title, summary="Click here to add a new show for the %s section" %section_title, thumb=R(ICON), prompt="Enter the full URL (including http://) for the show you would like to add"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no shows to list right now.")
  else:
   return oc

#######################################################################################################################
# This is the section for instructions and resetting Dict[] files
@route(PREFIX + '/sectiontools')
def SectionTools (title):

  oc = ObjectContainer(title2=title)
  if Client.Platform == 'Roku':
    oc.add(DirectoryObject(key=Callback(RokuUsers, title="Special Instructions for Roku Users"), title="Special Instructions for Roku Users", thumb=R(ICON), summary="Click here to see special instructions necessary for Roku Users to add shows to this channel"))
  if Client.Platform in ('Chrome', 'Firefox', 'Edge', 'Safari', 'Internet Explorer'):
    oc.add(DirectoryObject(key=Callback(PlexWebUsers, title="Special Instructions for Plex Web Users"), title="Special Instructions for Plex Web Users", thumb=R(ICON), summary="Click here to see special instructions for Plex Web Users to add shows to this channel"))
  oc.add(DirectoryObject(key=Callback(ResetShows, title="Clear All Shows"), title="Clear All Shows", thumb=R(ICON), summary="Click here to remove all shows from this channel"))
  oc.add(DirectoryObject(key=Callback(LoadData), title="Replace Show List with JSON", thumb=R(ICON), summary="Click here to replace your show list with those in the data.json file"))
  oc.add(DirectoryObject(key=Callback(AddData), title="Add Shows from the JSON to my Current List", thumb=R(ICON), summary="Click here to add the data.json file to your existing list"))

  return oc

########################################################################################################################
# this is special instructions for Roku users
@route(PREFIX + '/rokuusers')
def RokuUsers (title):
  return ObjectContainer(header="Special Instructions for Roku Users", message="Remoku (www.remoku.tv) makes it easy to add new shows by cutting and pasting URLs from your browser.")

########################################################################################################################
# this is special instructions for Plex Web users
@route(PREFIX + '/plexwebusers')
def PlexWebUsers (title):
  return ObjectContainer(header="Special Instructions for Plex Web Users", message="Plex Web users can add new shows by pasting or typing the URLs in the Search Box at the top of the page while in the show section for that show type. A pop-up message will confirm if your new show has been added. New shows may not be visible for 24 hours, based on your browser cache settings.")

#############################################################################################################################
# The FUNCTION below can be used to reload the original data.json file if errors occur and you need to reset the program
@route(PREFIX + '/resetshows')
def ResetShows(title):
  Dict["MyShows"] = []
  return ObjectContainer(header="Cleared", message='All shows have been removed from this channel')

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
    # The link is not needed since these have a media url, but there may be a feedburner feed that has a Plex URL service
    try:
      new_url = item.xpath('./feedburner:origLink//text()', namespaces=NAMESPACES)[0]
      link = new_url
    except:
      pass
    if link and link.startswith('https://archive.org/'):
      # With Archive.org there is an issue where it is using https instead of http sometimes for the links and media urls
      # and when this happens it causes errors so we have to check those urls here and change them
      link = link.replace('https://', 'http://')
    # Test the link for a URL service
    if link:
      url_test = URLTest(link)
    else:
      url_test = 'false'
    # Feeds from archive.org load faster using the CreateObject() function versus the URL service.
    # Using CreateObject for Archive.org also catches items with no media and allows for feed that may contain both audio and video items
    # If archive.org is sent to URL service, adding #video to the end of the link makes it load faster
    if link and 'archive.org' in link:
      url_test = 'false'
      
    # Try to pull media url for item
    if url_test == 'false':
    # We try to pull the enclosure or the highest bitrate media:content. If no bitrate, the first one is taken.
    # There is too much variety in the way quality is specified to pull all and give quality options
    # This code can be added to only return media of type audio or video - [contains(@type,"video") or contains(@type,"audio")]
      try:
        # So first get the first media url and media type in case there are not multiples it will not go through the loop
        media_url = item.xpath('.//media:content/@url', namespaces=NAMESPACES2)[0]
        media_type = item.xpath('.//media:content/@type', namespaces=NAMESPACES2)[0]
        # Get a list of medias
        medias = item.xpath('.//media:content', namespaces=NAMESPACES2)
        bitrate = 0
        for media in medias:
          try: new_bitrate = int(media.get('bitrate', default=0))
          except: new_bitrate = 0
          if new_bitrate > bitrate:
            bitrate = new_bitrate
            media_url = media.get('url')
            #Log("taking media url %s with bitrate %s"  %(media_url, str(bitrate)))
            media_type = media.get('type')
      except:
        try:
          media_url = item.xpath('.//enclosure/@url')[0]
          media_type = item.xpath('.//enclosure/@type')[0]
        except:
          Log("no media:content objects found in bitrate check")
          media_url = None
          media_type = None
    else:
      # If the URL test was positive we do not need a media_url
      media_url = None
      # We do need to try to get a media type though so it will process it with the right player
      # This should not be necessary it added in the right group but just a extra level of security
      try: media_type = item.xpath('.//enclosure/@type')[0]
      except:
        try: media_type = item.xpath('.//media:content/@type', namespaces=NAMESPACES2)[0]
        except: media_type = None

    #Log("the value of media url is %s" %media_url)
    # With Archive.org there is an issue where it is using https instead of http sometimes for the media urls
    # and when this happens it causes errors so we have to check those urls here and change them
    if media_url and media_url.startswith('https://archive.org/'):
      media_url = media_url.replace('https://', 'http://')

    # theplatform stream links are SMIL, despite being referenced in RSS as the underlying mediatype
    if media_url and 'link.theplatform.com' in media_url:
      smil = XML.ElementFromURL(media_url)
      try:
        media_url = smil.xpath('//smil:video/@src', namespaces=NAMESPACE_SMIL)[0]
      except Exception as e:
        Log("Found theplatform.com link, but couldn't resolve stream: " + str(e))
        media_url = None
    
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
            thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), 
            originally_available_at = date
          ))
        else:
          oc.add(VideoClipObject(
            url = link, 
            title = title, 
            summary = summary, 
            thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), 
            originally_available_at = date
          ))
        oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)
      else:
        # Send those that have a media_url to the CreateObject function to build the media objects
        oc.add(CreateObject(url=media_url, media_type=media_type, title=title, summary=summary, originally_available_at=date, thumb=thumb))
   
  # Additional directories for deleting a show and adding images for a show
  # Moved to top since some feeds can be very long
  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=feed_title), title="Delete %s" %feed_title, summary="Click here to delete this feed"))
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=feed_title, url=url), title="Add Image For %s" %feed_title, summary="Click here to add an image url for this feed", prompt="Enter the full URL (including http://) for the image you would like displayed for this RSS Feed"))
   
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this RSS feed right now.")      
  else:
    return oc

####################################################################################################
# This function creates an media object container for RSS feeds that have a link to the media file in the feed
@route(PREFIX + '/createobject')
def CreateObject(url, media_type, title, originally_available_at, thumb, summary, include_container=False):

  local_url=url.split('?')[0]
  audio_codec = AudioCodec.AAC
  # Since we want to make the date optional, we need to handle the Datetime.ParseDate() as a try in case it is already done or blank
  try:
    originally_available_at = Datetime.ParseDate(originally_available_at)
  except:
    pass
  if local_url.endswith('.mp3'):
    container = 'mp3'
    audio_codec = AudioCodec.MP3
  elif  local_url.endswith('.m4a') or local_url.endswith('.mp4') or local_url.endswith('MPEG4') or local_url.endswith('h.264'):
    container = Container.MP4
  elif local_url.endswith('.flv') or local_url.endswith('Flash+Video'):
    container = Container.FLV
  elif local_url.endswith('.mkv'):
    container = Container.MKV
  else:
    Log('container type is None')
    container = ''

  if 'audio' in media_type:
    # This gives errors with AlbumObject, so it has to be a TrackObject
    object_type = TrackObject
  elif 'video' in media_type:
    object_type = VideoClipObject
  else:
    Log('This media type is not supported')
    new_object = DirectoryObject(key=Callback(URLUnsupported, url=url, title=title), title="Media Type Not Supported", summary='The file %s is not a type currently supported by this channel' %url)
    return new_object
    
  new_object = object_type(
    key = Callback(CreateObject, url=url, media_type=media_type, title=title, summary=summary, originally_available_at=originally_available_at, thumb=thumb, include_container=True),
    rating_key = url,
    title = title,
    summary = summary,
    thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON),
    originally_available_at = originally_available_at,
    items = [
      MediaObject(
        parts = [
          PartObject(key=url)
            ],
            container = container,
            audio_codec = audio_codec,
            audio_channels = 2
      )
    ]
  )

  if include_container:
    return ObjectContainer(objects=[new_object])
  else:
    return new_object
#############################################################################################################################
# This function creates directories for YouTube users and channels
@route(PREFIX + '/youtubesections')
def YouTubeSections(title, url, thumb=''):
  
  oc = ObjectContainer(title2=title)

  oc.add(DirectoryObject(key=Callback(YouTubeVideos, title="%s Videos" %title, url=url+'/videos?flow=list'), title="%s Videos" %title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
  oc.add(DirectoryObject(key=Callback(PlaylistYouTube, title="%s PlayLists" %title, url=url), title="%s PlayLists" %title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=title), title="***DELETE THE %s SHOW***" %title, summary="Click here to delete this YouTube Show"))
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=title, url=url), title="Add a Custom Image For %s" %title, summary="Add an alternative image url for this show", prompt="Enter the full URL (including http://) for an existing online image"))

  return oc
####################################################################################################################
# This function creates a list of playlists for a YouTube user or channel
@route(PREFIX + '/playlistyoutube')
def PlaylistYouTube(title, url, json_url=''):

  oc = ObjectContainer(title2=title)
  pl_url = url + '/playlists?sort=dd&view=1'
  (content, more_json) = YTcontent(pl_url, json_url)
  data = HTML.ElementFromString(content)

  for playlist in data.xpath('//li[contains(@class, "grid-item")]'):
    pl_title = playlist.xpath('.//div[@class="yt-lockup-content"]/h3/a/@title')[0]
    pl_url = playlist.xpath('.//div[@class="yt-lockup-content"]/h3/a/@href')[0]
    pl_url = YouTube_URL + pl_url
    pl_thumb = playlist.xpath('.//img/@src')[0]
    pl_thumb = 'http:' + pl_thumb
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
@route(PREFIX + '/youtubevideos', pl_only=bool)
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
      video_url = YouTube_URL + video_url
    try: video_title = video.xpath('./@data-title')[0]
    except: video_title = video.xpath('.//a/@title')[0]
    thumb = video.xpath('.//img/@data-thumb')[0]
    thumb = 'http:' + thumb
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
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=title), title="***DELETE THE %s SHOW***" %title, summary="Click here to delete this YouTube Show"))
    oc.add(InputDirectoryObject(key=Callback(AddImage, title=title, url=url), title="ADD a CUSTOM IMAGE FOR %s" %title, summary="Add an alternative image url for this show", prompt="Enter the full URL (including http://) for an existing online image"))

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
@route(PREFIX + '/ytcontent')
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
    try: content = HTTP.Request(url, cacheTime=CACHE_1HOUR).content
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

#############################################################################################################################
# This function creates sections for Daily Motion users and channels
@route(PREFIX + '/dailymotionsection')
def DailyMotionSections(title, url, vid_type, dm_id, thumb):
  
  oc = ObjectContainer(title2=title)
  show_title = title
  show_url = url
  oc.add(DirectoryObject(key=Callback(DailyMotionVideo, title="%s Videos" %title, vid_type=vid_type, dm_id=dm_id), title="%s Videos" %title, thumb=thumb))
  oc.add(DirectoryObject(key=Callback(DailyMotionPL, title="%s Playlist" %title, dm_id=dm_id), title="%s Playlist" %title, thumb=thumb))

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=title), title="***DELETE THE %s SHOW***" %title, summary="Click here to delete this Daily Motion Show"))
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=title, url=url), title="Add a Custom Image For %s" %title, summary="Add an alternative image url for this show", prompt="Enter the full URL (including http://) for an existing online image"))

  return oc
#############################################################################################################################
# This function pulls a lists of Daily Motion playlists for a user or channel
@route(PREFIX + '/dailymotionpl')
def DailyMotionPL(title, dm_id):
  
  oc = ObjectContainer(title2=title)

  fields = "id,name,description,thumbnail_url"
  dm_api = 'https://api.dailymotion.com/user/%s/playlists?limit=25&fields=%s' %(dm_id, fields)
  data = JSON.ObjectFromURL(dm_api)

  for playlist in data['list']:
    oc.add(DirectoryObject(key=Callback(DailyMotionVideo, title=playlist['name'], vid_type='playlist', dm_id=playlist['id']),
      title=playlist['name'],
      summary=playlist['description'],
      thumb=Resource.ContentsOfURLWithFallback(url=playlist['thumbnail_url'], fallback=ICON)
    ))
    
  if len(oc) < 1:
    return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
  else:
    return oc

####################################################################################################
# This function will produce videos for Daily Motion users, channels or playlists
@route(PREFIX + '/dailymotionvideos', page=int, pl_only=bool)
def DailyMotionVideo(title, vid_type, dm_id, url='', sort="recent", limit=25, page=1, pl_only=False):

  oc = ObjectContainer(title2=title)

  fields = "title,description,thumbnail_large_url,rating,url,duration,created_time,views_total"
  dm_api = 'https://api.dailymotion.com/%s/%s/videos?sort=%s&limit=%i&page=%i&fields=%s' %(vid_type, dm_id, sort, limit, page, fields)
  data = JSON.ObjectFromURL(dm_api)

  for video in data['list']:
    vid_title = video['title']
    vid_url = video['url']
    duration = video['duration']*1000 # worst case duration is 0 so we get 0
    try: views = "\n\nViews: %i" % video["views_total"]
    except: views = ""
    try:
      summary = String.StripTags(video['description'].replace("<br />", "\n")) + views
      summary = summary.strip()
    except: summary = None
    try: thumb_url = video['thumbnail_large_url']
    except: thumb_url = ""
    try: rating = float(video['rating']*2)
    except: rating = None
    try: originally_available_at = Datetime.FromTimestamp(video['created_time'])
    except: originally_available_at = None

    oc.add(
      VideoClipObject(
        url = vid_url,
        title = vid_title,
        summary = summary,
        duration = duration,
        rating = rating,
        originally_available_at = originally_available_at,
        thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
      )
    )

  # pagination
  if data['has_more']:
    page=page+1
    oc.add(NextPageObject(key=Callback(DailyMotionVideo, title=title, vid_type=vid_type, dm_id=dm_id, page=page), title="More..."))

  if pl_only:
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=title), title="***DELETE THE %s SHOW***" %title, summary="Click here to delete this Daily Motion Show"))
    oc.add(InputDirectoryObject(key=Callback(AddImage, title=title, url=url), title="Add a Custom Image For %s" %title, summary="Add an alternative image url for this show", prompt="Enter the full URL (including http://) for an existing online image"))

  if len(oc) < 1:
    return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
  else:
    return oc

#############################################################################################################################
# This function is used by the RSS show function to breaks content into pubdate, link with thumb and description 
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
# This is a function to test if there is a Plex URL service for  given url. Used by the RSSshows function
#       if URLTest(url) == "true":
@route(PREFIX + '/urltest')
def URLTest(url):
  if URLService.ServiceIdentifierForURL(url) is not None:
    url_good = 'true'
  else:
    url_good = 'false'
  return url_good

############################################################################################################################
# This function is for the ShowRSS function to show a directory for videos that do not have a URL service or a media stream URL value. 
# This way a directory entry for each incompatible URLs is shown, so any bad entries will still be listed with an explanation
@route(PREFIX + '/urlnoservice')
def URLNoService(title):
  return ObjectContainer(header="Error", message='There is no Plex URL service or media file link for the %s feed entry. A Plex URL service or a link to media files in the feed entry is required for this channel to create playable media. If all entries for this feed give this error, you can use the Delete button shown at the end of the feed entry listings to remove this feed' %title)

############################################################################################################################
# This function creates an error message for RSS Feed entries that have an unsupported media type and keeps a section of feeds
# from giving an error for the entire list of entries
@route(PREFIX + '/urlunsupported')
def URLUnsupported(url, title):
  oc = ObjectContainer()
  
  return ObjectContainer(header="Error", message='The media for the %s feed entry is of a type that is not supported. If you get this error with all entries for this feed, you can use the Delete option shown at the end of the feed entry listings to remove this feed from the channel' %title)

  return oc

############################################################################################################################
# This function creates a directory entry when a show URL from the Dict['MyShows'] fails an XML/HTML.ElementFromURL pull
# to show users the error instead of skipping them. And in this function we can give options to fix that show URL 
@route(PREFIX + '/urlerror')
def URLError(url, show_type):

  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(DeleteShow, title="Delete Show", url=url), title="Delete Show", summary="Delete this URL from your list of shows. You can try again by choosing the Add Show option"))
  return oc

############################################################################################################################
# This is a function to delete a show from the Dict['MyShows']
@route(PREFIX + '/deleteshow')
def DeleteShow(url, title):

  shows = Dict["MyShows"]
  for show in shows:
    if show['url'] == url:
      shows.remove(show)
      break
  #Log(Dict['MyShows'])
  return ObjectContainer(header=L('Deleted'), message=L('Your show has been deleted from the channel'))

#############################################################################################################################
# This is a function to add a show to Dict['MyShows'].  
@route(PREFIX + '/addshow')
def AddShow(show_type, query, url=''):

  Log('the value of query is %s' %query)
  url = query
  # Fix or clean up url
  if url.startswith('www') or url.startswith('http://') or url.startswith('https://'):
    url = URLCleanUp(url, show_type)
  else:
    url = URLFix(url, show_type)
    
  list_item = {}
  list_item[unicode('type')] = unicode(show_type)
  list_item[unicode('url')] = unicode(url)
  list_item[unicode('thumb')] = unicode('')
  Dict["MyShows"].append(list_item)

  #Log(Dict['MyShows'])
  return ObjectContainer(header=L('Added'), message=L('Your show has been added to the channel'))

###################################################################################################################
# This is a function cleans up URLs that have been entered as URLs
# It returns to the AddShow function to produce a proper url
@route(PREFIX + '/urlcleanup')
def URLCleanUp(url, show_type):

  #Log('the value entering URLFix function of url is %s and the value of show_type is %s' %(url, show_type))
  # Clean up the entry as much as possible by removing any extra url coding that may be added
  # strip any spaces
  url = url.strip().replace(' ', '')
  if url.startswith('www'):
    url = 'http://' + url
  if '#' in url:
    url = url.split('#')[0]
  if '?' in url and '?list=PL' not in url:
    url = url.split('?')[0]
  # edit based on type
  if show_type == 'youtube':
    # Often a playlist URLs are URLs for the first video in the playlist with the playlist ID attached at the end
    if 'watch?v=' in url and '=PL' in url :
      playlist = url.split('&list=')[1]
      url = '%splaylist?list=%s' %(YouTube_URL, playlist)
  # PLAYLIST SEEM TO START WITH x AND USE THE URL http://www.dailymotion.com/playlist/<PLAYLIST#>
  elif show_type == 'dailymotion':
    # Remove the Daily Motion page number at end
    if url.endswith('/1#') or  url.endswith('/1'):
      url = url.split('/1#')[-1]
  else:
    pass
  #Log('the value exiting URLFix function of url is %s' %url)
  return url
###################################################################################################################
# This is a function to make urls out of show names
# It returns to the AddShow function to produce a proper url
@route(PREFIX + '/urlfix')
def URLFix(url, show_type):

  #Log('the value entering URLFix function of url is %s and the value of show_type is %s' %(url, show_type))
  # strip any spaces
  url = url.strip().replace(' ', '')
  # edit based on type
  if show_type == 'youtube':
    if url.startswith('PL'):
      # for playlist
      url = '%s/playlist?list=%s' %(YouTube_URL, url)
    elif url.startswith('UC'):
      # for channels
      url = '%s/channel/%s' %(YouTube_URL, url)
    else:
      # for usernames
      url = '%s/user/%s' %(YouTube_URL, url)
  # PLAYLIST IDs SEEM TO START WITH x AND USE THE URL http://www.dailymotion.com/playlist/<PLAYLIST#>
  elif show_type == 'dailymotion':
    url = DAILYMOTION_URL + url
  else:
    url = url.lower()
    url = VIMEO_URL + url
  #Log('the value exiting URLFix function of url is %s' %url)
  return url
#############################################################################################################################
# This is a function to add an url for an image the Dict['MyShows'].  
@route(PREFIX + '/addimage')
def AddImage(query, url, title=''):

  thumb = query
  # Checking to make sure http on the front
  if thumb.startswith('www'):
    thumb = 'http://' + thumb
  else:
    pass

  shows = Dict["MyShows"]
  for show in shows:
    if show['url'] == url:
      show['thumb'] = thumb
      break
    else:
      pass

  return ObjectContainer(header=L('Added'), message=L('Your image has been added for the show'))
#############################################################################################################################
# This function loads the json data file and replaces the existing Dict["MyShows"] 
@route(PREFIX + '/loaddata')
def LoadData():
  Dict["MyShows"] = []
  json_data = Resource.Load(SHOW_DATA)
  Dict["MyShows"] = JSON.ObjectFromString(json_data)
  #Log(Dict['MyShows'])
  return ObjectContainer(header=L('Updated'), message=L('Your show data has been updated from the json data file in the Resources folder'))
#############################################################################################################################
# This function adds the json data file to the existing Dict["MyShows"] (can also use x.extend(y))
# CANNOT PREVENT DUPLICATES 
@route(PREFIX + '/adddata')
def AddData():
  shows = Dict["MyShows"]
  json_data = Resource.Load(SHOW_DATA)
  json_shows = JSON.ObjectFromString(json_data)
  Dict["MyShows"] = shows + json_shows
  return ObjectContainer(header=L('Updated'), message=L('Your show data has been updated to inlude the json data in the Resources folder'))
