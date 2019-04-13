select distinct lkj.lkjwholecourse,
to_char(lkj.starttime, 'yyyymmddhh24miss') as lkj_st_tm,
to_char(lkj.endtime, 'yyyymmddhh24miss') as lkj_ed_tm,
video.FILEPATH, 
to_char(video.STARTTIME, 'yyyy-mm-dd hh24:mi:ss') as video_st_tm, 
to_char(video.ENDTIME,'yyyy-mm-dd hh24:mi:ss') as video_ed_tm, 
lkj.JICHEXINGHAO, 
lkj.JCH, video.CHNO, 
lkj.TRACE, 
video.DRIVERNO, 
video.DRIVER2NO,
lkj.lkjid,                 
video.ID, 
video.DATASOURCE,
lkj.TIMEDEVIATION
from lkjvideoadmin.lkjvideoproblem lkj 
inner join LAVDR video 
on lkj.locotypeno = video.TRAINNO 
where  not(
(lkj.JCH like '1004%' or lkj.JCH like '1041%' or lkj.JCH like '1128%' or lkj.JCH like '1133%' or lkj.JCH like '1153%' or lkj.JCH like '1396%' or (cast(substr(lkj.JCH, 0,4) as int) > 1495 and cast(substr(lkj.JCH, 0,4) as int) <= 1514)) and lkj.JCH != '1496B' and lkj.JCH != '1501A' and lkj.JCH != '1501B' and lkj.JCH != '1504A' and lkj.JCH != '1505A' and lkj.JCH != '1505B' and lkj.JCH != '1506B' and cast(to_char(video.starttime, 'hh24') as int) between 9 and 16
)
and lkj.JICHEXINGHAO = 'HXD2'
and lkj.videoneedanaly > lkj.videoanalyzed and lkj.lkjwholecourse is not null 
and ((video.STARTTIME >= lkj.STARTTIME and video.STARTTIME <= lkj.ENDTIME) or (video.ENDTIME >= lkj.STARTTIME and video.ENDTIME <= lkj.ENDTIME))
and video.ISANALYZED = 0
and (video.CHNO=2 or video.CHNO=10) 
and lkj.starttime is not null and lkj.endtime is not null and video.FILEPATH is not null and video.STARTTIME is not null and video.ENDTIME is not null and lkj.JICHEXINGHAO is not null and lkj.JCH is not null and video.CHNO is not null and lkj.TRACE is not null and video.DRIVERNO is not null and lkj.lkjid is not null and video.ID is not null and video.DATASOURCE is not null               
and to_char(lkj.LKJTIME, 'yyyy-mm-dd hh24:mi:ss')  like '2019-03%'
and rownum <= 100
order by lkj.LKJTIME
