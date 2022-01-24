from types import FunctionType
from PIL import Image as PilImage
import numpy as np
from numpy import ndarray
from typing import List, Optional, Tuple
import math as m


class MyImage:
    @staticmethod
    def fromArray(imArray: ndarray):
        im = MyImage(None)
        im.setIm(imArray)
        return im

    def __init__(self, filename: Optional[str] = "./Resources/Images/horse1") -> None:
        if filename is not None:
            try:
                # im = PilImage.open(filename)
                im = PilImage.open(str(filename))
                self.setIm(im)

            except Exception as e:
                print(e)
                print("load Image failed")
        else:
            self.setIm(None)

    def copy(self):
        return MyImage.fromArray(self.im.copy())

    def setIm(self, imArray: Optional[ndarray]):
        if imArray is None:
            self.im = None
        else:
            self.im = np.uint8(imArray)

    def getShape(self):
        if self.im is not None:
            h, w, c = self.im.shape
            return (h, w, c)
        return None

    def _getReflectPos(self, value_i, start_i, f_len, min_i, max_i):
        if min_i <= value_i < max_i:
            return value_i

        if value_i >= max_i:
            exceed_i = max_i - value_i - 1
            new_i = start_i - exceed_i
            if new_i < max_i:
                return new_i
            else:
                new_i = max_i - f_len + (value_i - start_i)
                return new_i

        if min_i > value_i:
            exceed_i = min_i - value_i
            new_i = start_i + f_len - 1 + exceed_i

            if new_i >= min_i:
                return new_i
            else:
                return min_i + (value_i - start_i)

    def filter2D(self, kernel: ndarray, stride=(1, 1), mask=None):
        if self.im is None:
            return
        im_height, im_width, depth = self.im.shape

        fheight, fwidth = kernel.shape
        im_offh, im_offw = fheight // 2, fwidth // 2

        # print(kernel)

        im = np.zeros([im_height // stride[0], im_width //
                      stride[1], depth], dtype=np.float32)
        for h in range(0, im_height, stride[0]):
            for w in range(0, im_width, stride[1]):

                if mask is None or (mask is not None and mask[h, w] == True):
                    sum_value = im[h, w, :]
                    start_h = h - im_offh
                    start_w = w - im_offw

                    for fh in range(fheight):
                        for fw in range(fwidth):
                            imh = self._getReflectPos(
                                start_h + fh, start_h, fheight, 0, im_height)
                            imw = self._getReflectPos(
                                start_w + fw, start_w, fwidth, 0, im_width)

                            im_value = self.im[imh, imw,
                                               :] if 0 <= imh < im_height and 0 <= imw < im_width else 0
                            sum_value += im_value * kernel[fh, fw]
                    # print(sum_value)

                    sum_value[sum_value < 0] = 0
                    sum_value[sum_value > 255] = 255
                    # if sum_value[0] == 0:
                    #     print(sum_value, h, w)

                    im[h // stride[0], w // stride[1], :] = sum_value
                else:
                    im[h // stride[0], w // stride[1], :] = self.im[h, w, :]

        return MyImage.fromArray(im)

    def _filter2DSort(
        self, selectValuePolicy="medium", kernel_size: Tuple[int, int] = (3, 3), stride=(1, 1), mask=None
    ):
        if self.im is None:
            return
        im_height, im_width, depth = self.im.shape

        fheight, fwidth = kernel_size
        im_offh, im_offw = fheight // 2, fwidth // 2

        im = np.zeros([im_height // stride[0], im_width //
                      stride[1], depth], dtype=np.float32)
        for h in range(0, im_height, stride[0]):
            for w in range(0, im_width, stride[1]):

                if mask is None or (mask is not None and mask[h, w] == True):
                    start_h = h - im_offh
                    start_w = w - im_offw

                    im_v_list = []
                    for fh in range(fheight):
                        for fw in range(fwidth):
                            imh = self._getReflectPos(
                                start_h + fh, start_h, fheight, 0, im_height)
                            imw = self._getReflectPos(
                                start_w + fw, start_w, fwidth, 0, im_width)

                            if 0 <= imh < im_height and 0 <= imw < im_width:
                                im_value = self.im[imh, imw, :]
                                im_v_list.append(im_value)
                            else:
                                continue

                    im_v_list = np.array(im_v_list)
                    im_v_list.sort(axis=0)
                    if selectValuePolicy.lower() == "medium":
                        selected_value = im_v_list[len(im_v_list) // 2]
                    elif selectValuePolicy.lower() == "max":
                        selected_value = im_v_list[-1]
                    elif selectValuePolicy.lower() == "min":
                        selected_value = im_v_list[0]
                    else:
                        raise NotImplementedError(
                            "the policy has not implemented")

                    im[h // stride[0], w // stride[1], :] = selected_value
                else:
                    im[h // stride[0], w // stride[1], :] = self.im[h, w, :]

        return MyImage.fromArray(im)

    def max(self, kernel_size: Tuple[int, int] = (3, 3), stride=(1, 1), mask=None):
        return self._filter2DSort("max", kernel_size, stride, mask)

    def min(self, kernel_size: Tuple[int, int] = (3, 3), stride=(1, 1), mask=None):
        return self._filter2DSort("min", kernel_size, stride, mask)

    def medium(self, kernel_size: Tuple[int, int] = (3, 3), stride=(1, 1), mask=None):
        return self._filter2DSort("medium", kernel_size, stride, mask)

    def mean(self, kernel_size: Tuple[int, int] = (3, 3), mask=None):
        """
        return a im:MyImage applied mean algorithm
        """

        kernel = self._generateMeanKernel(kernel_size)
        return self.filter2D(kernel, stride=(1, 1), mask=mask)

    def _generateMeanKernel(self, kernel_size):
        return np.ones(kernel_size) / float(np.prod(kernel_size))

    def _gaussian(self, x, mean=0, std=1):
        return m.exp(-((x - mean) ** 2) / (2 * std ** 2 + 1e-10))

    def _generateGaussionKernel(self, kernel_mean=0, kernel_std=1, kernel_size: Tuple[int, int] = (3, 3)):
        # define a filter function
        kheight, kwidth = kernel_size
        k_mid_x, k_mid_y = kwidth // 2, kheight // 2

        # recalculate ratio function
        kernel = np.zeros(kernel_size)
        sum_ratio_value = 0
        for kh in range(kheight):
            for kw in range(kwidth):  # count row first
                # id - middle => mean is 0
                dist = m.sqrt((k_mid_x - kw) ** 2 + (k_mid_y - kh) ** 2)
                ratio_value = self._gaussian(dist, kernel_mean, kernel_std)
                kernel[kh, kw] = ratio_value
                sum_ratio_value += ratio_value

        # return the neighbor function
        return kernel / sum_ratio_value

    def gaussianBlur(self, mean=0, std=1, kernel_size: Tuple[int, int] = (3, 3), mask=None):

        kernel = self._generateGaussionKernel(mean, std, kernel_size)
        return self.filter2D(kernel, stride=(1, 1), mask=mask)

    def threshold(self, min_th=0, max_th=255, min_val=0, max_val=255):
        """
        return a image:MyImage applied a threshold, where value <= min_th will be min_value and value >= max_th will be max_value
        """
        assert 0 <= min_val <= min_th <= max_th <= max_val <= 255, "threshold boundary may not intersect each outher"

        im = self.im.copy()

        im[self.im <= min_th] = min_val
        im[self.im > max_th] = max_val
        return MyImage.fromArray(im)

    def colorAdjust(self, adjust_funcs: List[FunctionType], mask=None):
        if adjust_funcs is None or len(adjust_funcs) == 0:
            return

        height, width, channel = self.getShape()

        new_im = np.zeros_like(self.im)
        for d in range(min(len(adjust_funcs), channel)):
            ad_func = adjust_funcs[d]
            if ad_func is None:
                continue

            for h in range(height):
                for w in range(width):

                    imvalue = self.im[h, w, d]
                    if mask is None or (mask is not None and mask[h, w] == True):
                        new_im[h, w, d] = int(ad_func(imvalue))
                    else:
                        new_im[h, w, d] = imvalue

        return MyImage.fromArray(new_im)

    def unsharp(self, kernel_size=(3, 3), weight=2, method="mean", gaussian_mean=0, gaussian_std=1, mask=None):
        if method == "mean":
            mean_kernel = self._generateMeanKernel(kernel_size)
        elif method == "gaussian":
            mean_kernel = self._generateGaussionKernel(
                gaussian_mean, gaussian_std, kernel_size)
        else:
            raise NotImplementedError(
                f'This method "{method}" has not been implemented. ')

        self_kernel = np.zeros(kernel_size)
        middle_h = kernel_size[0] // 2
        middle_w = kernel_size[1] // 2
        self_kernel[middle_h, middle_w] = weight
        unsharp_kernel = self_kernel - mean_kernel

        return self.filter2D(unsharp_kernel, mask=mask)

    def getHistograms(self, mask=None):
        if self.im is None:
            return

        im_height, im_width, depth = self.im.shape

        hist_list = []
        for d in range(depth):

            value_sum_array = np.zeros(256)
            for h in range(im_height):
                for w in range(im_width):

                    if mask is None or (mask is not None and mask[h, w] == True):
                        value_sum_array[self.im[h, w, d]] += 1

            hist_list.append(value_sum_array)

        return hist_list

    def histogramEqualization(self, mask=None):
        if self.im is None:
            return
        im_height, im_width, depth = self.im.shape

        hist_list = self.getHistograms(mask)

        new_im = self.im.copy()
        for d in range(depth):

            pos_dict = {}
            value_sum_array = hist_list[d]
            total_sum = value_sum_array.sum()
            acc_value = 0
            for vi, v in enumerate(value_sum_array):
                acc_value += v

                ratio = acc_value / (total_sum + 1e-10)
                new_pos = int(ratio * 255)
                pos_dict[vi] = new_pos

            for h in range(im_height):
                for w in range(im_width):

                    if mask is None or (mask is not None and mask[h, w] == True):
                        im_v = self.im[h, w, d]
                        new_im[h, w, d] = pos_dict.get(im_v, im_v)
        return MyImage.fromArray(new_im)

    def save(self, filename):
        try:
            PilImage.fromarray(self.im).save(filename)
        except Exception as e:
            print(e)
            print("save image failed")

    def show(self):
        pm = PilImage.fromarray(self.im)
        pm.show()
