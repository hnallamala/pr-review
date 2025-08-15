from src.components.facial_feature_extraction import *
from src.components.glasses_recommendation import *
from PIL import Image


image_path = "test/hari-images.jpg"

img = Image.open(image_path)
img.show()

facial_feature_extraction_object = FacialFeatureExtraction(image_path)
print(facial_feature_extraction_object.initiate_facial_feature_extraction())
glasses_recommendation_object = GlassesRecommendationSystem(image_path)
print(glasses_recommendation_object.get_glasses_recommendation())
glasses_recommendation_object.display_glasses_recommendations()