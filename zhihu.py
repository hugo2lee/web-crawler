import requests
from urllib import request
from lxml import html
from utils import log


class Model(object):
    def __str__(self):
        class_name = self.__class__.__name__
        # u在字符串前表示编码是unicode,相似的有b表示byte，在socket.send(b'balabala')
        properties = ('{0} : ({1})'.format(k, v) for k, v in self.__dict__.items())
        r = '{0}\n  {1}\n'.format('', '  \n  '.join(properties))
        return r


class Answers(Model):
    def __init__(self):
        self.question_link = []
        self.question = []
        self.answers = []


answers = Answers()


def get_html_urllib(url):
    page = request.urlopen(url)
    html_doc = page.read()
    return html_doc


def get_html_requests(url):
    r = requests.get(url)
    html_doc = r.content
    return html_doc


def down_html(url):
    html_doc = get_html_urllib(url)
    # r只读，w可写，a追加
    with open('down_html.html', 'wb') as f:
        f.write(html_doc)


def open_html_from_file():
    with open('down_html.html', 'rb') as f:
        r = f.read()
        return r


def page_from_file():
    page = open_html_from_file()
    root = html.fromstring(page)

    question_link = root.xpath('//a[@class="question_link"]/@href')
    for i in question_link:
        answers.question_link.append('https://www.zhihu.com{}'.format(i))

    question = root.xpath('//a[@class="question_link"]')
    for j in question:
        answers.question.append(j.text.replace('\n', ''))

    content = root.xpath('//textarea[@class="content"]')
    for k in content:
        answers.answers.append(k.text)


def find_page_num(url):
    real_url = url + '1'
    page = get_html_urllib(real_url)
    root = html.fromstring(page)
    page_index = root.xpath('//div[@class="zm-invite-pager"]')[0]
    num = page_index.xpath('.//a')[-2].text
    return num


def get_all_answer(url):
    # num = find_page_num(url)
    num = 5
    for i in range(1, int(num) + 1):
        log(url, i)
        real_url = url + str(i)
        down_html(real_url)
        page_from_file()
    # return answers


def save_answer():
    txt = ''
    for a in range(0, len(answers.question)):
        i = answers.question_link[a]
        j = answers.question[a]
        k = answers.answers[a]
        txt = txt + i + '\r' + j + '\n' + k + '\r\n\r\n'
    # log('txt', txt)
    with open('answers.txt', 'wb') as f:
        f.write(txt.encode('utf-8'))


def main():
    url = "https://www.zhihu.com/people/excited-vczh/answers?from=profile_answer_card&page="
    # log('find_page_num', find_page_num(url))
    # down_html(url)
    # log(page_from_file(), answers)
    log('get all ', get_all_answer(url))
    log('save to file', save_answer())


if __name__ == '__main__':
    main()
