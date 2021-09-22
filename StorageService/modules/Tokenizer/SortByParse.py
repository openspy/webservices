from modules.ReservedKeys import IsReservedKey
class MongoSortFactory():
    def Sort(self, input_string):
        
        sort_groups = input_string.split(',')

        results = {}
        for sort in sort_groups:
            sort_items = sort.strip().split(' ')
            sort_order = 1 #ASC
            
            if len(sort_items) > 1 and sort_items[1].lower() == 'desc':
                sort_order = -1

            key = sort_items[0]
            if not IsReservedKey(key):
                key = "data.{}.value".format(key)
            results[key] = sort_order

        return results