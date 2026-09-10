// Run with: node scripts/test-shaku-bank.cjs
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
let checks=0;
function boot(seed={}){
 const values=new Map(Object.entries(seed)),elements=new Map();
 const element=()=>({innerHTML:'',textContent:'',style:{},classList:{add(){},remove(){},toggle(){}},addEventListener(){},dataset:{},value:''});
 const context=vm.createContext({console,Date,Math,JSON,Map,Set,Object,Number,String,Array,Boolean,confirm:()=>true,alert(){},setTimeout(){},localStorage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>values.set(k,String(v)),removeItem:k=>values.delete(k)},document:{querySelector:s=>{if(!elements.has(s))elements.set(s,element());return elements.get(s)},querySelectorAll:()=>[]}});
 vm.runInContext(script,context);
 return {run:s=>vm.runInContext(s,context),values,context,elements};
}
function test(name,fn){fn();checks++;console.log('PASS '+name)}
const oldStats=JSON.stringify({'shaku-0001':{attempts:2,correct:1,wrong:1,totalMs:3200,history:[{answer:1,correct:true,ms:1200}]},'shaku-0002':{attempts:3,correct:3,wrong:0,totalMs:6000}});
const app=boot({takkenShakuchiShakkaStatsV1:oldStats});
const run=app.run;
const bank=()=>JSON.parse(run('JSON.stringify(initShakuBank())'));
const incoming=(questions)=>({...bank(),questions});
const merge=b=>run('mergeShakuBank('+JSON.stringify(b)+')');
const q=bank().questions[0];
const unchangedKeys=()=>JSON.stringify([...app.values].filter(([k])=>!k.includes('ShakuchiShakka')));
const unrelated=unchangedKeys();
test('34 seed questions, stable IDs and unchanged legacy history',()=>{assert.equal(bank().questions.length,34);assert.deepEqual(bank().questions.map(q=>q.id),Array.from({length:34},(_,i)=>'shaku-'+String(i+1).padStart(4,'0')));assert.equal(app.values.get('takkenShakuchiShakkaStatsV1'),oldStats)});
test('same-version equality ignores property order',()=>assert.equal(merge(incoming([{...Object.fromEntries(Object.entries(q).reverse())}])).unchanged,1));
test('new question is added',()=>{assert.equal(merge(incoming([{...q,id:'shaku-0035'}])).added,1);assert.equal(bank().questions.length,35)});
test('explanation/basis/category/difficulty/source/flags update preserves history',()=>{const updated={...q,version:2,exp:q.exp+'追記',basis:'根拠追記',cat:'更新・終了',difficulty:'B',source:'更新',verified:true,active:false};const r=merge(incoming([updated]));assert.equal(r.updated,1);assert.equal(r.resetStats,0);assert.equal(app.values.get('takkenShakuchiShakkaStatsV1'),oldStats)});
test('older version is ignored',()=>{assert.equal(merge(incoming([q])).skippedOld,1);assert.equal(bank().questions[0].version,2)});
test('same-version conflict rejects entire batch',()=>{const before=JSON.stringify([...app.values]);assert.throws(()=>merge(incoming([{...q,id:'shaku-0036'},{...q,version:2}])),/同じversion/);assert.equal(JSON.stringify([...app.values]),before)});
test('changed answer resets only its own history',()=>{const r=merge(incoming([{...q,version:3,answer:0}]));assert.equal(r.resetStats,1);assert.equal(run("shakuStats()['shaku-0001']"),undefined);assert.equal(run("shakuStats()['shaku-0002'].attempts"),3)});
for(const [field,value] of [['prompt','別の問題文'],['options',['A','B','C','D']]])test(field+' change resets existing history',()=>{run("saveShakuStats({...shakuStats(),'shaku-0001':{attempts:1}})");const current=bank().questions[0];assert.equal(merge(incoming([{...current,version:current.version+1,[field]:value}])).resetStats,1)});
const invalids=[['format',b=>b.format='other'],['duplicate ID',b=>b.questions.push(b.questions[0])],['missing options',b=>b.questions[0].options=['a']],['answer out of range',b=>b.questions[0].answer=4],['negative answer',b=>b.questions[0].answer=-1],['string answer',b=>b.questions[0].answer='1'],['fractional version',b=>b.questions[0].version=1.2],['bad ID',b=>b.questions[0].id='__proto__'],['bad category',b=>b.questions[0].cat='other'],['invalid boolean',b=>b.questions[0].active='false'],['empty prompt',b=>b.questions[0].prompt=' '],['bad date',b=>b.lawBaseDate='2026-02-30'],['missing difficulty',b=>delete b.questions[0].difficulty]];
for(const [name,mutate] of invalids)test('reject '+name+' without writes',()=>{const b=incoming([{...q,id:'shaku-0036'}]);mutate(b);const before=JSON.stringify([...app.values]);assert.throws(()=>merge(b));assert.equal(JSON.stringify([...app.values]),before)});
test('quota failure restores both problem bank and history',()=>{const current=bank().questions[1],before=JSON.stringify([...app.values]);const set=app.context.localStorage.setItem;app.context.localStorage.setItem=(k,v)=>{if(k==='takkenShakuchiShakkaBankV1')throw Error('quota');return set(k,v)};assert.throws(()=>merge(incoming([{...current,version:2,answer:0}])),/保存できません/);app.context.localStorage.setItem=set;assert.equal(JSON.stringify([...app.values]),before)});
test('bank export round trips and includes inactive questions',()=>{run('downloadJSON=(data,name)=>{globalThis.exported={data,name}};exportShakuBank()');assert.equal(app.context.exported.data.questions.length,35);assert.equal(merge(app.context.exported.data).unchanged,35)});
test('analysis export includes added questions, time and legacy history',()=>{run('exportShakuAnalysis()');const d=app.context.exported.data;assert.equal(d.perQuestion.length,35);assert.equal(d.summary.questionCount,35);assert.equal(d.perQuestion.find(q=>q.id==='shaku-0002').averageSeconds,2);assert.equal(d.format,'takken-chatgpt-analysis-shakuchi-shakka-v1')});
test('reload preserves additions without duplicate seeds',()=>{const reloaded=boot(Object.fromEntries(app.values));assert.equal(reloaded.run('shakuQuestions().length'),35)});
test('normal quiz and 35/37 storage remain unchanged',()=>assert.equal(unchangedKeys(),unrelated));
test('selective history reset keeps bank and unrelated storage',()=>{const before=app.values.get('takkenShakuchiShakkaBankV1');run('resetShakuStats()');assert.equal(app.values.get('takkenShakuchiShakkaStatsV1'),undefined);assert.equal(app.values.get('takkenShakuchiShakkaBankV1'),before);assert.equal(unchangedKeys(),unrelated)});
console.log(checks+' checks passed');
const fresh=boot();
test('34 existing questions render and record answers and time',()=>{
 fresh.run("renderShakuLanding();document.querySelector('#shakuCat').value='all';document.querySelector('#shakuCount').value='all';startShakuDrill()");
 assert.equal(fresh.run('shakuSession.ids.length'),34);
 for(let i=0;i<34;i++){fresh.run('answerShaku(currentShakuQ().answer)');fresh.run('nextShakuQ()')}
 assert.equal(fresh.run('Object.keys(shakuStats()).length'),34);
 assert.equal(fresh.run('Object.values(shakuStats()).every(s=>s.attempts===1&&s.correct===1&&s.totalMs>=0&&s.history.length===1)'),true);
 assert.match(fresh.elements.get('#sortView').innerHTML,/34 \/ 34 正解/);
});
test('inactive questions are excluded, empty categories do not start a session',()=>{
 fresh.run("const offBank=initShakuBank();offBank.questions=offBank.questions.map(q=>({...q,version:2,active:false}));mergeShakuBank(offBank);renderShakuLanding();document.querySelector('#shakuCat').value='all';document.querySelector('#shakuCount').value='all';startShakuDrill()");
 assert.equal(fresh.run('shakuSession'),null);
});
test('imported HTML is escaped in questions, choices and feedback',()=>{
 fresh.run("const textBank=initShakuBank();textBank.questions=[{...textBank.questions[0],version:3,active:true,prompt:'<img src=x onerror=alert(1)>',options:['<b>x</b>','B','C','D'],exp:'<script>alert(1)</script>',basis:'<b>根拠</b>'}];mergeShakuBank(textBank);startShakuDrill()");
 assert.match(fresh.elements.get('#sortView').innerHTML,/&lt;img/);
 assert.doesNotMatch(fresh.elements.get('#sortView').innerHTML,/<img/);
 fresh.run('answerShaku(0)');assert.match(fresh.elements.get('#shakuFeedback').innerHTML,/&lt;script/);
});
test('35/37 and normal quiz still render, answer and export analysis',()=>{
 fresh.run("render3537Landing();document.querySelector('#sortMode').value='all';document.querySelector('#sortObject').value='all';document.querySelector('#sortTransaction').value='all';document.querySelector('#sortCount').value='10';startSortDrill();answerSort(currentSortQ().answer);downloadJSON=(data)=>{globalThis.analysis=data};exportSortAnalysis()");
 assert.equal(fresh.context.analysis.summary.totalAttempts,1);
 fresh.run("startMode('random',1);answer(true);exportQuizAnalysis()");
 assert.equal(fresh.context.analysis.summary.totalAttempts,1);
 fresh.run('renderHome();renderWeak();renderStats()');
});
(async()=>{
 await fresh.run("importShakuFile({text:async()=>JSON.stringify({...initShakuBank(),questions:[{...initShakuBank().questions[0],id:'shaku-0035',version:1}]})})");
 test('file import updates counts and success status',()=>assert.match(fresh.elements.get('#shakuImportStatus').textContent,/追加 1問.*合計 35問/));
 await fresh.run("importShakuFile({text:async()=>'{bad json'})");
 test('malformed JSON file displays a clear error',()=>assert.match(fresh.elements.get('#shakuImportStatus').textContent,/読み込み失敗/));
 console.log('TOTAL '+checks+' checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
