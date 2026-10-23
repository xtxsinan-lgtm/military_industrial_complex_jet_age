// ============================================================================
// MIC: Jet Age — Interactive Engineering Blueprint & Freehand Sculpting Canvases
// 1. Interactive Airfoil Cross-Section Sculptor & Chordwise Cp(x/c) Studio
// 2. Interactive Fuselage Lofting & Sears-Haack Area-Rule A(x) Sculpting Bench
// 3. Interactive 3-View Orthographic Blueprint (with draggable Wing & Fuselage handles)
// 4. Boyd Specific Excess Power Ps(M, h) Heatmap & Envelope
// 5. Transonic Drag Rise CD0(M) & Drag Polar Plot
// ============================================================================

(function () {
  "use strict";

  function setupBlueprintCanvas(canvas) {
    if (!canvas) return null;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(480, Math.round(rect.width || 680));
    const h = Math.max(300, Math.round(rect.height || 360));
    if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
      canvas.width = w * dpr;
      canvas.height = h * dpr;
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Prussian Blueprint Background + Grid
    ctx.fillStyle = "#081224";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(0, 240, 255, 0.07)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 24) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 24) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }
    return { ctx, w, h };
  }

  // Helper to draw a glowing interactive handle node
  function drawHandleNode(ctx, x, y, color, label, isHovered, radius) {
    const r = radius || 6.0;
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, isHovered ? r + 3.5 : r + 1.5, 0, Math.PI * 2);
    ctx.fillStyle = isHovered ? "rgba(255, 255, 255, 0.32)" : "rgba(0, 240, 255, 0.16)";
    ctx.fill();

    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = isHovered ? "#FFFFFF" : color;
    ctx.fill();
    ctx.lineWidth = 1.8;
    ctx.strokeStyle = "#06101E";
    ctx.stroke();

    if (label) {
      ctx.fillStyle = isHovered ? "#FFFFFF" : color;
      ctx.font = "bold 10px 'JetBrains Mono', monospace";
      ctx.fillText(label, x - 7, y - r - 5);
    }
    ctx.restore();
  }

  // ==========================================================================
  // 0. Interactive Airfoil Cross-Section Sculptor & Transonic Cp(x/c) Studio
  // ==========================================================================
  function drawAirfoilStudio(canvas, design, perf) {
    const env = setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;
    const K = window.MIC_KERNEL;
    const af = K.ensureCustomAirfoil(design);
    const afEval = (perf && perf.airfoilEval) || K.evaluateAirfoilSpline(design);
    const xCtrl = K.AIRFOIL_X_CTRL;

    // Layout: Top 55% = Interactive Airfoil Cross-Section Editor; Bottom 45% = Chordwise Cp(x/c) Plot
    const padL = 58, padR = 28;
    const pw = w - padL - padR;
    const topY = 44, topH = Math.round((h - 76) * 0.54);
    const midY = topY + Math.round(topH * 0.50);
    // Adaptive vertical scale so thin supersonic sections stay legible (snaps to 4/6/8/10/14 %c)
    const maxAbsY = Math.max.apply(null, af.upper.concat(af.lower).map(Math.abs));
    const autoYMax = [0.04, 0.06, 0.08, 0.10, 0.14].find((v) => v >= maxAbsY * 1.6) || 0.14;
    // Freeze the scale while the player is dragging so nodes don't jump under the cursor
    const yMax = (canvas._lockScale && canvas._lastYMax) ? canvas._lastYMax : autoYMax;
    canvas._lastYMax = yMax;

    const toX = (xc) => padL + xc * pw;
    const toY = (yc) => midY - (yc / yMax) * (topH * 0.48);
    const fromX = (px) => Math.max(0.0, Math.min(1.0, (px - padL) / Math.max(1, pw)));
    const fromY = (py) => ((midY - py) / Math.max(1, topH * 0.48)) * yMax;

    // Header
    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText(
      "INTERACTIVE AIRFOIL CROSS-SECTION SCULPTOR & TRANSONIC PRESSURE Cp(x/c) // 拖拽控制点或按住鼠标直接手绘翼型",
      14,
      19
    );
    ctx.fillStyle = "#E09F3E";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Preset: ${af.preset_name || "Custom"} | (t/c)_max: ${(afEval.tc_max * 100).toFixed(2)}% @ ${(afEval.x_tc_max * 100).toFixed(0)}%c | Camber: ${(afEval.camber_max * 100).toFixed(2)}% | M_cr: ${afEval.m_cr.toFixed(2)} | M_dd(2D): ${afEval.m_dd_2d.toFixed(2)} | CL_max: ${afEval.cl_max_2d.toFixed(2)}`,
      14,
      35
    );

    // Airfoil Editor Box & Grid
    ctx.strokeStyle = "rgba(74, 107, 156, 0.55)";
    ctx.lineWidth = 1.0;
    ctx.strokeRect(padL, topY, pw, topH);

    // Horizontal y/c grid lines (scaled to current view)
    [-1, -0.5, 0, 0.5, 1].map((f) => f * yMax * 0.75).forEach(function (yg) {
      const py = toY(yg);
      ctx.strokeStyle = yg === 0.0 ? "rgba(224, 159, 62, 0.45)" : "rgba(0, 240, 255, 0.10)";
      ctx.setLineDash(yg === 0.0 ? [5, 4] : []);
      ctx.beginPath();
      ctx.moveTo(padL, py);
      ctx.lineTo(padL + pw, py);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#6E88AD";
      ctx.font = "9px 'JetBrains Mono', monospace";
      ctx.fillText(`${(yg * 100).toFixed(1)}%c`, 10, py + 3);
    });

    // Chordwise station grid lines (0%, 20%, 40%, 60%, 80%, 100% c)
    [0.0, 0.2, 0.4, 0.6, 0.8, 1.0].forEach(function (xg) {
      const px = toX(xg);
      ctx.strokeStyle = "rgba(0, 240, 255, 0.10)";
      ctx.beginPath();
      ctx.moveTo(px, topY);
      ctx.lineTo(px, topY + topH);
      ctx.stroke();
    });

    // Shade Internal Wing Box & Fuel Volume (between front spar 18%c and rear spar 68%c)
    ctx.fillStyle = "rgba(59, 206, 172, 0.13)";
    ctx.beginPath();
    const N = afEval.xs.length;
    let startedBox = false;
    for (let i = 0; i < N; i++) {
      if (afEval.xs[i] >= 0.18 && afEval.xs[i] <= 0.68) {
        const px = toX(afEval.xs[i]), py = toY(afEval.yu[i]);
        if (!startedBox) {
          ctx.moveTo(px, py);
          startedBox = true;
        } else {
          ctx.lineTo(px, py);
        }
      }
    }
    for (let i = N - 1; i >= 0; i--) {
      if (afEval.xs[i] >= 0.18 && afEval.xs[i] <= 0.68) {
        ctx.lineTo(toX(afEval.xs[i]), toY(afEval.yl[i]));
      }
    }
    ctx.closePath();
    ctx.fill();

    // Draw Front Spar (18%c) and Rear Spar (68%c) I-beams
    [0.18, 0.68].forEach(function (xSpar, idx) {
      const idxGrid = Math.round(xSpar * (N - 1));
      const sx = toX(xSpar);
      const syTop = toY(afEval.yu[idxGrid]);
      const syBot = toY(afEval.yl[idxGrid]);
      ctx.strokeStyle = "#3BCEAC";
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      ctx.moveTo(sx, syTop);
      ctx.lineTo(sx, syBot);
      ctx.stroke();
      ctx.fillStyle = "#3BCEAC";
      ctx.font = "9px 'JetBrains Mono', monospace";
      ctx.fillText(idx === 0 ? "前梁 18%c" : "后梁 68%c", sx + 4, (syTop + syBot) * 0.5 + 3);
    });

    // Shade Full Airfoil Cross Section
    ctx.fillStyle = "rgba(0, 240, 255, 0.11)";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toY(afEval.yu[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    for (let i = N - 1; i >= 0; i--) {
      ctx.lineTo(toX(afEval.xs[i]), toY(afEval.yl[i]));
    }
    ctx.closePath();
    ctx.fill();

    // Draw Mean Camber Line (dashed gold)
    ctx.strokeStyle = "#E09F3E";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toY(afEval.camber[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Upper Surface Curve (cyan)
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toY(afEval.yu[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Draw Lower Surface Curve (amber)
    ctx.strokeStyle = "#F59E0B";
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toY(afEval.yl[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // If local supersonic pocket exists on upper surface, draw standing normal shock wave indicator!
    let shockIdx = -1;
    for (let i = 5; i < N - 5; i++) {
      if (afEval.cp_upper[i] < afEval.cp_crit && afEval.cp_upper[i + 1] >= afEval.cp_crit) {
        shockIdx = i;
      }
    }
    if (shockIdx > 0) {
      const sx = toX(afEval.xs[shockIdx]);
      const sy = toY(afEval.yu[shockIdx]);
      ctx.strokeStyle = "#FF4757";
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(sx - 6, sy - 28);
      ctx.lineTo(sx + 4, sy - 46);
      ctx.stroke();
      ctx.fillStyle = "#FF4757";
      ctx.font = "bold 10px 'JetBrains Mono', monospace";
      ctx.fillText("⚡ 局部激波 (Shock)", sx + 6, sy - 26);
    }

    // Build & Render 10 Interactive Control Handles (U1..U5 and L1..L5)
    const handles = [];
    const activeId = canvas._activeHandleId || null;
    for (let k = 0; k < 5; k++) {
      const xc = xCtrl[k];
      const ux = toX(xc), uy = toY(af.upper[k]);
      const lx = toX(xc), ly = toY(af.lower[k]);
      const uId = `af_u_${k}`;
      const lId = `af_l_${k}`;
      handles.push({ id: uId, kind: "af_upper", index: k, x: ux, y: uy, xc });
      handles.push({ id: lId, kind: "af_lower", index: k, x: lx, y: ly, xc });
      drawHandleNode(ctx, ux, uy, "#00F0FF", `U${k + 1}`, activeId === uId, 6.2);
      drawHandleNode(ctx, lx, ly, "#F59E0B", `L${k + 1}`, activeId === lId, 6.2);
    }

    // ========================================================================
    // Bottom Panel: Chordwise Transonic Pressure Distribution -Cp(x/c) @ M0.90
    // ========================================================================
    const cpTop = topY + topH + 18;
    const cpH = h - cpTop - 22;
    const cpMin = -0.5, cpMax = 1.45; // plotting -Cp so suction is UPWARD
    const toCpY = (negCp) => cpTop + cpH - ((Math.max(cpMin, Math.min(cpMax, negCp)) - cpMin) / (cpMax - cpMin)) * cpH;

    ctx.strokeStyle = "rgba(74, 107, 156, 0.55)";
    ctx.lineWidth = 1.0;
    ctx.strokeRect(padL, cpTop, pw, cpH);

    // Sonic Rooftop Limit Line (-Cp_crit)
    const negCpCrit = -afEval.cp_crit;
    const yCrit = toCpY(negCpCrit);
    ctx.strokeStyle = "#FF4757";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(padL, yCrit);
    ctx.lineTo(padL + pw, yCrit);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#FF4757";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText(`--- 音速临界压力线 -Cp,crit = ${negCpCrit.toFixed(2)} (高于此线即形成超音速激波阻力)`, padL + 10, yCrit - 5);

    // Shade Supersonic Shock Pocket where -Cp_upper > -Cp_crit
    ctx.fillStyle = "rgba(255, 71, 87, 0.25)";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]);
      const negCp = Math.max(negCpCrit, -afEval.cp_upper[i]);
      if (i === 0) ctx.moveTo(px, toCpY(negCp));
      else ctx.lineTo(px, toCpY(negCp));
    }
    ctx.lineTo(padL + pw, yCrit);
    ctx.lineTo(padL, yCrit);
    ctx.closePath();
    ctx.fill();

    // Draw Upper Surface Suction Curve -Cp_upper(x/c)
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toCpY(-afEval.cp_upper[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Draw Lower Surface Curve -Cp_lower(x/c)
    ctx.strokeStyle = "#F59E0B";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const px = toX(afEval.xs[i]), py = toCpY(-afEval.cp_lower[i]);
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    ctx.fillStyle = "#94A8C8";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText("-Cp (Suction)", 4, cpTop + 12);
    ctx.fillText("0%c (前缘 LE)", padL, h - 6);
    ctx.fillText("50%c", padL + pw * 0.48, h - 6);
    ctx.fillText("100%c (后缘 TE)", padL + pw - 95, h - 6);

    canvas._interactive = {
      mode: "airfoil",
      handles,
      box: { x: padL, y: topY, w: pw, h: topH },
      toX,
      toY,
      fromX,
      fromY,
    };
  }

  // ==========================================================================
  // 1. 3-View Orthographic Blueprint + Interactive Wing & Fuselage Handles
  // ==========================================================================
  function draw3ViewBlueprint(canvas, design, perf) {
    const env = setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;
    const K = window.MIC_KERNEL;

    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const sweep_deg = Number(wing.sweep_quarter_chord_deg || 35.0);
    const taper = Number(wing.taper_ratio || 0.4);
    const afEval = (perf && perf.airfoilEval) || K.evaluateAirfoilSpline(design);
    const tc = afEval.tc_max;
    const L = Number(fus.length_m || 14.0);
    const D = Number(fus.max_diameter_m || 1.5);
    const ad = (perf && perf.areaDist) || K.computeAreaRuleDistribution(design);
    const stationRadii = K.ensureFuselageStations(design);
    const minRadii = ad.min_radii || K.getMinClearanceRadii(design);

    const span = Math.sqrt(S * AR);
    const c_root = (2.0 * S) / (span * (1.0 + taper));
    const c_tip = c_root * taper;
    const sweep_rad = (sweep_deg * Math.PI) / 180.0;

    // Scale meters to pixels for Top View (left 62% of canvas)
    const autoScale = Math.min((w * 0.52) / Math.max(12.0, L * 1.15), (h * 0.62) / Math.max(8.0, span * 1.18));
    // Freeze scale during a drag so the grabbed handle tracks the cursor 1:1
    const scale = (canvas._lockScale && canvas._lastScale) ? canvas._lastScale : autoScale;
    canvas._lastScale = scale;
    const ox = w * 0.06;
    const cy = h * 0.48;

    // Title block
    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText(
      "ORTHOGRAPHIC 3-VIEW & PLANFORM SCULPTOR // 可直接拖拽翼尖(改后掠角/展弦比/梯形比)与机身蜂腰控制点",
      14,
      19
    );
    ctx.fillStyle = "#94A8C8";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Span: ${span.toFixed(2)}m | L: ${L.toFixed(2)}m | S: ${S.toFixed(1)}m² | Sweep: ${sweep_deg.toFixed(1)}° | Taper: ${taper.toFixed(2)} | R_area: ${ad.r_area.toFixed(2)} (Waist Fit: ${(ad.waist_quality * 100).toFixed(0)}%)`,
      14,
      35
    );

    // Centerline
    ctx.strokeStyle = "rgba(224, 159, 62, 0.45)";
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(ox - 10, cy);
    ctx.lineTo(ox + L * scale + 20, cy);
    ctx.stroke();
    ctx.setLineDash([]);

    // Wing leading/trailing coordinates
    const x_wing_le = ox + 0.31 * L * scale;
    const half_span_px = 0.5 * span * scale;
    const dx_qc = half_span_px * Math.tan(sweep_rad);
    const x_tip_le = x_wing_le + dx_qc + 0.25 * (c_root - c_tip) * scale;
    const x_tip_te = x_tip_le + c_tip * scale;
    const x_root_te = x_wing_le + c_root * scale;

    // Draw Upper & Lower Wing Halves
    ctx.fillStyle = "rgba(0, 240, 255, 0.13)";
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 1.8;
    [-1, 1].forEach(function (dir) {
      const rRootPx = K.sampleFuselageRadius(stationRadii, 0.45) * scale * 0.85;
      ctx.beginPath();
      ctx.moveTo(x_wing_le, cy + dir * rRootPx);
      ctx.lineTo(x_tip_le, cy + dir * half_span_px);
      ctx.lineTo(x_tip_te, cy + dir * half_span_px);
      ctx.lineTo(x_root_te, cy + dir * rRootPx);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    });

    // Draw Horizontal Tail (unless pure tailless delta)
    const isTaillessDelta = (sweep_deg >= 50 && taper <= 0.18);
    if (!isTaillessDelta) {
      const x_ht_le = ox + 0.80 * L * scale;
      const ht_span = 0.34 * half_span_px;
      const ht_root = 0.42 * c_root * scale;
      const ht_tip = 0.45 * ht_root;
      const ht_dx = ht_span * Math.tan(sweep_rad * 0.9);
      const rTailPx = K.sampleFuselageRadius(stationRadii, 0.85) * scale * 0.85;
      [-1, 1].forEach(function (dir) {
        ctx.beginPath();
        ctx.moveTo(x_ht_le, cy + dir * rTailPx);
        ctx.lineTo(x_ht_le + ht_dx, cy + dir * ht_span);
        ctx.lineTo(x_ht_le + ht_dx + ht_tip, cy + dir * ht_span);
        ctx.lineTo(x_ht_le + ht_root, cy + dir * rTailPx);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      });
    }

    // Draw Sculpted Fuselage Contour from 11-station spline!
    ctx.fillStyle = "rgba(14, 34, 64, 0.92)";
    ctx.strokeStyle = ad.r_area <= 1.18 ? "#3BCEAC" : "#00F0FF";
    ctx.lineWidth = 2.2;
    ctx.beginPath();
    const N = ad.xs.length;
    for (let i = 0; i < N; i++) {
      const u = i / (N - 1);
      const x = ox + u * L * scale;
      const r = ad.r_fus_arr[i] * scale;
      if (i === 0) ctx.moveTo(x, cy - r);
      else ctx.lineTo(x, cy - r);
    }
    for (let i = N - 1; i >= 0; i--) {
      const u = i / (N - 1);
      const x = ox + u * L * scale;
      const r = ad.r_fus_arr[i] * scale;
      ctx.lineTo(x, cy + r);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Draw Minimum Engine/Cockpit Clearance Envelope inside Fuselage (dashed red)
    ctx.strokeStyle = "rgba(255, 71, 87, 0.55)";
    ctx.lineWidth = 1.2;
    ctx.setLineDash([3, 3]);
    [-1, 1].forEach(function (dir) {
      ctx.beginPath();
      for (let k = 0; k < 11; k++) {
        const u = k / 10.0;
        const x = ox + u * L * scale;
        const rMin = minRadii[k] * scale;
        if (k === 0) ctx.moveTo(x, cy + dir * rMin);
        else ctx.lineTo(x, cy + dir * rMin);
      }
      ctx.stroke();
    });
    ctx.setLineDash([]);

    // Draw CG & AC markers
    const x_cg = x_wing_le + 0.38 * c_root * scale + 0.35 * dx_qc;
    const sm = perf ? perf.static_margin : 0.06;
    const x_ac = x_cg + sm * c_root * scale * 2.2;
    ctx.fillStyle = "#E09F3E";
    ctx.beginPath();
    ctx.arc(x_cg, cy, 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText("CG", x_cg - 8, cy - 8);

    ctx.fillStyle = "#3BCEAC";
    ctx.beginPath();
    ctx.arc(x_ac, cy, 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText("AC", x_ac + 4, cy + 14);

    // Interactive Handles on Top-View Blueprint:
    // 1. Wingtip Leading-Edge Handle (drag X -> Sweep, drag Y -> Span/AR)
    // 2. Wingtip Trailing-Edge Handle (drag X -> Taper/Area)
    // 3. Fuselage Station Handles S2..S8 on upper fuselage wall (pinch waist directly!)
    const handles = [];
    const activeId = canvas._activeHandleId || null;

    const wLeHandle = {
      id: "planform_wing_le",
      kind: "wing_le",
      x: x_tip_le,
      y: cy - half_span_px,
    };
    const wTeHandle = {
      id: "planform_wing_te",
      kind: "wing_te",
      x: x_tip_te,
      y: cy - half_span_px,
    };
    handles.push(wLeHandle, wTeHandle);
    drawHandleNode(ctx, wLeHandle.x, wLeHandle.y, "#00F0FF", "", activeId === wLeHandle.id, 6.5);
    drawHandleNode(ctx, wTeHandle.x, wTeHandle.y, "#F59E0B", "", activeId === wTeHandle.id, 6.0);
    ctx.font = "bold 10px 'JetBrains Mono', monospace";
    ctx.textAlign = "right";
    ctx.fillStyle = activeId === wLeHandle.id ? "#FFFFFF" : "#00F0FF";
    ctx.fillText("翼尖前缘 · 后掠/展长", wLeHandle.x - 12, wLeHandle.y - 10);
    ctx.textAlign = "left";
    ctx.fillStyle = activeId === wTeHandle.id ? "#FFFFFF" : "#F59E0B";
    ctx.fillText("翼尖后缘 · 梢弦/面积", wTeHandle.x + 12, wTeHandle.y + 4);

    for (let k = 1; k <= 9; k++) {
      const u = k / 10.0;
      const hx = ox + u * L * scale;
      const hy = cy - stationRadii[k] * scale;
      const hId = `fus_st_${k}`;
      handles.push({
        id: hId,
        kind: "fus_station_3view",
        index: k,
        x: hx,
        y: hy,
        rMin: minRadii[k],
      });
      drawHandleNode(ctx, hx, hy, "#3BCEAC", k === 5 ? "腰部S5" : "", activeId === hId, 4.8);
    }

    // ========================================================================
    // Right Side: Side Profile + Sculpted Root Airfoil Cutout Preview
    // ========================================================================
    const sx0 = w * 0.63;
    const sy0 = h * 0.36;
    const sScale = scale * 0.78;
    ctx.strokeStyle = "#00F0FF";
    ctx.fillStyle = "rgba(0, 240, 255, 0.12)";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const u = i / (N - 1);
      const x = sx0 + u * L * sScale;
      const r = ad.r_fus_arr[i] * sScale;
      if (i === 0) ctx.moveTo(x, sy0 - r * 0.85);
      else ctx.lineTo(x, sy0 - r * 0.85);
    }
    for (let i = N - 1; i >= 0; i--) {
      const u = i / (N - 1);
      const x = sx0 + u * L * sScale;
      const r = ad.r_fus_arr[i] * sScale;
      ctx.lineTo(x, sy0 + r * 0.72);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Canopy & Vertical Tail on Side View
    ctx.beginPath();
    ctx.moveTo(sx0 + 0.16 * L * sScale, sy0 - 0.55 * D * sScale);
    ctx.quadraticCurveTo(sx0 + 0.27 * L * sScale, sy0 - 1.15 * D * sScale, sx0 + 0.42 * L * sScale, sy0 - 0.55 * D * sScale);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(sx0 + 0.70 * L * sScale, sy0 - 0.45 * D * sScale);
    ctx.lineTo(sx0 + 0.92 * L * sScale, sy0 - 1.85 * D * sScale);
    ctx.lineTo(sx0 + 0.99 * L * sScale, sy0 - 1.85 * D * sScale);
    ctx.lineTo(sx0 + 0.96 * L * sScale, sy0 - 0.40 * D * sScale);
    ctx.fill();
    ctx.stroke();

    // Draw Sculpted Root Airfoil Cross-Section Inset on the bottom-right!
    const afBoxX = w * 0.63;
    const afBoxY = h * 0.62;
    const afBoxW = w * 0.33;
    const afBoxH = h * 0.26;
    ctx.strokeStyle = "rgba(0, 240, 255, 0.35)";
    ctx.strokeRect(afBoxX, afBoxY, afBoxW, afBoxH);
    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 10px 'JetBrains Mono', monospace";
    ctx.fillText(`机翼根部实测手绘翼型截面 (t/c=${(tc * 100).toFixed(1)}%, Camber=${(afEval.camber_max * 100).toFixed(1)}%)`, afBoxX + 8, afBoxY + 14);

    const afMidY = afBoxY + afBoxH * 0.58;
    const afPadX = afBoxX + 14;
    const afDrawW = afBoxW - 28;
    const afScaleY = afDrawW * 1.45; // slight vertical exaggeration for blueprint visibility
    ctx.fillStyle = "rgba(245, 158, 11, 0.18)";
    ctx.strokeStyle = "#F59E0B";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    for (let i = 0; i < afEval.xs.length; i++) {
      const px = afPadX + afEval.xs[i] * afDrawW;
      const py = afMidY - afEval.yu[i] * afScaleY;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    for (let i = afEval.xs.length - 1; i >= 0; i--) {
      const px = afPadX + afEval.xs[i] * afDrawW;
      const py = afMidY - afEval.yl[i] * afScaleY;
      ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Static Margin & Stability Footer
    ctx.fillStyle = "#E09F3E";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Static Margin: ${(sm * 100).toFixed(1)}% MAC (${sm >= 0.02 ? "STABLE" : "RELAXED/PITCH-UP RISK"}) | Root t/c: ${(tc * 100).toFixed(1)}% | Fuselage Vol: ${ad.fus_vol_m3.toFixed(1)} m³`,
      14,
      h - 12
    );

    canvas._interactive = {
      mode: "blueprint_3view",
      handles,
      ox,
      cy,
      scale,
      x_wing_le,
      c_root,
    };
  }

  window.MIC_PLOTS_PART1 = {
    setupBlueprintCanvas,
    drawHandleNode,
    drawAirfoilStudio,
    draw3ViewBlueprint,
  };
})();

(function () {
  "use strict";
  const P1 = window.MIC_PLOTS_PART1;

  // ==========================================================================
  // 2. Interactive Fuselage Lofting & Sears-Haack Area Rule A(x) Sculptor
  // ==========================================================================
  function drawAreaRulePlot(canvas, design, perf) {
    const env = P1.setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;
    const K = window.MIC_KERNEL;

    const ad = (perf && perf.areaDist) || K.computeAreaRuleDistribution(design);
    const stationRadii = K.ensureFuselageStations(design);
    const minRadii = ad.min_radii || K.getMinClearanceRadii(design);
    const isSmooth = ad.r_area <= 1.18;

    const padL = 58, padR = 26;
    const pw = w - padL - padR;

    // Top Panel (42% height): Interactive Fuselage Radius Sculptor R_fus(x)
    const fusTop = 42;
    const fusH = Math.round((h - 76) * 0.42);
    const autoFusMaxR = Math.max(1.35, Number((design.fuselage && design.fuselage.max_diameter_m) || 1.5) * 0.68);
    const fusMaxR = (canvas._lockScale && canvas._lastFusMaxR) ? canvas._lastFusMaxR : autoFusMaxR;
    canvas._lastFusMaxR = fusMaxR;
    const toX = (u) => padL + u * pw;
    const toFusY = (r) => fusTop + fusH - (Math.max(0.0, Math.min(fusMaxR, r)) / fusMaxR) * fusH;
    const fromFusY = (py) => Math.max(0.08, Math.min(fusMaxR, ((fusTop + fusH - py) / Math.max(1, fusH)) * fusMaxR));

    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText(
      "INTERACTIVE FUSELAGE WAIST SCULPTOR & SEARS–HAACK AREA DISTRIBUTION A(x) // 拖拽 S0-S10 捏出可口可乐瓶蜂腰",
      14,
      19
    );
    ctx.fillStyle = isSmooth ? "#3BCEAC" : "#FF5A47";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Wave-Drag Factor R_area = ${ad.r_area.toFixed(2)} | 蜂腰吻合度: ${(ad.waist_quality * 100).toFixed(0)}% | 机身容积: ${ad.fus_vol_m3.toFixed(1)} m³ | 状态: ${isSmooth ? "✅ 面积律修形达标 (消除跨音速激波墙)" : "⚠️ 截面积二阶导数突变 (触发跨音速波阻墙!)"}`,
      14,
      35
    );

    // Fuselage Sculptor Frame
    ctx.strokeStyle = "rgba(74, 107, 156, 0.55)";
    ctx.lineWidth = 1.0;
    ctx.strokeRect(padL, fusTop, pw, fusH);

    // Shade Wing Axial Footprint inside Fuselage Sculptor so player knows WHERE to pinch!
    const N = ad.xs.length;
    ctx.fillStyle = "rgba(0, 240, 255, 0.08)";
    for (let i = 0; i < N - 1; i++) {
      if (ad.a_wing[i] > 0.02) {
        const x1 = toX(i / (N - 1)), x2 = toX((i + 1) / (N - 1));
        ctx.fillRect(x1, fusTop, x2 - x1 + 0.5, fusH);
      }
    }
    ctx.fillStyle = "rgba(0, 240, 255, 0.55)";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText("◀── 机翼厚度叠加区 (在此区间向内向下拉动控制点 S4~S7 即可补偿机翼截面积，捏出蜂腰!) ──▶", padL + pw * 0.24, fusTop + 14);

    // Shade Sculpted Fuselage Half-Profile R_fus(x)
    ctx.fillStyle = "rgba(0, 240, 255, 0.16)";
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    ctx.moveTo(toX(0), fusTop + fusH);
    for (let i = 0; i < N; i++) {
      ctx.lineTo(toX(i / (N - 1)), toFusY(ad.r_fus_arr[i]));
    }
    ctx.lineTo(toX(1), fusTop + fusH);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Draw Minimum Clearance Boundary R_min(x) (Cockpit + Engine clearance) in Red Dashed
    ctx.fillStyle = "rgba(255, 71, 87, 0.16)";
    ctx.strokeStyle = "#FF4757";
    ctx.lineWidth = 1.6;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    ctx.moveTo(toX(0), fusTop + fusH);
    for (let k = 0; k < 11; k++) {
      ctx.lineTo(toX(k / 10.0), toFusY(minRadii[k]));
    }
    ctx.lineTo(toX(1), fusTop + fusH);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "#FF6B81";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText("--- 红色虚线禁区: 座舱与发动机最小净空包线 R_min(x)", padL + 10, fusTop + fusH - 6);
    ctx.fillStyle = "#94A8C8";
    ctx.fillText("R_fus(m)", 6, fusTop + 14);

    // Render 11 Interactive Fuselage Station Handles S0..S10
    const handles = [];
    const activeId = canvas._activeHandleId || null;
    for (let k = 0; k < 11; k++) {
      const u = k / 10.0;
      const hx = toX(u);
      const hy = toFusY(stationRadii[k]);
      const hId = `fus_station_${k}`;
      handles.push({
        id: hId,
        kind: "fus_station",
        index: k,
        x: hx,
        y: hy,
        u,
        rMin: minRadii[k],
      });
      const color = (k >= 4 && k <= 7) ? "#3BCEAC" : "#00F0FF";
      P1.drawHandleNode(ctx, hx, hy, color, `S${k}`, activeId === hId, 5.8);
    }

    // ========================================================================
    // Bottom Panel (58% height): Sears-Haack Area Distribution A(x) vs A_SH(x)
    // ========================================================================
    const areaTop = fusTop + fusH + 18;
    const areaH = h - areaTop - 22;
    const maxA = Math.max(ad.peak_total * 1.18, 2.5);
    const toAreaY = (a) => areaTop + areaH - (Math.max(0.0, Math.min(maxA, a)) / maxA) * areaH;

    ctx.strokeStyle = "rgba(74, 107, 156, 0.55)";
    ctx.lineWidth = 1.0;
    ctx.strokeRect(padL, areaTop, pw, areaH);

    // Shade Excess Bump between A_total(x) and Ideal Sears-Haack A_SH(x)
    ctx.fillStyle = isSmooth ? "rgba(59, 206, 172, 0.15)" : "rgba(217, 74, 56, 0.25)";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = toX(i / (N - 1)), y = toAreaY(ad.a_total[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    for (let i = N - 1; i >= 0; i--) {
      ctx.lineTo(toX(i / (N - 1)), toAreaY(ad.a_sh[i]));
    }
    ctx.closePath();
    ctx.fill();

    // Draw Fuselage A_fus(x)
    ctx.strokeStyle = "rgba(0, 240, 255, 0.65)";
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = toX(i / (N - 1)), y = toAreaY(ad.a_fus[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw Ideal Sears-Haack Spindle A_SH(x) (dashed brass)
    ctx.strokeStyle = "#E09F3E";
    ctx.lineWidth = 2.0;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = toX(i / (N - 1)), y = toAreaY(ad.a_sh[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Total A(x) = Fuselage + Wing + Tail
    ctx.strokeStyle = isSmooth ? "#3BCEAC" : "#FF5A47";
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = toX(i / (N - 1)), y = toAreaY(ad.a_total[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Legend & Labels
    ctx.fillStyle = "#94A8C8";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText(`0.0 m (机头 Nose)`, padL, h - 6);
    ctx.fillText(`${ad.L.toFixed(1)} m (尾喷管 Nozzle)`, padL + pw - 125, h - 6);
    ctx.fillText(`A(x) m²`, 6, areaTop + 14);
    ctx.fillStyle = "#E09F3E";
    ctx.fillText("--- 理想西尔斯-哈克纺锤体 A_SH(x)", padL + 12, areaTop + 14);
    ctx.fillStyle = isSmooth ? "#3BCEAC" : "#FF5A47";
    ctx.fillText("─── 全机实际总截面积 A_total(x) = 机身 + 机翼 + 尾翼", padL + 235, areaTop + 14);
    ctx.fillStyle = "#00F0FF";
    ctx.fillText("─── 机身截面积 A_fus(x)", padL + 545, areaTop + 14);

    canvas._interactive = {
      mode: "fuselage_area",
      handles,
      box: { x: padL, y: fusTop, w: pw, h: fusH },
      toX,
      toFusY,
      fromFusY,
      minRadii,
    };
  }

  // 3. Boyd Energy-Maneuverability Ps(M, h) Heatmap & Envelope
  function drawPsContourPlot(canvas, design, perf) {
    const env = P1.setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;
    canvas._interactive = null;

    const padL = 56, padR = 24, padT = 44, padB = 36;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText("BOYD ENERGY-MANEUVERABILITY // 1G SPECIFIC EXCESS POWER Ps(Mach, Alt)", 14, 20);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Max Mach: M ${perf.max_mach_alt.toFixed(2)} | Ceiling: ${(perf.service_ceiling_m * 3.28084).toFixed(0)} ft | Climb (SL): ${(perf.climb_rate_sl_mps * 196.85).toFixed(0)} ft/min | M0.8 Turn: ${perf.sustained_turn_dps_m08_4572m.toFixed(1)} deg/s`,
      14,
      36
    );

    const cols = 38, rows = 22;
    const cellW = pw / cols, cellH = ph / rows;
    const maxM = 2.3, minM = 0.25;
    const maxAltFt = 65000;
    const isUnruled = perf.areaDist ? perf.areaDist.r_area > 1.25 : (!design.fuselage || !design.fuselage.area_ruled);

    for (let r = 0; r < rows; r++) {
      const altFt = maxAltFt * (1.0 - (r + 0.5) / rows);
      const altM = altFt * 0.3048;
      const altRatio = altM / Math.max(8000, perf.service_ceiling_m);
      for (let c = 0; c < cols; c++) {
        const m = minM + ((c + 0.5) / cols) * (maxM - minM);
        const machCapAtAlt = altM < 11000
          ? perf.max_mach_sl + (perf.max_mach_alt - perf.max_mach_sl) * (altM / 11000.0)
          : perf.max_mach_alt * Math.max(0.0, 1.0 - 0.65 * Math.pow(Math.max(0, altRatio - 0.68), 1.8));
        const transonicPinch = isUnruled && m > 0.94 && m < 1.15 ? 0.35 : 0.0;
        const psNorm = (1.0 - Math.pow(m / Math.max(0.45, machCapAtAlt), 2.2)) * (1.0 - Math.pow(altRatio, 1.65)) - transonicPinch;
        const psMps = psNorm * perf.climb_rate_sl_mps * 1.15;

        if (psMps > 0) {
          const intensity = Math.min(1.0, psMps / 140.0);
          const g = Math.round(90 + 145 * intensity);
          const b = Math.round(140 + 100 * intensity);
          ctx.fillStyle = `rgba(18, ${g}, ${b}, 0.58)`;
        } else {
          ctx.fillStyle = "rgba(217, 74, 56, 0.14)";
        }
        ctx.fillRect(padL + c * cellW, padT + r * cellH, cellW + 0.5, cellH + 0.5);
      }
    }

    ctx.strokeStyle = "#00F0FF";
    ctx.strokeRect(padL, padT, pw, ph);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "10px 'JetBrains Mono', monospace";
    for (let m = 0.4; m <= 2.2; m += 0.3) {
      const x = padL + ((m - minM) / (maxM - minM)) * pw;
      ctx.fillText(`M${m.toFixed(1)}`, x - 12, padT + ph + 15);
    }
    [0, 20000, 40000, 60000].forEach(function (ft) {
      const y = padT + ph * (1.0 - ft / maxAltFt);
      ctx.fillText(`${ft / 1000}k ft`, 8, y + 4);
    });
  }

  // 4. Transonic Drag Rise CD0(M) Plot
  function drawDragPolarPlot(canvas, design, perf) {
    const env = P1.setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;
    canvas._interactive = null;

    const padL = 56, padR = 26, padT = 44, padB = 36;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText("TRANSONIC WAVE-DRAG RISE // ZERO-LIFT DRAG COEFFICIENT CD0(Mach)", 14, 20);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText("Solid Cyan: Current Sculpted Airfoil & Fuselage | Dashed Amber: Counterfactual Area-Rule Comparison", 14, 36);

    const altDesign = JSON.parse(JSON.stringify(design));
    altDesign.fuselage = altDesign.fuselage || {};
    const flipRule = !Boolean(design.fuselage && design.fuselage.area_ruled);
    altDesign.fuselage.area_ruled = flipRule;
    altDesign.fuselage.station_radii = window.MIC_KERNEL.buildDefaultFuselageRadii(
      altDesign,
      flipRule,
      window.MIC_KERNEL.getMinClearanceRadii(altDesign)
    );
    const altDist = window.MIC_KERNEL.computeAreaRuleDistribution(altDesign);

    const maxCD = 0.085;
    const toX = (m) => padL + ((m - 0.4) / 1.9) * pw;
    const toY = (cd) => padT + ph - Math.min(1.0, cd / maxCD) * ph;

    // Draw Counterfactual Curve (dashed)
    ctx.strokeStyle = "#E09F3E";
    ctx.lineWidth = 1.8;
    ctx.setLineDash([5, 4]);
    ctx.beginPath();
    for (let i = 0; i <= 60; i++) {
      const m = 0.4 + (i / 60) * 1.9;
      const d = window.MIC_KERNEL.computeDragPolarAtMach(altDesign, m, altDist, perf.airfoilEval);
      if (i === 0) ctx.moveTo(toX(m), toY(d.cd0));
      else ctx.lineTo(toX(m), toY(d.cd0));
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Current Design Curve
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let i = 0; i <= 60; i++) {
      const m = 0.4 + (i / 60) * 1.9;
      const d = perf.computeDragAtMach(m);
      if (i === 0) ctx.moveTo(toX(m), toY(d.cd0));
      else ctx.lineTo(toX(m), toY(d.cd0));
    }
    ctx.stroke();

    ctx.strokeStyle = "#4A6B9C";
    ctx.strokeRect(padL, padT, pw, ph);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "10px 'JetBrains Mono', monospace";
    [0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.1].forEach(function (m) {
      ctx.fillText(`M${m.toFixed(1)}`, toX(m) - 12, padT + ph + 15);
    });
    [0.01, 0.03, 0.05, 0.07].forEach(function (cd) {
      ctx.fillText(cd.toFixed(2), 14, toY(cd) + 4);
    });
  }

  window.MIC_PLOTS = Object.assign({}, P1, {
    drawAreaRulePlot,
    drawPsContourPlot,
    drawDragPolarPlot,
  });
})();
