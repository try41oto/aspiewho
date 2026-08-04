#!/usr/bin/env python3
"""
🎵バッジ対象の動画タイトルを YouTube oEmbed から取得し、
work/oembed_titles_cache.json にキャッシュする。

このスクリプトはビルドとは分離されている。build.py はキャッシュを
「読むだけ」で、ネットワークには一切アクセスしない。
（ビルドをオフラインかつ決定論的に保つため）

使い方（どこから実行してもよい）:
    python3 tools/fetch_oembed.py            # キャッシュに無いものだけ取得
    python3 tools/fetch_oembed.py --refresh  # 全件を取り直す
    python3 tools/fetch_oembed.py --older-than 90   # 90日より古いものだけ取り直す
    python3 tools/fetch_oembed.py --retry-failed    # 前回失敗したものだけ再試行
"""
import json, os, re, sys, time, html as H
import urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # リポジトリのルート
INDEX = os.path.join(ROOT, 'index.html')
CACHE = os.path.join(ROOT, 'work', 'oembed_titles_cache.json')
DELAY = 0.25          # 連続アクセスの間隔（秒）
TIMEOUT = 20
RETRIES = 2


def targets():
    """index.html から .pk カード内の ♫ バッジを拾い、(video_id, 外部URL, ローカル題名) を返す"""
    h = open(INDEX, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<a class="pk[^"]*" href="([^"]+)"[^>]*>', h):
        s = m.end()
        e = h.find('</a>', s)
        inner = h[s:e]
        # data-anchor="music-N" が注入されている場合があるので属性順に依存しない
        b = re.search(r'<span class="reflink refbadge"[^>]*\sdata-url="([^"]+)"[^>]*>(.)</span>', inner)
        if not b or b.group(2) != '♫':
            continue
        url = H.unescape(b.group(1))
        vid = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_\-]{11})', url)
        if not vid:
            print(f'  [skip] 動画IDを抽出できません: {url}', file=sys.stderr)
            continue
        t = re.search(r'<p>(.*?)</p>', inner, re.S)
        out.append((vid.group(1), url, H.unescape(t.group(1)) if t else ''))
    return out


def fetch(vid):
    """oEmbed を叩いて title を返す。失敗時は (None, 理由)"""
    # 元URLには list= や pp= が付くものがあるので、正規化した watch URL で問い合わせる
    watch = f'https://www.youtube.com/watch?v={vid}'
    ep = 'https://www.youtube.com/oembed?url=' + urllib.parse.quote(watch, safe='') + '&format=json'
    last = ''
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(ep, headers={'User-Agent': 'aspiewho-build/1.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r).get('title'), None
        except urllib.error.HTTPError as e:
            # 404=削除/非公開, 401=埋め込み禁止 → 再試行しても無駄なので即あきらめる
            if e.code in (401, 403, 404):
                return None, f'HTTP {e.code}'
            last = f'HTTP {e.code}'
        except Exception as e:
            last = f'{type(e).__name__}: {e}'
        if attempt < RETRIES:
            time.sleep(1.5 * (attempt + 1))
    return None, last


def main():
    args = sys.argv[1:]
    refresh = '--refresh' in args
    retry_failed = '--retry-failed' in args
    older = None
    if '--older-than' in args:
        older = int(args[args.index('--older-than') + 1])

    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE, encoding='utf-8'))

    tg = targets()
    print(f'対象: {len(tg)}件 / キャッシュ済み: {len(cache)}件')

    now = datetime.now(timezone.utc)
    todo = []
    for vid, url, local in tg:
        e = cache.get(vid)
        if refresh or not e:
            todo.append((vid, url, local)); continue
        if retry_failed and not e.get('title'):
            todo.append((vid, url, local)); continue
        if older is not None:
            try:
                got = datetime.fromisoformat(e['fetched_at'])
                if now - got > timedelta(days=older):
                    todo.append((vid, url, local))
            except Exception:
                todo.append((vid, url, local))
    print(f'今回取得する件数: {len(todo)}\n')

    ok = ng = 0
    for i, (vid, url, local) in enumerate(todo, 1):
        t0 = time.time()
        title, err = fetch(vid)
        ms = int((time.time() - t0) * 1000)
        cache[vid] = {
            'title': title,                 # 取得できなければ None
            'local_title': local,           # フォールバック用
            'source_url': url,
            'fetched_at': now.isoformat(),
            'error': err,
        }
        if title:
            ok += 1
            print(f'{i:>3}/{len(todo)} ✅ {ms:>5}ms  {title[:56]}')
        else:
            ng += 1
            print(f'{i:>3}/{len(todo)} ❌ {ms:>5}ms  {vid}  {err}  → ローカル題名にフォールバック')
        time.sleep(DELAY)

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(f'\n成功 {ok} / 失敗 {ng}  → {CACHE} に保存しました')
    if ng:
        print('失敗分は build.py 側でローカルの分類タイトルにフォールバックされます。')


if __name__ == '__main__':
    main()
