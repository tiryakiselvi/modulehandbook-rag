const pptxgen = require('pptxgenjs');
const path = require('path');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Modulhandbuch-RAG Team';
pptx.subject = 'Seminar Suchmaschinen, LMU';
pptx.title = 'Modulhandbuch-RAG';
pptx.company = 'LMU';
pptx.lang = 'de-DE';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'de-DE'
};
pptx.defineSlideMaster({
  title: 'LIGHT',
  background: { color: 'F8FAFF' },
  objects: [
    { rect: { x: 0.15, y: 0.15, w: 13.03, h: 7.2, rectRadius: 0.16, fill: { color: 'FFFFFF', transparency: 2 }, line: { color: 'E8ECF7', transparency: 15, width: 0.8 }, shadow: { type: 'outer', color: 'AAB3C8', opacity: 0.16, blur: 3, angle: 45, distance: 1.2 } } },
    { ellipse: { x: 10.4, y: 4.4, w: 3.5, h: 3.5, fill: { color: 'C9C2FF', transparency: 72 }, line: { color: 'C9C2FF', transparency: 100 } } },
    { ellipse: { x: 10.8, y: -0.5, w: 2.6, h: 2.6, fill: { color: 'BFEAFF', transparency: 76 }, line: { color: 'BFEAFF', transparency: 100 } } },
  ],
  slideNumber: { x: 12.35, y: 7.06, w: 0.45, h: 0.18, color: '9AA5BD', fontFace: 'Aptos', fontSize: 8, align: 'right' }
});

const C = {
  navy: '07142F',
  body: '526078',
  muted: '71809A',
  blue: '5F7CFF',
  blue2: '6CA9FF',
  purple: '9B74FF',
  cyan: '67D7FF',
  lavender: 'EEEAFE',
  paleBlue: 'EAF3FF',
  line: 'E2E7F2',
  white: 'FFFFFF',
  green: '50C878',
  orange: 'FFB65C',
  red: 'FF6B6B'
};

const shadow = { type: 'outer', color: '9CA7BD', opacity: 0.18, blur: 2.5, angle: 45, distance: 1.1 };

function addTitle(slide, title, subtitle, number) {
  if (number) addPill(slide, 0.62, 0.48, 0.55, 0.28, number, C.blue, 'EEF1FF', 9);
  slide.addText(title, { x: 0.68, y: 0.72, w: 8.7, h: 0.64, fontFace: 'Aptos Display', fontSize: 34, bold: true, color: C.navy, margin: 0, breakLine: false, fit: 'shrink' });
  if (subtitle) slide.addText(subtitle, { x: 0.72, y: 1.42, w: 8.7, h: 0.38, fontFace: 'Aptos', fontSize: 16, color: C.body, margin: 0, fit: 'shrink' });
}

function addPill(slide, x, y, w, h, text, textColor=C.blue, fillColor='F2F4FF', fontSize=10, icon='') {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fillColor, transparency: 0 }, line: { color: textColor, transparency: 72, width: 0.8 } });
  slide.addText(icon ? `${icon}  ${text}` : text, { x: x+0.05, y: y+0.03, w: w-0.1, h: h-0.06, fontFace: 'Aptos', fontSize, color: textColor, bold: true, align: 'center', valign: 'mid', margin: 0, fit: 'shrink' });
}

function addCard(slide, x, y, w, h, opts={}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: opts.radius || 0.12,
    fill: { color: opts.fill || C.white, transparency: opts.transparency ?? 2 },
    line: { color: opts.line || C.line, transparency: opts.lineTransparency ?? 10, width: opts.lineWidth || 0.8 },
    shadow: opts.shadow === false ? undefined : shadow
  });
}

function addIcon(slide, x, y, symbol, fill='EEF1FF', color=C.blue, size=0.46) {
  slide.addShape(pptx.ShapeType.ellipse, { x, y, w: size, h: size, fill: { color: fill }, line: { color: fill, transparency: 100 }, shadow: { type: 'outer', color: color, opacity: 0.11, blur: 1.2, angle: 45, distance: 0.5 } });
  slide.addText(symbol, { x, y: y+0.005, w: size, h: size-0.01, align: 'center', valign: 'mid', fontFace: 'Aptos', fontSize: size*25, color, bold: true, margin: 0 });
}

function addBullets(slide, items, x, y, w, h, fontSize=18, color=C.body, bulletColor=C.blue, gap=7) {
  const runs = [];
  items.forEach((item, i) => {
    runs.push({ text: item, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1, color, fontSize, paraSpaceAfterPt: gap } });
  });
  slide.addText(runs, { x, y, w, h, fontFace: 'Aptos', fontSize, color, margin: 0.02, breakLine: false, fit: 'shrink', bulletColor });
}

function addFooter(slide, text='Seminar Suchmaschinen · LMU') {
  slide.addText(text, { x: 0.72, y: 6.98, w: 4.5, h: 0.2, fontFace: 'Aptos', fontSize: 9, color: '8B96AD', margin: 0 });
}

function addSectionLabel(slide, x, y, text, icon='✦') {
  addIcon(slide, x, y, icon, 'EEF1FF', C.blue, 0.42);
  slide.addText(text, { x: x+0.55, y: y+0.03, w: 2.8, h: 0.34, fontFace: 'Aptos Display', fontSize: 17, bold: true, color: C.navy, margin: 0, fit: 'shrink' });
}

// Slide 1
{
  const slide = pptx.addSlide('LIGHT');
  slide.addText('Modulhandbuch-RAG', { x: 0.72, y: 2.03, w: 7.8, h: 0.78, fontFace: 'Aptos Display', fontSize: 39, bold: true, color: C.navy, margin: 0, fit: 'shrink' });
  slide.addText('Struktur-aware Retrieval für LMU-Modulhandbücher', { x: 0.76, y: 2.91, w: 7.2, h: 0.42, fontFace: 'Aptos', fontSize: 18, color: C.body, margin: 0 });
  addPill(slide, 0.76, 3.66, 2.65, 0.43, 'Deutsch · English · Türkçe', C.body, 'FFFFFF', 11, '◎');
  addPill(slide, 0.76, 4.22, 2.5, 0.43, 'BM25 · Dense · Hybrid', C.body, 'FFFFFF', 11, '≋');
  slide.addText('Seminar Suchmaschinen', { x: 0.78, y: 6.52, w: 3.1, h: 0.25, fontSize: 11, color: '7A879F', margin: 0 });

  // Right-side document/search/evidence motif
  addCard(slide, 8.15, 1.68, 1.38, 1.45, { fill: 'FFFFFF' });
  addIcon(slide, 8.55, 1.97, '▤', 'F2F4FF', C.muted, 0.52);
  slide.addShape(pptx.ShapeType.line, { x: 8.48, y: 2.66, w: 0.76, h: 0, line: { color: 'D6DCE9', width: 2 } });
  slide.addShape(pptx.ShapeType.line, { x: 8.48, y: 2.84, w: 0.54, h: 0, line: { color: 'E3E7F0', width: 2 } });

  addCard(slide, 9.65, 1.2, 1.92, 1.92, { fill: 'EAF3FF', line: 'B8D9FF' });
  addIcon(slide, 10.28, 1.56, '⌕', 'EAF3FF', C.blue, 0.66);
  slide.addShape(pptx.ShapeType.line, { x: 10.05, y: 2.42, w: 1.1, h: 0, line: { color: 'C5D9F6', width: 3 } });
  slide.addShape(pptx.ShapeType.line, { x: 10.05, y: 2.68, w: 0.76, h: 0, line: { color: 'D7E4F7', width: 3 } });

  addCard(slide, 11.82, 2.04, 0.88, 0.92, { fill: 'FFFFFF' });
  slide.addText('•••\n≡', { x: 12.02, y: 2.22, w: 0.48, h: 0.52, fontSize: 16, color: C.purple, bold: true, align: 'center', valign: 'mid', margin: 0 });

  addCard(slide, 8.85, 3.62, 2.45, 1.05, { fill: 'FFFFFF' });
  addIcon(slide, 9.1, 3.9, '✦', 'EDE8FF', C.purple, 0.4);
  slide.addText('EVIDENZ GEFUNDEN', { x: 9.62, y: 3.95, w: 1.4, h: 0.22, fontSize: 10, bold: true, color: C.purple, margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 9.62, y: 4.3, w: 1.24, h: 0, line: { color: 'E0DBF7', width: 3 } });

  addCard(slide, 8.1, 4.95, 1.72, 0.83, { fill: 'FFFFFF' });
  slide.addText('“', { x: 8.33, y: 5.12, w: 0.35, h: 0.35, fontSize: 28, color: C.blue, bold: true, margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 8.7, y: 5.28, w: 0.78, h: 0, line: { color: 'DCE5F6', width: 3 } });

  addCard(slide, 10.0, 4.95, 1.72, 0.83, { fill: 'FFFFFF' });
  slide.addText('“', { x: 10.22, y: 5.12, w: 0.35, h: 0.35, fontSize: 28, color: C.purple, bold: true, margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 10.6, y: 5.28, w: 0.78, h: 0, line: { color: 'E5DDF7', width: 3 } });
}

// Slide 2
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Problem & Ziel', '', '02');
  addCard(slide, 0.72, 1.95, 5.35, 4.35);
  addBullets(slide, [
    'Modulhandbücher sind lang, heterogen und halb-strukturiert',
    'Nutzer:innen stellen Fragen in natürlicher Sprache',
    'Reine PDF-Suche liefert oft unpräzise Treffer',
    'Generative Antworten sind nur nützlich, wenn die Evidenz stimmt'
  ], 1.05, 2.35, 4.65, 3.55, 19, C.body, C.blue, 12);

  addCard(slide, 6.7, 1.75, 5.73, 2.65, { fill: 'EEF5FF', line: 'D7E5FF' });
  addSectionLabel(slide, 7.08, 2.09, 'Unser Ziel', '◎');
  slide.addText('Die richtige answer-bearing evidence finden: präzise, nachvollziehbar und zitierbar.', { x: 7.08, y: 2.82, w: 4.9, h: 1.05, fontFace: 'Aptos', fontSize: 21, color: C.navy, bold: false, margin: 0, breakLine: false, fit: 'shrink' });

  const cards = [
    ['▤', 'Mehrere\nDokumente'], ['◯', 'Natürliche\nSprache'], ['✓', 'Transparente\nEvidenz']
  ];
  cards.forEach((d, i) => {
    const x = 6.75 + i*1.92;
    addCard(slide, x, 4.72, 1.63, 1.35);
    addIcon(slide, x+0.53, 4.92, d[0], 'EEF3FF', i===1 ? C.purple : C.blue, 0.52);
    slide.addText(d[1], { x: x+0.15, y: 5.55, w: 1.33, h: 0.42, fontSize: 13, bold: true, color: C.navy, align: 'center', margin: 0, fit: 'shrink' });
  });
  addFooter(slide);
}

// Slide 3
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Systemüberblick', 'Von Dokumenten zur belegten Antwort', '03');
  const steps = [
    ['▤', 'Ingestion', 'PDF, TXT, Markdown'],
    ['✦', 'Cleaning', 'Text extrahieren und normalisieren'],
    ['⬡', 'Chunking', 'naive · module · field'],
    ['⌕', 'Retrieval', 'BM25 · Dense · Hybrid'],
    ['✓', 'Evidence', 'Top-k relevante Chunks'],
    ['◌', 'Antwort', 'optional mit LLM']
  ];
  const startX = 0.62, y = 2.25, w = 1.83, h = 2.48, gap = 0.24;
  steps.forEach((s, i) => {
    const x = startX + i*(w+gap);
    addCard(slide, x, y, w, h);
    addIcon(slide, x+0.64, y+0.3, s[0], 'EEF1FF', i%2 ? C.purple : C.blue, 0.55);
    slide.addText(s[1], { x: x+0.17, y: y+1.08, w: w-0.34, h: 0.34, fontSize: 16, bold: true, color: C.navy, align: 'center', margin: 0, fit: 'shrink' });
    slide.addShape(pptx.ShapeType.line, { x: x+0.55, y: y+1.56, w: 0.73, h: 0, line: { color: i%2 ? 'C8B7FF' : 'A9CFFF', width: 3 } });
    slide.addText(s[2], { x: x+0.18, y: y+1.82, w: w-0.36, h: 0.48, fontSize: 11.5, color: C.body, align: 'center', valign: 'mid', margin: 0, fit: 'shrink' });
    if (i < steps.length-1) slide.addText('→', { x: x+w+0.02, y: y+1.08, w: 0.2, h: 0.35, fontSize: 18, color: C.blue, bold: true, margin: 0, align: 'center' });
  });
  addCard(slide, 2.7, 5.36, 7.95, 0.84, { shadow: false });
  addIcon(slide, 3.02, 5.55, '!', 'EEF1FF', C.purple, 0.42);
  slide.addText('Wichtig: Der Kernbeitrag ist die Evidenzsuche, nicht nur die Generierung.', { x: 3.58, y: 5.58, w: 6.7, h: 0.3, fontSize: 16, color: C.body, margin: 0, fit: 'shrink' });
  addFooter(slide);
}

// Slide 4
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Retrieval & Evaluation', 'Drei Chunking-Strategien, drei Retriever, klare Metriken', '04');
  const cols = [
    { x:0.72, icon:'≋', title:'Chunking', bullets:['naive','module','field'], note:'Field-Level-Chunks liefern häufig präzisere Evidenz.' },
    { x:4.48, icon:'⌕', title:'Retriever', bullets:['BM25','Dense Retrieval','Hybrid Retrieval'], note:'Dense und Hybrid helfen bei semantischen und mehrsprachigen Fragen.' },
    { x:8.24, icon:'▥', title:'Metriken', bullets:['Hit@1','MRR','nDCG@k','Precision@k / Recall@k'], note:'Bewertet wird die gefundene Evidenz.' }
  ];
  cols.forEach((c, idx) => {
    addCard(slide, c.x, 2.02, 3.35, 3.94);
    addIcon(slide, c.x+0.3, 2.33, c.icon, 'EEF1FF', idx===1 ? C.purple : C.blue, 0.52);
    slide.addText(c.title, { x: c.x+0.96, y: 2.39, w: 2.0, h: 0.35, fontSize: 20, bold: true, color: C.navy, margin: 0 });
    addBullets(slide, c.bullets, c.x+0.45, 3.12, 2.5, 1.5, 17, C.navy, C.blue, 7);
    slide.addShape(pptx.ShapeType.line, { x: c.x+0.38, y: 4.85, w: 2.6, h: 0, line: { color: C.line, width: 1.2 } });
    addIcon(slide, c.x+0.35, 5.08, idx===0?'!':idx===1?'✦':'▥', 'F3F1FF', idx===1?C.purple:C.blue, 0.38);
    slide.addText(c.note, { x: c.x+0.87, y: 5.08, w: 2.15, h: 0.55, fontSize: 11.5, color: C.body, margin: 0, fit: 'shrink' });
  });
  addCard(slide, 0.72, 6.18, 10.87, 0.62, { shadow: false });
  addIcon(slide, 0.95, 6.28, '⚗', 'EDE8FF', C.purple, 0.38);
  slide.addText('Ablation: BM25-Baseline vs. Section-Boosting', { x: 1.47, y: 6.33, w: 5.5, h: 0.2, fontSize: 14, bold: true, color: C.navy, margin: 0 });
  addFooter(slide);
}

// Slide 5
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Mehrsprachig & natürlich', 'Fragen müssen weder Modulnummer noch exakten Modultitel nennen', '05');
  const qcards = [
    { x:0.72, lang:'Deutsch', q:'Welche Veranstaltung behandelt Information Retrieval?' },
    { x:4.45, lang:'English', q:'Which course covers information retrieval?' },
    { x:8.18, lang:'Türkçe', q:'Bilgi erişimi ile ilgili hangi ders var?' }
  ];
  qcards.forEach((c, i) => {
    addCard(slide, c.x, 2.03, 3.35, 1.87);
    addIcon(slide, c.x+0.3, 2.28, '◎', 'EEF4FF', C.blue, 0.46);
    slide.addText(c.lang, { x:c.x+0.88, y:2.34, w:1.6, h:0.3, fontSize:17, bold:true, color:C.blue, margin:0 });
    slide.addText('“', { x:c.x+0.28, y:2.94, w:0.38, h:0.36, fontSize:27, bold:true, color:i===2?C.purple:C.blue, margin:0 });
    slide.addText(c.q, { x:c.x+0.72, y:2.9, w:2.3, h:0.7, fontSize:15.5, color:C.navy, margin:0, fit:'shrink', valign:'mid' });
  });
  addCard(slide, 0.72, 4.3, 10.82, 1.58);
  addIcon(slide, 1.05, 4.73, '✦', 'EDE8FF', C.purple, 0.56);
  addBullets(slide, [
    'Explizite Modulnamen helfen, sind aber nicht zwingend nötig',
    'Dense und Hybrid verstehen semantisch ähnliche Formulierungen',
    'BM25 ist besonders stark, wenn die Frage deutsche Handbuchbegriffe trifft'
  ], 1.86, 4.59, 8.95, 1.0, 15.5, C.body, C.blue, 4);
  addPill(slide, 0.72, 6.16, 2.45, 0.43, 'Deutsch: Auto / Hybrid', C.blue, 'FFFFFF', 10.5, '≋');
  addPill(slide, 3.38, 6.16, 3.3, 0.43, 'English / Türkçe: Dense / Hybrid', C.purple, 'FFFFFF', 10.5, '⌘');
  addFooter(slide);
}

// Slide 6
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Mehrere Modulhandbücher', 'Die Auswahl ist automatisch möglich, bleibt aber transparent', '06');
  addCard(slide, 0.72, 2.02, 5.85, 3.82);
  addSectionLabel(slide, 1.06, 2.32, 'Recommended Demo Corpus', '▤');
  addBullets(slide, [
    'Computerlinguistik Bachelor',
    'Computerlinguistik Master',
    'Informatik Bachelor, integriertes Anwendungsfach',
    'Informatik Master, Beginn WiSe'
  ], 1.14, 3.22, 4.92, 2.06, 16.5, C.body, C.blue, 8);

  addCard(slide, 6.85, 2.02, 5.55, 3.82);
  addSectionLabel(slide, 7.2, 2.32, 'Automatische Auswahl', '✦');
  addBullets(slide, [
    '„Master Computerlinguistik“ → CL Master',
    '„Informatik Bachelor“ → integriertes Anwendungsfach',
    '„Nebenfach 60 ECTS“ → passende Nebenfachvariante',
    '„Beginn im SoSe“ → Informatik Master SoSe'
  ], 7.28, 3.22, 4.5, 2.06, 16, C.body, C.purple, 8);

  addCard(slide, 0.72, 6.12, 11.68, 0.58, { shadow:false });
  slide.addText('Ohne Studiengangsangabe wird der empfohlene Vier-Dokumente-Korpus durchsucht. Die Quelle jedes Treffers bleibt sichtbar.', { x:1.05, y:6.28, w:11.0, h:0.22, fontSize:13.2, color:C.body, margin:0, fit:'shrink' });
  addFooter(slide);
}

// Slide 7
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Interface', 'Modern, clean, verspielt und vollständig transparent', '07');
  slide.addText('Das Texteingabefeld ist bewusst abgerundet.', { x:0.76, y:3.65, w:2.8, h:0.7, fontSize:17, color:C.body, margin:0, fit:'shrink' });
  addIcon(slide, 0.78, 3.02, '✦', 'EDE8FF', C.purple, 0.55);

  // Browser frame
  addCard(slide, 3.7, 1.18, 8.75, 5.45, { fill:'FBFCFF', line:'D7DDF0' });
  slide.addShape(pptx.ShapeType.line, { x:3.7, y:1.68, w:8.75, h:0, line:{color:'E2E7F2', width:1} });
  ['FF6B6B','FFB65C','50C878'].forEach((color,i)=>slide.addShape(pptx.ShapeType.ellipse,{x:3.93+i*0.18,y:1.4,w:0.09,h:0.09,fill:{color},line:{color,transparency:100}}));
  slide.addText('≋  Modulhandbuch-RAG', { x:4.45, y:1.85, w:2.7, h:0.26, fontSize:15, bold:true, color:C.navy, margin:0 });

  // Rounded input
  slide.addShape(pptx.ShapeType.roundRect, { x:4.5, y:2.34, w:7.25, h:0.62, rectRadius:0.2, fill:{color:'FFFFFF'}, line:{color:'B9C6FF',width:1.1}, shadow });
  slide.addText('Stelle eine Frage zum Modulhandbuch …', { x:4.78, y:2.53, w:5.7, h:0.2, fontSize:13, color:'7C89A2', margin:0 });
  slide.addShape(pptx.ShapeType.ellipse, { x:11.13, y:2.42, w:0.46, h:0.46, fill:{color:C.blue}, line:{color:C.blue,transparency:100} });
  slide.addText('→', { x:11.13, y:2.48, w:0.46, h:0.26, fontSize:16, bold:true, color:'FFFFFF', align:'center', margin:0 });

  const controls = [
    ['Sprache',4.5,3.2,1.35], ['Korpus',5.98,3.2,1.35], ['Retriever',7.46,3.2,1.45], ['Top-k',9.04,3.2,1.15], ['Section Boost',10.32,3.2,1.43]
  ];
  controls.forEach(c=>addPill(slide,c[1],c[2],c[3],0.36,c[0],C.body,'FFFFFF',9.5));
  ['Deutsch','English','Türkçe'].forEach((t,i)=>addPill(slide,4.5+i*0.9,3.72,0.82,0.32,t,i===0?C.blue:C.body,i===0?'EEF1FF':'FFFFFF',8.5));
  ['Auto','BM25','Dense','Hybrid'].forEach((t,i)=>addPill(slide,7.45+i*0.76,3.72,0.69,0.32,t,i===0?C.blue:C.body,i===0?'EEF1FF':'FFFFFF',8.5));

  const rows = [
    ['1','WP3 · Information Retrieval','Inhalte','0.92'],
    ['2','WP3 · Information Retrieval','Form der Modulprüfung','0.87'],
    ['3','WP2 · Grundlagen','Lernziele','0.78']
  ];
  rows.forEach((r,i)=>{
    const y=4.38+i*0.58;
    addCard(slide,4.5,y,7.25,0.48,{shadow:false,fill:'FFFFFF'});
    addPill(slide,4.68,y+0.09,0.45,0.28,r[0],C.blue,'EEF1FF',8.5);
    slide.addText(r[1],{x:5.32,y:y+0.12,w:2.75,h:0.18,fontSize:10.5,color:C.navy,margin:0,fit:'shrink'});
    slide.addText(r[2],{x:8.2,y:y+0.12,w:2.5,h:0.18,fontSize:10.5,color:C.body,margin:0,fit:'shrink'});
    slide.addText(r[3],{x:10.95,y:y+0.12,w:0.5,h:0.18,fontSize:10.5,color:C.body,align:'right',margin:0});
  });
  addFooter(slide);
}

// Slide 8
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Aktueller BM25-Benchmark', '25 Queries · top-k = 3 · veröffentlichter Stand des Repos', '08');

  const data = [
    {label:'naive', value:0.760, color:'A9CFFF'},
    {label:'module', value:0.960, color:'8B7CFF'},
    {label:'field', value:0.840, color:'6CA9FF'}
  ];
  addCard(slide,0.72,2.02,7.15,3.9);
  slide.addText('Hit@1, Modul-Level-Relevanz', { x:1.1, y:2.35, w:4.8, h:0.35, fontSize:20, bold:true, color:C.navy, margin:0 });
  data.forEach((d,i)=>{
    const y=3.08+i*0.78;
    slide.addText(d.label,{x:1.1,y:y+0.08,w:0.92,h:0.2,fontSize:14,color:C.body,margin:0});
    slide.addShape(pptx.ShapeType.roundRect,{x:2.15,y,w:4.6,h:0.38,rectRadius:0.08,fill:{color:'EEF1F7'},line:{color:'EEF1F7',transparency:100}});
    slide.addShape(pptx.ShapeType.roundRect,{x:2.15,y,w:4.6*d.value,h:0.38,rectRadius:0.08,fill:{color:d.color},line:{color:d.color,transparency:100}});
    slide.addText(d.value.toFixed(3),{x:6.92,y:y+0.06,w:0.58,h:0.22,fontSize:14,bold:true,color:C.navy,align:'right',margin:0});
  });
  slide.addText('Interpretation: Module-Level-Chunking ist am stärksten, wenn nur das richtige Modul gesucht wird.', { x:1.1, y:5.33, w:6.2, h:0.35, fontSize:12.5, color:C.body, margin:0, fit:'shrink' });

  addCard(slide,8.15,2.02,4.25,3.9,{fill:'F4F1FF',line:'E1D9FF'});
  addSectionLabel(slide,8.5,2.34,'Strikte Field-Relevanz','✓');
  slide.addText('0.680', { x:8.5, y:3.15, w:2.05, h:0.78, fontSize:43, bold:true, color:C.purple, margin:0 });
  slide.addText('Hit@1', { x:10.28, y:3.56, w:1.2, h:0.25, fontSize:15, color:C.body, margin:0 });
  slide.addShape(pptx.ShapeType.line,{x:8.5,y:4.18,w:3.2,h:0,line:{color:'D8CFFF',width:1.2}});
  slide.addText('MRR 0.733\nnDCG@3 0.735\nRecall@3 0.780', { x:8.5, y:4.45, w:2.5, h:0.98, fontSize:16, color:C.navy, margin:0, breakLine:false, fit:'shrink' });
  slide.addText('Wichtig: Das ist die anspruchsvollere RAG-Einstellung, weil Modul und korrektes Feld stimmen müssen.', { x:8.5, y:5.38, w:3.4, h:0.43, fontSize:11.5, color:C.body, margin:0, fit:'shrink' });
  slide.addText('Quelle: docs/evaluation_results.md im Projekt-Repository', { x:0.78, y:6.55, w:5.6, h:0.2, fontSize:9.5, color:'8B96AD', margin:0 });
  addFooter(slide);
}

// Slide 9
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Was versteht das System wirklich?', 'Natürliche Sprache ja, aber ohne übertriebene Versprechen', '09');
  const cards = [
    {x:0.72,title:'Funktioniert gut',icon:'✓',items:['Themenfragen ohne Modulnummer','Paraphrasen über Dense/Hybrid','Deutsch, English und Türkçe','Fragen nach Prüfung, ECTS oder Inhalten']},
    {x:4.45,title:'Bleibt schwierig',icon:'!',items:['Sehr vage Fragen ohne Kontext','Mehrere gleichartige Module im selben Korpus','Antworten, die mehrere Felder kombinieren','Cross-linguale Suche ohne Dense-Modell']},
    {x:8.18,title:'Methodisch sauber',icon:'◎',items:['Retriever und Korpus werden angezeigt','Quellen bleiben sichtbar','BM25-Boost wird als Ablation berichtet','LLM-Antwort ist optional']}
  ];
  cards.forEach((c,i)=>{
    addCard(slide,c.x,2.02,3.35,3.95,{fill:i===1?'FFF9F2':'FFFFFF',line:i===1?'F7DFC1':C.line});
    addIcon(slide,c.x+0.32,2.34,c.icon,i===1?'FFF1DE':'EEF1FF',i===1?C.orange:(i===2?C.purple:C.blue),0.52);
    slide.addText(c.title,{x:c.x+0.98,y:2.4,w:2.0,h:0.34,fontSize:19,bold:true,color:C.navy,margin:0});
    addBullets(slide,c.items,c.x+0.43,3.15,2.5,2.25,14.2,C.body,i===1?C.orange:C.blue,6);
  });
  addCard(slide,0.72,6.2,10.8,0.55,{shadow:false});
  slide.addText('Präsentationsclaim: Explizite Modulnamen helfen, sind aber nicht zwingend nötig. Hybrid Retrieval ist der robuste Default für freie Fragen.', {x:1.02,y:6.35,w:10.2,h:0.22,fontSize:13.2,bold:true,color:C.navy,margin:0,fit:'shrink'});
  addFooter(slide);
}

// Slide 10
{
  const slide = pptx.addSlide('LIGHT');
  addTitle(slide, 'Fazit', 'Wesentliche Takeaways', '10');
  const cards = [
    ['◎','Präzise Evidenz','Struktur-aware Chunking verbessert die Auffindbarkeit relevanter Textstellen.'],
    ['◯','Natürliche Sprache','Fragen können frei formuliert werden, auch ohne Modulnummer.'],
    ['▣','Klare Demo','Korpuswahl, Retriever und Quellen bleiben im modernen Interface sichtbar.']
  ];
  cards.forEach((c,i)=>{
    const x=0.72+i*3.82;
    addCard(slide,x,2.55,3.45,2.6);
    addIcon(slide,x+0.32,2.88,c[0],'EEF1FF',i===1?C.purple:C.blue,0.54);
    slide.addText(c[1],{x:x+0.98,y:2.94,w:2.1,h:0.34,fontSize:19,bold:true,color:C.navy,margin:0,fit:'shrink'});
    slide.addShape(pptx.ShapeType.line,{x:x+0.98,y:3.48,w:0.55,h:0,line:{color:i===1?'C8B7FF':'A9CFFF',width:3}});
    slide.addText(c[2],{x:x+0.32,y:3.85,w:2.82,h:0.82,fontSize:14.2,color:C.body,margin:0,fit:'shrink'});
  });
  addCard(slide,0.72,5.62,11.4,0.82,{shadow:false});
  addIcon(slide,1.02,5.82,'→','EEF1FF',C.blue,0.4);
  slide.addText('Demo-Frage: Welche Veranstaltung behandelt Information Retrieval?', { x:1.58, y:5.88, w:7.0, h:0.24, fontSize:15, bold:true, color:C.blue, margin:0 });
  slide.addText('Danke.', { x:9.95, y:5.78, w:1.45, h:0.42, fontSize:25, bold:true, color:C.navy, align:'right', margin:0 });
  addFooter(slide);
}

pptx.writeFile({ fileName: path.join(__dirname, 'modulhandbuch-rag_praesentation_editierbar.pptx') });
