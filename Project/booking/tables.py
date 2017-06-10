import django_tables2 as tables
from .models import Meetingroom

class RoomTable(tables.Table):
    selection = tables.RadioColumn(accessor='pk')
    room_type = tables.Column(orderable=False)
    room_dscp = tables.Column(orderable=False)
    room_noofperson = tables.Column(orderable=False)

    class Meta:
        model = Meetingroom
        attrs = {'class': 'table table-striped',
		}
	sequence = ('selection', 'room_type','room_dscp', 'room_noofperson')