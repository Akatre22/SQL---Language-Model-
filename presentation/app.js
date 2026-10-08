/**
 * Tiny SQL LLM — Enterprise Technical Presentation Controller
 * Includes:
 * 1. Slide transitions & keyboard navigation
 * 2. Background Neural Particle Canvas
 * 3. Laser Pointer Mode
 * 4. Interactive 5-Layer Stack Inspector (Slide 2)
 * 5. Interactive Neural Forward Pass & Attention Matrix (Slide 3)
 * 6. Interactive 4-Stage Training Metrics Switcher (Slide 4)
 * 7. Live NLP Intent Router & AST Simulator (Slide 5)
 * 8. REST API cURL Playground & Endpoint Switcher (Slide 8)
 */

class PresentationApp {
  constructor() {
    this.slides = Array.from(document.querySelectorAll('.slide'));
    this.currentIndex = 0;
    this.totalSlides = this.slides.length;

    this.currentSlideNumEl = document.getElementById('currentSlideNum');
    this.totalSlidesNumEl = document.getElementById('totalSlidesNum');
    this.currentSlideTopicEl = document.getElementById('currentSlideTopic');
    this.progressBarEl = document.getElementById('progressBar');

    this.prevBtn = document.getElementById('prevSlideBtn');
    this.nextBtn = document.getElementById('nextSlideBtn');
    this.openDrawerBtn = document.getElementById('openDrawerBtn');
    this.closeDrawerBtn = document.getElementById('closeDrawerBtn');
    this.drawerOverlay = document.getElementById('drawerOverlay');
    this.drawerSlideList = document.getElementById('drawerSlideList');
    this.fullscreenBtn = document.getElementById('fullscreenBtn');
    this.laserToggleBtn = document.getElementById('laserToggleBtn');
    this.laserCursor = document.getElementById('laserCursor');

    this.isLaserActive = true;

    this.init();
  }

  init() {
    if (this.totalSlidesNumEl) {
      this.totalSlidesNumEl.textContent = this.totalSlides;
    }

    this.buildDrawerList();
    this.bindEvents();
    this.initCanvasAnimation();
    this.initLaserPointer();
    this.initSlide2StackExplorer();
    this.initSlide3NeuralPipeline();
    this.initSlide4TrainingStages();
    this.initSlide5IntentRouter();
    this.initSlide8ApiPlayground();
    this.initSlide9RoadmapExplorer();
    this.updateUI();
  }

  /* ==========================================================================
     SLIDE NAVIGATION & UI
     ========================================================================== */
  goToSlide(index) {
    if (index < 0 || index >= this.totalSlides || index === this.currentIndex) return;

    const currentSlide = this.slides[this.currentIndex];
    const targetSlide = this.slides[index];

    if (index > this.currentIndex) {
      currentSlide.classList.remove('active');
      currentSlide.classList.add('prev');
      targetSlide.classList.remove('prev');
      targetSlide.classList.add('active');
    } else {
      currentSlide.classList.remove('active', 'prev');
      targetSlide.classList.remove('prev');
      targetSlide.classList.add('active');
    }

    this.currentIndex = index;
    this.updateUI();
  }

  nextSlide() {
    if (this.currentIndex < this.totalSlides - 1) {
      this.goToSlide(this.currentIndex + 1);
    }
  }

  prevSlide() {
    if (this.currentIndex > 0) {
      this.goToSlide(this.currentIndex - 1);
    }
  }

  updateUI() {
    const activeSlide = this.slides[this.currentIndex];
    const topic = activeSlide.getAttribute('data-topic') || `Slide ${this.currentIndex + 1}`;

    if (this.currentSlideNumEl) this.currentSlideNumEl.textContent = this.currentIndex + 1;
    if (this.currentSlideTopicEl) this.currentSlideTopicEl.textContent = topic;

    // Update Progress Bar
    const progressPercent = ((this.currentIndex + 1) / this.totalSlides) * 100;
    if (this.progressBarEl) {
      this.progressBarEl.style.width = `${progressPercent}%`;
    }

    // Update Navigation Buttons State
    if (this.prevBtn) {
      this.prevBtn.disabled = this.currentIndex === 0;
      this.prevBtn.style.opacity = this.currentIndex === 0 ? '0.4' : '1';
    }

    if (this.nextBtn) {
      if (this.currentIndex === this.totalSlides - 1) {
        this.nextBtn.innerHTML = '<span>Restart</span> <svg class="icon-svg" viewBox="0 0 24 24"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>';
      } else {
        this.nextBtn.innerHTML = '<span>Next</span> <svg class="icon-svg" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>';
      }
    }

    // Update Drawer Active Item
    const drawerRows = document.querySelectorAll('.drawer-row');
    drawerRows.forEach((item, idx) => {
      if (idx === this.currentIndex) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  buildDrawerList() {
    if (!this.drawerSlideList) return;
    this.drawerSlideList.innerHTML = '';

    this.slides.forEach((slide, idx) => {
      const topic = slide.getAttribute('data-topic') || `Slide ${idx + 1}`;
      const item = document.createElement('div');
      item.className = `drawer-row ${idx === this.currentIndex ? 'active' : ''}`;
      item.innerHTML = `
        <span class="drawer-row-num">0${idx + 1}</span>
        <span class="drawer-row-title">${topic}</span>
      `;
      item.addEventListener('click', () => {
        this.goToSlide(idx);
        this.closeDrawer();
      });
      this.drawerSlideList.appendChild(item);
    });
  }

  openDrawer() {
    if (this.drawerOverlay) this.drawerOverlay.classList.add('open');
  }

  closeDrawer() {
    if (this.drawerOverlay) this.drawerOverlay.classList.remove('open');
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.warn('Fullscreen request failed:', err);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  /* ==========================================================================
     LASER POINTER
     ========================================================================== */
  toggleLaser() {
    this.isLaserActive = !this.isLaserActive;
    document.body.classList.toggle('laser-mode', this.isLaserActive);
    if (this.laserToggleBtn) {
      this.laserToggleBtn.classList.toggle('active', this.isLaserActive);
    }
  }

  initLaserPointer() {
    // Enable laser mode by default
    this.isLaserActive = true;
    document.body.classList.add('laser-mode');
    if (this.laserToggleBtn) {
      this.laserToggleBtn.classList.add('active');
    }

    window.addEventListener('mousemove', (e) => {
      if (this.laserCursor && this.isLaserActive) {
        this.laserCursor.style.left = `${e.clientX}px`;
        this.laserCursor.style.top = `${e.clientY}px`;
      }
    });
  }

  /* ==========================================================================
     CANVAS NEURAL PARTICLES BACKGROUND
     ========================================================================== */
  initCanvasAnimation() {
    const canvas = document.getElementById('bgCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const particleCount = 38;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        radius: Math.random() * 2 + 1.2,
      });
    }

    function render() {
      ctx.clearRect(0, 0, width, height);

      // Draw particle nodes
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#94A3B8';
        ctx.fill();

        // Connect nearby nodes with subtle lines
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 130) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(148, 163, 184, ${0.2 * (1 - dist / 130)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(render);
    }

    render();
  }

  /* ==========================================================================
     SLIDE 2: LAYERED ARCHITECTURE STACK EXPLORER
     ========================================================================== */
  initSlide2StackExplorer() {
    const layerData = {
      1: {
        title: "Layer 01: 6.16M Neural Core Foundation",
        badge: "Neural Core",
        heading: "Deterministic SQL Synthesis on Zero-GPU Hardware",
        desc: "The foundational 6.16M parameter Causal Decoder Transformer trained specifically on multi-dialect SQL syntax, foreign key graphs, and relational schemas.",
        nodes: ["SQL-BPE (4,096)", "→", "RoPE 6-Layer Core", "→", "AST Clean SQL"],
        benefit: "Runs 100% locally or inside your private VPC on CPU with <50ms latency. Zero cloud GPU costs, zero data leak vectors."
      },
      2: {
        title: "Layer 02: Dual-Brain Agent Reasoning Engine",
        badge: "Agent Intelligence",
        heading: "Hybrid Intent Classification & AST Self-Repair",
        desc: "Combines fast NLP intent routing, ChromaDB semantic vector RAG for complex concepts, and a 3-attempt sqlglot AST verification sandbox loop.",
        nodes: ["Intent Router", "→", "ChromaDB RAG", "→", "sqlglot AST Validator"],
        benefit: "Prevents column hallucinations and syntactically invalid queries before they ever reach your production database engine."
      },
      3: {
        title: "Layer 03: Enterprise Web Interface Workspace",
        badge: "Interactive UI",
        heading: "Monochrome Light Canvas & Relational Data Grid",
        desc: "High-contrast data exploration workspace with real-time execution trace telemetry, schema modals, and one-click CSV export.",
        nodes: ["NL Prompt Input", "→", "Trace Bar Telemetry", "→", "Relational Grid & CSV"],
        benefit: "Provides business analysts, developers, and executives with an intuitive interface to query complex enterprise databases effortlessly."
      },
      4: {
        title: "Layer 04: Universal REST API & Token Security",
        badge: "API Gateway",
        heading: "FastAPI Backend with Tiered Key Security",
        desc: "High-throughput asynchronous API server (port 8000) featuring SHA-256 hashed keys, rate-limiting, and detailed endpoint telemetry.",
        nodes: ["POST /v1/agent/query", "→", "SHA-256 Auth", "→", "Sub-50ms JSON Payload"],
        benefit: "Enables programmatic integration across internal microservices, Python notebooks, and automated reporting pipelines."
      },
      5: {
        title: "Layer 05: Enterprise Extensibility & Ecosystem",
        badge: "Ecosystem",
        heading: "Custom BI Dashboards, Slack Bots & Automated ETL",
        desc: "The ultimate layer allowing businesses to embed deterministic Natural Language SQL capabilities across their entire technology ecosystem.",
        nodes: ["Slack/Teams NL Bot", "→", "Automated ETL Pipelines", "→", "Executive BI Feeds"],
        benefit: "Completely replaces costly cloud LLM subscriptions (saving $10k+/yr) while maintaining total enterprise data sovereignty."
      }
    };

    const layerBtns = document.querySelectorAll('.stack-layer-btn');
    const titleEl = document.getElementById('inspectorTitle');
    const badgeEl = document.getElementById('inspectorBadge');
    const contentEl = document.getElementById('inspectorContent');

    layerBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        layerBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        const layerNum = btn.getAttribute('data-layer');
        const data = layerData[layerNum];
        if (!data || !contentEl) return;

        if (titleEl) titleEl.textContent = data.title;
        if (badgeEl) badgeEl.textContent = data.badge;

        contentEl.innerHTML = `
          <h4>${data.heading}</h4>
          <p>${data.desc}</p>
          <div class="inspector-diagram">
            <div class="diagram-node highlight">${data.nodes[0]}</div>
            <span>${data.nodes[1]}</span>
            <div class="diagram-node highlight">${data.nodes[2]}</div>
            <span>${data.nodes[3]}</span>
            <div class="diagram-node highlight">${data.nodes[4]}</div>
          </div>
          <div class="inspector-highlight-box">
            <strong>Enterprise Architecture Advantage:</strong>
            <span>${data.benefit}</span>
          </div>
        `;
      });
    });
  }

  /* ==========================================================================
     SLIDE 3: NEURAL FORWARD PASS & ATTENTION HEATMAP
     ========================================================================== */
  initSlide3NeuralPipeline() {
    const stageSpecs = {
      1: {
        title: "Stage 01: Domain SQL-BPE Tokenization",
        badge: "Vocabulary: 4,096",
        rows: [
          { k: "Tokenizer Type", v: "Byte-Pair Encoding (BPE)" },
          { k: "SQL Keyword Optimization", v: "Atomic Multi-Word Tokens (LEFT JOIN, GROUP BY)" },
          { k: "Context Length Window", v: "512 Sequence Tokens" },
          { k: "Schema Conditioning Strategy", v: "Compact DDL Table Header Serialization" },
          { k: "Special Tokens", v: "[QUESTION], [SCHEMA], [SQL], [EOS]" }
        ]
      },
      2: {
        title: "Stage 02: Embedding & Rotary Position (RoPE)",
        badge: "Dimension: 384",
        rows: [
          { k: "Embedding Dimension (d_model)", v: "384 Channels" },
          { k: "Positional Encoding", v: "Rotary Position Embeddings (RoPE)" },
          { k: "Frequency Base (theta)", v: "10,000.0" },
          { k: "Relative Distance Decay", v: "Smooth Multi-token Attention Decay" },
          { k: "Memory Footprint", v: "6.02 MB Tensor Buffer" }
        ]
      },
      3: {
        title: "Stage 03: 6x Transformer Blocks & SwiGLU FFN",
        badge: "6 Heads (d_k = 64)",
        rows: [
          { k: "Layer Depth", v: "6 Causal Decoder Blocks" },
          { k: "Attention Heads", v: "6 Multi-Head Attention Channels" },
          { k: "Feed-Forward Network", v: "SwiGLU Gated Activation (dim: 1,024)" },
          { k: "Layer Normalization", v: "RMSNorm (Root Mean Square Normalization)" },
          { k: "Attention Mechanism", v: "Causal Masked Multi-Head Attention" }
        ]
      },
      4: {
        title: "Stage 04: Linear Output Projection & Softmax",
        badge: "Deterministic Output",
        rows: [
          { k: "Projection Layer", v: "Linear (384 -> 4,096 Vocab Logits)" },
          { k: "Decoding Strategy", v: "Greedy Search (Temperature = 0.0)" },
          { k: "Target Output Dialect", v: "ANSI / Snowflake / PostgreSQL SQL" },
          { k: "Inference Latency", v: "< 50ms on standard Intel/AMD CPU" },
          { k: "Syntactic Determinism", v: "100% Reproducible Output" }
        ]
      }
    };

    const stageBtns = document.querySelectorAll('.neural-stage-btn');
    const titleEl = document.getElementById('neuralStageTitle');
    const badgeEl = document.getElementById('neuralStageBadge');
    const rowsEl = document.getElementById('neuralStageRows');

    stageBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        stageBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        const stageNum = btn.getAttribute('data-stage');
        const spec = stageSpecs[stageNum];
        if (!spec || !rowsEl) return;

        if (titleEl) titleEl.textContent = spec.title;
        if (badgeEl) badgeEl.textContent = spec.badge;

        rowsEl.innerHTML = spec.rows
          .map((r) => `
            <div class="spec-item">
              <span class="spec-k">${r.k}</span>
              <span class="spec-v">${r.v}</span>
            </div>
          `)
          .join('');

        this.renderAttentionGrid(parseInt(stageNum, 10));
      });
    });

    this.renderAttentionGrid(1);
  }

  renderAttentionGrid(stage) {
    const gridEl = document.getElementById('attMatrixGrid');
    if (!gridEl) return;

    gridEl.innerHTML = '';
    const tokens = ['[Q]', 'cust', 'id', '=', '1003', '[SQL]'];

    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 6; c++) {
        const cell = document.createElement('div');
        cell.className = 'att-cell';

        let weight = 0.05;
        if (r >= c) {
          weight = Math.min(0.95, (0.2 + (r * 0.15) - (c * 0.05) + (stage * 0.1)).toFixed(2));
        }

        const opacity = r >= c ? Math.max(0.1, weight) : 0.02;
        cell.style.background = r >= c ? `rgba(37, 99, 235, ${opacity})` : 'rgba(226, 232, 240, 0.4)';
        cell.style.color = opacity > 0.5 ? '#FFFFFF' : '#334155';
        cell.textContent = r >= c ? weight : '-';
        cell.title = `${tokens[r]} → ${tokens[c]}: Attention Weight ${weight}`;

        gridEl.appendChild(cell);
      }
    }
  }

  /* ==========================================================================
     SLIDE 4: 4-STAGE TRAINING METHODOLOGY
     ========================================================================== */
  initSlide4TrainingStages() {
    const trainData = {
      1: {
        title: "Stage 01: Foundational Unsupervised Pre-Training",
        desc: "Trained on a curated multi-dialect SQL corpus spanning ISO standards, open-source schemas, and technical manuals. Instills deep structural priors for relational table relationships.",
        loss: "1.15",
        tokens: "120M",
        time: "3.4h"
      },
      2: {
        title: "Stage 02: Supervised Instruction Fine-Tuning (SFT)",
        desc: "Conditioned on paired natural language questions and compact DDL schemas. Enforces column-level grounding and schema adherence without hallucinating missing tables.",
        loss: "0.42",
        tokens: "45M",
        time: "1.8h"
      },
      3: {
        title: "Stage 03: Adversarial Hard-Negative Sampling",
        desc: "Trained against subtle SQL logic edge cases (Cartesian joins, WHERE vs HAVING misuse, incorrect GROUP BY column projections) to achieve high execution accuracy.",
        loss: "0.18",
        tokens: "18M",
        time: "55m"
      },
      4: {
        title: "Stage 04: Autonomous Schema Shadow Adaptation",
        desc: "Live zero-shot fine-tuning on newly connected database schemas. The engine creates in-memory shadow tables, validates FK paths, and aligns vocabulary to your exact catalog.",
        loss: "0.08",
        tokens: "5M",
        time: "12m"
      }
    };

    const cards = document.querySelectorAll('.stage-card');
    const titleEl = document.getElementById('trainDetailTitle');
    const descEl = document.getElementById('trainDetailDesc');
    const lossEl = document.getElementById('trainStatLoss');
    const tokensEl = document.getElementById('trainStatTokens');
    const timeEl = document.getElementById('trainStatTime');

    cards.forEach((card) => {
      card.addEventListener('click', () => {
        cards.forEach((c) => c.classList.remove('active'));
        card.classList.add('active');

        const stage = card.getAttribute('data-train-stage');
        const data = trainData[stage];
        if (!data) return;

        if (titleEl) titleEl.textContent = data.title;
        if (descEl) descEl.textContent = data.desc;
        if (lossEl) lossEl.textContent = data.loss;
        if (tokensEl) tokensEl.textContent = data.tokens;
        if (timeEl) timeEl.textContent = data.time;
      });
    });
  }

  /* ==========================================================================
     SLIDE 5: NLP INTENT ROUTER & AST SIMULATOR
     ========================================================================== */
  initSlide5IntentRouter() {
    const intentSim = {
      text_to_sql: {
        prompt: '"customer whose id is 1003"',
        slm: 'SELECT CUSTOMER_ID, FIRST_NAME, LAST_NAME FROM CUSTOMERS WHERE CUSTOMER_ID = 1003 LIMIT 1;',
        val: 'AST Tree Validated (sqlglot Snowflake)',
        ok: 'Return Clean Results (1 Row)',
        err: '0 Retries Needed (998ms)'
      },
      join_query: {
        prompt: '"left join branch and loan table"',
        slm: 'SELECT b.branch_name, l.loan_id, l.amount FROM branches b LEFT JOIN loans l ON b.branch_id = l.branch_id;',
        val: 'AST Join Tree Validated (FK: branch_id)',
        ok: 'Return Clean Joined Results',
        err: '0 Retries Needed (1.12s)'
      },
      concept_rag: {
        prompt: '"what is CTE in SQL?"',
        slm: 'ChromaDB Vector Retrieval: "Common Table Expressions (WITH clause)"',
        val: 'RAG Markdown Formatted',
        ok: 'Render Educational Markdown Tutorial',
        err: 'Dispatched to Vector Store (42ms)'
      },
      comparison: {
        prompt: '"difference between WHERE and HAVING"',
        slm: 'Comparison Matrix: Row filter vs Group aggregate filter',
        val: 'Structured Comparison Table',
        ok: 'Render Syntax Comparison Table',
        err: 'Dispatched to Agent Knowledge Base (38ms)'
      }
    };

    const intentItems = document.querySelectorAll('.intent-item');
    const stepPrompt = document.getElementById('astStepPrompt');
    const stepSlm = document.getElementById('astStepSlm');
    const stepVal = document.getElementById('astStepVal');
    const okText = document.getElementById('astOkText');
    const errText = document.getElementById('astErrText');

    intentItems.forEach((item) => {
      item.addEventListener('click', () => {
        intentItems.forEach((i) => i.classList.remove('active'));
        item.classList.add('active');

        const intentKey = item.getAttribute('data-intent');
        const sim = intentSim[intentKey];
        if (!sim) return;

        if (stepPrompt) stepPrompt.textContent = sim.prompt;
        if (stepSlm) stepSlm.textContent = sim.slm;
        if (stepVal) stepVal.textContent = sim.val;
        if (okText) okText.textContent = sim.ok;
        if (errText) errText.textContent = sim.err;
      });
    });
  }

  /* ==========================================================================
     SLIDE 8: REST API PLAYGROUND
     ========================================================================== */
  initSlide8ApiPlayground() {
    const apiSnippets = {
      query: {
        title: "POST /v1/agent/query",
        auth: "SHA-256 Hashed",
        code: `curl -X POST http://localhost:8000/v1/agent/query \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: tiny-dev-key-xxxx" \\
  -d '{
    "question": "show top 5 customers by loan amount",
    "execute": true
  }'`
      },
      schema: {
        title: "GET /v1/schema/detailed",
        auth: "Public / Key",
        code: `curl -X GET http://localhost:8000/v1/schema/detailed \\
  -H "X-API-Key: tiny-dev-key-xxxx"`
      },
      adapt: {
        title: "POST /v1/schema/adapt",
        auth: "Admin Only",
        code: `curl -X POST http://localhost:8000/v1/schema/adapt \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: tiny-admin-key-xxxx" \\
  -d '{
    "force_retrain": false
  }'`
      },
      connect: {
        title: "POST /v1/database/connect",
        auth: "Admin Only",
        code: `curl -X POST http://localhost:8000/v1/database/connect \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: tiny-admin-key-xxxx" \\
  -d '{
    "connection_type": "snowflake",
    "database": "BANKING_DB",
    "schema": "BANKING_SCHEMA"
  }'`
      },
      keys: {
        title: "POST /v1/keys/generate",
        auth: "Admin Only",
        code: `curl -X POST http://localhost:8000/v1/keys/generate \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: tiny-admin-key-xxxx" \\
  -d '{
    "name": "Analytics-Service",
    "tier": "enterprise"
  }'`
      },
      analytics: {
        title: "GET /v1/keys/analytics",
        auth: "Admin / Enterprise",
        code: `curl -X GET http://localhost:8000/v1/keys/analytics \\
  -H "X-API-Key: tiny-admin-key-xxxx"`
      }
    };

    const routeRows = document.querySelectorAll('.api-route-row');
    const titleEl = document.getElementById('curlEndpointTitle');
    const authBadgeEl = document.getElementById('curlAuthBadge');
    const snippetEl = document.getElementById('curlSnippet');
    const copyBtn = document.getElementById('copyCurlBtn');

    routeRows.forEach((row) => {
      row.addEventListener('click', () => {
        routeRows.forEach((r) => r.classList.remove('active'));
        row.classList.add('active');

        const ep = row.getAttribute('data-endpoint');
        const data = apiSnippets[ep];
        if (!data || !snippetEl) return;

        if (titleEl) titleEl.textContent = data.title;
        if (authBadgeEl) authBadgeEl.textContent = data.auth;
        snippetEl.innerHTML = `<code>${data.code}</code>`;
      });
    });

    if (copyBtn && snippetEl) {
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(snippetEl.innerText);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.background = 'var(--accent-green)';
        setTimeout(() => {
          copyBtn.textContent = originalText;
          copyBtn.style.background = '';
        }, 1800);
      });
    }
  }

  /* ==========================================================================
     SLIDE 9: TREE OF INTELLIGENCE: ROOTS, TRUNK, BRANCHES & CANOPY
     ========================================================================== */
  initSlide9RoadmapExplorer() {
    const treeData = {
      crown: {
        title: "Crown Impact: 100% Elimination of Generic Cloud LLMs",
        badge: "Zero Cloud Costs",
        desc: "By grounding execution in custom 6.16M neural weights, an autonomous dual-brain agent, and native database drivers, Tiny SQL LLM makes 70B+ general cloud LLMs (GPT-4 / Claude / Gemini) obsolete for SQL operations.",
        caps: [
          "<strong>Zero API Subscription Bills:</strong> Saves thousands in recurring monthly cloud token fees ($0/month).",
          "<strong>100% Data Sovereignty:</strong> Banking and healthcare schemas/data never leave private VPC networks.",
          "<strong>Sub-50ms CPU Execution:</strong> 40x faster than cloud API internet roundtrips."
        ],
        highlightTitle: "Tree System Synergy:",
        highlightText: "Deep neural roots feed the central agent trunk, which branches into Web UI, REST API, Snowflake, and future autonomous agents."
      },
      r_transformer: {
        title: "Root 01: 6.16M Decoder Transformer Architecture",
        badge: "Neural Core",
        desc: "The primary structural root: a custom Causal Decoder Transformer engineered with Rotary Position Embeddings (RoPE), RMSNorm, and SwiGLU gated activations.",
        caps: [
          "<strong>6.16M Neural Weights:</strong> Lightweight footprint designed specifically for zero-GPU CPU execution.",
          "<strong>Rotary Embeddings (RoPE):</strong> Preserves relational token distances, parentheses depth, and operator precedence.",
          "<strong>SwiGLU FFN (dim: 1,024):</strong> High capacity non-linear relational logic synthesis."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Executes in <50ms on standard CPUs without requiring $30,000 GPU servers or third-party cloud AI vendors."
      },
      r_tokenizer: {
        title: "Root 02: Domain SQL-BPE Tokenizer (Vocab: 4,096)",
        badge: "Vocabulary Root",
        desc: "A custom Byte-Pair Encoding tokenizer trained exclusively on ANSI SQL, multi-dialect keywords, and database schemas.",
        caps: [
          "<strong>Atomic Keyword Tokens:</strong> Multi-word phrases like 'LEFT JOIN', 'GROUP BY', 'IS NOT NULL' tokenized as single IDs.",
          "<strong>512 Sequence Length:</strong> Efficient compact context window optimized for prompt and DDL table serialization.",
          "<strong>Special Semantic Markers:</strong> [QUESTION], [SCHEMA], [SQL], and [EOS] tokens prevent syntax drift."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Eliminates token fragmentation that causes generic LLMs to misspell column identifiers or split syntax keywords."
      },
      r_training: {
        title: "Root 03: 4-Stage Progressive SFT & Hard-Negative Loss",
        badge: "Training Root",
        desc: "A progressive 4-phase curriculum that transforms raw grammar fluency into zero-shot multi-dialect SQL mastery.",
        caps: [
          "<strong>Pre-Training + SFT:</strong> Trained on textbook schemas, ANSI standards, and SQL paired queries.",
          "<strong>Adversarial Negatives:</strong> Explicit loss penalties for WHERE vs HAVING bugs, missing FK joins, and Cartesian products.",
          "<strong>Live Shadow Adaptation:</strong> Fine-tunes dynamically in memory when connected to new enterprise schemas."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Delivers deterministic accuracy specifically tuned for relational algebra without hallucinating non-existent tables."
      },
      trunk: {
        title: "Central Trunk: Autonomous Dual-Brain Agent Core",
        badge: "Agent Trunk",
        desc: "The central intelligence conduit that routes queries, retrieves conceptual knowledge, and guarantees valid database execution.",
        caps: [
          "<strong>SQLIntentRouter:</strong> Categorizes user prompts into text_to_sql, table joins, concept explanations, and comparisons.",
          "<strong>ChromaDB Vector RAG:</strong> Embedded vector search across 150+ SQL concepts and tutorials.",
          "<strong>sqlglot AST Self-Repair:</strong> 3-attempt sandbox feedback loop that catches syntax errors and self-repairs in memory."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Generic LLMs have no validation loop; the Dual-Brain Trunk ensures 100% AST syntactical correctness before database execution."
      },
      b_workspace: {
        title: "Branch 01: Enterprise Web Interface Workspace",
        badge: "Interactive UI",
        desc: "A sleek monochrome React + Vite workspace engineered for business analysts, developers, and executives.",
        caps: [
          "<strong>Execution Trace Bar:</strong> Real-time visual telemetry displaying intent categorization, status badge, and latency timer.",
          "<strong>Relational Data Grid:</strong> High-contrast table with sticky column headers, monospace ID highlights, and one-click CSV export.",
          "<strong>Schema Explorer Modal:</strong> Interactive database catalog inspector showcasing tables, columns, and foreign keys."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Provides an end-to-end user workspace with direct query execution, eliminating copy-pasting SQL into separate database tools."
      },
      b_api: {
        title: "Branch 02: Universal Enterprise REST API Gateway",
        badge: "FastAPI Gateway",
        desc: "A production-ready asynchronous API server (port 8000) allowing any internal system to execute natural language SQL queries.",
        caps: [
          "<strong>Core Endpoints:</strong> POST /v1/agent/query, GET /v1/schema/detailed, and POST /v1/schema/adapt.",
          "<strong>SHA-256 Tiered Security:</strong> Admin (Unlimited), Enterprise (100k req/mo), and Developer (10k req/mo) API keys.",
          "<strong>Real-Time Telemetry:</strong> Tracks token usage, latency distribution, and execution success metrics."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Acts as a secure internal drop-in replacement for OpenAI API endpoints with 40x lower latency and zero recurring token costs."
      },
      b_snowflake: {
        title: "Branch 03: Snowflake & Enterprise Multi-DB Hub",
        badge: "Data Cloud Hub",
        desc: "Native database connectors bridging Cloud Data Warehouses and On-Premise Relational Systems.",
        caps: [
          "<strong>Snowflake Data Cloud:</strong> Dedicated form (Account, User, Password, Warehouse, DB, Schema, Role) + all drivers (ODBC, JDBC, SSO, Python).",
          "<strong>Multi-Dialect Coverage:</strong> PostgreSQL, SQL Server (SSMS/T-SQL), MySQL, and SQLite.",
          "<strong>Live Schema Introspection:</strong> Automatic table and foreign key discovery without manual configuration."
        ],
        highlightTitle: "How it Skips Other Cloud LLMs:",
        highlightText: "Direct native database connections ensure secure query execution with zero transmission of sensitive credentials to third-party APIs."
      },
      b_future: {
        title: "Branch 04: Future Vision — Autonomous Multi-Agent Ecosystem",
        badge: "Next-Gen Frontier",
        desc: "The next evolution: an autonomous fleet of domain-specialized agents managing and optimizing enterprise data intelligence.",
        caps: [
          "<strong>Predictive Data Analyst Agent:</strong> Proactively schedules SQL queries to identify anomalies and auto-generates weekly business KPI digests.",
          "<strong>Cross-Warehouse Data Mesh:</strong> Seamlessly federates multi-table joins across Snowflake, Postgres, and S3 Data Lakes into unified SQL.",
          "<strong>Autonomous Self-Healing DBA:</strong> Inspects query performance plans, generates missing indexes, and auto-tunes queries in real-time.",
          "<strong>Slack/Teams NL Data Bots:</strong> Conversational bots allowing team members to query enterprise databases via natural speech/text."
        ],
        highlightTitle: "The Ultimate Replacement Thesis:",
        highlightText: "Completely replaces cloud-dependent generic LLMs with sovereign, domain-specialized, zero-cost, sub-50ms SLM multi-agent ecosystems."
      }
    };

    const treeNodes = document.querySelectorAll('[data-tree-node]');
    const titleEl = document.getElementById('treeInspectorTitle');
    const badgeEl = document.getElementById('treeInspectorBadge');
    const descEl = document.getElementById('treeInspectorDesc');
    const capsEl = document.getElementById('treeInspectorCaps');
    const highlightTitleEl = document.getElementById('treeInspectorHighlightTitle');
    const highlightTextEl = document.getElementById('treeInspectorHighlightText');

    treeNodes.forEach((node) => {
      node.addEventListener('click', () => {
        treeNodes.forEach((n) => n.classList.remove('active'));
        node.classList.add('active');

        const nodeKey = node.getAttribute('data-tree-node');
        const data = treeData[nodeKey];
        if (!data) return;

        if (titleEl) titleEl.textContent = data.title;
        if (badgeEl) badgeEl.textContent = data.badge;
        if (descEl) descEl.textContent = data.desc;

        if (capsEl) {
          capsEl.innerHTML = data.caps
            .map((cap) => `
              <div class="tree-cap-item">
                <span class="icon">✓</span>
                <span>${cap}</span>
              </div>
            `)
            .join('');
        }

        if (highlightTitleEl) highlightTitleEl.textContent = data.highlightTitle;
        if (highlightTextEl) highlightTextEl.textContent = data.highlightText;
      });
    });
  }

  /* ==========================================================================
     GLOBAL EVENT LISTENERS
     ========================================================================== */
  bindEvents() {
    if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prevSlide());
    if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.nextSlide());
    if (this.openDrawerBtn) this.openDrawerBtn.addEventListener('click', () => this.openDrawer());
    if (this.closeDrawerBtn) this.closeDrawerBtn.addEventListener('click', () => this.closeDrawer());
    if (this.fullscreenBtn) this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    if (this.laserToggleBtn) this.laserToggleBtn.addEventListener('click', () => this.toggleLaser());

    if (this.drawerOverlay) {
      this.drawerOverlay.addEventListener('click', (e) => {
        if (e.target === this.drawerOverlay) {
          this.closeDrawer();
        }
      });
    }

    // Global Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

      switch (e.key) {
        case 'ArrowRight':
        case 'PageDown':
        case ' ':
          e.preventDefault();
          this.nextSlide();
          break;
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault();
          this.prevSlide();
          break;
        case 'Home':
          e.preventDefault();
          this.goToSlide(0);
          break;
        case 'End':
          e.preventDefault();
          this.goToSlide(this.totalSlides - 1);
          break;
        case 'f':
        case 'F':
          this.toggleFullscreen();
          break;
        case 'l':
        case 'L':
          this.toggleLaser();
          break;
        case 'Escape':
          this.closeDrawer();
          break;
        default:
          break;
      }
    });
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.presentationApp = new PresentationApp();
});
