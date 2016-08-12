clear all;
close all;
peak=1;
len=0;


sus = [];

for q=1:4
    j=0;
    rest_V = [];
    string = ['output' num2str(q) '.txt'];%EPSC:0: IPSC:70 mv
    
    p=load(string);
    time=p(:,1);
    voltage_filter=p(:,2);
%       figure;
%      plot(time,voltage_filter);end

    


    d=deriv(voltage_filter);
    m=0;
    for j=50000:(length(voltage_filter)-1)
       if d(j) > 0.01
          j=j+100;
       else
          rest_V(m+1) = voltage_filter(j);
       end
       m=m+1;
    end

    sus(q) = mean(rest_V);
end
  





%  plot(time,voltage_filter,PeakX,PeakY,'rv', 'MarkerFaceColor','r');
%  freq=(peak-1)/(length(time)/50000);

% xvalues=10:10:600;
% hist(PeakZ,xvalues);
% probplot('normal',PeakZ);
% cdfplot(PeakZ);
%s1=load(filename);
%s2=load(filename2);
% times=[s1.time;s2.time];


%  save('cell47_CC_0_0','PeakZ');
% % save('cell21_70_0_7','PeakZ');
% 
% freq=(peak-1)/((len-(50000*(0+1)))/50000);

% size(voltage_filter);
% 
% N=;
% fs=50000;
% ts=1/fs;
% tmax=(N-1)*ts;
% 
% t=0:ts:tmax;
% 
% f=-fs/2:fs/(N-1):fs/2;
% z=fftshift(fft(voltage_filter));
% plot(f,abs(z));


% plot(faxis,2*F)
% xlim([0 100]);

