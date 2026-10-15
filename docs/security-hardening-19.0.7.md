# Sicherheitskorrekturen 19.0.7.0.0

## Rechte und Datenzugriff

- Normale interne Benutzer erhalten nicht länger pauschal Zugriff auf Widerrufe.
- **Widerrufsbearbeiter** dürfen Vorgänge der freigegebenen Unternehmen lesen, erstellen und bearbeiten, aber nicht löschen.
- **Widerrufsmanager** besitzen zusätzlich Löschrechte. Systemadministratoren behalten administrative Rechte.
- Eine globale Unternehmen-Record-Rule gilt auch für Fachgruppen. Rollen werden nicht automatisch an alle bisherigen Benutzer vergeben.
- Kundenportal und Anhangdownload bleiben auf das verifizierte kommerzielle Kundenkonto beschränkt. Anonyme Einsendungen werden nicht anhand einer frei eingegebenen Belegnummer einem Portal-Konto zugeordnet.
- Ein unveränderlicher Eingangssnapshot hält die ursprünglichen Formulardaten und Anhangprüfsummen fest. Bearbeitbare Arbeitsfelder bleiben getrennt. Dies ist kein WORM-Speicher und keine rechtliche Zertifizierung.

## Öffentlicher Ablauf

1. Formular mit nativen CSRF-Tokens, typisierten und längenbegrenzten Eingaben ausfüllen.
2. Der Server erzeugt einen zufälligen, 20 Minuten gültigen Entwurf. Gespeichert wird nur sein Token-Hash; der Entwurf ist an Sitzung und Website gebunden.
3. **Angaben korrigieren** erhält Felder und Anhänge. Jede neue Prüfansicht ist eine eigene Revision.
4. Eine zeilenweise Datenbanksperre und ein eindeutiger Einreichungsschlüssel verhindern Doppelverarbeitung desselben Entwurfs, auch bei Parallelaufrufen.
5. Nach Eingang wird eine E-Mail nur für die native Warteschlange erzeugt. Wiederholungen zeigen denselben Vorgang und erzeugen keine zweite Eingangsbestätigung.

Grenzen: Name 200, E-Mail 254, Referenz 128 und Mitteilung 10000 Zeichen; genau eine normalisierte E-Mail-Adresse. Höchstens fünf Entwürfe je Sitzung und 30 je gehashtem IP-Fingerabdruck in zehn Minuten. Fingerabdrücke sind mit dem Datenbankgeheimnis HMAC-geschützt; keine Klartext-IP-Speicherung im Modul. Bei öffentlichen Installationen zusätzlich Reverse-Proxy-Limits und Monitoring einsetzen; dies ersetzt keinen DDoS-Schutz.

## Anhänge

- Optional bis zu drei PDF/JPG/JPEG/PNG-Dateien; Dateigröße in den Einstellungen zwischen 1 und 10 MB pro Datei.
- Zusätzlich höchstens **10 MB zusammen je Formular**, **20 MB je Sitzung** und **30 MB je IP-Fingerabdruck in zehn Minuten**. Formularkorrekturen mit Dateikopien zählen mit.
- Dateiendung und Inhalte werden serverseitig geprüft: Bildformat, Bildintegrität und Pixelzahl; bei PDF Header und EOF-Struktur. Die vom Browser gemeldete MIME-Angabe wird nicht vertraut.
- Es gibt **keinen eingebauten Virenscanner und keine vollständige PDF-Sicherheitsanalyse**. Für produktive Umgebungen kann zusätzliche Malware-Prüfung nötig sein.
- Dateien sind nicht öffentlich, bekommen kein freies Zugriffstoken und werden nur als Download mit sicherem Content-Disposition, nosniff und Sandbox-Header ausgegeben.
- Temporäre Entwürfe und nicht übernommene Dateien werden über Odoos native Transient-Vakuumierung bereinigt. Bestätigte Originalanhänge werden vorher an den Eingang umgebunden.

## E-Mails und Sprache

- Odoo-19-Inline-Templates verwenden `{{ ... }}`; HTML verwendet natives QWeb.
- Neue Standardtexte und Formulare unterstützen Deutsch, Englisch und Niederländisch. Betreibertexte werden nicht maschinell überschrieben/übersetzt.
- Technisch eingegangen, für Versand vorgemerkt, gesendet und fehlgeschlagen sind unterschiedliche Zustände. `sent` bedeutet technische Übergabe durch Odoo, keine garantierte Zustellung beim Empfänger.
- Bei einem Mailfehler bleibt die Erklärung gespeichert. SMTP wird nicht synchron im öffentlichen Formular aufgerufen.
- Mailvorlagen sind nach Anlage editor-eigen (`noupdate`). Der Upgradepfad repariert alte `${...}`-Envelope-Felder gezielt und ersetzt unveränderte Standardtexte; individuell bearbeitete HTML-Texte bleiben erhalten.
- Funktionierender Ausgangsmailserver, Absender und interne Empfänger müssen vom Betreiber eingerichtet werden.

## Upgrade von 19.0.6

Vorher Datenbank, Filestore und Modulcode sichern. Migration ausschließlich mit dem echten installierten Modulnamen durchführen:

```sh
odoo -c /pfad/odoo.conf -d TESTDATENBANK -u odoo_widerrufbutton --stop-after-init --no-http --max-cron-threads=0
```

Historische Versandflags werden als **ungeprüfte Legacy-Nachweise** archiviert und nicht nachträglich als verifizierter Versand ausgegeben. Ein Legacy-Eingangssnapshot wird zum Upgradezeitpunkt aus dem vorhandenen Datensatz gebildet; er behauptet keine rückwirkende Unverändertheit. Der ursprüngliche Erstellungszeitpunkt bleibt als Eingangszeit erhalten.

Optionale Sale-/Accounting-Brücken bleiben optional. Die Verknüpfung erfolgt nur bei exaktem, eindeutigem Treffer im selben Unternehmen; freie Belegnummern ändern niemals die verifizierte Portalidentität. Eine E-Mail-Abweichung bleibt ein Bearbeiterhinweis, kein Beweis für oder gegen ein Widerrufsrecht.

## Verifikation

- Native `TransactionCase`-Tests im Addon: ACLs, Unternehmen, unveränderliche Belege, Validatoren, Mailgenerierung/Fehler, Uploads, Größenlimits, Sitzungsbindung, Frist und aggregierte Speicherquote.
- Öffentlicher HTTP-Smoke (`scripts/security_http_smoke.py`) nur auf isoliertem, SMTP-neutralisiertem Klon: CSRF, Escaping, Upload, Korrektur, Fremdsitzung, manipulierte Tokens, Retry/Parallelität, DE/EN/NL und Rate-Limit.
- Verpackungs-/Syntax-/XML-/Secret-Hygiene: `python3 scripts/validate_module.py`. Das ist kein Ersatz für native Laufzeittests.
- Rechtliche Anwendbarkeit und Pflichttexte müssen vor Produktivbetrieb fachlich geprüft werden; keine automatische Stornierung, Erstattung oder Entscheidung über die Wirksamkeit.
