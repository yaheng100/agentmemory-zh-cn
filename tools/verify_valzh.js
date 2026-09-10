// 功能级校验：在 Node 沙箱里执行 viewer 脚本，取 VAL_ZH / valZh 做断言
const fs = require('fs');
const f = process.argv[2];
const html = fs.readFileSync(f, 'utf8');
const src = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
  .map(m => m[1]).join('\n');

// 用 vm 在上文中执行，拿不到内部 var；改用“截取 VAL_ZH 定义 + valZh 定义”后 eval
const iVal = src.indexOf('var VAL_ZH');
const iFn  = src.indexOf('function valZh');
if (iVal < 0 || iFn < 0) { console.log('[FAIL] 未找到 VAL_ZH / valZh'); process.exit(1); }
const iFnEnd = src.indexOf('\n    }', iFn);
const snippet = src.slice(iVal, iFnEnd + 6);
let valZh;
try {
  valZh = eval('(function(){' + snippet + '; return valZh;})()');
} catch (e) { console.log('[FAIL] eval 失败: ' + e.message); process.exit(1); }

const cases = [
  ['architecture', '架构'], ['fact', '事实'], ['workflow', '流程'], ['bug', '缺陷'],
  ['pattern', '模式'], ['preference', '偏好'],
  ['observe', '观察'], ['remember', '记住'], ['consolidate', '整合'], ['delete', '删除'],
  ['supersedes', '取代'], ['extends', '扩展'],
  ['closed', '已关闭'], ['open', '已断开'], ['half-open', '半开'],
  ['running', '运行中'], ['starting', '启动中'], ['stopped', '已停止'],
  ['active', '进行中'], ['completed', '已完成'], ['done', '已完成'],
  ['pending', '待处理'], ['blocked', '受阻'], ['cancelled', '已取消'],
  ['prompt', '提示词'], ['response', '响应'], ['tool_call', '工具调用'],
  ['tool_error', '工具错误'], ['tool_result', '工具结果'],
];
let bad = 0;
for (const [k, want] of cases) {
  const got = valZh(k);
  if (got !== want) { console.log('  [!] ' + k + ' => ' + got + ' (期望 ' + want + ')'); bad++; }
}
console.log(bad === 0 ? '[OK] VAL_ZH 全部 ' + cases.length + ' 项断言通过' : '[FAIL] ' + bad + ' 项不符');

// 未知值应原样返回（不破坏逻辑）
const passthrough = valZh('some_unknown_value');
console.log(passthrough === 'some_unknown_value' ? '[OK] 未知值原样透传' : '[FAIL] 未知值被改写: ' + passthrough);

// 确认渲染点已切换，且 CSS 类未被误改
const checks = [
  ["esc(cb.state)", false], ["valZh(cb.state)", true],
  ["esc(w.status)", false], ["valZh(w.status)", true],
  ["esc(s.status)", false], ["valZh(s.status)", true],
  ["esc(a.status)", false], ["valZh(a.status)", true],
  ["esc(m.type)", false], ["valZh(m.type)", true],
  ["replay-event-' + esc(ev.kind)", true],   // CSS 类必须保持英文
  ["esc(ev.kind) + '</span>", false],
];
let bad2 = 0;
for (const [needle, shouldExist] of checks) {
  const has = src.includes(needle);
  if (has !== shouldExist) { console.log('  [!] ' + JSON.stringify(needle) + ' 存在=' + has + ' 期望=' + shouldExist); bad2++; }
}
console.log(bad2 === 0 ? '[OK] 渲染点切换全部正确（含 CSS 类未被误改）' : '[FAIL] ' + bad2 + ' 项不符');
process.exit(bad === 0 && bad2 === 0 ? 0 : 1);
