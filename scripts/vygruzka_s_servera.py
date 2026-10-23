import json, os, re, urllib.request, urllib.parse
env = {}
for line in open('/opt/teyes-case-studio/.env.production.local'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1); env[k] = v.strip().strip('"\'')
TOK = env['YANDEX_DISK_TOKEN']; ROOT = env.get('YANDEX_TELEGRAM_CASES_ROOT') or '/TEYES Case Studio/Кейсы из Telegram'
IMG = re.compile(r'\.(jpe?g|png|heic|webp|gif|mp4|mov)$', re.I)
def listdir(p):
    items, off = [], 0
    while True:
        q = urllib.parse.urlencode(dict(path=p, limit=1000, offset=off, fields='_embedded.items.name,_embedded.items.type,_embedded.total'))
        r = urllib.request.Request('https://cloud-api.yandex.net/v1/disk/resources?' + q, headers={'Authorization': 'OAuth ' + TOK})
        for t in range(4):
            try: d = json.load(urllib.request.urlopen(r, timeout=60)); break
            except urllib.error.HTTPError as e:
                if e.code == 404: return None
            except Exception: pass
        else: return None
        e = d['_embedded']; items += e['items']; off += 1000
        if off >= e['total']: return items
def files(p):
    out = []
    for i in listdir(p) or []:
        if i['type'] == 'file':
            if IMG.search(i['name']): out.append(i['name'])
        else: out += files(p + '/' + i['name'])
    return out
def url(p): return 'https://disk.yandex.ru/client/disk' + urllib.parse.quote(p)
root = [i['name'] for i in listdir(ROOT) if i['type'] == 'dir']
folders = {n: files(ROOT + '/' + n) for n in root}
byno = {}
for n in root:
    m = re.match(r'(\d+)_', n)
    if m: byno.setdefault(int(m.group(1)), []).append(n)
data = json.load(open('/opt/teyes-case-studio/data/cases.json'))
rows, used = [], set()
for c in data['cases']:
    fp = (c.get('source_folder_path') or '').strip()
    if fp.startswith('disk:'): fp = fp[5:]
    name = fp.rsplit('/', 1)[-1] if fp.startswith(ROOT + '/') else ''
    if fp.startswith(ROOT + '/') and name not in folders: name = ''
    if name not in folders and not fp:
        cand = byno.get(c['id'], [])
        name = cand[0] if len(cand) == 1 else ''
    disk_path, disk_files = '', None
    if name: disk_path, disk_files = ROOT + '/' + name, folders[name]; used.add(name)
    elif fp:
        disk_files = files(fp); disk_path = fp if disk_files is not None else ''
    roles = [p.get('filename') for p in c.get('photo_roles') or [] if p.get('filename')]
    local = None
    m = re.search(r'/uploads/([^/]+)/?$', c.get('photo_folder_url') or '')
    for d in (('/opt/teyes-case-studio/uploads/' + m.group(1)) if m else '', '/opt/teyes-case-studio/media/cases/%s' % c['id']):
        if d and os.path.isdir(d):
            local = (local or 0) + sum(1 for _, _, fs in os.walk(d) for f in fs if IMG.search(f))
    tg = ''
    if c.get('telegram_chat_id') and c.get('telegram_message_id'):
        tg = 'https://t.me/c/%s/%s' % (str(c['telegram_chat_id']).replace('-100', '', 1), c['telegram_message_id'])
    rows.append(dict(id=c['id'], date=c.get('date') or '', created=(c.get('created_at') or '')[:16], source=c.get('source'),
        author=c.get('performed_by') or '', tg=tg, text=c.get('raw_text') or c.get('work') or '',
        vehicle=c.get('vehicle') or '', year=c.get('year') or '', work=c.get('work') or '',
        disk=url(disk_path) if disk_path else '', folder=disk_path.rsplit('/', 1)[-1],
        on_disk=None if disk_files is None else len(disk_files), in_system=c.get('photo_count') or 0, local=local,
        not_on_disk=[r for r in roles if disk_files is not None and r not in disk_files],
        site=c.get('site_status') or '', tilda=c.get('tilda_post_id') or ''))
orph = [dict(folder=n, disk=url(ROOT + '/' + n), on_disk=len(folders[n])) for n in root if n not in used]
json.dump(dict(root=ROOT, rows=rows, orphans=orph, deleted=data.get('deleted_case_ids'), updated=data.get('updated_at')), open('/root/cs_export.json', 'w'), ensure_ascii=False)
print('DONE', len(rows), len(orph))
