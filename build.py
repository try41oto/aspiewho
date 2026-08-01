#!/usr/bin/env python3
# aspiewho 動画目次サイト ジェネレーター v7
import json, html, os, gzip, sys
SRC = sys.argv[1] if len(sys.argv)>1 else '/mnt/user-data/outputs/aspiewho_1502_classified.json'
OUT = sys.argv[2] if len(sys.argv)>2 else '/mnt/user-data/outputs/index.html'

# ================= 設定 =================
ORDER=['サブカル','お笑い','生活・文化','言葉','音楽','スポーツ・遊び','地域','歴史','科学',
 '心理・知覚','健康・医療','障がい・福祉','教育','思想・宗教','社会・政治','経済',
 'メディア','デバイス・デジタル生活','IT基盤','AI']
TAIL_GROUP=('ハーモニカ',['029','033'])

FIRST=[(None,['e_sYnb1CdAs','etxG4LU462U','ARyDkAJ4FBQ'])]
ID_WAR='cEkx8UrBpAU'
CAP_WAR='量産のきっかけは、戦争の話。'
ID_HAIBOKU='NjBJJ3JSqag'
TXT_HAIBOKU='技術的敗北と再生の物語'
import base64
def _b64(n):
    p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'img',n)
    return 'data:image/webp;base64,'+base64.b64encode(open(p,'rb').read()).decode()
IMGS={n:_b64(n+'.webp') for n in ('norikome','chiko','nori','kome','haiboku')}
IMGS['arigatou']=_b64('arigatou_anim.webp')
MORE=['TCe2SvES2x4','2Zky_cifOmw','w3dKDFOc-8I','GNnv5kXhJJs','y7VptpwGrX0',
      '3D6P6cqT1X8','WRWJdmNTj8U','v-EOKlp8Vfk','lXz5Y8umPxY','SQIpV-Jcpl8','2GwZJScpJeA']

# NotebookLM の口ぐせ（この順に、ページ全体へ均等に差し込む）
PHRASES=['学ぶことがだいすきなアナタ、本日もようこそ、このディープライブへ',
 'あの〜、ちょっと想像してみてほしいんですけど．．','まさにそこなんですよ','パラダイムシフト',
 'よーし、これらを紐解いていきましょう',
 'さいごあなたに、挑発的な思考のタネを投げかけて、この思考の旅を、、']
PHRASE_AT=[0,4,8,11,15,18]      # 何番目の分野の前に置くか
BANNER_AT=10                     # 「一気見」バナーを置く位置

# 1504本のうち外に出した2本（入れ替わっていたら下の2行を交換）
ID_ICHIMI='uBtnbr0gu80'   # 1500タイトルを24分で一気見！
ID_OWARI ='76XZgkPmg2s'   # 終わり☆AI能力把握実験、脳内発散訓練、遺言】動画量産1500本
TXT_ICHIMI='1500タイトルを24分で一気見！'
TXT_OWARI='終わり☆AI能力把握実験、脳内発散訓練、遺言】動画量産1500本'

SHORT_URL_HREF='https://sites.google.com/view/aspiewho'
LINK_TIME='https://www.youtube.com/watch?v=QMAloSCkHag&t=60s'
LINK_IKKI='https://www.youtube.com/watch?v=hpo7e3-MewI&t=60s'
LINK_INTENT='https://www.youtube.com/watch?v=HvdUHeEzltA&t=60s'
QR='iVBORw0KGgoAAAANSUhEUgAAAJgAAACXAQAAAADB769ZAAAB60lEQVR42qWWQWrdMBCGf1vOQXqIgiGbLmwseFfoLpBT2GiCj5FlzvDgleyCRQfeEQpd9Rgapgs/2SZ1wOnoX1lIP2PNp9EUin9G+VQU1eb7qSiqCgAi1TzrvgBQYmfvzlwFAPevqx+A0qkSC2U5VTrqh5HcqOsYyY0lAKx2H+79MD5HyFrXic/6jN885y5Zyxwb/Or3fiEh+ixGSIf9QIDbnB8BrgIAPvpvO+dXr98/AEBVdQrpJlVVPepX7DBZxfF8Gi6cAYQ7n0x+YLnA+ewnr+1o8SsZ0TMvGWnbwVv8kPqQutRNs5o+pM4UH8C8BVBs8ZXgOLQbnKW1+cXWx2FYLzCDTX7SDhQ3dnyc531eIrmLZF6uF6GrMR+RhBg3yWA7P9c+v909v909fpn18Pub6fwwBU19s/AXUlAbz02Ymi6tCj9tfl3qm7C49X1juh/Q1HRTvxSs1NjiK4WEol/4i2TkT06Er8QLf7DeDw/EDX8Ujfw9vLz8Wvl7/M5/bPmYmpBW/vrO+n5cwPX1fJo1EGpnvL9ApFv9az2i5/99f5e3UdpcsDxHsvk51U39Y8Tj9f59f6WqWs391fr+or5+rr8ad9bxQh9YyBLf3F/ljqj10Yu3+YUEltxeiReCOb8LL15IbPndY/Iv/bsOQ2OFyVkAAAAASUVORK5CYII='
LINK_STAR='https://www.youtube.com/watch?v=d774Mau6-aI&t=60s'
# ================= 設定ここまで =================

d=json.load(open(SRC))
B={b['block']:b for b in d['blocks']}
C={c['category_id']:c for b in d['blocks'] for c in b['categories']}
V={v['video_id']:v for b in d['blocks'] for c in b['categories'] for v in c['videos']}
ZERO_CATS={'029'}          # 冒頭から再生するカテゴリ
tn=lambda i:f'https://img.youtube.com/vi/{i}/mqdefault.jpg'
tnhq=lambda i:f'https://img.youtube.com/vi/{i}/hqdefault.jpg'
wu=lambda i,s=60:f'https://www.youtube.com/watch?v={i}'+(f'&t={s}s' if s else '')

for c in C.values():
    z = c['category_id'] in ZERO_CATS
    for v in c['videos']:
        v['start_sec']=0 if z else 60
        v['watch_url']=f'https://www.youtube.com/watch?v={v["video_id"]}'+('' if z else '&t=60s')

tname,tids=TAIL_GROUP
groups=[]
for n in ORDER:
    cs=[c for c in B[n]['categories'] if c['category_id'] not in tids]
    if cs: groups.append((n,cs))
groups.append((tname,[C[x] for x in tids]))
assert sum(len(cs) for _,cs in groups)==len(C)
assert sum(c['count'] for _,cs in groups for c in cs)==d['total_videos']

def pkgrid(ids,extra=''):
    return '<div class="pks">'+''.join(
     f'<a class="pk" href="{V[i]["watch_url"]}" target="_blank" rel="noopener">'
     f'<img src="{V[i]["thumbnail_url"]}" alt="" width="320" height="180" loading="lazy" decoding="async">'
     f'<p>{html.escape(V[i]["title"])}</p></a>' for i in ids)+extra+'</div>'

def onerow(href,thumb,title):
    return (f'<a class="row" href="{href}" target="_blank" rel="noopener" style="--th:url({thumb})">'
            f'<img class="mini" src="{thumb}" alt="" width="320" height="180" loading="lazy" decoding="async">'
            f'<span class="ttl">{html.escape(title)}</span><span class="pop" aria-hidden="true"></span></a>')

def rows(vids):
    out=''
    for v in vids:
        t=('<b>神回</b>' if v['kamikai'] else '')+html.escape(v['title'])
        out+=(f'<a class="row" href="{v["watch_url"]}" target="_blank" rel="noopener" '
              f'style="--th:url({v["thumbnail_url"]})">'
              f'<img class="mini" src="{v["thumbnail_url"]}" alt="" width="320" height="180" loading="lazy" decoding="async">'
              f'<span class="ttl">{t}</span><span class="pop" aria-hidden="true"></span></a>')
    return f'<div class="rows">{out}</div>'

KAMI=[v['video_id'] for _,cats in groups for c in cats for v in c['videos'] if v['kamikai']]

CHIKO=('<div class="stkcell"><img src="'+IMGS['chiko']+'" alt="" width="300" height="265" decoding="async"></div>')
first=''.join((f'<p class="pkcap">{html.escape(c)}</p>' if c else '')+pkgrid(i,CHIKO) for c,i in FIRST)

phr={p:(k,PHRASES[k]) for k,p in enumerate(PHRASE_AT)}
idx=''
for gi,(name,cats) in enumerate(groups):
    if gi in phr:
        k,txt=phr[gi]
        idx+=f'<p class="say{" l" if k%2 else ""}">{html.escape(txt)}</p>'
    if gi==BANNER_AT:
        idx+=(f'<a class="banner" href="{wu(ID_ICHIMI,0)}" target="_blank" rel="noopener" '
              f'style="--th:url({tnhq(ID_ICHIMI)})">'
              f'<img src="{tn(ID_ICHIMI)}" alt="" width="320" height="180" loading="lazy" decoding="async">'
              f'<span class="lbl"><em>＞</em>{html.escape(TXT_ICHIMI)}<i>click</i></span>'
              f'<span class="pop" aria-hidden="true"></span>'
              f'<img class="stk nori" src="{IMGS['nori']}" alt="" width="270" height="254" loading="lazy" decoding="async"></a>')
    items=''.join(
     f'<a class="item" href="#c{c["category_id"]}">'
     f'<span class="row1"><span class="pm" aria-hidden="true">＋</span>'
     f'<span class="t">{html.escape(c["name"])}</span></span>'
     f'<span class="d">{html.escape(c["description"])}</span></a>' for c in cats)
    if name==tname:
        items+=(f'<div class="stkitem"><img src="{IMGS['kome']}" alt="" '
                f'width="266" height="254" loading="lazy" decoding="async"></div>')
    idx+=f'<section class="blk"><h2>{html.escape(name)}</h2><div class="items">{items}</div></section>'

secs=''.join(
 f'<section class="cat" id="c{c["category_id"]}"><div class="wrap">'
 f'<a class="back" href="#top">← もどる</a>'
 f'<header><h1>{html.escape(c["name"])}</h1>'
 f'<p class="desc">{html.escape(c["description"])}</p></header>'
 f'{rows(c["videos"])}<a class="back bottom" href="#top">← もどる</a></div></section>'
 for _,cats in groups for c in cats)
secs+=(f'<section class="cat solo" id="rec"><div class="wrap"><a class="back" href="#top">← もどる</a>'
 f'<header><h1>つぎにこのへんオススメはいかが</h1>'
 f'<p class="desc">カテゴリをまたいで、気に入っているものを。</p></header>'
 f'{pkgrid(MORE)}<a class="back bottom" href="#top">← もどる</a></div></section>')
secs+=(f'<section class="cat solo" id="kamikai"><div class="wrap"><a class="back" href="#top">← もどる</a>'
 f'<header><h1>神回★</h1>'
 f'<p class="desc">名作お気に入り</p></header>'
 f'{pkgrid(KAMI)}<a class="back bottom" href="#top">← もどる</a></div></section>')

CSS='''
:root{--bg:#FFF;--face:#FAFBFC;--line:#D7DEE5;--line2:#EDF0F3;--fg:#16212D;--dim:#65758A;
--accent:#9A6B12;--sub:#2E6280;--tint:#FFF8E9;--soft:#F3F7F9;--deep:#21708F;
--green:#F1F8F1;--greenline:#DBEADB;--alt:#FFFDF3;--blue:#1668A8}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-size:15px;line-height:1.7;
font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;
-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:0 14px}
a{color:inherit}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
.hero{padding:26px 0 4px}
.url{display:inline-block;padding:5px 11px;border:1px solid var(--line);border-radius:4px;
background:var(--face);font-size:12.5px;color:var(--sub);text-decoration:none;font-variant-numeric:tabular-nums}
.url b{color:var(--fg);font-weight:700}
.mins{margin:14px 0 0;font-size:14px;color:var(--dim)}
.thanks{margin:4px 0 0;font-size:14px;color:var(--dim)}
.thanks a,.note a{color:var(--sub);text-underline-offset:3px}
.ahawrap{display:flex;align-items:center;gap:14px;margin:20px 0 0}
.aha{margin:0;flex:1 1 auto;min-width:0;font-size:clamp(26px,7.4vw,44px);font-weight:800;letter-spacing:.04em;line-height:1.25}
.stk{display:block;height:auto;flex:0 0 auto}
.arig{width:58px;margin-right:-4px}
.qrbox{display:flex;align-items:flex-end;gap:6px;flex:0 0 auto}
.nk{width:88px}
.red{color:#C0342B;font-weight:700}
.qr{flex:0 0 auto;text-align:center;text-decoration:none;color:var(--fg);display:block}
.qr .qr1{display:block;font-size:10px;font-weight:700;color:var(--dim);letter-spacing:-.04em}
.qr .qr2{display:block;font-size:12px;font-weight:800;color:var(--sub);
letter-spacing:-.06em;margin:1px 0 3px;white-space:nowrap}
.qr img{display:block;width:92px;height:auto;padding:4px;background:#fff;
border:1px solid var(--line);border-radius:4px;image-rendering:pixelated}
.aha small{display:block;font-size:14px;font-weight:600;color:var(--dim);letter-spacing:.1em;margin-bottom:2px}
.lead{margin:12px 0 0;font-size:14px;line-height:1.85}
.note{margin:24px 0 0;padding:14px 15px;background:var(--green);border-radius:6px;font-size:13px;line-height:1.85}
.note h3{margin:0 0 6px;font-size:12px;letter-spacing:.14em;color:var(--sub);font-weight:700}
.note .sep{margin:11px 0 0;padding-top:11px;border-top:1px solid var(--greenline)}
.note .ff{font-weight:700}
/* 口ぐせの帯 */
.say{margin:34px 0;padding:26px 20px;background:var(--deep);color:#fff;border-radius:4px;
font-family:"Hiragino Mincho ProN","ヒラギノ明朝 ProN","Yu Mincho","游明朝","YuMincho",
"Noto Serif JP","Noto Serif CJK JP","MS PMincho",serif;
font-size:clamp(16px,3.9vw,23px);line-height:1.95;letter-spacing:.1em;font-weight:400;
font-style:italic;font-style:oblique 12deg}
.say.l{font-style:normal;font-style:oblique -12deg}
/* ピックアップ */
.pkwrap{margin:30px 0 0}
.pkwrap h2{margin:0 0 12px;font-size:16px;font-weight:800;letter-spacing:.04em;color:var(--blue)}
.item.solo .t{color:var(--blue)}
.stkitem{display:flex;align-items:center;justify-content:flex-end;padding:4px}
.stkitem img{width:88px;height:auto}
.cat.solo h1{color:var(--blue)}
.pks{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 10px;margin-bottom:14px}
.pk{text-decoration:none;display:block}
.pk img{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;
border:1px solid var(--line2);border-radius:4px;background:var(--face)}
.pk p{margin:6px 0 0;font-size:12px;line-height:1.5;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pks .stkcell{display:flex;align-items:center;justify-content:center}
.pks .stkcell img{width:100%;max-width:190px;height:auto}
.pkcap{margin:6px 0 12px;font-size:clamp(17px,4.4vw,22px);font-weight:700;
color:var(--blue);letter-spacing:.02em;line-height:1.5}
.allnote{margin:34px 0 0;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--dim)}
/* 一気見バナー */
.banner{display:flex;gap:12px;align-items:center;margin:30px 0;padding:12px 14px;
background:var(--tint);border:1px solid var(--accent);border-radius:6px;text-decoration:none}
.banner img{width:112px;height:63px;object-fit:cover;border-radius:3px;flex:0 0 auto;border:1px solid var(--line2)}
.banner{position:relative}
.banner .nori{width:88px;margin-left:auto;flex:0 0 auto}
.banner .pop{display:none}
.banner .lbl{font-size:15px;font-weight:800;line-height:1.5;
text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:4px}
.banner em{font-style:normal;color:var(--accent);margin-right:6px;text-decoration:none;display:inline-block}
.banner i{display:block;font-style:normal;font-size:11px;font-weight:600;color:var(--accent);
letter-spacing:.16em;text-decoration:none;margin-top:3px}
/* カテゴリ一覧 */
.blk{margin:26px 0 0}
.blk h2{margin:0 0 9px;padding-bottom:5px;border-bottom:1px solid var(--line);
font-size:13px;letter-spacing:.16em;color:var(--sub);font-weight:700}
.items{display:grid;grid-template-columns:1fr;gap:7px}
.item{display:block;padding:11px 12px;text-decoration:none;background:#FFF;
border:1px solid var(--line);border-radius:5px;transition:background .12s,border-color .12s}
.item:nth-child(even){background:var(--alt)}
.item:active{background:var(--tint)}
.row1{display:flex;align-items:baseline;gap:8px}
.item .pm{font-size:14px;font-weight:700;color:var(--accent);flex:0 0 auto;line-height:1.4}
.item .t{font-size:15px;font-weight:700;flex:1;min-width:0;text-decoration:underline;
text-decoration-thickness:1px;text-underline-offset:3px;text-decoration-color:var(--line)}
.item .d{display:block;margin-top:3px;padding-left:22px;font-size:12.5px;color:var(--dim);line-height:1.6}
.item.solo .d{color:var(--dim)}
/* カテゴリ中身 */
.cat{display:none;padding:16px 0 44px}
.cat:target{display:block}
.cat header{padding:14px 0;border-bottom:2px solid var(--fg);margin-bottom:14px}
.cat h1{margin:0;font-size:21px;line-height:1.4}
.cat .desc{margin:6px 0 0;font-size:13.5px;color:var(--dim)}
.back{display:inline-block;padding:7px 14px;border:1px solid var(--line);border-radius:4px;
background:var(--face);font-size:13px;text-decoration:none;color:var(--sub)}
.back:active{background:var(--tint)}
.back.bottom{margin-top:26px}
/* 動画1本ぶん（スマホ：左サムネ＋右タイトル） */
.rows{display:flex;flex-direction:column}
.row{display:flex;gap:11px;align-items:center;padding:9px 2px;
border-bottom:1px solid var(--line2);text-decoration:none;position:relative}
.row .mini{width:50%;max-width:190px;height:auto;aspect-ratio:16/9;object-fit:cover;
border-radius:3px;border:1px solid var(--line2);background:var(--face);flex:0 0 auto}
.row .ttl{font-size:12.5px;line-height:1.5;min-width:0;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row .pop{display:none}
.row b{display:inline-block;margin-right:5px;padding:1px 5px;border-radius:2px;
background:var(--tint);border:1px solid var(--accent);color:var(--accent);
font-size:10px;font-weight:700;vertical-align:1px}
.row:active{background:var(--tint)}
.endwrap{margin:44px 0 30px}
.endgrid{display:grid;grid-template-columns:1fr;gap:10px 28px;margin-top:16px}
.endgrid .pkcap{margin:0 0 6px}
.tail{margin:36px 0 26px;height:1px;background:var(--line)}
@media(min-width:600px){
 .wrap{padding:0 20px}
 .items{grid-template-columns:repeat(2,1fr)}
 .pks{grid-template-columns:repeat(3,1fr);gap:18px 14px}
 .cat h1{font-size:25px}
 .endgrid{grid-template-columns:repeat(3,1fr);align-items:end}
 .banner img{width:160px;height:90px}
 .qr img{width:116px}
 .arig{width:76px}
 .banner .lbl{font-size:19px}
}
@media(min-width:940px){
 .items{grid-template-columns:repeat(3,1fr)}
 .pks{grid-template-columns:repeat(4,1fr)}
 .item:hover{background:var(--tint);border-color:var(--accent)}
 .item:hover .t{text-decoration-color:var(--accent)}
 .pk:hover img{border-color:var(--accent)}
 .back:hover{background:var(--tint);border-color:var(--accent)}
 .banner:hover{background:#FFF3D6}
}
/* PC（マウスがある画面）：文字だけ並べて、乗せるとフワッと出す */
@media (hover:hover) and (pointer:fine) and (min-width:700px){
 .banner .pop{display:block;position:absolute;left:0;top:calc(100% + 9px);
  width:min(1040px,94vw);aspect-ratio:16/9;border-radius:6px;border:1px solid var(--line);
  background:#fff center/cover no-repeat;box-shadow:0 14px 36px rgba(20,35,50,.26);
  opacity:0;transform:translateY(-8px) scale(.97);
  transition:opacity .22s ease,transform .22s ease;pointer-events:none;z-index:12}
 .banner:hover .pop,.banner:focus-visible .pop{background-image:var(--th);opacity:1;
  transform:translateY(0) scale(1)}
 .rows{display:grid;grid-template-columns:repeat(2,1fr);column-gap:28px}
 .row{padding:7px 2px}
 .row .mini{display:none}
 .row .ttl{-webkit-line-clamp:1;font-size:13.5px}
 .row .pop{display:block;position:absolute;left:0;top:calc(100% + 5px);
  width:232px;height:130px;border-radius:5px;border:1px solid var(--line);
  background:#fff center/cover no-repeat;box-shadow:0 8px 22px rgba(20,35,50,.20);
  opacity:0;transform:translateY(-5px);transition:opacity .18s ease,transform .18s ease;
  pointer-events:none;z-index:9}
 .row:hover .pop,.row:focus-visible .pop{background-image:var(--th);opacity:1;transform:translateY(0)}
 .row:hover .ttl{text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--accent)}
 .row:hover{background:transparent}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
'''

HTML=f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>脳アハ！｜ aspiewho</title>
<meta name="description" content="必ずみつかる、脳アハ！ 新たな気づきに出会えますように。">
<style>{CSS}</style></head><body>
<div class="wrap" id="top">
<div class="hero">
<p class="mins">1つ視聴に25分。🥴</p>
<p class="thanks">大切な<a href="{LINK_TIME}" target="_blank" rel="noopener">お時間</a>をもって、ご視聴いただく方、ありがとうございます。</p>
<div class="ahawrap"><img class="stk arig" src="{IMGS['arigatou']}" alt="" width="200" height="151" decoding="async"><p class="aha"><small>必ずみつかる、</small>脳アハ！</p><div class="qrbox"><img class="stk nk" src="{IMGS['norikome']}" alt="" width="274" height="252" decoding="async"><a class="qr" href="{SHORT_URL_HREF}" target="_blank" rel="noopener"><span class="qr1">［ＵＲＬ１１文字］</span><span class="qr2">ｎ９．ｃｌ／ｔｒｙ４ａ</span><img src="data:image/png;base64,{QR}" alt="" width="152" height="151" decoding="async"></a></div></div>
<p class="lead">年代や性別・日々の環境・経験・人生フェーズに応じた、新たな気づきに出会ってくださいますと嬉しいです。</p>
</div>
<div class="note">
<h3>［ あらかじめ ］</h3>
ＡＩは音読み・訓読みが苦手です。<a href="{LINK_IKKI}" target="_blank" rel="noopener">五木寛之氏</a>を「ごきかんゆき」<span class="red">(失礼！)</span>、と読んだりします。<br>
そういえばワタクシたちも、人名・地名は難しいですね。人もAIも永遠の課題だと思われます。「温かく」聞き流しを。
<div class="sep">
動画「前／中／後」３回の、耳痛いハーモニカ演奏は、<a href="{LINK_INTENT}" target="_blank" rel="noopener">意図があって</a>挿入しています。<br>
<span class="red">倍速や早送りなど推奨</span>(⇒<a href="{LINK_STAR}" target="_blank" rel="noopener">★</a>)　<span class="red">どうぞ！早送りくださいませ。</span>
</div>
</div>
<div class="pkwrap"><h2>まずはこのあたりから</h2>{first}
<div class="items"><a class="item solo" href="#rec">
<span class="row1"><span class="pm" aria-hidden="true">＋</span>
<span class="t">つぎにこのへんオススメはいかが</span></span>
<span class="d">カテゴリをまたいで、気に入っているものを。</span></a>
<a class="item solo" href="#kamikai">
<span class="row1"><span class="pm" aria-hidden="true">＋</span>
<span class="t">神回★</span></span>
<span class="d">名作お気に入り</span></a></div>
</div>
{idx}
<div class="endwrap">
<p class="allnote">1502本を125のカテゴリに分けました。</p>
<div class="endgrid">
<div><p class="pkcap">{html.escape(CAP_WAR)}</p>{onerow(V[ID_WAR]["watch_url"],V[ID_WAR]["thumbnail_url"],V[ID_WAR]["title"])}</div>
<div>{onerow(wu(ID_HAIBOKU),IMGS['haiboku'],TXT_HAIBOKU)}</div>
<div>{onerow(wu(ID_OWARI),tn(ID_OWARI),TXT_OWARI)}</div>
</div></div>
<div class="tail"></div>
</div>
{secs}
</body></html>'''
open(OUT,'w').write(HTML)
print(f'{OUT} {os.path.getsize(OUT)/1024:.1f}KB / gzip {len(gzip.compress(HTML.encode()))/1024:.1f}KB')
print(f'カテゴリ{len(C)} 動画{d["total_videos"]} 先頭{sum(len(i) for _,i in FIRST)}本 / オススメ{len(MORE)}本 / 神回{len(KAMI)}本 / 口ぐせ{len(PHRASES)}')
