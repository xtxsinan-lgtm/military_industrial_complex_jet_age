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

function renderTopBarAndRightFeed() {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];

  const elDate = document.getElementById("hud-date");
  if (elDate) elDate.textContent = scen.date_str + " (" + scen.customer + ")";
  const elCash = document.getElementById("hud-cash");
  if (elCash) elCash.textContent = "$" + (STATE.companyCashUsd / 1e6).toFixed(2) + "M";
  const elRepAF = document.getElementById("hud-rep-usaf");
  if (elRepAF) elRepAF.textContent = STATE.repUSAF + "/100";
  const elRepNavy = document.getElementById("hud-rep-usn");
  if (elRepNavy) elRepNavy.textContent = STATE.repUSN + "/100";
  const elPol = document.getElementById("hud-pol");
  if (elPol) elPol.textContent = STATE.polCapital + "/100";
  const elWon = document.getElementById("hud-won");
  if (elWon) elWon.textContent = STATE.contractsWon + " 项";

  // Update Left Nav Active Button
  document.querySelectorAll(".nav-btn").forEach(function (btn) {
    btn.classList.toggle("active", btn.getAttribute("data-ws") === STATE.activeWorkspace);
  });

  // Update Right Event Feed & Status
  const feedEl = document.getElementById("right-event-list");
  if (feedEl) {
    const unfixed = STATE.flaws.filter((f) => !f.fixed);
    const uncharted = unfixed.filter((f) => f.uncharted_before_discovery && !f.discovered);
    const knownUnfixed = unfixed.filter((f) => f.discovered || !f.uncharted_before_discovery);

    let alertHtml = `<div class="card" style="margin-bottom:10px;border-color:#e09f3e;">
      <div class="card-title">当前竞标与原型机状态</div>
      <div style="font-size:12px;margin-bottom:6px;"><b>当前剧本：</b>${scen.title_zh}</div>
      <div style="font-size:11.5px;color:#98b0d4;margin-bottom:8px;">${scen.desc_zh}</div>
      <div style="font-family:var(--font-mono);font-size:11.5px;">
        <div>数据来源：<span class="badge ${STATE.flightPhaseRun > 0 ? "badge-flight" : STATE.tunnelLevelRun > 0 ? "badge-tunnel" : "badge-sim"}">${STATE.sourceBadge}</span></div>
        <div style="margin-top:4px;">未知高速领域风险 (D7)：<span class="badge badge-uncharted">${uncharted.length} 项潜伏</span></div>
        <div style="margin-top:4px;">已暴露待修缺陷：<b style="color:${knownUnfixed.length > 0 ? "#d94a38" : "#3bceac"}">${knownUnfixed.length} 项</b></div>
      </div>
    </div>`;

    const logsHtml = STATE.eventLog.map(function (ev) {
      return `<div style="border-bottom:1px solid #1a3358;padding:6px 2px;font-size:11.8px;">
        <span style="font-family:var(--font-mono);color:#00f0ff;">[${ev.date}]</span>
        <span class="badge badge-sim" style="margin:0 4px;">${ev.cat}</span>
        <span>${ev.text}</span>
      </div>`;
    }).join("");

    feedEl.innerHTML = alertHtml + `<div class="card"><div class="card-title">电传警报与试飞日志 (TELETYPE FEED)</div>${logsHtml}</div>`;
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
      { lbl: "高空最大马赫数 (Max Mach)", key: "max_mach_alt", scale: 1.0, unit: "M", fmt: 2 },
      { lbl: "实用升限 (Service Ceiling)", key: "service_ceiling_m", scale: K.M_TO_FT, unit: "ft", fmt: 0 },
      { lbl: "海平面爬升率 (Climb Rate)", key: "climb_rate_sl_mps", scale: K.M_TO_FT * 60, unit: "fpm", fmt: 0 },
      { lbl: "作战半径 (Combat Radius)", key: "combat_radius_m", scale: K.M_TO_NMI, unit: "nmi", fmt: 0 },
      { lbl: "M0.8 持续盘旋率 (Turn Rate)", key: "sustained_turn_dps_m08_4572m", scale: 1.0, unit: "°/s", fmt: 1 },
    ];

    const perfRowsHtml = rows.map(function (r) {
      const e = est[r.key];
      const v = (e.value * r.scale).toFixed(r.fmt);
      const s = (e.sigma * r.scale).toFixed(r.fmt);
      const t = (scen.thresholds[r.key] * r.scale).toFixed(r.fmt);
      const o = (scen.objectives[r.key] * r.scale).toFixed(r.fmt);
      const pass = e.value >= scen.thresholds[r.key];
      return `<tr>
        <td>${r.lbl}</td>
        <td><b style="color:${pass ? "#3bceac" : "#d94a38"}">${v}</b> <span style="color:#98b0d4">±${s} ${r.unit}</span></td>
        <td>${t} / ${o} ${r.unit}</td>
        <td><span class="badge" style="background:${pass ? "#0e3d33" : "#451a16"};color:${pass ? "#54f5cf" : "#ff9c8f"}">${pass ? "达标 OK" : "未达标 LOW"}</span></td>
      </tr>`;
    }).join("");

    const vitalsHtml = `
      <div class="vital-pill"><span class="lbl">空重 Empty:</span><span class="val">${STATE.perf.empty_mass_kg.toFixed(0)} kg</span></div>
      <div class="vital-pill"><span class="lbl">最大起飞 MTOW:</span><span class="val">${STATE.perf.mtow_kg.toFixed(0)} kg</span></div>
      <div class="vital-pill"><span class="lbl">起飞滑跑距离:</span><span class="val">${(STATE.perf.takeoff_distance_m * 3.28084).toFixed(0)} ft</span></div>
      <div class="vital-pill"><span class="lbl">单机出厂成本:</span><span class="val brass">$${(STATE.perf.unit_flyaway_cost_usd / 1e3).toFixed(0)}k</span></div>
    `;

    const isSmooth = ad.r_area <= 1.18;
    const diagHtml = `
      <div style="color:#e09f3e;font-weight:700;margin-bottom:4px;">总师实时手绘气动诊断 (LIVE AIRFOIL & FUSELAGE DIAGNOSTICS)：</div>
      <div>• <b>手绘翼型：</b>(t/c)_max = ${(afEval.tc_max * 100).toFixed(2)}% (@ ${(afEval.x_tc_max * 100).toFixed(0)}%c) | 弯度 = ${(afEval.camber_max * 100).toFixed(2)}% | 2D M_dd = ${afEval.m_dd_2d.toFixed(2)} | CL_max = ${afEval.cl_max_2d.toFixed(2)}</div>
      <div>• <b>手绘机身与面积律：</b>波阻系数 R_area = <b style="color:${isSmooth ? "#3bceac" : "#ff5a47"}">${ad.r_area.toFixed(2)}</b> (蜂腰修形吻合度 ${(ad.waist_quality * 100).toFixed(0)}% | 机身容积 ${ad.fus_vol_m3.toFixed(1)} m³)</div>
      <div>• <b>纵向静稳定裕度：</b>${(STATE.perf.static_margin * 100).toFixed(1)}% MAC | <b>预估研发总费：</b>$${(STATE.perf.dev_cost_usd_estimate / 1e6).toFixed(2)}M</div>
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

    drawActiveDesignCanvas();
    renderTopBarAndRightFeed();
  }

  function renderDesignWorkspace(host) {
    const A1 = window.MIC_APP_PART1;
    const K = window.MIC_KERNEL;
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
      return `<option value="${k}" ${sel}>${item.design.name || k} (${item.id})</option>`;
    }).join("");

    const engKeys = Object.keys(A1.DATA.engines_hist || {});
    const engOpts = engKeys.map(function (ek) {
      const e = A1.DATA.engines_hist[ek];
      const sel = (prop.engine_id === ek || ek.indexOf(prop.engine_id) !== -1) ? "selected" : "";
      return `<option value="${ek}" ${sel}>${e.name || ek} (${((e.thrust_ab_sl_N || e.thrust_dry_sl_N || 35000)/1000).toFixed(1)} kN)</option>`;
    }).join("");

    const { perfRowsHtml, vitalsHtml, diagHtml } = buildPerfAndDiagHtml();

    // Context-sensitive sculpting toolbar above the interactive canvas
    let sculptToolbarHtml = "";
    if (STATE.activeCanvasTab === "airfoil") {
      sculptToolbarHtml = `
        <div style="background:#0d213f;border:1px solid #00f0ff;border-radius:4px;padding:7px 10px;display:flex;flex-direction:column;gap:6px;">
          <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
            <span style="font-size:11.5px;color:#00f0ff;font-weight:700;">✏️ 翼型画笔模式：</span>
            <button class="btn ${STATE.airfoilBrushMode === "nodes" ? "btn-brass" : ""}" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.setAirfoilBrush('nodes')">🎯 拖拽控制点 (U1-U5 / L1-L5)</button>
            <button class="btn ${STATE.airfoilBrushMode === "free_upper" ? "btn-brass" : ""}" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.setAirfoilBrush('free_upper')">🖌️ 自由涂抹手绘：上翼面</button>
            <button class="btn ${STATE.airfoilBrushMode === "free_lower" ? "btn-brass" : ""}" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.setAirfoilBrush('free_lower')">🖌️ 自由涂抹手绘：下翼面</button>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:5px;align-items:center;">
            <span style="font-size:11px;color:#98b0d4;">经典翼型一键载入：</span>
            <button class="btn" style="padding:2px 7px;font-size:11px;" onclick="window.MIC_UI.applyAirfoilPreset('naca_64a210')">NACA 64A-210 (F-86 亚音速高升力)</button>
            <button class="btn" style="padding:2px 7px;font-size:11px;" onclick="window.MIC_UI.applyAirfoilPreset('naca_65a006')">NACA 65A-006 (F-102 跨音速薄翼)</button>
            <button class="btn" style="padding:2px 7px;font-size:11px;" onclick="window.MIC_UI.applyAirfoilPreset('biconvex_34')">3.4% 双弧刀锋超音速翼 (F-104)</button>
            <button class="btn" style="padding:2px 7px;font-size:11px;" onclick="window.MIC_UI.applyAirfoilPreset('supercritical_early')">平顶超临界减波阻翼 (Supercritical)</button>
            <button class="btn" style="padding:2px 7px;font-size:11px;" onclick="window.MIC_UI.applyAirfoilPreset('high_camber_navy')">高弯度舰载机翼 (低失速)</button>
          </div>
        </div>
      `;
    } else if (STATE.activeCanvasTab === "area_rule" || STATE.activeCanvasTab === "3view") {
      sculptToolbarHtml = `
        <div style="background:#0d213f;border:1px solid #3bceac;border-radius:4px;padding:7px 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
          <span style="font-size:11.5px;color:#3bceac;font-weight:700;">✏️ 机身与机翼手绘塑形工具：</span>
          <span style="font-size:11px;color:#98b0d4;">直接在画布上按住鼠标拖拽 S0–S10 站位捏出蜂腰（或在三视图拖拽翼尖改后掠角/展长）！</span>
          <button class="btn" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.sculptFuselagePreset('tube')">还原直筒机身 (无蜂腰)</button>
          <button class="btn btn-green" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.sculptFuselagePreset('waist')">✨ 一键惠特科姆蜂腰修形 (Coke-Bottle)</button>
          <button class="btn" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.sculptFuselagePreset('fatten')">机身扩容加粗 +6%</button>
          <button class="btn" style="padding:3px 8px;font-size:11px;" onclick="window.MIC_UI.sculptFuselagePreset('slim')">机身减阻收窄 -6%</button>
        </div>
      `;
    }

    host.innerHTML = `
      <div class="panel-header">
        <div>
          <div class="panel-title">2. 飞机总体气动设计局与手绘塑形工作台 (AIRFRAME & FREEHAND SCULPTING BUREAU // SCREEN 2)</div>
          <div style="font-size:12px;color:#98b0d4;">支持在中央画布<b>直接用鼠标手绘/拖拽翼型上下表面 (U1–U5 / L1–L5)、捏合机身 11 个轴向站位 (S0–S10 蜂腰修形)、拖拽三视图翼尖</b>，实时解算激波分布与性能误差棒！</div>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-brass" onclick="window.MIC_UI.goWorkspace('testing')">前往风洞与试飞中心 (收窄 ±1σ & 排雷) &rarr;</button>
          <button class="btn btn-green" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">直接提交爱德华兹真机竞飞 &rarr;</button>
        </div>
      </div>

      <div class="design-grid">
        <!-- Left Column: Parametric Sliders -->
        <div class="card">
          <div class="card-title">总体气动与推进参数 (PARAMETRIC INPUTS)</div>
          <div class="slider-row">
            <div class="slider-header"><span>史实基准模板 (Baseline Template)</span></div>
            <select id="inp-template">${templateOpts}</select>
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>机翼参考面积 S (Wing Area)</span><span class="s-val" id="lbl-area">${Number(wing.area_m2).toFixed(1)} m² (${(wing.area_m2 * 10.764).toFixed(0)} sq.ft)</span></div>
            <input type="range" id="inp-area" min="14" max="68" step="0.5" value="${wing.area_m2}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>1/4弦线后掠角 Λ (Quarter-Chord Sweep)</span><span class="s-val" id="lbl-sweep">${Number(wing.sweep_quarter_chord_deg).toFixed(1)}°</span></div>
            <input type="range" id="inp-sweep" min="0" max="60" step="1" value="${wing.sweep_quarter_chord_deg}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>展弦比 AR (Aspect Ratio)</span><span class="s-val" id="lbl-ar">${Number(wing.aspect_ratio).toFixed(2)}</span></div>
            <input type="range" id="inp-ar" min="1.8" max="6.5" step="0.05" value="${wing.aspect_ratio}">
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>翼根相对厚度 t/c (缩放手绘翼型厚度)</span><span class="s-val" id="lbl-tc">${(Number(wing.t_c_root) * 100).toFixed(1)}%</span></div>
            <input type="range" id="inp-tc" min="0.034" max="0.13" step="0.002" value="${wing.t_c_root}">
          </div>
          <div class="slider-row" style="background:#17345c;padding:8px;border-radius:4px;border:1px solid #00f0ff;">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:700;color:#00f0ff;">
              <input type="checkbox" id="inp-arearule" ${fus.area_ruled ? "checked" : ""}>
              <span>启用惠特科姆跨音速面积律修形 (Wasp-Waist Area Rule)</span>
            </label>
            <div style="font-size:11px;color:#98b0d4;margin-top:3px;">勾选自动生成蜂腰，或在【Tab C】亲手拖拽 S0–S10 捏合机身！</div>
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>发动机型号 (Engine Model)</span></div>
            <select id="inp-engine">${engOpts}</select>
          </div>
          <div class="slider-row" style="display:flex;gap:12px;align-items:center;">
            <label style="display:flex;align-items:center;gap:5px;cursor:pointer;">
              <input type="checkbox" id="inp-ab" ${prop.afterburner ? "checked" : ""}> <span>加力燃烧室 (Afterburner)</span>
            </label>
            <label style="display:flex;align-items:center;gap:5px;cursor:pointer;">
              <input type="checkbox" id="inp-twin" ${Number(prop.count) === 2 ? "checked" : ""}> <span>双发构型 (2x Engines)</span>
            </label>
          </div>
          <div class="slider-row">
            <div class="slider-header"><span>内部燃油重量 (Internal Fuel)</span><span class="s-val" id="lbl-fuel">${Number(fuel.internal_kg).toFixed(0)} kg (${(fuel.internal_kg * 2.2046).toFixed(0)} lb)</span></div>
            <input type="range" id="inp-fuel" min="800" max="6500" step="50" value="${fuel.internal_kg}">
          </div>
        </div>

        <!-- Center Column: 5 Interactive Blueprint & Freehand Sculpting Canvases -->
        <div class="card" style="display:flex;flex-direction:column;gap:8px;">
          <div style="display:flex;flex-wrap:wrap;gap:6px;">
            <button class="btn ${STATE.activeCanvasTab === "airfoil" ? "btn-brass" : ""}" onclick="window.MIC_UI.setCanvasTab('airfoil')">✏️ Tab E: 手绘翼型与激波台 (Airfoil Studio)</button>
            <button class="btn ${STATE.activeCanvasTab === "area_rule" ? "btn-brass" : ""}" onclick="window.MIC_UI.setCanvasTab('area_rule')">✏️ Tab C: 手绘机身蜂腰与面积律 A(x)</button>
            <button class="btn ${STATE.activeCanvasTab === "3view" ? "btn-brass" : ""}" onclick="window.MIC_UI.setCanvasTab('3view')">✏️ Tab A: 正交三视图与机翼手绘蓝图</button>
            <button class="btn ${STATE.activeCanvasTab === "ps_contour" ? "btn-brass" : ""}" onclick="window.MIC_UI.setCanvasTab('ps_contour')">Tab D: Boyd 能量包线 Ps</button>
            <button class="btn ${STATE.activeCanvasTab === "drag_polar" ? "btn-brass" : ""}" onclick="window.MIC_UI.setCanvasTab('drag_polar')">Tab B: 跨音速波阻 CD0(M)</button>
          </div>
          ${sculptToolbarHtml}
          <canvas id="design-main-canvas" class="blueprint-canvas" style="cursor:crosshair;"></canvas>
          <div id="design-vital-pills" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;font-family:var(--font-mono);font-size:11.5px;">
            ${vitalsHtml}
          </div>
        </div>

        <!-- Right Column: PerformanceReport with EstimateBadge Error Bars -->
        <div class="card">
          <div class="card-title">性能报告与误差棒 (PERFORMANCE REPORT & ±1σ)</div>
          <div style="margin-bottom:8px;font-size:11.8px;">
            当前置信度来源：<span class="badge ${STATE.flightPhaseRun > 0 ? "badge-flight" : STATE.tunnelLevelRun > 0 ? "badge-tunnel" : "badge-sim"}">${STATE.sourceBadge}</span>
          </div>
          <table class="bp-table">
            <thead><tr><th>指标</th><th>当前估值 (±1σ)</th><th>招标门槛/目标</th><th>状态</th></tr></thead>
            <tbody id="design-perf-tbody">${perfRowsHtml}</tbody>
          </table>
          <div id="design-diag-box" style="margin-top:12px;padding:9px;background:#091529;border:1px solid #244778;border-radius:4px;font-size:11.8px;line-height:1.5;">
            ${diagHtml}
          </div>
        </div>
      </div>
    `;
  }

function renderTestingWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;

  const pilotCards = A1.PILOTS.map(function (p, idx) {
    const sel = idx === STATE.selectedPilotIdx;
    return `<div class="card" style="border-color:${sel ? "#00f0ff" : "#244778"};cursor:pointer;" onclick="window.MIC_UI.selectPilot(${idx})">
      <div style="font-weight:700;color:${sel ? "#00f0ff" : "#eaf2ff"}">${sel ? "✓ " : ""}${p.name}</div>
      <div style="font-size:11.5px;color:#98b0d4;margin-top:4px;">${p.desc_zh}</div>
      <div style="font-family:var(--font-mono);font-size:11px;color:#e09f3e;margin-top:6px;">津贴：$${(p.cost_usd / 1e3).toFixed(0)}k / 阶段 | 技术：${(p.skill * 100).toFixed(0)}</div>
    </div>`;
  }).join("");

  const flawCards = STATE.flaws.map(function (fl) {
    if (!fl.discovered && fl.uncharted_before_discovery) {
      return `<div class="card" style="border-color:#ff4785;background:#241122;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="badge badge-uncharted">D7 迷雾：未知高速领域风险 (Uncharted High-Speed Regime Risk)</span>
          <span style="font-family:var(--font-mono);font-size:11px;color:#ff9ec4;">史实认知年份：${fl.known_from_year} 年</span>
        </div>
        <div style="margin-top:6px;font-size:12px;color:#ffd6e6;">您的新颖高速气动构型正踏入人类尚未掌握的跨/超音速未知禁区！必须通过【L2 开槽跨音速风洞】或【阶段 3 超音速俯冲试飞】才能揭开该隐患的真实面目！</div>
      </div>`;
    }
    const statusBadge = fl.fixed
      ? `<span class="badge badge-flight">✓ 已整改修复 (FIXED)</span>`
      : fl.discovered
      ? `<span class="badge" style="background:#451a16;color:#ff9c8f;border:1px solid #d94a38;">⚠️ 已暴露缺陷 (严重度 S${fl.severity})</span>`
      : `<span class="badge badge-sim">潜伏未检出 (请安排风洞或试飞)</span>`;

    return `<div class="card" style="border-color:${fl.fixed ? "#3bceac" : fl.discovered ? "#d94a38" : "#244778"};">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <b style="color:${fl.fixed ? "#3bceac" : "#00f0ff"}">${fl.true_title_zh}</b>
        ${statusBadge}
      </div>
      <div style="font-size:12px;color:#98b0d4;margin-bottom:8px;">${fl.true_desc_zh}</div>
      <div style="font-family:var(--font-mono);font-size:11.5px;color:#e09f3e;margin-bottom:8px;">
        整改方案：${fl.fix_action_zh}（费用 $${(fl.fix_cost_usd / 1e3).toFixed(0)}k，工期 +${Math.round(fl.fix_days * 0.65)} 天）
      </div>
      ${!fl.fixed ? `<button class="btn btn-green" onclick="window.MIC_APP_ACTIONS.fixFlaw('${fl.id}')">立即立项修形整改 ($${(fl.fix_cost_usd / 1e3).toFixed(0)}k) &rarr;</button>` : ""}
    </div>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title">4. 风洞试验、试飞中心与未知风险排雷 (WIND TUNNEL & FLIGHT TEST // SCREEN 4)</div>
        <div style="font-size:12px;color:#98b0d4;">通过 NACA 风洞与爱德华兹 4 阶段试飞收窄 ±1σ 误差棒，揭开【未知高速领域风险 (D7)】并在真机竞飞前完成修形！</div>
      </div>
      <button class="btn btn-green" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">完成试飞，进入爱德华兹真机竞飞 &rarr;</button>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title">步骤 A：预约 NACA 地面风洞试验 (WIND TUNNEL CAMPAIGNS)</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <button class="btn" onclick="window.MIC_APP_ACTIONS.runWindTunnel(1)">1. 运行 L1 低速亚音速风洞 ($180k, +8天) — 检验起降与低速稳定度</button>
          <button class="btn btn-brass" onclick="window.MIC_APP_ACTIONS.runWindTunnel(2)">2. 运行 L2 NACA 开槽喉道跨音速风洞 ($450k, +14天) — ★ 揪出跨音速激波阻力墙！</button>
          <button class="btn" onclick="window.MIC_APP_ACTIONS.runWindTunnel(3)">3. 运行 L3 超音速吹气式风洞与颤振台 ($780k, +19天) — 全面排查高速副翼反效</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">步骤 B：爱德华兹空军基地 4 阶段实机试飞 (EDWARDS AFB FLIGHT TEST)</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
          <button class="btn" onclick="window.MIC_APP_ACTIONS.runFlightTestPhase(1)">P1: 滑跑与首飞验证 (First Flight)</button>
          <button class="btn" onclick="window.MIC_APP_ACTIONS.runFlightTestPhase(2)">P2: 亚音速包线扩展 (Subsonic)</button>
          <button class="btn btn-brass" onclick="window.MIC_APP_ACTIONS.runFlightTestPhase(3)">P3: 跨/超音速俯冲穿音障 (Mach Dive)</button>
          <button class="btn" onclick="window.MIC_APP_ACTIONS.runFlightTestPhase(4)">P4: 高过载与武器打靶 (High-G)</button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">试飞员选派名册 (FICTIONAL 1950s TEST PILOT ROSTER — DECISION D9)</div>
      <div class="grid-3">${pilotCards}</div>
    </div>

    <div class="card">
      <div class="card-title">气动与工程隐患排雷看板 (HIDDEN FLAWS & UNCHARTED REGIME RISKS — DECISION D7)</div>
      <div class="grid-2">${flawCards || "<div>当前设计无潜伏高危缺陷！</div>"}</div>
    </div>
  `;
}

function renderProcurementWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const scen = A1.SHOWDOWN_SCENARIOS[STATE.scenarioId];

  const sigMach = STATE.inquiryLevel === 0 ? 0.14 : STATE.inquiryLevel === 1 ? 0.07 : 0.03;
  const sigPrice = STATE.inquiryLevel === 0 ? 180 : STATE.inquiryLevel === 1 ? 90 : 35;

  const rumorRows = scen.rivals.map(function (rv) {
    const h = A1.DATA.aircraft_hist && A1.DATA.aircraft_hist[rv.stem];
    const m = h ? h.oracle_perf.max_mach_alt : 1.35;
    const r = h ? (h.oracle_perf.combat_radius_m / 1852).toFixed(0) : 380;
    return `<tr>
      <td><b>${rv.company}</b> (${rv.designation})</td>
      <td>${rv.config_zh}</td>
      <td><span style="color:#00f0ff">M ${m.toFixed(2)} ± ${sigMach.toFixed(2)}</span></td>
      <td>${r} ± ${STATE.inquiryLevel === 0 ? 55 : 22} nmi</td>
      <td><span style="color:#e09f3e">$${(rv.price_usd / 1e3).toFixed(0)}k ± $${sigPrice}k</span></td>
    </tr>`;
  }).join("");

  let debriefHtml = `<div class="card" style="text-align:center;padding:22px;">
    <div style="font-size:14px;color:#98b0d4;margin-bottom:10px;">尚未执行二阶段真机同台竞飞 (Two-Stage Hardware Fly-Off)。设定下方报价后点击按钮立即开赛！</div>
    <button class="btn btn-green" style="font-size:14px;padding:10px 22px;" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">★ 启动爱德华兹真机同台竞飞 (RUN HARDWARE FLY-OFF) ★</button>
  </div>`;

  if (STATE.flyoffResults) {
    const resRows = STATE.flyoffResults.map(function (r, idx) {
      const sc = r.scores;
      return `<tr style="background:${r.isPlayer ? "rgba(0, 240, 255, 0.12)" : "transparent"}">
        <td><b>#${idx + 1}</b> ${idx === 0 ? "🏆" : ""}</td>
        <td><b style="color:${r.isPlayer ? "#00f0ff" : "#eaf2ff"}">${r.company} — ${r.designation}</b></td>
        <td>M ${r.perf.max_mach_alt.toFixed(2)} / ${(r.perf.combat_radius_m / 1852).toFixed(0)} nmi</td>
        <td>$${(r.price_usd / 1e3).toFixed(0)}k</td>
        <td>${sc.S_perf}</td>
        <td>${sc.S_cost}</td>
        <td>${sc.S_sched}</td>
        <td>${sc.S_risk}</td>
        <td>${sc.S_pol}</td>
        <td><b style="color:#3bceac;font-size:13px;">${sc.S_total}</b></td>
      </tr>`;
    }).join("");

    debriefHtml = `<div class="card" style="border-color:#3bceac;">
      <div class="card-title">五角大楼定标复盘报告 (SOURCE SELECTION DEBRIEF // DECISIONS D6 & D10)</div>
      <table class="bp-table">
        <thead><tr><th>名次</th><th>竞标厂商与原型机</th><th>实测极速/半径</th><th>单机报价</th><th>S_perf(性能)</th><th>S_cost(成本)</th><th>S_sched(进度)</th><th>S_risk(可靠性)</th><th>S_pol(声望)</th><th>总分 S_TOTAL</th></tr></thead>
        <tbody>${resRows}</tbody>
      </table>
    </div>`;
  }

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title">5. 五角大楼招标、截标前情报传闻与真机竞飞复盘 (PROCUREMENT & FLY-OFF // SCREEN 5)</div>
        <div style="font-size:12px;color:#98b0d4;">截标前可查阅《航空周刊》传闻或动用华盛顿联络官打探对手区间（D10）；定标采用两阶段真机同台竞飞（D6）！</div>
      </div>
    </div>

    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div class="card-title" style="margin:0;">截标前竞争对手媒体传闻与情报 (PRE-BID COMPETITOR RUMORS — DECISION D10)</div>
        <div style="display:flex;gap:6px;">
          <button class="btn ${STATE.inquiryLevel === 0 ? "btn-brass" : ""}" onclick="window.MIC_UI.setInquiry(0)">L0: 免费《航空周刊》传闻</button>
          <button class="btn ${STATE.inquiryLevel === 1 ? "btn-brass" : ""}" onclick="window.MIC_UI.setInquiry(1)">L1: 华盛顿联络官打探 (-4 政治资本)</button>
          <button class="btn ${STATE.inquiryLevel === 2 ? "btn-brass" : ""}" onclick="window.MIC_UI.setInquiry(2)">L2: 深度技术侦察 (-$150k)</button>
        </div>
      </div>
      <table class="bp-table">
        <thead><tr><th>竞争对手与代号</th><th>传闻气动构型</th><th>传闻最大马赫数 (±1σ)</th><th>传闻作战半径 (±1σ)</th><th>传闻单机报价区间 (±1σ)</th></tr></thead>
        <tbody>${rumorRows}</tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-title">我方商务报价与合同类型设定 (BID PRICING & CONTRACT TERMS)</div>
      <div class="grid-3">
        <div>
          <div class="slider-header"><span>我方单机出厂报价 (Unit Bid Price)</span><span class="s-val">$${(STATE.bidPriceUsd / 1e3).toFixed(0)}k (上限 $${(scen.unit_price_ceiling_usd / 1e3).toFixed(0)}k)</span></div>
          <input type="range" id="inp-bid-price" min="${Math.round(scen.unit_price_ceiling_usd * 0.55)}" max="${Math.round(scen.unit_price_ceiling_usd * 1.15)}" step="10000" value="${STATE.bidPriceUsd}">
        </div>
        <div>
          <div class="slider-header"><span>当前累计交付周期</span><span class="s-val">${STATE.schedDays} 天 (招标要求 ${scen.flyoff_days_budget} 天)</span></div>
          <div style="font-size:11.5px;color:#98b0d4;">风洞与缺陷整改会增加天数，但能大幅提高 S_perf 与 S_risk！</div>
        </div>
        <div style="display:flex;align-items:center;justify-content:flex-end;">
          <button class="btn btn-green" style="width:100%;padding:10px;" onclick="window.MIC_APP_ACTIONS.runHardwareFlyOff()">★ 提交原型机并开始真机竞飞 ★</button>
        </div>
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
    return `<div class="card">
      <div style="font-weight:700;color:#00f0ff;font-size:13px;">${q.vendor.name}</div>
      <div style="font-size:11.5px;color:#98b0d4;margin:5px 0 8px;">${q.vendor.specialty_zh}</div>
      <div style="font-family:var(--font-mono);font-size:11.5px;display:grid;grid-template-columns:1fr 1fr;gap:4px;">
        <div>研发立项费：<b style="color:#e09f3e">$${(q.nre_cost_usd / 1e6).toFixed(2)}M</b></div>
        <div>预计周期：<b>${q.dev_months} 个月</b></div>
        <div>单台采购价：<b>$${(q.unit_cost_usd / 1e3).toFixed(0)}k</b></div>
        <div>预估干重：<b>${q.est_mass_kg} kg</b></div>
        <div>研发延期风险：<b style="color:${q.failure_risk_pct > 25 ? "#d94a38" : "#3bceac"}">${q.failure_risk_pct}%</b></div>
      </div>
      <button class="btn btn-brass" style="margin-top:8px;width:100%" onclick="window.MIC_UI.commissionEngine('${q.vendor.id}', '${q.vendor.name}', ${q.nre_cost_usd})">点名委托 ${q.vendor.name.split(" ")[0]} 定制研发 &rarr;</button>
    </div>`;
  }).join("");

  const catalogRows = Object.keys(A1.DATA.engines_hist || {}).map(function (ek) {
    const e = A1.DATA.engines_hist[ek];
    const dryKn = ((e.thrust_dry_sl_N || 30000) / 1000).toFixed(1);
    const abKn = e.thrust_ab_sl_N ? (e.thrust_ab_sl_N / 1000).toFixed(1) + " kN" : "无加力";
    return `<tr>
      <td><b>${e.name || ek}</b></td>
      <td>${e.manufacturer || "US Vendor"}</td>
      <td>${dryKn} kN</td>
      <td><span style="color:#00f0ff">${abKn}</span></td>
      <td>${e.mass_kg || 1200} kg</td>
      <td><button class="btn" onclick="window.MIC_UI.equipCatalogEngine('${ek}')">装机选用</button></td>
    </tr>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title">3. 航空发动机目录与五巨头点名定制研发 (PROPULSION & VENDOR R&D // SCREEN 3 — DECISION D9)</div>
        <div style="font-size:12px;color:#98b0d4;">可直接选用 12 款史实成熟航发，或显式点名委托【普惠 / 通用电气 / 艾里逊 / 柯蒂斯-赖特 / 西屋】五大巨头定制新核心机！</div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">五大美国航发巨头定制委托报价对比 (NAMED ENGINE VENDOR COMMISSIONING — DECISION D9)</div>
      <div class="grid-3">${vendorCards}</div>
    </div>
    <div class="card">
      <div class="card-title">1945–1960 史实航空发动机目录 (HISTORICAL ENGINE CATALOG)</div>
      <table class="bp-table">
        <thead><tr><th>型号</th><th>原厂</th><th>最大军用推力 (Dry)</th><th>全加力推力 (Wet)</th><th>干重</th><th>操作</th></tr></thead>
        <tbody>${catalogRows}</tbody>
      </table>
    </div>
  `;
}

function renderTechAndCompanyWorkspace(host) {
  const A1 = window.MIC_APP_PART1;
  const STATE = A1.STATE;
  const rawNodes = (A1.DATA.tech_nodes && (A1.DATA.tech_nodes.nodes || A1.DATA.tech_nodes)) || [];
  const nodeList = Array.isArray(rawNodes) ? rawNodes.slice(0, 18) : [];

  const techRows = nodeList.map(function (t) {
    const yr = t.unlock_year || t.historical_year || 1950;
    const aot = yr > A1.SHOWDOWN_SCENARIOS[STATE.scenarioId].year;
    return `<tr>
      <td><b style="color:#00f0ff">${t.name || t.id}</b></td>
      <td>${t.branch || t.category || "Aero"}</td>
      <td>${yr} 年</td>
      <td><span class="badge ${aot ? "badge-uncharted" : "badge-flight"}">${aot ? "超前研发 (+惩罚)" : "时代已成熟"}</span></td>
    </tr>`;
  }).join("");

  const progRows = (A1.DATA.programs || []).map(function (p) {
    return `<tr>
      <td><b>${p.program_name || p.id}</b></td>
      <td>${p.customer || "USAF"}</td>
      <td>${p.issue_date || "1950"}</td>
      <td><span class="badge badge-tunnel">${STATE.forceFlyoffMode ? "两阶段真机竞飞 (D6 Default)" : (p.acquisition && p.acquisition.style) || "flyoff"}</span></td>
    </tr>`;
  }).join("");

  host.innerHTML = `
    <div class="panel-header">
      <div>
        <div class="panel-title">6 & 7. 全貌科技树 (1945–1960)、战役规则开关与 1960 沙盒延续 (DECISIONS D6, D7, D8)</div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">已锁定的五大口味机制实时开关 (CAMPAIGN RULE TOGGLES D6–D10)</div>
        <div style="display:flex;flex-direction:column;gap:10px;font-size:12.5px;">
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
            <input type="checkbox" ${STATE.forceFlyoffMode ? "checked" : ""} onchange="window.MIC_UI.toggleRule('forceFlyoffMode', this.checked)">
            <span><b>D6 采购模式：</b>默认将全部 16 个主战项目统一为【两阶段真机同台竞飞 (Fly-Off)】</span>
          </label>
          <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
            <input type="checkbox" ${STATE.hindsightMode ? "checked" : ""} onchange="window.MIC_UI.toggleRule('hindsightMode', this.checked)">
            <span><b>D7 历史后见之明开关：</b>关闭时，超前时代的隐患显示为【未知高速领域风险】直至风洞/试飞揭晓</span>
          </label>
          <div style="margin-top:6px;padding:10px;background:#091529;border:1px solid #3bceac;border-radius:4px;">
            <div style="font-weight:700;color:#3bceac;margin-bottom:6px;">D8 1960 战役终局与沙盒延续 (POST-1960 SANDBOX CONTINUATION)：</div>
            <button class="btn btn-green" onclick="window.MIC_UI.trigger1960Sandbox()">模拟推进至 1960-12-31 结算并生成 1961+ 动态沙盒招标书 &rarr;</button>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">1945–1960 全部 16 个史实军方招标项目库</div>
        <div style="max-height:240px;overflow-y:auto;">
          <table class="bp-table">
            <thead><tr><th>项目代号</th><th>军种</th><th>发布日期</th><th>定标流程 (D6)</th></tr></thead>
            <tbody>${progRows}</tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">1945–1960 全貌科技树节点预览 (开局全貌可见 — DECISION D7)</div>
      <table class="bp-table">
        <thead><tr><th>科技节点</th><th>学科分支</th><th>史实年份</th><th>超前状态</th></tr></thead>
        <tbody>${techRows}</tbody>
      </table>
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

  window.addEventListener("mouseup", function () {
    if (isDragging) {
      isDragging = false;
      activeHandle = null;
      cvs.style.cursor = "crosshair";
    }
  });

  cvs.addEventListener("touchstart", function (ev) {
    const pos = getCanvasPos(ev);
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
    if (bp) bp.addEventListener("input", (e) => { STATE.bidPriceUsd = Number(e.target.value); renderAll(); });
  } else if (STATE.activeWorkspace === "propulsion") {
    renderPropulsionWorkspace(host);
  } else {
    renderTechAndCompanyWorkspace(host);
  }
}

window.MIC_UI = {
  goWorkspace: function (ws) { window.MIC_APP_PART1.STATE.activeWorkspace = ws; renderAll(); },
  setCanvasTab: function (tab) { window.MIC_APP_PART1.STATE.activeCanvasTab = tab; renderAll(); },
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
  window.MIC_APP_ACTIONS.loadScenario("1952_interceptor");
});
window.addEventListener("resize", function () {
  if (window.MIC_APP_PART1.STATE.activeWorkspace === "design") renderAll();
});
