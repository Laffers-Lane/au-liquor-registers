import re,sys,time,json,csv,io,os
import urllib.request as U
os.makedirs('data',exist_ok=True)
H={'User-Agent':'Mozilla/5.0 (compatible; LaffersLane-registers/1.0)'}
def get(url,binary=False):
    r=U.urlopen(U.Request(url,headers=H),timeout=120); b=r.read()
    return b if binary else b.decode('utf-8','replace')
# VIC: all licence-type CSVs
VIC=['Full_Club_Licence','General_Licence','Late_Night_General_Licence','Late_Night_On_Premises_Licence','Limited_Licence','On_Premises_Licence','Packaged_Liquor_Licence','Pre_retail_Licence','Producers_Licence','Remote_Seller_Packaged_Liquor_Licence','Renewable_Limited_Licence','Restaurant_and_Cafe_Licence','Restricted_Club_Licence','Wine_and_Beer_Producers_Licence','Late_Night_Packaged_Liquor_Licence','Major_Event_Licence']
ok=[]
for n in VIC:
    try:
        b=get(f'https://dar6fu3d3rk1b.cloudfront.net/datasets/liqvic/{n}.csv',True)
        open(f'data/vic_{n}.csv','wb').write(b); ok.append((n,len(b)))
    except Exception as e: print('VIC miss',n,e)
print('VIC',ok)
# NSW: find current CSV/XLSX link on the resources page
try:
    page=get('https://www.liquorandgaming.nsw.gov.au/resources/liquor-licence-data')
    links=re.findall(r'href="([^"]+\.(?:csv|xlsx|xls))"',page,re.I)
    print('NSW links',links[:10])
    for l in links:
        if not l.startswith('http'): l='https://www.liquorandgaming.nsw.gov.au'+l
        b=get(l,True); ext=l.rsplit('.',1)[-1].lower()
        open(f'data/nsw_premises.{ext}','wb').write(b); print('NSW saved',l,len(b)); break
except Exception as e: print('NSW page fail',e)
# ABR entity names by scraping the public ABN view page
abns=[a.strip() for a in open('abns.txt') if a.strip()]
out=[]
for i,a in enumerate(abns):
    try:
        h=get(f'https://abr.business.gov.au/ABN/View?abn={a}')
        name=re.search(r'Entity name:</th>\s*<td[^>]*>\s*(.*?)\s*</td>',h,re.S)
        etype=re.search(r'Entity type:</th>\s*<td[^>]*>\s*<a[^>]*>(.*?)</a>',h,re.S)
        status=re.search(r'ABN status:</th>\s*<td[^>]*>\s*(.*?)\s*</td>',h,re.S)
        bn=re.findall(r'Business name[s]?.*?</th>.*?<td[^>]*>(.*?)</td>',h,re.S)
        bnames=[]
        for blk in bn: bnames+= [re.sub('<[^>]+>','',x).strip() for x in re.findall(r'<tr[^>]*>\s*<td[^>]*>(.*?)</td>',blk,re.S)]
        out.append(dict(abn=a,entity=re.sub('<[^>]+>','',name.group(1)).strip() if name else '',type=etype.group(1).strip() if etype else '',status=re.sub('<[^>]+>','',status.group(1)).strip()[:60] if status else '',business_names='|'.join(x for x in bnames if x)))
    except Exception as e: out.append(dict(abn=a,entity='',type='',status='ERR '+str(e)[:40],business_names=''))
    if i%100==0: print('ABR',i); time.sleep(1)
    time.sleep(0.4)
with open('data/abr_entities.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['abn','entity','type','status','business_names']); w.writeheader(); w.writerows(out)
print('ABR done',len(out))
