"""Rebuild the deterministic demonstration data, database, audit and analysis.
Standard library only. Run: python scripts/generate_project.py from project root.
"""
from pathlib import Path
import csv, json, random, sqlite3, math, collections, copy

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260930
DISCLAIMER = 'This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.'
FIELDS = ['Member_ID','Age','Gender','Region','Provider_Group','Measure_Name','Eligible_Flag','Compliant_Flag','Gap_Status','Measurement_Month','Outreach_Attempts','Outreach_Channel','Outreach_Status','Gap_Closed','Target_Rate']
SPECS = [
 ('Controlling Blood Pressure',1600,.62,.80,.88),
 ('Colorectal Cancer Screening',1500,.43,.75,.95),
 ('Breast Cancer Screening',1100,.60,.80,.95),
 ('Diabetes Care',1400,.55,.78,.74),
 ('Medication Adherence',1500,.77,.85,.90),
 ('Follow-Up After Hospitalization',900,.40,.75,.76)]
REGIONS = ['North','South','East','West']
GROUPS = ['Provider Group A','Provider Group B','Provider Group C','Provider Group D','Provider Group E']

def write_csv(path, rows, fields=None):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0])); w.writeheader(); w.writerows(rows)

def main():
    for folder in ['data','analysis','sql']: (ROOT/folder).mkdir(exist_ok=True)
    rng=random.Random(SEED)
    members=[]
    for i in range(1,3201):
        members.append(dict(Member_ID=f'SYN{i:05d}',Age=rng.choices(list(range(65,90)),weights=[3 if a<76 else 1.3 for a in range(65,90)])[0],Gender=rng.choices(['Female','Male'],[.54,.46])[0],Region=rng.choices(REGIONS,[.26,.31,.21,.22])[0],Provider_Group=rng.choices(GROUPS,[.24,.22,.21,.18,.15])[0],Measurement_Month=f'2026-{rng.randint(1,6):02d}-01'))
    rows=[]
    for name,n,base,target,elig_prob in SPECS:
        # Weighted sampling without replacement, using exponential keys.
        selected=sorted(members,key=lambda m:-math.log(max(rng.random(),1e-12))/(8 if name=='Breast Cancer Screening' and m['Gender']=='Female' else 1))[:n]
        for member in selected:
            r=member.copy(); r['Measure_Name']=name
            allowed=not (name=='Colorectal Cancer Screening' and r['Age']>75 or name=='Breast Cancer Screening' and (r['Gender']!='Female' or r['Age']>74))
            eligible=int(allowed and rng.random()<elig_prob)
            month=int(r['Measurement_Month'][5:7])
            p=base+{'Provider Group A':.09,'Provider Group B':.03,'Provider Group C':-.10,'Provider Group D':-.04,'Provider Group E':.01}[r['Provider_Group']]+{'North':.045,'South':-.065,'East':.015,'West':.025}[r['Region']]+(month-1)*.018
            if name=='Follow-Up After Hospitalization' and r['Provider_Group']=='Provider Group C': p-=.06
            initial=int(eligible and rng.random()<min(.96,max(.15,p)))
            attempts=0; channel='None'; status='Not Needed'; closed=0
            if eligible and not initial:
                status='Not Attempted'
                if rng.random()<(.67+(month-1)*.025):
                    channel=rng.choices(['Phone','SMS','Mail','Care Coordinator'],[.43,.25,.20,.12])[0]
                    attempts=rng.choices([1,2,3,4],[.45,.32,.16,.07])[0]
                    reach={'Phone':.70,'SMS':.65,'Mail':.44,'Care Coordinator':.84}[channel]
                    if r['Region']=='South': reach-=.06
                    status=rng.choices(['Reached','Unable to Reach','Declined'],[reach,1-reach-.08,.08])[0]
                    if status=='Reached':
                        closure={'Phone':.48,'SMS':.42,'Mail':.25,'Care Coordinator':.68}[channel]
                        closure+=(month-1)*.012
                        if name=='Colorectal Cancer Screening':closure-=.08
                        if name=='Follow-Up After Hospitalization':closure-=.06
                        closed=int(rng.random()<closure)
            compliant=int(initial or closed)
            r.update(Eligible_Flag=eligible,Compliant_Flag=compliant,Gap_Status='Not Eligible' if not eligible else 'Compliant' if compliant else 'Open',Outreach_Attempts=attempts,Outreach_Channel=channel,Outreach_Status=status,Gap_Closed=closed,Target_Rate=target)
            rows.append({k:r[k] for k in FIELDS})
    rows.sort(key=lambda r:(r['Measurement_Month'],r['Member_ID'],r['Measure_Name']))
    assert len(rows)==8000
    assert len({(r['Member_ID'],r['Measure_Name']) for r in rows})==8000
    write_csv(ROOT/'data/medicare_quality_synthetic.csv',rows,FIELDS)
    raw=copy.deepcopy(rows)
    pool=list(range(8000));rng.shuffle(pool)
    for i in pool[:8]:raw[i]['Member_ID']=''
    for i in pool[8:16]:raw[i]['Age']=127
    attempted=[i for i in pool[16:] if raw[i]['Outreach_Attempts']>0][:12]
    for i in attempted:raw[i]['Outreach_Channel']=''
    used=set(pool[:16]+attempted)
    target_ids=[i for i in pool if i not in used][:8]
    for i in target_ids:raw[i]['Target_Rate']=.99
    used.update(target_ids)
    conflict_ids=[i for i in pool if i not in used and raw[i]['Eligible_Flag']==0][:10]
    for i in conflict_ids:raw[i]['Compliant_Flag']=1
    used.update(conflict_ids)
    dup_ids=[i for i in pool if i not in used][:20]
    raw.extend(copy.deepcopy(rows[i]) for i in dup_ids)
    write_csv(ROOT/'data/medicare_quality_staging.csv',raw,FIELDS)
    db_path=ROOT/'data/medicare_quality.db'
    if db_path.exists():db_path.unlink()
    db=sqlite3.connect(db_path);db.row_factory=sqlite3.Row
    db.executescript((ROOT/'sql/01_schema.sql').read_text())
    for table,data in [('quality_fact',rows),('quality_staging',raw)]:
        db.executemany(f'INSERT INTO {table} ({",".join(FIELDS)}) VALUES ({",".join("?" for _ in FIELDS)})',[[r[k] for k in FIELDS] for r in data])
    db.executemany('INSERT INTO measure_targets VALUES (?,?)',[(s[0],s[3]) for s in SPECS])
    db.executescript((ROOT/'sql/02_analysis_queries.sql').read_text())
    db.executescript((ROOT/'sql/03_data_quality_checks.sql').read_text())
    def query(sql):return [dict(x) for x in db.execute(sql)]
    audit=query('SELECT * FROM dq_audit ORDER BY Row_ID')
    errors=query('SELECT * FROM dq_errors ORDER BY Row_ID, Rule_ID')
    write_csv(ROOT/'data/dq_audit.csv',audit)
    write_csv(ROOT/'data/dq_errors.csv',errors)
    checks=query('SELECT Rule_ID, Rule_Name, COUNT(*) AS Issue_Count FROM dq_errors GROUP BY Rule_ID,Rule_Name ORDER BY Rule_ID')
    outputs={key:query(f'SELECT * FROM {view}') for key,view in [('overall','v_overall'),('measures','v_measure_performance'),('providers','v_provider_performance'),('regions','v_region_performance'),('months','v_monthly_trend'),('outreach','v_outreach_effectiveness'),('gaps','v_care_gaps'),('target','v_target_opportunity')]}
    outputs['dq']={'rows':len(audit),'affected_rows':sum(r['Issue_Count']>0 for r in audit),'issues':len(errors),'checks':checks}
    outputs['seed']=SEED;outputs['unique_members']=len({r['Member_ID'] for r in rows})
    outputs['raw_unique_members']=len({r['Member_ID'] for r in raw if r['Member_ID']})
    outputs['disclaimer']=DISCLAIMER
    (ROOT/'analysis/results.json').write_text(json.dumps(outputs,indent=2))
    for key in ['measures','providers','regions','months','outreach','gaps','target']:write_csv(ROOT/f'analysis/{key}.csv',outputs[key])
    db.commit()
    # Validate both business logic and test coverage independently of SQL views.
    assert all(r['Compliant_Flag']<=r['Eligible_Flag'] for r in rows)
    assert all(not r['Gap_Closed'] or r['Compliant_Flag']==1 and r['Outreach_Status']=='Reached' for r in rows)
    assert sum(r['Gap_Status']=='Open' for r in rows)==outputs['overall'][0]['Open_Gaps']
    assert sum(r['Compliant_Flag'] for r in rows)==outputs['overall'][0]['Compliant_Opportunities']
    assert sum(r['Eligible_Flag'] for r in rows)==outputs['overall'][0]['Eligible_Opportunities']
    assert len(audit)==8020 and sum(r['Issue_Count']>0 for r in audit)==66
    assert len(errors)>=66
    # Test the same rule view against the clean fact. Zero issues expected.
    db.execute('DELETE FROM quality_staging')
    db.executemany(f'INSERT INTO quality_staging ({",".join(FIELDS)}) VALUES ({",".join("?" for _ in FIELDS)})',[[r[k] for k in FIELDS] for r in rows])
    assert db.execute('SELECT COUNT(*) FROM dq_errors').fetchone()[0]==0
    db.rollback() # restores staging defects saved in the prior commit
    db.close()
    (ROOT/'analysis/validation_report.txt').write_text('PASS: 8,000 unique member-measure records.\nPASS: flag, gap and outreach consistency.\nPASS: SQL and independent counts reconcile.\nPASS: 8,020 staging rows and 66 affected rows detected.\nPASS: same data-quality rules detect zero issues on clean data.\nPASS: staging defect data restored after clean-data test.\nDAX and Power BI visuals require final validation in Power BI Desktop.\n')
    print(json.dumps(outputs,indent=2))

if __name__=='__main__':main()
