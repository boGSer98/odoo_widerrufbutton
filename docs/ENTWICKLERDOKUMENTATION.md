# Entwicklerdokumentation: Odoo Widerrufbutton

Diese Dokumentation beschreibt Architektur, Module, Datenmodelle, Controller, Views und Erweiterungspunkte des Repositorys `odoo_widerrufbutton`.

## Ziel

Das Projekt stellt eine technische Grundlage fuer einen Widerrufbutton in Odoo bereit. Kunden koennen ueber die Website einen Widerruf erfassen. Der Vorgang wird in Odoo gespeichert und kann im Backend, Portal sowie optional im Zusammenhang mit Verkaufsauftraegen und Rechnungen genutzt werden.

## Moduluebersicht

### Basismodul: `odoo_widerrufbutton`

Pflichtmodul. Es enthaelt die eigentliche Website- und Backend-Logik.

Abhaengigkeiten:

```python
"website"
"mail"
"portal"
```

Hauptfunktionen:

- Website-Footer-Link
- Formularseite `/widerruf`
- alternative URL `/vertrag-widerrufen`
- Pruefseite `/widerruf/pruefen`
- Bestaetigungsroute `/widerruf/bestaetigen`
- Backend-Modell `widerruf.record`
- Kundenportal-Routen
- E-Mail-Templates
- Konfigurationsmaske

### Zusatzmodul: `odoo_widerrufbutton_sale`

Optionales Modul fuer Verkaufsauftraege.

Abhaengigkeiten:

```python
"odoo_widerrufbutton"
"sale"
```

Hauptfunktionen:

- Feld `sale_order_id` auf `widerruf.record`
- Suche ueber `sale.order.name`
- Suche ueber `sale.order.client_order_ref`
- Button `Verkaufsauftrag suchen`
- Smartbutton `Widerrufe` auf dem Verkaufsauftrag

### Zusatzmodul: `odoo_widerrufbutton_account`

Optionales Modul fuer Rechnungen aus Invoicing/Rechnungsstellung.

Abhaengigkeiten:

```python
"odoo_widerrufbutton"
"account"
```

Hauptfunktionen:

- Feld `invoice_id` auf `widerruf.record`
- Suche ueber `account.move.name`
- Suche ueber `account.move.payment_reference`
- Suche ueber `account.move.ref`
- Button `Rechnung suchen`

## Repository-Struktur

```text
odoo_widerrufbutton/
├── __manifest__.py
├── controllers/
├── data/
├── models/
├── security/
├── static/
├── views/
├── odoo_widerrufbutton_sale/
├── odoo_widerrufbutton_account/
└── docs/
```

Wichtig: Das Basismodul liegt im Repository-Root. Die Zusatzmodule liegen als Unterordner. Deshalb muss der Addons-Pfad in der Entwicklungsumgebung beide Ebenen enthalten.

```bash
--addons-path=addons,/home/odoo/odoo-dev,/home/odoo/odoo-dev/odoo_widerrufbutton
```

## Datenmodell `widerruf.record`

Datei:

```text
models/widerruf_record.py
```

Wichtige Felder:

| Feld | Typ | Zweck |
|---|---|---|
| `name` | Char | Vorgangsnummer |
| `customer_name` | Char | Name des Kunden |
| `customer_email` | Char | E-Mail-Adresse des Kunden |
| `order_reference` | Char | Bestell- oder Rechnungsnummer |
| `partner_id` | Many2one `res.partner` | verknuepftes Kundenkonto |
| `withdrawal_type` | Selection | Art des Widerrufs |
| `message` | Text | optionale Mitteilung |
| `state` | Selection | Bearbeitungsstatus |
| `website_id` | Many2one `website` | Herkunftswebsite |
| `company_id` | Many2one `res.company` | Unternehmen |
| `confirmation_mail_sent` | Boolean | Status der Kundenmail |
| `internal_mail_sent` | Boolean | Status der internen Mail |

Statuswerte:

```python
confirmed
in_progress
done
cancelled
```

## Sequenz

Datei:

```text
data/sequence.xml
```

Die Sequenz erzeugt eindeutige Vorgangsnummern fuer Widerrufe. Die Vergabe erfolgt beim Erstellen des Datensatzes in `create()`.

## Website-Controller

Datei:

```text
controllers/main.py
```

### Routen

| Route | Methode | Zweck |
|---|---|---|
| `/widerruf` | GET | Formular anzeigen |
| `/vertrag-widerrufen` | GET | alternative Formular-URL |
| `/widerruf/pruefen` | POST | Eingaben validieren und Pruefansicht anzeigen |
| `/widerruf/bestaetigen` | POST | Widerruf final speichern |

### Validierung

Die Methode `_validate_form_values()` prueft:

- Name vorhanden
- E-Mail vorhanden
- einfache E-Mail-Pruefung mit `@`
- Bestell- oder Rechnungsnummer vorhanden
- gueltiger Widerrufstyp
- Honeypot-Feld `website_url`

### Dateiupload

Dateiuploads wurden bewusst entfernt. Das Formular enthaelt kein Upload-Feld mehr und der Controller verarbeitet keine Anhaenge aus der Website.

## Portal-Controller

Datei:

```text
controllers/portal.py
```

Funktionen:

- Portalzaehler fuer Widerrufe
- Liste `/my/widerrufe`
- Detailansicht `/my/widerrufe/<id>`
- optionaler Zugriff auf vorhandene alte Anhaenge

Portalzugriff erfolgt nur fuer angemeldete Benutzer. Angezeigt werden Widerrufe, deren `partner_id` dem kommerziellen Partner des angemeldeten Benutzers entspricht.

## E-Mail-Templates

Datei:

```text
data/mail_template.xml
```

Templates:

- Eingangsbestätigung an Kunden
- interne Benachrichtigung
- Statusaenderung an Kunden

Voraussetzung ist ein funktionierender ausgehender Mailserver in Odoo.

## Einstellungen

Dateien:

```text
models/res_config_settings.py
views/res_config_settings_views.xml
```

Konfigurationswerte werden ueber `ir.config_parameter` gespeichert.

Wichtige Optionen:

- interne Benachrichtigungsadresse
- zustaendiger Benutzer fuer Aktivitaeten
- Aktivitaet bei neuem Widerruf erstellen
- interne E-Mail senden
- Statusmails an Kunden senden
- Portalansicht anzeigen
- Footer-Button anzeigen
- Einleitungstext der Widerrufsseite

## Backend-Views

Datei:

```text
views/widerruf_record_views_19.xml
```

Enthaelt:

- Listenansicht
- Formularansicht
- Aktion `action_widerruf_record`
- Menuepunkt `Widerrufe`

## Website-Templates

Datei:

```text
views/website_widerruf_templates.xml
```

Templates:

- Footer-Link
- Formularseite
- Pruefseite
- Erfolgsseite

Das Styling nutzt Bootstrap-/Odoo-Klassen wie `btn`, `btn-primary`, `form-control`, `card`, damit das Layout zum Website-Theme passt.

## SCSS

Datei:

```text
static/src/scss/widerrufbutton.scss
```

Die Datei enthaelt nur ergaenzendes Styling. Farben sollen nach Moeglichkeit ueber Odoo-/Theme-Klassen kommen, damit sich das Modul an das Website-Design anpasst.

## Zusatzmodul Verkauf

### Modell-Erweiterung `widerruf.record`

Datei:

```text
odoo_widerrufbutton_sale/models/widerruf_record.py
```

Felder:

- `sale_order_id`
- `sale_reference_found`
- `sale_email_matches`
- `sale_email_mismatch_warning`

Suchlogik:

1. exakte Suche nach `sale.order.name`
2. exakte Suche nach `sale.order.client_order_ref`
3. unscharfe Suche mit `ilike`

Bei Treffer wird optional `partner_id` aus dem Verkaufsauftrag gesetzt.

### Modell-Erweiterung `sale.order`

Datei:

```text
odoo_widerrufbutton_sale/models/sale_order.py
```

Felder:

- `widerruf_ids`
- `widerruf_count`

Methode:

```python
action_view_widerrufe()
```

Diese Methode oeffnet die zugeordneten Widerrufe. Bei genau einem Widerruf wird direkt die Formularansicht geoeffnet.

### Smartbutton

Datei:

```text
odoo_widerrufbutton_sale/views/sale_order_views.xml
```

Der Smartbutton wird im Verkaufsauftrag angezeigt, wenn `widerruf_count > 0`.

## Zusatzmodul Rechnung

Datei:

```text
odoo_widerrufbutton_account/models/widerruf_record.py
```

Felder:

- `invoice_id`
- `invoice_reference_found`
- `invoice_email_matches`
- `invoice_email_mismatch_warning`

Suchlogik:

1. `account.move.name`
2. `account.move.payment_reference`
3. `account.move.ref`
4. zunaechst exakt, danach unscharf mit `ilike`

Beruecksichtigte Rechnungstypen:

```python
out_invoice
out_refund
```

## Installationsbefehle Entwicklung

Basismodul:

```bash
cd ~/odoo-dev/odoo
source ~/odoo-dev/odoo_venv/bin/activate

python3 odoo-bin \
  -r odoo \
  -w odoo \
  --addons-path=addons,/home/odoo/odoo-dev,/home/odoo/odoo-dev/odoo_widerrufbutton \
  -d odoo_widerruf_dev \
  -u odoo_widerrufbutton \
  --stop-after-init
```

Verkaufsmodul:

```bash
python3 odoo-bin -r odoo -w odoo --addons-path=addons,/home/odoo/odoo-dev,/home/odoo/odoo-dev/odoo_widerrufbutton -d odoo_widerruf_dev -u odoo_widerrufbutton_sale --stop-after-init
```

Rechnungsmodul:

```bash
python3 odoo-bin -r odoo -w odoo --addons-path=addons,/home/odoo/odoo-dev,/home/odoo/odoo-dev/odoo_widerrufbutton -d odoo_widerruf_dev -u odoo_widerrufbutton_account --stop-after-init
```

Bei Erstinstallation `-i` statt `-u` verwenden.

## Erweiterungspunkte

Sinnvolle naechste technische Erweiterungen:

- Smartbutton auch auf Rechnungen
- PDF-Eingangsbestaetigung
- bessere E-Mail-Validierung
- Captcha oder Rate-Limiting
- rechtlich gepruefte Texte
- Fristenlogik
- automatische Workflows fuer Rueckerstattung oder Gutschrift
- Tests fuer Controller und Modelle

## Rechtlicher Hinweis

Diese Dokumentation beschreibt die technische Umsetzung. Sie ersetzt keine rechtliche Pruefung des Widerrufsprozesses.
