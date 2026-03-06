# Readme

Ein kleines Tool zur Inventarisierung via QR Codes.

## Voraussetzungen

- Microsoft Excel
- Git
- Python (Getestet mit Python 3.14)
- Erlaube Skript-Execution auf Windows (Zur Aktivierung des Python Virtual-Environments)
- OpenSSH auf Windows aktivieren

## Powershell als Administrator

Das erlaubt das ausführen von Skripten.
```powershell
Set-ExecutionPolicy RemoteSigned
```

Installiert git:
```powershell
winget install git
```

Installiert python:
```powershell
winget install python
```

Aktiviert Openssh Client Funktionalität
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

SSH Agent Dienste aktivieren, um authentifizierung gegenüber dem Server zu erlauben
```powershell
Set-Service ssh-agent -StartupType Automatic
Start-Service ssh-agent
```

## Powershell als User

Um ein Public-Private Key-Pair zu erstellen, muss man den Befehl `ssh-keygen -t ed25519 -a 100 -C "inventar"` ausführen. !Achtung! für richtige Deployments wird stark empfohlen eine PassPhrase zu verwenden! 

Den folgenden Befehl dann wieder mit dem Nutzeraccount ausführen:
`ssh-add $env:USERPROFILE\.ssh\id_ed25519`

Verifizieren das es geklappt hat mit `ssh-add -l`.

Der Private-Key `id_ed25519` muss unbedingt geheim gehalten werden, es ist wie ein Passwort! 
Der Public Key `id_ed25519.pub` muss auf dem Server in die `~/.ssh/authorized_keys` kopiert werden.

## Installation auf Windows

### 1. Download der notwendigen Files

Öffne Powershell und klone das Git-Repo mit dem Befehl `git clone https://github.com/Chewiiee/Inventar`

Navigieren in den Ordner `Inventar` und erstelle in Python VirtualEnvironment mit dem Befehl `python -m venv venv`.

Aktiviere das Virtual Environment und installiere die notwendigen Dependencies `.\venv\Scripts\activate`
`pip install -r requirements.txt`

## Enviroment konfigurieren

Im Ordner die Datei `env.template` kopieren und zu `.env` umbenennen. Die Werte müssten angepasst werden.

## Excel Datei erstellen

Die Excel Datei `inventar_template.xlsm` auf den Desktop kopieren und zu `inventar.xlsm` umbenennen.

`inventar.xlsm` öffnen, dann unter 'Datei -> Optionen -> `Customize Ribbons` -> Developer/Entwickler` Haken setzen. Dann einmal Excel schließen und die Datei erneut öffnen.

Dann im Reiter `Developer/Entwickler` rechts auf 'VBAProject (inventar.xlsx)' klicken, und Einfügen -> Modul auswählen.

Im Module den `basePath` anpassen

Beim click auf 'veröffentlichen' werden auf dem Desktop nun die Ordner `html` und `qrcodes` erstellt und die html Dateien auf dem Server veröffentlicht.

Die QR Codes sollten bereits mit dem Smartphone scanbar sein und die Informationen aus der Liste anzeigen.

## WebServer Konfiguration

Auf dem Server muss ein Webserver eingerichtet werden. Hier kann ein beliebiger Webserver gewählt werden, welcher statische Dateien ausliefern kann. Ein Beispiel wäre Caddy. Eine einfache Konfiguration für den Webserver wäre:

```json
https://eigene.domain.de {
    # Serve files from /var/www/html/inventar
    root * /var/www/html/inventar

    # Enable file server
    file_server

    # Optional: Enable HTTP Basic Authentication
    basicauth {
        hier_muss_ein_Passwort_Hash_stehen
    }
}
```

Ein Passwort Hash can auf einer Linux Maschine auf welcher Caddy installiert ist z.B. mit dem Befehl `caddy hash-password` erstellt werden.