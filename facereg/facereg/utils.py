import cv2 
import os
from profiles.models import Profile

path = 'D:\\computer-vision-project\\assignment\\facereg\\facereg\\output'

"""
function for comparing histogram of two faces
"""
def compare_histograms(imageA, imageB, method='correlation'):
    # convert color to HSV for comparing more easily
    imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2HSV)
    imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2HSV)
    # compute histogram
    histA = cv2.calcHist([imageA], [0, 1], None, [50, 60], [0, 180, 0, 256])
    histB = cv2.calcHist([imageB], [0, 1], None, [50, 60], [0, 180, 0, 256])
    # standardize histogram
    cv2.normalize(histA, histA, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(histB, histB, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    # fomulars to compare the similarity of two faces
    methods = {
        'correlation': cv2.HISTCMP_CORREL,
        'chi-square': cv2.HISTCMP_CHISQR,
        'bhattacharyya': cv2.HISTCMP_BHATTACHARYYA
    }

    comparison = cv2.compareHist(histA, histB, methods[method])
    return comparison

"""
hàm lấy ra khuôn mặt
"""
def extract_face(img):    
    # looking for the face in the image 
    try:
        image = cv2.imread(img)
        # model 
        face_cascade = cv2.CascadeClassifier('D:\\computer-vision-project\\assignment\\.venv\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_alt2.xml')
        # convert to gray image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.1, 4) 
    except:
        pass
    
    # draw a rectangle around the face and save in jpg format
    for (x, y, w, h) in faces: 
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2) 
        faces = image[y:y + h, x:x + w] 
        cv2.imwrite(os.path.join(path, 'face2.jpg'), faces) 

"""
function for comparing the image taken by webcam of the user 
then comparing to each image is already saved in the database
"""
def classify_face(img):
    # read image taken by webcam
    image = cv2.imread(img) 
    # convert to gray image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    # haarcascade model
    face_cascade = cv2.CascadeClassifier('C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml') 
    # find the face in the image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4) 
    
    # draw a rectangle around the face and save in jpg format
    for (x, y, w, h) in faces: 
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2) 
        faces = image[y:y + h, x:x + w] 
        cv2.imwrite(os.path.join(path, 'face1.jpg'), faces) 
   
    # return false if the model cannot find any face in the image
    if (len(faces) == 0):
        return False
    
    # initialize best_match as the output
    # the higher best_match the more similar in faces 
    best_match = 0
    # initialize name variable for returning username that match in the database
    name = ''
    # traverse through all images in the databse
    qs = Profile.objects.all()
    
    for p in qs:
        photoPath = str(p.photo.path)
        extract_face(photoPath)
        imageA = cv2.imread(str(path) + '\\face1.jpg')
        imageB = cv2.imread(str(path) + '\\face2.jpg')
        hist_score = compare_histograms(imageA, imageB, method='correlation')
        
        if (hist_score > best_match):
            best_match = hist_score
            name = p.user.username
        print(best_match)
        
    if (best_match >= 0.7):
        print(best_match)
        return name
    
    return False
