% Read IEEE488.2 binary data from agilent/lecroy scope
% data format: 'sampleReate\n voltageOffset\n voltageScale\n ??? #dssssxx...xx. ??? #dssssxx...xx.':
% d: digital follows as data size in bytes
% varargout: sampleRate, voltageOffset, voltageScale
% varargin: set data type 'int8' or 'uint8', default is 'uint8'
function [waves, varargout] = analysis_readPowerData(fileName, nSample, varargin)
if (nargin >= 2)
    if strcmp(varargin{1}, 'int8')
        precision = 'int8=>int8';
    elseif strcmp(varargin{1}, 'uint8')
        precision = 'uint8=>uint8';
    else
        precision = 'uint8=>uint8';
        fprintf('Unrecognized setting for data type, use uint8 as default');
    end
else
    precision = 'uint8=>uint8';
end

fileId = fopen(fileName, 'r');
waves = [];
%startChar = fread(fileId, 1, 'char=>char'); % '#' = 35

if nargout > 1
    % scopeSettings = [sampleRate, voltageOffset, voltageScale, timeScale];
    scopeSettings = getScopeSettings(fileId);
    for k = 1:nargout-1 
        varargout{k} = scopeSettings(k);
    end
end

while findStartChar(fileId)
    nDigits = fread(fileId, 1, 'char=>char');
    nDigits = str2double(nDigits);
    dataBytes = fread(fileId, nDigits, 'char=>char');
    dataBytes = str2double(dataBytes);
    wave = fread(fileId, dataBytes, precision);
    wave(end-mod(numel(wave),10)+1:end) = []; % remove possible extra data points
    waves = [waves, wave];
    if size(waves, 2) >= nSample
        break
    end
    stopChar = fread(fileId, 1, 'uint8=>uint8');
    assert(stopChar == 10, 'stop char is not equal to 10');
end

% correct sample rate using timeInfo and  wave length
if nargout > 1
    [traceLength, ~] = size(waves);
    varargout{1} = traceLength / scopeSettings(4) / 10;
end

fclose(fileId);
end

function scopeSettings = getScopeSettings(fileId)
% sampleRate from scope may not be correct
sampleRate = fgets(fileId);
sampleRate = str2double(sampleRate(1:end-1));
voltageOffset = fgets(fileId);
voltageOffset = str2double(voltageOffset(1:end-1));
voltageScale = fgets(fileId);
voltageScale = str2double(voltageScale(1:end-1));
timeScale = fgets(fileId);
timeScale = str2double(timeScale(1:end-1));
scopeSettings = [sampleRate, voltageOffset, voltageScale, timeScale];
%scopeSettings = [sampleRate, voltageOffset, voltageScale];
end

function output = findStartChar(fileId)
output = true;
i = 0;
maximumSearch = 128;
while true
    if (feof(fileId))
        output = false;
        return;
    end
    char = fread(fileId, 1, 'char=>char');
    if char == '#'
        output = true;
        return;
    end
    i = i + 1;
    if (i >= maximumSearch)
        output = false;
        return;
    end
end
end