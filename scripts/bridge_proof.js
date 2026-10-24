⌄
⌄
⌄
⌄
⌄
// Bridge proof: run Wendy Face's PSVC sealer (extracted verbatim from wendy.html)
// in Node, then validate the container with the repo's Python psvc_reference.
const fs = require('fs');

// --- extract the two functions from the live page so we test EXACTLY what ships ---
const html = fs.readFileSync('/home/z/my-project/wendy-repo/wendy.html', 'utf8');
const grab = (name) => {
  const start = html.indexOf(`function ${name}(`);
  if (start < 0) throw new Error(`${name} not found in wendy.html`);
  let depth = 0, i = html.indexOf('{', start);
  const open = i;
  for (; i < html.length; i++) {
    if (html[i] === '{') depth++;
    else if (html[i] === '}') { depth--; if (!depth) break; }
  }
  return html.slice(start, i + 1);
};
eval(grab('embedText') + '\n' + grab('sealPSVC'));

(async () => {
  // determinism check
  const v1 = embedText('Wendy, transcribe this voice note.');
  const v2 = embedText('Wendy, transcribe this voice note.');
  const same = v1.every((x, i) => x === v2[i]);
  console.log('embed determinism:', same ? 'PASS' : 'FAIL');
  let norm = 0; for (const x of v1) norm += x * x;
  console.log('vector norm:', Math.sqrt(norm).toFixed(6), 'dim:', v1.length);

  if (typeof CompressionStream === 'undefined') {
    console.log('CompressionStream missing in this Node; patching via zlib...');
    const zlib = require('zlib');
    globalThis.CompressionStream = class {
      constructor(fmt) { if (fmt !== 'deflate') throw new Error('bad fmt'); }
      get writable() { return zlib.createDeflate(); }
      get readable() { return this._writable; }
    };
    // Simpler: do it manually below instead of patching streams.
  }

  const blob = await sealPSVC(v1);
  fs.writeFileSync('/tmp/js_sealed.psvc', Buffer.from(blob));
  console.log('sealed .psvc:', blob.byteLength, 'bytes');
  console.log('magic:', Buffer.from(blob.slice(0, 4)).toString('ascii'));
})().catch(e => { console.error('FAIL:', e); process.exit(1); });