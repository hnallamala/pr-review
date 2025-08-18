from src.components.facial_feature_extraction import *
import pandas as pd
import random
import matplotlib.pyplot as plt
from PIL import Image
import logging

class GlassesRecommendationSystem:

    def __init__(self, image_path):
        self.facial_feature_extraction_object = FacialFeatureExtraction(image_path=image_path)
        self.dataset_path = "src/data/product.csv"

    def get_facial_features(self):
        return self.facial_feature_extraction_object.initiate_facial_feature_extraction()
    
    def get_glasses_recommendation(self):
        
        predictions = self.get_facial_features()
        df = pd.read_csv(self.dataset_path)

        filtered_df = df[
                (df['gender'].str.lower() == predictions['gender_prediction'].lower()) &
                (df['face_shape'].str.lower() == predictions['face_shape_prediction'].lower()) &
                (df['skin'].str.lower() == predictions['skintone_prediction'].lower())
            ]

        image_src_list = filtered_df['image_src'].tolist()
        random_image_paths = random.sample(image_src_list, min(len(image_src_list), 5))
        logging.info('',random_image_paths)

        return random_image_paths

    def display_glasses_recommendations(self):

        glasses_prediction_list = self.get_glasses_recommendation()

        for image_path in glasses_prediction_list:
            img = Image.open(image_path)
            img.show()

