<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Detective Mystery Game — Starter</title>
  <style>
    :root{
      --bg:#0f1724; --card:#0b1220; --accent:#eab308; --muted:#9aa4b2; --glass: rgba(255,255,255,0.04);
      font-family: "Segoe UI", Roboto, system-ui, -apple-system, "Helvetica Neue", Arial;
    }
    *{box-sizing:border-box}
    body{margin:0; min-height:100vh; background:
      linear-gradient(180deg,#071026 0%, #0f1724 60%);
      color:#eef2ff; display:flex; align-items:center; justify-content:center; padding:20px;}
    .container{width:980px; max-width:100%; display:grid; grid-template-columns: 1fr 320px; gap:20px;}
    .panel{background:var(--card); border-radius:12px; padding:18px; box-shadow:0 6px 18px rgba(2,6,23,0.6);}
    .screen{height:620px; position:relative; overflow:hidden; border-radius:10px; background:linear-gradient(180deg,#122031,#0b1520);}
    header h1{margin:0; font-size:20px; color:var(--accent)}
    .hud{display:flex; gap:8px; align-items:center; margin-bottom:12px; justify-content:space-between}
    .btn{background:var(--glass); border:1px solid rgba(255,255,255,0.03); padding:8px 12px; border-radius:8px; cursor:pointer; color:inherit}
    .small{font-size:13px; opacity:.95}
    /* Scene layout */
    .scene {position:relative; width:100%; height:100%; display:flex; flex-direction:column;}
    .scene-bg{flex:1; position:relative; display:flex; align-items:center; justify-content:center; color:#cfe8ff; font-weight:600; font-size:18px}
    /* hotspots (clickable clues) */
    .hotspot{position:absolute; padding:6px 8px; background:rgba(255,255,255,0.035); border-radius:8px; border:1px dashed rgba(255,255,255,0.05); cursor:pointer; transition:transform .12s}
    .hotspot:hover{transform:scale(1.06)}
    .inventory{display:flex; gap:8px; flex-wrap:wrap;}
    .item{background:var(--glass); padding:6px 8px; border-radius:6px; font-size:13px}
    .log{height:220px; overflow:auto; background:linear-gradient(180deg, rgba(255,255,255,0.01), transparent); padding:10px; border-radius:8px; font-size:13px}
    .dialogue{margin-top:10px; display:flex; flex-direction:column; gap:8px;}
    .choice{background:transparent; border:1px solid rgba(255,255,255,0.06); padding:8px; border-radius:8px; cursor:pointer; text-align:left}
    .footer{display:flex; gap:8px; justify-content:space-between; align-items:center; margin-top:12px}
    .center{display:flex; align-items:center; justify-content:center}
    /* endings */
    .ending{padding:18px; text-align:center}
    footer small{color:var(--muted)}
    /* responsive */
    @media (max-width:920px){ .container{grid-template-columns:1fr; } .screen{height:520px} }
  </style>
</head>
<body>
  <div class="container">
    <!-- Left: Game Screen -->
    <div class="panel">
      <header class="hud">
        <div>
          <h1>Detective Mystery</h1>
          <div class="small">Case: The Vanishing Letter</div>
        </div>
        <div class="small">Day 1 • <span id="time">Evening</span></div>
      </header>

      <div class="screen" id="gameScreen">
        <!-- Scenes are rendered here -->
      </div>

      <div style="display:flex; gap:8px; margin-top:12px;">
        <button class="btn" id="restartBtn">Restart</button>
        <button class="btn" id="hintBtn">Hint</button>
      </div>
    </div>

    <!-- Right: Sidebar: Inventory, Log, Dialogue -->
    <div class="panel" aria-live="polite">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <strong>Inventory</strong>
        <small id="clueCount">0 clues</small>
      </div>
      <div class="inventory" id="inventory"></div>

      <hr style="border:none; height:8px; opacity:.03; margin:12px 0;">

      <strong>Case Log</strong>
      <div class="log" id="log"></div>

      <div class="dialogue" id="dialogueArea"></div>

      <div class="footer">
        <small>Tip: Click hotspots to search scenes.</small>
        <small>Made with HTML • JavaScript</small>
      </div>
    </div>
  </div>

  <script>
    // --- Game data ---
    const scenes = {
      foyer: {
        title: "Foyer — Family Home",
        desc: "A dim foyer. A coat stand, a table with a lamp, and a painting on the wall.",
        hotspots: [
          { id:'lamp', x: '60%', y:'60%', label:'Lamp', text:'You found a folded paper in the lamp — a portion of the missing letter.', clue:true },
          { id:'painting', x: '20%', y:'25%', label:'Painting', text:'The painting frame has scratch marks and a hidden key behind it.', clue:true, item:'brass key' },
          { id:'coat', x: '80%', y:'30%', label:'Coat', text:'Inside the coat pocket: a receipt from the train station.', clue:true }
        ],
        next: 'study'
      },
      study: {
        title: "Study — Locked Drawer",
        desc: "Bookshelf and a locked drawer. A typewriter sits on the desk.",
        hotspots: [
          { id:'drawer', x:'72%', y:'62%', label:'Locked Drawer', text:'It is locked. Maybe a key fits?', requires:'brass key', openAction:'openDrawer' },
          { id:'typewriter', x:'34%', y:'70%', label:'Typewriter', text:'A typed page with a cryptic phrase: "Red at midnight."', clue:true }
        ],
        next: 'garden'
      },
      garden: {
        title: "Garden — Back Patio",
        desc: "A stone path and a shed. The air smells of wet soil.",
        hotspots: [
          { id:'shed', x:'82%', y:'50%', label:'Shed', text:'Inside the shed: a torn envelope matching the missing letter.', clue:true },
          { id:'bench', x:'40%', y:'40%', label:'Garden Bench', text:'A secret carved on the bench: initials "E.P."'},
        ],
        next: null
      }
    };

    // Dialogue suspects
    const suspects = {
      emma: {
        name:'Emma Porter',
        intro: 'She is anxious and quick to change the subject.',
        questions: [
          { q:'Where were you last night?', a:'I was at the station buying a ticket. I needed to leave town.' },
          { q:'Do you know anything about the letter?', a:'No! Why would I know? I barely knew they had a private drawer.' },
          { q:'Why do your initials match the bench?', a:'That is not mine. Maybe someone framed me.' }
        ]
      },
      paul: {
        name:'Paul Reed',
        intro:'Calm, collected; has a deep voice.',
        questions: [
          { q:'Did you see anyone near the study?', a:'I saw Emma leave earlier, but I didn’t follow.' },
          { q:'Any reason someone would want the letter gone?', a:'It hinted at money. Some secrets cost a lot.' }
        ]
      }
    };

    // Game state
    let state = {
      currentScene: 'foyer',
      clues: [],
      items: [],
      log: [],
      solved: false,
      ending: null
    };

    // --- Helpers ---
    const el = id => document.getElementById(id);
    const addLog = (text) => {
      state.log.unshift(`[${new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}] ${text}`);
      renderLog();
    };
    const renderLog = () => {
      el('log').innerHTML = state.log.map(t => `<div style="margin-bottom:8px">${t}</div>`).join('');
    };
    const renderInventory = () => {
      el('inventory').innerHTML = state.items.map(i => `<div class="item">${i}</div>`).join('');
      el('clueCount').textContent = `${state.clues.length} clues`;
    };

    // --- Scene Rendering ---
    function renderScene() {
      const s = scenes[state.currentScene];
      const screen = el('gameScreen');
      screen.innerHTML = `
        <div class="scene">
          <div style="padding:12px 18px; border-bottom:1px solid rgba(255,255,255,0.03); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:700">${s.title}</div>
              <div class="small" style="opacity:.9">${s.desc}</div>
            </div>
            <div>
              <button class="btn" id="toNext">${s.next ? 'Go to next' : 'Investigate'}</button>
            </div>
          </div>
          <div class="scene-bg" id="sceneArea">
            <div style="width:90%; height:88%; position:relative;">
              <!-- Visual / stylized room -->
              <div style="position:absolute; left:5%; top:10%; width:40%; height:70%; border-radius:8px; background:linear-gradient(180deg, rgba(255,255,255,0.02), transparent); display:flex; align-items:center; justify-content:center; color:var(--muted)">
                <div>Room center</div>
              </div>
              ${s.hotspots.map(h => `
                <div class="hotspot" data-id="${h.id}" style="left:${h.x}; top:${h.y};">
                  ${h.label}
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `;

      // attach hotspot listeners
      document.querySelectorAll('.hotspot').forEach(node=>{
        node.addEventListener('click', ()=>handleHotspot(node.dataset.id));
      });
      const nextBtn = document.getElementById('toNext');
      nextBtn.addEventListener('click', ()=> {
        if (s.next) {
          state.currentScene = s.next;
          addLog(`Moved to ${scenes[state.currentScene].title}`);
          renderScene();
        } else {
          // show suspects to question
          showSuspects();
        }
      });
    }

    // --- Hotspot interaction ---
    function handleHotspot(id) {
      const s = scenes[state.currentScene];
      const h = s.hotspots.find(x=>x.id===id);
      if(!h) return;
      addLog(`Examined: ${h.label}`);

      // If hotspot requires an item
      if (h.requires && !state.items.includes(h.requires)) {
        addLog(`You need '${h.requires}' to interact with ${h.label}.`);
        showMessage(`The ${h.label} is locked. It looks like it needs a ${h.requires}.`);
        return;
      }

      // If hotspot triggers a special open action
      if (h.openAction === 'openDrawer') {
        // Simple puzzle: check if we already found clue
        openDrawer();
        return;
      }

      // If hotspot gives an item
      if(h.item && !state.items.includes(h.item)) {
        state.items.push(h.item);
        addLog(`Picked up item: ${h.item}`);
      }

      // If it's a clue and new
      if (h.clue && !state.clues.includes(h.id)) {
        state.clues.push(h.id);
        addLog(`Found clue: ${h.label}`);
        showMessage(h.text);
      } else {
        showMessage(h.text);
      }
      renderInventory();
    }

    // --- Drawer puzzle ---
    function openDrawer() {
      // small puzzle: guess the word 'RED'
      const answer = prompt("The drawer has a small note: type the secret word (hint: color in the note)");
      if(answer && answer.trim().toLowerCase() === 'red') {
        addLog('Drawer opened with the secret word.');
        // reward: a new clue and the missing letter piece
        if(!state.clues.includes('drawerPiece')) {
          state.clues.push('drawerPiece');
          addLog('Found clue: torn letter piece inside the drawer.');
        }
        state.items.push('torn letter piece');
        renderInventory();
        showMessage('You opened the drawer and found a torn piece of the missing letter.');
      } else {
        addLog('Failed to open the drawer (wrong answer).');
        showMessage('The drawer remains locked. The note suggests a color.');
      }
    }

    // --- Suspect interaction ---
    function showSuspects() {
      const area = el('dialogueArea');
      area.innerHTML = `<strong>Suspects</strong>`;
      Object.keys(suspects).forEach(key=>{
        const s = suspects[key];
        const btn = document.createElement('button');
        btn.className = 'choice';
        btn.textContent = s.name;
        btn.addEventListener('click', ()=>interrogate(key));
        area.appendChild(btn);
      });
    }

    function interrogate(key) {
      const s = suspects[key];
      const area = el('dialogueArea');
      area.innerHTML = `<div style="font-weight:700">${s.name}</div><div class="small">${s.intro}</div>`;
      s.questions.forEach((qObj, idx) => {
        const btn = document.createElement('button');
        btn.className = 'choice';
        btn.textContent = qObj.q;
        btn.addEventListener('click', ()=> {
          addLog(`Asked ${s.name}: "${qObj.q}"`);
          showMessage(`${s.name}: "${qObj.a}"`);
          // small hint: if player has the torn letter piece, enable accusation
          if(state.items.includes('torn letter piece')) {
            showAccuseArea(s.name);
          }
        });
        area.appendChild(btn);
      });
    }

    function showAccuseArea(name) {
      const area = el('dialogueArea');
      const accuse = document.createElement('button');
      accuse.className = 'choice';
      accuse.textContent = `Accuse ${name}`;
      accuse.style.borderColor = '#7fffd4';
      accuse.addEventListener('click', ()=>makeAccusation(name));
      area.appendChild(accuse);
    }

    function makeAccusation(name) {
      // simple logic: correct accused is 'Emma Porter'
      addLog(`You accused ${name}.`);
      if(name.toLowerCase().includes('emma')) {
        state.ending = 'solved';
        state.solved = true;
        showEnding(true);
      } else {
        state.ending = 'failed';
        showEnding(false);
      }
    }

    // --- UI small message (modal-like) ---
    function showMessage(text) {
      // small ephemeral message at top of scene
      const wrap = document.createElement('div');
      wrap.style.position='absolute';
      wrap.style.left='50%';
      wrap.style.top='10px';
      wrap.style.transform='translateX(-50%)';
      wrap.style.background='linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))';
      wrap.style.padding='10px 14px';
      wrap.style.borderRadius='8px';
      wrap.style.border='1px solid rgba(255,255,255,0.04)';
      wrap.style.zIndex = 999;
      wrap.style.maxWidth='86%';
      wrap.innerHTML = `<div style="font-size:13px">${text}</div>`;
      el('gameScreen').appendChild(wrap);
      setTimeout(()=>wrap.remove(), 3500);
    }

    // --- Endings ---
    function showEnding(success) {
      const screen = el('gameScreen');
      screen.innerHTML = `
        <div class="center" style="height:100%; flex-direction:column; gap:18px; padding:30px;">
          <div class="ending">
            <h2>${success ? 'Case Solved' : 'Case Unresolved'}</h2>
            <p>${success ? 'You exposed the truth. Emma was hiding the letter to protect someone — but your choices forced the secret open.' : 'Your accusation missed the mark. The real secret stays hidden... for now.'}</p>
            <div style="margin-top:12px;">
              <button class="btn" id="restartEnd">Play Again</button>
            </div>
          </div>
        </div>
      `;
      document.getElementById('restartEnd').addEventListener('click', initGame);
      addLog(success ? 'Case closed: successful accusation.' : 'Wrong accusation: case remains open.');
    }

    // --- Controls: hints and restart ---
    el('hintBtn').addEventListener('click', ()=> {
      if(state.clues.length === 0) {
        showMessage('Try searching the lamp or painting in the foyer.');
      } else if(state.clues.length < 3) {
        showMessage('You have some pieces — try using the key in the study drawer.');
      } else {
        showMessage('You can question suspects now. Use clues to support your accusation.');
      }
    });

    el('restartBtn').addEventListener('click', ()=> {
      if(confirm('Restart the game? All progress will be lost.')) initGame();
    });

    // --- Initialization ---
    function initGame(){
      state = { currentScene: 'foyer', clues: [], items: [], log: [], solved:false, ending:null };
      addLog('Game started. You arrive at the family home.');
      renderInventory();
      renderScene();
      el('dialogueArea').innerHTML = '';
      renderLog();
      document.getElementById('time').textContent = 'Evening';
    }

    // Start
    initGame();
  </script>
</body>
</html>
