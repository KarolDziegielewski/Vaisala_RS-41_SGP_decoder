# Vaisala_RS-41_SGP_decoder

Projekt rekrutacyjny SKA polegał na stworzeniu programu do zdekodowania sygnału z sondy RS41-SGP. 

Na podstawie przykładowego pliku "/rs41.wav", dostępnych źródeł różnego rodzaju (w tym załączone w treści zadania repozytoria) powstał program, który z pliku WAV robi gotowe, zdekodowane dane, które przedstawiają podstawowe dane przekazywane przez te sondę takie jak numer ramki, ID sondy, czas, oraz współrzędne geograficzne (szerokość, długość i wysokość). 

Program został napisany w Pythonie.

Parametry sygnału i sygnał z pliku WAV został "wyciągnięty" przy pomocy funkcji z biblioteki scipy.io.wavfile. Częstotliwość próbkowania w przykładowym pliku to 4800 Hz. 
Baud rate tej sondy to również 4800Hz (https://github.com/rs1729/RS/blob/master/rs41/rs41sg.c - logika tego kodu była częstą inspiracją w wielu częsciach kodu).

Zatem każda próbka dźwięku to jeden bit, co znacznie ułatwia analizę.

Na początku próbki są poddawne operacji SIGN (ale dla x = 0 wartość to 1):

$$
\text{sgn}(x) = 
\begin{cases} 
1 & \text{dla } x >= 0 \\ 
-1 & \text{dla } x < 0 
\end{cases}
$$

Na podstawie przejść przez zero odnajdywana jest wartość binarna danego bitu. 

Teraz gdy mamy gotowe wartości bitów przechodzimy do etapu dekodowania. 

Na podstawie słowa sunchronizującego "0000100001101101010100111000100001000100011010010100100000011111" odnajdywane są ramki, a następnie z ramek wyciągane są dane zgodnie ze speyfikacją z tego repozytorium: https://github.com/bazjo/RS41_Decoding/tree/master/RS41-SGP

Ostatni etap to zapisanie danych do plików CSV/JSON lub wypisanie na konsolę.​

# Wyniki działania programu na plik przykładowy:
```

    =======================================
       DEKODER SYGNAŁU Z SONDY RS$!-SGP
    ============================'==========
         Karol Dzięgielewski SP5XKD
    =======================================

    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼███████┼┼┼┼████████┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼██┼┼█┼┼██┼┼██████████┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼█┼┼█████┼██┼┼█┼┼███┼█┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼█┼████┼┼██████┼█████┼█┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼██┼┼██████████████┼█┼█┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼███┼██████████████████┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼█┼██┼██┼┼┼██████┼┼██┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼██┼┼█████████┼█┼██┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼███┼┼███┼┼┼█████┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼█████████┼██┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼██┼┼┼██┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼██┼██┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼█┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼
    ┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼

[*] Wczytywanie pliku: rs41.wav
[*] Częstotliwość próbkowania: 4800 Hz
[*] Próbki na bit: 1.00
[*] Szukanie ramek (synchronizacja)...
[*] Znaleziono 26 pełnych ramek.
[  196] (S1640290) 2025-06-08 19:24:24 lat: 80.95621  lon: 4.27600  alt: -1269864.44m
[  197] (S1640290) 2025-06-09 04:41:29 lat: 52.21888  lon: 20.98380  alt: 143.75m
[  199] (S1640290) 2025-06-09 04:41:31 lat: 52.21888  lon: 20.98380  alt: 144.19m
[  200] (S1640290) 2025-06-09 04:41:32 lat: 52.21888  lon: 20.98381  alt: 144.62m
[  201] (S1640290) 2025-06-09 04:41:33 lat: 52.21889  lon: 20.98381  alt: 144.81m
[  204] (S1640290) 2025-06-09 04:41:36 lat: 52.21890  lon: 20.98381  alt: 147.09m
[  205] (S1640290) 2025-06-09 04:41:37 lat: 52.21890  lon: 20.98382  alt: 147.40m
[  206] (S1640290) 2025-06-09 04:41:38 lat: 53.34476  lon: 21.89945  alt: -94315.16m
[  207] (S1640290) 2025-06-09 04:41:39 lat: 52.21890  lon: 20.98382  alt: 146.90m
[  212] (S1640290) 2025-06-09 04:41:44 lat: 52.21890  lon: 20.98386  alt: 149.99m
[  213] (S1640290) 2025-06-09 04:41:45 lat: 52.21889  lon: 20.98386  alt: 150.22m
[  214] (S1640290) 2025-06-09 04:41:46 lat: 80.65156  lon: 4.28663  alt: -1435481.65m
[  216] (S1640290) 2025-06-09 04:41:48 lat: 52.21888  lon: 20.98386  alt: 149.99m
[  220] (S1640290) 2025-06-09 04:41:52 lat: 52.21887  lon: 20.98385  alt: 149.84m
[  222] (S1640290) 2025-06-09 04:41:54 lat: 52.21887  lon: 20.98385  alt: 150.05m
[  224] (S1640290) 2025-06-09 04:41:56 lat: 52.21888  lon: 20.98385  alt: 150.62m
[  225] (S1640290) 2025-06-09 04:41:57 lat: 52.21888  lon: 20.98386  alt: 151.02m
[  227] (S1640290) 2025-06-09 04:41:59 lat: 52.21888  lon: 20.98386  alt: 151.54m
[  228] (S1640290) 2025-06-09 04:42:00 lat: 52.21888  lon: 20.98387  alt: 151.80m
[  229] (S1640290) 2025-06-09 04:42:01 lat: 55.40487  lon: 0.98978  alt: -247796.43m
[  230] (S1640290) 2025-06-09 04:42:02 lat: 52.21889  lon: 20.98387  alt: 152.35m
[  233] (S1640290) 2025-06-09 04:42:05 lat: 53.40176  lon: 21.89951  alt: -85893.80m
[  236] (S1640290) 2025-06-09 04:42:08 lat: 52.21889  lon: 20.98387  alt: 152.09m
[  237] (S1640290) 2025-06-09 04:42:09 lat: 52.21889  lon: 20.98387  alt: 151.69m
[  240] (S1640290) 2025-06-09 04:42:12 lat: 52.21889  lon: 20.98386  alt: 150.47m
[  241] (S1640290) 2025-06-09 04:42:13 lat: 52.21889  lon: 20.98385  alt: 149.82m
[*] Pomyślnie zdekodowano 26 poprawnych ramek.
```
Pomijając kilka wyników znacząco odbiegających od reszty (tzw. błąd gruby) łatwo zauważyć, że sonda znajduje się na współrzędnych w pobliżu 52.2189 20.98386 (w pobliżu placu Narutowicza - Warszawa). A czas wysłania pakietu to 9 czerwca 2025 r. między 4:41:29 a 4:42:13. ID sondy wszędzie jest identyczne więc z dużym prawdopodieństwem jest to sonda S1640290.
