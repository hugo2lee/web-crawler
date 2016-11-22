import os
import requests
from urllib import request
from lxml import html
from utils import log, now
from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
manager = Manager(app)


class ModelHelper(object):
    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} \n>\n'.format(classname, s)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class School(db.Model, ModelHelper):
    __tablename__ = 'school'
    # 下面是字段定义
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    tel = db.Column(db.String(), default=None)
    address = db.Column(db.String(), default=None)
    website = db.Column(db.String(), default=None)
    email = db.Column(db.String(), default=None)
    area = db.Column(db.String(), default=None)
    grade = db.Column(db.String(), default=None)
    synopsis = db.Column(db.String(), default=None)

    def __init__(self):
        self.name = []
        self.tel = []
        self.address = []
        self.website = []
        self.email = []
        self.area = []
        self.grade = []
        self.synopsis = []


def get_html_urllib(url):
    try:
        page = request.urlopen(url)
        html_doc = page.read()
        return html_doc
    except:
        log('not exist', url)


def get_html_requests(url):
    r = requests.get(url)
    html_doc = r.content
    return html_doc


def down_html(url):
    '''
    sample http://guangzhou.xuexiaodaquan.com/haizhuqu-gaozhong/
    '''
    for i, v in enumerate(url):
        ag = v.split('/')[-2]
        area_grade = ag.split('-')
        path = 'school_map/{}-{}.html'.format(area_grade[0], area_grade[1])
        html_doc = get_html_urllib(v)
        if html_doc is None:
            pass
        else:
            # r只读，w可写，a追加
            with open(path, 'wb') as f:
                f.write(html_doc)
    return '成功下载全部页面'


def open_html_from_file(url):
    all_page = []
    for i, v in enumerate(url):
        ag = v.split('/')[-2]
        area_grade = ag.split('-')
        path = 'school_map/{}-{}.html'.format(area_grade[0], area_grade[1])
        try:
            with open(path, 'r', encoding='gbk') as f:
                all_page.append(f.read())
        except:
            pass
    return all_page


def page_from_file(page):
    root = html.fromstring(page)
    area_grade = root.xpath('.//div[@class="list-title"]/h1')[0].text
    left_items = root.xpath('//dl[@class="left"]')
    right_items = root.xpath('//dl[@class="right"]')
    school_item = left_items + right_items
    return school_item, area_grade


def synopsis_from_page(i, name):
    link = i.xpath('.//a/@href')[0]
    page = get_html_requests(link)
    path = 'school_synopsis/{}.html'.format(name)
    # if path is os.path.exists(r'{}'.format(path)):
    #     pass
    # else:
    with open(path, 'wb') as f:
        f.write(page)
    try:
        with open(path, 'r', encoding='gbk') as f:
            file_page = f.read()
            root = html.fromstring(file_page)
            synopsis = root.xpath('//div[@class="detail-xx-jieshao"]/p')[0].text
            return synopsis
    except:
            return None


def school_from_page(url):
    all_school = []
    page = open_html_from_file(url)
    for p in page:
        item, area_grade = page_from_file(p)
        for i in item:
            school = School()
            school.area = area_grade[:3]
            school.grade = area_grade[3:5]
            school.name = i.xpath('.//a/@title')[0]
            school.synopsis = synopsis_from_page(i, school.name)
            school.address = i.xpath('.//li/span')[0].text
            school.tel = i.xpath('.//li/span')[1].text
            school.website = i.xpath('.//li/span')[2].text
            school.email = None
            school.save()
            all_school.append(school)
    return 'all school', len(all_school)


def out():
    for i in range(1, 1210):
        n = School.query.filter_by(id=i).first()
        log(n.area, n.grade, n.name, n.tel, n.address, n.website, n.synopsis)
    # return n


def make_url(url, school_area, school_grade):
    '''
    sample http://guangzhou.xuexiaodaquan.com/haizhuqu-gaozhong/
    '''
    real_url = []
    for i in school_area:
        for j in school_grade:
            real_url.append(url + i + '-' + j + '/')
    return real_url


def make_dir(school_area):
    # for i in school_area:
    #     os.makedirs("school_map")
        os.makedirs("school_synopsis")


def main():
    url = 'http://guangzhou.xuexiaodaquan.com/'
    school_area = ['liwanqu', 'conghuashi', 'haizhuqu', 'huangpuqu', 'baiyunqu', 'tianhequ', 'yuexiuqu', 'zengchengshi',
                   'luogangqu', 'fanqu', 'nanshaqu', 'huaduqu']
    school_grade = ['youeryuan', 'xiaoxue', 'chuzhong', 'gaozhong', 'daxue', 'chengrenjiaoyu']

    real_url = make_url(url, school_area, school_grade)
    # log('全部学校共有页面', len(real_url), real_url)
    # make_dir(school_area)
    # down_html(real_url)
    # log('open page', open_html_from_file(real_url))
    # log(page_from_file(real_url))
    # log('school from page', school_from_page(real_url))
    log('select', out())


def init_db():
    # 先 drop_all 删除所有数据库中的表
    # 再 create_all 创建所有的表
    db.drop_all()
    db.create_all()
    print('rebuild database')

if __name__ == '__main__':
    main()
    # init_db()
