from pathlib import Path
from IMPS import MyImage
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.lines as mlines
from PIL import Image


def compare_ims(ori_im, new_im):
    plt.subplot(121)
    plt.title("original image")
    plt.imshow(ori_im)
    # plt.imshow(ori_im, cmap="gray")
    plt.subplot(122)
    plt.title("mean image")
    plt.imshow(new_im)
    # plt.imshow(new_im, cmap="gray")
    plt.show()


def cv_testing():
    import cv2 as cv

    project_path = Path(".")
    images_path = project_path.absolute().joinpath("Resources/Images/look_gray.jpg")
    pil_im = Image.open(str(images_path))
    # im = cv.imread(str(one_image_path))
    # im = cv.cvtColor(im, cv.COLOR_BGR2RGB)

    # kernel_size = (7, 7)
    # # kernel = np.ones(kernel_size) / np.prod(kernel_size)
    # # kernel = np.random.(0, 1, kernel_size)
    # # mean_image = cv.filter2D(im, -1, kernel)
    # result_image = cv.bilateralFilter(im, 9, 25, 75)
    # # result_image = cv.GaussianBlur(im, kernel_size, 0)
    # print(result_image.shape)
    # compare_ims(im, result_image)

    im = cv.imread(str(images_path))
    im = cv.cvtColor(im, cv.COLOR_BGR2RGB)
    # im = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    # me_im = cv.medianBlur(im, ksize=7)
    # blur_im = cv.GaussianBlur(im, (3, 3), 1)
    # edge_im = cv.Canny(blur_im, 100, 200)

    # # dilate_im = cv.dilate(edge_im, cv.getStructuringElement(cv.MORPH_RECT, (5, 5)), iterations=1)
    # # erode_im = cv.erode(dilate_im, cv.getStructuringElement(cv.MORPH_RECT, (5, 5)), iterations=1)

    # dilate_im = cv.dilate(edge_im, cv.getStructuringElement(cv.MORPH_RECT, (3, 3)), iterations=1)
    # erode_im = cv.erode(dilate_im, cv.getStructuringElement(cv.MORPH_RECT, (3, 3)), iterations=1)
    # compare_ims(im, me_im)
    # line_detection_non_vectorized(im, edge_im)
    h, w, c = im.shape
    print((h, w))
    # Image.fromarray(im).resize((500, 750)).save(str(images_path))
    # MyImage.fromArray(im).show()
    print(np.allclose(pil_im, im))


def main():
    project_path = Path(".")
    images_path = project_path.absolute().joinpath("Resources/Images/look_gray.jpg")

    one_image = MyImage(str(images_path.absolute()))
    # one_image = MyImage(str(one_image_path.absolute()), "gray")
    # result_image = one_image.gaussianBlur(mean=0, std=1, kernel_size=(5, 5))
    # result_image = one_image.mean((5, 5))
    # result_image = one_image.unsharp((5, 5), "gaussian")
    result_image = one_image.histogramEqualization()
    # result_image = one_image.threshold(70, 200)

    # print(result_image.im)
    compare_ims(one_image.im, result_image.im)


if __name__ == "__main__":
    # main()
    cv_testing()
