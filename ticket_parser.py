from rt_local import Rt, ConnectionError, UnexpectedResponse
from elasticsearch import Elasticsearch
import logging
from datetime import date, timedelta

from ticket import ticket, ticket, TicketContent


def __connect_elasticsearch():
    # TODO: documentation
    _es = None
    _es = Elasticsearch(['https://server:9200'], http_auth=('mainMasterSuperUserAccountName', 'andItsPassword'))
    if _es.ping():
        logging.info('Successfully connected to Elasticsearch')
    else:
        logging.info('Could not connect to Elasticsearch')
    return _es


def post_to_elasticsearch(es_obj: Elasticsearch, index_name, rt_ticket, ticket_id):
    # posts the ticket objects to ELK, mapped by an index (here rt_search)
    try:
        result = es_obj.index(index=index_name, body=rt_ticket, id=ticket_id)
        logging.info(result)
    except Exception as ex:
        logging.error('Error indexing data:\n' + str(ex))


def get_tickets_for_last_n_days(rt_obj: Rt, n: int, queue):
    
    since_date = date.today() - timedelta(days=n)
    logging.info(
        'Retrieving the tickets in queue {0} updated in the last {1} day(s) (since {2})'.format(queue, n, since_date))
    rt_tickets = rt_obj.last_updated(since=str(since_date), queue=queue)
    logging.info(rt_tickets.__len__())

    processed_tickets = []
    for rt_ticket in rt_tickets:
        processed_tickets.append(ticket(ticket_data=rt_ticket))

    return processed_tickets


def get_relevant_tickets_since(rt_obj: Rt, from_date: str, queue, to_date: str = None):
    logging.info('Retrieving tickets in queue {0} updated since {1}'.format(queue, from_date))
    rt_ticket_search_query = "LastUpdated > '{0}' " \
                "AND Subject NOT LIKE 'automatically generated tcket for system monitoring' " \
                "AND Subject NOT LIKE 'tickets we dont want to rememeber' " \
        .format(from_date)
    # also adding the To date, if given
    if to_date is not None:
        rt_ticket_search_query = rt_ticket_search_query + " AND LastUpdated < '{0}'".format(to_date)
    logging.info('raw_query: "{0}"'.format(rt_ticket_search_query))
    rt_tickets = rt_obj.search(Queue=queue, raw_query=rt_ticket_search_query)
    logging.info('Retrieved {0} tickets'.format(rt_tickets.__len__()))

    processed_tickets = []
    for rt_ticket in rt_tickets:
        processed_tickets.append(ticket(ticket_data=rt_ticket))

    return processed_tickets


def create_ticket_objects(rt_obj: Rt, rt_tickets: list):
    counter = 1
    for rt_ticket in rt_tickets:
        logging.info('{0} of {1}'.format(counter, rt_tickets.__len__()))
        try:
            create_ticket_object(rt_obj=rt_obj, rt_ticket=rt_ticket)
        except (ConnectionError, UnexpectedResponse) as e:
            logging.error('Could not get content for RT#{0}'.format(rt_ticket), e)
        counter += 1



def create_ticket_object(rt_obj: Rt, rt_ticket: ticket):
    ticket_id = rt_ticket.ticket_id
    logging.info('Retrieving content for RT#{0}'.format(ticket_id))    
    history = rt_obj.get_history(ticket_id=ticket_id)
    try:   
            comments_and_correspondence = list(
            filter(lambda element: element['Type'] in ['Comment', 'Correspond', 'Create'], history))
            content = TicketContent(comments_and_correspondence)
            rt_ticket.set_content(content)
            logging.info('Success RT#{0} was processed'.format(rt_ticket.ticket_id)) 
    except KeyError as e:
            logging.info('Invalid ticket content RT#{0}'.format(rt_ticket.ticket_id), e)


