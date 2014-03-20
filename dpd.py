# -*- coding: utf-8 -*-
"""
    dpd
    ~~~

    Douban photo album downloader

    :copyright: (c) 2014 by fsp.
    :license: BSD.
"""
import os
import re
import time

# from gevent import monkey; monkey.patch_all()
import urllib
# import gevent


def grab_photos(album):
    """Get all photo links
    
    :param album: album id.
    """
    photos = []
    # regex used to find next page link
    next_re = re.compile(r'<span class="thispage".*?>.*?</span>.*?'
                           '<a href="(?P<next_url>.*?)".*?</a>', re.S)
    # regex used to find photo links
    photo_re = re.compile(r'<div class="photo_wrap">.*?'
            '<a href="(?P<photo_url>.*?)" class="photolst_photo".*?>', re.S)
    
    next_url = "http://www.douban.com/photos/album/%s/" % album
    while next_url:
        html = urllib.urlopen(next_url).read()
        for photo_m in photo_re.finditer(html):
            photos.append(photo_m.group('photo_url'))
        next_m = next_re.search(html)
        next_url = next_m.group('next_url') if next_m else None
    return photos


def down_photos(photos, path):
    """Download
    
    :param photos: The photos list.
    :param path: The path you want to save files.
    """
    # regex used to find photo link in photo detail page
    photo_re = re.compile(r'<div class="image-show-inner">.*?'
                           '<a class="mainphoto".*?<img src='
                           '"(?P<photo_url>.*?)".*?>.*?.*?</a>.*?</div>', re.S)

    def down_photo(photo):
        html = urllib.urlopen(photo).read()
        photo_m = photo_re.search(html)
        if not photo_m:
            return
        photo_url = photo_m.group('photo_url')
        filename = photo_url.split('/')[-1]
        filename = os.path.join(path, filename)
        urllib.urlretrieve(photo_url, filename)
    
    for photo in photos:
        time.sleep(1)
        down_photo(photo)
    # Douban baned
    # while photos[:100]:
    #     jobs = [gevent.spawn(down_photo, photo) for photo in photos[:100]]
    #     gevent.joinall(jobs)
    #     photos = photos[100:]


def main(album, path):
    photos = grab_photos(album)
    print "抓取到%s张图片" % str(len(photos))
    print "下载中..."
    down_photos(photos, path)
    print "图片下载完成"


if __name__ == "__main__":
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-a", "--album", dest="album", help="The album number")
    parser.add_option("-p", "--path", dest="path", help="The destination")
    (options, args) = parser.parse_args()

    album = options.album if options.album else None
    path = options.path if options.path else None
    if album and path:
        main(album, path)
    else:
        print "必须提供图片相册序号和本地存储路径... （使用-h获取帮助)"
