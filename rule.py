class Rule:
    """语法优先->关键字"""

    # 翻译后: 替换规则前的替换关系
    translate_mark_before = {
        '：': ': ',
        # '> <': '><',
    }
    # 翻译后: 替换规则后的替换关系
    translate_mark_after = {
        '] (': '](',
        ' 。。': '。',
        'https: //': 'https://',
        ': : :': ':::',
        '::: ': ':::',
        ':::\n:::': ':::',
        '光盘': '形状',
        '-https://': '- https://',
        '运行: ': '运行以下命令',
    }
    # 特殊文本跳过翻译(使用元祖匹配)
    Keyword = [
        r'Flet UI',
        r'Flet',
        r'\n(id\:\s?)',
        r'\n(title\:\s?)',
        r'\n(slug\:\s?)',
        r'\n(sidebar_label\:\s?)',
        r'(material design)',
        r'(material)',
        r'(children)',
        r'(child)',
        r'(Free-hand)',
        r'(fly-io)',
        r'(fly\.io)' r'(Fly)',
        # r'TextField',
        r'(Keyboard)',
        r'(leading)',
    ]

    # Markdown 语法跳过(\n是为了尽可能的保留原有格式))
    # 匹配长度尽可能的由长到短
    markdown = {
        # 'code': r'```(?:w{1,}[\n])?(?:.*\n){1,}```',  # 将匹配整个代码块
        # 'html': r'<\w+\s.*>?<?/\w*?>',  # 匹配 html 内容 <[\s\S]+?>\n*?</.*?>
        'html': r'\n(<(?!/)[\s\S]+?>\n*?</.*>)',  # 匹配 html 内容
        'html2': r'<.+/>',  # 匹配单标签
        'code': r'```[\s\S]*?```',  # 匹配代码块(代码编辑器查找需要添加 \n ```[\n\s\S]*?```)
        'md-link': r'\[.*?\](\(.*?\))',  # 匹配整个链接 r'((\[.*?\])(\(.*?\)))'
        'round-brackets-coor': r'\(`\w+`,\s*`\w+`\)',  # 匹配带反引号的坐标 (`x`, `y`)
        'square-brackets-coor': r'(`\[.+\]`)',  # 匹配带反引号的坐标 (`x`, `y`) (解决``匹配异常)
        'backtick': r'(`[\w\.=\*\(\)]+?`)',  # 匹配一般的反引号 `func()` (TODO：手动再周围加上一个空,美观)
        'url': r'(`(?:https?|ftp)://.+`)',
        '<+>': r'`<.*?>`',  # `<your-app-name>`
        'title2': r'(\n\s*#+\s)',  # 匹配标题2
        'ns4': r'\n(\n(?:\s{4}.+)(?:[\n\s].+)*)',  # 匹配4缩进的代码块
        'li1': r'(\n\s*\-\s)[\s\S]+',  # 匹配列表1
        'li2': r'(\n\s*\*\s)[\s\S]+',  # 匹配列表2
        'note-token': r'\n:::',
        'react-import': 'import.+',  # react
    }
