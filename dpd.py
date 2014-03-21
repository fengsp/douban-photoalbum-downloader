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
import urllib2
import cookielib
# import gevent


# handler=urllib2.HTTPHandler(debuglevel=1)
redirect_handler = urllib2.HTTPRedirectHandler()
cookie_jar = cookielib.CookieJar()
# Set cookie part
cookie = {}
cookie["__utma"] = "30149280.947231545.1372924530.1395309577.1395314599.5"
cookie["__utmv"] = "30149280.6435"
cookie["__utmz"] = "30149280.1395309577.4.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)"
cookie["bid"] = "QaJRnANYt3A"
cookie["ll"] = "108288"
cookie_list = []
for k, v in cookie.iteritems():
    cookie_list.append(k + '=' + v)
cookie = ';'.join(cookie_list)

cookie_handler = urllib2.HTTPCookieProcessor(cookie_jar)
opener = urllib2.build_opener(redirect_handler, cookie_handler)
headers = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36')]
opener.addheaders = headers
# opener.addheaders.append(('Cookie', cookie))
urllib2.install_opener(opener)


def save_photo(photo_url, filename):
    """Save one photo

    :param photo_url: photo link.
    :param filename: filepath.
    """
    r = urllib2.urlopen(photo_url).read()
    with open(filename, "wb") as f:
        f.write(r)


def get_page(page_url):
    return urllib2.urlopen(page_url).read()


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
        html = get_page(next_url)
        for photo_m in photo_re.finditer(html):
            photos.append(photo_m.group('photo_url'))
        next_m = next_re.search(html)
        next_url = next_m.group('next_url') if next_m else None
        time.sleep(1)
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

    photo_count = 0

    def down_photo(photo):
        try:
            html = get_page(photo)
            photo_m = photo_re.search(html)
            if not photo_m:
                return False
            photo_url = photo_m.group('photo_url')
            filename = photo_url.split('/')[-1]
            filename = os.path.join(path, filename)
            save_photo(photo_url, filename)
            return True
        except:
            return False
    
    for photo in photos:
        time.sleep(1)
        if down_photo(photo):
            photo_count += 1
        if photo_count and photo_count % 10 == 0:
            print "已下载到%s张图片..." % photo_count
    # Douban baned
    # while photos[:100]:
    #     jobs = [gevent.spawn(down_photo, photo) for photo in photos[:100]]
    #     gevent.joinall(jobs)
    #     photos = photos[100:]


def main(album, path):
    photos = grab_photos(album)
    print "抓取到%s张图片" % len(photos)
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
