"""把阶段三乙的合校稿拼成成品：去页码标记、繁转简（保护「乾」），加文前说明。

用法（在仓库根目录）：
  python3 遁甲符应经_补缺/工具/成品.py            # 写根目录 遁甲符应经_校订完整版.txt
  python3 遁甲符应经_补缺/工具/成品.py --check    # 只检查，不写
"""
import argparse, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, '遁甲符应经_补缺')
OUT = os.path.join(ROOT, '遁甲符应经_校订完整版.txt')
FRONT = os.path.join(BASE, '校勘', '成品_文前说明.txt')


def t2s(s):
    from opencc import OpenCC
    cc = OpenCC('t2s')
    return cc.convert(s.replace('乾', '◆')).replace('◆', '乾')


def clean(s):
    s = re.sub(r'【[^】]*】(（[^）]*）)?\n?', '', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    s = re.sub(r'〔\?([^〕]*)〕', r'\1（?）', s)  # 图中认不准的字
    return s.strip('\n') + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(BASE, '校勘', '阶段三乙_合校_批*.txt')))
    if not files:
        sys.exit('没有合校稿')
    body = '\n'.join(clean(open(f, encoding='utf-8').read()) for f in files)
    left = re.findall(r'〔\?[^〕]*〕|【[^】]*】|〔刪〕|〔旁注[^〕]*〕|〔粘簽[^〕]*〕|〔附簽[^〕]*〕|〔眉批[^〕]*〕', body)
    print('合校稿', len(files), '份；正文', len(re.sub(r'\s', '', body)), '字')
    print('校注', body.count('〔校：'), '条；残留记号', len(left), left[:20])
    if a.check:
        return
    front = open(FRONT, encoding='utf-8').read() if os.path.exists(FRONT) else ''
    text = t2s(front.rstrip('\n') + '\n\n' + body) if front else t2s(body)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('写入', OUT)


if __name__ == '__main__':
    main()
