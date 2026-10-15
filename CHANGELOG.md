# Changelog

Alle relevanten Änderungen am Modul `odoo_widerrufbutton` werden in dieser Datei dokumentiert.

## 19.0.7.0.0

### Sicherheit und Fehlerkorrekturen

- Pauschale interne ACL durch eigene Bearbeiter-/Managerrollen und globale Unternehmenstrennung ersetzt; keine versteckte sales_team-Abhängigkeit mehr.
- Odoo-19-Mail-Platzhalter korrigiert; native Mailwarteschlange statt synchronem SMTP. Versandflags folgen tatsächlichem Mailstatus, Erfolgsseite unterscheidet Eingang und Versand.
- Sitzungs- und websitegebundene, kurzlebige Entwürfe mit Einmalverarbeitung, Zeilensperre und eindeutigem Einreichungsschlüssel. Typ-/Adress-/Längenvalidierung und Missbrauchsquoten ergänzt.
- Dateiupload tatsächlich implementiert: Dateiendungen, Inhalts-/Größenprüfung, vertrauliche Bindung an Entwurf/Eingang, sichere Downloadheader und temporäre Bereinigung.
- Korrekturlink erhält Angaben/Anhänge. Öffentliche Seiten und Mailstandards DE/EN/NL ergänzt.
- Originaleingänge und Legacy-Versandnachweise beim Upgrade erhalten; editor-eigene Mailtexte updatebeständig.
- Optionale Belegbrücken auf exakte, eindeutige Treffer je Unternehmen begrenzt; keine automatische unbestätigte Portal-Kontozuordnung. Verkaufs-Smartbutton-Abhängigkeiten korrigiert.
- Native Sicherheitsregressionen und isolierter HTTP-Smoke ergänzt.

## 19.0.6.0.6

### Geändert

- Repository-Struktur gemäß Odoo Vendor Guidelines auf Root-Add-on-Verzeichnisse vorbereitet.
- Apps-Store-Metadaten ergänzt: Support-Adresse, Preis `10,00 EUR`, Währung und Bildverweis.
- Englische Apps-Store-Beschreibung unter `static/description/index.html` ergänzt.
- Validierungsskript für Manifest-, Beschreibung-, Paketstruktur-, XML-/Python- und Secret-Hygiene ergänzt.
- Versehentlich versionierte Python-Bytecode-Dateien entfernt und `.gitignore` ergänzt.

## 19.0.6.0.0

### Hinzugefügt

- Erweiterte Konfigurationsseite unter **Einstellungen > Widerrufbutton**
- Dateiupload kann aktiviert oder deaktiviert werden
- erlaubte Dateiendungen sind konfigurierbar
- maximale Uploadgröße ist konfigurierbar
- Einleitungstext der Widerrufsseite ist konfigurierbar
- Portalansicht kann aktiviert oder deaktiviert werden
- Footer-Button kann aktiviert oder deaktiviert werden
- Fälligkeit der automatisch erzeugten Aktivität ist konfigurierbar
- Suche nach passenden Ausgangsrechnungen/Gutschriften über `account.move`
- Verknüpfung mit Verkaufsauftrag oder Rechnung wird im Backend angezeigt
- Warnhinweis bei abweichender E-Mail-Adresse zwischen Widerruf und verknüpftem Dokument
- zusätzliche Backend-Filter:
  - mit Anhängen
  - ohne Dokumentverknüpfung
  - E-Mail-Abweichung

### Geändert

- Abhängigkeit `account` ergänzt, damit Rechnungen sauber verknüpft werden können
- Modulversion von `19.0.5.0.0` auf `19.0.6.0.0` erhöht
- Dateiupload validiert nun Dateiendung und Größe aus den Einstellungen
- Portalrouten prüfen, ob die Portalansicht in den Einstellungen aktiv ist

### Noch offen

- PDF-Eingangsbestätigung
- Virenscan für Dateianhänge
- mehrsprachige Übersetzungsdateien
- rechtliche Finalisierung der Texte

## 19.0.5.0.0

### Hinzugefügt

- optionaler Datei-Anhang im Widerrufsformular
- Speicherung als `ir.attachment`
- Anzeige der Anhänge im Backend
- Anzeige und Download der Anhänge im Kundenportal
- einfacher Honeypot-Spam-Schutz

## 19.0.4.0.0

### Hinzugefügt

- interne Benachrichtigung bei neuen Widerrufen
- automatische To-do-Aktivität
- Kunden-E-Mail bei Statusänderungen
- Einstellungsbereich für Benachrichtigungen

## 19.0.3.0.0

### Hinzugefügt

- Kundenportalübersicht `/my/widerrufe`
- Detailansicht `/my/widerrufe/<id>`
- Verknüpfung mit eingeloggtem Kundenkonto

## 19.0.2.0.0

### Hinzugefügt

- öffentliches Widerrufsformular
- Prüfschritt
- finale Bestätigung
- Backend-Modell `widerruf.record`
- Eingangsbestätigung per E-Mail

## 19.0.1.0.0

### Hinzugefügt

- initiales Modul
- Footer-Button **Vertrag widerrufen**
- öffentliche Widerrufsseite `/widerruf`
