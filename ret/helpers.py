#def get_player_by_participant_id(group, participant_id):
 #   """
  #     Find a player in the given group by their participant ID.
   # """
    #return next((p for p in group.get_players() if p.participant.id == participant_id), None)
def get_player_by_participant_id(group, participant_id, round_number):
    for p in group.subsession.in_round(round_number).get_players():
        if p.participant.id == participant_id:
            return p
    return None


