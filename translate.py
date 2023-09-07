import os
import urllib.parse as parser

from dotenv import load_dotenv
from playwright.sync_api import Page

load_dotenv()


class Url:
    Google = 'https://translate.google.com/'
    Deepl = 'https://www.deepl.com/translator'


class Engine:
    def __init__(self, page: Page, dst_lang='zh', src_lang='en') -> None:
        self.page = page
        self.dst_lang = dst_lang
        self.src_lang = src_lang

        self.url = Url.Google

    def setUrl(self, url: str = '', translate_text: str = ''):
        page_base_url = url or self.url
        self.url = page_base_url
        text = parser.quote(translate_text)
        if text == '':
            return page_base_url
        match url:
            case Url.Google:
                return f'{page_base_url}?sl=auto&tl=zh-CN&text={text}&op=translate'
            case Url.Deepl:
                return f'{page_base_url}#en/zh/{text}'

    def google(self, text: str):
        # init
        self.page.goto(self.setUrl(text, Url.Google))
        assert 'Google' in self.page.title()

        return self

    def deep(self, text: str):
        deep_user = os.getenv('deepl_user')
        deep_pass = os.getenv('deepl_pass')
        self.page.goto(self.setUrl(text, Url.Google))
        assert 'DeepL' in self.page.title()
        return self
