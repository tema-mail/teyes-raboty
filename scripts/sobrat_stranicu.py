import json, sys, html
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src))
rows = []
for x in d['rows']:
    date = x['date']
    if x['source'] == 'telegram' and x['created']:
        date = x['created'][8:10] + '.' + x['created'][5:7] + '.' + x['created'][:4] + ' ' + x['created'][11:16]
    # ключ сортировки даты: ГГГГММДД
    dd = x['date']
    if x['source'] == 'telegram' and x['created']:
        key = x['created'].replace('-', '').replace('T', '').replace(':', '')
    elif len(dd) == 5:
        key = '20' + dd[3:5] + dd[0:2] + '00'
    else:
        key = ''
    rows.append(dict(n=x['id'], date=date, key=key, src='Telegram' if x['source'] == 'telegram' else 'Старая база',
        tg=x['tg'], author=x['author'], text=x['text'], car=(x['vehicle'] + (' ' + x['year'] if x['year'] and x['year'] not in x['vehicle'] else '')).strip(),
        work=x['work'], disk=x['disk'], folder=x['folder'], disk_n=x['on_disk'], sys_n=x['in_system'] - sum(1 for f in x['not_on_disk'] if f.startswith('generated-')), srv_n=x['local'],
        site={'published': 'Опубликован', 'not_published': 'Нет', 'scheduled': 'Запланирован'}.get(x['site'], x['site'] or 'Нет')))
for o in d['orphans']:
    if o['folder'].startswith('_'):
        continue
    num = o['folder'].split('_', 1)
    rows.append(dict(n=int(num[0]) if num[0].isdigit() else 0, date='', key='', src='Только Диск', tg='', author='', text='',
        car=num[1] if len(num) > 1 else o['folder'], work='', disk=o['disk'], folder=o['folder'], disk_n=o['on_disk'], sys_n=None, srv_n=None, site=''))
meta = dict(updated=d.get('updated', '')[:16].replace('T', ' '))
page = open(sys.argv[3]).read().replace('/*DATA*/[]', json.dumps(rows, ensure_ascii=False)).replace('/*META*/{}', json.dumps(meta, ensure_ascii=False))
open(out, 'w').write(page)
print(len(rows))
