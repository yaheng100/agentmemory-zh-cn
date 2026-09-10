// 校验 viewer index.html 内联脚本语法（把 <script> 内容抽出来单独交给 node --check 是行不通的，
// 这里用 new Function 包裹来触发解析，只检查语法不执行）
const fs = require('fs');
const f = process.argv[2];
const html = fs.readFileSync(f, 'utf8');
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
console.log('内联 script 块数量:', scripts.length, '总字符:', scripts.reduce((a, s) => a + s.length, 0));
let ok = 0, bad = 0;
scripts.forEach((s, i) => {
  try {
    new Function(s);               // 仅解析，不执行
    ok++;
  } catch (e) {
    bad++;
    console.log('  [!] 第 ' + (i + 1) + ' 个 script 语法错误: ' + e.message);
    // 打印出错位置附近
    const m = /(\d+):(\d+)/.exec(e.stack || '');
    if (m) {
      const lines = s.split('\n');
      const ln = parseInt(m[1], 10);
      console.log('     大约在第 ' + ln + ' 行附近:');
      for (let k = Math.max(0, ln - 3); k < Math.min(lines.length, ln + 2); k++)
        console.log('       ' + (k + 1) + ' | ' + lines[k].slice(0, 160));
    }
  }
});
console.log(ok > 0 && bad === 0 ? '[OK] 全部脚本语法通过' : ('[FAIL] 通过 ' + ok + ' / 失败 ' + bad));
process.exit(bad === 0 ? 0 : 1);
