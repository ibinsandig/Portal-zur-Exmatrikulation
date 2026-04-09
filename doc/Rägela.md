# Regler auslegung zum Ansteuern der Motoren des Portalroboters

## Planung und erste gedankengänge

**PDF-Regler**

Der PDF (Pseudo-Derivative-Feedback) Regler eignet sich gut für beschleunigungsbasierte Ansteuerung. 
Er verlagert die Differenzelemnt (D-Anteil) in die Rückführung und reagiert so extrem stabil auf abrupte Beschleunigungsänderungen, ohne das das System stark zum Schwingen gebracht wird. 

Es handelt sich um ein PT2-Strecvkenmodell (weil wir zweimal integrieren: Beschleunigung -> Geschwindigkeit -> Position)

> s² + 2·D·ω₀·s + ω₀² = 0

Zusammenfassung:


Größe  | Bedeutung    |               Wirkung

Fehler | Sollposition − Istposition | Eingang für P

Kp    |  Verstärkung P-Anteil    |    Größer → schneller, aber mehr Überschwingen

Kd    |  Verstärkung D-Anteil   |     Größer → mehr Dämpfung, weniger Überschwingen

ω₀    |  Wunschgeschwindigkeit   |    Bestimmt beide K-Werte  

D    |   Wunschdämpfung      |        D=1 → kein Überschwingen

*Warum PDF statt PID bei Beschleunigungsvorgaben?*

Sanfteres Anlaufen: Da der P-Anteil nicht direkt auf den Sollwertsprung wirkt (kein "Proportional Kick"), folgt der Motor der Beschleunigungsrampe wesentlich sauberer.
Störunterdrückung: Er verhält sich extrem robust gegenüber Lastwechseln, was bei Robotern (z. B. wechselnder Untergrund oder Gewicht) entscheidend ist.

> Integrator: $I_{sum} = I_{sum} + (v_{soll} - v_{ist})$

> Stellgröße: $u = (K_i \cdot I_{sum}) - (K_p \cdot v_{ist})$

## Zweite Version (auch Programmtechnisch umgesetzt)

