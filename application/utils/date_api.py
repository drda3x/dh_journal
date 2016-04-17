# -*- coding:utf-8 -*-

import datetime

WEEK = (
    (0, u'Пн'),
    (1, u'Вт'),
    (2, u'Ср'),
    (3, u'Чт'),
    (4, u'Пт'),
    (5, u'Сб'),
    (6, u'Вс')
)

MONTH_RUS = [
    '',
    u'Январь',
    u'Февраль',
    u'Март',
    u'Апрель',
    u'Май',
    u'Июнь',
    u'Июль',
    u'Август',
    u'Сентябрь',
    u'Октябрь',
    u'Ноябрь',
    u'Декабрь'
]

MONTH_PARENT_FORM = [
    '',
    u'Января',
    u'Февраля',
    u'Марта',
    u'Апреля',
    u'Мая',
    u'Июня',
    u'Июля',
    u'Августа',
    u'Сентября',
    u'Октября',
    u'Ноября',
    u'Декабря'
]

def get_week_days_names(nums):
    return [
        WEEK[int(i)][1] for i in nums
    ]


def get_count_of_weekdays_per_interval(wd, int_start, int_stop):

    def _gen(cnt, st_index):
        index = st_index

        for i in xrange(cnt):
            yield WEEK[index]
            index = index + 1 if index < 6 else 0

    d_delta = (int_stop - int_start).days + 1
    first_day = int_start.weekday()

    return len(
        filter(
            lambda d: d in wd,
            [day[1] for day in _gen(d_delta, first_day)]
        )
    )


def get_week_offsets(week_days):
    days = week_days + [week_days[0]]
    week = get_week_days_names(range(7))

    def req(wd):

        if len(wd) < 2:
            return []

        offset = week.index(wd[1]) - week.index(wd[0])
        offset = (7 + offset) if offset < 0 else offset

        return [offset] + req(wd[1:])

    return req(days) if len(week_days) > 1 else [7]


def get_week_offsets_from_start_date(start_date, week_days):
    day = WEEK[start_date.weekday()][1]

    return get_week_offsets([day, week_days[0]])[:1] + get_week_offsets(week_days)


def get_last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


def get_month_offset(date, offset):
    month = date.month
    year = date.year

    if month > offset:
        return datetime.datetime(year, month-offset, 1)
    else:
        return datetime.datetime(year-1, 12+(month-offset), 1)
