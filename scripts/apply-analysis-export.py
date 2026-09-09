from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Remove the bottom quiz tab, keep quizView for flows launched from Home.
s=s.replace('<button data-view="quiz"><span class="ico">🧠</span>一問一答</button>','')
s=s.replace('grid-template-columns:repeat(5,1fr)','grid-template-columns:repeat(4,1fr)')

# 2) Enrich drill stats with per-attempt history going forward.
s=s.replace("s.version=q.version??1;all[q.id]=s;setSortStats(all);", "s.version=q.version??1;s.history=Array.isArray(s.history)?s.history:[];s.history.push({at:new Date().toISOString(),answer:val,correct:ok,ms});if(s.history.length>200)s.history=s.history.slice(-200);all[q.id]=s;setSortStats(all);")
s=s.replace("x.totalMs=(x.totalMs||0)+ms;x.lastAt=new Date().toISOString();all[q.id]=x;saveShakuStats(all);", "x.totalMs=(x.totalMs||0)+ms;x.lastAnswer=v;x.lastAt=new Date().toISOString();x.history=Array.isArray(x.history)?x.history:[];x.history.push({at:x.lastAt,answer:v,correct:ok,ms});if(x.history.length>200)x.history=x.history.slice(-200);all[q.id]=x;saveShakuStats(all);")

# 3) Add export buttons to the three relevant places.
quiz_toolbar='<div class="toolbar"><button class="smallbtn" onclick="exportQuestions()">問題JSON</button><button class="smallbtn" onclick="exportBackup()">完全バックアップ</button></div>'
quiz_toolbar_new='<div class="toolbar"><button class="smallbtn" onclick="exportQuestions()">問題JSON</button><button class="smallbtn" onclick="exportBackup()">完全バックアップ</button><button class="smallbtn primaryish" onclick="exportQuizAnalysis()">ChatGPT分析用JSON</button></div>'
s=s.replace(quiz_toolbar,quiz_toolbar_new)

sort_button='<button class="secondary" style="margin-top:10px" onclick="exportSortBank()">現在の問題JSONを書き出す</button>'
sort_button_new='<button class="secondary" style="margin-top:10px" onclick="exportSortAnalysis()">ChatGPT分析用JSONを書き出す</button>'+sort_button
s=s.replace(sort_button,sort_button_new)

shaku_reset='<button class="secondary danger" onclick="resetShakuStats()">借地借家法の学習履歴をリセット</button>'
shaku_reset_new='<button class="secondary" style="margin-bottom:10px" onclick="exportShakuAnalysis()">ChatGPT分析用JSONを書き出す</button>'+shaku_reset
s=s.replace(shaku_reset,shaku_reset_new)

# 4) Inject structured analysis exporters once.
marker="function exportQuestions(){downloadJSON({format:'takken-question-bank-v1'"
if 'function exportQuizAnalysis()' not in s:
    insert=r'''function pct(c,t){return t?Math.round(c/t*100):0}
function exportQuizAnalysis(){
  const qs=state.questions||[],ans=state.answers||[],active=qs.filter(q=>q.active!==false),qmap=new Map(qs.map(q=>[q.id,q]));
  const group=(keyFn)=>{const m={};for(const a of ans){const q=qmap.get(a.qid);if(!q)continue;const k=keyFn(q,a);if(!k)continue;if(!m[k])m[k]={attempts:0,correct:0};m[k].attempts++;if(a.correct)m[k].correct++}return Object.fromEntries(Object.entries(m).map(([k,v])=>[k,{...v,wrong:v.attempts-v.correct,accuracy:pct(v.correct,v.attempts)}]))};
  const daily={};for(const a of ans){const d=a.date||new Date(a.ts||Date.now()).toLocaleDateString('sv-SE');if(!daily[d])daily[d]={attempts:0,correct:0};daily[d].attempts++;if(a.correct)daily[d].correct++}for(const v of Object.values(daily)){v.wrong=v.attempts-v.correct;v.accuracy=pct(v.correct,v.attempts)}
  const perQuestion=qs.map(q=>{const h=ans.filter(a=>a.qid===q.id).sort((a,b)=>(a.ts||0)-(b.ts||0)),c=h.filter(a=>a.correct).length,recent=h.slice(-5),rc=recent.filter(a=>a.correct).length;let streak=0;for(let i=h.length-1;i>=0&&h[i].correct;i--)streak++;return{id:q.id,category:q.cat,topic:q.topic,difficulty:q.diff,active:q.active!==false,favorite:!!q.favorite,question:q.q,attempts:h.length,correct:c,wrong:h.length-c,accuracy:pct(c,h.length),recent5Accuracy:pct(rc,recent.length),currentCorrectStreak:streak,lastAnsweredAt:h.length?(h[h.length-1].ts||null):null}}).filter(x=>x.attempts>0);
  const data={format:'takken-chatgpt-analysis-quiz-v1',exportedAt:new Date().toISOString(),source:'通常一問一答',responseTimeAvailable:false,summary:{registeredQuestions:qs.length,activeQuestions:active.length,totalAttempts:ans.length,correct:ans.filter(a=>a.correct).length,wrong:ans.filter(a=>!a.correct).length,accuracy:pct(ans.filter(a=>a.correct).length,ans.length),streak:state.streak||0,lastStudy:state.lastStudy||null},byCategory:group(q=>q.cat),byTopic:group(q=>q.topic),byDifficulty:group(q=>q.diff),daily,mistakeReasons:state.mistakeReasons||{},perQuestion,history:ans.map(a=>({qid:a.qid,correct:!!a.correct,date:a.date||null,ts:a.ts||null}))};
  downloadJSON(data,`takken-analysis-quiz-${today()}.json`)
}
function exportSortAnalysis(){
  const qs=sortQuestions(),st=sortStats(),perf=sortPerformanceStats();
  const perQuestion=qs.map(q=>{const x=st[q.id]||{},a=x.attempts||0,c=x.correct||0;return{id:q.id,objectType:q.objectType,transactionType:q.transactionType,conditions:q.conditions||{},prompt:q.prompt,correctClass:q.answer,correctLabel:SORT_LABELS[q.answer],attempts:a,correct:c,wrong:x.wrong||0,accuracy:pct(c,a),averageSeconds:a?Math.round(((x.totalMs||0)/a)/100)/10:null,lastAnswer:x.lastAnswer||null,lastAt:x.lastAt||null,history:Array.isArray(x.history)?x.history:[]}});
  const data={format:'takken-chatgpt-analysis-3537-v1',exportedAt:new Date().toISOString(),source:'35条・37条仕分けドリル',lawBaseDate:initSortBank().lawBaseDate||null,summary:{questionCount:qs.length,totalAttempts:perf.attempts,correct:perf.correct,wrong:perf.attempts-perf.correct,accuracy:perf.rate,averageSeconds:perf.avg===null?null:Math.round(perf.avg*10)/10},byClassification:perf.rows.map(r=>({...r,wrong:r.attempts-r.correct})),perQuestion};
  downloadJSON(data,`takken-analysis-3537-${today()}.json`)
}
function exportShakuAnalysis(){
  const st=shakuStats(),cats=shakuCategoryStats(),attempts=Object.values(st).reduce((a,x)=>a+(x.attempts||0),0),correct=Object.values(st).reduce((a,x)=>a+(x.correct||0),0),totalMs=Object.values(st).reduce((a,x)=>a+(x.totalMs||0),0);
  const perQuestion=SHAKU_QUESTIONS.map(q=>{const x=st[q.id]||{},a=x.attempts||0,c=x.correct||0;return{id:q.id,category:q.cat,prompt:q.prompt,options:q.options,correctAnswerIndex:q.answer,correctAnswer:q.options[q.answer],basis:q.basis,attempts:a,correct:c,wrong:x.wrong||0,accuracy:pct(c,a),averageSeconds:a?Math.round(((x.totalMs||0)/a)/100)/10:null,lastAnswerIndex:Number.isInteger(x.lastAnswer)?x.lastAnswer:null,lastAnswer:Number.isInteger(x.lastAnswer)?q.options[x.lastAnswer]:null,lastAt:x.lastAt||null,history:Array.isArray(x.history)?x.history:[]}});
  const data={format:'takken-chatgpt-analysis-shakuchi-shakka-v1',exportedAt:new Date().toISOString(),source:'借地借家法ドリル',summary:{questionCount:SHAKU_QUESTIONS.length,totalAttempts:attempts,correct,wrong:attempts-correct,accuracy:pct(correct,attempts),averageSeconds:attempts?Math.round((totalMs/attempts)/100)/10:null},byCategory:cats.map(x=>({...x,wrong:x.attempts-x.correct})),perQuestion};
  downloadJSON(data,`takken-analysis-shakuchi-shakka-${today()}.json`)
}
'''
    s=s.replace(marker,insert+marker)

p.write_text(s,encoding='utf-8')
