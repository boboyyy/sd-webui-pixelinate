import numpy as np
import os
import glob
from PIL import Image
import math

def resize_image(image, gridh, gridw, mode='NEAREST'):
    # mode: NEAREST, BILINEAR, LANCZOS
    mode_dict = {'NEAREST': Image.NEAREST, 'BILINEAR': Image.BICUBIC, 'LANZCOS': Image.LANCZOS}

    original_height, original_width = image.size[1], image.size[0]
    resized_img = image.resize((gridw, gridh), mode_dict[mode])
    return resized_img

def merge_overlapping_grids_linear(gridsPath, height, width, gridh, gridw, overlaph, overlapw, ratio):
    '''
    scale: 图像/网格比例
    gridsPath: 网格路径
    height, width: 待合成图像的高宽
    overlaph, overlapw: 重叠高宽
    '''
    TopRegionWeights = np.linspace(0, 1, overlaph)
    TopRegionWeights = TopRegionWeights.reshape(-1, 1).repeat(gridh, axis=1)
    BottomRegionWights = np.linspace(1, 0, overlaph)
    BottomRegionWights = BottomRegionWights.reshape(-1, 1).repeat(gridh, axis=1)
    LeftRigionWeights = np.linspace(0, 1, overlapw)
    LeftRigionWeights = LeftRigionWeights.reshape(1, -1).repeat(gridw, axis=0)
    RightRegionWeights = np.linspace(1, 0, overlapw)
    RightRegionWeights = RightRegionWeights.reshape(1, -1).repeat(gridw, axis=0)

    im = np.zeros((height, width, 3)) * 255
    count = np.zeros((height, width, 3))
    ImageWeight = np.zeros((height, width, 3))
    gridnames = sorted(glob.glob(gridsPath + "/*.png"))
    refernames = os.listdir(gridsPath)

    for gridname, refername in zip(gridnames, refernames):
        if "-0000-1.png" in gridname:
            continue
        splitname = refername[:-9].split('_')
        x, y = int(splitname[-2]), int(splitname[-1])
        grid = Image.open(gridname)
        grid = resize_image(grid, gridh, gridw)
        grid = np.asarray(grid)

        start_row = y*(gridh- overlaph)
        end_row = start_row + gridh
        start_col = x*(gridw-overlapw) 
        end_col = start_col + gridw
        RegionWeights = np.ones((gridh, gridw))
        if start_row >= overlaph:
            RegionWeights[:overlaph, :] += TopRegionWeights
            #print(RegionWeights[:overlaph, :].shape, TopRegionWeights.shape)
        if end_row <= height:
            RegionWeights[(gridh - overlaph):, :] += BottomRegionWights
            #print(RegionWeights[(gridh - overlaph):, :].shape)
        if start_col >= overlapw:
            RegionWeights[:, :overlapw] += LeftRigionWeights
            #print(RegionWeights[:, :overlapw].shape, LeftRigionWeights.shape)
        if end_col <= width:
            RegionWeights[:, (gridw - overlapw):] += RightRegionWeights
            #print(RegionWeights[:, (gridw - overlapw):].shape, RightRegionWeights.shape)

        RegionWeights = RegionWeights.reshape(gridh, gridw, 1).repeat(3, axis=2)
        im[start_row:end_row, start_col:end_col] += grid * RegionWeights

        ImageWeight[start_row:end_row, start_col:end_col] += RegionWeights

        # im[y*(gridh- overlaph):y*(gridh- overlaph)+gridh, x*(gridw-overlapw):x*(gridw-overlapw)+gridw]  +=grid
        # count[y*(gridh- overlaph):y*(gridh- overlaph)+gridh, x*(gridw-overlapw):x*(gridw-overlapw)+gridw] += 1
        #print(ImageWeight[gridh-overlaph:gridh, gridw-overlapw:gridw])
        #break

    ImageWeight = np.where(ImageWeight==0, 1, ImageWeight)
    im = im // ImageWeight

    return Image.fromarray(im.astype(np.uint8))

def divide_and_save_Overlap(img_path, step_x, step_y, overlap_x, overlap_y, output_folder):
    # 打开图片
    imname = img_path.split('\\')[-1]
    img = Image.open(img_path)

    # 获取图片的宽度和高度
    width, height = img.size

    # 确定每个网格的宽高数
    nx = (width - step_x) // (step_x - overlap_x) + 1
    ny = (height - step_y) // (step_y - overlap_y) + 1

    # 确保输出目录存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 循环划分并保存
    for i in range(nx):
        for j in range(ny):
            left = i * (step_x - overlap_x)
            upper = j * (step_y - overlap_y)
            right = left + step_x
            lower = upper + step_y
            box = (left, upper, right, lower)
            cropped_img = img.crop(box)
            #minn, maxn = np.array(cropped_img).min(), np.array(cropped_img).max()
            #if (maxn - minn) == 0:
            #    continue
            prefix = '_'.join(imname.split('_')[:2])
            cropped_name = os.path.join(output_folder, prefix + f"_grid_{i}_{j}.png")
            cropped_img.save(cropped_name)

    # 图片切割完成
    success_massage = "done!"
    return success_massage