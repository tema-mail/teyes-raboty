# Реестр работ TEYES Sibir

Таблица всех работ Case Studio: дата, сообщение в чате, текст, машина, работа, папка на Яндекс Диске и число фото.
Страница: https://tema-mail.github.io/teyes-raboty/

Обновление (снимок, сам не обновляется):
1. `scripts/vygruzka_s_servera.py` запустить на сервере Case Studio (45.12.72.227) – пишет `/root/cs_export.json`.
2. `python3 scripts/sobrat_stranicu.py cs_export.json page.html scripts/shablon.html`, затем обернуть в index.html.
