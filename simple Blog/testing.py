from datetime import date


def getdate():
    months = ["January", "February", "March", "April", "May", "June", "Juli", "August", "September", "October", "November", "December"]
    month =  months[date.today().month]
    dateString = f"{month} {date.today().day}, {date.today().year} "
    return dateString

print(getdate())