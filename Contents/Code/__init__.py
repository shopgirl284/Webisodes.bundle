
TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

playlistURL = 'http://www.youtube.com/playlist?list='
YouTubeURL = 'http://www.youtube.com'
LstudioURL = 'http://www.lstudio.com'
channelURL3 = 'http://www.blip.tv'
HuluURL = 'http://www.hulu.com'
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
# would like to eventually pull this info from a database and even later have the option of entering info to add you own shows
  oc = ObjectContainer()
  
  show_url = 'http://www.lstudio.com/rss/lstudiorss-web-therapy.xml'
  page = XML.ElementFromURL(show_url)
  title = page.xpath("//channel/title//text()")[0]
  description = page.xpath("//channel/description//text()")[0]

  oc.add(DirectoryObject(
    key=Callback(ShowRSS, title=title, url='http://www.lstudio.com/rss/lstudiorss-web-therapy.xml'),
    title=title, 
    summary=description,
    thumb='http://www.lstudio.com/img/WebTherapy_Series_197x111.jpg'))

  show_url = 'http://www.hulu.com/battleground'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	
	
  oc.add(DirectoryObject(
    key=Callback(ShowHulu, title=title, url='battleground'), 
    title=title, 
    thumb=thumb,
    summary=description))

  show_url = 'http://screen.yahoo.com/burning-love/'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = 'http://l.yimg.com/bt/api/res/1.2/6A3u9oiAMdXRTR8fdMdrKQ--/YXBwaWQ9eW5ld3M7Zmk9ZmlsbDtoPTEyOTtweW9mZj0wO3E9ODU7dz0yMzA-/http://l.yimg.com/os/595/2012/05/02/burninglovelogo-jpg_144203.jpg'	
	
  oc.add(DirectoryObject(
    key=Callback(ShowYahoo, title=title, url='burning-love'), 
    title=title, 
    thumb=thumb,
    summary=description))

  show_url = 'https://www.youtube.com/playlist?list=PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url='PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G'), 
    title=title, 
    thumb=thumb,
    summary=description))

  show_url = 'https://www.youtube.com/playlist?list=PL4F5986B34F73F112'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url='PL4F5986B34F73F112'), 
    title=title, 
    thumb=thumb,
    summary=description))

  show_url = 'https://www.youtube.com/playlist?list=PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'
  page = HTML.ElementFromURL(show_url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0]
  thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]	

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title=title, url='PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'), 
    title=title, 
    thumb=thumb,
    summary=description))

  return oc
###################################################################################################
@route(PREFIX + '/showplaylist')
def ShowPlaylist(title, url):
# This is for shows that have a YouTube Playlist. Hope it translates to all.

  oc = ObjectContainer()
  url = playlistURL + url

  for video in HTML.ElementFromURL(url).xpath('//div[@id="gh-activityfeed"]/ol/li/div'):

    ep_url = video.xpath('./div/div/h3[@class="video-title-container"]/a//@href')[0]
    ep_url = YouTubeURL + ep_url
    ep_description = video.xpath('./div/div/p[@class="video-description yt-ui-ellipsis yt-ui-ellipsis-2"]//text()')[0]
    ep_description = ep_description.lstrip()
    ep_title = video.xpath('./div/div/h3[@class="video-title-container"]/a//@title')[0]
    ep_duration = video.xpath('./div/div/span[@class="video-time"]//text()')[0]
    ep_duration = Datetime.MillisecondsFromString(ep_duration)
    ep_thumb = video.xpath('./div/div/span/span/span/span[@class="yt-thumb-clip-inner"]/img//@src') [0]
    ep_thumb = http + ep_thumb
	
    oc.add(VideoClipObject(
      url = ep_url, 
      summary = ep_description,
      title = ep_title, 
      duration = ep_duration,
      thumb = Function(Thumb, url=ep_thumb),
      ))
	  
  # it will loop through and return the values for all items in the page 
  return oc

########################################################################################################################
@route(PREFIX + '/showrss')
def ShowRSS(title, url):
# This is for shows that have an RSS Feed.  Will have to look back to see if it will work with all RSS feeds

  oc = ObjectContainer(title2=title)
  xml = RSS.FeedFromURL(url)

  for item in xml.entries:
    epUrl = item.link
    epTitle = item.title
    epDate = Datetime.ParseDate(item.date)
    # The description actually contains pubdate, link with thumb and description so we need to break it up
    epDesc = item.description
    html = HTML.ElementFromString(epDesc)
    # episode description are on line [2], trailers are line [1]. So need to figure out how to pull it
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
def ShowHulu(title, url):
# This is for shows that are on Hulu. 
# cannot pull this data out for some reason says no results
  url = HuluURL + '/grid/' + url + '?video_type=episode'

  oc = ObjectContainer()
  
  for video in HTML.ElementFromURL(url).xpath('//div[@id="main"]/div/div/div/div/div/div[@id="episodes_8845_battleground_true"]/div/div/div/div/a'):

    ep_url = video.xpath('.//@href')[0]
    ep_url = HuluURL + ep_url
    Log('the value of ep_url is%s'%ep_url)
    # There is no description for these videos, just the season and episode number, so putting that in the description field
    ep_description = video.xpath('./div/div[@class="title"]//text()')[0]
    Log('the value of ep_description is%s'%ep_description)
    ep_title = video.xpath('./div/div[@class="subtitle"]')[0].text()
    ep_duration = video.xpath('./div/div/span[@class="duration"]//text()')[0]
    # duration in in the format of ([number value] min) so need to convert it, if not a command then multiply times 60000
    ep_duration = int(ep_duration.strip('(' , ' min)')) * 60000
    # duration = Datetime.MillisecondsFromString(duration)
    Log('the value of ep_duration is%s'%ep_duration)
    ep_thumb = video.xpath('./img//@src') [0]
	
    oc.add(VideoClipObject(
      url = ep_url, 
      summary = ep_description,
      title = ep_title, 
      # duration = ep_duration,
      thumb = Function(Thumb, url=ep_thumb),
      ))
	  
  # it will loop through and return the values for all items in the page 
  return oc
  
###################################################################################################
@route(PREFIX + '/showyahoo')
def ShowYahoo(title, url):

  oc = ObjectContainer()
  url = YahooURL + '/' + url
  html = HTML.ElementFromURL(url)
  
  for video in html.xpath('//div[@class="feature"]'):

    ep_url = video.xpath('./a//@href')[0]
    ep_url = YahooURL + ep_url
    Log('the value of ep_url is%s'%ep_url)
    # There is a description for these videos
    ep_description = video.xpath('./div/div[@class="bd"]/div/p//text()')[0]
    ep_title = video.xpath('./div/div[@class="bd"]/div/h2//text()')[0]
    # There is no duration for these videos, so not adding that fields
    # below is to pull the thumb that actual url is hidden in a style code at //div[@class="yog-col yog-16u yom-primary"]/style
    # This line below pulls the name associated with background image
    # ep_thumb = video.xpath('./a/span/@id') [0]
    # Log('the value of ep_thumb is%s'%ep_thumb)
    # this line below would pull the data from around the url
    # ep_thumb = ep_thumb.replace("background-image:url('", '').replace("');", '')
    # Log('the value of ep_thumb is%s'%ep_thumb)
	
    oc.add(VideoClipObject(
      url = ep_url, 
      title = ep_title, 
      summary = ep_description
      ))
  
  for video in html.xpath('//div/ul/li/ul/li[@data-provider-id="video.burninglove.com"]/div[@class="item-wrap"]'):

    ep_url = video.xpath('./a//@href')[0]
    ep_url = YahooURL + ep_url
    Log('the value of ep_url is%s'%ep_url)
    # There is no description for these videos, just the title and episode number, so not adding the description field
    ep_title = video.xpath('./div/p[@class="title"]/a//text()')[0]
    # There is no duration for these videos, so not adding the duration field
    ep_thumb = video.xpath('./a/img//@style') [0]
    Log('the value of ep_thumb is%s'%ep_thumb)
    ep_thumb = ep_thumb.replace("background-image:url('", '').replace("');", '')
    Log('the value of ep_thumb is%s'%ep_thumb)
	
    oc.add(VideoClipObject(
      url = ep_url, 
      title = ep_title, 
      thumb = Function(Thumb, url=ep_thumb)
      ))
	  
  # it will loop through and return the values for all items in the page 
  return oc
  
###########################################################################################################
#This just tests to make sure there is a valid image in the thumb address, if not, you get the defaul icon
def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))
  
