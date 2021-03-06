from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import numpy as np 
import os
import glob
import imageio
import cv2
from scipy import misc
#from libtiff import TIFF

class myAugmentation(object):
	
	"""
	A class used to augmentate image
	Firstly, read train image and label seperately, and then merge them together for the next process
	Secondly, use keras preprocessing to augmentate image
	Finally, seperate augmentated image apart into train image and label
	"""

	def __init__(self, train_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/train/image",
		label_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/train/label",
		merge_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/aumentation",
		aug_merge_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/aumentation/aug_merge",
		aug_train_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/aumentation/aug_train",
		aug_label_path="/home/ahmed/github/melanoma.1.0/dataset/2016data/aumentation/aug_label",
		img_type="jpg"):
		
		"""
		Using glob to get all .img_type form path
		"""

		self.train_imgs = glob.glob(train_path + "/*" + img_type)
		self.label_imgs = glob.glob(label_path+"/*.png")
		self.train_path = train_path
		self.label_path = label_path
		self.merge_path = merge_path
		self.img_type = img_type
		self.aug_merge_path = aug_merge_path
		self.aug_train_path = aug_train_path
		self.aug_label_path = aug_label_path
		self.slices = len(self.train_imgs)
		self.datagen = ImageDataGenerator(
							        rotation_range=180,
							        width_shift_range=5,
							        height_shift_range=5,
							        shear_range=1,
							        zoom_range=5,
							        horizontal_flip=True,
							        vertical_flip=True,
							        fill_mode='nearest')

	def Augmentation(self):

		"""
		Start augmentation.....
		"""
		trains = self.train_imgs
		labels = self.label_imgs
		path_train = self.train_path
		path_label = self.label_path
		path_merge = self.merge_path
		imgtype = self.img_type
		path_aug_merge = self.aug_merge_path
		if len(trains) != len(labels) or len(trains) == 0 or len(trains) == 0:
			print("trains can't match labels")
			return 0
		for i in trains:
			name = i[i.rindex("/")+1:-11]
			img_t = load_img(i)
			img_l = load_img(path_label+"/"+ name + "padding_ground.png", grayscale=True)
			x_t = img_to_array(img_t)
			x_l = img_to_array(img_l)
			x = np.dstack((x_t, x_l))
			
			# np.save(path_merge+"/"+name+".npy" , x)
			img = x
			img = img.reshape((1,) + img.shape)
			savedir = path_aug_merge + "/" + name
			if not os.path.lexists(savedir):
				os.mkdir(savedir)
			self.doAugmentate(img, savedir, name)


	def doAugmentate(self, img, save_to_dir, save_prefix, batch_size=1, save_format='tif', imgnum=10):

		"""
		augmentate one image
		"""
		datagen = self.datagen
		i = 0
		for batch in datagen.flow(img,
                          batch_size=batch_size,
                          save_to_dir=save_to_dir,
                          save_prefix=save_prefix,
                          save_format=save_format):
		    i += 1
		    if i > imgnum:
		        break

	def splitMerge(self):

		"""
		split merged image apart
		"""
		path_merge = self.aug_merge_path
		path_train = self.aug_train_path
		path_label = self.aug_label_path
		for i in self.train_imgs:
			name = i[i.rindex("/")+1:-11]
			path = path_merge + "/" + name
			train_is = glob.glob(path+"/*.npy")
			savedir = path_train + "/" + name
			if not os.path.lexists(savedir):
				os.mkdir(savedir)
			savedir = path_label + "/" + name
			if not os.path.lexists(savedir):
				os.mkdir(savedir)
			for imgname in train_is:
				midname = imgname[imgname.rindex("/")+1:imgname.rindex(".npy")]
				img = np.load(imgname)
				img_train = img[:,:,:3]#cv2 read image rgb->bgr
				img_label = img[:,:,3]
				misc.imsave(path_train+"/"+name+"/"+midname+"_train"+".jpg",img_train)
				misc.imsave(path_label+"/"+name+"/"+midname+"_label"+".png",img_label)

	def splitTransform(self):

		"""
		split perspective transform images
		"""
		#path_merge = "transform"
		#path_train = "transform/data/"
		#path_label = "transform/label/"
		path_merge = "deform/deform_norm2"
		path_train = "deform/train/"
		path_label = "deform/label/"
		train_imgs = glob.glob(path_merge+"/*."+self.img_type)
		for imgname in train_imgs:
			midname = imgname[imgname.rindex("/")+1:imgname.rindex("."+self.img_type)]
			img = cv2.imread(imgname)
			img_train = img[:,:,2]#cv2 read image rgb->bgr
			img_label = img[:,:,0]
			cv2.imwrite(path_train+midname+"."+self.img_type,img_train)
			cv2.imwrite(path_label+midname+"."+self.img_type,img_label)



class dataProcess(object):

	def __init__(self, out_rows, out_cols, data_path="/content/melanoma.1.0/dataset/2016data/train/image",
				 label_path="/content/melanoma.1.0/dataset/2016data/train/label",
				 test_path="/content/melanoma.1.0/dataset/2016data/test/image", npy_path="/content/unet-keras/npydata",
				 img_type="jpg"):
		"""
		
		"""

		self.out_rows = out_rows
		self.out_cols = out_cols
		self.data_path = data_path
		self.label_path = label_path
		self.img_type = img_type
		self.test_path = test_path
		self.npy_path = npy_path

	def create_train_data(self):
		i = 0
		print('-'*30)
		print('Creating training images...')
		print('-'*30)
		imgs = glob.glob(self.data_path+"/*."+self.img_type)
		print(len(imgs))
		imgdatas = np.ndarray((len(imgs),self.out_rows,self.out_cols,3), dtype=np.uint8)
		imglabels = np.ndarray((len(imgs),self.out_rows,self.out_cols,1), dtype=np.uint8)
		imgffts = np.ndarray((len(imgs),self.out_rows,self.out_cols,1), dtype=np.uint8)
		for imgname in imgs:
			midname = imgname[imgname.rindex("/")+1:]
			img = load_img(self.data_path + "/" + midname,grayscale = False)
			img_gray = load_img(self.data_path + "/" + midname, grayscale = True)
			label = load_img(self.label_path + "/" + midname.replace(".jpg","_ground.png"), grayscale=True)
			img = img_to_array(img)
			label = img_to_array(label)
			#img = cv2.imread(self.data_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
			#label = cv2.imread(self.label_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
			#img = np.array([img])
			#label = np.array([label])
			imgdatas[i] = img
			imglabels[i] = label

			fft_img = np.fft.fft2(img_gray)
			fft_img = np.fft.fftshift(fft_img)
			fft_img = 20*np.log(np.abs(fft_img))
			fft_img = img_to_array(fft_img)
			imgffts[i] = fft_img

			# imglabels[i, ..., 1] = 255 - label
			if i % 100 == 0:
				print('Done: {0}/{1} images'.format(i, len(imgs)))
			i += 1
		print('loading done')
		np.save(self.npy_path + '/imgs_train.npy', imgdatas)
		np.save(self.npy_path + '/imgs_mask_train.npy', imglabels)
		np.save(self.npy_path + '/imgs_fft_train.npy', imgffts)
		print('Saving to .npy files done.')

	def create_test_data(self):
		i = 0
		print('-'*30)
		print('Creating test images...')
		print('-'*30)
		imgs = glob.glob(self.test_path+"/*."+self.img_type)
		names = []
		for name in imgs:
			n = name[name.rindex("/")+1:name.rindex("/")+8]
			names.append(n)
		np.save("/content/unet-keras/names.npy", names)
		print(len(imgs))
		imgdatas = np.ndarray((len(imgs),self.out_rows,self.out_cols,3), dtype=np.uint8)
		imgffts = np.ndarray((len(imgs),self.out_rows,self.out_cols,1), dtype=np.uint8)
		for imgname in imgs:
			midname = imgname[imgname.rindex("/")+1:]
			img = load_img(self.test_path + "/" + midname,grayscale = False)
			img = img_to_array(img)
			imgfft = load_img(self.test_path + "/" + midname, grayscale=True)
			imgfft = np.fft.fftshift(np.fft.fft2(imgfft))
			imgfft = 20*np.log(np.abs(imgfft))
			imgfft = img_to_array(imgfft)
			#img = cv2.imread(self.test_path + "/" + midname,cv2.IMREAD_GRAYSCALE)
			#img = np.array([img])
			imgdatas[i] = img
			imgffts[i] = imgfft
			i += 1
		print('loading done')
		np.save(self.npy_path + '/imgs_test.npy', imgdatas)
		np.save(self.npy_path + '/imgs_test_fft.npy', imgffts)
		print('Saving to imgs_test.npy files done.')

	def load_train_data(self):
		print('-'*30)
		print('load train images...')
		print('-'*30)
		imgs_train = np.load(self.npy_path+"/imgs_train.npy")
		imgs_mask_train = np.load(self.npy_path+"/imgs_mask_train.npy")
		imgs_fft = np.load(self.npy_path + "/imgs_fft_train.npy")
		imgs_train = imgs_train.astype('float32')
		imgs_mask_train = imgs_mask_train.astype('float32')
		imgs_fft = imgs_fft.astype('float32')

		self.mean_fft = imgs_fft.mean(axis = 0)
		self.range_fft = (imgs_fft.max() - imgs_fft.min())
		imgs_fft -= self.mean_fft
		imgs_fft /= self.range_fft
		imgs_train /= 255
		self.mean = imgs_train.mean(axis = 0)
		imgs_train -= self.mean	
		imgs_mask_train /= 255
		imgs_mask_train[imgs_mask_train > 0.5] = 1
		imgs_mask_train[imgs_mask_train <= 0.5] = 0

		# train = np.zeros((imgs_train.shape[0], imgs_train.shape[1], imgs_train.shape[2], 4))
		# for i, img in enumerate(imgs_train):
		# 	train[i] = np.concatenate((imgs_train[i], imgs_fft[i]), axis=2)
		return imgs_fft, imgs_train, imgs_mask_train

	def load_test_data(self):
		print('-'*30)
		print('load test images...')
		print('-'*30)
		imgs_test = np.load(self.npy_path+"/imgs_test.npy")
		imgs_test_fft = np.load(self.npy_path + '/imgs_test_fft.npy')
		imgs_test = imgs_test.astype('float32')
		imgs_test_fft = imgs_test_fft.astype('float32')
		imgs_test /= 255
		# mean = imgs_test.mean(axis = 0)
		imgs_test -= self.mean

		imgs_test_fft -= self.mean_fft
		imgs_test_fft /= self.range_fft
		return imgs_test_fft, imgs_test

if __name__ == "__main__":

	#aug = myAugmentation()
	#aug.Augmentation()
	#aug.splitMerge()
	#aug.splitTransform()
	mydata = dataProcess(256,256)
	mydata.create_train_data()
	mydata.create_test_data()
	#imgs_train,imgs_mask_train = mydata.load_train_data()
	#print imgs_train.shape,imgs_mask_train.shape
