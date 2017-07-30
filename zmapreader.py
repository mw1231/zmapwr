# -*- coding: utf-8 -*-
"""
A python module for reading/writing/
Zmap formatted filed
This is version2.0

"""
# Author: MaWei

import numpy as np

head_number = [3, 5, 6, 3] #the number of the items of each head line.
head_list = []
ori_dic = {}


def dickeychange(dic):
    """
    read the exist dictionary 'dic', change
    the keys as we need,  store in a new dictionary.
    Args:
        'dic' must be a dictionary file .
    Return the new dictionary.
    
    """
    newdic = {}
    head_keys = [['File_define', 'File', 'Grid_nodes'],
                 ['Field_width', 'Null_data', 'Null_define',
                  'Decimal_places', 'Starting_column'],
                 ['Row_number', 'Columns_number', 'Xmin',
                  'Xmax', 'Ymin', 'Ymax'],
                 ['ThirdLine1', 'ThirdLine2', 'ThirdLine3']]
    #find the headdata's position, give it a meaningful key
    for key in dic.keys():
        for i in range(len(key)-1):
            newkey = head_keys[int(key[i])][int(key[i+1])]
            newdic[newkey] = dic[key]
    return newdic


def zmap_reader(zmapfile, trans_null=True):
    """
    read the head info ,store the info into a dic.
    read the data, store it into a numpyarray

    Args:
        'zmapfile' must be a zmap file witch can be reading
        'trans_null' is a bool, default is Ture, if it's True,
        the data which is None will be turn into nan.

    Returns:
        data_array, ann
        ori_dic: the original head dictionary file, which keys are 
        'row&position'.
        head_dic: the head dictionary file, which keys are changed by 
        the dickeychange, and the keys are meaningful keys.
        data_array:the zmapfile's  data array, which is a numpy array.
        ann: the annotation which is reading from the zmapfile.

    """
    data_array = np.array([])
    with open(zmapfile, 'r') as fzi:
        fline = fzi.readline()
        line_number = 0
        ann = []
        while not fline.strip() == '@':
            #if the line is start with '!', the line is annotation,
            #just continue.
            if fline.strip().startswith('!'):
                ann.append(fline.lstrip('!'))
            else:
                fline = fline.strip().rstrip(',').replace('@', '').split(',')
                #if the line's length is lager than or equal to the
                #head_number, then the head
                #information is enough, read it!
                for i in range(len(fline)):
                    if len(fline) >= head_number[line_number]:
                        ori_dic['%d%d'%(line_number, i)] = fline[i].strip()
                        #head_dic[head_keys[line_number][i]] = fline[i].strip()
                        head_dic = dickeychange(ori_dic)


                line_number += 1
            fline = fzi.readline()
        nodes = int(head_dic['Grid_nodes'])
        data_row = int(head_dic['Row_number'])
        data_colu = int(head_dic['Columns_number'])
        field_width = int(head_dic['Field_width'])
        while fline:
            if fline.strip() == '@':
                print('read the last @')
            else:
                dataline = fline.strip().split()
                int(head_dic['Field_width'])
                lastline_n = int(head_dic['Row_number']) % nodes
                # if the data line equal the number of nodes or equal the
                #number of lastline_n ,appened the
                #dataline to the data's array
                if len(dataline) == nodes or len(dataline) == lastline_n:
                    for data in dataline:
                        #check the Data, if the data has decimal then do
                        #nothing, else add the decimal point to data
                        if data.find('.') == -1:
                            data = data + '.'
                        #check the Data,  if the data's length is
                        #longer than field_width  change the data's length
                        #equal to the field_width
                        if len(data) > field_width:
                            data = data.replace(data[-(len(data)-field_width)],
                                                '')
                        data_array = np.append(data_array, data)
                else:
                    print('data is not right..')
            fline = fzi.readline()

    #if the Decimal_places is <= 7, then change the type to float32,
    #else change the type to float64.
    if int(head_dic['Decimal_places']) <= 7:
        data_array = data_array.astype('float32')
    else:
        data_array = data_array.astype('float64')
    #if the trans_null is True, then change the data '-9999.0000000' to None
    for i in range(len(data_array)):
        if trans_null == True:
            if data_array[i] == float(head_dic['Null_data']):
                data_array[i] = None

    data_array = data_array.reshape((data_colu, data_row))
    return ori_dic, head_dic, data_array, ann

def zmap_writer(fout, ori_head, f_head, datary, annotation):
    """
    write the zmap head dictionary,the zmap data array and the 
    annotation  into a zmap format file.

    Args:
        'fout' must be a file witch can be writing
        'ori_head' is a head dictionary which keys are 'row&position'.
        'f_head' is the head dictionary file, which keys are changed by 
        the dickeychange, and the keys are meaningful keys.
        'datary' the zmapfile's  data array, which is a numpy array.
        'annotation' the annotation which is reading from the zmapfile.
    """
    linev = []
    strhead = ''

    with open(fout, 'w') as fzo:
        if annotation:
            for ann_line in annotation:
                fzo.writelines('!' + ann_line)
        for i in range(len(head_number)):
            for j in range(head_number[i]):
                linev.append(ori_head['%d%d'%(i, j)])

            #fzo.writelines(",".join(linev)+ '\n')
            strhead = strhead + (",".join(linev)+ '\n')
            linev = []
        strhead = '@' + strhead  + '@' + '\n'
        fzo.writelines(strhead)
        nodes = int(f_head['Grid_nodes'])
        lines = int(f_head['Row_number']) // nodes
        lastline_n = int(f_head['Row_number']) % nodes
        #decimal = int(f_head['Decimal_places'])
        data_row = int(f_head['Row_number'])
        #data_colu = int(f_head['Columns_number'])
        datary = datary.flat
        #if the data in the array is None, change into the Null_data
        for i in range(len(datary)):
            if np.isnan(datary[i]):
                datary[i] = float(f_head['Null_data'])
        if lastline_n == 0:  #if
            strdata = ''
            for i in range(len(datary) // nodes):
                row = datary[i*nodes:(i+1)*nodes]
                for ndata in row:
                    strdata = strdata + '%20.7f'%ndata
                strdata = strdata + '\n'
                fzo.writelines(strdata)
                strdata = ''
        else:
            strdata = []
            for i in range(data_row):
                row = datary[i*data_row:(i+1)*data_row]
                for n in row:
                    strdata.append('%20.7f'%n)
                for j in range(lines):
                    strdata.insert((j+1)*nodes, '\n')
                    fzo.writelines("".join(strdata)+ '\n')
                strdata = []

orihead, head, data, anno = zmap_reader('new1.dat')
print('................This is head dic.......,\n', head)
print('................This is data.......,\n', data)
print('................This is head annotation.......,\n', anno)
zmap_writer('out.txt', orihead, head, data, anno)