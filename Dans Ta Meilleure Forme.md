
# Objet

Ce document a pour objet de fournir une solution à l'épreuve crypto "[Dans Ta Meilleure Forme ](https://hackropole.fr/fr/challenges/misc/fcsc2024-misc-dans-ta-meilleure-forme/)" d'hackropole.
Dans le cadre de ce CTF,  un fichier audio (.wav) contenant une séquence de tons DTMF (Dual-Tone Multi-Frequency), le type de signaux utilisés par les téléphones à touches, est mis à disposition.

# Phase d'étude
L'observation du fichier dans Audacity a révélé une série claire de signaux [DTMF](https://en.wikipedia.org/wiki/DTMF), caractérisés par :
- Des impulsions uniformes et distinctes (environ 50ms chacune)
- Des séparations nettes entre les signaux (entre 30ms et 40ms)
- Une amplitude constante pendant chaque ton
- Une absence de chevauchement entre les signaux 

![Aperçu du signal dans Audacity](https://github.com/CyrilAlr/hackropole/blob/master/DTMF_signal_1.png)

Une rapide analyse de spectre montre des piques de fréquences qui se détachent nettement et qui nous permettront rapidement de retrouver les touches à pour chaque partie du signal.
![Analyse de spectre dans Audacity](https://github.com/CyrilAlr/hackropole/blob/master/DTMF_signal_2.png)

# Etape 1 : extraction de la séquence DTMF
Je commence par développer un script Python utilisant scipy pour décoder les tons DTMF avec les caractéristiques suivantes :
- Utilisation de la transformée de Fourier (spectrogramme) pour détecter les fréquences
- Matrices de fréquences DTMF standard (697-1633 Hz)
- Paramètres optimisés :
- Fenêtre d'analyse de 30ms
- Tolérance de fréquence de 30 Hz (même si les signaux semblent de bonne qualité)
- Seuil de puissance adaptatif
- Vérification de la durée minimale des tons

[Script de détection DTMF_detect.py](https://github.com/CyrilAlr/hackropole/blob/master/DTMF_Detect.py)

J'exporte ensuite depuis Audacity un nouveau fichier wav, débarassé de la conversation du début, en 8000Hz Mono et je lance la détection.
La séquence extraite commence par `1#8B0800000000000003*C5B`, ce qui est un premier indice crucial.
# Etape 2 : Etude de la séquence extraite
Le DTMF compte, en standard, 16 touches, nous pouvons donc aisément le rapprocher de l'hexadécimal en remplaçant les touches "*" et "#".
L'observation de la séquence a révélé un pattern intéressant :
- Début par `1#8B08` 
- Utilisation exclusive des caractères 0-9, A-D, * et #
En remplaçant :
- '*' par 'E'
- '#' par 'F'

On obtient `1F8B08...` qui est le "magic number" caractéristique du format GZIP !
# Etape 3 : Décodage
Je développe alors un second script pour :
1. Remplacer * et # par leurs équivalents hexadécimaux (E et F)
2. Convertir la chaîne hexadécimale en bytes
3. Décompresser le GZIP résultant

[Script de décodage DTMF_decode.py](https://github.com/CyrilAlr/hackropole/blob/master/DTMF_decode.py)

Le GZIP contient un fichier binaire linux et un README_PLEASE.TXT qui nous invite à lancer le programme afin d'obtenir le flag ... Fin de l'épreuve :) !


