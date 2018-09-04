from datetime import datetime, timedelta, date
from vSQL.vattr import *
import pymysql
import json

from pymysql import OperationalError

with open(__file__[:-8] + '/db.json', 'r', encoding='utf-8') as f:
    json_dict = json.loads(f.read())

CREATE = "CREATE TABLE IF NOT EXISTS {} ({})"
INSERT = "INSERT INTO {}({}) VALUES ({})"
UPDATE = "UPDATE {} SET {} WHERE {} = {}"
DELETE = "DELETE FROM {} {}"
SELECT = "SELECT * FROM {} {}"
COUNT = "SELECT COUNT(*) FROM {} {}"
SELECTANDCOUNT = "SELECT SQL_CALC_FOUND_ROWS  * FROM {} {}"
DROP = "DROP TABLE IF EXISTS {}"
SHOWTABLE = "SHOW TABLES LIKE '{}'"
SHOWDATA = "SHOW DATABASES LIKE '{}'"

HOUR_DIFF = "HOUR(timediff(now(), {})) AS {}"
MINUTE_DIFF = "MINUTE(timediff(now(), {})) AS {}"
SECOND_DIFF = "SECOND(timediff(now(), {})) AS {}"
DAY_DIFF = "DAY(timediff(now(), {})) AS {}"

HOST = json_dict['HOST']
USER = json_dict['USER']
PWD = json_dict['PWD']
DB = json_dict['DB']


def create_all_table():
    for table in Module.get_tables():
        rows = ''
        role = ''
        if not isexists(table['table']):
            for k, v in table['rows'].items():
                if v.__class__.__name__ == 'column':
                    rows = '{} {} {}, '.format(rows + k, v.type, v.col)
                if v.__class__.__name__ == 'foreign':
                    role = '{} {}, '.format(role, v.col)
            if role:
                rows = rows + role
            sql = CREATE.format(table['table'], rows[:-2])
            execute(sql)


def isexists(table):
    sql = SHOWTABLE.format(table)
    result = execute_get_one(sql)
    return result


def drop(mod):
    table = mod.table()
    sql = DROP.format(table)
    execute(sql)


def cover(attr, s):
    if isinstance(attr, str) or isinstance(attr, datetime) or isinstance(attr, date):
        return s.format(attr)
    else:
        return str(attr)


def create(mod):
    table = mod.get_sql()['table']
    rows = ''
    for k, v in mod.get_sql()['rows'].items():
        rows = rows + k + ' ' + v + ', '
    sql = CREATE.format(table, rows[:-2])
    execute(sql)


def insert(mod):
    table = mod.table()
    keys = ''
    values = ''
    for k, v in mod.get_attr().items():
        if v is not None:
            keys = keys + k + ', '
            values = values + cover(v, "'{}'") + ', '
    sql = INSERT.format(table, keys[:-2], values[:-2])
    print(sql)
    execute(sql)


def update(mod):
    table = mod.table()
    rows = ''
    num = 0
    for k, v in mod.get_attr().items():
        if k == mod.primary and v is not None:
            num = v
        elif v is not None:
            rows = rows + k + '=' + cover(v, "'{}'") + ', '
    sql = UPDATE.format(table, rows[:-2], mod.primary, num)
    print(sql)
    execute(sql)


def delete(mod):
    table = mod.table()
    rule = 'WHERE '
    rule = rule + mod.like
    if isinstance(mod.period, Period):
        rule = rule + mod.period.get_sql() + ' and '

    for k, v in mod.get_attr().items():
        if v is not None:
            rule = rule + k + ' = ' + cover(v, "'{}'") + ' and '
    rule = rule + '1=1 '
    sql = DELETE.format(table, rule)
    execute(sql)


def select(mod, oder='', asc=True, count=False, limit=0, one=False):
    table = mod.table()
    rule = 'WHERE '
    if mod.period:
        rule = rule + mod.period.get_sql()
    rule = rule + mod.no
    rule = rule + mod.like
    rule = rule + mod.distinct
    for k, v in mod.get_attr().items():
        if v is not None and not isinstance(v, (column, foreign)):
            rule = rule + k + ' = ' + cover(v, "'{}'") + ' and '

    rule = rule + '1=1 '
    if oder:
        rule = rule + ' ORDER BY ' + oder
        if asc:
            rule = rule + ' ASC '
        else:
            rule = rule + ' DESC '
    if limit:
        limit = 'LIMIT {}'.format(limit)
    if mod.pagination:
        limit = mod.pagination.get_limit()
        limit = 'LIMIT {}, {}'.format(limit[0], limit[1])
    if limit:
        rule = rule + limit

    if count:
        sql = COUNT.format(table, rule)
    elif mod.pagination:
        sql = SELECTANDCOUNT.format(table, rule)
    else:
        sql = SELECT.format(table, rule)
    if count:
        return execute_get_one(sql)
    elif one:
        return execute_get_item(sql, mod)
    else:
        return execute_get(sql, mod.__class__, pagination=mod.pagination)


def execute(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except TypeError:
        print('ERROR: Type Error unable to connect')
        db.rollback()
    except OperationalError:
        print('ERROR: Operational Error unable to connect')
        db.rollback()
    finally:
        db.close()


def execute_get(sql, clazz, pagination=None):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        items = []
        for rows in results:
            mod = clazz()
            mod.set_attr(list(rows))
            items.append(mod)
        if pagination:
            cursor.execute('SELECT FOUND_ROWS()')
            count = cursor.fetchall()[0][0]
            pagination.item_count = count
            pagination.items = items
            pagination.set_default()
            return pagination
        else:
            return items
    except IndexError:
        print("Error: unable to fetch data")
        db.rollback()
    finally:
        db.close()


def execute_get_item(sql, mod):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            mod.set_attr(list(results[0]))
        return mod
    except IndexError:
        print("Error: unable to fetch data")
        db.rollback()
    finally:
        db.close()


def execute_get_one(sql):
    db = pymysql.connect(HOST, USER, PWD, DB, charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            results = results[0][0]
        else:
            results = None
        return results
    except TypeError:
        print("Error: unable to fetch data")
        db.rollback()
    finally:
        db.close()


class Period:
    TIMESTAMP = "{} BETWEEN '{}' AND '{}' AND "

    def __init__(self, field, time_slot, moment):
        if time_slot[0] is '+':
            self.oper = True
        else:
            self.oper = False
        self.field = field
        self.__get_moment(moment)
        self.__get_segment(time_slot[1:])
        if self.oper:
            self.other_moment = self.moment + self.segment
        else:
            self.other_moment = self.moment - self.segment

    def __get_moment(self, moment):
        if moment.upper().__eq__('NOW'):
            moment = datetime.now()
        else:
            moment = datetime.strptime(moment, "%Y-%m-%d %H:%M:%S")
        self.moment = moment

    def __get_segment(self, time_slot):
        time = time_slot.split(':')
        for i in range(len(time)):
            time[i] = int(time[i])
        delta = None
        if len(time) is 1:
            delta = timedelta(seconds=time[-1])
        elif len(time) is 2:
            delta = timedelta(seconds=time[-1], minutes=time[-2])
        elif len(time) is 3:
            delta = timedelta(seconds=time[-1], minutes=time[-2], hours=time[-3])
        elif len(time) is 4:
            delta = timedelta(seconds=time[-1], minutes=time[-2], hours=time[-3], days=time[-4])
        self.segment = delta

    def get_sql(self):
        sql = ''
        if self.oper:
            time_1 = self.moment
            time_2 = self.other_moment
        else:
            time_1 = self.other_moment
            time_2 = self.moment
        sql = Period.TIMESTAMP.format(self.field, time_1, time_2)
        return sql


class Pagination:
    def __init__(self, page, paging):
        self.page = page  # now page
        self.paging = paging  # one page items count
        self.item_count = None  # all page items count
        self.items = None  # all items
        self.pages = None  # all page count
        self.hasPrev = None
        self.hasNext = None
        self.hasItem = None

    def get_limit(self):
        return [(self.page - 1) * self.paging, self.paging]

    def set_default(self):
        self.pages = self.item_count // self.paging + 1
        self.hasPrev = self.page is not 1
        self.hasNext = self.page is not self.pages
        self.hasItem = self.item_count


class ValueOfvSQLError(Exception):
    def __init__(self, arg):
        self.args = arg


class Module:
    INIT = True
    M_SELECT = 1
    M_INSERT = 2
    M_UPDATE = 3
    M_DELETE = 4
    M_DROP = 5

    def __init__(self, **args):
        self.no = ''
        self.like = ''
        self.period = ''
        self.distinct = ''
        self.pagination = ''
        self.primary = ''
        for k in self.rows():
            v = args.get(k)
            self.__setattr__(k, v)

        if Module.INIT and Module.__subclasses__():
            Module.INIT = False
            create_all_table()

    @staticmethod
    def get_tables():
        tables = []
        for clazz in Module.__subclasses__():
            tables.append(clazz().get_sql())
        return tables

    def get_sql(self):
        return {'table': self.table(), 'rows': self.rows()}

    def table(self):
        return self.__class__.__name__

    def rows(self):
        rows = {}
        for r in self.__class__.__dict__.items():
            if isinstance(r[1], (column, foreign)):
                rows[r[0]] = r[1]
                if r[1].primary:
                    self.primary = r[0]
        return rows

    def set_attr(self, params):
        for row in self.rows().keys():
            if params or isinstance(params, (int, bool)):
                self.__setattr__(row, params.pop(0))

    def get_attr(self):
        attr = {}
        for k in self.rows():
            attr[k] = self.__getattribute__(k)
        return attr

    def __str__(self):
        string = ''
        for k, v in self.rows().items():
            string = string + k + ' : ' + v + ' '
        return string

    def set_pagination(self, page, paging):
        self.pagination = Pagination(paging=paging, page=page)
        return self

    def set_period(self, field, time_slot, moment="now"):
        self.period = Period(field, time_slot, moment)
        return self

    def No(self, **kwargs):
        order = ''
        for k, v in kwargs.items():
            order = order + k + '!=' + cover(v, "'{}'") + ' AND '
        self.no = order
        return self

    def Like(self, **kwargs):
        order = ''
        for k, v in kwargs.items():
            order = order + k + ' LIKE ' + cover(v, "'%{}%'") + ' AND '
        self.like = order
        return self

    def Distinct(self, *args):
        order = ''
        for field in args:
            order = order + ' DISTINCT ' + field + ' AND '
        self.distinct = order
        return self

    def exists(self):
        return isexists(self.table()) is not None

    def create(self):
        create(self)

    def insert(self):
        self.listener_begin(do=Module.M_INSERT)
        insert(self)
        item = self.select(one=True)
        self.listener_end(do=Module.M_INSERT)
        return item

    def insert_without_return(self):
        self.listener_begin(do=Module.M_INSERT)
        insert(self)
        self.listener_end(do=Module.M_INSERT)

    def update(self):
        self.listener_begin(do=Module.M_UPDATE)
        update(self)
        item = self.select(one=True)
        self.listener_end(do=Module.M_UPDATE)
        return item

    def delete(self):
        self.listener_begin(do=Module.M_DELETE)
        delete(self)
        self.listener_end(do=Module.M_DELETE)

    def select(self, oder='', limit=0, asc=True, count=False, one=False):
        self.listener_begin(do=Module.M_SELECT)
        items = select(self, oder=oder, asc=asc, limit=limit, count=count, one=one)
        self.listener_end(do=Module.M_SELECT)
        return items

    def drop(self):
        return drop(self)

    def listener_begin(self, do):
        pass

    def listener_end(self, do):
        pass
