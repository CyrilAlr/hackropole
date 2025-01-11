import gzip
from pathlib import Path

def read_input_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def decode_gzip_data(encoded_data):
    # Remplacement de caractères pour obtenir de l'hexadécimal
    hex_data = encoded_data.replace('*', 'E').replace('#', 'F')
    
    # Conversion de l'hexadécimal en bytes
    try:
        binary_data = bytes.fromhex(hex_data)
    except ValueError as e:
        print(f"Error converting hex: {e}")
        return None
    
    # Sauvegarde en GZip
    with open('output.gz', 'wb') as f:
        f.write(binary_data)
        print("Saved compressed data to 'output.gz'")
    
    # Tentative de décompression
    try:
        decompressed = gzip.decompress(binary_data)
        return decompressed
    except Exception as e:
        print(f"Error decompressing: {e}")
        return None

# Lecture du fichier de DTMF extraits
encoded = read_input_file('dtmf_output.txt')

if encoded:
    # Décoder ...
    result = decode_gzip_data(encoded)

    if result:
        print("Ooooooh yeah !")
else:
    print("Failed to read input file")