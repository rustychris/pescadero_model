%% Convert a mat file to a csv

clear all

in_path = 'E:\Pescadero\data\BML_data\2017\all_concatenated\mat\' % directory of input file
out_path = 'E:\Pescadero\data\BML_data\2017\all_concatenated\csv\' % directory of output file

% 2017_NCK_wll_concat
% 2017_BC1_wll_concat 
% 2017_BC3_wll_concat
% 2017_CH2_wll_concat
% 2017_PC3_wll_concat


in_fname= '2017_PC3_wll_concat'

S = load([in_path,in_fname,'.mat'])
dtime = datestr(S.PC3.mtime(:,1),'yyyy-mm-dd HH:MM:SS');
depth = S.PC3.depth(:,1);
temp=S.PC3.temp(:,1);
pressure=S.PC3.pressraw(:,1);

T=table(dtime,depth,temp,pressure);
writetable(T,[out_path,in_fname,'.csv']);  %default delimiter is comma