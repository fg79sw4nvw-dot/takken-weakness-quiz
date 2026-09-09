from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# 1) Make the object / transaction chips easier to read.
old_css = ".sort-meta{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0}.sort-chip{font-size:11px;font-weight:800;padding:6px 8px;border-radius:999px;background:#e0ecff;color:#1d4ed8}"
new_css = ".sort-meta{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.sort-chip{font-size:12px;font-weight:800;padding:7px 9px;border-radius:999px;background:#e0ecff;color:#1d4ed8}.sort-meta>.sort-chip:nth-child(-n+2){font-size:15px;padding:9px 12px;line-height:1.2}"
if old_css in text:
    text = text.replace(old_css, new_css, 1)
elif new_css not in text:
    raise SystemExit('Could not find sort chip CSS')

# 2) Add more unambiguous “both” questions. They are appended to SORT_SEED,
#    then initSortBank migrates missing IDs into an existing local bank.
labels_line = "const SORT_LABELS={'35_only':'35条のみ','37_only':'37条のみ','both':'両方','neither':'どちらでもない'};"
addition = r'''
const SORT_ADDITIONAL_BOTH=[
{id:'3537-0046',version:1,objectType:'建物',transactionType:'売買・交換',conditions:{hasProvision:true},prompt:'代金以外に授受される金銭の額と授受の目的',answer:'both',explanation:'建物の売買・交換でも、代金以外の金銭は35条で額・目的を説明し、契約に定めがあれば37条にも記載する。37条では授受時期も記載事項となる。',legalBasis:'宅建業法35条1項7号、37条1項6号',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0047',version:1,objectType:'土地',transactionType:'貸借',conditions:{hasProvision:true},prompt:'借賃以外に授受される金銭の額と授受の目的',answer:'both',explanation:'宅地の貸借でも、借賃以外の金銭は35条で額・目的を説明し、37条書面にも額・授受時期・目的を記載する。',legalBasis:'宅建業法35条1項7号、37条2項3号',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0048',version:1,objectType:'建物',transactionType:'売買・交換',conditions:{hasProvision:true},prompt:'契約の解除に関する事項',answer:'both',explanation:'解除に関する事項は契約前に35条で説明し、契約に定めがある場合は37条書面にも記載する。',legalBasis:'宅建業法35条1項8号、37条1項7号',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0049',version:1,objectType:'土地',transactionType:'貸借',conditions:{hasProvision:true},prompt:'契約の解除に関する事項',answer:'both',explanation:'宅地の貸借でも解除に関する事項は35条の説明対象で、定めがある場合は37条書面にも記載する。',legalBasis:'宅建業法35条1項8号、37条2項1号（1項7号を準用）',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0050',version:1,objectType:'建物',transactionType:'売買・交換',conditions:{hasProvision:true},prompt:'損害賠償額の予定または違約金に関する事項',answer:'both',explanation:'損害賠償額の予定や違約金は35条で事前に説明し、契約に定めがある場合は37条書面にも記載する。',legalBasis:'宅建業法35条1項9号、37条1項8号',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0051',version:1,objectType:'土地',transactionType:'貸借',conditions:{hasProvision:true},prompt:'損害賠償額の予定または違約金に関する事項',answer:'both',explanation:'宅地の貸借でも、損害賠償額の予定や違約金は35条の説明対象で、定めがある場合は37条書面にも記載する。',legalBasis:'宅建業法35条1項9号、37条2項1号（1項8号を準用）',category:'宅建業法',topic:'35条・37条書面',difficulty:'A',verified:true,active:true},
{id:'3537-0052',version:1,objectType:'建物',transactionType:'売買・交換',conditions:{hasProvision:true},prompt:'代金についての金銭貸借のあっせんが成立しないときの措置',answer:'both',explanation:'住宅ローン等の金銭貸借のあっせんに関する所定事項は35条で説明し、契約に定めがある場合は37条書面にも記載する。',legalBasis:'宅建業法35条1項12号、37条1項9号',category:'宅建業法',topic:'35条・37条書面',difficulty:'B',verified:true,active:true}
];
for(const q of SORT_ADDITIONAL_BOTH){if(!SORT_SEED.questions.some(x=>x.id===q.id))SORT_SEED.questions.push(q)};'''
if 'const SORT_ADDITIONAL_BOTH=' not in text:
    if labels_line not in text:
        raise SystemExit('Could not find SORT_LABELS line')
    text = text.replace(labels_line, labels_line + addition, 1)

# 3) Migrate newly bundled seed questions into browsers that already have a bank.
old_init = "function initSortBank(){let b=sortBank();if(!b){b=JSON.parse(JSON.stringify(SORT_SEED));setSortBank(b)}return b}"
new_init = "function initSortBank(){let b=sortBank();if(!b){b=JSON.parse(JSON.stringify(SORT_SEED));setSortBank(b);return b}const ids=new Set((b.questions||[]).map(q=>q.id));let changed=false;for(const q of SORT_SEED.questions){if(!ids.has(q.id)){b.questions.push(JSON.parse(JSON.stringify(q)));ids.add(q.id);changed=true}}if(changed){b.questions.sort((a,b)=>String(a.id).localeCompare(String(b.id)));b.lawBaseDate=SORT_SEED.lawBaseDate||b.lawBaseDate;b.examYear=SORT_SEED.examYear||b.examYear;setSortBank(b)}return b}"
if old_init in text:
    text = text.replace(old_init, new_init, 1)
elif new_init not in text:
    raise SystemExit('Could not find initSortBank')

# 4) Show 35/37 results with the same horizontal-bar visual language as the main stats screen.
if 'function sortPerformanceStats()' not in text:
    pattern = re.compile(r"function renderSortLanding\(\)\{.*?\}\nfunction startSortDrill", re.S)
    match = pattern.search(text)
    if not match:
        raise SystemExit('Could not find renderSortLanding block')
    replacement = r'''function sortPerformanceStats(){const qs=sortQuestions(),st=sortStats();let attempts=0,correct=0,totalMs=0;const rows=Object.entries(SORT_LABELS).map(([key,label])=>{let a=0,c=0,ms=0;for(const q of qs.filter(q=>q.answer===key)){const s=st[q.id];if(!s)continue;a+=s.attempts||0;c+=s.correct||0;ms+=s.totalMs||0}attempts+=a;correct+=c;totalMs+=ms;return{key,label,attempts:a,correct:c,rate:a?Math.round(c/a*100):0}});return{rows,attempts,correct,rate:attempts?Math.round(correct/attempts*100):0,avg:attempts?totalMs/attempts/1000:null}}
function sortStatsGraphHtml(){const x=sortPerformanceStats();return `<section class="card"><h3 style="margin-top:0">仕分け成績</h3><div class="grid"><div class="mini"><b>${x.attempts?x.rate+'%':'-'}</b><span>総合正答率</span></div><div class="mini"><b>${x.avg===null?'-':x.avg.toFixed(1)+'秒'}</b><span>平均回答時間</span></div></div>${x.rows.map(r=>`<div class="stat-row"><div class="line"><b>${r.label}</b><span>${r.attempts?`${r.correct}/${r.attempts}（${r.rate}%）`:'未回答'}</span></div><div class="bar"><i style="width:${r.rate}%"></i></div></div>`).join('')}</section>`}
function renderSortLanding(){initSortBank();const v=$('#sortView');v.innerHTML=`<section class="card"><h2 style="margin-top:0">35条・37条 仕分けドリル</h2><p class="note">目的物と取引類型まで見て、「35条のみ・37条のみ・両方・どちらでもない」を瞬時に仕分けます。</p><div class="pill" style="display:inline-block;margin-top:6px">${sortStatusText()}</div><div class="sort-controls"><label class="note">出題モード<select id="sortMode" class="sort-select"><option value="all">全項目</option><option value="wrong">間違えた項目だけ</option></select></label><label class="note">出題数<select id="sortCount" class="sort-select"><option value="10">10問</option><option value="20">20問</option><option value="all">全問</option></select></label><label class="note">目的物<select id="sortObject" class="sort-select"><option value="all">すべて</option><option value="土地">土地</option><option value="建物">建物</option></select></label><label class="note">取引<select id="sortTransaction" class="sort-select"><option value="all">すべて</option><option value="売買・交換">売買・交換</option><option value="貸借">貸借</option></select></label></div><button class="primary" style="margin-top:12px" onclick="startSortDrill()">仕分けドリルを開始</button></section>${sortStatsGraphHtml()}<section class="card"><h3 style="margin-top:0">問題データ管理</h3><p class="note">ChatGPTで修正したJSONを読み込むと、同じIDの問題を更新します。古いversionは上書きしません。正答や取引条件が変わった問題だけ、その問題の学習統計をリセットします。</p><input id="sortImport" class="sort-file" type="file" accept="application/json,.json" onchange="importSortFile(this.files[0])"><div id="sortImportStatus" class="note" style="margin-top:8px">内蔵問題 ${sortQuestions().length}問</div><button class="secondary" style="margin-top:10px" onclick="exportSortBank()">現在の問題JSONを書き出す</button><button class="secondary danger" style="margin-top:10px" onclick="resetSortStats()">仕分け学習履歴をリセット</button><div class="sort-bank-list">${sortQuestions().map(q=>`<div class="sort-bank-row"><div><span class="sort-id">${q.id} / v${q.version??1}</span></div><b>${q.prompt}</b><div class="note">${q.objectType}・${q.transactionType} → ${SORT_LABELS[q.answer]}</div></div>`).join('')}</div></section>`}
function startSortDrill'''
    text = text[:match.start()] + replacement + text[match.end():]

path.write_text(text, encoding='utf-8')
print('Applied 35/37 drill improvements')
