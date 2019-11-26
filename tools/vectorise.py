import argparse
import cv2


DESCRIPTION = " Convert a mask image into vector format..."
KERNEL_SIZE = 4


def _parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', "--input", type=str, default=None,
                        help="mask or image to be vectorised")
    parser.add_argument('-d', "--directory", type=str, default=None,
                        help="a directory containing images or masks to be vectorised")
    return parser.parse_args()


def cluster(mask):
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (KERNEL_SIZE, 1))
    mask_h = cv2.erode(mask, kernel=kernel_h, iterations=3)
    mask_h = cv2.dilate(mask_h, kernel=kernel_h, iterations=3)

    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, KERNEL_SIZE))
    mask_v = cv2.erode(mask, kernel=kernel_v, iterations=3)
    mask_v = cv2.dilate(mask_v, kernel=kernel_v, iterations=3)

    return cv2.addWeighted(mask_v, 0.5, mask_h, 0.5, 0.0)


def save_as_png(image):
    cv2.imwrite("output.png", image)

def bin_mask(mask):
    for

if __name__ == '__main__':
    args = _parse_args()
    if args.input is not None:
        mask = cv2.imread(args.input, 0)
        mask = cluster(mask)
        save_as_png(mask)


