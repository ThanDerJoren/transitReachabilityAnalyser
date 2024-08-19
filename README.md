# Guide
> **Hinweis:** [Die Anleitung auf Deutsch](#anleitung) ist weiter unten zu finden.
> **Note:** Translated from German by ChatGPT

With the *Transit Reachability Analyser* plugin, public transport reachability can be calculated and visualized. Starting from a given point, the fastest route to each station in the public transport network is calculated using OpenTripPlanner (OTP). As a result, a dataset is created in which each station is represented as a point on the map. In QGIS, a dataset consisting of points is referred to as a point layer. Various information is provided for each station, including travel effort indicators such as travel time, travel time ratio, walking time, and walking distance to the first stop, as well as transfer frequency. Additionally, it indicates which public transport connections were identified for the station and which one was selected. Information in QGIS is referred to as attributes and can be displayed via the attribute table of the point layer.

A heatmap can be created for each indicator by coloring the points on the map. In addition to points, areas can also be colored. These can be isochrones or buildings, for example. An isochrone includes all points that can be reached from a starting point within a specified time frame.

> **Note:** The *Transit Reachability Analyser* plugin was developed as part of a bachelor's thesis. The results were only spot-checked for plausibility. A thorough investigation of the results was not conducted. Anomalous data should be compared with additional sources.

## Table of Contents

- [Guide](#guide)
  - [Quick Guide](#quick-guide)
  - [Detailed Guide](#detailed-guide)
    - [Preparing the GTFS Feed](#preparing-the-gtfs-feed)
      - [Downloading the GTFS Feed](#downloading-the-gtfs-feed)
      - [Filtering the GTFS Feed](#filtering-the-gtfs-feed)
    - [Downloading the .osm.pbf File](#downloading-the-osmpbf-file)
    - [Starting OTP](#starting-otp)
    - [Using the Transit Reachability Analyser](#using-the-transit-reachability-analyser)
      - [Installation](#installation)
      - [Reachability Analysis](#reachability-analysis)
      - [Layer Symbolization](#layer-symbolization)
      - [Symbolizing Isochrone Layers](#symbolizing-isochrone-layers)
      - [Symbolizing Building Layers](#symbolizing-building-layers)
    - [Evaluating Data](#evaluating-data)
    - [Possible Solutions](#possible-solutions)
      - [OTP Cannot Be Started](#otp-cannot-be-started)
      - [OTP Crashes When Starting the Server](#otp-crashes-when-starting-the-server)
      - [Problems with the Transit Reachability Analyser](#problems-with-the-transit-reachability-analyser)
      - [Layer Not Found on the Map](#layer-not-found-on-the-map)
      - [Distorted Representation of Layers](#distorted-representation-of-layers)
- [German version](#anleitung)

Example heatmap of the travel time indicator for point and polygon layers, own representation, map data from [OpenStreetMap](https://www.openstreetmap.org):

![punkt-polygon_bsp.png](punkt-polygon_bsp.png)

Excerpt from the attribute table: Route Main Station - Dedekindstraße:

| **name**                                    | Braunschweig, Dedekindstraße                                                                                                                                                                                                                     |
|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **travel time [min]**                      | 19                                                                                                                                                                                                                                                  |
| **travel time ratio**                       | 1.2                                                                                                                                                                                                                                                 |
| **itinerary frequency [min]**               | 30                                                                                                                                                                                                                                                  |
| **walk time [min]**                         | 1.2                                                                                                                                                                                                                                                 |
| **walk distance [m]**                       | 104.1                                                                                                                                                                                                                                               |
| **number of transfers**                     | 0                                                                                                                                                                                                                                                   |
| **travel time car [min]**                   | 15.6                                                                                                                                                                                                                                                |
| **max distance station to stop [m]**       | 44.5                                                                                                                                                                                                                                                |
| **selected itinerary**                      | ['WALK', '411', 'WALK'], duration: 19, frequency: 30.0, meters_to_first_stop: 104.1, walktime_to_first_stop: 1.2, firstStop: Braunschweig Hauptbahnhof, lastStop: Braunschweig, Dedekindstraße;                                           |
| **possible itineraries**                    | ['WALK', '4', 'WALK', '421', 'WALK'], duration: 35, frequency: 15.0, meters_to_first_stop: 157.0, walktime_to_first_stop: 1.9, firstStop: Braunschweig, Hauptbahnhof/Viewegs Garten, lastStop: Braunschweig, Dedekindstraße;<br> ['WALK', '411', '421', 'WALK'], duration: 23, frequency: 15.0, meters_to_first_stop: 104.1, walktime_to_first_stop: 1.2, firstStop: Braunschweig Hauptbahnhof, lastStop: Braunschweig, Dedekindstraße; |

## Quick Guide

1. Prepare the GTFS feed ([Details](#preparing-the-gtfs-feed))
   1. Download the GTFS feed. For example, from [DELFI e.V.](https://www.opendata-oepnv.de/ht/de/organisation/delfi/startseite?tx_vrrkit_view%5Baction%5D=details&tx_vrrkit_view%5Bcontroller%5D=View&tx_vrrkit_view%5Bdataset_formats%5D%5B0%5D=ZIP&tx_vrrkit_view%5Bdataset_name%5D=deutschlandweite-sollfahrplandaten-gtfs&cHash=01414d5793fcd0abb0f3a2e35176752c) or [Connect](https://connect-fahrplanauskunft.de/datenbereitstellung/) ([Details](#downloading-the-gtfs-feed)).
   2. Filter the GTFS feed using [gtfstools](https://ipeagit.github.io/gtfstools/) ([Details](#filtering-the-gtfs-feed)).

2. Download an .osm.pbf file from [Protomaps](https://app.protomaps.com/) that corresponds to the area of the GTFS feed ([Details](#downloading-the-osm-pbf-file)).

3. Start [OpenTripPlanner 2.5](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) via the terminal ([Details](#starting-otp)).

4. Install and open the *Transit Reachability Analyser*.
   1. Reachability Analysis ([Details](#reachability-analysis))
      1. Specify the coordinates of the starting point.
      2. Set the investigation date and period.
      3. Choose walking speed and maximum walking time.
      4. Specify the storage location for the point layer.
      5. Start the calculation by clicking the *Reachability Analysis* button.
   2. Optional: Create isochrone layers or building layers with attribute values ([Details](#symbolizing-isochrone-layers)).
   3. Symbolizing the data ([Details](#symbolizing-isochrone-layers))
      1. The OTP server is not required for this.
      2. Choose a layer (point or polygon layer).
      3. Specify the indicator to be displayed.

## Detailed Guide

In the *Transit Reachability Analyser*, the reachability of stops is to be calculated. For simplification, stops with the same name are grouped into one destination. A destination that aggregates multiple stops is referred to as a station in this work. The common name of the stops is used as the name of the station. Typically, a station combines two stops. However, there are also larger stations that encompass more than two stops with the same name.

### Preparing the GTFS Feed

GTFS feeds enable OpenTripPlanner (OTP) to calculate public transport connections. They contain information about the line offerings and travel times, among other things.

#### Downloading the GTFS Feed

There are various providers from which GTFS feeds can be downloaded. This plugin requires GTFS schedule feeds. Some transport companies offer GTFS feeds directly for their area. However, there are often GTFS feeds covering larger regions and thus containing the offerings of various transport companies. For example, the company [Connect](https://connect-fahrplanauskunft.de/) provides a GTFS feed for Lower Saxony, Germany. The GTFS feed from DELFI e.V. covers all of Germany and can be downloaded via the [Open Data ÖPNV](https://www.opendata-oepnv.de/ht/de/willkommen) portal. Older GTFS feeds are also available under the *Archive* tab.

#### Filtering the GTFS Feed

The *Transit Reachability Analyser* attempts to calculate a connection to each station from the starting point. The more stops present in the GTFS feed, the longer the calculation takes. **Therefore, it is recommended to use a GTFS feed that only covers the area of investigation.** If that is already the case, this section can be skipped. Otherwise, the following is required:

- GTFS feed
- R
- RStudio (optional)
- [gtfstools](https://ipeagit.github.io/gtfstools/)

The goal is to filter all data of a transport company from a larger GTFS feed. The file `agency.txt` in the GTFS feed lists all transport companies whose traffic information is represented in the GTFS feed. In the end, each file of the GTFS feed should only contain information related to that one transport company. To achieve this, gtfstools is used. gtfstools is an R programming language package that allows GTFS feeds to be filtered, among other things, using the `agency_id`. The RStudio IDE provides an environment for working with R.

After R and RStudio have been installed, gtfstools is installed with the following command:
```r
install.packages("gtfstools") 
```

After that, the lines in the following code block can be executed step by step. Please note the following:

- The `agency_id` of the used transport company can be found in the GTFS feed in the file `agency.txt`.
- The file path must be adjusted. It is important to refer to the .zip file. For Windows, the `r` and the parentheses must be retained.
- The new file name must contain *gtfs*, otherwise OTP will not be able to find the file.

```r
library(gtfstools)
path <- r"(C:\Users\Username\Documents\GTFS_Feed_Name.zip)"
gtfs <- read_gtfs(path)
smaller_gtfs <- filter_by_agency_id(gtfs, "12021") # Hier die agency_id ersetzen.
filename <- r"(C:\Users\Username\Documents\Filtered_GTFS_Feed_Name.zip)"
write_gtfs(smaller_gtfs, filename)
```

### Downloading the .osm.pbf File

In addition to a GTFS feed for the public transport offer, OTP also requires information about the associated network of paths. This allows, for example, the calculation of walking routes to stops. For this, OTP uses the pbf format, which stores the information of a section of the OSM map in a file.

There are various ways to obtain an .osm.pbf file. The following tools will be used for the next steps:

- Unzipped GTFS feed
- QGIS
- QuickMapServices plugin
- Protomaps website

It is important at this point that the map in the .osm.pbf file covers at least the area of the GTFS feed. To ensure this, the following steps are necessary:

1. In QGIS, open the *Data Source Manager* (Ctrl+L).
2. Open the *Delimited Text* section.
3. At the top under *File Name*, open the stops.txt file of the reduced GTFS feed.
4. Click on *Add*.
5. Add the OSM map as background using the QuickMapServices plugin.
6. Open the [Protomaps](https://app.protomaps.com/) website.
7. Protomaps allows the creation of a customized map section. Align the section in Protomaps with the location of the stops in QGIS so that the section includes all stops.
8. Use *Create Extract* to create and download the .osm.pbf file.

### Starting OTP

[OpenTripPlanner](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) is a multimodal route planner. The plugin uses this as a backend for the calculation of public transport routes. OTP calculates a graph representing the transport network based on the GTFS feed and the .osm.pbf file. OTP provides a server that can be interacted with through a web browser. Before a calculation can be started with the *Transit Reachability Analyser*, this server must be running. To start OTP, the following is required:

- Java Runtime (JRE) or Java Development Kit (JDK) version 21 or newer.
- OpenTripPlanner version OTP 2.5.0 or newer. To do this, select the desired version on the linked page and download the file with the extension `shaded.jar` [here](https://repo1.maven.org/maven2/org/opentripplanner/otp/).

The following steps can be taken to start OTP, so that a local server is ready:

1. Place the OTP file, the GTFS feed, and the .osm.pbf file in a common folder that contains no other files (e.g., `OTP_City`).
2. Ensure that the name of the GTFS feed contains *gtfs*.
3. Open the terminal.
4. With the following command, OTP will create a graph:
   ```bash
   java -Xmx2G -jar C:\Users\Username\Documents\OTP_City\
      otp-2.5.0-shaded.jar --build --serve C:\Users\Username\Documents\OTP_City
   ```
5. Wait until *Grizzly server running* appears in the terminal. Depending on the file size, this may take several minutes.

Notes:

- The file path is an example for Windows.
- If a folder in the file path contains a space in its name, the terminal may encounter issues.
- `-Xmx` specifies the maximum amount of memory that OTP can use. Since GTFS feeds and .osm.pbf files are relatively large, OTP requires a significant amount of memory.
- If starting the server fails, it can be attempted again with more than 2 GB of memory, while keeping the computer's limits in mind.
- In addition to `--build` and `--serve`, there are other execution options available. For example, a graph can be saved and accessed again, saving time for regular use of the same graph. Details on this can be found in the [OTP documentation](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/).

### Using the Transit Reachability Analyser

The following sections will explain the installation and usage of the plugin. Additionally, the steps needed to color isochrones or buildings using the *Transit Reachability Analyser* will be shown.

#### Installation

For the *Transit Reachability Analyser* to work, the following Python packages must be installed in QGIS:

- requests
- json
- geopandas
- pandas
- geopy

It is quite possible that the packages are already installed. If not, QGIS will display an error message during the installation of the plugin or when starting it. In that case, the packages must be manually installed via `pip`. The method for doing this in QGIS varies by operating system. The following steps are recommended for Windows:

- Open the OSGeo4W shell. This was installed along with QGIS.
- ```bash
   python -m pip install {package name}
   ```
#### Reachability Analysis

To perform an reachability analysis, a value must be defined for each bolded category.

- The starting point of the calculation must be specified using coordinates. The coordinates of a point can be copied from [OpenStreetMap](https://www.openstreetmap.org). By right-clicking on the appropriate point, the option *Show Address* can be selected. This will display the coordinates in the *Search Field*.
- A GTFS feed is only valid for a specific time. When choosing the day, the date should fall within this timeframe.
- When entering values, it is especially important to pay attention to the syntax of the input. The examples in the respective fields can serve as a guide.
- After selecting the walking speed and walking time, the resulting distance in meters can be calculated. This step is optional and serves as a guideline.
- If OTP is started according to the above instructions, the server will start on port number 8080. This setting only needs to be changed if a different port number was specified when starting OTP. If it is unclear whether the connection to OTP works, it can be tested using the appropriate button. This step is optional.
- By confirming the **Get All Stops** button, a point layer with all stops will be created. The attribute table contains a column listing all departure times of each line within the selected time window.
- The **Get All Stations** button creates a point layer where each point summarizes all stops with the same name. No reachability calculations are performed yet, so the runtime is short, but the attribute table remains empty.
- The **Reachability Analysis** button performs the reachability analysis. OTP calculates various connections from the starting point to each station. The plugin selects the fastest connection from the proposed options. Based on the values of this connection, the travel effort indicators are set. The more stations are located in the area, the longer the calculations will take. Depending on processing power, it may take a few minutes for the calculations to finish and for QGIS to become usable again.

#### Layer Symbolization

During symbolization, the columns in the attribute table are used. Therefore, it is important that the names of the columns are not changed. The position can be altered. A layer and an indicator to be symbolized must always be selected. Symbolization can be modified for both point and polygon layers.

#### Symbolizing Isochrone Layers

**Calculating Isochrones**

- Install the Valhalla plugin.
- Open *Toolbox - Valhalla - Pedestrian - Isochrones Pedestrian*.
- FOSSGIS should be preset as the *Provider*.
- Choose a point layer generated with the Transit Reachability Analyser as the *Input Point layer*.
- Select the name as the *Input layer ID Field*. This step is important because the rest of the attributes will be correctly assigned later based on this name.
- The *Mode* of *Shortest* has proven effective.
- Specify the isochrone size.
- Start the calculation.

In principle, other plugins can also be used. However, an API key is usually required, which must first be created (for free). This is not necessary for FOSSGIS. Additionally, relatively many isochrones need to be calculated. Some providers set a limit on the number of calculations per minute, which can prolong the process.  
The size of the isochrones should correspond to a distance that is to be covered at most, for example, 5 minutes. To define the isochrones in Valhalla using a kilometer specification, time and speed must be converted to distance.  
When entering, use a point for decimal values. The comma separates the different sizes of isochrones.

**Assigning Attributes to Isochrones**

- Open *Toolbox - General Vector - Link Attributes by Field Value*.
- *Input Layer*: Polygon layer with the calculated isochrones.
- *Table Column*: Name.
- *Input Layer 2*: Point layer with the attribute table generated by the Transit Reachability Analyser.
- *Table Field 2*: Name.
- *Layer 2 Fields to Copy*: Select all columns to be copied via the button with three dots on the right.
- Start.
- Launch the *Transit Reachability Analyser* and select the isochrone layer for symbolization.

It is crucial that the name column in both the point layer and the isochrone layer are the same. This is definitely true for the layer from which the isochrones were generated. It is advisable to duplicate the isochrone layer to keep an unchanged layer. This way, the isochrones do not need to be recalculated every time.

#### Symbolizing Building Layers

**Downloading the Buildings Layer**

- Install the QuickOSM plugin.
- Open *Vector - QuickOSM - QuickOSM*.
- In *Map settings*, select *Urban*. Alternatively, use the *Key* *building* in *Fast Query*.
- For the download area, select *Layer Extent* from the dropdown menu and use a point layer from the Transit Reachability Analyser.

**Assigning Attributes to Buildings**

- Open *Toolbox - General Vector - Link Attributes by Location*.
- *Link to Objects in*: Buildings layer.
- *Location of Objects*: select intersects.
- *By Comparing with*: Isochrone layer with attributes.
- *Fields to Add*: select all desired attributes via the button with three dots.
- In the dropdown menu, select *Create separate object for each matching object (one-to-many)*.
- Start.
- Select the new layer in Transit Reachability Analyser and change symbolization.

It is important that the text field for *Prefix for linked fields* remains empty. Otherwise, the column names will be altered, and the symbolization of the Transit Reachability Analyser will no longer function.

### Evaluating Data

When evaluating the data, it should be noted that the results only apply to the one starting point. The results cannot and should not be generalized to the entire network and total offering.  
In a non-representative evaluation of the data, it was found that the connections proposed by OTP are optimized for few transfers and not for the shortest travel time.  
The information in the attribute table on walking distances refers only to the path to the first stop. The remaining walking paths, such as those during a transfer or between the last stop and the destination, are not directly considered. They only contribute to the travel time.  
Some calculations of the path length from the last stop to the corresponding station are unrealistically long, which extends the travel time.  
The frequency is only calculated based on the first departures of a connection. Therefore, a frequency change within a search window is not visible. If the focus of the analysis is on frequency, care should be taken that the frequency at the beginning of the time window is representative of the analyzed period.  
Due to unexpected returns from OTP, the frequency calculation is not always accurate. In some cases, the calculated frequency can be better than the actual frequency. If certain values seem unrealistic, they should be double-checked.

### Possible Solutions

In the following sections, problems that may occur when using the *Transit Reachability Analyser* will be addressed. If further problems arise, forums for QGIS or OTP can be consulted. Alternatively, a [pull request](https://github.com/ThanDerJoren/transitReachabilityAnalyser/pulls) for the *Transit Reachability Analyser* can also be written.

#### OTP Cannot Be Started

In the terminal, spaces in a file path cause errors. There should be no spaces in the entire file path specified when starting OTP. If this cannot be avoided, the file path must be enclosed in quotes on Windows.

#### OTP Crashes When Starting the Server

gtfstools does not always filter the GTFS feed from DELFI e.V. correctly. As a result, OTP may not be able to start the server. In advance, the GTFS feed can be checked using the [GTFS validator](https://gtfs-validator.mobilitydata.org/). If the report contains *ERROR*, the GTFS feed cannot be used with OTP. A few *ERROR* messages can be fixed manually. Alternatively, there is the tool [gtfstidy](https://github.com/patrickbr/gtfstidy), which can likely improve GTFS feeds. *WARNINGS* do not need to be addressed.


#### Problems with Transit Reachability Analyser

If the plugin cannot be executed, checking the QGIS log can be helpful. There, the *WARNING* specifies the error preventing the plugin from running. The *INFO* above it indicates what needs to be changed to avoid the error.  
If nothing is calculated despite proper execution, this might be due to the day of calculation. A GTFS feed is only valid for a certain timeframe. If the calculation day falls outside this range, nothing will be calculated, and no error will be reported. To rule out this error, it is best to choose the day the GTFS feed was downloaded as the calculation day.

#### Layer Not Found on the Map

If a layer cannot be found on the map, the first step is to check whether the layer is set to be visible. If so, you can right-click on the layer and select the option *Zoom to Layer*. This will help determine where the layer is displayed. A representation in the wrong location may be due to the choice of the coordinate reference system (CRS).

#### Distorted Representation of Layers

*Transit Reachability Analyser* exports point layers using the coordinate reference system (CRS) EPSG:4326 WGS84. Otherwise, the points would be displayed in the wrong location. In contrast, the OSM background map uses the CRS EPSG:3857 WGS84/Pseudo-Mercator. To ensure this map is displayed without distortion, the CRS of the entire project must be set to EPSG:3857. This can be adjusted at the bottom right in QGIS.

-----------------------
# Anleitung

Mit dem Plugin *Transit Reachability Analyser* können Erreichbarkeiten des ÖPNV berechnet und dargestellt werden. Von einem Startpunkt aus wird zu jeder Station des ÖPNV-Netzes mithilfe von OpenTripPlanner (OTP) die schnellste Verbindung berechnet. Als Ergebnis wird ein Datensatz erstellt, indem jede Station einen Punkt auf der Karte repräsentiert. In QGIS wird ein Datensatz, bestehend aus Punkten, Punktlayer genannt. Zu jeder Station werden verschiedene Informationen bereitgestellt. Dazu gehören die Reiseaufwandsindikatoren Reisezeit, Reisezeitverhältnis, Gehzeit und Gehdistanz zur ersten Haltestelle sowie die Umsteigehäufigkeit. Zusätzlich wird angegeben, welche ÖPNV-Verbindungen zu der Station ermittelt wurden und welche daraus ausgewählt wurde. Informationen werden in QGIS als Attribute bezeichnet und lassen sich über die Attributtabelle des Punktlayers anzeigen.

Für jeden Indikator kann eine Heatmap erstellt werden, indem die Punkte auf der Karte eingefärbt werden. Neben Punkten können auch Flächen eingefärbt werden. Das können zum Beispiel Isochronen oder Gebäude sein. Eine Isochrone beinhaltet alle Punkte, die von einem Startpunkt aus innerhalb einer vorgegebenen Zeitspanne erreichbar sind.

> **Hinweis:** Das Plugin *Transit Reachability Analyser* ist im Rahmen einer Bachelorarbeit entstanden. Die Ergebnisse wurden nur in Stichproben auf Plausibilität geprüft. Eine ausführliche Untersuchung der Ergebnisse wurde nicht durchgeführt. Auffällige Daten sollten mit zusätzlichen Quellen verglichen werden.

## Inhaltsverzeichnis

- [Anleitung](#anleitung)
  - [Kurzanleitung](#kurzanleitung)
  - [Ausführliche Anleitung](#ausführliche-anleitung)
    - [GTFS-Feed vorbereiten](#gtfs-feed-vorbereiten)
      - [GTFS-Feed herunterladen](#gtfs-feed-herunterladen)
      - [GTFS-Feed filtern](#gtfs-feed-filtern)
    - [.osm.pbf-Datei herunterladen](#osmpbf-datei-herunterladen)
    - [OTP starten](#otp-starten)
    - [Transit Reachability Analyser nutzen](#transit-reachability-analyser-nutzen)
      - [Installation](#installation)
      - [Erreichbarkeitsanalyse](#erreichbarkeitsanalyse)
      - [Layer Symbolisierung](#layer-symbolisierung)
      - [Isochronenlayer symbolisieren](#isochronenlayer-symbolisieren)
      - [Gebäudelayer symbolisieren](#gebaeudelayer-symbolisieren)
    - [Daten auswerten](#daten-auswerten)
    - [Mögliche Problemlösungen](#moegliche-problemloesungen)
      - [OTP lässt sich nicht starten](#otp-laesst-sich-nicht-starten)
      - [OTP bricht beim Starten des Servers ab](#otp-bricht-beim-starten-des-servers-ab)
      - [Probleme mit Transit Reachability Analyser](#probleme-mit-transit-reachability-analyser)
      - [Layer ist auf der Karte nicht zu finden](#layer-ist-auf-der-karte-nicht-zu-finden)
      - [Verzerrte Darstellung der Layer](#verzerrte-darstellung-der-layer)



Beispiel Heatmap des Indikators Reisezeit für Punkt- und Polygonlayer, eigene Darstellung, Kartendaten von [OpenStreetMap](https://www.openstreetmap.org):

![punkt-polygon_bsp.png](punkt-polygon_bsp.png)

Auszug aus der Attributtabelle: Strecke Hauptbahnhof - Dedekindstraße:

| **name**                                    | Braunschweig, Dedekindstraße                                                                                                                                                                                                                     |
|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **travel time [min]**                      | 19                                                                                                                                                                                                                                                  |
| **travel time ratio**                       | 1.2                                                                                                                                                                                                                                                 |
| **itinerary frequency [min]**               | 30                                                                                                                                                                                                                                                  |
| **walk time [min]**                         | 1.2                                                                                                                                                                                                                                                 |
| **walk distance [m]**                       | 104.1                                                                                                                                                                                                                                               |
| **number of transfers**                     | 0                                                                                                                                                                                                                                                   |
| **travel time car [min]**                   | 15.6                                                                                                                                                                                                                                                |
| **max distance station to stop [m]**       | 44.5                                                                                                                                                                                                                                                |
| **selected itinerary**                      | ['WALK', '411', 'WALK'], duration: 19, frequency: 30.0, meters_to_first_stop: 104.1, walktime_to_first_stop: 1.2, firstStop: Braunschweig Hauptbahnhof, lastStop: Braunschweig, Dedekindstraße;                                           |
| **possible itineraries**                    | ['WALK', '4', 'WALK', '421', 'WALK'], duration: 35, frequency: 15.0, meters_to_first_stop: 157.0, walktime_to_first_stop: 1.9, firstStop: Braunschweig, Hauptbahnhof/Viewegs Garten, lastStop: Braunschweig, Dedekindstraße;<br> ['WALK', '411', '421', 'WALK'], duration: 23, frequency: 15.0, meters_to_first_stop: 104.1, walktime_to_first_stop: 1.2, firstStop: Braunschweig Hauptbahnhof, lastStop: Braunschweig, Dedekindstraße; |

## Kurzanleitung

1. GTFS-Feed vorbereiten ([Details](#GTFS-Feed-vorbereiten))
   1.  GTFS-Feed herunterladen. Zum Beispiel von [DELFI e.V.](https://www.opendata-oepnv.de/ht/de/organisation/delfi/startseite?tx_vrrkit_view%5Baction%5D=details&tx_vrrkit_view%5Bcontroller%5D=View&tx_vrrkit_view%5Bdataset_formats%5D%5B0%5D=ZIP&tx_vrrkit_view%5Bdataset_name%5D=deutschlandweite-sollfahrplandaten-gtfs&cHash=01414d5793fcd0abb0f3a2e35176752c) oder [Connect](https://connect-fahrplanauskunft.de/datenbereitstellung/) ([Details](#GTFS-Feed-herunterladen)).
   2. GTFS-Feed filtern mithilfe von [gtfstools](https://ipeagit.github.io/gtfstools/) ([Details](#GTFS-Feed-filtern)).

2. Eine .osm.pbf-Datei bei [Protomaps](https://app.protomaps.com/) herunterladen, die dem Gebiet des GTFS-Feeds entspricht ([Details](#osmpbf-datei-herunterladen)).

3. [OpenTripPlanner 2.5](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) über das Terminal starten ([Details](#OTP-starten)).

4. *Transit Reachability Analyser* installieren und öffnen.
   1. Erreichbarkeitsanalyse ([Details](#Erreichbarkeitsanalyse))
      1. Koordinaten des Startpunktes angeben.
      2. Untersuchungstag und -zeitraum festlegen.
      3. Gehgeschwindigkeit und maximale Gehzeit wählen.
      4. Speicherort für den Punktlayer festlegen.
      5. Berechnung durch Button *Reachability Analysis* starten.
   2. Optional: Isochronenlayer oder Gebäudelayer mit Attributwerten erstellen ([Details](#Isochronenlayer-symbolisieren)).
   3. Symbolisierung der Daten ([Details](#Isochronenlayer-symbolisieren))
      1. Hierfür wird der OTP-Server nicht benötigt.
      2. Layer wählen (Punkt- oder Polygonlayer möglich).
      3. Darzustellenden Indikator festlegen.

## Ausführliche Anleitung

In *Transit Reachability Analyser* soll die Erreichbarkeit von Haltestellen berechnet werden. Zur Vereinfachung werden Haltestellen mit gleichem Namen zu einem Ziel zusammengefasst. Ein Ziel, das mehrere Haltestellen zusammenfasst, wird in dieser Arbeit Station genannt. Als Name der Station wird der gemeinsame Name der Haltestellen genutzt. In der Regel fasst eine Station zwei Haltestellen zusammen. Es gibt aber auch größere Stationen, die mehr als zwei Haltestellen mit gleichem Namen vereinen.

### GTFS-Feed vorbereiten

GTFS-Feeds ermöglichen es, OpenTripPlanner (OTP) ÖPNV-Verbindungen zu berechnen. Sie enthalten unter anderem Informationen über das Linienangebot und die Fahrzeiten.

#### GTFS-Feed herunterladen

Es gibt verschiedene Anbieter, über die GTFS-Feeds heruntergeladen werden können. Für dieses Plugin werden GTFS-Schedule-Feeds benötigt. Manche Verkehrsunternehmen bieten für ihr Gebiet direkt einen GTFS-Feed an. Häufig gibt es aber GTFS-Feeds, die eine größere Region abdecken und dadurch das Angebot verschiedener Verkehrsunternehmen enthalten. Für Niedersachsen stellt zum Beispiel das Unternehmen [Connect](https://connect-fahrplanauskunft.de/) einen GTFS-Feed zur Verfügung. Der GTFS-Feed von DELFI e.V. deckt ganz Deutschland ab und lässt sich über das Portal [Open Data ÖPNV](https://www.opendata-oepnv.de/ht/de/willkommen) herunterladen. Über den Reiter *Archiv* sind auch alte GTFS-Feeds verfügbar.

#### GTFS-Feed filtern

*Transit Reachability Analyser* versucht, vom Startpunkt aus zu jeder Station eine Verbindung zu berechnen. Je mehr Stops in dem GTFS-Feed vorhanden sind, desto länger dauert die Berechnung. **Deswegen ist es empfehlenswert, einen GTFS-Feed zu nutzen, der nur das Untersuchungsgebiet abdeckt.** Ist das bereits der Fall, kann dieser Abschnitt übersprungen werden. Ansonsten wird Folgendes benötigt:

- GTFS-Feed
- R
- RStudio (optional)
- [gtfstools](https://ipeagit.github.io/gtfstools/)

Das Ziel ist es, alle Daten eines Verkehrsunternehmens aus einem größeren GTFS-Feed zu filtern. In der Datei `agency.txt` des GTFS-Feeds sind alle Verkehrsunternehmen aufgelistet, deren Verkehrsinformationen in dem GTFS-Feed abgebildet sind. Am Ende sollen in jeder Datei des GTFS-Feeds nur noch Informationen stehen, die zu dem einen Verkehrsunternehmen gehören. Um das zu bewerkstelligen, wird gtfstools benutzt. gtfstools ist ein Package der Programmiersprache R, mit dem GTFS-Feeds unter anderem mithilfe der `agency_id` gefiltert werden können. Die IDE RStudio bietet eine Umgebung, in der mit R gearbeitet werden kann.

Nachdem R und RStudio installiert wurden, wird mit dem folgendem Befehl gtfstools installiert:

```r
install.packages("gtfstools") 
```

Danach können die Zeilen in dem folgenden Code-Block Schritt für Schritt ausgeführt werden. Dabei bitte folgendes beachten:

- Die `agency_id` des verwendeten Verkehrsunternehmens lässt sich in dem GTFS-Feed in der Datei `agency.txt` finden.
- Der Dateipfad muss angepasst werden. Dabei ist es wichtig, auf die .zip-Datei zu verweisen. Für Windows müssen das `r` und die Klammern beibehalten werden.
- Der neue Dateiname muss *gtfs* enthalten, sonst kann OTP die Datei nicht finden.

```r
library(gtfstools)
path <- r"(C:\Benutzer\Benutzername\Dokumente\GTFS_Feed_Name.zip)"
gtfs <- read_gtfs(path)
smaller_gtfs <- filter_by_agency_id(gtfs, "12021") # Hier die agency_id ersetzen.
filename <- r"(C:\Benutzer\Benutzername\Dokumente\Name_gefilterter_GTFS_Feed.zip)"
write_gtfs(smaller_gtfs, filename)
```

### .osm.pbf-Datei herunterladen

Neben einem GTFS-Feed für das ÖPNV-Angebot benötigt OTP auch Informationen über das zugehörige Wegenetz. Damit können zum Beispiel Fußwege zu Haltestellen berechnet werden. Dafür nutzt OTP das Format pbf, welches die Informationen eines Ausschnitts der OSM-Karte in einer Datei speichert.

Es gibt verschiedene Wege, an eine .osm.pbf-Datei zu kommen. Für die nächsten Schritte werden folgende Tools benutzt:

- Entpackter GTFS-Feed
- QGIS
- Plugin QuickMapServices
- Website Protomaps

Wichtig ist an dieser Stelle, dass die Karte in der osm.pbf-Datei mindestens das Gebiet des GTFS-Feeds abdeckt. Um das sicherzustellen, sind folgende Schritte nötig:

1. In QGIS die *Datenquellenverwaltung* öffnen (Strg+L).
2. Den Abschnitt *Getrennte Texte* öffnen.
3. Ganz oben unter *Dateiname* die stops.txt-Datei des verkleinerten GTFS-Feeds öffnen.
4. Auf *Hinzufügen* klicken.
5. Über das Plugin QuickMapServices die OSM-Karte als Hintergrund hinzufügen.
6. Die Website [Protomaps](https://app.protomaps.com/) öffnen.
7. Mit Protomaps lässt sich ein individueller Kartenausschnitt erstellen. Den Ausschnitt in Protomaps mit der Lage der Stops in QGIS abgleichen, damit der Ausschnitt alle Stops beinhaltet.
8. Über *Create Extract* die .osm.pbf-Datei erstellen lassen und herunterladen.


### OTP starten

[OpenTripPlanner](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) ist ein multimodaler Routenplaner. Das Plugin verwendet diesen als Backend für die Berechnung der ÖPNV-Routen. OTP berechnet auf Basis des GTFS-Feeds und der .osm.pbf-Datei einen Graphen, der das Verkehrsnetz repräsentiert. OTP stellt einen Server zur Verfügung, mit dem über einen Webbrowser interagiert werden kann. Bevor eine Berechnung mit *Transit Reachability Analyser* gestartet werden kann, muss dieser Server gestartet sein. Um OTP zu starten, wird Folgendes benötigt:

- Java Runtime (JRE) oder Java Development Kit (JDK) mindestens in der Version Java 21 oder neuer.
- OpenTripPlanner mindestens in der Version OTP 2.5.0 oder neuer. Dafür auf der verlinkten Seite die gewünschte Version auswählen und die Datei mit der Endung `shaded.jar` [herunterladen](https://repo1.maven.org/maven2/org/opentripplanner/otp/).

Mit den folgenden Schritten lässt sich OTP starten, sodass ein lokaler Server bereitsteht:

1. Die OTP-Datei, den GTFS-Feed und die .osm.pbf-Datei in einen gemeinsamen Ordner legen, der keine weiteren Dateien enthält (z.B. `OTP_Stadt`).
2. Sicherstellen, dass in dem Namen des GTFS-Feeds *gtfs* vorkommt.
3. Terminal öffnen.
4. Mit dem folgenden Befehl erstellt OTP einen Graphen:
   ```bash
   java -Xmx2G -jar C:\Benutzer\Benutzername\Dokumente\OTP_Stadt\
   otp-2.5.0-shaded.jar --build --serve C:\Benutzer\Benutzername\Dokumente\OTP_Stadt
   ```
5. Warten, bis im Terminal *Grizzly server running* steht. Je nach Dateigröße kann dies mehrere Minuten dauern.

Hinweise:

- Der Dateipfad ist ein Beispiel für Windows.
- Enthält ein Ordner in dem Dateipfad ein Leerzeichen im Namen, kann es passieren, dass das Terminal Probleme macht.
- `-Xmx` legt fest, wie viel Speicher OTP maximal nutzen darf. Da GTFS-Feeds und .osm.pbf-Dateien relativ groß sind, braucht OTP relativ viel Speicher.
- Klappt das Starten des Servers nicht, kann es mit mehr Speicher als 2 GB erneut versucht werden. Dabei sollten die Grenzen des Computers im Blick behalten werden.
- Statt `--build` und `--serve` gibt es noch weitere Ausführungsmöglichkeiten. Ein Graph lässt sich zum Beispiel speichern und erneut darauf zurückgreifen. Dadurch wird bei regelmäßigem Nutzen des gleichen Graphen Zeit gespart. Details dazu sind in der [Dokumentation von OTP](https://docs.opentripplanner.org/en/latest/Basic-Tutorial/) zu finden.

### Transit Reachability Analyser nutzen

In den folgenden Abschnitten wird die Installation und Nutzung des Plugins erläutert. Zusätzlich werden die Schritte aufgezeigt, die nötig sind, um Isochronen oder Gebäude mithilfe von *Transit Reachability Analyser* einzufärben.

#### Installation

Damit *Transit Reachability Analyser* funktioniert, müssen die folgenden Python-Packages in QGIS installiert sein:

- requests
- json
- geopandas
- pandas
- geopy

Es ist gut möglich, dass die Packages bereits installiert sind. Ist das nicht der Fall, wird QGIS bei der Installation des Plugins oder beim Starten eine Fehlermeldung einblenden. Dann müssen die Packages manuell über `pip` installiert werden. Wie das in QGIS geht, ist für jedes Betriebssystem verschieden. Folgende Schritte werden für Windows empfohlen:

- OSGeo4W shell öffnen. Das wurde zusammen mit QGIS installiert.
- ```bash
   python -m pip install {package name}
   ```

#### Erreichbarkeitsanalyse

Um eine Erreichbarkeitsanalyse durchzuführen, muss für jede fett gedruckte Kategorie ein Wert festgelegt werden.

- Der Startpunkt der Berechnung muss über Koordinaten angegeben werden. Die Koordinaten von einem Punkt können zum Beispiel aus [OpenStreetMap](https://www.openstreetmap.org) kopiert werden. Über einen *Rechtsklick* an den entsprechenden Punkt kann die Option *Adresse anzeigen* gewählt werden. Dadurch werden die Koordinaten in dem *Suchfeld* angezeigt.
- Ein GTFS-Feed gilt nur für eine bestimmte Zeit. Bei der Wahl des Tages sollte das Datum in diesem Zeitraum liegen.
- Bei der Eingabe der Werte ist es vor allem wichtig, auf die Syntax der Eingabe zu achten. Dabei kann sich an den Beispielen in den jeweiligen Feldern orientiert werden.
- Nach Auswahl der Gehgeschwindigkeit und Gehzeit kann die daraus resultierende Distanz in Metern berechnet werden. Dieser Schritt ist optional und dient als Orientierungshilfe.
- Wird OTP nach der obigen Anleitung gestartet, startet der Server auf der Portnummer 8080. Diese Einstellung muss nur geändert werden, wenn beim Starten von OTP eine andere Portnummer angegeben wurde. Ist unklar, ob die Verbindung zu OTP funktioniert, kann dies über den entsprechenden Button ausprobiert werden. Dieser Schritt ist optional.
- Bei der Bestätigung des **Get All Stops**-Buttons wird ein Punktlayer mit allen Haltestellen erzeugt. Die Attributtabelle enthält eine Spalte, in der alle Abfahrtszeiten jeder Linie in dem gewählten Zeitfenster aufgelistet sind.
- Der **Get All Stations**-Button erstellt einen Punktlayer, bei dem je ein Punkt alle Stops mit gleichem Namen zusammenfasst. Es werden noch keine Erreichbarkeiten berechnet, weswegen die Laufzeit kurz ist, die Attributtabelle aber leer bleibt.
- Der **Reachability Analysis**-Button führt die Erreichbarkeitsanalyse durch. OTP berechnet für jede Strecke vom Startpunkt zu den einzelnen Stationen verschiedene Verbindungen. Das Plugin wählt aus den vorgeschlagenen Verbindungen die schnellste aus. Anhand der Werte dieser Verbindung werden die Reiseaufwandsindikatoren gesetzt. Je mehr Stationen in dem Gebiet liegen, desto länger dauern die Berechnungen. Je nach Rechenleistung kann es einige Minuten dauern, bis die Berechnung fertig ist und QGIS wieder nutzbar ist.

#### Layer Symbolisierung

Bei der Symbolisierung werden die Spalten in der Attributtabelle genutzt. Deswegen ist es wichtig, dass die Namen der Spalten nicht verändert werden. Die Position kann verändert werden. Es muss immer ein Layer und ein Indikator, der symbolisiert werden soll, ausgewählt werden. Es kann sowohl die Symbolisierung von Punkt- als auch von Polygonlayer verändert werden.

#### Isochronenlayer symbolisieren

**Isochronen Berechnen**

- Plugin Valhalla installieren.
- *Werkzeugkiste - Valhalla - Pedestrian - Isochrones Pedestrian* öffnen.
- Als *Provider* sollte FOSSGIS voreingestellt sein.
- Als *Input Point layer* einen Punktlayer auswählen, der mit Transit Reachability Analyser berechnet wurde.
- Als *Input layer ID Field* Name auswählen. Dieser Schritt ist wichtig, weil über den Namen später die restlichen Attribute richtig zugeordnet werden.
- Als *Mode* hat sich *Shortest* bewährt.
- Isochronengröße angeben.
- Berechnung starten.

Prinzipiell können auch andere Plugins verwendet werden. Meistens ist aber ein API-Key nötig, der erst (kostenfrei) erstellt werden muss. Das ist bei FOSSGIS nicht nötig. Außerdem müssen relativ viele Isochronen berechnet werden. Manche Anbieter haben ein Limit an Berechnungen pro Minute gesetzt, weswegen das relativ lange dauern kann.  
Die Größe der Isochronen sollte einer Entfernung entsprechen, die am Ende maximal gelaufen werden soll, zum Beispiel 5 Minuten. Um die Isochronen in Valhalla über eine Kilometerangabe zu definieren, müssen Zeit und Geschwindigkeit in Entfernung umgerechnet werden.  
Bei der Eingabe einen Punkt für Dezimalwerte nutzen. Das Komma trennt verschieden große Isochronen.

**Attribute den Isochronen zuweisen**

- *Werkzeugkiste - Vektoren allgemein - Attribute nach Feldwert verknüpfen* öffnen.
- *Eingabelayer*: Polygonlayer mit den berechneten Isochronen.
- *Tabellenspalte*: Name.
- *Eingabelayer 2*: Punktlayer mit Attributtabelle, die über Transit Reachability Analyser berechnet wurde.
- *Tabellenfeld 2*: Name.
- *Layer 2 zu kopierende Felder*: Hier über die drei Punkte rechts alle Spalten auswählen, die kopiert werden sollen.
- Starte.
- *Transit Reachability Analyser* starten und Isochronenlayer für die Symbolisierung auswählen.

Hierbei ist es wichtig, dass die Namensspalte in dem Punkt- und Isochronenlayer gleich sind. Das trifft auf jeden Fall auf den Layer zu, über den die Isochronen generiert wurden. Es empfiehlt sich, den Isochronenlayer zu duplizieren und so einen unveränderten Layer zu behalten. Dadurch müssen die Isochronen nicht immer neu berechnet werden.

#### Gebäudelayer symbolisieren

**Buildingslayer herunterladen**

- Plugin QuickOSM installieren.
- *Vektor - QuickOSM - QuickOSM* öffnen.
- In *Kartenvolage* *Urban* auswählen. Alternativ in *Schnelle Abfrage* den *Schlüssel* *building* nutzen.
- Für den Downloadbereich im Dropdown Menü *Layer-Ausdehnung* auswählen und einen Punktlayer von Transit Reachability Analyser nutzen.

**Attribute den Gebäuden zuordnen**

- *Werkzeugkiste - Vektoren allgemein - Attribute nach Position verknüpfen* öffnen.
- *Mit Objekten verknüpfen in*: Gebäudelayer.
- *Ort der Objekte*: schneidet auswählen.
- *Durch Vergleich mit*: Isochronenlayer mit Attributen.
- *Hinzufügende Felder*: über den Button mit den drei Punkten alle gewünschten Attribute auswählen.
- Im Dropdown Menü *Separates Objekt für jedes passende Objekt erzeugen (eines-zu-vielen)* auswählen.
- Starte.
- Den neuen Layer in Transit Reachability Analyser auswählen und Symbolisierung verändern.

Wichtig ist, dass das Textfeld zu *Präfix für verknüpfte Felder* leer bleibt. Sonst werden die Spaltennamen verändert und dann funktioniert die Symbolisierung von Transit Reachability Analyser nicht mehr.

### Daten auswerten

Beim Bewerten der Daten ist zu beachten, dass die Ergebnisse nur für den einen Startpunkt gelten. Die Ergebnisse können und sollten nicht auf das Gesamtnetz und Gesamtangebot verallgemeinert werden.  
Bei einer nicht repräsentativen Auswertung der Daten zeigte sich, dass die Verbindungen, die von OTP vorgeschlagen werden, auf wenig Umstiege und nicht auf die kürzeste Reisezeit optimiert sind.  
Die Angaben in der Attributtabelle zu Fußstrecken beziehen sich nur auf den Weg zur ersten Haltestelle. Die restlichen Fußwege, zum Beispiel bei einem Umstieg oder zwischen letzter Haltestelle und Ziel, werden nicht direkt betrachtet. Sie fließen nur in die Reisezeit mit ein.  
Manche Berechnungen der Weglänge von der letzten Haltestelle zur zugehörigen Station sind unrealistisch lang. Das verlängert die Reisezeit.  
Der Takt wird nur über die ersten Abfahrten einer Verbindung berechnet. Deswegen ist ein Taktwechsel innerhalb eines Suchfensters nicht sichtbar. Sollte der Fokus der Analyse auf dem Takt liegen, sollte darauf geachtet werden, dass der Takt am Anfang des Zeitfensters repräsentativ für den analysierten Zeitraum ist.  
Aufgrund von unerwarteten Rückgaben von OTP ist die Taktberechnung nicht immer richtig. An manchen Stellen kann der berechnete Takt besser sein, als der tatsächliche Takt. Wirken Werte unrealistisch, sollten diese nachgeprüft werden.

### Mögliche Problemlösungen

In den folgenden Abschnitten wird auf Probleme eingegangen, die bei der Nutzung von *Transit Reachability Analyser* auftreten können. Treten weitere Probleme auf, kann sich an Foren für QGIS oder OTP gewandt werden. Alternativ kann auch ein [Pull request](https://github.com/ThanDerJoren/transitReachabilityAnalyser/pulls) für *Transit Reachability Analyser* geschrieben werden.

#### OTP lässt sich nicht starten

Im Terminal führen Leerzeichen in einem Dateipfad zu Fehlern. In dem gesamten Dateipfad, der beim Starten von OTP angegeben wird, darf kein Leerzeichen vorkommen. Lässt sich das nicht vermeiden, muss bei Windows der Dateipfad in Anführungszeichen angegeben werden.

#### OTP bricht beim Starten des Servers ab

gtfstools filtert nicht immer den GTFS-Feed von DELFI e.V. richtig. Dann kann es sein, dass OTP den Server nicht gestartet bekommt. Im Vorhinein kann der GTFS-Feed mithilfe des [GTFS-validators](https://gtfs-validator.mobilitydata.org/) untersucht werden. Enthält der Bericht *ERROR*, lässt sich der GTFS-Feed nicht mit OTP nutzen. Wenige *ERROR* können manuell behoben werden. Alternativ gibt es noch das Tool [gtfstidy](https://github.com/patrickbr/gtfstidy), mit dem sich wohl GTFS-Feeds verbessern lassen. *WARNINGS* müssen nicht behoben werden.


#### Probleme mit Transit Reachability Analyser

Lässt sich das Plugin nicht ausführen, hilft es, in das Protokoll von QGIS zu schauen. Dort wird in der *WARNING* der Fehler spezifiziert, weswegen das Plugin nicht ausführbar ist. In der *INFO* darüber wird angezeigt, was geändert werden muss, um den Fehler zu vermeiden.  
Wird trotz korrekter Ausführung nichts berechnet, kann das an dem Tag der Berechnung liegen. Ein GTFS-Feed gilt nur für eine bestimmte Zeitspanne. Ist der Berechnungstag außerhalb dieser Spanne, wird nichts berechnet, es kommt aber auch kein Fehler. Zum Ausschließen dieses Fehlers sollte am besten als Berechnungstag der Tag gewählt werden, an dem der GTFS-Feed heruntergeladen wurde.

#### Layer ist auf der Karte nicht zu finden

Ist ein Layer auf der Karte nicht zu finden, sollte als Erstes kontrolliert werden, ob der Layer sichtbar geschaltet ist. Ist das der Fall, lässt sich nach Rechtsklick auf den Layer die Option *Auf Layer zoomen* auswählen. So lässt sich herausfinden, wo der Layer angezeigt wird. Eine Darstellung am falschen Ort kann an der Wahl des Koordinatenbezugssystems (KBS) liegen.

#### Verzerrte Darstellung der Layer

*Transit Reachability Analyser* exportiert die Punktlayer mit dem Koordinatenbezugssystem (KBS) EPSG:4326 WGS84. Sonst würden die Punkte an einem falschen Ort angezeigt werden. Die OSM-Hintergrundkarte hat dagegen das KBS EPSG:3857 WGS84/Pseudo-Mercator. Damit diese Karte verzerrungsfrei dargestellt wird, muss das KBS des gesamten Projektes auf EPSG:3857 gestellt werden. Das lässt sich ganz unten rechts in QGIS einstellen.












[//]: # (# Anleitung)

[//]: # ()
[//]: # (Mit dem Plugin Transit Reachability Analyser können Erreichbarkeiten des ÖPNV berechnet und dargestellt werden. Es wird von einem Startpunkt zu jeder Station des ÖPNV-Netzes mithilfe von OpenTripPlanner die schnellste Verbindung berechnet. Als Ergebnis wird ein Punktlayer mit einer Attributtabelle erstellt, der zu jeder Station verschiedene Informationen bereitstellt. Dazu gehören die Reiseaufwandsindikatoren Reisezeit, Reisezeitverhältnis, Gehzeit und Gehdistanz zur ersten Haltestelle sowie die Umsteigehäufigkeit. Zusätzlich sind in der Attributtabelle die gewählte Verbindung und weitere mögliche Verbindungen sichtbar.  )

[//]: # (Für jeden Reiseaufwandsindikator stellt das Plugin ein Farbschema bereit, in dem sich der Punktlayer einfärben lässt. Wird auf Basis des Punklayers ein Polygonlayer erzeugt, lässt sich auch dieser von dem Plugin in den verschiedenen Farbschemata einfärben.)

[//]: # ()
[//]: # (## Hinweis)

[//]: # ()
[//]: # (Das Plugin Transit Reachability Analyser ist im Rahmen einer Bachelorarbeit entstanden. Das sollte beim Nutzen der berechneten Daten berücksichtigt werden. Die Berechnungen wurden nicht systematisch auf Plausibilität geprüft. Merkwürdige Daten sollten mit einer weiteren Quelle verglichen werden.)

[//]: # ()
[//]: # (## Kurzanleitung)

[//]: # ()
[//]: # (- GTFS Feed herunterladen. Zum Beispiel von [DELFI e.V.]&#40;https://www.opendata-oepnv.de/ht/de/organisation/delfi/startseite?tx_vrrkit_view%5Baction%5D=details&tx_vrrkit_view%5Bcontroller%5D=View&tx_vrrkit_view%5Bdataset_formats%5D%5B0%5D=ZIP&tx_vrrkit_view%5Bdataset_name%5D=deutschlandweite-sollfahrplandaten-gtfs&cHash=01414d5793fcd0abb0f3a2e35176752c&#41; oder [Connect]&#40;https://connect-fahrplanauskunft.de/&#41;.)

[//]: # (- GTFS Feed vorbereiten mithilfe von [gtfstools]&#40;https://ipeagit.github.io/gtfstools/&#41;.  )

[//]: # (- `.osm.pbf` Datei in der Ausdehnung des GTFS Feeds bei [Protomaps]&#40;https://app.protomaps.com/&#41; herunterladen.)

[//]: # (- [OpenTripPlanner]&#40;https://docs.opentripplanner.org/en/latest/Basic-Tutorial/&#41; im Terminal ausführen.)

[//]: # (- Transit Reachability Analyser öffnen.)

[//]: # (    - Erreichbarkeitsanalyse)

[//]: # (        - Koordinaten des Startpunkts angeben.)

[//]: # (        - Untersuchungstag und -zeitraum festlegen.)

[//]: # (        - Gehgeschwindigkeit und maximale Gehzeit wählen.)

[//]: # (        - Speicherort für den Punktlayer festlegen.)

[//]: # (        - Berechnung durch Button „Reachability Analysis“ starten.)

[//]: # (    - Optional: Isochronenlayer oder Buildingslayer mit Attributwerten erstellen.)

[//]: # (    - Symbolisierung der Daten)

[//]: # (        - Hierfür wird der OTP Server nicht benötigt.)

[//]: # (        - Layer wählen &#40;Punkt- oder Polygonlayer möglich&#41;.)

[//]: # (        - Darzustellenden Indikator festlegen.)

