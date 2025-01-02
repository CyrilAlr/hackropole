# Objet

Ce document a pour objet de fournir une solution à l'épreuve crypto "[hamac](https://hackropole.fr/fr/challenges/crypto/fcsc2022-crypto-hamac/)" d'hackropole.

# Phase d'étude

Deux fichiers sont fournis pour cette épreuve :

 - Un fichier python `hamac.py`
 - Un fichier json comprenant trois éléments ("iv", "c" et "h")

## Etude du code python

Le code commence par demander un mot de passe, puis génère un HMAC (Hash-based Message Authentication Code) basé sur SHA-256. Une donnée fixe, `b"FCSC2022"`est mise à jour dans l'instance HMAC pour produire un hash unique.

    print("Enter your password")
    password = input(">>> ").encode()
    h = HMAC.new(password, digestmod = SHA256)
    h.update(b"FCSC2022")
Un Vecteur d'Initialisation (IV) aléatoire de 16 octets est généré. L'IV est nécessaire pour le mode CBC. Ensuite, une clé de 256 bits (32 octets) est dérivée du mot de passe en appliquant SHA-256.

    iv = get_random_bytes(16)
    k  = SHA256.new(password).digest()
Le contenu d'un fichier `flag.txt` est lu et rempli pour que sa taille soit un multiple de 16 octets (taille des blocs AES). Le contenu est ensuite chiffré avec AES en mode CBC, en utilisant la clé dérivée et le vecteur d'initialisation.

    c  = AES.new(k, AES.MODE_CBC, iv = iv).encrypt(pad(open("flag.txt", "rb").read(), 16))

Enfin, un dictionnaire contenant les éléments suivants est créé  puis sauvegardé :
-   `iv` : Le vecteur d'initialisation, encodé en hexadécimal ;
-   `c` : Le texte chiffré, encodé en hexadécimal ;
-   `h` : Le HMAC calculé, en format hexadécimal.

Le fichier généré est `output.txt`, fourni dans l'épreuve.

    r = { "iv": iv.hex(), "c": c.hex(), "h": h.hexdigest(), }
    open("output.txt", "w").write(json.dumps(r))

## Elaboration d'un mode d'attaque

Sans connaître le mot de passe utilisé, il est impossible de déchiffrer le fichier fourni. L'auteur nous met cependant sur la voie avec un indice dans la description de l'épreuve :

> Connaissez-vous l’existence de `rockyou` ?

Il semble donc que la solution réside dans l'utilisation du fameux dictionnaire de mot de passe afin de réaliser un "Brut Force Attack". Il y a fort à parier que le mot de passe choisi a été extrait du dictionnaire pour nous faciliter la tâche ...

# Phase de réalisation

Afin de déchiffrer ce fichier, il faudra élaborer un script qui, pour chaque mot de passe présent dans le dictionnaire :
- Calcul le HMAC du mot de passe testé en reproduisant la logique de chiffrement utilisée
- Compare le HMAC obtenu à celui du JSON

Si les HMAC correspondent, nous aurons trouvé le mot de passe. Il ne restera alors qu'à déchiffrer la valeur de "c" en utilisant "iv" et le mot de passe trouvé.

## Développement du script

Etant plus à l'aise avec C# qu'avec Python, je commence par développer un script dont les entrées sont le fichier `output.txt` et le dictionnaire `rockyou.txt`.

Le code parcourt l'ensemble du dictionnaire pour réaliser la comparaison de HMAC et déchiffre le message si un mot de passe est trouvé. Une fonction est dédiée à ce déchiffrage en fin de code.

    using System;
    using System.IO;
    using System.Text;
    using System.Security.Cryptography;
    using System.Text.Json;
    
    // Lire le fichier output.txt
    Console.WriteLine($"Reading the ouptut.txt file...");
    string jsonContent = File.ReadAllText("output.txt");
    var output = JsonSerializer.Deserialize<Output>(jsonContent);
    
    // Convertir les valeurs hexadécimales en bytes
    byte[] iv = Convert.FromHexString(output.iv);
    byte[] ciphertext = Convert.FromHexString(output.c);
    byte[] targetHmac = Convert.FromHexString(output.h);
    
    // Message constant pour le HMAC
    byte[] hmacMessage = Encoding.ASCII.GetBytes("FCSC2022");
    Console.WriteLine($"Starting BFA using RockYou...");
    // Démarrer une BFA en testant chaque ligne du fichier
    using (var reader = new StreamReader("rockyou.txt"))
    {
        string password;
        int count = 0;
        while ((password = reader.ReadLine()) != null)
        {
            count++;
            if (count % 10000 == 0)
                Console.WriteLine($"Tested {count} passwords...");
    
            try
            {
                byte[] passwordBytes = Encoding.UTF8.GetBytes(password);
    
                // Calculer le HMAC avec le mot de passe actuel
                byte[] hmac = ComputeHMAC(passwordBytes, hmacMessage);
    
                // Vérifier si le HMAC correspond
                if (BitConverter.ToString(hmac).Replace("-", "").ToLower() == output.h)
                {
                    Console.WriteLine($"\nFound password: {password}");
    
                    // Déchiffrer le message
                    try
                    {
                        string decryptedText = DecryptAES(passwordBytes, iv, ciphertext);
                        Console.WriteLine("\nDecrypted message:");
                        Console.WriteLine(decryptedText);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Decryption failed: {ex.Message}");
                    }
                    return;
                }
                
            }
            catch (Exception)
            {
                // Ignorer les mots de passe qui causent des erreurs
                continue;
            }
        }
    }
    
    Console.WriteLine("Password not found!");
    
    public class Output
    {
        public string iv { get; set; }
        public string c { get; set; }
        public string h { get; set; }
    }
    
    static byte[] ComputeHMAC(byte[] key, byte[] message)
    {
        using (var hmac = new HMACSHA256(key))
        {
            return hmac.ComputeHash(message);
        }
    }
    
    static byte[] ComputeSHA256(byte[] input)
    {
        using (var sha256 = SHA256.Create())
        {
            return sha256.ComputeHash(input);
        }
    }
    
    static string DecryptAES(byte[] key, byte[] iv, byte[] ciphertext)
    {
        using (var aes = Aes.Create())
        {
            aes.Key = ComputeSHA256(key); // La clé est le hash SHA256 du mot de passe
            aes.IV = iv;
            aes.Mode = CipherMode.CBC;
            aes.Padding = PaddingMode.PKCS7;
    
            using (var decryptor = aes.CreateDecryptor())
            using (var msDecrypt = new MemoryStream(ciphertext))
            using (var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read))
            using (var srDecrypt = new StreamReader(csDecrypt))
            {
                return srDecrypt.ReadToEnd();
            }
        }
    }

## Exploitation

J'enregistre ce script sous le nom `camah.cs` (car il fait l'inverse de `hamac.py`).
Le script est ensuite lancé depuis une commande développeur :

    dotnet-script camah.cs
Il testera un peu plus de 4910000 mots de passe en quelques secondes, avant de livrer son verdict :

    Tested 4910000 passwords...
    
    Found password: omgh4xx0r
    
    Decrypted message:
    FCSC{5bb0780f8af31f69b4eccf18870f493628f135045add3036f35a4e3a423976d6}

Fin de l'épreuve :) !
