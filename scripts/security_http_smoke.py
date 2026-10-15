"""Run ONLY against an isolated, SMTP-neutralized database. Persists labelled fixtures."""
import argparse
import io
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--db',required=True);p.add_argument('--output',required=True);a=p.parse_args()
assert a.db.startswith('ahd_widerruf7_'), 'Isolated clone only'
base=a.base_url.rstrip('/');checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name);print('OK',name)
def client():
    s=requests.Session();r=s.get(base+'/web/login',params={'db':a.db},timeout=30);assert r.status_code==200;return s
def hidden(body,name):
    m=re.search('name="'+name+'"[^>]*value="([^"]*)"',body);assert m,'Missing '+name;return m.group(1)
def form(s,path='/de/widerruf'):
    r=s.get(base+path,timeout=30);assert r.status_code==200;return hidden(r.text,'csrf_token')
def preview(s,csrf,ref='AHD7-HTTP',files=None,draft=''):
    return s.post(base+'/widerruf/pruefen',data={'csrf_token':csrf,'customer_name':'AHD7 isolated HTTP test','customer_email':'http-test@example.invalid','order_reference':ref,'withdrawal_type':'full','message':'AHD7 HTTP fixture <script>alert(1)</script>','draft':draft},files=files,timeout=30)
s=client();csrf=form(s)
check('csrf_missing_rejected',s.post(base+'/widerruf/pruefen',data={'customer_name':'Test'},timeout=30).status_code==400)
buf=io.BytesIO();Image.new('RGB',(2,2),'red').save(buf,format='PNG');png=buf.getvalue()
r=preview(s,csrf,files=[('attachments',('test.png',png,'image/png'))]);check('valid_upload_review',r.status_code==200 and 'test.png' in r.text)
check('review_escapes_html','&lt;script&gt;' in r.text and '<script>alert(1)</script>' not in r.text)
token=hidden(r.text,'payload')
r=s.get(base+'/de/widerruf',params={'draft':token},timeout=30);check('correction_preserves_values_and_file',r.status_code==200 and 'AHD7-HTTP' in r.text and 'test.png' in r.text)
other=client();othercsrf=form(other)
r=other.post(base+'/widerruf/bestaetigen',data={'csrf_token':othercsrf,'payload':token},timeout=30);check('stolen_token_other_session_rejected',r.status_code==400)
r=s.post(base+'/widerruf/bestaetigen',data={'csrf_token':csrf,'payload':token},timeout=30);check('confirm_queued_not_claimed_sent',r.status_code==200 and 'für den Versand vorgemerkt' in r.text)
r2=s.post(base+'/widerruf/bestaetigen',data={'csrf_token':csrf,'payload':token},timeout=30);check('same_token_retry_same_receipt',r2.status_code==200 and re.findall(r'WID/[^< ]+',r.text)==re.findall(r'WID/[^< ]+',r2.text))
for index,payload in enumerate(['[]','null','123','tampered',token+'x']):
    r=s.post(base+'/widerruf/bestaetigen',data={'csrf_token':csrf,'payload':payload},timeout=30);check('invalid_token_'+str(index),r.status_code==400)
r=preview(s,csrf,ref='AHD7-HTTP-BAD',files=[('attachments',('fake.pdf',b'<html>not pdf</html>','application/pdf'))]);check('disguised_file_rejected',r.status_code==400)
r=preview(s,csrf,ref='AHD7-HTTP-BAD',files=[('attachments',('file.svg',b'<svg/>','image/svg+xml'))]);check('active_svg_rejected',r.status_code==400)
r=preview(s,csrf,ref='AHD7-HTTP-PARALLEL');assert r.status_code==200;parallel=hidden(r.text,'payload')
cookies=s.cookies.get_dict()
def confirm_parallel(_):
    c=requests.Session();c.cookies.update(cookies);return c.post(base+'/widerruf/bestaetigen',data={'csrf_token':csrf,'payload':parallel},timeout=60)
with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(confirm_parallel,range(2)))
check('parallel_confirm_http_both_successful',all(r.status_code==200 for r in results))
for code,title,queued in [('de','Vertrag widerrufen','für den Versand vorgemerkt'),('nl','Overeenkomst herroepen','klaar voor verzending'),('en','Withdraw from contract','queued for delivery')]:
    c=client();path='/widerruf' if code=='en' else '/'+code+'/widerruf';page=c.get(base+path,timeout=30);check('localized_form_'+code,title in page.text)
    cr=hidden(page.text,'csrf_token');rv=preview(c,cr,ref='AHD7-HTTP-LANG-'+code);assert rv.status_code==200
    done=c.post(base+'/widerruf/bestaetigen',data={'csrf_token':cr,'payload':hidden(rv.text,'payload')},timeout=30);check('localized_queued_status_'+code,done.status_code==200 and queued in done.text)
# Quota is per session AND per keyed IP hash; no X-Forwarded-For spoofing is needed.
c=client();cr=form(c);statuses=[preview(c,cr,ref='AHD7-HTTP-RATE').status_code for _ in range(6)]
check('draft_rate_limit',statuses==[200,200,200,200,200,429])
Path(a.output).write_text(json.dumps({'checks':checks,'count':len(checks),'result':'passed'},indent=2));print('HTTP_CHECK_COUNT',len(checks))
