trace_plt = analysis_readPowerData('STM11_150000_07-12-19', 10, 'int8');
trace_plt = trace_plt';


%csvwrite('STM_traces.txt', traces);


% for i from 1 to 500000:
    % traces = analysis_readPowerData('STM_data1_500000_07-08-19', i, 'int8');
    % ith trace timepoint =  traces(18968);
    % append it to txt 
   


% line 1 will be 1st trace's  18968 timepoint
% line 2 will be 2snd trace's  18968 timepoint
% line 3 will be 3rdt trace's  18968 timepoint
