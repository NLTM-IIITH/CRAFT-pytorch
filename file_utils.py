# -*- coding: utf-8 -*-
import os

import cv2
import numpy as np

import imgproc


# borrowed from https://github.com/lengstrom/fast-style-transfer/blob/master/src/utils.py
def get_files(img_dir):
    imgs, masks, xmls = list_files(img_dir)
    return imgs, masks, xmls

def list_files(in_path):
    img_files = []
    mask_files = []
    gt_files = []
    for (dirpath, dirnames, filenames) in os.walk(in_path):
        for file in filenames:
            filename, ext = os.path.splitext(file)
            ext = str.lower(ext)
            if ext == '.jpg' or ext == '.jpeg' or ext == '.gif' or ext == '.png' or ext == '.pgm':
                img_files.append(os.path.join(dirpath, file))
            elif ext == '.bmp':
                mask_files.append(os.path.join(dirpath, file))
            elif ext == '.xml' or ext == '.gt' or ext == '.txt':
                gt_files.append(os.path.join(dirpath, file))
            elif ext == '.zip':
                continue
    # img_files.sort()
    # mask_files.sort()
    # gt_files.sort()
    return img_files, mask_files, gt_files

def convert_to_xywh(result):
    a = result.strip().split(',')
    a = list(map(int, a))
    assert len(a) == 8
    x = min(a[0], a[6])
    y = min(a[1], a[3])
    x2 = max(a[2], a[4])
    y2 = max(a[5], a[7])
    ret = [x,y,x2-x,y2-y]
    ret = list(map(str, ret))
    return ','.join(ret) + '\r\n'

def sort_words(boxes):
    """Sort boxes - (x, y, x+w, y+h) from left to right, top to bottom."""
    mean_height = sum([y2 - y1 for _, y1, _, y2 in boxes]) / len(boxes)

    # boxes.view('i8,i8,i8,i8').sort(order=['f1'], axis=0)
    current_line = boxes[0][1]
    lines = []
    tmp_line = []
    for box in boxes:
        if box[1] > current_line + mean_height:
            lines.append(tmp_line)
            tmp_line = [box]
            current_line = box[1]            
            continue
        tmp_line.append(box)
    lines.append(tmp_line)

    for line in lines:
        line.sort(key=lambda box: box[0])

    return lines

def convert_to_string(lines):
    """
    this function gets the input from the sort_words func
    converts each of the individual line from xyxy format to xywh format
    then, output the complete string
    """
    ret = ''
    for line in lines:
        for i in line:
            x = [i[0], i[1], i[2]-i[0], i[3]-i[1]]
            ret += ','.join(list(map(str, x))) + '\r\n'
        ret += '\r\n'
    return ret.strip()

def saveResult(img_file, img, boxes, dirname='./result/', verticals=None, texts=None):
        """ save text detection result one by one
        Args:
            img_file (str): image file name
            img (array): raw image context
            boxes (array): array of result file
                Shape: [num_detections, 4] for BB output / [num_detections, 4] for QUAD output
        Return:
            None
        """
        img = np.array(img)

        # make result file list
        filename, file_ext = os.path.splitext(os.path.basename(img_file))

        # result directory
        res_file = dirname + "res_" + filename + '.txt'

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        ret = ''
        for box in boxes:
            poly = np.array(box).astype(np.int32).reshape((-1))
            strResult = ','.join([str(p) for p in poly]) + '\r\n'
            strResult = convert_to_xywh(strResult)
            ret += strResult

        a = ret.strip().split('\n')
        a = [i.strip() for i in a]
        a = [tuple(map(int, i.split(','))) for i in a]
        out = []
        for i in a:
            out.append((
                i[0], i[1],
                i[0] + i[2],
                i[1] + i[3],
            ))
        ret = sort_words(out)
        ret = convert_to_string(ret)

        with open(res_file, 'w') as f:
            f.write(ret)

