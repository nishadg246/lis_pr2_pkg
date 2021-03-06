import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from lis_pr2_pkg.uber_controller import UberController

rospy.init_node("head_tracking")

head_limits = np.array([[-2.0, -.5], [2.0, .5]])
dx = -0.06/320
dy = 0.04/240
eps = 0.03

class HeadListener:
	def __init__(self):
		self.bridge = CvBridge()
		self.faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
		self.UC = UberController()
		self.head_pos = np.array(self.UC.get_head_pose())
		self.sub = rospy.Subscriber('/head_mount_kinect/rgb/image_rect_color',
			Image,
			self.call_back,
			queue_size = 1)
		self.pub = rospy.Publisher('/head_tracking/face_detections', Image)

		
	def call_back(self, data):
		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
		except CvBridgeError as e:
			print(e)

		faces = self.faceCascade.detectMultiScale(
			cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY),
			scaleFactor = 1.1,
			minNeighbors = 5,
			minSize = (30,30),
			flags = cv2.cv.CV_HAAR_SCALE_IMAGE)

		for x, y, w, h in faces:
			cv2.rectangle(cv_image, (x, y), (x+w, y+h), (0, 0, 255), 2)

		head_pos = self.head_pos
		avg = [(f[0] + f[2]/2, f[1] + f[3]/2) for f in faces]

		image_shape = cv_image.shape


		if len(avg) > 0:
			avg = np.mean(avg, axis=0)
			off_center = avg - np.array((image_shape[0]/2, image_shape[1]/2))

			if off_center[0] > eps*image_shape[0]:
				head_pos[0] += dx*np.abs(off_center[0])
			elif off_center[0] < - eps*image_shape[0]:
				head_pos[0] -= dx*np.abs(off_center[0])

			if off_center[1] > eps*image_shape[1]:
				head_pos[1] += dy*np.abs(off_center[1])
			elif off_center[1] < - eps*image_shape[1]:
				head_pos[1] -= dy*np.abs(off_center[1])

		head_pos = np.clip(head_pos, *head_limits)
		self.head_pos = head_pos

		self.UC.command_head(head_pos, 0.2, False)

		try:
			self.pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
		except CvBridgeError as e:
			print(e)


HeadListener()
rospy.spin()