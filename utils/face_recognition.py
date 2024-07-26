from deepface import DeepFace

def verify_faces(img1_path, img2_path):
    output = DeepFace.verify(img1_path, img2_path)
    return output['verified']
