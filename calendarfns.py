from datetime import datetime, timezone, timedelta
from dateutil import tz
import dateutil.parser as p
import matplotlib.pyplot as plt
import calendar

def utc_to_eastern(utc_dt):
    """Converts a UTC datetime object to Eastern Time."""
    x = tz.gettz('US/EASTERN').utcoffset(utc_dt)
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(timezone(x))

# Function to parse events from an ICS file
# (Without using the icalendar package)
def parse_ics(file_path):
    events = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    event = {}
    for line in lines:
        line = line.strip()
        if line.startswith("BEGIN:VEVENT"):
            event = {}
        elif line.startswith("SUMMARY:"):
            event["summary"] = line[len("SUMMARY:"):].strip()
        elif line.startswith("DTSTART:"):
            dtstart = line[len("DTSTART:"):].strip()
            event["start"] = utc_to_eastern(p.parse(dtstart))
        elif line.startswith("DTEND:"):
            dtend = line[len("DTEND:"):].strip()
            event["end"] = utc_to_eastern(p.parse(dtend))
            event["times"] = event["start"].strftime("%H:%M") + '-' + event["end"].strftime("%H:%M")
        elif line.startswith("DTSTART;VALUE=DATE:"):
            dtstart = line[len("DTSTART;VALUE=DATE:"):].strip()
            event["start"] = p.parse(dtstart)
        elif line.startswith("DTEND;VALUE=DATE:"):
            dtend = line[len("DTEND;VALUE=DATE:"):].strip()
            event["end"] = p.parse(dtend)
            event["times"] = 'ALL DAY'
        elif line.startswith("END:VEVENT"):
            events.append(event)
    return events

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
                day_events = []
                for k in events_df:
                    if (k["start"].day == day and k["start"].month == month and k["start"].year == year): 
                        day_events.append(k)
                y_offset = 0.7
                for event in day_events:
                    ax[i + 1, j].text(0.5, y_offset, f"{event['summary']} \n {event['times']}", fontsize=7, ha='center', va='top', color='blue', wrap=True)
                    y_offset -= 0.2

    # Adjust layout
    fig.set_figheight(8.5)
    fig.set_figwidth(11)
    plt.subplots_adjust(hspace=0, wspace=0, left=0.02, right=0.98, top=0.94, bottom = 0.02)

    #plt.tight_layout(rect=[0.03, 0.03, 0.97, 0.97])
    plt.savefig(output_file, format='pdf')
    plt.close()
