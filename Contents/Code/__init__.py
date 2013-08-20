# COULD ADD CODE TO LOOK FOR RSS FEED URLS IN THE HEAD OF THE URL AS EXTRA CHECK FOR VIMEO AND OTHERS THAT HAVE RSS
TITLE    = 'Webisodes'
PREFIX   = '/video/webisodes'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'

RSS_ICON = 'rss-feed-icon.png'
YOUTUBE_ICON = 'youtube-icon.png'
HULU_ICON = 'hulu-icon.png'
YAHOO_ICON = 'yahoo-icon.png'
VIMEO_ICON = 'vimeo-icon.png'
BLIPTV_ICON = 'bliptv-icon.png'

SHOW_DATA = 'data.json'
NAMESPACES = {'feedburner': 'http://rssnamespace.org/feedburner/ext/1.0'}

RE_LIST_ID = Regex('listId: "(.+?)", pagesConfig: ')
RE_CONTENT_ID = Regex('CONTENT_ID = "(.+?)";')
RE_HULU_ID = Regex('var rawData = {"id": (.+?), "name":')
RE_HULU_TOKEN = Regex("API_DONUT = '(.+?)';")

YouTubeFeedURL = 'https://gdata.youtube.com/feeds/api/'
HuluEpURL = 'http://www.hulu.com/watch/'
HuluJSON = 'http://www.hulu.com/mozart/v1.h2o/shows/%s/episodes?free_only=0&show_id=%s&sort=seasons_and_release&video_type=episode&items_per_page=32&access_token=%s'
YahooURL = 'http://screen.yahoo.com'
YahooOrigURL = 'http://screen.yahoo.com/yahoo-originals/'
YahooJSON = 'http://screen.yahoo.com/_xhr/slate-data/?list_id=%s&start=0&count=50&pc_starts=1,6,11,16,21,26&pc_layouts=1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u,1u-1u-1u-1u-1u'
# This is a global variable for the parameters of the Yahoo JSON data file. Currently it returns 32 items. 
# To add more returned results, add the last number plus 5 to pc_starts and ",1u-1u-1u-1u-1u" to pc_layouts for each five entries you want to add

http = 'http:'
MAXRESULTS = 50

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
  
  #oc.add(DirectoryObject(key=Callback(OtherSections, title="Hulu Original Shows", show_type='hulu'), title="Hulu Original Shows", thumb=R(HULU_ICON)))
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

        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type='rss'), title=title, summary=description, thumb=thumb))
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
      url = show[i]["url"]
      thumb = show[i]["thumb"]
      i+=1
      try:
        page = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
        title = page.xpath("//head//meta[@property='og:title']//@content")[0]
      except:
        oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type=show_type), title="Invalid or Incompatible URL", summary="The URL entered in the database was either incorrect or not in the proper format for use with this channel."))
        continue

      description = page.xpath("//head//meta[@name='description']//@content")[0] 
      if not thumb:
        try:
          # THOUGHT ABOUT CHANGING THIS TO A REDIRECT THUMB BUT THE OPTION TO ADD YOUR OWN THUMB WOULD NOT WORK IF THIS WERE IN THE CALLBACK
          if show_type == 'yahoo':
            thumb = GetYahooThumb(title)
          else:
            thumb = page.xpath("//head//meta[@property='og:image']//@content")[0]
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
          oc.add(DirectoryObject(key=Callback(ShowYouTube, title=title, url=url, json_url=json_url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb), summary=description))
        else:
          oc.add(DirectoryObject(key=Callback(URLError, url=url, show_type='youtube'),title="Invalid URL", summary="The URL entered in the database was incorrect."))
      elif show_type == 'hulu':
        oc.add(DirectoryObject(key=Callback(ShowHulu, title=title, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb), summary=description))
      elif show_type == 'yahoo':
        oc.add(DirectoryObject(key=Callback(ShowYahoo, title=title, url=url, thumb=thumb), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb), summary=description))
      elif show_type == 'blip':
        oc.add(DirectoryObject(key=Callback(ShowBlip, title=title, url=url), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb), summary=description))
      else:
        oc.add(DirectoryObject(key=Callback(ShowRSS, title=title, url=url, show_type=show_type), title=title, thumb=Resource.ContentsOfURLWithFallback(thumb), summary=description))
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
@route(PREFIX + '/showrss')
def ShowRSS(title, url, show_type):

# The RSSSection try above tells us if the RSS feed is the correct format. so we do not need to put this function's data pull in a try/except

  oc = ObjectContainer(title2=title)
  show_title = title
  show_url = url
  if show_type == 'vimeo':
    rss_url = url + '/videos/rss'
  else:
    rss_url = url
  xml = XML.ElementFromURL(rss_url)
  for item in xml.xpath('//item'):
    epUrl = item.xpath('./link//text()')[0]
    title = item.xpath('./title//text()')[0]
    date = Datetime.ParseDate(item.xpath('./pubDate//text()')[0])
    # The description actually contains pubdate, link with thumb and description so we need to break it up
    epDesc = item.xpath('./description//text()')[0]
    try:
      new_url = item.xpath('./feedburner:origLink//text()', namespaces=NAMESPACES)[0]
      Log('the value of new_url is %s' %new_url)
      epUrl = new_url
    except:
      pass
    html = HTML.ElementFromString(epDesc)
    els = list(html)
    try:
      thumb = html.cssselect('img')[0].get('src')
    except:
      thumb = R(RSS_ICON)

    summary = []

    for el in els:
      if el.tail: summary.append(el.tail)
	
    summary = '. '.join(summary)

    test = URLTest(epUrl)
    if test == 'true':
      oc.add(VideoClipObject(
        url = epUrl, 
        title = title, 
        summary = summary, 
        thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(ICON)), 
        originally_available_at = date
      ))
      oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

    else:
      Log('The url test failed and returned a value of %s' %test)
      oc.add(DirectoryObject(key=Callback(URLNoService, title=title),title="No URL Service for Video", summary='There is not a Plex URL service for %s.' %title))

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type=show_type, title=title), title="Delete This Show", summary="Click here to delete this show", thumb=R(ICON)))

  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type=show_type, url=show_url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this RSS feed right now.")      
  else:
    return oc

###################################################################################################
# This is for shows that are on Hulu. 
# Unfortunately Hulu Webkit only plays audio for me at this time, so not fully tested
@route(PREFIX + '/showhulu')
def ShowHulu(title, url):
  oc = ObjectContainer(title2 = title)
  show_title = title
  show_url = url
  show_id = HuluID(url)
  # they changed the access_token for the JSON, so now just pulling it from page
  access_token = HuluToken(url)
  json_url = HuluJSON %(show_id, show_id, access_token)

  try:
    ep_data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

  for video in ep_data['data']:
    ep_url = HuluEpURL + str(video['video']['id'])
    title = video['video']['title']
    episode =  video['video']['episode_number']
    season = video['video']['season_number']
    thumb = video['video']['thumbnail_url']
    duration = video['video']['duration']
    duration = float(duration) * 1000
    date = Datetime.ParseDate(video['video']['available_at'])
    summary = video['video']['description']

    oc.add(EpisodeObject(
      url = ep_url, 
      title = title,
      season = season,
      thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(HULU_ICON)),
      summary = summary,
      index = int(episode),
      duration = int(duration),
      originally_available_at = date))

  oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='hulu', title=title), title="Delete Hulu Show", summary="Click here to delete this Hulu Show", thumb=R(ICON)))

  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='hulu', url=show_url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")      
  else:
    return oc

###############################################################################################################
# This function pulls the show ID from each show page for it to be entered into the JSON data url for Hulu
# The best place to pull it is in the show's URL from a javascript in the head of type text/javascript that
# contains the line "Hulu.Mobile.currentShowId = 6918;"
@route(PREFIX + '/huluid')
def HuluID(url):
  ID = ''
  content = HTTP.Request(url, cacheTime = CACHE_1DAY).content
  ID = RE_HULU_ID.search(content).group(1)
  return ID

###############################################################################################################
# This function pulls the API_DONUT from each show page for it to be entered into the JSON data url for Hulu as the access token
# This access token seems to change every day
@route(PREFIX + '/hulutoken')
def HuluToken(url):
  token = ''
  content = HTTP.Request(url, cacheTime = CACHE_1HOUR).content
  token = RE_HULU_TOKEN.search(content).group(1)
  return token

###############################################################################################################
# This function splits Yahoo Shows into two folders to pull the first 3 videos at top and any current episodes with the JSON data file
# through the VideoYahoo function and extra videos that is found may be in the second carousel through the MoreVideosYahoo function
# Not sure if I should keep both section for all Yahoo Shows or just use it for Burning Love 
@route(PREFIX + '/yahooshows')
def ShowYahoo(title, url, thumb):
# Create two folders, for current episodes and for other videos that we can pull from the MoreVideosYahoo function below
  oc = ObjectContainer(title2=title)

  show_title = title
  show_url = url
  oc.add(DirectoryObject(
    key=Callback(VideoYahoo, title=title, url=url),
    title='Latest Videos',
    thumb=thumb))

  oc.add(DirectoryObject(
    key=Callback(MoreVideosYahoo, title=title, url=url),
    title='Addtional Videos',
    thumb=thumb))

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='yahoo', title=title), title="Delete Yahoo Show", summary="Click here to delete this Yahoo Show", thumb=R(ICON)))
      
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='yahoo', url=show_url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

  return oc

###############################################################################################################
# This function pulls the Content ID from each show page for it to be entered into the JSON data url
# One show (Animal All Stars) does use a List ID instead, so we check for that List ID first.
@route(PREFIX + '/yahooid')
def YahooID(url):
  ID = ''
  content = HTTP.Request(url, cacheTime = CACHE_1DAY).content
  try:
    ID = RE_LIST_ID.search(content).group(1)
  except:
    ID = RE_CONTENT_ID.search(content).group(1)
  return ID

################################################################################################################
# This function pulls the videos for Yahoo shows using JSON data file
# It pulls the videos in the main box as well as any recent episodes
@route(PREFIX + '/showyahoo')
def VideoYahoo(title, url):

  oc = ObjectContainer(title2=title)
  JSON_ID = YahooID(url)
  # could clean this url up with global variables
  JSON_url = YahooJSON %JSON_ID
  try:
    data = JSON.ObjectFromURL(JSON_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

  if data.has_key('items'):
    for video in data['items']:
      description = video['summary_short']
      desc_data = HTML.ElementFromString(description)
      summary = desc_data.xpath('//text()')[0]
      title = video['title_short'] 
      thumb = video['image_thumb_url']
      if video['type'] == 'video':
        url = video['link_url'] 
        duration = Datetime.MillisecondsFromString(video['duration'])
        date = Datetime.ParseDate(video['date'])
		# some entries do not have urls
        if url:
          if not url.startswith('http://'):
            url = YahooURL + url

          oc.add(VideoClipObject(
            url = url, 
            title = title, 
            thumb = Resource.ContentsOfURLWithFallback(thumb),
            summary = summary,
            duration = duration,
            originally_available_at = date))
	# This section is for show with type link in json data that have no dates or duration(just one Yahoo Animal Allstars)
      else:
        # The url in the link_url field does not work with URL service so pull url out of summary_short
        url = desc_data.xpath('//a//@href')[0]
		# some entries do not have urls
        if url:
          if not url.startswith('http://'):
            url = YahooURL + url

          oc.add(VideoClipObject(
            url = url, 
            title = title, 
            summary = summary,
            thumb = Resource.ContentsOfURLWithFallback(thumb))) 

  # They already put these in the right order, so adding a sort just messes up the order because sometimes three episodes are released on the same day
  # oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc

#####################################################################################################################
# This picks up videos in the second section on a show page with an id="mediabcarouselmixedlpca_2"
# It only picks up older episodes available on the Yahoo Screens website for Burning Love right now
# BECAUSE WE DO A 1 DAY CACHE ON THE HTML, THIS MAY NOT UPDATE VIDEOS AS FAST AS NORMAL FOR VIDEO PULLS, BUT MISC VIDEOS SO NO ISSUE FOR NOW
@route(PREFIX + '/morevideosyahoo')
def MoreVideosYahoo(title, url):

  oc = ObjectContainer(title2=title)
  try:
    html = HTML.ElementFromURL(url)
    smTitle = title.lower()
    smTitle = smTitle.replace(" ", '')
    for video in html.xpath('//div[@id="mediabcarouselmixedlpca_2"]/div/div/ul/li/ul/li'):
      url = video.xpath('./div/a/@href')[0]
      url = YahooURL + url
      thumb = video.xpath('./div/a/img//@style')[0]
      thumb = thumb.replace("background-image:url('", '').replace("');", '')
      title = video.xpath('./div/div/p/a//text()')[0]
      data_provider =  video.xpath('.//@data-provider-id')[0]
	
      if smTitle in data_provider: 
        oc.add(VideoClipObject(
          url = url, 
          title = title, 
          thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(YAHOO_ICON))))

      else:  
        return ObjectContainer(header="Empty", message="There are no addtional videos to display for this show right now.")

  except:  
    return ObjectContainer(header="Empty", message="There are no addtional videos to display for this show right now.")

  # This section does not have a release date, so you would have to sort by title, which will not always give your the best results
  # oc.objects.sort(key = lambda obj: obj.title, reverse=True)
    
  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc
    
###################################################################################################################
# This is a function to produce the JSON url needed for the YouTubeFeed function
# It returns to the OtherSectiona so it can also serve as added url validation
@route(PREFIX + '/youtubejson')
def YouTubeJSON(url):

  user = 'user'
  play = 'playlist'
  if url.find(play)  > -1:
    playlist = url.split('list=')[1]
    json_url = YouTubeFeedURL + 'playlists/' + playlist
  else:
    if url.find(user)  > -1:
      if '?' in url: 
        # Some may have a quesiton mark after the username Ex. http://www.youtube.com/user/NewarkTimesWeddings?feature=watch
        url = url.split('?')[0]
      user_name = url.split('/user/') [1]
      # need to change all letters to lowercase
      user_name = user_name.lower()
      json_url = YouTubeFeedURL + 'users/' + user_name + '/uploads'
    else:
      json_url = 'false'

  return json_url

####################################################################################################################
# Currently this function will work with playlist or user upload feeds and produces results after the JSON url is constructed
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
        thumb = Resource.ContentsOfURLWithFallback(thumb),
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

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='youtube', title=title), title="Delete YouTube Show", summary="Click here to delete this YouTube Show", thumb=R(ICON)))

  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='youtube', url=show_url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

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
@route(PREFIX + '/showblip')
def ShowBlip(title, url):

  oc = ObjectContainer(title2=title)
  show_title = title
  # do not need a show_url for add image, just use url
  # since we are just pulling page info here an not videos, a one day cache should be fine and speed up pull
  html = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
  # Put in a try except error message here to make sure URL in in proper formate
  try:
    user_id = html.xpath('//div[@id="PageInfo"]//@data-users-id')[0]
    # to get all pages we get the number of pages and make a loop to get all the pages
    page_num = int(html.xpath('//div[@class="Pagination"]/span[@class="LastPage"]//text()')[0])
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for this show. Reenter URL and try again'))

  data_url = 'http://blip.tv/pr/show_get_full_episode_list?users_id=' + user_id + '&lite=0&esi=1'
  count = 0

  while count <= page_num: 
    count += 1
    show_url = data_url + '&page=' + str(count)
    page = HTML.ElementFromURL(show_url)

    for video in page.xpath('//div[@class="EpisodeList"]/ul/li/a'):
      ep_url = video.xpath('./meta//@content')[0]
      thumb = video.xpath('./span/img//@src')[0]
      # lots of extra spaces before and after the text in the fields below so we need to do a strip on all of them
      title = video.xpath('./span[@class="Title"]//text()')[0]
      title = title.strip()
      description = video.xpath('./span[@class="Description"]//text()')[0]
      description = description.strip()
      date = video.xpath('./span[@class="ReleaseDate"]//text()')[0]
      date = Datetime.ParseDate(date.strip())
      try:
        duration = video.xpath('./span[@class="Runtime"]//text()')[0]
        duration = Datetime.MillisecondsFromString(duration.strip())
      except:
        duration = 0
				
      oc.add(VideoClipObject(
        url = ep_url, 
        title = title,
        summary = description,
        originally_available_at = date,
        duration = duration,
        thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=R(BLIPTV_ICON))))

  oc.objects.sort(key = lambda obj: obj.originally_available_at, reverse=True)

  oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, show_type='blip', title=title), title="Delete Blip TV Show", summary="Click here to delete this Blip TV Show", thumb=R(ICON)))
     
  oc.add(InputDirectoryObject(key=Callback(AddImage, title=show_title, show_type='blip', url=url), title="Add Image For %s" %show_title, summary="Click here to add an image url for this show", prompt="Enter the full URL (including http://) for the image you would like displayed for this show"))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")
  else:
    return oc

#############################################################################################################################
# This is a function to pull the thumb from a the Yahoo Originals page and uses the show title to find the correct image
# It does not go through all selections in the carousel, but picks up most.  Would have to know the Yahoo section like 
# comedy, living, finance, etc to be able to pull the full list from the carousel
@route(PREFIX + '/getyahoothumb')
def GetYahooThumb(title):

  try:
    thumb_page = HTML.ElementFromURL(YahooOrigURL, cacheTime = CACHE_1WEEK)
    try:
      thumb = thumb_page.xpath('//a[@class="media"]/img[@alt="%s"]//@style' % title)[0]
    except:
      thumb = thumb_page.xpath('//a[@class="img-wrap"]/img[@alt="%s"]//@style' % title)[0]
    thumb = thumb.replace("background-image:url('", '').replace("');", '')
  except:
    thumb = R(YAHOO_ICON)

  return thumb

############################################################################################################################
# This is to test if there is a Plex URL service for  given url.  
# Seems to return some RSS feeds as not having a service when they do, so currently unused and needs more testing
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
# This would possibly eventually allow reentry of a bad url. Right Now it just keeps a section of show from giving an error
# for the entire section if one of the URLs are incorrect
@route(PREFIX + '/urlerror')
def URLError(url, show_type):

  oc = ObjectContainer()
  
  oc.add(DirectoryObject(key=Callback(EditShow, url=url), title="Edit Show", thumb=R(ICON)))
  oc.add(DirectoryObject(key=Callback(DeleteShow, title="Delete Show", url=url, show_type=show_type), title="Delete Show", thumb=R(ICON), summary="Delete this URL from your list of Shows"))

  return oc

############################################################################################################################
# This keeps a section of show from giving an error for the entire section if one of the URLs does not have a service
@route(PREFIX + '/urlnoservice')
def URLNoService(title):
  return ObjectContainer(header="Error", message='There is no Plex URL service for the %s. A Plex URL service is required for RSS feeds to work. You can use the Delete Show button to remove this show' %title)

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
@route(PREFIX + '/addshow')
def AddShow(show_type, query, url=''):

  url = query
  # Checking to make sure http on the front
  if url.startswith('www'):
    url = http + '//' + url
  else:
    pass
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
