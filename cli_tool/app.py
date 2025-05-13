import cv2
import os
import numpy as np

class ImageStitcher:
    def __init__(self, min_matches=100):
        self.min_matches = min_matches
        self.sift = cv2.SIFT_create()

    def load_images(self, img_paths):
        images = []
        self.img_paths = img_paths
        for path in img_paths:
            img = cv2.imread(path)
            if img is None:
                print(f"{path}' could not be loaded.")
                continue
            images.append(img)
        self.images = images
       
    def stitch_images(self, output_path=None):
        min_matches = self.min_matches
        images = self.images
        img_paths = self.img_paths

        # the min number of common matches between two images for them to be stiched
        sift = cv2.SIFT_create()

        base_idx = len(images) // 2

        print(f"Base image: {img_paths[base_idx]}")

        base_img = images[base_idx]
        base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)

        keys_base, des_base = sift.detectAndCompute(base_img, None)

        # stores the homography matrcies
        homos = {base_idx: np.eye(3)}

        for i in range(len(images)):
            if i == base_idx:
                continue

            img = cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)
            keys, des = sift.detectAndCompute(img, None)

            matches = []

            # find the best matches
            for idx1, d1 in enumerate(des):
                dists = np.linalg.norm(des_base - d1, axis=1)
                nn_idx = np.argsort(dists)[:2]
                m, n = dists[nn_idx[0]], dists[nn_idx[1]]

                if n!=0 and m/n < 0.75:
                    matches.append((nn_idx[0], idx1))

            # get the images with most matches
            if len(matches) > min_matches:
                src_pts = np.float32([keys[idx2].pt for _, idx2 in matches]).reshape(-1, 2, 1)
                dst_pts = np.float32([keys_base[idx1].pt for idx1, _ in matches]).reshape(-1, 2, 1)

                H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                if H is not None:
                    homos[i] = H
                else:
                    print(f"Homography for image {img_paths[i]} failed.")
            else:
                print(f"Not enough good matches for image {img_paths[i]}")

        # prepare the canvas
        height = base_img.shape[0]
        width = base_img.shape[1]
        corners = np.float32([[0, 0], [0, height], [width, height], [width, 0]]).reshape(-1, 1, 2)
        all_corners = []

        for i, H in homos.items():
            warped_corners = cv2.perspectiveTransform(corners, H)
            all_corners.append(warped_corners)

        all_corners = np.concatenate(all_corners, axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)

        offset = [-x_min, -y_min]
        canvas_shape = (y_max - y_min, x_max - x_min, 3)
        result = np.zeros(canvas_shape, dtype=np.uint8)

        # stiching the images
        for i, H in homos.items():
            img = images[i]
            H_offset = np.eye(3)
            H_offset[:2, 2] = offset
            full_H = H_offset @ H

            warped = cv2.warpPerspective(img, full_H, (canvas_shape[1], canvas_shape[0]))
            mask = (warped > 0).astype(np.uint8)
            result = np.where(mask, warped, result)

        return cv2.imwrite(output_path, result)