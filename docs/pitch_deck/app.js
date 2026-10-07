// Tiny SQL LLM - Web Presentation Controller & 12 Interactive Abstract Simulators

class PresentationApp {
  constructor() {
    this.currentSlide = 0;
    this.slides = document.querySelectorAll('.slide');
    this.totalSlides = this.slides.length;
    this.slidesTrack = document.getElementById('slidesTrack');
    this.progressBar = document.getElementById('progressBar');
    this.currentSlideEl = document.getElementById('currentSlideNum');
    this.totalSlidesEl = document.getElementById('totalSlidesNum');
    this.prevBtn = document.getElementById('prevSlideBtn');
    this.nextBtn = document.getElementById('nextSlideBtn');
    this.drawerOverlay = document.getElementById('drawerOverlay');
    this.genAiModal = document.getElementById('genAiModalOverlay');

    this.slide6ActiveLayer = 'rope';
    this.slide9ActiveScenario = 'scenario1';

    this.currentGenAiIdeaIdx = 0;
    this.currentGenAiSlideIdx = 0;
    this.genAiCanvasAnimId = null;

    this.init();
  }

  init() {
    if (this.totalSlidesEl) this.totalSlidesEl.textContent = this.totalSlides;
    this.updateSlide(0);

    this.prevBtn?.addEventListener('click', () => this.prev());
    this.nextBtn?.addEventListener('click', () => this.next());

    window.addEventListener('keydown', (e) => {
      if (['input', 'textarea', 'select'].includes(document.activeElement.tagName.toLowerCase())) {
        return;
      }

      const isGenAiModalOpen = this.genAiModal?.classList.contains('open');

      if (e.key === 'Escape') {
        if (isGenAiModalOpen) {
          this.closeGenAiModal();
        } else {
          this.closeDrawer();
        }
        return;
      }

      if (isGenAiModalOpen) {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
          e.preventDefault();
          this.nextGenAiSlide();
        } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
          e.preventDefault();
          this.prevGenAiSlide();
        } else if (e.key === 'Tab') {
          e.preventDefault();
          if (e.shiftKey) {
            this.prevGenAiIdea();
          } else {
            this.nextGenAiIdea();
          }
        }
        return;
      }

      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
        e.preventDefault();
        this.next();
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        this.prev();
      } else if (e.key === 'Home') {
        this.goTo(0);
      } else if (e.key === 'End') {
        this.goTo(this.totalSlides - 1);
      } else if (e.key === 'f' || e.key === 'F') {
        this.toggleFullscreen();
      }
    });

    document.getElementById('openDrawerBtn')?.addEventListener('click', () => this.openDrawer());
    document.getElementById('closeDrawerBtn')?.addEventListener('click', () => this.closeDrawer());
    this.drawerOverlay?.addEventListener('click', (e) => {
      if (e.target === this.drawerOverlay) this.closeDrawer();
    });

    this.renderDrawerList();

    // Initialize all simulators & interactive handlers
    this.initPipelineSimulator();
    this.initTokenizerDemo();
    this.initArchitectureExplorer();
    this.initRagExplorer();
    this.initSandboxPlayground();
    this.initTcoCalculator();
    this.initGenAiWorkspace();

    // Canvas visualizers
    this.initAllCanvasArtifacts();
  }

  openGenAiModal() {
    this.genAiModal?.classList.add('open');
    this.renderGenAiTabs();
    this.renderGenAiCurrentIdea();
  }

  closeGenAiModal() {
    this.genAiModal?.classList.remove('open');
    if (this.genAiCanvasAnimId) {
      cancelAnimationFrame(this.genAiCanvasAnimId);
      this.genAiCanvasAnimId = null;
    }
  }

  updateSlide(index) {
    if (index < 0 || index >= this.totalSlides) return;
    this.currentSlide = index;

    if (this.slidesTrack) {
      this.slidesTrack.style.transform = `translateX(-${this.currentSlide * 100}vw)`;
    }

    this.slides.forEach((slide, idx) => {
      slide.classList.toggle('active', idx === this.currentSlide);
    });

    if (this.currentSlideEl) this.currentSlideEl.textContent = this.currentSlide + 1;
    if (this.progressBar) {
      const progressPercent = ((this.currentSlide + 1) / this.totalSlides) * 100;
      this.progressBar.style.width = `${progressPercent}%`;
    }

    if (this.prevBtn) this.prevBtn.disabled = this.currentSlide === 0;
    if (this.nextBtn) this.nextBtn.disabled = this.currentSlide === this.totalSlides - 1;

    const drawerItems = document.querySelectorAll('.drawer-item');
    drawerItems.forEach((item, idx) => {
      item.classList.toggle('active', idx === this.currentSlide);
    });

    window.dispatchEvent(new Event('resize'));
  }

  next() {
    if (this.currentSlide < this.totalSlides - 1) {
      this.updateSlide(this.currentSlide + 1);
    }
  }

  prev() {
    if (this.currentSlide > 0) {
      this.updateSlide(this.currentSlide - 1);
    }
  }

  goTo(index) {
    this.updateSlide(index);
    this.closeDrawer();
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }

  openDrawer() {
    this.drawerOverlay?.classList.add('open');
  }

  closeDrawer() {
    this.drawerOverlay?.classList.remove('open');
  }

  renderDrawerList() {
    const listEl = document.getElementById('drawerList');
    if (!listEl) return;
    listEl.innerHTML = '';

    this.slides.forEach((slide, idx) => {
      const title = slide.querySelector('.slide-title')?.textContent.trim() || `Slide ${idx + 1}`;
      const item = document.createElement('div');
      item.className = `drawer-item ${idx === this.currentSlide ? 'active' : ''}`;
      item.innerHTML = `
        <span class="drawer-item-num">${String(idx + 1).padStart(2, '0')}</span>
        <span class="drawer-item-title">${escapeHtml(title)}</span>
      `;
      item.addEventListener('click', () => this.goTo(idx));
      listEl.appendChild(item);
    });
  }

  // =========================================================================
  // Canvas Abstract Artifacts for all 12 slides
  // =========================================================================
  initAllCanvasArtifacts() {
    this.setupSlide1Canvas();
    this.setupSlide2Canvas();
    this.setupSlide3Canvas();
    this.setupSlide5Canvas();
    this.setupSlide6Canvas();
    this.setupSlide7Canvas();
    this.setupSlide8Canvas();
    this.setupSlide9Canvas();
    this.setupSlide10Canvas();
    this.setupSlide11Canvas();
    this.setupSlide12Canvas();
  }

  // Slide 1: Neural SQL Core Radar
  setupSlide1Canvas() {
    const canvas = document.getElementById('canvas-slide-1');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    const render = () => {
      if (this.currentSlide === 0) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);
        const cx = w / 2;
        const cy = h / 2;

        for (let r = 25; r <= 85; r += 20) {
          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(56, 189, 248, ${0.15 - r * 0.001})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }

        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(t * 0.02);
        ctx.beginPath();
        ctx.arc(0, 0, 18, 0, Math.PI * 2);
        ctx.fillStyle = '#0284c7';
        ctx.fill();
        ctx.restore();

        const nodes = [
          { label: 'SCHEMA [7 TABLES]', angle: t * 0.03, r: 50, color: '#38bdf8' },
          { label: 'ROPE MATRIX', angle: -t * 0.025 + 2, r: 70, color: '#818cf8' },
          { label: 'SQL AST OUT', angle: t * 0.02 + 4, r: 85, color: '#34d399' }
        ];

        nodes.forEach(n => {
          const nx = cx + Math.cos(n.angle) * n.r;
          const ny = cy + Math.sin(n.angle) * n.r;

          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(nx, ny);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(nx, ny, 3.5, 0, Math.PI * 2);
          ctx.fillStyle = n.color;
          ctx.fill();

          ctx.font = '9px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(n.label, nx + 6, ny + 3);
        });

        ctx.font = '10px monospace';
        ctx.fillStyle = '#e2e8f0';
        ctx.textAlign = 'center';
        ctx.fillText('6.16M CORE', cx, cy + 32);
        ctx.textAlign = 'left';

        t += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 2: Exfiltration Risk vs Air-Gapped Airwall
  setupSlide2Canvas() {
    const canvas = document.getElementById('canvas-slide-2');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let offset = 0;

    const render = () => {
      if (this.currentSlide === 1) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        const midX = w / 2;

        ctx.fillStyle = 'rgba(239, 68, 68, 0.05)';
        ctx.fillRect(10, 10, midX - 15, h - 20);
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.3)';
        ctx.strokeRect(10, 10, midX - 15, h - 20);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#f87171';
        ctx.fillText('PUBLIC CLOUD API [EXFILTRATION]', 20, 28);

        const leakY = (offset * 1.5) % (h - 60) + 40;
        ctx.beginPath();
        ctx.arc(midX / 2, leakY, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#ef4444';
        ctx.fill();
        ctx.fillText('schema_dump.json -> API', midX / 2 + 10, leakY + 3);

        ctx.fillStyle = 'rgba(52, 211, 153, 0.05)';
        ctx.fillRect(midX + 5, 10, midX - 15, h - 20);
        ctx.strokeStyle = 'rgba(52, 211, 153, 0.3)';
        ctx.strokeRect(midX + 5, 10, midX - 15, h - 20);

        ctx.fillStyle = '#34d399';
        ctx.fillText('AIRWALL VPC [100% PRIVATE]', midX + 15, 28);

        const loopAngle = offset * 0.05;
        const loopCx = midX + (midX - 10) / 2;
        const loopCy = h / 2 + 10;
        ctx.beginPath();
        ctx.arc(loopCx, loopCy, 28, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(52, 211, 153, 0.25)';
        ctx.stroke();

        const px = loopCx + Math.cos(loopAngle) * 28;
        const py = loopCy + Math.sin(loopAngle) * 28;
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#10b981';
        ctx.fill();
        ctx.fillText('Local DB Loop', loopCx - 32, loopCy + 4);

        offset += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 3: Parameter Knowledge Density Spectrum
  setupSlide3Canvas() {
    const canvas = document.getElementById('canvas-slide-3');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    const render = () => {
      if (this.currentSlide === 2) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('70B CLOUD MODEL: 99.8% GENERAL DILUTION', 20, 30);
        
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(20, 40, w - 40, 24);
        ctx.fillStyle = '#38bdf8';
        ctx.fillRect(20, 40, (w - 40) * 0.005, 24);

        ctx.font = '9px monospace';
        ctx.fillStyle = '#ef4444';
        ctx.fillText('0.2% SQL Knowledge', 20, 78);

        ctx.fillStyle = '#94a3b8';
        ctx.fillText('TINY SQL LLM: 100% RELATIONAL DENSITY', 20, 115);

        const pulseAlpha = 0.7 + Math.sin(t * 0.05) * 0.3;
        ctx.fillStyle = `rgba(16, 185, 129, ${pulseAlpha})`;
        ctx.fillRect(20, 125, w - 40, 24);

        ctx.fillStyle = '#10b981';
        ctx.fillText('100% Dedicated SQL, AST & Relational Algebra (6.16M Weights)', 20, 165);

        t += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 5: BPE Byte Slicer Laser Animation
  setupSlide5Canvas() {
    const canvas = document.getElementById('canvas-slide-5');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let laserX = 0;

    const render = () => {
      if (this.currentSlide === 4) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('BYTE-LEVEL BPE VOCAB SLICER (4,096 TOKENS)', 20, 25);

        ctx.fillStyle = '#fee2e2';
        ctx.strokeStyle = '#f87171';
        const genericTokens = ['PART', 'ITION', '_', 'BY', 'D', 'ENSE', '_', 'RANK'];
        let gx = 20;
        genericTokens.forEach(tok => {
          const tw = ctx.measureText(tok).width + 12;
          ctx.fillRect(gx, 45, tw, 22);
          ctx.strokeRect(gx, 45, tw, 22);
          ctx.fillStyle = '#991b1b';
          ctx.fillText(tok, gx + 6, 59);
          ctx.fillStyle = '#fee2e2';
          gx += tw + 4;
        });

        ctx.fillStyle = '#e0f2fe';
        ctx.strokeStyle = '#38bdf8';
        const customTokens = ['PARTITION BY', 'DENSE_RANK()', 'OVER()', 'FROM'];
        let cx = 20;
        customTokens.forEach(tok => {
          const tw = ctx.measureText(tok).width + 14;
          ctx.fillRect(cx, 95, tw, 26);
          ctx.strokeRect(cx, 95, tw, 26);
          ctx.fillStyle = '#0369a1';
          ctx.fillText(tok, cx + 7, 111);
          ctx.fillStyle = '#e0f2fe';
          cx += tw + 8;
        });

        laserX = (laserX + 2) % (w - 30);
        ctx.beginPath();
        ctx.moveTo(20 + laserX, 35);
        ctx.lineTo(20 + laserX, 140);
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.8)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.font = '9px monospace';
        ctx.fillStyle = '#38bdf8';
        ctx.fillText('BPE Token Boundary Scanner', 20, 155);
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 6: 5 DISTINCT Dynamic Visualizations for each Layer
  setupSlide6Canvas() {
    const canvas = document.getElementById('canvas-slide-6');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    const render = () => {
      if (this.currentSlide === 5) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        const mode = this.slide6ActiveLayer;

        if (mode === 'rope') {
          // Visual 1: RoPE Rotary Position Embeddings
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('ROTARY POSITION EMBEDDINGS (RoPE) ROTATION VECTORS', 15, 20);

          const cx = w / 2;
          const cy = h / 2 + 10;
          const r = 55;

          ctx.beginPath();
          ctx.arc(cx, cy, r, 0, Math.PI * 2);
          ctx.strokeStyle = '#334155';
          ctx.stroke();

          const qAngle = t * 0.03;
          const kAngle = qAngle + 1.15;

          const qx = cx + Math.cos(qAngle) * r;
          const qy = cy + Math.sin(qAngle) * r;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(qx, qy);
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 2;
          ctx.stroke();

          const kx = cx + Math.cos(kAngle) * r;
          const ky = cy + Math.sin(kAngle) * r;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(kx, ky);
          ctx.strokeStyle = '#34d399';
          ctx.lineWidth = 2;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(cx, cy, 22, qAngle, kAngle);
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          ctx.font = '9px monospace';
          ctx.fillStyle = '#38bdf8';
          ctx.fillText('Query q_m', qx + 6, qy);
          ctx.fillStyle = '#34d399';
          ctx.fillText('Key k_n', kx + 6, ky);
          ctx.fillStyle = '#f59e0b';
          ctx.fillText('Δθ = m - n (Distance Invariant)', cx - 80, cy + r + 24);

        } else if (mode === 'rmsnorm') {
          // Visual 2: RMSNorm Vector Normalization
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('RMSNORM NORMALIZATION SCALING (NO MEAN CENTERING)', 15, 20);

          const padL = 25;
          const padB = h - 25;
          const padT = 40;
          const padR = w - 25;

          ctx.beginPath();
          ctx.moveTo(padL, padB);
          ctx.lineTo(padR, padB);
          ctx.strokeStyle = '#334155';
          ctx.stroke();

          ctx.beginPath();
          for (let x = padL; x <= padR; x += 3) {
            const rawY = padB - 20 - Math.sin((x - padL) * 0.08 + t * 0.05) * 45;
            if (x === padL) ctx.moveTo(x, rawY);
            else ctx.lineTo(x, rawY);
          }
          ctx.strokeStyle = '#f87171';
          ctx.setLineDash([3, 3]);
          ctx.stroke();
          ctx.setLineDash([]);

          ctx.beginPath();
          for (let x = padL; x <= padR; x += 3) {
            const normY = padB - 35 - Math.sin((x - padL) * 0.08 + t * 0.05) * 18;
            if (x === padL) ctx.moveTo(x, normY);
            else ctx.lineTo(x, normY);
          }
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 2;
          ctx.stroke();

          ctx.font = '9px monospace';
          ctx.fillStyle = '#f87171';
          ctx.fillText('Raw Activation Variance', padL + 10, padT + 12);
          ctx.fillStyle = '#38bdf8';
          ctx.fillText('RMSNorm Scaled Tensor: [Batch, 256, 256]', padL + 10, padT + 26);

        } else if (mode === 'mha') {
          // Visual 3: 8-Head Attention Heatmap & Causal Mask
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('8-HEAD CAUSAL SELF-ATTENTION TENSORS (Head Dim: 32)', 15, 20);

          const gridSize = 8;
          const cellSize = 12;
          const startX = 25;
          const startY = 38;

          for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
              if (j > i) {
                ctx.fillStyle = '#0f172a';
              } else {
                const val = Math.sin(t * 0.05 + i * 0.5 + j * 0.4) * 0.5 + 0.5;
                ctx.fillStyle = `rgba(168, 85, 247, ${val * 0.8 + 0.2})`;
              }
              ctx.fillRect(startX + j * cellSize, startY + i * cellSize, cellSize - 1, cellSize - 1);
            }
          }

          ctx.font = '9px monospace';
          ctx.fillStyle = '#cbd5e1';
          for (let hIdx = 0; hIdx < 8; hIdx++) {
            const hy = startY + hIdx * 12 + 8;
            ctx.fillStyle = hIdx % 2 === 0 ? '#38bdf8' : '#818cf8';
            ctx.fillText(`Head ${hIdx + 1}: 32-d subspace`, startX + 115, hy);
          }

        } else if (mode === 'swiglu') {
          // Visual 4: SwiGLU Gated Feed-Forward Network Dual Branch
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('SWIGLU GATED DUAL LINEAR BRANCHING [SiLU(xW_1) ⊙ xW_3] W_2', 15, 20);

          const midY = h / 2 + 5;

          ctx.fillStyle = '#1e293b';
          ctx.fillRect(15, midY - 12, 45, 24);
          ctx.strokeStyle = '#94a3b8';
          ctx.strokeRect(15, midY - 12, 45, 24);
          ctx.font = '9px monospace';
          ctx.fillStyle = '#e2e8f0';
          ctx.fillText('x (256)', 20, midY + 4);

          ctx.beginPath();
          ctx.moveTo(60, midY);
          ctx.lineTo(95, midY - 30);
          ctx.lineTo(135, midY - 30);
          ctx.strokeStyle = '#38bdf8';
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.fillRect(135, midY - 42, 75, 24);
          ctx.strokeStyle = '#38bdf8';
          ctx.strokeRect(135, midY - 42, 75, 24);
          ctx.fillStyle = '#38bdf8';
          ctx.fillText('SiLU(xW_1)', 140, midY - 26);

          ctx.beginPath();
          ctx.moveTo(60, midY);
          ctx.lineTo(95, midY + 30);
          ctx.lineTo(135, midY + 30);
          ctx.strokeStyle = '#34d399';
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.fillRect(135, midY + 18, 75, 24);
          ctx.strokeStyle = '#34d399';
          ctx.strokeRect(135, midY + 18, 75, 24);
          ctx.fillStyle = '#34d399';
          ctx.fillText('Linear(xW_3)', 140, midY + 34);

          ctx.beginPath();
          ctx.moveTo(210, midY - 30);
          ctx.lineTo(235, midY);
          ctx.moveTo(210, midY + 30);
          ctx.lineTo(235, midY);
          ctx.strokeStyle = '#f59e0b';
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(245, midY, 12, 0, Math.PI * 2);
          ctx.fillStyle = '#1e293b';
          ctx.fill();
          ctx.strokeStyle = '#f59e0b';
          ctx.stroke();
          ctx.fillStyle = '#f59e0b';
          ctx.fillText('⊙', 242, midY + 4);

          ctx.beginPath();
          ctx.moveTo(257, midY);
          ctx.lineTo(285, midY);
          ctx.strokeStyle = '#e2e8f0';
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.fillRect(285, midY - 12, 60, 24);
          ctx.strokeStyle = '#e2e8f0';
          ctx.strokeRect(285, midY - 12, 60, 24);
          ctx.fillStyle = '#e2e8f0';
          ctx.fillText('Out W_2', 290, midY + 4);

        } else if (mode === 'tiedhead') {
          // Visual 5: Weight-Tied Output LM Head Bridge
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('WEIGHT-TIED LM HEAD [W_token_embed == W_lm_head^T]', 15, 20);

          const midY = h / 2 + 10;

          ctx.fillStyle = '#1e293b';
          ctx.fillRect(25, midY - 25, 90, 50);
          ctx.strokeStyle = '#38bdf8';
          ctx.strokeRect(25, midY - 25, 90, 50);
          ctx.font = '9px monospace';
          ctx.fillStyle = '#38bdf8';
          ctx.fillText('TOKEN EMBED', 32, midY - 8);
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('[4096 x 256]', 34, midY + 12);

          ctx.fillStyle = '#1e293b';
          ctx.fillRect(w - 125, midY - 25, 90, 50);
          ctx.strokeStyle = '#34d399';
          ctx.strokeRect(w - 125, midY - 25, 90, 50);
          ctx.fillStyle = '#34d399';
          ctx.fillText('LM HEAD', w - 105, midY - 8);
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('[256 x 4096]', w - 116, midY + 12);

          const flowOffset = (t * 2) % 30;
          ctx.beginPath();
          ctx.moveTo(115, midY);
          ctx.lineTo(w - 125, midY);
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 6]);
          ctx.lineDashOffset = -flowOffset;
          ctx.stroke();
          ctx.setLineDash([]);

          ctx.font = '9.5px monospace';
          ctx.fillStyle = '#f59e0b';
          ctx.textAlign = 'center';
          ctx.fillText('SHARED WEIGHT TENSOR', w / 2, midY - 12);
          ctx.fillStyle = '#34d399';
          ctx.fillText('★ Saved 1,048,576 Redundant Parameters', w / 2, midY + 22);
          ctx.textAlign = 'left';
        }

        t += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 7: Convergence Dynamics Loss Curve
  setupSlide7Canvas() {
    const canvas = document.getElementById('canvas-slide-7');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const points = [
      { epoch: 1, loss: 3.4772, ppl: 32.37 },
      { epoch: 2, loss: 2.8873, ppl: 17.95 },
      { epoch: 3, loss: 2.6119, ppl: 13.63 },
      { epoch: 4, loss: 2.4807, ppl: 11.95 },
      { epoch: 5, loss: 2.4371, ppl: 11.44 }
    ];

    const render = () => {
      if (this.currentSlide === 6) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('VALIDATION LOSS & PERPLEXITY DESCENT', 20, 22);

        const padL = 35;
        const padB = h - 30;
        const padT = 35;
        const padR = w - 20;

        ctx.beginPath();
        ctx.moveTo(padL, padT);
        ctx.lineTo(padL, padB);
        ctx.lineTo(padR, padB);
        ctx.strokeStyle = '#334155';
        ctx.stroke();

        const getX = (idx) => padL + (idx / (points.length - 1)) * (padR - padL);
        const getY = (loss) => padB - ((loss - 2.2) / (3.8 - 2.2)) * (padB - padT);

        ctx.beginPath();
        points.forEach((p, idx) => {
          const px = getX(idx);
          const py = getY(p.loss);
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 2;
        ctx.stroke();

        points.forEach((p, idx) => {
          const px = getX(idx);
          const py = getY(p.loss);
          ctx.beginPath();
          ctx.arc(px, py, 3.5, 0, Math.PI * 2);
          ctx.fillStyle = idx === 4 ? '#10b981' : '#38bdf8';
          ctx.fill();

          ctx.font = '8.5px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(`E${p.epoch}`, px - 6, padB + 15);
          ctx.fillText(`${p.loss}`, px - 10, py - 8);
        });
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 8: 194-Topic Vector Space Canvas
  setupSlide8Canvas() {
    const canvas = document.getElementById('vectorNetworkCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const clusters = [
      { name: 'Window Functions', x: 0.22, y: 0.45, count: 15, color: '#38bdf8' },
      { name: 'Common Table Expressions', x: 0.38, y: 0.32, count: 10, color: '#818cf8' },
      { name: 'Relational Joins & Sets', x: 0.52, y: 0.65, count: 15, color: '#34d399' },
      { name: 'Aggregations & Grouping', x: 0.68, y: 0.35, count: 15, color: '#f472b6' },
      { name: 'DDL & Constraints', x: 0.82, y: 0.55, count: 15, color: '#fbbf24' },
      { name: 'ACID & Transactions', x: 0.18, y: 0.75, count: 12, color: '#60a5fa' },
      { name: 'Indexing & CBO', x: 0.45, y: 0.82, count: 12, color: '#a78bfa' },
      { name: 'Normalization (1NF-5NF)', x: 0.75, y: 0.78, count: 10, color: '#4ade80' }
    ];

    let nodes = [];
    clusters.forEach((c, cIdx) => {
      for (let i = 0; i < c.count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 22 + 4;
        nodes.push({
          clusterIdx: cIdx,
          baseX: c.x,
          baseY: c.y,
          offsetX: Math.cos(angle) * radius,
          offsetY: Math.sin(angle) * radius,
          color: c.color,
          radius: Math.random() * 1.5 + 2
        });
      }
    });

    let activeClusterIdx = 0;
    let queryPulse = 0;

    const render = () => {
      if (this.currentSlide === 7) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        nodes.forEach(n => {
          const nx = n.baseX * w + n.offsetX;
          const ny = n.baseY * h + n.offsetY;
          const isClusterActive = n.clusterIdx === activeClusterIdx;

          ctx.beginPath();
          ctx.arc(nx, ny, isClusterActive ? n.radius + 1 : n.radius, 0, Math.PI * 2);
          ctx.fillStyle = isClusterActive ? '#38bdf8' : n.color;
          ctx.globalAlpha = isClusterActive ? 1 : 0.5;
          ctx.fill();
          ctx.globalAlpha = 1;
        });

        const tc = clusters[activeClusterIdx];
        if (tc) {
          const cx = tc.x * w;
          const cy = tc.y * h;
          ctx.beginPath();
          ctx.arc(cx, cy, 26 + Math.sin(queryPulse) * 3, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
          ctx.fill();
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.5)';
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(15, h / 2);
          ctx.lineTo(cx, cy);
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.6)';
          ctx.setLineDash([3, 3]);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        queryPulse += 0.05;
      }
      requestAnimationFrame(render);
    };
    render();

    this.vectorNetwork = {
      setActiveCluster: (idx, metricsText) => {
        activeClusterIdx = idx;
        const mEl = document.getElementById('vectorSearchMetrics');
        if (mEl) mEl.textContent = metricsText;
      }
    };
  }

  // Slide 9: 3 DISTINCT AST Parse Tree Visualizations for each Scenario
  setupSlide9Canvas() {
    const canvas = document.getElementById('canvas-slide-9');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const render = () => {
      if (this.currentSlide === 8) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        const scenario = this.slide9ActiveScenario;
        const rx = w / 2;
        const ry = 35;

        const drawNode = (text, x, y, col) => {
          ctx.fillStyle = '#1e293b';
          ctx.fillRect(x - 32, y - 9, 64, 18);
          ctx.strokeStyle = col || '#38bdf8';
          ctx.strokeRect(x - 32, y - 9, 64, 18);
          ctx.font = '8px monospace';
          ctx.fillStyle = '#e2e8f0';
          ctx.textAlign = 'center';
          ctx.fillText(text, x, y + 3);
          ctx.textAlign = 'left';
        };

        const drawEdge = (x1, y1, x2, y2) => {
          ctx.beginPath();
          ctx.moveTo(x1, y1 + 9);
          ctx.lineTo(x2, y2 - 9);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
          ctx.stroke();
        };

        if (scenario === 'scenario1') {
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('AST PARSE TREE: MULTI-TABLE INNER JOIN & ORDER', 15, 18);

          drawNode('SELECT', rx, ry, '#34d399');

          const l1 = [
            { name: 'PROJECTION', x: rx - 75, y: ry + 36 },
            { name: 'FROM', x: rx, y: ry + 36 },
            { name: 'ORDER BY', x: rx + 75, y: ry + 36 }
          ];

          l1.forEach(n => {
            drawEdge(rx, ry, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#38bdf8');
          });

          const l2 = [
            { name: 'emp_name, sal', x: rx - 95, y: ry + 72, parent: l1[0] },
            { name: 'dept_name', x: rx - 48, y: ry + 72, parent: l1[0] },
            { name: 'JOIN: dept', x: rx, y: ry + 72, parent: l1[1] },
            { name: 'DESC LIMIT 4', x: rx + 75, y: ry + 72, parent: l1[2] }
          ];

          l2.forEach(n => {
            drawEdge(n.parent.x, n.parent.y, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#818cf8');
          });

        } else if (scenario === 'scenario2') {
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('AST PARSE TREE: AGGREGATION & GROUP BY CATEGORY', 15, 18);

          drawNode('SELECT', rx, ry, '#f59e0b');

          const l1 = [
            { name: 'AGGREGATES', x: rx - 75, y: ry + 36 },
            { name: 'FROM: products', x: rx, y: ry + 36 },
            { name: 'GROUP BY', x: rx + 75, y: ry + 36 }
          ];

          l1.forEach(n => {
            drawEdge(rx, ry, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#f59e0b');
          });

          const l2 = [
            { name: 'COUNT(item_id)', x: rx - 100, y: ry + 72, parent: l1[0] },
            { name: 'SUM(revenue)', x: rx - 48, y: ry + 72, parent: l1[0] },
            { name: 'JOIN: order_item', x: rx, y: ry + 72, parent: l1[1] },
            { name: 'category', x: rx + 75, y: ry + 72, parent: l1[2] }
          ];

          l2.forEach(n => {
            drawEdge(n.parent.x, n.parent.y, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#34d399');
          });

        } else if (scenario === 'scenario3') {
          ctx.font = '10px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText('AST PARSE TREE: LEFT JOIN COHORT MULTI-GROUPING', 15, 18);

          drawNode('SELECT', rx, ry, '#a855f7');

          const l1 = [
            { name: 'COHORTS', x: rx - 75, y: ry + 36 },
            { name: 'LEFT JOIN', x: rx, y: ry + 36 },
            { name: 'GROUP BY', x: rx + 75, y: ry + 36 }
          ];

          l1.forEach(n => {
            drawEdge(rx, ry, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#a855f7');
          });

          const l2 = [
            { name: 'region, segment', x: rx - 95, y: ry + 72, parent: l1[0] },
            { name: 'AVG(total_amt)', x: rx - 48, y: ry + 72, parent: l1[0] },
            { name: 'orders: c_id', x: rx, y: ry + 72, parent: l1[1] },
            { name: '1, 2 ORDER DESC', x: rx + 75, y: ry + 72, parent: l1[2] }
          ];

          l2.forEach(n => {
            drawEdge(n.parent.x, n.parent.y, n.x, n.y);
            drawNode(n.name, n.x, n.y, '#38bdf8');
          });
        }
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 10: TCO Margin Divergence Curves
  setupSlide10Canvas() {
    const canvas = document.getElementById('canvas-slide-10');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const render = () => {
      if (this.currentSlide === 9) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('INFRASTRUCTURE COST PROJECTION', 20, 22);

        const padL = 30;
        const padB = h - 30;
        const padT = 35;
        const padR = w - 20;

        ctx.beginPath();
        ctx.moveTo(padL, padT);
        ctx.lineTo(padL, padB);
        ctx.lineTo(padR, padB);
        ctx.strokeStyle = '#334155';
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(padL, padB - 10);
        ctx.lineTo(padR, padT + 10);
        ctx.strokeStyle = '#f87171';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = '#f87171';
        ctx.fillText('Cloud API Cost ($0.008 * N)', padR - 130, padT + 22);

        ctx.beginPath();
        ctx.moveTo(padL, padB - 18);
        ctx.lineTo(padR, padB - 18);
        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = '#34d399';
        ctx.fillText('Tiny SQL Baseline ($X Flat)', padL + 15, padB - 25);

        ctx.beginPath();
        ctx.moveTo(padL, padB - 18);
        ctx.lineTo(padR, padT + 10);
        ctx.lineTo(padR, padB - 18);
        ctx.closePath();
        ctx.fillStyle = 'rgba(52, 211, 153, 0.08)';
        ctx.fill();
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 11: Deployment Topology Network Router
  setupSlide11Canvas() {
    const canvas = document.getElementById('canvas-slide-11');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    const render = () => {
      if (this.currentSlide === 10) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        const cx = w / 2;
        const cy = h / 2;

        ctx.fillStyle = '#1e293b';
        ctx.fillRect(cx - 45, cy - 15, 90, 30);
        ctx.strokeStyle = '#38bdf8';
        ctx.strokeRect(cx - 45, cy - 15, 90, 30);
        ctx.font = '9px monospace';
        ctx.fillStyle = '#e2e8f0';
        ctx.textAlign = 'center';
        ctx.fillText('TINY SQL ENGINE', cx, cy + 3);
        ctx.textAlign = 'left';

        const nodes = [
          { name: 'Airwall VPC', x: cx - 90, y: cy - 45, col: '#34d399' },
          { name: 'Embedded BI', x: cx + 90, y: cy - 45, col: '#38bdf8' },
          { name: 'CI/CD Gate', x: cx - 90, y: cy + 45, col: '#f59e0b' },
          { name: 'Local Edge CLI', x: cx + 90, y: cy + 45, col: '#a855f7' }
        ];

        nodes.forEach(n => {
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(n.x, n.y);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.fillRect(n.x - 38, n.y - 10, 76, 20);
          ctx.strokeStyle = n.col;
          ctx.strokeRect(n.x - 38, n.y - 10, 76, 20);
          ctx.font = '8px monospace';
          ctx.fillStyle = '#cbd5e1';
          ctx.textAlign = 'center';
          ctx.fillText(n.name, n.x, n.y + 3);
          ctx.textAlign = 'left';
        });

        t += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // Slide 12: Dialect Transpiler & LoRA Adapter Hub
  setupSlide12Canvas() {
    const canvas = document.getElementById('canvas-slide-12');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    const render = () => {
      if (this.currentSlide === 11) {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        canvas.width = w * window.devicePixelRatio;
        canvas.height = h * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        ctx.clearRect(0, 0, w, h);

        ctx.font = '10px monospace';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('MULTI-DIALECT AST TRANSPILATION COMPILER', 20, 22);

        const cx = 80;
        const cy = h / 2;

        ctx.fillStyle = '#1e293b';
        ctx.fillRect(cx - 40, cy - 20, 80, 40);
        ctx.strokeStyle = '#34d399';
        ctx.strokeRect(cx - 40, cy - 20, 80, 40);
        ctx.font = '9px monospace';
        ctx.fillStyle = '#34d399';
        ctx.fillText('ANSI SQL AST', cx - 32, cy + 4);

        const dialects = [
          { name: 'PostgreSQL 16', y: cy - 40, col: '#38bdf8' },
          { name: 'Snowflake SQL', y: cy - 12, col: '#60a5fa' },
          { name: 'Google BigQuery', y: cy + 16, col: '#fbbf24' },
          { name: 'Oracle PL/SQL', y: cy + 44, col: '#f87171' }
        ];

        dialects.forEach(d => {
          ctx.beginPath();
          ctx.moveTo(cx + 40, cy);
          ctx.lineTo(w - 110, d.y);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.fillRect(w - 110, d.y - 8, 95, 18);
          ctx.strokeStyle = d.col;
          ctx.strokeRect(w - 110, d.y - 8, 95, 18);
          ctx.font = '8px monospace';
          ctx.fillStyle = '#e2e8f0';
          ctx.fillText(d.name, w - 100, d.y + 4);
        });

        t += 1;
      }
      requestAnimationFrame(render);
    };
    render();
  }

  // =========================================================================
  // Simulators & Loggers
  // =========================================================================
  initPipelineSimulator() {
    const runBtn = document.getElementById('btnRunPipeline');
    const inputEl = document.getElementById('pipelinePromptInput');
    const terminalBody = document.getElementById('pipelineTerminalBody');
    const statusPill = document.getElementById('terminalStatusPill');
    const stepEls = document.querySelectorAll('.pipeline-step');
    const lineEls = document.querySelectorAll('.step-line');

    const sampleQueries = {
      "Find top 5 highest paid employees with dept": {
        route: "TEXT_TO_SQL",
        conf: "99.8%",
        schema: "employees (emp_name, salary), departments (dept_name)",
        sql: "SELECT e.emp_name, d.dept_name, e.salary FROM employees e JOIN departments d ON e.department_id = d.department_id ORDER BY e.salary DESC LIMIT 5;",
        ast: "Parsed: AST valid, 0 dialect errors, verified SQLite read-only SELECT",
        db: "Executed in 0.018s | Rows returned: 5 | Max: $148,000 (CDO)"
      },
      "Explain difference between RANK and DENSE_RANK": {
        route: "CONCEPT_COMPARISON",
        conf: "99.4%",
        schema: "194-Vector Corpus: Window Functions - RANK vs DENSE_RANK",
        sql: "Synthesizing dynamic comparative matrix & SQL execution examples",
        ast: "Markdown AST verified: Pedagogical Synthesizer formatted",
        db: "Rendered comparative table with partition & frame behavior"
      },
      "Calculate monthly customer retention rate": {
        route: "TEXT_TO_SQL / CTE",
        conf: "99.2%",
        schema: "orders (customer_id, order_date, total_amount)",
        sql: "WITH monthly_active AS (SELECT customer_id, strftime('%Y-%m', order_date) as month FROM orders GROUP BY 1, 2) SELECT month, COUNT(customer_id) as active_users FROM monthly_active GROUP BY month;",
        ast: "Parsed: Valid recursive CTE syntax, grammar confirmed",
        db: "Executed in 0.024s | 12 monthly cohorts aggregated"
      }
    };

    const appendLog = (badge, badgeType, message) => {
      if (!terminalBody) return;
      const now = new Date();
      const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.${String(now.getMilliseconds()).padStart(3, '0')}`;
      
      const row = document.createElement('div');
      row.className = 'log-entry';
      row.innerHTML = `
        <span class="log-time">${timeStr}</span>
        <span class="log-badge ${badgeType}">${badge}</span>
        <span class="log-msg">${message}</span>
      `;
      terminalBody.appendChild(row);
      terminalBody.scrollTop = terminalBody.scrollHeight;
    };

    if (runBtn) {
      runBtn.addEventListener('click', () => {
        const query = inputEl.value.trim() || "Find top 5 highest paid employees with dept";
        const matched = sampleQueries[query] || sampleQueries["Find top 5 highest paid employees with dept"];

        runBtn.disabled = true;
        runBtn.textContent = 'Processing...';
        if (statusPill) {
          statusPill.textContent = 'STATUS: EXECUTING';
          statusPill.style.color = '#93c5fd';
        }

        stepEls.forEach(s => s.classList.remove('active', 'completed'));
        lineEls.forEach(l => l.classList.remove('completed'));
        if (terminalBody) terminalBody.innerHTML = '';

        appendLog('INIT', 'info', `Ingesting query: "<code>${escapeHtml(query)}</code>"`);

        const steps = [
          {
            badge: 'ROUTER',
            type: 'info',
            text: `Intent routed to <b>${matched.route}</b> (Confidence score: <b>${matched.conf}</b>)`
          },
          {
            badge: 'VECTOR_RAG',
            type: 'info',
            text: `ChromaDB 384-d MiniLM matched schema context: <code>${escapeHtml(matched.schema)}</code>`
          },
          {
            badge: 'TRANSFORMER',
            type: 'info',
            text: `6.16M Transformer with RoPE & SwiGLU generated code:<br/><code>${escapeHtml(matched.sql)}</code>`
          },
          {
            badge: 'AST_CHECK',
            type: 'success',
            text: `<code>sqlglot</code> Syntax Validation passed: ${escapeHtml(matched.ast)}`
          },
          {
            badge: 'SANDBOX',
            type: 'success',
            text: `SQLite DB Execution Complete: ${escapeHtml(matched.db)}`
          }
        ];

        let currentStepIdx = 0;

        const interval = setInterval(() => {
          if (currentStepIdx > 0) {
            stepEls[currentStepIdx - 1]?.classList.remove('active');
            stepEls[currentStepIdx - 1]?.classList.add('completed');
            if (lineEls[currentStepIdx - 1]) {
              lineEls[currentStepIdx - 1].classList.add('completed');
            }
          }

          if (currentStepIdx < steps.length) {
            stepEls[currentStepIdx]?.classList.add('active');
            const s = steps[currentStepIdx];
            appendLog(s.badge, s.type, s.text);
            currentStepIdx++;
          } else {
            clearInterval(interval);
            runBtn.disabled = false;
            runBtn.textContent = 'Run Pipeline';
            if (statusPill) {
              statusPill.textContent = 'STATUS: COMPLETE';
              statusPill.style.color = '#6ee7b7';
            }
            appendLog('DAEMON', 'success', 'All pipeline stages finished with exit code 0.');
          }
        }, 750);
      });
    }

    document.querySelectorAll('.preset-query-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (inputEl) {
          inputEl.value = chip.getAttribute('data-query') || '';
          runBtn?.click();
        }
      });
    });
  }

  initTokenizerDemo() {
    const input = document.getElementById('tokInput');
    const genericOut = document.getElementById('tokGenericTokens');
    const customOut = document.getElementById('tokCustomTokens');
    const genericCount = document.getElementById('tokGenericCount');
    const customCount = document.getElementById('tokCustomCount');

    if (!input) return;

    const tokenize = () => {
      const genericSplits = [
        "SE", "LECT", " ", "D", "ENSE", "_", "R", "ANK", "(", ")", " ",
        "O", "VER", " (", "PART", "ITION", " ", "BY", " ", "depart", "ment", "_", "id", " ",
        "OR", "DER", " ", "BY", " ", "sal", "ary", " ", "DESC", ")", " ", "AS", " ", "rn", "k", " ",
        "FROM", " ", "employees", ";"
      ];

      const customSplits = [
        "SELECT", " ", "DENSE_RANK()", " ", "OVER", " ", "(", "PARTITION BY", " ",
        "department_id", " ", "ORDER BY", " ", "salary", " ", "DESC", ")", " ", "AS", " ", "rnk", " ",
        "FROM", " ", "employees", ";"
      ];

      if (genericOut) {
        genericOut.innerHTML = genericSplits.map(t => 
          `<span style="display:inline-block; padding: 2px 5px; margin: 2px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 3px; font-family: var(--font-mono); font-size: 0.74rem; color: #991b1b;">${escapeHtml(t)}</span>`
        ).join('');
      }

      if (customOut) {
        customOut.innerHTML = customSplits.map(t => 
          `<span style="display:inline-block; padding: 2px 5px; margin: 2px; background: #e0f2fe; border: 1px solid #7dd3fc; border-radius: 3px; font-family: var(--font-mono); font-size: 0.74rem; color: #0369a1;">${escapeHtml(t)}</span>`
        ).join('');
      }

      if (genericCount) genericCount.textContent = `${genericSplits.length} Tokens`;
      if (customCount) customCount.textContent = `${customSplits.length} Tokens (-42%)`;
    };

    input.addEventListener('input', tokenize);
    tokenize();
  }

  initArchitectureExplorer() {
    const layers = document.querySelectorAll('.arch-layer-item');
    const detailTitle = document.getElementById('archDetailTitle');
    const detailDesc = document.getElementById('archDetailDesc');
    const vizHeader = document.getElementById('slide6VizHeader');

    const layerDetails = {
      'rope': {
        title: 'Rotary Position Embeddings (RoPE)',
        desc: 'Applies rotational transformation matrices directly to Query and Key states. Maintains relative distance invariance across long SQL statements and deeply nested subqueries.',
        vizName: 'ROTARY POSITION EMBEDDINGS (RoPE)'
      },
      'rmsnorm': {
        title: 'RMSNorm (Root Mean Square Layer Normalization)',
        desc: 'Replaces standard LayerNorm by removing mean computation, accelerating backward pass operations and reducing memory bandwidth bottlenecks on standard CPU architectures.',
        vizName: 'RMSNORM VECTOR SCALING'
      },
      'mha': {
        title: '8-Head Causal Multi-Head Attention',
        desc: '8 parallel attention heads compute intra-sequence dependencies with upper-triangular autoregressive masking to enforce sequential generation.',
        vizName: '8-HEAD CAUSAL ATTENTION MATRIX'
      },
      'swiglu': {
        title: 'SwiGLU Gated Feed-Forward Network',
        desc: 'Gated linear unit with SiLU activation function delivering sharper gradient responses suited for formal programming languages and structured SQL grammar.',
        vizName: 'SWIGLU GATED DUAL BRANCHING'
      },
      'tiedhead': {
        title: 'Weight-Tied Output LM Head',
        desc: 'Ties token embedding weights directly to the output projection matrix, eliminating 1,048,576 redundant parameters without loss in validation perplexity.',
        vizName: 'WEIGHT-TIED LM HEAD BRIDGE'
      }
    };

    layers.forEach(layer => {
      layer.addEventListener('click', () => {
        layers.forEach(l => l.classList.remove('selected'));
        layer.classList.add('selected');
        const key = layer.getAttribute('data-layer');
        this.slide6ActiveLayer = key;

        const d = layerDetails[key];
        if (d) {
          if (detailTitle) detailTitle.textContent = d.title;
          if (detailDesc) detailDesc.textContent = d.desc;
          if (vizHeader) vizHeader.textContent = `ABSTRACT ARTIFACT: ${d.vizName}`;
        }
      });
    });
  }

  initRagExplorer() {
    const navButtons = document.querySelectorAll('.rag-nav-btn');
    const displayCard = document.getElementById('ragDisplayCard');

    const ragData = {
      'rank_vs_denserank': {
        clusterIdx: 0,
        metrics: 'Nearest Cluster: Window Functions (Cosine Dist: 0.082)',
        title: 'RANK() vs DENSE_RANK()',
        leftTitle: 'RANK()',
        leftDesc: 'Produces gaps in ranking sequence when ties occur (e.g. 1, 2, 2, 4).',
        rightTitle: 'DENSE_RANK()',
        rightDesc: 'Maintains contiguous ranking sequence without skipping values (e.g. 1, 2, 2, 3).'
      },
      'cte_vs_subquery': {
        clusterIdx: 1,
        metrics: 'Nearest Cluster: Common Table Expressions (Cosine Dist: 0.094)',
        title: 'CTE vs Subqueries',
        leftTitle: 'CTE (WITH Clause)',
        leftDesc: 'Defined upfront before main query. Clean modular structure, supports recursion.',
        rightTitle: 'Inline Subquery',
        rightDesc: 'Nested within FROM or WHERE clauses. Difficult to maintain when deeply nested.'
      },
      'delete_vs_truncate': {
        clusterIdx: 4,
        metrics: 'Nearest Cluster: DDL & Constraints (Cosine Dist: 0.076)',
        title: 'DELETE vs TRUNCATE',
        leftTitle: 'DELETE (DML)',
        leftDesc: 'Row-by-row operation. Supports WHERE filters, triggers fire, full transaction logs.',
        rightTitle: 'TRUNCATE (DDL)',
        rightDesc: 'Deallocates data pages. Resets identity counters, cannot accept WHERE filters.'
      },
      'acid_properties': {
        clusterIdx: 5,
        metrics: 'Nearest Cluster: ACID & Transactions (Cosine Dist: 0.088)',
        title: 'ACID Transaction Guarantees',
        leftTitle: 'Atomicity & Consistency',
        leftDesc: 'All operations succeed or all rollback cleanly. Database schema state is conserved.',
        rightTitle: 'Isolation & Durability',
        rightDesc: 'Concurrent transactions do not interfere (MVCC). Committed changes survive power loss.'
      }
    };

    const renderCard = (key) => {
      const data = ragData[key] || ragData['rank_vs_denserank'];
      if (!displayCard) return;

      if (this.vectorNetwork) {
        this.vectorNetwork.setActiveCluster(data.clusterIdx, data.metrics);
      }

      displayCard.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.4rem; padding-bottom: 0.3rem; border-bottom: 1px solid var(--border-light);">
          <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">${escapeHtml(data.title)}</h4>
          <span style="font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-secondary);">Dynamic Synthesizer</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
          <div style="background: var(--bg-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-sm); padding: 0.5rem;">
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.2rem;">${escapeHtml(data.leftTitle)}</div>
            <p style="font-size: 0.74rem; color: var(--text-secondary);">${escapeHtml(data.leftDesc)}</p>
          </div>

          <div style="background: var(--bg-subtle); border: 1px solid var(--border-light); border-radius: var(--radius-sm); padding: 0.5rem;">
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.2rem;">${escapeHtml(data.rightTitle)}</div>
            <p style="font-size: 0.74rem; color: var(--text-secondary);">${escapeHtml(data.rightDesc)}</p>
          </div>
        </div>
      `;
    };

    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const key = btn.getAttribute('data-topic');
        renderCard(key);
      });
    });

    renderCard('rank_vs_denserank');
  }

  initSandboxPlayground() {
    const sandboxTabs = document.querySelectorAll('.sandbox-tab');
    const sqlDisplay = document.getElementById('sandboxSqlCode');
    const tableContainer = document.getElementById('sandboxTableContainer');
    const vizHeader = document.getElementById('slide9VizHeader');

    const sandboxScenarios = {
      'scenario1': {
        title: 'JOIN',
        sql: `SELECT e.emp_name, d.dept_name, e.salary, e.job_title\nFROM employees e\nJOIN departments d ON e.department_id = d.department_id\nORDER BY e.salary DESC\nLIMIT 4;`,
        headers: ['emp_name', 'dept_name', 'salary'],
        rows: [
          ['Sophia Patel', 'Executive', '$148,000'],
          ['Marcus Thorne', 'Engineering', '$135,000'],
          ['Elena Rostova', 'Engineering', '$128,000']
        ]
      },
      'scenario2': {
        title: 'AGGREGATION',
        sql: `SELECT p.category, COUNT(oi.item_id) as total_sold, SUM(oi.quantity * oi.item_price) as gross_revenue\nFROM products p\nJOIN order_items oi ON p.product_id = oi.product_id\nGROUP BY p.category\nORDER BY gross_revenue DESC;`,
        headers: ['category', 'total_sold', 'gross_revenue'],
        rows: [
          ['Enterprise Cloud', '1,420', '$482,000'],
          ['Data Warehousing', '980', '$324,500']
        ]
      },
      'scenario3': {
        title: 'COHORT',
        sql: `SELECT c.region, c.segment, COUNT(o.order_id) as total_orders, AVG(o.total_amount) as avg_order_val\nFROM customers c\nLEFT JOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.region, c.segment\nORDER BY total_orders DESC;`,
        headers: ['region', 'segment', 'total_orders'],
        rows: [
          ['North America', 'Enterprise', '3,410'],
          ['EMEA', 'Enterprise', '2,180']
        ]
      }
    };

    sandboxTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        sandboxTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const key = tab.getAttribute('data-scenario');
        this.slide9ActiveScenario = key;
        const data = sandboxScenarios[key];
        if (!data) return;

        if (sqlDisplay) sqlDisplay.textContent = data.sql;
        if (vizHeader) vizHeader.textContent = `ABSTRACT ARTIFACT: AST PARSE TREE (${data.title})`;

        if (tableContainer) {
          let tableHtml = `<table class="data-table"><thead><tr>`;
          data.headers.forEach(h => { tableHtml += `<th>${escapeHtml(h)}</th>`; });
          tableHtml += `</tr></thead><tbody>`;
          data.rows.forEach(r => {
            tableHtml += `<tr>`;
            r.forEach(c => { tableHtml += `<td>${escapeHtml(c)}</td>`; });
            tableHtml += `</tr>`;
          });
          tableHtml += `</tbody></table>`;
          tableContainer.innerHTML = tableHtml;
        }
      });
    });
  }

  initTcoCalculator() {
    const slider = document.getElementById('calcVolumeSlider');
    const volumeDisplay = document.getElementById('calcVolumeDisplay');
    const cloudCostDisplay = document.getElementById('calcCloudCost');
    const tinyCostDisplay = document.getElementById('calcTinyCost');
    const savingsDisplay = document.getElementById('calcAnnualSavings');

    if (!slider) return;

    const calculate = () => {
      const queriesPerMonth = parseInt(slider.value, 10);
      const millions = (queriesPerMonth / 1000000).toFixed(1);
      if (volumeDisplay) volumeDisplay.textContent = `${millions}M Queries / month`;

      const cloudMonthly = queriesPerMonth * 0.008;
      const annualCloud = cloudMonthly * 12;

      if (cloudCostDisplay) cloudCostDisplay.textContent = `$${Math.round(cloudMonthly).toLocaleString()} / mo`;
      if (tinyCostDisplay) tinyCostDisplay.textContent = `$X / mo (Constant)`;
      if (savingsDisplay) savingsDisplay.textContent = `$${Math.round(annualCloud).toLocaleString()} - 12X / Year`;
    };

    slider.addEventListener('input', calculate);
    calculate();
  }

  // ============================================================
  // GENAI IDEAS WORKSPACE CONTROLLER (1-to-2 Slide Mini Pitch)
  // ============================================================

  getGenAiIdeas() {
    return window.GENAI_IDEAS_REGISTRY || [];
  }

  initGenAiWorkspace() {
    const openBtn = document.getElementById('openGenAiIdeaBtn');
    const closeBtn = document.getElementById('closeGenAiModalBtn');
    const prevIdeaBtn = document.getElementById('genAiPrevIdeaBtn');
    const nextIdeaBtn = document.getElementById('genAiNextIdeaBtn');
    const prevSlideBtn = document.getElementById('genAiPrevSlideBtn');
    const nextSlideBtn = document.getElementById('genAiNextSlideBtn');
    const tabsContainer = document.getElementById('genAiIdeaTabs');
    const pillsContainer = document.getElementById('genAiSlidePills');

    openBtn?.addEventListener('click', () => this.openGenAiModal());
    closeBtn?.addEventListener('click', () => this.closeGenAiModal());
    prevIdeaBtn?.addEventListener('click', () => this.prevGenAiIdea());
    nextIdeaBtn?.addEventListener('click', () => this.nextGenAiIdea());
    prevSlideBtn?.addEventListener('click', () => this.prevGenAiSlide());
    nextSlideBtn?.addEventListener('click', () => this.nextGenAiSlide());

    tabsContainer?.addEventListener('click', (e) => {
      const tab = e.target.closest('.genai-tab');
      if (!tab) return;
      const idx = parseInt(tab.getAttribute('data-idea-idx'), 10);
      if (!isNaN(idx)) this.selectGenAiIdea(idx);
    });

    pillsContainer?.addEventListener('click', (e) => {
      const pill = e.target.closest('.genai-pill');
      if (!pill) return;
      const sIdx = parseInt(pill.getAttribute('data-slide-idx'), 10);
      if (!isNaN(sIdx)) this.setGenAiSlide(sIdx);
    });
  }

  selectGenAiIdea(idx) {
    const ideas = this.getGenAiIdeas();
    if (!ideas.length) return;
    this.currentGenAiIdeaIdx = Math.max(0, Math.min(idx, ideas.length - 1));
    this.currentGenAiSlideIdx = 0;
    this.renderGenAiTabs();
    this.renderGenAiCurrentIdea();
  }

  setGenAiSlide(slideIdx) {
    const ideas = this.getGenAiIdeas();
    const idea = ideas[this.currentGenAiIdeaIdx];
    if (!idea) return;
    const totalSlides = idea.slides?.length || 1;
    this.currentGenAiSlideIdx = Math.max(0, Math.min(slideIdx, totalSlides - 1));
    this.renderGenAiCurrentIdea();
  }

  nextGenAiSlide() {
    const ideas = this.getGenAiIdeas();
    const idea = ideas[this.currentGenAiIdeaIdx];
    if (!idea) return;
    const totalSlides = idea.slides?.length || 1;
    if (this.currentGenAiSlideIdx < totalSlides - 1) {
      this.setGenAiSlide(this.currentGenAiSlideIdx + 1);
    } else {
      this.nextGenAiIdea();
    }
  }

  prevGenAiSlide() {
    if (this.currentGenAiSlideIdx > 0) {
      this.setGenAiSlide(this.currentGenAiSlideIdx - 1);
    } else {
      this.prevGenAiIdea();
    }
  }

  nextGenAiIdea() {
    const ideas = this.getGenAiIdeas();
    if (!ideas.length) return;
    this.selectGenAiIdea((this.currentGenAiIdeaIdx + 1) % ideas.length);
  }

  prevGenAiIdea() {
    const ideas = this.getGenAiIdeas();
    if (!ideas.length) return;
    this.selectGenAiIdea((this.currentGenAiIdeaIdx - 1 + ideas.length) % ideas.length);
  }

  renderGenAiTabs() {
    const container = document.getElementById('genAiIdeaTabs');
    if (!container) return;
    const ideas = this.getGenAiIdeas();
    if (!ideas.length) {
      container.innerHTML = '<span style="font-size: 0.72rem; color: var(--text-tertiary);">No registered ideas found</span>';
      return;
    }

    container.innerHTML = ideas.map((idea, idx) => {
      const shortTag = idea.tag.split('//')[0].trim();
      const isActive = idx === this.currentGenAiIdeaIdx;
      const color = idea.themeColor || '#007BFF';
      const activeStyle = `background: ${color}; border-color: ${color}; color: ${color === '#FFD300' ? '#111418' : '#ffffff'}; font-weight: 700; box-shadow: 0 2px 4px rgba(0,0,0,0.08);`;
      const inactiveStyle = `border-left: 3px solid ${color};`;
      return `<button class="genai-tab ${isActive ? 'active' : ''}" data-idea-idx="${idx}" style="${isActive ? activeStyle : inactiveStyle}" type="button">${escapeHtml(shortTag)}: ${escapeHtml(idea.title)}</button>`;
    }).join('');
  }

  renderGenAiCurrentIdea() {
    const ideas = this.getGenAiIdeas();
    const viewport = document.getElementById('genAiSlideViewport');
    const tagEl = document.getElementById('genAiIdeaTag');
    const headingEl = document.getElementById('genAiIdeaHeading');
    const ideaCounterEl = document.getElementById('genAiIdeaCounter');
    const slideCounterEl = document.getElementById('genAiSlideCounter');
    const pillsContainer = document.getElementById('genAiSlidePills');

    if (!ideas.length) {
      if (viewport) {
        viewport.innerHTML = `
          <div class="genai-slide-card" style="align-items: center; justify-content: center; text-align: center; padding: 3rem;">
            <h3 class="card-title" style="font-size: 1.1rem; margin-bottom: 0.5rem;">Ideas Registry Empty</h3>
            <p class="card-desc">Add ideas into <code>Productpitch/Ideas/ideas_registry.js</code> to generate interactive slide decks.</p>
          </div>
        `;
      }
      return;
    }

    const idea = ideas[this.currentGenAiIdeaIdx];
    const themeColor = idea.themeColor || '#007BFF';
    const themeLight = idea.themeLight || 'rgba(0, 123, 255, 0.12)';
    const slides = idea.slides || [];
    const totalSlides = Math.max(1, slides.length);
    const activeSlideIdx = Math.min(this.currentGenAiSlideIdx, totalSlides - 1);
    const slide = slides[activeSlideIdx] || {};

    if (tagEl) {
      tagEl.textContent = idea.tag || `IDEA ${this.currentGenAiIdeaIdx + 1}`;
      tagEl.style.color = themeColor;
    }
    if (headingEl) headingEl.textContent = idea.title || 'Untitled GenAI Concept';
    if (ideaCounterEl) ideaCounterEl.textContent = `Idea ${this.currentGenAiIdeaIdx + 1} of ${ideas.length}`;
    if (slideCounterEl) slideCounterEl.textContent = `Slide ${activeSlideIdx + 1} of ${totalSlides}`;

    const badge = document.querySelector('.genai-badge');
    if (badge) {
      badge.style.borderColor = themeColor;
      badge.style.color = themeColor === '#FFD300' ? '#92400e' : themeColor;
      badge.style.background = themeLight;
    }

    // Render Mini Slide Pills with theme color
    if (pillsContainer) {
      if (totalSlides > 1) {
        pillsContainer.innerHTML = slides.map((s, sIdx) => {
          const isActive = sIdx === activeSlideIdx;
          const label = sIdx === 0 ? 'Slide 1: Concept & Impact' : 'Slide 2: Architecture Blueprint';
          const activePillStyle = `background: ${themeLight}; border: 1px solid ${themeColor}; color: #111418; font-weight: 700;`;
          return `<button class="genai-pill ${isActive ? 'active' : ''}" data-slide-idx="${sIdx}" style="${isActive ? activePillStyle : ''}" type="button">${label}</button>`;
        }).join('');
      } else {
        pillsContainer.innerHTML = `<button class="genai-pill active" data-slide-idx="0" style="background: ${themeLight}; border: 1px solid ${themeColor}; color: #111418; font-weight: 700;" type="button">Slide 1: Proposition Overview</button>`;
      }
    }

    // Render Viewport HTML based on Slide 1 vs Slide 2
    if (!viewport) return;

    if (activeSlideIdx === 1 || slide.slideType === 'architecture') {
      // Slide 2: Technical Architecture & Pipeline
      viewport.innerHTML = `
        <div class="genai-slide-card">
          <div class="slide-header" style="margin-bottom: 0.85rem;">
            <div class="slide-tag" style="color: ${themeColor}; font-weight: 700;">${escapeHtml(slide.slideTag || 'Technical Architecture & Pipeline')}</div>
            <h2 class="slide-title" style="font-size: 1.25rem; margin-bottom: 0.2rem;">${escapeHtml(slide.slideTitle || idea.title)}</h2>
            <p class="slide-subtitle">${escapeHtml(slide.slideSubtitle || slide.architecture || '')}</p>
          </div>

          <div class="grid-2col" style="flex: 1; align-items: stretch; gap: 1rem;">
            <div style="display: flex; flex-direction: column; gap: 0.55rem;">
              <div class="card" style="padding: 0.85rem; border-top: 3px solid ${themeColor};">
                <div class="card-num" style="color: ${themeColor === '#FFD300' ? '#92400e' : themeColor};">ARCHITECTURE BLUEPRINT</div>
                <p class="card-desc" style="font-size: 0.82rem; font-weight: 500; color: var(--text-primary); margin-top: 0.2rem;">
                  ${escapeHtml(slide.architecture || 'Specialized Micro-Model Pipeline with Deterministic Validation')}
                </p>

                <div class="genai-flow-list">
                  ${(slide.flowSteps || []).map(f => `
                    <div class="genai-flow-item">
                      <span class="genai-flow-step" style="background: ${themeLight}; color: ${themeColor === '#FFD300' ? '#92400e' : themeColor}; border-color: ${themeColor};">${escapeHtml(f.step || 'STEP')}</span>
                      <div class="genai-flow-content">
                        <span class="genai-flow-title">${escapeHtml(f.title || '')}</span>
                        <span class="genai-flow-desc">${escapeHtml(f.desc || '')}</span>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>

              ${slide.codeSnippet ? `
                <div class="card" style="padding: 0.65rem;">
                  <div class="card-num" style="margin-bottom: 0.25rem;">PREVIEW &amp; ARTIFACT TRACE</div>
                  <pre class="code-container" style="font-size: 0.72rem; padding: 0.5rem; margin: 0; max-height: 85px; overflow-y: auto;"><code>${escapeHtml(slide.codeSnippet)}</code></pre>
                </div>
              ` : ''}
            </div>

            <!-- Dynamic Architecture Abstract Canvas -->
            <div class="abstract-viz-panel" style="display: flex; flex-direction: column;">
              <div class="abstract-viz-header">
                <span>ABSTRACT ARTIFACT: PIPELINE EXECUTION</span>
                <span style="color: ${themeColor}; font-weight: 700;">${escapeHtml(idea.canvasType ? idea.canvasType.toUpperCase() : 'NEURAL FLOW')}</span>
              </div>
              <div class="abstract-canvas-wrap tall" style="flex: 1; min-height: 280px;">
                <canvas id="genaiCanvas" class="abstract-canvas"></canvas>
              </div>
              ${slide.stack ? `
                <div style="padding: 0.45rem 0.65rem; background: var(--bg-surface); border-top: 1px solid var(--border-light); font-size: 0.72rem; color: var(--text-secondary);">
                  <b>Engineering Stack:</b> ${escapeHtml(slide.stack)}
                </div>
              ` : ''}
            </div>
          </div>
        </div>
      `;
    } else {
      // Slide 1: Concept, Problem Statement & Metrics
      viewport.innerHTML = `
        <div class="genai-slide-card">
          <div class="slide-header" style="margin-bottom: 0.85rem;">
            <div class="slide-tag" style="color: ${themeColor}; font-weight: 700;">${escapeHtml(slide.slideTag || 'Concept & Problem Statement')}</div>
            <h2 class="slide-title" style="font-size: 1.25rem; margin-bottom: 0.2rem;">${escapeHtml(slide.slideTitle || idea.title)}</h2>
            <p class="slide-subtitle">${escapeHtml(slide.slideSubtitle || idea.subtitle || '')}</p>
          </div>

          <div class="grid-2col" style="flex: 1; align-items: stretch; gap: 1rem;">
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
              <div class="card" style="padding: 0.85rem; border-top: 3px solid ${themeColor};">
                <div class="card-num" style="color: ${themeColor === '#FFD300' ? '#92400e' : themeColor};">EXECUTIVE SUMMARY</div>
                <p class="card-desc" style="margin-top: 0.25rem; font-size: 0.84rem; line-height: 1.45;">
                  ${escapeHtml(slide.overview || idea.subtitle || '')}
                </p>
              </div>

              <!-- 4 Metrics Grid with theme accents -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                ${(idea.metrics || []).map(m => `
                  <div class="metric-box" style="padding: 0.65rem; border-left: 3px solid ${themeColor};">
                    <div class="metric-val" style="font-size: 1.15rem; color: ${themeColor === '#FFD300' ? '#92400e' : themeColor};">${escapeHtml(m.val)}</div>
                    <div class="metric-label" style="font-size: 0.66rem;">${escapeHtml(m.label)}</div>
                  </div>
                `).join('')}
              </div>

              <div class="card" style="padding: 0.85rem;">
                <div class="card-num">CORE INNOVATION HIGHLIGHTS</div>
                <ul style="list-style: none; margin-top: 0.45rem; display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.78rem; color: var(--text-secondary);">
                  ${(slide.highlights || slide.keyPoints || []).map(h => `
                    <li style="display: flex; gap: 0.45rem; align-items: flex-start;">
                      <span style="color: ${themeColor}; font-weight: 700; font-family: var(--font-mono);">&bull;</span>
                      <span>${escapeHtml(h)}</span>
                    </li>
                  `).join('')}
                </ul>
              </div>
            </div>

            <!-- Dynamic Concept Abstract Canvas -->
            <div class="abstract-viz-panel" style="display: flex; flex-direction: column;">
              <div class="abstract-viz-header">
                <span>ABSTRACT ARTIFACT: CONCEPT VISUALIZER</span>
                <span style="color: ${themeColor}; font-weight: 700;">${escapeHtml(idea.canvasType ? idea.canvasType.toUpperCase() : 'DOMAIN NEURAL')}</span>
              </div>
              <div class="abstract-canvas-wrap tall" style="flex: 1; min-height: 280px;">
                <canvas id="genaiCanvas" class="abstract-canvas"></canvas>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Launch dedicated canvas animation
    this.initGenAiCanvas(idea, activeSlideIdx + 1);
  }

  initGenAiCanvas(idea, slideNum) {
    if (this.genAiCanvasAnimId) {
      cancelAnimationFrame(this.genAiCanvasAnimId);
      this.genAiCanvasAnimId = null;
    }

    const canvas = document.getElementById('genaiCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.resetTransform?.();
      ctx.scale(dpr, dpr);
    };
    resize();

    const canvasType = idea.canvasType || 'generic';
    let tick = 0;

    const animate = () => {
      if (!this.genAiModal?.classList.contains('open')) return;
      const rect = canvas.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height;
      if (width === 0 || height === 0) return;

      ctx.clearRect(0, 0, width, height);

      // Background subtle grid
      ctx.strokeStyle = '#e6e9f0';
      ctx.lineWidth = 1;
      const gridSize = 24;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      if (canvasType === 'data_studio') {
        // Universal Data & BI Intelligence Studio: 4-Pillar Cross-Engine Visualizer
        const cx = width / 2;
        const cy = height / 2;

        const hubRadius = 38;
        const orbitX = Math.min(width * 0.36, 140);
        const orbitY = Math.min(height * 0.34, 90);

        const pillars = [
          { name: "1. SCHEMA GRAPH", sub: "Metadata / PII", x: cx, y: cy - orbitY, color: "#3b82f6" },
          { name: "2. LAKEHOUSE", sub: "Snowflake / Delta", x: cx - orbitX, y: cy, color: "#10b981" },
          { name: "3. AST SQL ENGINE", sub: "Self-Healing", x: cx + orbitX, y: cy, color: "#f59e0b" },
          { name: "4. BI DASHBOARDS", sub: "Vega / DAX", x: cx, y: cy + orbitY, color: "#8b5cf6" },
        ];

        // Draw connecting rays and flowing data packets
        pillars.forEach((p, idx) => {
          ctx.strokeStyle = '#cbd5e1';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(p.x, p.y);
          ctx.stroke();

          // Flowing packet along ray
          const progress = ((tick * 0.02 + idx * 0.25) % 1);
          const px = cx + (p.x - cx) * progress;
          const py = cy + (p.y - cy) * progress;

          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(px, py, 4, 0, Math.PI * 2);
          ctx.fill();
        });

        // Draw Central Neural Hub
        const pulse = 1 + 0.05 * Math.sin(tick * 0.08);
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(cx, cy, hubRadius * pulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '700 9.5px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('5.4M CORE', cx, cy - 6);
        ctx.fillStyle = '#94a3b8';
        ctx.font = '500 8px sans-serif';
        ctx.fillText('NEURAL ENGINE', cx, cy + 7);

        // Draw 4 Pillar Cards
        pillars.forEach((p) => {
          const pw = 110;
          const ph = 32;

          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(p.x - pw / 2, p.y - ph / 2, pw, ph, 4);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#111418';
          ctx.font = '700 8.5px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(p.name, p.x, p.y - 5);

          ctx.fillStyle = '#64748b';
          ctx.font = '500 7.5px sans-serif';
          ctx.fillText(p.sub, p.x, p.y + 6);
        });

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 10.5px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`UNIVERSAL DATA OS // 4 PILLARS ACTIVE [SUB-12MS INFERENCE]`, 16, height - 16);

      } else if (canvasType === 'poc_to_product') {
        // ShipDeck AI: Codebase-to-5-Deliverables Commercialization Funnel (Bright Orange Theme)
        const cx = width / 2;
        const cy = height / 2;

        const leftX = width * 0.22;
        const midX = width * 0.48;
        const rightX = width * 0.82;

        // 1. Source Repo Box
        const srcW = 100;
        const srcH = 34;
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#FF6F00';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.roundRect(leftX - srcW / 2, cy - srcH / 2, srcW, srcH, 4);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#1e293b';
        ctx.font = '700 8.5px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('GITHUB / ZIP', leftX, cy - 5);
        ctx.fillStyle = '#64748b';
        ctx.font = '500 7.5px sans-serif';
        ctx.fillText('RAW CODEBASE', leftX, cy + 6);

        // 2. Central Analyzer Node
        const coreR = 30;
        const corePulse = 1 + 0.06 * Math.sin(tick * 0.08);
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#FF6F00';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(midX, cy, coreR * corePulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8px monospace';
        ctx.fillText('AST PARSER', midX, cy - 5);
        ctx.fillStyle = '#fed7aa';
        ctx.font = '500 7px sans-serif';
        ctx.fillText('& SYNTHESIZER', midX, cy + 6);

        // Connection from Source to Central Analyzer
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(leftX + srcW / 2, cy);
        ctx.lineTo(midX - coreR, cy);
        ctx.stroke();

        // Inbound particle
        const inProg = (tick * 0.03) % 1;
        const ipx = (leftX + srcW / 2) + ((midX - coreR) - (leftX + srcW / 2)) * inProg;
        ctx.fillStyle = '#FF6F00';
        ctx.beginPath();
        ctx.arc(ipx, cy, 3.5, 0, Math.PI * 2);
        ctx.fill();

        // 3. 5 Output Deliverable Cards
        const deliverables = [
          { name: "1. PITCH DECK", sub: "Sales PPT", yOffset: -85, color: "#FF6F00" },
          { name: "2. 1-PAGE FLYER", sub: "Marketing PDF", yOffset: -42, color: "#FF6F00" },
          { name: "3. SOLUTION SPEC", sub: "Technical Doc", yOffset: 0, color: "#ea580c" },
          { name: "4. GTM STRATEGY", sub: "Pricing / SLA", yOffset: 42, color: "#FF6F00" },
          { name: "5. ROI PROOF PACK", sub: "Before vs After", yOffset: 85, color: "#c2410c" }
        ];

        deliverables.forEach((d, idx) => {
          const dy = cy + d.yOffset;

          // Branch lines from Analyzer to Deliverable
          ctx.strokeStyle = '#cbd5e1';
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.moveTo(midX + coreR, cy);
          ctx.lineTo(rightX - 58, dy);
          ctx.stroke();

          // Outbound flowing particle
          const outProg = ((tick * 0.025 + idx * 0.2) % 1);
          const opx = (midX + coreR) + ((rightX - 58) - (midX + coreR)) * outProg;
          const opy = cy + (dy - cy) * outProg;

          ctx.fillStyle = d.color;
          ctx.beginPath();
          ctx.arc(opx, opy, 3.5, 0, Math.PI * 2);
          ctx.fill();

          // Deliverable Box
          const dw = 114;
          const dh = 28;
          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = d.color;
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(rightX - dw / 2, dy - dh / 2, dw, dh, 4);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#111418';
          ctx.font = '700 8px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(d.name, rightX, dy - 4);

          ctx.fillStyle = '#64748b';
          ctx.font = '500 7px sans-serif';
          ctx.fillText(d.sub, rightX, dy + 5);
        });

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 10.5px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`SHIPDECK AI // 5 COMMERCIAL DELIVERABLES SYNTHESIZED (< 30S)`, 16, height - 16);

      } else if (canvasType === 'rto_junction') {
        // TrafficSentry AI: Smart Junction, 2-Stage Voice Warnings & Ambulance Corridor (Lemon Yellow Theme)
        const cx = width / 2;
        const cy = height / 2;

        // Road Surface
        const roadW = width - 40;
        const roadH = 140;
        const roadX = 20;
        const roadY = cy - 60;

        ctx.fillStyle = '#1e293b';
        ctx.beginPath();
        ctx.roundRect(roadX, roadY, roadW, roadH, 6);
        ctx.fill();

        // Lane divider dashed line
        ctx.strokeStyle = '#f8fafc';
        ctx.lineWidth = 2;
        ctx.setLineDash([12, 8]);
        ctx.beginPath();
        ctx.moveTo(roadX, roadY + roadH / 2);
        ctx.lineTo(roadX + roadW, roadY + roadH / 2);
        ctx.stroke();
        ctx.setLineDash([]);

        // Zebra Crossing & Stop Line
        const stopLineX = roadX + roadW * 0.45;

        // White Solid Stop Line
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(stopLineX, roadY);
        ctx.lineTo(stopLineX, roadY + roadH);
        ctx.stroke();

        // Zebra stripes
        ctx.fillStyle = '#ffffff';
        for (let i = 0; i < 5; i++) {
          ctx.fillRect(stopLineX + 8 + i * 14, roadY + 8, 8, roadH - 16);
        }

        // 1. Traffic Signal Pole with Directional Voice Horn & Sound Waves
        const poleX = stopLineX - 45;
        const poleY = roadY - 40;

        // Signal Housing
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(poleX - 8, poleY, 16, 32);
        // Red Light active
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(poleX, poleY + 8, 5, 0, Math.PI * 2);
        ctx.fill();

        // Directional Speaker Horn (Lemon Yellow)
        ctx.fillStyle = '#FFD300';
        ctx.beginPath();
        ctx.moveTo(poleX + 8, poleY + 16);
        ctx.lineTo(poleX + 22, poleY + 8);
        ctx.lineTo(poleX + 22, poleY + 24);
        ctx.closePath();
        ctx.fill();

        // Sound Waves radiating from speaker (Lemon Yellow)
        const waveTick = (tick * 0.08) % 3;
        ctx.strokeStyle = 'rgba(255, 211, 0, 0.9)';
        ctx.lineWidth = 2;
        for (let w = 1; w <= 3; w++) {
          const r = 10 + w * 12 + waveTick * 4;
          ctx.beginPath();
          ctx.arc(poleX + 22, poleY + 16, r, -Math.PI / 4, Math.PI / 4);
          ctx.stroke();
        }

        // Voice Alert Bubble over Signal
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#FFD300';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(poleX + 40, poleY - 8, 145, 26, 4);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#854d0e';
        ctx.font = '700 7.5px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('STAGE 1: 3s VOICE WARNING', poleX + 46, poleY + 3);
        ctx.fillStyle = '#1e293b';
        ctx.font = '500 7px sans-serif';
        ctx.fillText('MH 12 AB 1234: Please Reverse', poleX + 46, poleY + 13);

        // 2. Car 1 (Violating Stop Line in Upper Lane)
        const car1X = stopLineX - 15;
        const car1Y = roadY + 12;
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(car1X - 35, car1Y, 50, 24, 3);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#991b1b';
        ctx.font = '700 7.5px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('MH 12 AB 1234', car1X - 10, car1Y + 14);

        // 3. Ambulance (Approaching in Lower Lane - Emergency Corridor)
        const ambX = roadX + ((tick * 1.5) % (roadW * 0.38));
        const ambY = roadY + roadH / 2 + 16;
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(ambX, ambY, 56, 28, 4);
        ctx.fill();
        ctx.stroke();

        // Red cross
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(ambX + 24, ambY + 6, 8, 16);
        ctx.fillRect(ambX + 20, ambY + 10, 16, 8);

        // Flashing Emergency Beacon
        const beaconColor = Math.sin(tick * 0.2) > 0 ? '#3b82f6' : '#ef4444';
        ctx.fillStyle = beaconColor;
        ctx.beginPath();
        ctx.arc(ambX + 28, ambY - 3, 4, 0, Math.PI * 2);
        ctx.fill();

        // Ambulance Green Corridor Label
        ctx.fillStyle = '#10b981';
        ctx.font = '700 8px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('EMERGENCY CORRIDOR: LANE 2 CLEARING', roadX + 10, roadY + roadH + 18);

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 10.5px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`TRAFFICSENTRY AI // 2-STAGE VOICE INTERVENTION & AMBULANCE CORRIDOR`, 16, height - 16);

      } else if (canvasType === 'team_orchestration') {
        // TeamForge AI: Autonomous Bandwidth-Aware Task Allocation & Zero-Timesheet Telemetry (Sage Green Theme)
        const cx = width / 2;
        const cy = height / 2;

        const leftX = width * 0.20;
        const midX = width * 0.50;
        const rightX = width * 0.80;

        // 1. Inbound Backlog Tasks on Left
        const taskCards = [
          { code: "TF-4192", name: "Stripe Webhooks", domain: "Fintech LoRA", yOffset: -50 },
          { code: "TF-4193", name: "FHIR Patient Sync", domain: "MedTech LoRA", yOffset: 0 },
          { code: "TF-4194", name: "Delta Lake dbt", domain: "Data Lake LoRA", yOffset: 50 }
        ];

        taskCards.forEach((t) => {
          const ty = cy + t.yOffset;
          const tw = 105;
          const th = 32;

          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = '#cbd5e1';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(leftX - tw / 2, ty - th / 2, tw, th, 4);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#8f8863';
          ctx.font = '700 8px monospace';
          ctx.textAlign = 'left';
          ctx.fillText(t.code, leftX - tw / 2 + 6, ty - 4);

          ctx.fillStyle = '#1e293b';
          ctx.font = '600 7.5px sans-serif';
          ctx.fillText(t.name, leftX - tw / 2 + 6, ty + 6);
        });

        // 2. Central Neural Matcher Node (Sage Green)
        const matchR = 32;
        const matchPulse = 1 + 0.05 * Math.sin(tick * 0.08);
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#BCB88A';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(midX, cy, matchR * matchPulse, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '700 8px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('NEURAL', midX, cy - 5);
        ctx.fillStyle = '#e2dfc8';
        ctx.font = '500 7px sans-serif';
        ctx.fillText('MATCHER', midX, cy + 6);

        // Connections from Tasks to Neural Matcher
        taskCards.forEach((t, idx) => {
          const ty = cy + t.yOffset;
          ctx.strokeStyle = '#cbd5e1';
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.moveTo(leftX + 52, ty);
          ctx.lineTo(midX - matchR, cy);
          ctx.stroke();

          // Flowing task packet into matcher
          const inProg = ((tick * 0.025 + idx * 0.33) % 1);
          const ipx = (leftX + 52) + ((midX - matchR) - (leftX + 52)) * inProg;
          const ipy = ty + (cy - ty) * inProg;
          ctx.fillStyle = '#BCB88A';
          ctx.beginPath();
          ctx.arc(ipx, ipy, 3, 0, Math.PI * 2);
          ctx.fill();
        });

        // 3. Team Member Capacity Cards on Right
        const teamMembers = [
          { name: "Alex K.", role: "Senior Backend", cap: "65% Free", barColor: "#8f8863", yOffset: -50, match: true },
          { name: "Marcus T.", role: "Frontend Lead", cap: "90% Busy", barColor: "#ef4444", yOffset: 0, match: false },
          { name: "Sophia P.", role: "Data Architect", cap: "45% Free", barColor: "#8f8863", yOffset: 50, match: true }
        ];

        teamMembers.forEach((m, idx) => {
          const my = cy + m.yOffset;
          const mw = 120;
          const mh = 36;

          // Connecting line from Matcher to Team Member
          ctx.strokeStyle = m.match ? '#BCB88A' : '#cbd5e1';
          ctx.lineWidth = m.match ? 1.8 : 0.8;
          ctx.beginPath();
          ctx.moveTo(midX + matchR, cy);
          ctx.lineTo(rightX - mw / 2, my);
          ctx.stroke();

          if (m.match) {
            // Flowing assigned task packet to engineer
            const outProg = ((tick * 0.03 + idx * 0.4) % 1);
            const opx = (midX + matchR) + ((rightX - mw / 2) - (midX + matchR)) * outProg;
            const opy = cy + (my - cy) * outProg;
            ctx.fillStyle = '#BCB88A';
            ctx.beginPath();
            ctx.arc(opx, opy, 3.5, 0, Math.PI * 2);
            ctx.fill();
          }

          // Member Box
          ctx.fillStyle = '#ffffff';
          ctx.strokeStyle = m.match ? '#BCB88A' : '#cbd5e1';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(rightX - mw / 2, my - mh / 2, mw, mh, 4);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#111418';
          ctx.font = '700 8px monospace';
          ctx.textAlign = 'left';
          ctx.fillText(m.name, rightX - mw / 2 + 6, my - 6);

          ctx.fillStyle = '#64748b';
          ctx.font = '500 7px sans-serif';
          ctx.fillText(m.role, rightX - mw / 2 + 6, my + 4);

          // Capacity Badge
          ctx.fillStyle = m.barColor;
          ctx.font = '700 7px monospace';
          ctx.textAlign = 'right';
          ctx.fillText(m.cap, rightX + mw / 2 - 6, my - 6);
        });

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 10.5px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`TEAMFORGE AI // AUTONOMOUS TASK ALLOCATION & ZERO-TIMESHEET TELEMETRY`, 16, height - 16);

      } else if (canvasType === 'linter') {
        // SQL Performance & Anti-Pattern Linter Tree Visualizer
        const cx = width / 2;
        const cy = height / 2;

        const nodes = [
          { x: cx, y: cy - 70, label: "SELECT (ROOT)", alert: false },
          { x: cx - 110, y: cy, label: "JOIN (orders)", alert: false },
          { x: cx + 110, y: cy, label: "WHERE (filter)", alert: true },
          { x: cx - 140, y: cy + 70, label: "SCAN [index]", alert: false },
          { x: cx - 80, y: cy + 70, label: "ON [c_id = o_id]", alert: false },
          { x: cx + 60, y: cy + 70, label: "YEAR(date) [Non-SARGable]", alert: true },
          { x: cx + 140, y: cy + 70, label: "status = 1", alert: false },
        ];

        // Draw connections
        ctx.lineWidth = 1.5;
        const edges = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]];
        edges.forEach(([p, c]) => {
          const n1 = nodes[p];
          const n2 = nodes[c];
          ctx.strokeStyle = n2.alert ? '#fca5a5' : '#cbd5e1';
          ctx.beginPath();
          ctx.moveTo(n1.x, n1.y);
          ctx.lineTo(n2.x, n2.y);
          ctx.stroke();
        });

        // Laser scan wave
        const scanY = (cy - 90) + ((tick * 1.8) % (height * 0.7));
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)';
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(cx - 160, scanY);
        ctx.lineTo(cx + 160, scanY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Render nodes
        nodes.forEach((n, i) => {
          const isScanning = Math.abs(n.y - scanY) < 18;
          ctx.fillStyle = n.alert ? '#fef2f2' : (isScanning ? '#eff6ff' : '#ffffff');
          ctx.strokeStyle = n.alert ? '#ef4444' : (isScanning ? '#3b82f6' : '#94a3b8');
          ctx.lineWidth = n.alert ? 2 : 1.5;

          const nw = n.label.length * 6.5 + 16;
          const nh = 24;
          ctx.beginPath();
          ctx.roundRect(n.x - nw / 2, n.y - nh / 2, nw, nh, 4);
          ctx.fill();
          ctx.stroke();

          // Text
          ctx.fillStyle = n.alert ? '#b91c1c' : (isScanning ? '#1d4ed8' : '#1e293b');
          ctx.font = '600 10px monospace';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(n.label, n.x, n.y);
        });

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`AST SCANNER // RECALL: 99.4% [NON-SARGABLE DETECTED]`, 16, height - 16);

      } else if (canvasType === 'bi_chart') {
        // Conversational BI Vega-Lite Visual Grammar Visualizer
        const chartLeft = 50;
        const chartRight = width - 40;
        const chartTop = 40;
        const chartBottom = height - 50;

        // Axes
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(chartLeft, chartTop);
        ctx.lineTo(chartLeft, chartBottom);
        ctx.lineTo(chartRight, chartBottom);
        ctx.stroke();

        // Dynamic multi-series bars & area line
        const barCount = 7;
        const barWidth = (chartRight - chartLeft - 40) / barCount;
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];

        for (let i = 0; i < barCount; i++) {
          const bx = chartLeft + 20 + i * barWidth;
          const val = 0.4 + 0.35 * Math.sin(tick * 0.03 + i * 0.8);
          const barHeight = (chartBottom - chartTop - 30) * val;
          const by = chartBottom - barHeight;

          // Bar
          ctx.fillStyle = i % 2 === 0 ? 'rgba(59, 130, 246, 0.75)' : 'rgba(16, 185, 129, 0.75)';
          ctx.beginPath();
          ctx.roundRect(bx, by, barWidth * 0.65, barHeight, [3, 3, 0, 0]);
          ctx.fill();

          // Month label
          ctx.fillStyle = '#64748b';
          ctx.font = '500 10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(months[i], bx + (barWidth * 0.65) / 2, chartBottom + 16);
        }

        // Animated trend line over bars
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        for (let i = 0; i < barCount; i++) {
          const bx = chartLeft + 20 + i * barWidth + (barWidth * 0.65) / 2;
          const trendVal = 0.5 + 0.3 * Math.cos(tick * 0.03 + i * 0.6);
          const py = chartBottom - (chartBottom - chartTop - 30) * trendVal;
          if (i === 0) ctx.moveTo(bx, py);
          else ctx.lineTo(bx, py);
        }
        ctx.stroke();

        // Grammar badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`VEGA-LITE WASM COMPILER // LATENCY: 12ms`, 16, height - 16);

      } else if (canvasType === 'log_anomaly') {
        // Edge Log & Threat Anomaly Detector Pulse Visualizer
        const cy = height / 2;
        const totalPackets = 14;

        // Packet stream rail
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(30, cy);
        ctx.lineTo(width - 30, cy);
        ctx.stroke();

        // Gate barrier in middle
        const gateX = width / 2;
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(gateX, cy - 45);
        ctx.lineTo(gateX, cy + 45);
        ctx.stroke();

        ctx.fillStyle = '#991b1b';
        ctx.font = '700 9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('POLICY GATE', gateX, cy - 52);

        // Moving packets
        for (let i = 0; i < totalPackets; i++) {
          const px = ((tick * 1.5 + i * (width / totalPackets)) % (width - 60)) + 30;
          const isThreat = (i % 5 === 0);

          if (isThreat && px > gateX) {
            // Blocked packet
            ctx.fillStyle = '#ef4444';
            ctx.strokeStyle = '#b91c1c';
            ctx.beginPath();
            ctx.arc(gateX, cy, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
          } else {
            ctx.fillStyle = isThreat ? '#f87171' : '#34d399';
            ctx.strokeStyle = isThreat ? '#dc2626' : '#059669';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(px, cy, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
          }
        }

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`ENVOY PROXY SIDECAR // SUB-2MS THREAT INFERENCE`, 16, height - 16);

      } else {
        // Generic Neural Computational Graph
        const cx = width / 2;
        const cy = height / 2;
        const layerCounts = [3, 5, 5, 3];
        const layerX = [cx - 140, cx - 45, cx + 45, cx + 140];

        // Draw weights
        for (let l = 0; l < layerCounts.length - 1; l++) {
          const n1Count = layerCounts[l];
          const n2Count = layerCounts[l + 1];
          const x1 = layerX[l];
          const x2 = layerX[l + 1];

          for (let i = 0; i < n1Count; i++) {
            const y1 = cy - ((n1Count - 1) * 22) / 2 + i * 22;
            for (let j = 0; j < n2Count; j++) {
              const y2 = cy - ((n2Count - 1) * 22) / 2 + j * 22;
              const active = Math.sin(tick * 0.05 + l + i + j) > 0.4;
              ctx.strokeStyle = active ? 'rgba(59, 130, 246, 0.45)' : 'rgba(203, 213, 225, 0.3)';
              ctx.lineWidth = active ? 1.5 : 0.8;
              ctx.beginPath();
              ctx.moveTo(x1, y1);
              ctx.lineTo(x2, y2);
              ctx.stroke();
            }
          }
        }

        // Draw nodes
        layerCounts.forEach((count, l) => {
          const x = layerX[l];
          for (let i = 0; i < count; i++) {
            const y = cy - ((count - 1) * 22) / 2 + i * 22;
            const pulse = 0.5 + 0.5 * Math.sin(tick * 0.08 + l * 1.2 + i);
            ctx.fillStyle = pulse > 0.6 ? '#3b82f6' : '#ffffff';
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
          }
        });

        // Status badge
        ctx.fillStyle = '#111418';
        ctx.font = '600 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`NEURAL WEIGHT GRAPH // QUANTIZED INFERENCE`, 16, height - 16);
      }

      tick++;
      this.genAiCanvasAnimId = requestAnimationFrame(animate);
    };

    animate();
  }
}

function escapeHtml(string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
      '/': '&#x2F;',
      '`': '&#x60;',
      '=': '&#x3D;'
    }[s];
  });
}

document.addEventListener('DOMContentLoaded', () => {
  window.presentationApp = new PresentationApp();
});
