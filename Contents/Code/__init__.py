
TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
RSS_ICON = 'rss-feed-icon.png'
SHOW_DATA = 'data.json'

RE_LIST_ID = Regex('listId: "(.+?)", pagesConfig: ')
RE_CONTENT_ID = Regex('CONTENT_ID = "(.+?)";')
RE_HULU_ID = Regex('Hulu.Mobile.currentShowId = (.+?);')

YouTubePlaylistURL = 'http://www.youtube.com/playlist?list='
YouTubePLFeedURL = 'https://gdata.youtube.com/feeds/api/playlists/'
YouTubeURL = 'http://www.youtube.com'
LstudioURL = 'http://www.lstudio.com'
channelURL3 = 'http://www.blip.tv'
HuluURL = 'http://www.hulu.com'
HuluEpURL = 'http://www.hulu.com/watch/'
YahooURL = 'http://screen.yahoo.com'
YahooOrigURL = 'http://screen.yahoo.com/yahoo-originals/'

http = 'http:'

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
    
  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:18.0) Gecko/20100101 Firefox/18.0'

###################################################################################################
# Since these shows will be added individually, for now this Main Menu will be hardcoded in.
# would like to eventually pull this info from a database file and even later have the option of entering info to add you own shows
# I wold need to add a step of verification to ensure the data was accurate
# also I could see changing this to a format where it tries a couple different things to pull data for
# populating front page for show
# It would also require some more error testing
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

def MainMenu():

  oc = ObjectContainer()
  
  json_data = Resource.Load(SHOW_DATA)
  Dict["shows"] = JSON.ObjectFromString(json_data)
  
  oc.add(DirectoryObject(key=Callback(SectionHulu, title="Hulu Original Shows"), title="Hulu Original Shows", thumb=GetThumb(HuluURL)))
	
  oc.add(DirectoryObject(key=Callback(SectionYahoo, title="Yahoo Screen Original Shows"), title="Yahoo Screen Original Shows", thumb=GetThumb(YahooURL)))
	
  oc.add(DirectoryObject(key=Callback(SectionPlaylist, title="YouTube Playlist Shows"), title="YouTube Playlist Shows", thumb=GetThumb(YouTubeURL)))

  oc.add(DirectoryObject(key=Callback(SectionRSS, title="RSS Feeds"), title="RSS Feeds", thumb=R(RSS_ICON)))

  return oc

#########################################################################################################################
# For RSS Feeds
@route(PREFIX + '/sectionrss')
def SectionRSS(title):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == 'rss':
      url = show["url"]
      show_thumb = show["thumb"]
      try:
        rss_page = XML.ElementFromURL(url)
        title = rss_page.xpath("//channel/title//text()")[0]
        description = rss_page.xpath("//channel/description//text()")[0]
        if show_thumb:
          thumb = show_thumb
        else:
          try:
            thumb = rss_path.xpath("//channel/image/url//text()")[0]
          except:
            thumb = R(RSS_ICON)

        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url), title=title, summary=description, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(RSS_ICON))))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no RSS Feed shows to list right now.")

  return oc
  
########################################################################################################################
# For Hulu Shows
@route(PREFIX + '/sectionhulu')
def SectionHulu(title):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == 'hulu':
      url = show["url"]
      show_thumb = show["thumb"]
      try:
        page = HTML.ElementFromURL(url)
        title = page.xpath("//head//meta[@property='og:title']//@content")[0]
        description = page.xpath("//head//meta[@name='description']//@content")[0]
        if show_thumb:
          thumb = show_thumb
        else:
          thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

        oc.add(DirectoryObject(key=Callback(ShowHulu, title=title, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)), summary=description))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no Hulu shows to list right now.")

  return oc

#########################################################################################################################
# For Yahoo Shows
@route(PREFIX + '/sectionyahoo')
def SectionYahoo(title):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == 'yahoo':
      url = show["url"]
      show_thumb = show["thumb"]
      try:
        page = HTML.ElementFromURL(url)
        title = page.xpath("//head//meta[@property='og:title']//@content")[0]
        description = page.xpath("//head//meta[@name='description']//@content")[0]
        if show_thumb:
          thumb = show_thumb
        else:
	  # We may want to put this in a try
          thumb_page = HTML.ElementFromURL(YahooOrigURL)
          thumb = thumb_page.xpath('//ul/li/ul/li/div/a/img[@alt="%s"]//@style' % title)[0]
          thumb = thumb.replace("background-image:url('", '').replace("');", '')
	
        oc.add(DirectoryObject(key=Callback(ShowYahoo, title=title, url=url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)), summary=description))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))

    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no Yahoo Screen shows to list right now.")      

  return oc

#########################################################################################################################
# For Youtube Playlist
@route(PREFIX + '/sectionplaylist')
def SectionPlaylist(title):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == 'youtube':
      url = show['url']
      show_thumb = show['thumb']
      try:
        page = HTML.ElementFromURL(url)
        title = page.xpath("//head//meta[@property='og:title']//@content")[0]
        description = page.xpath("//head//meta[@name='description']//@content")[0]
        if show_thumb:
          thumb = show_thumb
        else:
          thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

        oc.add(DirectoryObject(key=Callback(ShowPlaylist, title=title, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)), summary=description))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))

    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no YouTube Playlist shows to list right now.")      

  return oc

########################################################################################################################
@route(PREFIX + '/showrss')
def ShowRSS(title, url):
# This is for shows that have an RSS Feed.  Will have to look back to see if it will work with other RSS feeds
# Need to add a error message for RSS feeds that do not have a Plex URL service.  Maybe a try pulling shows except give a message
# saying the service may not be supported

  oc = ObjectContainer(title2=title)
  xml = RSS.FeedFromURL(url)

  for item in xml.entries:
    epUrl = item.link
    epTitle = item.title
    epDate = Datetime.ParseDate(item.date)
    # The description actually contains pubdate, link with thumb and description so we need to break it up
    epDesc = item.description
    html = HTML.ElementFromString(epDesc)
    els = list(html)
    epThumb = html.cssselect('img')[0].get('src')

    epSummary = []

    for el in els:
      if el.tail: epSummary.append(el.tail)
	
    epSummary = '. '.join(epSummary)
    oc.add(VideoClipObject(
      url = epUrl, 
      title = epTitle, 
      summary = epSummary, 
      thumb = Resource.ContentsOfURLWithFallback(epThumb, fallback=R(ICON)), 
      originally_available_at = epDate
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")      

  return oc

###################################################################################################
@route(PREFIX + '/showhulu')
def ShowHulu(title, url):
# This is for shows that are on Hulu. 
# Unfortunately unable to play Webkit videos at this time so not able to play these
  oc = ObjectContainer(title2 = title)
  show_id = HuluID(url)
  json_url = 'http://www.hulu.com/mozart/v1.h2o/shows/' + show_id +'/episodes?free_only=0&show_id=6918&sort=seasons_and_release&video_type=episode&items_per_page=32&access_token=Jk0-QLbtXxtSMOV4TUnwSXqhhDM%3DaoY_yiNlac0ed1d501bee91624b25159a0c57b05d5f34fa3dc981da5c5e9169daf661ffb043b2805717849b7bdeb8e01baccc43f'

  ep_data = JSON.ObjectFromURL(json_url)
  for video in ep_data['data']:
    ep_url = video['video']['id']
    ep_url = HuluEpURL + str(ep_url)
    title = video['video']['title']
    episode =  video['video']['episode_number']
    title = 'Episode ' + str(episode) + ', ' + title
    season = video['video']['season_number']
    thumb = video['video']['thumbnail_url']
    duration = video['video']['duration']
    # duration = int(duration) * 1000
    date = video['video']['available_at']
    date = Datetime.ParseDate(date)
    summary = video['video']['description']

    oc.add(EpisodeObject(
      url = ep_url, 
      title = title,
      season = season,
      thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
      summary = summary,
      # duration = duration,
      originally_available_at = date))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")      

  return oc

###############################################################################################################
# This function pulls the show ID from each show page for it to be entered into the JSON data url for Hulu
# The best place to pull it is in the show's URL from a javascript in the head of type text/javascript that
# contains the line "Hulu.Mobile.currentShowId = 6918;"
def HuluID(url):

  ID = ''
  content = HTTP.Request(url).content
  ID = RE_HULU_ID.search(content).group(1)
  return ID

###############################################################################################################
# This is a special funcion for handling Yahoo Shows so it can have extra videos
@route(PREFIX + '/burninglove')
def ShowYahoo(title, url, thumb):
# Create two folders, for current episodes and for other videos that we can pull from the MoreVideosYahoo function below
  oc = ObjectContainer(title2=title)

  oc.add(DirectoryObject(
    key=Callback(VideoYahoo, title=title, url=url),
    title='Current Videos',
    thumb=thumb))

  oc.add(DirectoryObject(
    key=Callback(MoreVideosYahoo, title=title, url=url),
    title='Older Videos',
    thumb=thumb))
      
  return oc

###############################################################################################################
# This function pulls the Content ID from each show page for it to be entered into the JSON data url for Yahoo
# The best place to find the show ID is to use the CONTENT_ID in a script in the head with language='javascript', 
# but I have found one show that the Contenet ID did not produce data in the JSON url, that show had a listID found
# in the body in a script with language='javascript' so we have to check and see if there is a listID before we 
# pull the CONTENT_ID to make sure we can pull JSON data for the show
def YahooID(url):

  ID = ''
  content = HTTP.Request(url).content
  try:
    ID = RE_LIST_ID.search(content).group(1)
  except:
    ID = RE_CONTENT_ID.search(content).group(1)
  return ID

################################################################################################################
@route(PREFIX + '/showyahoo')
def VideoYahoo(title, url):

  oc = ObjectContainer(title2=title)
  JSON_url = YahooID(url)
  JSON_url = 'http://screen.yahoo.com/_xhr/slate-data/?list_id=' + JSON_url + '&start=0&count=50&pc_starts=1,6,11,16,21,26&pc_layouts=1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u'

  try:
    data = JSON.ObjectFromURL(JSON_url)
    for video in data['items']:
      if video['type'] == 'video':
        url = video['link_url'] 
        if url:
          description = video['summary_short']
          desc_data = HTML.ElementFromString(description)
          summary = desc_data.xpath('//text()')[0]
          title = video['title_short'] 
          thumb = video['image_thumb_url']
          duration = video['duration']
          duration = Datetime.MillisecondsFromString(duration)
          date = video['date']
          date = Datetime.ParseDate(date)
          if not url.startswith('http://'):
            url = YahooURL + url

          oc.add(VideoClipObject(
            url = url, 
            title = title, 
            thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)),
            summary = summary,
            duration = duration,
            originally_available_at = date))
      # This section is for type link right now just one show uses the Yahoo Animal Allstars and the URL service is not picking up its videos
      else:
        # The url in the link_url field does not work with the service so we are pulling the url out of summary_short
        if video['type'] == 'link':
          description = video['summary_short']
          desc_data = HTML.ElementFromString(description)
          summary = desc_data.xpath('//text()')[0]
          url = desc_data.xpath('//a//@href')[0]
          if url:
            title = video['title_short'] 
            thumb = video['image_thumb_url']
            if not url.startswith('http://'):
              url = YahooURL + url

            oc.add(VideoClipObject(
              url = url, 
              title = title,
              summary = summary,
              thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)))) 
        else:
          break
  except:
    if len(oc) < 1:
      Log ('still no value for objects')
      return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")      
  return oc

#####################################################################################################################
# This function picks up the first page of results from the second carousel on a page, so it could be used for any show
# Want to use this function to pick up other videos available for Burning Love
@route(PREFIX + '/morevideosyahoo')
def MoreVideosYahoo(title, url):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL(url)

  for video in html.xpath('//div[@id="mediabcarouselmixedlpca_2"]/div/div/ul/li/ul/li'):
  # need to check if urls need additions and if image is transparent and needs style to access it or any additions to address
    url = video.xpath('./div/a/@href')[0]
    url = YahooURL + url
    thumb = video.xpath('./div/a/img//@style')[0]
    thumb = thumb.replace("background-image:url('", '').replace("');", '')
    title = video.xpath('./div/div/p/a//text()')[0]
				
    oc.add(VideoClipObject(
      url = url, 
      title = title, 
      thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))
      
  return oc
    
####################################################################################################################
@route(PREFIX + '/showplaylist')
def ShowPlaylist(title, url):
# This is for shows that have a YouTube Playlist. 
# The json_url is 'https://gdata.youtube.com/feeds/api/playlists/' + PlaylistID +'?v=2&alt=json&start-index=1&max-results=50'

  oc = ObjectContainer()
  # show_url is for the alternative HTML method in the comments below
  show_url = url
  url = url.replace('http://www.youtube.com/playlist?list=', '')
  json_url = YouTubePLFeedURL + url + '?v=2&alt=json&start-index=1&max-results=50'

####################################################################################################################
# Just stole this below from Youtube's ParseFeed function and changed rawfeed to data, also added CheckRejectedEntry
####################################################################################################################
  try:
    data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('This feed does not contain any video'))

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
        thumb = Resource.ContentsOfURLWithFallback(thumb),
        originally_available_at = date,
        rating = rating
      ))

    # Check to see if there are any futher results available.
    if data['feed'].has_key('openSearch$totalResults'):
      total_results = int(data['feed']['openSearch$totalResults']['$t'])
      items_per_page = int(data['feed']['openSearch$itemsPerPage']['$t'])
      start_index = int(data['feed']['openSearch$startIndex']['$t'])

      if (start_index + items_per_page) < total_results:
        oc.add(NextPageObject(
          key = Callback(ShowPlaylist, title = title, url = url, page = page + 1), 
          title = L("Next Page ...")
        ))

  if len(oc) < 1:
    return ObjectContainer(header=L('Error'), message=L('This feed does not contain any video'))
  else:
    return oc

####################################################################################################################
#  This below is alternative way to pull the code from Youtube Playlist using HTML elements from the playlist page
####################################################################################################################
#  for video in HTML.ElementFromURL(show_url).xpath('//div[@id="gh-activityfeed"]/ol/li/div'):
#
#    ep_url = video.xpath('./div/div/h3[@class="video-title-container"]/a//@href')[0]
#    ep_url = YouTubeURL + ep_url
#    ep_description = video.xpath('./div/div/p[@class="video-description yt-ui-ellipsis yt-ui-ellipsis-2"]//text()')[0]
#    ep_description = ep_description.lstrip()
#    ep_title = video.xpath('./div/div/h3[@class="video-title-container"]/a//@title')[0]
#    ep_duration = video.xpath('./div/div/span[@class="video-time"]//text()')[0]
#    ep_duration = Datetime.MillisecondsFromString(ep_duration)
#    ep_thumb = video.xpath('./div/div/span/span/span/span[@class="yt-thumb-clip-inner"]/img//@src') [0]
#    ep_thumb = http + ep_thumb
#	
#    oc.add(VideoClipObject(
#      url = ep_url, 
#      summary = ep_description,
#      title = ep_title, 
#      duration = ep_duration,
#      thumb = Resource.ContentsOfURLWithFallback(ep_thumb, fallback=R(ICON))
#      ))
#####################################################################################################################

#####################################################################################################################
# This is a side function for YouTube Playlist
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
  
##########################################################################################################################
def NoData():

  return ObjectContainer(header="Empty", message="This show is not an accepted type. Unable to display data or videos for this show.")      


#############################################################################################################################
# This is a function to pull the thumb from a page
def GetThumb(url):
  page = HTML.ElementFromURL(url)
  try:
    thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
    if not thumb.startswith('http://'):
      thumb = http + thumb
  except:
    thumb = R(ICON)
  return thumb

############################################################################################################################
# this is to test if there is a URL service for this url
#       if URLTest(url) == "true":
def URLTest(url):
  if URLService.ServiceIdentifierForURL(url) is not None:
    url_good = 'true'
  else:
    url_good = 'false'
  return url_good

############################################################################################################################
# this would allow reentry of a bad url
# InputDirectoryObject(prompt=??,  title=??, )
def URLError(url):
  return ObjectContainer(header="Empty", message='Unable to display videos for this show. The show URL %s is entered incorrectly or incompatible with this channel' %url)

############################################################################################################################
# this would allow reentry of a bad url
# InputDirectoryObject(prompt=??,  title=??, )
def VideoError(url):
  return ObjectContainer(header="Error", message="Unable to display this video. The video's URL %s is not compatible with Plex's URL Services." %url)

