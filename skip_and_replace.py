from typing import Callable
from enum import Enum
import re
from tool import fprint, sysHasArgs
from rule import Rule


class StringPreprocessing:
    class Oper(Enum):
        SKIP = 0
        REPLACE = 1

    skip_regex = r'|'.join(Rule.Keyword)  # 匹配规则
    letter_case = sysHasArgs('--ignore-case') or False
    translate_mark_before = Rule.translate_mark_before
    translate_mark_after = Rule.translate_mark_after

    def __init__(self) -> None:
        self._in_text = ''
        self._out_text = ''
        self._skips = {}  # Save skip dictionary
        self._replaces = {}  # Save replacement dictionary
        self._re_replaces = {}  # Save replacement dictionary
        self._save_path = ''
        self._perfix = '{{{}}}'  # '≮{}≯'
        self._written = {}
        self.__index = 0
        self.__count = 0

    def skip(self, func) -> Callable:
        """Skip some translations"""

        def warpper(cls, fp):
            def inner():
                self._in_text = func(cls, fp)
                return self.dealwith(self.Oper.SKIP)

            return inner()

        return warpper

    def replace(self, func) -> Callable:
        """Accept translation"""

        def warpper(cls, save_fp, text):
            def inner():
                self._out_text = func(cls, save_fp, text)
                self._save_path = save_fp
                return self.dealwith(self.Oper.REPLACE)

            return inner()

        return warpper

    def saveResult(self, text: str = '', save_path: str = ''):
        save_path = save_path or self._save_path
        fprint('Output=>', save_path)
        fprint('split'.center(50, '-'))

        with open(save_path, 'w', encoding='utf-8') as fpw:
            ret = fpw.write(text or self._out_text)
            self._written.update({self.__index: save_path})
            self.__index += 1
            return ret

    def checkFiles(self):
        for index, file_path in self._written.items():
            with open(file_path, 'r', encoding='utf-8') as fpr:
                content = fpr.read()
                # chars = self._perfix.replace('{}', '|')
                chars = r'\{\d+\}'
                if pips := re.findall(f'{chars}', content):
                    fprint('check failed:', f'{pips} at {{index:{index}}}', file_path)

    def setReplaces(self, key, value):
        self._replaces.update({key: value})
        self._re_replaces.update({value: key})

    @property
    def getReplaces(self) -> dict:
        return self._replaces

    def translateAfter(self, text: str = ''):
        text = text or self._out_text

        def inner_replace(repls: dict):
            nonlocal text
            # 先替换长的
            repls = dict(sorted(repls.items(), key=lambda t: len(t[1]), reverse=True))
            for key, value in repls.items():
                text = text.replace(key, value)

        inner_replace(self.translate_mark_before)
        inner_replace(self._replaces)
        # Check again to see if there are still unrestored Keys.
        inner_replace(self._replaces)
        inner_replace(self.translate_mark_after)
        # inner_replace(self.translate_mark_after)

        # 标头中有url的，除去空格 (\n.+:\shttps.+)
        if text1 := re.findall(r'((\n.+:)\s(https.+))', text):
            for txt in text1:
                # print(txt)
                t1, t2, t3 = txt
                new_txt = (
                    ''.join([t2.rstrip() + ' ', t3.replace(' ', '')])
                    .replace('？', '?')
                    .replace('＆', '&')
                )
            text = text.replace(t1, new_txt)
        self._out_text = text
        return text

    def specialRules(self, text: str):
        """匹配特殊规则,翻译结果会将<K_01>转为<k_01>

        :param str text: _description_
        :return _type_: _description_s
        """
        # 长度由长到短
        for ruleName, rule in Rule.markdown.items():
            if sysHasArgs(f'--no-rule={ruleName}', f'--no:{ruleName}'):
                continue

            if codes := re.findall(rule, text):
                # 相同开头的项，长度优先
                # codes = sorted(list(set(codes)), reverse=True)
                match ruleName:
                    case 'md-link':
                        # codes = [x[0] for x in codes]
                        pass
                    case _:
                        if isinstance(codes[0], tuple):
                            new_codes = []
                            [new_codes.extend(x) for x in codes]
                            codes = new_codes

                for i, code in enumerate(codes):
                    placeholder = self._perfix.format(f'{self.__count}{i}')
                    text = text.replace(code, placeholder)
                    self.setReplaces(placeholder, code)

                self.__count += 1

        return text

    def replaceText(self, text: str):
        """先匹配给定字符串中的值，然后组成一个过滤列表
            然后使用这些过滤项循环，使用数字编号作为占位符替换给定字符串

        :param str text: input text
        """
        _flag = re.I if self.letter_case else re.NOFLAG
        text = self.specialRules(text)
        repls = re.findall(self.skip_regex, text, _flag)
        new_repls = []
        if repls and isinstance(repls[0], tuple):
            [new_repls.extend(rep) for rep in repls]

        # Find the longest one and replace it first, such as ['Python Run', 'Python']
        # 相同开头的项，长度优先
        new_repls = sorted(list(set(new_repls or repls)), reverse=True)
        new_repls = [x for x in new_repls if f'{x}'.strip()]
        for i, rep in enumerate(new_repls):
            placeholder = self._perfix.format(f'{self.__count}{i}')
            text = text.replace(rep, placeholder)
            self.setReplaces(placeholder, rep)
        if sysHasArgs('-r', '--replaces'):
            fprint('self._replaces:', self.getReplaces)
        return text

    def dealwith(self, oper: Oper) -> str:
        """Read the configuration file and replace some variables, then skip

        :param Oper oper: _description_
        :return str: _description_
        """
        match oper:
            case self.Oper.SKIP:
                return self.replaceText(self._in_text)
            case self.Oper.REPLACE:
                self.translateAfter(self._out_text)
                self.saveResult()
                self.checkFiles()
                return self._out_text
            case _:
                return '<NULL>'


if __name__ == '__main__':
    pass

"""
SkipRegex = "s?`.+`s?|Python Run|Python"  # Python Run > Python
Replaces = {}
test_str = '''
`Python Version` is a program language
adfsaf Python 4324 0Python Run
43   DOC wrwqr32dfs fds4532
'''
com = re.compile(SkipRegex)
repls = com.findall(test_str)
print(repls)

new_repls = []
if repls and (isinstance(repls[0], tuple)):
    for x in repls:
        new_repls.extend(x)
if not new_repls:
    new_repls = repls

# Remove space
new_repls = [x for x in new_repls if x]

# Find the longest one and replace it first
# ['`Python Version`', 'Python Run', 'Python']
# Python Run > Python
new_repls = sorted(list(set(new_repls)), reverse=True)
print(new_repls)

for i, rep in enumerate(new_repls):
    if rep in test_str:
        test_str = test_str.replace(rep, f'$Key_{i}')
        Replaces.update({f'$Key_{i}': rep})

print(test_str)
print(Replaces)
for key, value in Replaces.items():
    test_str = test_str.replace(key, value)
# print(test_str)

"""
