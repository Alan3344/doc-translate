doc-translate:
`GoogleTranslate` 支持部分文本格式，只需要过滤掉无需翻译的部分即可

##### 原理

- 扫描文档目录生成源文件队列(使用 `unittest` 框架以略过这一步)
- 预设匹配规则，递归替换
- 待翻译词替换为占位符 `$Key_<int>` 格式,存储原先的字典，代码 `$Code_<int>`
- 填入待翻译文本，获取译文
- 使用字典替换占位符
