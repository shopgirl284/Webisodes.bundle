
TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

# For Web Therapy, we can use the main show ('http://www.lstudio.com/web-therapy/') or the RSS Feed ('http://www.lstudio.com/rss/lstudiorss-web-therapy.xml')
WebTherapyURL = 'http://www.lstudio.com/rss/lstudiorss-web-therapy.xml'
WebTherapyThumb = 'http://www.lstudio.com/img/WebTherapy_Series_197x111.jpg'

# For Neil's Puppet Dreams, we can use the main page('http://henson-alternative.wikia.com/wiki/Neil%27s_Puppet_Dreams') or the YouTube playlist ('https://www.youtube.com/playlist?list=PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G')
# alternate for thumb is tvdb at 'http://thetvdb.com/banners/fanart/original/264624-2.jpg' show link is 'http://thetvdb.com/?tab=series&id=264624&lid=7'
NeilSHOWURL = 'http://henson-alternative.wikia.com/wiki/Neil%27s_Puppet_Dreams'
NeilSHOWPL = 'PLl4T6p7km9dbx0o8J35KjWAwaiEo5tV7G'
NeilSHOWThumb = 'http://images.wikia.com/henson-alternative/images/4/46/NeilsPuppetDreams.jpg'

# For Chris Hardwick's All Star Celebrity Bowling, we can use his page at Nerdist ('http://www.nerdist.com/category/bowling/') or the YouTube playlist ('http://www.youtube.com/playlist?list=PL4F5986B34F73F112')
# Getting thumb from TVDB, show link is  'http://thetvdb.com/?tab=series&id=264502&lid=7'
AllStarBowlingSHOWURL = 'http://www.nerdist.com/category/bowling/'
AllStarBowlingSHOWPL = 'PL4F5986B34F73F112'
AllStarBowlingSHOWThumb = 'http://thetvdb.com/banners/fanart/original/264502-1.jpg'

# For Write Now! with Jimmy Pardo, we can use the nerdist page ('http://www.nerdist.com/2012/10/jimmy-pardos-new-show-starts-write-now/') or the YouTube playlist ('http://www.youtube.com/playlist?list=PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB')
# Got thumb from YouTube
WriteNowSHOWURL = 'http://www.youtube.com/playlist?list=PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'
WriteNowSHOWPL = 'PLl4T6p7km9dYIjdVhuqlEFa4eP0kM3TQB'
WriteNowSHOWThumb = 'http://i2.ytimg.com/vi/am0dlMGN2nw/mqdefault.jpg'

playlistURL = 'http://www.youtube.com/playlist?list='
channelURL1 = 'http://www.youtube.com'
channelURL2 = 'http://www.lstudio.com'
channelURL3 = 'http://www.blip.tv'
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

# Since these shows will be added individually, this Main Menu will need to be setup differently
# probably shouwl use RSS Feeds where available to keep it simple or youtube playlist where available

# Could set up an xpath loop to go to each main site and pull info such as thumb and description

  oc = ObjectContainer()
	
  oc.add(DirectoryObject(
    key=Callback(ShowRSS, title='Web Therapy', url=WebTherapyURL),
    title="Web Therapy", 
    thumb=WebTherapyThumb))
		
  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Neil's Puppet Dreams", url=playlistURL + NeilSHOWPL), 
    title="Neil's Puppet Dreams", 
    thumb=NeilSHOWThumb))

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Chris Hardwick's All Star Celebrity Bowling", url=playlistURL + AllStarBowlingSHOWPL), 
    title="Chris Hardwick's All Star Celebrity Bowling", 
    thumb=AllStarBowlingSHOWThumb))

  oc.add(DirectoryObject(
    key=Callback(ShowPlaylist, title="Write Now! with Jimmy Pardo", url=playlistURL + WriteNowSHOWPL), 
    title="Write Now! with Jimmy Pardo", 
    thumb=WriteNowSHOWThumb))

  return oc

###################################################################################################
@route(PREFIX + '/showplaylist')
def ShowPlaylist(title, url):
# This is for shows that have a YouTube Playlist. Hope it translates to all.

  oc = ObjectContainer()

  for video in HTML.ElementFromURL(url).xpath('//div[@id="gh-activityfeed"]/ol/li/div'):

    url = video.xpath('./div/div/h3[@class="video-title-container"]/a//@href')[0]
    url = channelURL1 + url
    description = video.xpath('./div/div/p[@class="video-description yt-ui-ellipsis yt-ui-ellipsis-2"]//text()')[0]
    Log('the value of description is%s'%description)
    description = description.lstrip()
    Log('the value of description is%s'%description)
    title = video.xpath('./div/div/h3[@class="video-title-container"]/a//@title')[0]
    duration = video.xpath('./div/div/span[@class="video-time"]//text()')[0]
    duration = Datetime.MillisecondsFromString(duration)
    Log('the value of duration is%s'%duration)
    thumb = video.xpath('./div/div/span/span/span/span[@class="yt-thumb-clip-inner"]/img//@src') [0]
    thumb = http + thumb
	
    oc.add(VideoClipObject(
      url = url, 
      summary = description,
      title = title, 
      duration = duration,
      thumb = Function(Thumb, url=thumb),
      ))
	  
  # it will loop through and return the values for all items in the page 
  return oc

########################################################################################################################
@route(PREFIX + '/showrss')
def ShowRSS(title, url):
# This is for shows that have an RSS Feed.  Will have to look back to see if it will work with all

  oc = ObjectContainer(title2=title)
  xml = RSS.FeedFromURL(url)

  for item in xml.entries:
    epUrl = item.link
    epTitle = item.title
    epDate = Datetime.ParseDate(item.date)
    # The description actually contains pubdate, link with thumb and description so we need to break it up
    epDesc = item.description
    Log('the value of epDesc is%s'%epDesc)
    html = HTML.ElementFromString(epDesc)
    Log('the value of html is%s'%html)
    # episode description are on line [2], trailers are line [1]. So need to figure out how to pull it
    els = list(html)
    Log('the value of els is%s'%els)
    epThumb = html.cssselect('img')[0].get('src')
    Log('the value of epThumb is%s'%epThumb)

    epSummary = []
    Log('the value of epSummary is%s'%epSummary)

    for el in els:
      if el.tail: epSummary.append(el.tail)
      Log('the value of el is%s'%el)
      Log('the value of epSummary is%s'%epSummary)
	
    Log('the value of epSummary is%s'%epSummary)

    epSummary = '. '.join(epSummary)
    Log('the value of epSummary is%s'%epSummary)
	
    oc.add(VideoClipObject(
      url = epUrl, 
      title = epTitle, 
      summary = epSummary, 
      thumb = Function(Thumb, url=epThumb), 
      originally_available_at = epDate
      ))

  return oc
  
###########################################################################################################
#This just tests to make sure there is a valid image in the thumb address, if not, you get the defaul icon
def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))
  
