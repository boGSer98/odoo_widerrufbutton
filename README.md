# Odoo Widerrufbutton

Odoo-Module fuer einen Widerrufbutton auf einer Odoo-Website.

Das Repository enthaelt ein schlankes Basismodul sowie optionale Zusatzmodule fuer Verkauf und Rechnungsstellung.

## Module

### `odoo_widerrufbutton`

Basismodul fuer Website, Formular, Portal und Backend-Verwaltung.

Funktionen:

- Button **Vertrag widerrufen** im Website-Footer
- Widerrufsseite unter `/widerruf` und `/vertrag-widerrufen`
- Formular mit Pflichtfeldern: Name, E-Mail, Bestell- oder Rechnungsnummer
- Auswahl: vollstaendiger Widerruf, teilweiser Widerruf, sonstige Mitteilung
- Pruefansicht vor finalem Absenden
- Speicherung als Widerrufsvorgang im Backend
- automatische Vorgangsnummer
- Eingangs-E-Mail an den Kunden
- interne Aktivitaet und optionale interne Benachrichtigung
- Anzeige im Kundenportal bei angemeldeten Kunden
- Konfiguration unter **Einstellungen > Widerrufbutton**

Abhaengigkeiten:

```python
"website", "mail", "portal"
```

### `odoo_widerrufbutton_sale`

Optionales Zusatzmodul fuer die Verknuepfung mit Verkaufsauftraegen.

Funktionen:

- Suche nach `sale.order.name`
- Suche nach `sale.order.client_order_ref`
- automatische Verknuepfung des Widerrufs mit dem Auftrag
- E-Mail-Abgleich zwischen Widerruf und Auftrag
- Smartbutton **Widerrufe** im Verkaufsauftrag, sichtbar nur bei vorhandener Verknuepfung

Abhaengigkeiten:

```python
"odoo_widerrufbutton", "sale"
```

### `odoo_widerrufbutton_account`

Optionales Zusatzmodul fuer die Verknuepfung mit Rechnungen aus der Odoo-App Invoicing/Rechnungsstellung.

Funktionen:

- Suche nach `account.move.name`
- Suche nach `account.move.payment_reference`
- Suche nach `account.move.ref`
- automatische Verknuepfung des Widerrufs mit der Rechnung
- E-Mail-Abgleich zwischen Widerruf und Rechnung

Abhaengigkeiten:

```python
"odoo_widerrufbutton", "account"
```

## Installation in der Entwicklungsumgebung

Repository aktualisieren:

```bash
cd ~/odoo-dev/odoo_widerrufbutton
git pull
```

Basismodul installieren oder aktualisieren:

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

Optionale Zusatzmodule:

```bash
-u odoo_widerrufbutton_sale
-u odoo_widerrufbutton_account
```

Bei Erstinstallation statt `-u` bitte `-i` verwenden.

## Dokumentation

- `docs/ENTWICKLERDOKUMENTATION.md`
- `docs/ANWENDERANLEITUNG.md`

## Hinweis

Das Modul ist eine technische Umsetzungshilfe und ersetzt keine Rechtsberatung. Texte, Button-Beschriftungen und Prozesslogik muessen vor produktivem Einsatz rechtlich geprueft werden.

## Autor

IT-Service AHD  
https://it-service-ahd.de
