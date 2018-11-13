#coding:utf-8

import sys, os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import src.common as common
import time
import pandas as pd
import src.time_check as time_check
import datetime
import traceback
os_sep = os.path.sep
#os.environ["CUDA_VISIBLE_DEVICES"]="1"



# def add_to_db(db, qry_result, result_list, table_name, violate):
#     ''' for each result from result_list, insert it to database
#         input:
#                 db: database
#                 root_arr: path list split by '/'
#                 result_list: the result list returned by model
#                 driver: driver info
#                 violate: violate tag
#         return:
#                 a boolean flag to determine the success of db insertion
#     '''
#     global mysql_logger
#     mysql_logger.info('function add_to_db: execute begin')
#     # dirname = root_arr[-1].split('_')
#     # train_type, train_num, duan = dirname[0], dirname[1], dirname[2]
#     lkj_fname, video_st_tm, video_ed_tm, video_name, traintype, trainum, port, shift_num, driver, _, video_path = qry_result
#     #print(video_path)
#     for result in result_list:
#         #ptc_fname = result[2]
#         violate_st_tm = result[0]
#         #violate_ed_tm = result[4]
#         #frame_st = result[1]
#         #frame_ed = result[5]
#         #violate = result[3]
#         #violate = '未手比'
        
#         sql = "insert into {0} ({1}) values (\'{2}\', \'{3}\', \'{4}\', \'{5}\', \'{6}\', \'{7}\', {8}, \'{9}\', \'{10}\', \'{11}\', \'{12}\', now(), \'{13}\')".\
#             format(table_name, 'LKJ_FILENAME,VIDEO_FILENAME,VIDEO_STARTTIME,VIDEO_ENDTIME,TRAIN_TYPE,TRAIN_NUM,PORT,SHIFT_NUM,DRIVER,VIOLATE,START_TIME,INSERT_TIME,VIDEO_PATH',\
#                 lkj_fname, video_name, video_st_tm, video_ed_tm, traintype, trainum, port, shift_num, driver, violate, violate_st_tm, video_path)
#         mysql_logger.info('function add_to_db: executing insert sql: {0}'.format(sql))
#         try:
#             db.Insert(sql)
#             mysql_logger.info('function add_to_db: insert sql execute successfully')
#         except Exception as e:
#             mysql_logger.error('function add_to_db: insert sql execute failed: {0}'.format(traceback.format_exc()))
#             return False
#     return True

def init(log_name):
    ''' initialization process including config parameters and logger fetch
        input: model log name
        return: config and loggers objects, json path and box info
    '''
    print('run_yolo initializing')
    cfg = common.get_config('config.ini')
    yl_cfg = common.get_config('config/yolo.ini')
    main_logger = common.get_logger('run_yolo', 'logconfig.ini', True)
    mdl_logger = common.get_logger(log_name, 'logconfig.ini', False)
    db_logger = common.get_logger('mysql', 'logconfig.ini', False)
    
    dn_path = yl_cfg.get('path', 'darknet')
    common.path_check(dn_path, mdl_logger, 'darknet path NOT set!', 8)
    sys.path.append(dn_path)
    print(dn_path)
    mdl_logger.info('function init: execute begin')
    mdl_logger.info('function init: loading darknet')
    import darknet as dn
    mdl_logger.info('function init: loading yolo config files')
    yolo_cfg = yl_cfg.get('path', 'cfg')
    common.file_check(yolo_cfg, mdl_logger, 'yolo cfg file set wrong!', 9)
    yolo_weights = yl_cfg.get('path', 'weights')
    common.file_check(yolo_weights, mdl_logger, 'yolo weight file set wrong!', 9)
    yolo_meta = yl_cfg.get('path', 'meta')
    common.file_check(yolo_meta, mdl_logger, 'yolo meta file set wrong!', 9)
    mdl_logger.info('function init: loading yolo network')
    net = dn.load_net(yolo_cfg.encode('utf-8'), yolo_weights.encode('utf-8'), 0)
    mdl_logger.info('function init: loading yolo meta')
    meta = dn.load_meta(yolo_meta.encode('utf-8'))
    return cfg, main_logger, mdl_logger, db_logger, [dn, net, meta]


# get_lkj_signal = lambda lkj_data: lkj_data[pd.notnull(lkj_data['信号'])][['时间', '信号','事件']].reset_index(drop=True)
# def get_lkj_signal(lkj_data):
#     lkj_data_not_nan = lkj_data[pd.notnull(lkj_data['信号'])][['时间', '信号','事件']].reset_index(drop=True)
#     #lkj_data_not_nan['时间'] = [date_str_fmt+' '+ x for x in lkj_data_not_nan['时间']]
#     return lkj_data_not_nan

def exe_yolo(path_in,yolo_result,dn, net, meta, st_time, fps):
    ''' function to call yolo
        input: 
                path_in: frame path
                yolo_result: array to store yolo result 
                dn: darknet main program
                net: darknet network and weights
                meta: darknet data
                st_time: video start time
                fps: video fps
        return:
                exe_flg: a flag to determine the success of running yolo
    '''
    global model_logger
    exe_flg = 0
    model_logger.info('function exe_yolo: yolo execute begin under path {0}'.format(path_in))
    for ptc in os.listdir(path_in):
        if ptc.endswith('.png'):
            yolo_rt = []
            try:
                yolo_rt = dn.detect(net, meta, os.path.join(path_in,ptc))
                # if ptc.endswith('00435.png'):
                #     print(yolo_rt)
            except Exception as e:
                model_logger.error('functon exe_yolo: yolo execute failed with picture {0}: {1}'.format(os.path.join(path_in,ptc), e))
                exe_flg = 2
            #print(yolo_rt)
            # if yolo_rt != []:
            #     if yolo_rt[1] != []:
            #         for j in range(len(yolo_rt[1])):
            #             # label: yolo_rt[1][j][0]
            #             # prob: yolo_rt[1][j][1]
            #             common.add_result(yolo_result, yolo_rt[0], fps, st_time, yolo_rt[1][j][0].decode('ascii'))
            if yolo_rt != []:
                for j in range(len(yolo_rt)):
                    common.add_result(yolo_result, os.path.splitext(ptc)[0], fps, st_time, yolo_rt[j][0].decode('utf-8'))
                    #common.add_result(yolo_result, os.path.splitext(ptc)[0], fps, st_time, yolo_rt[j][0])
            else:
                model_logger.warning('function exe_yolo: no result return by yolo for picture {0}'.format(ptc))

    if not 'yolo_rt' in locals().keys():
        model_logger.warning('function exe_yolo: yolo does not execute under path {0}'.format(path_in))
        exe_flg = 1
    model_logger.info('function exe_yolo: yolo execute finish under path {0}'.format(path_in))
    return exe_flg


def match_lkj(qry_result, yolo_result, root_arr):

    global model_logger, video_pth
    model_logger.info('function match_lkj: execute begin')
    lkj_fname = qry_result[0][0]
    dirname = video_pth+os_sep+root_arr[1]+os_sep+root_arr[2]
    model_logger.info('function match_lkj: reading lkj data {0}/{1}'.format(dirname, lkj_fname))
    lkj_result = common.get_lkj(dirname, lkj_fname)

    match_flg = 0
    #point_forward = []
    #point_forward_include = []
    #no_break = []
    #sleep = []
    #cellphone = []
    #stand_2 = []

    if lkj_result[0] == False:
        model_logger.error('function match_lkj: {0}'.format(lkj_result[1]))
        match_flg = 1
    else:
        model_logger.info('function match_lkj: lkj data read successfully')
        # speed related result
        #lkj_speed = get_lkj_speed(lkj_data, date_str_fmt)
        # hand posture related result
        # model_logger.info('function match_lkj: filtering lkj signal')
        # try:
        #     lkj_signal = get_lkj_signal(lkj_result[1])
        #     model_logger.info('function match_lkj: filter lkj signal successfully')
        # except Exception as e:
        #     model_logger.error('function match_lkj: filter lkj signal failed {0}'.format(traceback.format_exc()))
        #     match_flg = 2
        # execute time check yolo
        #yolo_result_speed = time_check.yolo_speed_filter(yolo_result, lkj_speed)
        #print(yolo_result)
        #print(lkj_signal)
        #dt = root_arr[3].split('_')[-4]
        #tm = root_arr[3].split('_')[-3]
        #tm_len = int(root_arr[3].split('_')[-2])
        #ed_time = common.date_time_reformat(dt, tm)
        #ed_time = (datetime.datetime.strptime(ed_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=tm_len)).strftime('%Y-%m-%d %H:%M:%S')
        st_time = qry_result[0][1]
        ed_time = qry_result[0][2]
        #print(st_time, ed_time)
        model_logger.info('function match_lkj: joining lkj signal data and yolo result')
        no_break = [x for x in yolo_result if x[-1] == 'no_break']
        sleep = [x for x in yolo_result if x[-1] == 'sleep_1' or x[-1] == 'sleep_2']
        cellphone = [x for x in yolo_result if x[-1] == 'cellphone' ]
        stand_2 = [x for x in yolo_result if x[-1] == 'stand_2' ]

        no_break_final = []
        sleep_final = []
        cellphone_final = []
        stand_2_final = []
        #print(yolo_result)
        #print(len(yolo_result),lkj_signal.shape)

        # no_break check
        if no_break != [] and no_break != [[]]:
            try:
                no_break_final = time_check.lkj_time_filter(no_break,lkj_result[1],speed_thresh=1, time_range=5)
                model_logger.info('function match_lkj: lkj data and no_break result join successfully')
            except Exception as e:
                model_logger.error('function match_lkj: lkj data and no_break result join failed {0}'.format(traceback.format_exc()))
                match_flg = 2
            if no_break_final != []:
                no_break_final = common.leave_filt(no_break_final, lkj_result[1], qry_result[0][3])

        # sleep check
        if sleep != [] and sleep != [[]]:
            try:
                sleep_final = time_check.lkj_time_filter(sleep,lkj_result[1],speed_thresh=0, time_range=300)
                model_logger.info('function match_lkj: lkj data and sleep result join successfully')
            except Exception as e:
                model_logger.error('function match_lkj: lkj data and sleep result join failed {0}'.format(traceback.format_exc()))
                match_flg = 3 

        # cellphone check
        if cellphone != [] and cellphone != [[]]:
            try:
                cellphone_final = time_check.lkj_time_filter(cellphone,lkj_result[1],speed_thresh=0, time_range=2)
                model_logger.info('function match_lkj: lkj data and cellphone result join successfully')
            except Exception as e:
                model_logger.error('function match_lkj: lkj data and cellphone result join failed {0}'.format(traceback.format_exc()))
                match_flg = 4 

        # # point check
        # try:
        #     #print(st_time)
        #     point_forward = time_check.yolo_signal_filter(yolo_result,lkj_signal,[st_time, ed_time],30,10,['victory_1', 'leave_1', 'leave_2'],['出站'],['绿灯', '绿黄灯','双黄灯'])
        #     #print(point_forward)
        #     point_forward_include = time_check.yolo_signal_include_filter(yolo_result,lkj_signal,[st_time, ed_time],30,10,['victory_1'],['出站'],['绿灯', '绿黄灯','双黄灯'])
        #     model_logger.info('function match_lkj: lkj signal data and point_forward result join successfully')
        # except Exception as e:
        #     model_logger.error('function match_lkj: lkj signal data and point_forward result join failed {0}'.format(traceback.format_exc()))
        #     match_flg = 3 

        # stand_2 check
        if stand_2 != [] and stand_2 != [[]]:
            try:
                stand_2_final = time_check.lkj_event_exclude(stand_2, lkj_result[1],'进站','出站',[st_time, ed_time], 2,10)
                model_logger.info('function match_lkj: lkj data and stand_2 result join successfully')
            except Exception as e:
                model_logger.error('function match_lkj: lkj data and stand_2 result join failed {0}'.format(traceback.format_exc()))
                match_flg = 5

    final_result = ([no_break_final] + [sleep_final] + [cellphone_final] + [stand_2_final])
    return match_flg, final_result
        

def model_rt_check(match_rt, path):
    global main_logger
    rt = True
    main_logger.info('function model_rt_check: checking lkj and yolo matching result')
    if match_rt == 1:
        main_logger.error('function model_rt_check: lkj data read error under path {0}'.format(path))
        rt = False
    elif match_rt == 2:
        main_logger.error('function model_rt_check: lkj data and no_break result matching error under path {0}'.format(path))
        rt = False
    elif match_rt == 3:
        main_logger.error('function model_rt_check: lkj data and sleep result matching error under path {0}'.format(path))
        rt = False
    elif match_rt == 4:
        main_logger.error('function model_rt_check: lkj data and cellphone result matching error under path {0}'.format(path))
        rt = False
    elif match_rt == 5:
        main_logger.error('function model_rt_check: lkj data and stand_2 result matching error under path {0}'.format(path))
        rt = False
    elif match_rt < 0 or match_rt > 5:
        main_logger.error('function model_rt_check: lkj match program error: return out of range under path {0}'.format(path))
        rt = False
    return rt


def store_result(model_result, qry_result, mysql_db, save_tmp, path):
    global main_logger, mysql_logger
    no_break_final, sleep_final, cellphone_final, stand_2_final = model_result
    
    # add no_break result to db
    if no_break_final == []:
        main_logger.info('function store_result: no no_break detected under path {0}'.format(path))
    else:
        if common.add_to_db(mysql_db, qry_result, no_break_final, 'violate_result.report', '未握大闸', mysql_logger, save_tmp) == False:
            main_logger.error('function store_result: no_break result insert to db failed under path {0}'.format(path))
        else:
            main_logger.info('function store_result: no_break result insert to db successfully under path {0}'.format(path))
    
    # add sleep result to db
    if sleep_final == []:
        main_logger.info('function store_result: no sleep detected under path {0}'.format(path))
    else:
        if common.add_to_db(mysql_db, qry_result, sleep_final, 'violate_result.report', '平躺睡觉', mysql_logger, save_tmp) == False:
            main_logger.error('function store_result: sleep result insert to db failed under path {0}'.format(path))
        else:
            main_logger.info('function store_result: sleep result insert to db successfully under path {0}'.format(path))
    
    # add cellphone result to db
    if cellphone_final == []:
        main_logger.info('function store_result: no cellphone detected under path {0}'.format(path))
    else:
        if common.add_to_db(mysql_db, qry_result, cellphone_final, 'violate_result.report', '手机', mysql_logger, save_tmp) == False:
            main_logger.error('function store_result: cellphone result insert to db failed under path {0}'.format(path))
        else:
            main_logger.info('function store_result: cellphone result insert to db successfully under path {0}'.format(path))
    
    # add stand_2 result to db
    if stand_2_final == []:
        main_logger.info('function store_result: no stand_2 violation detected under path {0}'.format(path))
    else:
        if common.add_to_db(mysql_db, qry_result, stand_2_final, 'violate_result.report', '副司机未立岗', mysql_logger) == False:
            main_logger.error('function store_result: stand_2 result insert to db failed under path {0}'.format(path))
        else:
            main_logger.info('function store_result: stand_2 result insert to db successfully under path {0}'.format(path))

if __name__ =='__main__':
    # initialize
    cfg, main_logger, model_logger, mysql_logger, dn_list = init('yolo')
    #print(main_logger, model_logger, mysql_logger)
    main_logger.info('function main: execute begin')
    video_pth = cfg.get('path', 'video_path')
    common.path_check(video_pth, main_logger, 'Video path NOT set!', 8)
    main_logger.info('function main: video_path {0} get successfully'.format(video_pth))
    frame_pth = cfg.get('path', 'frame_path')
    common.path_check(frame_pth, main_logger, 'Frame path NOT set!', 8)
    main_logger.info('function main: frame_path {0} get successfully'.format(frame_pth))
    
    # Connect to DB
    main_logger.info('function main: connecting to Mysql database')
    db = common.connect_db(cfg, mysql_logger, 'mysql')
    if db == False:
        main_logger.error('function main: Mysql database connect failed')
    else:
        main_logger.info('function main: Mysql database conneting successfully')
        main_logger.info('function main: prepare to execute yolo')
        
        save_tmp=open('tmp/pict.sav', 'a+')
        main_logger.info('function main: temp file {0} generate successfully'.format(save_tmp))

        model_logger.info('function main: preparing darknet')
        dn, net, meta = dn_list
        model_logger.info('function main: load darknet setting: darknet -- {0}; net -- {1}; meta -- {2}'.format(dn, net, meta))
        gpu = 0
        dn.set_gpu(gpu)
        model_logger.info('function main: gpu set to {0}'.format(gpu))

        model_logger.info('function main: walk through dirs under frame path {0}'.format(frame_pth))
        for root,dirs,files in os.walk(frame_pth):
            root_arr = root.split(os_sep)
            yolo_result = []
            if len(root_arr) == 4:
                #path_in = os_sep.join(root_arr)
                main_logger.info('function main: searching video infomation under path {0}'.format(root))
                fps = root_arr[-1].split('_')[-1]   # dirname include video info
                go_flg, qry_result = common.get_video_info(root_arr, db, model_logger, mysql_logger)
                if go_flg == False:
                    main_logger.error('function main: video info get failed under path {0}'.format(root))
                else:
                    main_logger.info('function main: video info get successfully under path {0}'.format(root))
                    #st_time = common.date_time_reformat(dirname[-4], dirname[-3])
                    st_time = qry_result[0][1]
                    #print(st_time)
                    # executing yolo
                    main_logger.info('function main: yolo execute begin under path {0}'.format(root))
                    yolo_exe_rt = exe_yolo(root,yolo_result,dn, net, meta,st_time, fps)
                    main_logger.info('function main: checking yolo result under path {0}'.format(root))
                    if yolo_exe_rt == 2:
                        main_logger.error('function main: yolo execute failed under path {0}'.format(root))
                    elif yolo_exe_rt == 1:
                        main_logger.warning('function main: yolo was not be executed under path {0}'.format(root))
                    elif yolo_exe_rt < 0 or yolo_exe_rt > 2:
                        main_logger.error('function main: yolo program error: return out of range under path {0}'.format(root))
                    else:
                        main_logger.info('function main: yolo execute successfully under path {0}'.format(root))
                        # execute judge rules
                        if yolo_result == [[]] or yolo_result == []:
                            main_logger.warning('function main: no yolo return under path {0}'.format(root))
                        else:
                            #print(yolo_result)
                            main_logger.info('function main: matching lkj data and yolo result under path {0}'.format(root))
                            match_rt, model_final = match_lkj(qry_result, yolo_result, root_arr)
                            store_flg = model_rt_check(match_rt, root)
                            if not store_flg:
                                main_logger.error('function main: model return code check failed under path {0}'.format(root))
                            else:
                                store_result(model_final, qry_result[0], db, save_tmp, root)
                            
        main_logger.info('function main: closing temp file {0}'.format(save_tmp))
        save_tmp.close()                        
                        
    # close db
    mysql_logger.info('function main: closing database')
    try:
        db.__del__()
        mysql_logger.info('function main: database close successfully')
    except Exception as e:
        mysql_logger.error('function main: database close failed {0}'.format(traceback.format_exc()))

    main_logger.info('function main: execute finish')