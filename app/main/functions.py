def users_in_json(users):

    string = '['
    for user in users:
        string += '{"id":' + str(user.id) + ',"username":"' + str(user.username) + \
                  '","birthday":"' + str(user.birthday) + '","team":"' + str(user.team) + \
                  '",'
        for i in range(5):
            string += '"sum_grade_{}":'.format(i) + \
                      str(user.__dict__['sum_grade_{}'.format(i)]) + ','
        string += '"sum_grade_all":' + str(user.sum_grade_all) + '},'

    string = string[:len(string) - 1] + ']'

    return string
