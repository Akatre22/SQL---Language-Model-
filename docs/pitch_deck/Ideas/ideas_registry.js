// GenAI Ideas Registry - Modular Storage for New Propositions & Mini-Slide Decks
// Color Palette:
// Idea 1: Electric Blue (#007BFF)
// Idea 2: Bright Orange (#FF6F00)
// Idea 3: Lemon Yellow (#FFD300)
// Idea 4: Sage Green (#BCB88A)

window.GENAI_IDEAS_REGISTRY = [
  {
    id: "idea_01",
    tag: "IDEA 01 // UNIVERSAL DATA & BI STUDIO",
    title: "Universal Data & BI Intelligence Studio",
    subtitle: "An all-in-one on-premise AI platform uniting automated schema discovery, Snowflake/Databricks lakehouse engineering, self-healing SQL, and real-time BI dashboard design.",
    canvasType: "data_studio",
    themeColor: "#007BFF",
    themeLight: "rgba(0, 123, 255, 0.12)",
    metrics: [
      { val: "5.4M", label: "Model Parameters" },
      { val: "< 12ms", label: "Pipeline Latency" },
      { val: "100%", label: "Dialect Coverage" },
      { val: "On-Prem", label: "Zero Data Egress" }
    ],
    slides: [
      {
        slideNum: 1,
        slideType: "overview",
        slideTag: "Concept & Problem Statement",
        slideTitle: "Universal Data & BI Intelligence Studio",
        slideSubtitle: "Unifying Data Engineering, Analytics, and BI Reporting through a single on-premise domain model.",
        overview: "Enterprises face fragmented data stacks: engineers write boilerplate pipelines for Snowflake/Databricks, analysts debug complex SQL, and BI teams struggle with DAX/Tableau formulas. This platform connects any data source to a specialized 5.4M parameter Transformer to automate the entire data lifecycle.",
        problem: "Generalist cloud LLMs leak confidential schemas, suffer 2-5s latency bottlenecks, hallucinate SQL syntax, and cost thousands in variable API tokens.",
        solution: "A domain-specialized 5.4M micro-transformer with in-memory schema graphing, deterministic AST validation, and native code generation for Snowflake, Databricks, dbt, and Power BI.",
        highlights: [
          "Automated Schema Understanding & PII Dictionary: Ingests metadata and documents cryptic tables automatically.",
          "Lakehouse Engineering Automation: Generates Snowpark tasks, Databricks Delta Lake optimizations, and dbt models.",
          "Self-Healing SQL & BI Synthesis: Auto-fixes syntax errors and compiles directly to Vega-Lite / Power BI DAX."
        ]
      },
      {
        slideNum: 2,
        slideType: "architecture",
        slideTag: "Technical Architecture & Pipeline",
        slideTitle: "Universal Studio Cross-Engine Architecture",
        slideSubtitle: "In-memory Information Schema Knowledge Graph coupled with a multi-dialect neural compiler.",
        architecture: "In-Memory Schema Graph + Cross-Engine AST Transpiler + 5.4M Transformer Core + BI / Lakehouse Compilers",
        flowSteps: [
          { step: "01", title: "Metadata Ingestion", desc: "Crawls Snowflake, Databricks, Postgres information schemas to build an active semantic graph." },
          { step: "02", title: "Intent & Dialect Routing", desc: "Classifies task into Schema Q&A, Lakehouse Pipeline, SQL Query, or BI Visual Spec." },
          { step: "03", title: "Neural Synthesis & AST Gate", desc: "Generates code and runs it through sqlglot deterministic AST validation for 100% safety." },
          { step: "04", title: "Multi-Target Delivery", desc: "Deploys verified Snowpark tasks, Delta Lake maintenance, dbt models, or interactive WebGL charts." }
        ],
        stack: "Python, sqlglot, PyTorch Micro-Decoder (5.4M), Vega-Lite, Snowflake Snowpark, Delta Lake, WASM",
        codeSnippet: "-- Automated Lakehouse Generation (Snowflake Dynamic Table + dbt Model)\nCREATE OR REPLACE DYNAMIC TABLE gold_customer_cohorts\n  TARGET_LAG = '1 hour'\n  WAREHOUSE = compute_wh\nAS SELECT cohort_month, COUNT(user_id) AS active_users, SUM(ltv) AS cohort_revenue FROM silver_events GROUP BY 1;"
      }
    ]
  },
  {
    id: "idea_02",
    tag: "IDEA 02 // CODE-TO-COMMERCIALIZATION",
    title: "ShipDeck AI: POC-to-Product Commercialization Studio",
    subtitle: "Connect any GitHub repo or zip file to automatically synthesize the Top 5 client-ready deliverables: Pitch Deck, 1-Page Flyer, Technical Solution Doc, GTM Strategy, and ROI Case Study.",
    canvasType: "poc_to_product",
    themeColor: "#FF6F00",
    themeLight: "rgba(255, 111, 0, 0.12)",
    metrics: [
      { val: "Top 5", label: "Full Deliverables" },
      { val: "< 30s", label: "Generation Time" },
      { val: "100%", label: "Codebase Verified" },
      { val: "Full GTM", label: "Sales Enablement" }
    ],
    slides: [
      {
        slideNum: 1,
        slideType: "overview",
        slideTag: "Concept & Problem Statement",
        slideTitle: "ShipDeck AI: Autonomous POC-to-GTM Studio",
        slideSubtitle: "Transforming raw engineering code into complete, client-ready commercial collateral in seconds.",
        overview: "Tech teams build high-value POCs and tools, but getting them commercialized requires weeks of tedious slide creation, flyer design, technical documentation, and pricing calculation. ShipDeck AI connects to GitHub to inspect architecture, APIs, and benchmarks, automatically outputting the 5 essential commercial deliverables.",
        problem: "Engineers resist writing sales decks and brochures, while marketing and sales teams cannot decipher complex codebases to extract accurate architecture and ROI numbers.",
        solution: "A unified code comprehension engine that extracts capabilities directly from repository ASTs to generate pitch decks, marketing flyers, solution specs, rollout plans, and ROI packs.",
        highlights: [
          "Executive Pitch Deck & Flyer: Auto-generates client sales presentations and 1-page marketing brochures.",
          "Product & Solution Doc: Produces in-depth architecture diagrams, integration specs, and security boundaries.",
          "GTM Strategy & ROI Proofs: Calculates pricing tiers, implementation milestones, and Before-vs-After savings metrics."
        ]
      },
      {
        slideNum: 2,
        slideType: "architecture",
        slideTag: "Technical Architecture & Pipeline",
        slideTitle: "Codebase Inspection & 5-Stage Deliverable Pipeline",
        slideSubtitle: "Multi-language AST parsing connected to a structured document generation engine.",
        architecture: "Codebase AST Parser + Endpoint & Schema Extractor + Semantic Capability Synthesizer + Multi-Format Compiler",
        flowSteps: [
          { step: "01", title: "Repo Ingestion", desc: "Clones GitHub repo or unpacks .zip; inspects directory hierarchy, Dockerfiles, and dependencies." },
          { step: "02", title: "AST & Schema Scan", desc: "Extracts API routes (FastAPI/Express), data schemas (Pydantic/SQL), and core algorithmic workflows." },
          { step: "03", title: "Capability Mapping", desc: "Synthesizes value proposition, target personas, hardware footprint, and competitive advantages." },
          { step: "04", title: "5-Deliverable Export", desc: "Compiles Slide Deck (PPTX/Web), Flyer (PDF), Solution Doc (MD), GTM Strategy, and ROI Pack." }
        ],
        stack: "Python, AST Parsers (Tree-sitter), PyTorch Micro-Encoder, Jinja2, WeasyPrint, Vega-Lite",
        codeSnippet: "// Output Deliverables Manifest Generated from repo: 'github.com/org/payment-router'\n1. [Deck]     Executive_Pitch_Deck_v1.html (12 Slides)\n2. [Flyer]    Product_Brochure_1Page.pdf\n3. [Solution] Solution_Architecture_Spec.md (Full Technical)\n4. [GTM]      POC_to_Production_Roadmap.md (Commercialization)\n5. [ROI]      Benchmark_ROI_Proof_Pack.json (Before vs After)"
      }
    ]
  },
  {
    id: "idea_03",
    tag: "IDEA 03 // CIVIC TECH & SMART TRAFFIC",
    title: "TrafficSentry AI: RTO Smart Junction Voice Copilot",
    subtitle: "Active audio-visual traffic enforcement with two-stage pre-challan voice warnings, cabin/safety violation detection, and automated ambulance green corridors.",
    canvasType: "rto_junction",
    themeColor: "#FFD300",
    themeLight: "rgba(255, 211, 0, 0.20)",
    metrics: [
      { val: "< 200ms", label: "Voice PA Alert" },
      { val: "99.2%", label: "ANPR Accuracy" },
      { val: "65% Faster", label: "Ambulance Corridors" },
      { val: "2-Stage", label: "Grace Warning" }
    ],
    slides: [
      {
        slideNum: 1,
        slideType: "overview",
        slideTag: "Concept & Problem Statement",
        slideTitle: "TrafficSentry AI: RTO Smart Junction Voice Copilot",
        slideSubtitle: "Transforming passive traffic signals into active, voice-assisted compliance corridors.",
        overview: "Passive challan cameras issue fines days later without altering driver behavior in real time, while emergency ambulances stay stranded in traffic. TrafficSentry AI uses edge computer vision and directional PA speakers to issue immediate 3-second grace warnings before fines, scans safety violations, and coordinates emergency green corridors.",
        problem: "Drivers ignore zebra stop lines, ride triple-seat without helmets, and block ambulances because existing camera systems lack active, immediate feedback.",
        solution: "An edge AI junction copilot with real-time ANPR, polarized in-cabin vision, acoustic siren detection, and targeted directional voice announcements.",
        highlights: [
          "Two-Stage Stop-Line Intervention: Warns creeping vehicles via voice PA before generating an official challan.",
          "Active Safety Enforcement: Instant detection of triple seat, no helmet, unfastened seatbelts, and dark illegal window tint.",
          "Emergency Green Corridor: Visual & acoustic siren detection with automated lane-clearing audio broadcasts."
        ]
      },
      {
        slideNum: 2,
        slideType: "architecture",
        slideTag: "Technical Architecture & Pipeline",
        slideTitle: "Edge Vision & Audio Actuation Pipeline",
        slideSubtitle: "Polarized camera feeds, acoustic siren spectrograms, and multi-lingual voice synthesis.",
        architecture: "Polarized 4K Vision + Edge ANPR OCR + Acoustic Siren Classifier + Directional PA Audio Horns + Parivahan API",
        flowSteps: [
          { step: "01", title: "Edge Video & Audio Stream", desc: "4K polarized cameras scan stop lines & in-cabin seats; micro-array mics capture emergency siren frequencies." },
          { step: "02", title: "Neural Violation Inference", desc: "Runs ANPR plate extraction, helmet/triple-seat pose estimation, and window tint optical density analysis." },
          { step: "03", title: "2-Stage Decision Gate", desc: "Triggers 3-second directional voice warning. If ignored or severe, commits cryptographic violation hash." },
          { step: "04", title: "Actuation & Dispatch", desc: "Broadcasts voice alert over PA horn, updates LED message board, and pushes instant e-challan to Parivahan." }
        ],
        stack: "Edge GPU (NVIDIA Jetson), YOLOv10 Pose, PyTorch Audio CNN, TTS Voice Horns, Parivahan API",
        codeSnippet: "// Edge Event Dispatched: 2-Stage Warning Triggered\n{\n  \"junction\": \"JK_CHOWK_04\",\n  \"plate\": \"MH 12 AB 1234\",\n  \"violation\": \"STOP_LINE_BREACH_STAGE_1\",\n  \"voice_alert\": \"Warning: White Sedan [MH 12 AB 1234], please move behind the stop line.\",\n  \"status\": \"GRACE_PERIOD_ACTIVE (3s)\"\n}"
      }
    ]
  },
  {
    id: "idea_04",
    tag: "IDEA 04 // AUTONOMOUS AGILE & WORKFORCE OS",
    title: "TeamForge AI: Autonomous Agile & Workforce OS",
    subtitle: "AI-powered team management replacing Jira manual overhead with bandwidth-aware task allotment, zero-touch automated timesheets, and domain-focused micro-transformers.",
    canvasType: "team_orchestration",
    themeColor: "#BCB88A",
    themeLight: "rgba(188, 184, 138, 0.22)",
    metrics: [
      { val: "0 Manual", label: "Timesheet Entries" },
      { val: "+35%", label: "Sprint Velocity" },
      { val: "100%", label: "Org Transparency" },
      { val: "Domain LoRA", label: "Industry Adapted" }
    ],
    slides: [
      {
        slideNum: 1,
        slideType: "overview",
        slideTag: "Concept & Problem Statement",
        slideTitle: "TeamForge AI: Autonomous Agile & Workforce OS",
        slideSubtitle: "Everything Jira does, plus autonomous bandwidth matching, zero manual timesheets, and domain intelligence.",
        overview: "Traditional project trackers (Jira, Asana) act as passive, bureaucratic databases forcing engineers to spend hours filling manual timesheets while managers guess task allocation. TeamForge AI uses domain-specialized micro-models to automatically assign tasks based on live bandwidth, track progress passively via Git telemetry, and enforce domain standards.",
        problem: "Manual timesheet overhead frustrates developers, blind task allotment causes burnout, and generic ticket systems fail to understand domain-specific compliance or technical nuances.",
        solution: "An autonomous workforce intelligence platform that matches tasks to engineer skill graphs and bandwidth, infers hours passively from commits, and alerts leads to industry tech upgrades.",
        highlights: [
          "Bandwidth-Aware Auto-Allotment: Matches backlog items to real-time developer cognitive capacity and skill proficiencies.",
          "Zero-Touch Timesheets: Infers hours and milestones passively from Git commits, PRs, and voice memos.",
          "Domain LoRA Intelligence & Tech Radar: Specialized models (Fintech, MedTech, Data Lakes) + proactive framework modernization alerts."
        ]
      },
      {
        slideNum: 2,
        slideType: "architecture",
        slideTag: "Technical Architecture & Pipeline",
        slideTitle: "Neural Workforce Engine & Telemetry Pipeline",
        slideSubtitle: "Passive developer telemetry, dynamic capacity graph, and domain-specialized LoRA models.",
        architecture: "Passive Git/IDE Telemetry Gateway + Dynamic Skill/Bandwidth Graph + Domain LoRA Micro-Transformer + Blocker Engine",
        flowSteps: [
          { step: "01", title: "Signal Ingestion", desc: "Passively ingests Git commits, PR reviews, voice memos, and incoming backlog requirements." },
          { step: "02", title: "Neural Capacity Matching", desc: "Evaluates developer cognitive load, historical velocity, and skill profiles to auto-assign tasks." },
          { step: "03", title: "Domain Checklist Generation", desc: "Applies industry LoRA (Fintech, MedTech, Lakehouse) to generate acceptance tests & compliance gates." },
          { step: "04", title: "Zero-Touch Logging & Radar", desc: "Auto-reconciles sprint burndown, generates timesheets, and surfaces framework upgrade alerts." }
        ],
        stack: "Python, PyTorch Micro-Transformer, Tree-sitter, Git Telemetry API, Webhooks, FastAPI",
        codeSnippet: "// Autonomous Task Allocation & Telemetry Inferred\n{\n  \"ticket_id\": \"TF-4192\",\n  \"title\": \"Implement Idempotent Stripe Webhook Handler\",\n  \"assigned_to\": \"Alex K. (Bandwidth: 65% | Senior Backend)\",\n  \"effort_inferred\": \"3.5 hrs (via 4 commits + 1 PR)\",\n  \"compliance_gate\": \"PCI-DSS Idempotency Verified\"\n}"
      }
    ]
  }
];
