function ret = calibrate(file)
    numImages = 7;
    squareSize = 100;
    
    files = cell(1, numImages);
    for i = 1:numImages
        files{i} = sprintf('calibrate/calibrate0%d.jpg', i);
    end
    files{7} = file;
    
    [imagePoints, boardSize] = detectCheckerboardPoints(files);
    worldPoints = generateCheckerboardPoints(boardSize, squareSize);
    I = imread(files{1});
    imageSize = [size(I, 1), size(I, 2)];
    cameraParams = estimateCameraParameters(imagePoints, worldPoints, 'ImageSize', imageSize);
    
    save('temp/cameraParams.mat', 'cameraParams')
    ret = 2;
end
