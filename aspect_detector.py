
import utils


import pandas as pd



class AspectDetector(object):

    def __init__(self,mind_map_path="", data_type='english'):
        #ROOT_DIR = utils.get_parent_root()
        self.data_type = data_type

        self.set_mind_map(mind_map_path)

    def set_mind_map(self, path):
        self.mind_map = self.read_mind_map(path)


    def read_mind_map_new(self,filePath):
        df=pd.read_excel(filePath)
        df['key_word_name'].str.lower()
        return df

    def read_mind_map(self,filePath):
        #gui_screen.progress(0)
        #main_screen.change_progress_bar(20)
        data=utils.read_excel_file(filePath)
        #gui_screen.progress(10)
        category_map_to_subcategory={}
        sub_category_map_to_keyword={}

        try:
            #fill sub_category_map_to_keyword , keys is sub categories and values is list of keywords for each sub category
            sub_category_data = data[['sub_categories_name', 'key_word_name']]
            for index, row in sub_category_data.iterrows():
                if row[0] not in sub_category_map_to_keyword:
                    sub_category_map_to_keyword[row[0]] = [row[1]]
                else:
                    sub_category_map_to_keyword[row[0]] = sub_category_map_to_keyword[row[0]] + [row[1]]
            #self.gui_screen.progress(20)
        except:
            pass
            #self.gui_screen.message_box("Error","Failed to map subcategory to its keywords from the mindmap")

        try:

            #fill category_map_to_subcategory, keys is the categories , values is a list of subcategories of each category
            category_data = data[['categories_name', 'sub_categories_name']]
            for index, row in category_data.iterrows():
                if row[0] not in category_map_to_subcategory:
                    category_map_to_subcategory[row[0]] = [row[1]]
                else:
                    category_map_to_subcategory[row[0]] = list(set(category_map_to_subcategory[row[0]] + [row[1]]))
            #gui_screen.progress(30)
            return category_map_to_subcategory,sub_category_map_to_keyword
        except:
            pass
            #gui_screen.message_box("Error", "Failed to map category to its subcategories from the mindmap")


