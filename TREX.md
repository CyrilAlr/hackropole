


# Objet

Ce document a pour objet de fournir une solution à l'épreuve crypto [TRex](https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-t-rex/) d'hackropole.

# Phase d'étude

Deux fichiers sont fournis pour cette épreuve :

 - Un fichier python `T-Rex.py`
 - Un fichier texte contenant de une ligne encodée en hexadécimal 

## Etude du code python

Le code est assez simple : 
Une clé est d'abord générée, d'une longueur de 16 bytes (128 bits) et est passée à la classe TRex (Text Rex). 

    E = TRex(os.urandom(16))
    
C'est ici que cela se complique. La classe, à l'initialisation, va calculer un IV en dérivant la clé selon la fonction suivante :

    R(x) = ((2 * x + 1) * x) mod M
    M = 2^128

Donc à chaque dérivation 

    R(x) = 2x²+x mod (2^128)

Voici le code de la classe qui réalise cette action :

    class TRex:
        def __init__(self, key):
            N = len(key)
            M = 2 ** (8 * N)
            self.key = key
            self.iv = int.from_bytes(key, "big")
            R = lambda x: ((2 * x + 1) * x)
            for _ in range(31337):
                self.iv = R(self.iv) % M
            self.iv = int.to_bytes(self.iv, N, "big")
    
        def encrypt(self, data):
            E = AES.new(self.key, AES.MODE_CBC, iv = self.iv)
            return self.iv + E.encrypt(pad(data, 16))

La dérivation est réalisée 31337 fois - un clin d'œil de l'auteur au "L33t".
Enfin, le flag est chiffré en AES CBC et il est écrit, à la suite de l'IV, dans un fichier qui nous est fourni.

## Analyse mathématiques

AES avec un clé de 128 bits n'est absolument pas attaquable directement, et la taille de la clé indique qu'une approche en brut force est impensable. 

On répète assez souvent qu'en utilisant AES CBC, l'IV (dont l'objectif est de produire des contenus différents avec la même clé et les mêmes valeurs en clair) devrait être obtenu de manière parfaitement aléatoire pour ne pas être recalculé. C'est donc très certainement la bonne approche.

Analyse de la fonction de dérivation de clé et de la possibilité d'inversion
Compréhension de la fonction R(x)
La fonction R(x) proposée est une fonction mathématique qui prend un entier x en entrée et retourne un entier compris entre 0 et M-1 (inclus), où M est une puissance de 2. Cette fonction est utilisée de manière itérative 31337 fois pour dériver l'IV à partir d'une clé.

**Caractéristiques clés de R(x) :**

 - Non-linéaire: La présence du terme x² rend la fonction non-linéaire, ce qui complique son inversion.
 - Modulo M: L'opération modulo M limite la plage des valeurs de sortie,
   ce qui peut entraîner des collisions (deux entrées différentes
   donnant la même sortie).
 - Itérations: L'application répétée de la fonction augmente
   considérablement la complexité du calcul et rend l'inversion encore
   plus difficile.

En théorie, on pourrait donc penser que la réversion de l'IV vers la clé est impossible... c'est tout ce qu'il faut pour avoir encore plus envie de le faire.

# Phase de réalisation


Inverser une fonction non linéaire telle que celle ci est donc  compliqué à cause du **modulo**, qui rend la fonction périodique, et de la perte d'information induite par les itérations successives. Avec 31337 itérations, remonter à la clé initiale devient un défi majeur, car il faut retrouver x à chaque étape sans pouvoir annuler directement R(x).

L'astuce utilisée repose sur une **inversion bit par bit**. Plutôt que d'inverser R(x) d'un coup, on reconstruit x progressivement, en testant chaque bit du moins significatif au plus significatif. 
À chaque étape, on active un bit i si cela rend le résultat cohérent avec y dans le contexte du modulo M. Cela permet de contourner les contraintes imposées par R(x).

En vérifiant uniquement les i+1 bits significatifs à chaque étape (grâce à un masque binaire), on s'assure que chaque bit de x est correct.

Enfin, en appliquant cette inversion sur 31337 itérations, on remonte progressivement à l'IV initial, converti en entier. La clé récupérée est ensuite utilisée avec AES en mode CBC pour déchiffrer les données. Ce processus est un équilibre efficace entre exploration bit par bit et calcul modulo, permettant de déjouer une dérivation complexe de l'IV.

## Développement du script

Voici le script python développé et s'appuyant sur `output.txt` pour récupérer les valeurs d'entrée de l'algorithme.

    import os
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    from tqdm import tqdm
    
    def R(x: int, M: int) -> int:
        return ((2 * x + 1) * x) % M
    
    def find_inverse_bitwise(y: int, M: int) -> int:
        x = 0
        nbits = M.bit_length() - 1  # pour 2^128, c'est 128 bits
        
        # Résolution bit par bit, du moins significatif au plus significatif
        for i in range(nbits):
            mask = 1 << i
            # Test avec le bit à 0 puis 1, garde la valeur qui donne le bon résultat
            x_test = x | mask
            if (R(x_test, M) - y) & ((1 << (i+1)) - 1) == 0:
                x = x_test
        return x
    
    def reverse_derivation(iv: bytes, num_iterations: int = 31337) -> bytes:
        M = 2 ** (8 * len(iv))
        current = int.from_bytes(iv, "big")
        
        for _ in tqdm(range(num_iterations)):
            current = find_inverse_bitwise(current, M)
        
        return current.to_bytes(len(iv), "big")
    
    def main():
        with open("output.txt", "r") as f:
            ciphertext = bytes.fromhex(f.read().strip())
        
        iv, encrypted_data = ciphertext[:16], ciphertext[16:]
        key = reverse_derivation(iv)
        
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        flag = unpad(cipher.decrypt(encrypted_data), 16).decode()
        print(f"Flag: {flag}")
    
    if __name__ == "__main__":
        main()

## Exploitation

    100%|████████████████████████████████████| 31337/31337 [00:02<00:00, 13512.02it/s]
    Flag: FCSC{54a680c151c2bff32fd2fdc12b4f8558012dc71e429f075bab6bfc0322354bf4}

Et comme dirait Duke Caboom : "Ohhhhh, yeah !"

