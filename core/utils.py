def forward_chaining(gejala_input, all_rules):
    input_set = set(map(int, gejala_input))
    kandidat = []

    for rule in all_rules:
        rule_set = set(map(int, rule['gejala_ids'].split(',')))
        match_count = len(input_set & rule_set)
        total_count = len(rule_set)

        if match_count > 0:
            kandidat.append({
                'rule': rule,
                'match_count': match_count,
                'total_count': total_count,
                'akurasi': int((match_count / total_count) * 100)
            })

    if kandidat:
        kandidat.sort(key=lambda x: (-x['akurasi'], -x['match_count']))
        best_match = kandidat[0]
        saran = set(map(int, best_match['rule']['gejala_ids'].split(','))) - input_set
        return best_match, saran
    return None, None
