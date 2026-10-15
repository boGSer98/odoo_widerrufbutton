# Dokumentzuordnung für Widerrufe – 19.0.8.0.0

## Installation und Rechte

Das Basismodul bleibt ohne Verkauf oder Rechnungsstellung verwendbar. Für die Dokumentintegration werden zusätzlich `odoo_widerrufbutton_sale` und/oder `odoo_widerrufbutton_account` installiert. Ein neues Vorgangs-/Ticketmodell wird nicht eingeführt.

Bearbeiter benötigen die Widerrufsrolle **und** passende native Dokumentrechte (Verkauf bzw. Rechnungsstellung/Leserechte). Smartbuttons öffnen ausschließlich Dokumente, die der aktuelle Benutzer tatsächlich lesen darf. Es wird kein pauschaler Zugriff auf Verkauf/Rechnungsstellung erteilt.

## Automatisch beim Eingang

- Eingetragene Referenz gegen Angebots-/Auftragsnummer oder Kundenreferenz sowie Rechnungs-/Gutschriftnummer, Zahlungsreferenz und externe Rechnungsreferenz prüfen.
- Nur exakte und innerhalb des Unternehmens eindeutige Treffer verknüpfen. Leere Referenzen und `/` sind keine verwertbaren Belegnummern. Kein `ilike`, kein beliebiger erster Treffer bei mehreren Ergebnissen.
- Zum Auftrag gehörende native Rechnungen/Gutschriften ebenfalls über Smartbuttons zeigen. Bei einer direkt verknüpften Rechnung werden die über Rechnungszeilen tatsächlich verbundenen Aufträge berücksichtigt.
- Die E-Mail-Abweichung ist ein Bearbeiterhinweis. Freie Formulardaten und Belegnummern ändern niemals die verifizierte Portalidentität.
- Eine Dokumentverknüpfung entscheidet nicht über die rechtliche Wirksamkeit des Widerrufs und führt weder Stornierung noch Erstattung aus.

## Manuell zuordnen

1. Widerruf öffnen und **Dokument zuordnen** wählen.
2. Dokumentart **Angebot / Auftrag** oder **Kundenrechnung / Gutschrift** wählen.
3. Ein vorhandenes Dokument desselben Unternehmens auswählen und **Zuordnen** klicken. Eine Belegneuanlage über diesen Dialog ist deaktiviert.
4. Der Vorgang wird als manuell zugeordnet markiert; die Auswahl wird im Chatter dokumentiert. Eine neue manuelle Auswahl ersetzt frühere direkte Zuordnungen, sodass keine alte Rechnung am falschen Auftrag hängen bleibt.
5. **Dokumente prüfen** sucht erneut, überschreibt aber keine manuelle Auswahl. Das gilt auch bei späterer Korrektur des Arbeitsfelds Bestell-/Rechnungsnummer.
6. **Zuordnung entfernen** löscht ausschließlich Links und gibt automatische Suche wieder frei. Originaleingang und Dokumente bleiben erhalten.

**Angebote / Aufträge** und **Rechnungen / Gutschriften** erscheinen als Smartbuttons bei vorhandenen, zugänglichen Dokumenten. Ein Treffer öffnet die Formularansicht, mehrere Treffer eine gefilterte Liste. Auftrag und Rechnung haben umgekehrt einen Widerrufe-Smartbutton; dessen Zähler berücksichtigt die nativen Querverbindungen und die Widerrufsrechte.

Bestehende Widerrufe werden bei der Installation nicht ungefragt massenhaft neu verknüpft. Sie können über **Dokumente prüfen** oder manuell zugeordnet werden.

## Verifikation

Native Tests decken automatischen Auftrag-/Rechnungstreffer, Gutschrift, Auftrags-Rechnungs-Kette, manuelle Zuordnung, Neuzuordnung, Entfernung, Erhalt bei erneuter Suche, eindeutige Suche, Unternehmens- und Dokumentrechte, blockierte Lieferantenrechnungen, rückwärtige Smartbuttons und unveränderte Finanzzustände ab. Die Sicherheitsregressionen des Basismoduls bleiben Bestandteil der Testsuite.

Der manuelle Ablauf und das Öffnen der vorhandenen Rechnung werden zusätzlich im echten Odoo-Webclient auf einem isolierten Klon geprüft. Keine echten Kundenmails, Zahlungen, Stornierungen oder Erstattungen als Funktionsprobe auslösen.
