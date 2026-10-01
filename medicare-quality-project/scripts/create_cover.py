"""Create a static portfolio cover using the verified analysis results."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import PercentFormatter
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'analysis/results.json').read_text());o=d['overall'][0]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(15,10.6),dpi=140,facecolor='#f3f6fa')
navy='#14243b';blue='#2563eb';green='#15803d';muted='#61718a'
fig.text(.045,.956,'HEALTHCARE ANALYTICS PORTFOLIO',color=blue,size=10,weight='bold')
fig.text(.045,.915,'Medicare Advantage Quality Improvement Dashboard',color=navy,size=21,weight='bold')
fig.text(.045,.881,'Synthetic assessment cohorts  |  January–June 2026  |  Independent demonstration project',color=muted,size=10)
kpis=[('Synthetic members','3,075'),('Eligible opportunities','5,884'),('Compliance rate','70.9%'),('Demo target','79.5%'),('Open care gaps','1,711'),('Closures to target','531')]
for i,(label,value) in enumerate(kpis):
    x=.045+i*.154
    fig.add_artist(FancyBboxPatch((x,.753),.142,.097,boxstyle='round,pad=0.006',facecolor='white',edgecolor='#dfe6ef',transform=fig.transFigure))
    fig.text(x+.009,.821,label,color=muted,size=9)
    fig.text(x+.009,.777,value,color=navy,size=25,weight='bold')
ax=fig.add_axes([.075,.447,.40,.24],facecolor='white');m=d['months']
ax.plot(range(6),[r['Compliance_Rate'] for r in m],color=blue,lw=2.5,marker='o',ms=5,label='Compliance')
ax.plot(range(6),[r['Weighted_Target_Rate'] for r in m],color=green,lw=2,ls='--',label='Demo target')
ax.set_ylim(0,1);ax.set_xticks(range(6),['Jan','Feb','Mar','Apr','May','Jun']);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.grid(axis='y',alpha=.16);ax.set_title('Monthly assessed-cohort compliance',loc='left',pad=17,color=navy,weight='bold',size=12);ax.legend(loc='lower right',frameon=False,fontsize=9)
ax=fig.add_axes([.62,.447,.31,.24],facecolor='white');p=sorted(d['providers'],key=lambda r:r['Compliance_Rate'])
ax.barh([r['Provider_Group'].replace('Provider ','') for r in p],[r['Compliance_Rate'] for r in p],color=blue,height=.58)
ax.set_xlim(0,1);ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.grid(axis='x',alpha=.16);ax.set_title('Provider performance',loc='left',pad=17,color=navy,weight='bold',size=12)
for i,r in enumerate(p):ax.text(r['Compliance_Rate']+.018,i,f"{r['Compliance_Rate']*100:.1f}%",va='center',size=9,color=navy)
ax=fig.add_axes([.075,.153,.40,.205],facecolor='white');r=sorted(d['regions'],key=lambda r:r['Open_Gaps'])
ax.barh([x['Region'] for x in r],[x['Open_Gaps'] for x in r],color='#d97706',height=.55);ax.set_xlim(0,700);ax.set_title('Regional care-gap backlog',loc='left',pad=17,color=navy,weight='bold',size=12);ax.grid(axis='x',alpha=.16)
for i,x in enumerate(r):ax.text(x['Open_Gaps']+12,i,str(x['Open_Gaps']),va='center',size=9,color=navy)
ax=fig.add_axes([.55,.153,.39,.205]);ax.axis('off');ax.set_title('Improvement priorities',loc='left',pad=17,color=navy,weight='bold',size=12)
table=ax.table(cellText=[['Colorectal screening','57.5%','162'],['Hospital follow-up','53.0%','146'],['Blood pressure','72.9%','99'],['Diabetes care','69.6%','85'],['Breast screening','72.9%','39']],colLabels=['Measure','Rate','Closures needed'],colWidths=[.53,.18,.29],cellLoc='left',loc='center')
table.auto_set_font_size(False);table.set_fontsize(9);table.scale(1,1.8)
for (i,j),cell in table.get_celld().items():cell.set_edgecolor('#e3e9f0');cell.set_text_props(color=navy);cell.set_facecolor('#edf2f8' if i==0 else 'white')
fig.text(.045,.087,'Two measures account for 58.0% of required closures. 545 remaining open gaps have no outreach attempt.',size=10,color=navy,weight='bold')
fig.text(.045,.058,'Demonstration targets are not CMS cut points. Monthly cohorts differ. Provider rates are unadjusted.',size=9,color=muted)
fig.text(.045,.031,'Entirely synthetic data. No PHI, PII, patient records or proprietary employer data. Static project overview.',size=8.5,color=muted)
fig.savefig(ROOT/'portfolio/dashboard_cover.png',facecolor=fig.get_facecolor());plt.close(fig)
print('Static portfolio cover created.')
