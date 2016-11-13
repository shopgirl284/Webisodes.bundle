PREFIX   = '/video/webisodes'
FEATURE_PREFIX = '%s/mediaobjects' % PREFIX

####################################################################################################
# This function creates an audio object container for RSS feeds that have a media file in the feed
@route(PREFIX + '/createaudioobject')
def CreateAudioObject(url, media_type, title, originally_available_at, thumb, summary, include_container=False):

    local_url=url.split('?')[0]
    # Since we want to make the date optional, we need to handle the Datetime.ParseDate() as a try in case it is already done or blank
    try:
        originally_available_at = Datetime.ParseDate(originally_available_at)
    except:
        pass
    if local_url.endswith('.mp3'):
        container = 'mp3'
        audio_codec = AudioCodec.MP3
    elif local_url.endswith('.flac'):
        container = Container.FLAC
        audio_codec = AudioCodec.FLAC
    elif local_url.endswith('.ogg'):
        container = Container.OGG
        audio_codec = AudioCodec.OGG
    else:
        Log('container type is None')
        container = ''

    new_object = TrackObject(
        key = Callback(CreateAudioObject, url=url, media_type=media_type, title=title, summary=summary, originally_available_at=originally_available_at, thumb=thumb, include_container=True),
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
####################################################################################################
# This function creates a video object container for RSS feeds that have a media file in the feed
@route(PREFIX + '/createvideoobject')
def CreateVideoObject(url, media_type, title, originally_available_at, thumb, summary, include_container=False):

    local_url=url.split('?')[0]
    # Since we want to make the date optional, we need to handle the Datetime.ParseDate() as a try in case it is already done or blank
    try:
        originally_available_at = Datetime.ParseDate(originally_available_at)
    except:
        pass

    if  local_url.endswith('.m4a') or local_url.endswith('.mp4') or local_url.endswith('MPEG4') or local_url.endswith('h.264'):
        container = Container.MP4
    elif local_url.endswith('.flv') or local_url.endswith('Flash+Video'):
        container = Container.FLV
    elif local_url.endswith('.mkv'):
        container = Container.MKV
    else:
        Log('container type is None')
        container = ''

    new_object = VideoClipObject(
        key = Callback(CreateVideoObject, url=url, media_type=media_type, title=title, summary=summary, originally_available_at=originally_available_at, thumb=thumb, include_container=True),
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
                audio_codec = AudioCodec.AAC,
                video_codec = VideoCodec.H264,
                audio_channels = 2
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[new_object])
    else:
        return new_object
####################################################################################################
# This function will produce a live feed media object
@route(FEATURE_PREFIX + '/createliveobject', include_container=bool)
def CreateLiveObject(m3u8_url, title, thumb='', include_container=False):
    videoclip_obj = VideoClipObject(
        key = Callback(CreateLiveObject, m3u8_url=m3u8_url, title=title, include_container=True),
        rating_key = m3u8_url,
        title = title,
        items = [
            MediaObject(
                parts = [
                    PartObject(key=HTTPLiveStreamURL(m3u8_url))
                ],
                protocol = 'hls',
                container = 'mpegts'
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[videoclip_obj])
    else:
        return videoclip_obj
