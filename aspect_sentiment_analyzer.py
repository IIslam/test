
import classifier
import utils


import pandas as pd

class AspectSentimentAnalyzer(object):

    def __init__(self, config_path='aspect_config.ini', data_type='english', model_path=None, model_type=None):


        config_path = 'sentiment_config.ini'

        try:
            self.classifier = classifier.Classifier(config_path=config_path, model_path=model_path,
                                         model_type=model_type)
        except:
            pass
            #gui_screen.message_box("Error", "Failed to upload the classifier")

        self.data_type = data_type



    def predict_aspect_file_old(self,inputFilePath,outputFilePath,mindmap):
        data, fieldName = utils.read_csv_dict(inputFilePath)
        verbatim_list = []
        category_list = []
        sentiment_list=[]

        for row in data:
            verbatim = row['VERBATIM_DESC']
            predicted_categories = self.predict_verbatim_aspect(verbatim,mindmap)
            for key, values in predicted_categories.items():
                sentiment, cleaned_sentence = self.classifier.predict_sentence(key)
                if len(values)>0:
                    for value in values:
                        verbatim_list.append(cleaned_sentence)
                        category_list.append(value)
                        sentiment_list.append(sentiment)
                        #self.aspect_detector.insert_database(conn,cursor,cleaned_sentence,value,sentiment)
                else:
                    verbatim_list.append(cleaned_sentence)
                    category_list.append("Not Defined")
                    sentiment_list.append(sentiment)
                    #self.aspect_detector.insert_database(conn,cursor, cleaned_sentence, "Not Defined", sentiment)

        d = {'verbatim': verbatim_list, 'category':category_list,'label': sentiment_list}
        df = pd.DataFrame(data=d)

        df.to_csv(outputFilePath, encoding='utf-8', index=False)
        # print(predict_list)


    def predict_aspect_file(self,inputFilePath,outputFilePath,mindmap):
        data, fieldName = utils.read_excel_dict(inputFilePath)
        verbatim_list = []
        category_list = []
        sentiment_list=[]
        subcategory_list=[]
        full_df=pd.DataFrame()

        #progress_step=len(data)/50
        #c=0
        #progress_value=50
        for row in data:
            try:
                verbatim = str(row['verbatim'])
            except:
                pass
                #gui_screen.message_box("Error","There is no 'verbatim' column in the input file")

            # return dictionary consist of key as sentences, and value as a tuple consist of category and subcategory
            predicted_categories = self.predict_verbatim_aspect(verbatim,mindmap)
         #   gui_screen.progress(50)

            rest_data_frame_columns=pd.DataFrame(row,index=[0])
            rest_data_frame_columns = rest_data_frame_columns.loc[:, rest_data_frame_columns.columns != 'verbatim']

            cleaned_verbatim=self.classifier.clean_verbatim(verbatim)
            flag=0
            for sentence in predicted_categories:
                category_subcategory=predicted_categories[sentence]
                sentiment, cleaned_sentence = self.classifier.predict_sentence(sentence)
                # check if after cleaning there are still any word in the sentence
                if len(cleaned_sentence)>0:
                    rest_data_frame_columns['Verbatim']=cleaned_verbatim
                    rest_data_frame_columns['Sentiment'] = sentiment
                    if len(category_subcategory)>0:
                        flag=1
                        for category,subcateory in category_subcategory:
                            rest_data_frame_columns['Category'] = category
                            rest_data_frame_columns['SubCategory'] = subcateory
                            full_df = pd.concat([full_df, rest_data_frame_columns],sort=False, axis=0)
            if flag==0:
                rest_data_frame_columns['Category'] = "Not Defined"
                rest_data_frame_columns['SubCategory'] = "Not Defined"
                full_df = pd.concat([full_df, rest_data_frame_columns],sort=False, axis=0)
          #  c+=1
           # if c%20==0:
            #    gui_screen.progress(progress_value+1)


        full_df.drop_duplicates(inplace=True)
        full_df.to_csv(outputFilePath, encoding='utf-8', index=False)
        #print(predict_list)


    def get_aspect_sentence(self, sentence, mindmap):
        category_subcategory_list=[]
        words_in_mindmap=[]
        sentence=' '+sentence+' '
        '''
        for row in mindmap.itertuples(index=True, name='Pandas'):
            keyword=str(getattr(row, "key_word_name"))
            if ' '+keyword +' ' in sentence:
                words_in_mindmap.append(keyword)
                category_subcategory_list.append((str(getattr(row, "categories_name")), str(getattr(row, "sub_categories_name"))))
        '''
        for row in zip(mindmap['categories_name'], mindmap['sub_categories_name'],mindmap['key_word_name']):
            if ' ' + str(row[2]) + ' ' in sentence:
                words_in_mindmap.append(str(row[2]))
                category_subcategory_list.append((str(row[0]), str(row[1])))

        return category_subcategory_list,words_in_mindmap

    def get_aspect_sentence_new(self, sentence, mindmap):
        sub_category_dict = {}
        words_in_mindmap = []
        category_map_to_subcategory, sub_category_map_to_keyword = mindmap[0], mindmap[1]


        for sub_category in sub_category_map_to_keyword:
            for keyword in sub_category_map_to_keyword[sub_category]:
                if str(keyword) in sentence:
                    words_in_mindmap.append(keyword)
                    sub_category_dict[sub_category] = 1


        if len(sub_category_dict) > 0:
            category_subcategory_list = []
            for category in category_map_to_subcategory:
                for sub_category in sub_category_dict:
                    if sub_category in category_map_to_subcategory[category] :
                        category_subcategory_list.append((category, sub_category))

            return category_subcategory_list, words_in_mindmap
        else:
            return [], []



    def predict_verbatim_aspect(self,verbatim,mind_map):
        verbatim_categories={}
        sentences=verbatim.split(".")
        #to avoid empty scentence at the end ex:"hii python." -->["hii python",''] will be ["hii python"]
        sentences=[s for s in sentences if s!='']
        #add clear sentence function here at the future
        #entences = [clear_sentence(s) for s in sentences]
        words_in_mindmap_per_sentence=[]
        for sentence in sentences:
            #sentence_words=utils.sentence_to_words(sentence)
            categories,words_in_mindmap=self.get_aspect_sentence(sentence,mind_map)
            #s='Issue went on too long before being resolved with unsatisfactory compensation.'
            if len(categories)>0:
                verbatim_categories[sentence]=categories
                words_in_mindmap_per_sentence.append(words_in_mindmap)


        #return dictionary each key is a sentence and each value is the categories of the sentence
        return verbatim_categories,words_in_mindmap_per_sentence


    def predict_verbatim_aspect_old(self,verbatim,mind_map):
        verbatim_categories={}
        sentences=verbatim.split(".")
        #to avoid empty scentence at the end ex:"hii python." -->["hii python",''] will be ["hii python"]
        sentences=[s for s in sentences if s!='']
        for sentence in sentences:
            sentence_words=utils.sentence_to_words(sentence)
            categories=self.get_aspect_sentence(sentence_words,mind_map)
            #s='Issue went on too long before being resolved with unsatisfactory compensation.'
            verbatim_categories[sentence]=list(categories)


        #return dictionary each key is a sentence and each value is the categories of the sentence
        return verbatim_categories






