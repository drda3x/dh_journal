# -*- coding:utf-8 -*-


WEEK = [u'Пн', u'Вт', u'Ср', u'Чт', u'Пт', u'Сб', u'Вс']


def get_count_of_weekdays_per_interval(wd, int_start, int_stop):

    d_delta = (int_stop - int_start).days
    first_day = int_start.weekday()
    weeks = int(round(d_delta / 7))

    calendar = (WEEK[first_day:] + WEEK * weeks)[:d_delta + 1]

    return len(
        filter(
            lambda d: d in wd,
            calendar
        )
    )


def get_week_offsets(week_days):
    days = week_days + [week_days[0]]

    def req(wd):

        if len(wd) < 2:
            return []

        offset = WEEK.index(wd[1]) - WEEK.index(wd[0])
        offset = (7 + offset) if offset < 0 else offset

        return [offset] + req(wd[1:])

    return req(days) if len(week_days) > 1 else [7]


def get_week_offsets_from_start_date(start_date, week_days):
    day = WEEK[start_date.weekday()]

    return get_week_offsets([day, week_days[0]])[:1] + get_week_offsets(week_days)