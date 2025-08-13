from flask import Flask, render_template
import sqlite3
import enum
import datetime
import calendar


class ProjectCode(enum.IntEnum):
    NetsimulyzerApp = 1
    NetsimulyzerModule = 2


app = Flask(__name__)


def connect_db() -> sqlite3.Connection:
    connection = sqlite3.connect("file:data/clone-stats.sqlite?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


@app.route('/')
def index():
    d = datetime.date.today()
    end_of_fy = datetime.date(year=d.year, month=10, day=1)

    if d > end_of_fy:
        target = end_of_fy
    else:
        target = datetime.date(year=d.year - 1, month=10, day=1)

    conn = connect_db()
    c = conn.cursor()
    c.execute("""
              select project_id,
                     sum(clone_count)        as total_clones,
                     sum(unique_clone_count) as total_unique_clones
              from clones
              where clone_day > ?
              group by project_id;
              """, (target,))
    clones = c.fetchall()

    c.execute("""
              select sum(clone_count)                       as 'clone_count',
                     sum(unique_clone_count)                as 'unique_clone_count',
                     strftime('%m-%Y', clone_day)           as 'month_year',
                     cast(strftime('%m', clone_day) as int) as 'month',
                     strftime('%Y', clone_day)              as 'year'
              from clones
              group by strftime('%m-%Y', clone_day)
              order by clone_day;
              """)
    clones_by_month = c.fetchall()

    c.execute("""
              select project_id,
                     sum(view_count)        as total_views,
                     sum(unique_view_count) as total_unique_views
              from views
              where view_day > ?
              group by project_id;
              """, (target,))

    views = c.fetchall()

    c.execute("""
              select sum(view_count)                       as 'view_count',
                     sum(unique_view_count)                as 'unique_view_count',
                     strftime('%m-%Y', view_day)           as 'month_year',
                     cast(strftime('%m', view_day) as int) as 'month',
                     strftime('%Y', view_day)              as 'year'
              from views
              group by strftime('%m-%Y', view_day)
              order by view_day;
              """)
    views_by_month = c.fetchall()

    total_clones = {
        'clones': 0,
        'unique_clones': 0,
    }

    for r in clones:
        total_clones['clones'] += r['total_clones']
        total_clones['unique_clones'] += r['total_unique_clones']

    total_views = {
        'views': 0,
        'unique_views': 0,
    }

    for v in views:
        total_views['views'] += v['total_views']
        total_views['unique_views'] += v['total_unique_views']

    c.close()
    conn.close()
    return render_template("index.html",
                           clones=clones,
                           views=views,
                           projectCode=ProjectCode,
                           target_date=target,
                           total_clones=total_clones,
                           clones_by_month=clones_by_month,
                           total_views=total_views,
                           views_by_month=views_by_month,
                           month_names=calendar.month_name
                           )


if __name__ == '__main__':
    app.run()
