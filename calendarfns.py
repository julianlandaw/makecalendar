from datetime import datetime, timezone, timedelta
from icalendar import Calendar
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import pytz

# Function to read Google Calendar .ics file and parse events
def parse_calendar(file_path):
    import pytz
    file_path = 'gcalendar.ics'
    with open(file_path, 'r') as f:
        cal = Calendar.from_ical(f.read())

    events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            if ((component.get("summary") is not None) and (component.get("dtstart") is not None) and (component.get("dtend") is not None)):
                if (type(component.get("dtstart").dt) is datetime):
                    tstart = component.get("dtstart").dt.astimezone(pytz.timezone('US/Eastern'))
                    tend = component.get("dtend").dt.astimezone(pytz.timezone('US/Eastern'))
                    event = {
                        "summary": component.get("summary"),
                        "start": tstart,
                        "end": tend,
                        "times": tstart.strftime("%H:%M") + '-' + tend.strftime("%H:%M")
                    }
                else:
                    event = {
                        "summary": component.get("summary"),
                        "start": component.get("dtstart").dt,
                        "end": component.get("dtend").dt,
                        "times": "All Day"
                    }
                events.append(event)

    return pd.DataFrame(events)

# Function to generate a printable calendar layout
def generate_printable_calendar(events_df, month, year, output_file):
    cal = calendar.Calendar()
    days_in_month = [day for day in cal.itermonthdays(year, month) if day != 0]
    num_weeks = len(list(cal.monthdayscalendar(year, month)))

    fig, ax = plt.subplots(num_weeks + 1, 7, dpi=100)
    fig.suptitle(f"{calendar.month_name[month]} {year}", fontsize=20)

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for j, day_name in enumerate(days_of_week):
        ax[0, j].set_facecolor("lightgray")
        ax[0, j].text(0.5, 0.5, day_name, fontsize=12, ha='center', va='center', color='black')
        ax[0, j].set_xlim(0, 1)
        ax[0, j].set_ylim(0, 1)
        ax[0, j].spines['top'].set_visible(False)
        ax[0, j].spines['bottom'].set_visible(False)
        if (day_name == "Saturday"):
            ax[0, j].spines['left'].set_visible(True)
        else:
            ax[0, j].spines['left'].set_visible(False)
        if (day_name == "Friday"):
            ax[0, j].spines['right'].set_visible(True)
        else:
            ax[0, j].spines['right'].set_visible(False)
        ax[0, j].spines['top'].set_color('black')
        ax[0, j].spines['bottom'].set_color('black')
        ax[0, j].spines['left'].set_color('black')
        ax[0, j].spines['right'].set_color('black')
        ax[0, j].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    for i, week in enumerate(cal.monthdayscalendar(year, month)):
        for j, day in enumerate(week):
            ax[i + 1, j].set_facecolor("white")
            ax[i + 1, j].set_xlim(0, 1)
            ax[i + 1, j].set_ylim(0, 1)
            ax[i + 1, j].spines['top'].set_visible(True)
            ax[i + 1, j].spines['bottom'].set_visible(True)
            ax[i + 1, j].spines['left'].set_visible(True)
            ax[i + 1, j].spines['right'].set_visible(True)
            ax[i + 1, j].spines['top'].set_color('black')
            ax[i + 1, j].spines['bottom'].set_color('black')
            ax[i + 1, j].spines['left'].set_color('black')
            ax[i + 1, j].spines['right'].set_color('black')
            ax[i + 1, j].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

            if day != 0:  # Non-zero days are part of the current month
                ax[i + 1, j].text(0.5, 0.9, str(day), fontsize=12, ha='center', va='top', color='black', wrap=True)

                # Add events to the corresponding day
                day_events = events_df[events_df['start'].dt.day == day]
                y_offset = 0.7
                for _, event in day_events.iterrows():
                    if (event['start'].month == month and event['start'].year == year):
                        ax[i + 1, j].text(
                            0.5, y_offset, f"{event['summary']} \n {event['times']}", fontsize=7, ha='center', va='top', color='blue', wrap=True)
                        y_offset -= 0.2

    # Adjust layout
    fig.set_figheight(8.5)
    fig.set_figwidth(11)
    plt.subplots_adjust(hspace=0, wspace=0, left=0.02, right=0.98, top=0.94, bottom = 0.02)

    #plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.97])
    plt.savefig(output_file, format='pdf')
    plt.close()