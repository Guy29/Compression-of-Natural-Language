import wget, time, os, urllib

urls = open('../../Data/all_urls.txt','r+').read().split()
urls = list(enumerate(urls))
print(len(urls))

downloaded = set(os.listdir('../../Data/book_zips'))

t0 = time.time()
for i,url in urls:
  try:
    if i<2900: continue
    print(i,url)
    if url.split('/')[-1] in downloaded: continue
    wget.download(url, out='../../Data/book_zips/'+url.split('/')[-1], bar=None)
    print(i,url,time.time()-t0)
  except urllib.error.HTTPError: continue