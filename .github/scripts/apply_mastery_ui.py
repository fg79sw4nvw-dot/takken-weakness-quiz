from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) mastery badge styles
css_anchor=".clickable{cursor:pointer}"
css_add=""".clickable{cursor:pointer}.mastery-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:14px}.mastery-stat{font-size:12px;color:var(--muted);background:#f8fafc;border:1px solid var(--line);padding:7px 9px;border-radius:999px}.mastery-badge{display:inline-flex;align-items:center;font-size:12px;font-weight:850;padding:7px 10px;border-radius:999px;border:1px solid transparent}.mastery-unlearned{background:#f1f5f9;color:#475569;border-color:#e2e8f0}.mastery-learning{background:#dbeafe;color:#1d4ed8;border-color:#bfdbfe}.mastery-candidate{background:#ffedd5;color:#c2410c;border-color:#fed7aa}.mastery-graduated{background:#dcfce7;color:#15803d;border-color:#bbf7d0}.mastery-change-list{display:grid;gap:9px;margin-top:12px;text-align:left}.mastery-change{border:1px solid var(--line);border-radius:14px;padding:11px 12px;background:#fff}.mastery-change.changed{background:#f8fffb;border-color:#bbf7d0}.mastery-change.regressed{background:#fffaf7;border-color:#fed7aa}.mastery-change-title{font-size:12px;font-weight:800;line-height:1.45;margin-bottom:7px}.mastery-arrow{color:var(--muted);font-weight:800;margin:0 5px}.mastery-summary{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:12px 0}.mastery-summary span{font-size:12px;font-weight:800;padding:7px 10px;border-radius:999px;background:#f8fafc;border:1px solid var(--line)}"""
if '.mastery-badge{' not in s:
    if css_anchor not in s: raise SystemExit('css anchor missing')
    s=s.replace(css_anchor,css_add,1)

# 2) add session mastery snapshot variable + helpers after reconcileMastery
anchor="function reconcileMastery(){let changed=false;for(const q of state.questions){const before=JSON.stringify([q.active,q.inactiveReason,q.graduatedAt,q.masteryStage]);applyMasteryFor(q.id,{retroactive:true});const after=JSON.stringify([q.active,q.inactiveReason,q.graduatedAt,q.masteryStage]);if(before!==after)changed=true}if(changed)save()}"
add="""
let sessionMasteryStart={};
const MASTERY_ORDER={unlearned:0,learning:1,candidate:2,graduated:3};
function masteryBadge(m){return `<span class=\"mastery-badge mastery-${m.stageKey}\">${m.stageKey==='graduated'?'🎓 ':m.stageKey==='candidate'?'🔥 ':m.stageKey==='learning'?'📘 ':'○ '}${m.stage}</span>`}
function masterySnapshot(id){const m=masteryFor(id);return{stage:m.stage,stageKey:m.stageKey}}
function masteryChangeClass(before,after){const d=(MASTERY_ORDER[after.stageKey]??0)-(MASTERY_ORDER[before.stageKey]??0);return d>0?'changed':d<0?'regressed':''}
"""
if 'let sessionMasteryStart={};' not in s:
    if anchor not in s: raise SystemExit('mastery helper anchor missing')
    s=s.replace(anchor,anchor+add,1)

# 3) snapshot stages when session begins
old="if(m==='weak'||m==='today')session=pickWeighted(n);else session=ids.sort(()=>Math.random()-.5).slice(0,n);idx=0;answered=false;sessionStartAnswerCount=state.answers.length;show('quiz');renderQuestion()"
new="if(m==='weak'||m==='today')session=pickWeighted(n);else session=ids.sort(()=>Math.random()-.5).slice(0,n);idx=0;answered=false;sessionStartAnswerCount=state.answers.length;sessionMasteryStart=Object.fromEntries(session.map(id=>[id,masterySnapshot(id)]));show('quiz');renderQuestion()"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('start session anchor missing')

# 4) question screen: accuracy + mastery badge side by side
old="let h=historyFor(id),r=h.length?Math.round(h.filter(x=>x.correct).length/h.length*100):null;$('#quizView').innerHTML=`<section class=\"card\"><div class=\"quiz-head\"><span>${idx+1} / ${session.length}</span><span>${modeName()}</span></div><div style=\"display:flex;justify-content:space-between;align-items:center;gap:8px\"><span class=\"qtag\">${esc(q.cat)} ・ ${esc(q.topic)} ・ 難易度${esc(q.diff)}</span><button class=\"iconbtn ${q.favorite?'fav':''}\" onclick=\"toggleFavorite('${q.id}',true)\">${q.favorite?'★':'☆'}</button></div><div class=\"question\">${esc(q.q)}</div><div class=\"answer-grid\"><button id=\"yes\" class=\"answer\" onclick=\"answer(true)\">○</button><button id=\"no\" class=\"answer\" onclick=\"answer(false)\">×</button></div><div id=\"feedback\"></div>${r===null?'':`<p class=\"note\" style=\"margin-top:14px\">この問題のあなたの正答率：${r}%</p>`}</section>`"
new="let h=historyFor(id),r=h.length?Math.round(h.filter(x=>x.correct).length/h.length*100):null,mst=masteryFor(id);$('#quizView').innerHTML=`<section class=\"card\"><div class=\"quiz-head\"><span>${idx+1} / ${session.length}</span><span>${modeName()}</span></div><div style=\"display:flex;justify-content:space-between;align-items:center;gap:8px\"><span class=\"qtag\">${esc(q.cat)} ・ ${esc(q.topic)} ・ 難易度${esc(q.diff)}</span><button class=\"iconbtn ${q.favorite?'fav':''}\" onclick=\"toggleFavorite('${q.id}',true)\">${q.favorite?'★':'☆'}</button></div><div class=\"question\">${esc(q.q)}</div><div class=\"answer-grid\"><button id=\"yes\" class=\"answer\" onclick=\"answer(true)\">○</button><button id=\"no\" class=\"answer\" onclick=\"answer(false)\">×</button></div><div id=\"feedback\"></div><div class=\"mastery-row\">${r===null?'<span class=\"mastery-stat\">正答率：未回答</span>':`<span class=\"mastery-stat\">正答率：${r}%</span>`}${masteryBadge(mst)}</div></section>`"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('renderQuestion anchor missing')

# 5) result screen with stage changes
old="function renderFinish(){let ids=session.slice(),recent=state.answers.slice(sessionStartAnswerCount),c=recent.filter(x=>x.correct).length,p=ids.length?Math.round(c/ids.length*100):0;$('#quizView').innerHTML=`<section class=\"card\" style=\"text-align:center\"><div style=\"font-size:54px\">${p>=80?'🎉':p>=60?'👍':'🧠'}</div><h2>${c} / ${ids.length} 正解</h2><div style=\"font-size:30px;font-weight:800;margin:8px 0\">${p}%</div><p class=\"note\">今回の${ids.length}問の結果です。学習結果を弱点判定に反映しました。</p><button class=\"secondary\" onclick=\"show('home')\">ホームへ</button></section>`;session=[];renderHome()}"
new="""function renderFinish(){let ids=session.slice(),recent=state.answers.slice(sessionStartAnswerCount),c=recent.filter(x=>x.correct).length,p=ids.length?Math.round(c/ids.length*100):0;const changes=ids.map(id=>{const q=getQ(id),before=sessionMasteryStart[id]||masterySnapshot(id),after=masterySnapshot(id),cls=masteryChangeClass(before,after),delta=(MASTERY_ORDER[after.stageKey]??0)-(MASTERY_ORDER[before.stageKey]??0);return{id,q,before,after,cls,delta}});const advanced=changes.filter(x=>x.delta>0).length,graduated=changes.filter(x=>x.before.stageKey!=='graduated'&&x.after.stageKey==='graduated').length,regressed=changes.filter(x=>x.delta<0).length;const rows=changes.map(x=>`<div class=\"mastery-change ${x.cls}\"><div class=\"mastery-change-title\">${esc(x.q?.topic||'')}｜${esc((x.q?.q||'').slice(0,54))}${(x.q?.q||'').length>54?'…':''}</div><div>${masteryBadge(x.before)}<span class=\"mastery-arrow\">→</span>${masteryBadge(x.after)}${x.delta>0?'<span style=\"margin-left:7px;font-size:12px;font-weight:800;color:#15803d\">進歩</span>':x.delta<0?'<span style=\"margin-left:7px;font-size:12px;font-weight:800;color:#c2410c\">要復習</span>':'<span style=\"margin-left:7px;font-size:12px;color:var(--muted)\">維持</span>'}</div></div>`).join('');$('#quizView').innerHTML=`<section class=\"card\" style=\"text-align:center\"><div style=\"font-size:54px\">${p>=80?'🎉':p>=60?'👍':'🧠'}</div><h2>${c} / ${ids.length} 正解</h2><div style=\"font-size:30px;font-weight:800;margin:8px 0\">${p}%</div><p class=\"note\">今回の${ids.length}問の結果です。正答だけでなく、定着の進み方も記録しました。</p><div class=\"mastery-summary\"><span>⬆️ 段階アップ ${advanced}問</span><span>🎓 卒業 ${graduated}問</span>${regressed?`<span>↩️ 要復習 ${regressed}問</span>`:''}</div></section><section class=\"card\"><h3 style=\"margin-top:0\">今回の定着段階</h3><p class=\"note\">開始時 → 終了時。変化があった問題は強調表示しています。</p><div class=\"mastery-change-list\">${rows}</div><button class=\"secondary\" style=\"margin-top:14px\" onclick=\"show('home')\">ホームへ</button></section>`;session=[];sessionMasteryStart={};renderHome()}"""
if old in s:
    s=s.replace(old,new,1)
elif '今回の定着段階' not in s:
    raise SystemExit('renderFinish anchor missing')

p.write_text(s,encoding='utf-8')
print('mastery progress UI patched')
