import re,sys,time,json,csv,io,os,html
import urllib.request as U
os.makedirs('data',exist_ok=True)
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36','Accept':'*/*'}
def get(url,binary=False):
    r=U.urlopen(U.Request(url,headers=H),timeout=300); b=r.read()
    return b if binary else b.decode('utf-8','replace')
def xlsx_to_csv(path,out):
    from openpyxl import load_workbook
    wb=load_workbook(path,read_only=True,data_only=True)
    n=0
    with open(out,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                if any(c is not None and str(c).strip()!='' for c in row):
                    w.writerow(['' if c is None else c for c in row]); n+=1
            break
    print('converted',path,n,'rows')
# VIC: latest "Victorian liquor licences by location" xlsx (links on the DataVic page)
try:
    page=get('https://discover.data.vic.gov.au/dataset/victorian-liquor-licences-by-location')
    links=[html.unescape(l) for l in re.findall(r'href="([^"]+\.(?:xlsx|csv))"',page,re.I)]
    print('VIC links',links)
    l=links[0]
    b=get(l,True); ext=l.rsplit('.',1)[-1].lower()
    open(f'data/vic_licences.{ext}','wb').write(b); print('VIC saved',l,len(b))
    if ext=='xlsx': xlsx_to_csv('data/vic_licences.xlsx','data/vic_licences.csv')
except Exception as e: print('VIC fail',e)
# NSW: latest premises list xlsx on the licensed premises data page
try:
    page=get('https://www.nsw.gov.au/business-and-economy/liquor-and-gaming/gaming/gaming-machine-data-reports/licensed-premises-data')
    links=[html.unescape(l) for l in re.findall(r'href="([^"]+premises-list[^"]+\.(?:xlsx|csv))"',page,re.I)]
    print('NSW links',links[:5])
    l=links[0]
    if not l.startswith('http'): l='https://www.nsw.gov.au'+l
    b=get(l,True); ext=l.rsplit('.',1)[-1].lower()
    open(f'data/nsw_premises.{ext}','wb').write(b); print('NSW saved',l,len(b))
    if ext=='xlsx': xlsx_to_csv('data/nsw_premises.xlsx','data/nsw_premises.csv')
except Exception as e: print('NSW fail',e)
# ABR entity names: skip if already done this month
if os.path.exists('data/abr_entities.csv') and os.environ.get('REFRESH_ABR','')!='1':
    print('ABR exists, skipping'); sys.exit(0)
abns=[a.strip() for a in open('abns.txt') if a.strip()]
out=[]
for i,a in enumerate(abns):
    try:
        h=get(f'https://abr.business.gov.au/ABN/View?abn={a}')
        name=re.search(r'Entity name:</th>\s*<td[^>]*>\s*(.*?)\s*</td>',h,re.S)
        etype=re.search(r'Entity type:</th>\s*<td[^>]*>\s*<a[^>]*>(.*?)</a>',h,re.S)
        status=re.search(r'ABN status:</th>\s*<td[^>]*>\s*(.*?)\s*</td>',h,re.S)
        out.append(dict(abn=a,entity=html.unescape(re.sub('<[^>]+>','',name.group(1))).strip() if name else '',type=etype.group(1).strip() if etype else '',status=html.unescape(re.sub('<[^>]+>','',status.group(1))).strip()[:60] if status else '',business_names=''))
    except Exception as e: out.append(dict(abn=a,entity='',type='',status='ERR '+str(e)[:40],business_names=''))
    if i%100==0: print('ABR',i); time.sleep(1)
    time.sleep(0.4)
with open('data/abr_entities.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['abn','entity','type','status','business_names']); w.writeheader(); w.writerows(out)
print('ABR done',len(out))
