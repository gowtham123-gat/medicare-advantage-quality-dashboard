import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const qa=path.join(os.tmpdir(),'medicare_quality_workbook_qa');
await fs.mkdir(qa,{recursive:true});
const results=JSON.parse(await fs.readFile(`${root}/analysis/results.json`,'utf8'));
const source=await Workbook.fromCSV(await fs.readFile(`${root}/data/medicare_quality_synthetic.csv`,'utf8'),{sheetName:'Source'});
const sourceValues=source.worksheets.getItem('Source').getUsedRange().values;
const headers=sourceValues[0];
const records=sourceValues.slice(1).map(row=>row.map((v,c)=>[1,6,7,10,13,14].includes(c)?Number(v):c===9?new Date(`${v}T00:00:00Z`):v));
const wb=Workbook.create();
const overview=wb.worksheets.add('Overview');
const perf=wb.worksheets.add('Performance');
const out=wb.worksheets.add('Outreach');
const data=wb.worksheets.add('Data');
const audit=wb.worksheets.add('Staging audit');
const navy='#14243B',blue='#2563EB',green='#15803D';
const disclaimer=results.disclaimer;
function base(sh,range){sh.showGridLines=false;sh.getRange(range).format.font={name:'Arial',size:10,color:navy};sh.getRange(range).format.verticalAlignment='center';sh.getRange(range).format.rowHeight=23;sh.tabColor=blue;}
function header(sh,range){sh.getRange(range).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:40};}
function text(sh,range,value,height=36){sh.mergeCells(range);sh.getRange(range).values=[[value]];sh.getRange(range).format.wrapText=true;sh.getRange(range).format.rowHeight=height;}
base(data,'A1:O8004');data.getRange('A1').values=[['Synthetic quality data']];data.getRange('A1').format.font.size=14;
text(data,'A2:O2',disclaimer,30);
data.getRange('A3:O3').values=[headers];data.getRange('A4:O8003').values=records;
header(data,'A3:O3');data.getRange('A3:O3').format.rowHeight=42;
const widths=[16,8,12,12,23,38,12,12,15,20,13,23,21,12,13];
widths[10]=22; widths.forEach((w,c)=>data.getRangeByIndexes(0,c,8003,1).format.columnWidth=w);
data.getRange('J4:J8003').setNumberFormat('mmm yyyy');data.getRange('O4:O8003').setNumberFormat('0.0%');
data.tables.add('A3:O8003',true,'QualityData');data.freezePanes.freezeRows(3);data.freezePanes.freezeColumns(1);

base(perf,'A1:H42');perf.getRange('A1').values=[['Quality performance calculations']];perf.getRange('A1').format.font.size=14;
text(perf,'A2:H2','Rates use eligible opportunities. All targets are demonstration assumptions. Monthly cohorts are assessed once, not repeated snapshots.',35);
perf.getRange('A1:A42').format.columnWidth=39;perf.getRange('B1:H42').format.columnWidth=17;
const range=(c)=>`Data!$${c}$4:$${c}$8003`;
const count=(col,row,cond)=>`COUNTIFS(${range(col)},$A${row},${range('G')},1${cond?','+range(cond)+',1':''})`;
perf.getRange('A4').values=[['Measure performance']];perf.getRange('A5:H5').values=[['Measure','Eligible','Compliant','Compliance rate','Demo target','Variance pp','Open gaps','Closures to target']];header(perf,'A5:H5');
const names=results.measures.map(x=>x.Measure_Name);
names.forEach((n,i)=>{const r=i+6;perf.getRange(`A${r}`).values=[[n]];perf.getRange(`B${r}:H${r}`).formulas=[[
`=${count('F',r)}`,`=${count('F',r,'H')}`,`=IF(B${r}=0,"",C${r}/B${r})`,
`=IF(B${r}=0,"",SUMIFS(${range('O')},${range('F')},A${r},${range('G')},1)/B${r})`,
`=IF(B${r}=0,"",100*(D${r}-E${r}))`,`=B${r}-C${r}`,`=IF(B${r}=0,0,MAX(0,ROUNDUP(ROUND(B${r}*E${r},8),0)-C${r}))`
]];});
perf.getRange('D6:E11').setNumberFormat('0.0%');perf.getRange('F6:F11').setNumberFormat('0.0');perf.getRange('A6:A11').format.wrapText=true;perf.getRange('A6:H11').format.rowHeight=34;
perf.getRange('A12').values=[['Overall / sum']];perf.getRange('B12:H12').formulas=[['=SUM(B6:B11)','=SUM(C6:C11)','=C12/B12',`=SUMIFS(${range('O')},${range('G')},1)/B12`,'=100*(D12-E12)','=SUM(G6:G11)','=SUM(H6:H11)']];perf.getRange('B12:H12').format.font.bold=true;perf.getRange('D12:E12').setNumberFormat('0.0%');perf.getRange('F12').setNumberFormat('0.0');
perf.getRange('F6:F11').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#B91C1C'}}});
perf.getRange('A15').values=[['Provider performance']];perf.getRange('A16:G16').values=[['Provider','Eligible','Compliant','Compliance rate','Demo target','Variance pp','Open gaps']];header(perf,'A16:G16');
results.providers.forEach((p,i)=>{const r=17+i;perf.getRange(`A${r}`).values=[[p.Provider_Group]];perf.getRange(`B${r}:G${r}`).formulas=[[
`=${count('E',r)}`,`=${count('E',r,'H')}`,`=IF(B${r}=0,"",C${r}/B${r})`,`=IF(B${r}=0,"",SUMIFS(${range('O')},${range('E')},A${r},${range('G')},1)/B${r})`,`=IF(B${r}=0,"",100*(D${r}-E${r}))`,`=B${r}-C${r}`]];});
perf.getRange('D17:E21').setNumberFormat('0.0%');perf.getRange('F17:F21').setNumberFormat('0.0');
perf.getRange('A24').values=[['Regional performance']];perf.getRange('A25:E25').values=[['Region','Eligible','Compliant','Compliance rate','Open gaps']];header(perf,'A25:E25');
results.regions.forEach((p,i)=>{const r=26+i;perf.getRange(`A${r}`).values=[[p.Region]];perf.getRange(`B${r}:E${r}`).formulas=[[
`=${count('D',r)}`,`=${count('D',r,'H')}`,`=IF(B${r}=0,"",C${r}/B${r})`,`=B${r}-C${r}`]];});perf.getRange('D26:D29').setNumberFormat('0.0%');
perf.getRange('A32').values=[['Monthly assessment cohorts']];perf.getRange('A33:G33').values=[['Month','Eligible','Compliant','Compliance rate','Demo target','MoM change pp','Open gaps']];header(perf,'A33:G33');
results.months.forEach((p,i)=>{const r=34+i;perf.getRange(`A${r}`).values=[[new Date(p.Measurement_Month+'T00:00:00Z')]];perf.getRange(`B${r}:G${r}`).formulas=[[
`=${count('J',r)}`,`=${count('J',r,'H')}`,`=IF(B${r}=0,"",C${r}/B${r})`,`=IF(B${r}=0,"",SUMIFS(${range('O')},${range('J')},A${r},${range('G')},1)/B${r})`,i?`=IF(OR(D${r}="",D${r-1}=""),"",100*(D${r}-D${r-1}))`:'=""',`=B${r}-C${r}`]];});
perf.getRange('A34:A39').setNumberFormat('mmm yyyy');perf.getRange('D34:E39').setNumberFormat('0.0%');perf.getRange('F34:F39').setNumberFormat('0.0');
perf.getRange('B6:C39').setNumberFormat('#,##0');perf.getRange('G6:H39').setNumberFormat('#,##0');

base(out,'A1:I18');out.getRange('A1').values=[['Outreach effectiveness']];out.getRange('A1').format.font.size=14;
text(out,'A2:I2','Denominator is attempted eligible gaps. Channel comparisons are simulated associations, not causal effects.',36);
out.getRange('A1:A18').format.columnWidth=24;out.getRange('B1:I18').format.columnWidth=17;
out.getRange('A4:I4').values=[['Channel','Attempted gaps','Reached gaps','Closed gaps','Total attempts','Closure rate','Reach rate','Closure among reached','Average attempts']];header(out,'A4:I4');out.getRange('A4:I4').format.rowHeight=50;
results.outreach.forEach((p,i)=>{const r=5+i;out.getRange(`A${r}`).values=[[p.Outreach_Channel]];out.getRange(`B${r}:I${r}`).formulas=[[
`=COUNTIFS(${range('L')},A${r},${range('G')},1,${range('K')},">0")`,
`=COUNTIFS(${range('L')},A${r},${range('G')},1,${range('K')},">0",${range('M')},"Reached")`,
`=SUMIFS(${range('N')},${range('L')},A${r},${range('G')},1)`,
`=SUMIFS(${range('K')},${range('L')},A${r},${range('G')},1)`,
`=IF(B${r}=0,"",D${r}/B${r})`,`=IF(B${r}=0,"",C${r}/B${r})`,`=IF(C${r}=0,"",D${r}/C${r})`,`=IF(B${r}=0,"",E${r}/B${r})`
]];});out.getRange('F5:H8').setNumberFormat('0.0%');out.getRange('I5:I8').setNumberFormat('0.00');
out.getRange('A11:B14').values=[['Backlog metric','Count'],['Unattempted open gaps',null],['Starting gaps',null],['Outreach coverage',null]];header(out,'A11:B11');out.getRange('A12:A14').format.wrapText=true;out.getRange('A12:B14').format.rowHeight=36;
out.getRange('B12').formulas=[[`=COUNTIFS(${range('G')},1,${range('H')},0,${range('K')},0)`]];
out.getRange('B13').formulas=[['=Performance!G12+SUM(D5:D8)']];out.getRange('B14').formulas=[['=SUM(B5:B8)/B13']];out.getRange('B14').setNumberFormat('0.0%');
text(out,'D11:I14','Pre-existing compliant opportunities are excluded from outreach denominators. Gap_Closed records are newly closed, while Compliant_Flag also includes previously compliant opportunities.',25);

const auditSource=await Workbook.fromCSV(await fs.readFile(`${root}/data/dq_audit.csv`,'utf8'),{sheetName:'Audit'});
const a=auditSource.worksheets.getItem('Audit').getUsedRange().values;
const errorSource=await Workbook.fromCSV(await fs.readFile(`${root}/data/dq_errors.csv`,'utf8'),{sheetName:'Errors'});
const errorValues=errorSource.worksheets.getItem('Errors').getUsedRange().values;
const errorMap=new Map(errorValues.slice(1).map(r=>[Number(r[0]),r[2]]));
const auditRows=a.slice(1).map(r=>r.map((v,c)=>c===0||c===6?Number(v):c===5?new Date(v+'T00:00:00Z'):v).concat(errorMap.get(Number(r[0]))||''));
base(audit,'A1:I8028');audit.getRange('A1').values=[['Staging source audit']];audit.getRange('A1').format.font.size=14;
text(audit,'A2:I2','SQL-generated staging audit. Rebuild the audit CSV after changing staging. Pages 1-3 of the report use the clean reference, not these source defects.',36);
audit.getRange('A4:F4').values=[['Staging rows',null,'Affected rows',null,'Valid row rate',null]];
audit.getRange('B4').formulas=[['=COUNTA(A8:A8027)']];audit.getRange('D4').formulas=[['=COUNTIF(G8:G8027,">0")']];audit.getRange('F4').formulas=[['=1-D4/B4']];audit.getRange('F4').setNumberFormat('0.00%');
audit.getRange('A7:I7').values=[a[0].concat('Failed_Rule')];audit.getRange('A8:I8027').values=auditRows;header(audit,'A7:I7');
[11,16,12,24,40,21,13,19,46].forEach((w,c)=>audit.getRangeByIndexes(0,c,8027,1).format.columnWidth=w);
audit.getRange('F8:F8027').setNumberFormat('mmm yyyy');audit.tables.add('A7:I8027',true,'SourceAudit');audit.freezePanes.freezeRows(7);audit.freezePanes.freezeColumns(2);

base(overview,'A1:J35');overview.getRange('A1:J35').format.columnWidth=13;
text(overview,'A1:J1','Medicare Advantage Quality Improvement Dashboard',30);overview.getRange('A1').format.font.size=16;
text(overview,'A2:J2','January-June 2026 synthetic assessment cohorts. Rates count eligible member-measure opportunities.',30);
function kpi(label,formula,labelRange,valueRange,format){text(overview,labelRange,label,22);text(overview,valueRange,'',27);overview.getRange(valueRange).formulas=[[formula]];overview.getRange(valueRange).setNumberFormat(format);overview.getRange(valueRange).format.font={name:'Arial',size:20,bold:true,color:blue};overview.getRange(labelRange).format.fill='#E9EFF8';overview.getRange(valueRange).format.fill='#E9EFF8';}
kpi('Compliance rate','=Performance!D12','A4:C4','A5:C6','0.0%');kpi('Demo target','=Performance!E12','D4:F4','D5:F6','0.0%');kpi('Open gaps','=Performance!G12','G4:J4','G5:J6','#,##0');
kpi('Eligible opportunities','=Performance!B12','A8:C8','A9:C10','#,##0');kpi('Compliant opportunities','=Performance!C12','D8:F8','D9:F10','#,##0');kpi('Closures to target','=Performance!H12','G8:J8','G9:J10','#,##0');
// Source-linked charts, never static rendered pictures.
// Text labels avoid serial-date labels in the preview and charts.
overview.getRange('L1:N1').values=[['Month','Compliance','Demo target']];results.months.forEach((m,i)=>{const r=i+2;overview.getRange(`L${r}`).values=[[new Date(m.Measurement_Month+'T00:00:00Z').toLocaleDateString('en-US',{month:'short',timeZone:'UTC'})]];overview.getRange(`M${r}:N${r}`).formulas=[[`=Performance!D${i+34}`,`=Performance!E${i+34}`]];});overview.getRange('M2:N7').setNumberFormat('0.0%');
const line=overview.charts.add('line',overview.getRange('L1:N7'));line.title='Monthly cohort compliance versus demonstration target';line.setPosition('A13','I28');line.titleTextStyle.typeface='Arial';line.titleTextStyle.fontSize=12;line.series.items[0].fill=blue;line.series.items[1].fill=green;line.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:10}};line.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};line.yAxis={numberFormatCode:'0%',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
line.series.items[0].line={fill:blue,style:'solid',width:2};line.series.items[1].line={fill:green,style:'dashed',width:2};
text(overview,'A30:J31','Priorities: colorectal screening and post-hospital follow-up account for 58.0% of required closures. Review Provider Group C and the South region within each measure.',24);
text(overview,'A33:J35',disclaimer,22);
wb.recalculate();
const actual=perf.getRange('B12:H12').values[0];
if(actual[0]!==5884||actual[1]!==4173||actual[5]!==1711||actual[6]!==531)throw Error('Performance totals failed: '+actual);
if(Math.abs(actual[2]-results.overall[0].Compliance_Rate)>1e-10)throw Error('Rate mismatch');
// Verify an actual input change propagates and restore it.
const sampleIndex=records.findIndex(r=>r[6]===1&&r[7]===0)+4;
data.getRange(`H${sampleIndex}`).values=[[1]];wb.recalculate();
if(perf.getRange('C12').values[0][0]!==4174)throw Error('Input recalculation failed');
data.getRange(`H${sampleIndex}`).values=[[0]];wb.recalculate();
if(perf.getRange('C12').values[0][0]!==4173)throw Error('Restoration failed');
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
console.log((await wb.inspect({kind:'table',range:'Performance!A5:H12',include:'values,formulas',tableMaxRows:8,tableMaxCols:8,maxChars:1800})).ndjson);
const checks=[['Overview','A1:J35'],['Performance','A1:H40'],['Outreach','A1:I15'],['Data','A1:H12'],['Data','I3:O12'],['Staging audit','A1:I13']];
for(let i=0;i<checks.length;i++){const [sheetName,range]=checks[i];const png=await wb.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(`${qa}/workbook_${i}.png`,new Uint8Array(await png.arrayBuffer()));}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(`${root}/Medicare_Quality_Analysis.xlsx`);
console.log('Verified and exported Medicare_Quality_Analysis.xlsx');
