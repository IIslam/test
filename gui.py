from PyQt5 import uic,QtWidgets,QtCore,QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from functools import partial
import xlrd
import importlib_metadata
import utils
import time

import pandas as pd
import threading
import calendar
import aspect_sentiment_analyzer
import classifier


class getThread(QThread):

    countChanged = pyqtSignal(int)
    messageBoxSignal=pyqtSignal(str,str)
    clearSignal=pyqtSignal()
    disableButtonsSignal=pyqtSignal()

    def run(self):
        self.disableButtonsSignal.emit()
        test_path = input_file_path
        #test_path = "D:/Vodafone Work/Desktop Sentiment Project/Input and Output files Example/IE files/IE Telesales fixed input1.xlsx"

        config_path = 'sentiment_config.ini'
        self.countChanged.emit(5)

        output_file = output_file_path+".csv"
        #output_file = "D:/outputFile.xlsx"

        mindmap_file = mindmap
        #mindmap_file = "D:/Vodafone Work/Desktop Sentiment Project/mindmap/IEmindmap.xlsx"

        import aspect_detector
        self.countChanged.emit(10)
        try:
            analyzer = aspect_detector.AspectDetector(mindmap_file)
            mind_map = analyzer.read_mind_map_new(mindmap_file)
        except:
            self.messageBoxSignal.emit("Error","Failed to read the mind map file")
            self.clear()
            return

        #aspect_detector = aspect_sentiment_analyzer.AspectSentimentAnalyzer()
        self.countChanged.emit(20)
        self.predict_aspect_file(test_path, output_file, mind_map,language)


    def predict_aspect_file(self,inputFilePath, outputFilePath, mindmap,language):
        config_path = 'sentiment_config.ini'
        import pickle
        classifier = pickle.load(open("english_classifier.pickle", 'rb'), fix_imports=True, encoding="latin1")
        print(1)
        try:
            clf = classifier.Classifier(config_path=config_path,language=language)
        except:
            self.messageBoxSignal.emit("Error", "Failed to load the classifier file")
            self.clear()
            return

        #analyzer = aspect_detector.AspectDetector()
        asa = aspect_sentiment_analyzer.AspectSentimentAnalyzer()

        try:
            data, fieldName = utils.read_excel_dict(inputFilePath)
            #data.columns = map(str.lower, data.columns)
        except:
            self.messageBoxSignal.emit("Error","Failed to read the input file")
            self.clear()
            return

        full_df = pd.DataFrame()
        '''
        try:
            verbatim = str(data[0]['verbatim'])
        except:
            self.messageBoxSignal.emit("Error","There is no 'verbatim' column in the input file")
            self.clear()
            return

        try:
            verbatim = str(data[0]['date'])
        except:
            self.messageBoxSignal.emit("Error","There is no 'date' column in the input file")
            self.clear()
            return
        '''
        progress_step = int(len(data) / 80)
        c = 0
        step = 20

        for row in data:
            verbatim = str(row['verbatim'])
            cleaned_verbatim = clf.clean_verbatim(verbatim)
            # return dictionary consist of key as sentences, and value as a tuple consist of category and subcategory

            predicted_categories, words_in_mindmap_per_sentence = asa.predict_verbatim_aspect(verbatim.lower(), mindmap)

            rest_data_frame_columns = pd.DataFrame(row, index=[0])

            rest_data_frame_columns = rest_data_frame_columns.loc[:, rest_data_frame_columns.columns != 'verbatim']

            words_in_mindmap_per_verbatim = utils.change_listoflist_to_list(words_in_mindmap_per_sentence)
            words_in_mindmap_per_verbatim = ','.join(words_in_mindmap_per_verbatim)
            #words_in_mindmap_per_sentence=utils.change_listoflist_to_listofstrings(words_in_mindmap_per_sentence)


            # get month from 'Response Date' Column
            if '/' in str(row['date']):
                date = str(row['date']).split("/")
            elif '-' in str(row['date']):
                date = str(row['date']).split("-")
            else:
                self.messageBoxSignal.emit("Error","Please check date format in the file , it should have '/' or '-' separator")
                self.clear()
                return

            month = calendar.month_name[int(date[1])]
            #mindmap_index=0

            try:
                sentiment, cleaned_sentence = clf.predict_sentence(cleaned_verbatim)
            except:
                self.messageBoxSignal.emit("Error", "Failed to predict sentiment")
                self.clear()
                return

            if len(predicted_categories)>0:

                for sentence in predicted_categories:
                    category_subcategory = predicted_categories[sentence]

                    # check if after cleaning there are still any word in the sentence

                    rest_data_frame_columns['month'] = month
                    rest_data_frame_columns['original verbatim'] = verbatim
                    rest_data_frame_columns['cleaned verbatim'] = cleaned_verbatim
                    rest_data_frame_columns['sentiment'] = sentiment

                    for category, subcategory in category_subcategory:
                        rest_data_frame_columns['category'] = category
                        rest_data_frame_columns['subcategory'] = subcategory

                        #rest_data_frame_columns['words in mindmap'] = words_in_mindmap_per_verbatim + '| ' + words_in_mindmap_per_sentence[mindmap_index]
                        rest_data_frame_columns['words in mindmap'] = words_in_mindmap_per_verbatim
                        full_df = pd.concat([full_df, rest_data_frame_columns], sort=False, axis=0)

            elif cleaned_verbatim!='':
                rest_data_frame_columns['month'] = month
                rest_data_frame_columns['original verbatim'] = verbatim
                rest_data_frame_columns['cleaned verbatim'] = cleaned_verbatim
                rest_data_frame_columns['sentiment'] = sentiment

                rest_data_frame_columns['category'] = "Not Defined"
                rest_data_frame_columns['subcategory'] = "Not Defined"
                rest_data_frame_columns['words in mindmap'] = "No Words"
                full_df = pd.concat([full_df, rest_data_frame_columns], sort=False, axis=0)
                #mindmap_index+=1
            c += 1

            if c % progress_step == 0:
                step += 1
                if step<=99:
                    self.countChanged.emit(step)

        try:
            self.countChanged.emit(100)
            full_df.drop_duplicates(inplace=True)
            full_df.to_csv(outputFilePath, encoding='utf-8', index=False)
            self.messageBoxSignal.emit("Done", "The file was written successfully")
            self.clear()
        except:
            self.messageBoxSignal.emit("Error","Failed to write the file correctly")
            self.clear()
            return


    def clear(self):
        self.countChanged.emit(0)
        self.clearSignal.emit()

class Actions(QDialog):
    defaultFileName='File Name'
    def __init__(self):
        super(Actions, self).__init__()
        self.initUI()

    def initUI(self):
        self.window = uic.loadUi("screen.ui")

        self.window.run.setStyleSheet('''border-image: url("rounded button.png")''')
        '''
        template_css = """QProgressBar::chunk { background: %s; }""" % "red"
        #css = template_css % "red"
        self.window.progressBar.setStyleSheet(template_css)
        '''
        self.window.run.clicked.connect(self.onButtonClick)
        self.window.importFile.clicked.connect(partial(self.upload_file, "file"))
        self.window.importMindmap.clicked.connect(partial(self.upload_file, "mindmap"))
        self.window.extractOutput.clicked.connect(partial(self.upload_file, "output"))

        self.window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.clear()
        self.window.show()

    def onButtonClick(self):
        if self.window.inputFile.toPlainText()==self.defaultFileName:
            self.message_box("Error","Please Choose Input file")

        elif self.window.inputMindmap.toPlainText()==self.defaultFileName:
            self.message_box("Error","Please Choose Mind Map file")

        elif self.window.outputFile.toPlainText()==self.defaultFileName:
            self.message_box("Error","Please Choose Output file")

        else:
            self.calc = getThread()
            self.calc.countChanged.connect(self.change_progress_bar)
            self.calc.messageBoxSignal.connect(self.message_box)
            self.calc.clearSignal.connect(self.clear)
            self.calc.disableButtonsSignal.connect(self.disableButtons)
            self.calc.start()

    def clear(self):
        self.window.inputMindmap.document().setPlainText(self.defaultFileName)
        self.window.inputFile.document().setPlainText(self.defaultFileName)
        self.window.outputFile.document().setPlainText(self.defaultFileName)

        self.window.importFile.setDisabled(False)
        self.window.extractOutput.setDisabled(False)
        self.window.importMindmap.setDisabled(False)
        self.window.run.setDisabled(False)

    def disableButtons(self):
        self.window.importFile.setDisabled(True)
        self.window.extractOutput.setDisabled(True)
        self.window.importMindmap.setDisabled(True)
        self.window.run.setDisabled(True)

    def change_progress_bar(self, value):
            self.window.progressBar.setValue(value)

    def message_box(self,title, text):
        msg = QtWidgets.QMessageBox()
        if title=="Done":
            msg.setIcon(QMessageBox.Information)
        elif title=="Error":
            msg.setIcon(QMessageBox.Critical)

        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        retval = msg.exec_()

        if retval == QtWidgets.QMessageBox.Ok:
            pass
            #window.importFile.setPlainText("Input Fileeee")

    def upload_file(self,state=None):
        global input_file_path
        global mindmap
        global output_file_path
        global language
        try:
            if state == "file":
                input_file_path = self.openFileNameDialog()

                if input_file_path!=None:
                    try:
                        data, fieldName = utils.read_excel_dict(input_file_path)
                        # data.columns = map(str.lower, data.columns)
                    except:
                        self.message_box("Error", "Failed to read the input file")
                        self.clear()
                        return

                    try:
                        verbatim = str(data[0]['verbatim'])
                    except:
                        self.message_box("Error", "There is no 'verbatim' column in the input file")
                        self.clear()
                        return

                    try:
                        verbatim = str(data[0]['date'])
                    except:
                        self.message_box("Error", "There is no 'date' column in the input file")
                        self.clear()
                        return

                    self.window.inputFile.document().setPlainText(input_file_path)
                else:
                    self.window.inputFile.document().setPlainText(self.defaultFileName)

            elif state == "output":
                if self.window.inputFile.toPlainText()==self.defaultFileName:
                    self.message_box("Error","Please choose Input file before choosing the Output File")
                elif self.window.inputMindmap.toPlainText()==self.defaultFileName:
                    self.message_box("Error","Please choose Mind Map file before choosing the Output File")
                else:
                    output_file_path = self.saveFileDialog()
                    self.window.outputFile.document().setPlainText(output_file_path+".csv")
                    language=self.get_language().lower()
            elif state == "mindmap":
                if self.window.inputFile.toPlainText()==self.defaultFileName:
                    self.message_box("Error","Please choose input file before choosing the Mind Map File")
                else:
                    mindmap = self.openFileNameDialog()

                    if self.get_language() not in mindmap.split("/")[-1].lower():
                        self.message_box("Error", "Please choose mindmap for {:} language".format(self.get_language()))
                    else:
                        self.window.inputMindmap.document().setPlainText(mindmap)

        except:
            self.message_box("Error", "Failed to upload the file, please check that the input file is Excel")


    def openFileNameDialog(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(window, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return fileName

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(window, "QFileDialog.getSaveFileName()", "",
                                                  "Excel Files (*.csv);;All Files (*)", options=options)
        if fileName:
            return fileName

    def get_language(self):
        return str(self.window.langList.currentText()).lower()


if __name__ == '__main__':
    input_file_path = output_file_path = mindmap = ""
    app = QtWidgets.QApplication([])
    window=Actions()
    app.exec_()
