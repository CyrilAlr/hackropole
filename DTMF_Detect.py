import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram
import matplotlib.pyplot as plt

def detect_dtmf(wav_file):
    # fréquences DTMF
    LOW_FREQS = [697, 770, 852, 941]  # Lignes
    HIGH_FREQS = [1209, 1336, 1477, 1633]  # Colonnes
    
    # Matrice DTMF
    DTMF_MATRIX = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    
    # Lecture du fichier WAV
    sample_rate, data = wavfile.read(wav_file)
    if len(data.shape) > 1:
        data = data[:, 0]  # Si stéréo, prendre seulement le canal gauche
    
    # Paramètres pour la détection
    window_size = int(0.03 * sample_rate)  # 30ms window
    hop_length = int(0.01 * sample_rate)   # 10ms hop
    
    # Calcul du spectrogramme
    frequencies, times, Sxx = spectrogram(data, fs=sample_rate, 
                                        window='hamming',
                                        nperseg=window_size,
                                        noverlap=window_size-hop_length)
    
    # Paramètres de détection
    freq_tolerance = 30  # Hz
    power_threshold = np.max(Sxx) * 0.1  # 10% du maximum
    min_duration = 3  # Nombre minimum de frames consécutives
    
    # Pour chaque fenêtre temporelle
    dtmf_sequence = []
    current_digit = None
    duration = 0
    
    for t in range(Sxx.shape[1]):
        # Il faut trouver les pics de fréquence
        peaks = []
        for freq_list in [LOW_FREQS, HIGH_FREQS]:
            max_power = 0
            max_freq = None
            for target_freq in freq_list:
                freq_idx = np.argmin(np.abs(frequencies - target_freq))
                power = np.sum(Sxx[freq_idx-1:freq_idx+2, t])
                if power > max_power and power > power_threshold:
                    max_power = power
                    max_freq = target_freq
            if max_freq:
                peaks.append(max_freq)
        
        # Puis identifier la touche, avec un attention particulière à la durée
        # afin d'éviter de rater une touche quand la précédente était la même
        if len(peaks) == 2:
            row = None
            col = None
            for i, f in enumerate(LOW_FREQS):
                if abs(peaks[0] - f) < freq_tolerance:
                    row = i
            for i, f in enumerate(HIGH_FREQS):
                if abs(peaks[1] - f) < freq_tolerance:
                    col = i
            
            if row is not None and col is not None:
                digit = DTMF_MATRIX[row][col]
                if digit == current_digit:
                    duration += 1
                else:
                    if current_digit and duration >= min_duration:
                        dtmf_sequence.append(current_digit)
                    current_digit = digit
                    duration = 1
            else:
                if current_digit and duration >= min_duration:
                    dtmf_sequence.append(current_digit)
                current_digit = None
                duration = 0
        else:
            if current_digit and duration >= min_duration:
                dtmf_sequence.append(current_digit)
            current_digit = None
            duration = 0
    
    # Ajouter le dernier digit si nécessaire
    if current_digit and duration >= min_duration:
        dtmf_sequence.append(current_digit)
    
    return ''.join(dtmf_sequence)

# Main
filename = "DTMFx.wav"  # Exporté depuis audacity en 8000Hz Mono 16Bit
try:
    sequence = detect_dtmf(filename)
    print("Séquence DTMF détectée :")
    print(sequence)
    with open('DTMF_output.txt', 'w') as f:
        f.write(sequence)
    print("\nSéquence enregistrée !")
except Exception as e:
    print(f"Erreur lors de l'analyse : {e}")
