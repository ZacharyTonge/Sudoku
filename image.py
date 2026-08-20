import cv2
import numpy as np
from keras.models import load_model

model = load_model('model.keras', compile=False)

def scaleAndCentre(img, size, margin=0, background=0):
	# Scales and centres an image onto a new background square
	h, w = img.shape[:2]

	def centre_pad(length):
		# Handles centering for a given length that may be odd or even
		if length % 2 == 0:
			side1 = int((size - length) / 2)
			side2 = side1
		else:
			side1 = int((size - length) / 2)
			side2 = side1 + 1
		return side1, side2

	def scale(r, x):
		return int(r * x)

	if h > w:
		t_pad = int(margin / 2)
		b_pad = t_pad
		ratio = (size - margin) / h
		w, h = scale(ratio, w), scale(ratio, h)
		l_pad, r_pad = centre_pad(w)
	else:
		l_pad = int(margin / 2)
		r_pad = l_pad
		ratio = (size - margin) / w
		w, h = scale(ratio, w), scale(ratio, h)
		t_pad, b_pad = centre_pad(h)

	img = cv2.resize(img, (w, h))
	img = cv2.copyMakeBorder(img, t_pad, b_pad, l_pad, r_pad, cv2.BORDER_CONSTANT, None, background)
	return cv2.resize(img, (size, size))

def predict(img):
    image = img.copy()

    image = cv2.resize(image, (28, 28))

    image = image.astype('float32') / 255.0

    prediction = model.predict(image.reshape(1, 28, 28, 1), batch_size=1)

    return prediction.argmax()

def preProcessImage(image): 
    blurredImage = cv2.GaussianBlur(image.copy(), (9, 9), 0)
    segmenetedBlurredImage = cv2.adaptiveThreshold(blurredImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    invertedSegmenetedBlurredImage = cv2.bitwise_not(segmenetedBlurredImage, segmenetedBlurredImage)
    kernel = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]], np.uint8)
    dilatedInvertedSegmentedBlurredImage = cv2.dilate(invertedSegmenetedBlurredImage, kernel)

    # cv2.imwrite(f'images/numbers/test/preprocessed.png', dilatedInvertedSegmentedBlurredImage)

    return dilatedInvertedSegmentedBlurredImage


def warpAndCropSudokuImage(img): 
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # img = cv2.imread('C:\\Users\\zacha\\Projects\\Sudoku\\images\\EasySudokuImage.png')
    # highlightedContourImage = cv2.drawContours(dilatedInvertedSegmentedBlurredImage, contours, -1, (0, 255, 0), 2)

    corners = None;
    for c in contours:
        perimiter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * perimiter, True)
        if len(approx) == 4:
            # Here we are looking for the largest 4 sided contour
            corners = approx
            break
        
    corners = [(corner[0][0], corner[0][1]) for corner in corners]
    topRightCoordinnate, topLeftCoordinate, bottomLeftCoordinate, bottomRightCoordinate = corners[0], corners[1], corners[2], corners[3]

    # Perform pythagorous theorem incase corners aren't vertically aligned
    widthA = np.sqrt(((bottomRightCoordinate[0] - bottomLeftCoordinate[0]) ** 2) + ((bottomRightCoordinate[1] - bottomLeftCoordinate[1]) ** 2))
    widthB = np.sqrt(((topRightCoordinnate[0] - topLeftCoordinate[0]) ** 2) + ((topRightCoordinnate[1] - topLeftCoordinate[1]) ** 2))
    width = max(int(widthA), int(widthB))

    heightA = np.sqrt(((topRightCoordinnate[0] - bottomRightCoordinate[0]) ** 2) + ((topRightCoordinnate[1] - bottomRightCoordinate[1]) ** 2))
    heightB = np.sqrt(((topLeftCoordinate[0] - bottomLeftCoordinate[0]) ** 2) + ((topLeftCoordinate[1] - bottomLeftCoordinate[1]) ** 2))
    height = max(int(heightA), int(heightB))

    dimensions = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1],
                        [0, height - 1]], dtype="float32")
    # Convert to Numpy format
    # prespectiveTransform wants coordinates in order (topleft, topright, bottomright, bottomleft)
    orderedCornersForTransform = [corners[0], corners[3], corners[2], corners[1]];
    orderedCornersForTransform = np.array(orderedCornersForTransform, dtype="float32")

    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    transformations = cv2.getPerspectiveTransform(orderedCornersForTransform, dimensions)
    croppedImage = cv2.warpPerspective(img, transformations, (width, height))

    # cv2.imwrite(f'images/numbers/test/croppedImage.png', croppedImage)

    return croppedImage


def splitImageIntoCells(img):
    sudokuHeight = np.shape(img)[0]
    sudokuWidth = np.shape(img)[1]
    cellHeight = sudokuHeight // 9
    cellWidth = sudokuWidth // 9

    tempgrid = []
    for i in range(cellHeight, sudokuHeight + 1, cellHeight):
        for j in range(cellWidth, sudokuWidth + 1, cellWidth):
            rows = img[i - cellHeight:i]
            tempgrid.append([rows[k][j - cellWidth:j] for k in range(len(rows))])

    # Creating the 9X9 grid of images
    finalgrid = []
    # 81 cells and starts on iteration 0 so -8 so it only loops 9 times (i.e. 9 grids)
    for i in range(0, len(tempgrid) - 8, 9):
        finalgrid.append(tempgrid[i:i + 9])

    # Converting all the cell images to np.array
    for i in range(9):
        for j in range(9):
            finalgrid[i][j] = np.array(finalgrid[i][j])

    return finalgrid



def extractSudokuCellValues(grid):
    predictedSudoku = [[None for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):

            thresh = 128  # 128 is the middle of black and white in grey scale so anything above 128 goes black and anything below goes white
            gray = cv2.threshold(grid[i][j], thresh, 255, cv2.THRESH_BINARY)[1]

            # Finds contours meaning the outside coordinates of any shapes, third arguments just condenses coordinates
            # i.e. instead of (0, 1), (0, 2), (0,3) becomes (0, 1) to (0, 3)
            # Use RETR_LIST instead of RETR_EXTERNAL as the latter will only take outermost contour, 
            # so if a number was fully enclosed by lines, it would ignore the number and just take the outermost contour 
            cnts = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            # Grab the first as findContours returns (contours, hierachy)
            cnts = cnts[0] 

            valid = []
            for c in cnts:
                # Find the outermost coordinates to create a rectangle around the shape
                x, y, w, h = cv2.boundingRect(c)

                # If the shape starts to close to edge (left) or is very thin (i.e. a line on the right), ignore
                if x < 10 or y < 10 or w < 10 or h < 10:
                    continue

                valid.append(c)

            # No shape within the middle found, probably empty
            if not valid:
                continue

            # Of all found shapes assume the largest one is the number
            c = max(valid, key=cv2.contourArea)

            # Encapsulate the number by its outermost coordinates and crop 
            x, y, w, h = cv2.boundingRect(c)

            # Region of interest
            ROI = gray[y:y + h, x:x + w]
            
            # increasing the size of the number allws for better interpreation,
            # try adjusting the number and you will see the differnce
            ROI = scaleAndCentre(ROI, 120)

            prediction = predict(ROI)
            
            predictedSudoku[i][j] = prediction

            # cv2.imwrite(f'images/numbers/test/{i}{j}.png', ROI)

        
    return predictedSudoku

def extractSudoku(imgLocation):
    img = cv2.imread(imgLocation, cv2.IMREAD_GRAYSCALE)

    if (img is None):
        raise Exception("Image path not found")
    
    processedImage = preProcessImage(img)

    extractedSudokuImage = warpAndCropSudokuImage(processedImage)

    extractedCells = splitImageIntoCells(extractedSudokuImage)

    finalSudoku = extractSudokuCellValues(extractedCells)

    return finalSudoku