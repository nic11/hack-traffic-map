import pandas as pd
from scipy.stats import binom


def parsing():
    fin_csv = open("table_matches.csv", 'r')
    fin_csv.readline()
    for i in range(48):
        x = fin_csv.readline().split(',')
        city = x[1]
        capacity = x[3]
        first = x[4]
        second = x[5]
        date = x[6][5:10]
        countries.add(first)
        countries.add(second)
        cities_list.add(city)
        if cities.get(city) != None:
            cities[city].append([first, second, date, capacity])
        else:
            cities[city] = [[first, second, date, capacity]]

    for i in range(6):
        x = fin_csv.readline().split(',')
        city = x[1]
        capacity = x[3]
        first = x[4]
        second = x[5]
        date = x[6][:10]
        if first in countries and second in countries:
            if cities.get(city) != None:
                cities[city].append([first, second, date, capacity])
            else:
                cities[city] = [[first, second, date, capacity]]


def parse_date(date):
    month = int(date[:2])
    day = int(date[3:])
    return month, day


def diff_dates(first, second):
    month_1, day_1 = parse_date(first)
    month_2, day_2 = parse_date(second)
    if month_1 == month_2:
        return day_2 - day_1
    else:
        return day_2 + (30 - day_1)


def distribution(people, number):
    rv = binom(number - 1, 0.5)
    return [int(people * rv.pmf(x)) for x in range(number)]


def predict_traffic(first, second, date):
    first_match = cities[first]
    second_match = cities[second]
    answer = []

    for match in first_match:
        first_team, second_team, match_date, capacity = match
        capacity = int(capacity) / 2
        for other in second_match:
            if (((first_team in other[:2]) or (second_team in other[:2]))
                    and match_date <= other[2] and match_date <= date < other[2]):
                diff = diff_dates(match_date, other[2])
                dist = distribution(capacity, diff)
                index = diff_dates(match_date, date)
                answer.append([match, other, dist[index]])

    #print(answer)
    answer = clear_2(answer)
    return answer


def get_team_edges():
    team_edges = {}
    for events1 in cities.values():
        for events2 in cities.values():
            for event1 in events1:
                for event2 in events2:
                    event1 = tuple(event1)
                    common_team = get_common_team(event1, event2)
                    if common_team and event1[2] < event2[2] and ((event1, common_team) not in team_edges or event2[2]\
                            < team_edges[event1, common_team][2]):
                        team_edges[event1, common_team] = event2
    return [[list(x[0][0]), x[1]] for x in team_edges.items()]


def clear_2(trans_events):
    team_edges = get_team_edges()
    return [x for x in trans_events if x[:2] in team_edges]


def get_common_team(match, other):
    if match[0] in other[:2]:
        return match[0]
    elif match[1] in other[:2]:
        return match[1]
    else:
        return None


def clear_1(trans_events):
    for event in trans_events:
        pass


def all_date():

    def for_all(date):
        for curr in list(cities_list):
            for other in list(cities_list):
                if curr != other:
                    prediction = predict_traffic(curr, other, date)
                    # print(curr, other, prediction)
                    answer = 0
                    for i in prediction:
                        answer += i[2]
                    if answer:
                        print(curr, other, date, answer)
                    big_data.append([curr, other, "2018-" + date,  answer])
    fin_input_date = open("date.txt", 'r')
    big_data = []
    for i in fin_input_date.readlines():
        for_all(i.strip())
    frame = pd.DataFrame(big_data, columns=["from", "to", "date", "traffic"])
    open("predictions_json", 'w').write(frame.to_json(orient="records"))
    open("predictions_csv", 'w').write(frame.to_csv())


def for_one():
    fin_input_one = open("input.txt", 'r')
    first, second, date = fin_input_one.readline().split()
    print(predict_traffic(first, second, date))


cities = dict()
dates = dict()
countries = set()
cities_list = set()
parsing()
print(countries)
all_date()