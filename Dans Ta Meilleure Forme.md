
# Objet

Ce document a pour objet de fournir une solution à l'épreuve crypto "[Dans Ta Meilleure Forme ](https://hackropole.fr/fr/challenges/misc/fcsc2024-misc-dans-ta-meilleure-forme/)" d'hackropole.
Dans le cadre de ce CTF,  un fichier audio (.wav) contenant une séquence de tons DTMF (Dual-Tone Multi-Frequency), le type de signaux utilisés par les téléphones à touches, est mis à disposition.

# Phase d'étude
L'observation du fichier dans Audacity a révélé une série claire de signaux DTMF, caractérisés par :
 - Des impulsions uniformes et distinctes 
- Des séparations nettes entre les signaux
- Une amplitude constante pendant chaque ton
- Une absence de chevauchement entre les signaux 
![Aperçu du signal dans Audacity](https://github.com/CyrilAlr/hackropole/blob/master/DTMF_signal_1.png)

