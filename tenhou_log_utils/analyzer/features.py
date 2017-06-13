def extract_feature(game):
    meta_info = {
        'table': game.table,
        'red': game.config.red,
        'kui': game.config.kui,
        'soku': game.config.soku,
        'sanma': game.config.sanma,
        'ton_nan': game.config.ton_nan,
        'ton_pu': not game.config.ton_nan,
    }

    for index, player in enumerate(game.players):
        key = 'name%s' % (index)
        meta_info[key] = player.name
        key = 'dan%s' % (index)
        meta_info[key] = player.dan
        key = 'rate%s' % (index)
        meta_info[key] = player.rate
    infos = []
    for round_ in game.past_rounds:
        round_info = {
            'round': round_.index,
            'winner': round_._agari.get('winner'),
            'loser': round_._agari.get('loser'),
            'yaku': [val[0] for val in round_._agari['yaku']],
        }
        round_info.update(meta_info)
        infos.append(round_info)
    return infos
