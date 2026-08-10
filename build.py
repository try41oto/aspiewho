#!/usr/bin/env python3
# aspiewho 動画目次サイト ジェネレーター v7
import json, html, os, gzip, sys, re
# 引数なしの `python3 build.py` だけで動くよう、既定の入出力は build.py と同じ場所にする
# （どのディレクトリから実行しても、リポジトリ直下の index.html を作る）
_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv)>1 else os.path.join(_HERE,'aspiewho_1502_classified.json')
OUT = sys.argv[2] if len(sys.argv)>2 else os.path.join(_HERE,'index.html')

# ================= 設定 =================
ORDER=['サブカル','お笑い','生活・文化','言葉','音楽','スポーツ・遊び','地域','歴史','科学',
 '心理・知覚','健康・医療','障がい・福祉','教育','思想・宗教','社会・政治','経済',
 'メディア','デバイス・デジタル生活','IT基盤','AI']
TAIL_GROUP=('ハーモニカ',['029','033'])
NEWCAT_GROUP='この動画生成'
NEWCAT_TITLE='失敗と勉強の動画作りと公開'
NEWCAT_ID='genvid'
MOVE_IDS=['8UFhGDi4YUg','4gZthMfSs2Y','bQJ4fE9GQSI','HvdUHeEzltA','o4HopqoW8ek','QPwuHSsXyU4',
 'H9-7-fHTvoY','ddjkcRM3H4s','nsl3lWw2ZEc','uG0WFwTonJw','DGjNEqHEIDQ','MpkyVKiV1pk',
 'pgQQI_ykxUI']

FIRST=[(None,['e_sYnb1CdAs','etxG4LU462U','1fg64F4OBnU','dccoLUinYDQ','KxMbR6po5wA','ARyDkAJ4FBQ'])]
ID_WAR='cEkx8UrBpAU'
CAP_WAR='量産のきっかけは、戦争の話。'
ID_HAIBOKU='NjBJJ3JSqag'
ID_INTENT='uG0WFwTonJw'  # ★当初オンプレmp4生成思想…（追加2／「意図があって」のアンカー先）
ID_FINAL='ddjkcRM3H4s'    # ★スマホだけで1日15本以上…（この動画生成／追加3のリンク先）
TXT_FINAL='最終形はこうなった'
# カテゴリ一覧の表示からのみ除外するID（データ自体は残すので神回★グリッドには載る）
KAMI_ONLY_IDS={'CKOHd9PrqeE','1v_H2rHfhQw','cE6IhFUDq4A'}  # 神回★とカテゴリの二重掲載を解消
HIDE_FROM_CAT=KAMI_ONLY_IDS|{ID_FINAL,ID_INTENT}
TXT_HAIBOKU='技術的敗北と再生の物語'
IMGS={n:f'img/{n}.webp' for n in ('norikome','chiko','nori','kome','haiboku')}
IMGS['arigatou']='img/arigatou_anim.webp'
IMGS['nanananana']='img/nanananana_anim.webp'
MORE=['TCe2SvES2x4','2Zky_cifOmw','_BnfibpgX-A','GNnv5kXhJJs','bsVYxPsVdCQ',
      '3D6P6cqT1X8','nEayqs5K8x8','v-EOKlp8Vfk','lXz5Y8umPxY','SQIpV-Jcpl8','I4Mx8zksrh0',
      'TfRZv5DW3Es']

# NotebookLM の口ぐせ（この順に、ページ全体へ均等に差し込む）
PHRASES=['学ぶことがだいすきなアナタ、本日もようこそ、このディープライブへ',
 'あの〜、ちょっと想像してみてほしいんですけど．．','まさにそこなんですよ','パラダイムシフト',
 'よーし、これらを紐解いていきましょう',
 'さいごあなたに、挑発的な思考のタネを投げかけて、この深掘りの旅を、、']

# 1504本のうち外に出した2本（入れ替わっていたら下の2行を交換）
ID_ICHIMI='uBtnbr0gu80'   # 1500タイトルを24分で一気見！
ID_OWARI ='76XZgkPmg2s'   # 終わり☆AI能力把握実験、脳内発散訓練、遺言】動画量産1500本
TXT_ICHIMI_HTML='全タイトルを<br>24分一気見！'   # 明示改行で必ず2行にする
TXT_OWARI='終わり☆AI能力把握実験、脳内発散訓練、ポートフォリオ、遺言】動画量産1500本'
ID_SELFINTRO='zQP6i3wEvPY'   # 自己紹介】積極奇異型アスペルガー(ASD)症候群、ワタシはココに居ます！(自慢)
TXT_SELFINTRO='自己紹介'
ID_KEITORA='hZIE2BqHt6c'    # 軽自動車 as a Japanese Service
ID_CFRZ6='ffXw0GwXpP8'      # レッツノート究極の開発哲学
ID_XUBUNTU='th1DV_2jO2c'    # Corei5,メモリ4gb,hdd500gで中古4千円のパナレッツノート...xubuntuで結構使える
ID_SWIFT='Xq5R_9k6lLg'      # 90年代国産スポーツカーとMT車の再評価と魅力
ID_M1='PfPNEnZWqU0'         # 神回★】Armプロセッサは他とどう違うのか
ID_A2337='yw2PKdR2I3A'      # 神回★】MacPCでLinuxを動かすためAppleSiliconをハックする...
ID_ASAHI='Og-FD63kuxk'      # MacbookをハックしてるAsahiLinuxって、どうして日本語っぽい朝日Asahiと命名されているのですか？
NORI_AT_CAT='073'   # のり画像を差し込むカテゴリ（発達障害の特性とライフハック）

SHORT_URL_HREF='https://try41oto.github.io/aspiewho/'
# ♫一覧の先頭に置く8本（旧・一気見バナーの♫バッジ）。ページ内にサムネイルが無いので
# 矢羽は付けず題名リンクだけを並べる。ローカル題名はoEmbed取得失敗時のフォールバック
TOPREF=[
 ('https://www.youtube.com/watch?v=v6xUXCclN04&list=RDv6xUXCclN04&start_radio=1&pp=ygUV5qW96IiI44Gu5pmC44CA5Lit5bedoAcB','\u697d\u8208\u306e\u6642\u3000\u4e2d\u5ddd'),
 ('https://www.youtube.com/watch?v=mNSDWf2EX3Q&list=RDmNSDWf2EX3Q&start_radio=1&pp=ygUt5YiH5omL44Gu44Gq44GE44GK44GP44KK44KC44Gu44CA6L-R6Jek44KG44GNoAcB','\u5207\u624b\u306e\u306a\u3044\u304a\u304f\u308a\u3082\u306e\u3000\u8fd1\u85e4\u3086\u304d'),
 ('https://www.youtube.com/watch?v=R5zxnw5NMxU&list=RDR5zxnw5NMxU&start_radio=1&pp=ygUW5oSb44Gu5oyo5ou244CAVGVtaXJrYaAHAQ%3D%3D','\u611b\u306e\u6328\u62f6\u3000Temirka'),
 ('https://www.youtube.com/watch?v=xrfu574p1Y4&list=RDxrfu574p1Y4&start_radio=1&pp=ygUb44OR44Oq44Gu56m644Gu5LiL44CA6KeS6LC3oAcB','\u30d1\u30ea\u306e\u7a7a\u306e\u4e0b\u3000\u89d2\u8c37'),
 ('https://www.youtube.com/watch?v=slesVH8wERU&list=RDslesVH8wERU&start_radio=1&pp=ygUf44G844GP44Gf44Gh44Gu5aSx5pWX44CANzM3Z3VhbaAHAdIHCQnFCwGHKiGM7w%3D%3D','\u307c\u304f\u305f\u3061\u306e\u5931\u6557\u3000737guam'),
 ('https://www.youtube.com/watch?v=Zq1cqWIRLAc&list=RDZq1cqWIRLAc&start_radio=1&pp=ygUQ44GT44Gu6YGTIOi_keiXpKAHAQ%3D%3D','\u3053\u306e\u9053\u3000\u8fd1\u85e4'),
 ('https://www.youtube.com/watch?v=J02j_bjTO7k&list=RDJ02j_bjTO7k&start_radio=1&pp=ygUi44OV44Kj44Ks44Ot44Gu57WQ5ama44CAUGVsdG9rb3NraaAHAQ%3D%3D','\u30d5\u30a3\u30ac\u30ed\u306e\u7d50\u5a5a\u3000Peltokoski'),
 ('https://www.youtube.com/watch?v=GUBh7HOBXBg&list=RDGUBh7HOBXBg&start_radio=1&pp=ygUW5Lq655Sf44Gu5omJ44CANzM3Z3VhbaAHAQ%3D%3D','\u4eba\u751f\u306e\u6249\u3000737guam'),
]
TOPREF_LOCAL={re.search(r'v=([A-Za-z0-9_\-]{11})',u).group(1):t for u,t in TOPREF}
LINK_TIME='https://www.youtube.com/watch?v=QMAloSCkHag&t=60s'
LINK_IKKI='https://www.youtube.com/watch?v=hpo7e3-MewI&t=60s'
LINK_STAR='https://www.youtube.com/watch?v=d774Mau6-aI&t=60s'
# ================= 設定ここまで =================

d=json.load(open(SRC))
B={b['block']:b for b in d['blocks']}
C={c['category_id']:c for b in d['blocks'] for c in b['categories']}
V={v['video_id']:v for b in d['blocks'] for c in b['categories'] for v in c['videos']}
V['lXz5Y8umPxY']['title']=V['lXz5Y8umPxY']['title'].removeprefix('100本目】')
for _v in V.values():
    if _v['title'].startswith('神回★】'):
        _v['title']=_v['title'].removeprefix('神回★】')

# LMボタンの除外対象：ハーモニカ演奏系カテゴリ（029 複音ハーモニカの演奏 / 033 ハーモニカの歴史・道具・名演奏家）
HARMONICA_IDS={v['video_id'] for cid in TAIL_GROUP[1] for v in C[cid]['videos']}

import csv as _csv
MUSIC_CATS={'複音ハーモニカの演奏','楽曲の歌詞を深掘りする','童謡・唱歌と日本の歌','世界の音楽とクラシック',
 '楽器と音響のしくみ','ハーモニカの歴史・道具・名演奏家','昭和歌謡・演歌のつくり手'}
MUSIC_OVERRIDE_IDS={'lmnI2SvWfM0','ymbaX87ij0M'}  # B'z LOVE PHANTOM / 尾崎豊 15の夜（非音楽カテゴリだが実際は楽曲）
REF={}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'work','out-todo_368_all.csv'),encoding='utf-8') as _f:
    for _row in _csv.DictReader(_f):
        _url=_row['found_url'].strip()
        if not _url.startswith('http'):
            continue
        _is_music=_row['category_name'] in MUSIC_CATS or _row['video_id'] in MUSIC_OVERRIDE_IDS
        REF[_row['video_id']]={'symbol':'♫' if _is_music else '＠','url':_url}

def refbadge(vid):
    r=REF.get(vid)
    if not r: return ''
    return f'<span class="reflink refbadge" data-url="{html.escape(r["url"])}">{r["symbol"]}</span>'

def reflink(vid):
    r=REF.get(vid)
    if not r: return ''
    return f' <span class="reflink" data-url="{html.escape(r["url"])}">[ {r["symbol"]} ]</span>'

OEMBED_CACHE={}
_oc=os.path.join(os.path.dirname(os.path.abspath(__file__)),'work','oembed_titles_cache.json')
if os.path.exists(_oc):
    OEMBED_CACHE=json.load(open(_oc,encoding='utf-8'))

CLIPICON='<span class="clipicon" aria-hidden="true">🔗</span>'
ZERO_CATS={'029'}          # 冒頭から再生するカテゴリ
tn=lambda i:f'https://img.youtube.com/vi/{i}/mqdefault.jpg'
tnhq=lambda i:f'https://img.youtube.com/vi/{i}/hqdefault.jpg'
wu=lambda i,s=60:f'https://www.youtube.com/watch?v={i}'+(f'&t={s}s' if s else '')

for c in C.values():
    z = c['category_id'] in ZERO_CATS
    for v in c['videos']:
        v['start_sec']=0 if z else 60
        v['watch_url']=f'https://www.youtube.com/watch?v={v["video_id"]}'+('' if z else '&t=60s')

SOLO_IDS={ID_WAR,ID_HAIBOKU}  # 末尾で専用カード表示するため、通常カテゴリの一覧からは外す（重複表示防止）
moved_map={}
solo_map={}
for c in C.values():
    keep=[]
    for v in c['videos']:
        if v['video_id'] in MOVE_IDS:
            moved_map[v['video_id']]=v
        elif v['video_id'] in SOLO_IDS:
            solo_map[v['video_id']]=v
        else:
            keep.append(v)
    c['videos']=keep
    c['count']=len(keep)
assert len(moved_map)==len(MOVE_IDS)
assert len(solo_map)==len(SOLO_IDS)
NEWCAT={'category_id':NEWCAT_ID,'name':NEWCAT_TITLE,'videos':[moved_map[i] for i in MOVE_IDS],'count':len(MOVE_IDS)}
C[NEWCAT_ID]=NEWCAT
for b in d['blocks']:
    b['categories']=[c for c in b['categories'] if c['count']>0]
C={cid:c for cid,c in C.items() if c['count']>0}

tname,tids=TAIL_GROUP
groups=[]
for n in ORDER:
    cs=[c for c in B[n]['categories'] if c['category_id'] not in tids]
    if cs: groups.append((n,cs))
groups.append((tname,[C[x] for x in tids]))
groups.append((NEWCAT_GROUP,[NEWCAT]))
assert sum(len(cs) for _,cs in groups)==len(C)
assert sum(c['count'] for _,cs in groups for c in cs)==d['total_videos']-len(SOLO_IDS)

def cut(t,n=26):
    return t if len(t)<=n else t[:n]+'…'

def best_cols(n,options):
    # 最終行の空きマスが最小の列数を選ぶ。同数なら列数が多い方を優先
    def empty(g): return (-n)%g
    return max(options,key=lambda g:(-empty(g),g))

def pkgrid(ids,extra='',cls='',anchor=False,jump=False):
    """anchor=True でカードに id="v-動画ID" を振る（飛び先。カテゴリ一覧だけに振ること）。
    jump=True で data-jump を付け、スマホでは動画を開かずその id へ飛ばす。"""
    at=lambda i:(f' id="v-{i}"' if anchor else '')+(f' id="s-{i}" data-jump="v-{i}"' if jump else '')
    return f'<div class="pks{cls}">'+''.join(
     f'<a class="pk"{at(i)} href="{V[i]["watch_url"]}" target="_blank" rel="noopener">'
     f'<span class="thumb"><img src="{V[i]["thumbnail_url"]}" alt="" width="320" height="180" loading="lazy" decoding="async">{refbadge(i)}{CLIPICON}</span>'
     f'<p>{html.escape(V[i]["title"])}</p>'
     f'<span class="pop" aria-hidden="true" data-t="{html.escape(V[i]["title"])}"></span></a>' for i in ids)+extra+'</div>'

def pkcard(href,thumb,title,cls='',vid=None):
    return (f'<a class="pk{cls}" href="{href}" target="_blank" rel="noopener">'
            f'<span class="thumb"><img src="{thumb}" alt="" width="320" height="180" loading="lazy" decoding="async">{refbadge(vid) if vid else ""}{CLIPICON}</span>'
            f'<p>{html.escape(title)}</p>'
            f'<span class="pop" aria-hidden="true" data-t="{html.escape(title)}"></span></a>')

def ilink(href,vid,text):
    return (f'<a class="ilink" href="{href}" target="_blank" rel="noopener" style="--th:url({tnhq(vid)})">'
            f'{text}<span class="pop" aria-hidden="true"></span></a>')

def vlink(vid,text):
    return (f'<a class="ilink vlink" href="{wu(vid)}" target="_blank" rel="noopener" style="--th:url({tnhq(vid)})">'
            f'{text}<span class="pop" aria-hidden="true"></span></a>')

def rows(vids):
    out=''
    for v in vids:
        t=html.escape(v['title'])
        out+=(f'<a class="row" href="{v["watch_url"]}" target="_blank" rel="noopener">'
              f'<span class="thumb"><img class="mini" src="{v["thumbnail_url"]}" alt="" width="320" height="180" loading="lazy" decoding="async">{refbadge(v["video_id"])}{CLIPICON}</span>'
              f'<span class="ttl"><span class="ttlx">{t}</span>{reflink(v["video_id"])}</span>'
              f'<span class="pop" aria-hidden="true" data-t="{t}"></span></a>')
    return f'<div class="rows">{out}</div>'

# ピックアップ枠の重複防止：FIRST/MORE（最上部）と WAR・HAIBOKU・ハーモニカ移設組（末尾の専用カード）は
# それぞれ別枠で確定表示するので、神回★グリッドには二重に出さない
FIRST_IDS={i for _,ids in FIRST for i in ids}
BELOW_PRIORITY_IDS=set(MOVE_IDS)|{ID_WAR,ID_HAIBOKU}
KAMI=[v['video_id'] for _,cats in groups for c in cats for v in c['videos']
      if v['kamikai'] and v['video_id'] not in FIRST_IDS|set(MORE)|BELOW_PRIORITY_IDS]

CHIKO=('<img class="stk masc chikoimg" src="'+IMGS['chiko']+'" alt="" width="300" height="265" decoding="async" fetchpriority="high">')
first=''.join((f'<p class="pkcap">{html.escape(c)}</p>' if c else '')+
 pkgrid([x for x in i+MORE if x not in BELOW_PRIORITY_IDS],cls=' pksfirst',jump=True) for c,i in FIRST)

TOTAL_CATS=sum(len(cats) for name,cats in groups if name!=tname)
NPHR=len(PHRASES)
SEG=24  # 4の倍数で行が割れず、さいごが最後尾固定でも末尾の区切りが大きくなりすぎない
THR={SEG*i:i for i in range(1,NPHR-1)}

def catbox(name,c,desc=True,grid=False,firstlabel=False,cls='',hide=True,anchor=False,gid=''):
    """cls は details に足すクラス（神回★の ' solo' など）。
    hide=False にすると HIDE_FROM_CAT の除外を行わない（神回★専用に載せる動画があるため）。
    name が空ならブロック名のバッジを出さない。"""
    d=f'<span class="d">{html.escape(c["description"])}</span>' if desc else ''
    vids=[v for v in c['videos'] if not hide or v['video_id'] not in HIDE_FROM_CAT]
    if grid:
        n=len(vids)
        g=best_cols(n,(2,3)); pc=best_cols(n,(5,6))
        ids=[v['video_id'] for v in vids]
        body=pkgrid(ids,cls=f' g{g} pc{pc}',anchor=anchor)
    else:
        body=rows(vids)
    # 名前が長いと絶対配置の青バッジが「戻る」に重なるため、8文字以上は別クラスで小さくする
    lbl=(f'<span class="blklabel{" grouptop" if firstlabel else ""}'
         f'{" longname" if firstlabel and len(name)>=8 else ""}"'
         f'{f" id={chr(34)}{gid}{chr(34)}" if gid else ""}>{html.escape(name)}</span>'
         if name else '')
    # 上位カテゴリの先頭にだけ、枠の右上に「戻る」（ページ最上部の矢羽一覧へ）。スマホのみ表示
    if gid:
        # 青バッジと「戻る」を1行にまとめる。絶対配置で個別に置くと画面幅次第で重なるため
        lbl='<span class="toprow">'+lbl+'<a class="gback" href="#top">\u623b\u308b</a></span>'
    return (f'<details class="item{cls}" id="c{c["category_id"]}">'
     f'<summary>{lbl}'
     f'<span class="row1"><span class="pm" aria-hidden="true">＋</span>'
     f'<span class="t">{html.escape(c["name"])}</span>'
     f'<span class="closelbl" aria-hidden="true">↑ とじる</span></span>'
     f'{d}</summary>'
     f'<div class="catbody">{body}</div></details>')

HARMONICA_MERGED={'category_id':'harmonica','name':'ハーモニカ演奏とその歴史・調律',
 'videos':[v for x in tids for v in C[x]['videos']]}
HARMONICA_BOXES=catbox(tname,HARMONICA_MERGED,desc=False)
NEWCAT_BOX=catbox(NEWCAT_GROUP,NEWCAT,desc=False,grid=True)

# 神回★はカテゴリ一覧の先頭（ドラゴンボール考察の左隣）に、他のカテゴリと同じ大きさで置く。
# KAMI_ONLY_IDS はカテゴリ側では隠すが神回★には載せるため hide=False にする
KAMI_CAT={'category_id':'kamikai','name':'\u795e\u56de\u2605','description':'\u304a\u6c17\u306b\u5165\u308a',
 'videos':[V[i] for i in KAMI]}
DESC_BOX=('<p class="shinkai-description full">'
 '<strong>\u5de6\u300e\uff0b\u300f\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068\u3001\u305d\u306e\u4e0b\u5074\u306b\u30ba\u30e9\u30c3\u30c8</strong>'
 '\u30bf\u30a4\u30c8\u30eb\u8868\u793a\u3055\u308c\u307e\u3059\u3002</p>')
# 上位カテゴリ（サブカル〜AI）。青バッジをアンカー先にし、ページ上部に矢羽の飛び先を並べる
GROUPTOP=[nm for nm,_ in groups if nm not in (tname,NEWCAT_GROUP)]
def _w(t):
    """矢羽のおおよその幅。半角は狭いので0.55文字ぶんとして数える"""
    return sum(0.55 if c.isascii() else 1 for c in t)
# スマホは順不同でよいので、幅の広い順に並べ替えて隙間を減らす（4行に収めるため）。
# 並べ替えは CSS の order だけで行い、DOM順＝パソコンの表示順は変えない
_rank={nm:i for i,nm in enumerate(sorted(GROUPTOP,key=_w,reverse=True))}
GNAV=('<nav class="gnav" aria-label="\u4e0a\u4f4d\u30ab\u30c6\u30b4\u30ea\u3078\u79fb\u52d5">'
 +''.join(f'<a class="gjump" style="--o:{_rank[nm]}" href="#g{i:02d}">{html.escape(nm)}</a>'
          for i,nm in enumerate(GROUPTOP))+'</nav>')

gitems=[f'<p class="say full">{html.escape(PHRASES[0])}</p>', DESC_BOX,
        catbox('',KAMI_CAT,grid=True,cls=' solo',hide=False)]
n=1
for gi,(name,cats) in enumerate(groups):
    if name in (tname,NEWCAT_GROUP):
        continue
    for ci,c in enumerate(cats):
        gitems.append(catbox(name,c,grid=True,firstlabel=(ci==0),anchor=True,
                             gid=(f'g{GROUPTOP.index(name):02d}' if ci==0 else '')))
        n+=1
        if c['category_id']==NORI_AT_CAT:
            gitems.append(f'<img class="stk masc noridex" src="{IMGS["nori"]}" alt="" width="270" height="254" loading="lazy" decoding="async">')
            n+=1
        if n in THR:
            k=THR[n]
            gitems.append(f'<p class="say{" l" if k%2 else ""} full">{html.escape(PHRASES[k])}</p>')
klast=NPHR-1
gitems.append(f'<p class="say{" l" if klast%2 else ""} full">{html.escape(PHRASES[klast])}</p>')
idx=f'<div class="items">{"".join(gitems)}</div>'

CSS='''
:root{--bg:#FFF;--face:#FAFBFC;--line:#C4CFD9;--line2:#E2E7EC;--fg:#16212D;--dim:#4B5A6B;
--accent:#8A5F0F;--sub:#245670;--tint:#FFF8E9;--soft:#F3F7F9;--deep:#1D6483;
--green:#F8FCF8;--greenline:#CFE3CF;--alt:#FFFCF0;--blue:#125A93;--ltblue:#E7F2FA;--ltblue2:#D6EAF7;--rowalt:#F6FAFD}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-size:19px;line-height:1.85;
font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
a{color:inherit}
a:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:4px}
a[target="_blank"]::after{content:'🔗';display:inline-block;font-size:.55em;margin-left:3px;vertical-align:middle;opacity:.7;text-decoration:none}
.hero{padding:28px 0 4px}
.url{display:inline-flex;align-items:center;min-height:44px;padding:8px 16px;border:1px solid var(--line);border-radius:6px;
background:var(--face);font-size:17px;color:var(--sub);text-decoration:none;font-variant-numeric:tabular-nums}
.url b{color:var(--fg);font-weight:700}
.mins{margin:16px 0 0;font-size:19px;color:var(--dim)}
.thankswrap{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:6px 0 0}
.thanks{margin:0;font-size:19px;color:var(--dim)}
.thanks a,.note a{color:var(--sub);text-underline-offset:3px}
.aha{margin:0;font-size:clamp(34px,10vw,54px);font-weight:800;letter-spacing:.04em;line-height:1.3;text-align:center}
.ahatop{display:flex;align-items:center;gap:10px;margin:22px 0 0}
.ahatop .aha{text-align:left;flex:1 1 auto;min-width:0}
.ahawrap .noripc{display:none}
@media(min-width:940px){
 /* 「必ずみつかる、脳アハ！」を、ありがとう と ナナナナ のちょうど中間へ移す。
    DOMは動かさず、hero を1本のフレックス行に畳んで（display:contents）order で並べ替える。
    .aha の左右 auto マージンが余白を二等分するので、2つのアイコンの中間に来る */
 .hero{display:flex;flex-wrap:wrap;align-items:center;column-gap:10px}
 .greet,.thankswrap,.ahatop{display:contents}
 .hero .mins{order:1;flex:0 0 100%}
 .hero .thanks{order:2;flex:0 1 auto;min-width:0}
 .hero .arig{order:3}
 .hero .aha{order:4;margin:0;text-align:center}
 .hero .nana{order:5;margin-left:0}
 /* 矢羽はスマホと同じくページ最上部へ。全幅を使うぶん行数が最小になる */
 .hero .gnav{order:0;flex:0 0 100%;margin:0 0 6px}
 /* きちんと2行に収まる上限まで大きくする。1行の必要幅は文字寸法にほぼ比例するので、
    画面幅から線形に決め、広い画面では21pxで止める */
 .hero .gjump{font-size:clamp(11px,calc(2.4vw - 11px),21px);padding:8px 22px 8px 12px;line-height:1.2}
 .hero .ahawrap{order:7;flex:0 0 100%;margin-top:14px}
 .ahatop .norimobile{display:none}
 .ahawrap .noripc{display:block}
}
/* スマホは2つの動くアイコンでリード文を挟む。パソコンでは挨拶行の側を使うので、
   こちらは隠し、逆にスマホでは挨拶行の側を隠す（同じ画像が二重に出ないようにする） */
.leadrow{display:flex;align-items:center;gap:8px}
.leadrow .lead{flex:1 1 auto;min-width:0}
@media(max-width:939.98px){.leadrow .lead{font-size:13px;line-height:1.6}}   /* 例示語と同寸。後方の .lead に勝たせる */
.leadrow .leadicon{flex:0 0 auto;margin:0}
@media(min-width:940px){.leadrow{display:block}.leadrow .leadicon{display:none}}   /* .stk が後方にあるため詳細度を上げる */
/* ありがとうは「必ずみつかる、脳アハ！」の左へ。パソコンでは挨拶行の側を使うので隠す */
@media(min-width:940px){.ahatop .ahaicon{display:none}}
@media(max-width:939.98px){
 /* ありがとうが入ったぶん行が狭くなる。「脳アハ！」を折り返させないよう周囲を詰める */
 .ahatop .ahaicon{flex:0 0 auto;align-self:center;margin:0;width:52px}
 .ahatop .norimobile{width:clamp(80px,24vw,150px)}
 .ahatop .aha{white-space:nowrap}
}
/* 「ありがとうございます」等はパソコンだけ。スマホは短い文面にする */
@media(max-width:939.98px){.ponly{display:none}}
@media(max-width:939.98px){.thankswrap .arig,.thankswrap .nana{display:none}
 /* スマホの並び順：矢羽 → 脳アハ！ → 1つ視聴に25分 → 挨拶文 → 以降。
    1列グリッドにして order だけで入れ替える（DOMは触らない） */
 .hero{display:grid;grid-template-columns:1fr;padding-top:12px}
 .hero>.gnav{order:1;margin:0;grid-template-columns:repeat(auto-fill,minmax(78px,1fr))}
 /* 25分・挨拶は「必ずみつかる、」の真上へ。両者は改行して2行にする */
 .hero>.greet{order:2;margin:16px 0 0}
 .hero>.ahatop{order:3;margin:6px 0 0}
 .hero>.ahawrap{order:4}
 .greet .mins{margin:0}
 .greet .thankswrap{margin:2px 0 0}
 .greet .thanks{font-size:13px}
}
/* 上位カテゴリへ飛ぶ矢羽。色は飛び先の青バッジと同じ #2563EB / 白。
   ＠一覧のLMボタンと同じ形・同じ文字サイズだが、左端は閉じた（まっすぐな）右向き矢羽にする */
/* 文字数なりの幅で左から詰める。1行に入るだけ入れるので、画面幅がいくつでも行数が最小になる */
.gnav{display:flex;flex-wrap:wrap;align-content:start;gap:3px;min-width:0}
.gjump{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
 background:#2563EB;color:#fff;font-size:11px;font-weight:700;line-height:1.15;
 padding:5px 12px 5px 5px;text-decoration:none;white-space:nowrap;
 /* 矢羽の先端は幅によらず10px固定。%指定だと短い項目で尖りが潰れる */
 clip-path:polygon(0 0,calc(100% - 10px) 0,100% 50%,calc(100% - 10px) 100%,0 100%)}
/* スマホだけ幅の広い順に並べ替える。パソコンはDOM順＝上位カテゴリの並び順のまま */
@media(max-width:939.98px){.gjump{order:var(--o)}}
@media(max-width:359.98px){.gjump{font-size:10px;padding:4px 11px 4px 4px}}
.gjump:hover{background:#1D4ED8}
/* アンカー先の右上に置く「戻る」。ページ最上部の矢羽一覧へ戻す。スマホのみ。
   左向き矢羽（左端が尖り右端はまっすぐ）で、色は濃い緑・白文字 */
/* 上位カテゴリの先頭だけ、枠の上辺に「名前 … 戻る」の1行を渡す。
   フレックスなので、名前が長くても戻るに重なることはない */
.item .toprow{position:absolute;top:-18px;left:10px;right:10px;z-index:3;
 display:flex;align-items:center;gap:6px}
.item .toprow .blklabel.grouptop{position:static;flex:0 1 auto;min-width:0;top:auto;left:auto}
details.item[open]>summary .toprow{display:none}
.item .gback{flex:0 0 auto;margin-left:auto;
 display:inline-flex;align-items:center;justify-content:center;
 background:#276B3B;color:#fff;font-size:21px;font-weight:700;letter-spacing:.08em;
 line-height:1.4;padding:3px 10px 3px 16px;text-decoration:none;white-space:nowrap;
 clip-path:polygon(10px 0,100% 0,100% 100%,10px 100%,0 50%)}
details.item[open]>summary .gback{display:none}
@media(min-width:940px){.item .gback{font-size:16px;padding:3px 9px 3px 15px}}
.ahawrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:20px;margin:16px 0 0}
.leadcol{flex:1 1 260px;min-width:220px;max-width:480px}
.stk{display:block;height:auto;flex:0 0 auto}
.arig{width:64px;margin-right:-4px}
.nana{width:64px;margin-left:auto}
.masc{width:clamp(120px,32vw,170px)}
.qrbox{display:flex;align-items:flex-end;gap:8px;flex:0 0 auto}
.qrcol{display:flex;flex-direction:column;align-items:center;gap:8px}
.addhome{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:44px;
padding:10px 16px;background:#fff;color:var(--blue);border:1px solid var(--blue);border-radius:8px;
font-size:15px;font-weight:700;letter-spacing:.03em;cursor:pointer;font-family:inherit;
white-space:nowrap}
.addhome:hover{background:var(--ltblue)}
.sharebtn{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:40px;
padding:8px 16px;background:#fff;color:var(--blue);border:1px solid var(--blue);border-radius:8px;
font-size:14px;font-weight:700;letter-spacing:.03em;cursor:pointer;font-family:inherit}
.sharebtn:hover{background:var(--ltblue)}
.modal-overlay{position:fixed;inset:0;background:rgba(10,18,28,.55);display:flex;
align-items:center;justify-content:center;z-index:50;padding:20px}
.modal-overlay[hidden]{display:none}
.modal-box{background:#fff;border-radius:10px;padding:24px 22px;max-width:340px;width:100%;
box-shadow:0 20px 60px rgba(10,18,28,.35)}
.modal-box p{margin:0 0 18px;font-size:17px;line-height:1.8;color:var(--fg)}
.modal-close{display:inline-flex;min-height:44px;padding:10px 22px;background:var(--accent);
color:#fff;border:none;border-radius:20px;font-size:15px;font-weight:700;cursor:pointer;
font-family:inherit}
.red{color:#B02E24;font-weight:700}
.hl{color:var(--blue);font-size:24px;font-weight:800;letter-spacing:.04em}
.qr{flex:0 0 auto;text-align:left;text-decoration:none;color:var(--fg);display:block;min-height:44px}
.qr img{display:block;width:115px;height:auto;padding:5px;background:#fff;
border:1px solid var(--line);border-radius:5px;image-rendering:pixelated}
@media(max-width:939.98px){
 .qrbox{display:grid;grid-template-columns:auto auto;grid-template-areas:"book share" "qr chiko";align-items:center;justify-content:center;gap:10px 16px}
 .qrcol{display:contents}
 .addhome{grid-area:book}
 .sharebtn{grid-area:share}
 .qr{grid-area:qr}
 .chikoimg{grid-area:chiko}
}
.aha small{display:block;font-size:18px;font-weight:600;color:var(--dim);letter-spacing:.06em;margin-bottom:3px}
.lead{margin:0;font-size:17px;line-height:1.7;text-align:left;color:var(--dim)}
.note{margin:26px 0 0;padding:20px 18px;background:var(--green);border-radius:8px;font-size:18px;line-height:1.95}
.note h3{margin:0 0 8px;font-size:17px;letter-spacing:.1em;color:var(--sub);font-weight:700}
.note .sep{margin:14px 0 0;padding-top:14px;border-top:1px solid var(--greenline)}
@media(min-width:940px){.note .sep.pccenter{text-align:center}}
.note .ff{font-weight:700}
/* 口ぐせの帯 */
.say{margin:36px 0;padding:30px 22px;background:var(--deep);color:#fff;border-radius:6px;
font-family:"Hiragino Mincho ProN","ヒラギノ明朝 ProN","Yu Mincho","游明朝","YuMincho",
"Noto Serif JP","Noto Serif CJK JP","MS PMincho",serif;
font-size:clamp(21px,5.4vw,29px);line-height:2;letter-spacing:.08em;font-weight:400;
font-style:italic;font-style:oblique 12deg}
.say.l{font-style:normal;font-style:oblique -12deg}
/* ピックアップ */
.pkwrap{margin:32px 0 0}
.pkwrap h2{margin:0 0 14px;font-size:24px;font-weight:800;letter-spacing:.04em;color:var(--blue)}
.item.solo .t{color:var(--blue)}
.noridex{justify-self:center;align-self:center}
.stkitem{display:flex;align-items:center;justify-content:flex-end;padding:4px}
.pks{display:grid;grid-template-columns:repeat(2,1fr);gap:18px 14px;margin-bottom:16px}
.pks.pksfirst{grid-template-columns:repeat(3,1fr)}
@media(max-width:939.98px){
 .pks.g2{grid-template-columns:repeat(3,minmax(0,1fr))}
 .pks.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
}
@media(min-width:940px){
 .pks.pc5{grid-template-columns:repeat(5,minmax(0,1fr))}
 .pks.pc6{grid-template-columns:repeat(6,minmax(0,1fr))}
}
.pk{text-decoration:none;display:block;min-height:44px}
.thumb{position:relative;display:block}
.pk .thumb img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;
border:1px solid var(--line2);border-radius:6px;background:var(--face)}
.pk p{margin:8px 0 0;font-size:17px;line-height:1.6;overflow-wrap:anywhere;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pk .pop{display:none}
.pkcap{margin:8px 0 14px;font-size:clamp(22px,5.8vw,29px);font-weight:700;
color:var(--blue);letter-spacing:.02em;line-height:1.5}
/* 一気見バナー */
.bannerrow{position:relative;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:16px;margin:32px 0}
/* 上段は「全タイトル」バナー／♫の音楽／＠の動画 の3等分（1x3）。
   一覧を開いた側だけが grid-column:1/-1 で行いっぱいに広がる */
.bannerrow.top{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
align-items:stretch;gap:8px;margin:14px 0 0}
/* バナーの幅は画面幅に比例しない（1024pxで276px、540pxで480px）ため、
   タイトルの文字サイズは箱自身の幅に追従させる */
.bannerrow{container-type:inline-size}
.banner{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;min-height:44px;margin:0;padding:14px 10px;
background:var(--ltblue);border:1px solid var(--blue);border-radius:8px;text-decoration:none;position:relative}
.banner .pop{display:none}
/* a[target=_blank] の🔗はフレックス項目として1行を占めてしまうため、隅に絶対配置する */
.banner::after{position:absolute;right:5px;bottom:2px;margin:0}
/* 3等分になり1枠が狭いので、箱の幅に追従させつつ折り返しも許す */
.banner .lbl{font-size:min(19px,4.2cqi);font-weight:800;letter-spacing:.02em;line-height:1.35;color:var(--blue);text-align:center}
/* ページ内検索：3等分のすぐ下。1502本の題名から絞り込み、押すとその場所へ飛ぶ */
.findbox{margin:8px 0 0}
/* 例示は語数が多く4〜5行に折り返る。見出し行は置かず、これだけを検索欄の上に出す */
.findeg{margin:0;font-size:13px;font-weight:500;line-height:1.5;color:var(--dim)}
.findeg.under{margin:4px 0 0}   /* 検索欄を上下の語群で挟む */
.findrow{display:flex;gap:6px;margin:4px 0 0}
.findinput{flex:1;min-width:0;min-height:40px;padding:6px 10px;font-size:16px;font-family:inherit;
 color:var(--fg);background:#fff;border:1px solid var(--line);border-radius:6px}
.findinput:focus-visible{outline:3px solid var(--accent);outline-offset:1px}
.findbtn{flex:0 0 auto;min-height:40px;padding:6px 14px;font-size:14px;font-weight:700;
 font-family:inherit;color:#fff;background:var(--blue);border:1px solid var(--blue);
 border-radius:6px;cursor:pointer;white-space:nowrap}
.findbtn:hover{background:var(--deep)}
.findmsg{margin:4px 0 0;min-height:1.2em;font-size:13px;color:var(--dim)}
.findlist{max-height:46vh;overflow-y:auto;border:1px solid var(--line);border-radius:6px;background:#fff}
.findlist[hidden]{display:none}
.findhitbtn{display:block;width:100%;padding:8px 10px;font-size:14px;line-height:1.45;
 font-family:inherit;color:var(--fg);text-align:left;background:none;border:0;
 border-bottom:1px solid var(--line2);cursor:pointer}
.findhitbtn:last-child{border-bottom:0}
.findhitbtn:hover,.findhitbtn:focus-visible{background:var(--ltblue)}
.findhitbtn mark{background:#FFE58A;color:inherit;font-weight:700;padding:0 1px;border-radius:2px}
.findhitbtn .findcat{display:block;font-size:11px;color:var(--dim);margin-top:2px}
/* スマホは検索結果が読みにくいので、「あらかじめ」と同じ18pxに上げ、
   一覧の高さも広げる。検索語を画面最上部へ寄せるぶん下に余地ができる */
@media(max-width:939.98px){
 .findrow{scroll-margin-top:8px}
 .findlist{max-height:62vh}
 .findhitbtn{font-size:18px;line-height:1.6;padding:10px 12px}
 .findhitbtn .findcat{font-size:13px;margin-top:3px}
}
/* 検索から飛んだ先を一時的に光らせる */
.findhit{outline:4px solid #B02E24;outline-offset:3px;border-radius:6px}
/* 文中リンクのフワッとプレビュー */
.ilink{position:relative}
.ilink .pop{display:none}
/* カテゴリ一覧 */
.full{grid-column:1/-1}
.items{display:grid;grid-template-columns:1fr;gap:28px 10px}
.item .blklabel{position:absolute;top:-13px;left:14px;display:inline-block;
background:#FFF;padding:0 8px;font-size:18px;letter-spacing:.1em;color:var(--sub);font-weight:700;line-height:1.4}
.item:nth-of-type(even) .blklabel{background:var(--alt)}
details.item[open]>summary .blklabel{display:none}
.item{display:block;position:relative;min-height:44px;padding:26px 16px 18px;text-decoration:none;background:#FFF;
border:1px solid var(--line);border-radius:8px;transition:background .12s,border-color .12s}
.item:nth-of-type(even){background:var(--alt)}
.item:active{background:var(--tint)}
.item summary{cursor:pointer;list-style:none}
.item summary::-webkit-details-marker{display:none}
.item summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:4px}
.row1{display:flex;align-items:center;gap:10px}
.item .pm{font-size:22px;font-weight:700;color:var(--accent);flex:0 0 auto;line-height:1.4;
display:inline-block;transition:transform .15s ease}
details.item[open] .pm{transform:rotate(45deg)}
.item .t{font-size:26px;font-weight:700;flex:1;min-width:0;text-decoration:underline;
text-decoration-thickness:1px;text-underline-offset:3px;text-decoration-color:var(--line)}
.item .d{display:block;margin-top:8px;padding-left:29px;font-size:23px;color:var(--dim);line-height:1.7;font-weight:500}
.closelbl{display:none}
.items details.item[open]{grid-column:1/-1;background:#FFF}
.item .catbody{margin:16px 0 0;padding-top:16px;border-top:1px solid var(--line2)}
/* 展開時：見出しを「閉じるボタン」として大きく目立たせ、スクロール中も追従させる */
details.item[open]>summary{position:sticky;top:0;z-index:5;margin:-26px -16px 0;
padding:18px 16px;background:var(--tint);border-bottom:2px solid var(--accent);
box-shadow:0 3px 10px rgba(20,35,50,.14)}
details.item[open]>summary .t{color:var(--accent)}
details.item[open]>summary .d{display:none}
details.item[open] .closelbl{display:inline-block;margin-left:auto;flex:0 0 auto;
font-size:17px;font-weight:800;color:#fff;background:var(--accent);
padding:6px 14px;border-radius:20px;white-space:nowrap}
/* 動画1本ぶん（スマホ：左右2カラム、サムネは行の高さいっぱいに表示） */
.rows{display:flex;flex-direction:column}
.row{display:flex;align-items:stretch;min-height:48px;padding:0;
border-bottom:6px double var(--line);text-decoration:none;position:relative}
.row:nth-child(even){background:var(--rowalt)}
.row .thumb{width:50%;flex:0 0 auto}
.row .thumb img{width:100%;height:100%;object-fit:cover;
border-radius:6px;border:1px solid var(--line2);background:var(--face)}
.row .ttl{width:50%;flex:0 0 auto;box-sizing:border-box;padding:12px 12px 12px 14px;font-size:21px;line-height:1.5;min-width:0;font-weight:600;
align-self:center}
.row .ttl .ttlx{display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.row .ttl .reflink{display:none}
@media(max-width:359px){
 .row .thumb{width:45%}
 .row .ttl{width:55%}
}
.row .pop{display:none}
.row:active{background:var(--tint)}
.reflink{color:#FF0000;font-weight:700;cursor:pointer;white-space:nowrap;text-decoration:none}
.refbadge{position:absolute;top:6px;right:6px;min-width:34px;height:34px;padding:0 7px;
display:flex;align-items:center;justify-content:center;border-radius:17px;
background:#FF0000;color:#fff;font-size:20px;font-weight:700;line-height:1;z-index:2;
box-shadow:0 1px 4px rgba(0,0,0,.35)}
.clipicon{position:absolute;bottom:3px;right:3px;font-size:8px;line-height:1;
padding:2px 3px;border-radius:3px;background:rgba(15,25,35,.6);pointer-events:none;z-index:2}
a.pk::after,a.row::after{content:none}
.endwrap{margin:48px 0 32px}
.endgrid{margin-top:18px;gap:28px 14px}
.endgrid .endkome{grid-column:auto}
.endgrid details.item[open]{grid-column:1/-1;background:#FFF}
.selfline{margin:20px 0 0;font-size:19px;color:var(--sub)}
.techdesc{margin:12px 0 0;font-size:12px;line-height:1.8;color:var(--dim)}
.owariend{margin:14px 0 0;text-align:right;font-size:19px;color:var(--sub)}
.tail{margin:40px 0 28px;height:1px;background:var(--line)}
@media(min-width:600px){
 .wrap{padding:0 24px}
 .items{grid-template-columns:repeat(2,1fr)}
 .pks{grid-template-columns:repeat(3,1fr);gap:20px 16px}
 .qr img{width:140px}
 .arig{width:80px}
 .nana{width:80px}
 .masc{width:200px}
 .endgrid .endkome{grid-column:auto}
}
@media(min-width:940px){
 /* パソコンのみQRを大きく。上下の8pxを詰めてブックマーク／共有ボタンと隙間ゼロで接する
    正方形にする。スマホ側（〜939px）は現状のまま */
 .qrcol{gap:0}
 .qr img{width:200px}
 .wrap{max-width:1180px}
 .items{grid-template-columns:repeat(3,1fr)}
 .pks{grid-template-columns:repeat(4,1fr)}
 .item:hover{background:var(--tint);border-color:var(--accent)}
 .item:hover .t{text-decoration-color:var(--accent)}
 .pk:hover img{border-color:var(--accent)}
 .back:hover{background:var(--tint);border-color:var(--accent)}
 .banner:hover{background:var(--ltblue2)}
 .masc{width:250px}
}
@media(min-width:1280px){
 .wrap{max-width:1320px}
 .items{grid-template-columns:repeat(4,1fr)}
 .pks{grid-template-columns:repeat(5,1fr)}
 .pks.pksfirst{grid-template-columns:repeat(6,1fr)}
}
/* PC（マウスがある画面）：文字だけ並べて、乗せるとフワッと出す（画面中央に固定し、絶対にはみ出さない） */
@media (hover:hover) and (pointer:fine) and (min-width:700px){
 .banner .pop,.ilink .pop,.pk .pop{display:block;position:fixed;left:50%;top:50%;
  width:min(720px,66vw,116vh);aspect-ratio:16/9;border-radius:6px;border:1px solid var(--line);
  background:#fff center/cover no-repeat;box-shadow:0 20px 60px rgba(10,18,28,.45);
  opacity:0;transform:translate(-50%,-50%) scale(.96);
  transition:opacity .18s ease,transform .18s ease;pointer-events:none;z-index:20}
 .banner.popshow .pop,.ilink.popshow .pop,.pk.popshow .pop{background-image:var(--th);opacity:1;transform:translate(-50%,-50%) scale(1)}
 .ilink:hover{text-decoration:underline;text-underline-offset:3px}
 .rows{display:grid;grid-template-columns:repeat(2,1fr);column-gap:36px;row-gap:4px}
 .row{padding:18px 4px;border-bottom:2px solid var(--line)}
 .row .thumb{display:none}
 .row .ttl{width:100%;font-size:34px;line-height:1.45;font-weight:700}
 .row .ttl .ttlx{-webkit-line-clamp:6}
 .row .ttl .reflink{display:inline-block;margin-top:8px}
 .row .pop{display:block;position:fixed;left:50%;top:50%;
  width:min(720px,66vw,116vh);aspect-ratio:16/9;border-radius:6px;border:1px solid var(--line);
  background:#fff center/cover no-repeat;box-shadow:0 20px 60px rgba(10,18,28,.45);
  opacity:0;transform:translate(-50%,-50%) scale(.96);
  transition:opacity .18s ease,transform .18s ease;pointer-events:none;z-index:20}
 .row.popshow .pop{background-image:var(--th);opacity:1;transform:translate(-50%,-50%) scale(1)}
 /* プレビューの真下に動画タイトル。紺地に白（コントラスト比16.5:1）、本文と同じ
    ゴシックで、大きさは「脳アハ！」と同じ。題名が長い画面外へ出ないよう2行で止める */
 .pk .pop::after,.row .pop::after{content:attr(data-t);position:absolute;left:0;right:0;top:100%;
  padding:12px 18px;background:#0B1F3B;color:#fff;font-family:inherit;
  font-size:clamp(34px,10vw,54px);line-height:1.25;font-weight:700;text-align:left;
  border-radius:0 0 6px 6px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
 /* 題名のぶんだけ下へ伸びるので、プレビュー全体をやや上寄せにして画面内に収める */
 .pk .pop,.row .pop{top:44%}
 .row:hover .ttl{text-decoration:underline;text-underline-offset:5px;text-decoration-color:var(--accent)}
}
@media(min-width:1600px) and (hover:hover) and (pointer:fine){
 .rows{grid-template-columns:repeat(3,1fr)}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}

/* ===== 以下、index.html に直接入れていた修正を build.py に移植 ===== */
/* QR下の🔗を消す。a[target="_blank"]::after と詳細度が同値のため後ろに置いて後勝ちさせる */
a.qr::after{content:none}
/* スマホのカードタイトルは最大4行 */
@media(max-width:939.98px){.pk p{-webkit-line-clamp:5;text-overflow:ellipsis}}
/* 末尾4ブロック：スマホ2x2 / PC1x4 */
@media(max-width:699.98px){.pks.endgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(min-width:700px){.pks.endgrid{grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.4fr) minmax(0,1.4fr)}.pks.endgrid .masc{width:100%;max-width:250px}}
@media(max-width:939.98px){.pks.endgrid .item{padding:20px 10px 12px}.pks.endgrid .item .t{font-size:17px}.pks.endgrid .item .pm{font-size:17px}.pks.endgrid .item .blklabel{font-size:14px;left:10px;top:-11px}.pks.endgrid .row1{gap:6px}}
/* 神回★エリア：スマホ左右2列＋説明文 / PC3列 */
/* 「＋を押すと開きます」の案内。口ぐせの帯と神回★のあいだに、行いっぱいで置く。
   配色は神回★のボックスと同じ薄緑 */
.shinkai-description{display:block;margin:0;padding:12px 14px;font-size:16px;line-height:1.5;
 color:#333;background:#E9F5EA;border:1px solid var(--greenline);border-radius:8px;
 word-break:break-word}
.shinkai-description strong{color:var(--blue);font-weight:700}
/* 説明文が抜けたので、スマホでは「量産のきっかけは、戦争の話。」を右半分ではなく1列で大きく出す */
@media(max-width:939.98px){.items.shinkai-wrapper{grid-template-columns:1fr;gap:8px}.items.shinkai-wrapper>.pkcap{margin:0}}
/* 「量産のきっかけは、戦争の話。」の真上に出すイチオシ表示。スマホ専用。
   ⭐️は絵文字なので朱色を継がせず、そのままの色で出す */
.oshi{display:block;font-size:17px;font-weight:800;letter-spacing:.06em;line-height:1.3;
 color:#D6350F}   /* 白地とのコントラスト比4.80:1 */
.oshistar{color:initial}
/* パソコンは .warpc 側にだけ出す。見出しの直後に続けて置くので inline にする */
.warpc .oshi{display:inline;margin-left:.45em;white-space:nowrap}
/* 青帯：スマホのみ上下余白を半分・文字を拡大 */
@media(max-width:939.98px){.say{padding:15px 22px;font-size:clamp(25px,6.4vw,34px);line-height:1.4}}
/* 自己紹介・終わりリンクの下線を消す */
.selfline>a,.owariend>a{text-decoration:none}

/* ===== 今回の4点 ===== */
/* 修正1 カテゴリ説明文：スマホのみ .thanks と同じ19pxで黒。神回★(.solo)は対象外 */
@media(max-width:939.98px){.item .d{font-size:19px;color:#000}}
/* 修正2 ＋記号：カテゴリ名26pxに対しスマホは同寸、PCはやや大きく。行高は .t が決めるため変化しない */
@media(max-width:939.98px){.item .pm{font-size:26px}}
@media(min-width:940px){.item .pm{font-size:30px}}
/* 修正3 展開中ヘッダー：薄緑。閉じると[open]が外れて元のベージュへ自動で戻る */
details.item[open]>summary{background:#E9F5EA;border-bottom-color:#276B3B}
details.item[open]>summary .t{color:#276B3B}
details.item[open] .closelbl{background:#276B3B}
/* 外部リンクの一覧：スマホ・パソコンとも最下部に出す。
   バッジを押したときの挙動だけが端末で異なる（スマホ＝一覧へ移動／PC＝外部リンクを開く）。
   「逆戻」ボタンはどちらの端末でもサムネイルへ戻すアンカー元。 */
/* ♫／＠の2つはカテゴリと同じ「＋」開閉式。上段バナー行の2枠目・3枠目に入る */
.musiclist{position:relative;min-width:0;padding:14px 10px;background:#FCE4EC;
 border:1px solid #E6A3C0;border-radius:8px}
details.musiclist[open]{grid-column:1/-1;background:#FFF;border-color:var(--line)}
/* 一覧を開くと数百行になる。ヒーローの横並びのままでは のりこめ画像・QR と
   高さが噛み合わないため、開いている間だけ縦積みにして全幅で読ませる */
.ahawrap:has(.musiclist[open]){display:block}
.ahawrap:has(.musiclist[open]) .leadcol{max-width:none;width:100%}
.ahawrap:has(.musiclist[open]) .noripc{display:none}
.musiclist>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:6px;min-height:44px}
.musiclist>summary::-webkit-details-marker{display:none}
.musiclist>summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:4px}
.musiclist .pm{flex:0 0 auto;font-size:22px;font-weight:700;line-height:1;color:#A32063;
 transition:transform .15s ease}
details.musiclist[open] .pm{transform:rotate(45deg)}
.musiclist .mlh{flex:1;min-width:0;font-size:17px;font-weight:800;letter-spacing:0;color:#A32063;white-space:nowrap}
.musiclist .closelbl{display:none}
details.musiclist[open] .closelbl{display:inline-block;flex:0 0 auto;margin-left:auto;
 font-size:17px;font-weight:800;color:#fff;background:#A32063;padding:6px 14px;
 border-radius:20px;white-space:nowrap}
/* 開いている間、見出しを閉じるボタンとして画面上端に貼り付ける（一覧が長いため） */
details.musiclist[open]>summary{position:sticky;top:0;z-index:5;margin:-14px -10px 0;
 padding:14px 16px;background:#FCE4EC;border-bottom:2px solid #A32063;
 box-shadow:0 3px 10px rgba(20,35,50,.14)}
.musiclist .mlbody{margin:14px 0 0;padding-top:14px;border-top:1px solid var(--line2)}
@media(max-width:939.98px){
 .musiclist{padding:10px 7px}
 details.musiclist[open]>summary{margin:-10px -7px 0;padding:10px 8px}
 .banner{padding:10px 5px}
 .musiclist>summary{gap:3px}
 .musiclist .pm{font-size:16px}
 .musiclist .mlh{font-size:13px}
 details.musiclist[open] .closelbl{font-size:14px;padding:5px 10px}
}
/* 行番号は出さない（左端をボタンに揃える） */
.musiclist ol{margin:0;padding:0;list-style:none}
.musiclist li{margin:0 0 10px}
/* 見出しの♫は .refbadge と同じ #FF0000 / #fff。絵文字ではCSSのcolorが効かないため記号+丸で再現 */
.musiclist .mlbadge{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;min-width:28px;
 height:28px;padding:0 5px;border-radius:14px;background:#FF0000;color:#fff;font-size:19px;
 font-weight:700;line-height:1;box-shadow:0 1px 4px rgba(0,0,0,.35)}
@media(max-width:939.98px){.musiclist .mlbadge{min-width:22px;height:22px;padding:0 4px;font-size:15px}}
/* 1行を 戻る 1/8 ｜ タイトル 6/8 ｜ LM 1/8 の3分割にする（♫一覧・＠一覧で共通） */
.music-item{display:grid;grid-template-columns:1fr 6fr 1fr;align-items:center;gap:10px}
.music-item .ml-title{min-width:0;font-size:15px;line-height:1.5;color:var(--sub);
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-underline-offset:3px}
.music-item .ml-title::after{content:none}
/* 左右のボタンは矢羽根型。色は一覧ではなく「向き」で決まる（左＝ダーク青／右＝濃い緑）ので、
   ♫一覧と＠一覧のどちらでも同じ配色になる */
.music-item .backlink,.music-item .lmlink{min-width:0;display:flex;align-items:center;
 justify-content:center;color:#fff;font-size:12px;font-weight:700;
 line-height:1;padding:8px 1px;text-decoration:none;white-space:nowrap}
.music-item .backlink{background:var(--blue)}
.music-item .lmlink{background:#276B3B}   /* 白文字とのコントラスト比6.46:1 */
/* 左向き矢羽根：左端が尖り、右端がV字に凹む */
.music-item .backlink{clip-path:polygon(22% 0,100% 0,78% 50%,100% 100%,22% 100%,0 50%)}
/* 右向き矢羽根：左端がV字に凹み、右端が尖る */
.music-item .lmlink{clip-path:polygon(0 0,78% 0,100% 50%,78% 100%,0 100%,22% 50%)}
.music-item .backlink::after,.music-item .lmlink::after{content:none}
/* アンカー到達時のハイライト：黒背景＋ごく薄いピンク文字。
   飛び先がひと目で分かるよう、その行だけ文字を5px大きくする（15→20px） */
.musiclist li:target{background:#000;color:#FFF0F5;border-radius:6px;padding:4px 6px;margin-left:-6px}
.musiclist li:target .ml-title{color:#FFF0F5;font-size:20px}
/* パソコンは1行が長くなりすぎるので、読める幅で止める */
@media(min-width:940px){
 .musiclist ol{max-width:760px}
 .music-item .ml-title{font-size:16px}
 .musiclist li:target .ml-title{font-size:21px}   /* 16→21px */
 .music-item .backlink,.music-item .lmlink{font-size:13px;padding:7px 4px}
}
/* サムネイルを押したときの拡大表示（スマネのみ）。行いっぱいに広げ、
   黒背景・白文字にして「視聴する」「戻る」を重ねる */
.zoomui{display:none}
@media(max-width:939.98px){
 .pks .pk.zoom{grid-column:1/-1;background:#0B1F3B;border-radius:8px;padding:6px}
 /* 拡大時のタイトル：紺地に白（コントラスト比16.5:1）。本文と同じゴシックで、
    大きさは「脳アハ！」と同じ。行数は制限せず、長い題名も最後まで出す */
 .pks .pk.zoom p{color:#fff;font-family:inherit;
  font-size:clamp(34px,10vw,54px);line-height:1.3;font-weight:700;
  display:block;overflow:visible;-webkit-line-clamp:none;text-overflow:clip}
 .pks .pk.zoom .thumb img{border-color:#0B1F3B}
 .pks .pk.zoom .clipicon{display:none}   /* 視聴するボタンと同じ隅にあるため */
 .pk.zoom .zoomui{display:block}
 /* 2つのボタンはサムネイルの下の隅へ。中身が隠れず、下のタイトルとも重ならない */
 .zwatch{position:absolute;right:6px;bottom:6px;z-index:5;
  display:inline-flex;flex-direction:column;align-items:center;justify-content:center;
  background:#D6350F;color:#fff;font-size:15px;font-weight:800;line-height:1.2;
  letter-spacing:.04em;padding:7px 9px;border-radius:0;
  box-shadow:0 2px 10px rgba(0,0,0,.6);cursor:pointer}
 .zback{position:absolute;left:6px;bottom:6px;z-index:5;
  display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;
  background:#276B3B;color:#fff;font-size:15px;font-weight:700;
  padding:6px 13px;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.6);cursor:pointer}
}
/* 神回★ボックスの薄緑：PC・スマホで同色にする */
/* 神回★はカテゴリ一覧の一員だが、お気に入りとして薄緑で見分けられるようにする。
   :nth-of-type(even) の縞より後に置き、詳細度も高いので確実に上書きされる */
.items>.item.solo,.items>.item.solo:nth-of-type(even){background:#E9F5EA;border-color:var(--greenline)}
.items>.item.solo:active{background:var(--tint)}
.items>.item.solo:hover{background:var(--tint);border-color:var(--accent)}
.items>.item.solo[open]{background:#FFF;border-color:var(--line)}
/* PC版「量産のきっかけ」：あらかじめセクションの右側へ。スマホでは出さない */
.warpc{display:none}
@media(min-width:940px){
 .note .noterow{display:flex;gap:24px;align-items:flex-start}
 .noterow .notecol{flex:1.5;min-width:0}
 .warpc{display:block;flex:1;min-width:0;background:var(--bg);border-radius:8px;padding:14px;margin:-14px}
 .warpc .pkcap{margin:0 0 8px;font-size:22px;line-height:1.4}
 .warpc .pk p{font-size:15px;line-height:1.5;-webkit-line-clamp:3}
 /* スマホ版はPCでは非表示にし、神回★ブロックの上下余白も詰める */
 /* 神回★を一覧へ移したので、この枠に残るのはスマホ専用の3点だけ。まとめて隠す */
 .items.shinkai-wrapper{display:none}
}
.haibokuwrap{display:block}
.hblink.top{margin:0 0 6px}
.hblink{display:block;margin:6px 0 0;font-size:15px;line-height:1.5;color:var(--sub);text-decoration:underline;text-underline-offset:3px;overflow-wrap:anywhere}
/* 上位カテゴリの先頭だけ青バッジで強調する。スマホ・パソコン共通 */
.item .blklabel.grouptop,.item:nth-of-type(even) .blklabel.grouptop{
 background:#2563EB;color:#fff;font-size:21px;letter-spacing:.08em;
 padding:3px 12px;border-radius:6px;top:-18px;left:10px;
 scroll-margin-top:16px}
/* 「デバイス・デジタル生活」のような長い名前だけ、右上の「戻る」に重ならない大きさへ落とす。
   上の指定より後ろに置き、詳細度も1つ高くして確実に上書きする */
.item .blklabel.grouptop.longname{font-size:16px;line-height:1.2;white-space:normal}
@media(min-width:940px){.item .blklabel.grouptop.longname{font-size:14px}}
'''

HTML=f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>脳アハ！</title>
<meta name="description" content="必ずみつかる、脳アハ！ 新たな気づきに出会えますように。">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#125A93">
<link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<style>{CSS}</style></head><body>
<div class="wrap" id="top">
<div class="hero">
<div class="greet"><p class="mins">1つ視聴に25分。🥴</p>
<div class="thankswrap"><p class="thanks">大切なお時間をもって<span class="ponly">、</span>ご視聴いただく方、<span class="ponly">ありがとうございます。</span></p><img class="stk arig" src="{IMGS['arigatou']}" alt="" width="200" height="151" decoding="async" fetchpriority="high"><img class="stk nana" src="{IMGS['nanananana']}" alt="" width="180" height="150" decoding="async"></div></div>
<div class="ahatop">
<img class="stk arig ahaicon" src="{IMGS['arigatou']}" alt="" width="200" height="151" decoding="async" fetchpriority="high">
<p class="aha"><small>必ずみつかる、</small>脳アハ！</p>
<img class="stk masc norimobile" src="{IMGS['norikome']}" alt="のりこめゲームスタート！" width="274" height="252" decoding="async" fetchpriority="high">
</div>
{GNAV}
<div class="ahawrap">
<img class="stk masc noripc" src="{IMGS['norikome']}" alt="のりこめゲームスタート！" width="274" height="252" decoding="async" fetchpriority="high">
<div class="leadcol">
<div class="leadrow">
<p class="lead">年代や性別・日々の環境・経験・人生フェーズに応じた、新たな気づきに出会ってくださいますと嬉しいです。</p>
<img class="stk nana leadicon" src="{IMGS['nanananana']}" alt="" width="180" height="150" loading="lazy" decoding="async">
</div>
<div class="bannerrow top">
<a class="banner" href="{wu(ID_ICHIMI,0)}" target="_blank" rel="noopener" style="--th:url({tnhq(ID_ICHIMI)})">
<span class="lbl">{TXT_ICHIMI_HTML}</span>
<span class="pop" aria-hidden="true"></span></a>
<!--MUSICLIST-->
</div>
<div class="findbox">
<p class="findeg">「ドラえもん」「おかあさん」「お笑い」「エガちゃん」「落語」「発達障害」「LINE」「実験」「経済圏」「なぜ」「ゲーム」「柳川」「ネットワーク」「男女」「仕事」「時代」「ダジャレ」「歌詞」</p>
<div class="findrow">
<input type="search" id="findq" class="findinput" aria-label="ページ内をさがす" placeholder="ちびまる" autocomplete="off" enterkeyhint="search">
<button type="button" class="findbtn" id="findbtn">さがす</button>
</div>
<p class="findeg under">「宗教」「生きる」「死ぬ」「地球」「星」「Notebook」「数学」「トランプ」「マクドナルド」「トイレ」「車」「クーラー」「スマホ」「ゴミ」「教育」「医療」「リハビリ」など</p>
<p class="findmsg" id="findmsg" role="status" aria-live="polite"></p>
<div class="findlist" id="findlist" hidden></div>
</div>
</div>
<div class="qrbox"><div class="qrcol">
<button type="button" class="addhome" id="addhomeBtn">🔖 ブックマーク</button>
<a class="qr" href="{SHORT_URL_HREF}" target="_blank" rel="noopener"><img src="img/qr_github.webp" alt="" width="396" height="396" decoding="async" fetchpriority="high"></a>
<button type="button" class="sharebtn" id="shareBtn">
<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L7.04 9.81C6.5 9.31 5.79 9 5 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.91 2.92 2.91 1.61 0 2.92-1.3 2.92-2.91s-1.31-2.92-2.92-2.92z"/></svg>
共有
</button>
</div>{CHIKO}</div>
</div>
</div>
<div class="modal-overlay" id="addhomeModal" hidden>
<div class="modal-box">
<p id="addhomeModalText"></p>
<button type="button" class="modal-close" id="addhomeModalClose">閉じる</button>
</div>
</div>
<div class="note">
<div class="noterow">
<div class="notecol">
<h3>［ あらかじめ ］</h3>
ＡＩは音読み・訓読みが苦手です。{ilink(LINK_IKKI,'hpo7e3-MewI','五木寛之氏')}を「ごきかんゆき」<span class="red">(失礼！)</span>、と読んだりします。<br>
人もAIも、人名・地名は難しいですね。<span class="hl">「温かく」聞き流しを。</span>
<div class="sep pccenter">
動画「前／中／後」３回の、耳痛いハーモニカ演奏は、<a class="ilink" href="#techdefeat-top"><strong>意図があって</strong></a>挿入しています。<br>
<span class="red">倍速や早送りなど推奨</span>(⇒<a href="{LINK_STAR}" target="_blank" rel="noopener">★</a>)　<span class="red">どうぞ！早送りくださいませ。</span>
</div>
</div>
<div class="warpc"><p class="pkcap">{html.escape(CAP_WAR)}<span class="oshi">イチオシ<span class="oshistar">⭐️</span></span></p>{pkcard(V[ID_WAR]["watch_url"],V[ID_WAR]["thumbnail_url"],V[ID_WAR]["title"])}</div>
</div>
</div>
<div class="pkwrap"><h2>まずはこのあたりから</h2>{first}
<div class="items shinkai-wrapper"><p class="pkcap"><span class="oshi">イチオシ<span class="oshistar">⭐️</span></span>{html.escape(CAP_WAR)}</p>{pkcard(V[ID_WAR]["watch_url"],V[ID_WAR]["thumbnail_url"],V[ID_WAR]["title"])}</div>
</div>
{idx}
<div class="endwrap">
<div class="pks endgrid">
<div class="haibokuwrap"><a class="hblink top" id="techdefeat-top" href="{wu(ID_INTENT)}" target="_blank" rel="noopener">{html.escape(cut(V[ID_INTENT]["title"]))}</a>{pkcard(wu(ID_HAIBOKU),IMGS['haiboku'],TXT_HAIBOKU)}<a class="hblink" href="{wu(ID_FINAL)}" target="_blank" rel="noopener">{html.escape(TXT_FINAL)}</a></div>
<div class="stkitem endkome"><img class="stk masc" src="{IMGS['kome']}" alt="" width="266" height="254" loading="lazy" decoding="async"></div>
{NEWCAT_BOX}
{HARMONICA_BOXES}
</div>
<p class="selfline">{ilink(wu(ID_SELFINTRO),ID_SELFINTRO,html.escape(TXT_SELFINTRO))}</p>
<p class="techdesc">{vlink(ID_KEITORA,'軽トラ４ナンバー')}ダイハツハイゼットのような「{vlink(ID_CFRZ6,'CF-RZ6')}（{vlink(ID_XUBUNTU,'xubuntu')}）」と、スズキ{vlink(ID_SWIFT,'2020スイフト')}（{vlink(ID_M1,'M1')}；{vlink(ID_A2337,'A2337')}；{vlink(ID_ASAHI,'AsahiLinuxFedoraKDEplasma')}）M1MacbookAirを使ってます。</p>
<p class="owariend">{ilink(wu(ID_OWARI),ID_OWARI,html.escape(TXT_OWARI))}</p>
</div>
<div class="tail"></div>
</div>
<script>
var SKIP_TOGGLE_SCROLL_UNTIL=0;
/* サムネイル拡大のしくみ。ボタンは1組だけ作り、拡大したカードへ差し替えて使い回す。
   カードは <a> なので中に <button> は置けない。span を role=button として扱う */
var ZOOM=null,ZOOMORIGIN=null,ZUI=null;
function SP(){{return window.matchMedia('(max-width:939.98px)').matches;}}
function zoomUI(){{
 if(!ZUI){{
  ZUI=document.createElement('span');
  ZUI.className='zoomui';
  ZUI.innerHTML='<span class="zwatch" role="button" tabindex="0">\u8996\u8074<br>\u3059\u308b</span>'+
                '<span class="zback" role="button" tabindex="0">\u623b\u308b</span>';
 }}
 return ZUI;
}}
function unzoom(){{
 if(!ZOOM)return;
 ZOOM.classList.remove('zoom');
 if(ZUI&&ZUI.parentNode)ZUI.parentNode.removeChild(ZUI);
 ZOOM=null;ZOOMORIGIN=null;
}}
function zoomCard(card,origin){{
 unzoom();
 ZOOM=card;ZOOMORIGIN=origin||null;
 card.classList.add('zoom');
 (card.querySelector('.thumb')||card).appendChild(zoomUI());
 /* 行いっぱいに広がってから位置を測るため2フレーム待つ。
    題名が長く画面より高くなる場合は、中央寄せだと上下が切れるので上端に合わせる */
 requestAnimationFrame(function(){{
  requestAnimationFrame(function(){{
   var tall=card.getBoundingClientRect().height>window.innerHeight-16;
   card.scrollIntoView({{block:tall?'start':'center'}});
  }});
 }});
}}
document.addEventListener('toggle',function(e){{
 var d=e.target;
 if(d.tagName!=='DETAILS')return;
 if(Date.now()<SKIP_TOGGLE_SCROLL_UNTIL)return;   /* 「戻る」からの展開時は自前でスクロールする */
 if(d.open){{
  requestAnimationFrame(function(){{d.scrollIntoView({{behavior:'smooth',block:'start'}});}});
  return;
 }}
 requestAnimationFrame(function(){{
  if(d.classList.contains('solo')){{
   document.getElementById('top').scrollIntoView({{behavior:'smooth',block:'start'}});
   return;
  }}
  var el=d.previousElementSibling,band=null;
  while(el){{
   if(el.classList.contains('say')){{band=el;break;}}
   el=el.previousElementSibling;
  }}
  (band||d).scrollIntoView({{behavior:'smooth',block:'start'}});
 }});
}},true);
(function(){{
 var SHOW=2000,COOLDOWN=5000;
 function release(el){{
  if(el.classList.contains('popshow')){{el.classList.remove('popshow');el._hiddenAt=Date.now();}}
  clearTimeout(el._popTimer);
 }}
 function trigger(el){{
  var now=Date.now();
  if(el._hiddenAt&&now-el._hiddenAt<COOLDOWN)return;
  if(el.classList.contains('popshow'))return;
  if(!el.style.getPropertyValue('--th')){{
   var img=el.querySelector('img');
   if(img)el.style.setProperty('--th','url("'+img.src+'")');
  }}
  el.classList.add('popshow');
  clearTimeout(el._popTimer);
  el._popTimer=setTimeout(function(){{release(el);}},SHOW);
 }}
 document.querySelectorAll('.row,.banner,.ilink,.pk').forEach(function(el){{
  el.addEventListener('mouseenter',function(){{trigger(el);}});
  el.addEventListener('mouseleave',function(){{release(el);}});
  el.addEventListener('focus',function(){{trigger(el);}});
  el.addEventListener('blur',function(){{release(el);}});
 }});
}})();
document.addEventListener('click',function(e){{
 /* 上位カテゴリの「戻る」。summary の中にあるので、そのままだと開閉が起きる。
    既定動作を止めてページ最上部（矢羽一覧）へ戻す */
 var gb=e.target.closest('.gback');
 if(gb){{
  e.preventDefault();
  document.getElementById('top').scrollIntoView({{block:'start'}});
  return;
 }}
 /* 「戻る」：対象が閉じた details の中にあると、ブラウザ既定のハッシュ移動では
    自動展開で高さが変わり、着地位置が大きくずれる。開いてから自前で移動する */
 var bk=e.target.closest('.backlink');
 if(bk){{
  var id=bk.getAttribute('href').slice(1);
  var el=document.getElementById(id);
  if(el){{
   e.preventDefault();
   var d=el.closest('details');
   if(d&&!d.open){{SKIP_TOGGLE_SCROLL_UNTIL=Date.now()+600;d.open=true;}}
   requestAnimationFrame(function(){{
    location.hash=id;
    el.scrollIntoView({{block:'center'}});
   }});
  }}
  return;
 }}
 /* サムネイルの拡大表示（スマホのみ）。
    ・「まずはこのあたりから」の18枚 … 同じ動画がカテゴリ一覧のどこに居るかへ飛んで拡大。
      「戻る」は元の18枚の位置まで返す
    ・カテゴリを展開した3列のカード … その場で拡大。「戻る」は3列に戻すだけ
    バッジ（.reflink）の上を押したときは従来どおりバッジの動作を優先する */
 if(SP()){{
  var zb=e.target.closest('.zback');
  if(zb){{
   e.preventDefault();
   var org=ZOOMORIGIN; unzoom();
   if(org){{
    var oe=document.getElementById(org);
    if(oe)oe.scrollIntoView({{block:'center'}});
   }}
   return;
  }}
  if(e.target.closest('.zwatch')){{
   e.preventDefault();
   if(ZOOM)window.open(ZOOM.href,'_blank','noopener');
   return;
  }}
  if(!e.target.closest('.reflink')){{
   var pk=e.target.closest('.pk');
   if(pk){{
    if(pk===ZOOM){{                      /* 拡大中のカード自体を押したら再生 */
     e.preventDefault();
     window.open(pk.href,'_blank','noopener');
     return;
    }}
    if(pk.dataset.jump){{
     var tg=document.getElementById(pk.dataset.jump);
     if(tg){{
      e.preventDefault();
      var dd=tg.parentElement?tg.parentElement.closest('details'):null;
      while(dd){{
       if(!dd.open){{SKIP_TOGGLE_SCROLL_UNTIL=Date.now()+800;dd.open=true;}}
       dd=dd.parentElement?dd.parentElement.closest('details'):null;
      }}
      zoomCard(tg,pk.id||null);
      return;
     }}
    }} else if(pk.closest('.catbody')){{   /* 展開したカテゴリの中のカード */
     e.preventDefault();
     zoomCard(pk,null);
     return;
    }}
   }}
  }}
 }}
 var t=e.target.closest('.reflink');
 if(!t)return;
 e.preventDefault();
 e.stopPropagation();
 if(t.dataset.anchor&&window.matchMedia('(max-width:939.98px)').matches){{
  var el=document.getElementById(t.dataset.anchor);
  if(el){{
   /* 飛び先の一覧は details で畳まれている。閉じたままだと高さ0で座標が取れないため先に開く */
   var dd=el.parentElement?el.parentElement.closest('details'):null;
   while(dd){{
    if(!dd.open){{SKIP_TOGGLE_SCROLL_UNTIL=Date.now()+600;dd.open=true;}}
    dd=dd.parentElement?dd.parentElement.closest('details'):null;
   }}
   requestAnimationFrame(function(){{
    location.hash=t.dataset.anchor;      /* :target のハイライトを効かせる */
    el.scrollIntoView({{block:'center'}});  /* 既定は瞬間移動。画面の上下中央へ */
   }});
  }}
  return;
 }}
 window.open(t.dataset.url,'_blank','noopener');
}});
(function(){{
 /* ページ内検索。1502本の題名（カード .pk p ／ 行 .row .ttlx）から部分一致で絞り込む。
    カタカナ・ひらがな・全角英数の違いを吸収するため、双方を正規化してから照合する */
 var q=document.getElementById('findq'),btn=document.getElementById('findbtn');
 var msg=document.getElementById('findmsg'),list=document.getElementById('findlist');
 var MAX=60,idx=null;
 function norm(s){{
  return s.toLowerCase()
   .replace(/[\uff21-\uff3a\uff41-\uff5a\uff10-\uff19]/g,function(c){{
     return String.fromCharCode(c.charCodeAt(0)-0xFEE0);}})
   .replace(/[\u30a1-\u30f6]/g,function(c){{
     return String.fromCharCode(c.charCodeAt(0)-0x60);}})   /* カタカナ→ひらがな */
   .replace(/[\s\u3000\u30fb]/g,'');   /* \u7a7a\u767d\u30fb\u5168\u89d2\u7a7a\u767d\u30fb\u4e2d\u9ed2\u306f\u7121\u8996\u3059\u308b */
 }}
 function build(){{
  idx=[];
  document.querySelectorAll('.pk p,.row .ttlx').forEach(function(e){{
   var card=e.closest('.pk')||e.closest('.row');
   if(!card)return;
   var d=card.closest('details.item');
   var cat=d?(d.querySelector('summary .t')||{{}}).textContent||'':'';
   idx.push({{el:card,t:e.textContent,k:norm(e.textContent),cat:cat}});
  }});
 }}
 function esc(s){{return s.replace(/[&<>"]/g,function(c){{
   return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
 function jump(card){{
  var d=card.closest('details');
  while(d){{
   if(!d.open){{SKIP_TOGGLE_SCROLL_UNTIL=Date.now()+600;d.open=true;}}
   d=d.parentElement?d.parentElement.closest('details'):null;
  }}
  requestAnimationFrame(function(){{
   card.scrollIntoView({{block:'center'}});
   card.classList.add('findhit');
   setTimeout(function(){{card.classList.remove('findhit');}},2600);
  }});
 }}
 function run(){{
  if(!idx)build();
  var raw=q.value.trim(),k=norm(raw);
  list.innerHTML='';
  if(!k){{list.hidden=true;msg.textContent='';return;}}
  var hits=[];
  for(var i=0;i<idx.length&&hits.length<MAX;i++){{
   if(idx[i].k.indexOf(k)>=0)hits.push(idx[i]);
  }}
  var total=0;
  for(var j=0;j<idx.length;j++)if(idx[j].k.indexOf(k)>=0)total++;
  if(!total){{
   list.hidden=true;
   msg.textContent='「'+raw+'」は見つかりませんでした。';
   return;
  }}
  msg.textContent=total+'件'+(total>MAX?'（上位'+MAX+'件を表示）':'');
  hits.forEach(function(h){{
   var b=document.createElement('button');
   b.type='button';b.className='findhitbtn';
   /* 一致部分は正規化後の位置で数えるが、元の題名とは文字数が一致するため流用できる */
   var p=h.k.indexOf(k);
   b.innerHTML=esc(h.t.slice(0,p))+'<mark>'+esc(h.t.substr(p,k.length))+'</mark>'+
               esc(h.t.slice(p+k.length))+
               (h.cat?'<span class="findcat">'+esc(h.cat)+'</span>':'');
   b.addEventListener('click',function(){{jump(h.el);}});
   list.appendChild(b);
  }});
  list.hidden=false;
  /* スマホは結果が画面外に出やすいので、入力欄を最上部に寄せて一覧を広く見せる */
  if(SP())document.querySelector('.findrow').scrollIntoView({{block:'start'}});
 }}
 var timer=null;
 q.addEventListener('input',function(){{clearTimeout(timer);timer=setTimeout(run,180);}});
 q.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();run();}}}});
 btn.addEventListener('click',run);
}})();
if('serviceWorker' in navigator){{
 window.addEventListener('load',function(){{navigator.serviceWorker.register('sw.js');}});
}}
(function(){{
 var modal=document.getElementById('addhomeModal');
 var modalText=document.getElementById('addhomeModalText');
 var modalClose=document.getElementById('addhomeModalClose');
 function showModal(html){{modalText.innerHTML=html;modal.hidden=false;}}
 function hideModal(){{modal.hidden=true;}}
 modalClose.addEventListener('click',hideModal);
 modal.addEventListener('click',function(e){{if(e.target===modal)hideModal();}});

 var deferredPrompt=null;
 var btn=document.getElementById('addhomeBtn');
 window.addEventListener('beforeinstallprompt',function(e){{
  e.preventDefault();
  deferredPrompt=e;
 }});
 window.addEventListener('appinstalled',function(){{deferredPrompt=null;}});
 btn.addEventListener('click',function(){{
  if(deferredPrompt){{
   deferredPrompt.prompt();
   deferredPrompt.userChoice.finally(function(){{deferredPrompt=null;}});
   return;
  }}
  var ua=navigator.userAgent;
  var isIOS=/iPad|iPhone|iPod/.test(ua)&&!window.MSStream;
  if(isIOS){{
   showModal('Safariの共有ボタン<b>（□に↑）</b>をタップして、<br>「ホーム画面に追加」を選んでください。');
  }}else{{
   var isMac=/Mac/.test(navigator.platform)&&!isIOS;
   showModal((isMac?'<b>Cmd + D</b>':'<b>Ctrl + D</b>')+' でブックマークできます。');
  }}
 }});

 var shareBtn=document.getElementById('shareBtn');
 shareBtn.addEventListener('click',function(){{
  if(navigator.share){{
   navigator.share({{title:document.title,url:location.href}}).catch(function(){{}});
   return;
  }}
  if(navigator.clipboard&&navigator.clipboard.writeText){{
   navigator.clipboard.writeText(location.href).then(function(){{
    showModal('リンクをコピーしました。');
   }}).catch(function(){{
    showModal('コピーできませんでした。<br>アドレスバーのURLをコピーしてください。');
   }});
  }}else{{
   showModal('コピーできませんでした。<br>アドレスバーのURLをコピーしてください。');
  }}
 }});
}})();
</script>
</body></html>'''
def _minify_css(css):
    css=re.sub(r'/\*.*?\*/','',css,flags=re.S)
    css=re.sub(r'\s+',' ',css)
    css=re.sub(r'\s*([{}:;,])\s*',r'\1',css)
    css=re.sub(r';}','}',css)
    return css.strip()

def _minify_js(js):
    lines=[l.strip() for l in js.split('\n')]
    return ' '.join(l for l in lines if l)

def _minify_html(html_str):
    def sub(m):
        tag=m.group(1)
        body=m.group(2)
        fn=_minify_css if tag=='style' else _minify_js
        return f'<{tag}>{fn(body)}</{tag}>'
    parts=re.split(r'(<style>.*?</style>|<script>.*?</script>)',html_str,flags=re.S)
    out=[]
    for p in parts:
        if p.startswith('<style>') or p.startswith('<script>'):
            out.append(re.sub(r'<(style|script)>(.*)</\1>',sub,p,flags=re.S))
        else:
            out.append(re.sub(r'>\s+<','><',p))
    return ''.join(out)


def build_ref_lists(doc):
    """組み上がったHTMLを文書順に1回だけ走査し、♫/＠バッジへ
    music-N / thumb-N（♫）と video-N / vthumb-N（＠）を1対1で採番する。
    バッジは .pk カード内にのみ置かれる。
    採番は必ず最終的な文書順で行うため、ここで後処理している
    （テンプレート内の各パーツは文書順とは異なる順で組み立てられているため）。"""
    SPEC={
     '\u266b':{'cls':'musiclist','head':'\u306e\u97f3\u697d','li':'music','th':'thumb'},
     '\uff20':{'cls':'musiclist videolist','head':'\u306e\u52d5\u753b','li':'video','th':'vthumb'},
    }
    out=[]; items={k:[] for k in SPEC}; cnt={k:0 for k in SPEC}; pos=0
    for b in re.finditer(r'<span class="reflink refbadge([^"]*)" data-url="([^"]+)">(.)</span>', doc):
        sym=b.group(3)
        if sym not in SPEC:
            continue
        # バッジを囲む .pk カードがあるか。.row 内（ハーモニカ等）は一覧の対象外
        ts=doc.rfind('<a class="pk', 0, b.start())
        te=doc.find('>', ts)+1 if ts!=-1 else -1
        inside = ts!=-1 and doc.find('</a>', te) > b.start()
        if not inside:
            continue
        sp=SPEC[sym]; cnt[sym]+=1; n=cnt[sym]
        url=html.unescape(b.group(2))
        vid=re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_\-]{11})', url)
        vid=vid.group(1) if vid else ''
        card=doc[te:doc.find('</a>', te)]
        lt=re.search(r'<p>(.*?)</p>', card, re.S)
        local=html.unescape(lt.group(1)) if lt else ''
        # カードのhrefがその動画の自チャンネルURL。外部音源リンク(data-url)とは別物
        own=html.unescape(re.search(r'href="([^"]*)"', doc[ts:te]).group(1))
        ovid=re.search(r'v=([A-Za-z0-9_\-]{11})', own)
        if ovid and ovid.group(1) in HARMONICA_IDS:
            own=''   # ハーモニカ演奏系はNotebookLM制作ではないため対象外
        # 開始タグに id="thumb-N"、バッジに data-anchor="music-N" を注入
        out.append(doc[pos:ts])
        out.append(doc[ts:te-1]+f' id="{sp["th"]}-{n}">')
        out.append(doc[te:b.start()])
        out.append(b.group(0).replace(' data-url=',
                   f' data-anchor="{sp["li"]}-{n}" data-url=', 1))
        pos=b.end()
        title=(OEMBED_CACHE.get(vid) or {}).get('title') or local   # 取得失敗時はローカル題名へ
        items[sym].append({'n':n,'url':b.group(2),'title':title,'own':own})
    out.append(doc[pos:])
    doc=''.join(out)

    # 旧・一気見バナーの♫8本を一覧の先頭へ。ページ内にサムネイル（戻り先）が無く、
    # 1502本のいずれにも対応しないので、矢羽は左右とも空欄にして題名リンクだけ残す。
    # 'n':None がその目印
    topmusic=[]
    for u,t in TOPREF:
        v=re.search(r'v=([A-Za-z0-9_\-]{11})',u).group(1)
        topmusic.append({'n':None,'url':html.escape(u),
                         'title':(OEMBED_CACHE.get(v) or {}).get('title') or t,'own':''})
    items['\u266b']=topmusic+items['\u266b']

    secs=''
    for sym,sp in SPEC.items():
        lis=''
        for i in items[sym]:
            title=(f'<a class="ml-title" href="{i["url"]}" target="_blank" rel="noopener">'
                   f'{html.escape(cut(i["title"]))}</a>')
            if i['n'] is None:
                # 矢羽なしの行。3分割は保ったまま両端を空セルにして、題名の左端を他の行と揃える
                lis+=(f'<li><div class="music-item">'
                      f'<span class="lmnone"></span>{title}<span class="lmnone"></span>'
                      f'</div></li>')
                continue
            # 右の枠：自チャンネル動画へのLMボタン。ハーモニカ演奏系の行は
            # 枠だけ残して空欄にする
            lm=(f'<a class="lmlink" href="{html.escape(i["own"])}" target="_blank" rel="noopener">'
                f'LM</a>') if i['own'] else '<span class="lmnone"></span>'
            lis+=(f'<li id="{sp["li"]}-{i["n"]}"><div class="music-item">'
                  f'<a class="backlink" href="#{sp["th"]}-{i["n"]}">\u623b</a>'
                  f'{title}{lm}</div></li>')
        # カテゴリと同じ details 開閉式。閉じている間は .bannerrow.top の3等分グリッドに並ぶ
        secs+=(f'<details class="{sp["cls"]}">'
               f'<summary><span class="pm" aria-hidden="true">\uff0b</span>'
               f'<span class="mlbadge">{sym}</span>'
               f'<span class="mlh">{sp["head"]}</span>'
               f'<span class="closelbl" aria-hidden="true">\u2191 \u3068\u3058\u308b</span></summary>'
               f'<div class="mlbody"><ol>{lis}</ol></div></details>')
    return doc.replace('<!--MUSICLIST-->', secs), {k:len(v) for k,v in items.items()}

HTML,_REF_N=build_ref_lists(HTML)

HTML=_minify_html(HTML)
open(OUT,'w').write(HTML)
print(f'{OUT} {os.path.getsize(OUT)/1024:.1f}KB / gzip {len(gzip.compress(HTML.encode()))/1024:.1f}KB')
print('一覧 '+' / '.join(f'{k}{v}件' for k,v in _REF_N.items()))
print(f'カテゴリ{len(C)} 動画{d["total_videos"]} 先頭{sum(len(i) for _,i in FIRST)}本 / オススメ{len(MORE)}本 / 神回{len(KAMI)}本 / 口ぐせ{len(PHRASES)}')
