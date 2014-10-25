from libs.db_mongo import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY
from libs.security import (generate_admin_hash_and_salt,
                           generate_user_hash_and_salt,
                           compare_password, device_hash,
                           generate_user_password_and_salt,
                           generate_admin_password_and_salt,
                           generate_upper_case_alphanumeric_string,)

# NOTES on the password setup (by eli, he was tired.)

# TODO: implement initial user setup/device registration pin provided by an admin to a user.
# actually we should implement this by just setting a default password that the user has to type in on first run.

# HOWTO: implement password reset
# on login screen: 1 regular enter password to log-in field, one forgot password button
# forgot password button: explains they need to call the study, and talk with someone.
# that someone will send them a reset code, which they type into the single field
# that you can enter from the forgot password screen.  On entering the reset pin
# sets the reset pin to be your new password.  You can then go and reset your password in
# the password reset screen.  Note that resetting a password requires a data connection.

# TODO: Dori.  The reset password activity inside of the app (the one that you
# can access when you are logged in on the device) requires an active internet connection.


# TODO: Eli/Dori.  weeeee need to make a single column bluetooth address database...


# TODO: Eli.  cleanup and document this.

################################################################################
################################### USER STUFF #################################
################################################################################



class User( DatabaseObject ):
    
    PATH = "database.users"
    
    # Column Name:Default Value.  Use REQUIRED to indicate a non-nullable value.
    # We are using the patient's assigned ID as a unique Id.
    DEFAULTS = { "password":REQUIRED, 'device_id':None, 'salt':REQUIRED }
    
    @classmethod
    def create(cls):
        """ Creates a new patient with random patient_id and password."""
        patient_id = generate_upper_case_alphanumeric_string()
        password, password_hash, salt = generate_user_password_and_salt()
        new_client = {ID_KEY: patient_id, "password":password_hash,
                      'device_id':None, "salt":salt }
        super(User, cls).create(new_client)
        return patient_id, password
    
    
    @classmethod
    def check_password(cls, patient_id, compare_me ):
        """ Checks if a patient id and user name combination are valid, returns
            a boolean."""
        if not User.exists( patient_id ):
            return False
        user = User( patient_id )
        return user.validate_password( compare_me )
    
    
    def validate_password(self, compare_me):
        """ Checks if the input matches the instance's password hash."""
        return compare_password( compare_me, self['salt'], self['password'] )
    
    
    def reset_password_for_debugging(self):
        """ Resets the password to match something new and random,
            returns the new password string."""
        password = generate_upper_case_alphanumeric_string()
        self.set_password(password)
        return password
    
    
    def reset_password(self):
        """ Resets the patient's password to match an sha256 hash of the returned string."""
        password = generate_upper_case_alphanumeric_string()
        device_password_hash = device_hash(device_hash( password ))
        self.set_password( device_password_hash )
        return password
    
    
    def set_device(self, device_id):
        """ Sets the device id to the new value"""
        self['device_id'] =  device_id
        self.save()
    
    
    def clear_device(self):
        """ Clears the device entry."""
        self['device_id'] =  None
        self.save()
    
    
    def set_password(self, password):
        """ Sets the instance's password hash to match the provided string."""
        password, salt  = generate_user_hash_and_salt( password )
        self['password'] = password
        self['salt'] = salt
        self.save()


#the thing I use to access the entire table
class Users( DatabaseCollection ):
    """ The Users database."""
    OBJTYPE = User
    
################################################################################
################################### ADMIN STUFF ################################
################################################################################
    
    
class Admin( DatabaseObject ):
    PATH = "database.admins"
    
    DEFAULTS = { "password":REQUIRED, 'salt':REQUIRED }
    
    @classmethod
    def create(cls, username, password):
        """ Creates a new Admin with provided password and user name."""
        password, salt = generate_admin_hash_and_salt( password )
        new_admin = {ID_KEY :username, 'password':password, 'salt':salt }
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    def check_password(cls, username, compare_me ):
        """ Checks if the provided password matches the hash of the provided
            Admin's password."""
        if not Admin.exists( username ):
            return False
        admin = Admin( username )
        return admin.validate_password( compare_me )
    
    
    #provide this instance with a password, it returns true if it matches
    def validate_password(self, compare_me):
        """ Checks if the input matches the instance's password hash."""
        return compare_password( compare_me, self['salt'], self['password'] )
    
    
    def set_password(self, new_password):
        """Sets the instances password hash to match the provided password."""
        password, salt = generate_admin_hash_and_salt( new_password )
        self['password'] = password
        self['salt'] = salt
        self.save()
    
    
class Admins( DatabaseCollection ):
    """ The Admins Database."""
    OBJTYPE = Admin