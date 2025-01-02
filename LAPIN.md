# Objet

Ce document a pour objet de fournir une solution à l'épreuve crypto "[La PIN](https://hackropole.fr/fr/challenges/crypto/fcsc2021-crypto-lapin/)" d'hackropole.

# Phase d'étude

Deux fichiers sont fournis pour cette épreuve :

 - Un fichier python `lapin.py`
 - Un fichier texte contenant de une ligne encodée en hexadécimal 

## Etude du code python

Le code commence par demander un mot code pin compris entre 1 et 9998 inclus. Les code PIN `0000` et `9999` ne sont donc pas acceptés.

    while True: 
    pin = int(input(">>> PIN code (4 digits): ")) 
    if 0 < pin < 9999: break
    
Ensuite, un fichier flag.txt, contenant la réponse de l'épreuve, est lu. 
Puis, le code PIN est dérivé par `scrypt`, une fonction de dérivation de clé qui permet de générer une clé cryptographique à partir d'un mot de passe
La fonction prend le code PIN converti en bytes avec `long_to_bytes(pin)` comme entrée, ainsi qu'un sel (`b"FCSC"`) pour empêcher les attaques par dictionnaire - cela ajoute un facteur d'entropie.

    flag = open("flag.txt", "rb").read()
    k = scrypt(long_to_bytes(pin), b"FCSC", 32, N = 2 ** 10, r = 8, p = 1)

Le nombre de bits générés par `scrypt` est fixé à 32 bytes (donc une clé de 256 bits). `N`, `r`, et `p` sont des paramètres utilisés pour la configuration de l'algorithme `scrypt`, qui ajuste la sécurité et la lenteur du calcul de la clé :
    -   `N = 2 ** 10` : définit le facteur de coût computationnel (c'est-à-dire combien de fois l'algorithme doit être répété).
    -   `r = 8` et `p = 1` sont des paramètres spécifiques au processus de dérivation de la clé.
La clé est stockée dans la variable `k`.
Le code vient ensuite créer une instance `AES`  avec la clé `k` dérivée précédemment. Le mode `AES.MODE_GCM` est utilisé, ce qui permet un chiffrement authentifié avec vérification de l'intégrité.  

    aes = AES.new(k, AES.MODE_GCM)
    c, tag = aes.encrypt_and_digest(flag)

Le message (`flag`) est chiffré avec la méthode `encrypt_and_digest()`, qui retourne deux valeurs :
    -   `c` : le texte chiffré.
    -   `tag` : le tag d'authentification, utilisé pour vérifier l'intégrité du message lors du déchiffrement.

Enfin, le message final est  `enc` est créé par  la concaténation de trois parties :
-   `nonce` : le nonce, un chiffre aléatoire généré pour ce chiffrement par AES
-   `c` : le texte chiffré.
-   `tag` : le tag d'authentification

La valeur de `enc` est convertie en hexadécimal avant d'être enregistrée dans un fichier de sortie.

    enc = aes.nonce + c + tag
    print(enc.hex())

## Elaboration d'un mode d'attaque

Le mode de chiffrage utilisé ici est couteux et rendrait une attaque "Brut Force" trop coûteuse dans un contexte classique. Cependant, le nombre de combinaisons à essayer est très faible : moins de 10 000 - l'attaque est donc réalisable. Voilà de quoi rappeler que non, un code PIN à 4 chiffres, ça n'est pas une sécurité acceptable dans la plupart des cas (courrez désactiver Windows Hello :D).

# Phase de réalisation

Afin de déchiffrer ce fichier, il faudra élaborer un script qui reconvertira le message en ascii puis testera tous les code PIN de 1 à 9998 pour le déchiffrer.
Nous pouvons recalculer `k` pour chaque valeur de PIN et initialiser un AES avec cette valeur et le `nonce`, récupéré dans le fichier.

En tentant de déchiffrer le message avec ces valeurs et le tag, lui aussi récupéré dans le fichier, nous saurons si le PIN fonctionne ou s'il faut passer au suivant.

## Développement du script

Voici le script python développé et s'appuyant sur `output.txt` pour récupérer les valeurs d'entrée de l'algorithme.
Il fait exactement l'inverse de `lapin.py`, donc se nomme très logiquement `nipal.py` ...

    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import scrypt
    from Crypto.Util.number import long_to_bytes
    import binascii
    
    # Lecture et décodage du fichier chiffré (en hexadécimal)
    with open("output.txt", "r") as f:
        enc_hex = f.read().strip()
    
    # Conversion hexadécimale vers bytes
    enc = binascii.unhexlify(enc_hex)
    
    # Extraction des composants nécessaires (nonce, ciphertext, tag)
    nonce = enc[:16]  # Les 16 premiers octets pour le nonce
    ciphertext = enc[16:-16]  # Le contenu chiffré
    tag = enc[-16:]  # Les 16 derniers octets pour le tag

    # Tentative de déchiffrement avec tous les codes PIN possibles
    for pin in range(10000):  # De 0000 à 9999
        try:
            # Génération de la clé avec scrypt
            k = scrypt(long_to_bytes(pin), b"FCSC", 32, N=2**10, r=8, p=1)
            
            # Initialisation du déchiffrement AES en mode GCM
            aes = AES.new(k, AES.MODE_GCM, nonce=nonce)
            
            # Tentative de déchiffrement
            flag = aes.decrypt_and_verify(ciphertext, tag)
            
            print(f"PIN trouvé : {pin}")
            print(f"Contenu déchiffré : {flag.decode('utf-8')}")
            break  # Arrête la boucle une fois le bon PIN trouvé
        except (ValueError, KeyError):
            # Continue si le déchiffrement échoue pour ce PIN
            continue
    else:
        print("Aucun PIN valide trouvé.")

## Exploitation

    python nipal.py
    PIN trouvé : 6273
    Contenu déchiffré : FCSC{c1feab88e6c6932c57fbaf0c1ff6c32e51f07ae87197fcd08956be4408b2c802}

Fin de l'épreuve :) !

