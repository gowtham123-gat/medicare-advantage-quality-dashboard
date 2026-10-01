from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def read(name,numeric):
    with (ROOT/'data'/name).open() as f:
        rows=list(csv.DictReader(f))
    for row in rows:
        for key in numeric:row[key]=float(row[key]) if key=='Target_Rate' else int(row[key])
    return rows
rows=read('medicare_quality_synthetic.csv',['Age','Eligible_Flag','Compliant_Flag','Outreach_Attempts','Gap_Closed','Target_Rate'])
audit=read('dq_audit.csv',['Row_ID','Issue_Count']);errors=read('dq_errors.csv',['Row_ID'])
rules=[('R01','Missing member or measure key'),('R02','Duplicate member-measure key'),('R03','Age outside demo cohort'),('R04','Invalid or conflicting flags'),('R05','Gap status or closure conflict'),('R06','Outreach field inconsistency'),('R07','Target differs from demo reference'),('R08','Invalid measurement month'),('R09','Missing or unknown dimension'),('R10','Eligibility outside demo age gender rule')]
fields=list(rows[0]);payload={'fields':fields,'rows':[[r[k] for k in fields] for r in rows],'audit':audit,'errors':errors,'rules':rules}
html=(ROOT/'scripts/dashboard_template.html').read_text().replace('__PROJECT_DATA__',json.dumps(payload,separators=(',',':')))
(ROOT/'portfolio/dashboard_preview.html').write_text(html)
print('Standalone browser dashboard created.')
