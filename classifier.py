import utils
import re
import pickle
import sklearn
class Classifier:
    def __init__(self,config_path=None,train_path=None,model_path = None,language='english' ,model_type= 'ML'):

        self.options = utils.read_options(config_path, "classifier options")
        #print(self.options)
        self.model_type = model_type if model_type != None else self.options['classifier']
        #print(self.model_type)
        #model_path = model_path if (model_path != None) else self.options['model_path']
        #print(model_path)
        self.load_classifier(language)

    def cleanData(self,features):
        processed_features = []
        # this condition is for the testing one scentence
        if type(features)==str:
            features=[features]

        for sentence in range(0, len(features)):
            # Remove all the special characters
            processed_feature = re.sub(r'\W', ' ', str(features[sentence]))

            # Remove all single characters
            processed_feature = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_feature)

            # Remove single characters from the start
            processed_feature = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_feature)

            # Substituting multiple spaces with single space
            processed_feature = re.sub(r'\s+', ' ', processed_feature, flags=re.I)

            # Removing prefixed 'b'
            processed_feature = re.sub(r'^b\s+', '', processed_feature)

            # Remove white spaces
            processed_feature = processed_feature.strip()

            # Converting to Lowercase
            processed_feature = processed_feature.lower()


            processed_features.append(processed_feature)


        return processed_features


    def cleanSentence(self,sentence):

        # Converting to Lowercase
        sentence = sentence.lower()

        # Remove all the special characters
        sentence = re.sub(r'\W', ' ', sentence)

        # Remove all the numbers
        sentence = re.sub(r'\d', ' ', sentence)

        # Remove all single characters
        sentence = re.sub(r"\b[a-zA-Z]\b", "", sentence)

        # Substituting multiple spaces with single space
        sentence = re.sub(r'\s+', ' ', sentence, flags=re.I)

        # Remove some keywords from the verbatim
        sentence = re.sub(r"no verbatim", '', sentence)
        sentence = re.sub(r"no time", '', sentence)
        sentence = re.sub(r" busy ", '', sentence)
        sentence = re.sub(r" no ", '', sentence)
        sentence = re.sub(r"no comments", '', sentence)

        # Remove white spaces
        sentence = sentence.strip()

        return sentence
    def clean_verbatim(self,verbatim):
        verbatim=utils.removeUnnecessaryDots(verbatim)
        # Converting to Lowercase
        verbatim = verbatim.lower()

        # Remove all single characters
        verbatim = re.sub(r"\b[a-zA-Z]\b", "", verbatim)

        # Substituting multiple spaces with single space
        verbatim = re.sub(r'\s+', ' ', verbatim, flags=re.I)

        # Remove some keywords from the verbatim
        verbatim = re.sub(r"no verbatim", '', verbatim)
        verbatim = re.sub(r"no time", '', verbatim)
        verbatim = re.sub(r" busy ", '', verbatim)
        verbatim = re.sub(r" no ", '', verbatim)
        verbatim = re.sub(r"no comments", '', verbatim)

        # Remove white spaces
        verbatim = verbatim.strip()

        return verbatim


    def get_vectorized_data(self, data, train):
        dataset = self.cleanData(data)
        # self.export_dataset(dataset)
        if train:
            arr = self.vectorizer.fit_transform(dataset).toarray()
        else:
            arr = self.vectorizer.transform(dataset).toarray()
        return arr


    def load_classifier(self,language):

        classifier_path = language+"_classifier.pickle"
        vectorizer_path = language+"_vectorizer.pickle"
        #print("FN:",fileName)


        self.classifier = pickle.load(open(classifier_path,'rb'), fix_imports=True, encoding="latin1")

        self.vectorizer = pickle.load(open(vectorizer_path,'rb'), fix_imports=True, encoding="latin1")



    def predict_sentence(self, sentence):
        cleanedSentence=self.cleanSentence(sentence)
        test_setX = self.get_vectorized_data([cleanedSentence], False)
        predicted = self.classifier.predict(test_setX)
        return predicted[0],cleanedSentence