import datetime
plus_one_hour = datetime.datetime.strptime("21:00:00", "%H:%M:%S") + datetime.timedelta(hours=2)
print(plus_one_hour.strftime("%H:%M:%S"))