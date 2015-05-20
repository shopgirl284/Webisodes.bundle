TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

RSS_ICON = 'rss-feed-icon.png'
YOUTUBE_ICON = 'youtube-icon.png'
YAHOO_ICON = 'yahoo-icon.png'
VIMEO_ICON = 'vimeo-icon.png'
BLIPTV_ICON = 'bliptv-icon.png'

SHOW_DATA = 'data.json'
NAMESPACES = {'feedburner': 'http://rssnamespace.org/feedburner/ext/1.0'}
NAMESPACES2 = {'media': 'http://search.yahoo.com/mrss/'}
NAMESPACE_SMIL = {'smil': 'http://www.w3.org/2005/SMIL21/Language'}

YouTubeFeedURL = 'https://gdata.youtube.com/feeds/api/'
YahooURL = 'http://screen.yahoo.com/'
YahooShowJSON = 'http://screen.yahoo.com/ajax/resource/channel/id/%s;count=20;start='
YahooShowURL = 'http://screen.yahoo.com/%s/%s.html'
BLIP_URL = 'http://blip.tv/pr/show_get_full_episode_list?users_id=%s&lite=0&page=%s'
YouTube_URL = 'http://www.youtube.com/'
BLIPTV_URL = 'http://blip.tv/'
VIMEO_URL = 'http://vimeo.com/'

http = 'http:'
MAXRESULTS = 50
# Season and Episode for Yahoo Screen are always in the title and can be in brackets  
RE_SEASON  = Regex('(SEASON|Season|\[S) ?(\d+)')
RE_EPISODE  = Regex('(Episode|Ep.) ?(\d+)')

###################################################################################################
# Set up containers for all possible objects
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.thumb = R(ICON)
  DirectoryObject.art = R(ART)
  EpisodeObject.thumb = R(ICON)
  EpisodeObject.art = R(ART)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)

  #HTTP.CacheTime = CACHE_1DAY 

  #This Checks to see if there is a list of shows
  if Dict['MyShows'] == None:
  # HERE WE PULL IN THE JSON DATA IN TO POPULATE THIS DICT THE FIRST TIME THEY LOAD THE CHANNEL
  # THIS ALSO ALLOWS USERS TO REVERT BACK TO A DEFAULT LIST IF THERE ARE ISSUES
  # ALSO NEED THE 50 ENTRIES IN THE JSON DATA TO HOLD ADDITIONS SINCE FORMAT DOES NOT TRULY ALLOW ADDTION OF ENTRIES
    Dict["MyShows"] = LoadData()

  else:
    Log(Dict['MyShows'])

###################################################################################################
# This Main Menu provides a section for each type of show. It is hardcoded in since the types of show have to be set and preprogrammed in
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

def MainMenu():

  oc = ObjectContainer()
  
  json_data = Resource.Load(SHOW_DATA)
  Dict["shows"] = JSON.ObjectFromString(json_data)
  
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Yahoo Screen Original Shows", show_type='yahoo'), title="Yahoo Screen Original Shows", thumb=R(YAHOO_ICON)))
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Blip TV Shows", show_type='blip'), title="Blip TV Shows", thumb=R(BLIPTV_ICON)))
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Vimeo Shows", show_type='vimeo'), title="Vimeo Shows", thumb=R(VIMEO_ICON)))
  oc.add(DirectoryObject(key=Callback(OtherSections, title="YouTube Shows", show_type='youtube'), title="YouTube Shows", thumb=R(YOUTUBE_ICON)))
  oc.add(DirectoryObject(key=Callback(SectionRSS, title="RSS Feeds"), title="RSS Feeds", thumb=R(RSS_ICON)))
  oc.add(DirectoryObject(key=Callback(SectionTools, title="Channel Tools"), title="Channel Tools", thumb=R(ICON), summary="Click here to for reset options, extras and special instructions"))

  return oc

#########################################################################################################################
# For RSS Feeds
@route(PREFIX + '/sectionrss')
def SectionRSS(title):

  oc = ObjectContainer(title2=title)
  i=1
  shows = Dict["MyShows"]
  for show in shows:
    if show[i]['type'] == 'rss':
      url = show[i]["url"]
      thumb = show[i]["thumb"]
      i+=1
      try:
        rss_page = XML.ElementFromURL(url, cacheTime = CACHE_1DAY)
        title = rss_page.xpath("//channel/title//text()")[0]
        # sometimes the description is blank and it gives an error, so we added this as a try
        try:
          description = rss_page.xpath("//channel/description//text()")[0]
        except:
          description = ' '
        if not thumb:
          try:
            thumb = rss_page.xpath("//channel/image/url//text()")[0]
          except:
            thumb = R(RSS_ICON)

        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type='rss', thumb=thumb), title=title, summary=description, thumb=thumb))

      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type='rss'), title="Invalid or Incompatible URL", summary="The URL entered in the database was either incorrect or not in the proper format for use with this channel."))
    else:
      i+=1

  oc.objects.sort(key = lambda obj: obj.title)

  oc.add(InputDirectoryObject(key=Callback(AddShow, show_type='rss'), title="Add A RSS Feed", summary="Click here to add a new RSS Feed", thumb=R(ICON), prompt="Enter the full URL (including http://) for the RSS Feed you would like to add"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no RSS Feed shows to list right now.")
  else:
    return oc

#############################################################################################################################
# This is a function that automates the sections function for each of the shows that are the same or similar
@route(PREFIX + '/othersections')
def OtherSections(title, show_type):
  oc = ObjectContainer(title2=title)
  i=1
  shows = Dict["MyShows"]
  for show in shows:
    if show[i]['type'] == show_type:
      thumb = show[i]["thumb"]
      url = show[i]["url"]
      i+=1
      try:
        page = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
        try: title = page.xpath('//head//meta[@property="og:title"]//@content')[0]
        # YouTube change the format of its playlist urls so the title was no longer picked up with og:title
        # Adding this except will fix that and help with other shows as well
        except: title = page.xpath('//meta[@name="title"]//@content')[0]
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL - %s" %url, summary="The URL entered in the database was either incorrect or not in the proper format for use with this channel."))
        continue

      description = page.xpath("//head//meta[@name='description']//@content")[0] 
      if not thumb:
        try:
          # THOUGHT ABOUT CHANGING THIS TO A REDIRECT THUMB BUT THE OPTION TO ADD YOUR OWN THUMB WOULD NOT WORK IF THIS WERE IN THE CALLBACK
          try:
            thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
          except:
            # this is for youtube playlists
            try: thumb = page.xpath('//div[@class="pl-header-thumb"]/img/@src')[0]
            except: thumb = R(ICON)
          if not thumb.startswith('http'):
            thumb = http + thumb
        except:
          pass
      # here we have an if based on type
      if show_type == 'youtube':
        # below we create the url for YouTube to pull the JSON feed. We pull it here for additional error checking
        # The function returns false if the url does not include keywords noting accepted feeds, so if it returns false, the url is invalid
        json_url = YouTubeJSON(url)
        if json_url != 'false':
          oc.add(DirectoryObject(key=Callback(PlaylistYouTube, title=title, url=url, json_url=json_url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), summary=description))
        else:
          oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type='youtube'),title="Invalid URL - %s" %title, summary="The URL entered in the database was incorrect."))
      elif show_type == 'yahoo':
        oc.add(DirectoryObject(key=Callback(ShowYahoo, title=title, url=url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), summary=description))
      elif show_type == 'blip':
        oc.add(DirectoryObject(key=Callback(ShowBlip, title=title, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), summary=description))
      else:
        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type=show_type, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=ICON), summary=description))
    else:
      i+=1

  oc.objects.sort(key = lambda obj: obj.title)

  oc.add(InputDirectoryObject(key=Callback(AddShow, show_type=show_type), title="Add A New Show", summary="Click here to add a new Show", thumb=R(ICON), prompt="Enter the full URL (including http://) for the show you would like to add"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no shows to list right now.")
  else:
   return oc

#######################################################################################################################
# This is the section for system settings
@route(PREFIX + '/systemsection')
def SectionTools (title):

  oc = ObjectContainer(title2=title)
  oc.add(DirectoryObject(key=Callback(RokuUsers, title="Special Instructions for Roku Users"), title="Special Instructions for Roku Users", thumb=R(ICON), summary="Click here to see special instructions necessary for Roku Users to add shows to this channel"))
  oc.add(DirectoryObject(key=Callback(ResetShows, title="Reset Shows"), title="Reset Shows", thumb=R(ICON), summary="Click here to reset you show list back to the original default list the channel started with"))

  return oc

########################################################################################################################
def RokuUsers (title):
# this is special instructions for Roku users
  return ObjectContainer(header="Special Instructions for Roku Users", message="To add a new show, Roku users must be using version 2.6.5 or higher of the Plex Roku Channel (currently requires using PlexTest channel). Also, adding the URL for shows is made much easier with the Remoku (www.remoku.tv) WARNING: DO NOT DIRECTLY TYPE OR PASTE THE URL IN THE ADD SHOWS SECTION USING ROKU PLEX CHANNELS 2.6.4. THAT VERSION USES A SEARCH INSTEAD OF ENTRY SCREEN AND EVERY LETTER OF THE URL YOU ENTER WILL PRODUCE IN AN INVALID SHOW ICON.")

#############################################################################################################################
# The FUNCTION below can be used to reload the original data.json file if errors occur and you need to reset the program
@route(PREFIX + '/resetshow')
def ResetShows(title):
  Dict["MyShows"] = LoadData()
  return ObjectContainer(header="Reset", message='The shows have been set back to the default list of shows.')

########################################################################################################################
# This is for shows that have an RSS Feed.  Seems to work with different RSS feeds
# TO ADD AUDIO SUPPORT FOR THOSE WITH URL SERVICES ADD A TRY/EXCEPT FOR 
# rss_type = item.xpath('./media:content//@type', namespaces=NAMESPACES2)[0]
@route(PREFIX + '/showrss')
def ShowRSS(title, url, show_type, thumb):

  oc = ObjectContainer(title2=title)
  show_title = title
  feed_title = title
  show_url = url
  if show_type == 'vimeo':
    rss_url = url + '/videos/rss'
  else:
    rss_url = url
  xml = XML.ElementFromURL(rss_url)
  for item in xml.xpath('//item'):
  
    # All Items must have a title
    title = item.xpath('./title//text()')[0]
    
    # Try to pull the link for the item
    try:
      link = item.xpath('./link//text()')[0]
    except:
      link = None
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
      continue
    
    else: 
    # Collect all other optionnal data for item
      try:
        date = item.xpath('./pubDate//text()')[0]
      except:
        date = None
      try:
        item_thumb = item.xpath('./media:thumbnail//@url', namespaces=NAMESPACES2)[0]
      except:
        item_thumb = None
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
        if media_type and 'audio' in media_type:
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
        oc.add(CreateObject(url=media_url, media_type=media_type, title=title, summary = summary, originally_available_at = date, thumb=thumb))

  # Additional directories for deleting a show and adding images for a show
  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=show_title, show_type=show_type), title="Delete %s" %show_title, summary="Click here to delete this show"))
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type=show_type, url=url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this RSS Feed"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this RSS feed right now.")      
  else:
    return oc

####################################################################################################
# This function creates an object container for RSS feeds that have a media file in the feed
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
    new_object = DirectoryObject(key=Callback(URLUnsupported, url=url, title=title), title="Media Type Not Supported", thumb=R('no-feed.png'), summary='The file %s is not a type currently supported by this channel' %url)
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
###################################################################################################################
# This is a function to produce the JSON url needed for the Yahoo function
@route(PREFIX + '/yahoojson')
def YahooJSON(url):
  # This pull show name from urls
  url = url.split(YahooURL)[1]
  if url.endswith('/'):
    url = url.split('/')[0]
  json_url = YahooShowJSON %(url)
  return json_url
######################################################################################################
# This is a JSON to produce videos on Yahoo
@route(PREFIX + '/showyahoo', start=int)
def ShowYahoo(title, url, thumb, start=0):

  oc = ObjectContainer(title2=title)
  show_title = title
  local_url = YahooJSON(url) + str(start)
  try:
    data = JSON.ObjectFromURL(local_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('This feed does not contain any video'))

  x=0
  for video in data['videos']:
    x=x+1 
    url_show = video['channel_url_alias']
    url_name = video['url_alias'] 
    video_url = YahooShowURL %(url_show, url_name)
    duration = int(video['duration']) * 1000
    date = Datetime.ParseDate(video['publish_time'])
    summary = video['description']
    title = video['title'] 
    # check for episode and season in title
    try: season = int(RE_SEASON.search(title).group(2))
    except: season = 0
    try: episode = int(RE_EPISODE.search(title).group(2))
    except: episode = 0
    if '[' in title:
      title = title.split('[')[0]
    try:
      vid_thumb = video['thumbnails'][1]['url']
    except:
      vid_thumb = R(ICON)
    # May need this for excluding videos that may not work with URL service
    #provider_name = video['provider_name']

    if episode or season:
      oc.add(EpisodeObject(
        url = video_url, 
        title = title, 
        thumb = Resource.ContentsOfURLWithFallback(vid_thumb),
        index = episode,
        season = season,
        summary = summary,
        duration = duration,
        originally_available_at = date))
    else:
      oc.add(VideoClipObject(
        url = video_url, 
        title = title, 
        thumb = Resource.ContentsOfURLWithFallback(vid_thumb),
        summary = summary,
        duration = duration,
        originally_available_at = date))

# Paging code. Each page pulls 20 results use x counter for need of next page
  if x >= 20:
    start = start + 20
    oc.add(NextPageObject(key = Callback(ShowYahoo, title=show_title, url=url, thumb=thumb, start=start), title = L("Next Page ...")))
  # add Delete Show and Add Image directory to last page
  else:
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='yahoo', title=show_title), title="Delete Yahoo Show", summary="Click here to delete this Yahoo Show", thumb=R(ICON)))    
    oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='yahoo', url=url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))
          
  if len(oc) < 1:
    return ObjectContainer(header="Empty", message="This directory appears to be empty or contains videos that are not compatible with this channel.")      
  else:
    return oc
###################################################################################################################
# This is a function to produce the JSON url needed for the YouTube Playlist and Feed functions
# It returns to the OtherSectiona so it can also serve as added url validation
@route(PREFIX + '/youtubejson')
def YouTubeJSON(url):
  #Log('the value of url entering the YOUTUBEJSON function is %s' %url)
  if 'PL' in url:
    playlist = 'PL' + url.split('PL')[1]
    json_url = YouTubeFeedURL + 'playlists/' + playlist
  else:
    if 'user/' in url:
      if '?' in url: 
        # Some may have a quesiton mark after the username Ex. http://www.youtube.com/user/NewarkTimesWeddings?feature=watch
        url = url.split('?')[0]
      user_name = url.split('user/') [1]
      # need to change all letters to lowercase
      user_name = user_name.lower()
      json_url = YouTubeFeedURL + 'users/' + user_name + '/playlists'
    elif '/channel/' in url:
      channel_id = url.split('/channel/') [1]
      json_url = YouTubeFeedURL + 'users/' + channel_id + '/playlists'
    else:
      json_url = 'false'
  #Log('the value of json_url is %s' %json_url)
  return json_url
####################################################################################################################
# This function will create a list of playlist for user or channels
# Using API v2 which currently works for playlists
@route(PREFIX + '/playlistyoutube', page=int)
def PlaylistYouTube(title, url, json_url, thumb='', page = 1):

  oc = ObjectContainer(title2=title, replace_parent=(page > 1))
  show_title = title
  show_url = url
  # If it is already a playlist, then we just send it on to produces videos
  if 'PL' in url:
    oc.add(DirectoryObject(key=Callback(ShowYouTube, title=title, url=url, json_url=json_url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)))
  # Otherwise we produce a list of playlists for the channel or user
  else:
    local_url = json_url + '?v=2&alt=json'
    local_url += '&start-index=' + str((page - 1) * MAXRESULTS + 1)
    local_url += '&max-results=' + str(MAXRESULTS)

    try:
      data = JSON.ObjectFromURL(local_url)
    except:
      return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

    if data['feed'].has_key('entry'):
      for playlist in data['feed']['entry']:
        pl_url = None
        for pl_links in playlist['link']:
          if pl_links['type'] == 'text/html':
            pl_url = pl_links['href']
            break
        pl_json_url = playlist['content']['src'].split('?')[0]

        pl_title = playlist['title']['$t']
        thumb = playlist['media$group']['media$thumbnail'][0]['url']
        summary = None
        try: summary = playlist['summary']['$t']
        except: pass

        oc.add(DirectoryObject(key=Callback(ShowYouTube, title=pl_title, url=url, json_url=pl_json_url),
          title = pl_title,
          summary = summary,
          thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
        ))

      # Check to see if there are any further results available.
      if data['feed'].has_key('openSearch$totalResults'):
        total_results = int(data['feed']['openSearch$totalResults']['$t'])
        items_per_page = int(data['feed']['openSearch$itemsPerPage']['$t'])
        start_index = int(data['feed']['openSearch$startIndex']['$t'])

        if (start_index + items_per_page) < total_results:
          oc.add(NextPageObject(
            key = Callback(PlaylistYouTube, title = title, url = url, json_url = json_url, page = page + 1), 
            title = L("Next Page ...")
          ))

  if page < 2:
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='youtube', title=title), title="Delete YouTube Show", summary="Click here to delete this YouTube Show", thumb=R(ICON)))
    oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='youtube', url=show_url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

  if len(oc) < 1:
    return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
  else:
    return oc

####################################################################################################################
# This function will work with playlist and produces results after the JSON url is constructed
# Using API v2 which currently works for playlists
@route(PREFIX + '/showyoutube', page=int)
def ShowYouTube(title, url, json_url, page = 1):

  oc = ObjectContainer(title2=title, replace_parent=(page > 1))
  show_title = title
  show_url = url
  # show_url is needed for the alternative HTML method in the comments below

####################################################################################################################
# Just stole this below from Youtube's ParseFeed function and changed rawfeed to data, also added CheckRejectedEntry
####################################################################################################################
  local_url = json_url + '?v=2&alt=json'
  local_url += '&start-index=' + str((page - 1) * MAXRESULTS + 1)
  local_url += '&max-results=' + str(MAXRESULTS)
  #Log('the value of local_url is %s' %local_url)

  try:
    data = JSON.ObjectFromURL(local_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

  if data['feed'].has_key('entry'):
    for video in data['feed']['entry']:
      # If the video has been rejected, ignore it.
      if CheckRejectedEntry(video):
        continue

      # Determine the actual HTML URL associated with the view. This will allow us to simply redirect
      # to the associated URL Service, when attempting to play the content.
      video_url = None
      for video_links in video['link']:
        if video_links['type'] == 'text/html':
          video_url = video_links['href']
          break

      # This is very unlikely to occur, but we should at least log.
      if video_url is None:
        Log('Found video that had no URL')
        continue

      # As well as the actual video URL, we need the associate id. This is required if the user wants
      # to see related content.
      video_id = None
      try: video_id = RE_VIDEO_ID.search(video_url).group(1).split('&')[0]
      except: pass

      video_title = video['media$group']['media$title']['$t']
      thumb = video['media$group']['media$thumbnail'][0]['url']
      duration = int(video['media$group']['yt$duration']['seconds']) * 1000

      summary = None
      try: summary = video['media$group']['media$description']['$t']
      except: pass

      # [Optional]
      rating = None
      try: rating = float(video['gd$rating']['average']) * 2
      except: pass

      # [Optional]
      date = None
      try: date = Datetime.ParseDate(video['published']['$t'].split('T')[0])
      except:
        try: date = Datetime.ParseDate(video['updated']['$t'].split('T')[0])
        except: pass

      oc.add(VideoClipObject(
        url = video_url,
        title = video_title,
        summary = summary,
        thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON),
        originally_available_at = date,
        rating = rating
      ))

    oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

    # Check to see if there are any futher results available.
    if data['feed'].has_key('openSearch$totalResults'):
      total_results = int(data['feed']['openSearch$totalResults']['$t'])
      items_per_page = int(data['feed']['openSearch$itemsPerPage']['$t'])
      start_index = int(data['feed']['openSearch$startIndex']['$t'])

      if (start_index + items_per_page) < total_results:
        oc.add(NextPageObject(
          key = Callback(ShowYouTube, title = title, url = url, json_url = json_url, page = page + 1), 
          title = L("Next Page ...")
        ))

  if len(oc) < 1:
    return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
  else:
    return oc

#####################################################################################################################
# This is a side function for YouTube Playlist
@route(PREFIX + '/checkrejectedentry')
def CheckRejectedEntry(entry):

  try:
    status_name = entry['app$control']['yt$state']['name']

    if status_name in ['deleted', 'rejected', 'failed']:
      return True

    if status_name == 'restricted':
      status_reason = entry['app$control']['yt$state']['reasonCode']

      if status_reason in ['private', 'requesterRegion']:
        return True

  except:
    pass

  return False

#####################################################################################################################
# This pulls videos for shows hosted at BlipTV
@route(PREFIX + '/showblip', page=int)
def ShowBlip(title, url, page=1, user_id=''):

  oc = ObjectContainer(title2=title)
  show_title = title
  if not user_id:
    # Need user id from show url to produce carousel
    # pulling page info that was used in show pull above, so a one day cache
    html = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
    # Put in a try except error message here to make sure URL in in proper format
    try:
      user_id = html.xpath('//div[@id="PageInfo"]//@data-users-id')[0]
    except:
      return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

  data_url = BLIP_URL %(user_id, str(page))
  data = HTML.ElementFromURL(data_url)

  for video in data.xpath('//div[@class="EpisodeList"]/ul/li/a'):
    ep_url = video.xpath('./meta[@itemprop="url"]//@content')[0]
    thumb = video.xpath('./span[@class="Thumbnail"]/img//@src')[0]
    title = video.xpath('./span[@class="Title"]//text()')[0].strip()
    description = video.xpath('./span[@class="Description"]//text()')[0].strip()
    date = Datetime.ParseDate(video.xpath('./span[@class="ReleaseDate"]//text()')[0].strip())
    try: duration = Datetime.MillisecondsFromString(video.xpath('./span[@class="Runtime"]//text()')[0].strip())
    except: duration = 0
				
    oc.add(VideoClipObject(
      url = ep_url, 
      title = title,
      summary = description,
      originally_available_at = date,
      duration = duration,
      thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=BLIPTV_ICON)))

  oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  # Paging
  # get the total number of pages
  total_pages = int(data.xpath('//div[@class="Pagination"]/span[@class="LastPage"]//text()')[0])
  if total_pages > page:
    oc.add(NextPageObject(key = Callback(ShowBlip, title=show_title, url=url, page=page+1, user_id=user_id), title = L("Next Page ...")))
  # add Delete Show and Add Image directory to last page
  else:
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='blip', title=title), title="Delete Blip TV Show", summary="Click here to delete this Blip TV Show", thumb=R(ICON)))    
    oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='blip', url=url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))
    if Client.Platform in ('Safari', 'Firefox', 'Chrome'):
      oc.add(DirectoryObject(key=Callback(AddShowDialog, title="Add A BlipTV show"), title="Add A BlipTV show", summary='To add a show, paste or type the url into the Search Box at the top of the page'))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc

#############################################################################################################################
# The description actually contains pubdate, link with thumb and description so we need to break it up
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
# This is to test if there is a Plex URL service for  given url.  
#       if URLTest(url) == "true":
@route(PREFIX + '/urltest')
def URLTest(url):
  url_good = ''
  if URLService.ServiceIdentifierForURL(url) is not None:
    url_good = 'true'
  else:
    url_good = 'false'
  return url_good

############################################################################################################################
# This keeps a section of the show from giving an error for the entire section if one of the URLs does not have a service or attached media
@route(PREFIX + '/urlnoservice')
def URLNoService(title):
  return ObjectContainer(header="Error", message='There is no Plex URL service or media file link for the %s show entry. A Plex URL service or a link to media files in the show entry is required for this channel to create playable media. If all entries for this show give this error, you can use the Delete button shown at the end of the show entry listings to remove this show' %title)

############################################################################################################################
# This function creates an error message for feed entries that have an usupported media type and keeps a section of feeds from giving an error for the entire list of entries
@route(PREFIX + '/urlunsupported')
def URLUnsupported(url, title):
  oc = ObjectContainer()
  
  return ObjectContainer(header="Error", message='The media for the %s show entry is of a type that is not supported. If you get this error with all entries for this show, you can use the Delete option shown at the end of the show entry listings to remove this show from the channel' %title)

  return oc

############################################################################################################################
# This function creates a directory for incorectly entered urls and keeps a section of shows from giving an error if one url is incorrectly entered
# Would like to allow for reentry of a bad url but for now, just allows for deletion. 
@route(PREFIX + '/urlerror')
def URLError(url, show_type):

  oc = ObjectContainer()
  
  oc.add(DirectoryObject(key=Callback(EditShow, url=url), title="Edit Show"))

  oc.add(DirectoryObject(key=Callback(DeleteShow, title="Delete Show", url=url, show_type=show_type), title="Delete Show", summary="Delete this URL from your list of shows"))

  return oc

#############################################################################################################################
# Here we could possible include or pull the show type and give messages based on type that show proper format
# and tell them to delete the url and try again
@route(PREFIX + '/editshow')
def EditShow(url):
  return ObjectContainer(header="Error", message='Unable to edit show urls at this time')

############################################################################################################################
# This is a function to delete a show from the json data file
# cannot just delete the entry or it will mess up the numbering and cause errors in the program.
# Instead we will make the entry blank and then check for reuse in the add function
@route(PREFIX + '/deleteshow')
def DeleteShow(url, show_type, title):
  i=1
  shows = Dict["MyShows"]
  for show in shows:
    if show[i]['url'] == url:
      show[i] = {"type":"", "url":"", "thumb":""}
      # once we find the show to delete we need to break out of the for loop
      break
    else:
      i += 1
  # Then send a message
  return ObjectContainer(header=L('Deleted'), message=L('Your show has been deleted from the channel'))

#############################################################################################################################
# This is a function to add a show to the json data file.  Wanted to make a true add but running into errors based on 
# the structure of my dictionary, so we created 50 items and just taking the first empty show and filling it with
# the show info
# NEED TO ADD A WARNING ABOUT CHANNELS IN YOUTUBE
@route(PREFIX + '/addshow')
def AddShow(show_type, query, url=''):

  #Log('the value of query is %s' %query)
  url = query
  # Checking to make sure http on the front
  if url.startswith('www'):
    url = http + '//' + url
    
  if not url.startswith('http://') and not url.startswith('https://'):
    url = URLFix(url, show_type)
    
  i=1

  shows = Dict["MyShows"]
  for show in shows:
    if show[i]['url'] == "":
      show[i]['type'] = show_type
      show[i]['url'] = url
      break
    else:
      i += 1
      if i > len(Dict['MyShows']):
        return ObjectContainer(header=L('Error'), message=L('Unable to add new show. You have added the maximum amount of 50 show. Please delete a show and try again'))
      else:
        pass

  return ObjectContainer(header=L('Added'), message=L('Your show has been added to the channel'))

#############################################################################################################################
# This is a function to add an url for an image to a feed.  
@route(PREFIX + '/addimage')
def AddImage(show_type, title, query, url=''):

  thumb = query
  # Checking to make sure http on the front
  if thumb.startswith('www'):
    thumb = http + '//' + thumb
  else:
    pass
  i=1

  shows = Dict["MyShows"]
  for show in shows:
    if show[i]['url'] == url:
      show[i]['thumb'] = thumb
      break
    else:
      i += 1
      if i > len(Dict['MyShows']):
        return ObjectContainer(header=L('Error'), message=L('Unable to add image for %s.' %title))
      else:
        pass

  return ObjectContainer(header=L('Added'), message=L('Your RSS feed image has been added to %s' %title))
#############################################################################################################################
# This function loads the json data file
@route(PREFIX + '/loaddata')
def LoadData():
  json_data = Resource.Load(SHOW_DATA)
  return JSON.ObjectFromString(json_data)
###################################################################################################################
# This is a function to make urls out of show names
# It returns to the AddShow function to produce a proper url
@route(PREFIX + '/urlfix')
def URLFix(url, show_type):

  #Log('the value entering URLFix function of url is %s and the value of show_type is %s' %(url, show_type))
  # Clean up the entry as much as possible by removing any extra url coding that may be added
  if '/' in url:
    url_list = url.split('/')
    url = url_list[len(url_list)-1]
  if '#' in url:
    url = url.split('#')[0]
  if '?' in url and '?list=PL' not in url:
    url = url.split('?')[0]
  # strip any leading and trailing spaces
  url = url.strip()
  # edit based on type
  if show_type == 'youtube':
    # remove any spaces
    url = url.replace(' ', '')
    if 'PL' in url:
      # for plyalist
      url = 'PL' + url.split('PL')[1]
      url = YouTube_URL + 'playlist?list=' + url
    elif url.startswith('UC'):
      # for channels
      url = 'UC' + url.split('UC')[1]
      url = YouTube_URL + 'channel/' + url
    else:
      # for usernames
      url = YouTube_URL + 'user/' + url
  else:
    url = url.lower()
    if show_type == 'yahoo':
      url = url.replace(' ', '-')
      url = YahooURL + url
    elif show_type == 'blip':
      url = url.replace(' ', '')
      url = BLIPTV_URL + url
    else:
      url = url.replace(' ', '')
      url = VIMEO_URL + url
  #Log('the value exiting URLFix function of url is %s' %url)
  return url
#############################################################################################################################
# To provide explanation for Plex/Web Interface
@route(PREFIX + '/addshowdialog')
def AddShowDialog():
  return ObjectContainer(header="Add Show", message='To add a show, paste or type the url into the Search Box at the top of the page')
