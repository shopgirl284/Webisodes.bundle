
TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
RSS_ICON = 'rss-feed-icon.png'
SHOW_DATA = 'data.json'

RE_LIST_ID = Regex('listId: "(.+?)", pagesConfig: ')
RE_CONTENT_ID = Regex('CONTENT_ID = "(.+?)";')
RE_HULU_ID = Regex('Hulu.Mobile.currentShowId = (.+?);')
RE_HULU_TOKEN = Regex("API_DONUT = '(.+?)';")

YouTubePlaylistURL = 'http://www.youtube.com/playlist?list='
YouTubeFeedURL = 'https://gdata.youtube.com/feeds/api/'
YouTubeURL = 'http://www.youtube.com'
LstudioURL = 'http://www.lstudio.com'
BlipTVURL = 'http://www.blip.tv'
VimeoURL = 'http://www.vimeo.com'
VimeoLogo = 'http://vimeo.com/assets/downloads/logos/vimeo_logo_dark.jpg'
HuluURL = 'http://www.hulu.com'
HuluEpURL = 'http://www.hulu.com/watch/'
HuluJSON1 = 'http://www.hulu.com/mozart/v1.h2o/shows/'
HuluJSON2 = '&sort=seasons_and_release&video_type=episode&items_per_page=32&access_token='
YahooURL = 'http://screen.yahoo.com'
YahooOrigURL = 'http://screen.yahoo.com/yahoo-originals/'
YahooJSON1 = 'http://screen.yahoo.com/_xhr/slate-data/?list_id='
# This is a global variable for the parameters of the Yahoo JSON data file. Currently it returns 32 items. 
# To add more returned results, add the last number plus 5 to pc_starts and ",1u-1u-1u-1u-1u" to pc_layouts for each five entries you want to add
YahooJSON2 = '&start=0&count=50&pc_starts=1,6,11,16,21,26&pc_layouts=1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u'

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

###################################################################################################
# This Main Menu will be hardcoded in to provide a section for each type of show.
# Could pull the types from the JSON file, where if this type exist, create directory
# would like have the option of entering info to add you own shows
@handler(PREFIX, TITLE, art=ART, thumb=ICON)

def MainMenu():

  oc = ObjectContainer()
  
  json_data = Resource.Load(SHOW_DATA)
  Dict["shows"] = JSON.ObjectFromString(json_data)
  
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Hulu Original Shows", show_type='hulu'), title="Hulu Original Shows", thumb=GetThumb(HuluURL)))
	
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Yahoo Screen Original Shows", show_type='yahoo'), title="Yahoo Screen Original Shows", thumb=GetThumb(YahooURL)))
	
  oc.add(DirectoryObject(key=Callback(OtherSections, title="Blip TV Shows", show_type='blip'), title="Blip TV Shows", thumb=GetThumb(BlipTVURL)))

  oc.add(DirectoryObject(key=Callback(OtherSections, title="Vimeo Shows", show_type='vimeo'), title="Vimeo Shows", thumb=VimeoLogo))

  oc.add(DirectoryObject(key=Callback(SectionYouTube, title="YouTube Playlist Shows"), title="YouTube Playlist Shows", thumb=GetThumb(YouTubeURL)))

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

        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url), title=title, summary=description, thumb=thumb))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no RSS Feed shows to list right now.")
  else:
    return oc

#########################################################################################################################
# For Youtube Playlist
@route(PREFIX + '/sectionyoutube')
def SectionYouTube(title):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == 'youtube':
      show_type = 'youtube'
      url = show['url']
      show_thumb = show['thumb']
      # below we create the url for YouTube to pull the JSON feed. We pull it here for additional error checking
	  # The function returns false if the url does not include keywords noting accepted feeds, so if it returns false, the url is invalid
      json_url = YouTubeJSON(url)
      if json_url != 'false':
        try:
          show_list = GetShowInfo(url, show_thumb, show_type)
          oc.add(DirectoryObject(key=Callback(ShowYouTube, title=show_list[0], url=json_url), title=show_list[0], thumb=Resource.ContentsOfURLWithFallback(show_list[2]), summary=show_list[1]))
        except:
          oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
      else:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no YouTube Playlist shows to list right now.")      
  else:
    return oc

#############################################################################################################################
# This is a function would automate the sections function for each of the shows that are the same or similar
def OtherSections(title, show_type):
  oc = ObjectContainer()
  shows = Dict["shows"]
  for show in shows:
    if show['type'] == show_type:
      url = show["url"]
      show_thumb = show["thumb"]
      try:
        show_list = GetShowInfo(url, show_thumb, show_type)
	# here we would just have an if based on type
        if show_type == 'hulu':
          oc.add(DirectoryObject(key=Callback(ShowHulu, title=show_list[0], url=url), title=show_list[0], thumb=Resource.ContentsOfURLWithFallback(show_list[2]), summary=show_list[1]))
        elif show_type == 'yahoo':
          oc.add(DirectoryObject(key=Callback(ShowYahoo, title=show_list[0], url=url, thumb=show_list[2]), title=show_list[0], thumb=Resource.ContentsOfURLWithFallback(show_list[2]), summary=show_list[1]))
        elif show_type == 'blip':
          oc.add(DirectoryObject(key=Callback(ShowBlip, title=show_list[0], url=url), title=show_list[0], thumb=Resource.ContentsOfURLWithFallback(show_list[2]), summary=show_list[1]))
        else:
          oc.add(DirectoryObject(key=Callback(ShowRSS, title=show_list[0], url=url + '/videos/rss'), title=show_list[0], thumb=Resource.ContentsOfURLWithFallback(show_list[2]), summary=show_list[1]))
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url),title="Invalid URL", summary="The URL entered in the database was incorrect."))
    else:
      pass

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no Hulu shows to list right now.")
  else:
   return oc

########################################################################################################################
# This is for shows that have an RSS Feed.  Seems to work with different RSS feeds
@route(PREFIX + '/showrss')
def ShowRSS(title, url):
# Would like to add a error message for RSS feeds that do not have a Plex URL service, but the function seems to
# block some RSS feeds

# Do we need to put this in a try except so it will not return errors

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
    return ObjectContainer(header="Empty", message="There are no videos to display for this RSS feed right now.")      
  else:
    return oc

###################################################################################################
# This is for shows that are on Hulu. 
# Unfortunately unable to play Webkit videos at this time so not able to play these
@route(PREFIX + '/showhulu')
def ShowHulu(title, url):
  oc = ObjectContainer(title2 = title)
  show_id = HuluID(url)
  # they changed the access_token for the JSON, so now just pulling it from page
  access_token = HuluToken(url)
  json_url = HuluJSON1 + show_id +'/episodes?free_only=0&show_id=' + show_id + HuluJSON2 + access_token

  try:
    ep_data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for shows'))

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
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")      
  else:
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
# This function pulls the API_DONUT from each show page for it to be entered into the JSON data url for Hulu
# got an error because they changed the access token for the JSON, so pulling that info from the page
# the access token is the API_DONUT
def HuluToken(url):

  token = ''
  content = HTTP.Request(url).content
  token = RE_HULU_TOKEN.search(content).group(1)
  return token

###############################################################################################################
# This function splits Yahoo Shows to show extra videos
# Think this needs to be just for Burning Love since other shows do not have older videos
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
# One show (Animal All Stars) does not work with its Content ID, but does work with a List ID that is
# only available on that page, so we check for that List ID first.
def YahooID(url):

  ID = ''
  content = HTTP.Request(url).content
  try:
    ID = RE_LIST_ID.search(content).group(1)
  except:
    ID = RE_CONTENT_ID.search(content).group(1)
  return ID

################################################################################################################
# This function pulls the videos for Yahoo shows using JSON data file
@route(PREFIX + '/showyahoo')
def VideoYahoo(title, url):

  oc = ObjectContainer(title2=title)
  JSON_url = YahooID(url)
  # could clean this url up with global variables
  JSON_url = YahooJSON1 + JSON_url + YahooJSON2
  # JSON_url = 'http://screen.yahoo.com/_xhr/slate-data/?list_id=' + JSON_url + '&start=0&count=50&pc_starts=1,6,11,16,21,26&pc_layouts=1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u'

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
      # This section is for type link right now just one show uses the Yahoo Animal Allstars 
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
    return ObjectContainer(header="Error", message="Unable to access video information for this show.")

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc

#####################################################################################################################
# This function picks up the first page of results from the second carousel on a page
# Using this function to pick up other videos available for Burning Love, no other shows have a second carousel
# so not sure if it works for other shows
# Test if with Chow Ciao
@route(PREFIX + '/morevideosyahoo')
def MoreVideosYahoo(title, url):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL(url)
  # Do we need some type of try here to prevent errors

  for video in html.xpath('//div[@id="mediabcarouselmixedlpca_2"]/div/div/ul/li/ul/li'):
    url = video.xpath('./div/a/@href')[0]
    url = YahooURL + url
    thumb = video.xpath('./div/a/img//@style')[0]
    thumb = thumb.replace("background-image:url('", '').replace("');", '')
    title = video.xpath('./div/div/p/a//text()')[0]
				
    oc.add(VideoClipObject(
      url = url, 
      title = title, 
      thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))
      
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc
    
###################################################################################################################
# This is a function to produce the JSON url needed for the YouTubeFeed function
# We can add other types of YouTube feed types here as we need
# It returns to the SectionYahoo so it can also serve as added url validation
def YouTubeJSON(url):

  user = 'user'
  play = 'playlist'
  if url.find(play)  > -1:
    playlist = url.replace('http://www.youtube.com/playlist?list=', '')
    json_url = YouTubeFeedURL + 'playlists/' + playlist
  else:
    if url.find(user)  > -1:
      # I have seen some user feed urls that may also have data after the user name 
	  # Ex. http://www.youtube.com/user/NewarkTimesWeddings?feature=watch
	  # could use if url.find('?') then username.split(?) and then username=username[0] to pull that out
      user_name = url.replace('http://www.youtube.com/user/', '') 
      # need to change all letters to lowercase
      user_name = user_name.lower()
      json_url = YouTubeFeedURL + 'users/' + user_name + '/uploads'
    else:
      json_url = 'false'

  return json_url

####################################################################################################################
# Currently this function will work with playlist or user upload feeds and produces results after the JSON url is constructed
# Set up a separate function (YouTubeJSON) for putting together the JSON url 
# The json_url used in this function is 'https://gdata.youtube.com/feeds/api/' + 'playlists/' OR 'users/' + ID +'?v=2&alt=json&start-index=1&max-results=50'

# Need to change the function name to YouTubeFeed function 
@route(PREFIX + '/showyoutube')
def ShowYouTube(title, url):

  oc = ObjectContainer()
  # show_url is needed for the alternative HTML method in the comments below
  json_url = url + '?v=2&alt=json&start-index=1&max-results=50'

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
    return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
  else:
    return oc

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

#####################################################################################################################
# This function picks up the first page of results from the second carousel on a page
# Using this function to pick up other videos available for Burning Love, no other shows have a second carousel
# so not sure if it works for other shows
# Test if with Chow Ciao
@route(PREFIX + '/showblip')
def ShowBlip(title, url):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL(url)
  user_id = html.xpath('//div[@id="PageInfo"]//@data-users-id')[0]
  # it only seems to get the first page even though there are other pages. 
  # so we have to get the number of pages and make a loop to get all the pages
  page_num = html.xpath('//div[@class="Pagination"]/span[@class="LastPage"]//text()')[0]
  page_num = int(page_num)
  data_url = 'http://blip.tv/pr/show_get_full_episode_list?users_id=' + user_id + '&lite=0&esi=1'
  page = HTML.ElementFromURL(data_url)
  count = 0

  while count <= page_num: 
    count += 1
    show_url = data_url + '&page=' + str(count)
    page = HTML.ElementFromURL(show_url)

    for video in page.xpath('//div[@class="EpisodeList"]/ul/li/a'):
      url = video.xpath('./meta//@content')[0]
      thumb = video.xpath('./span/img//@src')[0]
      # lots of extra spaces before and after the text in the fields below so we need to do a strip on all of them
      title = video.xpath('./span[@class="Title"]//text()')[0]
      title = title.strip()
      description = video.xpath('./span[@class="Description"]//text()')[0]
      description = description.strip()
      date = video.xpath('./span[@class="ReleaseDate"]//text()')[0]
      date = date.strip()
      date = Datetime.ParseDate(date)
      duration = video.xpath('./span[@class="Runtime"]//text()')[0]
      duration = duration.strip()
      duration = Datetime.MillisecondsFromString(duration)
				
      oc.add(VideoClipObject(
        url = url, 
        title = title,
        summary = description,
        originally_available_at = date,
        duration = duration,
        thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON))))
      
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc

#############################################################################################################################
# This is a function to pulls the title and description from the head of a page
# may just use sections function instead
def GetShowInfo(url, show_thumb, show_type):
  page = HTML.ElementFromURL(url)
  title = page.xpath("//head//meta[@property='og:title']//@content")[0]
  description = page.xpath("//head//meta[@name='description']//@content")[0] 
  if show_thumb:
    thumb = show_thumb
  else:
    if show_type == 'yahoo':
      thumb = GetYahooThumb(title)
    else:
      thumb = GetThumb(url)

  show_list = [title, description, thumb]

  return show_list
  
#############################################################################################################################
# This is a function to pull the thumb from the head of a page
def GetThumb(url):
  page = HTML.ElementFromURL(url)
  try:
    thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
    if not thumb.startswith('http://'):
      thumb = http + thumb
  except:
    thumb = R(ICON)
  return thumb

#############################################################################################################################
# This is a function to pull the thumb from a the Yahoo Originals page and uses the show title to find the correct image
# It does not go through all selections in the carousel, but picks up most.  Would have to know the Yahoo section like 
# comedy, living, finance, etc to be able to pull the full list from the carousel
def GetYahooThumb(title):

  try:
    thumb_page = HTML.ElementFromURL(YahooOrigURL)
    try:
      thumb = thumb_page.xpath('//a[@class="media"]/img[@alt="%s"]//@style' % title)[0]
    except:
      thumb = thumb_page.xpath('//a[@class="img-wrap"]/img[@alt="%s"]//@style' % title)[0]
    thumb = thumb.replace("background-image:url('", '').replace("');", '')
  except:
    thumb = R(ICON)

  return thumb

############################################################################################################################
# This is to test if there is a Plex URL service for  given url.  
# Seems to return some RSS feeds as not having a service when they do, so currently unused and needs more testing
#       if URLTest(url) == "true":
def URLTest(url):
  if URLService.ServiceIdentifierForURL(url) is not None:
    url_good = 'true'
  else:
    url_good = 'false'
  return url_good

############################################################################################################################
# This would possibly eventually allow reentry of a bad url. Right Now it just keeps a section of show from giving an error
# for the entire section if one of the URLs are incorrect
# InputDirectoryObject(prompt=??,  title=??, )
def URLError(url):
  return ObjectContainer(header="Empty", message='Unable to display videos for this show. The show URL %s is entered incorrectly or incompatible with this channel' %url)

