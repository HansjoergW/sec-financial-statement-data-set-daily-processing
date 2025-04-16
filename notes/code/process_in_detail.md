#Ablauf
1. täglich/regelmässig prüfung der sec index files
    1. grundsätzlich erfolgt die prüfung für die index files der letzten vier Monate
        1. zuerst wird das älteste geprüft
        1. wurde das file noch nicht verarbeitet (tabelle sec-index-file) oder ist es im process "progress", so erfolgt die verarbeitung
        1. die Datei wird heruntergeladen und im Verzeichnis feed gespeichert.
        1. falls neu nötig wird ein eintrag erzeugt,bzw. angepasst (sec-index-file), ältere files werden mit status "done" versehen
        1. sind reports vorhanden, die noch nicht in der db sind (tabelle sec-feeds), dann werden diese hinzugefügt
2. fehlende xbrlInsUrl Einträge werden nachgeführt. Es kommt oft vor, dass die "direkte" XBRLInsDatei nicht vorhanden ist und dass diese anders erzeugt worden ist (suffix htm). Das erfolgt jedoch nicht nach einem konkreten Schema, weshalb die index.json Dateien dieser Reports untersucht werden müssen.
3. duplicate check wird durchgeführt. Es kann vorkommen, dass ein Report in zwei aufeinanderfolgenden Monaten erfolgt. Ist das der Fall, wird der 2. Report mit dem Status duplicate versehen

download der xml-dateien 
1. nur nicht duplicated selectieren
2. Dateien runterladen und speichern -> beim Namen wird die ADSH nummer als Prefix vorangestellt, sowohl für num, wie auch für pre Dateien
       
