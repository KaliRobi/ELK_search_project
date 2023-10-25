import json
import logging


class TicketContentItem:
    rt_history_fields = {
        'date_time': 'Created',
        'creator': 'Creator',
        'subject': 'Data',
        'type': 'Type',
        'description': 'Description',
        'content': 'Content',
    }

    def __init__(self, history_data_item):
        self.date_time = history_data_item[self.rt_history_fields['date_time']]
        self.creator = history_data_item[self.rt_history_fields['creator']]
        self.subject = history_data_item[self.rt_history_fields['subject']]
        self.type = history_data_item[self.rt_history_fields['type']]
        self.description = history_data_item[self.rt_history_fields['description']]
        self.content = history_data_item[self.rt_history_fields['content']]

    def get_string(self):
        separator = '########################################################################################'
        return '{0} {1}:\n\n{2}\n\n{3}\n\n'.format(self.date_time, self.description, self.content, separator)


class TicketContent:
    def __init__(self, history_data):
        self.ticket_content_items = []
        for history_data_item in history_data:
            self.ticket_content_items.append(TicketContentItem(history_data_item))

    def get_string(self):
        return ''.join(
            list(map(lambda ticket_content_item: ticket_content_item.get_string(), self.ticket_content_items)))


class ticket:
    rt_field_names = {
        'ticket_id': 'numerical_id',
        'queue': 'Queue',
        'owner': 'Owner',
        'creator': 'Creator',
        'subject': 'Subject',
        'status': 'Status',
        'requestors': 'Requestors',
        'cc': 'Cc',
        'created': 'Created',
        'last_updated': 'LastUpdated',
        'affected_application': 'CF.{Affected Application}',
        'ticket_category': 'CF.{Ticket Category}',
        'ticket_type': 'CF.{Ticket Type}',
        'region': 'CF.{ - Region}',
        'extension': 'CF.{Extension}',
        'company': 'CF.{ - Company}',
        'environment': 'CF.{Environment}',
        'affected_module': 'CF.{ - Affected Module}',
        'affected_module_other': 'CF.{ - Affected_Module_Other}',
        'application_area': 'CF.{ - Application_Area}',
        'application_area_other': 'CF.{ - Application_Area_Other}',
        'hpqc_ticket': 'CF.{HPQC Ticket No.}',
        'jira_ticket': 'CF.{Jira Ticket No.}',
    }

    def __init__(self, ticket_data, ticket_content: TicketContent = None):
        if ticket_data is not None:
            self.__ticket_data = ticket_data
            self.ticket_id = None
            self.ticket_id = self._add_field('ticket_id')
            self.queue = self._add_field('queue')
            self.owner = self._add_field('owner')
            self.creator = self._add_field('creator')
            self.subject = self._add_field('subject')
            self.status = self._add_field('status')
            self.requestors = self._add_field('requestors')
            self.cc = self._add_field('cc')
            self.created = self._add_field('created')
            self.last_updated = self._add_field('last_updated')
            if ticket_content is not None:
                self.content = ticket_content.get_string()

    def _add_field(self, rt_field_name):
        """Checks if the requested rt field exists in the passed ticket data. If it does and the value of the field is
        not an empty string, returns the value. Otherwise, returns None.

        :param ticket_data:     rt ticket data that is being parsed
        :param rt_field_name:   the rt field name to be looked up in the ticket data
        :return:                rt field value if it exists and is non-empty. None otherwise.
        """
        if self.rt_field_names[rt_field_name] in self.__ticket_data:
            if self.__ticket_data[self.rt_field_names[rt_field_name]] != '':
                logging.debug('Setting field {0} to {1} for rt#{2}'.format(rt_field_name, self.__ticket_data[
                    self.rt_field_names[rt_field_name]], self.ticket_id))
                return self.__ticket_data[self.rt_field_names[rt_field_name]]
        else:
            logging.debug('Field {0} does not exist for rt#{1}. Setting to None.'.format(rt_field_name, self.ticket_id))
            return None

    def set_content(self, ticket_content: TicketContent):
        self.content = ticket_content.get_string()

    def get_json(self):
        fields_data_dict = dict(self.__dict__)
        del fields_data_dict['_Ticket__ticket_data']
        return json.dumps(fields_data_dict)


class Ticket(ticket):
    def __init__(self, ticket_data):
        if ticket_data is not None:
            super().__init__(ticket_data)
            self.affected_application = self._add_field('affected_application')
            self.ticket_category = self._add_field('ticket_category')
            self.ticket_type = self._add_field('ticket_type')
            self.air_sea = self._add_field('air_sea')
            self.region = self._add_field('region')
            self.extension = self._add_field('extension')
            self.company = self._add_field('company')
            self.environment = self._add_field('environment')
            self.affected_module = self._add_field('affected_module')
            self.affected_module_other = self._add_field('affected_module_other')
            self.application_area = self._add_field('application_area')
            self.application_area_other = self._add_field('application_area_other')
            self.hpqc_ticket = self._add_field('hpqc_ticket')
            self.jira_ticket = self._add_field('jira_ticket')

    def _add_field(self, rt_field_name):
        return super(ticket, self)._add_field(rt_field_name)
