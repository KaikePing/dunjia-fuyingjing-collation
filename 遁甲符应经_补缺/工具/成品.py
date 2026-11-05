"""把阶段三乙的合校稿拼成成品，出繁体、简体两版。

繁体版：合校稿本来就是繁体，只去页码标记，不做任何转换。
简体版：opencc t2s 转换，但一对多的字先保护、后处理（全书逐个核过，见校勘记录.md 日志）：
  - 「乾」全书都是卦名、方位，不转成「干」；
  - 「覆」不转（opencc 会把「天地反覆」「三五反覆」转成「反复」，这里是翻覆义）；
  - 「著」全书都是穿着、附着、放置义，转成「着」。

用法（在仓库根目录）：
  python3 遁甲符应经_补缺/工具/成品.py            # 写根目录两个文件
  python3 遁甲符应经_补缺/工具/成品.py --check    # 只检查，不写
"""
import argparse, glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, '遁甲符应经_补缺')
OUT_S = os.path.join(ROOT, '遁甲符应经_校订完整版_简体.txt')
OUT_T = os.path.join(ROOT, '遁甲符应经_校订完整版_繁体.txt')
FRONT_S = os.path.join(BASE, '校勘', '成品_文前说明.txt')
FRONT_T = os.path.join(BASE, '校勘', '成品_文前说明_繁体.txt')

KEEP = {'乾': '', '覆': ''}   # 简体版里不转的字
AFTER = {'著': '着'}                      # 简体版转换后再改的字


def t2s(s):
    from opencc import OpenCC
    for k, v in KEEP.items():
        s = s.replace(k, v)
    s = OpenCC('t2s').convert(s)
    for k, v in KEEP.items():
        s = s.replace(v, k)
    for k, v in AFTER.items():
        s = s.replace(k, v)
    return s


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
    body_t = '\n'.join(clean(open(f, encoding='utf-8').read()) for f in files)
    left = re.findall(r'【[^】]*】|〔刪〕|〔旁注[^〕]*〕|〔粘簽[^〕]*〕|〔附簽[^〕]*〕|〔眉批[^〕]*〕', body_t)
    print('合校稿', len(files), '份；正文', len(re.sub(r'\s', '', body_t)), '字')
    print('校注', body_t.count('〔校：'), '条；残留记号', len(left), left[:20])
    body_s = t2s(body_t)
    # 核对：保护的字数目两版一致，简体版不留「著」
    for k in KEEP:
        print(f'「{k}」繁体 {body_t.count(k)}，简体 {body_s.count(k)}')
        assert body_t.count(k) == body_s.count(k)
    assert '著' not in body_s
    if a.check:
        return
    front_t = open(FRONT_T, encoding='utf-8').read().rstrip('\n')
    front_s = open(FRONT_S, encoding='utf-8').read().rstrip('\n')
    open(OUT_T, 'w', encoding='utf-8').write(front_t + '\n\n' + body_t)
    open(OUT_S, 'w', encoding='utf-8').write(front_s + '\n\n' + body_s)
    print('写入', OUT_T)
    print('写入', OUT_S)


if __name__ == '__main__':
    main()
