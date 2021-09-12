class ConstructListMixin:

    def construct_list(self, object_list, COLUMNS=4):

        TOTAL_ITEMS = len(object_list)
        ROWS = TOTAL_ITEMS // COLUMNS
        ROWS = ROWS + 1 if (TOTAL_ITEMS % COLUMNS) else ROWS

        result_list = []
        
        for _ in range(ROWS):
            new_row = [None for i in range(COLUMNS)]
            result_list.append(new_row)

        i = 0
        for row_count in range(ROWS):            
            for item_count in range(COLUMNS):
                result_list[row_count][item_count] = object_list[i]
                i += 1
                if (i == TOTAL_ITEMS):
                    break
        
        return result_list