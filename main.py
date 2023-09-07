from time import sleep
from playwright.sync_api import Page, sync_playwright
from skip_and_replace import StringPreprocessing
from tool import (
    add_data,
    filterInvalidItems,
    fprint,
    init,
    setAndGetUrl,
    setNewPath,
    sysHasArgs,
)

MAX_WORDS = 5000
# filePaths = endswith()  # [8:9]
skipAndReplace = StringPreprocessing()


def main():
    Paths = init()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page: Page = browser.new_page()

        class Translate:
            """docstring for Translate."""

            def get_lRu31(self):
                return page.inner_text('.lRu31', timeout=20000)

            def goPage(self, ready_to_translated_text: str):
                url = setAndGetUrl(ready_to_translated_text)
                if sysHasArgs('-l', '--link'):
                    fprint('>>', url)
                page.goto(url)
                assert 'Google' in page.title()
                time_out = 10
                while self.get_lRu31() == '' and time_out > 0:
                    sleep(time_out := time_out - 1)

            @skipAndReplace.skip
            def readyReadText(self, file_path: str) -> str:
                with open(file_path, 'r', encoding='utf-8') as stream:
                    return stream.read()

            @skipAndReplace.replace
            def writeTranslateContent(self, save_path: str, text: str):
                if not text:
                    return f'Get Text is Null, Skip {save_path}'
                return text

            @add_data(*Paths)
            def translate(self, index: int, filePath: str):
                fprint('Input=>', index, filePath)

                # self.readyReadText(filePath)
                fprint('split'.center(50, '-'))

                def getResult():
                    fileContent: str = self.readyReadText(filePath)
                    if len(fileContent) >= MAX_WORDS:
                        fcs = fileContent.split('\n')
                        texts = []
                        temp = ''
                        for i, fc in enumerate(fcs):
                            temp += f'{fc}\n'
                            if len(f'{temp}{fc}') >= MAX_WORDS:
                                texts.append(temp)
                                temp = ''
                        if temp:
                            texts.append(temp.rstrip('\n'))

                        # for i in range(0, len(fileContent), 4800):
                        #     files.append(fileContent[i : 4800 + i])  # noqa

                        texts = filterInvalidItems(texts)
                        if sysHasArgs('--text'):
                            fprint(len(texts), texts)
                        ret = ''
                        for text in texts:
                            if text.strip():
                                self.goPage(text)
                                ret += '\n' + self.get_lRu31()
                        return ret
                    else:
                        self.goPage(fileContent)
                        return self.get_lRu31()

                self.writeTranslateContent(setNewPath(filePath), getResult())
                # .cHEsi

        Translate().translate()


if __name__ == '__main__':
    main()
