import re

TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

YouTubePlaylistURL = 'http://www.youtube.com/playlist?list='
YouTubePLFeedURL = 'https://gdata.youtube.com/feeds/api/playlists/'
YouTubeURL = 'http://www.youtube.com'
LstudioURL = 'http://www.lstudio.com'
channelURL3 = 'http://www.blip.tv'
HuluURL = 'http://www.hulu.com'
HuluEpURL = 'http://www.hulu.com/watch/'
YahooURL = 'http://screen.yahoo.com'

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

@handler(PREFIX, TITLE, art=ART, thumb=ICON)

def MainMenu():
# Since these shows will be added individually, for now this Main Menu will be hardcoded in.
# would like to eventually pull this info from a database file and even later have the option of entering info to add you own shows
  oc = ObjectContainer()

# For RSS feed shows, you need the address of the RSS feed and the http address of the thumb image for the show  
  show_url = 'http://www.lstudio.com/rss/lstudiorss-web-therapy.xml'
  page = XML.ElementFromURL(show_url)
  title = page.xpath("//channel/title//text()")[0]
  description = page.xpath("//channel/description//text()")[0]

  oc.add(DirectoryObject(
    key=Callback(ShowRSS, title=title, url=show_url),
    title=title, 
    summary=description,
    thumb='http://www.lstudio.com/img/WebTherapy_Series_197x111.jpg'))

# For Hulu shows, you need the address of the show and the show id (pulling the show id from the page will take a separate function)
# could use YahooID type function to pull the id of the show
  show_url = 'http://www.hulu.com/battleground'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	
	
  oc.add(DirectoryObject(
    key=Callback(ShowHulu, title=title, url=show_url, show_id='8845'), 
    title=title, 
    thumb=thumb,
    summary=description))

  show_url = 'http://www.hulu.com/the-booth-at-the-end'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	
	
  oc.add(DirectoryObject(
    key=Callback(ShowHulu, title=title, url=show_url, show_id='6918'), 
    title=title, 
    thumb=thumb,
    summary=description))

# For Yahoo shows, you need the address of the show and the http address of the thumb image for the show  
  show_url = 'http://screen.yahoo.com/burning-love/'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = 'http://l.yimg.com/bt/api/res/1.2/6A3u9oiAMdXRTR8fdMdrKQ--/YXBwaWQ9eW5ld3M7Zmk9ZmlsbDtoPTEyOTtweW9mZj0wO3E9ODU7dz0yMzA-/http://l.yimg.com/os/595/2012/05/02/burninglovelogo-jpg_144203.jpg'	
	
  oc.add(DirectoryObject(
    key=Callback(ShowYahoo, title=title, url=show_url, thumb = 'http://l.yimg.com/bt/api/res/1.2/6A3u9oiAMdXRTR8fdMdrKQ--/YXBwaWQ9eW5ld3M7Zmk9ZmlsbDtoPTEyOTtweW9mZj0wO3E9ODU7dz0yMzA-/http://l.yimg.com/os/595/2012/05/02/burninglovelogo-jpg_144203.jpg'), 
    title=title, 
    thumb=thumb,
    summary=description))

# For Youtube shows, you need the playlist number for the show  
# Alternatively, we could make it to where you use your Youtube login to just return all of your playlists
  PlaylistID = 'PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G'
  show_url = YouTubePlaylistURL + PlaylistID
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url=PlaylistID), 
    title=title, 
    thumb=thumb,
    summary=description))

  PlaylistID = 'PL4F5986B34F73F112'
  show_url = YouTubePlaylistURL + PlaylistID
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url=PlaylistID), 
    title=title, 
    thumb=thumb,
    summary=description))

  PlaylistID = 'PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'
  show_url = YouTubePlaylistURL + PlaylistID
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url=PlaylistID), 
    title=title, 
    thumb=thumb,
    summary=description))

  return oc

########################################################################################################################
@route(PREFIX + '/showrss')
def ShowRSS(title, url):
# This is for shows that have an RSS Feed.  Will have to look back to see if it will work with other RSS feeds

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
      thumb = Function(Thumb, url=epThumb), 
      originally_available_at = epDate
      ))

  return oc

###################################################################################################
@route(PREFIX + '/showhulu')
def ShowHulu(title, url, show_id):
# This is for shows that are on Hulu. May later make a function to pull show id automatically
# Unfortunately unable to play Webkit videos at this time so not able to play these
  oc = ObjectContainer(title2 = title)
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
      thumb = thumb,
      summary = summary,
      # duration = duration,
      originally_available_at = date))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="Unable to display videos for this show right now.")      

  return oc

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
# This function pulls the Content ID from each show page for it to be entered into the JSON data url
def YahooID(url):

  ID = ''
  html = HTML.ElementFromURL(url)
  for script in html.xpath('//head/script[@language="javascript"]'):
    text = script.xpath('.//text()')[0]
    match = re.search("CONTENT_ID .+", text)
    if match:
      ID = match.group(0)
      ID = ID.replace('CONTENT_ID = "', '').replace('";', '')
      break
      
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
            thumb = thumb,
            summary = summary,
            duration = duration,
            originally_available_at = date))
      # This section is for type link right now just one show uses the Yahoo Animal Allstars and the URL service is not picking up its videos
      else:
        # The url in the link_url field does not work with the service so we are pulling the url out of summary_short
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
            thumb = thumb)) 
	
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
      thumb = thumb))
      
  return oc
    
####################################################################################################################
@route(PREFIX + '/showplaylist')
def ShowPlaylist(title, url):
# This is for shows that have a YouTube Playlist. 
# The json_url is 'https://gdata.youtube.com/feeds/api/playlists/' + PlaylistID +'?v=2&alt=json&start-index=1&max-results=50'

  oc = ObjectContainer()
  # show_url is for the alternative HTML method in the comments below
  show_url = YouTubePlaylistURL + url
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
#      thumb = Function(Thumb, url=ep_thumb),
#      ))
#####################################################################################################################

#####################################################################################################################
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

########################################################################################################################
#This just tests to make sure there is a valid image in the thumb address, if not, you get the defaul icon
def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))
