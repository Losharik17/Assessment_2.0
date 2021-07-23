def users_in_json(users):
    string = '['
    for user in users:
        string += '{' + '"id":{0},"username":"{1}","birthday":"{2}","team":"{3}",' \
            .format(str(user.id),
                    str(user.username),
                    str(user.birthday),
                    str(user.team))

        for i in range(5):
            string += '"sum_grade_{0}":"{1}",' \
                .format(i, str(user.__dict__['sum_grade_{}'.format(i)]))

        string += '"sum_grade_all":"{0}"'.format(str(user.sum_grade_all)) + '},'

    string = string[:len(string) - 1] + ']'

    return string


def experts_in_json(experts):
    string = '['

    for expert in experts:
        string += '{' + '"id":{0},"username":"{1}","weight":"{2}","quantity":"{3}},' \
            .format(str(expert.id),
                    str(expert.username),
                    str(expert.weight),
                    str(expert.quantity)) + '},'

    string = string[:len(string) - 1] + ']'

    return string
