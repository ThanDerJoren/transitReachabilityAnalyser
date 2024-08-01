# Anleitung

Mit dem Plugin Transit Reachability Analyser können Erreichbarkeiten des ÖPNV berechnet und dargestellt werden. Es wird von einem Startpunkt zu jeder Station des ÖPNV-Netzes mithilfe von OpenTripPlanner die schnellste Verbindung berechnet. Als Ergebnis wird ein Punktlayer mit einer Attributtabelle erstellt, der zu jeder Station verschiedene Informationen bereitstellt. Dazu gehören die Reiseaufwandsindikatoren Reisezeit, Reisezeitverhältnis, Gehzeit und Gehdistanz zur ersten Haltestelle sowie die Umsteigehäufigkeit. Zusätzlich sind in der Attributtabelle die gewählte Verbindung und weitere mögliche Verbindungen sichtbar.  
Für jeden Reiseaufwandsindikator stellt das Plugin ein Farbschema bereit, in dem sich der Punktlayer einfärben lässt. Wird auf Basis des Punklayers ein Polygonlayer erzeugt, lässt sich auch dieser von dem Plugin in den verschiedenen Farbschemata einfärben.

## Hinweis

Das Plugin Transit Reachability Analyser ist im Rahmen einer Bachelorarbeit entstanden. Das sollte beim Nutzen der berechneten Daten berücksichtigt werden. Die Berechnungen wurden nicht systematisch auf Plausibilität geprüft. Merkwürdige Daten sollten mit einer weiteren Quelle verglichen werden.

## Kurzanleitung

- GTFS Feed herunterladen. Zum Beispiel von [DELFI e.V.](https://www.opendata-oepnv.de/ht/de/organisation/delfi/startseite?tx_vrrkit_view%5Baction%5D=details&tx_vrrkit_view%5Bcontroller%5D=View&tx_vrrkit_view%5Bdataset_formats%5D%5B0%5D=ZIP&tx_vrrkit_view%5Bdataset_name%5D=deutschlandweite-sollfahrplandaten-gtfs&cHash=01414d5793fcd0abb0f3a2e35176752c) oder [Connect](https://connect-fahrplanauskunft.de/).
- GTFS Feed vorbereiten mithilfe von [gtfstools](https://ipeagit.github.io/gtfstools/).  
- `.osm.pbf` Datei in der Ausdehnung des GTFS Feeds bei [Protomaps](https://app.protomaps.com/) herunterladen.
- [OpenTripPlanner](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) im Terminal ausführen.
- Transit Reachability Analyser öffnen.
    - Erreichbarkeitsanalyse
        - Koordinaten des Startpunkts angeben.
        - Untersuchungstag und -zeitraum festlegen.
        - Gehgeschwindigkeit und maximale Gehzeit wählen.
        - Speicherort für den Punktlayer festlegen.
        - Berechnung durch Button „Reachability Analysis“ starten.
    - Optional: Isochronenlayer oder Buildingslayer mit Attributwerten erstellen.
    - Symbolisierung der Daten
        - Hierfür wird der OTP Server nicht benötigt.
        - Layer wählen (Punkt- oder Polygonlayer möglich).
        - Darzustellenden Indikator festlegen.

