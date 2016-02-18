import json
import re
import urllib2

import sys

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, Response, jsonify
# from werkzeug import check_password_hash, generate_password_hash
import rcdb
from collections import defaultdict
from rcdb import DefaultConditions
from rcdb.model import Run, BoardInstallation, Condition, ConditionType
from rcdb_www.pagination import Pagination
from sqlalchemy import func
from sqlalchemy.orm import subqueryload, joinedload

mod = Blueprint('runs', __name__, url_prefix='/runs')

_nsre=re.compile("([0-9]+)")

def natural_sort_key(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


PER_PAGE = 500


@mod.route('/', defaults={'page': 1, 'run_from': -1, 'run_to': -1})
@mod.route('/page/<int:page>', defaults={'run_from': -1, 'run_to': -1})
@mod.route('/<int:run_from>-<int:run_to>', defaults={'page': 1})
def index(page, run_from, run_to):

    query = g.tdb.session.query(Run)

    # Run range is defined?
    if run_from != -1 and run_to != -1:

        # Check what is max/min run
        run_min, run_max = run_from, run_to
        if run_max < run_min:
            run_min, run_max = run_max, run_min

        # Filter query and count results
        query = query.filter(Run.number >= run_min, Run.number <= run_max)
        count = g.tdb.session.query(func.count(Run.number)).filter(Run.number >= run_min, Run.number <= run_max).scalar()

        # we don't want pagination in this case, setting page size same/bigger than count
        per_page = run_max - run_min
    else:
        count = g.tdb.session.query(func.count(Run.number)).scalar()
        per_page = PER_PAGE

    # Create pagination
    pagination = Pagination(page, per_page, count)

    # Get runs from query
    runs = query.options(subqueryload(Run.conditions))\
        .order_by(Run.number.desc())\
        .slice(pagination.item_limit_from, pagination.item_limit_to)\
        .all()

    return render_template("runs/index.html", runs=runs, DefaultConditions=DefaultConditions, pagination=pagination)
    pass


@mod.route('/conditions/<int:run_number>')
def conditions(run_number):
    run = g.tdb.session. \
        query(Run). \
        options(subqueryload(Run.conditions)). \
        filter_by(number=int(run_number)).one()

    return render_template("runs/conditions.html", run=run)


@mod.route('/info/<int:run_number>')
def info(run_number):
    """Shows run information and statistics
    :param run_number:
    """

    run = g.tdb.session \
        .query(Run) \
        .options(subqueryload(Run.conditions)) \
        .filter(Run.number == run_number) \
        .first()

    prev_run = g.tdb.get_prev_run(run_number)
    next_run = g.tdb.get_next_run(run_number)

    if not isinstance(run, Run):
        return render_template("runs/not_found.html", run_number=run_number, prev_run=prev_run, next_run=next_run)

    assert (isinstance(run, Run))
    conditions_by_name = run.get_conditions_by_name()

    # create board by crate list
    bi_by_crate = defaultdict(list)
    for bi in run.board_installations:
        bi_by_crate[bi.crate].append(bi)

    # sort boards by slot
    for bis in bi_by_crate.values():
        bis.sort(key=lambda x: x.slot)

    if rcdb.DefaultConditions.COMPONENT_STATS in conditions_by_name:
        component_stats = json.loads(conditions_by_name[rcdb.DefaultConditions.COMPONENT_STATS].value)
        component_sorted_keys = natural_sort_key([str(key) for key in component_stats.keys()])
    else:
        component_stats = None
        component_sorted_keys = None

    return render_template("runs/info.html",
                           run=run,
                           conditions=run.conditions,
                           conditions_by_name=conditions_by_name,
                           board_installs_by_crate=bi_by_crate,
                           component_stats=component_stats,
                           component_sorted_keys=component_sorted_keys,
                           DefaultConditions=rcdb.DefaultConditions,
                           prev_run=prev_run,
                           next_run=next_run
                           )


@mod.route('/elog/<int:run_number>')
def elog(run_number):
    try:
        elog_json = urllib2.urlopen('https://logbooks.jlab.org/api/elog/entries?book=hdrun&title=Run_{}&limit=1'.format(run_number)).read()
    except urllib2.HTTPError as e:
        return jsonify(stat=str(e.code))

    resp = Response(response=elog_json, status=200, mimetype="application/json")
    return resp


def _parse_run_range(run_range_str):
    """ Parses run range, returning a pair (run_from, run_to) or (run_from, None) or (None, None)

    Function doesn't raise FormatError
    :exception ValueError: if run_range_str is not str

    :param run_range_str: string to parse
    :return: (run_from, run_to). Function always return lower run number as run_from
    """

    if run_range_str is None:
        return None, None

    run_range_str = str(run_range_str).strip()
    if not run_range_str:
        return None, None

    assert isinstance(run_range_str, str)

    # Have run-range?
    if '-' in run_range_str:
        tokens = [t.strip() for t in run_range_str.split("-")]
        try:
            run_from = int(tokens[0])
        except (ValueError, KeyError):
            return None, None

        try:
            run_to = int(tokens[1])
        except (ValueError, KeyError):
            return run_from, None

        return (run_from, run_to) if run_from <= run_to else (run_to, run_from)

    # Have run number?
    if run_range_str.isdigit():
        return int(run_range_str), None

    # Default return is index
    return None, None


@mod.route('/search', methods=['GET'])
def search():
    run_range = request.args.get('rr', '')
    search_query = request.args.get('q', '')

    args = {}
    run_from, run_to = _parse_run_range(run_range)

    if not search_query or not search_query.strip():
        if run_from is not None and run_to is not None:
            return redirect(url_for('.index', run_from=run_from, run_to=run_to))
        elif run_from is not None:
            return redirect(url_for('.info', run_number=int(search_query)))
        else:
            return redirect(url_for('.index'))

    if run_from is None:
        run_from = 0

    if run_to is None:
        run_to = sys.maxint

    try:
        result = g.tdb.select_runs(search_query, run_to, run_from, sort_desc=True)

        # Create pagination
        pagination = Pagination(1, len(result.runs), len(result.runs))

        return render_template("runs/index.html", runs=result.runs, DefaultConditions=DefaultConditions, pagination=pagination)
    except Exception as err:
        flash("Error in performing request: {}".format(err), 'danger')
        return redirect(url_for('.index'))


















