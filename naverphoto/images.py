import requests
import lxml.html
import os
import time
from .functions import create_dir


class DLImages:
    JSON_URI = 'https://entertain.naver.com/photo/issueItemList.json'

    def __init__(self, category_id):
        self.params = {
            'cid': category_id,
            'page': 1
        }
        self.thumbnail_uris = []
        self.home_uri = 'https://entertain.naver.com/photo/issue/%s/100' % category_id
        self.title = ''
        self.total = 0
        self.main()

    def main(self):
        self.fetch_title()
        self.total = self.fetch_thumbnails()
        print('\r%s Images Found.' % self.total)
        self.download_image()
        print('\rDone.')

    def fetch_title(self):
        res = requests.get(self.home_uri)
        self.title = lxml.html.fromstring(res.text).xpath('//title')[0].text

    def fetch_thumbnails(self):
        print('\rFetch JSON Page %s ...' % self.params['page'], end='')
        res = requests.get(self.JSON_URI, params=self.params)
        thumbnails = res.json()['results'][0]['thumbnails']
        if len(thumbnails) == 0:
            return len(self.thumbnail_uris)
        for i in thumbnails:
            thumbnail_uri = i['thumbUrl'].split('?')[0]
            self.thumbnail_uris.append(thumbnail_uri)
        self.params['page'] += 1
        return self.fetch_thumbnails()

    def download_image(self):
        dir_path = './download/'
        create_dir(dir_path)
        dir_path += self.title + '/'
        create_dir(dir_path)
        count = 1
        for i in self.thumbnail_uris:
            parts = i.split('/')
            file_path = dir_path + parts[-1]
            if os.path.exists(file_path):
                print('\r%s / %s "%s" Already Exists.' % (count, self.total, file_path), end='')
            else:
                print('\r%s / %s Download "%s" to "%s" ...' % (count, self.total, i, file_path), end='')
                res = requests.get(i, timeout=10)
                with open(file_path, mode='wb') as f:
                    f.write(res.content)
                ctime = time.mktime((int(parts[-4]), int(parts[-3]), int(parts[-2]), 0, 0, 0, 0, 0, 0))
                os.utime(file_path, (ctime, ctime))
            count += 1
