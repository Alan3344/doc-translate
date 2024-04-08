# 不被翻译的标签集合
"""
ret = []
$0.querySelectorAll('tr').forEach(e=>{
    let d = e.querySelector('td')
    if (d) ret.push(d.innerText.replace(/</, '').replace(/>/, ''))
})
"""

tags = sorted(
    [
        'abbr',
        'acronym',
        'address',
        'applet',
        'area',
        'article',
        'aside',
        'audio',
        'base',
        'basefont',
        'bdi',
        'bdo',
        'big',
        'blockquote',
        'body',
        'button',
        'canvas',
        'caption',
        'center',
        'cite',
        'code',
        'col',
        'colgroup',
        'command',
        'data',
        'datalist',
        'dd',
        'del',
        'details',
        'dir',
        'div',
        'dfn',
        'dialog',
        'dl',
        'dt',
        'em',
        'embed',
        'fieldset',
        'figcaption',
        'figure',
        'font',
        'footer',
        'form',
        'frame',
        'frameset',
        'head',
        'header',
        'hr',
        'html',
        'iframe',
        'img',
        'input',
        'ins',
        'isindex',
        'kbd',
        'keygen',
        'label',
        'legend',
        'li',
        'link',
        'main',
        'map',
        'mark',
        'menu',
        'menuitem',
        'meta',
        'meter',
        'nav',
        'noframes',
        'noscript',
        'object',
        'optgroup',
        'option',
        'output',
        'param',
        'pre',
        'progress',
        'ruby',
        'samp',
        'script',
        'section',
        'select',
        'small',
        'source',
        'span',
        'strike',
        'strong',
        'style',
        'sub',
        'summary',
        'sup',
        'svg',
        'table',
        'tbody',
        'template',
        'textarea',
        'tfoot',
        'thead',
        'time',
        'title',
        'track',
        'var',
        'video',
        'wbr',
        'xmp',
    ],
    reverse=True,
)
html_tag = [r'(<%s)' % x for x in tags]
html_tag.extend(r'(</%s>)' % x for x in tags)


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
        ' P>': '</p>',
        ' p>': '</p>',
        '</p>> </p>': '</p>',
        '<p>，': '<p>',
        '* : ': '* :',
        ' *: ': ' * :',
        '\n*: ': '\n* :',
        '\n   *': '\n   * ',
        '\n*': '\n* ',
        '\n*  ': '\n* ',
        '\n   *  ': '\n   * ',
        '</p>）。</p>': '',
        # '{Flet': 'Flet',
        # '\n作者_ title:  ': '\nauthor_title: ',
        # '\n作者_title: ': 'author_title: ',
        '\nTitle: ': '\ntitle: ',
        '\nAuthor_title: ': '\nauthor_title: ',
        'Author_image_url: ': 'author_image_url: ',
        '卡': '卡片',
        'PIECHART': 'PieChart',
        'POPUPMENUBUTTON': 'PopupMenuButton',
        'Drov': 'Drop',
    }
    #
    translate_mark_after_regex = {'': ''}
    # 特殊文本跳过翻译(使用元祖匹配)
    Keyword = [
        # -----------file headers-----------
        # r'\n(author_title:\s.+\n)',
        # r'\n(author_url:\shttps?://.+\n)',
        # r'\n(author_image_url:\shttps?://.+\n)',
        # r'\n(author:\s.+\n)',
        # r'\n(tags:\s\[[\w\s,_-]+\]\n)',
        # r'\n(slug:\s.+\n)',
        # r'\n(id:\s.+\n)',
        # r'\n(title:\s.+\n)',
        # r'\n(sidebar_label:\s.+\n)',
        # -----------file headers-----------
        r'(Flet UI)',
        r'(Fly.io)',
        r'(Flet)',
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
    # TODO: 直接翻译html引号丢失解决方案: 检查代码块中是否存在unicode字符或者基本字符之外的块
    markdown = {
        # 'code': r'```(?:w{1,}[\n])?(?:.*\n){1,}```',  # 将匹配整个代码块
        # 'html': r'<\w+\s.*>?<?/\w*?>',  # 匹配 html 内容 <[\s\S]+?>\n*?</.*?>
        'file-headers': r'(---(?:\n.+)*\n---\n\n)',
        'html': r'\n(<(?!/)[\s\S]+?>\n*?</.*>)',  # 匹配 html 内容
        'react-import': '(?:(\nimport.+from.+;?)+\n)',  # react-import
        'export': r'\n(export\s*.+[\s\S]+\);)',
        'attr': r'''<\w+\s*\n*((?:\w+)\s*=\s*['"]\w+['"]\s*)>''',  # 匹配属性 <\w+.+=.+>
        # 'html1': r'\n(<(?!(/|p|h[1-6]|strong|b|i|ul|li|article))[\s\S]+?>\n*?</\w+>)',  # 匹配html
        'html-code-s': r'(<(?:img|code|pre)\s.+/>)',  # 优先匹配单行标签
        'html-code-m': r'(<(?:img|code|pre)\s*.+[\s\S\n]*?/(?!\w+)>)',  # 匹配多行标签
        'code': r'```[\s\S]*?```',  # 匹配代码块(代码编辑器查找需要添加 \n ```[\n\s\S]*?```)
        'md-link-cli': r'(\[[A-Z0-9a-z]+\]\([A-Z0-9a-z]+\))',  # CLI: [create](create)
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
    }


Rule.Keyword.extend(html_tag)
