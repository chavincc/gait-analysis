function savePointsToCsv(points, file)
    [x, y] = size(points);
    IPCell = cell(x, y);
    for i = 1:x
        for j = 1:y
            IPCell{i,j} = points(i,j);
        end
    end

    T = cell2table(IPCell, 'VariableNames', {'x', 'y'});
    writetable(T, file);
end