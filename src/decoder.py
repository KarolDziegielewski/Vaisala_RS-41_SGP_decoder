import numpy as np
from scipy.io import wavfile
import struct
import math
from datetime import datetime, timedelta
import argparse
import json
import csv
# Maska XOR (pseudo-losowa sekwencja) używana do descramblingu, długość 64 bajty
XOR_MASK = [
    0x96, 0x83, 0x3E, 0x51, 0xB1, 0x49, 0x08, 0x98, 
    0x32, 0x05, 0x59, 0x0E, 0xF9, 0x44, 0xC6, 0x26,
    0x21, 0x60, 0xC2, 0xEA, 0x79, 0x5D, 0x6D, 0xA1,
    0x54, 0x69, 0x47, 0x0C, 0xDC, 0xE8, 0x5C, 0xF1,
    0xF7, 0x76, 0x82, 0x7F, 0x07, 0x99, 0xA2, 0x2C,
    0x93, 0x7C, 0x30, 0x63, 0xF5, 0x10, 0x2E, 0x61,
    0xD0, 0xBC, 0xB4, 0xB6, 0x06, 0xAA, 0xF4, 0x23,
    0x78, 0x6E, 0x3B, 0xAE, 0xBF, 0x7B, 0x4C, 0xC1
]

def ecef_to_lla(x, y, z):
    """
    Konwertuje współrzędne kartezjańskie ECEF na klasyczne 
    współrzędne geograficzne WGS84 (szerokość, długość, wysokość).
    Zaimplementowane na podstawie oryginalnego wzoru z kodu C.
    """
    a = 6378137.0
    b = 6356752.31424518
    
    e = math.sqrt((a**2 - b**2) / (a**2))
    ee = math.sqrt((a**2 - b**2) / (b**2))
    
    p = math.sqrt(x**2 + y**2)
    if p == 0:
        return 0.0, 0.0, 0.0
        
    lam = math.atan2(y, x)
    t = math.atan2(z * a, p * b)
    
    phi = math.atan2(
        z + ee**2 * b * math.sin(t)**3,
        p - e**2 * a * math.cos(t)**3
    )
    
    # Promień krzywizny
    R = a / math.sqrt(1 - e**2 * math.sin(phi)**2)
    h = p / math.cos(phi) - R
    
    lat = math.degrees(phi)
    lon = math.degrees(lam)
    
    return lat, lon, h

def parse_frame(descrambled_bytes):
    # Sprawdzenie, czy ramka ma odpowiednią długość
    if len(descrambled_bytes) < 320:
        return None
        
    try:
        # Numer ramki: offset 0x03B (59), 2 bajty, unsigned short (H)
        frame_nb = struct.unpack_from("<H", descrambled_bytes, 0x03B)[0]
        
        # ID sondy: offset 0x03D (61), 8 bajtów, tekst ASCII
        sonde_id_bytes = descrambled_bytes[0x03D : 0x03D + 8]
        sonde_id = sonde_id_bytes.decode('ascii').strip('\x00')
        
        # Czas GPS (Tydzień i Sekundy): offsety 0x095 i 0x097
        gps_week = struct.unpack_from("<H", descrambled_bytes, 0x095)[0]
        gps_tow_ms = struct.unpack_from("<I", descrambled_bytes, 0x097)[0]
        gps_tow_sec = gps_tow_ms / 1000.0
        
        # Konwersja czasu GPS na datę i godzinę (Epoka GPS zaczęła się 6 stycznia 1980)
        gps_epoch = datetime(1980, 1, 6)
        frame_time = gps_epoch + timedelta(weeks=gps_week, seconds=gps_tow_sec)
        
        # Współrzędne ECEF (X, Y, Z w centymetrach): offset 0x114, 4 bajty, signed int (i)
        ecef_x_cm = struct.unpack_from("<i", descrambled_bytes, 0x114)[0]
        ecef_y_cm = struct.unpack_from("<i", descrambled_bytes, 0x118)[0]
        ecef_z_cm = struct.unpack_from("<i", descrambled_bytes, 0x11C)[0]
        
        # Zamiana na metry
        x, y, z = ecef_x_cm / 100.0, ecef_y_cm / 100.0, ecef_z_cm / 100.0
        
        # Transformacja na stopnie i wysokość n.p.m.
        lat, lon, alt = ecef_to_lla(x, y, z)
        
        # Zwracamy czysty słownik z wynikami
        return {
            "frame_number": frame_nb,
            "sonde_id": sonde_id,
            "timestamp": frame_time.strftime("%Y-%m-%d %H:%M:%S"),
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "alt": round(alt, 2)
        }
        
    except (struct.error, UnicodeDecodeError):
        # Jeśli ramka jest uszkodzona i nie da się jej sparsować, omijamy ją (zgodnie z założeniami z Twojego polecenia)
        return None
def descramble_frame(frame_bytes):

    descrambled = bytearray(len(frame_bytes))
    
    for i in range(len(frame_bytes)):
        descrambled[i] = frame_bytes[i] ^ XOR_MASK[i % len(XOR_MASK)]
        
    return descrambled
def extract_bits(wav_path, baud_rate=4800):

    print(f"[*] Wczytywanie pliku: {wav_path}")
    sample_rate, data = wavfile.read(wav_path)

    if len(data.shape) > 1:
        data = data[:, 0]
        
    samples_per_bit = sample_rate / baud_rate
    print(f"[*] Częstotliwość próbkowania: {sample_rate} Hz")
    print(f"[*] Próbki na bit: {samples_per_bit:.2f}")
    signs = np.sign(data)
    signs[signs == 0] = 1
    zero_crossings = np.where(np.diff(signs) != 0)[0]
    bits = []
    prev_idx = 0
    

    for idx in zero_crossings:
        n_samples = idx - prev_idx
        
  
        n_bits = int(round(n_samples / samples_per_bit))
        
        if n_bits > 0:
            #dodatnia połówka fali to bit 0, ujemna to bit 1
            current_sign = signs[prev_idx]
            bit_val = 0 if current_sign > 0 else 1
            bits.extend([bit_val] * n_bits)
        
        prev_idx = idx
        
    return np.array(bits, dtype=np.uint8)

SYNC_WORD_BITS = "0000100001101101010100111000100001000100011010010100100000011111"
FRAME_LEN_BYTES = 320
FRAME_LEN_BITS = FRAME_LEN_BYTES * 8

def bits_to_bytes(bit_array):
    bytes_list = bytearray()
    
    for i in range(0, len(bit_array), 8):
        chunk = bit_array[i:i+8]
        if len(chunk) < 8:
            break
            
        # Zgodnie z logiką z kodu C (funkcja bits2byte):
        # bit 0 ma wagę 1, bit 1 ma wagę 2, bit 2 ma wagę 4 itd.
        val = sum(bit_val << idx for idx, bit_val in enumerate(chunk))
        bytes_list.append(val)
        
    return bytes_list

def find_frames(bits):
    print("[*] Szukanie ramek (synchronizacja)...")
    bit_str = ''.join(bits.astype(str))
    
    frames = []
    idx = 0
    
    while True:
        idx = bit_str.find(SYNC_WORD_BITS, idx)
        if idx == -1:
            break

        if idx + FRAME_LEN_BITS > len(bits):
            break

        frame_bits = bits[idx : idx + FRAME_LEN_BITS]

        frame_bytes = bits_to_bytes(frame_bits)
        frames.append(frame_bytes)
        idx += FRAME_LEN_BITS
        
    print(f"[*] Znaleziono {len(frames)} pełnych ramek.")
    return frames

def main():
    parser = argparse.ArgumentParser(description="Dekoder telemetrii radiosondy Vaisala RS41-SGP")
    parser.add_argument("wav_file", help="Ścieżka do pliku audio WAV (np. rs41_audio.wav)")
    parser.add_argument("--csv", help="Zapisz zdekodowane dane do pliku CSV", metavar="PLIK.csv")
    parser.add_argument("--json", help="Zapisz zdekodowane dane do pliku JSON", metavar="PLIK.json")
    parser.add_argument("-v", "--verbose", action="store_true", help="Wyświetlaj zdekodowane ramki w terminalu")
    
    args = parser.parse_args()
    
    #demodulacja
    bits = extract_bits(args.wav_file)
    if len(bits) == 0:
        print("[-] Błąd: Nie znaleziono żadnych bitów w pliku audio.")
        return

    #ramki
    frames = find_frames(bits)
    if not frames:
        print("[-] Błąd: Nie znaleziono żadnych pełnych ramek RS41 w sygnale.")
        return

    parsed_data = []

    #dekodowanie
    for frame in frames:
        descrambled = descramble_frame(frame)
        data = parse_frame(descrambled)
        
        #odrzucenie błędnych
        if data is not None and data["lat"] != 0.0 and data["lon"] != 0.0:
            parsed_data.append(data)
            
            #jeśli -v
            if args.verbose:
                print(f"[{data['frame_number']:5d}] ({data['sonde_id']}) {data['timestamp']} "
                      f"lat: {data['lat']:.5f}  lon: {data['lon']:.5f}  alt: {data['alt']:.2f}m")

    print(f"[*] Pomyślnie zdekodowano {len(parsed_data)} poprawnych ramek.")

    if args.csv and parsed_data:
        with open(args.csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=parsed_data[0].keys())
            writer.writeheader()
            writer.writerows(parsed_data)
        print(f"[*] Zapisano dane do pliku CSV: {args.csv}")

    if args.json and parsed_data:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=4)
        print(f"[*] Zapisano dane do pliku JSON: {args.json}")

if __name__ == "__main__":
    main()