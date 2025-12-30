# Dokumentation Wireshark Logging

1. Initialisierung und Betriebsart
- Das Gerät wird beim Öffnen der App automatisch erkannt und initialisiert
- Das Gerät unterstützt die folgenden Betriebsarten:
  - `Absorption`: default nach der Initialisierung eingstellt
  - `Transmission`
  - `Fluoreszenz 405 nm`
  - `Fluoreszenz 500 nm`
  - `Intensität`: zeichnet mit Hilfe einer Glasfaser die Emission einer externen Lichtquelle auf
  - `Unkalibrierte Messwerte`: erfasst Rohdaten als Counts
- Details siehe: [init_mode.md](init_mode.md)
- Log-Daten: 
  - docs\wireshark\capture_files
    - Der Name es Unterverzeichnisses bezieht sich beim Wechsel des Betriebsmodus auf den Endzustand
    - Das Unterverzeichnis `absorbance` im Ordner `change_mode` enthält die files für den Zustandswechsel in **beide** Richtungen
  - docs\wireshark\init
  - docs\wireshark\change_mode
    - Der Name des übergeordneten Ordners bezieht sich auf den Endzustand
    - Der Name des Unterverzeichnisses bezieht sich auf den Ausgangszustand
2. Konfiguration
3. Datenerfassung