# Funkcjonalności projektu

<img src="logo.png" width=256 height=256>

Model komunikacji 2 ↔ 1
- Protokół wartstwy transportowej: UDP.
- Pola nagłówka protokołu tekstowego zadefiniowane jako klucz>wartość< (przykład: Operacja>podaj_liczbe<).
- Podstawowe pola nagłówka oraz odpowiadające im klucze: pole operacji – „Operacja”, pole odpowiedzi – „Odpowiedz”, pole identyfikatora sesji – „Identyfikator”, dodatkowe pola zdefiniowane przez programistę – zgodnie z wymaganiami.


- Funkcje oprogramowania:
    * klienta:
	* uzyskanie identyfikatora sesji,
	* przesłanie pojedynczej, parzystej liczby naturalnej L,
	* przesłanie wartości liczbowych, będących „odpowiedziami”:
	    * klient ma odgadnąć liczbę wylosowaną przez serwer;
    * serwera:
	* wygenerowanie identyfikatora sesji,
	* wyznaczenie liczby prób od podjęcia (liczba prób = (L1 + L2) / 2),
	* wylosowanie liczby tajnej,
	* przesłanie maksymalnej liczby prób odgadnięcia wartości tajnej,
	* informowanie klientów, czy wartość została odgadnięta.
	
- Wymagania dodatkowe:
    * identyfikator sesji oraz znacznik czasu powinny być przesyłane w każdym komunikacie,
    * każdy wysłany komunikat powinien zostać potwierdzony przez drugą stronę.
