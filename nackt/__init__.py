import numpy as np
import cv2

SIMILARITY_CONSTANT = 50


def get_skin_color(image):
    cnt = []
    for i in range(256):
        array2d = []
        for j in range(256):
            array1d = []
            for k in range(256):
                array1d.append(0)
            array2d.append(array1d)
        cnt.append(array2d)
    rows, columns, tmp = image.shape
    for row in range(rows):
        for column in range(columns):
            r = image[row][column][0]
            g = image[row][column][1]
            b = image[row][column][2]

            r1 = max(0, r - SIMILARITY_CONSTANT)
            g1 = max(0, g - SIMILARITY_CONSTANT)
            b1 = max(0, b - SIMILARITY_CONSTANT)
            r2 = min(255, r + SIMILARITY_CONSTANT)
            g2 = min(255, g + SIMILARITY_CONSTANT)
            b2 = min(255, b + SIMILARITY_CONSTANT)
            cnt[r1][g1][b1] += 1
            cnt[r1][g1][b2] -= 1
            cnt[r1][g2][b1] -= 1
            cnt[r1][g2][b2] += 1
            cnt[r2][g1][b1] -= 1
            cnt[r2][g1][b2] += 1
            cnt[r2][g2][b1] += 1
            cnt[r2][g2][b2] -= 1
    answer = (0, 0, 0)
    for r in range(256):
        for g in range(256):
            for b in range(256):
                if b > 0:
                    cnt[r][g][b] += cnt[r - 0][g - 0][b - 1]
                if g > 0:
                    cnt[r][g][b] += cnt[r - 0][g - 1][b - 0]
                if g > 0 and b > 0:
                    cnt[r][g][b] -= cnt[r - 0][g - 1][b - 1]
                if r > 0:
                    cnt[r][g][b] += cnt[r - 1][g - 0][b - 0]
                if r > 0 and b > 0:
                    cnt[r][g][b] -= cnt[r - 1][g - 0][b - 1]
                if r > 0 and g > 0:
                    cnt[r][g][b] -= cnt[r - 1][g - 1][b - 0]
                if r > 0 and g > 0 and b > 0:
                    cnt[r][g][b] += cnt[r - 1][g - 1][b - 1]
                if cnt[answer[0]][answer[1]][answer[2]] < cnt[r][g][b]:
                    answer = (r, g, b)
    return answer


def is_similar(r1, g1, b1, r2, g2, b2):
    return abs(r1 - r2) < SIMILARITY_CONSTANT and abs(g1 - g2) < SIMILARITY_CONSTANT and abs(b1 - b2) < SIMILARITY_CONSTANT


def paint(image, stc, fic):
    rows, columns, tmp = image.shape
    for row in range(rows):
        for column in range(columns):
            if is_similar(stc[0], stc[1], stc[2], image[row][column][0], image[row][column][1], image[row][column][2]):
                cv2.rectangle(image, (column, row), (column, row), fic)


def get_nudity(image, skin_color):
    rows, columns, tmp = image.shape
    area = 0.0
    for row in range(rows):
        for column in range(columns):
            if is_similar(skin_color[0], skin_color[1], skin_color[2], image[row][column][0], image[row][column][1], image[row][column][2]):
                area += 1.0
    return area / (rows * columns)


face_cascade = cv2.CascadeClassifier('xmls/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('xmls/haarcascade_eye.xml')

img = cv2.imread('tests/true_08.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = face_cascade.detectMultiScale(gray, 1.3, 5)
skin_color = (1000, 1000, 1000)
for (x, y, w, h) in faces:
    face = img[y:y + h, x:x + w]
    skin_color = get_skin_color(face)
    upper_body = img[y + h:y + h + 3 * h, x - w / 2:x + w + w / 2]
    nudity = get_nudity(upper_body, skin_color)
    print(nudity)
    if nudity > 0.5:
        print('Nude picture!')

paint(img, skin_color, (255, 0, 0))

cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
