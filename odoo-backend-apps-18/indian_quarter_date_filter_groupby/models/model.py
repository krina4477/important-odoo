# -*- coding: utf-8 -*-
import logging
import re
import babel.dates
import dateutil.relativedelta
import psycopg2.extensions
import datetime
import pytz
from odoo import api, models
import babel
import babel.dates
import dateutil.relativedelta
from odoo.models import BaseModel
from odoo.tools import (
    clean_context, config, date_utils, discardattr,
    DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, frozendict,
    get_lang, lazy_classproperty, OrderedSet, ormcache,
    partition, populate, Query, split_every, unique, SQL,
)
from odoo.osv import expression

_logger = logging.getLogger(__name__)
_unlink = logging.getLogger(__name__ + '.unlink')

READ_GROUP_TIME_GRANULARITY = {
    'hour': dateutil.relativedelta.relativedelta(hours=1),
    'day': dateutil.relativedelta.relativedelta(days=1),
    'week': datetime.timedelta(days=7),
    'month': dateutil.relativedelta.relativedelta(months=1),
    'quarter': dateutil.relativedelta.relativedelta(months=3),
    'year': dateutil.relativedelta.relativedelta(years=1)
}

READ_GROUP_DISPLAY_FORMAT = {
    'hour': 'hh:00 dd MMM',
    'day': 'dd MMM yyyy',  # yyyy = normal year
    'week': "'W'w YYYY",  # w YYYY = ISO week-year
    'month': 'MMMM yyyy',
    'quarter': 'QQQ yyyy',
    'year': 'yyyy',
}


regex_read_group_spec = re.compile(r'(\w+)(\.(\w+))?(?::(\w+))?$')  # For _read_group

AUTOINIT_RECALCULATE_STORED_FIELDS = 1000

INSERT_BATCH_SIZE = 100
SQL_DEFAULT = psycopg2.extensions.AsIs("DEFAULT")

def parse_read_group_spec(spec: str) -> tuple:
    """ Return a triplet corresponding to the given groupby/path/aggregate specification. """
    res_match = regex_read_group_spec.match(spec)
    if not res_match:
        raise ValueError(
            f'Invalid aggregate/groupby specification {spec!r}.\n'
            '- Valid aggregate specification looks like "<field_name>:<agg>" example: "quantity:sum".\n'
            '- Valid groupby specification looks like "<no_datish_field_name>" or "<datish_field_name>:<granularity>" example: "date:month" or "<properties_field_name>.<property>:<granularity>".'
        )

    groups = res_match.groups()
    return groups[0], groups[2], groups[3]

class BaseModelExtend(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _read_group_format_result(self, rows_dict, lazy_groupby):
        """
            Helper method to format the data contained in the dictionary data by
            adding the domain corresponding to its values, the groupbys in the
            context and by properly formatting the date/datetime values.

        :param data: a single group
        :param annotated_groupbys: expanded grouping metainformation
        :param groupby: original grouping metainformation
        """
        for group in lazy_groupby:
            field_name = group.split(':')[0].split('.')[0]
            field = self._fields[field_name]

            if field.type in ('date', 'datetime'):
                locale = get_lang(self.env).code
                fmt = DEFAULT_SERVER_DATETIME_FORMAT if field.type == 'datetime' else DEFAULT_SERVER_DATE_FORMAT
                granularity = group.split(':')[1] if ':' in group else 'month'
                interval = READ_GROUP_TIME_GRANULARITY[granularity]

            elif field.type == "properties":
                self._read_group_format_result_properties(rows_dict, group)
                continue

            for row in rows_dict:
                value = row[group]

                if isinstance(value, BaseModel):
                    row[group] = (value.id, value.sudo().display_name) if value else False
                    value = value.id

                if not value and field.type == 'many2many':
                    other_values = [other_row[group][0] if isinstance(other_row[group], tuple)
                                    else other_row[group].id if isinstance(other_row[group], BaseModel)
                    else other_row[group] for other_row in rows_dict if other_row[group]]
                    additional_domain = [(field_name, 'not in', other_values)]
                else:
                    additional_domain = [(field_name, '=', value)]

                if field.type in ('date', 'datetime'):
                    if value and isinstance(value, (datetime.date, datetime.datetime)):
                        range_start = value
                        range_end = value + interval
                        if field.type == 'datetime':
                            tzinfo = None
                            if self._context.get('tz') in pytz.all_timezones_set:
                                tzinfo = pytz.timezone(self._context['tz'])
                                range_start = tzinfo.localize(range_start).astimezone(pytz.utc)
                                # take into account possible hour change between start and end
                                range_end = tzinfo.localize(range_end).astimezone(pytz.utc)

                            label = babel.dates.format_datetime(
                                range_start, format=READ_GROUP_DISPLAY_FORMAT[granularity],
                                tzinfo=tzinfo, locale=locale
                            )

                            if READ_GROUP_DISPLAY_FORMAT[granularity] == 'yyyy':
                                label = '%s-%s' % (value.year, str(value.year + 1)[2:])

                            if READ_GROUP_DISPLAY_FORMAT[granularity] == 'QQQ yyyy':
                                if value.month == 4:
                                    label = '%s %s-%s' % ('Q1', value.year, str(value.year + 1)[2:])
                                elif value.month == 7:
                                    label = '%s %s-%s' % ('Q2', value.year, str(value.year + 1)[2:])
                                elif value.month == 10:
                                    label = '%s %s-%s' % ('Q3', value.year, str(value.year + 1)[2:])
                                elif value.month == 1:
                                    label = '%s %s-%s' % ('Q4', value.year - 1, str(value.year)[2:])
                        else:
                            label = babel.dates.format_date(
                                value, format=READ_GROUP_DISPLAY_FORMAT[granularity],
                                locale=locale
                            )

                            if READ_GROUP_DISPLAY_FORMAT[granularity] == 'yyyy':
                                label = '%s-%s' % (value.year, str(value.year + 1)[2:])

                            if READ_GROUP_DISPLAY_FORMAT[granularity] == 'QQQ yyyy':
                                if value.month == 4:
                                    label = '%s %s-%s' % ('Q1', value.year, str(value.year + 1)[2:])
                                elif value.month == 7:
                                    label = '%s %s-%s' % ('Q2', value.year, str(value.year + 1)[2:])
                                elif value.month == 10:
                                    label = '%s %s-%s' % ('Q3', value.year, str(value.year + 1)[2:])
                                elif value.month == 1:
                                    label = '%s %s-%s' % ('Q4', value.year - 1, str(value.year)[2:])

                        range_start = range_start.strftime(fmt)
                        range_end = range_end.strftime(fmt)
                        row[group] = label  # TODO should put raw data
                        row.setdefault('__range', {})[group] = {'from': range_start, 'to': range_end}
                        additional_domain = [
                            '&',
                            (field_name, '>=', range_start),
                            (field_name, '<', range_end),
                        ]
                    elif not value:
                        # Set the __range of the group containing records with an unset
                        # date/datetime field value to False.
                        row.setdefault('__range', {})[group] = False

                row['__domain'] = expression.AND([row['__domain'], additional_domain])