import aspect_detector,aspect_sentiment_analyzer
import classifier

import utils

if __name__ == "__main__":

    ROOT_DIR = utils.get_parent_root()
    trainFile = "sentimentDataCsv.csv"
    train_path = trainFile
    config_path = 'sentiment_config.ini'
    cf = classifier.Classifier(config_path)

    analyzer =aspect_detector.AspectDetector()
    mind_map=analyzer.mind_map
    aspect_sentiment_analyzer=aspect_sentiment_analyzer.AspectSentimentAnalyzer()
    #verbatim='Issue went on too long before being resolved with unsatisfactory compensation.'

    #test_path = os.path.join(ROOT_DIR, "Copy of Digital Input.csv")
    test_path="D:/Vodafone Work/Desktop Sentiment Project/Input and Output files Example/IE files/IE Telesales fixed input.xls"
    output_path="output-aspect_new.csv"
    aspect_sentiment_analyzer.predict_aspect_file(test_path,output_path,mind_map)


