function ret = detectChessBoard(squareSize, file)
    load('temp/cameraParams.mat', 'cameraParams');
%     cameraParams = cameraParameters;
    imOrig = imread(file);
    [im, newOrigin] = undistortImage(imOrig, cameraParams, 'OutputView', 'full');
    [imagePoints, boardSize] = detectCheckerboardPoints(im);
    imagePoints = imagePoints + newOrigin;
    save('temp/imagePoints.mat', 'imagePoints');
    ret = 0;
    
    if (boardSize(1) + boardSize(2) ~= 0)
        ret = 1;
        worldPoints = generateCheckerboardPoints(boardSize, squareSize);
        [R, t] = extrinsics(imagePoints, worldPoints, cameraParams);  
        
        savePointsToCsv(boardSize, 'temp/boardSize.csv');
        savePointsToCsv(worldPoints, 'temp/wp.csv');
        savePointsToCsv(imagePoints, 'temp/ip.csv');
        save('temp/boardSize.mat', 'boardSize');
        save('temp/R.mat', 'R');
        save('temp/t.mat', 't');
        
%       gen transformed point (tp)
        [x, y] = size(imagePoints);
        TPCell = cell(x, y);
        for i = 1:x
            out = pointsToWorld(cameraParams, R, t, [imagePoints(i, 1), imagePoints(i, 2)]);
            TPCell{i, 1} = out(1);
            TPCell{i, 2} = out(2);
        end
        T = cell2table(TPCell, 'VariableNames', {'x', 'y'});
        writetable(T, 'temp/tp.csv');
    end
end
