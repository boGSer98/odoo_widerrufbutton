# Odoo Widerrufbutton

Odoo-Module für einen Widerrufbutton auf einer Odoo-Website.

Das Repository enthält ein schlankes Basismodul sowie optionale Zusatzmodule für Verkauf und Rechnungsstellung. Die Add-on-Verzeichnisse liegen gemäß Odoo Vendor Guidelines direkt im Repository-Root, damit GitHub-Importe und ZIP-Pakete ohne zusätzliche Verschachtelung funktionieren.

## Dokumentzuordnung 19.0.8.0.0

Neue Widerrufe prüfen vorhandene Angebote/Aufträge sowie Rechnungen/Gutschriften über die optionalen Integrationen. Smartbuttons erschließen die nativen Belegketten. Ohne eindeutigen Treffer ist eine manuelle Auswahl vorhandener Dokumente möglich; manuelle Zuordnungen bleiben erhalten. Kein neues Ticket-/Vorgangsmodell und keine automatische finanzielle Aktion.

[Bedienung, Rechte und Tests](docs/document-assignment-19.0.8.md).

## Sicherheitsstand 19.0.7.0.0

Die Sicherheitskorrekturen umfassen Fachrollen und Unternehmenstrennung, Odoo-19-Mailvorlagen mit echter Warteschlange, unveränderte Eingangssnapshots, einmalige sitzungsgebundene Bestätigung, sichere optionale Anhänge sowie DE/EN/NL.

**Nach Upgrade:** Bearbeitern die Gruppe **Widerrufsbearbeiter** bzw. **Widerrufsmanager** gezielt zuweisen. SMTP/Absender prüfen. Die Erfolgsseite bestätigt den Eingang, nicht pauschal einen erfolgreichen Mailversand.

[Details, Grenzen, Upgrade und Tests](docs/security-hardening-19.0.7.md).

## Module

### `odoo_widerrufbutton`

Basismodul für Website, Formular, Portal und Backend-Verwaltung.

Funktionen:

- Button **Vertrag widerrufen** im Website-Footer
- Widerrufsseite unter `/widerruf` und `/vertrag-widerrufen`
- Formular mit Pflichtfeldern: Name, E-Mail, Bestell- oder Rechnungsnummer
- Auswahl: vollständiger Widerruf, teilweiser Widerruf, sonstige Mitteilung
- Prüfansicht vor finalem Absenden
- Speicherung als Widerrufsvorgang im Backend
- automatische Vorgangsnummer
- Eingangs-E-Mail an den Kunden
- interne Aktivität und optionale interne Benachrichtigung
- Anzeige im Kundenportal bei angemeldeten Kunden
- Konfiguration unter **Einstellungen > Widerrufbutton**

Abhängigkeiten:

```python
"website", "mail", "portal"
```

### `odoo_widerrufbutton_sale`

Optionales Zusatzmodul für die Verknüpfung mit Verkaufsaufträgen.

Funktionen:

- Suche nach `sale.order.name`
- Suche nach `sale.order.client_order_ref`
- automatische Verknüpfung des Widerrufs mit dem Auftrag
- E-Mail-Abgleich zwischen Widerruf und Auftrag
- Smartbutton **Widerrufe** im Verkaufsauftrag, sichtbar nur bei vorhandener Verknüpfung

Abhängigkeiten:

```python
"odoo_widerrufbutton", "sale"
```

### `odoo_widerrufbutton_account`

Optionales Zusatzmodul für die Verknüpfung mit Rechnungen aus der Odoo-App Invoicing/Rechnungsstellung.

Funktionen:

- Suche nach `account.move.name`
- Suche nach `account.move.payment_reference`
- Suche nach `account.move.ref`
- automatische Verknüpfung des Widerrufs mit der Rechnung
- E-Mail-Abgleich zwischen Widerruf und Rechnung

Abhängigkeiten:

```python
"odoo_widerrufbutton", "account"
```

## Odoo Apps / Vendor-Informationen

- Odoo-Version: `19.0`
- Verkaufsmodul: `odoo_widerrufbutton`
- Preis: `10,00 EUR`
- Lizenz: `LGPL-3`
- Hersteller/Autor: `IT-Service AHD`
- Support: `info@it-service-ahd.de`
- Apps-Store-Beschreibung: `odoo_widerrufbutton/static/description/index.html`
- Bildmaterial: `odoo_widerrufbutton/static/description/icon.png` und `odoo_widerrufbutton/static/description/widerrufbutton_overview.png`

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
  --addons-path=addons,/home/odoo/odoo-dev/odoo_widerrufbutton \
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

## Validierung

```bash
python3 scripts/validate_module.py
```

Die Validierung prüft Manifest-Metadaten, Beschreibung, Bildverweise, Python/XML-Syntax, GitHub-/Apps-Store-Paketstruktur und offensichtliche Secret-/Token-/private-IP-Muster in paketierten Textdateien.

## Dokumentation

- `docs/ENTWICKLERDOKUMENTATION.md`
- `docs/ANWENDERANLEITUNG.md`

## Hinweis

Das Modul ist eine technische Umsetzungshilfe und ersetzt keine Rechtsberatung. Texte, Button-Beschriftungen und Prozesslogik müssen vor produktivem Einsatz rechtlich geprüft werden.

## Autor

IT-Service AHD  
https://it-service-ahd.de
