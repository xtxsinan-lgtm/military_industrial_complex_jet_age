// ============================================================================
// MIC: Jet Age — Deterministic Client-Side Physics, Cost, Testing & Fly-Off Kernel
// Conforms to docs/spec/00_conventions.md, 01_aero_physics.md, 05_procurement.md, 06_testing_uncertainty.md
// ============================================================================

(function () {
  "use strict";

  const G0 = 9.80665;
  const GAMMA = 1.4;
  const R_AIR = 287.05287;
  const MPS_TO_KT = 1.0 / 0.514444;
  const M_TO_FT = 1.0 / 0.3048;
  const M_TO_NMI = 1.0 / 1852.0;
  const KG_TO_LB = 1.0 / 0.45359237;
  const N_TO_LBF = 1.0 / 4.4482216152605;

  // Deterministic PCG32 / Mulberry32 PRNG for reproducible browser runs
  function createRng(seed) {
    let a = (seed >>> 0) || 19520301;
    return {
      nextFloat: function () {
        a |= 0;
        a = (a + 0x6D2B79F5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296.0;
      },
      nextGaussian: function () {
        const u1 = Math.max(1e-7, this.nextFloat());
        const u2 = this.nextFloat();
        return Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
      }
    };
  }

  // ISA 1976 Atmosphere up to 25 km
  function isaAtmosphere(alt_m) {
    const h = Math.max(0.0, Math.min(25000.0, alt_m));
    let T, p;
    if (h <= 11000.0) {
      T = 288.15 - 0.0065 * h;
      p = 101325.0 * Math.pow(T / 288.15, 5.255876);
    } else if (h <= 20000.0) {
      T = 216.65;
      p = 22632.06 * Math.exp(-G0 * (h - 11000.0) / (R_AIR * T));
    } else {
      T = 216.65 + 0.001 * (h - 20000.0);
      p = 5474.889 * Math.pow(T / 216.65, -34.16319);
    }
    const rho = p / (R_AIR * T);
    const a = Math.sqrt(GAMMA * R_AIR * T);
    return { T, p, rho, a };
  }

  // Resolve engine from MIC_DATA.engines_hist or fallback
  function getEngineSpec(engine_id) {
    const engines = (window.MIC_DATA && window.MIC_DATA.engines_hist) || {};
    if (engines[engine_id]) return engines[engine_id];
    // Fuzzy match
    const keys = Object.keys(engines);
    for (let k of keys) {
      if (k.indexOf(engine_id) !== -1 || engine_id.indexOf(k) !== -1) return engines[k];
    }
    return engines["j57_p_21"] || engines[keys[0]];
  }

  // Evaluate Engine Thrust [N] and TSFC [kg/(N*s)] at (mach, alt_m, ab)
  function evalEngineAt(eng, mach, alt_m, ab) {
    const atm = isaAtmosphere(alt_m);
    const sigma = atm.rho / 1.225;
    const theta = atm.T / 288.15;
    const dry_sl = (eng.thrust_dry_sl_N || (eng.cycle && eng.cycle.design_thrust_dry_N) || 40000.0);
    const ab_sl = (eng.thrust_ab_sl_N || (eng.cycle && eng.cycle.design_thrust_ab_N) || dry_sl * 1.45);
    const has_ab = Boolean(eng.afterburner_capable || (eng.cycle && eng.cycle.afterburner_capable) || ab_sl > dry_sl * 1.05);
    const use_ab = Boolean(ab && has_ab);
    const base_thrust = use_ab ? ab_sl : dry_sl;

    // Ram recovery & altitude lapse
    const ram = 1.0 + 0.18 * mach * mach - (mach > 1.6 ? 0.12 * Math.pow(mach - 1.6, 1.5) : 0.0);
    const lapse = Math.pow(sigma, alt_m <= 11000 ? 0.72 : 0.88) / Math.sqrt(Math.max(0.75, theta));
    const thrust_N = base_thrust * lapse * Math.max(0.4, ram);

    const tsfc_dry = eng.tsfc_dry_kg_N_s || 0.000026;
    const tsfc_ab = eng.tsfc_ab_kg_N_s || tsfc_dry * 2.15;
    const tsfc = (use_ab ? tsfc_ab : tsfc_dry) * (1.0 + 0.12 * mach) * Math.sqrt(theta);
    return { thrust_N, tsfc, has_ab };
  }

  // ==========================================================================
  // Interactive Airfoil Spline / CST Solver (5 Upper + 5 Lower Draggable Nodes)
  // ==========================================================================
  const AIRFOIL_X_CTRL = [0.08, 0.25, 0.45, 0.68, 0.88];

  const AIRFOIL_PRESETS = {
    naca_64a210: {
      id: "naca_64a210",
      name: "NACA 64A-210 (F-86 亚音速层流翼)",
      name_zh: "NACA 64A-210 (高亚音速层流翼 — F-86 佩刀)",
      upper: [0.039, 0.058, 0.056, 0.038, 0.015],
      lower: [-0.025, -0.041, -0.044, -0.029, -0.011],
    },
    naca_65a006: {
      id: "naca_65a006",
      name: "NACA 65A-006 (F-102 跨音速薄翼)",
      name_zh: "NACA 65A-006 (跨音速薄对称翼 — F-100 / F-102)",
      upper: [0.021, 0.031, 0.033, 0.023, 0.009],
      lower: [-0.021, -0.031, -0.033, -0.023, -0.009],
    },
    biconvex_34: {
      id: "biconvex_34",
      name: "3.4% 双弧超音速刀锋翼 (F-104)",
      name_zh: "3.4% 剃刀双弧超音速翼 (Biconvex Mach 2 — F-104 星式)",
      upper: [0.009, 0.015, 0.017, 0.013, 0.005],
      lower: [-0.009, -0.015, -0.017, -0.013, -0.005],
    },
    supercritical_early: {
      id: "supercritical_early",
      name: "Whitcomb 平顶超临界减波阻翼 (Supercritical)",
      name_zh: "惠特科姆早期平顶超临界翼 (削平上表面激波峰值 + 后缘反弯)",
      upper: [0.028, 0.032, 0.032, 0.028, 0.014],
      lower: [-0.024, -0.032, -0.030, -0.014, 0.002],
    },
    high_camber_navy: {
      id: "high_camber_navy",
      name: "高弯度舰载机大升力翼 (F8U / F4D)",
      name_zh: "高弯度舰载大升力翼型 (High-Lift Carrier — F8U / F4D)",
      upper: [0.044, 0.062, 0.055, 0.036, 0.014],
      lower: [-0.016, -0.024, -0.025, -0.016, -0.006],
    },
    cambered_carrier: {
      id: "cambered_carrier",
      name: "高弯度舰载机大升力翼 (F8U / F4D)",
      name_zh: "高弯度舰载大升力翼型 (High-Lift Carrier — F8U / F4D)",
      upper: [0.044, 0.062, 0.055, 0.036, 0.014],
      lower: [-0.016, -0.024, -0.025, -0.016, -0.006],
    },
    thick_early_jet: {
      id: "thick_early_jet",
      name: "NACA 65-212 (P-80 厚平直翼)",
      name_zh: "NACA 65-212 (二战末期厚平直翼 — P-80 / F-84)",
      upper: [0.048, 0.069, 0.066, 0.044, 0.017],
      lower: [-0.034, -0.050, -0.051, -0.034, -0.013],
    },
  };

  function createAirfoilFromTc(tc_target, hasCamber) {
    const tc = Math.max(0.03, Math.min(0.16, Number(tc_target || 0.07)));
    const scale = tc / 0.066;
    const camb = hasCamber ? 0.007 : 0.0;
    return {
      preset_id: "custom",
      upper: [
        Number((0.021 * scale + camb * 0.7).toFixed(4)),
        Number((0.031 * scale + camb).toFixed(4)),
        Number((0.033 * scale + camb).toFixed(4)),
        Number((0.023 * scale + camb * 0.7).toFixed(4)),
        Number((0.009 * scale + camb * 0.3).toFixed(4)),
      ],
      lower: [
        Number((-0.021 * scale + camb * 0.5).toFixed(4)),
        Number((-0.031 * scale + camb * 0.7).toFixed(4)),
        Number((-0.033 * scale + camb * 0.7).toFixed(4)),
        Number((-0.023 * scale + camb * 0.5).toFixed(4)),
        Number((-0.009 * scale + camb * 0.2).toFixed(4)),
      ],
    };
  }

  function ensureCustomAirfoil(design) {
    design.wing = design.wing || {};
    if (!design.custom_airfoil || !Array.isArray(design.custom_airfoil.upper) || design.custom_airfoil.upper.length !== 5) {
      const tc = Number(design.wing.t_c_root || 0.07);
      const isSub = Number(design.wing.sweep_quarter_chord_deg || 35) < 38;
      design.custom_airfoil = createAirfoilFromTc(tc, isSub);
    }
    return design.custom_airfoil;
  }

  // Smooth piecewise cubic / cosine interpolation through (0,0), 5 control nodes, and (1,0)
  function sampleAirfoilSurface(ctrlVals, x) {
    if (x <= 0.0 || x >= 1.0) return 0.0;
    const xs = [0.0, 0.08, 0.25, 0.45, 0.68, 0.88, 1.0];
    const ys = [0.0, ctrlVals[0], ctrlVals[1], ctrlVals[2], ctrlVals[3], ctrlVals[4], 0.0];
    if (x <= xs[1]) {
      // Square-root + linear blend for realistic airfoil leading edge
      const u = x / xs[1];
      return ys[1] * (0.65 * Math.sqrt(u) + 0.35 * u);
    }
    for (let i = 1; i < xs.length - 1; i++) {
      if (x <= xs[i + 1]) {
        const u = (x - xs[i]) / (xs[i + 1] - xs[i]);
        const s = 0.5 * (1.0 - Math.cos(Math.PI * u));
        return ys[i] * (1.0 - s) + ys[i + 1] * s;
      }
    }
    return 0.0;
  }

  function evaluateAirfoilSpline(design) {
    const af = ensureCustomAirfoil(design);
    const N = 61;
    const xs = [];
    const yu = [];
    const yl = [];
    const thick = [];
    const camber = [];

    let tc_max = 0.02;
    let x_tc_max = 0.35;
    let camber_max = 0.0;
    let area_norm = 0.0;

    for (let i = 0; i < N; i++) {
      const x = i / (N - 1);
      const uVal = Math.max(0.002, sampleAirfoilSurface(af.upper, x));
      const lVal = Math.min(-0.002, sampleAirfoilSurface(af.lower, x));
      const tVal = uVal - lVal;
      const cVal = 0.5 * (uVal + lVal);
      xs.push(x);
      yu.push(uVal);
      yl.push(lVal);
      thick.push(tVal);
      camber.push(cVal);
      if (tVal > tc_max) {
        tc_max = tVal;
        x_tc_max = x;
      }
      if (Math.abs(cVal) > Math.abs(camber_max)) {
        camber_max = cVal;
      }
      if (i > 0) {
        area_norm += 0.5 * (thick[i] + thick[i - 1]) * (1.0 / (N - 1));
      }
    }

    // Leading-edge bluntness parameter
    const le_thick = Math.max(0.008, af.upper[0] - af.lower[0]);
    const le_sharpness = Math.max(0.0, Math.min(1.0, 1.0 - (le_thick / Math.max(0.025, tc_max * 0.82))));

    // Compute chordwise Cp(x/c) at transonic Mach M_inf = 0.86, alpha = 2.5 deg
    const cp_crit = -0.28; // critical pressure coefficient near M=0.86 swept
    const cp_upper = [];
    const cp_lower = [];
    for (let i = 0; i < N; i++) {
      const x = xs[i];
      const slopeTerm = Math.sin(Math.PI * Math.pow(x, 0.65));
      const suctionPeak = (i > 0 && i < N - 1)
        ? -2.85 * (yu[i] * 1.35 + 0.018 * Math.pow(1.0 - x, 0.7) * Math.sqrt(Math.max(0.05, x))) * slopeTerm
        : 0.15;
      const lowerPress = (i > 0 && i < N - 1)
        ? 2.25 * (yl[i] * 1.15 + 0.008 * (1.0 - x)) * slopeTerm
        : 0.20;
      cp_upper.push(Number(Math.max(-1.65, Math.min(0.45, suctionPeak)).toFixed(3)));
      cp_lower.push(Number(Math.max(-1.10, Math.min(0.55, lowerPress)).toFixed(3)));
    }

    const min_cp = Math.min(...cp_upper);
    // Critical Mach & Drag-Divergence Mach from drawn airfoil shape
    const aft_bonus = Math.max(-0.025, Math.min(0.025, (x_tc_max - 0.35) * 0.14));
    const m_cr = Math.max(0.68, Math.min(0.95, 0.91 - 1.45 * tc_max - 1.1 * Math.abs(camber_max) + aft_bonus));
    const m_dd_2d = m_cr + 0.065 + 0.025 * le_sharpness;

    // 2D CL_max: helped by positive camber and rounded leading edge, hurt by razor-thin LE
    const cl_max_2d = Math.max(0.78, Math.min(1.72,
      0.92 + 5.8 * Math.min(0.09, tc_max) + 9.5 * Math.max(-0.01, camber_max) - 0.22 * le_sharpness
    ));

    // Wave-drag shape multiplier: razor-thin & aft-loaded reduces supersonic wave drag
    const wave_drag_af_mult = Math.max(0.62, Math.min(1.65,
      1.0 - 0.24 * le_sharpness - 0.65 * (x_tc_max - 0.36) + 2.5 * Math.abs(camber_max)
    ));

    return {
      xs,
      yu,
      yl,
      thick,
      camber,
      tc_max: Number(tc_max.toFixed(4)),
      x_tc_max: Number(x_tc_max.toFixed(2)),
      camber_max: Number(camber_max.toFixed(4)),
      le_sharpness: Number(le_sharpness.toFixed(2)),
      area_norm: Number(area_norm.toFixed(4)),
      cp_upper,
      cp_lower,
      cp_crit,
      min_cp: Number(min_cp.toFixed(2)),
      m_cr: Number(m_cr.toFixed(3)),
      m_dd_2d: Number(m_dd_2d.toFixed(3)),
      cl_max_2d: Number(cl_max_2d.toFixed(2)),
      wave_drag_af_mult: Number(wave_drag_af_mult.toFixed(3)),
      ctrl_x: AIRFOIL_X_CTRL,
      upper_ctrl: af.upper,
      lower_ctrl: af.lower,
    };
  }

  // ==========================================================================
  // Interactive 11-Station Sculptable Fuselage & Sears-Haack Area Rule Solver
  // ==========================================================================
  const FUS_STATION_U = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];

  function getMinClearanceRadii(design) {
    const fus = design.fuselage || {};
    const prop = design.propulsion || {};
    const D = Number(fus.max_diameter_m || 1.5);
    const rMax = 0.5 * D;
    const isTwin = Number(prop.count || 1) >= 2;
    const engR = isTwin ? Math.max(0.56, rMax * 0.72) : Math.max(0.42, rMax * 0.56);
    // 11 stations: Nose, Radome/Intake, Cockpit, Shoulder, Wing-LE, Wing-Mid, Wing-TE, Aft-Bay, Engine-Mid, Tailpipe, Nozzle
    return [
      0.16,
      Math.min(rMax * 0.62, 0.42),
      Math.min(rMax * 0.74, 0.52), // Cockpit clearance
      Math.min(rMax * 0.74, 0.52),
      engR,                        // Wing root / duct clearance
      engR,                        // Wasp-waist minimum limit (cannot crush engine!)
      engR,
      engR * 1.02,
      engR * 0.96,
      engR * 0.85,
      Math.max(0.28, engR * 0.70), // Exhaust nozzle
    ];
  }

  function buildDefaultFuselageRadii(designOrD, forceAreaRulePinch, minClearOpt) {
    const isObj = designOrD && typeof designOrD === "object";
    const design = isObj ? designOrD : {};
    const fus = design.fuselage || {};
    const wing = design.wing || {};
    const L = Number(fus.length_m || 14.0);
    const D = isObj ? Number(fus.max_diameter_m || 1.5) : Number(designOrD || 1.5);
    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const tc = Number(wing.t_c_root || 0.08);
    const sweep_rad = Number(wing.sweep_quarter_chord_deg || 35.0) * Math.PI / 180.0;
    const area_ruled = forceAreaRulePinch !== undefined ? Boolean(forceAreaRulePinch) : Boolean(fus.area_ruled);

    const A_max_fus = Math.PI * 0.25 * D * D;
    const span = Math.sqrt(S * AR);
    const c_mean = S / Math.max(1.0, span);
    const wing_vol_est = 0.68 * S * c_mean * tc;
    const wing_x0 = 0.30 * L;
    const wing_len = Math.min(0.48 * L, Math.max(0.24 * L, c_mean * 1.35 + 0.5 * span * Math.sin(sweep_rad)));
    const wing_peak = (wing_vol_est / Math.max(1.0, wing_len)) * 1.85;
    const minClear = minClearOpt || getMinClearanceRadii(isObj ? design : { fuselage: { max_diameter_m: D } });

    return FUS_STATION_U.map(function (u, idx) {
      if (idx === 0) return Number(minClear[0].toFixed(3));
      const u0 = wing_x0 / L;
      const u1 = Math.min(0.88, (wing_x0 + wing_len) / L);
      let w_a = 0.0;
      if (u >= u0 && u <= u1) {
        const w_u = (u - u0) / Math.max(0.05, u1 - u0);
        w_a = wing_peak * Math.pow(Math.sin(Math.PI * w_u), 1.6);
      }
      let t_a = 0.0;
      if (u >= 0.78 && u <= 0.96) {
        const t_u = (u - 0.78) / 0.18;
        t_a = 0.22 * wing_peak * Math.pow(Math.sin(Math.PI * t_u), 1.5);
      }
      const base_f = A_max_fus * Math.pow(Math.max(0.06, 4.0 * u * (1.0 - u)), 0.85);
      const pinch = area_ruled ? Math.min(0.52 * base_f, 0.82 * w_a + 0.45 * t_a) : 0.0;
      const f_a = Math.max(Math.PI * minClear[idx] * minClear[idx], base_f - pinch);
      return Number(Math.sqrt(f_a / Math.PI).toFixed(3));
    });
  }

  function ensureFuselageStations(design) {
    design.fuselage = design.fuselage || {};
    if (!Array.isArray(design.fuselage.station_radii) || design.fuselage.station_radii.length !== 11) {
      design.fuselage.station_radii = buildDefaultFuselageRadii(design, Boolean(design.fuselage.area_ruled));
    }
    return design.fuselage.station_radii;
  }

  function sampleFuselageRadius(radii, u) {
    const clampedU = Math.max(0.0, Math.min(1.0, u));
    const scaled = clampedU * 10.0;
    const idx = Math.min(9, Math.floor(scaled));
    const frac = scaled - idx;
    const s = 0.5 * (1.0 - Math.cos(Math.PI * frac));
    return radii[idx] * (1.0 - s) + radii[idx + 1] * s;
  }

  // Compute longitudinal Cross-Sectional Area Distribution A(x) vs Ideal Sears-Haack A_SH(x)
  function computeAreaRuleDistribution(design) {
    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const L = Number(fus.length_m || 14.0);
    const D = Number(fus.max_diameter_m || 1.5);
    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const sweep_rad = Number(wing.sweep_quarter_chord_deg || 35.0) * Math.PI / 180.0;

    const afStats = evaluateAirfoilSpline(design);
    const tc = afStats.tc_max;
    const radii = ensureFuselageStations(design);
    const minClear = getMinClearanceRadii(design);
    const unruledRadii = buildDefaultFuselageRadii(design, false, minClear);

    const N = 61;
    const xs = [];
    const r_fus_arr = [];
    const a_fus = [];
    const a_wing = [];
    const a_tail = [];
    const a_total = [];
    const a_sh = [];

    const span = Math.sqrt(S * AR);
    const c_mean = S / Math.max(1.0, span);
    const wing_vol_est = 0.68 * S * c_mean * tc;
    const wing_x0 = 0.30 * L;
    const wing_len = Math.min(0.48 * L, Math.max(0.24 * L, c_mean * 1.35 + 0.5 * span * Math.sin(sweep_rad)));
    const wing_peak = (wing_vol_est / Math.max(1.0, wing_len)) * 1.85;

    let fus_vol_m3 = 0.0;
    let wingZoneRelief = 0.0;
    let wingZoneUnruled = 0.0;

    for (let i = 0; i < N; i++) {
      const u = i / (N - 1); // 0..1 along fuselage
      const x = u * L;
      xs.push(x);

      // Wing cross-section contribution (smooth bell between u_start and u_end)
      const u0 = wing_x0 / L;
      const u1 = Math.min(0.88, (wing_x0 + wing_len) / L);
      let w_a = 0.0;
      if (u >= u0 && u <= u1) {
        const w_u = (u - u0) / Math.max(0.05, u1 - u0);
        w_a = wing_peak * Math.pow(Math.sin(Math.PI * w_u), 1.6);
      }

      // Empennage bump near aft end
      let t_a = 0.0;
      if (u >= 0.78 && u <= 0.96) {
        const t_u = (u - 0.78) / 0.18;
        t_a = 0.22 * wing_peak * Math.pow(Math.sin(Math.PI * t_u), 1.5);
      }

      // Player-sculpted fuselage radius at station u
      const r_val = sampleFuselageRadius(radii, u);
      const r_unruled = sampleFuselageRadius(unruledRadii, u);
      const r_min = sampleFuselageRadius(minClear, u);
      const f_a = Math.PI * r_val * r_val;
      const f_unruled = Math.PI * r_unruled * r_unruled;
      const f_min = Math.PI * r_min * r_min;

      if (w_a > 0.05 * wing_peak) {
        const maxPossibleRelief = Math.max(0.04, Math.min(0.52 * f_unruled, 0.82 * w_a + 0.45 * t_a, f_unruled - f_min));
        wingZoneRelief += Math.min(maxPossibleRelief * 1.12, Math.max(0.0, f_unruled - f_a));
        wingZoneUnruled += maxPossibleRelief;
      }

      r_fus_arr.push(r_val);
      a_fus.push(f_a);
      a_wing.push(w_a);
      a_tail.push(t_a);
      a_total.push(f_a + w_a + t_a);
      if (i > 0) {
        fus_vol_m3 += 0.5 * (a_fus[i] + a_fus[i - 1]) * (L / (N - 1));
      }
    }

    const peak_total = Math.max(...a_total, 0.5);
    const ruledRefRadii = buildDefaultFuselageRadii(design, true, minClear);
    let sh_peak = 0.5;
    for (let i = 0; i < N; i++) {
      const u = i / (N - 1);
      const r_ref = sampleFuselageRadius(ruledRefRadii, u);
      sh_peak = Math.max(sh_peak, Math.PI * r_ref * r_ref + a_wing[i] + a_tail[i]);
    }
    for (let i = 0; i < N; i++) {
      const u = i / (N - 1);
      // Sears-Haack ideal spindle matched to area-ruled target peak
      a_sh.push(sh_peak * Math.pow(Math.max(0.0, 4.0 * u * (1.0 - u)), 1.05));
    }

    // Continuous Sears-Haack deviation & waist relief metric (works for both auto area-rule AND manual mouse sculpting!)
    const reliefRatio = Math.max(0.0, Math.min(1.10, wingZoneRelief / Math.max(0.10, wingZoneUnruled)));
    const raw_r_area = 1.58 - 0.54 * reliefRatio;
    const r_area = Number(Math.max(1.01, Math.min(1.95, raw_r_area)).toFixed(3));

    // Effective area-rule quality 0..1 (1.0 = ideal Sears-Haack waist, 0.0 = un-pinched cylinder bump)
    const waist_quality = Number(Math.max(0.0, Math.min(1.05, (1.58 - r_area) / 0.54)).toFixed(3));

    return {
      xs,
      r_fus_arr,
      a_fus,
      a_wing,
      a_tail,
      a_total,
      a_sh,
      r_area,
      waist_quality,
      fus_vol_m3: Number(fus_vol_m3.toFixed(2)),
      L,
      D,
      peak_total,
      station_u: FUS_STATION_U,
      station_radii: radii,
      min_radii: minClear,
      min_clearance_radii: minClear,
    };
  }

  window.MIC_KERNEL_PART1 = {
    createRng,
    isaAtmosphere,
    getEngineSpec,
    evalEngineAt,
    AIRFOIL_X_CTRL,
    AIRFOIL_PRESETS,
    createAirfoilFromTc,
    ensureCustomAirfoil,
    evaluateAirfoilSpline,
    FUS_STATION_U,
    getMinClearanceRadii,
    buildDefaultFuselageRadii,
    ensureFuselageStations,
    sampleFuselageRadius,
    computeAreaRuleDistribution,
    MPS_TO_KT,
    M_TO_FT,
    M_TO_NMI,
    KG_TO_LB,
    N_TO_LBF,
    G0,
  };
})();

(function () {
  "use strict";
  const P1 = window.MIC_KERNEL_PART1;

  // Evaluate CD0(M) and Induced Drag factor K(M) for a given design
  function computeDragPolarAtMach(design, mach, areaDist, afEvalOpt) {
    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const sweep_deg = Number(wing.sweep_quarter_chord_deg || 35.0);
    const sweep_rad = sweep_deg * Math.PI / 180.0;
    const afEval = afEvalOpt || P1.evaluateAirfoilSpline(design);
    const tc = afEval.tc_max;
    const L = Number(fus.length_m || 14.0);
    const D = Number(fus.max_diameter_m || 1.5);
    const area_ruled = Boolean(fus.area_ruled);

    // Subsonic parasitic CD0 (sensitive to airfoil thickness & camber)
    const S_wet_fus = Math.PI * D * L * 0.78;
    const S_wet_wing = 2.04 * S;
    const cf = 0.00285;
    const cd0_sub = cf * ((S_wet_fus * 1.18 + S_wet_wing * (1.0 + 1.8 * tc + 1.6 * Math.abs(afEval.camber_max))) / Math.max(8.0, S)) + 0.0045;

    // 3D Korn drag-divergence Mach M_dd from custom 2D airfoil m_dd_2d and sweep
    const m_dd = Math.max(0.72, (afEval.m_dd_2d / Math.pow(Math.cos(sweep_rad), 0.55)));

    // Transonic & Supersonic Sears-Haack wave drag (combining custom fuselage r_area + custom airfoil wave_drag_af_mult)
    const r_area = areaDist ? areaDist.r_area : (area_ruled ? 1.02 : 1.58);
    let cd_wave = 0.0;
    if (mach > m_dd - 0.05) {
      const dm = Math.max(0.0, mach - (m_dd - 0.05));
      const peak_wave = 0.028 * r_area * afEval.wave_drag_af_mult * Math.pow(tc / 0.08, 1.45) * Math.pow(Math.cos(sweep_rad), 1.1) * (1.0 + 1.5 * (D * D / Math.max(10.0, S)));
      if (mach <= 1.18) {
        const x = Math.min(1.0, dm / Math.max(0.12, 1.18 - (m_dd - 0.05)));
        cd_wave = peak_wave * (3.0 * x * x - 2.0 * x * x * x);
      } else {
        cd_wave = peak_wave * Math.pow(1.18 / mach, 0.42);
      }
    }

    // Induced drag factor K(M) (camber improves subsonic Oswald efficiency slightly)
    const e0 = Math.max(0.58, Math.min(0.92, 0.84 - 0.0035 * Math.max(0.0, sweep_deg - 20.0) + 0.75 * Math.max(0.0, Math.min(0.04, afEval.camber_max))));
    const k_sub = 1.0 / (Math.PI * AR * e0);
    const k_sup = mach > 1.05 ? k_sub * (1.0 + 0.55 * (mach - 1.0)) : k_sub;

    return {
      cd0: cd0_sub + cd_wave,
      cd0_sub,
      cd_wave,
      k: k_sup,
      m_dd,
      r_area,
    };
  }

  // Evaluate Full Aircraft Performance Report (anchored to Python Oracle when matching template)
  function evaluateAircraftPerformance(design, baseTemplateStem) {
    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const prop = design.propulsion || {};
    const fuel = design.fuel || {};
    const struct = design.structure || {};

    const S = Number(wing.area_m2 || 30.0);
    const AR = Number(wing.aspect_ratio || 3.5);
    const sweep_deg = Number(wing.sweep_quarter_chord_deg || 35.0);
    const taper = Number(wing.taper_ratio || 0.4);
    const afEval = P1.evaluateAirfoilSpline(design);
    const tc = afEval.tc_max;
    wing.t_c_root = Number(tc.toFixed(4));
    const L = Number(fus.length_m || 14.0);
    const D = Number(fus.max_diameter_m || 1.5);
    const area_ruled = Boolean(fus.area_ruled);
    const eng_id = prop.engine_id || "j57_p_21";
    const eng_count = Number(prop.count || 1);
    const ab = Boolean(prop.afterburner);
    const fuel_kg = Number(fuel.internal_kg || 2500.0);
    const n_max = Number(struct.design_load_factor_g || 7.33);

    const eng = P1.getEngineSpec(eng_id);
    const areaDist = P1.computeAreaRuleDistribution(design);

    // Structural & Empty Mass calculation (sensitive to airfoil internal cross-section area_norm & fuselage volume)
    const eng_mass = Number(eng.mass_kg || 1600.0) * eng_count;
    const sweep_rad = sweep_deg * Math.PI / 180.0;
    const afBoxStiffness = Math.max(0.55, Math.min(1.45, (afEval.area_norm / Math.max(0.02, 0.68 * tc))));
    const wing_mass = 26.5 * Math.pow(S, 1.12) * Math.pow(AR, 0.48) * Math.pow(n_max / 7.33, 0.55) / (Math.pow(Math.max(0.032, tc) * Math.cos(sweep_rad), 0.38) * Math.pow(afBoxStiffness, 0.25));
    const fus_mass = 38.0 * Math.pow(L * D, 1.18) * (struct.carrier_capable ? 1.11 : 1.0);
    const sys_mass = 980.0 + (design.systems && design.systems.radar_id ? 260.0 : 0.0);
    let empty_mass_kg = eng_mass + wing_mass + fus_mass + sys_mass;

    // If baseTemplateStem is known, calibrate baseline empty mass & aero efficiency to Python oracle
    const histMap = (window.MIC_DATA && window.MIC_DATA.aircraft_hist) || {};
    let effectiveStem = baseTemplateStem;
    if (baseTemplateStem === "yf102_pre_area_rule" && area_ruled && histMap["f102a_delta_dagger"]) {
      effectiveStem = "f102a_delta_dagger";
    } else if (baseTemplateStem === "f102a_delta_dagger" && !area_ruled && histMap["yf102_pre_area_rule"]) {
      effectiveStem = "yf102a_pre_area_rule" in histMap ? "yf102a_pre_area_rule" : "yf102_pre_area_rule";
    }
    const histEntry = effectiveStem && histMap[effectiveStem];
    if (histEntry && histEntry.design && histEntry.oracle_perf) {
      const hd = histEntry.design;
      const hp = histEntry.oracle_perf;
      const hS = Number((hd.wing && hd.wing.area_m2) || S);
      const hSweep = Number((hd.wing && hd.wing.sweep_quarter_chord_deg) || sweep_deg);
      const hTc = Number((hd.wing && hd.wing.t_c_root) || tc);
      const hAR = Number((hd.wing && hd.wing.aspect_ratio) || AR);
      const hAreaRuled = Boolean(hd.fuselage && hd.fuselage.area_ruled);
      const hFuel = Number((hd.fuel && hd.fuel.internal_kg) || fuel_kg);
      const hEngId = (hd.propulsion && hd.propulsion.engine_id) || eng_id;
      const hEngCount = Number((hd.propulsion && hd.propulsion.count) || eng_count);
      const hAb = Boolean(hd.propulsion && hd.propulsion.afterburner);

      // Compute exact parametric sensitivity deltas around the Python oracle point!
      const hEng = P1.getEngineSpec(hEngId);
      const thrustRatio = (P1.evalEngineAt(eng, 1.1, 10668, ab).thrust_N * eng_count) /
                          Math.max(1000.0, P1.evalEngineAt(hEng, 1.1, 10668, hAb).thrust_N * hEngCount);

      const dS_ratio = S / Math.max(5.0, hS);
      const dTc = tc - hTc;
      const dSweep = sweep_deg - hSweep;
      const dAR = AR - hAR;
      const dFuel = fuel_kg - hFuel;

      empty_mass_kg = hp.empty_mass_kg * (0.45 + 0.30 * dS_ratio + 0.25 * (eng_mass / Math.max(400.0, Number(hEng.mass_kg || 1500.0) * hEngCount)))
                      * (1.0 - 1.4 * dTc + 0.04 * dAR + 0.0025 * Math.abs(dSweep))
                      * (n_max / Number((hd.structure && hd.structure.design_load_factor_g) || 7.33) * 0.25 + 0.75);

      const mtow_kg = empty_mass_kg + fuel_kg + 680.0;
      const combat_mass_kg = empty_mass_kg + 0.5 * fuel_kg + 450.0;
      const hCombatMass = hp.empty_mass_kg + 0.5 * hFuel + 450.0;
      const massRatio = combat_mass_kg / Math.max(1000.0, hCombatMass);

      // Continuous Area-Rule / Fuselage Sculpting Mach effect + Airfoil Wave-Drag effect
      const baselineWaist = hAreaRuled ? 1.0 : 0.0;
      const currentWaist = areaDist.waist_quality;
      let areaRuleMachDelta = 0.0;
      if (hp.max_mach_alt >= 0.94 || currentWaist > 0.2) {
        areaRuleMachDelta = 0.31 * (currentWaist - baselineWaist);
      }
      // Custom airfoil shape bonus/penalty (e.g. moving x_tc_max aft to 0.45-0.50 & sharp LE helps supersonic Mach; excessive camber hurts supersonic Mach)
      const afShapeMachDelta = -0.18 * (afEval.wave_drag_af_mult - 1.0);
      const clMaxRatio = afEval.cl_max_2d / 1.18;

      const max_mach_alt = Math.max(0.55, Math.min(2.45,
        hp.max_mach_alt * Math.pow(thrustRatio, 0.42) * Math.pow(1.0 / dS_ratio, 0.14)
        + areaRuleMachDelta + afShapeMachDelta - 2.6 * dTc + 0.0045 * dSweep
      ));
      const max_mach_sl = Math.max(0.48, Math.min(1.25,
        hp.max_mach_sl * Math.pow(thrustRatio, 0.32) - 1.4 * dTc + 0.002 * dSweep + 0.35 * (areaRuleMachDelta + afShapeMachDelta)
      ));
      const service_ceiling_m = Math.max(8000.0, Math.min(22000.0,
        hp.service_ceiling_m + 3200.0 * Math.log(Math.max(0.4, thrustRatio / Math.pow(massRatio, 0.7))) + 650.0 * (dS_ratio - 1.0)
      ));
      const climb_rate_sl_mps = Math.max(10.0,
        hp.climb_rate_sl_mps * Math.pow(thrustRatio / massRatio, 1.18) * (1.0 + 0.08 * (areaRuleMachDelta + afShapeMachDelta))
      );
      const sustained_turn_dps_m08_4572m = Math.max(3.5, Math.min(22.0,
        hp.sustained_turn_dps_m08_4572m * Math.pow(dS_ratio / massRatio, 0.52) * Math.pow(thrustRatio, 0.45) * (1.0 + 0.06 * dAR - 0.004 * dSweep) * Math.pow(clMaxRatio, 0.35)
      ));
      const instantaneous_turn_dps_m08_4572m = Math.max(sustained_turn_dps_m08_4572m + 2.5,
        hp.instantaneous_turn_dps_m08_4572m * Math.pow(dS_ratio / massRatio, 0.48) * (n_max / 7.33) * Math.pow(clMaxRatio, 0.55)
      );
      const combat_radius_m = Math.max(180000.0,
        hp.combat_radius_m * (fuel_kg / Math.max(400.0, hFuel)) * Math.pow(1.0 / massRatio, 0.55) * (1.0 + 0.12 * areaRuleMachDelta + 0.04 * dAR)
      );
      const stall_speed_mps = hp.stall_speed_mps * Math.sqrt(massRatio / (dS_ratio * Math.max(0.65, clMaxRatio))) * (1.0 + 0.0025 * dSweep);
      const takeoff_distance_m = Math.max(350.0, hp.takeoff_distance_m * Math.pow(massRatio / (dS_ratio * Math.max(0.7, clMaxRatio)), 1.25) / Math.pow(thrustRatio, 0.65));

      const unit_flyaway_cost_usd = Math.round(hp.unit_flyaway_cost_usd * (empty_mass_kg / hp.empty_mass_kg) * (currentWaist > 0.5 && !hAreaRuled ? 1.04 : 1.0));
      const dev_cost_usd_estimate = Math.round(hp.dev_cost_usd_estimate * (empty_mass_kg / hp.empty_mass_kg) * (currentWaist > 0.5 && !hAreaRuled ? 1.08 : 1.0));
      const static_margin = Number((0.065 + 0.0012 * (sweep_deg - 35.0) - 0.02 * (dS_ratio - 1.0) - 0.15 * (afEval.x_tc_max - 0.36)).toFixed(3));

      return {
        max_mach_alt,
        max_mach_sl,
        service_ceiling_m,
        climb_rate_sl_mps,
        sustained_turn_dps_m08_4572m,
        instantaneous_turn_dps_m08_4572m,
        combat_radius_m,
        ferry_range_m: combat_radius_m * 2.45,
        takeoff_distance_m,
        stall_speed_mps,
        empty_mass_kg,
        mtow_kg,
        internal_fuel_kg: fuel_kg,
        unit_flyaway_cost_usd,
        dev_cost_usd_estimate,
        static_margin,
        areaDist,
        airfoilEval: afEval,
        computeDragAtMach: (m) => computeDragPolarAtMach(design, m, areaDist, afEval),
      };
    }

    // Fallback pure parametric physics if no historical template anchor
    const mtow_kg = empty_mass_kg + fuel_kg + 680.0;
    const thr_alt = P1.evalEngineAt(eng, 1.2, 10668, ab).thrust_N * eng_count;
    const tw = thr_alt / (mtow_kg * P1.G0);
    const dp1 = computeDragPolarAtMach(design, 1.05, areaDist, afEval);
    const max_mach_alt = Math.max(0.65, Math.min(2.35, 0.78 + 1.15 * Math.sqrt(tw / Math.max(0.015, dp1.cd0))));
    return {
      max_mach_alt,
      max_mach_sl: Math.min(1.15, max_mach_alt * 0.78),
      service_ceiling_m: 12500.0 + 4500.0 * tw,
      climb_rate_sl_mps: 35.0 + 95.0 * tw,
      sustained_turn_dps_m08_4572m: 9.5 * (afEval.cl_max_2d / 1.18),
      instantaneous_turn_dps_m08_4572m: 15.0 * (afEval.cl_max_2d / 1.18),
      combat_radius_m: 650000.0 * (fuel_kg / 2500.0),
      ferry_range_m: 1600000.0,
      takeoff_distance_m: 950.0,
      stall_speed_mps: 62.0 / Math.sqrt(Math.max(0.65, afEval.cl_max_2d / 1.18)),
      empty_mass_kg,
      mtow_kg,
      internal_fuel_kg: fuel_kg,
      unit_flyaway_cost_usd: Math.round(empty_mass_kg * 115.0),
      dev_cost_usd_estimate: Math.round(empty_mass_kg * 3800.0),
      static_margin: 0.06,
      areaDist,
      airfoilEval: afEval,
      computeDragAtMach: (m) => computeDragPolarAtMach(design, m, areaDist, afEval),
    };
  }

  window.MIC_KERNEL = Object.assign({}, P1, {
    computeDragPolarAtMach,
    evaluateAircraftPerformance,
  });
})();

(function () {
  "use strict";
  const K = window.MIC_KERNEL;

  // Synthesize hidden aerodynamic/structural/propulsion flaws for an aircraft design
  // Implements Locked Decision D7 (Era Fog-of-War: "Uncharted High-Speed Regime Risk" before known_from_year)
  function generateFlawsForDesign(design, perf, year, hindsight) {
    const wing = design.wing || {};
    const fus = design.fuselage || {};
    const prop = design.propulsion || {};
    const emp = design.empennage || {};
    const sweep = Number(wing.sweep_quarter_chord_deg || 35.0);
    const tc = (perf && perf.airfoilEval) ? perf.airfoilEval.tc_max : Number(wing.t_c_root || 0.08);
    const ar = Number(wing.aspect_ratio || 3.5);
    const area_ruled = Boolean(fus.area_ruled) || Boolean(perf && perf.areaDist && perf.areaDist.r_area <= 1.18);
    const t_tail = Boolean(emp.t_tail);
    const mach = perf.max_mach_alt;

    const raw = [];
    if (mach >= 0.96 && !area_ruled) {
      raw.push({
        id: "flaw_transonic_wave_wall",
        true_title_zh: "跨音速截面积突变激波阻力墙 (Transonic Wave-Drag Spike)",
        true_desc_zh: "机翼与机身最大截面重合导致 d²A/dx² 剧烈突变，跨音速波阻暴增，无法突破音障。",
        known_from_year: 1953,
        severity: 4,
        detect_tunnel: { 1: 0.25, 2: 0.90, 3: 0.95 },
        detect_flight: { 1: 0.0, 2: 0.20, 3: 0.95, 4: 0.95 },
        fix_cost_usd: 1850000,
        fix_days: 45,
        fix_action_zh: "应用惠特科姆面积律修形（可口可乐瓶蜂腰机身）",
        triggers_area_rule: true,
        penalty: {
          max_mach_alt: -0.22,
          combat_radius_m: -85000,
          climb_rate_sl_mps: -11.0,
        },
      });
    }
    if (sweep >= 40.0 || t_tail) {
      raw.push({
        id: "flaw_pitch_up_inertial_coupling",
        true_title_zh: "大迎角上仰发散与滚转惯性耦合 (“佩刀舞” Sabre-Dance / Pitch-Up)",
        true_desc_zh: "大后掠翼翼尖先失速导致气动中心前移，高速滚转时引发致命俯仰-偏航惯性耦合。",
        known_from_year: 1954,
        severity: 4,
        detect_tunnel: { 1: 0.30, 2: 0.72, 3: 0.85 },
        detect_flight: { 1: 0.08, 2: 0.35, 3: 0.68, 4: 0.94 },
        fix_cost_usd: 1200000,
        fix_days: 30,
        fix_action_zh: "加装翼刀/前缘锯齿并扩大垂尾面积，升级全动平尾不可逆助力器",
        triggers_area_rule: false,
        penalty: {
          sustained_turn_dps_m08_4572m: -1.85,
          max_mach_alt: -0.05,
        },
      });
    }
    if (tc <= 0.068 && ar >= 3.0) {
      raw.push({
        id: "flaw_aileron_reversal_flutter",
        true_title_zh: "跨音速副翼反效与气动弹性颤振 (Transonic Aileron Reversal & Flutter)",
        true_desc_zh: "薄机翼在高动压下扭转刚度不足，副翼偏转反而引起机翼反向扭转。",
        known_from_year: 1951,
        severity: 3,
        detect_tunnel: { 1: 0.22, 2: 0.78, 3: 0.88 },
        detect_flight: { 1: 0.0, 2: 0.42, 3: 0.88, 4: 0.92 },
        fix_cost_usd: 850000,
        fix_days: 22,
        fix_action_zh: "加厚蒙皮扭力盒并改用内侧高速副翼/扰流板",
        triggers_area_rule: false,
        penalty: {
          max_mach_alt: -0.09,
          sustained_turn_dps_m08_4572m: -0.95,
        },
      });
    }
    if (prop.afterburner) {
      raw.push({
        id: "flaw_ab_screech_inlet_buzz",
        true_title_zh: "高空加力燃烧室高频振荡与进气道喘振 (Afterburner Screech & Buzz)",
        true_desc_zh: "45,000 英尺以上开加力时发生声学共振与激波吞吐，导致高空熄火。",
        known_from_year: 1952,
        severity: 2,
        detect_tunnel: { 1: 0.15, 2: 0.55, 3: 0.82 },
        detect_flight: { 1: 0.20, 2: 0.76, 3: 0.88, 4: 0.90 },
        fix_cost_usd: 480000,
        fix_days: 14,
        fix_action_zh: "加装加力隔热防振衬套与进气道附面层放气门",
        triggers_area_rule: false,
        penalty: {
          service_ceiling_m: -1150,
          combat_radius_m: -45000,
        },
      });
    }

    return raw.map(function (fl) {
      const uncharted = (year < fl.known_from_year) && !hindsight;
      return Object.assign({}, fl, {
        uncharted_before_discovery: uncharted,
        discovered: false,
        discovered_by: null,
        fixed: false,
      });
    });
  }

  // Compute True Performance (including unfixed flaws) & Player Estimate { value, sigma, source }
  function computeEstimates(basePerf, flaws, sigmaMult, sourceBadge) {
    const truePerf = Object.assign({}, basePerf);
    flaws.forEach(function (fl) {
      if (!fl.fixed) {
        Object.keys(fl.penalty).forEach(function (k) {
          if (typeof truePerf[k] === "number") {
            truePerf[k] = Math.max(0.1, truePerf[k] + fl.penalty[k]);
          }
        });
      }
    });

    const baseSigmas = {
      max_mach_alt: 0.08,
      max_mach_sl: 0.05,
      service_ceiling_m: 780.0,
      climb_rate_sl_mps: 6.5,
      combat_radius_m: 56000.0,
      sustained_turn_dps_m08_4572m: 0.85,
      instantaneous_turn_dps_m08_4572m: 1.10,
      takeoff_distance_m: 95.0,
      stall_speed_mps: 3.5,
      unit_flyaway_cost_usd: 58000.0,
    };

    const estimates = {};
    Object.keys(baseSigmas).forEach(function (k) {
      const baseVal = Number(basePerf[k] || 0);
      let knownDelta = 0.0;
      flaws.forEach(function (fl) {
        if (fl.discovered && !fl.fixed && fl.penalty[k]) {
          knownDelta += fl.penalty[k];
        }
      });
      estimates[k] = {
        value: Math.max(0.1, baseVal + knownDelta),
        sigma: baseSigmas[k] * sigmaMult,
        source: sourceBadge,
      };
    });

    return { truePerf, estimates };
  }

  // Named Engine Vendor Custom Commissioning Quotes (Locked Decision D9)
  const ENGINE_VENDORS = [
    {
      id: "pratt_whitney",
      name: "Pratt & Whitney (普惠 — 东哈特福德)",
      specialty_zh: "双转子轴流技术领袖 (J57/J75)：发动机大修间隔 (MTBF) +25%，油耗 -4%，研发报价略高 (+10%)",
      cost_mult: 1.10,
      months_mult: 1.00,
      tsfc_mult: 0.96,
      mass_mult: 1.02,
      risk_pct: 12,
    },
    {
      id: "general_electric",
      name: "General Electric (通用电气 — 埃文代尔)",
      specialty_zh: "可变静子叶片与高马赫加力专家 (J47/J79)：推重比 +12%，M2.0 冲压推力优异，研发周期 -10%",
      cost_mult: 1.05,
      months_mult: 0.90,
      tsfc_mult: 0.99,
      mass_mult: 0.89,
      risk_pct: 14,
    },
    {
      id: "allison",
      name: "Allison Division of GM (艾里逊 — 印第安纳波利斯)",
      specialty_zh: "通用汽车雄厚量产底蕴 (J33/J35/J71)：单台出厂价 -12%，研发费用 -15%，极限推重比中规中矩",
      cost_mult: 0.85,
      months_mult: 0.95,
      tsfc_mult: 1.01,
      mass_mult: 1.04,
      risk_pct: 16,
    },
    {
      id: "curtiss_wright",
      name: "Curtiss-Wright (柯蒂斯-赖特 — 伍德-里奇)",
      specialty_zh: "英国许可证改型快枪手 (J65 Sapphire)：早期现货快 (-20% 周期)，但自主跨代核心机风险偏高 (26%)",
      cost_mult: 0.92,
      months_mult: 0.80,
      tsfc_mult: 1.02,
      mass_mult: 1.00,
      risk_pct: 26,
    },
    {
      id: "westinghouse",
      name: "Westinghouse Aviation Gas Turbine (西屋电气 — 费城)",
      specialty_zh: "早期小迎风面积先驱 (J34/J40)：机身迎风直径小，但高推力型号存在严重进度拖延风险 (38% — 谨防 J40 悲剧!)",
      cost_mult: 0.88,
      months_mult: 1.22,
      tsfc_mult: 1.05,
      mass_mult: 0.95,
      risk_pct: 38,
    },
  ];

  function quoteCustomEngines(thrustDryKn, abEnabled, opr, year) {
    const baseNreUsd = (3.8 + 0.095 * thrustDryKn * (abEnabled ? 1.32 : 1.0) * (opr / 7.0)) * 1e6;
    const baseMonths = Math.round(16 + (thrustDryKn / 12.0) + (abEnabled ? 4 : 0) + Math.max(0, (opr - 8) * 1.5));
    return ENGINE_VENDORS.map(function (v) {
      return {
        vendor: v,
        nre_cost_usd: Math.round(baseNreUsd * v.cost_mult),
        dev_months: Math.round(baseMonths * v.months_mult),
        unit_cost_usd: Math.round((48000 + thrustDryKn * 1450 * (abEnabled ? 1.25 : 1.0)) * v.cost_mult),
        est_mass_kg: Math.round((620 + thrustDryKn * 21.5 * (abEnabled ? 1.18 : 1.0)) * v.mass_mult),
        tsfc_dry: Number((0.0000255 * v.tsfc_mult * Math.pow(7.0 / Math.max(4.0, opr), 0.18)).toFixed(7)),
        failure_risk_pct: v.risk_pct,
      };
    });
  }

  window.MIC_KERNEL = Object.assign(window.MIC_KERNEL, {
    generateFlawsForDesign,
    computeEstimates,
    ENGINE_VENDORS,
    quoteCustomEngines,
  });
})();
