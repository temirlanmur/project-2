class CustomPageRangeMixin:
    pages_on_each_side = 1  # The number of pages on each side of the current page number

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.pages_on_each_side == None or self.pages_on_each_side == 0:
            return context
            
        # Add custom page range to the context. (For pagination)
        page_number = context['page_obj'].number
        num_pages = context['paginator'].num_pages

        left_index = int(page_number) - self.pages_on_each_side
        if left_index < 1:
            left_index = 1
        right_index = int(page_number) + self.pages_on_each_side
        if right_index > num_pages:
            right_index = num_pages
        custom_range = range(left_index, right_index + 1)  # Because python range(1, 4) is from 1 till 3
        
        context['custom_page_range'] = custom_range
        return context