from datetime import datetime
from urs_solution.msg import PIDController
import rospy

class PID:
    """
        This class implements a simple PID control algorithm.
    """

    def __init__(self):
        """
            Initializes PID gains (proportional - kp, integral - ki, derivative - kd) and control values to zero.
        """

        # initialize gains
        self.kp = 0     # proportional gain
        self.ki = 0     # integral gain
        self.kd = 0     # derivative gain

        # initialize control values
        self.up = 0                     # P part
        self.ui = 0                     # I part
        self.ui_old = 0                 # I part from previous step
        self.ud = 0                     # D part
        self.u = 0                      # total control value
        self.lim_up = float("inf")      # control value upper limit
        self.lim_low = -float("inf")    # control value lower limit

        # init referent control value (set-value)
        self.ref = 0

        # init measure control value
        self.meas = 0

        # init time stamp of the previous algorithm step
        self.t_old = datetime.now()

        # init error from the previous algorithm step
        self.error_old = 0

        # flag indicates first step of the algorithm
        self.firstPass = True

        # ros message formed when create_msg method is called
        self.pid_msg = PIDController()

    def reset(self):
        ''' Resets pid algorithm by setting all P,I,D parts to zero'''
        self.up = 0
        self.ui = 0
        self.ui_old = 0
        self.ud = 0
        self.u = 0
        self.t_old = datetime.now()

    def set_kp(self, invar):
        """ Set proportional gain. """
        self.kp = invar

    def get_kp(self):
        """Returns proportional gain"""
        return self.kp

    def set_ki(self, invar):
        """ Set integral gain. """
        self.ki = invar

    def get_ki(self):
        """Returns integral gain"""
        return self.ki

    def set_kd(self, invar):
        """ Set derivative gain. """
        self.kd = invar

    def get_kd(self):
        """Returns derivative gain"""
        return self.kd

    def set_lim_up(self, invar):
        """Set PID upper limit value"""
        self.lim_up = invar

    def get_lim_up(self):
        """Returns PID upper limit value"""
        return self.lim_up

    def set_lim_low(self, invar):
        """Set PID lower limit value"""
        self.lim_low = invar

    def get_lim_low(self):
        """Returns PID lower limit value"""
        return self.lim_low

    def compute(self, ref, meas):
        '''
        Performs a PID computation and returns a control value based on
        the elapsed time (dt) and the error signal.
        :param ref: referent value
        :param meas: measured value
        :return: control value
        '''

        self.ref = ref
        self.meas = meas

        if self.firstPass:
            # This is the first step of the algorithm
            # Init time stamp and error
            self.t_old = datetime.now()
            self.error_old = ref - meas
            self.firstPass = False
            return self.u           # initialized to zero
        else:
            ##############################################
            ##############################################
            # Add your code here
            # 1. You should compute elapsed time from the previous step (dt, in seconds),
            # 2. compute proportional part (self.up),
            # 3. compute integral part (self.ui),
            # 4. compute derivative part (self.ud),
            # 5. compute total control value (self.u),
            # 6. implement saturation function and antiwind-up,
            
            
            t = datetime.now()
            dt = (t - self.t_old).total_seconds()           # 1.
            self.ref = ref
            self.meas = meas
            error = ref - meas

            de = error - self.error_old                         
            self.up = self.kp * error                           # 2.

            if self.ki == 0:
                self.ui = 0
            else:
                self.ui = self.ui_old + self.ki * error * dt        # 3.

            self.ud = self.kd * de / dt                         # 4.

            self.u = self.up + self.ui + self.ud

            if self.u > self.lim_up:
                self.u =  self.lim_up
                self.ui = self.ui_old           # 6. Integral antiwind up
            elif self.u < self.lim_low:
                self.u =  self.lim_low
                self.ui = self.ui_old          

            self.ui_old = self.ui                          
            self.t_old = t                                  
            self.error_old = error                          

            # End of added code
            ###############################################
            ###############################################

            return self.u

    def get_pid_values(self):
        """ Returns P, I, D components and total control value
        """
        return [self.up, self.ui, self.ud, self.u]

    def create_msg(self):
        """ Returns ros message of type PIDController
        """
        self.pid_msg.ref = self.ref
        self.pid_msg.meas = self.meas
        self.pid_msg.P = self.up
        self.pid_msg.I = self.ui
        self.pid_msg.D = self.ud
        self.pid_msg.U = self.u
        self.pid_msg.header.stamp = rospy.Time.now()
        return self.pid_msg
