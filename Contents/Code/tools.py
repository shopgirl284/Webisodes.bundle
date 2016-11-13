PREFIX   = '/video/webisodes'
FEATURE_PREFIX = '%s/tools' % PREFIX

SHOW_DATA = 'data.json'
LIVE_DATA = 'live.json'

YouTube_URL = 'http://www.youtube.com'
VIMEO_URL = 'http://vimeo.com/'
DAILYMOTION_URL = 'http://www.dailymotion.com/'


####################################################################################################################
@route(FEATURE_PREFIX)
def MainMenu():

    oc = ObjectContainer()
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
@route(FEATURE_PREFIX + '/rokuusers')
def RokuUsers (title):
    return ObjectContainer(header="Special Instructions for Roku Users", message="Remoku (www.remoku.tv) makes it easy to add new shows by cutting and pasting URLs from your browser.")

########################################################################################################################
# this is special instructions for Plex Web users
@route(FEATURE_PREFIX + '/plexwebusers')
def PlexWebUsers (title):
    return ObjectContainer(header="Special Instructions for Plex Web Users", message="Plex Web does not provide input boxes. To add a new show with Plex Web paste or type the URLs in the Search Box at the top of the page while in the main section for that type of show. A pop-up message will confirm if your new show has been added. New shows may not be visible for 24 hours, based on your browser cache settings.")

#############################################################################################################################
# The FUNCTION below can be used to reload the original data.json file if errors occur and you need to reset the program
@route(FEATURE_PREFIX + '/resetshows')
def ResetShows(title):
    Dict["MyShows"] = []
    return ObjectContainer(header="Cleared", message='All shows have been removed from this channel')

############################################################################################################################
# This function creates a directory entry when a show URL from the Dict['MyShows'] fails an XML/HTML.ElementFromURL pull
# to show users the error instead of skipping them. And in this function we can give options to fix that show URL 
@route(PREFIX + '/urlerror')
def URLError(url, show_type):

    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(DeleteShow, title="Delete Show", url=url), title="Delete Show", thumb=R('delete.png'), summary="Delete this URL from your list of shows. You can try again by choosing the Add Show option"))
    return oc

#############################################################################################################################
# This is a function to add a show to Dict['MyShows'].  
@route(FEATURE_PREFIX + '/addshow')
def AddShow(show_type, query, url=''):

    Log('the value of query is %s' %query)
    url = query
    # Fix or clean up url
    if show_type=='live':
        if '.m3u8' not in url:
            return ObjectContainer(header=L('Not Added'), message=L('Unable to add the live feed. Only HLS (m3u8) live feeds can be added to this channel'))
        if url.startswith('www'):
            url = 'http://' + url
    else:
        if url.startswith('www') or url.startswith('http://') or url.startswith('https://'):
            url = URLCleanUp(url, show_type)
        else:
            url = URLFix(url, show_type)
    
    # create new item as json
    shows = Dict["MyShows"]
    list_item = {}
    list_item[unicode('type')] = unicode(show_type)
    list_item[unicode('name')] = unicode('')
    list_item[unicode('url')] = unicode(url)
    list_item[unicode('thumb')] = unicode('')
    shows.append(list_item)
    Dict["MyShows"] = shows

    #Log(Dict['MyShows'])
    return ObjectContainer(header=L('Added'), message=L('Your show has been added to the channel'))

###################################################################################################################
# This is a function cleans up URLs that have been entered as URLs
# It returns to the AddShow function to produce a proper url
@route(FEATURE_PREFIX + '/urlcleanup')
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
@route(FEATURE_PREFIX + '/urlfix')
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
# This function loads the json data file and replaces the existing Dict["MyShows"] 
@route(FEATURE_PREFIX + '/loaddata')
def LoadData():
    Dict["MyShows"] = []
    json_data = Resource.Load(SHOW_DATA)
    Dict["MyShows"] = JSON.ObjectFromString(json_data)
    #Log(Dict['MyShows'])
    return ObjectContainer(header=L('Updated'), message=L('Your show data has been updated from the json data file in the Resources folder'))
#############################################################################################################################
# This function adds the json data file to the existing Dict["MyShows"] (can also use x.extend(y))
# CANNOT PREVENT DUPLICATES 
@route(FEATURE_PREFIX + '/adddata')
def AddData():
    shows = Dict["MyShows"]
    json_data = Resource.Load(SHOW_DATA)
    json_shows = JSON.ObjectFromString(json_data)
    Dict["MyShows"] = shows + json_shows
    return ObjectContainer(header=L('Updated'), message=L('Your show data has been updated to inlude the json data in the Resources folder'))

############################################################################################################################
# This is a function shows the options to delete a show from the Dict['MyShows'] or update or add images or tilte for live shows
@route(FEATURE_PREFIX + '/editeshow')
def EditShow(url, title):

    oc = ObjectContainer()
  
    oc.add(DirectoryObject(key=Callback(DeleteShow, url=url, title=title), title="Delete Show", summary="Click here to delete this show from your listing"))
    oc.add(InputDirectoryObject(key=Callback(AddTitle, url=url, title=title), title="Add or Change Title", summary="Click here to add a title or update the existing title for this show", prompt="Enter the title that you would like to appear in the listing for this show"))
    oc.add(InputDirectoryObject(key=Callback(AddImage, url=url, title=title), title="Add or Change Image", summary="Click here to add a custom image or update the existing image for this show by entering the full URL of an existing online image", prompt="Enter the full URL (including http://) for an existing online image"))

    return oc

############################################################################################################################
# This is a function to delete a show from the Dict['MyShows']
@route(FEATURE_PREFIX + '/deleteshow')
def DeleteShow(url, title):

    shows = Dict["MyShows"]
    for show in shows:
        if show['url'] == url:
            shows.remove(show)
            break
    Dict["MyShows"] = shows
    #Log(Dict['MyShows'])
    return ObjectContainer(header=L('Deleted'), message=L('Your show has been deleted from the channel'))

#############################################################################################################################
# This is a function to add an url for an image the Dict['MyShows'].  
@route(FEATURE_PREFIX + '/addimage')
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
    Dict["MyShows"] = shows

    return ObjectContainer(header=L('Added'), message=L('Your image has been added for the show'))
#############################################################################################################################
# This is a function to add or update the title the Dict['MyShows'] for a show.  
@route(FEATURE_PREFIX + '/addtitle')
def AddTitle(query, url, title=''):

    title = query

    shows = Dict["MyShows"]
    for show in shows:
        if show['url'] == url:
            show['name'] = title
            break
        else:
            pass
    Dict["MyShows"] = shows

    return ObjectContainer(header=L('Added'), message=L('Your show title has been updated'))
