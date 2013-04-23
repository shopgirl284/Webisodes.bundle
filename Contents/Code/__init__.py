
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

  oc.add(DirectoryObject(
    key=Callback(ShowRSS, title='Web Therapy', url='http://www.lstudio.com/rss/lstudiorss-web-therapy.xml'),
    title="Web Therapy", 
    thumb='http://www.lstudio.com/img/WebTherapy_Series_197x111.jpg'))
	
  oc.add(DirectoryObject(
    key=Callback(ShowHulu, title="Battleground", url='battleground'), 
    title="Battleground", 
    thumb='http://ib2.huluim.com/show/8845?region=US&size=600x400'))
	
  oc.add(DirectoryObject(
    key=Callback(ShowYahoo, title="Burning Love", url='burning-love'), 
    title="Burning Love", 
    thumb='http://l.yimg.com/bt/api/res/1.2/6A3u9oiAMdXRTR8fdMdrKQ--/YXBwaWQ9eW5ld3M7Zmk9ZmlsbDtoPTEyOTtweW9mZj0wO3E9ODU7dz0yMzA-/http://l.yimg.com/os/595/2012/05/02/burninglovelogo-jpg_144203.jpg'))

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Neil's Puppet Dreams", url='PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G'), 
    title="Neil's Puppet Dreams", 
    thumb='https://i3.ytimg.com/vi/zBh__ymaFQo/hqdefault.jpg'))

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Chris Hardwick's All Star Celebrity Bowling", url='PL4F5986B34F73F112'), 
    title="Chris Hardwick's All Star Celebrity Bowling", 
    thumb='http://i2.ytimg.com/vi/5M-iiIpzEfU/hqdefault.jpg'))

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Write Now! with Jimmy Pardo", url='PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'), 
    title="Write Now! with Jimmy Pardo", 
    thumb='http://i2.ytimg.com/vi/am0dlMGN2nw/mqdefault.jpg'))

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
  
  for video in html.xpath('//div[@class="feature"]/div/div[@class="bd"]/div'):

    ep_url = video.xpath('./h2//@href')[0]
    ep_url = YahooURL + ep_url
    Log('the value of ep_url is%s'%ep_url)
    # There is a description for these videos
    ep_description = video.xpath('./p//text()')[0]
    ep_title = video.xpath('./h2//text()')[0]
    # There is no image or duration for these videos, so not adding these fields
	
    oc.add(VideoClipObject(
      url = ep_url, 
      title = ep_title, 
      summary = ep_description
      ))
  
  for video in html.xpath('//div/ul/li/ul/li[@data-provider-id="video.burninglove.com"]/div[@class="item-wrap"]'):

    ep_url = video.xpath('./div/p[@class="title"]/a//@href')[0]
    ep_url = YahooURL + ep_url
    Log('the value of ep_url is%s'%ep_url)
    # There is no description for these videos, just the title and episode number, so not adding the description field
    ep_title = video.xpath('./div/p[@class="title"]/a//text()')[0]
    # There is no duration for these videos, so not adding the duration field
    ep_thumb = video.xpath('./a[@class="img-wrap"]/img') [0].get('src')
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
  
