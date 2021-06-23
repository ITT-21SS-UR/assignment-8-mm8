import pathlib
from enum import Enum
from pyqtgraph.flowchart import Node
from pyqtgraph.Qt import QtGui
import pandas as pd
from sklearn import svm


class Mode(Enum):
    INACTIVE = "Inactive"
    TRAIN = "Train"
    PREDICT = "Predict"


# noinspection PyAttributeOutsideInit
class ClassifierNode(Node):
    """
    Contains a svm classifier that trains on the given input data and tries to predict a pre-defined activity;
    Current Mode can be switched between training and predicting; an activity name can be specified with whom the
    currently trained data is associated with.
    """
    nodeName = "ClassifierNode"

    def __init__(self, name):
        terminals = {
            'valX': dict(io='in'),
            'valY': dict(io='in'),
            'valZ': dict(io='in'),
            'prediction': dict(io='out'),
        }

        self.__log_folder = "recorded_actions/"
        self.__log_file_path = pathlib.Path(self.__log_folder + "/recording.csv")
        self.__recording_active = False
        self.__activity_name = ""

        self.__recorded_data_X = []
        self.__recorded_data_Y = []
        self.__recorded_data_Z = []
        self.__recorded_data = []  # avg of the 3 input values
        self.__predicted_action = "Unknown"

        self.classifier = svm.SVC()

        self.__init_record_log()
        self._init_ui()

        Node.__init__(self, name, terminals=terminals)

    def __init_record_log(self):
        folder_path = pathlib.Path(self.__log_folder)
        if not folder_path.is_dir():
            folder_path.mkdir()

        # check if the file already exists
        if self.__log_file_path.exists():
            # load existing recordings
            self.existing_activity_data = pd.read_csv(self.__log_file_path, sep=";")
            # TODO load from csv with genfromtxt
        else:
            # or create a new csv if no exist
            self.existing_activity_data = pd.DataFrame(columns=['activity', 'data'])

    def _save_recorded_data(self):
        # TODO save separate ones for X, Y and Z too?
        new_recording = {'activity': self.__activity_name, 'data': self.__recorded_data}
        # TODO or append directly to the activity if it exists in the df ?
        self.existing_activity_data = self.existing_activity_data.append(new_recording, ignore_index=True)
        self.existing_activity_data.to_csv(self.__log_file_path, sep=";", index=False)

    def _init_ui(self):
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        label = QtGui.QLabel("Mode:")
        self.layout.addWidget(label)
        # create a selection box for the current mode ("inactive", "train" or "predict")
        self.mode_selection = QtGui.QComboBox()
        self.mode_selection.addItems([Mode.INACTIVE.value, Mode.TRAIN.value, Mode.PREDICT.value])
        self.mode_selection.currentIndexChanged.connect(self.mode_changed)
        self.layout.addWidget(self.mode_selection)
        self.current_mode = Mode.INACTIVE.value  # initially we start in the "inactive" mode

        instruction_label = QtGui.QLabel("With the selection box above you can choose the mode of the classifier.\n"
                                         "If mode is \"Train\" you can start recording a sequence of accelerometer "
                                         "values by clicking on the button \"Start recording\". By clicking the button"
                                         " again the recording is stopped After you have recorded some data and "
                                         "entered a name (i.e. a label) for this activity the recorded data will be "
                                         "saved in a csv and the classifier will be trained with the recorded data.\n"
                                         "If mode is \"Predict\" you can start recording your accelerometer values as "
                                         "well but this time when you stop the recorded data will be used to predict "
                                         "the activity you most likely performed based on existing activities. The "
                                         "prediction result is displayed in the DisplayTextNode.")
        instruction_label.setWordWrap(True)
        self.layout.addWidget(instruction_label)

        # setup the two uis for training and predicting but hide them at the start as we start in "inactive mode"
        self.setup_training_ui()
        self.setup_prediction_ui()
        self.training_ui.hide()
        self.prediction_ui.hide()

        self.ui.setLayout(self.layout)

    def setup_training_ui(self):
        self.training_ui = QtGui.QFrame()
        training_layout = QtGui.QVBoxLayout()

        self.activity_name_input = QtGui.QLineEdit()
        self.activity_name_input.setPlaceholderText("Enter the name of the activity you are going to record, "
                                                    "e.g. \"Running\"")
        self.activity_name_input.textEdited.connect(self.on_activity_name_changed)  # listen to edit text changes
        training_layout.addWidget(self.activity_name_input)

        training_button_layout = QtGui.QHBoxLayout()
        self.train_button = QtGui.QPushButton("Start recording")
        self.train_button.setStyleSheet("QPushButton {background-color: rgb(120, 206, 63)};")
        self.train_button.clicked.connect(self.toggle_train_recording)
        training_button_layout.addWidget(self.train_button)

        self.save_button = QtGui.QPushButton("Save recording")
        self.save_button.setStyleSheet("QPushButton {background-color: rgb(223, 183, 20)};")
        self.save_button.clicked.connect(self.finish_training_recording)
        self.save_button.setEnabled(False)  # disable button at first
        training_button_layout.addWidget(self.save_button)

        training_layout.addLayout(training_button_layout)

        self.train_text_field = QtGui.QTextEdit()
        self.train_text_field.setReadOnly(True)  # make output field readonly
        training_layout.addWidget(self.train_text_field)

        self.training_ui.setLayout(training_layout)
        self.layout.addWidget(self.training_ui)

    def setup_prediction_ui(self):
        self.prediction_ui = QtGui.QFrame()
        prediction_layout = QtGui.QVBoxLayout()

        self.predict_button = QtGui.QPushButton("Start predicting")
        self.predict_button.setStyleSheet("QPushButton {background-color: rgb(120, 206, 63)};")
        self.predict_button.clicked.connect(self.toggle_prediction_recording)
        prediction_layout.addWidget(self.predict_button)

        self.predict_text_field = QtGui.QTextEdit()
        self.predict_text_field.setReadOnly(True)
        prediction_layout.addWidget(self.predict_text_field)

        self.prediction_ui.setLayout(prediction_layout)
        self.layout.addWidget(self.prediction_ui)

    def on_activity_name_changed(self, new_text):
        self.__activity_name = new_text

    def mode_changed(self, index):
        self.current_mode = self.mode_selection.currentText()
        print(f"Current index {index}; selection changed {self.current_mode}")

        if self.current_mode == Mode.TRAIN.value:
            # reset data when switching from train to predict and vice versa
            self.reset_recorded_data()
            # and show the correct ui
            self.show_training_ui()
        elif self.current_mode == Mode.PREDICT.value:
            self.reset_recorded_data()
            self.show_prediction_ui()
        elif self.current_mode == Mode.INACTIVE.value:
            self.training_ui.hide()
            self.prediction_ui.hide()
        else:
            print(f"Mode {self.current_mode} not known!")

    def reset_recorded_data(self):
        self.__recorded_data_X.clear()
        self.__recorded_data_Y.clear()
        self.__recorded_data_Z.clear()
        self.__recorded_data.clear()

    def show_training_ui(self):
        self.save_button.setEnabled(False)  # disable save button again in case we switched back from other mode
        self.activity_name_input.clear()
        self.train_text_field.clear()

        self.prediction_ui.hide()
        self.training_ui.show()

    def show_prediction_ui(self):
        self.predict_text_field.clear()
        # show which activities were already recorded:
        existing_activities = self.existing_activity_data.activity.unique()
        self.predict_text_field.setHtml(f"Existing recorded activities: {existing_activities}")

        self.training_ui.hide()
        self.prediction_ui.show()

    def toggle_train_recording(self):
        if self.__recording_active:
            # stop recording
            self.__recording_active = False
            self.train_button.setText("Start recording")
            self.train_text_field.setHtml(f"{self.get_current_output_text()}\nStopped recording.")

            self.save_button.setEnabled(True)  # enable the save and train button
        else:
            # start recording
            self.__recording_active = True
            self.train_button.setText("Stop recording")
            self.train_text_field.setHtml(f"{self.get_current_output_text()}\nRecording new train data...")

    def finish_training_recording(self):
        # check if a name has been entered; in python empty strings are false which is why the following works:
        if not self.__activity_name:
            self.train_text_field.setHtml(f"{self.get_current_output_text()}\n"
                                          f"<b>You have to enter a name for the recorded activity!</b>")
            return

        self.train_text_field.setHtml("Saving recorded data...")
        self._save_recorded_data()

        # do the actual training of the classifier
        self.train_text_field.setHtml(f"{self.get_current_output_text()}\nTraining classifier...")
        self.train_classifier()
        self.train_text_field.setHtml(f"{self.get_current_output_text()}\n<b>Finished training!</b>")

    def train_classifier(self):
        # TODO classifier training stuff
        pass

    def toggle_prediction_recording(self):
        if self.__recording_active:
            self.__recording_active = False
            self.predict_button.setText("Start recording")
            self.predict_text_field.setHtml(f"{self.get_current_output_text()}\nStopped recording.")

            # predict the most likely activity for the given time-series data
            self.predict_activity()
        else:
            self.__recording_active = True
            self.predict_button.setText("Stop recording")
            self.predict_text_field.setHtml(f"{self.get_current_output_text()}\nRecording data for prediction...")

    def predict_activity(self):
        # self.__predicted_action = self.classifier.predict(self.__recorded_data)  # TODO
        self.predict_text_field.setHtml(f"{self.get_current_output_text()}\n<b>Predicted action!</b>")

    def get_current_output_text(self):
        if self.current_mode == Mode.TRAIN.value:
            return self.train_text_field.toHtml()
        elif self.current_mode == Mode.PREDICT.value:
            return self.predict_text_field.toHtml()
        else:
            return ""

    def ctrlWidget(self):
        return self.ui

    def process(self, **kwds):
        if self.__recording_active:
            # only read in new data during recording phase
            input_x = kwds["valX"]
            input_y = kwds["valY"]
            input_z = kwds["valZ"]
            input_avg = (input_x + input_y + input_z) / 3

            self.__recorded_data_X.extend(input_x)
            self.__recorded_data_Y.extend(input_y)
            self.__recorded_data_Z.extend(input_z)
            self.__recorded_data.extend(input_avg)

        return {'prediction': self.__predicted_action}
