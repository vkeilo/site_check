import urllib.request
import time
import datetime
import hashlib
import chardet
from bs4 import BeautifulSoup
import sys

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/49.0.2')]

file = open('./data/weblist.txt')
lines = file.readlines()
urls = []
for line in lines:
    temp = line.replace('\n', '')
    urls.append(temp)
print(urls)


def check1():
    print('开始检查1：')
    flag = 0
    ok_list = []
    for i in urls:
        tempurl = i
        try:
            opener.open(tempurl)
            print(tempurl+'正常')
            ok_list.append(tempurl)
        except urllib.error.HTTPError:
            print(tempurl+'=访问页面出错')
            with open('./data/连通性检测结果.txt', 'a') as f:
                f.write('\n')
                f.write('访问页面出错%s：%s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), tempurl))
                flag = 1
        except urllib.error.URLError:
            print(tempurl+'=访问页面出错')
            with open('./data/连通性检测结果.txt', 'a') as f:
                f.write('\n')
                f.write('访问页面出错%s：%s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), tempurl))
                flag = 1
        time.sleep(0.1)
    return ok_list, flag


def getmd5(str):
    str_md5 = hashlib.md5()
    str_md5.update(str.encode('utf-8'))
    return str_md5.hexdigest()


def check2(ok_list):
    print('开始检查2：')
    flag = 0
    f = open('./data/md5.txt', 'r')
    lines = f.read()
    lines = lines.split('\n')
    for i in range(len(lines)):
        lines[i] = lines[i].split('>')
    for i in ok_list:
        tempurl = i
        try:
            a = opener.open(tempurl)
        except urllib.error.HTTPError:
            print('连接失败')
            continue
        except urllib.error.URLError:
            print('连接失败')
            continue
        html = a.read()
        code = chardet.detect(html)
        encoding = code['encoding']
        html = html.decode(encoding)
        # print(html)
        soup = BeautifulSoup(html, 'html.parser')
        head = soup.find('head')
        if not head:
            head_text = ''
        else:
            head_text = head.text
        head_md5 = getmd5(head_text)
        print(head_md5)
        for j in lines:
            if j[0] == tempurl:
                if j[1] == head_md5:
                    print("%s 正常\n" % tempurl)
                else:
                    print("%s 网页头部可能被修改!\n" % tempurl)
                    with open('./data/headcheck.txt', 'a') as f:
                        f.write('\n')
                        f.write('%s：%s 网页头部可能被修改' % (datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), tempurl))
                    flag = 1
    return flag


def getinit(ok_list):
    print('获取初始对象：')
    dict_url = {}
    text_dict = {}
    md5_list = []
    for i in ok_list:
        tempurl = i
        img_list = []
        try:
            a = opener.open(tempurl)
        except urllib.error.HTTPError:
            print('连接失败')
            continue
        except urllib.error.URLError:
            print('连接失败')
            continue
        html = a.read()
        code = chardet.detect(html)
        encoding = code['encoding']
        html = html.decode(encoding)

        soup = BeautifulSoup(html, 'html.parser')
        head = soup.find('head')
        if not head:
            head_text = ''
        else:
            head_text = head.text
        head_md5 = getmd5(head_text)
        print(tempurl+'>'+head_md5)
        md5_list.append([tempurl, head_md5])

        dict_url[tempurl] = img_list
        soup = BeautifulSoup(html, 'html.parser')
        img = soup.find_all(name='img')
        for e in img:
            img_list.append(e.get('src'))
        dict_url[tempurl] = img_list

        body = soup.find('body')
        if not body:
            body_text = ''
        else:
            body_text = body.text
        text_dict[tempurl] = body_text

    with open('./data/md5.txt', 'w') as f:
        print('write md5...')
        for i in range(len(md5_list)):
            f.write('%s>%s\n' % (md5_list[i][0], md5_list[i][1]))
    with open('./data/img.txt', 'w') as f:
        print('write img_dict...')
        f.write(str(dict_url))
    with open('./data/bodytext.txt', 'w', encoding='utf-8') as f:
        print('write text_dict...')
        f.write(str(text_dict))


def check3(ok_list):
    print('开始检测3：')
    flag = 0
    dict_url = {}
    for i in ok_list:
        temp_list = []
        tempurl = i
        dict_url[tempurl] = temp_list
        try:
            a = opener.open(tempurl)
        except urllib.error.HTTPError:
            print('连接失败')
            continue
        except urllib.error.URLError:
            print('连接失败')
            continue
        html = a.read()
        code = chardet.detect(html)
        encoding = code['encoding']
        html = html.decode(encoding)
        soup = BeautifulSoup(html, 'html.parser')
        img = soup.find_all(name='img')
        for e in img:
            temp_list.append(e.get('src'))
        dict_url[tempurl] = temp_list
    with open('./data/img.txt', 'r') as f:
        check_dict = f.read()
    check_dict = eval(check_dict)
    for i in dict_url.keys():
        if dict_url[i] == check_dict[i]:
            print('%s 图片正常' % i)
        else:
            print('%s 图片可能被修改' % i)
            with open('./data/imgcheck.txt', 'a') as f:
                f.write('\n')
                f.write('%s：%s 网页图片可能被修改' % (datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), i))
            flag = 1
    return flag


def check4(ok_list):
    print('开始检测4:')
    flag = 0
    text_dict = {}
    for i in ok_list:
        tempurl = i
        try:
            a = opener.open(tempurl)
        except urllib.error.HTTPError:
            print('连接失败')
            continue
        except urllib.error.URLError:
            print('连接失败')
            continue
        html = a.read()
        code = chardet.detect(html)
        encoding = code['encoding']
        html = html.decode(encoding)
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        if not body:
            body_text = ''
        else:
            body_text = body.text

        text_dict[tempurl] = body_text
    with open('./data/bodytext.txt', 'r', encoding='utf-8') as f:
        check_dict = f.read()
    check_dict = eval(check_dict)
    for i in text_dict.keys():
        if text_dict[i] == check_dict[i]:
            print('%s body文本正常' % i)
        else:
            print('%s body文本可能被修改' % i)
            with open('./data/bodycheck.txt', 'a') as f:
                f.write('\n')
                f.write('%s：%s 网页文本可能被修改' % (datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'), i))
            flag = 1
    return flag


if __name__ == '__main__':
    if sys.argv[1] == '-init':
        ok_list, flag1 = check1()
        getinit(ok_list)
    elif sys.argv[1] == '-work':
        while True:
            ok_list, flag1 = check1()
            flag2 = check2(ok_list)
            flag3 = check3(ok_list)
            flag4 = check4(ok_list)
            if flag1+flag2+flag3+flag4 != 0:
                print('有站点无法访问或可能被修改！！！')
            time.sleep(10)
    else:
        print('参数错误,请输入-init或者-work')
