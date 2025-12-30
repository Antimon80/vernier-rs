# Initialisierung und Betriebsart

## init
Initialisierung:
- Spektrometer anschliessen
- LoggerPro starten
- Betriebsart ist default auf `Absorption`
- `Erfassungszeit` ist default auf 15 ms
- LoggerPro schliessen
- Spektrometer trennen


## change_mode
### absorbance
- Spektrometer ist angeschlossen
- LoggerPro ist gestartet 
- Betriebsart ist auf auf eine der möglichen Optionen (siehe Tabelle) eingestellt
- Betriebsart auf `Absorbanz` ändern
- `Erfassungszeit` ändert sich (siehe Tabelle)
- Lichtquelle ändert sich (siehe Tabelle)
- Paketaufzeichnung beenden

| **fluorescence_405nm**   | **fluorescence_500nm**   | **intensity**            | **transmittance**         |
| ------------------------ | ------------------------ | ------------------------ | ------------------------- |
| 30 ms &rarr; 15 ms       | 30 ms &rarr; 15 ms       | 30 ms &rarr; 15 ms       | bleibt bei 15 ms          |
| 400 nm LED stellt ab     | 500 nm LED stellt ab     | Weisslicht LED stellt an | Lichtquelle bleibt gleich |
| Weisslicht LED stellt an | Weisslicht LED stellt an | ---                      | ---                       |


### fluorescence_405nm
- Spektrometer ist angeschlossen
- LoggerPro ist gestartet 
- Betriebsart ist auf auf eine der möglichen Optionen (siehe Tabelle) eingestellt
- Betriebsart auf `Fluoreszenz 405 nm` ändern
- `Erfassungszeit` ändert sich (siehe Tabelle)
- Lichtquelle ändert sich (siehe Tabelle)
- Paketaufzeichnung beenden

| **absorbance**           | **fluorescence_500nm** | **intensity**        | **transmittance**        |
| ------------------------ | ---------------------- | -------------------- | ------------------------ |
| 15 ms &rarr; 30 ms       |                        |                      |                          |
| Weisslicht LED stellt ab | 500 nm LED stellt ab   | 405 nm LED stellt an | Weisslicht LED stellt ab |
| 405 nm LED stellt an     | 405 nm LED stellt an   | ---                  | 405 nm LED stellt an     |


### fluorescence_500nm
- Spektrometer ist angeschlossen
- LoggerPro ist gestartet 
- Betriebsart ist auf auf eine der möglichen Optionen (siehe Tabelle) eingestellt
- Betriebsart auf `Fluoreszenz 500 nm` ändern
- `Erfassungszeit` ändert sich (siehe Tabelle)
- Lichtquelle ändert sich (siehe Tabelle)
- Paketaufzeichnung beenden

| **absorbance**           | **fluorescence_405nm** | **intensity**        | **transmittance**        |
| ------------------------ | ---------------------- | -------------------- | ------------------------ |
| 15 ms &rarr; 30 ms       |                        |                      |                          |
| Weisslicht LED stellt ab | 405 nm LED stellt ab   | 500 nm LED stellt an | Weisslicht LED stellt ab |
| 500 nm LED stellt an     | 500 nm LED stellt an   | ---                  | 500 nm LED stellt an     |


### intensity
- Spektrometer ist angeschlossen
- LoggerPro ist gestartet 
- Betriebsart ist auf auf eine der möglichen Optionen (siehe Tabelle) eingestellt
- Betriebsart auf `Intensität` ändern
- `Erfassungszeit` ändert sich (siehe Tabelle)
- Lichtquelle ändert sich (siehe Tabelle)
- Paketaufzeichnung beenden

| **absorbance**           | **fluorescence_405nm** | **fluorescence_500nm** | **transmittance**        |
| ------------------------ | ---------------------- | ---------------------- | ------------------------ |
| 15 ms &rarr; 30 ms       |                        |                        |                          |
| Weisslicht LED stellt ab | 405 nm LED stellt ab   | 500 nm LED stellt ab   | Weisslicht LED stellt ab |


### transmittance
- Spektrometer ist angeschlossen
- LoggerPro ist gestartet 
- Betriebsart ist auf auf eine der möglichen Optionen (siehe Tabelle) eingestellt
- Betriebsart auf `Transmission` ändern
- `Erfassungszeit` ändert sich (siehe Tabelle)
- Lichtquelle ändert sich (siehe Tabelle)
- Paketaufzeichnung beenden

| **absorbance**            | **fluorescence_405nm**   | **fluorescence_500nm**   | **intensity**            |
| ------------------------- | ------------------------ | ------------------------ | ------------------------ |
| bleibt bei 15 ms          |                          |                          |                          |
| Lichtquelle bleibt gleich | 405 nm LED stellt ab     | 500 nm LED stellt ab     | Weisslicht LED stellt an |
| ---                       | Weisslicht LED stellt an | Weisslicht LED stellt an | ---                      |
