from os.path import basename
import os
import urllib.request
import csv
from urllib.parse import urlparse, parse_qs

download_dir = r'.\Video'

if not os.path.exists(download_dir):
    os.makedirs(download_dir, exist_ok=True)

def download(url, out_path):
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req)
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query)['video_id'][0]+'.mp4'
    localName = os.path.join(out_path, video_id)
    with open(localName, 'wb') as f:
        f.write(r.read())

now = 0
with open('./Crawl_data/link_download_video.csv', mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for row in csv_reader:
        now = now + 1
        download('https:'+row[1], download_dir)
        print(f'Downloaded {now} files')
