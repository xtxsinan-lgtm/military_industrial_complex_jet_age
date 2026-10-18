// ============================================================================
// MIC: Jet Age — Interactive Engineering Blueprint Canvases (Module 08 UI/UX)
// 1. 3-View Orthographic Blueprint (Top / Side / Front + MAC, CG, AC, Static Margin)
// 2. Sears-Haack Area Rule Cross-Section A(x) vs Ideal A_SH(x) Plot
// 3. Boyd Specific Excess Power Ps(M, h) Heatmap & Envelope
// 4. Transonic Drag Rise CD0(M) & Drag Polar Plot
// ============================================================================

(function () {
  "use strict";

  function setupBlueprintCanvas(canvas) {
    if (!canvas) return null;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(480, Math.round(rect.width || 680));
    const h = Math.max(280, Math.round(rect.height || 340));
    if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
      canvas.width = w * dpr;
      canvas.height = h * dpr;
    }
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Prussian Blueprint Background + Grid
    ctx.fillStyle = "#081224";
    ctx.fillRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(0, 240, 255, 0.08)";
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

  // 1. 3-View Orthographic Blueprint Canvas
  function draw3ViewBlueprint(canvas, design, perf) {
    const env = setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;

    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const sweep_deg = Number(wing.sweep_quarter_chord_deg || 35.0);
    const taper = Number(wing.taper_ratio || 0.4);
    const tc = Number(wing.t_c_root || 0.08);
    const L = Number(fus.length_m || 14.0);
    const D = Number(fus.max_diameter_m || 1.5);
    const area_ruled = Boolean(fus.area_ruled);

    const span = Math.sqrt(S * AR);
    const c_root = (2.0 * S) / (span * (1.0 + taper));
    const c_tip = c_root * taper;
    const sweep_rad = (sweep_deg * Math.PI) / 180.0;

    // Scale meters to pixels for Top View (left 62% of canvas)
    const scale = Math.min((w * 0.52) / Math.max(12.0, L * 1.15), (h * 0.58) / Math.max(8.0, span * 1.15));
    const ox = w * 0.07;
    const cy = h * 0.44;

    // Title block
    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText("ORTHOGRAPHIC 3-VIEW BLUEPRINT // TOP & SIDE PROJECTION", 14, 20);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Span: ${span.toFixed(2)}m (${(span * 3.28084).toFixed(1)}ft) | Length: ${L.toFixed(2)}m | S: ${S.toFixed(1)}m² | Sweep: ${sweep_deg.toFixed(1)}° | Area-Ruled: ${area_ruled ? "YES (Wasp-Waist)" : "NO"}`,
      14,
      36
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
    ctx.fillStyle = "rgba(0, 240, 255, 0.12)";
    ctx.strokeStyle = "#00F0FF";
    ctx.lineWidth = 1.8;
    [-1, 1].forEach(function (dir) {
      ctx.beginPath();
      ctx.moveTo(x_wing_le, cy + dir * 0.42 * D * scale);
      ctx.lineTo(x_tip_le, cy + dir * half_span_px);
      ctx.lineTo(x_tip_te, cy + dir * half_span_px);
      ctx.lineTo(x_root_te, cy + dir * 0.42 * D * scale);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    });

    // Draw Horizontal Tail (unless pure tailless delta with very low taper & high sweep)
    const isTaillessDelta = (sweep_deg >= 50 && taper <= 0.18);
    if (!isTaillessDelta) {
      const x_ht_le = ox + 0.80 * L * scale;
      const ht_span = 0.34 * half_span_px;
      const ht_root = 0.42 * c_root * scale;
      const ht_tip = 0.45 * ht_root;
      const ht_dx = ht_span * Math.tan(sweep_rad * 0.9);
      [-1, 1].forEach(function (dir) {
        ctx.beginPath();
        ctx.moveTo(x_ht_le, cy + dir * 0.28 * D * scale);
        ctx.lineTo(x_ht_le + ht_dx, cy + dir * ht_span);
        ctx.lineTo(x_ht_le + ht_dx + ht_tip, cy + dir * ht_span);
        ctx.lineTo(x_ht_le + ht_root, cy + dir * 0.28 * D * scale);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      });
    }

    // Draw Fuselage Contour (showing explicit Coke-Bottle waist pinch if area_ruled = true!)
    ctx.fillStyle = "rgba(14, 34, 64, 0.92)";
    ctx.strokeStyle = area_ruled ? "#3BCEAC" : "#00F0FF";
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    const steps = 40;
    for (let i = 0; i <= steps; i++) {
      const u = i / steps;
      const x = ox + u * L * scale;
      let r = 0.5 * D * scale * Math.pow(Math.sin(Math.PI * Math.pow(u, 0.72)), 0.65);
      if (u > 0.85) r = Math.max(r, 0.30 * D * scale * (1.0 - 0.3 * (u - 0.85) / 0.15));
      if (area_ruled && u >= 0.32 && u <= 0.74) {
        const pinch = 0.26 * Math.sin(Math.PI * (u - 0.32) / 0.42);
        r *= (1.0 - pinch);
      }
      if (i === 0) ctx.moveTo(x, cy - r);
      else ctx.lineTo(x, cy - r);
    }
    for (let i = steps; i >= 0; i--) {
      const u = i / steps;
      const x = ox + u * L * scale;
      let r = 0.5 * D * scale * Math.pow(Math.sin(Math.PI * Math.pow(u, 0.72)), 0.65);
      if (u > 0.85) r = Math.max(r, 0.30 * D * scale * (1.0 - 0.3 * (u - 0.85) / 0.15));
      if (area_ruled && u >= 0.32 && u <= 0.74) {
        const pinch = 0.26 * Math.sin(Math.PI * (u - 0.32) / 0.42);
        r *= (1.0 - pinch);
      }
      ctx.lineTo(x, cy + r);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

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

    // Side Profile & Front View on the right side
    const sx0 = w * 0.63;
    const sy0 = h * 0.36;
    const sScale = scale * 0.78;
    ctx.strokeStyle = "#00F0FF";
    ctx.fillStyle = "rgba(0, 240, 255, 0.12)";
    ctx.beginPath();
    ctx.moveTo(sx0, sy0);
    ctx.quadraticCurveTo(sx0 + 0.22 * L * sScale, sy0 - 0.55 * D * sScale, sx0 + 0.96 * L * sScale, sy0 - 0.35 * D * sScale);
    ctx.lineTo(sx0 + L * sScale, sy0 + 0.25 * D * sScale);
    ctx.quadraticCurveTo(sx0 + 0.4 * L * sScale, sy0 + 0.52 * D * sScale, sx0, sy0 + 0.12 * D * sScale);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Canopy & Vertical Tail on Side View
    ctx.beginPath();
    ctx.moveTo(sx0 + 0.18 * L * sScale, sy0 - 0.38 * D * sScale);
    ctx.quadraticCurveTo(sx0 + 0.28 * L * sScale, sy0 - 0.95 * D * sScale, sx0 + 0.42 * L * sScale, sy0 - 0.44 * D * sScale);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(sx0 + 0.72 * L * sScale, sy0 - 0.38 * D * sScale);
    ctx.lineTo(sx0 + 0.92 * L * sScale, sy0 - 1.85 * D * sScale);
    ctx.lineTo(sx0 + 0.99 * L * sScale, sy0 - 1.85 * D * sScale);
    ctx.lineTo(sx0 + 0.96 * L * sScale, sy0 - 0.35 * D * sScale);
    ctx.fill();
    ctx.stroke();

    // Static Margin & Stability Footer
    ctx.fillStyle = "#E09F3E";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Static Margin: ${(sm * 100).toFixed(1)}% MAC (${sm >= 0.02 ? "STABLE" : "RELAXED/PITCH-UP RISK"}) | Root t/c: ${(tc * 100).toFixed(1)}%`,
      14,
      h - 14
    );
  }

  window.MIC_PLOTS_PART1 = {
    setupBlueprintCanvas,
    draw3ViewBlueprint,
  };
})();

(function () {
  "use strict";
  const P1 = window.MIC_PLOTS_PART1;

  // 2. Sears-Haack Area Rule A(x) Cross-Section Plot
  function drawAreaRulePlot(canvas, design, perf) {
    const env = P1.setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;

    const ad = (perf && perf.areaDist) || window.MIC_KERNEL.computeAreaRuleDistribution(design);
    const area_ruled = Boolean(design.fuselage && design.fuselage.area_ruled);

    const padL = 56, padR = 26, padT = 46, padB = 38;
    const pw = w - padL - padR;
    const ph = h - padT - padB;
    const maxA = Math.max(ad.peak_total * 1.18, 2.5);

    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText("SEARS–HAACK LONGITUDINAL CROSS-SECTION AREA DISTRIBUTION A(x)", 14, 20);
    ctx.fillStyle = area_ruled ? "#3BCEAC" : "#D94A38";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText(
      `Wave-Drag Roughness R_area = ${ad.r_area.toFixed(2)} (${area_ruled ? "WHITCOMB WASP-WAIST SMOOTHED — LOW TRANSONIC DRAG" : "SEVERE d²A/dx² TRANSONIC WAVE-DRAG SPIKE!"})`,
      14,
      36
    );

    // Axes
    ctx.strokeStyle = "#4A6B9C";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(padL, padT);
    ctx.lineTo(padL, padT + ph);
    ctx.lineTo(padL + pw, padT + ph);
    ctx.stroke();

    const N = ad.xs.length;
    const toX = (i) => padL + (i / (N - 1)) * pw;
    const toY = (a) => padT + ph - (a / maxA) * ph;

    // Shade Excess Bump between A_total(x) and Ideal Sears-Haack A_SH(x)
    ctx.fillStyle = area_ruled ? "rgba(59, 206, 172, 0.14)" : "rgba(217, 74, 56, 0.25)";
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const x = toX(i), y = toY(ad.a_total[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    for (let i = N - 1; i >= 0; i--) {
      ctx.lineTo(toX(i), toY(ad.a_sh[i]));
    }
    ctx.closePath();
    ctx.fill();

    // Draw Fuselage A_fus(x)
    ctx.strokeStyle = "rgba(0, 240, 255, 0.65)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      if (i === 0) ctx.moveTo(toX(i), toY(ad.a_fus[i]));
      else ctx.lineTo(toX(i), toY(ad.a_fus[i]));
    }
    ctx.stroke();

    // Draw Ideal Sears-Haack Spindle A_SH(x) (dashed brass)
    ctx.strokeStyle = "#E09F3E";
    ctx.lineWidth = 2.0;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      if (i === 0) ctx.moveTo(toX(i), toY(ad.a_sh[i]));
      else ctx.lineTo(toX(i), toY(ad.a_sh[i]));
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Total A(x) = Fuselage + Wing + Tail
    ctx.strokeStyle = area_ruled ? "#3BCEAC" : "#FF5A47";
    ctx.lineWidth = 2.6;
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      if (i === 0) ctx.moveTo(toX(i), toY(ad.a_total[i]));
      else ctx.lineTo(toX(i), toY(ad.a_total[i]));
    }
    ctx.stroke();

    // Legend & Labels
    ctx.fillStyle = "#94A8C8";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText(`0.0 m (Nose)`, padL, padT + ph + 16);
    ctx.fillText(`${ad.L.toFixed(1)} m (Tail Nozzle)`, padL + pw - 110, padT + ph + 16);
    ctx.fillText(`A_max: ${ad.peak_total.toFixed(2)} m²`, 6, padT + 12);
    ctx.fillStyle = "#E09F3E";
    ctx.fillText("--- Ideal Sears–Haack Spindle A_SH(x)", padL + 16, padT + 14);
    ctx.fillStyle = area_ruled ? "#3BCEAC" : "#FF5A47";
    ctx.fillText("─── Actual Aircraft Total A(x)", padL + 260, padT + 14);
  }

  // 3. Boyd Energy-Maneuverability Ps(M, h) Heatmap & Envelope
  function drawPsContourPlot(canvas, design, perf) {
    const env = P1.setupBlueprintCanvas(canvas);
    if (!env) return;
    const { ctx, w, h } = env;

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

    for (let r = 0; r < rows; r++) {
      const altFt = maxAltFt * (1.0 - (r + 0.5) / rows);
      const altM = altFt * 0.3048;
      const altRatio = altM / Math.max(8000, perf.service_ceiling_m);
      for (let c = 0; c < cols; c++) {
        const m = minM + ((c + 0.5) / cols) * (maxM - minM);
        // Normalized envelope function matching perf.max_mach_alt & perf.service_ceiling_m
        const machCapAtAlt = altM < 11000
          ? perf.max_mach_sl + (perf.max_mach_alt - perf.max_mach_sl) * (altM / 11000.0)
          : perf.max_mach_alt * Math.max(0.0, 1.0 - 0.65 * Math.pow(Math.max(0, altRatio - 0.68), 1.8));
        const transonicPinch = (!design.fuselage || !design.fuselage.area_ruled) && m > 0.94 && m < 1.15 ? 0.35 : 0.0;
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

    // Axes labels
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

    const padL = 56, padR = 26, padT = 44, padB = 36;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    ctx.fillStyle = "#00F0FF";
    ctx.font = "bold 12px 'JetBrains Mono', monospace";
    ctx.fillText("TRANSONIC WAVE-DRAG RISE // ZERO-LIFT DRAG COEFFICIENT CD0(Mach)", 14, 20);
    ctx.fillStyle = "#94A8C8";
    ctx.font = "11px 'JetBrains Mono', monospace";
    ctx.fillText("Solid: Current Design | Dashed Amber: Counterfactual Area-Rule Toggle Comparison", 14, 36);

    const altDesign = JSON.parse(JSON.stringify(design));
    altDesign.fuselage = altDesign.fuselage || {};
    altDesign.fuselage.area_ruled = !Boolean(design.fuselage && design.fuselage.area_ruled);
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
      const d = window.MIC_KERNEL.computeDragPolarAtMach(altDesign, m, altDist);
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
