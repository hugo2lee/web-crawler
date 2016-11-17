# encoding: utf-8
__author__ = 'hugo'

import socket
import ssl
import requests
from lxml import html
from utils import log


def all_html_from_url(item):
    html = []
    for index in range(0, 250, 25):
        url = 'https://{}.douban.com/top250?start={}&filter='.format(item, index)
        r = requests.get(url)
        html.append(r.content)
    return html


def save_to_file(item):
    douban250 = all_html_from_url(item)
    for i, m in enumerate(douban250):
        path = 'douban250/' + '{}'.format(item) + str(i) + '.html'
        with open(path, 'wb') as f:
            f.write(m)


def open_html_from_file(item):
    all_html = []
    for i in range(10):
        path = 'douban250/' + '{}'.format(item) + str(i) + '.html'
        with open(path, 'rb') as f:
            all_html.append(f.read())
    return all_html


def items_from_file(item, num):
    page = open_html_from_file(item)
    root = html.fromstring(page[num])
    # 得到树形结构后用.xpath('')处理返回数组：//表示从树形结构的根开始找，div表示要找的结构，[什么样的div]即@class="item"的div。(@表示属性)
    tag_dict = {
        'movie': 'div',
        'book': 'tr',
        'music': 'tr',
    }
    tag = tag_dict.get(item, 'div')
    item_divs = root.xpath('//{}[@class="item"]'.format(tag))
    # movie_divs是list
    item_dict = {
        'movie': movies_from_div,
        'book': books_from_div,
        'music': musics_from_div,
    }
    run = item_dict.get(item, movies_from_div)
    items = [run(div) for div in item_divs]
    return items


class Model(object):
    def __str__(self):
        class_name = self.__class__.__name__
        # u在字符串前表示编码是unicode,相似的有b表示byte，在socket.send(b'balabala')
        properties = ('{0} : ({1})'.format(k, v) for k, v in self.__dict__.items())
        r = '{0}\n  {1}\n'.format('', '  \n  '.join(properties))
        return r


class Movie(Model):
    def __init__(self):
        # super(Movie, self).__init__()
        self.ranking = 0
        self.cover_url = ''
        self.name = ''
        self.staff = ''
        self.publish_info = ''
        self.rating = 0
        # self.quote = ''
        self.number_of_comments = 0


class Book(Model):
    def __init__(self):
        self.cover_url = ''
        self.name = ''
        self.rating = 0
        self.quote = ''
        self.number_of_comments = 0


class Music(Model):
    def __init__(self):
        self.cover_url = ''
        self.name = ''
        self.rating = 0
        self.number_of_comments = 0


def movies_from_div(div):
    movie = Movie()
    # .//的点表示当前的div, //表示根
    movie.ranking = div.xpath('.//div[@class="pic"]/em')[0].text
    # .:当前div, //:div的根, 找div[@属性为class="pic"]，路径：/a/img/ 里的属性@src
    movie.cover_url = div.xpath('.//div[@class="pic"]/a/img/@src')
    names = div.xpath('.//span[@class="title"]/text()')
    movie.name = ''.join(names)
    # xpath返回的是数组，取第一个元素是类的实例，它是取到的div里的<span >tag,里面包含有个text文本（self.text）？
    movie.rating = div.xpath('.//span[@class="rating_num"]')[0].text
    # movie.quote = div.xpath('.//span[@class="inq"]')[0].text
    infos = div.xpath('.//div[@class="bd"]/p/text()')
    movie.staff, movie.publish_info = [i.strip() for i in infos[:2]]
    movie.number_of_comments = div.xpath('.//div[@class="star"]/span')[-1].text[:-3]
    return movie


def books_from_div(div):
    book = Book()
    # .//的点表示当前的div, //表示根
    # .:当前div, //:div的根, 找div[@属性为class="pic"]，路径：/a/img/ 里的属性@src
    book.cover_url = div.xpath('.//a[@class="nbg"]/img/@src')[0]
    ch_name = div.xpath('.//div[@class="pl2"]/a/@title')[0]
    en_name = div.xpath('.//span[@style="font-size:12px;"]/text()')
    if len(en_name) == 0:
        en_name.append('')
    name = [str(ch_name), str(en_name[0])]
    book.name = ' '.join(name)
    # xpath返回的是数组，取第一个元素是类的实例，它是取到的div里的<span >tag,里面包含有个text文本（self.text）？
    book.rating = div.xpath('.//span[@class="rating_nums"]')[0].text + '分'
    book.quote = div.xpath('.//p[@class="pl"]')[0].text
    book.number_of_comments = div.xpath('.//span[@class="pl"]')[0].text[2:-2].strip()
    # log('book.number_of_comments', len(book.number_of_comments))
    return book


def musics_from_div(div):
    book = Music()
    # .//的点表示当前的div, //表示根
    # .:当前div, //:div的根, 找div[@属性为class="pic"]，路径：/a/img/ 里的属性@src
    book.cover_url = div.xpath('.//a[@class="nbg"]/img/@src')[0]
    ch_name = div.xpath('.//div[@class="pl2"]/a/@title')[0]
    en_name = div.xpath('.//span[@style="font-size:12px;"]/text()')
    if len(en_name) == 0:
        en_name.append('')
    name = [str(ch_name), str(en_name[0])]
    book.name = ' '.join(name)
    # xpath返回的是数组，取第一个元素是类的实例，它是取到的div里的<span >tag,里面包含有个text文本（self.text）？
    book.rating = div.xpath('.//span[@class="rating_nums"]')[0].text + '分'
    # book.quote = div.xpath('.//p[@class="pl"]')[0].text
    book.number_of_comments = div.xpath('.//span[@class="pl"]')[0].text[2:-2].strip()
    # log('book.number_of_comments', len(book.number_of_comments))
    return book


def main():
    item = ['movie', 'book', 'music']
    all_item = []
    txt = ''

    # 下面是先把网页下载到本地
    # save_to_file(item[0])

    # 下面为取出单条写入文件
    for i in range(10):
        a = items_from_file(item[0], i)
        for j in a:
            all_item.append(j)
    for i, m in enumerate(all_item):
        # print(m)
        txt += '第{}名：'.format(i + 1) + str(m) + '\r\n\r\n'
        pass

    path = 'douban250/' + '{}'.format(item[2]) + '250' + '.txt'
    with open(path, 'wb') as f:
        f.write(txt.encode('utf-8'))


if __name__ == '__main__':
    main()
