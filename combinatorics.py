def _num_combos(lists):
	num = 1
	for l in lists:
		num *= len(l)

	return num


def _tick_count_list(count_list):
	index = len(count_list) - 1
	while index > -1:
		element = count_list[index]
		if element[1] == element[0] - 1:
			for e in count_list[index:]:
				e[1] = 0
			index -= 1
		else:
			element[1] += 1
			return count_list

	return count_list


def _generate_configs(lists):
	count_list = [[len(i), 0] for i in lists]
	configs = []

	for i in range(_num_combos(lists)):
		l = _tick_count_list(count_list)
		configs.append([i[1] for i in l])

	return configs


def explode_combos(lists):
	configs = _generate_configs(lists)
	combos = []

	for config in configs:
		combo = []
		for i, index in enumerate(config):
			combo.append(lists[i][index])

		combos.append(combo)

	return combos
