#!/usr/bin/env python3
# aspiewho 動画目次サイト ジェネレーター v7
import json, html, os, gzip, sys, re
SRC = sys.argv[1] if len(sys.argv)>1 else '/mnt/user-data/outputs/aspiewho_1502_classified.json'
OUT = sys.argv[2] if len(sys.argv)>2 else '/mnt/user-data/outputs/index.html'

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

FIRST=[(None,['e_sYnb1CdAs','etxG4LU462U','1fg64F4OBnU','QrSTV7drbUo','KxMbR6po5wA','ARyDkAJ4FBQ'])]
ID_WAR='cEkx8UrBpAU'
CAP_WAR='量産のきっかけは、戦争の話。'
ID_HAIBOKU='NjBJJ3JSqag'
TXT_HAIBOKU='技術的敗北と再生の物語'
IMGS={n:f'img/{n}.webp' for n in ('norikome','chiko','nori','kome','haiboku')}
IMGS['arigatou']='img/arigatou_anim.webp'
MORE=['TCe2SvES2x4','2Zky_cifOmw','w3dKDFOc-8I','GNnv5kXhJJs','y7VptpwGrX0',
      '3D6P6cqT1X8','WRWJdmNTj8U','v-EOKlp8Vfk','lXz5Y8umPxY','SQIpV-Jcpl8','2GwZJScpJeA',
      'TfRZv5DW3Es']

# NotebookLM の口ぐせ（この順に、ページ全体へ均等に差し込む）
PHRASES=['学ぶことがだいすきなアナタ、本日もようこそ、このディープライブへ',
 'あの〜、ちょっと想像してみてほしいんですけど．．','まさにそこなんですよ','パラダイムシフト',
 'よーし、これらを紐解いていきましょう',
 'さいごあなたに、挑発的な思考のタネを投げかけて、この思考の旅を、、']

# 1504本のうち外に出した2本（入れ替わっていたら下の2行を交換）
ID_ICHIMI='uBtnbr0gu80'   # 1500タイトルを24分で一気見！
ID_OWARI ='76XZgkPmg2s'   # 終わり☆AI能力把握実験、脳内発散訓練、遺言】動画量産1500本
TXT_ICHIMI='1500タイトルを24分で一気見！'
TXT_OWARI='終わり☆AI能力把握実験、脳内発散訓練、遺言】動画量産1500本'
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

def best_cols(n,options):
    # 最終行の空きマスが最小の列数を選ぶ。同数なら列数が多い方を優先
    def empty(g): return (-n)%g
    return max(options,key=lambda g:(-empty(g),g))

def pkgrid(ids,extra='',cls=''):
    return f'<div class="pks{cls}">'+''.join(
     f'<a class="pk" href="{V[i]["watch_url"]}" target="_blank" rel="noopener">'
     f'<span class="thumb"><img src="{V[i]["thumbnail_url"]}" alt="" width="320" height="180" loading="lazy" decoding="async">{refbadge(i)}{CLIPICON}</span>'
     f'<p>{html.escape(V[i]["title"])}</p><span class="pop" aria-hidden="true"></span></a>' for i in ids)+extra+'</div>'

def pkcard(href,thumb,title,cls='',vid=None):
    return (f'<a class="pk{cls}" href="{href}" target="_blank" rel="noopener">'
            f'<span class="thumb"><img src="{thumb}" alt="" width="320" height="180" loading="lazy" decoding="async">{refbadge(vid) if vid else ""}{CLIPICON}</span>'
            f'<p>{html.escape(title)}</p><span class="pop" aria-hidden="true"></span></a>')

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
              f'<span class="pop" aria-hidden="true"></span></a>')
    return f'<div class="rows">{out}</div>'

# ピックアップ枠の重複防止：FIRST/MORE（最上部）と WAR・HAIBOKU・ハーモニカ移設組（末尾の専用カード）は
# それぞれ別枠で確定表示するので、神回★グリッドには二重に出さない
FIRST_IDS={i for _,ids in FIRST for i in ids}
BELOW_PRIORITY_IDS=set(MOVE_IDS)|{ID_WAR,ID_HAIBOKU}
KAMI=[v['video_id'] for _,cats in groups for c in cats for v in c['videos']
      if v['kamikai'] and v['video_id'] not in FIRST_IDS|set(MORE)|BELOW_PRIORITY_IDS]

CHIKO=('<img class="stk masc chikoimg" src="'+IMGS['chiko']+'" alt="" width="300" height="265" decoding="async" fetchpriority="high">')
first=''.join((f'<p class="pkcap">{html.escape(c)}</p>' if c else '')+
 pkgrid([x for x in i+MORE if x not in BELOW_PRIORITY_IDS],cls=' pksfirst') for c,i in FIRST)

TOTAL_CATS=sum(len(cats) for name,cats in groups if name!=tname)
NPHR=len(PHRASES)
SEG=24  # 4の倍数で行が割れず、さいごが最後尾固定でも末尾の区切りが大きくなりすぎない
THR={SEG*i:i for i in range(1,NPHR-1)}

def catbox(name,c,desc=True,grid=False,firstlabel=False):
    d=f'<span class="d">{html.escape(c["description"])}</span>' if desc else ''
    if grid:
        n=c['count']
        g=best_cols(n,(2,3)); pc=best_cols(n,(5,6))
        ids=[v['video_id'] for v in c['videos']]
        body=pkgrid(ids,cls=f' g{g} pc{pc}')
    else:
        body=rows(c['videos'])
    return (f'<details class="item" id="c{c["category_id"]}">'
     f'<summary><span class="blklabel{" grouptop" if firstlabel else ""}">{html.escape(name)}</span>'
     f'<span class="row1"><span class="pm" aria-hidden="true">＋</span>'
     f'<span class="t">{html.escape(c["name"])}</span>'
     f'<span class="closelbl" aria-hidden="true">↑ とじる</span></span>'
     f'{d}</summary>'
     f'<div class="catbody">{body}</div></details>')

HARMONICA_MERGED={'category_id':'harmonica','name':'ハーモニカ演奏とその歴史・調律',
 'videos':[v for x in tids for v in C[x]['videos']]}
HARMONICA_BOXES=catbox(tname,HARMONICA_MERGED,desc=False)
NEWCAT_BOX=catbox(NEWCAT_GROUP,NEWCAT,desc=False,grid=True)

gitems=[f'<p class="say full">{html.escape(PHRASES[0])}</p>']
n=0
for gi,(name,cats) in enumerate(groups):
    if name in (tname,NEWCAT_GROUP):
        continue
    for ci,c in enumerate(cats):
        gitems.append(catbox(name,c,grid=True,firstlabel=(ci==0)))
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
html{scroll-behavior:smooth}
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
 .ahatop{display:block}
 .ahatop .aha{text-align:center}
 .ahatop .norimobile{display:none}
 .ahawrap .noripc{display:block}
}
.ahawrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:20px;margin:16px 0 0}
.leadcol{flex:1 1 260px;min-width:220px;max-width:480px}
.stk{display:block;height:auto;flex:0 0 auto}
.arig{width:64px;margin-right:-4px}
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
.bannerrow.top{justify-content:flex-start;margin:14px 0 0}
.banner{display:inline-flex;align-items:center;min-height:44px;margin:0;padding:14px 20px;
background:var(--ltblue);border:1px solid var(--blue);border-radius:8px;text-decoration:none;position:relative}
.banner .pop{display:none}
.banner .lbl{font-size:24px;font-weight:800;letter-spacing:.04em;line-height:1.4;color:var(--blue)}
.banner i{display:block;font-style:normal;font-size:15px;font-weight:600;color:var(--blue);
letter-spacing:.12em;text-decoration:none;margin-top:4px}
@media(max-width:939.98px){
 .banner i{display:inline;margin-top:0;margin-left:6px}
}
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
.item.solo .d{color:var(--dim)}
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
 .masc{width:200px}
 .endgrid .endkome{grid-column:auto}
}
@media(min-width:940px){
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
@media(max-width:939.98px){.pk p{-webkit-line-clamp:4;text-overflow:ellipsis}}
/* 末尾4ブロック：スマホ2x2 / PC1x4 */
@media(max-width:699.98px){.pks.endgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(min-width:700px){.pks.endgrid{grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.4fr) minmax(0,1.4fr)}.pks.endgrid .masc{width:100%;max-width:250px}}
@media(max-width:939.98px){.pks.endgrid .item{padding:20px 10px 12px}.pks.endgrid .item .t{font-size:17px}.pks.endgrid .item .pm{font-size:17px}.pks.endgrid .item .blklabel{font-size:14px;left:10px;top:-11px}.pks.endgrid .row1{gap:6px}}
/* 神回★エリア：スマホ左右2列＋説明文 / PC3列 */
.shinkai-description{display:none}
@media(max-width:939.98px){.items.shinkai-wrapper{grid-template-columns:1fr 1fr;gap:12px}.shinkai-description{display:block;grid-area:1/1;font-size:16px;line-height:1.5;color:#333;margin:0;padding:12px;background:#E9F5EA;border:1px solid var(--greenline);border-radius:8px;word-break:break-word}.shinkai-description strong{color:var(--blue);font-weight:700}.items.shinkai-wrapper>.item.solo{grid-area:2/1;background:#E9F5EA;border-color:var(--greenline)}.items.shinkai-wrapper>.item.solo:active{background:var(--tint)}.items.shinkai-wrapper>.item.solo[open]{grid-column:1/-1;background:#FFF;border-color:var(--line)}.items.shinkai-wrapper>.pkcap{grid-area:1/2;margin:0;align-self:end}.items.shinkai-wrapper>.pk{grid-area:2/2}.items.shinkai-wrapper:has(>.item.solo[open]){grid-template-columns:1fr}.items.shinkai-wrapper:has(>.item.solo[open])>*{grid-area:auto}}
@media(min-width:940px){.items.shinkai-wrapper{grid-template-columns:repeat(3,minmax(0,1fr))}}
/* 青帯：スマホのみ上下余白を半分・文字を拡大 */
@media(max-width:939.98px){.say{padding:15px 22px;font-size:clamp(25px,6.4vw,34px);line-height:1.4}}
/* 自己紹介・終わりリンクの下線を消す */
.selfline>a,.owariend>a{text-decoration:none}

/* ===== 今回の4点 ===== */
/* 修正1 カテゴリ説明文：スマホのみ .thanks と同じ19pxで黒。神回★(.solo)は対象外 */
@media(max-width:939.98px){.item:not(.solo) .d{font-size:19px;color:#000}}
/* 修正2 ＋記号：カテゴリ名26pxに対しスマホは同寸、PCはやや大きく。行高は .t が決めるため変化しない */
@media(max-width:939.98px){.item .pm{font-size:26px}}
@media(min-width:940px){.item .pm{font-size:30px}}
/* 修正3 展開中ヘッダー：薄緑。閉じると[open]が外れて元のベージュへ自動で戻る */
details.item[open]>summary{background:#E9F5EA;border-bottom-color:#276B3B}
details.item[open]>summary .t{color:#276B3B}
details.item[open] .closelbl{background:#276B3B}
/* 修正4 上位カテゴリ 連続先頭の強調：スマホのみ。PCには一切効かせない */
@media(max-width:939.98px){
 .item .blklabel.grouptop,.item:nth-of-type(even) .blklabel.grouptop{
  background:#1E5E34;color:#fff;font-size:21px;letter-spacing:.08em;
  padding:3px 12px;border-radius:6px;top:-18px;left:10px}
}
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
<p class="mins">1つ視聴に25分。🥴</p>
<div class="thankswrap"><p class="thanks">大切な<a href="{LINK_TIME}" target="_blank" rel="noopener">お時間</a>をもって、ご視聴いただく方、ありがとうございます。</p><img class="stk arig" src="{IMGS['arigatou']}" alt="" width="200" height="151" decoding="async" fetchpriority="high"></div>
<div class="ahatop">
<p class="aha"><small>必ずみつかる、</small>脳アハ！</p>
<img class="stk masc norimobile" src="{IMGS['norikome']}" alt="のりこめゲームスタート！" width="274" height="252" decoding="async" fetchpriority="high">
</div>
<div class="ahawrap">
<img class="stk masc noripc" src="{IMGS['norikome']}" alt="のりこめゲームスタート！" width="274" height="252" decoding="async" fetchpriority="high">
<div class="leadcol">
<p class="lead">年代や性別・日々の環境・経験・人生フェーズに応じた、新たな気づきに出会ってくださいますと嬉しいです。</p>
<div class="bannerrow top">
<a class="banner" href="{wu(ID_ICHIMI,0)}" target="_blank" rel="noopener" style="--th:url({tnhq(ID_ICHIMI)})">
<span class="lbl">{html.escape(TXT_ICHIMI)}<i>click</i></span>
<span class="pop" aria-hidden="true"></span></a>
</div>
</div>
<div class="qrbox"><div class="qrcol">
<button type="button" class="addhome" id="addhomeBtn">🔖 ブックマーク</button>
<a class="qr" href="{SHORT_URL_HREF}" target="_blank" rel="noopener"><img src="img/qr_github.webp" alt="" width="296" height="296" decoding="async" fetchpriority="high"></a>
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
<h3>［ あらかじめ ］</h3>
ＡＩは音読み・訓読みが苦手です。{ilink(LINK_IKKI,'hpo7e3-MewI','五木寛之氏')}を「ごきかんゆき」<span class="red">(失礼！)</span>、と読んだりします。<br>
人もAIも、人名・地名は難しいですね。<span class="hl">「温かく」聞き流しを。</span>
<div class="sep pccenter">
動画「前／中／後」３回の、耳痛いハーモニカ演奏は、<a class="ilink" href="#c{NEWCAT_ID}">意図があって</a>挿入しています。<br>
<span class="red">倍速や早送りなど推奨</span>(⇒<a href="{LINK_STAR}" target="_blank" rel="noopener">★</a>)　<span class="red">どうぞ！早送りくださいませ。</span>
</div>
</div>
<div class="pkwrap"><h2>まずはこのあたりから</h2>{first}
<div class="items shinkai-wrapper"><div class="shinkai-description"><strong>左『＋』ボタンを押すと、その下側にズラット</strong>タイトル表示されます。</div><details class="item solo">
<summary><span class="row1"><span class="pm" aria-hidden="true">＋</span>
<span class="t">神回★</span>
<span class="closelbl" aria-hidden="true">↑ とじる</span></span>
<span class="d">お気に入り</span></summary>
<div class="catbody">{pkgrid(KAMI,cls=f' g{best_cols(len(KAMI),(2,3))}')}</div></details><p class="pkcap">{html.escape(CAP_WAR)}</p>{pkcard(V[ID_WAR]["watch_url"],V[ID_WAR]["thumbnail_url"],V[ID_WAR]["title"])}</div>
</div>
{idx}
<div class="endwrap">
<div class="pks endgrid">
{pkcard(wu(ID_HAIBOKU),IMGS['haiboku'],TXT_HAIBOKU)}
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
document.addEventListener('toggle',function(e){{
 var d=e.target;
 if(d.tagName!=='DETAILS')return;
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
 var t=e.target.closest('.reflink');
 if(!t)return;
 e.preventDefault();
 e.stopPropagation();
 window.open(t.dataset.url,'_blank','noopener');
}});
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

HTML=_minify_html(HTML)
open(OUT,'w').write(HTML)
print(f'{OUT} {os.path.getsize(OUT)/1024:.1f}KB / gzip {len(gzip.compress(HTML.encode()))/1024:.1f}KB')
print(f'カテゴリ{len(C)} 動画{d["total_videos"]} 先頭{sum(len(i) for _,i in FIRST)}本 / オススメ{len(MORE)}本 / 神回{len(KAMI)}本 / 口ぐせ{len(PHRASES)}')
