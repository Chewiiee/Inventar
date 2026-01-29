# Anforderungen

Abgeschottetes Firmennetzwerk:
    - Gibt es ein Regens-Wagner weites Firmennetz?
    - Hat jeder Standort ein eigenes Firmennetzwerk?
    - Wird ein eigener DNS Server betrieben?
    - Können statische IP Adressen für Geräte vergeben werden?
    - Ist das Internet aus dem Firmennetzwerk zugänglich?

## Infrastruktur (Vorschlag)

- RaspberryPi oder andere MiniPC

## Freigaben

- Gerät(Webserver) braucht eine statische IP Adresse im Firmennetzwerk
- Gerät(Webserver) braucht einen Domain Name welcher zumindest im Firmennetzwerk auf die IP des Raspi resolved.
- Es wird ein TLS Zertifikat benötigt. Lets Encrypt funktioniert aber nur für öffentliche Domains, eventuell gibt es einen ACME PROXY?
- Alternativ: Eventuell gibt es Unternehmsweites Root Zertifkat welches als Trusted auf den Unternehmensgeräten installiert ist?
- Firewall des RaspberryPi muss Port 80 und 443 erlauben.
- Unternehmesfirewall muss Trafic zum Raspberry Pi aus Standortnetzwerk auf Port 80/443 tcp erlauben.
- Create ssh key pair for sftp
- Create Password for User on Raspberry Pi

## Anforderungen Excel

- Jedes Gerät braucht eine unique ID (einzigartier Identifier)

- VBA Makro, welches aus einer Excel Tabelle ein HTML Template befüllt
    - Wenn ein Eintrag erneuert wird, soll das HTML File neu geschrieben werden.
    - Wenn ein Eintrag gelöscht wird, soll das HTML File gelöscht werden.
    - Wenn ein Eintrag hinzugefügt wird, soll ein neues HTML File erstellt werden
    - Wenn ein Eintrag noch nicht vollständig ist, sollen die Felder des HTMLs erstmal leer bleiben

- VBA Makro, welches mit dem Server (Raspi) spricht und die Dateien auf den Server kopiert/synchronisiert.

- VBA Makro, welches einen "https://.." link kodiert und einen QR Code generiert

## Anforderungen Webserver

- Keine größeren Hardware Anforderungen.
- Caddy oder Nginx als Webserver.
- Muss nur statische HTML Seiten ausliefern.
- Passwort Schutz: Bei funktionierender TLS Verschlüsselung kann HTTP Basic Auth verwendet werden.
- Passwort kann evtl. im Geräte Passwortmanager/Browser gespeichert werden für die Usability?

## Regelmäßige Aufgaben


- Zertifikat erneuerung: Automatisch über z.B. ACME oder händisch
- Pflege Excel Tabelle
- QR Codes müssen an Geräten angebracht werden.
- Beim Ausmustern von einem Gerät: Excel Tabelle muss gelöscht werden.

## Anforderungen Kenntnisse zur Umsetzung

- VBA Scripting
- HTML
- Python ? (-> More like basic programming)
- Encryption ? (-> Konzept)
- Webserver ? (-> Konzept)
- Netzwerktechnologien ? (-> Konzept)
- Linux ? (-> Besser für Webhosting, offener Standard, keine Abhängigkeit von Microsoft)
