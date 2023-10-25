import argparse
from datetime import datetime, timedelta
import logging

from rt_local.rt import Rt
from ticket_parser import __connect_elasticsearch, get_relevant_tickets_since, create_ticket_objects, post_to_elasticsearch

RT_HOSTNAME = 'https://RT_server/REST/1.0/'
RT_USERNAME = 'oursessionname'
RT_PASSWORD = '6-6db5c1c-6db5c1c6db5c1c6db5c1c6db5c1c6db5c1c6db5c1c'

# initializing the argument parser to read input from other scripts

arg_parser = argparse.ArgumentParser(
    description='Import tickets from RT to Kibana updated on or after the given date. By default, takes all tickets '
                'updated in between the time of execution and 00:00 UTC on the previous day. '
                'It is also possible to specify the exact "From" and "To" dates to get results only for a specific '
                'date range.'
)
arg_parser.add_argument('--dFrom', help='the "From" date to check for ticket updates')
arg_parser.add_argument('--dTo', help='the "To" date to specificall limit the date range')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = arg_parser.parse_args()

    es = __connect_elasticsearch()

    if es is None:
        logging.error("Could not connect to ELK. Exiting.")
        quit(1)

    tracker = Rt(RT_HOSTNAME, RT_USERNAME, RT_PASSWORD)
    if not tracker.login():
        logging.error("Could not log into RT. Exiting.")
        quit(2)

    if args.dFrom is not None and args.dTo is not None:
        date_from = args.dFrom
        # we need to add one day to the To date to make RT include it in search
        date_to = args.dTo
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        date_to = str(date_to_obj + timedelta(days=1))
        logging.debug('Provided dates: from: {0}, to: {1}'.format(date_from, date_to))
    else:
        date_from = str(datetime.date(datetime.now()) - timedelta(days=1))
        date_to = None

    # getting tickets from all relevant queues
    # Separate the tickets to different queues. log-* template should be able to get it together while we all have option for separate queue checking
    PM_tickets = get_relevant_tickets_since(rt_obj=tracker, from_date=date_from, to_date=date_to,
                                                 queue='PROBLEM.MANAGEMENT')
    SYSTEM_SUPPORT_TICKETS = get_relevant_tickets_since(rt_obj=tracker, from_date=date_from, to_date=date_to,
                                                 queue='ONESYSTEM-Support')
    TEAM_A1_TICKETS = get_relevant_tickets_since(rt_obj=tracker, from_date=date_from, to_date=date_to,
                                                 queue='SECONDESYSTEM.SUPPORT')
    YET_ANOTHER_TEAM_TICKETS = get_relevant_tickets_since(rt_obj=tracker, from_date=date_from, to_date=date_to,
                                                 queue='THIS.TEAMS.QUEUE')
    SO_MANY_TEAMS_MAN = get_relevant_tickets_since(rt_obj=tracker, from_date=date_from, to_date=date_to,
                                                 queue='THAT.TEAMS.QUEUE') 



    # retrieving content for all the retrieved tickets
    create_ticket_objects(tracker, PM_tickets)
    create_ticket_objects(tracker, SYSTEM_SUPPORT_TICKETS)
    create_ticket_objects(tracker, TEAM_A1_TICKETS)
    create_ticket_objects(tracker, YET_ANOTHER_TEAM_TICKETS)
    create_ticket_objects(tracker, SO_MANY_TEAMS_MAN)


    # storing tickets in ES 
    # each of these have the possibility to get their own indexes 
    for ticket in PM_tickets:
        post_to_elasticsearch(es_obj=es, index_name='rt_search_test', rt_ticket=ticket.get_json(), ticket_id=ticket.ticket_id)
    for ticket in SYSTEM_SUPPORT_TICKETS:
        post_to_elasticsearch(es_obj=es, index_name='rt_search_test', rt_ticket=ticket.get_json(), ticket_id=ticket.ticket_id)
    for ticket in TEAM_A1_TICKETS:
        post_to_elasticsearch(es_obj=es, index_name='rt_search_test', rt_ticket=ticket.get_json(), ticket_id=ticket.ticket_id)
    for ticket in YET_ANOTHER_TEAM_TICKETS:
        post_to_elasticsearch(es_obj=es, index_name='rt_search_test', rt_ticket=ticket.get_json(), ticket_id=ticket.ticket_id)
    for ticket in SO_MANY_TEAMS_MAN:
        post_to_elasticsearch(es_obj=es, index_name='rt_search_test', rt_ticket=ticket.get_json(), ticket_id=ticket.ticket_id)


    tracker.logout()
