from inference_sdk import InferenceHTTPClient

class FacialFeatureExtraction:

    def __init__(self, image_path):
        self.image_path = image_path

    def get_face_shape_model_prediction(self):

        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="ZIDMQRofZidTcNj0gedC"
        )
        
        result = CLIENT.infer(self.image_path, model_id="face-shape-detection/1")
        return result
    
    def get_face_shape_prediction(self):

        face_shape_api_results = self.get_face_shape_model_prediction()['predictions'][0]['class']
        return face_shape_api_results
    

    def get_gender_model_prediction(self):

        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="ZIDMQRofZidTcNj0gedC"
        )

        result = CLIENT.infer(self.image_path, model_id="gender-rkppz/1")
        return result
    
    def get_gender_prediction(self):

        person_gender_api_results = self.get_gender_model_prediction()['predictions'][0]['class']
        return person_gender_api_results
    

    def get_skintone_model_prediction(self):

        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="ZIDMQRofZidTcNj0gedC"
        )

        result = CLIENT.infer(self.image_path, model_id="facial-structure/5")

        return result

    def get_skintone_prediction(self):

        skintone_prediction_list = []
        for data in range(len(self.get_skintone_model_prediction()['predictions'])):
            skintone_prediction_list.append(self.get_skintone_model_prediction()['predictions'][data]['class'])

        if 'Light-Tone' or 'Medium-Tone' or 'Normal-Skin' or 'Oily-Skin' in skintone_prediction_list:
            return 'light'
        else:
            return 'Dark'

    def get_facial_features(self):

        facial_features = {

            'gender_prediction' : self.get_gender_prediction().lower(),
            'face_shape_prediction' : self.get_face_shape_prediction().lower(),
            'skintone_prediction' : self.get_skintone_prediction().lower()
        }

        return facial_features
    
    def initiate_facial_feature_extraction(self):
        return self.get_facial_features()
        

    

    
    
    


