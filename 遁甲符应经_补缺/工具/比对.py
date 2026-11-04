"""把一份录文跟底稿逐字比，列出差异（忽略标点、页码标记、图块）。

用法：
  python3 比对.py 录文.txt 底稿.txt [--t2s] [--from 起始短语] [--to 结束短语]
  --t2s   先把录文转成简体再比（底稿是简体时用），会保护「乾」字。
  --from/--to  只取底稿里这两个短语之间的一段。
"""
import argparse, difflib, re

PUN = set('，。：；、！？“”「」《》（）()·．.　 \n?—〔〕【】0123456789页頁')

def clean(s):
    s = re.sub(r'【[页頁]\w+】|（空白）', '', s)
    s = re.sub(r'〔[圖图][：:][^〕]*〕', '', s)
    return [c for c in s if c not in PUN]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lu'); ap.add_argument('di')
    ap.add_argument('--t2s', action='store_true')
    ap.add_argument('--from', dest='frm'); ap.add_argument('--to')
    a = ap.parse_args()
    lu = open(a.lu, encoding='utf-8').read()
    di = open(a.di, encoding='utf-8').read()
    if a.frm:
        di = di[di.find(a.frm):]
    if a.to:
        di = di[:di.find(a.to) + len(a.to)]
    if a.t2s:
        from opencc import OpenCC
        lu = OpenCC('t2s').convert(lu.replace('乾', '◆')).replace('◆', '乾')
    x, y = clean(di), clean(lu)
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    n = 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        n += 1
        ctx = ''.join(x[max(0, i1 - 5):i1])
        print(f'…{ctx}【底稿:{"".join(x[i1:i2])[:40] or "∅"} → 录文:{"".join(y[j1:j2])[:40] or "∅"}】')
    print(f'差异 {n} 处；底稿 {len(x)} 字，录文 {len(y)} 字')

if __name__ == '__main__':
    main()
