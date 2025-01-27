# QuizMeister!

QuizMeister ist eine responsive Web-App zum KI-basierten **Erstellen, Hosten und Spielen von Quizzes**, wie zum Beispiel Pub-Quizzes.

**Web-Link: https://quizmeister.eu.pythonanywhere.com/**

![Startseite](/docu/home.png)

## Ein Quiz erstellen

Ein Quiz kann entweder manuell erstellt werden, oder per Klick auf _Fragen generieren_ mittels Anbindung an Google Gemini per KI generiert werden. Die Fragen können in drei verschiedenen Schwierigkeitsgraden und passend zu 14 verschiedenen Kategorien generiert werden. Die generierten Fragen können im Nachhinein noch angepasst werden. So kann ein Quiz auch teilweise KI-generiert und teilweise manuell erstellt werden. Es ist außerdem möglich ein Bild zu einer Frage hochzuladen, um z.B. eine Frage zu diesem Bild zu stellen.

![Quiz erstellen](/docu/Quiz_erstellen.png)
![Fragen generieren](/docu/Fragen_generieren.png)

## Ein Quiz anzeigen

Die Quiz-Übersicht zeigt alle vom Nutzer erstellten Quiz an. Ein Quiz kann hier auch bearbeitet oder gehostet werden.

![Quiz anzeigen](/docu/Quiz_anzeigen.png)

## Ein Quiz hosten

Per Klick auf _Quiz hosten_ in der Quiz-Ansicht, kann dieses Quiz gestartet werden. Der Host sieht nun die Host-Ansicht des laufenden Quiz. Es wird automatisch ein Session-Code generiert, welcher den Teilnehmern mitgeteilt werden muss.

![Quiz hosten](/docu/Quiz_hosten.png)

## An einem Quiz teilnehmen

Jeder Teilnehmer kann über sein oder ihr eigenes Endgerät den oben stehenden Link aufrufen. Jeder eingeloggte Nutzer kann an einer aktiven Quiz-Session teilnehmen, sofern er oder sie über den Session-Code verfügt. Nach dem Klicken auf _An Quiz teilnehmen_ auf der Startseite, muss der Session-Code eingegeben werden. Der Nutzer landet so in der Teilnehmer-Ansicht des Quiz und wird dem Host in der Rangliste angezeigt.

![Spieleransicht](/docu/Quiz_spielen_Spieler.png)

## Ein Quiz spielen

Sobald alle Teilnehmer der Quiz-Session beigetreten sind, wählt der Host eine Frage aus und teilt diese per Klick auf _Diese Frage stellen_ mit den Spielern.

> Info: Wird eine Frage erneut gestellt, werden die bis dahin abgegebenen Antworten aus der Antwort-Übersicht gelöscht.

![Host-Ansicht](/docu/Quiz_spielen_Host.png)

Die Teilnehmer können nun eine **Antwort abgeben**.

![Antwort abgeben](/docu/Quiz_spielen_Spieler_2.png)

Der Host kann die abgegebenen Antworten einsehen und als **richtig oder falsch markieren** und ggf. die Punkte manuell anpassen.

![Antwort bewerten](/docu/Quiz_spielen_Host_2.png)

> **Wichtig**: Per Klick auf _Punktestand aktualisieren_ werden die vom Host vergebenen **Punkte gespeichert und das Leaderboard aktualisiert**. Nach jeder Fragerunde - sobald alle Punkte vergeben wurden - sollte der Host also auf diesen Button klicken.

Das Leaderboard kann per Klick auf _Punktestand teilen_ mit den Spielern geteilt werden.

Am Ende einer Quiz-Session kann der Host diese per Klick auf _Session beenden_ schließen.

**Viel Spaß beim Quiz erstellen und spielen mit QuizMeister!**
