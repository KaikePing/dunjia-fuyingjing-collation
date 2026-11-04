"""从美国国会图书馆 IIIF 下载明末朱丝栏钞本《景祐遁甲符应经》的对开图。

用法（在仓库根目录或任意位置都行）：
  python3 遁甲符应经_补缺/工具/下载国会图书馆书影.py            # 全部 166 张
  python3 遁甲符应经_补缺/工具/下载国会图书馆书影.py --only 2A  # 只下第 4–7 册（李氏序＋下部三卷）
  python3 遁甲符应经_补缺/工具/下载国会图书馆书影.py --only 1A  # 只下序目＋上部三册

已经下好的会跳过，断了重跑就能续。每张间隔几秒，别改快。
图存到 遁甲符应经_补缺/书影_国会图书馆明抄本/<册>/<叶号>.jpg（分辨率 pct:50，约 1790 宽）。
"""
import argparse, json, os, random, re, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)  # 遁甲符应经_补缺/
NAMES = {'Preface/Table of Contents': '00_序目'}
NAMES.update({f'Volume {i}': f'{i:02d}_第{i}册' for i in range(1, 8)})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', help='只下某一函：1A 或 2A')
    a = ap.parse_args()
    urls = json.load(open(os.path.join(BASE, '书影_国会图书馆明抄本_图址.json'), encoding='utf-8'))
    out = os.path.join(BASE, '书影_国会图书馆明抄本')
    n = 0
    for cap, u in urls:
        parts = re.search(r'2012402536:([^/]+)/full', u).group(1).split(':')
        vol, sid = parts[0], parts[-1]
        if a.only and not vol.startswith(a.only):
            continue
        d = os.path.join(out, NAMES[cap]); os.makedirs(d, exist_ok=True)
        fp = os.path.join(d, f'{sid}.jpg')
        if os.path.exists(fp) and os.path.getsize(fp) > 10000:
            continue
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (personal research; dunjia collation)'})
        for _ in range(3):
            try:
                data = urllib.request.urlopen(req, timeout=90).read()
                open(fp, 'wb').write(data); break
            except Exception as e:
                print('重试', sid, e, flush=True); time.sleep(20)
        n += 1
        print(n, NAMES[cap], sid, os.path.getsize(fp) if os.path.exists(fp) else '失败', flush=True)
        time.sleep(random.uniform(2.5, 4.5))
    print('DONE', flush=True)

if __name__ == '__main__':
    main()
