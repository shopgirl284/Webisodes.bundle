PREFIX   = '/video/webisodes'
FEATURE_PREFIX = '%s/dailymotion' % PREFIX

DAILYMOTION_URL = 'http://www.dailymotion.com/'
DAILYMOTION_ICON = 'dailymotion-icon.png'

import tools
####################################################################################################################
# This function creates sections for Daily Motion users and channels
@route(FEATURE_PREFIX)
def MainMenu(title, url, vid_type, dm_id, thumb):
  
    oc = ObjectContainer(title2=title)
    show_title = title
    show_url = url
    oc.add(DirectoryObject(key=Callback(DailyMotionVideo, title="%s Videos" %title, vid_type=vid_type, dm_id=dm_id), title="%s Videos" %title, thumb=thumb))
    oc.add(DirectoryObject(key=Callback(DailyMotionPL, title="%s Playlist" %title, dm_id=dm_id), title="%s Playlist" %title, thumb=thumb))

    oc.add(DirectoryObject(key=Callback(tools.EditShow, url=url, title=title), title="Edit this Show", summary="Click here to edit this Daily Motion Show"))

    return oc
#############################################################################################################################
# This function pulls a lists of Daily Motion playlists for a user or channel
@route(FEATURE_PREFIX + '/dailymotionpl')
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
@route(FEATURE_PREFIX + '/dailymotionvideos', page=int, pl_only=bool)
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
        oc.add(DirectoryObject(key=Callback(tools.DeleteShow, url=url, title=title), title="***DELETE THE %s SHOW***" %title, summary="Click here to delete this Daily Motion Show"))
        oc.add(InputDirectoryObject(key=Callback(tools.AddImage, title=title, url=url), title="Add a Custom Image For %s" %title, summary="Add an alternative image url for this show", prompt="Enter the full URL (including http://) for an existing online image"))

    if len(oc) < 1:
        return ObjectContainer(header=L('Empty'), message=L('There are no videos to display for this feed right now'))
    else:
        return oc

