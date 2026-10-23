// ============================================================================
// MIC: Jet Age — Interactive Web Prototype Application Controller (app.js)
// ============================================================================

(function () {
  "use strict";

  const K = window.MIC_KERNEL;
  const P = window.MIC_PLOTS;
  const DATA = window.MIC_DATA || {};

  // Curated Iconic Showdown Scenarios for 1-Click Playtesting
  const SHOWDOWN_SCENARIOS = {
    "1952_interceptor": {
      id: "1952_interceptor",
      year: 1952,
      date_str: "1952-09-15",
      title_zh: "1952 美国空军 WS-201A 超音速截击机真机竞飞 (YF-102 音障危机 vs F-102A 面积律突破)",
      customer: "USAF",
      desc_zh: "1952 年康维尔 YF-102 三角翼原型机在试飞中卡在 M 1.03 无法突破音障！请通过【开槽跨音速风洞】定位激波元凶，开启【惠特科姆面积律蜂腰修形 (F-102A)】，并在爱德华兹空军基地击败北美 F-100A 与洛克希德 CL-246！",
      default_template: "yf102_pre_area_rule",
      unit_price_ceiling_usd: 1450000,
      flyoff_days_budget: 560,
      quantity_planned: 650,
      weights: { perf: 0.45, cost: 0.20, sched: 0.15, risk: 0.20 },
      thresholds: {
        max_mach_alt: 1.25,
        service_ceiling_m: 15240,
        climb_rate_sl_mps: 65.0,
        combat_radius_m: 600000,
        sustained_turn_dps_m08_4572m: 8.5,
      },
      objectives: {
        max_mach_alt: 1.40,
        service_ceiling_m: 16200,
        climb_rate_sl_mps: 82.0,
        combat_radius_m: 880000,
        sustained_turn_dps_m08_4572m: 10.2,
      },
      rivals: [
        { company: "Republic Aviation", designation: "AP-63 (F-101A Voodoo)", config_zh: "双发重型远程截击机 (造价与工期超标)", stem: "f101a_voodoo", price_usd: 1440000, sched_days: 590, risk_score: 74, pol_score: 69 },
        { company: "Lockheed Skunk Works", designation: "CL-246 (XF-104)", config_zh: "超薄梯形短翼高速截击机 (作战半径不足)", stem: "f104a_starfighter", price_usd: 1210000, sched_days: 545, risk_score: 73, pol_score: 72 },
        { company: "Northrop Aircraft", designation: "F-89H Twin-Scorpion", config_zh: "平直翼双发全天候截击机 (无法超音速)", stem: "f89d_scorpion", price_usd: 1090000, sched_days: 470, risk_score: 88, pol_score: 75 },
      ],
    },
    "1946_day_fighter": {
      id: "1946_day_fighter",
      year: 1946,
      date_str: "1946-05-10",
      title_zh: "1946 美国陆航昼间喷气战斗机竞标 (P-80 平直翼 vs XP-86 35°后掠翼革命)",
      customer: "USAF",
      desc_zh: "二战刚结束，德国风洞档案揭示了 35° 后掠翼推迟临界马赫数的奥秘。将平直翼改为 35° 后掠翼并配备前缘缝翼，冲击高亚音速狗斗王座！",
      default_template: "f86a_sabre",
      unit_price_ceiling_usd: 340000,
      flyoff_days_budget: 480,
      quantity_planned: 1100,
      weights: { perf: 0.45, cost: 0.25, sched: 0.15, risk: 0.15 },
      thresholds: {
        max_mach_alt: 0.86,
        service_ceiling_m: 12500,
        climb_rate_sl_mps: 32.0,
        combat_radius_m: 520000,
        sustained_turn_dps_m08_4572m: 9.0,
      },
      objectives: {
        max_mach_alt: 0.93,
        service_ceiling_m: 14800,
        climb_rate_sl_mps: 46.0,
        combat_radius_m: 720000,
        sustained_turn_dps_m08_4572m: 12.0,
      },
      rivals: [
        { company: "Lockheed Aircraft", designation: "P-80B Shooting Star", config_zh: "平直翼 + J33 离心式涡喷", stem: "p80a_shooting_star", price_usd: 210000, sched_days: 410, risk_score: 90, pol_score: 76 },
        { company: "Republic Aviation", designation: "XP-84 Thunderjet", config_zh: "平直厚翼 + J35 轴流涡喷", stem: "f84g_thunderjet", price_usd: 265000, sched_days: 450, risk_score: 83, pol_score: 74 },
      ],
    },
    "1953_usn_carrier": {
      id: "1953_usn_carrier",
      year: 1953,
      date_str: "1953-06-01",
      title_zh: "1953 美国海军舰载超音速制空战斗机竞标 (F8U-1 十字军战士 vs F4D-1 天光)",
      customer: "USN",
      desc_zh: "美国海军航空局 (BuAer) 要求舰载机突破 M 1.45，同时着舰失速速度严格受航母甲板限制！平衡机翼面积、后掠角与发动机推力。",
      default_template: "f8u1_crusader",
      unit_price_ceiling_usd: 1180000,
      flyoff_days_budget: 540,
      quantity_planned: 520,
      weights: { perf: 0.45, cost: 0.20, sched: 0.15, risk: 0.20 },
      thresholds: {
        max_mach_alt: 1.40,
        service_ceiling_m: 15500,
        climb_rate_sl_mps: 85.0,
        combat_radius_m: 620000,
        sustained_turn_dps_m08_4572m: 9.5,
      },
      objectives: {
        max_mach_alt: 1.70,
        service_ceiling_m: 17200,
        climb_rate_sl_mps: 115.0,
        combat_radius_m: 880000,
        sustained_turn_dps_m08_4572m: 12.2,
      },
      rivals: [
        { company: "Douglas Aircraft", designation: "F4D-1 Skyray", config_zh: "无尾翼蝙蝠三角翼舰载截击机", stem: "f4d1_skyray", price_usd: 860000, sched_days: 480, risk_score: 85, pol_score: 80 },
        { company: "North American Aviation", designation: "FJ-4B Supersonic Fury", config_zh: "舰载改进型超佩刀", stem: "f100a_super_sabre", price_usd: 950000, sched_days: 490, risk_score: 84, pol_score: 72 },
      ],
    },
    "1955_mach2_showdown": {
      id: "1955_mach2_showdown",
      year: 1955,
      date_str: "1955-04-15",
      title_zh: "1955 双倍音速制空与截击巅峰决战 (F-104A 星式战斗机 vs F-105B 雷公)",
      customer: "USAF",
      desc_zh: "通用电气 J79 可变静子涡喷问世，人类迈入 Mach 2.0 时代！测试超薄机翼 (t/c = 3.4%) 与面积律修形在 2 倍音速下的终极气动包线。",
      default_template: "f104a_starfighter",
      unit_price_ceiling_usd: 1450000,
      flyoff_days_budget: 560,
      quantity_planned: 750,
      weights: { perf: 0.50, cost: 0.18, sched: 0.14, risk: 0.18 },
      thresholds: {
        max_mach_alt: 1.85,
        service_ceiling_m: 16800,
        climb_rate_sl_mps: 115.0,
        combat_radius_m: 500000,
        sustained_turn_dps_m08_4572m: 8.8,
      },
      objectives: {
        max_mach_alt: 2.15,
        service_ceiling_m: 18500,
        climb_rate_sl_mps: 145.0,
        combat_radius_m: 780000,
        sustained_turn_dps_m08_4572m: 11.5,
      },
      rivals: [
        { company: "Chance Vought", designation: "XF8U-2 Crusader II", config_zh: "高推力 J57/J75 超音速战斗机", stem: "f8u1_crusader", price_usd: 1080000, sched_days: 510, risk_score: 86, pol_score: 75 },
        { company: "Republic Aviation", designation: "YF-105B Thunderchief", config_zh: "J75 重型超音速战斗轰炸机", stem: "f105b_thunderchief", price_usd: 1380000, sched_days: 550, risk_score: 80, pol_score: 77 },
      ],
    },
  };

  const PILOTS = [
    { id: "vance", name: "Maj. Chuck 'Brick' Vance (前穆罗克王牌试飞员)", skill: 0.92, caution: 0.58, flaw_bonus: 0.22, crash_red: 0.25, cost_usd: 45000, desc_zh: "缺陷发现率 +22%，坠机风险 -25%，擅长跨音速俯冲包线扩展。" },
    { id: "mercer", name: "Capt. Hal 'Slide-Rule' Mercer (NACA 工程试飞员)", skill: 0.88, caution: 0.88, flaw_bonus: 0.35, crash_red: 0.45, cost_usd: 55000, desc_zh: "NACA 气动学者型试飞员：缺陷发现率 +35%，坠机风险 -45%，每阶段耗时 +12 天。" },
    { id: "callahan", name: "Lt. Walt 'Hotshoe' Callahan (朝鲜战争喷气王牌)", skill: 0.80, caution: 0.32, flaw_bonus: 0.08, crash_red: 0.0, cost_usd: 25000, desc_zh: "大胆激进：每阶段进度快 10 天，费用低，但未修高危缺陷时易引发试飞事故！" },
  ];

  // Global Reactive Application State
  const STATE = {
    activeWorkspace: "design", // design | testing | procurement | propulsion | tech | company
    activeCanvasTab: "airfoil", // airfoil | area_rule | 3view | ps_contour | drag_polar
    airfoilBrushMode: "nodes",  // nodes | free_upper | free_lower
    scenarioId: "1952_interceptor",
    templateStem: "yf102_pre_area_rule",
    design: null,
    perf: null,
    flaws: [],
    sigmaMult: 1.0,
    sourceBadge: "SIM (纸面计算器估值)",
    tunnelLevelRun: 0,
    flightPhaseRun: 0,
    selectedPilotIdx: 1,
    hindsightMode: false,      // Locked Decision D7 toggle
    forceFlyoffMode: true,     // Locked Decision D6 toggle
    inquiryLevel: 0,           // Locked Decision D10 (0=Free Trade Rumors, 1=Liaison, 2=Deep Recon)
    bidPriceUsd: 980000,
    contractType: "FPIF",
    schedDays: 470,
    companyCashUsd: 24500000,
    repUSAF: 74,
    repUSN: 68,
    polCapital: 52,
    contractsWon: 1,
    flyoffResults: null,
    eventLog: [],
    customEngines: [],
    sandboxPost1960: false,
  };

  window.MIC_APP_PART1 = {
    SHOWDOWN_SCENARIOS,
    PILOTS,
    STATE,
    DATA,
  };
})();

(function () {
  "use strict";
  const A1 = window.MIC_APP_PART1;
  const K = window.MIC_KERNEL;
  const P = window.MIC_PLOTS;
  const STATE = A1.STATE;

  function logEvent(dateStr, category, textZh) {
    STATE.eventLog.unshift({
      date: dateStr || A1.SHOWDOWN_SCENARIOS[STATE.scenarioId].date_str,
      cat: category,
      text: textZh,
    });
    if (STATE.eventLog.length > 30) STATE.eventLog.pop();
    STATE.unreadEvents = (STATE.unreadEvents || 0) + 1;
    if (typeof showToast === "function" && STATE.booted) showToast(category, textZh);
  }

  function loadTemplate(stem, keepScenario) {
    const hist = (A1.DATA.aircraft_hist && A1.DATA.aircraft_hist[stem]) || null;
    if (!hist) return;
    STATE.templateStem = stem;
    STATE.design = JSON.parse(JSON.stringify(hist.design));
    K.ensureCustomAirfoil(STATE.design);
    K.ensureFuselageStations(STATE.design);
    recalculateDesign(true);
    if (!keepScenario) {
      logEvent(null, "DESIGN", `已载入机体气动模板：【${STATE.design.name || stem}】`);
    }
  }

  function loadScenario(scenId) {
    const scen = A1.SHOWDOWN_SCENARIOS[scenId];
    if (!scen) return;
    STATE.scenarioId = scenId;
    STATE.inquiryLevel = 0;
    STATE.flyoffResults = null;
    loadTemplate(scen.default_template, true);
    STATE.bidPriceUsd = Math.round(STATE.perf.unit_flyaway_cost_usd * 1.08);
    STATE.schedDays = Math.round(scen.flyoff_days_budget * 0.86);
    logEvent(scen.date_str, "RFP", `五角大楼发布招标书：【${scen.title_zh}】`);
    renderAll();
  }

  function recalculateDesign(resetTests) {
    const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
    STATE.perf = K.evaluateAircraftPerformance(STATE.design, STATE.templateStem);
    if (resetTests) {
      STATE.tunnelLevelRun = 0;
      STATE.flightPhaseRun = 0;
      STATE.sigmaMult = 1.0;
      STATE.sourceBadge = "SIM (纸面计算尺估值)";
      STATE.flaws = K.generateFlawsForDesign(STATE.design, STATE.perf, scen.year, STATE.hindsightMode);
    } else {
      // Re-evaluate flaws while preserving already-discovered/fixed status where applicable
      const newFlaws = K.generateFlawsForDesign(STATE.design, STATE.perf, scen.year, STATE.hindsightMode);
      newFlaws.forEach(function (nf) {
        const old = STATE.flaws.find((f) => f.id === nf.id);
        if (old) {
          nf.discovered = old.discovered;
          nf.discovered_by = old.discovered_by;
          nf.fixed = old.fixed;
        }
      });
      STATE.flaws = newFlaws;
    }
  }

  function runWindTunnel(level) {
    const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
    const costs = { 1: 180000, 2: 450000, 3: 780000 };
    const days = { 1: 18, 2: 30, 3: 42 };
    const names = {
      1: "L1 低速亚音速风洞 (Low-Speed Subsonic Tunnel)",
      2: "L2 NACA 开槽喉道跨音速风洞 (Slotted-Throat Transonic Tunnel)",
      3: "L3 超音速吹气式风洞与颤振台 (Supersonic Blowdown Tunnel)",
    };
    const cost = costs[level] || 300000;
    STATE.companyCashUsd -= cost;
    STATE.schedDays += Math.round((days[level] || 20) * 0.45);
    STATE.tunnelLevelRun = Math.max(STATE.tunnelLevelRun, level);
    STATE.sigmaMult = Math.min(STATE.sigmaMult, level === 1 ? 0.58 : level === 2 ? 0.34 : 0.22);
    STATE.sourceBadge = level >= 2 ? "TUNNEL (NACA 开槽跨音速风洞)" : "TUNNEL (低速风洞)";

    let foundCount = 0;
    STATE.flaws.forEach(function (fl) {
      if (!fl.discovered && !fl.fixed) {
        const p = (fl.detect_tunnel && fl.detect_tunnel[level]) || 0.25;
        if (p >= 0.50 || (level >= 2 && p >= 0.30)) {
          fl.discovered = true;
          fl.discovered_by = names[level];
          foundCount++;
          logEvent(scen.date_str, "FLAW", `风洞试验发现重大隐患：【${fl.true_title_zh}】(严重度 S${fl.severity})`);
        }
      }
    });
    if (foundCount === 0) {
      logEvent(scen.date_str, "TUNNEL", `完成 ${names[level]}，性能误差棒 ±1σ 大幅收窄！`);
    }
    renderAll();
  }

  function runFlightTestPhase(phase) {
    const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
    const pilot = A1.PILOTS[STATE.selectedPilotIdx] || A1.PILOTS[0];
    const phaseNames = {
      1: "阶段 1：滑跑与首飞包线验证 (Taxi & First Flight)",
      2: "阶段 2：高亚音速机动与稳定性试飞 (Subsonic Envelope)",
      3: "阶段 3：跨音速/超音速俯冲穿音障试飞 (Transonic/Supersonic Dive)",
      4: "阶段 4：极限过载与武器火控打靶试飞 (High-G & Weapons)",
    };
    STATE.companyCashUsd -= (320000 + pilot.cost_usd);
    STATE.schedDays += (phase === 3 || phase === 4 ? 22 : 14);
    STATE.flightPhaseRun = Math.max(STATE.flightPhaseRun, phase);
    STATE.sigmaMult = Math.min(STATE.sigmaMult, Math.max(0.08, 0.32 - 0.06 * phase));
    STATE.sourceBadge = `FLIGHT (爱德华兹试飞 P1–P${STATE.flightPhaseRun})`;

    STATE.flaws.forEach(function (fl) {
      if (!fl.discovered && !fl.fixed) {
        const baseP = (fl.detect_flight && fl.detect_flight[phase]) || 0.15;
        if (baseP + pilot.flaw_bonus >= 0.48) {
          fl.discovered = true;
          fl.discovered_by = `${pilot.name.split(" ")[1]} @ ${phaseNames[phase]}`;
          logEvent(scen.date_str, "FLIGHT", `试飞员报告重大气动/结构问题：【${fl.true_title_zh}】`);
        }
      }
    });
    logEvent(scen.date_str, "FLIGHT", `试飞员 ${pilot.name} 完成 ${phaseNames[phase]}，实测数据收敛！`);
    renderAll();
  }

  function fixFlaw(flawId) {
    const fl = STATE.flaws.find((f) => f.id === flawId);
    if (!fl || fl.fixed) return;
    STATE.companyCashUsd -= fl.fix_cost_usd;
    STATE.schedDays += Math.round(fl.fix_days * 0.65);
    fl.fixed = true;
    fl.discovered = true;
    if (fl.triggers_area_rule) {
      STATE.design.fuselage = STATE.design.fuselage || {};
      STATE.design.fuselage.area_ruled = true;
      STATE.design.fuselage.station_radii = K.buildDefaultFuselageRadii(
        STATE.design,
        true,
        K.getMinClearanceRadii(STATE.design)
      );
      if (STATE.templateStem === "yf102_pre_area_rule" && STATE.design.fuel && STATE.design.fuel.internal_kg < 3200) {
        STATE.design.fuel.internal_kg = 3340;
      }
      STATE.perf = K.evaluateAircraftPerformance(STATE.design, STATE.templateStem);
      logEvent(null, "FIX", `完成【惠特科姆面积律蜂腰修形 + 机身加长扩容】！跨音速波阻降低 45%，极速跃升至 M ${STATE.perf.max_mach_alt.toFixed(2)}，作战半径达 ${(STATE.perf.combat_radius_m / 1852).toFixed(0)} nmi！`);
    } else {
      logEvent(null, "FIX", `已投入 $${(fl.fix_cost_usd / 1e3).toFixed(0)}k 完成缺陷整改：【${fl.true_title_zh}】`);
    }
    renderAll();
  }

  function scoreSingleContender(perf, priceUsd, schedDays, riskScore, polScore, scen) {
    const th = scen.thresholds;
    const ob = scen.objectives;
    const mWeights = {
      max_mach_alt: 0.35,
      service_ceiling_m: 0.20,
      climb_rate_sl_mps: 0.15,
      combat_radius_m: 0.15,
      sustained_turn_dps_m08_4572m: 0.15,
    };
    let sPerf = 0.0;
    const misses = [];
    Object.keys(mWeights).forEach(function (k) {
      const v = Number(perf[k] || 0);
      const t = th[k];
      const o = ob[k];
      let pts = 0;
      if (v < t) {
        pts = 55.0 * Math.pow(Math.max(0, v / Math.max(1e-5, t)), 2.5);
        misses.push(k);
      } else if (v >= o) {
        pts = Math.min(108.0, 100.0 + 15.0 * ((v - o) / Math.max(1e-5, o - t)));
      } else {
        pts = 60.0 + 40.0 * ((v - t) / Math.max(1e-5, o - t));
      }
      sPerf += mWeights[k] * pts;
    });

    const priceRatio = priceUsd / scen.unit_price_ceiling_usd;
    const sCost = Math.max(15.0, Math.min(100.0, 100.0 - 75.0 * Math.max(0.0, priceRatio - 0.72)));
    const schedRatio = schedDays / scen.flyoff_days_budget;
    const sSched = Math.max(20.0, Math.min(100.0, 100.0 - 65.0 * Math.max(0.0, schedRatio - 0.80)));
    const sRisk = Math.max(10.0, Math.min(100.0, riskScore));

    const w = scen.weights;
    const baseTot = w.perf * sPerf + w.cost * sCost + w.sched * sSched + w.risk * sRisk;
    const polMod = (polScore - 65.0) * 0.12;
    return {
      S_perf: Number(sPerf.toFixed(1)),
      S_cost: Number(sCost.toFixed(1)),
      S_sched: Number(sSched.toFixed(1)),
      S_risk: Number(sRisk.toFixed(1)),
      S_pol: Number(polScore.toFixed(1)),
      S_total: Number((baseTot + polMod).toFixed(2)),
      misses,
    };
  }

  function runHardwareFlyOff() {
    const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
    const estObj = K.computeEstimates(STATE.perf, STATE.flaws, STATE.sigmaMult, STATE.sourceBadge);
    const truePlayerPerf = estObj.truePerf;
    const unfixedFlaws = STATE.flaws.filter((f) => !f.fixed);
    const playerRisk = Math.max(22, 92 - 20 * unfixedFlaws.length + (STATE.tunnelLevelRun >= 2 ? 5 : -8) + (STATE.flightPhaseRun >= 3 ? 6 : -10));
    const playerPol = scen.customer === "USN" ? STATE.repUSN : STATE.repUSAF;

    const entries = [];
    const pScore = scoreSingleContender(truePlayerPerf, STATE.bidPriceUsd, STATE.schedDays, playerRisk, playerPol, scen);
    entries.push({
      isPlayer: true,
      company: "PLAYER BUREAU (我方原型机)",
      designation: `${STATE.design.name || STATE.templateStem} ${STATE.design.fuselage && STATE.design.fuselage.area_ruled ? "[Area-Ruled]" : ""}`,
      perf: truePlayerPerf,
      price_usd: STATE.bidPriceUsd,
      sched_days: STATE.schedDays,
      unfixedCount: unfixedFlaws.length,
      scores: pScore,
    });

    scen.rivals.forEach(function (rv) {
      const h = A1.DATA.aircraft_hist && A1.DATA.aircraft_hist[rv.stem];
      const rPerf = h ? h.oracle_perf : STATE.perf;
      const sc = scoreSingleContender(rPerf, rv.price_usd, rv.sched_days, rv.risk_score, rv.pol_score, scen);
      entries.push({
        isPlayer: false,
        company: rv.company,
        designation: rv.designation,
        perf: rPerf,
        price_usd: rv.price_usd,
        sched_days: rv.sched_days,
        unfixedCount: 0,
        scores: sc,
      });
    });

    entries.sort((a, b) => b.scores.S_total - a.scores.S_total);
    STATE.flyoffResults = entries;
    if (entries[0].isPlayer) {
      STATE.contractsWon++;
      const profit = Math.round(scen.quantity_planned * STATE.bidPriceUsd * 0.09);
      STATE.companyCashUsd += profit;
      logEvent(scen.date_str, "AWARD", `🏆 我方原型机在真机竞飞中夺冠（总分 ${entries[0].scores.S_total}）！斩获 ${scen.quantity_planned} 架量产合同！`);
    } else {
      logEvent(scen.date_str, "DEBRIEF", `⚠️ 竞飞落败：冠军为 ${entries[0].company} (${entries[0].designation}, ${entries[0].scores.S_total}分)。请查阅评标复盘报告！`);
    }
    STATE.activeWorkspace = "procurement";
    renderAll();
  }

  window.MIC_APP_ACTIONS = {
    logEvent,
    loadTemplate,
    loadScenario,
    recalculateDesign,
    runWindTunnel,
    runFlightTestPhase,
    fixFlaw,
    scoreSingleContender,
    runHardwareFlyOff,
  };
})();

// ---------------------------------------------------------------------------
// Shared UI helpers
// ---------------------------------------------------------------------------
const SCEN_SHORT = {
  "1946_day_fighter": { t1: "昼间喷气战斗机", t2: "P-80 平直翼 vs XP-86 后掠翼" },
  "1952_interceptor": { t1: "WS-201A 超音速截击机", t2: "YF-102 音障危机 · 面积律" },
  "1953_usn_carrier": { t1: "海军超音速舰载机", t2: "F8U-1 vs F4D-1" },
  "1955_mach2_showdown": { t1: "双倍音速制空决战", t2: "F-104A vs F-105B" },
};

const EVENT_TONE = {
  AWARD: "good", FIX: "good", FLIGHT: "warn", FLAW: "bad", DEBRIEF: "bad",
  RFP: "warn", TUNNEL: "", INTEL: "", ENGINE: "", VENDOR: "", AIRFOIL: "", FUSELAGE: "good", DESIGN: "", SANDBOX: "good",
};

function eventBadgeClass(cat) {
  const tone = EVENT_TONE[cat] || "";
  return tone === "good" ? "badge-ok" : tone === "bad" ? "badge-bad" : tone === "warn" ? "badge-sim" : "badge-tunnel";
}

function sourceBadgeClass(STATE) {
  return STATE.flightPhaseRun > 0 ? "badge-flight" : STATE.tunnelLevelRun > 0 ? "badge-tunnel" : "badge-sim";
}

function showToast(cat, text) {
  const host = document.getElementById("toast-host");
  if (!host || !host.appendChild) return;
  const tone = EVENT_TONE[cat] || "";
  const el = document.createElement("div");
  el.className = "toast" + (tone ? " t-" + tone : "");
  el.innerHTML = `<span class="badge ${eventBadgeClass(cat)}">${cat}</span><div>${text}</div>`;
  host.appendChild(el);
  while (host.children.length > 3) host.removeChild(host.firstChild);
  setTimeout(function () { el.classList.add("out"); }, 3800);
  setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 4200);
}

// Keep range-input fill (--pct) in sync with its value
function syncRangeFills(root) {
  if (!root || !root.querySelectorAll) return;
  root.querySelectorAll('input[type="range"]').forEach(function (el) {
    const min = Number(el.min || 0), max = Number(el.max || 100), v = Number(el.value);
    const pct = ((v - min) / Math.max(1e-9, max - min)) * 100;
    el.style.setProperty("--pct", Math.max(0, Math.min(100, pct)).toFixed(1) + "%");
  });
}

function renderTopBarAndRightFeed() {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];

  const setTxt = (id, t) => { const el = document.getElementById(id); if (el) el.textContent = t; };
  setTxt("hud-date", scen.date_str + " · " + scen.customer);
  setTxt("hud-cash", "$" + (STATE.companyCashUsd / 1e6).toFixed(2) + "M");
  setTxt("hud-rep-usaf", STATE.repUSAF + "/100");
  setTxt("hud-rep-usn", STATE.repUSN + "/100");
  setTxt("hud-pol", STATE.polCapital + "/100");
  setTxt("hud-won", STATE.contractsWon + " 项");
  setTxt("hud-feed-count", String(STATE.unreadEvents || 0));
  const cnt = document.getElementById("hud-feed-count");
  if (cnt && cnt.style) cnt.style.display = STATE.unreadEvents ? "" : "none";

  if (document.body && document.body.classList) {
    document.body.classList.toggle("ws-design", STATE.activeWorkspace === "design");
    if (STATE.activeWorkspace !== "design") document.body.classList.remove("feed-open");
  }

  // Scenario cards (active state follows STATE.scenarioId)
  const scenHost = document.getElementById("scenario-buttons");
  if (scenHost) {
    scenHost.innerHTML = Object.keys(A1.SHOWDOWN_SCENARIOS)
      .map((id) => A1.SHOWDOWN_SCENARIOS[id])
      .sort((a, b) => a.year - b.year)
      .map(function (s) {
        const sh = SCEN_SHORT[s.id] || { t1: s.title_zh, t2: "" };
        return `<button class="scen-card ${s.id === STATE.scenarioId ? "active" : ""}" onclick="window.MIC_APP_ACTIONS.loadScenario('${s.id}')" title="${s.title_zh}">
          <span class="yr">${s.year}</span>
          <span><span class="t1">${s.customer} · ${sh.t1}</span><br><span class="t2">${sh.t2}</span></span>
        </button>`;
      }).join("");
  }

  document.querySelectorAll(".nav-btn").forEach(function (btn) {
    btn.classList.toggle("active", btn.getAttribute("data-ws") === STATE.activeWorkspace);
  });

  const feedEl = document.getElementById("right-event-list");
  if (feedEl) {
    const unfixed = STATE.flaws.filter((f) => !f.fixed);
    const uncharted = unfixed.filter((f) => f.uncharted_before_discovery && !f.discovered);
    const knownUnfixed = unfixed.filter((f) => f.discovered || !f.uncharted_before_discovery);

    const statusHtml = `<div class="card accent-brass">
      <div class="card-title"><span class="dot"></span>当前竞标<button class="btn sm ghost feed-close" style="margin-left:auto" onclick="window.MIC_UI.toggleFeed(false)">✕</button></div>
      <div style="font-size:13px;font-weight:600;line-height:1.4;margin-bottom:6px;">${scen.title_zh}</div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:10px;line-height:1.55;">${scen.desc_zh}</div>
      <div class="status-kv"><span>数据来源</span><span class="badge ${sourceBadgeClass(STATE)}">${STATE.sourceBadge}</span></div>
      <div class="status-kv"><span>未知高速风险 (D7)</span><span class="badge ${uncharted.length ? "badge-uncharted" : "badge-muted"}">${uncharted.length} 项潜伏</span></div>
      <div class="status-kv"><span>已暴露待修缺陷</span><span class="badge ${knownUnfixed.length ? "badge-bad" : "badge-ok"}">${knownUnfixed.length} 项</span></div>
      <div class="status-kv"><span>累计工期</span><span class="mono" style="color:${STATE.schedDays > scen.flyoff_days_budget ? "var(--accent-red)" : "var(--text-primary)"}">${STATE.schedDays} / ${scen.flyoff_days_budget} 天</span></div>
    </div>`;

    const logsHtml = STATE.eventLog.length
      ? STATE.eventLog.map(function (ev) {
          return `<div class="feed-item">
            <span class="badge ${eventBadgeClass(ev.cat)}">${ev.cat}</span>
            <span class="when">${ev.date}</span>
            <div class="what">${ev.text}</div>
          </div>`;
        }).join("")
      : `<div class="empty">暂无电报</div>`;

    feedEl.innerHTML = statusHtml + `<div class="card"><div class="card-title">电传日志<span class="eyebrow">Teletype</span></div>${logsHtml}</div>`;
  }
}

  function buildPerfAndDiagHtml() {
    const A1 = window.MIC_APP_PART1;
    const K = window.MIC_KERNEL;
    const STATE = A1.STATE;
    const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
    const d = STATE.design;
    const fus = d.fuselage || {};
    const estObj = K.computeEstimates(STATE.perf, STATE.flaws, STATE.sigmaMult, STATE.sourceBadge);
    const est = estObj.estimates;
    const afEval = STATE.perf.airfoilEval || K.evaluateAirfoilSpline(d);
    const ad = STATE.perf.areaDist;

    const rows = [
      { lbl: "高空最大马赫数", key: "max_mach_alt", scale: 1.0, unit: "M", fmt: 2, pre: true },
      { lbl: "实用升限", key: "service_ceiling_m", scale: K.M_TO_FT, unit: "ft", fmt: 0 },
      { lbl: "海平面爬升率", key: "climb_rate_sl_mps", scale: K.M_TO_FT * 60, unit: "fpm", fmt: 0 },
      { lbl: "作战半径", key: "combat_radius_m", scale: K.M_TO_NMI, unit: "nmi", fmt: 0 },
      { lbl: "M0.8 持续盘旋率", key: "sustained_turn_dps_m08_4572m", scale: 1.0, unit: "°/s", fmt: 1 },
    ];

    // Each metric: value ± σ on a bar scaled to [0.6·threshold, 1.15·objective], with threshold/objective ticks
    const perfRowsHtml = rows.map(function (r) {
      const e = est[r.key];
      const th = scen.thresholds[r.key];
      const ob = scen.objectives[r.key];
      const lo = th * 0.6;
      const hi = ob + (ob - th) * 0.6;
      const pos = (x) => Math.max(0, Math.min(100, ((x - lo) / Math.max(1e-9, hi - lo)) * 100));
      const pass = e.value >= th;
      const great = e.value >= ob;
      const fmtV = (x) => (x * r.scale).toFixed(r.fmt);
      const withUnit = (x) => (r.pre ? `${r.unit} ${fmtV(x)}` : `${fmtV(x)} ${r.unit}`);
      return `<div class="metric">
        <div class="metric-top">
          <span class="metric-name">${r.lbl}</span>
          <span class="metric-val ${pass ? "pass" : "fail"}">${withUnit(e.value)}<span class="sig">±${fmtV(e.sigma)}</span></span>
        </div>
        <div class="mbar">
          <div class="zone-ok" style="left:${pos(th)}%;right:0"></div>
          <div class="fill ${pass ? "pass" : "fail"}" style="width:${pos(e.value)}%"></div>
          <div class="sigma" style="left:${pos(e.value - e.sigma)}%;width:${Math.max(0.8, pos(e.value + e.sigma) - pos(e.value - e.sigma))}%"></div>
          <div class="tick th" style="left:${pos(th)}%" title="门槛 Threshold"></div>
          <div class="tick ob" style="left:${pos(ob)}%" title="目标 Objective"></div>
        </div>
        <div class="metric-foot"><span class="th">门槛 ${withUnit(th)}</span><span>${great ? "★ 超过目标" : pass ? "达标" : "未达门槛"}</span><span class="ob">目标 ${withUnit(ob)}</span></div>
      </div>`;
    }).join("");

    const vitalsHtml = `
      <div class="kpi"><div class="k-lbl">空重 Empty</div><div class="k-val">${STATE.perf.empty_mass_kg.toFixed(0)}<small>kg</small></div></div>
      <div class="kpi"><div class="k-lbl">最大起飞 MTOW</div><div class="k-val">${STATE.perf.mtow_kg.toFixed(0)}<small>kg</small></div></div>
      <div class="kpi"><div class="k-lbl">起飞滑跑</div><div class="k-val">${(STATE.perf.takeoff_distance_m * 3.28084).toFixed(0)}<small>ft</small></div></div>
      <div class="kpi brass"><div class="k-lbl">单机出厂成本</div><div class="k-val">$${(STATE.perf.unit_flyaway_cost_usd / 1e3).toFixed(0)}<small>k</small></div></div>
    `;

    const isSmooth = ad.r_area <= 1.18;
    const sm = STATE.perf.static_margin;
    const diagHtml = `
      <ul class="diag-list">
        <li class="${isSmooth ? "ok" : "warn"}"><div><b>面积律</b> R<sub>area</sub> = <span class="mono" style="color:${isSmooth ? "var(--accent-green)" : "var(--accent-red)"}">${ad.r_area.toFixed(2)}</span> · 蜂腰吻合 ${(ad.waist_quality * 100).toFixed(0)}%<br><span class="muted">${isSmooth ? "截面积分布平滑，跨音速波阻已压低。" : "机翼处截面积突变 → 去「手绘机身」把 S4–S7 往下拉。"}</span></div></li>
        <li class="${afEval.tc_max <= 0.06 ? "ok" : "info"}"><div><b>翼型</b> t/c <span class="mono">${(afEval.tc_max * 100).toFixed(1)}%</span> @${(afEval.x_tc_max * 100).toFixed(0)}%c · 弯度 <span class="mono">${(afEval.camber_max * 100).toFixed(1)}%</span><br><span class="muted">M<sub>dd</sub>(2D) ${afEval.m_dd_2d.toFixed(2)} · C<sub>L,max</sub> ${afEval.cl_max_2d.toFixed(2)}</span></div></li>
        <li class="${sm >= 0.02 ? "ok" : "warn"}"><div><b>静稳定裕度</b> <span class="mono">${(sm * 100).toFixed(1)}%</span> MAC<br><span class="muted">机身容积 ${ad.fus_vol_m3.toFixed(1)} m³ · 研发费 $${(STATE.perf.dev_cost_usd_estimate / 1e6).toFixed(1)}M</span></div></li>
      </ul>
    `;

    return { perfRowsHtml, vitalsHtml, diagHtml };
  }

  function drawActiveDesignCanvas(cvs) {
    if (!cvs) cvs = document.getElementById("design-main-canvas");
    if (!cvs) return;
    const STATE = window.MIC_APP_PART1.STATE;
    const P = window.MIC_PLOTS;
    if (STATE.activeCanvasTab === "airfoil") P.drawAirfoilStudio(cvs, STATE.design, STATE.perf);
    else if (STATE.activeCanvasTab === "3view") P.draw3ViewBlueprint(cvs, STATE.design, STATE.perf);
    else if (STATE.activeCanvasTab === "ps_contour") P.drawPsContourPlot(cvs, STATE.design, STATE.perf);
    else if (STATE.activeCanvasTab === "drag_polar") P.drawDragPolarPlot(cvs, STATE.design, STATE.perf);
    else P.drawAreaRulePlot(cvs, STATE.design, STATE.perf);
  }

  function refreshDesignInPlace() {
    const STATE = window.MIC_APP_PART1.STATE;
    const d = STATE.design;
    const wing = d.wing || {};
    const fus = d.fuselage || {};
    const fuel = d.fuel || {};

    // Update slider readouts without destroying DOM or interrupting pointer drag
    const setTxt = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
    const setVal = (id, val) => { const el = document.getElementById(id); if (el && document.activeElement !== el) el.value = val; };
    setTxt("lbl-area", `${Number(wing.area_m2).toFixed(1)} m² (${(wing.area_m2 * 10.764).toFixed(0)} sq.ft)`);
    setVal("inp-area", wing.area_m2);
    setTxt("lbl-sweep", `${Number(wing.sweep_quarter_chord_deg).toFixed(1)}°`);
    setVal("inp-sweep", wing.sweep_quarter_chord_deg);
    setTxt("lbl-ar", `${Number(wing.aspect_ratio).toFixed(2)}`);
    setVal("inp-ar", wing.aspect_ratio);
    setTxt("lbl-tc", `${(Number(wing.t_c_root) * 100).toFixed(1)}%`);
    setVal("inp-tc", wing.t_c_root);
    setTxt("lbl-fuel", `${Number(fuel.internal_kg).toFixed(0)} kg (${(fuel.internal_kg * 2.2046).toFixed(0)} lb)`);
    setVal("inp-fuel", fuel.internal_kg);
    const arChk = document.getElementById("inp-arearule");
    if (arChk) arChk.checked = Boolean(fus.area_ruled);

    const { perfRowsHtml, vitalsHtml, diagHtml } = buildPerfAndDiagHtml();
    const tbody = document.getElementById("design-perf-tbody");
    if (tbody) tbody.innerHTML = perfRowsHtml;
    const vitals = document.getElementById("design-vital-pills");
    if (vitals) vitals.innerHTML = vitalsHtml;
    const diag = document.getElementById("design-diag-box");
    if (diag) diag.innerHTML = diagHtml;
    syncRangeFills(document);

    drawActiveDesignCanvas();
    renderTopBarAndRightFeed();
  }

  function renderDesignWorkspace(host) {
    const A1 = window.MIC_APP_PART1;
    const STATE = A1.STATE;
    const d = STATE.design;
    const wing = d.wing || {};
    const fus = d.fuselage || {};
    const prop = d.propulsion || {};
    const fuel = d.fuel || {};

    const histKeys = Object.keys(A1.DATA.aircraft_hist || {});
    const templateOpts = histKeys.map(function (k) {
      const item = A1.DATA.aircraft_hist[k];
      const sel = k === STATE.templateStem ? "selected" : "";
      return `<option value="${k}" ${sel}>${item.design.name || k}</option>`;
    }).join("");

    const engKeys = Object.keys(A1.DATA.engines_hist || {});
    const engOpts = engKeys.map(function (ek) {
      const e = A1.DATA.engines_hist[ek];
      const sel = prop.engine_id === ek ? "selected" : "";
      return `<option value="${ek}" ${sel}>${e.name || ek} · ${((e.thrust_ab_sl_N || e.thrust_dry_sl_N || 35000) / 1000).toFixed(1)} kN</option>`;
    }).join("");

    const { perfRowsHtml, vitalsHtml, diagHtml } = buildPerfAndDiagHtml();
    const tab = STATE.activeCanvasTab;
    const tabBtn = (id, icon, label, tag) =>
      `<button class="${tab === id ? "on" : ""}" onclick="window.MIC_UI.setCanvasTab('${id}')">${icon} ${label}<span class="tag">${tag}</span></button>`;

    let toolbarHtml = "";
    if (tab === "airfoil") {
      const bm = STATE.airfoilBrushMode;
      const curPreset = (d.custom_airfoil && d.custom_airfoil.preset_name) || "";
      const preset = (id, label, sub) =>
        `<button class="chip ${curPreset && curPreset.indexOf(label.split(" ")[0]) === 0 ? "on" : ""}" onclick="window.MIC_UI.applyAirfoilPreset('${id}')">${label} <small>${sub}</small></button>`;
      toolbarHtml = `<div class="toolbar">
        <span class="tb-label">画笔</span>
        <button class="chip ${bm === "nodes" ? "on" : ""}" onclick="window.MIC_UI.setAirfoilBrush('nodes')">🎯 控制点</button>
        <button class="chip ${bm === "free_upper" ? "on" : ""}" onclick="window.MIC_UI.setAirfoilBrush('free_upper')">🖌️ 涂抹上翼面</button>
        <button class="chip ${bm === "free_lower" ? "on" : ""}" onclick="window.MIC_UI.setAirfoilBrush('free_lower')">🖌️ 涂抹下翼面</button>
        <span class="tb-sep"></span>
        <span class="tb-label">预设</span>
        ${preset("naca_64a210", "NACA 64A-210", "F-86")}
        ${preset("naca_65a006", "NACA 65A-006", "F-102")}
        ${preset("biconvex_34", "3.4% 双弧", "F-104")}
        ${preset("supercritical_early", "Whitcomb 平顶超临界", "")}
        ${preset("high_camber_navy", "高弯度舰载", "F8U")}
      </div>`;
    } else if (tab === "area_rule" || tab === "3view") {
      toolbarHtml = `<div class="toolbar">
        <span class="tb-label">机身</span>
        <button class="chip go" onclick="window.MIC_UI.sculptFuselagePreset('waist')">✨ 一键蜂腰修形</button>
        <button class="chip" onclick="window.MIC_UI.sculptFuselagePreset('tube')">还原直筒</button>
        <button class="chip" onclick="window.MIC_UI.sculptFuselagePreset('fatten')">加粗 +6%</button>
        <button class="chip" onclick="window.MIC_UI.sculptFuselagePreset('slim')">收窄 −6%</button>
        <span class="hint">${tab === "3view" ? "拖拽翼尖改后掠 / 展长 / 梢弦，拖拽机身节点捏腰" : "拖拽 S0–S10 节点，或按住在轮廓上涂抹；红色虚线为发动机净空"}</span>
      </div>`;
    } else {
      toolbarHtml = `<div class="toolbar"><span class="hint" style="margin-left:0">${tab === "ps_contour" ? "1g 单位剩余功率 Ps(M, h)：青色越亮爬升潜力越大，红色区域无法维持平飞。" : "实线为当前设计的 CD0(M)，琥珀虚线为切换面积律后的反事实对比。"}</span></div>`;
    }

    host.innerHTML = `
      <div class="panel-header">
        <div>
          <div class="panel-title"><span class="step">1</span>飞机设计局 <span class="eyebrow" style="margin-left:4px">Airframe Bureau</span></div>
          <div class="panel-sub">直接在蓝图上手绘翼型、捏合机身蜂腰、拖拽翼尖；右侧性能条实时显示估值、±1σ 误差带与招标门槛/目标。</div>
        </div>
        <div class="panel-actions">
          <button class="btn" onclick="window.MIC_UI.goWorkspace('testing')">风洞与试飞 →</button>
          <button class="btn btn-green" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">提交真机竞飞 →</button>
        </div>
      </div>

      <div class="design-grid">
        <!-- Left: grouped parametric inputs -->
        <div class="card">
          <div class="slider-row" style="margin-bottom:6px;">
            <div class="slider-header"><span>史实基准模板</span></div>
            <select id="inp-template">${templateOpts}</select>
          </div>

          <div class="section-label">✈ 机翼 Wing</div>
          <div class="slider-row">
            <div class="slider-header"><span>参考面积 S</span><span class="s-val" id="lbl-area">${Number(wing.area_m2).toFixed(1)} m²</span></div>
            <input type="range" id="inp-area" min="14" max="68" step="0.5" value="${wing.area_m2}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>1/4 弦线后掠角 Λ</span><span class="s-val" id="lbl-sweep">${Number(wing.sweep_quarter_chord_deg).toFixed(1)}°</span></div>
            <input type="range" id="inp-sweep" min="0" max="60" step="1" value="${wing.sweep_quarter_chord_deg}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>展弦比 AR</span><span class="s-val" id="lbl-ar">${Number(wing.aspect_ratio).toFixed(2)}</span></div>
            <input type="range" id="inp-ar" min="1.8" max="6.5" step="0.05" value="${wing.aspect_ratio}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>翼根厚度比 t/c</span><span class="s-val" id="lbl-tc">${(Number(wing.t_c_root) * 100).toFixed(1)}%</span></div>
            <input type="range" id="inp-tc" min="0.034" max="0.13" step="0.002" value="${wing.t_c_root}">
          </div>

          <div class="section-label">◎ 机身 Fuselage</div>
          <label class="switch-row feature">
            <span class="txt"><b>惠特科姆面积律蜂腰</b><small>自动生成蜂腰；也可在「手绘机身」亲手捏</small></span>
            <input type="checkbox" id="inp-arearule" ${fus.area_ruled ? "checked" : ""}>
          </label>

          <div class="section-label">🔥 推进 Propulsion</div>
          <div class="slider-row" style="margin-bottom:4px;">
            <select id="inp-engine">${engOpts}</select>
          </div>
          <label class="switch-row"><span class="txt">加力燃烧室 Afterburner</span><input type="checkbox" id="inp-ab" ${prop.afterburner ? "checked" : ""}></label>
          <label class="switch-row"><span class="txt">双发构型 Twin engines</span><input type="checkbox" id="inp-twin" ${Number(prop.count) === 2 ? "checked" : ""}></label>

          <div class="section-label">⛽ 燃油 Fuel</div>
          <div class="slider-row" style="margin-bottom:0;">
            <div class="slider-header"><span>机内燃油</span><span class="s-val" id="lbl-fuel">${Number(fuel.internal_kg).toFixed(0)} kg</span></div>
            <input type="range" id="inp-fuel" class="brass" min="800" max="6500" step="50" value="${fuel.internal_kg}">
          </div>
        </div>

        <!-- Center: canvas stage -->
        <div class="card stage">
          <div class="stage-head">
            <div class="seg">
              ${tabBtn("airfoil", "✏️", "手绘翼型", "Airfoil")}
              ${tabBtn("area_rule", "✏️", "手绘机身", "Area rule")}
              ${tabBtn("3view", "✏️", "三视图", "Planform")}
              <span class="sep"></span>
              ${tabBtn("ps_contour", "📈", "能量包线", "Ps")}
              ${tabBtn("drag_polar", "📉", "波阻曲线", "CD0")}
            </div>
            <span class="badge ${sourceBadgeClass(STATE)}">${STATE.sourceBadge}</span>
          </div>
          ${toolbarHtml}
          <canvas id="design-main-canvas" class="blueprint-canvas" style="cursor:crosshair;"></canvas>
          <div id="design-vital-pills" class="grid-4">${vitalsHtml}</div>
        </div>

        <!-- Right: report -->
        <div class="report-col">
          <div class="card">
            <div class="card-title">性能报告<span class="eyebrow">vs RFP · ±1σ</span></div>
            <div id="design-perf-tbody">${perfRowsHtml}</div>
          </div>
          <div class="card">
            <div class="card-title">总师诊断<span class="eyebrow">Diagnostics</span></div>
            <div id="design-diag-box">${diagHtml}</div>
          </div>
        </div>
      </div>
    `;
  }

function renderTestingWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;

  const tunnels = [
    { lv: 1, t: "L1 低速亚音速风洞", d: "起降与低速稳定性", cost: "$180k", days: "+8 天" },
    { lv: 2, t: "L2 NACA 开槽喉道跨音速风洞", d: "★ 揪出跨音速激波阻力墙", cost: "$450k", days: "+14 天", star: true },
    { lv: 3, t: "L3 超音速吹气风洞 + 颤振台", d: "高速副翼反效与颤振", cost: "$780k", days: "+19 天" },
  ];
  const tunnelHtml = tunnels.map((t) => {
    const done = STATE.tunnelLevelRun >= t.lv;
    return `<button class="action-tile ${done ? "done" : t.star ? "star" : ""}" onclick="window.MIC_APP_ACTIONS.runWindTunnel(${t.lv})">
      <span class="ic">${done ? "✓" : "L" + t.lv}</span>
      <span class="body"><span class="t">${t.t}</span><span class="d" style="display:block">${t.d}</span></span>
      <span class="meta"><span class="c-brass">${t.cost}</span><span>${t.days}</span></span>
    </button>`;
  }).join("");

  const phases = [
    { p: 1, t: "滑跑与首飞", d: "First flight" },
    { p: 2, t: "亚音速包线", d: "Subsonic envelope" },
    { p: 3, t: "跨/超音速俯冲", d: "Mach dive", star: true },
    { p: 4, t: "高过载与打靶", d: "High-g & weapons" },
  ];
  const stepperHtml = phases.map((ph) => {
    const done = STATE.flightPhaseRun >= ph.p;
    return `<button class="step-node ${done ? "done" : ""} ${ph.star ? "star" : ""}" onclick="window.MIC_APP_ACTIONS.runFlightTestPhase(${ph.p})">
      <span class="bar"></span>
      <div class="p">${done ? "✓ " : ""}P${ph.p}${ph.star ? " ★" : ""}</div>
      <div class="t">${ph.t}</div>
      <div class="d">${ph.d}</div>
    </button>`;
  }).join("");

  const pilotCards = A1.PILOTS.map(function (p, idx) {
    const sel = idx === STATE.selectedPilotIdx;
    const nick = (p.name.match(/'([^']+)'/) || [])[1] || p.name;
    const initials = nick.split(/[\s-]+/).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
    const fullName = p.name.split("(")[0].trim();
    const role = (p.name.match(/\(([^)]+)\)/) || [])[1] || "";
    const stat = (lbl, v, color) => `<div class="statbar"><span>${lbl}</span><span class="b"><i style="width:${Math.round(v * 100)}%;background:${color}"></i></span><span class="v">${Math.round(v * 100)}</span></div>`;
    return `<div class="card pilot-card ${sel ? "sel" : ""}" onclick="window.MIC_UI.selectPilot(${idx})">
      ${sel ? `<span class="sel-check">✓</span>` : ""}
      <div class="pilot-head"><span class="avatar">${initials}</span><div><div class="pilot-name">${fullName}</div><div class="pilot-role">${role}</div></div></div>
      <div class="pilot-desc">${p.desc_zh}</div>
      ${stat("技术", p.skill, "var(--accent-cyan)")}
      ${stat("谨慎", p.caution, "var(--accent-green)")}
      ${stat("排雷", Math.min(1, p.flaw_bonus / 0.4), "var(--accent-brass)")}
      <div style="margin-top:10px;font-family:var(--font-mono);font-size:11px;color:var(--text-muted)">津贴 <span class="c-brass">$${(p.cost_usd / 1e3).toFixed(0)}k</span> / 阶段</div>
    </div>`;
  }).join("");

  const flawCards = STATE.flaws.map(function (fl) {
    if (!fl.discovered && fl.uncharted_before_discovery) {
      return `<div class="card accent-pink flaw-card">
        <div class="flaw-head"><span class="flaw-title" style="color:#ffc0dc">❓ 未知高速领域风险</span><span class="badge badge-uncharted">D7 · ${fl.known_from_year} 年才被认知</span></div>
        <div class="flaw-desc">你的构型正踏入人类尚未掌握的跨/超音速禁区。只有 <b>L2 跨音速风洞</b> 或 <b>P3 俯冲试飞</b> 才能揭开它的真面目。</div>
      </div>`;
    }
    const sevHtml = `<span class="sev" title="严重度 S${fl.severity}">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= fl.severity ? "on" : ""}"></i>`).join("")}</span>`;
    const status = fl.fixed
      ? `<span class="badge badge-ok">✓ 已修复</span>`
      : fl.discovered ? `<span class="badge badge-bad">已暴露</span>` : `<span class="badge badge-muted">潜伏未检出</span>`;
    return `<div class="card flaw-card ${fl.fixed ? "accent-green" : fl.discovered ? "accent-red" : ""}">
      <div class="flaw-head"><span class="flaw-title">${fl.true_title_zh}</span><span style="display:flex;gap:6px;align-items:center">${sevHtml}${status}</span></div>
      <div class="flaw-desc">${fl.true_desc_zh}</div>
      <div class="fix">
        <span>🔧 ${fl.fix_action_zh}<br><span class="mono muted">$${(fl.fix_cost_usd / 1e3).toFixed(0)}k · +${Math.round(fl.fix_days * 0.65)} 天</span></span>
        ${!fl.fixed ? `<button class="btn btn-green sm" onclick="window.MIC_APP_ACTIONS.fixFlaw('${fl.id}')">立项整改</button>` : ""}
      </div>
    </div>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title"><span class="step">2</span>风洞与试飞 <span class="eyebrow" style="margin-left:4px">Test & Flaws</span></div>
        <div class="panel-sub">风洞与四阶段试飞会收窄 ±1σ 误差带，并揭开隐藏缺陷与 D7「未知高速领域风险」。竞飞前修掉它们。</div>
      </div>
      <div class="panel-actions">
        <span class="badge ${sourceBadgeClass(STATE)}" style="align-self:center">${STATE.sourceBadge} · σ×${STATE.sigmaMult.toFixed(2)}</span>
        <button class="btn btn-green" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">进入真机竞飞 →</button>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">A · NACA 风洞试验<span class="eyebrow">Wind tunnel</span></div>
        <div class="stack">${tunnelHtml}</div>
      </div>
      <div class="card">
        <div class="card-title">B · 爱德华兹四阶段试飞<span class="eyebrow">Edwards AFB</span></div>
        <div class="stepper">${stepperHtml}</div>
        <div style="margin-top:10px;font-size:11.5px;color:var(--text-muted)">每阶段 $320k + 试飞员津贴；P3/P4 各 +22 天，其余 +14 天。</div>
      </div>
    </div>

    <div>
      <div class="card-title" style="padding:0 2px">试飞员名册<span class="eyebrow">Pilot roster · D9</span></div>
      <div class="grid-3">${pilotCards}</div>
    </div>

    <div>
      <div class="card-title" style="padding:0 2px">隐患排雷看板<span class="eyebrow">Hidden flaws · D7</span></div>
      <div class="grid-2">${flawCards || `<div class="empty">当前设计没有潜伏的高危缺陷。</div>`}</div>
    </div>
  `;
}

function renderProcurementWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];

  const sigMach = STATE.inquiryLevel === 0 ? 0.14 : STATE.inquiryLevel === 1 ? 0.07 : 0.03;
  const sigPrice = STATE.inquiryLevel === 0 ? 180 : STATE.inquiryLevel === 1 ? 90 : 35;
  const sigR = STATE.inquiryLevel === 0 ? 55 : STATE.inquiryLevel === 1 ? 22 : 9;

  const rumorRows = scen.rivals.map(function (rv) {
    const h = A1.DATA.aircraft_hist && A1.DATA.aircraft_hist[rv.stem];
    const m = h ? h.oracle_perf.max_mach_alt : 1.35;
    const r = h ? (h.oracle_perf.combat_radius_m / 1852).toFixed(0) : 380;
    return `<tr>
      <td><b>${rv.company}</b><div class="muted" style="font-size:11.5px">${rv.designation}</div></td>
      <td class="sec">${rv.config_zh}</td>
      <td class="num c-cyan">M ${m.toFixed(2)} <span class="muted">±${sigMach.toFixed(2)}</span></td>
      <td class="num">${r} <span class="muted">±${sigR} nmi</span></td>
      <td class="num c-brass">$${(rv.price_usd / 1e3).toFixed(0)}k <span class="muted">±${sigPrice}k</span></td>
    </tr>`;
  }).join("");

  let debriefHtml = `<div class="card sunken" style="text-align:center;padding:26px;">
    <div style="font-size:13px;color:var(--text-secondary);margin-bottom:14px;">尚未进行两阶段真机同台竞飞。设定报价后开赛。</div>
    <button class="btn btn-green lg" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">★ 启动爱德华兹真机竞飞</button>
  </div>`;

  if (STATE.flyoffResults) {
    const res = STATE.flyoffResults;
    const me = res.find((r) => r.isPlayer);
    const myRank = res.indexOf(me) + 1;
    const win = myRank === 1;
    const sb = (v) => `<div class="score-bar"><span class="b"><i style="width:${Math.max(0, Math.min(100, v))}%"></i></span><span class="v">${v}</span></div>`;
    const resRows = res.map(function (r, idx) {
      const sc = r.scores;
      return `<tr class="${r.isPlayer ? "me" : ""}">
        <td class="num"><b>#${idx + 1}</b> ${idx === 0 ? "🏆" : ""}</td>
        <td><b style="color:${r.isPlayer ? "var(--accent-cyan)" : "var(--text-primary)"}">${r.company}</b><div class="muted" style="font-size:11.5px">${r.designation}</div></td>
        <td class="num">M ${r.perf.max_mach_alt.toFixed(2)}<div class="muted">${(r.perf.combat_radius_m / 1852).toFixed(0)} nmi</div></td>
        <td class="num c-brass">$${(r.price_usd / 1e3).toFixed(0)}k</td>
        <td style="min-width:90px">${sb(sc.S_perf)}</td>
        <td style="min-width:90px">${sb(sc.S_cost)}</td>
        <td style="min-width:90px">${sb(sc.S_sched)}</td>
        <td style="min-width:90px">${sb(sc.S_risk)}</td>
        <td class="num">${sc.S_pol}</td>
        <td class="num"><b style="font-size:14px;color:${idx === 0 ? "var(--accent-green)" : "var(--text-primary)"}">${sc.S_total}</b></td>
      </tr>`;
    }).join("");
    debriefHtml = `
      <div class="result-banner ${win ? "win" : "lose"}">
        <span class="big">${win ? "🏆" : "📉"}</span>
        <div><div class="h">${win ? `中标！${scen.quantity_planned} 架量产合同` : `落败 · 第 ${myRank} 名`}</div>
        <div class="s">${win ? "我方原型机在爱德华兹同台竞飞中综合得分第一。" : `冠军：${res[0].company} (${res[0].designation})${me.scores.misses.length ? " · 我方未达门槛：" + me.scores.misses.join(", ") : ""}`}</div></div>
        <div class="score"><span class="muted" style="font-size:11px">我方总分</span><b class="${win ? "c-green" : "c-red"}">${me.scores.S_total}</b></div>
      </div>
      <div class="card">
        <div class="card-title">定标复盘<span class="eyebrow">Source selection debrief · D6 / D10</span></div>
        <div style="overflow-x:auto"><table class="bp-table">
          <thead><tr><th>名次</th><th>厂商 / 原型机</th><th>实测</th><th>报价</th><th>性能</th><th>成本</th><th>进度</th><th>风险</th><th>声望</th><th>总分</th></tr></thead>
          <tbody>${resRows}</tbody>
        </table></div>
      </div>`;
  }

  const intelBtn = (lv, label) => `<button class="${STATE.inquiryLevel === lv ? "on" : ""}" onclick="window.MIC_UI.setInquiry(${lv})">${label}</button>`;
  const priceRatio = STATE.bidPriceUsd / scen.unit_price_ceiling_usd;

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title"><span class="step">3</span>情报与真机竞飞 <span class="eyebrow" style="margin-left:4px">Procurement</span></div>
        <div class="panel-sub">截标前可用媒体传闻或华盛顿联络官收窄对手区间（D10）；定标采用两阶段真机同台竞飞（D6）。</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title" style="flex-wrap:wrap">截标前对手情报<span class="eyebrow" style="margin-left:6px;margin-right:auto">Rumors · D10</span>
        <div class="seg">${intelBtn(0, "L0《航空周刊》传闻")}${intelBtn(1, "L1 华盛顿联络官 −4 政治")}${intelBtn(2, "L2 深度技术侦察 −$150k")}</div>
      </div>
      <div style="overflow-x:auto"><table class="bp-table">
        <thead><tr><th>竞争对手</th><th>传闻构型</th><th>最大马赫 ±1σ</th><th>作战半径 ±1σ</th><th>单机报价 ±1σ</th></tr></thead>
        <tbody>${rumorRows}</tbody>
      </table></div>
    </div>

    <div class="card">
      <div class="card-title">我方报价与合同<span class="eyebrow">Bid</span></div>
      <div class="grid-3" style="align-items:center">
        <div>
          <div class="slider-header"><span>单机出厂报价</span><span class="s-val" style="color:${priceRatio > 1 ? "var(--accent-red)" : "var(--accent-brass)"}">$${(STATE.bidPriceUsd / 1e3).toFixed(0)}k <span class="muted">/ 上限 $${(scen.unit_price_ceiling_usd / 1e3).toFixed(0)}k</span></span></div>
          <input type="range" id="inp-bid-price" class="brass" min="${Math.round(scen.unit_price_ceiling_usd * 0.55)}" max="${Math.round(scen.unit_price_ceiling_usd * 1.15)}" step="10000" value="${STATE.bidPriceUsd}">
        </div>
        <div class="kpi"><div class="k-lbl">累计交付周期（招标要求 ${scen.flyoff_days_budget} 天）</div><div class="k-val" style="color:${STATE.schedDays > scen.flyoff_days_budget ? "var(--accent-red)" : "var(--text-primary)"}">${STATE.schedDays}<small>天</small></div></div>
        <button class="btn btn-green lg block" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">★ 提交原型机并开始竞飞</button>
      </div>
    </div>

    ${debriefHtml}
  `;
}

function renderPropulsionWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const K = window.MIC_KERNEL;
  const STATE = A1.STATE;
  const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];

  const quotes = K.quoteCustomEngines(58.0, true, 9.5, scen.year);
  const vendorCards = quotes.map(function (q) {
    const abbr = q.vendor.name.split("(")[0].split(/[\s&-]+/).filter((w) => /^[A-Za-z]/.test(w) && !/^(of|and)$/i.test(w)).map((w) => w[0]).join("").slice(0, 3).toUpperCase();
    const riskHigh = q.failure_risk_pct > 25;
    return `<div class="card vendor-card">
      <div class="vendor-head"><span class="vendor-logo">${abbr}</span><div><div style="font-weight:650">${q.vendor.name}</div><div class="muted" style="font-size:11.5px">${q.vendor.specialty_zh}</div></div></div>
      <div class="kv">
        <div><span>研发立项费</span><b class="c-brass">$${(q.nre_cost_usd / 1e6).toFixed(2)}M</b></div>
        <div><span>预计周期</span><b>${q.dev_months} 个月</b></div>
        <div><span>单台采购价</span><b>$${(q.unit_cost_usd / 1e3).toFixed(0)}k</b></div>
        <div><span>预估干重</span><b>${q.est_mass_kg} kg</b></div>
      </div>
      <div class="statbar" style="grid-template-columns:70px 1fr 40px;margin-bottom:12px"><span>延期风险</span><span class="b"><i style="width:${q.failure_risk_pct}%;background:${riskHigh ? "var(--accent-red)" : "var(--accent-green)"}"></i></span><span class="v" style="color:${riskHigh ? "var(--accent-red)" : "var(--accent-green)"}">${q.failure_risk_pct}%</span></div>
      <button class="btn btn-brass block" onclick="window.MIC_UI.commissionEngine('${q.vendor.id}', '${q.vendor.name}', ${q.nre_cost_usd})">委托定制研发</button>
    </div>`;
  }).join("");

  const engs = A1.DATA.engines_hist || {};
  const maxAb = Math.max.apply(null, Object.keys(engs).map((k) => engs[k].thrust_ab_sl_N || engs[k].thrust_dry_sl_N || 0));
  const curEng = STATE.design && STATE.design.propulsion ? STATE.design.propulsion.engine_id : "";
  const catalogRows = Object.keys(engs).map(function (ek) {
    const e = engs[ek];
    const dry = e.thrust_dry_sl_N || 30000;
    const ab = e.thrust_ab_sl_N || 0;
    const isCur = ek === curEng;
    return `<tr class="${isCur ? "me" : ""}">
      <td><b>${e.name || ek}</b>${isCur ? ` <span class="badge badge-tunnel">装机中</span>` : ""}</td>
      <td class="sec">${e.manufacturer || "—"}</td>
      <td style="min-width:200px">
        <div style="position:relative;height:8px;background:#13243f;border-radius:5px;overflow:hidden">
          ${ab ? `<i style="position:absolute;left:0;top:0;bottom:0;width:${(ab / maxAb) * 100}%;background:rgba(230,169,72,0.55)"></i>` : ""}
          <i style="position:absolute;left:0;top:0;bottom:0;width:${(dry / maxAb) * 100}%;background:var(--accent-cyan)"></i>
        </div>
        <div class="mono" style="font-size:11px;margin-top:3px"><span class="c-cyan">${(dry / 1000).toFixed(1)}</span>${ab ? ` / <span class="c-brass">${(ab / 1000).toFixed(1)}</span>` : ""} kN</div>
      </td>
      <td class="num">${e.mass_kg || "—"} kg</td>
      <td><button class="btn sm ${isCur ? "ghost" : ""}" ${isCur ? "disabled" : ""} onclick="window.MIC_UI.equipCatalogEngine('${ek}')">${isCur ? "已装机" : "装机"}</button></td>
    </tr>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title"><span class="step">4</span>航发定制 <span class="eyebrow" style="margin-left:4px">Propulsion · D9</span></div>
        <div class="panel-sub">直接选用史实成熟航发，或点名委托五大巨头定制新核心机。</div>
      </div>
    </div>
    <div>
      <div class="card-title" style="padding:0 2px">五巨头定制报价<span class="eyebrow">Named vendors</span></div>
      <div class="grid-3">${vendorCards}</div>
    </div>
    <div class="card">
      <div class="card-title">1945–1960 史实发动机目录<span class="eyebrow"><span class="c-cyan">■</span> 军用 <span class="c-brass">■</span> 加力</span></div>
      <div style="overflow-x:auto"><table class="bp-table">
        <thead><tr><th>型号</th><th>厂商</th><th>海平面推力</th><th>干重</th><th></th></tr></thead>
        <tbody>${catalogRows}</tbody>
      </table></div>
    </div>
  `;
}

function prettyTechName(id) {
  const parts = String(id).split("_");
  const rest = parts.slice(2).join(" ") || id;
  return rest
    .replace(/\b(\d+)pct\b/g, "$1%")
    .replace(/\b(\d+)deg\b/g, "$1°")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/\b(Le|Blc|Ab|Ww2|Hvar|Ai|Ibm|Fcs|Sas|Vhf|Scr720|Ffar|Labs|Fm|Rof|Mtbf|Tbo|Nc|Cnc|Mig|Usn|Usaf)\b/g, (m) => m.toUpperCase());
}

function renderTechAndCompanyWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const scenYear = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId].year;
  const rawNodes = (A1.DATA.tech_nodes && (A1.DATA.tech_nodes.nodes || A1.DATA.tech_nodes)) || [];
  const nodeList = Array.isArray(rawNodes) ? rawNodes : [];
  const branches = Array.from(new Set(nodeList.map((t) => t.branch || "aero")));
  const BR_ZH = { aero: "气动", structures: "结构", propulsion: "推进", avionics: "航电", armament: "武器", manufacturing: "制造", testing: "试验" };
  const curBr = STATE.techBranch || "all";
  const filtered = nodeList.filter((t) => curBr === "all" || t.branch === curBr);

  const byYear = {};
  filtered.forEach(function (t) {
    const y = Math.floor(Number(t.historical_year || 1950));
    (byYear[y] = byYear[y] || []).push(t);
  });
  const esc = (s) => String(s || "").replace(/"/g, "&quot;");
  const timelineHtml = Object.keys(byYear).sort().map(function (y) {
    const fut = Number(y) > scenYear;
    const nodes = byYear[y].map((t) => `<span class="tnode ${fut ? "future" : ""}" title="${esc(t.historical_note)}"><span class="br">${BR_ZH[t.branch] || t.branch}</span>${prettyTechName(t.id)}</span>`).join("");
    return `<div class="tl-year ${fut ? "future" : ""}"><span class="y">${y}</span><div class="tl-nodes">${nodes}</div></div>`;
  }).join("");

  const brBtn = (id, label) => `<button class="${curBr === id ? "on" : ""}" onclick="window.MIC_UI.setTechBranch('${id}')">${label}</button>`;

  const progRows = (A1.DATA.programs || []).map(function (p) {
    return `<tr>
      <td><b>${p.program_name || p.id}</b></td>
      <td><span class="badge ${p.customer === "USN" ? "badge-tunnel" : "badge-sim"}">${p.customer || "USAF"}</span></td>
      <td class="num">${p.issue_date || "—"}</td>
      <td><span class="badge badge-muted">${STATE.forceFlyoffMode ? "两阶段竞飞" : (p.acquisition && p.acquisition.style) || "flyoff"}</span></td>
    </tr>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title"><span class="step">5</span>科技树与战役规则 <span class="eyebrow" style="margin-left:4px">Tech · D6 D7 D8</span></div>
        <div class="panel-sub">科技树开局全貌可见；当前剧本年份（${scenYear}）之后的节点为“超前研发”，带惩罚。悬停节点查看史实注释。</div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">战役规则开关<span class="eyebrow">Rules</span></div>
        <label class="switch-row"><span class="txt"><b>D6 统一两阶段真机竞飞</b><small>全部 16 个主战项目统一为 Fly-Off 定标</small></span><input type="checkbox" ${STATE.forceFlyoffMode ? "checked" : ""} onchange="window.MIC_UI.toggleRule('forceFlyoffMode', this.checked)"></label>
        <label class="switch-row"><span class="txt"><b>D7 历史后见之明</b><small>关闭时，超前隐患显示为「未知高速领域风险」直至风洞/试飞揭晓</small></span><input type="checkbox" ${STATE.hindsightMode ? "checked" : ""} onchange="window.MIC_UI.toggleRule('hindsightMode', this.checked)"></label>
        <div class="card sunken accent-green" style="margin-top:12px">
          <div class="card-title" style="margin-bottom:6px">D8 · 1960 终局与沙盒延续</div>
          <div class="muted" style="font-size:12px;margin-bottom:10px">结算 1960-12-31 战役评分，并生成 1961+ 程序化招标书。</div>
          <button class="btn btn-green" onclick="window.MIC_UI.trigger1960Sandbox()">推进至 1960 结算 →</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">史实招标项目库<span class="eyebrow">${(A1.DATA.programs || []).length} programs</span></div>
        <div style="max-height:300px;overflow-y:auto">
          <table class="bp-table"><thead><tr><th>项目</th><th>军种</th><th>发布</th><th>定标 (D6)</th></tr></thead><tbody>${progRows}</tbody></table>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-title" style="flex-wrap:wrap">1945–1960 科技时间线<span class="eyebrow" style="margin-left:6px;margin-right:auto">${filtered.length} / ${nodeList.length} nodes</span>
        <div class="seg">${brBtn("all", "全部")}${branches.map((b) => brBtn(b, BR_ZH[b] || b)).join("")}</div>
      </div>
      <div style="display:flex;gap:14px;font-size:11.5px;margin-bottom:6px" class="muted"><span><span class="c-green">●</span> 时代已成熟</span><span><span style="color:var(--accent-pink)">●</span> 超前研发（${scenYear} 年后）</span></div>
      <div class="timeline">${timelineHtml}</div>
    </div>
  `;
}

function bindInteractiveCanvasEvents(cvs) {
  if (!cvs) return;
  const A1 = window.MIC_APP_PART1;
  const K = window.MIC_KERNEL;
  const STATE = A1.STATE;

  let isDragging = false;
  let activeHandle = null;

  function getCanvasPos(ev) {
    const rect = cvs.getBoundingClientRect();
    const clientX = ev.touches && ev.touches.length ? ev.touches[0].clientX : ev.clientX;
    const clientY = ev.touches && ev.touches.length ? ev.touches[0].clientY : ev.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top,
    };
  }

  function findHitHandle(pos) {
    const inter = cvs._interactive;
    if (!inter || !inter.handles) return null;
    let best = null;
    let bestDist = 18.0; // 18px hit radius
    for (let i = 0; i < inter.handles.length; i++) {
      const h = inter.handles[i];
      const d = Math.hypot(pos.x - h.x, pos.y - h.y);
      if (d < bestDist) {
        bestDist = d;
        best = h;
      }
    }
    return best;
  }

  function applyPointerSculpt(pos) {
    const inter = cvs._interactive;
    if (!inter) return;
    const d = STATE.design;

    // 1. Airfoil Cross-Section Sculpting (Control Point Drag OR Freehand Brush)
    if (inter.mode === "airfoil") {
      const af = K.ensureCustomAirfoil(d);
      const yc = inter.fromY(pos.y);
      const xc = inter.fromX(pos.x);

      if (activeHandle && activeHandle.kind === "af_upper") {
        const k = activeHandle.index;
        af.upper[k] = Number(Math.max(af.lower[k] + 0.015, Math.min(0.135, yc)).toFixed(4));
        af.preset_name = "Custom 手绘翼型";
      } else if (activeHandle && activeHandle.kind === "af_lower") {
        const k = activeHandle.index;
        af.lower[k] = Number(Math.min(af.upper[k] - 0.015, Math.max(-0.135, yc)).toFixed(4));
        af.preset_name = "Custom 手绘翼型";
      } else if (pos.y >= inter.box.y && pos.y <= inter.box.y + inter.box.h) {
        // Freehand brush stroke across airfoil chord! Find nearest x_ctrl index
        let nearestK = 0;
        let minDx = 999;
        for (let k = 0; k < K.AIRFOIL_X_CTRL.length; k++) {
          const dx = Math.abs(xc - K.AIRFOIL_X_CTRL[k]);
          if (dx < minDx) {
            minDx = dx;
            nearestK = k;
          }
        }
        const mode = STATE.airfoilBrushMode;
        const editUpper = mode === "free_upper" || (mode === "nodes" && yc >= 0);
        if (editUpper) {
          af.upper[nearestK] = Number(Math.max(af.lower[nearestK] + 0.015, Math.min(0.135, yc)).toFixed(4));
        } else {
          af.lower[nearestK] = Number(Math.min(af.upper[nearestK] - 0.015, Math.max(-0.135, yc)).toFixed(4));
        }
        af.preset_name = "Custom 手绘翼型";
      }
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
      return;
    }

    // 2. Fuselage Station Lofting & Area-Rule Waist Sculpting
    if (inter.mode === "fuselage_area") {
      const radii = K.ensureFuselageStations(d);
      const minR = inter.minRadii || K.getMinClearanceRadii(d);
      let targetIdx = activeHandle && activeHandle.kind === "fus_station" ? activeHandle.index : -1;
      if (targetIdx < 0 && pos.y >= inter.box.y - 12 && pos.y <= inter.box.y + inter.box.h + 12) {
        // Freehand fuselage sculpting along x/L!
        const u = Math.max(0.0, Math.min(1.0, (pos.x - inter.box.x) / Math.max(1, inter.box.w)));
        targetIdx = Math.round(u * 10);
      }
      if (targetIdx >= 0 && targetIdx <= 10) {
        const newR = inter.fromFusY(pos.y);
        radii[targetIdx] = Number(Math.max(minR[targetIdx], Math.min(1.45, newR)).toFixed(3));
        // Smoothlysync max_diameter_m & area_ruled flag from sculpted waist
        d.fuselage.max_diameter_m = Number((Math.max(...radii) * 2.0).toFixed(2));
        window.MIC_APP_ACTIONS.recalculateDesign(false);
        d.fuselage.area_ruled = STATE.perf.areaDist.r_area <= 1.18;
        window.MIC_APP_ACTIONS.recalculateDesign(false);
        refreshDesignInPlace();
      }
      return;
    }

    // 3. 3-View Blueprint Interactive Wing Planform & Fuselage Waist Dragging
    if (inter.mode === "blueprint_3view" && activeHandle) {
      if (activeHandle.kind === "wing_le") {
        // Vertical distance from centerline -> half_span -> Aspect Ratio AR
        const halfSpanM = Math.max(2.6, Math.min(11.0, Math.abs(pos.y - inter.cy) / inter.scale));
        const spanM = halfSpanM * 2.0;
        const S = Number(d.wing.area_m2 || 30.0);
        d.wing.aspect_ratio = Number(Math.max(1.8, Math.min(6.5, (spanM * spanM) / S)).toFixed(2));

        // Horizontal distance from wing root LE -> Sweep angle
        const dxM = (pos.x - inter.x_wing_le) / inter.scale;
        const sweepRad = Math.atan2(Math.max(0.0, dxM), halfSpanM);
        d.wing.sweep_quarter_chord_deg = Number(Math.max(0.0, Math.min(60.0, (sweepRad * 180.0) / Math.PI)).toFixed(1));
      } else if (activeHandle.kind === "wing_te") {
        // Horizontal drag of wingtip TE -> changes wingtip chord -> Wing Area S & Taper ratio
        const wLe = inter.handles.find((h) => h.id === "planform_wing_le");
        if (wLe) {
          const cTipM = Math.max(0.45, Math.min(4.8, (pos.x - wLe.x) / inter.scale));
          const newTaper = Math.max(0.12, Math.min(0.85, cTipM / Math.max(1.2, inter.c_root)));
          d.wing.taper_ratio = Number(newTaper.toFixed(2));
          const spanM = Math.sqrt(Number(d.wing.area_m2 || 30.0) * Number(d.wing.aspect_ratio || 3.5));
          const newArea = Math.max(14.0, Math.min(68.0, 0.5 * spanM * inter.c_root * (1.0 + newTaper)));
          d.wing.area_m2 = Number(newArea.toFixed(1));
        }
      } else if (activeHandle.kind === "fus_station_3view") {
        const k = activeHandle.index;
        const radii = K.ensureFuselageStations(d);
        const rM = Math.abs(pos.y - inter.cy) / inter.scale;
        radii[k] = Number(Math.max(activeHandle.rMin || 0.25, Math.min(1.4, rM)).toFixed(3));
        window.MIC_APP_ACTIONS.recalculateDesign(false);
        d.fuselage.area_ruled = STATE.perf.areaDist.r_area <= 1.18;
      }
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    }
  }

  cvs.addEventListener("mousedown", function (ev) {
    const pos = getCanvasPos(ev);
    cvs._lockScale = true;
    activeHandle = findHitHandle(pos);
    cvs._activeHandleId = activeHandle ? activeHandle.id : null;
    isDragging = true;
    applyPointerSculpt(pos);
  });

  cvs.addEventListener("mousemove", function (ev) {
    const pos = getCanvasPos(ev);
    if (!isDragging) {
      const hover = findHitHandle(pos);
      const newHoverId = hover ? hover.id : null;
      if (cvs._activeHandleId !== newHoverId) {
        cvs._activeHandleId = newHoverId;
        cvs.style.cursor = newHoverId ? "grab" : "crosshair";
        drawActiveDesignCanvas(cvs);
      }
      return;
    }
    cvs.style.cursor = "grabbing";
    applyPointerSculpt(pos);
  });

  if (window._micCanvasMouseUp && window.removeEventListener) window.removeEventListener("mouseup", window._micCanvasMouseUp);
  window._micCanvasMouseUp = function () {
    if (isDragging) {
      isDragging = false;
      activeHandle = null;
      cvs._lockScale = false;
      cvs.style.cursor = "crosshair";
      drawActiveDesignCanvas(cvs);
    }
  };
  window.addEventListener("mouseup", window._micCanvasMouseUp);

  cvs.addEventListener("touchstart", function (ev) {
    const pos = getCanvasPos(ev);
    cvs._lockScale = true;
    activeHandle = findHitHandle(pos);
    cvs._activeHandleId = activeHandle ? activeHandle.id : null;
    isDragging = true;
    applyPointerSculpt(pos);
    ev.preventDefault();
  }, { passive: false });

  cvs.addEventListener("touchmove", function (ev) {
    if (!isDragging) return;
    const pos = getCanvasPos(ev);
    applyPointerSculpt(pos);
    ev.preventDefault();
  }, { passive: false });

  cvs.addEventListener("touchend", function () {
    isDragging = false;
    activeHandle = null;
    cvs._lockScale = false;
    drawActiveDesignCanvas(cvs);
  });
}

function renderAll() {
  const A1 = window.MIC_APP_PART1;
  const K = window.MIC_KERNEL;
  const STATE = A1.STATE;

  renderTopBarAndRightFeed();
  const host = document.getElementById("workspace-host");
  if (!host) return;

  if (STATE.activeWorkspace === "design") {
    renderDesignWorkspace(host);
    const bindSlider = function (id, fn) {
      const el = document.getElementById(id);
      if (el) el.addEventListener("input", fn);
    };
    const tplEl = document.getElementById("inp-template");
    if (tplEl) {
      tplEl.addEventListener("change", function (e) {
        window.MIC_APP_ACTIONS.loadTemplate(e.target.value, false);
        renderAll();
      });
    }
    bindSlider("inp-area", (e) => {
      STATE.design.wing.area_m2 = Number(e.target.value);
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    });
    bindSlider("inp-sweep", (e) => {
      STATE.design.wing.sweep_quarter_chord_deg = Number(e.target.value);
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    });
    bindSlider("inp-ar", (e) => {
      STATE.design.wing.aspect_ratio = Number(e.target.value);
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    });
    bindSlider("inp-tc", (e) => {
      const targetTc = Number(e.target.value);
      const af = K.ensureCustomAirfoil(STATE.design);
      const curEval = K.evaluateAirfoilSpline(STATE.design);
      const ratio = targetTc / Math.max(0.02, curEval.tc_max);
      for (let k = 0; k < 5; k++) {
        const cam = 0.5 * (af.upper[k] + af.lower[k]);
        const halfT = 0.5 * (af.upper[k] - af.lower[k]) * ratio;
        af.upper[k] = Number(Math.min(0.135, cam + halfT).toFixed(4));
        af.lower[k] = Number(Math.max(-0.135, cam - halfT).toFixed(4));
      }
      STATE.design.wing.t_c_root = targetTc;
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    });
    bindSlider("inp-fuel", (e) => {
      STATE.design.fuel.internal_kg = Number(e.target.value);
      window.MIC_APP_ACTIONS.recalculateDesign(false);
      refreshDesignInPlace();
    });

    const arChk = document.getElementById("inp-arearule");
    if (arChk) {
      arChk.addEventListener("change", (e) => {
        STATE.design.fuselage.area_ruled = e.target.checked;
        STATE.design.fuselage.station_radii = K.buildDefaultFuselageRadii(
          STATE.design,
          e.target.checked,
          K.getMinClearanceRadii(STATE.design)
        );
        window.MIC_APP_ACTIONS.recalculateDesign(false);
        refreshDesignInPlace();
      });
    }
    const abChk = document.getElementById("inp-ab");
    if (abChk) abChk.addEventListener("change", (e) => { STATE.design.propulsion.afterburner = e.target.checked; window.MIC_APP_ACTIONS.recalculateDesign(false); refreshDesignInPlace(); });
    const twChk = document.getElementById("inp-twin");
    if (twChk) twChk.addEventListener("change", (e) => { STATE.design.propulsion.count = e.target.checked ? 2 : 1; window.MIC_APP_ACTIONS.recalculateDesign(false); refreshDesignInPlace(); });
    const engSel = document.getElementById("inp-engine");
    if (engSel) engSel.addEventListener("change", (e) => { STATE.design.propulsion.engine_id = e.target.value; window.MIC_APP_ACTIONS.recalculateDesign(false); refreshDesignInPlace(); });

    const cvs = document.getElementById("design-main-canvas");
    if (cvs) {
      drawActiveDesignCanvas(cvs);
      bindInteractiveCanvasEvents(cvs);
    }
  } else if (STATE.activeWorkspace === "testing") {
    renderTestingWorkspace(host);
  } else if (STATE.activeWorkspace === "procurement") {
    renderProcurementWorkspace(host);
    const bp = document.getElementById("inp-bid-price");
    if (bp) {
      bp.addEventListener("input", (e) => {
        STATE.bidPriceUsd = Number(e.target.value);
        syncRangeFills(host);
        const lbl = bp.parentNode && bp.parentNode.querySelector(".s-val");
        const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];
        if (lbl) {
          lbl.style.color = STATE.bidPriceUsd > scen.unit_price_ceiling_usd ? "var(--accent-red)" : "var(--accent-brass)";
          lbl.innerHTML = `$${(STATE.bidPriceUsd / 1e3).toFixed(0)}k <span class="muted">/ 上限 $${(scen.unit_price_ceiling_usd / 1e3).toFixed(0)}k</span>`;
        }
      });
    }
  } else if (STATE.activeWorkspace === "propulsion") {
    renderPropulsionWorkspace(host);
  } else {
    renderTechAndCompanyWorkspace(host);
  }
  syncRangeFills(host);
}

window.MIC_UI = {
  goWorkspace: function (ws) { window.MIC_APP_PART1.STATE.activeWorkspace = ws; renderAll(); if (window.scrollTo) window.scrollTo(0, 0); },
  setCanvasTab: function (tab) { window.MIC_APP_PART1.STATE.activeCanvasTab = tab; renderAll(); },
  setTechBranch: function (b) { window.MIC_APP_PART1.STATE.techBranch = b; renderAll(); },
  toggleFeed: function (force) {
    const S = window.MIC_APP_PART1.STATE;
    const open = typeof force === "boolean" ? force : !document.body.classList.contains("feed-open");
    document.body.classList.toggle("feed-open", open);
    if (open) S.unreadEvents = 0;
    renderTopBarAndRightFeed();
  },
  setAirfoilBrush: function (mode) { window.MIC_APP_PART1.STATE.airfoilBrushMode = mode; renderAll(); },
  applyAirfoilPreset: function (presetId) {
    const K = window.MIC_KERNEL;
    const S = window.MIC_APP_PART1.STATE;
    const p = K.AIRFOIL_PRESETS[presetId];
    if (!p) return;
    S.design.custom_airfoil = {
      preset_name: p.name,
      upper: p.upper.slice(),
      lower: p.lower.slice(),
    };
    window.MIC_APP_ACTIONS.recalculateDesign(false);
    window.MIC_APP_ACTIONS.logEvent(null, "AIRFOIL", `已载入并应用翼型截面：【${p.name}】((t/c)_max = ${(S.perf.airfoilEval.tc_max * 100).toFixed(1)}%)`);
    renderAll();
  },
  sculptFuselagePreset: function (action) {
    const K = window.MIC_KERNEL;
    const S = window.MIC_APP_PART1.STATE;
    const d = S.design;
    const minR = K.getMinClearanceRadii(d);
    const maxD = Number((d.fuselage && d.fuselage.max_diameter_m) || 1.5);
    if (action === "tube") {
      d.fuselage.area_ruled = false;
      d.fuselage.station_radii = K.buildDefaultFuselageRadii(d, false, minR);
      window.MIC_APP_ACTIONS.logEvent(null, "FUSELAGE", "已还原为直筒纺锤机身（无蜂腰面积律修形）。");
    } else if (action === "waist") {
      d.fuselage.area_ruled = true;
      d.fuselage.station_radii = K.buildDefaultFuselageRadii(d, true, minR);
      window.MIC_APP_ACTIONS.logEvent(null, "FUSELAGE", "✨ 已完成惠特科姆面积律蜂腰修形 (Coke-Bottle Waist)，跨音速激波阻力大幅下降！");
    } else if (action === "fatten" || action === "slim") {
      const mult = action === "fatten" ? 1.06 : 0.94;
      const radii = K.ensureFuselageStations(d);
      for (let k = 0; k < 11; k++) {
        radii[k] = Number(Math.max(minR[k], Math.min(1.45, radii[k] * mult)).toFixed(3));
      }
      d.fuselage.max_diameter_m = Number((Math.max(...radii) * 2.0).toFixed(2));
    }
    window.MIC_APP_ACTIONS.recalculateDesign(false);
    d.fuselage.area_ruled = S.perf.areaDist.r_area <= 1.18;
    window.MIC_APP_ACTIONS.recalculateDesign(false);
    renderAll();
  },
  selectPilot: function (idx) { window.MIC_APP_PART1.STATE.selectedPilotIdx = idx; renderAll(); },
  setInquiry: function (lvl) {
    const S = window.MIC_APP_PART1.STATE;
    S.inquiryLevel = lvl;
    window.MIC_APP_ACTIONS.logEvent(null, "INTEL", `已升级竞争对手情报等级至 L${lvl}，对手性能与报价误差棒收窄！`);
    renderAll();
  },
  equipCatalogEngine: function (ek) {
    const S = window.MIC_APP_PART1.STATE;
    S.design.propulsion.engine_id = ek;
    window.MIC_APP_ACTIONS.recalculateDesign(false);
    window.MIC_APP_ACTIONS.logEvent(null, "ENGINE", `已为当前飞机换装目录发动机：【${ek}】`);
    S.activeWorkspace = "design";
    renderAll();
  },
  commissionEngine: function (vid, vname, cost) {
    const S = window.MIC_APP_PART1.STATE;
    S.companyCashUsd -= cost;
    window.MIC_APP_ACTIONS.logEvent(null, "VENDOR", `已向【${vname}】签署定制发动机委托合同 (-$${(cost / 1e6).toFixed(2)}M)！`);
    renderAll();
  },
  toggleRule: function (key, val) {
    const S = window.MIC_APP_PART1.STATE;
    S[key] = val;
    window.MIC_APP_ACTIONS.recalculateDesign(false);
    renderAll();
  },
  trigger1960Sandbox: function () {
    window.MIC_APP_ACTIONS.logEvent("1961-02-01", "SANDBOX", "★ 1960 正式战役评分已锁定 (等级: A)！已进入【1961+ 动态沙盒模式 (D8)】，生成程序化招标：USAF-1961-ADX 远程截击机！");
    renderAll();
  },
};

window.addEventListener("DOMContentLoaded", function () {
  // Deep-link support: #<workspace>[/<canvasTab>], e.g. #design/3view, #testing
  const hash = (window.location.hash || "").replace(/^#/, "");
  const parts = hash.split("/");
  const S = window.MIC_APP_PART1.STATE;
  if (["design", "testing", "procurement", "propulsion", "tech"].indexOf(parts[0]) !== -1) S.activeWorkspace = parts[0];
  if (["airfoil", "area_rule", "3view", "ps_contour", "drag_polar"].indexOf(parts[1]) !== -1) S.activeCanvasTab = parts[1];
  window.MIC_APP_ACTIONS.loadScenario("1952_interceptor");
  S.unreadEvents = 0;
  S.booted = true;
  renderTopBarAndRightFeed();
  // Canvases use JetBrains Mono; redraw once the webfont is ready
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { if (S.activeWorkspace === "design") renderAll(); });
  }
});
window.addEventListener("keydown", function (e) {
  const map = { F2: "design", F3: "propulsion", F4: "testing", F5: "procurement", F6: "tech" };
  if (map[e.key]) { e.preventDefault(); window.MIC_UI.goWorkspace(map[e.key]); }
  if (e.key === "Escape") window.MIC_UI.toggleFeed(false);
});
window.addEventListener("resize", function () {
  if (window.MIC_APP_PART1.STATE.activeWorkspace === "design") renderAll();
});
