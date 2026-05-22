# Entwicklungsstand 19.0.5.0.0 – Anhänge und Spam-Schutz

Diese Entwicklungsphase erweitert das Modul um optionale Datei-Anhänge und eine einfache Spam-Abwehr.

## Neue Funktionen

- optionales Upload-Feld im öffentlichen Widerrufsformular
- maximale Dateigröße: 10 MB
- Anzeige des Dateinamens in der Prüfansicht
- Speicherung des Anhangs als `ir.attachment`
- Verknüpfung des Anhangs mit dem Widerrufsvorgang `widerruf.record`
- Anzeige der Anzahl der Anhänge in der Backend-Liste
- neuer Reiter **Anhänge** im Backend-Formular
- Anzeige von Anhängen im Kundenportal
- geschützter Download von Anhängen im Kundenportal
- einfacher Honeypot-Spam-Schutz über ein unsichtbares Formularfeld

## Betroffene Dateien

```text
odoo_widerrufbutton/models/widerruf_record.py
odoo_widerrufbutton/controllers/main.py
odoo_widerrufbutton/controllers/portal.py
odoo_widerrufbutton/views/website_widerruf_templates.xml
odoo_widerrufbutton/views/widerruf_record_views.xml
odoo_widerrufbutton/views/portal_widerruf_templates.xml
odoo_widerrufbutton/static/src/scss/widerrufbutton.scss
odoo_widerrufbutton/__manifest__.py
```

## Testablauf

1. Repository lokal aktualisieren:

```bash
cd /opt/odoo/custom-addons/odoo_widerrufbutton
git pull
```

2. Modul in der Testdatenbank aktualisieren:

```bash
cd /opt/odoo/odoo
source /opt/odoo/venv/bin/activate
python3 odoo-bin -c /etc/odoo.conf -d odoo_widerruf_test -u odoo_widerrufbutton --stop-after-init
```

3. Odoo neu starten:

```bash
sudo systemctl restart odoo
```

4. Widerrufsformular öffnen:

```text
/widerruf
```

5. Formular mit Anhang absenden.

6. Prüfen:

- Datei erscheint in der Prüfansicht
- Widerruf wird erstellt
- Anhang ist im Backend-Reiter **Anhänge** sichtbar
- bei eingeloggtem Portalnutzer ist der Anhang unter `/my/widerrufe/<id>` sichtbar
- Download im Portal funktioniert nur für den zugeordneten Kunden

## Hinweise

Die Anhangsfunktion ist aktuell bewusst einfach gehalten. Für produktive Nutzung sollten später weitere Prüfungen ergänzt werden:

- erlaubte Dateitypen
- Viren-/Malware-Scan
- konfigurierbare maximale Dateigröße
- automatische Lösch-/Aufbewahrungsfristen
- DSGVO-konforme Beschreibung im Datenschutzhinweis
