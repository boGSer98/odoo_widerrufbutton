# Entwicklungsstand 19.0.6.0.0 – Konfiguration, Upload-Sicherheit und Dokumentverknüpfung

Diese Version erweitert das Modul um mehr Konfigurierbarkeit, eine sicherere Upload-Prüfung und eine bessere Verknüpfung mit Verkaufs- und Rechnungsdokumenten.

## Neue Konfigurationsoptionen

Pfad in Odoo:

```text
Einstellungen > Widerrufbutton
```

### Website und Formular

- Footer-Button anzeigen
- Einleitungstext der Widerrufsseite
- Dateiupload aktivieren/deaktivieren
- erlaubte Dateiendungen, z. B. `pdf,jpg,jpeg,png`
- maximale Dateigröße in MB

### Kundenportal

- Portalansicht aktivieren/deaktivieren

### Benachrichtigungen und Aktivitäten

- interne E-Mail senden
- interne Benachrichtigungsadresse
- Aktivität bei neuem Widerruf erstellen
- zuständiger Benutzer
- Fälligkeit der Aktivität in Tagen
- Statusänderungen an Kunden senden

## Upload-Sicherheit

Der Dateiupload prüft jetzt:

- ob Uploads grundsätzlich aktiviert sind
- ob die Dateiendung erlaubt ist
- ob die Dateigröße innerhalb des konfigurierten Limits liegt
- ob der Dateiname bereinigt werden kann

Aktuell noch nicht umgesetzt:

- Virenscan
- echte Inhaltsprüfung der Datei
- erweiterte MIME-Type-Validierung

## Dokumentverknüpfung

Beim Erstellen eines Widerrufs wird versucht, die angegebene Bestell- oder Rechnungsnummer zuzuordnen.

Prüfreihenfolge:

1. Verkaufsauftrag über `sale.order.name`
2. Verkaufsauftrag über `sale.order.client_order_ref`
3. Ausgangsrechnung/Gutschrift über `account.move.name`
4. Ausgangsrechnung/Gutschrift über `account.move.payment_reference`

Das Ergebnis wird im Feld **Art der Referenzverknüpfung** angezeigt.

Mögliche Werte:

- Verkaufsauftrag
- Rechnung
- Keine Verknüpfung

## E-Mail-Abgleich

Wenn ein Verkaufsauftrag oder eine Rechnung gefunden wird, vergleicht das Modul die eingegebene E-Mail-Adresse mit der E-Mail-Adresse des verknüpften Dokuments.

Bei Abweichung wird im Backend ein Warnhinweis angezeigt.

## Backend-Filter

Neue Filter:

- Mit Anhängen
- Ohne Dokumentverknüpfung
- E-Mail-Abweichung

## Testablauf

```bash
cd /opt/odoo/custom-addons/odoo_widerrufbutton
git pull
```

```bash
cd /opt/odoo/odoo
source /opt/odoo/venv/bin/activate
python3 odoo-bin -c /etc/odoo.conf -d odoo_widerruf_test -u odoo_widerrufbutton --stop-after-init
```

```bash
sudo systemctl restart odoo
```

Danach testen:

1. Einstellungen öffnen: `Einstellungen > Widerrufbutton`
2. Upload aktivieren
3. erlaubte Dateiendungen setzen
4. maximale Dateigröße setzen
5. `/widerruf` öffnen
6. erlaubte Datei hochladen
7. nicht erlaubte Datei testen
8. zu große Datei testen
9. Widerruf mit bekannter Bestellnummer testen
10. Widerruf mit bekannter Rechnungsnummer testen
11. E-Mail-Abweichung im Backend prüfen
12. Portalansicht aktivieren/deaktivieren und `/my/widerrufe` testen
