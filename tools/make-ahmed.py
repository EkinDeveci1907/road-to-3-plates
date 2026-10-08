#!/usr/bin/env python3
"""Build Ahmed's copy of the app from this repo's index.html.

Both apps are the same code. Ahmed's differs only in: the name at the top, a
setup screen for his own starting numbers, no pre-loaded logs, and its own
storage keys (tpf.* instead of r235.*) so the two never mix.

    python3 tools/make-ahmed.py index.html  ../Ahmed/index.html
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'make-ahmed: expected {count} of {old[:80]!r}, found {n}')
    s = s.replace(old, new)


def rep_re(pattern, new):
    global s
    s, n = re.subn(pattern, new, s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f'make-ahmed: pattern not found: {pattern[:80]!r}')


# ---- name ----
rep('<title>Road to 3 Plates</title>', '<title>Ahmed’s Road to 3 Plates</title>')
rep('<p class="brand">Road to 3 Plates</p>', '<p class="brand">Ahmed’s Road to 3 Plates</p>')
rep('.actions-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}\n',
    '.actions-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}\nbody.setup .tabs,body.setup .gear{display:none}\n')

# ---- plan: Ahmed's targets come from his setup numbers, not Eko's ----
rep_re(r"var PLAN_START=new Date\(2026,8,28\), DELOAD_WEEK=8, GOAL=315, BEST_BENCH=\{w:235,r:3\};\nvar BENCH_TOP=\[.*?\];\nvar SQUAT_TOP=\[.*?\];\n",
       "var PROF=(function(){try{return JSON.parse(localStorage.getItem('tpf.profile'))}catch(e){return null}})();\n"
       "function mondayOf(d){var x=new Date(d.getFullYear(),d.getMonth(),d.getDate());x.setDate(x.getDate()-((x.getDay()+6)%7));return x;}\n"
       "var B0=PROF?PROF.bench:135,S0=PROF?PROF.squat:135,BWG=PROF&&PROF.bwGoal?PROF.bwGoal:155;\n"
       "var PLAN_START=PROF&&PROF.start?new Date(PROF.start[0],PROF.start[1],PROF.start[2]):mondayOf(new Date()), DELOAD_WEEK=8, GOAL=315, BEST_BENCH=null;\n"
       "function block(b,adds,reps){return adds.map(function(a,i){return a==='DL'?'DL':[b+a,reps[i]]});}\n"
       "var BENCH_TOP=block(B0,[0,5,10,10,15,20,20,25,'DL',30,35],['5','5','5','5','5','4–5','4–5','4','DL','3','3']);\n"
       "var SQUAT_TOP=block(S0,[0,5,10,15,20,25,30,35,'DL',40,45],['5','5','5','5','4–5','4–5','4','4','DL','3–4','3']);\n")
rep(",hint:'Start with the 60 lb dumbbells and keep your form clean.'}", "}")
rep(",hint:'Start at +30 lbs.'}", "}")
rep_re(r"var START_W=\{.*?\};\nvar OLD_LOGS=\[\n.*?\n\];\n", "var START_W={};\nvar OLD_LOGS=[];\n")
rep("if(bt==='DL'){o.benchTop={w:185,reps:'3',sets:1,easy:true};o.benchBack={w:155,reps:'6',sets:1};o.benchVol={w:135,reps:'8',sets:2};o.benchHeavy={w:165,reps:'3',sets:1,easy:true};}",
    "if(bt==='DL'){o.benchTop={w:B0,reps:'3',sets:1,easy:true};o.benchBack={w:r5(B0*0.85),reps:'6',sets:1};o.benchVol={w:r5(B0*0.72),reps:'8',sets:2};o.benchHeavy={w:r5(B0*0.9),reps:'3',sets:1,easy:true};}")
rep("if(i===10)o.benchTop.extra='If 225 lbs flies up, try 235 lbs × 1–3 with a spotter.';", "")
rep("if(st==='DL'){o.squatTop={w:185,reps:'3',sets:1,easy:true};o.squatBack={w:155,reps:'6',sets:1};}",
    "if(st==='DL'){o.squatTop={w:S0,reps:'3',sets:1,easy:true};o.squatBack={w:r5(S0*0.85),reps:'6',sets:1};}")
rep("if(!best) return {w:185,reps:'5',sets:1};", "if(!best) return {w:lift==='bench'?B0:S0,reps:'5',sets:1};")
rep("else{var b=bt||[185,'5'];", "else{var b=bt||[B0,'5'];")
rep("if(ex.backext){var pl=wi<=0?0:wi===1?1:2;r.phw=pl*45;r.plates=pl;r.hint=pl?'Hold '+pl+' plate'+(pl>1?'s':'')+' ('+pl*45+' lbs) against your chest.':'Bodyweight.';}",
    "if(ex.backext){r.hint='Bodyweight. Hold a plate once 3 × 15 feels easy.';}")
rep("  if(!done){var bw=LS.get(K.bw,[]);if(!bw.some(function(e){return e.date==='2026-09-20'}))bw.push({date:'2026-09-20',lbs:138});LS.set(K.bw,bw);}\n", "  \n")

# ---- words that are about Eko ----
rep("315 is about 2× your bodyweight, so it’s a long road. Getting back to 155+ lbs is part of it.",
    "3 plates is a long-term goal. Eating enough to gain bodyweight is a big part of it.")
rep("This block · back to 235", "This 11-week block")
rep("var toGo=Math.round((155-lb.lbs)*10)/10;", "var toGo=Math.round((BWG-lb.lbs)*10)/10;")
rep("(toGo>0?toGo+' lbs to go':'at 155+')", "(toGo>0?toGo+' lbs to go':'at '+BWG+'+')")
rep("155,'155 lbs','Bodyweight over time')", "BWG,String(BWG)+' lbs','Bodyweight over time')")

# ---- setup screen (first open) ----
rep("<button type=\"button\" class=\"btn btn--ghost\" data-act=\"restore\">Restore</button></div>'+\n    cloudCard()",
    "<button type=\"button\" class=\"btn btn--ghost\" data-act=\"restore\">Restore</button><button type=\"button\" class=\"btn btn--ghost\" data-act=\"redo-setup\">Redo setup</button></div>'+\n    cloudCard()")
rep("function render(){var v=S.view||S.tab;",
    "function renderSetup(){document.body.classList.add('setup');finishEl.classList.remove('show');document.body.classList.remove('has-finish');weeksEl.innerHTML='';\n"
    " main.innerHTML='<div class=\"enter\"><div class=\"pagehead\"><h1>Let’s set you up</h1><p class=\"about\">Your numbers set your weekly targets. You can redo this later in Settings.</p></div>'+\n"
    " '<section class=\"card\"><label class=\"flabel\" for=\"su-b\" style=\"margin-top:0\">Bench: heaviest weight you can do for 5 reps (lbs)</label><input class=\"field\" id=\"su-b\" inputmode=\"decimal\" placeholder=\"e.g. 155\">'+\n"
    " '<label class=\"flabel\" for=\"su-s\">Squat: heaviest weight you can do for 5 reps (lbs)</label><input class=\"field\" id=\"su-s\" inputmode=\"decimal\" placeholder=\"e.g. 185\">'+\n"
    " '<label class=\"flabel\" for=\"su-w\">Your bodyweight now (lbs)</label><input class=\"field\" id=\"su-w\" inputmode=\"decimal\" placeholder=\"e.g. 140\">'+\n"
    " '<label class=\"flabel\" for=\"su-g\">Goal bodyweight (lbs)</label><input class=\"field\" id=\"su-g\" inputmode=\"decimal\" placeholder=\"155\">'+\n"
    " '<p class=\"fine\">Not sure? Guess a bit low. Your targets go up 5 lbs each time you hit your reps.</p>'+\n"
    " '<button type=\"button\" class=\"btn\" data-act=\"setup-go\" style=\"width:100%;margin-top:16px\">Start training</button><button type=\"button\" class=\"btn btn--ghost\" data-act=\"restore\" style=\"width:100%;margin-top:10px\">Have a backup? Restore it</button></section></div>';}\n"
    "function setupGo(){function v(id){var n=parseFloat((document.getElementById(id).value||'').replace(',','.'));return isFinite(n)?n:null;}\n"
    " var b=v('su-b'),sq=v('su-s'),w=v('su-w'),g=v('su-g')||155;\n"
    " if(!b||b<45||!sq||sq<45){toast('Enter your bench and squat for 5 reps (45 lbs or more).');return;}\n"
    " var m=mondayOf(new Date());LS.set('tpf.profile',{bench:r5(b),squat:r5(sq),bwGoal:g,start:[m.getFullYear(),m.getMonth(),m.getDate()]});\n"
    " if(w&&w>=70&&w<=400){S.bw=[{date:todayStr(),lbs:w}];persist();}\n"
    " location.reload();}\n"
    "function resetSetup(){try{localStorage.removeItem('tpf.profile');}catch(e){}location.reload();}\n"
    "function render(){if(!PROF){renderSetup();return;}var v=S.view||S.tab;")
rep("  var b=ev.target.closest('button');if(!b)return;var act=b.dataset.act;\n",
    "  var b=ev.target.closest('button');if(!b)return;var act=b.dataset.act;\n"
    "  if(act==='setup-go'){setupGo();return;}if(act==='restore'&&!PROF){document.getElementById('restoreIn').click();return;}if(act==='redo-setup'){resetSetup();return;}\n")

rep("function planLine(){return 'Plan started '",
    "function planLine(){return (PROF?'Your numbers: bench '+PROF.bench+' \\u00b7 squat '+PROF.squat+' \\u00b7 goal weight '+BWG+' lbs. ':'')+'Plan started '")

# ---- backups carry his setup numbers too ----
rep("sessions:S.sessions,bw:S.bw,checks:S.checks}),'application/json');",
    "sessions:S.sessions,bw:S.bw,checks:S.checks,profile:PROF}),'application/json');")
rep("if(persist())toast('Backup restored');render();}",
    "var np=!PROF&&o.profile&&o.profile.bench&&o.profile.squat;if(np)LS.set('tpf.profile',o.profile);if(persist())toast('Backup restored');if(np){setTimeout(function(){location.reload()},700);return;}render();}")
rep("reg.update().catch(function(){});syncSheet();syncCloud();", "reg.update().catch(function(){});syncCloud();")
rep_re(r"function syncSheet\(\)\{.*?\n", "")   # Eko's logs.json import; Ahmed has no such file
rep("render();\nsyncSheet();\nsyncCloud();", "render();\nsyncCloud();")
# his old link tells him where the new one is
rep("aria-label=\"Dismiss tip\">×</button></div>';\n",
    "aria-label=\"Dismiss tip\">×</button></div>';\n"
    "  if(location.pathname.indexOf('/3-plates/')===0)h+='<div class=\"tip\"><p>Your app has a new link: <a href=\"https://ekindeveci1907.github.io/Ahmed/\" style=\"color:inherit\"><b>ekindeveci1907.github.io/Ahmed</b></a>. To move your workouts, open Settings (the gear at the top), tap <b>Back up now</b> and save the file. Then open the new link in Safari, add it to your Home Screen, and tap <b>Restore</b>.</p></div>';\n")

# ---- his own storage, so the two apps never share numbers ----
rep("'road-to-3-plates-workouts-'", "'ahmed-workouts-'")
rep("'road-to-3-plates-backup-'", "'ahmed-backup-'")
s = s.replace("'r235.", "'tpf.")
assert "r235." not in s, 'an r235 key slipped through'

open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst)
