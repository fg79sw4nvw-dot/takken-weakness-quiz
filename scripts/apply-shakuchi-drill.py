from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('<button data-view="sort"><span class="ico">🗂️</span>35/37</button>','<button data-view="sort"><span class="ico">🧩</span>ドリル</button>')
s=s.replace("if(view==='sort')renderSortLanding();","if(view==='sort')renderDrillHub();")

css='''\n    /* ドリル共通 */\n    .drill-menu{display:grid;gap:12px}.drill-card{border:1px solid var(--line);border-radius:18px;padding:18px;background:#fff;text-align:left;cursor:pointer}.drill-card b{font-size:18px;display:block;margin-bottom:5px}.drill-card span{font-size:12px;color:var(--muted);line-height:1.6}.drill-tag{display:inline-block;font-size:11px;font-weight:800;padding:5px 8px;border-radius:999px;background:#eef2ff;color:#3730a3;margin-bottom:10px}.shaku-category{font-size:13px;font-weight:800;color:#1e40af;background:#dbeafe;padding:7px 10px;border-radius:999px;display:inline-block}.shaku-options{display:grid;gap:9px;margin-top:18px}.shaku-option{border:2px solid var(--line);border-radius:15px;padding:14px 12px;background:#fff;text-align:left;font-weight:750;cursor:pointer}.shaku-option.ok{border-color:#86efac;background:#f0fdf4;color:#166534}.shaku-option.ng{border-color:#fca5a5;background:#fef2f2;color:#991b1b}.shaku-option.sel{box-shadow:0 0 0 2px #2563eb22}\n'''
s=s.replace('    @media(max-width:420px){.sort-controls,.sort-answers{grid-template-columns:1fr}.nav button{font-size:10px}.nav .ico{font-size:18px}}',css+'    @media(max-width:420px){.sort-controls,.sort-answers{grid-template-columns:1fr}.nav button{font-size:10px}.nav .ico{font-size:18px}}')

marker="const SORT_BANK_KEY='takken3537DrillBankV1';"
insert=r'''const SHAKU_STATS_KEY='takkenShakuchiShakkaStatsV1';
const SHAKU_CATS=['制度仕分け','数字・期間','更新・終了','対抗要件','書面要件','誰が何をできるか'];
const SHAKU_QUESTIONS=[
{id:'shaku-0001',cat:'制度仕分け',prompt:'存続期間を50年以上とし、更新・建物再築による期間延長・建物買取請求を排除できる借地権は？',options:['普通借地権','一般定期借地権','事業用定期借地権','建物譲渡特約付借地権'],answer:1,exp:'一般定期借地権は50年以上。更新等がなく、建物買取請求をしない特約を置ける。',basis:'借地借家法22条'},
{id:'shaku-0002',cat:'制度仕分け',prompt:'専ら事業用建物の所有を目的とし、存続期間を10年以上50年未満として設定できる借地権は？',options:['普通借地権','一般定期借地権','事業用定期借地権','普通借家'],answer:2,exp:'事業用定期借地権は10年以上50年未満で、居住用建物は対象外。',basis:'借地借家法23条'},
{id:'shaku-0003',cat:'制度仕分け',prompt:'借地権設定後30年以上を経過した日に、借地上の建物を地主へ相当の対価で譲渡して借地権を消滅させる制度は？',options:['一般定期借地権','事業用定期借地権','建物譲渡特約付借地権','普通借家'],answer:2,exp:'建物譲渡特約付借地権は、設定後30年以上経過した日に建物を地主へ譲渡する特約を利用する。',basis:'借地借家法24条'},
{id:'shaku-0004',cat:'制度仕分け',prompt:'建物賃貸借で「契約の更新がなく、期間満了で終了する」と定める制度は？',options:['普通借家','定期建物賃貸借','普通借地権','事業用定期借地権'],answer:1,exp:'定期建物賃貸借は更新がなく、期間満了により終了する。',basis:'借地借家法38条'},
{id:'shaku-0005',cat:'数字・期間',prompt:'普通借地権で存続期間を定めなかった場合の期間は？',options:['10年','20年','30年','50年'],answer:2,exp:'普通借地権の当初の存続期間は原則30年。30年未満の定めも30年となる。',basis:'借地借家法3条'},
{id:'shaku-0006',cat:'数字・期間',prompt:'普通借地権の最初の更新で、更新後の期間を定めなかった場合は？',options:['10年','20年','30年','50年'],answer:1,exp:'最初の更新は20年。2回目以降は10年。',basis:'借地借家法4条'},
{id:'shaku-0007',cat:'数字・期間',prompt:'普通借地権の2回目以降の更新で、更新後の期間を定めなかった場合は？',options:['5年','10年','20年','30年'],answer:1,exp:'2回目以降の更新期間は10年。',basis:'借地借家法4条'},
{id:'shaku-0008',cat:'数字・期間',prompt:'普通建物賃貸借で期間を8か月と定めた場合、原則どう扱われる？',options:['8か月で終了','1年に延長','期間の定めがないものとみなす','契約自体が無効'],answer:2,exp:'普通建物賃貸借で1年未満の期間を定めると、期間の定めがない建物賃貸借とみなされる。',basis:'借地借家法29条1項'},
{id:'shaku-0009',cat:'更新・終了',prompt:'普通建物賃貸借で賃貸人が期間満了による更新拒絶をする場合、必要となる中心的な条件は？',options:['公正証書','正当事由','借主の書面承諾','宅建士の説明'],answer:1,exp:'賃貸人の更新拒絶には正当事由が必要。通知期間のルールもある。',basis:'借地借家法26条・28条'},
{id:'shaku-0010',cat:'更新・終了',prompt:'期間の定めがない普通建物賃貸借で、賃貸人から解約申入れをした場合、原則いつ終了する？',options:['直ちに','1か月後','3か月後','6か月後'],answer:3,exp:'賃貸人の解約申入れから6か月で終了する。賃貸人側には正当事由も必要。',basis:'借地借家法27条・28条'},
{id:'shaku-0011',cat:'更新・終了',prompt:'定期建物賃貸借（期間1年以上）で、賃貸人が期間満了による終了を賃借人に対抗するための終了通知期間は？',options:['満了の3か月前まで','満了の1年前から6か月前まで','満了の2年前まで','通知不要'],answer:1,exp:'期間1年以上の定期建物賃貸借では、原則として満了の1年前から6か月前までの間に終了通知が必要。',basis:'借地借家法38条6項'},
{id:'shaku-0012',cat:'更新・終了',prompt:'普通借地権で契約更新がない場合、一定の要件の下で借地権者が地主に求められるものは？',options:['建物の無償譲渡','建物買取請求','土地所有権の移転','必ず再契約'],answer:1,exp:'借地権が期間満了で終了し更新がない場合、借地権者は一定の場合に建物買取請求権を行使できる。',basis:'借地借家法13条'},
{id:'shaku-0013',cat:'対抗要件',prompt:'土地の賃借権登記がない借地権者が第三者に借地権を対抗するために使えるものは？',options:['借地上の自己名義の建物登記','土地の引渡しだけ','契約書の保管','地主の口頭承諾'],answer:0,exp:'借地権者が借地上に自己名義で登記された建物を所有すると、土地賃借権の登記がなくても第三者に対抗できる。',basis:'借地借家法10条'},
{id:'shaku-0014',cat:'対抗要件',prompt:'建物賃借権について、登記がなくても第三者に対抗できる基本的な要件は？',options:['建物の引渡し','公正証書','敷金の支払い','1年以上の居住'],answer:0,exp:'建物の引渡しがあれば、建物賃借権の登記がなくても第三者に対抗できる。',basis:'借地借家法31条'},
{id:'shaku-0015',cat:'対抗要件',prompt:'普通借家と定期建物賃貸借で、建物の引渡しによる対抗要件の扱いは？',options:['普通借家だけ使える','定期借家だけ使える','どちらでも使える','どちらも登記が必須'],answer:2,exp:'建物引渡しによる対抗力は普通借家・定期建物賃貸借の双方で利用できる。',basis:'借地借家法31条'},
{id:'shaku-0016',cat:'対抗要件',prompt:'借地権の対抗要件として建物登記を利用するとき、重要なのは誰の名義の登記？',options:['地主','借地権者本人','宅建業者','金融機関'],answer:1,exp:'借地権者が自己名義で登記した建物を所有していることが重要。',basis:'借地借家法10条'},
{id:'shaku-0017',cat:'書面要件',prompt:'一般定期借地権の設定契約で必要な方式は？',options:['口頭だけでよい','書面または電磁的記録','必ず公正証書','登記だけで成立'],answer:1,exp:'一般定期借地権の特約は書面または電磁的記録による。公正証書限定ではない。',basis:'借地借家法22条'},
{id:'shaku-0018',cat:'書面要件',prompt:'事業用定期借地権の設定契約で必要な方式は？',options:['口頭','通常の書面なら何でもよい','公正証書','土地登記だけ'],answer:2,exp:'事業用定期借地権は公正証書によって設定する必要がある。',basis:'借地借家法23条3項'},
{id:'shaku-0019',cat:'書面要件',prompt:'定期建物賃貸借契約を有効に成立させるための契約方式は？',options:['口頭でも可','書面または電磁的記録','必ず公正証書','建物登記'],answer:1,exp:'定期建物賃貸借は書面または電磁的記録による契約が必要。',basis:'借地借家法38条1項'},
{id:'shaku-0020',cat:'書面要件',prompt:'定期建物賃貸借で、賃貸人が契約締結前に行う必要があるものは？',options:['更新がなく期間満了で終了する旨の説明','必ず保証会社を付ける説明','賃料を変更しない説明','建物を買い取る説明'],answer:0,exp:'賃貸人は、契約前に更新がなく期間満了で終了する旨を所定の方法で説明する必要がある。',basis:'借地借家法38条3項'},
{id:'shaku-0021',cat:'誰が何をできるか',prompt:'普通借地権が更新されず終了する場合、一定の要件で建物買取請求をする側は？',options:['地主','借地権者','隣地所有者','宅建業者'],answer:1,exp:'一定の場合、借地権者が借地権設定者に建物の買取りを請求する。',basis:'借地借家法13条'},
{id:'shaku-0022',cat:'誰が何をできるか',prompt:'普通建物賃貸借で更新を拒絶する賃貸人に正当事由が要求される主な理由として最も近いものは？',options:['賃借人の居住・利用の安定を保護するため','地主の税負担を減らすため','登記を不要にするため','宅建業者を保護するため'],answer:0,exp:'借地借家法は建物賃借人の利用・居住の安定を強く保護しており、賃貸人側の更新拒絶等に正当事由を要求する。',basis:'借地借家法28条'},
{id:'shaku-0023',cat:'誰が何をできるか',prompt:'借地権者が借地上の建物を第三者へ譲渡する際、土地賃借権の譲渡について地主の承諾が得られない場合に、一定の場合できることは？',options:['無条件で自由に譲渡','裁判所に地主の承諾に代わる許可を求める','土地所有権を取得する','必ず契約解除'],answer:1,exp:'一定の場合、裁判所は借地権設定者の承諾に代わる許可を与えることができる。',basis:'借地借家法19条'},
{id:'shaku-0024',cat:'誰が何をできるか',prompt:'建物譲渡特約付借地権で、特約に従って建物が地主へ譲渡された後、その建物を使用している借地権者等が一定の場合に請求できるものは？',options:['土地所有権の移転','建物の賃借権設定','建物の無償返還','借地権の永久更新'],answer:1,exp:'建物譲渡により借地権が消滅した後も、建物使用者は一定の場合に建物賃貸借の設定を請求できる。',basis:'借地借家法24条2項'}
];
'''
s=s.replace(marker,insert+'\n'+marker)

old_start="function renderSortLanding(){initSortBank();const v=$('#sortView');v.innerHTML=`<section class=\"card\"><h2 style=\"margin-top:0\">35条・37条 仕分けドリル</h2>"
if old_start not in s:
    raise SystemExit('renderSortLanding marker not found')
s=s.replace('function renderSortLanding(){initSortBank();const v=$(\'#sortView\');v.innerHTML=`<section class="card"><h2 style="margin-top:0">35条・37条 仕分けドリル</h2>', 'function render3537Landing(){initSortBank();const v=$(\'#sortView\');v.innerHTML=`<section class="card"><button class="smallbtn" onclick="renderDrillHub()">← ドリル一覧</button><h2 style="margin-top:14px">35条・37条 仕分けドリル</h2>')
# Runtime source uses normal quotes; fallback direct replacement
s=s.replace("function renderSortLanding(){initSortBank();const v=$('#sortView');v.innerHTML=`<section class=\"card\"><h2 style=\"margin-top:0\">35条・37条 仕分けドリル</h2>","function render3537Landing(){initSortBank();const v=$('#sortView');v.innerHTML=`<section class=\"card\"><button class=\"smallbtn\" onclick=\"renderDrillHub()\">← ドリル一覧</button><h2 style=\"margin-top:14px\">35条・37条 仕分けドリル</h2>")
s=s.replace('onclick="renderSortLanding()"','onclick="render3537Landing()"')
s=s.replace('renderSortLanding();const el=$(\'#sortImportStatus\');','render3537Landing();const el=$(\'#sortImportStatus\');')
s=s.replace("renderSortLanding();const el=$('#sortImportStatus');","render3537Landing();const el=$('#sortImportStatus');")
s=s.replace('sortSession=null;renderSortLanding()','sortSession=null;render3537Landing()')

addon=r'''
function shakuStats(){try{return JSON.parse(localStorage.getItem(SHAKU_STATS_KEY)||'{}')}catch(e){return {}}}
function saveShakuStats(x){localStorage.setItem(SHAKU_STATS_KEY,JSON.stringify(x))}
let shakuSession=null;
function shakuCategoryStats(){const st=shakuStats();return SHAKU_CATS.map(cat=>{let attempts=0,correct=0;SHAKU_QUESTIONS.filter(q=>q.cat===cat).forEach(q=>{const x=st[q.id];if(x){attempts+=x.attempts||0;correct+=x.correct||0}});return{cat,attempts,correct,rate:attempts?Math.round(correct/attempts*100):0}})}
function renderDrillHub(){const st=shakuStats(),sdone=SHAKU_QUESTIONS.filter(q=>(st[q.id]?.attempts||0)>0).length;$('#sortView').innerHTML=`<section class="card"><h2 style="margin-top:0">ドリル</h2><p class="note">知識を覚えるだけでなく、似た制度を条件から見分ける練習をします。</p><div class="drill-menu"><button class="drill-card" onclick="render3537Landing()"><span class="drill-tag">宅建業法</span><b>🗂️ 35条・37条</b><span>重要事項説明と契約書面を、目的物・取引条件まで見て仕分ける。</span></button><button class="drill-card" onclick="renderShakuLanding()"><span class="drill-tag">権利関係</span><b>🏠 借地借家法</b><span>制度・期間・更新・対抗要件・書面・主体を条件から判断。${SHAKU_QUESTIONS.length}問中 ${sdone}問学習済み。</span></button></div></section>`}
function renderShakuLanding(){const rows=shakuCategoryStats(),st=shakuStats(),attempts=Object.values(st).reduce((a,x)=>a+(x.attempts||0),0),correct=Object.values(st).reduce((a,x)=>a+(x.correct||0),0),rate=attempts?Math.round(correct/attempts*100):0;$('#sortView').innerHTML=`<section class="card"><button class="smallbtn" onclick="renderDrillHub()">← ドリル一覧</button><h2 style="margin-top:14px">借地借家法ドリル</h2><p class="note">○×ではなく、条件を読んで制度・数字・権利関係を選び分けます。</p><div class="grid"><div class="mini"><b>${attempts?rate+'%':'-'}</b><span>総合正答率</span></div><div class="mini"><b>${SHAKU_QUESTIONS.length}</b><span>問題数</span></div></div><div class="field"><label>出題カテゴリ</label><select id="shakuCat" class="select"><option value="all">総合ランダム</option>${SHAKU_CATS.map(c=>`<option value="${c}">${c}</option>`).join('')}</select></div><div class="field"><label>出題数</label><select id="shakuCount" class="select"><option value="10">10問</option><option value="20">20問</option><option value="all">全問</option></select></div><button class="primary" onclick="startShakuDrill()">借地借家法ドリルを開始</button></section><section class="card"><h3 style="margin-top:0">カテゴリ別成績</h3>${rows.map(r=>`<div class="stat-row"><div class="line"><b>${r.cat}</b><span>${r.attempts?`${r.correct}/${r.attempts}（${r.rate}%）`:'未回答'}</span></div><div class="bar"><i style="width:${r.rate}%"></i></div></div>`).join('')}<button class="secondary danger" onclick="resetShakuStats()">借地借家法の学習履歴をリセット</button></section>`}
function startShakuDrill(){const cat=$('#shakuCat').value,cnt=$('#shakuCount').value;let qs=SHAKU_QUESTIONS.filter(q=>cat==='all'||q.cat===cat).sort(()=>Math.random()-.5);if(cnt!=='all')qs=qs.slice(0,Math.min(Number(cnt),qs.length));shakuSession={ids:qs.map(q=>q.id),idx:0,correct:0,answers:[]};renderShakuQuestion()}
function currentShakuQ(){return SHAKU_QUESTIONS.find(q=>q.id===shakuSession?.ids[shakuSession.idx])}
function renderShakuQuestion(){const q=currentShakuQ();if(!q){renderShakuFinish();return}const st=shakuStats()[q.id]||{};shakuSession.started=Date.now();$('#sortView').innerHTML=`<section class="card"><div class="quiz-head"><span>${shakuSession.idx+1} / ${shakuSession.ids.length}</span><span>${shakuSession.correct}正解</span></div><div class="sort-progress"><i style="width:${Math.round(shakuSession.idx/shakuSession.ids.length*100)}%"></i></div><div style="margin-top:14px"><span class="shaku-category">${q.cat}</span></div><div class="sort-question">${q.prompt}</div><div class="shaku-options">${q.options.map((o,i)=>`<button class="shaku-option" data-shaku-answer="${i}" onclick="answerShaku(${i})">${i+1}. ${o}</button>`).join('')}</div><div id="shakuFeedback"></div><p class="note" style="margin-top:14px">ID ${q.id} ・ 過去 ${st.correct||0}正解 / ${st.wrong||0}誤答</p></section>`}
function answerShaku(v){if(!shakuSession||shakuSession.answered)return;shakuSession.answered=true;const q=currentShakuQ(),ok=v===q.answer,ms=Date.now()-shakuSession.started;if(ok)shakuSession.correct++;shakuSession.answers.push({id:q.id,correct:ok,ms});const all=shakuStats(),x=all[q.id]||{attempts:0,correct:0,wrong:0,totalMs:0};x.attempts++;x[ok?'correct':'wrong']++;x.totalMs=(x.totalMs||0)+ms;x.lastAt=new Date().toISOString();all[q.id]=x;saveShakuStats(all);document.querySelectorAll('.shaku-option').forEach(b=>{b.disabled=true;const n=Number(b.dataset.shakuAnswer);if(n===q.answer)b.classList.add('ok');if(n===v&&!ok)b.classList.add('ng');if(n===v)b.classList.add('sel')});$('#shakuFeedback').innerHTML=`<div class="sort-feedback ${ok?'good':'bad'}"><h4 style="margin:0">${ok?'✅ 正解':'❌ 不正解'}　正解：${q.options[q.answer]}</h4><p>${q.exp}</p><div class="note">根拠：${q.basis} ・ ${(ms/1000).toFixed(1)}秒</div><button class="primary" style="margin-top:12px" onclick="nextShakuQ()">${shakuSession.idx+1===shakuSession.ids.length?'結果を見る':'次の問題'}</button></div>`}
function nextShakuQ(){shakuSession.idx++;shakuSession.answered=false;if(shakuSession.idx>=shakuSession.ids.length)renderShakuFinish();else renderShakuQuestion()}
function renderShakuFinish(){const total=shakuSession.ids.length,c=shakuSession.correct,p=Math.round(c/total*100),avg=shakuSession.answers.reduce((a,x)=>a+x.ms,0)/Math.max(1,shakuSession.answers.length)/1000;$('#sortView').innerHTML=`<section class="card" style="text-align:center"><div style="font-size:52px">${p>=90?'🎯':p>=70?'👍':'🏠'}</div><h2>${c} / ${total} 正解</h2><p class="note">正答率 ${p}% ・ 平均回答 ${avg.toFixed(1)}秒</p><button class="primary" onclick="renderShakuLanding()">借地借家法の成績へ</button><button class="secondary" style="margin-top:8px" onclick="renderDrillHub()">ドリル一覧へ</button></section>`;shakuSession=null}
function resetShakuStats(){if(confirm('借地借家法ドリルの学習履歴をリセットしますか？')){localStorage.removeItem(SHAKU_STATS_KEY);renderShakuLanding()}}
'''
s=s.replace('\ninitSortBank();',addon+'\ninitSortBank();')

# Ensure any surviving direct landing calls are still valid by adding compatibility alias.
if 'function renderSortLanding()' not in s:
    s=s.replace('function renderDrillHub(){','function renderSortLanding(){render3537Landing()}\nfunction renderDrillHub(){')

p.write_text(s,encoding='utf-8')
print('patched',len(s))
