# Anwenderanleitung: Odoo Widerrufbutton

Diese Anwenderanleitung beschreibt die Einrichtung und tägliche Nutzung der Module `odoo_widerrufbutton`, `odoo_widerrufbutton_sale` und `odoo_widerrufbutton_account` in Odoo 19 Community.

Die Anleitung richtet sich an Website-Betreiber, Sachbearbeiter, Shop-Verantwortliche und Administratoren, die eingehende Widerrufe in Odoo erfassen, prüfen und bearbeiten möchten.

---

## 1. Zweck des Moduls

Das Modul stellt auf der Odoo-Website eine elektronische Widerrufsfunktion bereit.

Kunden können über die Website einen Widerruf absenden. Odoo speichert diesen Vorgang im Backend, versendet eine Eingangsbestätigung per E-Mail und ermöglicht die interne Bearbeitung des Vorgangs.

Das Modul unterstützt damit einen klaren digitalen Ablauf:

1. Kunde öffnet die Widerrufsseite.
2. Kunde füllt das Formular aus.
3. Kunde prüft seine Angaben.
4. Kunde bestätigt den Widerruf final.
5. Odoo erstellt automatisch einen Widerrufsvorgang.
6. Odoo sendet eine Eingangsbestätigung per E-Mail.
7. Interne Mitarbeitende bearbeiten den Vorgang im Backend.

Wichtig: Das Modul ist eine technische Umsetzungshilfe. Es ersetzt keine rechtliche Prüfung der konkreten Widerrufstexte, Pflichtinformationen und internen Prozesse.

---

## 2. Modulübersicht

Das Repository besteht aus drei Modulen.

### 2.1 Basismodul `odoo_widerrufbutton`

Das Basismodul enthält die eigentliche Widerrufsfunktion.

Funktionen:

- Footer-Button **Vertrag widerrufen**
- Widerrufsseite unter `/widerruf`
- alternative URL `/vertrag-widerrufen`
- öffentliches Formular ohne Login-Zwang
- Pflichtfelder für Name, E-Mail und Bestell- oder Rechnungsnummer
- Auswahl zwischen vollständigem Widerruf, teilweisem Widerruf und sonstiger Mitteilung
- Prüfansicht vor dem finalen Absenden
- finaler Button **Widerruf bestätigen**
- automatische Vorgangsnummer
- Speicherung als Backend-Datensatz
- automatische Eingangsbestätigung per E-Mail
- optionale interne Benachrichtigung
- optionale automatische Aktivität für zuständige Mitarbeitende
- Statusverwaltung
- Anzeige im Kundenportal bei eingeloggten Kunden
- zentrale Einstellungen unter **Einstellungen > Widerrufbutton**

### 2.2 Zusatzmodul `odoo_widerrufbutton_sale`

Dieses Modul erweitert den Widerruf um die Verknüpfung mit Verkaufsaufträgen.

Funktionen:

- Suche nach Verkaufsaufträgen über Auftragsnummer
- Suche über Kundenreferenz
- E-Mail-Abgleich zwischen Widerruf und Verkaufsauftrag
- automatische Zuordnung des Kundenkontos bei Treffer
- Smartbutton **Widerrufe** im Verkaufsauftrag

Das Modul ist optional und wird nur benötigt, wenn Widerrufe direkt mit Angeboten oder Verkaufsaufträgen aus der Odoo-Verkaufsapp verknüpft werden sollen.

### 2.3 Zusatzmodul `odoo_widerrufbutton_account`

Dieses Modul erweitert den Widerruf um die Verknüpfung mit Rechnungen.

Funktionen:

- Suche nach Rechnungsnummer
- Suche nach Zahlungsreferenz
- Suche nach interner Referenz
- E-Mail-Abgleich zwischen Widerruf und Rechnung
- Verknüpfung mit Ausgangsrechnungen und Gutschriften

Das Modul ist optional und wird nur benötigt, wenn Widerrufe direkt mit Rechnungen aus der Odoo-Rechnungsstellung verknüpft werden sollen.

---

## 3. Voraussetzungen

Vor der Nutzung sollten folgende Punkte erfüllt sein.

### 3.1 Technische Voraussetzungen

- Odoo 19 Community ist installiert.
- Die Website-App ist installiert.
- Das technische Modul `mail` ist verfügbar.
- Das Portal ist verfügbar.
- Ein ausgehender Mailserver ist eingerichtet, wenn Eingangsbestätigungen per E-Mail versendet werden sollen.
- Für Verkaufsauftragsverknüpfungen ist die Odoo-Verkaufsapp erforderlich.
- Für Rechnungsverknüpfungen ist die Odoo-Rechnungsstellung bzw. das technische Modul `account` erforderlich.

### 3.2 Fachliche Voraussetzungen

Vor dem produktiven Einsatz sollte festgelegt werden:

- Wer ist intern für eingehende Widerrufe zuständig?
- An welche interne E-Mail-Adresse sollen Hinweise gesendet werden?
- Innerhalb welcher Frist sollen Widerrufe intern geprüft werden?
- Welche Statuslogik soll im Unternehmen genutzt werden?
- Welche Texte sollen auf der Widerrufsseite angezeigt werden?
- Welche E-Mail-Texte sollen an Kunden gesendet werden?
- Wer prüft die rechtliche Ausgestaltung der Texte und Prozesse?

---

## 4. Installation in Odoo

### 4.1 Apps-Liste aktualisieren

Nach dem Einspielen des Moduls muss die App-Liste in Odoo aktualisiert werden.

Vorgehen:

1. In Odoo mit einem Administratorbenutzer anmelden.
2. App **Apps** öffnen.
3. Falls nötig den Entwicklermodus aktivieren.
4. Auf **Apps-Liste aktualisieren** klicken.
5. Nach `Widerrufbutton` suchen.

### 4.2 Basismodul installieren

Installiere zuerst immer das Basismodul:

```text
odoo_widerrufbutton
```

Dieses Modul ist die Grundlage für alle weiteren Funktionen.

### 4.3 Verkaufsmodul installieren

Installiere das Verkaufsmodul nur, wenn Widerrufe mit Verkaufsaufträgen verknüpft werden sollen:

```text
odoo_widerrufbutton_sale
```

Voraussetzung:

```text
sale
```

### 4.4 Rechnungsmodul installieren

Installiere das Rechnungsmodul nur, wenn Widerrufe mit Rechnungen verknüpft werden sollen:

```text
odoo_widerrufbutton_account
```

Voraussetzung:

```text
account
```

---

## 5. Erste Einrichtung

Die zentrale Konfiguration befindet sich unter:

```text
Einstellungen > Widerrufbutton
```

Je nach Odoo-Berechtigung kann es notwendig sein, mit einem Administratorbenutzer oder einem Benutzer mit entsprechenden Rechten angemeldet zu sein.

### 5.1 Footer-Button aktivieren

Einstellung:

```text
Footer-Button anzeigen
```

Wenn diese Option aktiv ist, zeigt die Website im Footer den Button oder Link **Vertrag widerrufen** an.

Empfehlung:

- Für produktive Websites aktivieren.
- Nach Aktivierung die Website im Frontend prüfen.
- Bei mehreren Websites prüfen, ob der Button auf der gewünschten Website erscheint.

### 5.2 Einleitungstext der Widerrufsseite prüfen

In den Einstellungen kann der Einleitungstext der Widerrufsseite gepflegt werden.

Dieser Text sollte kurz erklären:

- wofür das Formular genutzt wird,
- welche Angaben erforderlich sind,
- dass nach dem Absenden eine Eingangsbestätigung versendet wird,
- an wen sich Kunden bei Rückfragen wenden können.

Beispieltext:

```text
Über dieses Formular können Sie einen Vertrag oder eine Bestellung widerrufen. Bitte geben Sie Ihren Namen, Ihre E-Mail-Adresse sowie eine Bestell- oder Rechnungsnummer an, damit wir Ihren Vorgang zuordnen können. Nach dem Absenden erhalten Sie eine Eingangsbestätigung per E-Mail.
```

### 5.3 Kundenportal aktivieren

Einstellung:

```text
Widerrufe im Kundenportal anzeigen
```

Wenn diese Option aktiv ist, können eingeloggte Kunden ihre eigenen Widerrufe im Kundenportal sehen.

Hinweis:

- Die Portalansicht funktioniert nur zuverlässig, wenn der Widerruf einem Kundenkonto zugeordnet ist.
- Bei nicht eingeloggten Kunden erfolgt die Zuordnung in der Regel nur über E-Mail, Auftrag oder Rechnung.

### 5.4 Interne Benachrichtigung aktivieren

Einstellung:

```text
Interne E-Mail bei neuem Widerruf senden
```

Wenn diese Option aktiv ist, sendet Odoo bei einem neuen Widerruf eine interne Benachrichtigung.

Dazu sollte eine interne Empfängeradresse gepflegt werden, zum Beispiel:

```text
widerruf@beispiel.de
```

Empfehlung:

- Verwende eine zentrale Funktionsadresse.
- Stelle sicher, dass mehrere zuständige Personen Zugriff auf dieses Postfach haben.
- Prüfe regelmäßig, ob die E-Mails korrekt zugestellt werden.

### 5.5 Automatische Aktivität aktivieren

Einstellung:

```text
Aktivität bei neuem Widerruf erstellen
```

Wenn diese Option aktiv ist, erstellt Odoo bei einem neuen Widerruf automatisch eine Aktivität für einen zuständigen Benutzer.

Sinnvoll ist diese Funktion, wenn ein bestimmter Mitarbeiter oder ein Team regelmäßig Widerrufe bearbeiten soll.

Wichtige Felder:

- zuständiger Benutzer
- Fälligkeit der Aktivität in Tagen

Beispiel:

```text
Zuständiger Benutzer: Max Mustermann
Fälligkeit: 1 Tag
```

Damit erhält Max Mustermann bei jedem neuen Widerruf eine Aufgabe, die am nächsten Tag fällig ist.

### 5.6 Kunden über Statusänderungen informieren

Einstellung:

```text
Kunden bei Statusänderungen per E-Mail informieren
```

Wenn diese Option vorhanden und aktiv ist, kann Odoo Kunden bei bestimmten Statusänderungen informieren.

Vor produktiver Nutzung sollten die E-Mail-Texte geprüft werden.

---

## 6. Ablauf aus Kundensicht

### 6.1 Einstieg über den Footer

Der Kunde öffnet die Website und klickt im Footer auf:

```text
Vertrag widerrufen
```

Danach öffnet Odoo die Widerrufsseite.

Direkte URLs:

```text
/widerruf
/vertrag-widerrufen
```

### 6.2 Formular ausfüllen

Der Kunde füllt das Formular aus.

Pflichtfelder:

- Name
- E-Mail
- Bestell- oder Rechnungsnummer

Auswahlfeld:

- vollständiger Widerruf
- teilweiser Widerruf
- sonstige Mitteilung

Zusätzlich kann eine Nachricht erfasst werden, sofern das Formular diese Option anzeigt.

Wichtig:

- Es gibt kein Upload-Feld.
- Kunden müssen keine Datei anhängen.
- Das Formular ist öffentlich erreichbar und erfordert keinen Login.

### 6.3 Angaben prüfen

Nach dem Ausfüllen klickt der Kunde auf den Button zur Prüfung der Angaben.

Odoo zeigt anschließend eine Zusammenfassung der eingegebenen Daten an.

Der Kunde kann seine Angaben kontrollieren, bevor der Widerruf final abgeschickt wird.

### 6.4 Widerruf bestätigen

Der Kunde bestätigt den Vorgang über:

```text
Widerruf bestätigen
```

Erst danach wird der Widerruf final in Odoo gespeichert.

### 6.5 Eingangsbestätigung per E-Mail

Nach dem Absenden sendet Odoo eine Eingangsbestätigung an die vom Kunden angegebene E-Mail-Adresse.

Die E-Mail dient als Bestätigung, dass der Widerruf technisch eingegangen ist.

Voraussetzung:

- Der ausgehende Mailserver in Odoo ist korrekt eingerichtet.
- Die eingegebene Kunden-E-Mail-Adresse ist gültig.

---

## 7. Widerrufe im Backend finden

Die eingegangenen Widerrufe findest du im Backend unter:

```text
Widerrufe > Widerrufe
```

Je nach Menüstruktur kann der Menüpunkt auch direkt als **Widerrufe** angezeigt werden.

### 7.1 Listenansicht

In der Listenansicht werden alle Widerrufe angezeigt.

Typische Spalten:

- Vorgangsnummer
- Datum
- Name
- E-Mail
- Bestell- oder Rechnungsnummer
- Art des Widerrufs
- Status

### 7.2 Suche und Filter

Über die Odoo-Suche können Widerrufe gefunden werden.

Sinnvolle Suchbegriffe:

- Vorgangsnummer
- Name
- E-Mail-Adresse
- Bestellnummer
- Rechnungsnummer
- Status

Empfehlung:

- Neue Vorgänge regelmäßig filtern.
- Erledigte Vorgänge nicht löschen, sondern über den Status abschließen.
- Bei Rückfragen immer über die Vorgangsnummer arbeiten.

---

## 8. Einen Widerruf bearbeiten

### 8.1 Widerruf öffnen

Öffne einen Widerruf aus der Listenansicht.

Im Formular siehst du die wichtigsten Angaben zum Vorgang.

Typische Informationen:

- Vorgangsnummer
- Eingangsdatum
- Name des Kunden
- E-Mail-Adresse
- Bestell- oder Rechnungsnummer
- Art des Widerrufs
- Nachricht des Kunden
- zugeordnetes Kundenkonto
- zugeordneter Verkaufsauftrag
- zugeordnete Rechnung
- Website
- E-Mail-Status
- aktueller Status

### 8.2 Chatter verwenden

Im unteren Bereich des Formulars befindet sich der Odoo-Chatter.

Dort können interne Notizen und Nachrichten dokumentiert werden.

Empfehlung:

- Interne Bearbeitungsschritte als Notiz erfassen.
- Telefonische Rückfragen kurz dokumentieren.
- Entscheidungen zum Vorgang nachvollziehbar festhalten.

### 8.3 Status ändern

Das Modul arbeitet mit folgenden Statuswerten:

| Status | Bedeutung |
|---|---|
| Bestätigt | Der Widerruf ist eingegangen und wurde technisch bestätigt. |
| In Bearbeitung | Der Vorgang wird intern geprüft. |
| Erledigt | Der Vorgang wurde abgeschlossen. |
| Abgebrochen | Der Vorgang wurde intern abgebrochen oder ist nicht weiter zu bearbeiten. |

Empfohlene Nutzung:

1. Neuer Vorgang startet mit **Bestätigt**.
2. Sobald ein Mitarbeiter den Vorgang prüft, Status auf **In Bearbeitung** setzen.
3. Nach Abschluss der internen Bearbeitung Status auf **Erledigt** setzen.
4. Nur eindeutig nicht weiterzuführende Vorgänge auf **Abgebrochen** setzen.

### 8.4 Eingangs-E-Mail erneut senden

Im Widerruf kann eine Eingangs-E-Mail erneut gesendet werden.

Button:

```text
E-Mail erneut senden
```

Dies ist sinnvoll, wenn:

- der Kunde die Bestätigung nicht erhalten hat,
- die E-Mail-Zustellung zunächst fehlgeschlagen ist,
- die E-Mail nach einer Korrektur erneut ausgelöst werden soll.

Vor dem erneuten Versand prüfen:

- Ist die E-Mail-Adresse korrekt?
- Ist der Mailserver aktiv?
- Liegt die ursprüngliche E-Mail noch in der Mailqueue?

---

## 9. Empfohlener interner Bearbeitungsprozess

Ein klarer interner Prozess verhindert, dass Widerrufe übersehen werden.

Empfohlener Ablauf:

1. Neuer Widerruf geht über die Website ein.
2. Odoo erstellt automatisch einen Vorgang.
3. Kunde erhält eine Eingangsbestätigung.
4. Zuständiger Benutzer erhält eine Aktivität oder interne E-Mail.
5. Mitarbeiter öffnet den Widerruf im Backend.
6. Mitarbeiter prüft die Angaben.
7. Falls vorhanden, wird Verkaufsauftrag oder Rechnung gesucht und verknüpft.
8. Status wird auf **In Bearbeitung** gesetzt.
9. Interne Prüfung und weitere Bearbeitung erfolgen nach Unternehmensprozess.
10. Ergebnis wird im Chatter dokumentiert.
11. Status wird auf **Erledigt** gesetzt.

Empfehlung:

- Täglich neue Widerrufe prüfen.
- Eine zentrale Verantwortlichkeit festlegen.
- Vorgänge nicht außerhalb von Odoo bearbeiten, ohne dies im Chatter zu dokumentieren.
- Kundenkommunikation nachvollziehbar halten.

---

## 10. Kundenportal

Wenn der Kunde beim Absenden angemeldet war oder der Widerruf später einem Kundenkonto zugeordnet wurde, kann der Vorgang im Portal angezeigt werden.

Portal-URL:

```text
/my/widerrufe
```

Dort sieht der Kunde typischerweise:

- Vorgangsnummer
- Datum
- Bestell- oder Rechnungsnummer
- Art des Widerrufs
- Status
- Detailansicht

Hinweise:

- Portalbenutzer sehen nur ihre eigenen Widerrufe.
- Die Portalansicht ersetzt nicht die interne Bearbeitung im Backend.
- Bei Gastkunden ohne Login kann die Portalzuordnung eingeschränkt sein.

---

## 11. Verkaufsauftrag verknüpfen

Dieser Abschnitt gilt nur, wenn das Zusatzmodul installiert ist:

```text
odoo_widerrufbutton_sale
```

### 11.1 Verkaufsauftrag suchen

Im Widerruf steht ein Button zur Verfügung:

```text
Verkaufsauftrag suchen
```

Die Suche erfolgt über:

- Auftragsnummer
- Kundenreferenz

Das Modul sucht zuerst exakt. Danach kann eine unscharfe Suche erfolgen.

### 11.2 E-Mail-Abgleich

Beim Verknüpfen wird die E-Mail-Adresse des Widerrufs mit dem Verkaufsauftrag abgeglichen.

Das hilft, Fehlzuordnungen zu vermeiden.

Wenn ein passender Auftrag gefunden wird, kann das Kundenkonto im Widerruf automatisch gesetzt werden.

### 11.3 Smartbutton im Verkaufsauftrag

Wenn mindestens ein Widerruf mit einem Verkaufsauftrag verknüpft ist, erscheint im Verkaufsauftrag ein Smartbutton:

```text
Widerrufe
```

Verhalten:

- Bei einem Widerruf öffnet der Smartbutton direkt den Vorgang.
- Bei mehreren Widerrufen öffnet der Smartbutton eine gefilterte Liste.
- Der Smartbutton erscheint nur, wenn es tatsächlich verknüpfte Widerrufe gibt.

### 11.4 Wenn kein Auftrag gefunden wird

Prüfe:

- Ist das Verkaufsmodul installiert?
- Wurde die Auftragsnummer korrekt eingegeben?
- Wurde eventuell eine Rechnungsnummer statt einer Auftragsnummer angegeben?
- Ist die Kundenreferenz im Verkaufsauftrag gepflegt?
- Stimmt die E-Mail-Adresse des Kunden?

---

## 12. Rechnung verknüpfen

Dieser Abschnitt gilt nur, wenn das Zusatzmodul installiert ist:

```text
odoo_widerrufbutton_account
```

### 12.1 Rechnung suchen

Im Widerruf steht ein Button zur Verfügung:

```text
Rechnung suchen
```

Die Suche erfolgt über:

- Rechnungsnummer
- Zahlungsreferenz
- Referenz

Berücksichtigt werden insbesondere:

- Ausgangsrechnungen
- Gutschriften

### 12.2 E-Mail-Abgleich

Beim Verknüpfen wird die E-Mail-Adresse des Widerrufs mit der Rechnung abgeglichen.

Das reduziert das Risiko, einen Widerruf versehentlich einer falschen Rechnung zuzuordnen.

### 12.3 Wenn keine Rechnung gefunden wird

Prüfe:

- Ist das Rechnungsmodul installiert?
- Ist das technische Modul `account` installiert?
- Wurde die Rechnungsnummer korrekt eingegeben?
- Wurde eventuell eine Auftragsnummer statt einer Rechnungsnummer angegeben?
- Ist eine Zahlungsreferenz vorhanden?
- Stimmt die E-Mail-Adresse des Kunden?

---

## 13. E-Mail-Versand prüfen

Für die Nutzung des Moduls ist ein funktionierender E-Mail-Versand wichtig.

### 13.1 Ausgehenden Mailserver prüfen

Pfad in Odoo:

```text
Einstellungen > Technisch > E-Mail > Ausgehende Mailserver
```

Prüfe:

- Ist ein Mailserver eingerichtet?
- Sind Benutzername und Passwort korrekt?
- Ist der SMTP-Server erreichbar?
- Ist die Absenderadresse zulässig?
- Funktioniert eine Test-E-Mail?

### 13.2 E-Mail-Warteschlange prüfen

Pfad in Odoo:

```text
Einstellungen > Technisch > E-Mail > E-Mails
```

Dort kann geprüft werden, ob E-Mails:

- versendet wurden,
- noch ausstehend sind,
- fehlgeschlagen sind.

### 13.3 Typische Ursachen für fehlgeschlagene E-Mails

- falsche SMTP-Zugangsdaten
- blockierter SMTP-Port
- nicht erlaubte Absenderadresse
- ungültige Kunden-E-Mail-Adresse
- fehlende DNS-/SPF-/DKIM-Konfiguration
- Mailserver lehnt automatisierte E-Mails ab

---

## 14. Test vor Produktivbetrieb

Vor dem Einsatz auf einer produktiven Website sollte ein vollständiger Test durchgeführt werden.

### 14.1 Testfall: einfacher Widerruf

1. Website öffnen.
2. Footer-Link **Vertrag widerrufen** anklicken.
3. Formular mit Testdaten ausfüllen.
4. Angaben prüfen.
5. Widerruf bestätigen.
6. Prüfen, ob die Bestätigungsseite erscheint.
7. Prüfen, ob der Backend-Datensatz angelegt wurde.
8. Prüfen, ob die Kunden-E-Mail versendet wurde.
9. Prüfen, ob interne Benachrichtigung oder Aktivität erstellt wurde.

### 14.2 Testfall: Portalbenutzer

1. Als Portalbenutzer anmelden.
2. Widerruf absenden.
3. Backend-Datensatz prüfen.
4. Kundenkonto prüfen.
5. Portal unter `/my/widerrufe` öffnen.
6. Prüfen, ob der Vorgang sichtbar ist.

### 14.3 Testfall: Verkaufsauftrag

Voraussetzung: `odoo_widerrufbutton_sale` ist installiert.

1. Verkaufsauftrag erstellen.
2. Widerruf mit passender Auftragsnummer absenden.
3. Widerruf im Backend öffnen.
4. Button **Verkaufsauftrag suchen** nutzen.
5. Verknüpfung prüfen.
6. Verkaufsauftrag öffnen.
7. Smartbutton **Widerrufe** prüfen.

### 14.4 Testfall: Rechnung

Voraussetzung: `odoo_widerrufbutton_account` ist installiert.

1. Rechnung erstellen.
2. Widerruf mit passender Rechnungsnummer absenden.
3. Widerruf im Backend öffnen.
4. Button **Rechnung suchen** nutzen.
5. Verknüpfung prüfen.

---

## 15. Berechtigungen und Zuständigkeiten

Die konkrete Rechteverwaltung hängt von der Odoo-Installation ab.

Empfehlung:

- Administratoren dürfen das Modul konfigurieren.
- Sachbearbeiter dürfen Widerrufe lesen und bearbeiten.
- Portalbenutzer dürfen nur eigene Widerrufe sehen.
- Öffentliche Website-Besucher dürfen nur das Formular absenden.

Für produktive Systeme sollte geprüft werden:

- Wer darf Widerrufe sehen?
- Wer darf den Status ändern?
- Wer darf E-Mails erneut senden?
- Wer darf Einstellungen ändern?
- Werden personenbezogene Daten nur berechtigten Personen angezeigt?

---

## 16. Datenschutz und Aufbewahrung

Widerrufe enthalten personenbezogene Daten.

Typische Daten:

- Name
- E-Mail-Adresse
- Bestell- oder Rechnungsnummer
- Nachricht des Kunden
- Zeitpunkte und Bearbeitungshistorie

Empfehlung:

- Zugriff auf Widerrufe beschränken.
- Interne Notizen sachlich halten.
- Keine unnötigen sensiblen Daten im Chatter erfassen.
- Aufbewahrungs- und Löschkonzept mit Datenschutzverantwortlichen abstimmen.
- Keine Anhänge über das Formular anfordern, sofern diese nicht erforderlich sind.

Hinweis:

Das Modul enthält kein Upload-Feld im öffentlichen Formular. Dadurch werden unnötige Dateianhänge und zusätzliche personenbezogene Daten vermieden.

---

## 17. Empfohlene Arbeitsweise im Alltag

### 17.1 Tägliche Prüfung

Mindestens einmal täglich sollte geprüft werden:

```text
Widerrufe > Widerrufe
```

Filterempfehlung:

- Status **Bestätigt**
- Status **In Bearbeitung**

### 17.2 Bearbeitung dokumentieren

Jede relevante Bearbeitung sollte im Chatter dokumentiert werden.

Beispiele:

```text
Auftrag SO025 geprüft. Kunde stimmt mit Widerruf überein. Vorgang an Buchhaltung weitergegeben.
```

```text
Rechnung INV/2026/0012 gefunden. Teilwiderruf betrifft Position 2.
```

```text
Kunde telefonisch kontaktiert. Rücksendung angekündigt.
```

### 17.3 Abschluss

Nach Abschluss der Bearbeitung sollte der Status auf **Erledigt** gesetzt werden.

So bleibt die Liste übersichtlich und offene Vorgänge können zuverlässig erkannt werden.

---

## 18. Fehlerbehebung

### 18.1 Footer-Button wird nicht angezeigt

Prüfen:

- Ist das Basismodul installiert?
- Ist die Einstellung **Footer-Button anzeigen** aktiv?
- Wurde die richtige Website geöffnet?
- Ist der Website-Cache aktualisiert?
- Wurde die Seite nach der Installation neu geladen?

Mögliche Lösung:

- Apps-Liste aktualisieren.
- Modul aktualisieren.
- Website im Inkognito-Fenster testen.
- Odoo-Server neu starten, falls technische Änderungen eingespielt wurden.

### 18.2 Widerrufsseite ist nicht erreichbar

Prüfen:

- Ist das Basismodul installiert?
- Funktioniert `/widerruf`?
- Funktioniert `/vertrag-widerrufen`?
- Gibt es einen Reverse Proxy, der die Route blockiert?
- Ist die Website-App aktiv?

### 18.3 Formular lässt sich nicht absenden

Prüfen:

- Sind alle Pflichtfelder ausgefüllt?
- Ist die E-Mail-Adresse formal gültig?
- Wurde eine Widerrufsart ausgewählt?
- Gibt es eine Fehlermeldung im Formular?
- Gibt es Serverfehler im Odoo-Log?

### 18.4 Kunde erhält keine Eingangsbestätigung

Prüfen:

- Ist ein ausgehender Mailserver eingerichtet?
- Ist die E-Mail-Adresse korrekt?
- Liegt die E-Mail in der Warteschlange?
- Wurde die E-Mail als fehlgeschlagen markiert?
- Blockiert der Mailserver den Versand?

Pfad:

```text
Einstellungen > Technisch > E-Mail > E-Mails
```

### 18.5 Interne Benachrichtigung kommt nicht an

Prüfen:

- Ist die interne Benachrichtigung aktiviert?
- Ist eine interne Empfängeradresse eingetragen?
- Ist die Adresse korrekt geschrieben?
- Funktioniert der ausgehende Mailserver?
- Wird die E-Mail eventuell als Spam eingestuft?

### 18.6 Aktivität wird nicht erstellt

Prüfen:

- Ist die automatische Aktivität aktiviert?
- Ist ein zuständiger Benutzer ausgewählt?
- Ist die Fälligkeit korrekt gesetzt?
- Hat der Benutzer Zugriff auf Widerrufe?

### 18.7 Widerruf erscheint nicht im Kundenportal

Prüfen:

- War der Kunde beim Absenden angemeldet?
- Ist ein Kundenkonto im Widerruf gesetzt?
- Ist die Portalansicht in den Einstellungen aktiv?
- Hat der Benutzer Portalzugriff?

### 18.8 Verkaufsauftrag wird nicht gefunden

Prüfen:

- Ist `odoo_widerrufbutton_sale` installiert?
- Ist die Verkaufsapp installiert?
- Stimmt die Auftragsnummer?
- Wurde die Kundenreferenz gepflegt?
- Stimmt die E-Mail-Adresse?

### 18.9 Rechnung wird nicht gefunden

Prüfen:

- Ist `odoo_widerrufbutton_account` installiert?
- Ist `account` installiert?
- Stimmt die Rechnungsnummer?
- Stimmt die Zahlungsreferenz?
- Stimmt die Referenz?
- Handelt es sich um eine Ausgangsrechnung oder Gutschrift?

### 18.10 E-Mail-Abgleich schlägt fehl

Mögliche Ursachen:

- Kunde nutzt eine andere E-Mail-Adresse als im Auftrag.
- Rechnung wurde auf eine andere Kontaktadresse ausgestellt.
- Im Kundenkonto ist keine E-Mail-Adresse hinterlegt.
- Die E-Mail-Adresse enthält Tippfehler.

Empfehlung:

- Vorgang manuell prüfen.
- Kundenkonto, Auftrag und Rechnung vergleichen.
- Abweichung im Chatter dokumentieren.

---

## 19. Häufige Fragen

### Muss der Kunde angemeldet sein?

Nein. Das Formular ist öffentlich erreichbar und kann ohne Login genutzt werden.

### Gibt es einen Dateiupload?

Nein. Das öffentliche Formular enthält kein Upload-Feld.

### Kann ein Widerruf mit einem Verkaufsauftrag verbunden werden?

Ja, wenn das Zusatzmodul `odoo_widerrufbutton_sale` installiert ist.

### Kann ein Widerruf mit einer Rechnung verbunden werden?

Ja, wenn das Zusatzmodul `odoo_widerrufbutton_account` installiert ist.

### Kann der Kunde seine Widerrufe im Portal sehen?

Ja, sofern die Portalansicht aktiviert ist und der Widerruf einem Kundenkonto zugeordnet werden kann.

### Wird automatisch eine E-Mail versendet?

Ja, wenn der ausgehende Mailserver korrekt eingerichtet ist und das E-Mail-Template aktiv ist.

### Kann die Eingangs-E-Mail erneut gesendet werden?

Ja, über den Button **E-Mail erneut senden** im Widerruf.

### Kann der Footer-Button deaktiviert werden?

Ja, über die Einstellungen unter **Einstellungen > Widerrufbutton**.

---

## 20. Checkliste für den Produktivstart

Vor dem Produktivstart sollten folgende Punkte erledigt sein:

- [ ] Basismodul installiert
- [ ] optionale Zusatzmodule bei Bedarf installiert
- [ ] Footer-Button aktiviert
- [ ] Widerrufsseite erreichbar
- [ ] Einleitungstext geprüft
- [ ] E-Mail-Template geprüft
- [ ] ausgehender Mailserver getestet
- [ ] interne Benachrichtigung eingerichtet
- [ ] Aktivität für zuständigen Benutzer eingerichtet
- [ ] Portalansicht geprüft
- [ ] Testwiderruf durchgeführt
- [ ] Eingangsbestätigung erhalten
- [ ] Backend-Datensatz geprüft
- [ ] Verkaufsauftrag-Verknüpfung getestet, falls genutzt
- [ ] Rechnungsverknüpfung getestet, falls genutzt
- [ ] Berechtigungen geprüft
- [ ] Datenschutz- und Aufbewahrungsprozess abgestimmt
- [ ] rechtliche Prüfung der Texte und Prozesse abgeschlossen

---

## 21. Rechtlicher Hinweis

Diese Anleitung beschreibt die Bedienung und empfohlene Nutzung der technischen Umsetzung in Odoo.

Sie stellt keine Rechtsberatung dar. Vor einem produktiven Einsatz sollten insbesondere folgende Punkte rechtlich geprüft werden:

- konkrete Button-Beschriftungen
- Texte auf der Widerrufsseite
- Inhalt der Eingangsbestätigung
- Pflichtangaben im Formular
- Datenschutzinformationen
- Aufbewahrungs- und Löschfristen
- Einbindung in die bestehende Widerrufsbelehrung
- unternehmensinterner Bearbeitungsprozess

---

## 22. Kurzfassung für Anwender

Für die tägliche Arbeit genügt meist dieser Ablauf:

1. Menü **Widerrufe** öffnen.
2. Neue Vorgänge im Status **Bestätigt** prüfen.
3. Auftrag oder Rechnung suchen, falls das passende Zusatzmodul installiert ist.
4. Status auf **In Bearbeitung** setzen.
5. Bearbeitung im Chatter dokumentieren.
6. Vorgang nach Abschluss auf **Erledigt** setzen.

Damit bleibt jeder Widerruf nachvollziehbar im Odoo-Backend dokumentiert.
