def update_meeting_sla(rel, meeting_sla):
    rel.meeting_sla = meeting_sla.id


def update_call_sla(rel, call_sla):
    rel.call_sla = call_sla.id


def update_relationship_name(rel, name):
    rel.name = name
