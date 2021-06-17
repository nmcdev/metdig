import os

import numpy as np

import PIL.Image as Image


def auto_rc(N, row=None, col=None):
    if N == 1:
        return 1, 1
    if row == None and col == None:
        row = int(np.round(np.sqrt(N)))
        col = int(np.ceil(N / row))

    elif row == None and col != None:
        row = int(np.ceil(N / col))

    elif row != None and col == None:
        col = int(np.ceil(N / row))

    return row, col


def compose_byrgba(rgbalst, outfile, row=None, col=None, fill_pecent=0):
    """[根据rgba列表，多图合并到一张大图上]

    Args:
        rgbalst ([list]): [多个rgba组成的list]
        outfile ([str]): [输出文件]
        row ([int]], optional): [组成的新图的行数]. Defaults to None.
        col ([int], optional): [组成的新图的列数]. Defaults to None.
        fill_pecent (float, optional): [小图间距百分比，原理是各个小图在外围增加N圈白色像素，然后再组合成大图]]. Defaults to 1.
    """
    N = len(rgbalst)

    newrgbalst = []
    for n in range(N):
        buf = rgbalst[n]
        fill_xpix = int(buf.shape[0] * fill_pecent / 100)
        fill_ypix = int(buf.shape[1] * fill_pecent / 100)
        buf_copy = np.full((buf.shape[0] + fill_xpix*2, buf.shape[1] + fill_ypix*2, buf.shape[2]), 255, dtype=np.uint8)
        buf_copy[fill_xpix:buf.shape[0]+fill_xpix, fill_ypix:buf.shape[1]+fill_ypix, :] = buf

        newrgbalst.append(buf_copy)

    row, col = auto_rc(N, row=row, col=col)

    if row is None and col is None:
        row = int(np.ceil(np.sqrt(N)))
        if N % row == 0:
            col = int(N / row)
        else:
            col = int(np.ceil(N / row))

    max_pix_r = max([buf.shape[0] for buf in newrgbalst])
    max_pix_c = max([buf.shape[1] for buf in newrgbalst])

    rgbabuf = np.full((max_pix_r * row, max_pix_c * col, 4), 255, dtype=np.uint8)

    for ir in range(row):
        for ic in range(col):
            n = ir * col + ic
            if n >= N:
                continue
            buf = newrgbalst[n]

            paste_st_row = ir * max_pix_r
            paste_en_row = ir * max_pix_r + buf.shape[0]

            paste_st_col = ic * max_pix_c
            paste_en_col = ic * max_pix_c + buf.shape[1]

            rgbabuf[paste_st_row: paste_en_row, paste_st_col: paste_en_col, :buf.shape[2]] = buf

    image = Image.fromarray(rgbabuf.astype(np.uint8), mode='RGBA')

    image.save(outfile)


def savergba(rgbabuf, outfile):

    image = Image.fromarray(rgbabuf.astype(np.uint8), mode='RGBA')
    image.save(outfile)


if __name__ == '__main__':
    bufs = []
    colors = [
        [255, 128, 128],
        [255, 255, 128],
        [128, 255, 255],
        # [0, 128, 255],
        # [255, 0, 0],
        # [255, 255, 255],

        # [255, 128, 128],
        # [255, 255, 128],
        # [128, 255, 255],
        # [0, 128, 255],
        # [255, 0, 0],
        # [255, 255, 255],
    ]
    for i in range(len(colors)):
        buf = np.full((100, 100, 4), 255, dtype=np.uint8)
        buf[:, :, 0] = colors[i][0]
        buf[:, :, 1] = colors[i][1]
        buf[:, :, 2] = colors[i][2]
        bufs.append(buf)
        # print(buf)
        print()

    compose_byrgba(bufs, './a.png')
