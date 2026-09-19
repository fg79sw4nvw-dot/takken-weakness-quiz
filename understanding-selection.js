// Understanding-first selection layer.
// Canonical rationale: QUESTION_SELECTION_POLICY.md

const UNDERSTANDING_ROLES=['core','boundary','contrast','exception','application'];
const UNDERSTANDING_ROLE_LABELS={
  core:'核',
  boundary:'境界',
  contrast:'比較',
  exception:'例外',
  application:'具体例・応用'
};

function understandingRole(q){
  return UNDERSTANDING_ROLES.includes(q?.learningRole)?q.learningRole:'';
}

function answerProfile(id){
  const h=historyFor(id).slice().sort((a,b)=>(a.ts||0)-(b.ts||0));
  const attempts=h.length;
  const recent=h.slice(-5);
  const recentAccuracy=recent.length?recent.filter(x=>x.correct).length/recent.length:null;
  let streak=0;
  for(let i=h.length-1;i>=0&&h[i].correct;i--)streak++;
  const last=h.at(-1)||null;
  const days=last?.ts?Math.max(0,(Date.now()-last.ts)/86400000):Infinity;
  return{
    h,attempts,recentAccuracy,streak,last,
    lastWrong:last?last.correct===false:false,
    days
  };
}

function understandingPriority(q){
  const p=answerProfile(q.id);
  const m=masteryFor(q.id);
  let w=1;

  // New material matters because understanding cannot have gaps hidden behind repeated familiar items.
  if(!p.attempts)w+=1.2;

  // Recent misunderstanding is the strongest signal.
  if(p.lastWrong)w+=1.35;
  if(p.recentAccuracy!==null)w+=(1-p.recentAccuracy)*1.4;

  // Spaced retrieval: correct knowledge returns after some time instead of immediately looping.
  if(Number.isFinite(p.days)){
    if(p.days>=7)w+=.65;
    else if(p.days>=3)w+=.35;
    else if(p.days<.5&&p.last?.correct)w*=.55;
  }

  // Learning stage matters, but difficulty itself does not determine priority.
  if(m.stageKey==='unlearned')w*=1.15;
  else if(m.stageKey==='learning')w*=1.25;
  else if(m.stageKey==='candidate')w*=1.12;

  // Stable consecutive recall lowers urgency without making the item disappear forever.
  w-=Math.min(p.streak,4)*.12;

  if(q.favorite)w*=1.06;
  return Math.max(.12,w);
}

// Only verified material enters ordinary study sessions.
// Unverified questions stay available in management for review.
activeQs=function(){
  return state.questions.filter(q=>q.active!==false&&q.verified===true);
};

function reconcileVerification(){
  let changed=false;
  for(const q of state.questions){
    if(q.verified!==true&&q.active!==false){
      q.active=false;
      q.inactiveReason='unverified';
      changed=true;
    }
  }
  if(changed)save();
}

const _normalizeImportedUnderstanding=normalizeImported;
normalizeImported=function(x){
  const q=_normalizeImportedUnderstanding(x);
  q.learningRole=UNDERSTANDING_ROLES.includes(String(x.learningRole||x.role||''))
    ?String(x.learningRole||x.role):'';
  q.conceptKey=String(x.conceptKey||x.concept||'').trim();
  q.basis=String(x.basis||x.legalBasis||'').trim();
  q.lawBaseDate=String(x.lawBaseDate||'').trim();
  if(q.verified!==true){
    q.active=false;
    q.inactiveReason='unverified';
  }
  return q;
};

const _toggleActiveUnderstanding=toggleActive;
toggleActive=function(id){
  const q=getQ(id);
  if(q&&q.active===false&&q.verified!==true){
    alert('未確認の問題は通常出題に戻せません。内容・根拠を確認して「確認済み」にしてから出題ONにしてください。');
    return;
  }
  _toggleActiveUnderstanding(id);
};

const _saveEditorUnderstanding=saveEditor;
saveEditor=function(id){
  const verified=$('#edV')?.value==='true';
  const on=$('#edOn');
  if(on&&!verified)on.checked=false;
  _saveEditorUnderstanding(id);
  const q=id?getQ(id):state.questions[0];
  if(q&&q.verified!==true){
    q.active=false;
    q.inactiveReason='unverified';
    save();
  }
};

pickWeighted=function(n,filter=()=>true){
  let pool=activeQs().filter(filter).map(q=>({q,base:understandingPriority(q)}));
  const out=[];
  const topicCount={};
  const roleCount={};

  while(pool.length&&out.length<n){
    const weighted=pool.map(x=>{
      const topic=x.q.topic||'';
      const role=understandingRole(x.q);
      const tc=topicCount[topic]||0;
      const rc=role?(roleCount[role]||0):0;
      let diversity=tc===0?1:tc===1?.62:.24;

      // In explicit theme training, topic concentration is intended.
      if(mode==='topic')diversity=1;

      if(role){
        if(rc>=2)diversity*=.72;
        else if(rc===1)diversity*=.9;
      }

      // "Weak" mode can concentrate somewhat more strongly on actual misses.
      if(mode==='weak'&&answerProfile(x.q.id).lastWrong)diversity*=1.2;

      return{...x,w:Math.max(.02,x.base*diversity)};
    });

    let sum=weighted.reduce((s,x)=>s+x.w,0);
    let r=Math.random()*sum;
    let chosen=0;
    for(let i=0;i<weighted.length;i++){
      r-=weighted[i].w;
      if(r<=0){chosen=i;break}
    }

    const selected=pool.splice(chosen,1)[0].q;
    out.push(selected.id);
    topicCount[selected.topic||'']=(topicCount[selected.topic||'']||0)+1;
    const role=understandingRole(selected);
    if(role)roleCount[role]=(roleCount[role]||0)+1;
  }

  return out;
};

reconcileVerification();
renderHome();
