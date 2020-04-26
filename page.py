class Page:
    page_display_names = {"voting": "Spätná väzba učiteľom", "results": "Spätná väzba od žiakov",
                          "event_management": "Správa anketových udalostí", "supervisor": "Výsledky učiteľov",
                          "results2": "Spätná väzba k udalostiam"}

    @staticmethod
    def get_page_display_name(page_file_name):
        return Page.page_display_names[page_file_name]
