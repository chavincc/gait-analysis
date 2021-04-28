function distance = measure(x1, y1, x2, y2, option)
    load('temp/R.mat', 'R');
    load('temp/t.mat', 't');
    load('temp/cameraParams.mat', 'cameraParams');
    
    worldPoints1 = pointsToWorld(cameraParams, R, t, [x1, y1]);
    worldPoints2 = pointsToWorld(cameraParams, R, t, [x2, y2]);
    
    d = worldPoints1 - worldPoints2;
    
    if option == 0
        distance = hypot(d(1), d(2));
    elseif option == 1
        distance = d(1);
    elseif option == 2
        distance = d(2);
    end
end