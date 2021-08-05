list_dict = [
    {'first':'Mike', 'last': 'Jackson'},
    {'first':'Ken', 'last': 'Smith'},
    {'first':'Lisa', 'last': 'Foo'},
]

def func(array):
    print('First Names')
    for i in range(len(array)):
        print(array[i]['first'])
    print()
    print('Last Names')
    for j in range(len(array)):
        print(array[j]['last'])


func(list_dict)