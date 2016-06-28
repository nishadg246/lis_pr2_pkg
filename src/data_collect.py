#Data-collection script 
import rospy
import tf as tf

import roslib



def collect_data():
    file_name = raw_input("Enter file name to write to:")
    reference = raw_input("Enter a reference frame:")
    secondary = raw_input("Enter a secondary frame:")
    f = open(file_name, 'w')
    while not rospy.is_shutdown():
        try:
            t = listener.getLatestCommonTime('/' + reference + '_' + str(num) , '/' + secondary +'_' + str(num))
            (translation, rot) = listener.lookupTransform('/' + reference + '_' + str(num) , '/' + secondary + '_' + str(num), t)
            f.write("Time: "+ str(t) + '\n')            
	    f.write("Translation data: "+ str(translation) + '\n')
            f.write("Rotation data (quaternion): "+ str(rot) + '\n')
	    f.write("Rotation data (radians): " + str(tf.transformations.euler_from_quaternion(rot)) + '\n' )
	    f.write('\n' )
	    print "Writing to file!"

        except (tf.Exception):
            print "Human not detected"
            continue
 
    f.close() 
        
if __name__ == '__main__':
    rospy.init_node('tf_elbow')

    listener = tf.TransformListener()
    rate = rospy.Rate(10.0)
    num = 1
    collect_data()
