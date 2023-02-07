import pandas as pandas

# Erster Algorithmus, der die Aufträge in der korrekten Reihenfolge abgeht
def firstalg(df):

    # Wiederholende Schleife für alle Aufträge, in der das Ergebnis ausgerechnet wird und der Beginn des Neuen Auftrags
    # auf das Ende des letzten gesetzt wird, falls dieser länger gedauert hat als die Ankunft des neuen Auftrags
    for i in range(len(df)):

        df.loc[i, 'begin'] = actual_beginning(df.loc[i, 'begin'])
        df.loc[i, 'finished'] = completion_time(df.loc[i, 'begin'], df.loc[i, 'duration'])

        if (i+1 < len(df)) and (df['finished'][i] > df['recieved'][i+1]): df['begin'][i+1] =df['finished'][i]

    df['delay'] = df['finished'] - df['recieved']
    aftermath(df)

# Zweiter Algorithmus, der die Aufträge nach ihrer erwarteten Dauer abgeht
def secondalg(df):

    # Wiederholende Schleife für Anzahl der Aufträge wie bei firstalg()
    # Eingegrenzter Bereich bestimmt alle Aufträge, die zu der Zeit der Fertigstellung bereits eingetroffen sind und
    # sortiert sie nach 'duration', damit der kürzeste Auftrag als nächstes bearbeitet wird.
    for i in range(len(df)):

        counter =1

        df.loc[i, 'begin'] = actual_beginning(df.loc[i, 'begin'])
        df.loc[i, 'finished'] = completion_time(df.loc[i, 'begin'], df.loc[i, 'duration'])

        # -----------------------------------------------------------------------------
        while i+counter < len(df) and (df['finished'][i] > df['recieved'][i+counter]):
            df['begin'][i+counter] =df['finished'][i]
            counter +=1

        df[i+1: i+counter] =df[i+1: i+counter].sort_values(by='duration')
        # -----------------------------------------------------------------------------

    df['delay'] =df['finished'] - df['recieved']

    aftermath(df)


# Dritter Algorithmus, eigene Idee:
# Das Programm weist jedem Auftrag eine Priorität zu, die davon abhängt, wie lange der Autraggeber schon warten,
# und wie lange der Auftrag dauert.
def thirdalg(df):
    df['priority'] = 0

    for i in range(len(df)):

        counter =1

        df.loc[i, 'begin'] = actual_beginning(df.loc[i, 'begin'])
        df.loc[i, 'finished'] = completion_time(df.loc[i, 'begin'], df.loc[i, 'duration'])

        while(i+counter < len(df) and (df['finished'][i] > df['recieved'][i+counter])):
            df.loc[i+counter, 'begin'] =df.loc[i, 'finished']
            df.loc[i+counter, 'priority'] =getprio(df.loc[i+counter, 'begin'], df.loc[i+counter, 'recieved'], df.loc[i+counter, 'duration'])
            counter +=1

        df[i+1: i + counter] =df[i+1: i + counter].sort_values(by='priority', ascending=False)

    df['delay'] =df['finished'] - df['recieved']

    aftermath(df)

def getprio(begin, recieved, duration):
    return (begin-recieved)/duration
# Ausgabe der minimalen, durchschnittlichen & maximalen Wartezeit der Aufträge, indem zuerst die Zeilen mit der
# kürzesten/ höchsten 'duration' bestimmt werden und dann nur 'duration' ausgegeben wird.
# .mean() ist Teil der Library und berechnet den Durchschnitt aller Werte in einer Spalte
def aftermath(df):
    minrow =df['delay'].eq(df['delay'].min())
    maxrow =df['delay'].eq(df['delay'].max())
    print('_____________________________________________________')
    print('Order with minimum waiting time + time waited:', str(df['delay'][minrow]), end='\n')
    print('Average time waited:', str(round(df.loc[:, 'delay'].mean(), 4)), end='\n') # Datentyp: float
    print('Order with maximum waiting time + time waited:', str(df['delay'][maxrow]))
    print('_____________________________________________________')
    print(df.to_string())

# Öffnungszeit des nächsten Morgen seit Zeitbeginn berechnen
def get_opening_time_nextday(t): return (((t // 1440) + 1) * 1440) + 540 # Datentyp: float64

# Schließungszeit dieses Abends seit Zeitbeginn berechnen
def get_closing_time_day(t): return ((t // 1440) * 1440) + 1020 # Datentyp: float64

# Den Zeitpunkt herausfinden, an dem tatsächlich mit dem Auftrag begonnen wird,
# indem verschiedene Möglichkeiten zur Abschlusszeit des letzten Auftrags abgegangen werden
def actual_beginning(t):
    daytime =t%1440
    if daytime < 540: return t + 540 - daytime # Datentyp: int
    elif daytime > 1020: return get_opening_time_nextday(t) # Datentyp: int
    else: return t # Datentyp: int

# Berechnet die Dauer, die ein Projekt braucht um abgeschlossen zu werden rekursiv
# Dafür wird die Funktion für jeden Tag, den das Projekt braucht einmal wiederholt,
# bis die übrige Zeit an einem Tag abgearbeitet werden kann.
def completion_time(beginning, remaining):
    current_progress = beginning + remaining
    if not current_progress > get_closing_time_day(beginning):
        return current_progress # Datentyp: int
    else:
        time_left = remaining - (get_closing_time_day(beginning) - beginning)
        beginning = get_opening_time_nextday(beginning)
        return completion_time(beginning, time_left)


def main():
    # Erstellen der Tabelle mit den Aufträgen, indem zuerst die Csv Datei ausgelesen wird, deren Werten die Namen
    # 'recieved' und 'duration' zugeteilt werden, und weitere essenzielle Spalten hinzugefügt werden
    df = pandas.read_csv('fahrradwerkstatt5.txt', header=None, sep=' ')
    df.columns = ["recieved", "duration"]
    df['begin'] = df['recieved']
    df['finished'], df['delay'] = 0, 0

    firstalg(df)
    secondalg(df)
    thirdalg(df)

if __name__ == "__main__":
    main()
